"""Hexagons Classes

This module contains tools for drawing on a hexagons board.
The purpose of these tools is to translate drawing instructions given in natural language
into code.

Contains the main classes:
- Game - manages the board
- _Vec (for internal use only)
- _Hexagon (for internal use only)
- Shape - manages shapes (any set of tiles) on the board
- Tile(Shape) - a single tile on the board
- Line(Shape) - a line on the board
- Circle(Shape) - a circle on the board
- Triangle(Shape) - a triangle on the board
"""

from copy import copy
import logging
import numpy as np
from scipy.spatial.transform import Rotation
from typing import Optional, List, Iterable

from constants.constants import COLORS, WIDTH, HEIGHT, DIRECTIONS
import hexagen.plot_board as pb

logger = logging.getLogger(__name__)

_game_context = []


def _active_game():
    """Return the active ``Game`` instance.

    Raises:
    -------
    RuntimeError
      If no ``Game`` is currently active.
    """

    if not _game_context:
        raise RuntimeError(
            "No active Game. Use 'with Game() as g:' or pass game= explicitly"
        )
    return _game_context[-1]


class Game:
    """Manage a single hexagon board."""

    def __init__(self, width: int = WIDTH, height: int = HEIGHT):
        """Create a new game with the given board dimensions."""

        self.start(width, height)

    def __enter__(self):
        """Activate the game context."""

        _game_context.append(self)
        return self

    def __exit__(self, exc_type, exc, tb):
        """Deactivate the game context."""

        _game_context.pop()
        return False

    def start(self, width: int = WIDTH, height: int = HEIGHT):
        """Initialize the board with the given size."""

        self.width = width
        self.height = height
        self.board_state = [0] * width * height
        self.board_states = {}
        self._current_step_name = None
        self._step_drawn_hexagons = {}
        self._current_batch_name = None
        self._batch_draws = {}
        return self

    def _start_batch_record(self, batch_name):
        """Begin recording draw commands under ``batch_name``."""

        self._current_batch_name = batch_name
        self._batch_draws[batch_name] = []

    def _get_batch_record(self, batch_name):
        """Return recorded commands for ``batch_name``."""

        return self._batch_draws[batch_name]

    def record_step(self, step_name):
        """Start a new drawing step called ``step_name``."""

        if self._current_step_name is not None:
            self.board_states[self._current_step_name] = copy(self.board_state)
        self._current_step_name = step_name
        self._step_drawn_hexagons[step_name] = []

    def get_record(self, step_names):
        """Return the tiles recorded in the provided step or steps."""

        if not isinstance(step_names, list):
            step_names = [step_names]
        drawn_hexagons = [
            h for step_name in step_names for h in self._step_drawn_hexagons[step_name]
        ]
        return Shape(drawn_hexagons, from_hexagons=True)

    def plot(self, gold_boards=None, multiple=False, file_name=None, show=True):
        """Plot the current board state.

        Parameters
        ----------
        gold_boards: list[int] or list[list[int]], optional
          If provided, compare the drawn board with these boards.
        multiple: bool, optional
          Whether to plot all recorded steps.
        file_name: str, optional
          If provided, save the figure to this path.
        """

        def diff(board1, board2):
            return list(map(lambda x, y: 0 if x == y else 1, board1, board2))

        if self._current_step_name is None:
            self.board_states["final"] = copy(self.board_state)
        else:
            self.board_states[self._current_step_name] = copy(self.board_state)
        boards = list(self.board_states.values())
        titles = list(self.board_states.keys())
        if not multiple:
            boards = [boards[-1]]
            titles = [""]
        if gold_boards is not None:
            if not multiple:
                gold_board = (
                    gold_boards
                    if not isinstance(gold_boards[0], list)
                    else gold_boards[-1]
                )
                boards = [boards[-1], gold_board, diff(boards[-1], gold_board)]
                titles = ["code generated", "gold", "difference"]
            else:
                drawn_boards = boards
                drawn_titles = titles
                gold_boards = (
                    gold_boards if isinstance(gold_boards[0], list) else [gold_boards]
                )
                if len(drawn_boards) != len(gold_boards):
                    logger.debug(
                        "number of recorded steps (%s) doesn't match number of gold steps (%s)",
                        len(drawn_boards),
                        len(gold_boards),
                    )
                    return
                boards = []
                titles = []
                for i in range(len(drawn_boards)):
                    boards += [
                        drawn_boards[i],
                        gold_boards[i],
                        diff(drawn_boards[i], gold_boards[i]),
                    ]
                    titles += [
                        f"code generated ({drawn_titles[i]})",
                        f"gold ({i+1})",
                        "difference",
                    ]

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


