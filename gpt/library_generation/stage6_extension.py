"""Stage 6: Error-Driven Extension.

This stage iteratively improves the library based on validation failures:
1. Analyze failure patterns from Stage 5
2. Identify missing or problematic API methods
3. Generate improved implementation
4. Re-validate
5. Repeat until success rate plateaus or max cycles reached

DOMAIN-AGNOSTIC: Works with any generated library.
"""

from __future__ import annotations

import json
import argparse
from pathlib import Path
from typing import Dict, List


def load_validation_results(validation_file: Path) -> List[Dict]:
    """Load validation results from Stage 5."""
    if not validation_file.exists():
        raise FileNotFoundError(f"Validation results not found: {validation_file}")

    with open(validation_file) as f:
        return json.load(f)


def analyze_error_patterns(
    validation_results: List[Dict],
    current_implementation: str,
    user_message: str,
    model: str,
    temperature: float,
    max_tokens: int
) -> str:
    """Analyze validation failures to identify API gaps.

    Args:
        validation_results: Validation results from Stage 5
        current_implementation: Current library implementation
        user_message: Current user documentation
        model: LLM model name
        temperature: LLM temperature
        max_tokens: Max tokens for response

    Returns:
        Analysis of what's missing or broken in the API
    """
    from gpt.llm_wrapper import call_llm

    # Extract failures
    failures = [r for r in validation_results if not r["success"]]

    if not failures:
        return "No failures to analyze - library is working well!"

    # Prepare failure examples
    failure_examples = []
    for i, failure in enumerate(failures[:10]):  # Analyze first 10 failures
        example = f"""
Failure {i+1}:
Task: {failure['task_id']}
Instructions: {failure.get('num_steps', 0)} steps
Error: {failure.get('error', 'Unknown error')}
Generated code:
{failure.get('generated_code', 'N/A')}
"""
        failure_examples.append(example)

    failures_text = "\n".join(failure_examples)

    prompt = f"""You are analyzing failures in a generated Python library to identify API gaps and issues.

CURRENT LIBRARY IMPLEMENTATION:
```python
{current_implementation}
```

CURRENT DOCUMENTATION:
{user_message}

VALIDATION FAILURES ({len(failures)} total, showing first 10):
{failures_text}

Your task: Analyze these failures and identify what's missing or broken in the API.

Consider:
1. **Missing methods**: Are there common operations that the library doesn't support?
2. **Incorrect implementations**: Are existing methods buggy or poorly designed?
3. **Unclear documentation**: Are users misunderstanding how to use the library?
4. **Edge cases**: Are there boundary conditions not handled properly?
5. **API design issues**: Are methods hard to use or compose?

Provide a structured analysis:

## Failure Patterns
[Describe the main categories of failures]

## Root Causes
[Identify the underlying issues causing failures]

## Missing Functionality
[List specific methods or features that should be added]

## Implementation Issues
[Describe bugs or problems in existing methods]

## Recommendations
[Prioritized list of changes to improve the library]

Be specific and actionable."""

    system_prompt = "You are an expert software engineer debugging and improving APIs."

    print(f"Analyzing {len(failures)} failures to identify API gaps...")

    response = call_llm(
        prompt=prompt,
        system_prompt=system_prompt,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
    )

    return response["text"]


def extend_implementation(
    current_implementation: str,
    error_analysis: str,
    base_lib_docs: str,
    model: str,
    temperature: float,
    max_tokens: int
) -> str:
    """Generate improved implementation based on error analysis.

    Args:
        current_implementation: Current library code
        error_analysis: Analysis of failures
        base_lib_docs: Base library documentation
        model: LLM model name
        temperature: LLM temperature
        max_tokens: Max tokens for response

    Returns:
        Improved library implementation
    """
    from gpt.llm_wrapper import call_llm

    prompt = f"""You are improving a Python library based on failure analysis.

CURRENT IMPLEMENTATION:
```python
{current_implementation}
```

ERROR ANALYSIS:
{error_analysis}

BASE LIBRARY DOCUMENTATION:
{base_lib_docs}

Your task: Generate an improved version of the library that addresses the identified issues.

Requirements:
1. **Fix identified bugs**: Correct any implementation errors
2. **Add missing methods**: Implement recommended new methods
3. **Improve existing methods**: Enhance methods that are problematic
4. **Maintain compatibility**: Don't break existing working functionality
5. **Follow patterns**: Use the same coding style and patterns
6. **Complete file**: Output full, executable Python file

Focus on the highest-priority fixes identified in the error analysis.

Output Format:
Provide ONLY the complete Python code with no explanation.
Start with the module docstring and end with the last class definition."""

    system_prompt = "You are an expert Python developer improving library implementations."

    print(f"Generating improved implementation...")

    response = call_llm(
        prompt=prompt,
        system_prompt=system_prompt,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
    )

    return response["text"]


