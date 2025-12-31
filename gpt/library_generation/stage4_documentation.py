"""Stage 4: DSL API Specification Generation.

This stage generates a formal API specification for the generated library that can be
integrated into experiment prompts. The API spec follows the same format as the
existing Hexagen API documentation.

DOMAIN-AGNOSTIC: Works with any generated library.
"""

from __future__ import annotations

import json
import argparse
from pathlib import Path
from typing import Dict, List


def load_implementation(impl_file: Path) -> str:
    """Load generated implementation from Stage 3."""
    if not impl_file.exists():
        raise FileNotFoundError(f"Implementation not found: {impl_file}")
    return impl_file.read_text(encoding="utf-8")


def load_sample_instructions(data_path: str, num_samples: int = 10, seed: int = 42) -> List[str]:
    """Load sample instructions for documentation examples.

    Args:
        data_path: Path to standardized JSONL file
        num_samples: Number of instructions to sample
        seed: Random seed for reproducibility

    Returns:
        List of sampled instruction strings
    """
    import random
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


def generate_api_spec(
    implementation: str,
    sample_instructions: List[str],
    domain_description: str,
    model: str,
    temperature: float,
    max_tokens: int
) -> str:
    """Generate formal API specification for the library.

    Args:
        implementation: Generated library code
        sample_instructions: Sample instructions for examples
        domain_description: Brief description of domain
        model: LLM model name
        temperature: LLM temperature
        max_tokens: Max tokens for response

    Returns:
        API specification in the format used by experiment prompts
    """
    from gpt.llm_wrapper import call_llm

    instructions_text = "\n".join(f"{i+1}. {instr}" for i, instr in enumerate(sample_instructions))
    domain_context = f" for {domain_description}" if domain_description else ""

    system_prompt = "You are a technical writer creating formal API specifications for LLM consumption."

    prompt = f"""Create a formal API specification for this Python library{domain_context}.

LIBRARY CODE:
```python
{implementation}
```

EXAMPLE INSTRUCTIONS (what the library handles):
{instructions_text}

OUTPUT FORMAT (based on Hexagen API style):

# ================================  [LIBRARY NAME] API SPEC  ===============================
# One entity per line; two-space indentation shows containment.
# Extra "Notes:" lines clarify hidden behaviour.

Import: [import statement]

Constant: [NAME] = [value or type]

# -------------------------------------------------------------------------------------
Class: [ClassName]
  Method: __init__([parameters with types])
    Notes: [optional clarifications]
  Method: [method_name]([parameters with types]) -> [return_type]
    Param options: [if method accepts specific values, list them]
    Notes: [optional clarifications]
  Property: [property_name]:[type]

# -------------------------------------------------------------------------------------
Class: [AnotherClass] (inherits [BaseClass])
  Method: [method_name]([parameters]) -> [return_type]
  Static: [static_method]([parameters]) -> [return_type]

# -------------------------------------------------------------------------------------
Snippet: [common usage pattern]
Note: [important usage note]

REQUIREMENTS:
- Document ONLY public API (no methods starting with _)
- Clear parameter and return type annotations
- List specific accepted values under "Param options:" when applicable
- Two-space indentation for class members
- Separate sections with dashed lines
- Include important constants
- Show inheritance with "(inherits ClassName)"
- Mark static/class methods with "Static:"
- End with usage snippets and notes

This spec will be used by LLMs to write code - prioritize completeness and precision."""

    print(f"Generating API specification...")

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


def run_stage4(cfg: argparse.Namespace, output_dir: Path, stage3_result: Dict) -> Dict:
    """Run Stage 4: DSL API Specification Generation.

    Args:
        cfg: Configuration namespace
        output_dir: Directory to save outputs
        stage3_result: Results from Stage 3

    Returns:
        Dictionary with stage results
    """
    print(f"\n{'='*70}")
    print("STAGE 4: DSL API SPECIFICATION GENERATION")
    print(f"{'='*70}\n")

    # Load Stage 3 implementation
    stage3_impl_file = Path(stage3_result["outputs"]["implementation"])
    print(f"Loading implementation from {stage3_impl_file}...")
    implementation = load_implementation(stage3_impl_file)
    print(f"✓ Loaded implementation ({len(implementation)} characters)\n")

    # Load sample instructions for examples
    print(f"Loading sample instructions from {cfg.train_data}...")
    sample_instructions = load_sample_instructions(
        cfg.train_data,
        num_samples=10,
        seed=cfg.seed
    )
    print(f"✓ Loaded {len(sample_instructions)} sample instructions\n")

    # Generate API specification
    print("Generating API specification...")
    print("-" * 70)

    api_spec = generate_api_spec(
        implementation=implementation,
        sample_instructions=sample_instructions,
        domain_description=cfg.domain_description,
        model=cfg.model,
        temperature=cfg.temperature,
        max_tokens=cfg.max_tokens * 2
    )

    # Save API spec
    api_spec_file = output_dir / "api_spec.txt"
    api_spec_file.write_text(api_spec, encoding='utf-8')
    print(f"✓ Saved API specification to {api_spec_file}\n")

    # Create summary
    result = {
        "stage": 4,
        "timestamp": timestamp(),
        "config": {
            "train_data": cfg.train_data,
            "model": cfg.model,
        },
        "outputs": {
            "api_spec": str(api_spec_file),
            "api_spec_length": len(api_spec),
        }
    }

    # Save stage summary
    summary_file = output_dir / "stage4_summary.json"
    save_json(result, summary_file)

    print(f"{'='*70}")
    print("STAGE 4 COMPLETE")
    print(f"{'='*70}\n")
    print(f"API specification: {api_spec_file} ({len(api_spec)} chars)")
    print(f"\nTo use this in experiments, copy the API spec into your user message template:")
    print(f"  cp {api_spec_file} data/generated_api_spec.txt")
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
        print("Please run Stage 3 first!")
        sys.exit(1)

    with open(stage3_summary) as f:
        stage3_result = json.load(f)

    # Create output directory
    output_dir = Path(cfg.output_dir) / cfg.experiment_name / "stage4"
    output_dir.mkdir(parents=True, exist_ok=True)

    run_stage4(cfg, output_dir, stage3_result)
