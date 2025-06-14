import unittest
from hexagen import Tile
from tests.base import HexagonsTests

class GameTests(HexagonsTests):
    @HexagonsTests.wrap_test
    def test_record_steps(self):
        self.game.record_step(step_name='1')
        Tile(column=7, row=5).draw(color='black')
        self.game.record_step(step_name='2')
        Tile(column=7, row=5).neighbors().draw(color='yellow')

        self.assertShapeLinds(self.game.get_record(step_names=['1', '2']), [78, 77, 79, 96, 61, 59, 60])
        self.assertShapeLinds(self.game.get_record(step_names='2'), [77, 79, 96, 61, 59, 60])

def load_tests(loader, tests, pattern):
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(GameTests))
    return suite
