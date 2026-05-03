"""Orchestrator Ablation: No refinement (skip Stage 2).

This ablation variant skips the refinement stage entirely, going directly from
Stage 1 discovery → Stage 3 implementation → Stage 4 documentation.

This tests whether iterative refinement with sample validation provides benefits
over using the initial API proposal directly.

Key differences from standard orchestrator:
- Stage 2 (refinement) is SKIPPED
- Stage 3 uses Stage 1 output directly (no refined API)
- Faster pipeline but potentially lower-quality API design
"""

from __future__ import annotations

import sys
from pathlib import Path

from config import parse_args


def main():
    """Run library generation pipeline WITHOUT refinement stage."""
    cfg = parse_args()

    # Create experiment directory with ablation marker
    exp_dir = Path(cfg.output_dir) / f"{cfg.experiment_name}_ablation_norefinement"
    exp_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*80}")
    print(f"LIBRARY GENERATION EXPERIMENT (ABLATION: NO REFINEMENT): {cfg.experiment_name}")
    print(f"{'='*80}\n")
    print(f"Output directory: {exp_dir}")
    print(f"Training data: {cfg.train_data}")
    print(f"Model: {cfg.model}")
    print(f"Stages to run: {cfg.stage} (Stage 2 will be skipped)")
    print()

    stages_to_run = []
    if cfg.stage == "all":
        # Skip stage 2 in ablation
        stages_to_run = ["0", "1", "3", "4"]
    else:
        # If user explicitly requests stage 2, warn and skip
        if cfg.stage == "2":
            print("⚠ Warning: Stage 2 (refinement) is disabled in this ablation")
            print("  Skipping...")
            return {}
        stages_to_run = [cfg.stage]

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

    # Stage 1: API Discovery
    if "1" in stages_to_run:
        from stage1_discovery import run_stage1
        stage1_dir = exp_dir / "stage1"
        stage1_dir.mkdir(parents=True, exist_ok=True)
        results[1] = run_stage1(cfg, stage1_dir)

    # Stage 2: SKIPPED in this ablation
    if "2" in stages_to_run:
        print("\n" + "="*80)
        print("STAGE 2: REFINEMENT (SKIPPED IN ABLATION)")
        print("="*80 + "\n")
        print("This ablation skips refinement to test whether iterative")
        print("validation provides benefits over direct implementation.")
        print()

    # Stage 3: Implementation (uses Stage 1 output directly)
    if "3" in stages_to_run:
        # Check if Stage 1 results exist
        if 1 not in results:
            # Try to load Stage 1 results from disk
            import json
            stage1_summary = exp_dir / "stage1" / "stage1_summary.json"
            if stage1_summary.exists():
                print("Loading Stage 1 results from disk...")
                with open(stage1_summary) as f:
                    results[1] = json.load(f)
            else:
                print("⚠ Warning: Stage 3 requires Stage 1 results, skipping")
                print(f"  Expected: {stage1_summary}")

        if 1 in results:
            print("\n" + "="*80)
            print("STAGE 3: IMPLEMENTATION (using Stage 1 API directly)")
            print("="*80 + "\n")

            from stage3_implementation import run_stage3
            stage3_dir = exp_dir / "stage3"
            stage3_dir.mkdir(parents=True, exist_ok=True)

            # Create a fake stage2 result that points to stage1 API
            # This allows stage3 to work without modification
            stage2_result_fake = {
                "stage": 1,  # Actually from stage 1
                "outputs": {
                    "final_api": results[1]["outputs"]["api_proposal"]  # Use stage1 API
                }
            }

            results[3] = run_stage3(cfg, stage3_dir, stage2_result_fake)

    # Stage 4: Documentation
    if "4" in stages_to_run:
        # Check if Stage 3 results exist
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
    print("EXPERIMENT COMPLETE (ABLATION: NO REFINEMENT)")
    print("="*80 + "\n")
    print(f"Results saved to: {exp_dir}")
    print(f"Stages completed: {list(results.keys())}")
    print(f"Stage 2 (refinement) was SKIPPED")
    print()

    return results


if __name__ == "__main__":
    main()
