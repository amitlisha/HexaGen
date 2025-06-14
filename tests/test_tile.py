import unittest
from hexagen import Tile
from .base import HexagonsTests

class TileTests(HexagonsTests):
    @HexagonsTests.wrap_test
    def test_on_board_and_draw(self):
        self.assertTrue(Tile(1, 1).on_board())
        self.assertTrue(Tile(-3, -1).on_board())
        Tile(1, 1).draw('black')
        self.assertBoardNonZeros([0])

    @HexagonsTests.wrap_test
    def test_neighbor(self):
        self.assertEqual(Tile(1, 1).neighbor(direction='down')._lind, 18)
        self.assertTrue(Tile(1, 1).neighbor(direction='down').on_board())
        self.assertFalse(Tile(1, 1).neighbor(direction='up').on_board())

def load_tests(loader, tests, pattern):
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TileTests))
    return suite
