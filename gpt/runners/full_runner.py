"Full mode runner - single-shot execution of all instructions."

from __future__ import annotations

import argparse
import sys
import textwrap
import traceback as tb
import multiprocessing as mp
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any

sys.path.insert(0, str(Path(__file__).parent.parent))

from llm_wrapper import call_llm
from runner_utils import (
    extract_code,
    save_script,
    save_plot,
    run_with_timeout,
    _inject_custom_lib,
    simplify_traceback,
)
from constants.constants import WIDTH, HEIGHT
from metrics import evaluate_prediction


def _dsl_exec_worker(code_str: str, queue, input_grid_tuple, output_height=None, output_width=None):
    """Execute DSL code in separate process. Returns flat grid."""
    try:
        # Prepare namespace with all DSL functions
        namespace = {}

        # Add project root and larc directory to sys.path for the worker
        project_root = Path(__file__).parent.parent.parent
        sys.path.insert(0, str(project_root))
        sys.path.insert(0, str(project_root / "larc"))

        # Import everything from dsl
        try:
            import larc.dsl as dsl_module

            for name in dir(dsl_module):
                if not name.startswith("_"):
                    namespace[name] = getattr(dsl_module, name)
        except ImportError as e:
            queue.put(("error", f"Failed to import larc.dsl: {e}"))
            return

        # Execute the user code
        exec(code_str, namespace)

        if "solve" not in namespace:
            queue.put(
                ("error", "Generated code must define a solve(input_grid) function")
            )
            return

        solve_func = namespace["solve"]
        if not callable(solve_func):
            queue.put(("error", "solve must be a callable function"))
            return

        # Execute solve
        try:
            result = solve_func(input_grid_tuple)
        except Exception as e:
            queue.put(("error", f"solve(input_grid) raised {type(e).__name__}: {e}\n{tb.format_exc()}"))
            return

        # Convert result to flat list of ints
        flat_grid = []

        if isinstance(result, tuple):
            # Grid (tuple of tuples)
            if len(result) == 0:
                flat_grid = []
            else:
                flat_grid = [int(col) for row in result for col in row]

        elif isinstance(result, (set, frozenset)):
            # Object (frozenset of (value, (r, c)) tuples)
            # Use output dimensions if provided, else fall back to input dims
            h = output_height if output_height is not None else len(input_grid_tuple)
            w = output_width if output_width is not None else (len(input_grid_tuple[0]) if len(input_grid_tuple) > 0 else 0)
            grid_list = [[0 for _ in range(w)] for _ in range(h)]

            for item in result:
                if isinstance(item, tuple) and len(item) == 2:
                    val, coords = item
                    if isinstance(coords, tuple) and len(coords) == 2:
                        r, c = coords
                        if 0 <= r < h and 0 <= c < w:
                            grid_list[r][c] = val

            flat_grid = [int(col) for row in grid_list for col in row]

        elif isinstance(result, list):
            # list of lists (2D grid)
            if len(result) == 0:
                flat_grid = []
            elif isinstance(result[0], (tuple, list)):
                flat_grid = [int(col) for row in result for col in row]
            else:
                queue.put(
                    ("error", f"Unknown list format. Expected 2D grid (list of rows), got 1D list.")
                )
                return

        else:
            queue.put(
                (
                    "error",
                    f"Unknown return type: {type(result)}. Expected Grid (tuple of tuples), Object, or list of lists.",
                )
            )
            return

        queue.put(("ok", flat_grid))

    except Exception as e:
        queue.put(("error", f"Execution failed: {e}\n{tb.format_exc()}"))


def extract_and_execute_dsl(
    code: str, timeout: int, input_grid_2d: List[List[int]],
    output_width: int = None, output_height: int = None,
) -> List[int]:
    """Extract code, execute with timeout, return flat_board."""
    # Remove markdown
    code = re.sub(r"^```python\s*\n", "", code, flags=re.MULTILINE)
    code = re.sub(r"\n```\s*$", "", code, flags=re.MULTILINE)
    code = code.strip()

    # Convert input list-of-lists to tuple-of-tuples-of-ints (immutable DSL Grid)
    if input_grid_2d is None:
        input_grid_tuple = ()
    else:
        input_grid_tuple = tuple(tuple(int(c) for c in row) for row in input_grid_2d)

    ctx = mp.get_context("spawn")
    q = ctx.Queue()
    p = ctx.Process(
        target=_dsl_exec_worker, args=(code, q, input_grid_tuple, output_height, output_width), daemon=True
    )
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

    return result  # flat_grid


