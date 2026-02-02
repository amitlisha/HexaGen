"""Tiles mode runner - predict tiles directly instead of code."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from llm_wrapper import call_llm
from runner_utils import parse_tile_actions, save_plot
from constants.constants import COLORS, WIDTH, HEIGHT
from prompts import make_tile_prompt, make_larc_tile_prompt
from metrics import evaluate_prediction


def run_tile_step(
    cfg: argparse.Namespace,
    sys_prompt: str,
    user_tmpl: str,
    instruction: str,
    history: List[str],
    board: List[int],
    gold_board: List[int],
    prev_gold_board: List[int],
    image_path: Optional[Path],
    out_dir: Path,
    step_idx: int,
    run_ts: str,
    width: int = None,
    height: int = None,
    input_grid_2d: List[List[int]] = None,
) -> tuple[Dict, bool, List[int], Optional[Path]]:
    """Prompt LLM for tile predictions and update board state.

    Args:
        width: Board width (defaults to constants.WIDTH if None)
        height: Board height (defaults to constants.HEIGHT if None)
    """
    if width is None or height is None:
        width = WIDTH if width is None else width
        height = HEIGHT if height is None else height

    attempt = 0

    while True:
        attempt += 1

        # Build prompt based on dataset
        if cfg.dataset == "larc":
            # For LARC, pass 2D input grid to the prompt
            prompt = make_larc_tile_prompt(instruction, input_grid_2d, user_tmpl)
        else:
            # For Hexagons, use standard tile prompt
            prompt = make_tile_prompt(instruction, history, user_tmpl)

        resp = call_llm(
            prompt=prompt,
            system_prompt=sys_prompt,
            model=cfg.model,
            temperature=cfg.temperature,
            max_tokens=cfg.max_tokens,
            seed=cfg.seed,
            images=[str(image_path)] if image_path else None,
        )

        predicted_dims, tiles = parse_tile_actions(resp["text"])

        # For LARC: validate dimensions
        dimension_match = True
        if cfg.dataset == "larc":
            if predicted_dims is None:
                dimension_match = False
            else:
                predicted_height, predicted_width = predicted_dims
                if predicted_height != height or predicted_width != width:
                    dimension_match = False

        # For LARC: ignore board state, create new board
        # For Hexagons: modify existing board
        if cfg.dataset == "larc":
            new_board = [0] * (width * height)
        else:
            new_board = board.copy()

        # Apply tiles only if dimensions match (for LARC) or always (for Hexagons)
        if cfg.dataset != "larc" or dimension_match:
            for r, c, col in tiles:
                # Validate tile based on dataset
                if cfg.dataset == "larc":
                    # LARC: col is integer 0-9
                    if 1 <= r <= height and 1 <= c <= width and isinstance(col, int) and 0 <= col <= 9:
                        idx = (r - 1) * width + (c - 1)
                        new_board[idx] = col
                else:
                    # Hexagons: col is color name string
                    if 1 <= r <= height and 1 <= c <= width and col in COLORS:
                        idx = (r - 1) * width + (c - 1)
                        new_board[idx] = COLORS.index(col)

        metrics = evaluate_prediction(board, new_board, prev_gold_board, gold_board)
        log = {
            "step": step_idx,
            "attempt": attempt,
            "usage": resp["usage"],
            "tiles": tiles,
            "valid": True,
            **metrics,
        }

        # Add LARC-specific dimension tracking
        if cfg.dataset == "larc":
            log["dimension_match"] = dimension_match
            log["predicted_dimensions"] = predicted_dims if predicted_dims else (0, 0)
            log["gold_dimensions"] = (height, width)

        plot_path = out_dir / f"{run_ts}_plot_{step_idx:02}_{attempt:02}.png"
        plot_with_gold_path = out_dir / (
            f"{run_ts}_plot_{step_idx:02}_{attempt:02}_gold.png"
        )

        # Use appropriate plotting based on dataset
        if cfg.dataset == "larc":
            from larc_plot import save_larc_plot

            save_larc_plot(new_board, None, plot_path, width, height)
            save_larc_plot(new_board, gold_board, plot_with_gold_path, width, height)
        else:
            save_plot(new_board, None, plot_path)
            save_plot(new_board, gold_board, plot_with_gold_path)

        return log, True, new_board, plot_path
