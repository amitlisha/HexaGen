"""Python-full mode runner - generate unrestricted Python code that outputs tiles."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Optional
import re
import multiprocessing as mp

sys.path.insert(0, str(Path(__file__).parent.parent))

from llm_wrapper import call_llm
from runner_utils import save_plot
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

        # Convert to tuples and validate format
        tiles = []
        for item in result:
            if not (isinstance(item, (list, tuple)) and len(item) == 3):
                queue.put(("error", f"Each tile must be a (row, col, color) tuple, got {item}"))
                return
            r, c, col = item
            tiles.append((int(r), int(c), str(col).lower()))

        queue.put(("ok", tiles))
    except Exception as e:
        queue.put(("error", f"Failed to execute generated code: {e}"))


def extract_and_execute_python(code: str, timeout: int = 10) -> List[tuple]:
    """
    Extract Python code, execute it with timeout, and return the result from get_tiles().

    Args:
        code: Raw LLM output containing Python code
        timeout: Execution timeout in seconds

    Returns:
        List of (row, column, color) tuples
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

    status, result = q.get()
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
) -> Dict:
    """
    Single-shot prompt that passes ALL instructions as one block.
    Model generates Python code that computes tiles for all instructions.
    """
    # Format all instructions as a numbered block
    instructions_block = "\n".join(f"{i+1}. {txt}" for i, txt in enumerate(instructions))

    # Build the prompt with all instructions
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
        tiles = extract_and_execute_python(resp["text"], timeout=cfg.exec_timeout)
        valid = True
        error_msg = None
    except Exception as e:
        tiles = []
        valid = False
        error_msg = str(e)

    # Apply tiles to blank board
    board = [0] * (WIDTH * HEIGHT)
    for r, c, col in tiles:
        if 1 <= r <= HEIGHT and 1 <= c <= WIDTH and col in COLORS:
            idx = (r - 1) * WIDTH + (c - 1)
            board[idx] = COLORS.index(col)

    # Evaluate against gold final board
    metrics = evaluate_prediction(
        [0] * (WIDTH * HEIGHT),
        board,
        [0] * (WIDTH * HEIGHT),
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

    # Save plots
    plot_path = task_dir / f"{run_ts}_plot_python_full_01.png"
    save_plot(board, gold_final, plot_path)

    return log
