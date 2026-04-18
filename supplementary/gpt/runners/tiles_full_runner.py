"""Tiles-full mode runner - predict all tiles at once for all instructions."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from llm_wrapper import call_llm
from runner_utils import parse_tile_actions, save_plot
from constants.constants import COLORS, WIDTH, HEIGHT
from metrics import evaluate_prediction


def build_tiles_full_prompt(
    cfg: argparse.Namespace,
    user_tmpl: str,
    instructions: List[str],
    input_grid_2d: Optional[List[List[int]]] = None,
) -> str:
    """Build the first-attempt prompt for tiles-full mode."""
    instructions_block = "\n".join(f"{i+1}. {txt}" for i, txt in enumerate(instructions))
    return (
        user_tmpl.replace("{HISTORY_BLOCK}", "(none – full run)")
        .replace("{NEXT_STEP}", instructions_block)
    )


def run_tiles_full(
    cfg: argparse.Namespace,
    sys_prompt: str,
    user_tmpl: str,
    instructions: List[str],
    gold_final: List[int],
    image_path: Optional[Path],
    task_dir: Path,
    run_ts: str,
    prefetched_response: Optional[Dict] = None,
) -> Dict:
    """
    Single-shot prompt that passes ALL instructions as one block.
    Model predicts tiles directly for all instructions combined.
    """
    # Build prompt and get response (or use prefetched from batch)
    if prefetched_response is not None:
        resp = prefetched_response
    else:
        prompt = build_tiles_full_prompt(cfg, user_tmpl, instructions)
        resp = call_llm(
            prompt=prompt,
            system_prompt=sys_prompt,
            model=cfg.model,
            temperature=cfg.temperature,
            max_tokens=cfg.max_tokens,
            seed=cfg.seed,
            images=[str(image_path)] if image_path else None,
            reasoning_effort=getattr(cfg, "reasoning_effort", None),
            thinking_budget=getattr(cfg, "thinking_budget", None),
            thinking_level=getattr(cfg, "thinking_level", None),
        )

    # Parse tile predictions
    predicted_dims, tiles = parse_tile_actions(resp["text"])

    # Create board
    board = [0] * (WIDTH * HEIGHT)

    for r, c, col in tiles:
        if 1 <= r <= HEIGHT and 1 <= c <= WIDTH and col in COLORS:
            idx = (r - 1) * WIDTH + (c - 1)
            board[idx] = COLORS.index(col)

    # Evaluate against gold final board
    blank_board = [0] * (WIDTH * HEIGHT)
    metrics = evaluate_prediction(
        blank_board,
        board,
        blank_board,
        gold_final,
    )

    log = {
        "attempt": 1,
        "tiles": tiles,
        "valid": True,
        "usage": resp["usage"],
        **metrics,
    }

    # Save plots
    plot_path = task_dir / f"{run_ts}_plot_tiles_full_01.png"
    save_plot(board, gold_final, plot_path)

    return log
