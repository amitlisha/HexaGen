from hexagen import Game, Tile


def test_separate_boards():
    with Game(3, 2) as g1:
        Tile(1, 1).draw('red')
        board1 = g1.board_state.copy()
    with Game(3, 2) as g2:
        Tile(1, 1).draw('blue')
        board2 = g2.board_state.copy()
    assert board1 != board2

