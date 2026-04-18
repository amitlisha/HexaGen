"Full mode runner - single-shot execution of all instructions."

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
    simplify_traceback,
)
from constants.constants import WIDTH, HEIGHT
from metrics import evaluate_prediction


def build_code_full_prompt(
    cfg: argparse.Namespace,
    user_tmpl: str,
    instructions: List[str],
    code_so_far: str,
    input_grid_2d: Optional[List[List[int]]] = None,
) -> str:
    """Build the first-attempt prompt for code-full mode (no error feedback)."""
    todo_block = "\n".join(f"    # TODO: {txt}" for txt in instructions)
    return (
        user_tmpl.replace("{HISTORY_BLOCK}", "(none – full run)")
        .replace("{CODE_SO_FAR}", code_so_far.rstrip())
        .replace("{NEXT_STEP}", todo_block)
    )


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
    prefetched_response: Optional[Dict] = None,
) -> Dict:
    """
    Single-shot prompt that passes ALL instructions as one indented block.
    Includes retry logic with error feedback similar to step mode.
    """
    todo_block = "\n".join(f"    # TODO: {txt}" for txt in instructions)

    attempt = 0
    last_exc: Optional[str] = None
    last_code: Optional[str] = None
    last_warning: Optional[str] = None

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
                "   ### Your previous code\n"
                "   ```python\n"
                f"{textwrap.indent(last_code.strip(), '    ')}\n"
                "   ```\n\n"
                "   ### Previous execution error\n"
                f"{textwrap.indent(last_exc.strip(), '    ')}\n\n"
                "   ### Fix instructions\n"
                "   Analyze the error in your previous code and fix it. Do NOT repeat the same mistake.\n"
            )
        if last_warning:
            prompt += (
                "\n\n"
                "   ### Your previous code\n"
                "   ```python\n"
                f"{textwrap.indent(last_code.strip(), '    ')}\n"
                "   ```\n\n"
                "   ### Hexagen library warnings\n"
                "   Your code executed but the hexagen library raised the following warnings,\n"
                "   indicating incorrect API usage that may produce wrong results:\n"
                f"{textwrap.indent(last_warning.strip(), '    ')}\n\n"
                "   ### Fix instructions\n"
                "   Fix your code to avoid these warnings. Do NOT repeat the same mistake.\n"
            )

        if prefetched_response is not None and attempt == 1:
            resp = prefetched_response
        else:
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
        board_pred, err, hexagen_warnings = run_with_timeout(new_code, cfg.exec_timeout, cfg.lib_file)

        if err is None:
            # Code executed — check for hexagen warnings
            if hexagen_warnings and (not cfg.retries or attempt < cfg.retries):
                # Warnings present and retries remain — retry with warning feedback
                last_exc = None
                last_warning = "\n".join(f"- {w}" for w in hexagen_warnings)
                last_code = append
                log["warnings"] = hexagen_warnings
                continue

            # Accept result (no warnings, or last retry with warnings)
            if hexagen_warnings:
                log["warnings"] = hexagen_warnings
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
            last_exc = simplify_traceback(err)
            last_code = append
            last_warning = None
            log["traceback"] = last_exc

            # Check if we should retry
            if cfg.retries and attempt >= cfg.retries:
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
