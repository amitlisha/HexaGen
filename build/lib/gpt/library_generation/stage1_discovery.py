"""Stage 1: API Discovery through batch analysis and deduplication.

This stage analyzes the entire training set:
1. Split instructions into batches
2. Generate an API proposal for each batch
3. Merge all batch proposals
4. Deduplicate redundant methods via LLM

DOMAIN-AGNOSTIC: Works with any dataset in standard format.
See data_format.md for required format.
"""

from __future__ import annotations

import json
import argparse
from pathlib import Path
from typing import List, Dict, Optional, Union, Any
from concurrent.futures import ThreadPoolExecutor, as_completed


def load_base_library_docs(docs_path: str) -> str:
    """Load base library API documentation."""
    docs_file = Path(docs_path)
    if not docs_file.exists():
        raise FileNotFoundError(f"Base library docs not found: {docs_path}")
    return docs_file.read_text(encoding="utf-8")


def load_all_instructions(
    data_path: str, include_io: bool = False
) -> List[Union[str, Dict[str, Any]]]:
    """Load all instructions from a standardized JSONL dataset.

    Expected format (see data_format.md):
    {
      "task_id": "...",
      "steps": [
        {"instruction": "...", "input_state": [...], "output_state": [...]},
        ...
      ]
    }

    Args:
        data_path: Path to standardized JSONL file
        include_io: If True, return dicts with instruction + input/output states

    Returns:
        List of instruction strings, or list of dicts with instruction/input_state/output_state
    """
    instructions = []
    data_file = Path(data_path)

    if not data_file.exists():
        raise FileNotFoundError(f"Training data file not found: {data_path}")

    with open(data_file, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            try:
                obj = json.loads(line)

                if "task_id" not in obj or "steps" not in obj:
                    print(
                        f"Warning: Line {line_num} missing required fields (task_id, steps)"
                    )
                    continue

                for step in obj["steps"]:
                    if "instruction" not in step:
                        print(
                            f"Warning: Step in task {obj['task_id']} missing instruction"
                        )
                        continue

                    instruction = step["instruction"]
                    if instruction:
                        if include_io:
                            instructions.append(
                                {
                                    "instruction": instruction,
                                    "output_state": step.get("output_state", []),
                                }
                            )
                        else:
                            instructions.append(instruction)

            except json.JSONDecodeError as e:
                print(f"Warning: Invalid JSON on line {line_num}: {e}")
            except Exception as e:
                print(f"Warning: Error processing line {line_num}: {e}")

    return instructions


def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """Split a list into chunks of given size."""
    return [lst[i : i + chunk_size] for i in range(0, len(lst), chunk_size)]


def _format_state(state: List[Any]) -> str:
    """Format a board state compactly, showing only non-zero (colored) tiles."""
    if not state:
        return "[]"
    non_zero = [(idx, val) for idx, val in enumerate(state) if val != 0]
    if not non_zero:
        return "[all blank]"
    return str(non_zero)


def format_instructions(instructions: List[Union[str, Dict[str, Any]]]) -> str:
    """Format a list of instructions for display."""
    lines = []
    for i, item in enumerate(instructions):
        if isinstance(item, dict):
            line = f"{i+1}. Instruction: {item['instruction']}"
            line += f"\n   Output state: {_format_state(item.get('output_state', []))}"
        else:
            line = f"{i+1}. {item}"
        lines.append(line)
    return "\n".join(lines)


def build_batch_proposal_prompt(batch: List[Union[str, Dict[str, Any]]], base_lib_docs: str) -> str:
    """Build the prompt for generating an API proposal from a single batch."""
    io_note = ""
    if batch and isinstance(batch[0], dict):
        io_note = (
            "\nEach instruction includes its output state (board after). "
            "Non-zero values represent colored tiles. Use these to understand the transformations.\n"
        )

    prompt = f"""You have a minimal base library:

{base_lib_docs}

Analyze these {len(batch)} instructions and design NEW methods to extend the base library:
{io_note}
{format_instructions(batch)}

OUTPUT FORMAT:
```
Class: ClassName
  Method: method_name(param: type) -> ReturnType
    Description: [1 sentence - what it does]
    Rationale: [What problem this solves + how often this pattern appears in the instructions]
    Necessity: [Why users need this abstraction]
```

DESIGN CRITERIA:
Each method must:
- Address a complex pattern found in the instructions above
- Be non-trivial - users would struggle to implement correctly
- Involve non-trivial algorithms or domain-specific logic
- Require knowledge of internal data structures or complex rules

NOT:
- Easily composable from existing methods
- Simple wrapper or utility
- Simple property access, collection builders, thin wrappers

Quality > Quantity. Propose only methods meeting all criteria."""
    return prompt


def generate_batch_proposal(
    batch: List[Union[str, Dict[str, Any]]],
    batch_num: int,
    total_batches: int,
    base_lib_docs: str,
    model: str,
    temperature: float,
    max_tokens: Optional[int],
    thinking_effort: str | None = None,
    thinking_level: str | None = None,
    request_timeout: int = 300,
) -> str:
    """Generate an API proposal from a single batch of instructions."""
    system_prompt = "You are a programming language designer creating minimal, powerful APIs from pattern analysis."
    prompt = build_batch_proposal_prompt(batch, base_lib_docs)

    print(f"Generating proposal for batch {batch_num}/{total_batches} ({len(batch)} instructions)...")

    from gpt.llm_wrapper import call_llm

    response = call_llm(
        prompt=prompt,
        system_prompt=system_prompt,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        reasoning_effort=thinking_effort,
        thinking_level=thinking_level,
        request_timeout=request_timeout,
    )

    return response["text"]


def _build_dedup_prompt(api_proposal: str) -> str:
    """Build the prompt for deduplicating an API proposal."""
    return f"""Review this API proposal and remove any duplicated or redundant methods.
Methods are duplicates if they have the same name, or if they do essentially the same thing under different names.

When you find duplicates:
- Keep the best-described version
- Merge any unique details from the duplicate into the kept version
- Remove the duplicate entirely

Return the cleaned API proposal in the EXACT SAME FORMAT, with only unique methods remaining.
Do NOT add new methods or modify the logic of existing ones — only remove duplicates.

API PROPOSAL:
{api_proposal}"""


def deduplicate_api_proposal(
    api_proposal: str,
    model: str,
    temperature: float,
    max_tokens: Optional[int],
    thinking_effort: str | None = None,
    thinking_level: str | None = None,
    request_timeout: int = 300,
) -> str:
    """Use an LLM to remove duplicated methods from the merged API proposal."""
    from gpt.llm_wrapper import call_llm

    system_prompt = "You are a programming language designer reviewing an API proposal for redundancy."
    prompt = _build_dedup_prompt(api_proposal)

    print("Deduplicating API proposal (removing redundant methods)...")

    response = call_llm(
        prompt=prompt,
        system_prompt=system_prompt,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        reasoning_effort=thinking_effort,
        thinking_level=thinking_level,
        request_timeout=request_timeout,
    )

    return response["text"]


def save_json(data: Dict[str, Any], path: Path):
    """Save JSON data to file."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def timestamp() -> str:
    """Generate timestamp string."""
    from datetime import datetime

    return datetime.now().strftime("%Y-%m-%dT%H-%M-%S")


def run_stage1(cfg: argparse.Namespace, output_dir: Path) -> Dict[str, Any]:
    """Run Stage 1: API Discovery.

    Args:
        cfg: Configuration namespace
        output_dir: Directory to save outputs

    Returns:
        Dictionary with stage results
    """
    print(f"\n{'='*70}")
    print("STAGE 1: API DISCOVERY")
    print(f"{'='*70}\n")

    include_io = getattr(cfg, "include_io", False)
    merged_file = output_dir / "api_proposal_merged.md"

    # Check if we can resume from deduplication (merged proposal already exists)
    if merged_file.exists():
        print(f"Found existing merged proposal: {merged_file}")
        print("Skipping batch proposal generation, resuming from deduplication...\n")
        merged_proposal = merged_file.read_text(encoding="utf-8")

        all_instructions = load_all_instructions(cfg.train_data, include_io=include_io)
        num_batch_proposals = len(sorted(output_dir.glob("batch_*_proposal.md")))
        num_batches = num_batch_proposals
        print(f"Found {num_batch_proposals} existing batch proposals\n")
    else:
        # Load base library documentation
        print(f"Loading base library docs from {cfg.base_lib_docs}...")
        base_lib_docs = load_base_library_docs(cfg.base_lib_docs)
        print(f"✓ Loaded {len(base_lib_docs)} characters\n")

        # Load all instructions
        print(f"Loading instructions from {cfg.train_data}...")
        if include_io:
            print("  (including input/output states)")
        all_instructions = load_all_instructions(cfg.train_data, include_io=include_io)
        print(f"✓ Loaded {len(all_instructions)} instructions\n")

        # Step 1: Split into batches
        print(f"STEP 1: Batch API Proposal Generation (batch_size={cfg.batch_size})")
        print("-" * 70)

        if getattr(cfg, "semantic_batching", False):
            from stage1_semantic_batching import create_semantic_batches

            print("Using semantic batching (embedding-based clustering)")
            batches = create_semantic_batches(
                all_instructions,
                cfg.batch_size,
                embedding_model=getattr(cfg, "embedding_model", "BAAI/bge-m3"),
                output_dir=output_dir,
                cache_key=Path(cfg.train_data).stem,
            )
        else:
            batches = chunk_list(all_instructions, cfg.batch_size)

        print(f"Split into {len(batches)} batches\n")

        batch_proposals = []

        # Check for existing batch proposals to enable resume
        existing_batches = {}
        for bf in output_dir.glob("batch_*_proposal.md"):
            try:
                idx = int(bf.stem.split("_")[1]) - 1  # batch_001 -> index 0
                if 0 <= idx < len(batches):
                    existing_batches[idx] = bf
            except (ValueError, IndexError):
                pass

        if existing_batches:
            print(f"Found {len(existing_batches)}/{len(batches)} existing batch proposals, resuming...")

        if getattr(cfg, "batch", False) or getattr(cfg, "batch_resume", None):
            print("Using LLM Batch API for proposal generation...")
            import sys

            gpt_dir = Path(__file__).parent.parent
            if str(gpt_dir) not in sys.path:
                sys.path.insert(0, str(gpt_dir))

            from llm_wrapper import (
                _is_gemini_model,
                build_openai_messages,
                build_openai_request_body,
                submit_openai_batch,
                poll_openai_batch,
                parse_batch_results,
                build_gemini_batch_request,
                submit_gemini_batch,
                poll_gemini_batch,
                parse_gemini_batch_results,
            )

            system_prompt = "You are a programming language designer creating minimal, powerful APIs from pattern analysis."
            is_gemini = _is_gemini_model(cfg.model)

            if is_gemini:
                gemini_requests = []
                for i, batch in enumerate(batches):
                    prompt = build_batch_proposal_prompt(batch, base_lib_docs)
                    request = build_gemini_batch_request(
                        prompt=prompt,
                        system_prompt=system_prompt,
                        temperature=cfg.temperature,
                        max_tokens=cfg.max_tokens,
                        thinking_level=getattr(cfg, "thinking_level", None),
                    )
                    gemini_requests.append(request)

                if getattr(cfg, "batch_resume", None):
                    print(f"Resuming Gemini batch: {cfg.batch_resume}")
                    batch_job = poll_gemini_batch(cfg.batch_resume, getattr(cfg, "batch_poll_interval", 60), getattr(cfg, "batch_timeout", 86400))
                else:
                    display_name = f"{cfg.experiment_name}-stage1-{cfg.model}"
                    job_name = submit_gemini_batch(gemini_requests, cfg.model, display_name)
                    print(f"Created Gemini batch: {job_name}")
                    batch_job = poll_gemini_batch(job_name, getattr(cfg, "batch_poll_interval", 60), getattr(cfg, "batch_timeout", 86400))

                print(f"Parsing Gemini batch results...")
                batch_results = parse_gemini_batch_results(batch_job, gemini_requests)

                for i in range(len(batches)):
                    result = batch_results.get(i)
                    if result and not result.get("error"):
                        proposal = result["text"]
                    else:
                        err = (result or {}).get("error", "unknown error")
                        proposal = f"ERROR: {err}"
                    batch_proposals.append((i, proposal))

            else:
                jsonl_lines = []
                for i, batch in enumerate(batches):
                    custom_id = f"batch_{i}"
                    prompt = build_batch_proposal_prompt(batch, base_lib_docs)
                    messages = build_openai_messages(prompt=prompt, system_prompt=system_prompt)
                    body = build_openai_request_body(
                        messages=messages,
                        model=cfg.model,
                        temperature=cfg.temperature,
                        max_tokens=cfg.max_tokens,
                        reasoning_effort=getattr(cfg, "thinking_effort", None),
                    )
                    jsonl_lines.append(json.dumps({
                        "custom_id": custom_id,
                        "method": "POST",
                        "url": "/v1/chat/completions",
                        "body": body,
                    }))

                if getattr(cfg, "batch_resume", None):
                    print(f"Resuming OpenAI batch: {cfg.batch_resume}")
                    batch_obj = poll_openai_batch(cfg.batch_resume, getattr(cfg, "batch_poll_interval", 60), getattr(cfg, "batch_timeout", 86400))
                else:
                    batch_id = submit_openai_batch(jsonl_lines)
                    print(f"Created OpenAI batch: {batch_id}")
                    batch_obj = poll_openai_batch(batch_id, getattr(cfg, "batch_poll_interval", 60), getattr(cfg, "batch_timeout", 86400))

                batch_results = {}
                if batch_obj.output_file_id:
                    batch_results.update(parse_batch_results(batch_obj.output_file_id))
                if batch_obj.error_file_id:
                    batch_results.update(parse_batch_results(batch_obj.error_file_id))

                for i in range(len(batches)):
                    custom_id = f"batch_{i}"
                    result = batch_results.get(custom_id)
                    if result and not result.get("error"):
                        proposal = result["text"]
                    else:
                        err = (result or {}).get("error", "unknown error")
                        proposal = f"ERROR: {err}"
                    batch_proposals.append((i, proposal))

            for i, proposal in batch_proposals:
                batch_file = output_dir / f"batch_{i+1:03d}_proposal.md"
                batch_file.write_text(proposal, encoding="utf-8")

            batch_proposals = [s for _, s in sorted(batch_proposals)]

        elif cfg.workers <= 1:
            for i, batch in enumerate(batches):
                if i in existing_batches:
                    proposal = existing_batches[i].read_text(encoding="utf-8")
                    print(f"Loaded existing proposal for batch {i+1}/{len(batches)}")
                else:
                    proposal = generate_batch_proposal(
                        batch, i + 1, len(batches), base_lib_docs,
                        cfg.model, cfg.temperature, cfg.max_tokens,
                        getattr(cfg, "thinking_effort", None), getattr(cfg, "thinking_level", None),
                        getattr(cfg, "request_timeout", 300),
                    )
                    batch_file = output_dir / f"batch_{i+1:03d}_proposal.md"
                    batch_file.write_text(proposal, encoding="utf-8")
                batch_proposals.append(proposal)
        else:
            # Load existing proposals and only submit missing ones
            pending_batches = {
                i: batch for i, batch in enumerate(batches)
                if i not in existing_batches
            }

            results_map = {}
            for idx, bf in existing_batches.items():
                results_map[idx] = bf.read_text(encoding="utf-8")
                print(f"Loaded existing proposal for batch {idx+1}/{len(batches)}")

            if pending_batches:
                with ThreadPoolExecutor(max_workers=cfg.workers) as executor:
                    futures = {
                        executor.submit(
                            generate_batch_proposal, batch, i + 1, len(batches),
                            base_lib_docs, cfg.model, cfg.temperature, cfg.max_tokens,
                            getattr(cfg, "thinking_effort", None), getattr(cfg, "thinking_level", None),
                            getattr(cfg, "request_timeout", 300),
                        ): i
                        for i, batch in pending_batches.items()
                    }

                    for future in as_completed(futures):
                        i = futures[future]
                        try:
                            proposal = future.result()
                            results_map[i] = proposal

                            batch_file = output_dir / f"batch_{i+1:03d}_proposal.md"
                            batch_file.write_text(proposal, encoding="utf-8")
                        except Exception as exc:
                            print(f"Batch {i+1} failed: {exc}")
                            results_map[i] = f"ERROR: {exc}"

            batch_proposals = [results_map[i] for i in sorted(results_map)]

        print(f"\n✓ Generated {len(batch_proposals)} batch proposals\n")

        num_batch_proposals = len(batch_proposals)
        num_batches = len(batches)

        # Step 2: Merge all batch proposals
        print("STEP 2: Merge & Deduplicate")
        print("-" * 70)

        merged_proposal = "\n\n---\n\n".join(
            f"# Batch {i+1} Proposal\n{proposal}"
            for i, proposal in enumerate(batch_proposals)
        )

        merged_file.write_text(merged_proposal, encoding="utf-8")
        print(f"Merged {len(batch_proposals)} proposals\n")

    # Step 3: Deduplicate
    if getattr(cfg, "batch", False):
        import sys

        gpt_dir = Path(__file__).parent.parent
        if str(gpt_dir) not in sys.path:
            sys.path.insert(0, str(gpt_dir))

        from llm_wrapper import (
            _is_gemini_model,
            build_openai_messages,
            build_openai_request_body,
            submit_openai_batch,
            poll_openai_batch,
            parse_batch_results,
            build_gemini_batch_request,
            submit_gemini_batch,
            poll_gemini_batch,
            parse_gemini_batch_results,
        )

        dedup_system_prompt = "You are a programming language designer reviewing an API proposal for redundancy."
        dedup_prompt = _build_dedup_prompt(merged_proposal)
        is_gemini = _is_gemini_model(cfg.model)
        poll_interval = getattr(cfg, "batch_poll_interval", 60)
        batch_timeout = getattr(cfg, "batch_timeout", 86400)

        print("Submitting deduplication via Batch API...")

        if is_gemini:
            dedup_request = build_gemini_batch_request(
                prompt=dedup_prompt,
                system_prompt=dedup_system_prompt,
                temperature=cfg.temperature,
                max_tokens=cfg.max_tokens,
                thinking_level=getattr(cfg, "thinking_level", None),
            )
            display_name = f"{cfg.experiment_name}-stage1-dedup-{cfg.model}"
            job_name = submit_gemini_batch([dedup_request], cfg.model, display_name)
            print(f"Created Gemini dedup batch: {job_name}")
            batch_job = poll_gemini_batch(job_name, poll_interval, batch_timeout)

            dedup_results = parse_gemini_batch_results(batch_job, [dedup_request])
            result_0 = dedup_results.get(0)
            if result_0 and not result_0.get("error"):
                final_api = result_0["text"]
            else:
                err = (result_0 or {}).get("error", "unknown error")
                raise RuntimeError(f"Deduplication batch failed: {err}")
        else:
            dedup_messages = build_openai_messages(prompt=dedup_prompt, system_prompt=dedup_system_prompt)
            dedup_body = build_openai_request_body(
                messages=dedup_messages,
                model=cfg.model,
                temperature=cfg.temperature,
                max_tokens=cfg.max_tokens,
                reasoning_effort=getattr(cfg, "thinking_effort", None),
            )
            jsonl_lines = [json.dumps({
                "custom_id": "dedup_0",
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": dedup_body,
            })]
            batch_id = submit_openai_batch(jsonl_lines)
            print(f"Created OpenAI dedup batch: {batch_id}")
            batch_obj = poll_openai_batch(batch_id, poll_interval, batch_timeout)

            dedup_results = {}
            if batch_obj.output_file_id:
                dedup_results.update(parse_batch_results(batch_obj.output_file_id))
            if batch_obj.error_file_id:
                dedup_results.update(parse_batch_results(batch_obj.error_file_id))

            result_0 = dedup_results.get("dedup_0")
            if result_0 and not result_0.get("error"):
                final_api = result_0["text"]
            else:
                err = (result_0 or {}).get("error", "unknown error")
                raise RuntimeError(f"Deduplication batch failed: {err}")

        print("✓ Deduplication batch completed")
    else:
        final_api = deduplicate_api_proposal(
            api_proposal=merged_proposal,
            model=cfg.model,
            temperature=cfg.temperature,
            max_tokens=cfg.max_tokens,
            thinking_effort=getattr(cfg, "thinking_effort", None),
            thinking_level=getattr(cfg, "thinking_level", None),
            request_timeout=getattr(cfg, "request_timeout", 300),
        )

    api_file = output_dir / "api_proposal_v1.md"
    api_file.write_text(final_api, encoding="utf-8")
    print(f"\n✓ Deduplicated API proposal saved to: {api_file}\n")

    # Create summary
    result = {
        "stage": 1,
        "timestamp": timestamp(),
        "config": {
            "train_data": cfg.train_data,
            "base_lib_docs": cfg.base_lib_docs,
            "total_instructions": len(all_instructions),
            "batch_size": cfg.batch_size,
            "num_batches": num_batches,
            "model": cfg.model,
            "include_io": include_io,
            "semantic_batching": getattr(cfg, "semantic_batching", False),
            "embedding_model": (
                getattr(cfg, "embedding_model", None)
                if getattr(cfg, "semantic_batching", False)
                else None
            ),
        },
        "outputs": {
            "batch_proposals": num_batch_proposals,
            "merged_proposal": str(merged_file),
            "api_proposal": str(api_file),
        },
    }

    stage_summary_file = output_dir / "stage1_summary.json"
    save_json(result, stage_summary_file)

    print(f"{'='*70}")
    print("STAGE 1 COMPLETE")
    print(f"{'='*70}\n")
    print(f"Analyzed: {len(all_instructions)} instructions")
    print(f"Batches: {num_batches}")
    print(f"API Proposal: {api_file}")
    print()

    return result


if __name__ == "__main__":
    from config import parse_args

    cfg = parse_args()

    output_dir = Path(cfg.output_dir) / cfg.experiment_name / "stage1"
    output_dir.mkdir(parents=True, exist_ok=True)

    run_stage1(cfg, output_dir)
