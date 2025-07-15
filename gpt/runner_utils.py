from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Any, Dict, List
import ast

from hexagen import Game

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
RESULTS_DIR = ROOT_DIR / "results"
RESULTS_DIR.mkdir(exist_ok=True)


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
