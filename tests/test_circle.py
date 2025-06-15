from hexagen import Tile, Circle
from tests.helpers import assert_shape_linds, assert_board_non_zeros


def test_circle_shape(game):
    assert_shape_linds(
        Circle(center_tile=Tile(7, 6), radius=2),
        [76, 132, 80, 59, 113, 98, 115, 61, 94, 116, 60, 112],
    )


def test_circle_draw(game):
    Circle(center_tile=Tile(7, 6)).draw('black')
    assert_board_non_zeros(game, [77, 114, 79, 97, 78, 95])

