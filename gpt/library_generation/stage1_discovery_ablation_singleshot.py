"""Stage 1 Ablation: Single-shot API discovery (no hierarchical batching).

This ablation variant analyzes ALL instructions in a single LLM call instead of
using hierarchical batch analysis. This tests whether the hierarchical approach
provides benefits over a simpler single-pass approach.

Key differences from standard Stage 1:
- NO batch analysis
- NO meta-summaries
- NO hierarchical synthesis
- Single LLM call with all instructions → pattern summary
- Single LLM call for pattern summary → API proposal

This is faster but may struggle with large datasets due to context limits.
"""

from __future__ import annotations

import json
import argparse
from pathlib import Path
from typing import List, Dict, Union, Any, Optional


def load_base_library_docs(docs_path: str) -> str:
    """Load base library API documentation."""
    docs_file = Path(docs_path)
    if not docs_file.exists():
        raise FileNotFoundError(f"Base library docs not found: {docs_path}")
    return docs_file.read_text(encoding="utf-8")


def load_all_instructions(data_path: str, include_io: bool = False) -> List[Union[str, Dict[str, Any]]]:
    """Load all instructions from a standardized JSONL dataset."""
    instructions: List[Union[str, Dict[str, Any]]] = []
    data_file = Path(data_path)

    if not data_file.exists():
        raise FileNotFoundError(f"Training data file not found: {data_path}")

    with open(data_file, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            try:
                obj = json.loads(line)

                if "task_id" not in obj or "steps" not in obj:
                    print(f"Warning: Line {line_num} missing required fields")
                    continue

                for step in obj["steps"]:
                    if "instruction" not in step:
                        continue
                    instruction = step["instruction"]
                    if instruction:
                        if include_io:
                            instructions.append({
                                "instruction": instruction,
                                "output_state": step.get("output_state", []),
                            })
                        else:
                            instructions.append(instruction)

            except json.JSONDecodeError as e:
                print(f"Warning: Invalid JSON on line {line_num}: {e}")
            except Exception as e:
                print(f"Warning: Error processing line {line_num}: {e}")

    return instructions


def _format_state(state: List[Any]) -> str:
    """Format a board state compactly, showing only non-zero (colored) tiles."""
    if not state:
        return "[]"
    non_zero = [(idx, val) for idx, val in enumerate(state) if val != 0]
    if not non_zero:
        return "[all blank]"
    return str(non_zero)


def format_instructions(instructions: List[Union[str, Dict[str, Any]]], max_display: Optional[int] = None) -> str:
    """Format instructions for display.

    Handles both plain strings and dicts with instruction and output_state.

    Args:
        instructions: List of instruction strings or dicts
        max_display: Maximum number to display (None = all)

    Returns:
        Formatted string
    """
    to_display = instructions[:max_display] if max_display is not None else instructions
    lines = []
    for i, item in enumerate(to_display):
        if isinstance(item, dict):
            line = f"{i+1}. Instruction: {item['instruction']}"
            line += f"\n   Output state: {_format_state(item.get('output_state', []))}"
        else:
            line = f"{i+1}. {item}"
        lines.append(line)
    formatted = "\n".join(lines)

    if max_display is not None and len(instructions) > max_display:
        formatted += f"\n... ({len(instructions) - max_display} more instructions)"

    return formatted


def analyze_all_instructions_single_shot(
    instructions: List[Union[str, Dict[str, Any]]],
    base_lib_docs: str,
    model: str,
    temperature: float,
    max_tokens: int | None,
    thinking_effort: str | None = None,
    thinking_level: str | None = None,
) -> str:
    """Analyze ALL instructions in a single LLM call.

    Args:
        instructions: All instruction strings
        base_lib_docs: Base library API documentation
        model: LLM model name
        temperature: LLM temperature
        max_tokens: Max tokens for response

    Returns:
        Pattern summary
    """
    from gpt.llm_wrapper import call_llm

    system_prompt = "You are a programming language designer analyzing patterns to identify what merits abstraction."

    io_note = ""
    if instructions and isinstance(instructions[0], dict):
        io_note = ("\nEach instruction includes its output state (board after). "
                   "Non-zero values represent colored tiles. Use these to understand the transformations.\n")

    prompt = f"""You have a minimal base library:

{base_lib_docs}

Analyze ALL {len(instructions)} instructions to find patterns that justify new abstractions:
{io_note}
{format_instructions(instructions)}

Provide a comprehensive analysis of patterns. Be thorough since you're seeing the entire dataset at once.

OUTPUT FORMAT:
## Complex Patterns Found
- [Pattern name]: [Brief description + frequency estimate across {len(instructions)} instructions]
- [Pattern name]: [Brief description + frequency estimate]

## Potential Abstractions
For each abstraction:
- Operation: [What it does]
- Justification: [Why it's complex enough to abstract]
- Frequency: [Rough estimate: high (>30%), medium (10-30%), low (<10%)]

CRITERIA - Only identify abstractions that meet ALL:
- Involves non-trivial algorithms or domain-specific logic
- Requires knowledge of internal data structures or complex rules
- Would be error-prone if users implemented it themselves
- Appears frequently enough to justify abstraction

Skip: simple property access, collection builders, thin wrappers

CRITICAL: Ask for each candidate - "Does this solve a genuinely complex problem?"

Be comprehensive - you're seeing the ENTIRE dataset at once."""

    print(f"Analyzing all {len(instructions)} instructions in single shot...")

    response = call_llm(
        prompt=prompt,
        system_prompt=system_prompt,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        reasoning_effort=thinking_effort,
        thinking_level=thinking_level,
    )

    return response["text"]


def generate_api_proposal(
    pattern_summary: str,
    base_lib_docs: str,
    model: str,
    temperature: float,
    max_tokens: int | None,
    thinking_effort: str | None = None,
    thinking_level: str | None = None,
) -> str:
    """Generate API proposal from pattern summary.

    Args:
        pattern_summary: Summary of all patterns
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

{pattern_summary}

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
        reasoning_effort=thinking_effort,
        thinking_level=thinking_level,
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


def _min_batches(prompt_tokens: int, context_length: int) -> int:
    """Return the minimum number of batches needed.

    Args:
        prompt_tokens: Total prompt token count for all instructions.
        context_length: Model context window size in tokens.

    Each batch has its own system prompt / template overhead (~2000 tokens).
    """
    import math

    PER_BATCH_OVERHEAD = 2000  # system prompt + template chrome added per batch
    available_per_batch = context_length - PER_BATCH_OVERHEAD
    if available_per_batch <= 0 or prompt_tokens <= available_per_batch:
        return 1
    return math.ceil(prompt_tokens / available_per_batch)


def run_stage1_singleshot(cfg: argparse.Namespace, output_dir: Path) -> Dict[str, Any]:
    """Run Stage 1 Ablation: Single-shot API Discovery.

    Requires --max-tokens. When --context-length is also provided, uses it
    to determine the minimum number of batches needed to fit all instructions.
    When multiple batches are needed, reuses the standard Stage 1
    batch→merge→deduplicate pipeline.

    Args:
        cfg: Configuration namespace
        output_dir: Directory to save outputs
    Returns:
        Dictionary with stage results
    """

    print(f"\n{'='*70}")
    print("STAGE 1 ABLATION: SINGLE-SHOT API DISCOVERY")
    print("(No hierarchical batching)")
    print(f"{'='*70}\n")

    # Load base library documentation
    print(f"Loading base library docs from {cfg.base_lib_docs}...")
    base_lib_docs = load_base_library_docs(cfg.base_lib_docs)
    print(f"✓ Loaded {len(base_lib_docs)} characters\n")

    # Load all instructions
    include_io = getattr(cfg, 'include_io', False)
    print(f"Loading instructions from {cfg.train_data}...")
    if include_io:
        print("  (including input/output states)")
    all_instructions = load_all_instructions(cfg.train_data, include_io=include_io)
    print(f"✓ Loaded {len(all_instructions)} instructions\n")

    # Determine batch count: only batch when both --prompt-tokens and --context-length are provided
    prompt_tokens = getattr(cfg, "prompt_tokens", None)
    context_length = getattr(cfg, "context_length", None)
    if prompt_tokens and context_length:
        n_batches = _min_batches(prompt_tokens, context_length)
        print(f"Prompt: {prompt_tokens} tokens, model context: {context_length} → {n_batches} batch(es)\n")
    else:
        n_batches = 1

    thinking_kwargs = dict(
        thinking_effort=getattr(cfg, "thinking_effort", None),
        thinking_level=getattr(cfg, "thinking_level", None),
    )

    if n_batches == 1:
        # Everything fits — true single-shot: pattern analysis → API proposal
        print("SINGLE-SHOT ANALYSIS")
        print("-" * 70)

        pattern_summary = analyze_all_instructions_single_shot(
            instructions=all_instructions,
            base_lib_docs=base_lib_docs,
            model=cfg.model,
            temperature=cfg.temperature,
            max_tokens=cfg.max_tokens,
            **thinking_kwargs,
        )

        summary_file = output_dir / "pattern_summary_singleshot.md"
        summary_file.write_text(pattern_summary, encoding="utf-8")
        print(f"\n✓ Pattern summary saved to: {summary_file}\n")

        print("API PROPOSAL GENERATION")
        print("-" * 70)

        api_proposal = generate_api_proposal(
            pattern_summary=pattern_summary,
            base_lib_docs=base_lib_docs,
            model=cfg.model,
            temperature=cfg.temperature,
            max_tokens=cfg.max_tokens,
            **thinking_kwargs,
        )

        api_file = output_dir / "api_proposal_v1.md"
        api_file.write_text(api_proposal, encoding="utf-8")
        print(f"\n✓ API proposal saved to: {api_file}\n")
    else:
        # Too large for one call — split into minimal batches and reuse
        # the standard Stage 1 batch→merge→deduplicate pipeline
        import math
        from stage1_discovery import (
            chunk_list,
            generate_batch_proposal,
            deduplicate_api_proposal,
        )

        batch_size = math.ceil(len(all_instructions) / n_batches)
        batches = chunk_list(all_instructions, batch_size)

        print(f"BATCH PROPOSAL GENERATION ({len(batches)} batches of ~{batch_size})")
        print("-" * 70)

        batch_proposals = []
        for i, batch in enumerate(batches):
            proposal = generate_batch_proposal(
                batch, i + 1, len(batches), base_lib_docs,
                cfg.model, cfg.temperature, cfg.max_tokens,
                thinking_kwargs["thinking_effort"],
                thinking_kwargs["thinking_level"],
                getattr(cfg, "request_timeout", 300),
            )
            batch_file = output_dir / f"batch_{i+1:03d}_proposal.md"
            batch_file.write_text(proposal, encoding="utf-8")
            batch_proposals.append(proposal)

        print(f"\n✓ Generated {len(batch_proposals)} batch proposals\n")

        # Merge
        merged_proposal = "\n\n---\n\n".join(
            f"# Batch {i+1} Proposal\n{proposal}"
            for i, proposal in enumerate(batch_proposals)
        )
        merged_file = output_dir / "api_proposal_merged.md"
        merged_file.write_text(merged_proposal, encoding="utf-8")

        # Deduplicate
        print("DEDUPLICATION")
        print("-" * 70)

        api_proposal = deduplicate_api_proposal(
            api_proposal=merged_proposal,
            model=cfg.model,
            temperature=cfg.temperature,
            max_tokens=cfg.max_tokens,
            thinking_effort=thinking_kwargs["thinking_effort"],
            thinking_level=thinking_kwargs["thinking_level"],
            request_timeout=getattr(cfg, "request_timeout", 300),
        )

        api_file = output_dir / "api_proposal_v1.md"
        api_file.write_text(api_proposal, encoding="utf-8")
        print(f"\n✓ Deduplicated API proposal saved to: {api_file}\n")

    # Create summary
    result = {
        "stage": 1,
        "ablation": "singleshot",
        "timestamp": timestamp(),
        "config": {
            "train_data": cfg.train_data,
            "base_lib_docs": cfg.base_lib_docs,
            "total_instructions": len(all_instructions),
            "model": cfg.model,
            "include_io": include_io,
            "hierarchical_batching": False,
            "max_tokens": cfg.max_tokens,
            "n_batches": n_batches,
        },
        "outputs": {
            "api_proposal": str(output_dir / "api_proposal_v1.md"),
        },
    }

    stage_summary_file = output_dir / "stage1_summary.json"
    save_json(result, stage_summary_file)

    print(f"{'='*70}")
    print("STAGE 1 ABLATION COMPLETE")
    print(f"{'='*70}\n")
    print(f"Analyzed: {len(all_instructions)} instructions "
          f"({'single-shot' if n_batches == 1 else f'{n_batches} batches'})")
    print(f"API Proposal: {output_dir / 'api_proposal_v1.md'}")
    print()

    return result


if __name__ == "__main__":
    from config import parse_args

    cfg = parse_args()

    # Create output directory with ablation marker
    output_dir = (
        Path(cfg.output_dir) / f"{cfg.experiment_name}_ablation_singleshot" / "stage1"
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    run_stage1_singleshot(cfg, output_dir)
