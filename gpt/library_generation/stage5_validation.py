"""Stage 5: Validation of generated library.

This stage validates the generated library by:
1. Testing it on validation dataset
2. Computing success metrics
3. Identifying failure patterns

DOMAIN-AGNOSTIC: Works with any generated library.
"""

from __future__ import annotations

import json
import argparse
from pathlib import Path
from typing import Dict, List, Tuple
import sys
import traceback
import multiprocessing as mp


def _library_exec_worker(code_str: str, lib_path: Path, queue):
    """Execute code in separate process (module-level for pickling)."""
    try:
        # Create execution namespace
        namespace = {}

        # Import the library
        import importlib.util
        spec = importlib.util.spec_from_file_location("hexagen", lib_path)
        lib = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(lib)

        # Add library to namespace (both as module and as individual exports)
        namespace['hexagen'] = lib  # Make library available as module for "from hexagen import ..."
        namespace.update(vars(lib))  # Also add individual classes/functions

        # Execute code
        exec(code_str, namespace)

        # Extract result (assumes Game context was used)
        if '_game_context' in namespace and namespace['_game_context']:
            game = namespace['_game_context'][-1]
            result = game.board_state
        else:
            result = None

        queue.put(("ok", result, ""))

    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
        queue.put(("error", None, error_msg))


