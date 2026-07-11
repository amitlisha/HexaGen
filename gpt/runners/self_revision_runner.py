"""Self-revision runner — unified multi-turn conversational loop.

The model sees errors and rendered board images in a single shared conversation
context, revising freely until it signals [SATISFIED] or the turn budget runs out.

Supports code-full, tiles-full, and python-full modes for both hexagons and LARC.
Claude Code (agentic) models are not supported — callers should skip this runner.
"""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).parent.parent))

from llm_wrapper import call_llm
from runner_utils import (
    parse_tile_actions,
    run_with_timeout,
    save_plot,
    save_script,
    simplify_traceback,
    extract_code,
)
from constants.constants import COLORS, WIDTH, HEIGHT
from metrics import evaluate_prediction

# ── Satisfaction signal ───────────────────────────────────────────────────────

SATISFIED_TOKEN = "[SATISFIED]"

SELF_REVISION_SYSTEM_ADDENDUM = (
    "\n\n---\n"
    "SELF-REVISION MODE: After each attempt you will receive feedback — either "
    "an execution error or an image of the board your solution produced. "
    "Use this feedback to revise your answer. "
    f"When you are satisfied that your solution is correct, include the token "
    f"{SATISFIED_TOKEN} anywhere in your response and the session will end."
)

# ── Feedback message builders ─────────────────────────────────────────────────


def _build_error_feedback(error: str, code: str) -> str:
    return (
        "Your previous solution failed to execute:\n\n"
        f"### Error\n{error.strip()}\n\n"
        "Please fix the issue and output your complete revised solution.\n"
        f"When satisfied with your answer, include {SATISFIED_TOKEN} in your response."
    )


def _build_visual_feedback(instructions_text: str) -> str:
    return (
        "The image shows the board your latest solution produced.\n"
        "Review it carefully against the original instructions.\n"
        f"If it looks correct, include {SATISFIED_TOKEN} in your response.\n"
        "Otherwise, revise your solution.\n\n"
        f"Original instructions:\n{instructions_text}"
    )


# ── Per-mode execution helpers ────────────────────────────────────────────────


def _exec_code_full_hexagen(
    resp: Dict[str, Any],
    cfg: argparse.Namespace,
    code_so_far: str,
) -> Tuple[Optional[List[int]], Optional[str]]:
    """Execute code-full response for Hexagons. Returns (board, error)."""
    if resp.get("solution_code"):
        new_code = resp["solution_code"]
        if "board_state = g.board_state" not in new_code:
            new_code += "\nboard_state = g.board_state"
    else:
        append = extract_code(resp["text"])
        new_code = f"{code_so_far.rstrip()}\n    {append}"
        if "board_state = g.board_state" not in new_code:
            new_code += "\nboard_state = g.board_state"

    board, err, _warnings = run_with_timeout(new_code, cfg.exec_timeout, cfg.lib_file)
    if err is not None:
        return None, simplify_traceback(err)
    return board, None


def _exec_code_full_larc(
    resp: Dict[str, Any],
    cfg: argparse.Namespace,
    input_grid_2d: List[List[int]],
    width: int,
    height: int,
) -> Tuple[Optional[List[int]], Optional[str]]:
    """Execute code-full response for LARC. Returns (flat_board, error)."""
    from runners.full_runner import extract_and_execute_dsl

    try:
        board = extract_and_execute_dsl(
            resp["text"], cfg.exec_timeout, input_grid_2d,
            output_width=width, output_height=height,
        )
        return board, None
    except Exception as e:
        return None, str(e)


def _exec_tiles_full(
    resp: Dict[str, Any],
    cfg: argparse.Namespace,
    width: int,
    height: int,
) -> Tuple[Optional[List[int]], Optional[str]]:
    """Parse tiles and build board. Returns (board, error_or_None)."""
    predicted_dims, tiles = parse_tile_actions(resp["text"])

    board = [0] * (width * height)
    if cfg.dataset == "larc":
        if predicted_dims is None:
            return board, "Model did not provide output dimensions."
        ph, pw = predicted_dims
        if ph != height or pw != width:
            return board, (
                f"Dimension mismatch: predicted ({ph}, {pw}), expected ({height}, {width})."
            )
        for r, c, col in tiles:
            if 1 <= r <= height and 1 <= c <= width and isinstance(col, int) and 0 <= col <= 9:
                board[(r - 1) * width + (c - 1)] = col
    else:
        for r, c, col in tiles:
            if 1 <= r <= height and 1 <= c <= width and col in COLORS:
                board[(r - 1) * width + (c - 1)] = COLORS.index(col)

    return board, None


