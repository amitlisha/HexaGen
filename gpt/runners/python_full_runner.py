"""Python-full mode runner - generate unrestricted Python code that outputs tiles."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import re
import multiprocessing as mp

sys.path.insert(0, str(Path(__file__).parent.parent))

from llm_wrapper import call_llm
from runner_utils import save_plot, save_script
from constants.constants import COLORS, WIDTH, HEIGHT
from prompts import make_larc_tile_prompt
from metrics import evaluate_prediction


def _python_exec_worker(code_str: str, queue, input_grid=None):
    """Execute code in separate process and return tiles (module-level for pickling)."""
    try:
        namespace = {}
        if input_grid is not None:
            namespace['input_grid'] = input_grid
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

        # Detect format: LARC (first element is 2-tuple) vs Hexagons (all 3-tuples)
        dimensions = None
        tiles = []

        if len(result) > 0:
            first = result[0]
            if isinstance(first, (list, tuple)) and len(first) == 2:
                # LARC format: first element is (height, width)
                dimensions = (int(first[0]), int(first[1]))
                remaining = result[1:]
            else:
                remaining = result

            for item in remaining:
                if not (isinstance(item, (list, tuple)) and len(item) == 3):
                    queue.put(("error", f"Each tile must be a (row, col, color) tuple, got {item}"))
                    return
                r, c, col = item
                if isinstance(col, int):
                    tiles.append((int(r), int(c), col))
                else:
                    tiles.append((int(r), int(c), str(col).lower()))

        queue.put(("ok", (dimensions, tiles)))
    except Exception as e:
        queue.put(("error", f"Failed to execute generated code: {e}"))


def extract_and_execute_python(
    code: str, timeout: int = 10, input_grid=None,
) -> Tuple[Optional[Tuple[int, int]], List[tuple]]:
    """
    Extract Python code, execute it with timeout, and return the result from get_tiles().

    Args:
        code: Raw LLM output containing Python code
        timeout: Execution timeout in seconds
        input_grid: Optional 2D input grid (for LARC tasks)

    Returns:
        Tuple of (dimensions, tiles)
        - dimensions: (height, width) if present, else None
        - tiles: List of (row, col, color) tuples
    """
    # Remove markdown code blocks if present
    code = re.sub(r'^```python\s*\n', '', code, flags=re.MULTILINE)
    code = re.sub(r'\n```\s*$', '', code, flags=re.MULTILINE)
    code = code.strip()

    # Execute with timeout
    ctx = mp.get_context("spawn")
    q = ctx.Queue()
    p = ctx.Process(target=_python_exec_worker, args=(code, q, input_grid), daemon=True)
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

    return result


def run_python_full(
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
    Model generates Python code that computes tiles for all instructions.

    Args:
        initial_board: Initial board state (for LARC only)
        width: Board width (defaults to constants.WIDTH if None)
        height: Board height (defaults to constants.HEIGHT if None)
        input_grid_2d: 2D input grid for LARC tasks
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
        prompt = make_larc_tile_prompt(instructions_block, input_grid_2d, user_tmpl)
    else:
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

    # Extract and execute Python code with timeout
    try:
        dimensions, tiles = extract_and_execute_python(
            resp["text"],
            timeout=cfg.exec_timeout,
            input_grid=input_grid_2d if cfg.dataset == "larc" else None,
        )
        valid = True
        error_msg = None
    except Exception as e:
        dimensions = None
        tiles = []
        valid = False
        error_msg = str(e)

    # Save the generated Python script
    save_script(task_dir, run_ts, step=0, attempt=1, code=resp["text"], kind="python_full")

    # For LARC: validate dimensions
    dimension_match = True
    if cfg.dataset == "larc":
        if dimensions is None:
            dimension_match = False
            predicted_height, predicted_width = 0, 0
        else:
            predicted_height, predicted_width = dimensions
            if predicted_height != height or predicted_width != width:
                dimension_match = False
            else:
                width, height = predicted_width, predicted_height

    # Create board with appropriate dimensions
    board = [0] * (width * height)

    # Apply tiles (only if dimensions match for LARC)
    if cfg.dataset != "larc" or dimension_match:
        for r, c, col in tiles:
            if cfg.dataset == "larc":
                if 1 <= r <= height and 1 <= c <= width and isinstance(col, int) and 0 <= col <= 9:
                    idx = (r - 1) * width + (c - 1)
                    board[idx] = col
            else:
                if 1 <= r <= HEIGHT and 1 <= c <= WIDTH and col in COLORS:
                    idx = (r - 1) * WIDTH + (c - 1)
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
        "code": resp["text"],
        "tiles": tiles,
        "valid": valid,
        "usage": resp["usage"],
        **metrics,
    }

    if error_msg:
        log["error"] = error_msg

    # Add LARC-specific dimension tracking
    if cfg.dataset == "larc":
        log["dimension_match"] = dimension_match
        log["predicted_dimensions"] = dimensions if dimensions else (0, 0)
        log["gold_dimensions"] = (height, width)

    # Save plots
    plot_path = task_dir / f"{run_ts}_plot_python_full_01.png"
    if cfg.dataset == "larc":
        from larc_plot import save_larc_plot

        save_larc_plot(board, gold_final, plot_path, width, height)
    else:
        save_plot(board, gold_final, plot_path)

    return log
