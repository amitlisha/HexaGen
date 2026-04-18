"""Python-full mode runner - generate unrestricted Python code that outputs tiles."""

from __future__ import annotations

import argparse
import sys
import textwrap
from pathlib import Path
from typing import Dict, List, Optional
import re
import multiprocessing as mp

sys.path.insert(0, str(Path(__file__).parent.parent))

from llm_wrapper import call_llm
from runner_utils import save_plot, save_script
from constants.constants import COLORS, WIDTH, HEIGHT
from metrics import evaluate_prediction


def _python_exec_worker(code_str: str, queue):
    """Execute code in separate process and return tiles (module-level for pickling)."""
    try:
        namespace = {}
        exec(code_str, namespace)

        # Extract result from get_tiles() function
        if 'get_tiles' not in namespace:
            queue.put(("error", "Generated code must define a get_tiles() function"))
            return

        get_tiles_func = namespace['get_tiles']
        if not callable(get_tiles_func):
            queue.put(("error", "get_tiles must be a callable function"))
            return

        result = get_tiles_func()

        # Validate result format
        if not isinstance(result, list):
            queue.put(("error", f"get_tiles() must return a list, got {type(result)}"))
            return

        tiles = []
        for item in result:
            if not (isinstance(item, (list, tuple)) and len(item) == 3):
                queue.put(("error", f"Each tile must be a (row, col, color) tuple, got {item}"))
                return
            r, c, col = item
            if isinstance(col, int):
                tiles.append((int(r), int(c), col))
            else:
                tiles.append((int(r), int(c), str(col).lower()))

        queue.put(("ok", tiles))
    except Exception as e:
        queue.put(("error", f"Failed to execute generated code: {e}"))


def extract_and_execute_python(
    code: str, timeout: int = 10,
) -> List[tuple]:
    """
    Extract Python code, execute it with timeout, and return the result from get_tiles().

    Returns:
        List of (row, col, color) tuples
    """
    # Remove markdown code blocks if present
    code = re.sub(r'^```python\s*\n', '', code, flags=re.MULTILINE)
    code = re.sub(r'\n```\s*$', '', code, flags=re.MULTILINE)
    code = code.strip()

    # Execute with timeout
    ctx = mp.get_context("spawn")
    q = ctx.Queue()
    p = ctx.Process(target=_python_exec_worker, args=(code, q), daemon=True)
    p.start()
    p.join(timeout)

    if p.is_alive():
        p.terminate()
        p.join()
        raise TimeoutError(f"Code execution timed out after {timeout} seconds")

    try:
        status, result = q.get(timeout=10)
    except Exception:
        raise RuntimeError("Worker process died without returning result")
    if status == "error":
        raise RuntimeError(result)

    return result  # tiles list


# ── Main runner ──────────────────────────────────────────────────────────────


def build_python_full_prompt(
    cfg: argparse.Namespace,
    user_tmpl: str,
    instructions: List[str],
    input_grid_2d: Optional[List[List[int]]] = None,
) -> str:
    """Build the first-attempt prompt for python-full mode (no error feedback)."""
    instructions_block = "\n".join(f"{i+1}. {txt}" for i, txt in enumerate(instructions))
    return (
        user_tmpl.replace("{HISTORY_BLOCK}", "(none – full run)")
        .replace("{NEXT_STEP}", instructions_block)
    )


def run_python_full(
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
    Model generates Python code that computes tiles for all instructions.
    """
    instructions_block = "\n".join(f"{i+1}. {txt}" for i, txt in enumerate(instructions))

    attempt = 0
    last_exc: Optional[str] = None
    last_code: Optional[str] = None

    while True:
        attempt += 1

        prompt = (
            user_tmpl.replace("{HISTORY_BLOCK}", "(none – full run)")
            .replace("{NEXT_STEP}", instructions_block)
        )

        if last_exc:
            prompt += (
                "\n\n"
                "### Your previous code\n"
                "```python\n"
                f"{last_code.strip()}\n"
                "```\n\n"
                "### Previous execution error\n"
                f"{textwrap.indent(last_exc.strip(), '    ')}\n\n"
                "### Fix instructions\n"
                "    Analyze the error in your previous code and fix it. Do NOT repeat the same mistake.\n"
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

        try:
            tiles = extract_and_execute_python(
                resp["text"],
                timeout=cfg.exec_timeout,
            )
            valid = True
            error_msg = None
        except Exception as e:
            tiles = []
            valid = False
            error_msg = str(e)

        save_script(task_dir, run_ts, step=0, attempt=attempt, code=resp["text"], kind="python_full")

        if not valid:
            last_exc = error_msg
            last_code = resp["text"]

            if cfg.retries and attempt >= cfg.retries:
                blank_board = [0] * (WIDTH * HEIGHT)
                metrics = evaluate_prediction(
                    blank_board,
                    blank_board,
                    blank_board,
                    gold_final,
                )
                return {
                    "attempt": attempt,
                    "code": resp["text"],
                    "tiles": [],
                    "valid": False,
                    "usage": resp["usage"],
                    "error": error_msg,
                    **metrics,
                }

            continue

        # Build board from tiles
        board = [0] * (WIDTH * HEIGHT)
        for r, c, col in tiles:
            if 1 <= r <= HEIGHT and 1 <= c <= WIDTH and col in COLORS:
                idx = (r - 1) * WIDTH + (c - 1)
                board[idx] = COLORS.index(col)

        blank_board = [0] * (WIDTH * HEIGHT)
        metrics = evaluate_prediction(blank_board, board, blank_board, gold_final)

        log = {
            "attempt": attempt,
            "code": resp["text"],
            "tiles": tiles,
            "valid": valid,
            "usage": resp["usage"],
            **metrics,
        }

        plot_path = task_dir / f"{run_ts}_plot_python_full_{attempt:02}.png"
        save_plot(board, gold_final, plot_path)

        return log