def _exec_python_full_hexagen(
    resp: Dict[str, Any],
    cfg: argparse.Namespace,
    width: int,
    height: int,
) -> Tuple[Optional[List[int]], Optional[str]]:
    """Execute python-full response for Hexagons. Returns (board, error)."""
    from runners.python_full_runner import extract_and_execute_python

    code_text = resp.get("solution_code") or resp["text"]
    try:
        tiles = extract_and_execute_python(code_text, timeout=cfg.exec_timeout)
    except Exception as e:
        return None, str(e)

    board = [0] * (width * height)
    for r, c, col in tiles:
        if 1 <= r <= height and 1 <= c <= width and col in COLORS:
            board[(r - 1) * width + (c - 1)] = COLORS.index(col)
    return board, None


def _exec_python_full_larc(
    resp: Dict[str, Any],
    cfg: argparse.Namespace,
    input_grid_2d: List[List[int]],
    width: int,
    height: int,
) -> Tuple[Optional[List[int]], Optional[str]]:
    """Execute python-full response for LARC. Returns (flat_board, error)."""
    from runners.python_full_runner import execute_larc_python

    try:
        board = execute_larc_python(resp["text"], cfg.exec_timeout, input_grid_2d)
        return board, None
    except Exception as e:
        return None, str(e)


# ── Board rendering ───────────────────────────────────────────────────────────


def _render_board(
    board: List[int],
    gold: List[int],
    task_dir: Path,
    run_ts: str,
    turn: int,
    dataset: str,
    width: int,
    height: int,
) -> Optional[Path]:
    """Render board to a PNG and return its path, or None on failure."""
    plot_path = task_dir / f"{run_ts}_sr_turn_{turn:02}.png"
    try:
        if dataset == "larc":
            from larc_plot import save_larc_plot
            save_larc_plot(board, gold, plot_path, width, height)
        else:
            save_plot(board, gold, plot_path)
        return plot_path
    except Exception as e:
        print(f"  [self-revision] Warning: could not render board at turn {turn}: {e}")
        return None


# ── Main entry point ──────────────────────────────────────────────────────────