def load_validation_data(data_path: str, max_tasks: int = None) -> List[Dict]:
    """Load validation dataset.

    Args:
        data_path: Path to validation JSONL file
        max_tasks: Optional limit on number of tasks to validate

    Returns:
        List of task dictionaries
    """
    tasks = []
    data_file = Path(data_path)

    with open(data_file, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            try:
                task = json.loads(line)
                tasks.append(task)
                if max_tasks and len(tasks) >= max_tasks:
                    break
            except json.JSONDecodeError as e:
                print(f"Warning: Invalid JSON on line {line_num}: {e}")

    return tasks


def execute_with_library(
    code: str,
    library_path: Path,
    timeout: int = 5
) -> Tuple[bool, any, str]:
    """Execute generated code with the library using timeout protection.

    Args:
        code: Code to execute
        library_path: Path to generated library file
        timeout: Execution timeout in seconds

    Returns:
        (success, result, error_message)
    """
    # Execute with timeout using multiprocessing
    ctx = mp.get_context("spawn")
    q = ctx.Queue()
    p = ctx.Process(target=_library_exec_worker, args=(code, library_path, q), daemon=True)
    p.start()
    p.join(timeout)

    if p.is_alive():
        p.terminate()
        p.join()
        return False, None, f"TIMEOUT: Code execution exceeded {timeout} seconds"

    status, result, error_msg = q.get()
    return (status == "ok"), result, error_msg


def generate_code_with_llm(
    instructions: List[str],
    user_message: str,
    system_prompt: str,
    model: str,
    temperature: float,
    max_tokens: int
) -> str:
    """Generate code for instructions using the LLM.

    Args:
        instructions: List of instruction strings
        user_message: User message documentation
        system_prompt: System prompt for LLM
        model: LLM model name
        temperature: LLM temperature
        max_tokens: Max tokens for response

    Returns:
        Generated Python code
    """
    from gpt.llm_wrapper import call_llm

    instructions_text = "\n".join(f"{i+1}. {instr}" for i, instr in enumerate(instructions))

    prompt = f"""Using the library described below, write Python code to accomplish the following instructions:

{instructions_text}

Your code should:
- Import necessary components from the library
- Use a Game context manager (with Game() as g:)
- Execute all instructions in order
- Be complete and executable

Provide ONLY the Python code, no explanation."""

    # Combine system prompt and user message
    full_system_prompt = f"{system_prompt}\n\n{user_message}"

    response = call_llm(
        prompt=prompt,
        system_prompt=full_system_prompt,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
    )

    code = response["text"]

    # Extract code from markdown blocks if present
    if "```python" in code:
        start = code.find("```python") + len("```python")
        end = code.find("```", start)
        if end != -1:
            code = code[start:end].strip()
    elif "```" in code:
        start = code.find("```") + len("```")
        end = code.find("```", start)
        if end != -1:
            code = code[start:end].strip()

    return code


def compare_states(generated_state, expected_state) -> Tuple[bool, float]:
    """Compare generated and expected states.

    Args:
        generated_state: State from generated code
        expected_state: Expected state from dataset

    Returns:
        (exact_match, similarity_score)
    """
    if generated_state is None or expected_state is None:
        return False, 0.0

    if len(generated_state) != len(expected_state):
        return False, 0.0

    # Exact match
    if generated_state == expected_state:
        return True, 1.0

    # Similarity score (percentage of matching elements)
    matches = sum(1 for g, e in zip(generated_state, expected_state) if g == e)
    similarity = matches / len(expected_state)

    return False, similarity


def validate_task(
    task: Dict,
    library_path: Path,
    user_message: str,
    system_prompt: str,
    model: str,
    temperature: float,
    max_tokens: int
) -> Dict:
    """Validate a single task.

    Args:
        task: Task dictionary from validation dataset
        library_path: Path to generated library
        user_message: User message documentation
        system_prompt: System prompt for LLM
        model: LLM model name
        temperature: LLM temperature
        max_tokens: Max tokens for response

    Returns:
        Validation result dictionary
    """
    task_id = task["task_id"]
    steps = task["steps"]

    result = {
        "task_id": task_id,
        "num_steps": len(steps),
        "step_results": [],
        "success": False,
        "error": None
    }

    try:
        # Generate code for all instructions
        instructions = [step["instruction"] for step in steps]

        code = generate_code_with_llm(
            instructions=instructions,
            user_message=user_message,
            system_prompt=system_prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )

        result["generated_code"] = code

        # Execute code
        success, generated_state, error = execute_with_library(
            code=code,
            library_path=library_path
        )

        if not success:
            result["error"] = error
            return result

        # Compare with expected final state
        expected_state = steps[-1]["output_state"]
        exact_match, similarity = compare_states(generated_state, expected_state)

        result["success"] = exact_match
        result["similarity"] = similarity
        result["generated_state"] = generated_state
        result["expected_state"] = expected_state

    except Exception as e:
        result["error"] = f"{type(e).__name__}: {str(e)}"

    return result


def compute_metrics(validation_results: List[Dict]) -> Dict:
    """Compute aggregate metrics from validation results.

    Args:
        validation_results: List of validation result dictionaries

    Returns:
        Metrics dictionary
    """
    total = len(validation_results)
    successful = sum(1 for r in validation_results if r["success"])
    failed = sum(1 for r in validation_results if r["error"] is not None)
    partial = total - successful - failed

    similarities = [r.get("similarity", 0.0) for r in validation_results]
    avg_similarity = sum(similarities) / len(similarities) if similarities else 0.0

    return {
        "total_tasks": total,
        "successful": successful,
        "failed": failed,
        "partial": partial,
        "success_rate": successful / total if total > 0 else 0.0,
        "average_similarity": avg_similarity,
    }


def analyze_failures(validation_results: List[Dict]) -> Dict:
    """Analyze failure patterns.

    Args:
        validation_results: List of validation result dictionaries

    Returns:
        Failure analysis dictionary
    """
    failures = [r for r in validation_results if not r["success"]]

    if not failures:
        return {"num_failures": 0, "patterns": []}

    # Group by error type
    error_types = {}
    for failure in failures:
        error = failure.get("error", "Unknown")
        if error:
            error_type = error.split(":")[0] if ":" in error else "Unknown"
            error_types[error_type] = error_types.get(error_type, 0) + 1

    return {
        "num_failures": len(failures),
        "error_types": error_types,
        "sample_failures": failures[:5]  # First 5 failures for inspection
    }


def save_json(data: Dict, path: Path):
    """Save JSON data to file."""
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def timestamp() -> str:
    """Generate timestamp string."""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%dT%H-%M-%S")


def run_stage5(cfg: argparse.Namespace, output_dir: Path, stage4_result: Dict, stage3_result: Dict) -> Dict:
    """Run Stage 5: Validation.

    Args:
        cfg: Configuration namespace
        output_dir: Directory to save outputs
        stage4_result: Results from Stage 4
        stage3_result: Results from Stage 3

    Returns:
        Dictionary with stage results
    """
    print(f"\n{'='*70}")
    print("STAGE 5: VALIDATION")
    print(f"{'='*70}\n")

    # Check if validation data is provided
    if not cfg.validation_data:
        print("⚠ Warning: No validation data provided, skipping validation")
        return {
            "stage": 5,
            "timestamp": timestamp(),
            "skipped": True,
            "reason": "No validation data provided"
        }

    # Load generated library and documentation
    library_path = Path(stage3_result["outputs"]["implementation"])
    user_message_path = Path(stage4_result["outputs"]["user_message"])
    system_prompt_path = Path(stage4_result["outputs"]["system_prompt"])

    print(f"Loading generated library from {library_path}...")
    print(f"Loading user message from {user_message_path}...")
    print(f"Loading system prompt from {system_prompt_path}...")

    user_message = user_message_path.read_text(encoding="utf-8")
    system_prompt = system_prompt_path.read_text(encoding="utf-8")

    print(f"✓ Loaded library and documentation\n")

    # Load validation data
    print(f"Loading validation data from {cfg.validation_data}...")
    validation_tasks = load_validation_data(cfg.validation_data, max_tasks=50)  # Limit for cost
    print(f"✓ Loaded {len(validation_tasks)} validation tasks\n")

    # Validate each task
    print("Validating tasks...")
    print("-" * 70)

    validation_results = []
    for i, task in enumerate(validation_tasks):
        print(f"Task {i+1}/{len(validation_tasks)}: {task['task_id']}", end=" ")

        result = validate_task(
            task=task,
            library_path=library_path,
            user_message=user_message,
            system_prompt=system_prompt,
            model=cfg.model,
            temperature=cfg.temperature,
            max_tokens=cfg.max_tokens * 2
        )

        validation_results.append(result)

        if result["success"]:
            print("✓")
        elif result.get("similarity", 0) > 0.8:
            print(f"~ ({result['similarity']:.2f})")
        else:
            print("✗")

    # Compute metrics
    print("\nComputing metrics...")
    metrics = compute_metrics(validation_results)

    # Analyze failures
    print("Analyzing failures...")
    failure_analysis = analyze_failures(validation_results)

    # Save detailed results
    results_file = output_dir / "validation_results.json"
    save_json(validation_results, results_file)
    print(f"✓ Saved detailed results to {results_file}")

    # Create summary
    result = {
        "stage": 5,
        "timestamp": timestamp(),
        "config": {
            "validation_data": cfg.validation_data,
            "num_tasks": len(validation_tasks),
            "model": cfg.model,
        },
        "metrics": metrics,
        "failure_analysis": failure_analysis,
        "outputs": {
            "detailed_results": str(results_file),
        }
    }

    # Save stage summary
    summary_file = output_dir / "stage5_summary.json"
    save_json(result, summary_file)

    print(f"\n{'='*70}")
    print("STAGE 5 COMPLETE")
    print(f"{'='*70}\n")
    print(f"Tasks validated: {metrics['total_tasks']}")
    print(f"Success rate: {metrics['success_rate']:.1%}")
    print(f"Average similarity: {metrics['average_similarity']:.1%}")
    print(f"Failures: {failure_analysis['num_failures']}")
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

    # Load Stage 4 results
    stage4_dir = Path(cfg.output_dir) / cfg.experiment_name / "stage4"
    stage4_summary = stage4_dir / "stage4_summary.json"

    if not stage4_summary.exists():
        print(f"Error: Stage 4 results not found at {stage4_summary}")
        print("Please run Stage 4 first!")
        sys.exit(1)

    with open(stage4_summary) as f:
        stage4_result = json.load(f)

    # Create output directory
    output_dir = Path(cfg.output_dir) / cfg.experiment_name / "stage5"
    output_dir.mkdir(parents=True, exist_ok=True)

    run_stage5(cfg, output_dir, stage4_result, stage3_result)
