"""Suite runner for DSL generation experiments.

Runs multiple DSL generation + evaluation cycles with different configurations,
collecting and aggregating results across setups and repeats.

Usage:
    python gpt/suite_runner.py configs/my_suite.yaml
    python gpt/suite_runner.py configs/my_suite.yaml --dry-run
    python gpt/suite_runner.py configs/my_suite.yaml --skip-generation
    python gpt/suite_runner.py configs/my_suite.yaml --setup baseline singleshot
"""

from __future__ import annotations

import argparse
import json
import shutil
import statistics
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML is required. Install with: pip install pyyaml")
    sys.exit(1)


PROJECT_ROOT = Path(__file__).resolve().parent.parent


# ── YAML loading & validation ────────────────────────────────────────────────


def load_yaml(path: str) -> dict:
    """Load and return a YAML config file."""
    with open(path) as f:
        return yaml.safe_load(f)


def validate_config(config: dict) -> None:
    """Validate suite config, raising ValueError for missing/invalid fields."""
    required_top = ["suite_name", "dsl_defaults", "eval", "setups"]
    for key in required_top:
        if key not in config:
            raise ValueError(f"Missing required top-level key: '{key}'")

    required_dsl = ["train_data", "base_lib_docs", "base_lib"]
    for key in required_dsl:
        if key not in config["dsl_defaults"]:
            raise ValueError(f"Missing required dsl_defaults key: '{key}'")

    if "set" not in config["eval"]:
        raise ValueError("Missing required eval key: 'set'")

    if not config["setups"]:
        raise ValueError("'setups' list must have at least one entry")

    for i, setup in enumerate(config["setups"]):
        if "name" not in setup:
            raise ValueError(f"Setup at index {i} missing required 'name' field")

    names = [s["name"] for s in config["setups"]]
    if len(names) != len(set(names)):
        raise ValueError(f"Duplicate setup names found: {names}")

    valid_ablations = {"singleshot", "no-refinement"}
    for setup in config["setups"]:
        for abl in setup.get("ablation", []):
            if abl not in valid_ablations:
                raise ValueError(
                    f"Invalid ablation '{abl}' in setup '{setup['name']}'. "
                    f"Valid: {valid_ablations}"
                )


# ── Naming helpers ───────────────────────────────────────────────────────────


def compute_effective_exp_name(experiment_name: str, ablation: list) -> str:
    """Replicate orchestrator's ablation suffix logic (orchestrator.py:24-27)."""
    if ablation:
        ablation_suffix = "_".join(ablation).replace("-", "")
        return f"{experiment_name}_ablation_{ablation_suffix}"
    return experiment_name


# ── Command builders ─────────────────────────────────────────────────────────


def build_orchestrator_cmd(dsl_config: dict, experiment_name: str) -> list:
    """Build the subprocess command for orchestrator.py."""
    cmd = [
        sys.executable,
        str(PROJECT_ROOT / "gpt" / "library_generation" / "orchestrator.py"),
        "--experiment-name", experiment_name,
        "--train-data", dsl_config["train_data"],
        "--base-lib-docs", dsl_config["base_lib_docs"],
        "--base-lib", dsl_config["base_lib"],
    ]

    simple_args = {
        "model": "--model",
        "workers": "--workers",
        "temperature": "--temperature",
        "max_tokens": "--max-tokens",
        "seed": "--seed",
        "batch_size": "--batch-size",
        "meta_batch_size": "--meta-batch-size",
        "refinement_iterations": "--refinement-iterations",
        "output_dir": "--output-dir",
        "stage": "--stage",
        "domain_description": "--domain-description",
        "base_url": "--base-url",
        "api_key": "--api-key",
    }

    for key, flag in simple_args.items():
        val = dsl_config.get(key)
        if val is not None:
            cmd += [flag, str(val)]

    if dsl_config.get("vision"):
        cmd.append("--vision")

    ablation = dsl_config.get("ablation", [])
    if ablation:
        cmd += ["--ablation"] + list(ablation)

    return cmd


def build_eval_cmd(
    eval_config: dict,
    experiment_name: str,
    lib_file: str,
    api_spec_file: str,
) -> list:
    """Build the subprocess command for experiment.py."""
    cmd = [
        sys.executable,
        str(PROJECT_ROOT / "gpt" / "experiment.py"),
        "--set", eval_config["set"],
        "--mode", eval_config.get("mode", "code-full"),
        "--experiment-name", experiment_name,
        "--lib-file", lib_file,
        "--api-spec-file", api_spec_file,
    ]

    simple_args = {
        "model": "--model",
        "workers": "--workers",
        "temperature": "--temperature",
        "max_tokens": "--max-tokens",
        "exec_timeout": "--exec-timeout",
        "retries": "--retries",
        "base_url": "--base-url",
        "api_key": "--api-key",
    }

    for key, flag in simple_args.items():
        val = eval_config.get(key)
        if val is not None:
            cmd += [flag, str(val)]

    if eval_config.get("history") is False:
        cmd.append("--no-history")

    return cmd


