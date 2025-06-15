"""Validate a solution file by comparing its final board to the gold board."""
import runpy
import sys
from pathlib import Path

import matplotlib.pyplot as plt

from hexagen.hexagen import Game as OriginalGame
import hexagen

_latest_game = None

class ValidationGame(OriginalGame):
    def __enter__(self):
        global _latest_game
        super().__enter__()
        _latest_game = self
        return self

    def plot(self, gold_boards=None, multiple=False, file_name=None):
        if gold_boards is not None:
            gold_board = gold_boards if not isinstance(gold_boards[0], list) else gold_boards[-1]
            self.validation_passed = self.board_state == gold_board
        # disable plotting
        return None

# Patch Game class used by solution files
hexagen.Game = ValidationGame
hexagen.hexagen.Game = ValidationGame

# Prevent plotting windows
plt.show = lambda *args, **kwargs: None

def _validate_file(file_path: Path):
    global _latest_game
    _latest_game = None
    runpy.run_path(str(file_path), run_name="__main__")
    if _latest_game is None:
        print(f"{file_path}: No Game instance detected")
        return 2
    if getattr(_latest_game, "validation_passed", False):
        print(f"{file_path}: VALID SOLUTION")
        return 0
    else:
        print(f"{file_path}: INVALID SOLUTION")
        return 1


def main(path):
    target = Path(path)
    if target.is_file():
        return _validate_file(target)
    elif target.is_dir():
        codes = [_validate_file(p) for p in sorted(target.glob("*.py"))]
        if all(c == 0 for c in codes):
            return 0
        elif any(c == 1 for c in codes):
            return 1
        else:
            return 2
    else:
        print(f"Path {path} not found")
        return 2

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: validate_solution.py <path_to_solution_or_folder>")
        sys.exit(2)
    sys.exit(main(sys.argv[1]))

