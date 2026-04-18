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
        choices=["0", "1", "2", "3", "all"],
        default="all",
        help="Which stage to run (0=minimal lib, 1=discovery, 2=implement, "
        "3=docs, all=run all stages)",
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
        default="drawing colored shapes and patterns on a hexagonal tiled board.",
        help="Brief description of the domain (e.g., 'hexagonal board drawing', 'robot control', 'data visualization')",
    )

    # Batch API processing
    p.add_argument(
        "--batch",
        action="store_true",
        help="Use LLM Batch API instead of synchronous calls",
    )
    p.add_argument(
        "--batch-resume",
        type=str,
        default=None,
        help="Resume a previously submitted batch using its job ID",
    )
    p.add_argument(
        "--batch-poll-interval",
        type=int,
        default=60,
        help="Polling interval in seconds for the Batch API",
    )
    p.add_argument(
        "--batch-timeout",
        type=int,
        default=86400,
        help="Timeout in seconds for the Batch API polling",
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
        "--max-tokens", type=int, default=None, help="Max tokens for LLM responses (default: no limit)"
    )
    p.add_argument(
        "--thinking-effort",
        type=str,
        default=None,
        choices=["low", "medium", "high"],
        help="Reasoning effort for OpenAI models",
    )
    p.add_argument(
        "--thinking-level",
        type=str,
        default=None,
        choices=["low", "medium", "high"],
        help="Thinking level for Gemini reasoning models",
    )
    p.add_argument(
        "--base-url",
        type=str,
        default=None,
        help="Base URL for the LLM API (e.g., http://localhost:8000/v1 for local models)",
    )
    p.add_argument(
        "--api-key",
        type=str,
        default=None,
        help="API key for the LLM provider (overrides environment variables)",
    )

    # Vision
    p.add_argument(
        "--vision",
        action="store_true",
        help="Include board images in prompts for API discovery",
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

    # Input/Output inclusion
    p.add_argument(
        "--include-io",
        action="store_true",
        help="Include input/output states alongside instructions in Stage 1 analysis",
    )

    # Semantic batching
    p.add_argument(
        "--semantic-batching",
        action="store_true",
        help="Use embedding-based clustering for Stage 1 batching instead of random chunking",
    )
    p.add_argument(
        "--embedding-model",
        type=str,
        default="BAAI/bge-m3",
        help="Sentence-transformers model for semantic batching (default: BAAI/bge-m3)",
    )

    # Ablation controls
    p.add_argument(
        "--ablation",
        type=str,
        nargs="*",
        choices=["singleshot"],
        default=[],
        help="Ablation mode: 'singleshot' (no hierarchical batching in Stage 1).",
    )

    # Timeouts
    p.add_argument(
        "--request-timeout",
        type=int,
        default=300,
        help="Timeout in seconds for individual LLM API requests (default: 300). "
        "Lower for local models to avoid retry storms with many workers.",
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
