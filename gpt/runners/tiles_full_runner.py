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
from prompts import make_larc_tile_prompt
from metrics import evaluate_prediction


def run_tiles_full(
    cfg: argparse.Namespace,
    sys_prompt: str,
    user_tmpl: str,
    instructions: List[str],
    gold_final: List[int],
    image_path: Optional[Path],
    task_dir: Path,
    run_ts: str,
    initial_board: List[int] = None,
    width: int = None,
    height: int = None,
    input_grid_2d: List[List[int]] = None,
) -> Dict:
    """
    Single-shot prompt that passes ALL instructions as one block.
    Model predicts tiles directly for all instructions combined.

    Args:
        initial_board: Initial board state (for reference, LARC only)
        width: Board width (defaults to constants.WIDTH if None)
        height: Board height (defaults to constants.HEIGHT if None)
    """
    if width is None or height is None:
        width = WIDTH if width is None else width
        height = HEIGHT if height is None else height

    if initial_board is None:
        initial_board = [0] * (width * height)

    # Format all instructions as a numbered block
    instructions_block = "\n".join(f"{i+1}. {txt}" for i, txt in enumerate(instructions))

    # Build the prompt based on dataset
    if cfg.dataset == "larc":
        # For LARC, single instruction with input board (LARC tasks have only 1 instruction)
        prompt = make_larc_tile_prompt(instructions_block, input_grid_2d, user_tmpl)
    else:
        # For Hexagons, use standard format
        prompt = (
            user_tmpl.replace("{HISTORY_BLOCK}", "(none – full run)")
            .replace("{NEXT_STEP}", instructions_block)
        )

    resp = call_llm(
        prompt=prompt,
        system_prompt=sys_prompt,
        model=cfg.model,
        temperature=cfg.temperature,
        max_tokens=cfg.max_tokens,
        seed=cfg.seed,
        images=[str(image_path)] if image_path else None,
    )

    # Parse tile predictions
    predicted_dims, tiles = parse_tile_actions(resp["text"])

    # For LARC: validate dimensions and apply strict dimension check
    dimension_match = True
    if cfg.dataset == "larc":
        if predicted_dims is None:
            # LLM didn't provide dimensions - mark as failure
            dimension_match = False
            predicted_height, predicted_width = 0, 0
        else:
            predicted_height, predicted_width = predicted_dims
            # Check if dimensions match gold
            if predicted_height != height or predicted_width != width:
                dimension_match = False
            else:
                # Dimensions match, use predicted dimensions
                width, height = predicted_width, predicted_height

    # Create board with appropriate dimensions
    board = [0] * (width * height)

    # Apply tiles only if dimensions match (for LARC) or always (for Hexagons)
    if cfg.dataset != "larc" or dimension_match:
        for r, c, col in tiles:
            # Validate tile based on dataset
            if cfg.dataset == "larc":
                # LARC: col is integer 0-9
                if 1 <= r <= height and 1 <= c <= width and isinstance(col, int) and 0 <= col <= 9:
                    idx = (r - 1) * width + (c - 1)
                    board[idx] = col
            else:
                # Hexagons: col is color name string
                if 1 <= r <= height and 1 <= c <= width and col in COLORS:
                    idx = (r - 1) * width + (c - 1)
                    board[idx] = COLORS.index(col)

    # Evaluate against gold final board
    metrics = evaluate_prediction(
        initial_board,
        board,
        initial_board,
        gold_final,
    )

    log = {
        "attempt": 1,
        "tiles": tiles,
        "valid": True,
        "usage": resp["usage"],
        **metrics,
    }

    # Add LARC-specific dimension tracking
    if cfg.dataset == "larc":
        log["dimension_match"] = dimension_match
        log["predicted_dimensions"] = predicted_dims if predicted_dims else (0, 0)
        log["gold_dimensions"] = (height, width)

    # Save plots
    plot_path = task_dir / f"{run_ts}_plot_tiles_full_01.png"
    if cfg.dataset == "larc":
        from larc_plot import save_larc_plot

        save_larc_plot(board, gold_final, plot_path, width, height)
    else:
        save_plot(board, gold_final, plot_path)

    return log
