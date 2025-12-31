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
from prompts import make_tile_prompt
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
) -> tuple[Dict, bool, List[int], Optional[Path]]:
    """Prompt GPT for tile predictions and update board state."""
    attempt = 0

    while True:
        attempt += 1
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

        tiles = parse_tile_actions(resp["text"])
        new_board = board.copy()
        for r, c, col in tiles:
            if 1 <= r <= HEIGHT and 1 <= c <= WIDTH and col in COLORS:
                idx = (r - 1) * WIDTH + (c - 1)
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

        plot_path = out_dir / f"{run_ts}_plot_{step_idx:02}_{attempt:02}.png"
        plot_with_gold_path = out_dir / (
            f"{run_ts}_plot_{step_idx:02}_{attempt:02}_gold.png"
        )
        save_plot(new_board, None, plot_path)
        save_plot(new_board, gold_board, plot_with_gold_path)
        return log, True, new_board, plot_path
