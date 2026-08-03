"""Flat, pure-function equivalent of the hexagen OOP API (Game/Shape/Tile/Line/Circle/Triangle).

Every function here takes and returns plain tuples — (row, col) for bare geometry, or
(row, col, color) for painted tiles — never a Game/Shape/Tile object, and never mutates any
persistent board. This matches the flat, tuple-returning contract used by python-full and by
REGAL's learned libraries, so it can serve as a hand-crafted "flat library" baseline for
comparison against a REGAL-learned flat library, holding the execution paradigm constant and
varying only "hand-crafted vs. learned".

Internally, each function builds a throwaway hexagen.Game() and calls the real, already-vetted
hexagen geometry engine (rotation, reflection, flood-fill inside/outside, polygon angle-sorting,
Line colinearity snapping, etc.) rather than re-deriving that math by hand — this guarantees the
flat functions behave identically to the real hexagen library, differing only in surface
(function calls on tuples, not chained methods on a mutated board).

Board is fixed at WIDTH x HEIGHT (1-indexed rows/cols), matching the hexagen defaults.
"""

import hexagen as _hx
from constants.constants import WIDTH, HEIGHT, COLORS, DIRECTIONS


def _game():
    g = _hx.Game(WIDTH, HEIGHT)
    g.__enter__()
    return g


def _mk_tiles(rc_list, game):
    return [_hx.Tile(r, c, game=game) for (r, c) in rc_list]


def _mk_shape(rc_list, game):
    tiles = _mk_tiles(rc_list, game)
    return _hx.Shape(tiles, game=game) if tiles else _hx.Shape([], game=game)


def _replay_paint(painted, game):
    """Paint (row, col, color) tuples onto a throwaway game so color-dependent queries
    (get(color), neighbors('white'), recolor) see the right current colors."""
    if not painted:
        return
    for r, c, color in painted:
        _hx.Tile(r, c, game=game).draw(color)


def _as_rc(shape):
    return [(t.row, t.column) for t in shape]


def _as_rcc(shape):
    return [(t.row, t.column, t.color) for t in shape]


# ── Board-level statics ──────────────────────────────────────────────────────


def get_entire_board():
    """All (row, col) tiles on the board."""
    g = _game()
    return _as_rc(_hx.Shape.get_entire_board(game=g))


def get_board_perimeter():
    """All (row, col) tiles on the board's outer perimeter."""
    g = _game()
    return _as_rc(_hx.Shape.get_board_perimeter(game=g))


def get_color(painted, color):
    """Filter `painted` ((row,col,color) tuples) to tiles of the given color.
    color='all' or 'any' returns every non-white tile."""
    g = _game()
    _replay_paint(painted, g)
    return _as_rc(_hx.Shape.get_color(color, game=g))


def get_column(column):
    """All (row, col) tiles in the given 1-indexed column."""
    g = _game()
    return _as_rc(_hx.Shape.get_column(column, game=g))


# ── Tile-level ────────────────────────────────────────────────────────────────


def on_board(row, col):
    return 1 <= row <= HEIGHT and 1 <= col <= WIDTH


def neighbor(tile, direction):
    """The single (row, col) neighbor of `tile` (a (row,col) pair) in a hex direction.
    direction must be one of DIRECTIONS (up/down/up_left/up_right/down_left/down_right) —
    'left'/'right' are NOT valid here (use neighbors(..., 'left'/'right') for those)."""
    g = _game()
    t = _hx.Tile(tile[0], tile[1], game=g)
    n = t.neighbor(direction)
    return (n.row, n.column)


def neighbors(tiles, criterion="all", painted=None):
    """Neighbors of a whole shape (list of (row,col) tuples).
    criterion: 'all' | 'right' | 'left' | 'above' | 'below' | 'outside' | 'inside' | 'white'
               | any item of DIRECTIONS."""
    g = _game()
    _replay_paint(painted, g)
    shape = _mk_shape(tiles, g)
    return _as_rc(shape.neighbors(criterion))


# ── Pure geometric queries on a given shape ──────────────────────────────────


