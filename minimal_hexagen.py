WIDTH = 18
HEIGHT = 10
COLORS = ["white", "black", "yellow", "green", "red", "blue", "purple", "orange"]

_game_context = []


def _active_game():
    if not _game_context:
        raise RuntimeError(
            "No active Game. Use 'with Game() as g:' or pass game= explicitly"
        )
    return _game_context[-1]


class Game:
    def __init__(self, width: int = WIDTH, height: int = HEIGHT):
        self.start(width, height)

    def __enter__(self):
        _game_context.append(self)
        return self

    def __exit__(self, exc_type, exc, tb):
        _game_context.pop()
        return False

    def start(self, width: int = WIDTH, height: int = HEIGHT):
        self.width = width
        self.height = height
        self.board_state = [0] * (width * height)
        return self

    def plot(self, gold_boards=None, file_name=None, show=True):
        import hexagen.plot_board as pb

        boards = [self.board_state]
        titles = [""]

        if gold_boards is not None:
            gold_board = (
                gold_boards if not isinstance(gold_boards[0], list) else gold_boards[-1]
            )
            diff = [0 if x == y else 1 for x, y in zip(self.board_state, gold_board)]
            boards = [self.board_state, gold_board, diff]
            titles = ["code generated", "gold", "difference"]

        fig = pb.plot_boards(
            boards=boards,
            fig_size=[7, 5],
            height=self.height,
            width=self.width,
            max_in_row=3,
            h_pad=2,
            titles=titles,
            show=show,
        )
        if file_name is not None:
            fig.savefig(file_name)
        return fig


class Tile:
    """Single addressable cell on the board (drawing-only)."""

    def __init__(self, row: int, column: int, game: Game = None):
        self.game = game or _active_game()

        if row < 0:
            row = self.game.height + 1 + row
        if column < 0:
            column = self.game.width + 1 + column

        self.row = row
        self.column = column

    def on_board(self) -> bool:
        return 1 <= self.row <= self.game.height and 1 <= self.column <= self.game.width

    @property
    def _lind(self):
        if not self.on_board():
            return None
        return (self.row - 1) * self.game.width + (self.column - 1)

    @property
    def color(self):
        lind = self._lind
        if lind is None:
            return None
        return COLORS[self.game.board_state[lind]]

    def draw(self, color):
        """Paint this tile. color can be a string in COLORS or an int color_id."""
        lind = self._lind
        if lind is None:
            return self

        color_id = COLORS.index(color) if isinstance(color, str) else int(color)
        self.game.board_state[lind] = color_id
        return self

    def __str__(self):
        return f"Tile(row={self.row}, column={self.column}, color={self.color})"
