import unittest
from hexagen import Tile, Line
from tests.base import HexagonsTests

class LineTests(HexagonsTests):
    @HexagonsTests.wrap_test
    def test_shapes(self):
        self.assertShapeLinds(Line(start_tile=Tile(1, 1), direction='down_right'),
                              [0, 1, 20, 21, 40, 41, 60, 61, 80, 81, 100, 101, 120, 121, 140, 141, 160, 161])
        self.assertShapeLinds(Line(start_tile=Tile(1, 1), direction='down_right', length=5), [0, 1, 20, 21, 40])
        self.assertShapeLinds(Line(start_tile=Tile(1, 1), direction='down_right', length=5, include_start_tile=False),
                              [1, 20, 21, 40, 41])
        self.assertShapeLinds(Line(start_tile=Tile(1, 1), direction='down_right', length=5, include_end_tile=False),
                              [0, 1, 20, 21, 40])
        self.assertShapeLinds(Line(start_tile=Tile(1, 1), end_tile=Tile(5, 3)), [0, 1, 20, 21, 40])

    @HexagonsTests.wrap_test
    def test_draw(self):
        Line(start_tile=Tile(1, 1), direction='down_right', length=3).draw('black')
        self.assertBoardNonZeros([0, 1, 20])

    @HexagonsTests.wrap_test
    def test_parallel(self):
        line = Line(start_tile=Tile(5, 5), direction='up_right', length=5)
        self.assertShapeLinds(line.parallel(shift_direction='down', spacing=3), [163, 164, 147, 148, 131, 132, 115, 116, 99, 100, 83, 84, 67, 68, 51, 52, 35])

def load_tests(loader, tests, pattern):
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(LineTests))
    return suite