def get(tiles, criterion, painted=None):
    """Tiles from `tiles` (list of (row,col)) related to the shape by `criterion`:
    'outside'/'inside' (relative to board bounds, only valid if the shape is closed/not open),
    'above'/'below', 'top'/'bottom', 'corners', 'endpoints', any DIRECTIONS item, or a color name
    (filters `tiles` to those currently painted that color — pass `painted`)."""
    g = _game()
    _replay_paint(painted, g)
    shape = _mk_shape(tiles, g)
    return _as_rc(shape.get(criterion))


def boundary(tiles, criterion="all"):
    """Boundary tiles of `tiles` (list of (row,col)). criterion: 'all' | 'outer' | 'inner'."""
    g = _game()
    shape = _mk_shape(tiles, g)
    return _as_rc(shape.boundary(criterion))


def edge(tiles, direction):
    """Extreme tiles of `tiles` along `direction`: 'left'/'right'/'up'/'top'/'down'/'bottom'
    or any DIRECTIONS item."""
    g = _game()
    shape = _mk_shape(tiles, g)
    return _as_rc(shape.edge(direction))


def extreme(tiles, direction):
    """The single-most extreme tile(s) of `tiles` in a hex direction (a DIRECTIONS item)."""
    g = _game()
    shape = _mk_shape(tiles, g)
    return _as_rc(shape.extreme(direction))


def is_empty(tiles):
    return len(tiles) == 0


def is_open(tiles):
    """True if `tiles` does not enclose any area (has no 'inside')."""
    g = _game()
    shape = _mk_shape(tiles, g)
    return shape.is_open()


def overlaps(tiles_a, tiles_b):
    return len(set(tiles_a) & set(tiles_b)) > 0


def intersection(tiles_a, tiles_b):
    return list(set(tiles_a) & set(tiles_b))


def union(tiles_a, tiles_b):
    return list(set(tiles_a) | set(tiles_b))


def difference(tiles_a, tiles_b):
    return list(set(tiles_a) - set(tiles_b))


def center(tiles):
    """(row, col) center-of-mass of `tiles`, rounded to the nearest tile."""
    g = _game()
    shape = _mk_shape(tiles, g)
    c = shape.center()
    return (c.row, c.column)


# ── Painting & transforms (operate on already-colored (row,col,color) tiles) ────


def draw(tiles, color):
    """Paint every (row, col) in `tiles` with `color`. Returns (row,col,color) tuples —
    accumulate these into your own running tiles list."""
    return [(r, c, color) for (r, c) in tiles]


def copy_paste(painted, shift_direction=None, spacing=0, reference_tiles=None,
                source=None, destination=None, shift=None):
    """Copy `painted` ((row,col,color) tuples) to a new location, preserving each tile's own
    color. Provide exactly one of: shift_direction (+ optional spacing/reference_tiles),
    or source+destination (copy so that `source` lands on `destination`)."""
    g = _game()
    _replay_paint(painted, g)
    shape = _mk_shape([(r, c) for (r, c, _col) in painted], g)
    ref_shape = None
    if reference_tiles is not None:
        ref_shape = _mk_shape(reference_tiles, g)
    src_tile = _hx.Tile(source[0], source[1], game=g) if source is not None else None
    dst_tile = _hx.Tile(destination[0], destination[1], game=g) if destination is not None else None
    new_shape = shape.copy_paste(
        shift_direction=shift_direction, spacing=spacing, reference_shape=ref_shape,
        source=src_tile, destination=dst_tile, shift=shift,
    )
    return _as_rcc(new_shape)


def grid(painted, shift_direction, spacing, num_copies=None):
    """Repeated copies of `painted` along `shift_direction`, spaced `spacing` apart.
    Returns the original tiles plus every copy, each preserving its own color.
    num_copies=None fills the board with as many complete copies as fit."""
    g = _game()
    _replay_paint(painted, g)
    shape = _mk_shape([(r, c) for (r, c, _col) in painted], g)
    new_shape = shape.grid(shift_direction, spacing, num_copies)
    return _as_rcc(new_shape)