def extract_code_from_response(response: str) -> str:
    """Extract Python code from LLM response (handles markdown code blocks)."""
    if "```python" in response:
        start = response.find("```python") + len("```python")
        end = response.find("```", start)
        if end != -1:
            return response[start:end].strip()
    elif "```" in response:
        start = response.find("```") + len("```")
        end = response.find("```", start)
        if end != -1:
            return response[start:end].strip()

    return response.strip()


def save_json(data: Dict, path: Path):
    """Save JSON data to file."""
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def timestamp() -> str:
    """Generate timestamp string."""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%dT%H-%M-%S")


def run_stage6(
    cfg: argparse.Namespace,
    output_dir: Path,
    stage5_result: Dict,
    stage4_result: Dict,
    stage3_result: Dict
) -> Dict:
    """Run Stage 6: Error-Driven Extension.

    Args:
        cfg: Configuration namespace
        output_dir: Directory to save outputs
        stage5_result: Results from Stage 5
        stage4_result: Results from Stage 4
        stage3_result: Results from Stage 3

    Returns:
        Dictionary with stage results
    """
    print(f"\n{'='*70}")
    print("STAGE 6: ERROR-DRIVEN EXTENSION")
    print(f"{'='*70}\n")

    # Check if validation was skipped
    if stage5_result.get("skipped"):
        print("⚠ Stage 5 was skipped, cannot run error-driven extension")
        return {
            "stage": 6,
            "timestamp": timestamp(),
            "skipped": True,
            "reason": "Stage 5 was skipped"
        }

    # Check if validation was successful enough
    success_rate = stage5_result["metrics"]["success_rate"]
    if success_rate >= 0.95:  # 95% success rate
        print(f"✓ Success rate ({success_rate:.1%}) is high enough, skipping extension")
        return {
            "stage": 6,
            "timestamp": timestamp(),
            "skipped": True,
            "reason": f"Success rate {success_rate:.1%} already high enough"
        }

    # Load current implementation and documentation
    current_impl_path = Path(stage3_result["outputs"]["implementation"])
    user_message_path = Path(stage4_result["outputs"]["user_message"])
    validation_results_path = Path(stage5_result["outputs"]["detailed_results"])

    print(f"Loading current implementation from {current_impl_path}...")
    current_implementation = current_impl_path.read_text(encoding="utf-8")

    print(f"Loading user message from {user_message_path}...")
    user_message = user_message_path.read_text(encoding="utf-8")

    print(f"Loading validation results from {validation_results_path}...")
    validation_results = load_validation_results(validation_results_path)

    print(f"✓ Loaded current library and results\n")

    # Load base library docs
    print(f"Loading base library docs from {cfg.base_lib_docs}...")
    base_lib_docs = Path(cfg.base_lib_docs).read_text(encoding="utf-8")
    print(f"✓ Loaded base library docs\n")

    # Extension cycles
    print(f"Running up to {cfg.max_extension_cycles} extension cycles")
    print(f"Initial success rate: {success_rate:.1%}")
    print("-" * 70)

    extension_history = []
    best_implementation = current_implementation
    best_success_rate = success_rate

    for cycle in range(cfg.max_extension_cycles):
        print(f"\n=== Extension Cycle {cycle + 1}/{cfg.max_extension_cycles} ===\n")

        # Analyze errors
        print("Step 1: Analyzing error patterns...")
        error_analysis = analyze_error_patterns(
            validation_results=validation_results,
            current_implementation=current_implementation,
            user_message=user_message,
            model=cfg.model,
            temperature=cfg.temperature,
            max_tokens=cfg.max_tokens * 2
        )

        # Save analysis
        analysis_file = output_dir / f"cycle_{cycle + 1}_analysis.txt"
        analysis_file.write_text(error_analysis, encoding='utf-8')
        print(f"✓ Saved analysis to {analysis_file}")

        # Generate improved implementation
        print("\nStep 2: Generating improved implementation...")
        improved_impl = extend_implementation(
            current_implementation=current_implementation,
            error_analysis=error_analysis,
            base_lib_docs=base_lib_docs,
            model=cfg.model,
            temperature=cfg.temperature,
            max_tokens=cfg.max_tokens * 3
        )

        improved_code = extract_code_from_response(improved_impl)

        # Save improved implementation
        impl_file = output_dir / f"cycle_{cycle + 1}_implementation.py"
        impl_file.write_text(improved_code, encoding='utf-8')
        print(f"✓ Saved implementation to {impl_file}")

        # Note: In a full implementation, we would re-run validation here
        # For now, we record the cycle and move on

        extension_history.append({
            "cycle": cycle + 1,
            "analysis_file": str(analysis_file),
            "implementation_file": str(impl_file),
            "code_length": len(improved_code),
        })

        # Update current implementation for next cycle
        current_implementation = improved_code

        print(f"\nCycle {cycle + 1} complete")

    # Save final implementation
    final_impl_file = output_dir / "final_implementation.py"
    final_impl_file.write_text(current_implementation, encoding='utf-8')
    print(f"\n✓ Saved final implementation to {final_impl_file}\n")

    # Create summary
    result = {
        "stage": 6,
        "timestamp": timestamp(),
        "config": {
            "max_extension_cycles": cfg.max_extension_cycles,
            "initial_success_rate": success_rate,
            "model": cfg.model,
        },
        "outputs": {
            "final_implementation": str(final_impl_file),
            "extension_history": extension_history,
            "num_cycles": len(extension_history),
        }
    }

    # Save stage summary
    summary_file = output_dir / "stage6_summary.json"
    save_json(result, summary_file)

    print(f"{'='*70}")
    print("STAGE 6 COMPLETE")
    print(f"{'='*70}\n")
    print(f"Extension cycles: {len(extension_history)}")
    print(f"Final implementation: {final_impl_file}")
    print()
    print("Note: For full validation of improvements, re-run Stage 5 with the final implementation")
    print()

    return result


