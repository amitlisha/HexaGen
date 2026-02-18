"""Main orchestrator for library generation experiments.

This script runs the multi-stage library generation pipeline:
- Stage 0: Create minimal foundation library
- Stage 1: API discovery through hierarchical analysis
- Stage 2: API refinement
- Stage 3: Implementation generation
- Stage 4: DSL documentation generation
"""

from __future__ import annotations

import sys
from pathlib import Path

from config import parse_args


def main():
    """Run library generation pipeline."""
    cfg = parse_args()

    # Initialize LLM client (supports local models via --base-url)
    from gpt.llm_wrapper import init_llm
    init_llm(cfg)

    # Create experiment directory (add ablation suffix if applicable)
    exp_name = cfg.experiment_name
    if cfg.ablation:
        ablation_suffix = "_".join(cfg.ablation).replace("-", "")
        exp_name = f"{cfg.experiment_name}_ablation_{ablation_suffix}"

    exp_dir = Path(cfg.output_dir) / exp_name
    exp_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*80}")
    print(f"LIBRARY GENERATION EXPERIMENT: {cfg.experiment_name}")
    if cfg.ablation:
        print(f"ABLATION MODE: {', '.join(cfg.ablation)}")
    print(f"{'='*80}\n")
    print(f"Output directory: {exp_dir}")
    print(f"Training data: {cfg.train_data}")
    print(f"Validation data: {cfg.validation_data if cfg.validation_data else 'None'}")
    print(f"Model: {cfg.model}")
    if cfg.base_url:
        print(f"Base URL: {cfg.base_url}")
    print(f"Stages to run: {cfg.stage}")
    if cfg.ablation:
        print(f"Ablation: {', '.join(cfg.ablation)}")
    print()

    stages_to_run = []
    if cfg.stage == "all":
        stages_to_run = ["0", "1", "2", "3", "4"]
        # Handle ablations
        if "no-refinement" in cfg.ablation:
            stages_to_run.remove("2")  # Skip Stage 2
    else:
        stages_to_run = [cfg.stage]
        # Warn if trying to run incompatible stage with ablation
        if "no-refinement" in cfg.ablation and cfg.stage == "2":
            print("⚠ Warning: Stage 2 is disabled in no-refinement ablation")
            return {}

    results = {}

    # Stage 0: Minimal foundation library
    if "0" in stages_to_run:
        print("\n" + "="*80)
        print("STAGE 0: Minimal Foundation Library")
        print("="*80 + "\n")
        print("TODO: Extract minimal library from hexagen")
        print("This stage will create a stripped-down version with only:")
        print("  - Game (context manager, board_state, plot)")
        print("  - Tile (row, col, draw, basic properties)")
        print("  - Shape (collection of tiles, draw)")
        print("  - _Vec, _Hexagon (internal coordinate math)")
        print("  - Constants (WIDTH, HEIGHT, COLORS, DIRECTIONS)")
        print()
        # TODO: Implement stage0_minimal_lib.py
        # from stage0_minimal_lib import run_stage0
        # results[0] = run_stage0(cfg, exp_dir / "stage0")

    # Stage 1: API Discovery
    if "1" in stages_to_run:
        stage1_dir = exp_dir / "stage1"
        stage1_dir.mkdir(parents=True, exist_ok=True)

        if "singleshot" in cfg.ablation:
            # Use single-shot variant
            from stage1_discovery_ablation_singleshot import run_stage1_singleshot
            results[1] = run_stage1_singleshot(cfg, stage1_dir)
        else:
            # Use standard hierarchical batching
            from stage1_discovery import run_stage1
            results[1] = run_stage1(cfg, stage1_dir)

    # Stage 2: API Refinement
    if "2" in stages_to_run:
        # Check if Stage 1 results exist (either from current run or from disk)
        if 1 not in results:
            # Try to load Stage 1 results from disk
            import json
            stage1_summary = exp_dir / "stage1" / "stage1_summary.json"
            if stage1_summary.exists():
                print("Loading Stage 1 results from disk...")
                with open(stage1_summary) as f:
                    results[1] = json.load(f)
            else:
                print("⚠ Warning: Stage 2 requires Stage 1 results, skipping")
                print(f"  Expected: {stage1_summary}")

        if 1 in results:
            from stage2_refinement import run_stage2
            stage2_dir = exp_dir / "stage2"
            stage2_dir.mkdir(parents=True, exist_ok=True)
            results[2] = run_stage2(cfg, stage2_dir, results[1])

    # Stage 3: Implementation
    if "3" in stages_to_run:
        stage2_result = None

        # For no-refinement ablation, use Stage 1 output directly
        if "no-refinement" in cfg.ablation:
            if 1 not in results:
                # Try to load Stage 1 results from disk
                import json
                stage1_summary = exp_dir / "stage1" / "stage1_summary.json"
                if stage1_summary.exists():
                    print("Loading Stage 1 results from disk (no-refinement ablation)...")
                    with open(stage1_summary) as f:
                        results[1] = json.load(f)
                else:
                    print("⚠ Warning: Stage 3 requires Stage 1 results, skipping")
                    print(f"  Expected: {stage1_summary}")

            if 1 in results:
                print("\n" + "="*80)
                print("STAGE 3: IMPLEMENTATION (using Stage 1 API directly - no refinement)")
                print("="*80 + "\n")

                # Create fake stage2 result pointing to stage1 API
                stage2_result = {
                    "stage": 1,
                    "outputs": {
                        "final_api": results[1]["outputs"]["api_proposal"]
                    }
                }
        else:
            # Standard flow: check for Stage 2 results
            if 2 not in results:
                # Try to load Stage 2 results from disk
                import json
                stage2_summary = exp_dir / "stage2" / "stage2_summary.json"
                if stage2_summary.exists():
                    print("Loading Stage 2 results from disk...")
                    with open(stage2_summary) as f:
                        results[2] = json.load(f)
                else:
                    print("⚠ Warning: Stage 3 requires Stage 2 results, skipping")
                    print(f"  Expected: {stage2_summary}")

            if 2 in results:
                stage2_result = results[2]

        # Run Stage 3 if we have input (either from Stage 2 or Stage 1)
        if stage2_result:
            from stage3_implementation import run_stage3
            stage3_dir = exp_dir / "stage3"
            stage3_dir.mkdir(parents=True, exist_ok=True)
            results[3] = run_stage3(cfg, stage3_dir, stage2_result)

    # Stage 4: Documentation
    if "4" in stages_to_run:
        # Check if Stage 3 results exist (either from current run or from disk)
        if 3 not in results:
            # Try to load Stage 3 results from disk
            import json
            stage3_summary = exp_dir / "stage3" / "stage3_summary.json"
            if stage3_summary.exists():
                print("Loading Stage 3 results from disk...")
                with open(stage3_summary) as f:
                    results[3] = json.load(f)
            else:
                print("⚠ Warning: Stage 4 requires Stage 3 results, skipping")
                print(f"  Expected: {stage3_summary}")

        if 3 in results:
            from stage4_documentation import run_stage4
            stage4_dir = exp_dir / "stage4"
            stage4_dir.mkdir(parents=True, exist_ok=True)
            results[4] = run_stage4(cfg, stage4_dir, results[3])

    # Final summary
    print("\n" + "="*80)
    print("EXPERIMENT COMPLETE")
    if cfg.ablation:
        print(f"(ABLATIONS: {', '.join(cfg.ablation)})")
    print("="*80 + "\n")
    print(f"Results saved to: {exp_dir}")
    print(f"Stages completed: {list(results.keys())}")
    if "singleshot" in cfg.ablation:
        print("  Stage 1: Single-shot analysis (no hierarchical batching)")
    if "no-refinement" in cfg.ablation:
        print("  Stage 2: Skipped (no refinement)")
    print()

    return results


if __name__ == "__main__":
    main()
