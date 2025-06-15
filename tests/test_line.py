import pytest
from hexagen import Tile, Line
from tests.helpers import assert_shape_linds, assert_board_non_zeros


@pytest.mark.parametrize(
    "kwargs,expected",
    [
        ({"direction": "down_right"}, [0, 1, 20, 21, 40, 41, 60, 61, 80, 81, 100, 101, 120, 121, 140, 141, 160, 161]),
        ({"direction": "down_right", "length": 5}, [0, 1, 20, 21, 40]),
        ({"direction": "down_right", "length": 5, "include_start_tile": False}, [1, 20, 21, 40, 41]),
        ({"direction": "down_right", "length": 5, "include_end_tile": False}, [0, 1, 20, 21, 40]),
        ({"end_tile_coords": (5, 3)}, [0, 1, 20, 21, 40]),
    ],
)

def test_line_shapes(game, kwargs, expected):
    if "end_tile_coords" in kwargs:
        kwargs["end_tile"] = Tile(*kwargs.pop("end_tile_coords"))
    line = Line(start_tile=Tile(1, 1), **kwargs)
    assert_shape_linds(line, expected)


def test_line_draw(game):
    Line(start_tile=Tile(1, 1), direction="down_right", length=3).draw("black")
    assert_board_non_zeros(game, [0, 1, 20])


def test_line_parallel(game):
    line = Line(start_tile=Tile(5, 5), direction="up_right", length=5)
    assert_shape_linds(
        line.parallel(shift_direction="down", spacing=3),
        [163, 164, 147, 148, 131, 132, 115, 116, 99, 100, 83, 84, 67, 68, 51, 52, 35],
    )