if __name__ == "__main__":
    from config import parse_args
    import sys

    cfg = parse_args()

    # Load Stage 3 results
    stage3_dir = Path(cfg.output_dir) / cfg.experiment_name / "stage3"
    stage3_summary = stage3_dir / "stage3_summary.json"

    if not stage3_summary.exists():
        print(f"Error: Stage 3 results not found at {stage3_summary}")
        sys.exit(1)

    with open(stage3_summary) as f:
        stage3_result = json.load(f)

    # Load Stage 4 results
    stage4_dir = Path(cfg.output_dir) / cfg.experiment_name / "stage4"
    stage4_summary = stage4_dir / "stage4_summary.json"

    if not stage4_summary.exists():
        print(f"Error: Stage 4 results not found at {stage4_summary}")
        sys.exit(1)

    with open(stage4_summary) as f:
        stage4_result = json.load(f)

    # Load Stage 5 results
    stage5_dir = Path(cfg.output_dir) / cfg.experiment_name / "stage5"
    stage5_summary = stage5_dir / "stage5_summary.json"

    if not stage5_summary.exists():
        print(f"Error: Stage 5 results not found at {stage5_summary}")
        sys.exit(1)

    with open(stage5_summary) as f:
        stage5_result = json.load(f)

    # Create output directory
    output_dir = Path(cfg.output_dir) / cfg.experiment_name / "stage6"
    output_dir.mkdir(parents=True, exist_ok=True)

    run_stage6(cfg, output_dir, stage5_result, stage4_result, stage3_result)
