from hexagen import Tile
from tests.helpers import assert_board_non_zeros


def test_on_board_and_draw(game):
    assert Tile(1, 1).on_board()
    assert Tile(-3, -1).on_board()
    Tile(1, 1).draw('black')
    assert_board_non_zeros(game, [0])


def test_neighbor(game):
    assert Tile(1, 1).neighbor(direction='down')._lind == 18
    assert Tile(1, 1).neighbor(direction='down').on_board()
    assert not Tile(1, 1).neighbor(direction='up').on_board()