def build_code_full_prompt(
    cfg: argparse.Namespace,
    user_tmpl: str,
    instructions: List[str],
    code_so_far: str,
    input_grid_2d: Optional[List[List[int]]] = None,
) -> str:
    """Build the first-attempt prompt for code-full mode (no error feedback)."""
    if cfg.dataset == "larc":
        input_tuple_str = repr(tuple(tuple(r) for r in input_grid_2d)) if input_grid_2d else "()"
        full_instruction = "\n".join(instructions)
        return (
            user_tmpl.replace("{INPUT_GRID}", input_tuple_str)
            .replace("{NEXT_STEP}", full_instruction)
        )
    else:
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
    input_grid_2d: List[List[int]] = None,
    width: int = None,
    height: int = None,
    prefetched_response: Optional[Dict] = None,
) -> Dict:
    """
    Single-shot prompt that passes ALL instructions as one indented block.
    Includes retry logic with error feedback similar to step mode.

    Supports both Hexagen (default) and LARC (if cfg.dataset == 'larc').
    """

    # --- LARC DATASET LOGIC ---
    if cfg.dataset == "larc":
        # Format input grid for prompt as a Python tuple of tuples string
        if input_grid_2d is None:
            input_tuple_str = "()"
        else:
            input_tuple_str = repr(tuple(tuple(r) for r in input_grid_2d))

        full_instruction = "\n".join(instructions)

        attempt = 0
        last_exc: Optional[str] = None
        last_code: Optional[str] = None

        while True:
            attempt += 1

            prompt = user_tmpl.replace("{INPUT_GRID}", input_tuple_str).replace(
                "{NEXT_STEP}", full_instruction
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
                pred_board = extract_and_execute_dsl(
                    resp["text"], cfg.exec_timeout, input_grid_2d,
                    output_width=width, output_height=height,
                )
                valid = True
                error_msg = None
            except Exception as e:
                pred_board = []
                valid = False
                error_msg = str(e)

            save_script(task_dir, run_ts, step=0, attempt=attempt, code=resp["text"], kind="full")

            # If execution failed, retry with error feedback
            if not valid:
                last_exc = error_msg
                last_code = resp["text"]

                if cfg.retries and attempt >= cfg.retries:
                    blank = [0] * len(gold_final)
                    metrics = evaluate_prediction(blank, blank, blank, gold_final)
                    return {
                        "attempt": attempt,
                        "code": resp["text"],
                        "valid": False,
                        "usage": resp["usage"],
                        "error": error_msg,
                        "traceback": error_msg,
                        **metrics,
                    }

                continue

            # If prediction length doesn't match gold, zero it out for metrics
            if len(pred_board) != len(gold_final):
                eval_board = [0] * len(gold_final)
            else:
                eval_board = pred_board

            blank = [0] * len(gold_final)
            metrics = evaluate_prediction(blank, eval_board, blank, gold_final)

            log = {
                "attempt": attempt,
                "code": resp["text"],
                "valid": valid,
                "usage": resp["usage"],
                **metrics,
            }

            # Save plot
            gold_h = height if height else (len(input_grid_2d) if input_grid_2d else 1)
            gold_w = width if width else (len(input_grid_2d[0]) if input_grid_2d and input_grid_2d[0] else 1)
            plot_path = task_dir / f"{run_ts}_plot_full_{attempt:02}.png"

            try:
                from larc_plot import save_larc_plot
                save_larc_plot(eval_board, gold_final, plot_path, gold_w, gold_h)
            except ImportError:
                save_plot(eval_board, gold_final, plot_path)
            except Exception as e:
                print(f"Warning: could not save LARC plot: {e}")

            return log

    # --- HEXAGEN DATASET LOGIC (Original) ---
    else:
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
