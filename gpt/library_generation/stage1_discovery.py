"""Stage 1: API Discovery through hierarchical batch analysis.

This stage analyzes the entire training set using a hierarchical approach:
1. Split instructions into batches
2. Analyze each batch to find patterns
3. Summarize batch summaries into meta-summaries (if many batches)
4. Synthesize all summaries into a final unified pattern summary
5. Generate API proposal from the final pattern summary

DOMAIN-AGNOSTIC: Works with any dataset in standard format.
See data_format.md for required format.
"""

from __future__ import annotations

import json
import argparse
from pathlib import Path
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed


def load_base_library_docs(docs_path: str) -> str:
    """Load base library API documentation.

    Args:
        docs_path: Path to base library documentation file

    Returns:
        Documentation content as string
    """
    docs_file = Path(docs_path)
    if not docs_file.exists():
        raise FileNotFoundError(f"Base library docs not found: {docs_path}")

    return docs_file.read_text(encoding="utf-8")


def load_all_instructions(data_path: str) -> List[str]:
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

    Returns:
        List of all instruction strings
    """
    instructions = []
    data_file = Path(data_path)

    if not data_file.exists():
        raise FileNotFoundError(f"Training data file not found: {data_path}")

    with open(data_file, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            try:
                obj = json.loads(line)

                # Validate format
                if "task_id" not in obj or "steps" not in obj:
                    print(f"Warning: Line {line_num} missing required fields (task_id, steps)")
                    continue

                # Extract instructions from all steps
                for step in obj["steps"]:
                    if "instruction" not in step:
                        print(f"Warning: Step in task {obj['task_id']} missing instruction")
                        continue

                    instruction = step["instruction"]
                    if instruction:  # Skip empty instructions
                        instructions.append(instruction)

            except json.JSONDecodeError as e:
                print(f"Warning: Invalid JSON on line {line_num}: {e}")
            except Exception as e:
                print(f"Warning: Error processing line {line_num}: {e}")

    return instructions


def chunk_list(lst: List, chunk_size: int) -> List[List]:
    """Split a list into chunks of given size."""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def format_instructions(instructions: List[str]) -> str:
    """Format a list of instructions for display."""
    return "\n".join(f"{i+1}. {instr}" for i, instr in enumerate(instructions))


def analyze_batch(
    batch: List[str],
    batch_num: int,
    total_batches: int,
    base_lib_docs: str,
    model: str,
    temperature: float,
    max_tokens: int
) -> str:
    """Analyze a single batch of instructions.

    Args:
        batch: List of instruction strings
        batch_num: Index of this batch (1-based)
        total_batches: Total number of batches
        base_lib_docs: Base library API documentation
        model: LLM model name
        temperature: LLM temperature
        max_tokens: Max tokens for response

    Returns:
        Summary of patterns found in this batch
    """
    system_prompt = "You are a programming language designer analyzing patterns to identify what merits abstraction."

    prompt = f"""You have a minimal base library:

{base_lib_docs}

Analyze these {len(batch)} instructions to find patterns that justify new abstractions:

{format_instructions(batch)}

OUTPUT FORMAT (max 500 words):
## Complex Patterns Found
- [Pattern name]: [Brief description + frequency estimate]
- [Pattern name]: [Brief description + frequency estimate]

