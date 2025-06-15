from hexagen import Game


def assert_shape_linds(shape, linds):
    assert set(shape._linds) == set(linds)


def assert_board_non_zeros(game, indices):
    board_nz_indices = [i for i, v in enumerate(game.board_state) if v != 0]
    assert set(board_nz_indices) == set(indices)
