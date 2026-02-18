"""Code-step-full mode: all instructions visible, solve one at a time with emphasis on concise code."""

from __future__ import annotations

import argparse
import textwrap
from pathlib import Path
from typing import Dict, List, Optional

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from llm_wrapper import call_llm
from runner_utils import (
    _inject_custom_lib,
    extract_code,
    save_script,
    save_plot,
    run_with_timeout,
    fix_missing_tail_indent,
)
from constants.constants import WIDTH, HEIGHT
from prompts import make_code_step_full_prompt
from metrics import evaluate_prediction


def run_code_step_full(
    cfg: argparse.Namespace,
    sys_prompt: str,
    user_tmpl: str,
    instruction: str,
    all_instructions: List[str],
    history: List[str],
    code: str,
    gold_board: List[int],
    prev_gold_board: List[int],
    image_path: Optional[Path],
    out_dir: Path,
    step_idx: int,
    run_ts: str,
) -> tuple[Dict, bool, str, Optional[Path]]:
    """Run one code-completion step with all instructions visible and return updated script and log."""
    from runner_utils import exec_snippet

    attempt = 0
    last_exc: Optional[str] = None
    prev_pred_board: List[int]
    try:
        # Inject custom library if provided
        if cfg.lib_file:
            _inject_custom_lib(cfg.lib_file)

        ns_prev: Dict[str, object] = {}
        exec_snippet(code, ns_prev)
        prev_pred_board = ns_prev["board_state"]
    except Exception:
        prev_pred_board = [0] * (WIDTH * HEIGHT)
    while True:
        attempt += 1

        code_with_todo = f"{code.rstrip()}\n"
        prompt = make_code_step_full_prompt(
            instr=instruction,
            history=history,
            all_instructions=all_instructions,
            template=user_tmpl,
            code=code_with_todo,
        )

        if last_exc:
            prompt += (
                "\n\n"
                "   ### Previous execution error\n"
                f"{textwrap.indent(last_exc.strip(), '    ')}"
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

        append = extract_code(resp["text"])
        new_script = fix_missing_tail_indent(f"{code.rstrip()}\n    {append}")

        if "board_state = g.board_state" not in new_script:
            new_script += "\nboard_state = g.board_state"

        _ = save_script(out_dir, run_ts, step_idx, attempt, new_script, kind="code-step-full")

        log = {
            "step": step_idx,
            "attempt": attempt,
            "usage": resp["usage"],
            "code": append,
            "valid": False,
            "correct": False,
        }

        # execute with timeout
        board_pred, err = run_with_timeout(new_script, cfg.exec_timeout, cfg.lib_file)

        if err is None:
            log["valid"] = True
            log.update(
                evaluate_prediction(
                    prev_pred_board, board_pred, prev_gold_board, gold_board
                )
            )
            plot_path = out_dir / f"{run_ts}_plot_{step_idx:02}_{attempt:02}.png"
            plot_with_gold_path = (
                out_dir / f"{run_ts}_plot_{step_idx:02}_{attempt:02}_gold.png"
            )
            save_plot(board_pred, None, plot_path)
            save_plot(board_pred, gold_board, plot_with_gold_path)
            return log, True, new_script, plot_path
        else:
            last_exc = err
            log["traceback"] = last_exc
            if cfg.retries and attempt >= cfg.retries:
                # Compute gold counts so failed runs still contribute to
                # aggregate recall (board_g / action_g).
                board_g = sum(1 for t in gold_board if t != 0)
                action_g = sum(
                    1 for a, b in zip(prev_gold_board, gold_board) if a != b
                )
                log.update(
                    {
                        "precision_board": 0.0,
                        "recall_board": 0.0,
                        "f1_board": 0.0,
                        "exact_board": False,
                        "precision_action": 0.0,
                        "recall_action": 0.0,
                        "f1_action": 0.0,
                        "exact_action": False,
                        "board_tp": 0,
                        "board_p": 0,
                        "board_g": board_g,
                        "action_tp": 0,
                        "action_p": 0,
                        "action_g": action_g,
                    }
                )
                return log, False, code, image_path  # keep previous image
