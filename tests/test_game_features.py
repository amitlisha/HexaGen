from hexagen import Tile
from tests.helpers import assert_shape_linds


def test_record_steps(game):
    game.record_step(step_name='1')
    Tile(column=7, row=5).draw(color='black')
    game.record_step(step_name='2')
    Tile(column=7, row=5).neighbors().draw(color='yellow')

    assert_shape_linds(game.get_record(step_names=['1', '2']), [78, 77, 79, 96, 61, 59, 60])
    assert_shape_linds(game.get_record(step_names='2'), [77, 79, 96, 61, 59, 60])