## Potential Abstractions
For each abstraction:
- Operation: [What it does]
- Justification: [Why it's complex enough to abstract]

CRITERIA - Only identify abstractions that meet ALL:
- Involves non-trivial algorithms or domain-specific logic
- Requires knowledge of internal data structures or complex rules
- Would be error-prone if users implemented it themselves

Skip: simple property access, collection builders, thin wrappers

CRITICAL: Ask for each candidate - "Does this solve a genuinely complex problem?"

Focus on observation, not API design yet."""

    print(f"Analyzing batch {batch_num}/{total_batches} ({len(batch)} instructions)...")

    # Import here to avoid circular dependency
    from gpt.llm_wrapper import call_llm

    response = call_llm(
        prompt=prompt,
        system_prompt=system_prompt,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
    )

    return response["text"]


def synthesize_batch_summaries(
    summaries: List[str],
    model: str,
    temperature: float,
    max_tokens: int
) -> str:
    """Synthesize multiple summaries into a higher-level summary.

    Args:
        summaries: List of summary strings to synthesize
        model: LLM model name
        temperature: LLM temperature
        max_tokens: Max tokens for response

    Returns:
        Synthesized summary
    """
    from gpt.llm_wrapper import call_llm

    summaries_text = "\n\n---\n\n".join(
        f"SUMMARY {i+1}:\n{summary}"
        for i, summary in enumerate(summaries)
    )

    system_prompt = "You are a programming language designer synthesizing requirements across diverse use cases."

    prompt = f"""Synthesize {len(summaries)} batch summaries into a unified pattern analysis.

{summaries_text}

OUTPUT FORMAT (max 1000 words):
## Cross-Cutting Patterns (appear in multiple batches)
1. [Pattern]: Appears in [X] summaries - [description] - [frequency: high/medium/low]
2. [Pattern]: Appears in [X] summaries - [description] - [frequency: high/medium/low]

## Essential Abstractions (consensus across batches)
- [Abstraction]: [Why essential] [Which summaries mention it]

## Optional Abstractions (useful but not universal)
- [Abstraction]: [Why useful] [Limited to which contexts]

## Edge Cases (unique to single summary)
- [Pattern]: [Brief note on why it's edge case]

PRIORITIZE:
1. Patterns in MULTIPLE summaries (critical)
2. Consensus patterns (what most agree on)
3. Frequency estimates (how common is each)

Be specific about operations needed - this directly informs API design."""

    print(f"Synthesizing {len(summaries)} summaries into unified pattern summary...")

    response = call_llm(
        prompt=prompt,
        system_prompt=system_prompt,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
    )

    return response["text"]


def generate_api_proposal(
    final_summary: str,
    base_lib_docs: str,
    model: str,
    temperature: float,
    max_tokens: int
) -> str:
    """Generate API proposal from final pattern summary.

    Args:
        final_summary: Comprehensive summary of all patterns
        base_lib_docs: Base library API documentation
        model: LLM model name
        temperature: LLM temperature
        max_tokens: Max tokens for response

    Returns:
        API proposal document
    """
    from gpt.llm_wrapper import call_llm

    system_prompt = "You are a programming language designer creating minimal, powerful APIs from pattern analysis."

    prompt = f"""Design NEW methods to extend this minimal foundation:

{base_lib_docs}

Based on patterns identified across the dataset:

{final_summary}

OUTPUT FORMAT:
```
Class: ClassName
  Method: method_name(param: type) -> ReturnType
    Description: [1 sentence - what it does]
    Rationale: [What problem this solves + pattern frequency from summary]
    Necessity: [Why users need this abstraction]
```

DESIGN CRITERIA:
Each method must:
- Address a complex problem from the pattern analysis
- Be non-trivial - users would struggle to implement correctly

NOT:
- Easily composable from existing methods
- Simple wrapper or utility

Quality > Quantity. Propose only methods meeting all criteria."""

    print("Generating API proposal from pattern summary...")

    response = call_llm(
        prompt=prompt,
        system_prompt=system_prompt,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
    )

    return response["text"]


def save_json(data: Dict, path: Path):
    """Save JSON data to file."""
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def timestamp() -> str:
    """Generate timestamp string."""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%dT%H-%M-%S")


def run_stage1(cfg: argparse.Namespace, output_dir: Path) -> Dict:
    """Run Stage 1: API Discovery.

    Args:
        cfg: Configuration namespace
        output_dir: Directory to save outputs

    Returns:
        Dictionary with stage results
    """
    print(f"\n{'='*70}")
    print("STAGE 1: API DISCOVERY (Hierarchical Analysis)")
    print(f"{'='*70}\n")

    # Load base library documentation
    print(f"Loading base library docs from {cfg.base_lib_docs}...")
    base_lib_docs = load_base_library_docs(cfg.base_lib_docs)
    print(f"✓ Loaded {len(base_lib_docs)} characters\n")

    # Load all instructions
    print(f"Loading instructions from {cfg.train_data}...")
    all_instructions = load_all_instructions(cfg.train_data)
    print(f"✓ Loaded {len(all_instructions)} instructions\n")

    # Level 1: Batch analysis
    print(f"LEVEL 1: Batch Analysis (batch_size={cfg.batch_size})")
    print("-" * 70)
    batches = chunk_list(all_instructions, cfg.batch_size)
    print(f"Split into {len(batches)} batches\n")

    batch_summaries = []

    if cfg.workers <= 1:
        # Sequential processing
        for i, batch in enumerate(batches):
            summary = analyze_batch(
                batch, i+1, len(batches),
                base_lib_docs,
                cfg.model, cfg.temperature, cfg.max_tokens
            )
            batch_summaries.append(summary)

            # Save intermediate results
            batch_file = output_dir / f"batch_{i+1:03d}_summary.txt"
            batch_file.write_text(summary, encoding='utf-8')
    else:
        # Parallel processing
        with ThreadPoolExecutor(max_workers=cfg.workers) as executor:
            futures = {
                executor.submit(
                    analyze_batch, batch, i+1, len(batches),
                    base_lib_docs,
                    cfg.model, cfg.temperature, cfg.max_tokens
                ): i
                for i, batch in enumerate(batches)
            }

            for future in as_completed(futures):
                i = futures[future]
                try:
                    summary = future.result()
                    batch_summaries.append((i, summary))

                    # Save intermediate results
                    batch_file = output_dir / f"batch_{i+1:03d}_summary.txt"
                    batch_file.write_text(summary, encoding='utf-8')
                except Exception as exc:
                    print(f"Batch {i+1} failed: {exc}")
                    batch_summaries.append((i, f"ERROR: {exc}"))

        # Sort by index to maintain order
        batch_summaries = [s for _, s in sorted(batch_summaries)]

    print(f"\n✓ Completed {len(batch_summaries)} batch analyses\n")

    # Level 2: Meta-summaries (if needed)
    if len(batch_summaries) > cfg.meta_batch_size:
        print(f"LEVEL 2: Meta-Summary (meta_batch_size={cfg.meta_batch_size})")
        print("-" * 70)
        meta_batches = chunk_list(batch_summaries, cfg.meta_batch_size)
        print(f"Split into {len(meta_batches)} meta-batches\n")

        meta_summaries = []
        for i, meta_batch in enumerate(meta_batches):
            summary = synthesize_batch_summaries(
                meta_batch,
                model=cfg.model, temperature=cfg.temperature, max_tokens=cfg.max_tokens
            )
            meta_summaries.append(summary)

            # Save intermediate results
            meta_file = output_dir / f"meta_{i+1:03d}_summary.txt"
            meta_file.write_text(summary, encoding='utf-8')

        print(f"\n✓ Completed {len(meta_summaries)} meta-summaries\n")
        synthesis_input = meta_summaries
    else:
        # Skip meta-summary level if we have few batches
        print(f"\nSkipping meta-summary level ({len(batch_summaries)} batches < {cfg.meta_batch_size})\n")
        synthesis_input = batch_summaries

    # Level 3: Final Pattern Synthesis
    print("LEVEL 3: Final Pattern Synthesis")
    print("-" * 70)

    final_summary = synthesize_batch_summaries(
        synthesis_input,
        model=cfg.model, temperature=cfg.temperature, max_tokens=cfg.max_tokens * 2
    )

    # Save final pattern summary
    summary_file = output_dir / "final_pattern_summary.md"
    summary_file.write_text(final_summary, encoding='utf-8')
    print(f"\n✓ Final pattern summary saved to: {summary_file}\n")

    # Level 4: API Proposal Generation
    print("LEVEL 4: API Proposal Generation")
    print("-" * 70)

    final_api = generate_api_proposal(
        final_summary=final_summary,
        base_lib_docs=base_lib_docs,
        model=cfg.model, temperature=cfg.temperature, max_tokens=cfg.max_tokens * 2
    )

    # Save final API proposal
    api_file = output_dir / "api_proposal_v1.md"
    api_file.write_text(final_api, encoding='utf-8')
    print(f"\n✓ Final API proposal saved to: {api_file}\n")

    # Create summary
    result = {
        "stage": 1,
        "timestamp": timestamp(),
        "config": {
            "train_data": cfg.train_data,
            "base_lib_docs": cfg.base_lib_docs,
            "total_instructions": len(all_instructions),
            "batch_size": cfg.batch_size,
            "num_batches": len(batches),
            "meta_batch_size": cfg.meta_batch_size,
            "num_meta_batches": len(synthesis_input) if len(batch_summaries) > cfg.meta_batch_size else 0,
            "model": cfg.model,
        },
        "outputs": {
            "batch_summaries": len(batch_summaries),
            "meta_summaries": len(synthesis_input) if len(batch_summaries) > cfg.meta_batch_size else 0,
            "final_pattern_summary": str(summary_file),
            "api_proposal": str(api_file),
        }
    }

    # Save stage summary
    stage_summary_file = output_dir / "stage1_summary.json"
    save_json(result, stage_summary_file)

    print(f"{'='*70}")
    print("STAGE 1 COMPLETE")
    print(f"{'='*70}\n")
    print(f"Analyzed: {len(all_instructions)} instructions")
    print(f"Batches: {len(batches)}")
    print(f"API Proposal: {api_file}")
    print()

    return result


if __name__ == "__main__":
    from config import parse_args

    cfg = parse_args()

    # Create output directory
    output_dir = Path(cfg.output_dir) / cfg.experiment_name / "stage1"
    output_dir.mkdir(parents=True, exist_ok=True)

    run_stage1(cfg, output_dir)
