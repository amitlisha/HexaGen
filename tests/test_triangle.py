from hexagen import Tile, Triangle
from tests.helpers import assert_shape_linds, assert_board_non_zeros


def test_triangle_shape_and_draw(game):
    assert_shape_linds(
        Triangle(start_tile=Tile(6, 8), point='left', start_tile_type='bottom', side_length=3),
        [97, 96, 77, 78, 61, 79],
    )
    Triangle(start_tile=Tile(6, 8), point='left', start_tile_type='bottom', side_length=3).draw('black')
    assert_board_non_zeros(game, [97, 96, 77, 78, 61, 79])

