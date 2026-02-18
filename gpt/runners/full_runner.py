"""Full mode runner - single-shot execution of all instructions."""

from __future__ import annotations

import argparse
import sys
import textwrap
from pathlib import Path
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from llm_wrapper import call_llm
from runner_utils import (
    extract_code,
    save_script,
    save_plot,
    run_with_timeout,
    _inject_custom_lib,
)
from constants.constants import WIDTH, HEIGHT
from metrics import evaluate_prediction


def run_full(
    cfg: argparse.Namespace,
    sys_prompt: str,
    user_tmpl: str,
    instructions: List[str],
    code_so_far: str,
    gold_final: List[int],
    image_path: Optional[Path],
    task_dir: Path,
    run_ts: str,
) -> Dict:
    """
    Single-shot prompt that passes ALL instructions as one indented block.
    Includes retry logic with error feedback similar to step mode.
    """
    todo_block = "\n".join(f"    # TODO: {txt}" for txt in instructions)

    attempt = 0
    last_exc: Optional[str] = None

    while True:
        attempt += 1

        prompt = (
            user_tmpl.replace("{HISTORY_BLOCK}", "(none – full run)")
            .replace("{CODE_SO_FAR}", code_so_far.rstrip())
            .replace("{NEXT_STEP}", todo_block)
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
        new_code = f"{code_so_far.rstrip()}\n    {append}"

        if "board_state = g.board_state" not in new_code:
            new_code += "\nboard_state = g.board_state"

        _ = save_script(
            task_dir, run_ts, step=0, attempt=attempt, code=new_code, kind="full"
        )

        log = {
            "attempt": attempt,
            "code": new_code,
            "valid": False,
            "correct": False,
            "usage": resp["usage"],
        }

        # Execute with timeout
        board_pred, err = run_with_timeout(new_code, cfg.exec_timeout, cfg.lib_file)

        if err is None:
            log["valid"] = True
            log.update(
                evaluate_prediction(
                    [0] * (WIDTH * HEIGHT),
                    board_pred,
                    [0] * (WIDTH * HEIGHT),
                    gold_final,
                )
            )
            save_plot(
                board_pred,
                gold_final,
                task_dir / f"{run_ts}_plot_full_{attempt:02}.png",
            )
            return log
        else:
            last_exc = err
            log["traceback"] = last_exc

            # Check if we should retry
            if cfg.retries and attempt >= cfg.retries:
                # Compute gold counts so failed runs still contribute to
                # aggregate recall (board_g / action_g).
                board_g = sum(1 for t in gold_final if t != 0)
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
                        "action_g": board_g,
                    }
                )
                return log