def reflect(painted, column=None, axis_direction=None, tile_on_axis=None, axis_line=None):
    """Reflect `painted` ((row,col,color) tuples) through an axis, preserving colors.
    Specify exactly one axis: `column` (vertical line at that column), `axis_direction`
    ('horizontal' or a DIRECTIONS item, optionally with `tile_on_axis` to pin the line),
    or `axis_line` = (start_tile, direction) to reflect through a specific Line."""
    g = _game()
    _replay_paint(painted, g)
    shape = _mk_shape([(r, c) for (r, c, _col) in painted], g)
    axis_line_obj = None
    if axis_line is not None:
        start, direction = axis_line
        axis_line_obj = _hx.Line(start_tile=_hx.Tile(start[0], start[1], game=g), direction=direction)
    tile_on_axis_obj = _hx.Tile(tile_on_axis[0], tile_on_axis[1], game=g) if tile_on_axis is not None else None
    new_shape = shape.reflect(
        axis_line=axis_line_obj, column=column, axis_direction=axis_direction,
        tile_on_axis=tile_on_axis_obj,
    )
    return _as_rcc(new_shape)


def rotate(painted, center_tile, angle):
    """Rotate `painted` ((row,col,color) tuples) counterclockwise around `center_tile`
    (a (row,col) pair) by `angle` degrees (must be a multiple of 60), preserving colors."""
    g = _game()
    _replay_paint(painted, g)
    shape = _mk_shape([(r, c) for (r, c, _col) in painted], g)
    center = _hx.Tile(center_tile[0], center_tile[1], game=g)
    new_shape = shape.rotate(center, angle)
    return _as_rcc(new_shape)


def recolor(painted, color_map):
    """Remap colors in `painted` ((row,col,color) tuples) via color_map, e.g. {'red':'blue'}."""
    return [(r, c, color_map.get(color, color)) for (r, c, color) in painted]


# ── Shape factories (pure geometry, no color) ────────────────────────────────


def line(start, end=None, direction=None, length=None, end_tiles=None,
         include_start_tile=True, include_end_tile=True):
    """A straight line of (row,col) tiles from `start`. Either give `end` (must be hex-colinear
    with start — raises if not) or `direction` (+ optional `length`, else extends to the board
    edge). `end_tiles`: optional list of (row,col) tiles to stop at."""
    g = _game()
    start_tile = _hx.Tile(start[0], start[1], game=g)
    end_tile = _hx.Tile(end[0], end[1], game=g) if end is not None else None
    end_tiles_shape = _mk_shape(end_tiles, g) if end_tiles else None
    ln = _hx.Line(
        start_tile=start_tile, end_tile=end_tile, direction=direction, length=length,
        end_tiles=end_tiles_shape, include_start_tile=include_start_tile,
        include_end_tile=include_end_tile,
    )
    return _as_rc(ln)


def parallel_line(start, direction, shift_direction, spacing):
    """A new line parallel to the line starting at `start` going `direction`, shifted
    `shift_direction` with `spacing` tiles between them. Stretches to fill the board."""
    g = _game()
    start_tile = _hx.Tile(start[0], start[1], game=g)
    ln = _hx.Line(start_tile=start_tile, direction=direction)
    new_ln = ln.parallel(shift_direction, spacing)
    return _as_rc(new_ln)


def circle(center_tile, radius=1):
    """A hollow ring of (row,col) tiles at exactly `radius` from `center_tile` (a (row,col)
    pair) — does not include the center or inner rings."""
    g = _game()
    center = _hx.Tile(center_tile[0], center_tile[1], game=g)
    c = _hx.Circle(center, radius)
    return _as_rc(c)


def triangle(start, point, start_tile_type, side_length=2):
    """A hollow triangle (only its 3 sides, no interior) of (row,col) tiles.
    start: (row,col) of one vertex. point: 'left' | 'right' (which way the triangle points).
    start_tile_type: 'side' | 'top' | 'bottom' (which vertex `start` is). side_length >= 2."""
    g = _game()
    start_tile = _hx.Tile(start[0], start[1], game=g)
    tri = _hx.Triangle(start_tile, point, start_tile_type, side_length)
    return _as_rc(tri)


def polygon(vertices):
    """A closed polygon outline (row,col) tiles connecting `vertices` (list of (row,col)
    tuples) in order around their centroid. Consecutive vertices must be hex-colinear
    (share a q, r, or s cube coordinate) — draw separate lines for non-colinear edges."""
    g = _game()
    verts = _mk_tiles(vertices, g)
    poly = _hx.Shape.polygon(verts)
    return _as_rc(poly)
