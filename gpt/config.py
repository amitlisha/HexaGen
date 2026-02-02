"""Configuration and CLI argument parsing for experiments."""

from __future__ import annotations

import argparse


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for experiment execution."""
    p = argparse.ArgumentParser()

    grp = p.add_mutually_exclusive_group(required=True)
    grp.add_argument("--task", type=int, help="Run a single task ID (legacy mode)")
    grp.add_argument(
        "--set",
        type=str,
        help="Run every task in the chosen dataset split (e.g., 'train', 'dev', 'test' for Hexagons; 'train', 'test' for LARC)",
    )
    p.add_argument(
        "--dataset",
        choices=["hexagons", "larc"],
        default="hexagons",
        help="Dataset to use for experiments (default: hexagons)",
    )
    p.add_argument(
        "--model",
        default="gpt-4o",
        help="Model name (e.g., 'gpt-4o', 'gpt-4-turbo', 'gemini-2.0-flash-exp', 'gemini-1.5-pro')",
    )
    p.add_argument("--temperature", type=float, default=0)
    p.add_argument("--max-tokens", type=int, default=512)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument(
        "--history",
        dest="history",
        action="store_true",
        default=True,
        help="Include previous instructions in each prompt",
    )
    p.add_argument(
        "--no-history",
        dest="history",
        action="store_false",
        help="Send only the current instruction",
    )
    p.add_argument(
        "--retries", type=int, default=3, help="Max attempts per step (0 = unlimited)"
    )
    p.add_argument(
        "--mode",
        choices=["code-step", "code-full", "code-step-full", "tiles-step", "tiles-full", "tiles-step-full", "python-full"],
        default="code-step",
        help="code-step = one code instruction at a time (default); "
        "code-full = all code instructions in one prompt; "
        "code-step-full = all instructions visible, solve one at a time (emphasizes concise code); "
        "tiles-step = predict tiles step-by-step; "
        "tiles-full = predict all tiles at once for all instructions; "
        "tiles-step-full = all instructions visible, predict tiles one at a time; "
        "python-full = unrestricted Python code outputting (row, col, color) tuples",
    )
    p.add_argument(
        "--vision",
        action="store_true",
        help="Attach current board image to each prompt",
    )
    p.add_argument(
        "--workers",
        "-j",
        type=int,
        default=1,
        help="Number of tasks to run in parallel",
    )
    p.add_argument(
        "--exec-timeout",
        type=int,
        default=10,
        help="Seconds to wait for generated code before aborting (0 = no limit)",
    )
    p.add_argument(
        "--experiment-name",
        type=str,
        help="Experiment name",
    )
    p.add_argument(
        "--api-spec-file",
        type=str,
        default=None,
        help="Path to custom API spec file (for testing generated libraries). "
             "If not specified, uses default hexagen_api_spec.txt",
    )
    p.add_argument(
        "--lib-file",
        type=str,
        default="hexagen/hexagen.py",
        help="Path to library implementation file (for testing generated libraries). "
             "Default: hexagen/hexagen.py",
    )
    return p.parse_args()