def run_with_self_revision(
    cfg: argparse.Namespace,
    sys_prompt: str,
    user_tmpl: str,
    instructions: List[str],
    gold_final: List[int],
    image_path: Optional[Path],
    task_dir: Path,
    run_ts: str,
    # Shared optional kwargs forwarded from experiment.py
    code_so_far: str = "",
    initial_board: Optional[List[int]] = None,
    input_grid_2d: Optional[List[List[int]]] = None,
    width: Optional[int] = None,
    height: Optional[int] = None,
    prefetched_response: Optional[Dict] = None,
) -> Dict[str, Any]:
    """Run a full mode (code/tiles/python) with the self-revision conversation loop."""

    mode = cfg.mode
    dataset = cfg.dataset
    max_turns = getattr(cfg, "max_revision_turns", 10)

    # Board dimensions
    if width is None:
        width = WIDTH
    if height is None:
        height = HEIGHT
    if initial_board is None:
        initial_board = [0] * (width * height)

    # Build initial user prompt using the same builders as the original runners
    instructions_text = "\n".join(f"{i+1}. {txt}" for i, txt in enumerate(instructions))
    if mode == "code-full":
        from runners.full_runner import build_code_full_prompt
        initial_prompt = build_code_full_prompt(cfg, user_tmpl, instructions, code_so_far, input_grid_2d)
    elif mode == "tiles-full":
        from runners.tiles_full_runner import build_tiles_full_prompt
        initial_prompt = build_tiles_full_prompt(cfg, user_tmpl, instructions, input_grid_2d)
    else:  # python-full
        from runners.python_full_runner import build_python_full_prompt
        initial_prompt = build_python_full_prompt(cfg, user_tmpl, instructions, input_grid_2d)

    # Augment system prompt with self-revision instructions
    sys_prompt_sr = sys_prompt + SELF_REVISION_SYSTEM_ADDENDUM

    # Conversation state
    messages: List[Dict[str, Any]] = []
    turn_logs: List[Dict[str, Any]] = []
    last_valid_board: Optional[List[int]] = None
    last_valid_turn: Optional[int] = None
    satisfied = False
    turn = 0

    feedback_prompt: Optional[str] = None
    feedback_images: Optional[List[str]] = None

    blank = [0] * len(gold_final)

    while turn < max_turns and not satisfied:
        turn += 1

        if turn == 1:
            current_prompt = initial_prompt
            current_images = [str(image_path)] if image_path and cfg.vision else None
        else:
            current_prompt = feedback_prompt
            current_images = feedback_images

        # Call LLM (use prefetched response on turn 1 if provided)
        if prefetched_response is not None and turn == 1:
            resp = prefetched_response
        else:
            resp = call_llm(
                prompt=current_prompt,
                messages=messages,
                system_prompt=sys_prompt_sr,
                model=cfg.model,
                temperature=cfg.temperature,
                max_tokens=cfg.max_tokens,
                seed=cfg.seed,
                images=current_images,
                reasoning_effort=getattr(cfg, "reasoning_effort", None),
                thinking_budget=getattr(cfg, "thinking_budget", None),
                thinking_level=getattr(cfg, "thinking_level", None),
            )

        # Build the user message content for history (text-only; images tracked separately)
        messages.append({"role": "user", "content": current_prompt})
        messages.append({"role": "assistant", "content": resp["text"]})

        # Check for satisfaction signal — only honour if we already have a valid board
        satisfied_signal = SATISFIED_TOKEN in resp["text"]
        if satisfied_signal and last_valid_board is not None:
            satisfied = True
            # Skip execution: model is done, keep the last valid board.
            turn_logs.append({
                "turn": turn,
                "valid": True,
                "satisfied_signal": True,
                "error": None,
                "usage": resp["usage"],
            })
            print(f"  [self-revision] model signalled {SATISFIED_TOKEN} at turn {turn}, stopping")
            break

        # Save script for debugging
        save_script(task_dir, run_ts, step=0, attempt=turn, code=resp["text"], kind="sr")

        # Try to execute
        board: Optional[List[int]] = None
        error: Optional[str] = None

        if mode == "code-full":
            if dataset == "larc":
                board, error = _exec_code_full_larc(resp, cfg, input_grid_2d, width, height)
            else:
                board, error = _exec_code_full_hexagen(resp, cfg, code_so_far)
        elif mode == "tiles-full":
            board, error = _exec_tiles_full(resp, cfg, width, height)
        else:  # python-full
            if dataset == "larc":
                board, error = _exec_python_full_larc(resp, cfg, input_grid_2d, width, height)
            else:
                board, error = _exec_python_full_hexagen(resp, cfg, width, height)

        # Build per-turn log entry
        turn_log: Dict[str, Any] = {
            "turn": turn,
            "valid": error is None and board is not None,
            "satisfied_signal": satisfied_signal,
            "error": error,
            "usage": resp["usage"],
        }
        if error is None and board is not None:
            eval_board = board if len(board) == len(gold_final) else blank
            turn_log.update(evaluate_prediction(blank, eval_board, blank, gold_final))
        turn_logs.append(turn_log)

        if error is not None or board is None:
            # Invalid — prepare error feedback for next turn
            feedback_prompt = _build_error_feedback(error or "Unknown execution error.", resp["text"])
            feedback_images = None
            print(f"  [self-revision] turn {turn}: exec error → {str(error)[:120]}")
        else:
            # Valid board
            last_valid_board = board
            last_valid_turn = turn

            # Render board image for next feedback turn
            board_img = _render_board(board, gold_final, task_dir, run_ts, turn, dataset, width, height)
            feedback_prompt = _build_visual_feedback(instructions_text)
            feedback_images = [str(board_img)] if board_img else None

            print(f"  [self-revision] turn {turn}: valid board produced")

    # ── Build final result ────────────────────────────────────────────────────

    if last_valid_board is None:
        # Never produced a valid board
        final_metrics = evaluate_prediction(blank, blank, blank, gold_final)
        return {
            "self_revision": True,
            "total_turns": turn,
            "satisfied": False,
            "last_valid_turn": None,
            "attempt": turn,
            "valid": False,
            "usage": _merge_usage([tl["usage"] for tl in turn_logs]),
            "turns": turn_logs,
            **final_metrics,
        }

    eval_board = last_valid_board if len(last_valid_board) == len(gold_final) else blank
    final_metrics = evaluate_prediction(blank, eval_board, blank, gold_final)

    # Save final board plot
    _render_board(eval_board, gold_final, task_dir, run_ts, turn + 1, dataset, width, height)

    return {
        "self_revision": True,
        "total_turns": turn,
        "satisfied": satisfied,
        "last_valid_turn": last_valid_turn,
        "attempt": turn,
        "valid": True,
        "usage": _merge_usage([tl["usage"] for tl in turn_logs]),
        "turns": turn_logs,
        **final_metrics,
    }


# ── Utility ───────────────────────────────────────────────────────────────────


def _merge_usage(per_turn: List[Dict]) -> Dict[str, int]:
    """Sum token counts across all turns."""
    merged: Dict[str, int] = {}
    for u in per_turn:
        for k, v in u.items():
            merged[k] = merged.get(k, 0) + (v if isinstance(v, (int, float)) else 0)
    return merged
