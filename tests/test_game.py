import unittest
from hexagen import Game, Tile

class GameContextTests(unittest.TestCase):
    def test_separate_boards(self):
        with Game(3, 2) as g1:
            Tile(1, 1).draw('red')
            board1 = g1.board_state.copy()
        with Game(3, 2) as g2:
            Tile(1, 1).draw('blue')
            board2 = g2.board_state.copy()
        self.assertNotEqual(board1, board2)

def load_tests(loader, tests, pattern):
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(GameContextTests))
    return suite
