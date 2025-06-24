"""Validate solution files by comparing their final board to the gold board.

The script can validate either a single Python file or every ``.py`` file under
a directory. When a directory is supplied, all Python files in nested
subfolders are processed as well. For each file the task index is inferred from
its name or a ``task_index`` variable inside the file in order to load the
corresponding gold board using :func:`utils.reading_tasks.read_task`.

If running a file raises an exception, the error will be reported but the
validation process will continue.
"""

import re
import runpy
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from hexagen.hexagen import Game as OriginalGame
import hexagen
from utils.reading_tasks import read_task

_latest_game = None
_gold_board = None

class ValidationGame(OriginalGame):
    def __enter__(self):
        global _latest_game
        super().__enter__()
        _latest_game = self
        return self

    def plot(self, gold_boards=None, multiple=False, file_name=None):
        boards = gold_boards if gold_boards is not None else _gold_board
        if boards is not None:
            gold_board = boards if not isinstance(boards[0], list) else boards[-1]
            self.validation_passed = self.board_state == gold_board
        return None

hexagen.Game = ValidationGame
hexagen.hexagen.Game = ValidationGame
plt.show = lambda *args, **kwargs: None

def _extract_task_index(file_path: Path) -> int | None:
    """Try to infer the task index from the file name or its contents."""
    text = file_path.read_text(errors="ignore")
    match = re.search(r"task_index\s*=\s*(\d+)", text)
    if match:
        return int(match.group(1))

    digits = re.findall(r"\d+", file_path.stem)
    if digits:
        return int(digits[0])

    if file_path.parent.name.isdigit():
        return int(file_path.parent.name)

    return None

def _validate_file(file_path: Path):
    global _latest_game, _gold_board
    _latest_game = None
    task_index = _extract_task_index(file_path)

    if task_index is None:
        print(f"{file_path}: could not determine task index")
        return dict(task_number=None, path=str(file_path), status="failed", error_message="could not determine task index")

    _gold_board = read_task(task_index)["gold_boards"]

    try:
        runpy.run_path(str(file_path), run_name="__main__")
    except Exception as exc:
        print(f"{file_path}: ERROR during execution - {exc}")
        return dict(task_number=task_index, path=str(file_path), status="failed", error_message=str(exc))

    if _latest_game is None:
        print(f"{file_path}: No Game instance detected")
        return dict(task_number=task_index, path=str(file_path), status="failed", error_message="No Game instance detected")

    if not hasattr(_latest_game, "validation_passed") and _gold_board is not None:
        boards = _gold_board
        gold_board = boards if not isinstance(boards[0], list) else boards[-1]
        _latest_game.validation_passed = _latest_game.board_state == gold_board

    if getattr(_latest_game, "validation_passed", False):
        print(f"{file_path}: VALID SOLUTION")
        status = "valid"
    else:
        print(f"{file_path}: INVALID SOLUTION")
        status = "invalid"

    return dict(task_number=task_index, path=str(file_path), status=status, error_message="")

def main(path):
    target = Path(path)
    results = []

    if target.is_file():
        results.append(_validate_file(target))
    elif target.is_dir():
        for p in sorted(target.rglob("*.py")):
            results.append(_validate_file(p))
    else:
        print(f"Path {path} not found")
        sys.exit(2)

    df = pd.DataFrame(results)
    df.to_csv("validation_results.csv", index=False)
    print("\nSaved results to validation_results.csv")

    if all(r["status"] == "valid" for r in results):
        return 0
    elif any(r["status"] == "invalid" for r in results):
        return 1
    else:
        return 2

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: validate_solution.py <path_to_solution_or_directory>")
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
