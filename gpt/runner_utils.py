from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Any, Dict, List

from hexagen import Game

ROOT_DIR   = Path(__file__).resolve().parent.parent
DATA_DIR   = ROOT_DIR / "data"
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


def save_plot(board_state: List[int], gold_board: List[int] | List[List[int]], out: Path) -> None:
    """Plot board vs. gold and save PNG."""
    with Game() as g:
        g.board_state = board_state.copy()
        if gold_board:
            g.plot(gold_boards=gold_board, multiple=False, file_name=str(out), show=False)
        else:
            g.plot(multiple=False, file_name=str(out), show=False)
