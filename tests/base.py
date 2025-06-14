import sys
import os
from functools import wraps
import unittest

# Ensure package is importable when running tests directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from hexagen import Game

class HexagonsTests(unittest.TestCase):
    @staticmethod
    def wrap_test(func):
        @wraps(func)
        def mod_test(*args, **kwargs):
            print(f"starting {func.__qualname__}")
            func(*args, **kwargs)
            print(f"finishing {func.__qualname__}")
        return mod_test

    def setUp(self):
        self.game = Game()
        self.game.__enter__()

    def tearDown(self):
        self.game.__exit__(None, None, None)

    def assertShapeLinds(self, S, linds):
        self.assertEqual(set(S._linds), set(linds))

    def assertBoardNonZeros(self, indices, game=None):
        g = game if game is not None else self.game
        board_nz_indices = [i for i in range(len(g.board_state)) if g.board_state[i] != 0]
        self.assertEqual(set(board_nz_indices), set(indices))