class _Vec:
    """Class _Vec represents a vector on an infinite hexagonally tiled plane.
    It doesn't symbol a specific location on the board, but rather the difference
    between two location.
    It is for internal use only.
    """

    # directions_to_qrs = {key: DIRECTIONS[key].index(0) for key in DIRECTIONS}

    def __init__(self, *args):
        if isinstance(args[0], str):
            # _Vec is given as a direction name, e.g. 'up_right'
            q, r, s = DIRECTIONS[args[0]]
        elif len(args) == 3:
            # _Vec is given as cube [q, r, s]
            q, r, s = args
        elif len(args) == 2:
            # _Vec is given as offset [column_diff, row_diff]
            column_diff, row_diff = args
            # assert column_diff % 2 == 0, 'column_diff must be even, otherwise this is ambiguous'
            q = column_diff
            r = row_diff - (q - (q % 2)) // 2
            s = -q - r
        if abs(q + r + s) > 0.00001:
            raise Exception(f"cube coordinates {[q, r, s]} don't sum up to 0")
        self._cube = (q, r, -q - r)

    @property
    def _q(self):
        return self._cube[0]

    @property
    def _r(self):
        return self._cube[1]

    @property
    def _s(self):
        return self._cube[2]

    def cyclic_permutation(ls, k):
        # if k >= 0, element 0 becomes element k
        # if k < 0, element (-k) becomes element 0
        return ls[-k:] + ls[:-k]

    def _show(self):
        logger.debug("%s instance: cube=%s", self.__class__.__name__, self._cube)

    def _has_direction(self):
        # q*r*s=0 means that vec is proportional to one of the six direction vecs
        return not bool(self._q * self._r * self._s)

    def _normalize(self):
        if self._has_direction():
            norm = self._norm()
            direction_cube = [x // norm for x in self._cube]
            return _Vec(*direction_cube)
        logger.debug("vec %s is not a direction vector", self._cube)

    def _direction_str(self):
        # returns a string describing the direction of the vector
        if self._has_direction():
            return list(DIRECTIONS.keys())[
                list(DIRECTIONS.values()).index(self._normalize()._cube)
            ]
        logger.debug("vec %s is not a direction vector", self._cube)

    def __add__(self, other):
        new_cube = [_ for _ in [x + y for x, y in zip(self._cube, other._cube)]]
        return _Vec(*new_cube)

    def __sub__(self, other):
        new_cube = [_ for _ in [x - y for x, y in zip(self._cube, other._cube)]]
        return _Vec(*new_cube)

    def _scale(self, k):
        return _Vec(*[k * _ for _ in self._cube])

    def _norm(self):
        return np.sum([np.abs(_) for _ in self._cube]) / 2

    def _round(self):
        int_cube = [np.round(_) for _ in self._cube]
        diff = [abs(x - y) for x, y in zip(int_cube, self._cube)]
        ind = np.argmax(diff)
        int_cube[ind] = -(np.sum(int_cube)) + int_cube[ind]
        int_cube = [int(_) for _ in int_cube]
        return _Vec(*int_cube)


class _Hexagon:
    """Class _Hexagon represents a location on the board / in the plane.
    It is for internal use only.
    """

    def complete_arguments(row, column, cube, game):
        """An hexagon can be defined be two different sets of coordinates:
        offset (row, column) and cube (q, r, s).
        This method completes missing coordinates"""
        if (row is not None) and (column is not None):
            # _Hexagon is given as offset = [row, column]
            # compute cube coordinates. offset [1, 1] is cube [0, 0, 0]
            q = column - 1
            r = row - 1 - (q - (q % 2)) // 2
            s = -q - r
        elif cube is not None:
            # _Hexagon is given as cube = [q, r, s]
            q, r, s = cube
            if q + r + s != 0:
                raise Exception(f"cube coordinates {[q, r, s]} don't sum up to 0")
            column = q + 1
            row = r + (q - (q % 2)) // 2 + 1
        if 1 <= column <= game.width and 1 <= row <= game.height:
            lind = int((row - 1) * game.width + (column - 1))
        else:
            # tile is not on board, so it has no linear index
            lind = None
        return lind, (row, column), (q, r, s)

    def __init__(self, row=None, column=None, cube=None, game=None):
        self._game = game or _active_game()
        self._lind, self._offset, self._cube = _Hexagon.complete_arguments(
            row, column, cube, self._game
        )
        if self._lind is None:
            self._saved_color_id = 0

    @property
    def _q(self):
        return self._cube[0]

    @property
    def _r(self):
        return self._cube[1]

    @property
    def _s(self):
        return self._cube[2]

    @property
    def _color_id(self):
        if self._lind is None:
            return self._saved_color_id
        else:
            return self._game.board_state[self._lind]

    @property
    def _color(self):
        return COLORS[self._color_id]

    @property
    def _row(self):
        return self._offset[0]

    @property
    def _column(self):
        return self._offset[1]

    def _show(self):
        logger.debug(
            "%s instance: row=%s, column=%s, lind=%s, color=%s",
            self.__class__.__name__,
            self._row,
            self._column,
            self._lind,
            self._color_id,
        )

    def _from_lind(lind, game=None):
        """Returns a hexagon by its linear index on the board"""

        g = game or _active_game()
        if lind in range(g.width * g.height):
            row = lind // (g.width) + 1
            column = lind % g.width + 1
            return _Hexagon(row=row, column=column, game=g)
        logger.debug("lind %s not valid", lind)

    def _on_board(self):
        """Returns True iff self lies on the board"""

        return self._lind is not None

    def __sub__(self, other):
        """Compute the difference between self and other
        The difference is a _Vec object"""

        return _Vec(*[int(_) for _ in [x - y for x, y in zip(self._cube, other._cube)]])

    def _shift(self, *args):
        """Compute a new hexagon by shifting self to another location"""

        if isinstance(args[0], _Vec):
            vec = args[0]
        else:
            vec = _Vec(*args)
        new_cube = [int(_) for _ in [x + y for x, y in zip(self._cube, vec._cube)]]
        return _Hexagon(cube=new_cube)

    def _copy_paste(self, vec, color=None):
        """Copy self to another location
        Compute the new location and draw there"""

        new_tile = self._shift(vec)
        new_tile._draw(self._color_id if color is None else color)
        return new_tile

    def _reflect(
        self, axis_line=None, column=None, axis_direction=None, hexagon_on_axis=None
    ):
        """Reflect self
        Compute the new location and draw there"""

        if axis_direction == "horizontal":
            direction_vec = _Vec(2, -1, -1)
        else:
            if axis_line is not None:
                direction_vec = axis_line._direction_vec
                hexagon_on_axis = axis_line[0]._hexagon
            else:
                if axis_direction == "vertical" or column is not None:
                    axis_direction = "up"
                direction_vec = _Vec(axis_direction)

        v_direction_reciprocal = np.array(
            [
                direction_vec._r - direction_vec._s,
                direction_vec._s - direction_vec._q,
                direction_vec._q - direction_vec._r,
            ]
        )
        v_direction_reciprocal = v_direction_reciprocal / np.linalg.norm(
            v_direction_reciprocal
        )
        if column is not None:
            # we assume if axis_value is given it represents a column number
            column = column % (self._game.width + 1)
            axis_value = column - 1
            ind = direction_vec._cube.index(0)
            cube = _Vec.cyclic_permutation([axis_value, -axis_value, 0], ind)
            v_on_axis = np.array(cube)
        else:
            v_on_axis = np.array(hexagon_on_axis._cube)
        v_self = np.array(self._cube)
        v_diff = v_self - v_on_axis
        val_reciprocal = v_diff.dot(v_direction_reciprocal)
        reflect_vec = _Vec(*list(-2 * val_reciprocal * v_direction_reciprocal))._round()
        new_tile = self._shift(reflect_vec)
        new_tile._draw(self._color)
        return new_tile

    def _rotate(self, center, angle):
        """Rotate self
        Compute the new location and draw there"""

        v_self = np.array(self._cube)
        v_center = np.array(center._cube)
        rotvec = np.ones(3) / np.sqrt(3) * (angle / 60 * np.pi / 3)
        R = Rotation.from_rotvec(rotvec).as_matrix()
        v_new = np.matmul(v_self - v_center, R) + v_center
        new_tile_vec = _Vec(*list(v_new))._round()
        new_tile = _Hexagon(cube=new_tile_vec._cube)
        new_tile._draw(self._color)
        return new_tile

    def _draw(self, color):
        """Paint self with the given color"""

        color_id = COLORS.index(color) if isinstance(color, str) else color
        if self._lind is not None:
            self._game.board_state[self._lind] = color_id
        else:
            self._saved_color_id = color_id
        if self._game._current_step_name is not None:
            self._game._step_drawn_hexagons[self._game._current_step_name].append(self)
        if self._game._current_batch_name is not None:
            self._game._batch_draws[self._game._current_batch_name].append(
                {
                    "index": self._lind,
                    "row": self._row,
                    "column": self._column,
                    "color": color,
                }
            )

        return self

    def _neighbor(self, direction):
        """Return the neighbor of self in the given direction"""

        if direction not in DIRECTIONS:
            raise Exception(f"{direction} is not in - {list(DIRECTIONS.keys())}")

        if not isinstance(direction, _Vec):
            vec = _Vec(direction)
        return self._shift(vec)

    def _neighbors(self, criterion="all"):
        """Return all the neighbors of self"""

        if self._lind is None:
            return []
        return [
            self._shift(_Vec(*direction_cube)) for direction_cube in DIRECTIONS.values()
        ]


class Shape:
    """Class Shape represents any set of tiles on the board,
    including an empty set and a single tile"""

    def __init__(
        self, tiles, from_linds: bool = False, from_hexagons: bool = False, game=None
    ):
        """
        Construct a new Shape from tiles, shapes, or any mixture of them.

        Parameters
        ----------
        tiles : Tile | Shape | Iterable[Tile | Shape]
            Components that will make up the shape.  Examples:

                Shape(Tile(1,1))                         # single tile
                Shape(other_shape)                       # copy‐constructor
                Shape([Tile(1,1), Tile(2,1)])            # list of tiles
                Shape([shape_a, Tile(3,3), shape_b])     # **mixed tiles & shapes**
        """
        self.game = game or _active_game()

        # ── Handle the three special constructor modes ───────────────────────────
        if from_linds:
            linds = tiles
            hexagons = [_Hexagon._from_lind(lind, game=self.game) for lind in linds]

        elif from_hexagons:
            hexagons = tiles

        # ── Normal mode: accept Tile, Shape, or Iterable containing them ─────────
        else:
            # Wrap single objects so that we can iterate uniformly
            if isinstance(tiles, (Tile, Shape)):
                tiles = [tiles]

            # Flatten whatever mixture we were given
            hexagons: List[_Hexagon] = []
            for item in tiles:
                if isinstance(item, Tile):
                    hexagons.append(item._hexagon)
                elif isinstance(item, Shape):
                    hexagons.extend(item._hexagons)
                else:
                    raise TypeError(
                        f"Shape components must be Tile or Shape instances, not {type(item)}"
                    )

        # ── Deduplicate vertices ─────────────────────────────────────────────────
        unique_hexagons: List[_Hexagon] = []
        seen_cubes = set()
        for hx in hexagons:
            if hx._cube not in seen_cubes:
                seen_cubes.add(hx._cube)
                unique_hexagons.append(hx)
        self._hexagons = tuple(unique_hexagons)

        # A shape of size 1 behaves like a Tile
        if len(self._hexagons) == 1:
            self.__class__ = Tile

    @property
    def _size(self):
        return len(self._hexagons)

    @property
    def _linds(self):
        return [hexagon._lind for hexagon in self._hexagons]

    @property
    def tiles(self):
        return [Tile(hexagon._row, hexagon._column) for hexagon in self._hexagons]

    @property
    def colors(self):
        return [hexagon._color for hexagon in self._hexagons]

    @property
    def columns(self):
        """The list of columns of the tiles in the shape"""

        return [hexagon._column for hexagon in self._hexagons]

    @property
    def rows(self):
        """The list of rows of the tiles in the shape"""

        return [hexagon._row for hexagon in self._hexagons]

    @property
    def _cubes(self):
        """The list of cube coordinates of the tiles in the shape"""

        return [hexagon._cube for hexagon in self._hexagons]

    @property
    def _qs(self):
        """The list of q-coordinates of the tiles in the shape"""
        return [hexagon._q for hexagon in self._hexagons]

    @property
    def _rs(self):
        """The list of r-coordinates of the tiles in the shape"""
        return [hexagon._r for hexagon in self._hexagons]

    @property
    def _ss(self):
        """The list of s-coordinates of the tiles in the shape"""
        return [hexagon._s for hexagon in self._hexagons]

    def _show(self):
        logger.debug(
            "%s instance: size=%s, linds=%s",
            self.__class__.__name__,
            self._size,
            self._linds,
        )

    def __iter__(self):
        self.n = 0
        return self

    def __next__(self):
        if self.n < self._size:
            result = self.tiles[self.n]
            self.n += 1
            return result
        else:
            raise StopIteration

    def __getitem__(self, item):
        return self.tiles[item]

    def __add__(self, other):
        """Use the '+' sign to compute the union of two shapes"""

        cubes = list(set(self._cubes) | set(other._cubes))
        hexs = [_Hexagon(cube=cube) for cube in cubes]
        return Shape(hexs, from_hexagons=True)

    def __mul__(self, other):
        """Use the '*' sign to compute the intersection of two shapes"""

        cubes = list(set(self._cubes) & set(other._cubes))
        hexs = [_Hexagon(cube=cube) for cube in cubes]
        return Shape(hexs, from_hexagons=True)

    def __sub__(self, other):
        """Use the '-' sign to compute the difference between two shapes"""

        cubes = list(set(self._cubes).difference(set(other._cubes)))
        hexs = [_Hexagon(cube=cube) for cube in cubes]
        return Shape(hexs, from_hexagons=True)

    def _compute_shift_from_spacing(self, direction, spacing, reference_shape=None):
        """Compute how much to shift a shape, to create a copy with a desired spacing from self
        For internal use only"""

        if reference_shape is None:
            reference_shape = self
        vec_diff = reference_shape._center_of_mass() - self._center_of_mass()
        initial_shift = vec_diff._round()
        initial_new_shape = self._shift(initial_shift)

        def scale_shift(direction, k):
            if direction == "left":
                return _Vec(-k, 0)
            elif direction == "right":
                return _Vec(k, 0)
            else:
                return _Vec(direction)._scale(k)

        for k in range(max(self.game.width, self.game.height), -1, -1):
            if reference_shape.overlaps(
                initial_new_shape._shift(scale_shift(direction, k))
            ):
                break

        return initial_shift + scale_shift(direction, k + 1 + spacing)

    def _center_of_mass(self):
        cubes_arr = np.array([hexagon._cube for hexagon in self._hexagons])
        return _Vec(*np.mean(cubes_arr, axis=0))

    def _entirely_on_board(self):
        return None not in self._linds

    def is_empty(self):
        """
        Return True iff self is empty

        Returns:
        --------
        bool
          True of self is empty, False otherwise
        """

        return self._size == 0

    def overlaps(self, S):
        return not (self * S).is_empty()

    def _reduce_to_board(self):
        return Shape([tile for tile in self if tile.on_board()])

    def draw(self, color):
        """
        Draw the tiles of self in the given color

        Parameters:
        -----------
        color: str
          The color
        """

        for hexagon in self._hexagons:
            hexagon._draw(color)

        return self

    def copy_paste(
        self,
        shift_direction=None,
        spacing=0,
        reference_shape=None,
        source=None,
        destination=None,
        shift=None,
    ):
        """
        Draw a copy of self in a new location

        Parameters:
        -----------
        shift_direction: str
          The direction of the new shape relative to self.
          Supported values:
          - any item of DIRECTIONS
          - 'right'
          - 'left'
        spacing: int
          Number of tiles between self and the new shape
        reference_shape: Shape
          The new location is computed with respect to reference_shape.
          If not specified, location is computed with respect to the original shape.
        source: Tile
        destination: Tile
          Compute the shift such that tile 'source' will be copied to tile 'destination'
          This option is activated if 'shift_direction' is not provided
        shift: _Vec
          Specify the shift vector directly. This option is for internal use only.

        Returns:
        --------
        Shape
          New Shape object
        """

        if not self._linds:
            raise Exception("Cannot use copy_paste on an empty shape")

        if shift is None:
            if shift_direction is None:
                shift = Tile._compute_shift_from_tiles(source, destination)
            else:
                shift = self._compute_shift_from_spacing(
                    shift_direction, spacing, reference_shape
                )

        new_hexagons = []
        for hexagon in self._hexagons:
            hexagon._copy_paste(shift)
            new_hexagons.append(hexagon._shift(shift))
        new_shape = Shape(new_hexagons, from_hexagons=True)
        return new_shape

    def grid(self, shift_direction, spacing, num_copies=None):
        """
        Draw copies of self along a grid.
        This is done by repeated calls to 'copy_paste'.

        Parameters:
        -----------
        shift_direction: str
          The direction in which to shift the shape
        spacing: int
          Number of tiles between the original shape and the new shape
        num_copies: int
          The number of copies to create, not including the original shape.
          If not specified, the method creates the maximal possible number of complete copies.

        Returns:
        --------
        Shape
          New Shape object that holds the original shape and all its copies
        """

        if not self._linds:
            raise Exception("Cannot use grid on an empty shape")

        shift = self._compute_shift_from_spacing(shift_direction, spacing, None)

        grid = self
        k = 0
        shape = self
        while (num_copies is None and shape._shift(shift)._entirely_on_board()) or (
            num_copies is not None and k < num_copies
        ):
            shape = shape.copy_paste(shift=shift)
            grid = grid + shape
            k += 1
        return grid

    def reflect(
        self, axis_line=None, column=None, axis_direction=None, tile_on_axis=None
    ):
        """
        Draw a reflection of self
        The reflection is done through some axis-line on the board, and there are a few
        ways to define such line

        Parameters:
        -----------
        axis_line: Line
          Reflect self through this line
        column: int
          Reflect self through this line
        axis_direction: str
          Reflect self through a line in this direction (line is still underspecified)
          Can be any item of DIRECTIONS, or 'horizontal'
        tile_on_axis: Tile
          Specifies a tile on the axis of reflection
          Together with 'axis_direction' this specifies an axis-line

        Returns:
        --------
        Shape
          New Shape object that holds the original shape and all its copies
        """

        if not self._linds:
            raise Exception("Cannot use reflect on an empty shape")

        new_hexagons = []
        hexagon_on_axis = None if tile_on_axis is None else tile_on_axis._hexagon
        for hexagon in self._hexagons:
            new_hexagons.append(
                hexagon._reflect(
                    axis_line=axis_line,
                    column=column,
                    axis_direction=axis_direction,
                    hexagon_on_axis=hexagon_on_axis,
                )
            )
        new_shape = Shape(new_hexagons, from_hexagons=True)
        return new_shape

    def rotate(self, center_tile, angle):
        """
        Draw a rotation of self

        Parameters:
        -----------
        center_tile: Tile
          The tile around which to rotate
        angle: int
          Sets the angle of rotation, counterclockwise. Should be a multiple of 60.

        Returns:
        --------
        Shape
          New Shape object that holds the original shape and all its copies
        """

        if not self._linds:
            raise Exception("Cannot use rotate on an empty shape")

        new_hexagons = []
        for hexagon in self._hexagons:
            new_hexagons.append(
                hexagon._rotate(center=center_tile._hexagon, angle=angle)
            )
        new_shape = Shape(new_hexagons, from_hexagons=True)
        return new_shape

    def recolor(self, color_map):
        """
        re-color each tile in the shape
        color_map describes a mapping from colors to colors, e.g. {'red': 'blue', 'green': 'black'}
        """
        for hexagon in self._hexagons:
            if hexagon._on_board():
                hexagon._draw(color_map[hexagon._color])
        return self

    def _shift(self, V):
        """Shift self in some direction
        For internal use only"""

        return Shape(
            [hexagon._shift(V) for hexagon in self._hexagons], from_hexagons=True
        )

    def _get_color(self, color):
        if color not in COLORS:
            raise ValueError(
                f"Unknown color '{color}'. Valid colors: {COLORS + ['all','any']}"
            )

        return Shape([t for t in self.tiles if t.color == color], game=self.game)

    def get_entire_board(game=None):
        """Return a Shape object containing all the tiles on the board"""

        g = game or _active_game()
        tiles = []
        for row in range(1, g.height + 1):
            for column in range(1, g.width + 1):
                tiles.append(Tile(row, column))
        return Shape(tiles, game=g)

    def get_board_perimeter(game=None):
        """Return a Shape object containing all the tiles on the board's perimeter"""

        g = game or _active_game()
        B = Shape.get_entire_board(game=g)

        def tile_on_perimeter(tile):
            return tile.column in [1, g.width] or tile.row in [1, g.height]

        return Shape([tile for tile in B if tile_on_perimeter(tile)], game=g)

    def get_color(color, game=None):
        """Return a Shape object containing all the tiles painted in the given color
        If color is 'any' is will return all the tiles that are not white"""

        g = game or _active_game()
        if color in ["all", "any"]:
            return Shape(
                [
                    tile
                    for tile in Shape.get_entire_board(game=g).tiles
                    if tile.color != "white"
                ],
                game=g,
            )
        return Shape(
            [
                tile
                for tile in Shape.get_entire_board(game=g).tiles
                if tile.color == color
            ],
            game=g,
        )

    def get_column(column, game=None):
        """Return a Shape object containing all the tiles in the given column"""

        g = game or _active_game()
        return Shape([Tile(row, column) for row in range(1, g.height + 1)], game=g)

    def _get_directional_tiles(self, direction):
        """Return tiles in a given direction relative to self."""
        direction_cube = DIRECTIONS[direction]
        direction_ind = direction_cube.index(0)
        next_ind = (direction_ind + 1) % 3
        next_grows = direction_cube[next_ind] == 1
        shape_lines = [cube[direction_ind] for cube in self._cubes]
        hexagons = []
        entire_board_hexagons = Shape.get_entire_board(game=self.game)._hexagons
        for val in np.unique(shape_lines):
            hexagons_with_val = [
                hexagon
                for hexagon in self._hexagons
                if hexagon._cube[direction_ind] == val
            ]
            if next_grows:
                max_val = np.max([_._cube[next_ind] for _ in hexagons_with_val])
                hexagons += [
                    hex
                    for hex in entire_board_hexagons
                    if hex._cube[direction_ind] == val and hex._cube[next_ind] > max_val
                ]
            else:
                min_val = np.min([_._cube[next_ind] for _ in hexagons_with_val])
                hexagons += [
                    hex
                    for hex in entire_board_hexagons
                    if hex._cube[direction_ind] == val and hex._cube[next_ind] < min_val
                ]

        return Shape(hexagons, from_hexagons=True)

    def _get_outside_tiles(self):
        """Return tiles outside self using flood-fill from board perimeter."""
        S_ext = Shape.get_board_perimeter(game=self.game) - self
        while True:
            S_ext_neighbors_not_in_self = (
                S_ext.neighbors("all") - self
            ) * Shape.get_entire_board(game=self.game)
            # stop if S_ext didn't grow in the last iteration
            if S_ext_neighbors_not_in_self._size == 0:
                break
            else:
                S_ext += S_ext_neighbors_not_in_self
        return S_ext

    def _get_inside_tiles(self):
        """Return tiles inside self (complement of outside tiles)."""
        return (
            Shape.get_entire_board(game=self.game) - self
        ) - self._get_outside_tiles()

    def _validate_criterion_shape_compatibility(self, criterion):
        """Validate that criterion makes sense for this shape and warn if problematic."""
        import warnings

        # Check for conceptually meaningless combinations
        if self._size == 0:
            warnings.warn(
                f"Applying criterion '{criterion}' to empty shape - result will be empty",
                UserWarning,
                stacklevel=3,
            )
            return

        if self._size == 1:
            if criterion in ["corners", "endpoints"]:
                warnings.warn(
                    f"Applying '{criterion}' to single tile - result will be empty",
                    UserWarning,
                    stacklevel=3,
                )
            elif criterion in ["inside", "outside"]:
                warnings.warn(
                    f"Applying '{criterion}' to single tile - conceptually meaningless",
                    UserWarning,
                    stacklevel=3,
                )

        # Check for potentially problematic combinations
        if criterion == "inside" and self._size <= 3:
            warnings.warn(
                f"Applying 'inside' to small shape (size {self._size}) - may have no interior",
                UserWarning,
                stacklevel=3,
            )

        if criterion in ["endpoints"] and self._is_likely_closed_shape():
            warnings.warn(
                f"Applying 'endpoints' to likely closed shape - may not be meaningful",
                UserWarning,
                stacklevel=3,
            )

    def _is_likely_closed_shape(self):
        """Heuristic to detect if shape is likely closed (no obvious endpoints)."""
        if self._size <= 2:
            return False

        # Check if any boundary tile has only 1 neighbor in the boundary (indicating endpoint)
        try:
            boundary = self.boundary("outer")
            for hex in boundary._hexagons:
                neighbors_in_boundary = (
                    Shape(hex._neighbors(), from_hexagons=True) * boundary
                )
                if neighbors_in_boundary._size == 1:
                    return False  # Found an endpoint, so not closed
            return True  # No endpoints found, likely closed
        except:
            return False  # If boundary fails, assume not closed

    def _get_extreme_tiles(self, criterion):
        """Return extreme points like corners, endpoints, top, bottom tiles."""
        if criterion == "top":
            return self._max("up")

        if criterion == "bottom":
            return self._max("down")

        if criterion == "corners":
            ext = self.boundary("outer")
            corners = []
            for hexagon in ext._hexagons:
                neighbors = (
                    Shape(hexagon._neighbors(), from_hexagons=True) * ext
                )._hexagons
                if len(neighbors) == 2:
                    v0 = hexagon - neighbors[0]
                    v1 = hexagon - neighbors[1]
                    # Check if vectors are NOT collinear (i.e., they form a corner)
                    # In hex coordinates, collinear vectors pointing in opposite directions sum to (0,0,0)
                    sum_vec = v0 + v1
                    sum_magnitude = sum_vec._norm()
                    # A corner exists if the vectors don't cancel out (not collinear/opposite)
                    if sum_magnitude > 0.0001:
                        corners.append(hexagon)
            return Shape(corners, from_hexagons=True)

        if criterion == "endpoints":
            ext = self.boundary("outer")
            ends = []
            for hexagon in ext._hexagons:
                neighbors = (
                    Shape(hexagon._neighbors(), from_hexagons=True) * ext
                )._hexagons
                if len(neighbors) == 1:
                    ends.append(hexagon)
            return Shape(ends, from_hexagons=True)

    def get(self, criterion, _allow_open=False):
        """
        Return a new shape according to some geometrical relation with self, described by ‘criterion’
        Options:
        - 'outside' / 'inside': the tiles outside/inside self
        - 'above' / 'below': tiles that lie above/below self
        - 'top' / 'bottom': to topmost/bottommost tiles of self
        - 'corners': the corners of self. If the shape is a polygon, these will be the polygon’s vertices
        - 'endpoints': the endpoints of self. If the shape is a line, these will be the ends of the line
        - COLORS: get the tiles with provided color
        """

        if not self._linds:
            raise Exception("Cannot use get on an empty shape")

        if criterion in ["outside", "inside"]:
            if self.is_open() and not _allow_open:
                raise Exception(
                    "Cannot use get('outside') or get('inside') on an open shape"
                )

        if criterion in COLORS:
            return self._get_color(criterion)

        if criterion == "outside":
            return self._get_outside_tiles()

        if criterion == "inside":
            return self._get_inside_tiles()

        if criterion == "above":
            return self._get_directional_tiles("up")

        if criterion == "below":
            return self._get_directional_tiles("down")

        if criterion in DIRECTIONS:
            return self._get_directional_tiles(criterion)

        if criterion == "top":
            return self._get_extreme_tiles("top")

        if criterion == "bottom":
            return self._get_extreme_tiles("bottom")

        if criterion == "corners":
            return self._get_extreme_tiles("corners")

        if criterion == "endpoints":
            return self._get_extreme_tiles("endpoints")

        raise ValueError(
            f"Unrecognized criterion: {criterion} use one of the following: outside, inside, above, below, top, bottom. corners"
        )

    def boundary(self, criterion="all"):
        """Return the boundary of the shape. These are tiles that are part of the shape and touch
        tiles that are not part of the shape.

        Parameters:
        ---------------
        criterion: str
          Criterion to select parts of the boundary
          - ‘all’: the entire boundary
          - 'outer’: tiles that touch tiles that are outside the shape
          - ‘inner’: tiles that touch tiles that are inside the shape

        Returns:
        ---------------
        Shape
          New Shape object
        """

        if not self._linds:
            raise Exception("Cannot use boundary on an empty shape")

        if criterion == "outer":
            return self.get("outside", _allow_open=True).neighbors("all") * self

        if criterion == "inner":
            if self.is_open():
                raise Exception("Cannot use boundary('inner') on an open shape")
            return self.get("inside").neighbors("all") * self

        return self.boundary("outer") + self.boundary("inner")

    def _max(self, direction):
        """Returns a Shape object containing the tiles of the shape which are maximal in the given direction
        For internal use only"""

        direction_cube = DIRECTIONS[direction]
        direction_ind = direction_cube.index(0)
        next_ind = (direction_ind + 1) % 3
        next_grows = direction_cube[next_ind] == 1
        shape_lines = [cube[direction_ind] for cube in self._cubes]
        hexagons = []
        for val in np.unique(shape_lines):
            hexagons_with_val = [
                hexagon
                for hexagon in self._hexagons
                if hexagon._cube[direction_ind] == val
            ]
            if next_grows:
                hexagons.append(
                    hexagons_with_val[
                        np.argmax([_._cube[next_ind] for _ in hexagons_with_val])
                    ]
                )
            else:
                hexagons.append(
                    hexagons_with_val[
                        np.argmin([_._cube[next_ind] for _ in hexagons_with_val])
                    ]
                )
        return Shape(hexagons, from_hexagons=True)

    def is_open(self):
        """Return True if the shape does not enclose any area."""

        entire_board = Shape.get_entire_board(game=self.game)
        outside = Shape.get_board_perimeter(game=self.game) - self
        while True:
            S_ext_neighbors_not_in_self = (
                outside.neighbors("all") - self
            ) * entire_board
            if S_ext_neighbors_not_in_self._size == 0:
                break
            else:
                outside += S_ext_neighbors_not_in_self
        inside = (entire_board - self) - outside
        return inside.is_empty()

    def extreme(self, direction):
        """Returns a Shape object containing the extreme tiles of self in the given direction"""

        if not self._linds:
            raise Exception("Cannot use extreme on an empty shape")

        if direction not in DIRECTIONS:
            raise Exception(
                f"Can't get extreme of Shape - {direction} is not in - {list(DIRECTIONS.keys())}"
            )

        def height(cube, dcube):
            return cube[0] * dcube[0] + cube[1] * dcube[1] + cube[2] * dcube[2]

        direction_cube = DIRECTIONS[direction]
        hexagons = self._max(direction)._hexagons
        heights = [height(hexagon._cube, direction_cube) for hexagon in hexagons]
        vhexagons = []
        for i in range(len(heights)):
            if (i == 0 or heights[i] > heights[i - 1]) and (
                i == len(heights) - 1 or heights[i] > heights[i + 1]
            ):
                vhexagons.append(hexagons[i])
        return Shape(vhexagons, from_hexagons=True)

    def edge(self, direction):
        """Return the edge tiles of self according to some direction"""

        if not self._linds:
            raise Exception("Cannot use neighbors on an empty shape")

        if direction in ["up", "top"]:
            return self._max("up")
        if direction in ["down", "bottom"]:
            return self._max("down")

        if direction in ["right", "left"]:
            shape_lines = self._qs
        elif direction in ["down_left", "up_right"]:
            shape_lines = self._rs
        elif direction in ["up_left", "down_right"]:
            shape_lines = self._ss

        if direction in ["down_left", "up_left", "right"]:
            extreme_line = np.amax(shape_lines)
        else:
            extreme_line = np.amin(shape_lines)

        return Shape(
            [
                tile
                for tile, line in zip(self.tiles, shape_lines)
                if line == extreme_line
            ]
        )

    def neighbors(self, criterion="all"):
        """Return a Shape object containing the neighbors of self, or a subset of them,
        according to some criterion.

        Options:
        - ‘all’: all the neighbors of the shape
        - ‘right’ / ‘left’: neighbors to the right/left of the shape
        - ‘above’ / ‘below’: neighbors from above/below the shape
        - ‘outside’ / ‘inside’: neighbors outside/inside the shape
        - ‘white’: blank neighbors
        """

        if not self._linds:
            raise Exception("Cannot use neighbors on an empty shape")

        if criterion == "all":
            return (
                Shape(
                    [
                        neighbor_hexagon
                        for hexagon in self._hexagons
                        for neighbor_hexagon in hexagon._neighbors()
                    ],
                    from_hexagons=True,
                )
                - self
            )
        if criterion in ["right", "left"]:
            edge = self.edge(criterion)
            down = Shape([_.neighbor("down_" + criterion) for _ in edge])
            up = Shape([_.neighbor("up_" + criterion) for _ in edge])
            return down * up
        if criterion in ["above", "up"]:
            return self.get("above") * self.neighbors()
        if criterion in ["below", "down"]:
            return self.get("below") * self.neighbors()
        if criterion == "outside":
            if self.is_open():
                raise Exception("Cannot use neighbors('outside') on an open shape")
            return self.neighbors("all") * self.get("outside")
        if criterion == "inside":
            if self.is_open():
                raise Exception("Cannot use neighbors('inside') on an open shape")
            return self.neighbors("all") * self.get("inside")
        if criterion == "white":
            return (
                Shape(
                    [
                        tile
                        for tile in Shape.get_entire_board(game=self.game)
                        if tile.color == "white"
                    ],
                    game=self.game,
                )
                * self.neighbors()
            )
        if criterion in DIRECTIONS:
            return self.get(criterion) * self.neighbors()

    def neighbor(self, direction):
        """Return self's neighbor(s) in a given direction"""

        if not self._linds:
            raise Exception("Cannot use neighbor on an empty shape")

        if direction not in DIRECTIONS:
            raise Exception(
                f"Can't get neighbor of Shape - {direction} is not in - {list(DIRECTIONS.keys())}"
            )

        return Shape([tile.neighbor(direction) for tile in self.tiles]) - self

    def polygon(vertices, *args):
        """Return a polygon with the given vertices"""

        if isinstance(vertices, Shape):
            tiles = vertices.tiles
        elif isinstance(vertices, List):
            tiles = vertices
        else:
            tiles = [vertices] + args
        com = Shape(tiles)._center_of_mass()
        hexagons = Shape(tiles)._hexagons

        def angle(self, other):
            self_reciprocal = _Vec(
                *[self._r - self._s, self._s - self._q, self._q - self._r]
            )
            v_self = np.array(self._cube)
            v_self_reciprocal = np.array(self_reciprocal._cube)
            v_other = np.array(other._cube)
            # print(n_self.dot(n_other)) / np.linalg.norm(self_reciprocal._cube)
            # print(n_self.dot(n_other))
            product = (
                v_self.dot(v_other) / np.linalg.norm(v_self) / np.linalg.norm(v_other)
            )
            product = min(product, 1.0)
            product = max(product, -1.0)
            angle = np.arccos(product)
            if v_self_reciprocal.dot(v_other) < 0:
                angle = 2 * np.pi - angle
            return angle

        vecs = [_Vec(*hexagon._cube) - com for hexagon in hexagons]
        angles = [angle(vecs[0], _) for _ in vecs]
        sorted_tiles = [tile for angle, tile in sorted(zip(angles, tiles))]
        polygon = Shape([])
        for i in range(len(sorted_tiles)):
            polygon += Line(
                start_tile=sorted_tiles[i],
                end_tile=sorted_tiles[(i + 1) % len(sorted_tiles)],
            )

        return polygon

    def center(self):
        """Rturns the center of mass of self.
        If the center of mass is not an exact tile location, it will round it to be a tile location
        """

        if not self._linds:
            raise Exception("Cannot use center on an empty shape")

        hexagon_mean = _Hexagon(cube=self._center_of_mass()._round()._cube)
        return Tile(hexagon_mean._offset[0], hexagon_mean._offset[1])


class Tile(Shape):
    """
    A Class to represent a tile on the board

    Attributes:
    -----------
    row: int
      The row on which this tile is located. starts from 1 and counted from top to bottom
    column: int
      The column on which the tile is located. starts at 1 and counted from left to right
    color: str
      The color of the tile
    """

    def __init__(self, row, column, game=None):
        """
        Construct a new tile. The default color is ‘white’.

        Parameters:
        -----------
        row: int
          The row on which this tile is located. Starts from 1 and counted from top to bottom.
          A negative value represents counting from bottom to top. E.g., the first row from the bottom is -1.
        column: int
          The column on which the tile is located. Starts at 1 and counted from left to right.
          A negative value represents counting from right to left. E.g., the first column from the right is -1.
        """
        self.game = game or _active_game()
        column = column % (self.game.width + 1)
        row = row % (self.game.height + 1)
        self._hexagons = [_Hexagon(row=row, column=column, cube=None, game=self.game)]

    @property
    def _hexagon(self):
        return self._hexagons[0]

    @property
    def _lind(self):
        return self._hexagon._lind

    @property
    def color(self):
        return self._hexagon._color

    @property
    def column(self):
        return self._hexagon._column

    @property
    def row(self):
        return self._hexagon._row

    @property
    def offset(self):
        return self._hexagon._offset

    def _show(self):
        logger.debug(
            "%s instance: row=%s, column=%s, lind=%s, color=%s",
            self.__class__.__name__,
            self.row,
            self.column,
            self._lind,
            self.color,
        )

    def _to_tile(_hexagon):
        return Shape([_hexagon], from_hexagons=True)

    def on_board(self):
        return self._lind is not None

    def neighbor(self, direction):
        """
        Return the neighbor of self in the given direction.

        Parameters:
        -----------
        direction: str
          Must be an item of DIRECTIONS

        Returns:
        --------
        Tile
          new Tile object
        """

        if direction not in DIRECTIONS:
            raise Exception(
                f"Can't get neighbor of Tile - {direction} is not in - {list(DIRECTIONS.keys())}"
            )

        return Tile._to_tile(self._hexagon._neighbor(direction))

    def __str__(self):
        return f"Tile(row={self.row}, column={self.column}, color='{self.color}')"

    # TODO: unit_test
    # TODO: copy_paste upadates
    def _compute_shift_from_tiles(source, destination):
        """Computes the shift from tile 'source' to tile 'destination'
        Returns a _Vec object
        Used in Shape.copy_paste()
        """
        return destination._hexagon - source._hexagon


class Line(Shape):
    """A class to represent a straight line on the board.

    Attributes:
    ---------------
      start_tile: Tile
        First tile of the line
      end_tile: Tile
        Last tile of the line
      color: str
        The color of the line
      direction: str
        The direction of the line.
    """

    def __init__(
        self,
        start_tile: Tile,
        end_tile: Optional[Tile] = None,
        direction: str = None,
        length: int = None,
        end_tiles: Optional[Shape] = None,
        include_start_tile: bool = True,
        include_end_tile: bool = True,
    ):
        """
        Parameters:
        ---------------
        start_tile: Tile
          Where the line starts. Should always be specified
        end_tile: Tile
          Where the line ends. If this specified, direction and length are redundant.
        direction: str
          Any item of DIRECTIONS. The line's direction. If length is not specified, the line will continue until it
          reaches the board's perimeter
        length: int
          The line's length
        include_start_tile: bool
          If false, do not include the tile 'start_tile' in the line
        include_end_tile: bool
          If false, do not include the tile 'end_tile' in the line
        end_tiles: Shape | None
          Continue the line until you reach a tile that belongs to the shape
        """

        shexagon = start_tile._hexagon
        g = start_tile.game
        if end_tiles is None:
            end_tiles = Shape([], game=g)
        if length is None:
            length = max(g.height, g.width)
        if length <= 0:
            raise Exception(f"Cannot draw Line with non-positive length {length}")
        if end_tile is not None:
            if start_tile.row == end_tile.row and start_tile.column == end_tile.column:
                raise Exception(
                    f"Cannot create Line: start_tile and end_tile cannot be the same tile"
                )

            ehexagon = end_tile._hexagon
            v = ehexagon - shexagon
            direction_vec = v._normalize()

            if direction_vec is None:
                raise Exception(
                    f"Cannot create Line: tiles ({start_tile.row}, {start_tile.column}) and ({end_tile.row}, {end_tile.column}) are not colinear on any of the three hex-grid axes"
                )

            distance = v._norm()
            length = distance - 1 + 1 * include_start_tile + 1 * include_end_tile
        else:
            if direction not in DIRECTIONS:
                raise Exception(
                    f"Cannot create Line: direction {direction} is not in {list(DIRECTIONS.keys())}"
                )
            direction_vec = _Vec(direction)
        if not include_start_tile:
            shexagon = shexagon._shift(direction_vec)
        count = 0
        hexagons = []
        hexagon = shexagon
        while (
            count < length
            and hexagon._on_board()
            and hexagon._cube not in end_tiles._cubes
        ):
            hexagons.append(hexagon)
            hexagon = hexagon._shift(direction_vec)
            count += 1
        super().__init__(hexagons, from_hexagons=True, game=g)
        self.game = g
        self.length = len(hexagons)
        # self.color = None
        self._direction_vec = direction_vec
        self.direction = direction_vec._direction_str()
        if len(hexagons) > 1:
            self.start_tile = Tile._to_tile(hexagons[0])
            self.end_tile = Tile._to_tile(hexagons[-1])
            qrs_ind = direction_vec._cube.index(0)
            self.constant_value = hexagons[0]._cube[qrs_ind]

    def _show(self):
        logger.debug(
            "%s instance: linds=%s, size=%s, direction=%s, start=%s, end=%s, color=%s",
            self.__class__.__name__,
            self._linds,
            self._size,
            self.direction,
            self.tiles[0].offset,
            self.tiles[-1].offset,
            self.color,
        )

    def parallel(self, shift_direction, spacing):
        """Create a new line parallel to self, in the given direction, with the given spacing from self
        This is different from Shape.copy_paste() because it doesn't copy the line, but rather creates a new line,
        which can be of different length from self.
        The new line will stretch as far as possible in both directions.

        Parameters:
        ---------------
        shift_direction: str
          'right' / 'left' / any item of DIRECTIONS
          The direction of the new line relative to self.

        spacing: integer
          The spacing between self and the new shape.

        Returns:
        ---------------
        Shape
          New Line object
        """

        if self.direction in ["up", "down"]:
            start_column = (
                self.start_tile.column + spacing + 1
                if shift_direction == "right"
                else self.start_tile.column - spacing - 1
            )
            start_row = 1 if self.direction == "down" else -1
        else:
            all_tiles = Shape.get_entire_board().tiles
            if self.direction in ["up_right", "down_left"]:
                if shift_direction in ["up", "left", "up_left"]:
                    new_const_val = self.constant_value + spacing + 1
                else:
                    new_const_val = self.constant_value - spacing - 1
                all_tiles = Shape.get_entire_board().tiles
                new_line_tiles = list(
                    filter(lambda tile: tile._hexagon._s == new_const_val, all_tiles)
                )
                if self.direction == "up_right":
                    start_column = min([tile.column for tile in new_line_tiles])
                    start_row = max([tile.row for tile in new_line_tiles])
                else:
                    start_column = max([tile.column for tile in new_line_tiles])
                    start_row = min([tile.row for tile in new_line_tiles])
            else:
                if shift_direction in ["down", "left", "down_left"]:
                    new_const_val = self.constant_value + spacing + 1
                else:
                    new_const_val = self.constant_value - spacing - 1
                new_line_tiles = list(
                    filter(lambda tile: tile._hexagon._r == new_const_val, all_tiles)
                )
                if self.direction == "down_right":
                    start_column = min([tile.column for tile in new_line_tiles])
                    start_row = min([tile.row for tile in new_line_tiles])
                else:
                    start_column = max([tile.column for tile in new_line_tiles])
                    start_row = max([tile.row for tile in new_line_tiles])
            return Line(
                start_tile=Tile(start_row, start_column), direction=self.direction
            )

        if self.direction == "up_right":
            column = 1
            self_row = Line(
                start_tile=self.start_tile, direction="down_left"
            ).end_tile.row
            row = (
                self_row + spacing + 1
                if shift_direction in ["up", "left", "up_left"]
                else self_row - spacing - 1
            )
        if self.direction == "down_right":
            column = 1
            self_row = Line(
                start_tile=self.start_tile, direction="up_left"
            ).end_tile.row
            row = (
                self_row + spacing + 1
                if shift_direction in ["up", "right", "up_right"]
                else self_row - spacing - 1
            )
        if self.direction == "up_left":
            row = 1
            self_end = Line(start_tile=self.start_tile, direction="down_right").end_tile
            row = (
                self_row + spacing + 1
                if shift_direction in ["up", "left", "up_left"]
                else self_row - spacing - 1
            )

        return Line(start_tile=Tile(start_row, start_column), direction=self.direction)

    def draw(self, color):
        # self.color = color
        super().draw(color)
        return self


class Circle(Shape):
    """A class to represent a circle on the board. This is a Shape object with tiles that are along a circle

    Attributes:
    ---------------
      center_tile: Tile
        The center of the circle
      color: str
        The color of the circle
    """

    def __init__(self, center_tile, radius=1):
        """
        Parameters:
        ---------------
        center_tile: Tile
          The center of the circle
        radius: int
          The radius of the circle
        """

        g = center_tile.game
        rctile = center_tile._hexagon
        hexagons = []
        shifts = []
        for d0 in range(-radius, radius + 1):
            d1 = radius - d0 if d0 >= 0 else -radius - d0
            d2 = -d0 - d1
            d = [d0, d1, d2]
            for i in range(3):
                shift = _Vec(*[d[i % 3], d[(1 + i) % 3], d[(2 + i) % 3]])
                hexagons.append(rctile._shift(shift))
        super().__init__(hexagons, from_hexagons=True, game=g)
        self.center_tile = center_tile
        self.game = g
        # self.color = None

    def _show(self):
        logger.debug(
            "%s instance: linds=%s, size=%s, center=%s, color=%s",
            self.__class__.__name__,
            self._linds,
            self._size,
            self.center_tile.offset,
            self.color,
        )

    def draw(self, color):
        """Draw the circle in the given color.

        Parameters:
        ---------------
        color: str
          The color
        """

        # self.color = color
        super().draw(color)
        return self


class Triangle(Shape):
    """A class to represent a triangle on the board.
    This is a Shape object with tiles that are along a triangle.

    Attributes:
     ---------------
      point: str
      side_length: string
      color: string
    """

    def __init__(self, start_tile, point, start_tile_type, side_length=2):
        """
        Parameters:
        ---------------
        start_tile: Tile
          Specifies a vertex of the triangle, from which we start generating the triangle
        point: str
          'left' / 'right'
          The direction the triangle is pointing at.
        start_tile_type: str
          'side' / 'top' / 'bottom'
          A triangle has three vertices: side vertex, top vertex, and bottom vertex.
          'start_tile_type' specifies which vertex of the triangle is described by ‘start_tile’.
        side_length: int
          The length of the side of the triangle
        """

        if side_length < 2:
            raise Exception("side_length parameter cannot be smaller than 2")

        tiles = []
        d_directions = {
            "left": ["up_right", "down", "up_left"],
            "right": ["up_left", "down", "up_right"],
        }
        types = ["side", "top", "bottom"]
        tile = start_tile
        directions = _Vec.cyclic_permutation(
            d_directions[point], -types.index(start_tile_type)
        )
        for i_edge in range(3):
            for _ in range(side_length - 1):
                tiles.append(tile)
                tile = tile.neighbor(directions[i_edge])
        g = start_tile.game
        super().__init__(tiles, game=g)
        self.game = g
        self.point = point
        self.side_length = side_length
        # self.color = None

    def _show(self):
        logger.debug(
            "%s instance: linds=%s, size=%s, center=%s, color=%s",
            self.__class__.__name__,
            self._linds,
            self._size,
            self.center_tile.offset,
            self.color,
        )

    def draw(self, color):
        """Draw the triangle in the given color

        Parameters:
        ---------------
        color: str
          The color
        """

        # self.color = color
        super().draw(color)
        return self
