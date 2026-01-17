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
from typing import List, Dict


def load_base_library_docs(docs_path: str) -> str:
    """Load base library API documentation."""
    docs_file = Path(docs_path)
    if not docs_file.exists():
        raise FileNotFoundError(f"Base library docs not found: {docs_path}")
    return docs_file.read_text(encoding="utf-8")


def load_all_instructions(data_path: str) -> List[str]:
    """Load all instructions from a standardized JSONL dataset."""
    instructions = []
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
                        instructions.append(instruction)

            except json.JSONDecodeError as e:
                print(f"Warning: Invalid JSON on line {line_num}: {e}")
            except Exception as e:
                print(f"Warning: Error processing line {line_num}: {e}")

    return instructions


def format_instructions(instructions: List[str], max_display: int = None) -> str:
    """Format instructions for display.

    Args:
        instructions: List of instruction strings
        max_display: Maximum number to display (None = all)

    Returns:
        Formatted string
    """
    to_display = instructions[:max_display] if max_display else instructions
    formatted = "\n".join(f"{i+1}. {instr}" for i, instr in enumerate(to_display))

    if max_display and len(instructions) > max_display:
        formatted += f"\n... ({len(instructions) - max_display} more instructions)"

    return formatted


def analyze_all_instructions_single_shot(
    instructions: List[str],
    base_lib_docs: str,
    model: str,
    temperature: float,
    max_tokens: int,
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

    # For very large datasets, we sample to fit in context
    # Most models can handle ~100k tokens input, so we'll cap at reasonable size
    MAX_INSTRUCTIONS = 10000  # Adjust based on model context window

    if len(instructions) > MAX_INSTRUCTIONS:
        print(f"⚠ Warning: Dataset has {len(instructions)} instructions")
        print(f"  Sampling {MAX_INSTRUCTIONS} for single-shot analysis")
        import random

        random.seed(42)
        sampled = random.sample(instructions, MAX_INSTRUCTIONS)
    else:
        sampled = instructions

    prompt = f"""You have a minimal base library:

{base_lib_docs}

Analyze ALL {len(sampled)} instructions to find patterns that justify new abstractions:

{format_instructions(sampled)}

Provide a comprehensive analysis of patterns. Be thorough since you're seeing the entire dataset at once.

OUTPUT FORMAT:
## Complex Patterns Found
- [Pattern name]: [Brief description + frequency estimate across {len(sampled)} instructions]
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

    print(f"Analyzing all {len(sampled)} instructions in single shot...")

    response = call_llm(
        prompt=prompt,
        system_prompt=system_prompt,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens * 4,  # 4x tokens for comprehensive single-shot analysis
    )

    return response["text"]


def generate_api_proposal(
    pattern_summary: str,
    base_lib_docs: str,
    model: str,
    temperature: float,
    max_tokens: int,
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
        max_tokens=max_tokens * 2,
    )

    return response["text"]


def save_json(data: Dict, path: Path):
    """Save JSON data to file."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def timestamp() -> str:
    """Generate timestamp string."""
    from datetime import datetime

    return datetime.now().strftime("%Y-%m-%dT%H-%M-%S")


def run_stage1_singleshot(cfg: argparse.Namespace, output_dir: Path) -> Dict:
    """Run Stage 1 Ablation: Single-shot API Discovery.

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
    print(f"Loading instructions from {cfg.train_data}...")
    all_instructions = load_all_instructions(cfg.train_data)
    print(f"✓ Loaded {len(all_instructions)} instructions\n")

    # Single-shot pattern analysis
    print("SINGLE-SHOT ANALYSIS")
    print("-" * 70)

    pattern_summary = analyze_all_instructions_single_shot(
        instructions=all_instructions,
        base_lib_docs=base_lib_docs,
        model=cfg.model,
        temperature=cfg.temperature,
        max_tokens=cfg.max_tokens,
    )

    # Save pattern summary
    summary_file = output_dir / "pattern_summary_singleshot.md"
    summary_file.write_text(pattern_summary, encoding="utf-8")
    print(f"\n✓ Pattern summary saved to: {summary_file}\n")

    # API Proposal Generation
    print("API PROPOSAL GENERATION")
    print("-" * 70)

    api_proposal = generate_api_proposal(
        pattern_summary=pattern_summary,
        base_lib_docs=base_lib_docs,
        model=cfg.model,
        temperature=cfg.temperature,
        max_tokens=cfg.max_tokens,
    )

    # Save API proposal
    api_file = output_dir / "api_proposal_v1.md"
    api_file.write_text(api_proposal, encoding="utf-8")
    print(f"\n✓ API proposal saved to: {api_file}\n")

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
            "hierarchical_batching": False,
        },
        "outputs": {
            "pattern_summary": str(summary_file),
            "api_proposal": str(api_file),
        },
    }

    # Save stage summary
    stage_summary_file = output_dir / "stage1_summary.json"
    save_json(result, stage_summary_file)

    print(f"{'='*70}")
    print("STAGE 1 ABLATION COMPLETE")
    print(f"{'='*70}\n")
    print(f"Analyzed: {len(all_instructions)} instructions (single-shot)")
    print(f"API Proposal: {api_file}")
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
