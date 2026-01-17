"""Stage 2: API Refinement through iterative validation.

This stage takes the API proposal from Stage 1 and refines it by:
1. Testing the API with different sample subsets
2. Identifying gaps, redundancies, and improvements
3. Generating refined versions through multiple iterations

DOMAIN-AGNOSTIC: Works with any dataset in standard format.
"""

from __future__ import annotations

import json
import argparse
from pathlib import Path
from typing import List, Dict
import random


def load_api_proposal(api_file: Path) -> str:
    """Load API proposal from Stage 1."""
    if not api_file.exists():
        raise FileNotFoundError(f"API proposal not found: {api_file}")
    return api_file.read_text(encoding="utf-8")


def load_sample_instructions(data_path: str, num_samples: int, seed: int = 42) -> List[str]:
    """Load a random sample of instructions from the dataset.

    Args:
        data_path: Path to standardized JSONL file
        num_samples: Number of instructions to sample
        seed: Random seed for reproducibility

    Returns:
        List of sampled instruction strings
    """
    random.seed(seed)

    all_instructions = []
    data_file = Path(data_path)

    with open(data_file, "r", encoding="utf-8") as f:
        for line in f:
            obj = json.loads(line)
            for step in obj["steps"]:
                all_instructions.append(step["instruction"])

    # Sample without replacement
    sample_size = min(num_samples, len(all_instructions))
    return random.sample(all_instructions, sample_size)


def refine_api(
    api_proposal: str,
    sample_instructions: List[str],
    base_lib_docs: str,
    iteration: int,
    model: str,
    temperature: float,
    max_tokens: int
) -> str:
    """Refine the API proposal based on a sample of instructions.

    Args:
        api_proposal: Current API proposal
        sample_instructions: Sample instructions to test against
        base_lib_docs: Base library documentation
        iteration: Current iteration number
        model: LLM model name
        temperature: LLM temperature
        max_tokens: Max tokens for response

    Returns:
        Refined API proposal
    """
    from gpt.llm_wrapper import call_llm

    instructions_text = "\n".join(f"{i+1}. {instr}" for i, instr in enumerate(sample_instructions))

    system_prompt = "You are a programming language designer refining an API based on real usage patterns."

    prompt = f"""Refine this API proposal using sample instructions as test cases.

CURRENT API (Iteration {iteration}):
{api_proposal}

FOUNDATION LIBRARY:
{base_lib_docs}

TEST INSTRUCTIONS ({len(sample_instructions)} samples):
{instructions_text}

OUTPUT FORMAT:
```
## Changes in Iteration {iteration + 1}
- Added: [method name] - [why needed for these instructions]
- Removed: [method name] - [why not needed]
- Modified: [method name] - [what changed and why]

Class: ClassName
  Method: method_name(param: type) -> ReturnType
    Description: [1 sentence]
    Rationale: [Problem solved + which instructions need this]
    Necessity: [Why needed vs composing existing methods]
```

REFINEMENT CRITERIA:
Test each method against sample instructions:

ADD if:
- Sample instructions reveal missing complex capability
- Current API can't elegantly express these patterns

REMOVE if:
- No sample instructions actually need this method
- Trivial to compose from existing methods
- Too abstract - unclear what it does

MODIFY if:
- Parameters don't match actual instruction patterns
- Method scope too broad or too narrow

Quality > Quantity. Focus on minimal, powerful API."""

    print(f"Refining API (iteration {iteration}) with {len(sample_instructions)} test instructions...")

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


def run_stage2(cfg: argparse.Namespace, output_dir: Path, stage1_result: Dict) -> Dict:
    """Run Stage 2: API Refinement.

    Args:
        cfg: Configuration namespace
        output_dir: Directory to save outputs
        stage1_result: Results from Stage 1

    Returns:
        Dictionary with stage results
    """
    print(f"\n{'='*70}")
    print("STAGE 2: API REFINEMENT")
    print(f"{'='*70}\n")

    # Load Stage 1 API proposal
    stage1_api_file = Path(stage1_result["outputs"]["api_proposal"])
    print(f"Loading Stage 1 API proposal from {stage1_api_file}...")
    api_proposal = load_api_proposal(stage1_api_file)
    print(f"✓ Loaded API proposal\n")

    # Load base library docs
    print(f"Loading base library docs from {cfg.base_lib_docs}...")
    base_lib_docs = Path(cfg.base_lib_docs).read_text(encoding="utf-8")
    print(f"✓ Loaded base library docs\n")

    # Refinement iterations
    print(f"Running {cfg.refinement_iterations} refinement iterations")
    print("-" * 70)

    current_api = api_proposal
    refinement_history = []

    for i in range(cfg.refinement_iterations):
        # Sample different instructions each iteration
        sample_seed = cfg.seed + i
        sample_instructions = load_sample_instructions(
            cfg.train_data,
            num_samples=50,  # Sample 50 instructions per iteration
            seed=sample_seed
        )

        print(f"\nIteration {i+1}/{cfg.refinement_iterations}")
        print(f"  Sampled {len(sample_instructions)} instructions (seed={sample_seed})")

        # Refine API
        refined_api = refine_api(
            api_proposal=current_api,
            sample_instructions=sample_instructions,
            base_lib_docs=base_lib_docs,
            iteration=i,
            model=cfg.model,
            temperature=cfg.temperature,
            max_tokens=cfg.max_tokens * 2  # Give more tokens for refinement
        )

        # Save refined version
        refined_file = output_dir / f"api_proposal_v{i+2}.md"
        refined_file.write_text(refined_api, encoding='utf-8')
        print(f"  ✓ Saved refined API to {refined_file}")

        refinement_history.append({
            "iteration": i + 1,
            "sample_seed": sample_seed,
            "num_samples": len(sample_instructions),
            "output_file": str(refined_file)
        })

        current_api = refined_api

    # Save final version
    final_file = output_dir / "api_proposal_final.md"
    final_file.write_text(current_api, encoding='utf-8')
    print(f"\n✓ Final API proposal saved to {final_file}\n")

    # Create summary
    result = {
        "stage": 2,
        "timestamp": timestamp(),
        "config": {
            "train_data": cfg.train_data,
            "base_lib_docs": cfg.base_lib_docs,
            "refinement_iterations": cfg.refinement_iterations,
            "model": cfg.model,
        },
        "outputs": {
            "initial_api": str(stage1_api_file),
            "final_api": str(final_file),
            "refinement_history": refinement_history
        }
    }

    # Save stage summary
    summary_file = output_dir / "stage2_summary.json"
    save_json(result, summary_file)

    print(f"{'='*70}")
    print("STAGE 2 COMPLETE")
    print(f"{'='*70}\n")
    print(f"Iterations: {cfg.refinement_iterations}")
    print(f"Final API: {final_file}")
    print()

    return result


if __name__ == "__main__":
    from config import parse_args
    import sys

    cfg = parse_args()

    # Load Stage 1 results
    stage1_dir = Path(cfg.output_dir) / cfg.experiment_name / "stage1"
    stage1_summary = stage1_dir / "stage1_summary.json"

    if not stage1_summary.exists():
        print(f"Error: Stage 1 results not found at {stage1_summary}")
        print("Please run Stage 1 first!")
        sys.exit(1)

    with open(stage1_summary) as f:
        stage1_result = json.load(f)

    # Create output directory
    output_dir = Path(cfg.output_dir) / cfg.experiment_name / "stage2"
    output_dir.mkdir(parents=True, exist_ok=True)

    run_stage2(cfg, output_dir, stage1_result)