# ── Subprocess execution ─────────────────────────────────────────────────────


def run_subprocess(cmd: list, label: str, dry_run: bool = False) -> bool:
    """Run a subprocess, stream output, return True if exit code is 0."""
    print(f"\n[{label}] Running:")
    print(f"  {' '.join(cmd)}\n")

    if dry_run:
        print(f"[{label}] (dry-run, skipping execution)")
        return True

    try:
        result = subprocess.run(
            cmd,
            cwd=str(PROJECT_ROOT),
            stdout=sys.stdout,
            stderr=sys.stderr,
        )

        if result.returncode != 0:
            print(f"\n[{label}] FAILED with exit code {result.returncode}")
            return False

        print(f"\n[{label}] Completed successfully")
        return True

    except Exception as e:
        print(f"\n[{label}] Exception: {e}")
        return False


# ── Result collection ─────────────────────────────────────────────────────────


def collect_eval_results(experiment_name: str, eval_set: str) -> Optional[dict]:
    """Find and parse the eval results JSON written by experiment.py.

    experiment.py writes results to results-{name}-{UUID}/{set}/all_*.json.
    We glob for the directory since the UUID is generated at runtime.
    """
    pattern = f"results-{experiment_name}-*/{eval_set}/all_*.json"
    matches = sorted(
        PROJECT_ROOT.glob(pattern),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    if not matches:
        print(f"  Warning: no eval results found for pattern: {pattern}")
        return None

    result_path = matches[0]
    with open(result_path) as f:
        data = json.load(f)

    agg = data.get("aggregate")
    if agg:
        agg["result_file"] = str(result_path)
    return agg


# ── Summary & display ────────────────────────────────────────────────────────


def build_summary(all_results: list, config: dict) -> dict:
    """Build final suite summary with per-setup aggregated metrics."""
    by_setup: dict[str, list] = defaultdict(list)
    for entry in all_results:
        by_setup[entry["setup"]].append(entry)

    setup_summaries = {}
    for setup_name, entries in by_setup.items():
        successful_evals = [
            e["evaluation"]["aggregate"]
            for e in entries
            if e["evaluation"]["status"] == "OK" and e["evaluation"].get("aggregate")
        ]

        if successful_evals:
            total_steps_list = [e["total_steps"] for e in successful_evals]
            setup_summaries[setup_name] = {
                "n_repeats_attempted": len(entries),
                "n_repeats_succeeded": len(successful_evals),
                "mean_f1_board": statistics.mean(
                    e["f1_board"] for e in successful_evals
                ),
                "std_f1_board": (
                    statistics.stdev(e["f1_board"] for e in successful_evals)
                    if len(successful_evals) > 1
                    else 0.0
                ),
                "mean_f1_action": statistics.mean(
                    e["f1_action"] for e in successful_evals
                ),
                "std_f1_action": (
                    statistics.stdev(e["f1_action"] for e in successful_evals)
                    if len(successful_evals) > 1
                    else 0.0
                ),
                "mean_exact_rate": statistics.mean(
                    e["exact"] / e["total_steps"] if e["total_steps"] > 0 else 0
                    for e in successful_evals
                ),
                "mean_valid_rate": statistics.mean(
                    e["valid"] / e["total_steps"] if e["total_steps"] > 0 else 0
                    for e in successful_evals
                ),
                "per_repeat": successful_evals,
            }
        else:
            setup_summaries[setup_name] = {
                "n_repeats_attempted": len(entries),
                "n_repeats_succeeded": 0,
                "error": "All repeats failed",
            }

    return {
        "suite_name": config["suite_name"],
        "timestamp": time.strftime("%Y-%m-%dT%H-%M-%S"),
        "config": config,
        "setup_summaries": setup_summaries,
        "all_runs": all_results,
    }


def print_summary_table(all_results: list, config: dict) -> None:
    """Print a formatted summary table to the console."""
    by_setup: dict[str, list] = defaultdict(list)
    for entry in all_results:
        by_setup[entry["setup"]].append(entry)

    print(f"\n{'=' * 100}")
    print(f"SUITE SUMMARY: {config['suite_name']}")
    print(f"{'=' * 100}\n")

    header = (
        f"{'Setup':<25} | {'Repeats':>7} | {'Board F1 (mean +/- std)':>25} "
        f"| {'Action F1':>12} | {'Exact':>8} | {'Valid':>8}"
    )
    print(header)
    print("-" * len(header))

    for setup_name in [s["name"] for s in config["setups"]]:
        entries = by_setup.get(setup_name, [])
        successful_evals = [
            e["evaluation"]["aggregate"]
            for e in entries
            if e["evaluation"]["status"] == "OK" and e["evaluation"].get("aggregate")
        ]

        n_ok = len(successful_evals)
        n_total = len(entries)

        if not successful_evals:
            print(f"{setup_name:<25} | {n_ok:>2}/{n_total:<2}   |{'FAILED':>26} |{'':>13} |{'':>9} |{'':>9}")
            continue

        f1b = [e["f1_board"] for e in successful_evals]
        f1a = [e["f1_action"] for e in successful_evals]
        exact = [
            e["exact"] / e["total_steps"] * 100 if e["total_steps"] > 0 else 0
            for e in successful_evals
        ]
        valid = [
            e["valid"] / e["total_steps"] * 100 if e["total_steps"] > 0 else 0
            for e in successful_evals
        ]

        mean_f1b = statistics.mean(f1b)
        std_f1b = statistics.stdev(f1b) if len(f1b) > 1 else 0.0
        mean_f1a = statistics.mean(f1a)
        mean_exact = statistics.mean(exact)
        mean_valid = statistics.mean(valid)

        print(
            f"{setup_name:<25} | {n_ok:>2}/{n_total:<2}   | "
            f"{mean_f1b:.3f} +/- {std_f1b:.3f}             | "
            f"{mean_f1a:>10.3f}  | "
            f"{mean_exact:>6.1f}% | "
            f"{mean_valid:>6.1f}%"
        )

    print()


# ── Main suite runner ─────────────────────────────────────────────────────────


def run_suite(
    config_path: str,
    dry_run: bool = False,
    skip_gen: bool = False,
    skip_eval: bool = False,
    setup_filter: Optional[List[str]] = None,
    repeat_start: int = 1,
) -> dict:
    """Run the full suite of DSL generation + evaluation experiments."""
    config = load_yaml(config_path)
    validate_config(config)

    suite_name = config["suite_name"]
    repeats = config.get("repeats", 3)
    dsl_defaults = config["dsl_defaults"]
    eval_config = config["eval"]
    setups = config["setups"]

    # Filter setups if requested
    if setup_filter:
        setups = [s for s in setups if s["name"] in setup_filter]
        if not setups:
            available = [s["name"] for s in config["setups"]]
            raise ValueError(
                f"No setups matched filter {setup_filter}. Available: {available}"
            )

    # Create suite output directory
    ts = time.strftime("%Y-%m-%dT%H-%M-%S")
    suite_dir = PROJECT_ROOT / "suite_results" / f"{suite_name}_{ts}"
    suite_dir.mkdir(parents=True, exist_ok=True)

    # Copy config for reproducibility
    shutil.copy2(config_path, suite_dir / "suite_config.yaml")

    print(f"\n{'=' * 80}")
    print(f"DSL GENERATION SUITE: {suite_name}")
    print(f"{'=' * 80}")
    print(f"Setups: {[s['name'] for s in setups]}")
    print(f"Repeats: {repeats} (starting from {repeat_start})")
    print(f"Output: {suite_dir}")
    if dry_run:
        print("MODE: DRY RUN (no commands will be executed)")
    if skip_gen:
        print("MODE: SKIP GENERATION (evaluation only)")
    if skip_eval:
        print("MODE: SKIP EVALUATION (generation only)")
    print()

    all_results = []

    for setup in setups:
        setup_name = setup["name"]
        merged_dsl = {**dsl_defaults, **{k: v for k, v in setup.items() if k != "name"}}

        for repeat_idx in range(repeat_start, repeats + 1):
            run_key = f"{setup_name}__r{repeat_idx}"

            print(f"\n{'=' * 80}")
            print(f"SUITE RUN: {run_key} ({setups.index(setup) + 1}/{len(setups)} setups, "
                  f"repeat {repeat_idx}/{repeats})")
            print(f"{'=' * 80}")

            result_entry = {
                "setup": setup_name,
                "repeat": repeat_idx,
                "dsl_config": merged_dsl,
                "dsl_generation": None,
                "evaluation": None,
            }

            # --- Phase A: DSL Generation ---
            gen_exp_name = f"{suite_name}__{setup_name}__r{repeat_idx}"

            if not skip_gen:
                gen_cmd = build_orchestrator_cmd(merged_dsl, gen_exp_name)
                gen_ok = run_subprocess(
                    gen_cmd, label=f"DSL-GEN [{run_key}]", dry_run=dry_run
                )

                if not gen_ok:
                    result_entry["dsl_generation"] = {"status": "FAILED"}
                    result_entry["evaluation"] = {
                        "status": "SKIPPED",
                        "reason": "DSL generation failed",
                    }
                    all_results.append(result_entry)
                    continue

                result_entry["dsl_generation"] = {"status": "OK"}
            else:
                result_entry["dsl_generation"] = {"status": "SKIPPED (--skip-generation)"}

            # --- Locate generated library ---
            ablation = merged_dsl.get("ablation", [])
            output_dir = merged_dsl.get("output_dir", "generated_libs")
            effective_name = compute_effective_exp_name(gen_exp_name, ablation)

            lib_file = PROJECT_ROOT / output_dir / effective_name / "stage3" / "generated_library.py"
            api_spec_file = PROJECT_ROOT / output_dir / effective_name / "stage4" / "api_spec.txt"

            if not dry_run and (not lib_file.exists() or not api_spec_file.exists()):
                result_entry["dsl_generation"] = {
                    "status": "INCOMPLETE",
                    "lib_file_exists": lib_file.exists(),
                    "api_spec_exists": api_spec_file.exists(),
                    "expected_lib": str(lib_file),
                    "expected_spec": str(api_spec_file),
                }
                result_entry["evaluation"] = {
                    "status": "SKIPPED",
                    "reason": "Library files not found after generation",
                }
                all_results.append(result_entry)
                continue

            if result_entry["dsl_generation"].get("status") == "OK":
                result_entry["dsl_generation"]["lib_file"] = str(lib_file)
                result_entry["dsl_generation"]["api_spec_file"] = str(api_spec_file)

            # --- Phase B: Evaluation ---
            if not skip_eval:
                eval_exp_name = f"{suite_name}__eval__{setup_name}__r{repeat_idx}"
                eval_cmd = build_eval_cmd(
                    eval_config, eval_exp_name, str(lib_file), str(api_spec_file)
                )
                eval_ok = run_subprocess(
                    eval_cmd, label=f"EVAL [{run_key}]", dry_run=dry_run
                )

                if not eval_ok:
                    result_entry["evaluation"] = {"status": "FAILED"}
                    all_results.append(result_entry)
                    continue

                if dry_run:
                    result_entry["evaluation"] = {"status": "OK (dry-run)"}
                else:
                    eval_agg = collect_eval_results(
                        eval_exp_name, eval_config["set"]
                    )
                    result_entry["evaluation"] = {
                        "status": "OK",
                        "aggregate": eval_agg,
                    }
            else:
                result_entry["evaluation"] = {"status": "SKIPPED (--skip-evaluation)"}

            all_results.append(result_entry)

    # --- Final summary ---
    summary = build_summary(all_results, config)
    summary_path = suite_dir / "suite_summary.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2, default=str)

    print_summary_table(all_results, config)
    print(f"Results written to: {summary_path}")

    return summary


# ── CLI ───────────────────────────────────────────────────────────────────────


def main() -> None:
    p = argparse.ArgumentParser(
        description="Run a suite of DSL generation + evaluation experiments"
    )
    p.add_argument("config", type=str, help="Path to YAML suite configuration file")
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Print commands without executing",
    )
    p.add_argument(
        "--skip-generation",
        action="store_true",
        help="Skip DSL generation, only run evaluation (libraries must already exist)",
    )
    p.add_argument(
        "--skip-evaluation",
        action="store_true",
        help="Skip evaluation, only run DSL generation",
    )
    p.add_argument(
        "--setup",
        type=str,
        nargs="+",
        help="Only run specific setup(s) by name (default: all)",
    )
    p.add_argument(
        "--repeat-start",
        type=int,
        default=1,
        help="Start repeat index, for resuming interrupted suites (default: 1)",
    )

    args = p.parse_args()

    run_suite(
        config_path=args.config,
        dry_run=args.dry_run,
        skip_gen=args.skip_generation,
        skip_eval=args.skip_evaluation,
        setup_filter=args.setup,
        repeat_start=args.repeat_start,
    )


if __name__ == "__main__":
    main()