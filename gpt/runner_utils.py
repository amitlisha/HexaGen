from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Any, Dict, List
import ast
import traceback
import linecache
import multiprocessing as mp
import traceback
from typing import Optional, Tuple, List

from hexagen import Game

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
USER_FILE = "user_snippet.py"
RESULTS_DIR = ROOT_DIR / "results"
RESULTS_DIR.mkdir(exist_ok=True)


def _timeout_worker(code: str, q):
    """Executes `code` and returns ('ok', board_state) or ('err', traceback)."""
    try:
        ns = {}
        exec_snippet(code, ns)
        q.put(("ok", ns.get("board_state")))
    except Exception as exc:
        q.put(("err", format_user_tb(exc)))


def timestamp() -> str:
    return time.strftime("%Y-%m-%dT%H-%M-%S", time.localtime())


def ensure_task_dir(task_id: int) -> Path:
    path = RESULTS_DIR / f"task_{task_id}"
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_json(obj: Dict[str, Any], path: Path) -> None:
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False))


def extract_code(raw: str) -> str:
    """Remove ```python fences if present."""
    m = re.search(r"```(?:python)?\s*([\s\S]+?)```", raw, re.I)
    return (m.group(1) if m else raw).strip()


def save_plot(
    board_state: List[int], gold_board: List[int] | List[List[int]], out: Path
) -> None:
    """Plot board vs. gold and save PNG."""
    with Game() as g:
        g.board_state = board_state.copy()
        if gold_board:
            g.plot(
                gold_boards=gold_board, multiple=False, file_name=str(out), show=False
            )
        else:
            g.plot(multiple=False, file_name=str(out), show=False)


def parse_tile_actions(raw: str) -> List[tuple[int, int, str]]:
    """Parse `(row,column,color)` tuples from raw model output."""
    raw = raw.strip()
    try:
        data = ast.literal_eval(raw)
        if isinstance(data, tuple):
            data = [data]
        if isinstance(data, list):
            out = []
            for item in data:
                if isinstance(item, (list, tuple)) and len(item) == 3:
                    r, c, col = item
                    out.append((int(r), int(c), str(col).lower()))
            if out:
                return out
    except Exception:
        pass

    pattern = r"\(\s*(\d+)\s*,\s*(\d+)\s*,\s*['\"]?([a-zA-Z]+)['\"]?\s*\)"
    return [(int(r), int(c), col.lower()) for r, c, col in re.findall(pattern, raw)]


def format_user_tb(exc: BaseException, user_file: str = USER_FILE) -> str:
    """Return only the traceback frames that belong to the compiled user snippet."""
    tb = exc.__traceback__
    # Skip frames until we reach the snippet we compiled ourselves
    while tb and tb.tb_frame.f_code.co_filename != user_file:
        tb = tb.tb_next
    return "".join(traceback.format_exception(type(exc), exc, tb))


def exec_snippet(src: str, globals_ns: dict, filename: str = "user_snippet.py"):
    """Execute `src` so that tracebacks include the actual source lines."""
    linecache.cache[filename] = (
        len(src),  # length of source
        None,  # mtime (None = unknown / don’t check file)
        src.splitlines(True),  # list of lines *with* \n
        filename,
    )
    exec(compile(src, filename, "exec"), globals_ns)


import multiprocessing as mp


def run_with_timeout(
    src: str,
    timeout_sec: int = 10,
):
    ctx = mp.get_context("spawn")
    q = ctx.Queue()
    p = ctx.Process(target=_timeout_worker, args=(src, q), daemon=True)
    p.start()
    p.join(timeout_sec)

    if p.is_alive():
        p.terminate()
        p.join()
        return None, "TIMEOUT"

    status, payload = q.get()
    return (payload, None) if status == "ok" else (None, payload)


def save_script(
    out_dir: Path, run_ts: str, step: int, attempt: int, code: str, kind: str = "step"
) -> Path:
    path = out_dir / f"{run_ts}_{kind}_{step:02}_{attempt:02}.py"
    path.write_text(code, encoding="utf-8")
    return path
