"Full mode runner - single-shot execution of all instructions."

from __future__ import annotations

import argparse
import sys
import textwrap
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
)
from constants.constants import WIDTH, HEIGHT
from metrics import evaluate_prediction


def _dsl_exec_worker(code_str: str, queue, input_grid_tuple):
    """Execute DSL code in separate process."""
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
        result = solve_func(input_grid_tuple)

        # Convert result to standard format (height, width, flat_list)
        h_out, w_out = 0, 0
        flat_grid = []

        if isinstance(result, tuple):
            # Assumed to be Grid (tuple of tuples)
            h_out = len(result)
            w_out = len(result[0]) if h_out > 0 else 0
            flat_grid = [col for row in result for col in row]

        elif isinstance(result, (set, frozenset)):
            # Assumed to be Object
            h_in = len(input_grid_tuple)
            w_in = len(input_grid_tuple[0]) if h_in > 0 else 0

            # Create a blank grid
            grid_list = [[0 for _ in range(w_in)] for _ in range(h_in)]

            # Paint object
            for item in result:
                # item is (value, (r, c))
                if isinstance(item, tuple) and len(item) == 2:
                    val, coords = item
                    if isinstance(coords, tuple) and len(coords) == 2:
                        r, c = coords
                        if 0 <= r < h_in and 0 <= c < w_in:
                            grid_list[r][c] = val

            h_out, w_out = h_in, w_in
            flat_grid = [col for row in grid_list for col in row]

        elif isinstance(result, list):
            # List of tuples format
            h_in = len(input_grid_tuple)
            w_in = len(input_grid_tuple[0]) if h_in > 0 else 0
            grid_list = [[0 for _ in range(w_in)] for _ in range(h_in)]

            for item in result:
                if len(item) == 3:
                    r, c, val = item
                    if 0 <= r < h_in and 0 <= c < w_in:
                        grid_list[r][c] = val

            h_out, w_out = h_in, w_in
            flat_grid = [col for row in grid_list for col in row]

        else:
            queue.put(
                (
                    "error",
                    f"Unknown return type: {type(result)}. Expected Grid (tuple of tuples) or Object.",
                )
            )
            return

        queue.put(("ok", (h_out, w_out, flat_grid)))

    except Exception as e:
        queue.put(("error", f"Execution failed: {e}"))


def extract_and_execute_dsl(
    code: str, timeout: int, input_grid_2d: List[List[int]]
) -> Tuple[Optional[Tuple[int, int]], List[int]]:
    """Extract code, execute with timeout, return (dimensions, flat_board)."""
    # Remove markdown
    code = re.sub(r"^```python\s*\n", "", code, flags=re.MULTILINE)
    code = re.sub(r"\n```\s*$", "", code, flags=re.MULTILINE)
    code = code.strip()

    # Convert input list-of-lists to tuple-of-tuples (DSL Grid)
    if input_grid_2d is None:
        input_grid_tuple = ()
    else:
        input_grid_tuple = tuple(tuple(row) for row in input_grid_2d)

    ctx = mp.get_context("spawn")
    q = ctx.Queue()
    p = ctx.Process(
        target=_dsl_exec_worker, args=(code, q, input_grid_tuple), daemon=True
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

    h, w, flat_grid = result
    return (h, w), flat_grid


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

        prompt = user_tmpl.replace("{INPUT_GRID}", input_tuple_str).replace(
            "{NEXT_STEP}", full_instruction
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

        try:
            (pred_h, pred_w), pred_board = extract_and_execute_dsl(
                resp["text"], cfg.exec_timeout, input_grid_2d
            )
            valid = True
            error_msg = None

            # LARC validation: dimensions must match
            target_h = height if height is not None else len(input_grid_2d)
            target_w = (
                width
                if width is not None
                else (len(input_grid_2d[0]) if input_grid_2d else 0)
            )

            dimension_match = pred_h == target_h and pred_w == target_w

        except Exception as e:
            target_len = len(gold_final)
            pred_board = [0] * target_len
            valid = False
            error_msg = str(e)
            dimension_match = False
            pred_h, pred_w = 0, 0

        # If dimensions don't match, the prediction is entirely wrong –
        # use a zeroed board so metrics reflect a complete miss.
        if not dimension_match:
            eval_pred = [0] * len(gold_final)
        else:
            eval_pred = pred_board

        metrics = evaluate_prediction(
            [0] * len(gold_final),
            eval_pred,
            [0] * len(gold_final),
            gold_final,
        )

        log = {
            "attempt": 1,
            "code": resp["text"],
            "valid": valid,
            "usage": resp["usage"],
            "dimension_match": dimension_match,
            "predicted_dimensions": (pred_h, pred_w),
            **metrics,
        }

        if error_msg:
            log["error"] = error_msg
            log["traceback"] = error_msg

        save_script(task_dir, run_ts, step=0, attempt=1, code=resp["text"], kind="full")

        plot_path = task_dir / f"{run_ts}_plot_full_01.png"

        try:
            from larc_plot import save_larc_plot

            if dimension_match:
                save_larc_plot(
                    pred_board, gold_final, plot_path, width or pred_w, height or pred_h
                )
            else:
                # Dimensions differ – plot pred with its own shape, gold with its own
                plot_w = pred_w or (width or 1)
                plot_h = pred_h or (height or 1)
                save_larc_plot(pred_board, None, plot_path, plot_w, plot_h)
        except ImportError:
            save_plot(pred_board, gold_final, plot_path)
        except Exception as e:
            print(f"Warning: could not save LARC plot: {e}")

        return log

    # --- HEXAGEN DATASET LOGIC (Original) ---
    else:
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
