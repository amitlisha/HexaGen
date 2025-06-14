import unittest
from hexagen import Tile, Circle
from tests.base import HexagonsTests

class CircleTests(HexagonsTests):
    @HexagonsTests.wrap_test
    def test_shape(self):
        self.assertShapeLinds(Circle(center_tile=Tile(7, 6), radius=2),
                              [76, 132, 80, 59, 113, 98, 115, 61, 94, 116, 60, 112])

    @HexagonsTests.wrap_test
    def test_draw(self):
        Circle(center_tile=Tile(7, 6)).draw('black')
        self.assertBoardNonZeros([77, 114, 79, 97, 78, 95])

def load_tests(loader, tests, pattern):
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(CircleTests))
    return suite
