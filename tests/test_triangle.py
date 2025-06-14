import unittest
from hexagen import Tile, Triangle
from tests.base import HexagonsTests

class TriangleTests(HexagonsTests):
    @HexagonsTests.wrap_test
    def test_shape_and_draw(self):
        self.assertShapeLinds(Triangle(start_tile=Tile(8, 6), point='left', start_tile_type='bottom', side_length=3),
                              [97, 96, 77, 78, 61, 79])
        Triangle(start_tile=Tile(8, 6), point='left', start_tile_type='bottom', side_length=3).draw('black')
        self.assertBoardNonZeros([97, 96, 77, 78, 61, 79])

def load_tests(loader, tests, pattern):
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TriangleTests))
    return suite
