"""Configuration for library generation experiments."""

from __future__ import annotations

import argparse


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for library generation."""
    p = argparse.ArgumentParser(
        description="Generate a Python library from training samples using LLMs"
    )

    # Stage control
    p.add_argument(
        "--stage",
        choices=["0", "1", "2", "3", "4", "all"],
        default="all",
        help="Which stage to run (0=minimal lib, 1=discovery, 2=refine, 3=implement, "
        "4=docs, all=run all stages)",
    )

    # Dataset (domain-agnostic)
    p.add_argument(
        "--train-data",
        type=str,
        required=True,
        help="Path to training data JSONL file for API discovery",
    )
    p.add_argument(
        "--validation-data",
        type=str,
        help="Path to validation data JSONL file",
    )
    p.add_argument(
        "--instruction-field",
        type=str,
        default="drawing_procedure",
        help="JSONL field containing instructions (supports nested: 'field.subfield' or 'field[1]')",
    )

    # Base library documentation (domain-agnostic)
    p.add_argument(
        "--base-lib-docs",
        type=str,
        required=True,
        help="Path to base library API documentation file",
    )
    p.add_argument(
        "--base-lib",
        type=str,
        required=True,
        help="Path to base library Python code file",
    )
    p.add_argument(
        "--domain-description",
        type=str,
        default="",
        help="Brief description of the domain (e.g., 'hexagonal board drawing', 'robot control', 'data visualization')",
    )

    # Batch processing
    p.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help="Number of instructions per batch for hierarchical analysis",
    )
    p.add_argument(
        "--meta-batch-size",
        type=int,
        default=10,
        help="Number of summaries per meta-batch",
    )

    # LLM config
    p.add_argument("--model", default="gpt-4o", help="LLM model to use")
    p.add_argument("--temperature", type=float, default=0.7, help="LLM temperature")
    p.add_argument(
        "--max-tokens", type=int, default=2000, help="Max tokens for LLM responses"
    )

    # Vision
    p.add_argument(
        "--vision",
        action="store_true",
        help="Include board images in prompts for API discovery",
    )

    # Refinement
    p.add_argument(
        "--refinement-iterations",
        type=int,
        default=1,
        help="Number of refinement rounds in stage 2",
    )

    # Output
    p.add_argument(
        "--experiment-name",
        type=str,
        required=True,
        help="Name for this library generation experiment",
    )
    p.add_argument(
        "--output-dir",
        type=str,
        default="generated_libs",
        help="Base directory for generated libraries",
    )

    # Ablation controls
    p.add_argument(
        "--ablation",
        type=str,
        nargs="*",
        choices=["singleshot", "no-refinement"],
        default=[],
        help="Ablation mode(s): 'singleshot' (no hierarchical batching in Stage 1), 'no-refinement' (skip Stage 2). Can specify multiple.",
    )

    # Misc
    p.add_argument("--seed", type=int, default=42, help="Random seed")
    p.add_argument(
        "--workers",
        "-j",
        type=int,
        default=1,
        help="Number of parallel workers for batch processing",
    )

    return p.parse_args()
