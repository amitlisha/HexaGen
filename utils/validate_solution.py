"""Validate a solution file by comparing its final board to the gold board."""
import runpy
import sys
import types

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

def main(path):
    runpy.run_path(path, run_name="__main__")
    if _latest_game is None:
        print("No Game instance detected")
        return 2
    if getattr(_latest_game, "validation_passed", False):
        print("VALID SOLUTION")
        return 0
    else:
        print("INVALID SOLUTION")
        return 1

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: validate_solution.py <solution_file>")
        sys.exit(2)
    sys.exit(main(sys.argv[1]))

