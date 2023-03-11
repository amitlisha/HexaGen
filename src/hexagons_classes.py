'''Hexagons Classes

This module contains tools for drawing on a hexagons board.
The purpose of these tools is to translate drawing instructions given in natural language
into code.

Contains 7 classes:
- HexagonsGame - manages the board
- _Vec (for internal use only)
- _Hexagon (for internal use only)
- Shape - manages shapes (any set of tiles) on the board
- Tile(Shape) - a single tile on the board
- Line(Shape) - a line on the board
- Circle(Shape) - a circle on the board
- Triangle(Shape) - a triangle on the board

'''

import numpy as np
from scipy.spatial.transform import Rotation
import sys
from typing import Callable, Optional, List # Union
sys.path.append('../utils')
import plot_board as pb

class HexagonsGame:
  '''Class HexagonsGame manages the board: reset the board, hold the board parameters and constants,
  hold the board state, keep track of drawing steps
  '''

  _COLORS_LIST = ['white', 'black', 'yellow', 'green', 'red', 'blue', 'purple', 'orange']

  def start(width = 18, height = 10):
    HexagonsGame._W = width
    HexagonsGame._H = height
    HexagonsGame.board_state = [0] * width * height
    HexagonsGame._step = None
    HexagonsGame._drawn_hexagons = {'all': []}

  # TODO: write unit_test
  def record_step(step):
    '''After calling this method with some name for the step, all the tiles that are drawn
    will be saved in a list under the step's name. The list can later be retrieved using
    the method 'get_record'

    Parameters:
    ---------------
    step:
      The name of the step, should be a string or an integer
    '''

    HexagonsGame._drawn_hexagons[step] = []
    HexagonsGame._step = step

  # TODO: write unit_test
  def get_record(steps):
    '''Retrieving a shape consisting of the tiles drawn in previous step/steps

    Parameters:
    ---------------
    direction: str or List[str]
      The step(s) to retrieve

    Returns:
    ---------------
    Shape
      New Shape object
    '''

    if isinstance(steps, list):
      drawn_hexagons = []
      for step in steps:
        drawn_hexagons += HexagonsGame._drawn_hexagons[step]
      return Shape(drawn_hexagons, from_hexagons=True)
    else:
      return Shape(HexagonsGame._drawn_hexagons[steps], from_hexagons=True)

  def plot(gold_board = None, file_name = None):
    '''Plot the current state of the board'''

    if gold_board is None:
      pb.plot_boards(HexagonsGame.board_state, fig_size=[7, 5], titles = [''], file_name = file_name)
    else:
      diff = list(map(lambda x, y: 0 if x == y else 1, gold_board, HexagonsGame.board_state))
      pb.plot_boards([gold_board, HexagonsGame.board_state, diff], titles = ['gold', 'code generated', 'difference'], file_name = file_name)

class _Vec:
  '''Class _Vec represents a vector on an infinite hexagonally tiled plane.
  It doesn't symbol a specific location on the board, but rather the difference
  between two location.
  It is for internal use only.
  '''

  DIRECTIONS = {'up': (0, -1, 1), 'down': (0, 1, -1), 'down_right': (1, 0, -1), 'up_left': (-1, 0, 1),
                'down_left': (-1, 1, 0), 'up_right': (1, -1, 0)}
  DIRECTIONS_TO_QRS = {'up': 0, 'down': 0, 'down_right': 1, 'up_left': 1, 'down_left': 2, 'up_right': 2}

  def __init__(self, *args):
    if isinstance(args[0], str):
      # _Vec is given as a direction name, e.g. 'up_right'
      q, r, s = _Vec.DIRECTIONS[args[0]]
    elif len(args) == 3:
      # _Vec is given as cube [q, r, s]
      q, r, s = args
    elif len(args) == 2:
      # _Vec is given as offset [column_diff, row_diff]
      column_diff, row_diff = args
      assert column_diff % 2 == 0, 'column_diff must be even, otherwise this is ambiguous'
      q = column_diff
      r = row_diff - (q - (q % 2)) // 2
      s = -q - r
    if abs(q + r + s) > 0.00001:
      raise Exception(f'cube coordinates {[q, r, s]} don\'t sum up to 0')
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
    print(f'{self.__class__.__name__} instance: cube = {self._cube}')

  def _has_direction(self):
    # q*r*s=0 means that vec is proportional to one of the six direction vecs
    return not bool(self._q * self._r * self._s)

  def _normalize(self):
    if self._has_direction():
      norm = self._norm()
      direction_cube = [x // norm for x in self._cube]
      return _Vec(*direction_cube)
    print(f'vec {self._cube} is not a direction vector')

  def _direction_str(self):
    # returns a string describing the direction of the vector
    if self._has_direction():
      return list(_Vec.DIRECTIONS.keys())[list(_Vec.DIRECTIONS.values()).index(self._normalize()._cube)]
    print(f'vec {self._cube} is not a direction vector')

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
    int_cube[ind] = - (np.sum(int_cube)) + int_cube[ind]
    int_cube = [int(_) for _ in int_cube]
    return _Vec(*int_cube)

class _Hexagon:
  '''Class _Hexagon represents a location on the board / in the plane.
  It is for internal use only.
  '''

  def complete_arguments(column, row, cube):
    '''An hexagon can be defined be two different sets of coordinates:
    offset (column, row) and cube (q, r, s).
    This method completes missing coordinates'''
    if (column is not None) and (row is not None):
      # _Hexagon is given as offset = [column, row]
      # compute cube coordinates. offset [1, 1] is cube [0, 0, 0]
      q = column - 1
      r = row - 1 - (q - (q % 2)) // 2
      s = -q - r
    elif cube is not None:
      # _Hexagon is given as cube = [q, r, s]
      q, r, s = cube
      if q + r + s != 0:
        raise Exception(f'cube coordinates {[q, r, s]} don\'t sum up to 0')
      column = q + 1
      row = r + (q - (q % 2)) // 2 + 1
    if 1 <= column <= HexagonsGame._W and 1 <= row <= HexagonsGame._H:
      lind = int((row - 1) * HexagonsGame._W + (column - 1))
    else:
      # tile is not on board, so it has no linear index
      lind = None
    return lind, (column, row), (q, r, s)

  def __init__(self, column = None, row = None, cube = None):
    self._lind, self._offset, self._cube = _Hexagon.complete_arguments(column, row, cube)
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
      return HexagonsGame.board_state[self._lind]

  @property
  def _color(self):
      return HexagonsGame._COLORS_LIST[self._color_id]

  @property
  def _column(self):
    return self._offset[0]

  @property
  def _row(self):
    return self._offset[1]

  def _show(self):
    print(f'{self.__class__.__name__} instance: column = {self._column}, row = {self._row}, lind = {self._lind}, color = {self._color_id}')

  def _from_lind(lind):
    '''Returns a hexagon by its linear index on the board'''

    if lind in range(HexagonsGame._W * HexagonsGame._H):
      row = lind // (HexagonsGame._W) + 1
      column = lind % HexagonsGame._W + 1
      return _Hexagon(column = column, row = row)
    print(f'lind {lind} not valid')

  def _on_board(self):
    '''Returns True iff self lies on the board'''

    return self._lind is not None

  def __sub__(self, other):
    '''Compute the difference between self and other
    The difference is a _Vec object'''

    return _Vec(*[int(_) for _ in [x - y for x, y in zip(self._cube, other._cube)]])

  def _shift(self, *args):
    '''Compute a new hexagon by shifting self to another location'''

    if isinstance(args[0], _Vec):
      vec = args[0]
    else:
      vec = _Vec(*args)
    new_cube = [int(_) for _ in [x + y for x, y in zip(self._cube, vec._cube)]]
    return _Hexagon(cube = new_cube)

  def _copy_paste(self, vec, color = None):
    '''Copy self to another location
    Compute the new location and draw there'''

    new_tile = self._shift(vec)
    new_tile._draw(self._color_id if color is None else color)
    return new_tile

  def _reflect(self, axis_line = None, column = None, axis_direction = None, hexagon_on_axis = None):
    '''Reflect self
    Compute the new location and draw there'''

    if axis_direction == 'horizontal':
      direction_vec = _Vec(2, -1, -1)
    else:
      if axis_line is not None:
        direction_vec = axis_line._direction_vec
        hexagon_on_axis = axis_line[0]._hexagon
      else:
        if axis_direction == 'vertical' or column is not None:
          axis_direction = 'up'
        direction_vec = _Vec(axis_direction)

    v_direction_reciprocal = np.array([direction_vec._r - direction_vec._s, direction_vec._s - direction_vec._q, direction_vec._q - direction_vec._r])
    v_direction_reciprocal = v_direction_reciprocal / np.linalg.norm(v_direction_reciprocal)
    if column is not None:
      # we assume if axis_value is given it represents a column number
      column = column % (HexagonsGame._W + 1)
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

  def _rotate(self, rotation, center):
    '''Rotate self
    Compute the new location and draw there'''

    v_self = np.array(self._cube)
    v_center = np.array(center._cube)
    rotvec = np.ones(3) / np.sqrt(3) * (rotation * np.pi / 3)
    R = Rotation.from_rotvec(rotvec).as_matrix()
    v_new = np.matmul(v_self - v_center, R) + v_center
    new_tile_vec = _Vec(*list(v_new))._round()
    new_tile = _Hexagon(cube = new_tile_vec._cube)
    new_tile._draw(self._color)
    return new_tile

  def _draw(self, color):
    '''Paint self with the given color'''

    color_id = HexagonsGame._COLORS_LIST.index(color) if isinstance(color, str) else color
    if self._lind is not None:
      HexagonsGame.board_state[self._lind] = color_id
    else:
      self._saved_color_id = color_id
    HexagonsGame._drawn_hexagons['all'].append(self)
    if HexagonsGame._step is not None:
      HexagonsGame._drawn_hexagons[HexagonsGame._step].append(self)
    return self

  def _neighbor(self, direction):
    '''Return the neighbor of self in the given direction'''

    if not isinstance(direction, _Vec):
      vec = _Vec(direction)
    return self._shift(vec)

  def _neighbors(self, criterion = 'all'):
    '''Return all the neighbors of self'''

    if self._lind is None:
      return []
    return [self._shift(_Vec(*direction_cube)) for direction_cube in _Vec.DIRECTIONS.values()]

class Shape:
  '''Class Shape represents any set of tiles on the board,
  including an empty set and a single tile'''

  def __init__(self, tiles, from_linds=False, from_hexagons=False):
    '''
    Construct a new Shape from a list of tiles.

    Parameters:
    -----------
    tiles: list[Tile]
      The tiles that compose the shape
    '''

    if from_linds:
      linds = tiles
      hexagons = [_Hexagon._from_lind(lind) for lind in linds]
    else:
      if from_hexagons:
        hexagons = tiles
      elif isinstance(tiles, Shape):
        hexagons = tiles._hexagons
      else:
        hexagons = [tile._hexagon for tile in tiles]
    unique_hexagons = []
    unique_cubes = []
    for hexagon in hexagons:
      if hexagon._cube not in unique_cubes:
        unique_cubes.append(hexagon._cube)
        unique_hexagons.append(hexagon)
    self._hexagons = tuple(unique_hexagons)
    if len(unique_hexagons) == 1:
      self.__class__ = Tile

  @property
  def _size(self):
    return len(self._hexagons)

  @property
  def _linds(self):
    return [hexagon._lind for hexagon in self._hexagons]

  @property
  def tiles(self):
    return [Tile(hexagon._column, hexagon._row) for hexagon in self._hexagons]

  @property
  def colors(self):
    return [hexagon._color for hexagon in self._hexagons]

  @property
  def columns(self):
    '''The list of columns of the tiles in the shape'''

    return [hexagon._column for hexagon in self._hexagons]

  @property
  def rows(self):
    '''The list of rows of the tiles in the shape'''

    return [hexagon.row for hexagon in self._hexagons]

  @property
  def _cubes(self):
    '''The list of cube coordinates of the tiles in the shape'''

    return [hexagon._cube for hexagon in self._hexagons]

  @property
  def _qs(self):
    '''The list of q-coordinates of the tiles in the shape'''
    return [hexagon._q for hexagon in self._hexagons]

  @property
  def _rs(self):
    '''The list of r-coordinates of the tiles in the shape'''
    return [hexagon._r for hexagon in self._hexagons]

  @property
  def _ss(self):
    '''The list of s-coordinates of the tiles in the shape'''
    return [hexagon._s for hexagon in self._hexagons]

  def _show(self):
    print(f'{self.__class__.__name__} instance: size = {self._size}, linds = {self._linds}')

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
    '''Use the '+' sign to compute the union of two shapes'''

    cubes = list(set(self._cubes) | set(other._cubes))
    hexs = [_Hexagon(cube = cube) for cube in cubes]
    return Shape(hexs, from_hexagons = True)

  def __mul__(self, other):
    '''Use the '*' sign to compute the intersection of two shapes'''

    cubes = list(set(self._cubes) & set(other._cubes))
    hexs = [_Hexagon(cube = cube) for cube in cubes]
    return Shape(hexs, from_hexagons = True)

  def __sub__(self, other):
    '''Use the '-' sign to compute the difference between two shapes'''

    cubes = list(set(self._cubes).difference(set(other._cubes)))
    hexs = [_Hexagon(cube = cube) for cube in cubes]
    return Shape(hexs, from_hexagons = True)

  def _compute_shift_from_spacing(self, direction, spacing, reference_shape=None):
    '''Compute how much to shift a shape, to create a copy with a desired spacing from self
    for internal use only'''

    if reference_shape is None:
      reference_shape = self
    vec_diff = reference_shape._center_of_mass() - self._center_of_mass()
    initial_shift = vec_diff._round()
    if direction == 'left':
      shift = _Vec(-2, 0)
      spacing -= spacing % 2
    elif direction == 'right':
      shift = _Vec(2, 0)
      spacing -= spacing % 2
    else:
      shift = _Vec(direction)
    step_size = shift._norm()
    new_shape = self._shift(initial_shift)
    steps = 0
    count_space = 0
    while new_shape.overlaps(reference_shape) or count_space < spacing:
      if not new_shape.overlaps(reference_shape):
        count_space += step_size
      new_shape = new_shape._shift(shift)
      steps += 1
    total_shift = shift._scale(steps) + initial_shift
    return total_shift

  def _center_of_mass(self):
    cubes_arr = np.array([hexagon._cube for hexagon in self._hexagons])
    return _Vec(*np.mean(cubes_arr, axis=0))

  def _entirely_on_board(self):
    return None not in self._linds

  def is_empty(self):
    '''
    Return True iff self is empty

    Returns:
    --------
    bool
      True of self is empty, False otherwise
    '''

    return self._size == 0

  def overlaps(self, S):
    return not (self * S).is_empty()

  def _reduce_to_board(self):
    return Shape([tile for tile in self if tile.on_board()])

  def draw(self, color):
    '''
    Draw the tiles of self in the given color

    Parameters:
    -----------
    color: str
      The color
    '''

    for hexagon in self._hexagons:
      hexagon._draw(color)

  def copy_paste(self, shift_direction=None, spacing=None, reference_shape=None, shift=None):
    '''
    Draw a copy of self in a new location

    Parameters:
    -----------
    shift_direction: str
      The direction in which to shift the shape
      Supported values:
      - any item of DIRECTIONS
      - 'right'
      - 'left'
    spacing: int
      Number of tiles between the original shape and the new shape
    reference_shape: Shape
      The new location is computed with respect to reference_shape.
      If not specified, location is computed with respect to the original shape.

    Returns:
    --------
    Shape
      New Shape object
    '''

    if shift is None:
      shift = self._compute_shift_from_spacing(shift_direction, spacing, reference_shape)

    new_hexagons = []
    for hexagon in self._hexagons:
      hexagon._copy_paste(shift)
      new_hexagons.append(hexagon._shift(shift))
    new_shape = Shape(new_hexagons, from_hexagons=True)
    return new_shape

  def grid(self, shift_direction, spacing, num_copies = None):
    '''
    Draw copies of self along a grid.
    This is done by repeated calls to 'copy_paste'.

    Parameters:
    -----------
    shift_direction: str
      The direction in which to shift the shape
    spacing: int
      Number of tiles between the original shape and the new shape
    num_copies: int
      The number of copies.
      If not specified, copies will be created until there is no more room
      on the board

    Returns:
    --------
    Shape
      New Shape object that holds the original shape and all its copies
    '''

    shift = self._compute_shift_from_spacing(shift_direction, spacing, None)

    grid = self
    k = 0
    new_shape = self._shift(shift)
    while (num_copies is None and new_shape._entirely_on_board()) or (num_copies is not None and k < num_copies):
      grid = grid + new_shape
      new_shape = new_shape._shift(shift)
      k += 1
    return grid

  def reflect(self, axis_line=None, column=None, axis_direction=None, tile_on_axis=None):
    '''
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
    '''

    new_hexagons = []
    hexagon_on_axis = None if tile_on_axis is None else tile_on_axis._hexagon
    for hexagon in self._hexagons:
      new_hexagons.append(hexagon._reflect(axis_line=axis_line, column=column, axis_direction=axis_direction,
                                           hexagon_on_axis=hexagon_on_axis))
    new_shape = Shape(new_hexagons, from_hexagons=True)
    return new_shape

  def rotate(self, rotation, center_tile):
    '''
    Draw a rotation of self

    Parameters:
    -----------
    rotation: int
      Sets the angle of rotation
      1 - rotate 60 degrees counterclockwise
      2 - rotate 120 degrees counterclockwise
      etc.
    center_tile: Tile
      The tile around which to rotate

    Returns:
    --------
    Shape
      New Shape object that holds the original shape and all its copies
    '''

    new_hexagons = []
    for hexagon in self._hexagons:
      new_hexagons.append(hexagon._rotate(rotation=rotation, center=center_tile._hexagon))
    new_shape = Shape(new_hexagons, from_hexagons=True)
    return new_shape

  def recolor(self, color_map):
    '''
    re-color each tile in the shape
    color_map describes a mapping from colors to colors, e.g. {'red': 'blue', 'green': 'black'}
    '''
    for hexagon in self._hexagons:
      if hexagon._on_board():
        hexagon._draw(color_map[hexagon._color])
    return self

  def _shift(self, V):
    '''Shift self in some direction
    For internal use only'''

    return Shape([hexagon._shift(V) for hexagon in self._hexagons], from_hexagons=True)

  def get_entire_board():
    '''Return a Shape object containing all the tiles on the board'''

    tiles = []
    for row in range(1, HexagonsGame._H + 1):
      for column in range(1, HexagonsGame._W + 1):
        tiles.append(Tile(column, row))
    return Shape(tiles)

  def get_board_perimeter():
    '''Return a Shape object containing all the tiles on the board's perimeter'''

    B = Shape.get_entire_board()
    def tile_on_perimeter(tile):
      return tile.column in [1, HexagonsGame._W] or tile.row in [1, HexagonsGame._H]
    return Shape([tile for tile in B if tile_on_perimeter(tile)])

  def get_color(color):
    # TODO: write unit_test
    '''Return a Shape object containing all the tiles painted in the given color
    If color is 'any' is will return all the tiles that are not white'''

    if color == 'all':
      return Shape([tile for tile in Shape.get_entire_board().tiles if tile.color != 'white'])
    return Shape([tile for tile in Shape.get_entire_board().tiles if tile.color == color])

  # TODO: write unit_test
  def get_column(column):
    '''Return a Shape object containing all the tiles in the given column'''

    return Shape([Tile(column, row) for row in range(1, HexagonsGame._H + 1)])

  def get(self, criterion):
    '''
    Return a new shape according to some geometrical relation with self, described by ‘criterion’
    Options:
    - 'outside' / 'inside': the tiles outside/inside self
    - 'above' / 'below': tiles that lie above/below self
    - 'top' / 'bottom': to topmost/bottommost tiles of self
    - 'corners': the corners of self. If the shape is a polygon, these will be the polygon’s vertices
    - 'end_points': the end points of self. If the shape is a line, these will be the ends of the line
    '''

    if criterion == 'outside':
      S_ext = Shape.get_board_perimeter() - self
      while True:
        S_ext_neighbors_not_in_self = (S_ext.neighbors('all') - self) * Shape.get_entire_board()
        # stop if S_ext didn't grow in the last iteration
        if S_ext_neighbors_not_in_self._size == 0:
          break
        else:
          S_ext += S_ext_neighbors_not_in_self
      return S_ext

    if criterion == 'inside':
      return (Shape.get_entire_board() - self) - self.get('outside')

    if criterion in ['above', 'below']:
      S = Shape([])
      for column in np.unique(self.columns):
        if criterion == 'above':
          row = min([tile.row for tile in self if tile.column == column])
          S += Shape([tile for tile in Shape.get_entire_board() if tile.column == column and tile.row < row])
        elif criterion == 'below':
          row = max([tile.row for tile in self if tile.column == column])
          S += Shape([tile for tile in Shape.get_entire_board() if tile.column == column and tile.row > row])
      return S

    if criterion == 'top':
      return self._max('up')

    if criterion == 'bottom':
      return self._max('down')

    if criterion == 'corners':
      ext = self.boundary('outer')
      corners = []
      for hexagon in ext._hexagons:
        neighbors = (Shape(hexagon._neighbors(), from_hexagons = True) * ext)._hexagons
        if len(neighbors) == 2:
          v0 = hexagon - neighbors[0]
          v1 = hexagon - neighbors[1]
          if (v0 + v1)._norm() > 0.0001:
            corners.append(hexagon)
      return Shape(corners, from_hexagons=True)

    if criterion == 'end_points':
      ext = self.boundary('outer')
      ends = []
      for hexagon in ext._hexagons:
        neighbors = (Shape(hexagon._neighbors(), from_hexagons = True) * ext)._hexagons
        if len(neighbors) == 1:
          ends.append(hexagon)
      return Shape(ends, from_hexagons=True)

  def boundary(self, criterion='all'):
    if criterion == 'outer':
      return self.get('outside').neighbors('all') * self

    if criterion == 'inner':
      return self.get('inside').neighbors('all') * self

    return self.boundary('outer') + self.boundary('inner')

  def _max(self, direction):
    '''Returns a Shape object containing the tiles of the shape which are maximal in the given direction
    For internal use only'''

    direction_cube = _Vec.DIRECTIONS[direction]
    direction_ind = direction_cube.index(0)
    next_ind = (direction_ind + 1) % 3
    next_grows = (direction_cube[next_ind] == 1)
    shape_lines = [cube[direction_ind] for cube in self._cubes]
    hexagons = []
    for val in np.unique(shape_lines):
      hexagons_with_val = [hexagon for hexagon in self._hexagons if hexagon._cube[direction_ind] == val]
      if next_grows:
        hexagons.append(hexagons_with_val[np.argmax([_._cube[next_ind] for _ in hexagons_with_val])])
      else:
        hexagons.append(hexagons_with_val[np.argmin([_._cube[next_ind] for _ in hexagons_with_val])])
    return Shape(hexagons, from_hexagons=True)

  def extreme(self, direction):
    '''Returns a Shape object containing the extreme tiles of self in the given direction'''

    def height(cube, dcube):
      return cube[0] * dcube[0] + cube[1] * dcube[1] + cube[2] * dcube[2]

    direction_cube = _Vec.DIRECTIONS[direction]
    hexagons = self._max(direction)._hexagons
    heights = [height(hexagon._cube, direction_cube) for hexagon in hexagons]
    vhexagons = []
    for i in range(len(heights)):
      if (i == 0 or heights[i] > heights[i - 1]) and (i == len(heights) - 1 or heights[i] > heights[i + 1]):
        vhexagons.append(hexagons[i])
    return Shape(vhexagons, from_hexagons=True)

  def edge(self, criterion):
    '''Return the edge tiles of self according to some criterion'''

    if criterion in ['up', 'top']:
      return self._max('up')
    if criterion in ['down', 'bottom']:
      return self._max('down')

    if criterion in ['right', 'left']:
      shape_lines = self._qs
    elif criterion in ['down_left', 'up_right']:
      shape_lines = self._rs
    elif criterion in ['up_left', 'down_right']:
      shape_lines = self._ss

    if criterion in ['down_left', 'up_left', 'right']:
      extreme_line = np.amax(shape_lines)
    else:
      extreme_line = np.amin(shape_lines)

    return Shape([tile for tile, line in zip(self.tiles, shape_lines) if line == extreme_line])

  def neighbors(self, criterion='all'):
    '''Return a Shape object containing the neighbors of self, or a subset of them,
    accortidng to some criterion.

    Options:
    - ‘all’: all the neighbors of the shape
    - ‘right’ / ‘left’: neighbors to the right/left of the shape
    - ‘above’ / ‘below’: neighbors from above/below the shape
    - ‘outside’ / ‘inside’: neighbors outside/inside the shape
    - ‘white’: blank neighbors
    '''

    if criterion == 'all':
      return Shape([neighbor_hexagon for hexagon in self._hexagons for neighbor_hexagon in hexagon._neighbors()],
                   from_hexagons=True) - self
    if criterion in ['right', 'left']:
      edge = self.edge(criterion)
      down = Shape([_.neighbor('down_' + criterion) for _ in edge])
      up = Shape([_.neighbor('up_' + criterion) for _ in edge])
      return down * up
    if criterion in ['above', 'up']:
      return self.get('above') * self.neighbors()
    if criterion in ['below', 'down']:
      return self.get('below') * self.neighbors()
    if criterion == 'outside':
      return self.neighbors('all') * self.get('outside')
    if criterion == 'inside':
      return self.neighbors('all') * self.get('inside')
    if criterion == 'white':
      return Shape([tile for tile in Shape.get_entire_board() if tile.color == 'white']) * self.neighbors()
    if criterion in _Vec.DIRECTIONS:
      return Shape([tile.neighbor(criterion) for tile in self.tiles]) - self

  def neighbor(self, direction):
    '''Return self's neighbor(s) in a given direction'''

    return Shape([tile.neighbor(direction) for tile in self.tiles]) - self

  def polygon(vertices, *args):
    '''Return a polygon with the given vertices'''

    if isinstance(vertices, Shape):
      tiles = vertices.tiles
    elif isinstance(vertices, List):
      tiles = vertices
    else:
      tiles = [vertices] + args
    com = Shape(tiles)._center_of_mass()
    hexagons = Shape(tiles)._hexagons

    def angle(self, other):
      self_reciprocal = _Vec(*[self._r - self._s, self._s - self._q, self._q - self._r])
      v_self = np.array(self._cube)
      v_self_reciprocal = np.array(self_reciprocal._cube)
      v_other = np.array(other._cube)
      # print(n_self.dot(n_other)) / np.linalg.norm(self_reciprocal._cube)
      # print(n_self.dot(n_other))
      product = v_self.dot(v_other) / np.linalg.norm(v_self) / np.linalg.norm(v_other)
      product = min(product, 1.)
      product = max(product, -1.)
      angle = np.arccos(product)
      if v_self_reciprocal.dot(v_other) < 0:
        angle = 2 * np.pi - angle
      return angle

    vecs = [_Vec(*hexagon._cube) - com for hexagon in hexagons]
    angles = [angle(vecs[0], _) for _ in vecs]
    sorted_tiles = [tile for angle, tile in sorted(zip(angles, tiles))]
    polygon = Shape([])
    for i in range(len(sorted_tiles)):
      polygon += Line(start_tile=sorted_tiles[i], end_tile=sorted_tiles[(i + 1) % len(sorted_tiles)])

    return polygon

  def center(self):
    '''Rturns the center of mass of self.
    If the center of mass is not an exact tile location, it will round it to be a tile location'''

    hexagon_mean = _Hexagon(cube=self._center_of_mass()._round()._cube)
    return Tile(*hexagon_mean._offset)

class Tile(Shape):
  '''
  A Class to represent a tile on the board

  Attributes:
  -----------
  column: int
    The column on which the tile is located. starts at 1 and counted from left to right
  row: int
    The row on which this tile is located. starts from 1 and counted from top to bottom
  color: str
    The color of the tile
  '''

  def __init__(self, column, row):
    '''
    Construct a new tile. The default color is ‘white’.

    Parameters:
    -----------
    column: int
      The column on which the tile is located. Starts at 1 and counted from left to right.
      A negative value represents counting from right to left. E.g., the first column from the right is -1.
    row: int
      The row on which this tile is located. Starts from 1 and counted from top to bottom.
      A negative value represents counting from bottom to top. E.g., the first row from the bottom is -1.
    '''
    column = column % (HexagonsGame._W + 1)
    row = row % (HexagonsGame._H + 1)
    self._hexagons = [_Hexagon(column = column, row = row, cube = None)]

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
    print(f'{self.__class__.__name__} instance: column = {self.column}, row = {self.row}, lind = {self._lind}, color = {self.color}')

  def _to_tile(_hexagon):
    return Shape([_hexagon], from_hexagons = True)

  def on_board(self):
    return self._lind is not None

  def neighbor(self, direction):
    '''
    Return the neighbor of self in the given direction.

    Parameters:
    -----------
    direction: str
      Must be an item of DIRECTIONS

    Returns:
    --------
    Tile
      new Tile object
    '''

    return Tile._to_tile(self._hexagon._neighbor(direction))

class Line(Shape):
  '''A class to represent a straight line on the board.

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
  '''

  def __init__(self, start_tile: Tile, end_tile: Optional[Tile] = None, direction: str = None, length: int = None,
              end_tiles: Shape = Shape([]), include_start_tile: bool = True, include_end_tile: bool = True):
    '''
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
    include_end: bool
      If false, do not include the tile 'end_tile' in the line
    end_tiles: Shape
      Continue the line until you reach a tile that belong to the shape
    '''

    shexagon = start_tile._hexagon
    if length is None:
      length = max(HexagonsGame._H, HexagonsGame._W)
    if end_tile is not None:
      ehexagon = end_tile._hexagon
      v = ehexagon - shexagon
      direction_vec = v._normalize()
      distance = v._norm()
      length = distance - 1 + 1 * include_start_tile + 1 * include_end_tile
    else:
      direction_vec = _Vec(direction)
    if not include_start_tile:
      shexagon = shexagon._shift(direction_vec)
    count = 0
    hexagons = []
    hexagon = shexagon
    while count < length and hexagon._on_board() and hexagon._cube not in end_tiles._cubes:
        hexagons.append(hexagon)
        hexagon = hexagon._shift(direction_vec)
        count += 1
    super().__init__(hexagons, from_hexagons = True)
    self.length = len(hexagons)
    self.color = None
    self._direction_vec = direction_vec
    self.direction = direction_vec._direction_str()
    if len(hexagons) > 1:
      self.start_tile = Tile._to_tile(hexagons[0])
      self.end_tile = Tile._to_tile(hexagons[-1])
      qrs_ind = direction_vec._cube.index(0)
      self.constant_value = hexagons[0]._cube[qrs_ind]

  def _show(self):
    print(f'{self.__class__.__name__} instance: linds = {self._linds}, size = {self._size}, direction = {self.direction}, \
    start = {self.tiles[0].offset}, end = {self.tiles[-1].offset}, color = {self.color}')

  # TODO: write unit_test
  def parallel(self, direction, spacing=0):
    '''Create a new line parallel to self, in the given direction, with the given spacing from self
    This is different from Shape.copy_paste() because it doesn't copy the line, but rather creates a new line,
    which can be of different length from self.
    The new line will stretch as far as possible in both directions.

    Parameters:
    ---------------
    direction: str
      'right' / 'left' / any item of DIRECTIONS
      The direction in which you move from self to the new line

    Returns:
    ---------------
    Shape
      New Line object
    '''

    if self.direction in ['up', 'down']:
      start_column = self.start_tile.column + spacing + 1 if direction == 'right' else \
        self.start_tile.column - spacing - 1
      start_row = 1 if self.direction == 'down' else -1
    else:
      all_tiles = Shape.get_entire_board().tiles
      if self.direction in ['up_right', 'down_left']:
        if direction in ['up', 'left', 'up_left']:
          new_const_val = self.constant_value + spacing + 1
        else:
          new_const_val = self.constant_value - spacing - 1
        all_tiles = Shape.get_entire_board().tiles
        new_line_tiles = list(filter(lambda tile: tile._hexagon._s == new_const_val, all_tiles))
        if self.direction == 'up_right':
          start_column = min([tile.column for tile in new_line_tiles])
          start_row = max([tile.row for tile in new_line_tiles])
        else:
          start_column = max([tile.column for tile in new_line_tiles])
          start_row = min([tile.row for tile in new_line_tiles])
      else:
        if direction in ['down', 'left', 'down_left']:
          new_const_val = self.constant_value + spacing + 1
        else:
          new_const_val = self.constant_value - spacing - 1
        new_line_tiles = list(filter(lambda tile: tile._hexagon._r == new_const_val, all_tiles))
        if self.direction == 'down_right':
          start_column = min([tile.column for tile in new_line_tiles])
          start_row = min([tile.row for tile in new_line_tiles])
        else:
          start_column = max([tile.column for tile in new_line_tiles])
          start_row = max([tile.row for tile in new_line_tiles])
      return Line(start_tile = Tile(start_column, start_row), direction = self.direction)

    if self.direction == 'up_right':
      column = 1
      self_row = Line(start_tile = self.start_tile, direction = 'down_left').end_tile.row
      row = self_row + spacing + 1 if direction in ['up', 'left', 'up_left'] else \
        self_row - spacing - 1
    if self.direction == 'down_right':
      column = 1
      self_row = Line(start_tile = self.start_tile, direction = 'up_left').end_tile.row
      row = self_row + spacing + 1 if direction in ['up', 'right', 'up_right'] else \
        self_row - spacing - 1
    if self.direction == 'up_left':
      row = 1
      self_end = Line(start_tile = self.start_tile, direction = 'down_right').end_tile
      row = self_row + spacing + 1 if direction in ['up', 'left', 'up_left'] else \
        self_row - spacing - 1

    return Line(start_tile = Tile(start_column, start_row), direction = self.direction)

  def draw(self, color):
    self.color = color
    super().draw(color)
    return self

class Circle(Shape):
  '''A class to represent a circle on the board. This is a Shape object with tiles that are along a circle

  Attributes:
  ---------------
    center_tile: Tile
      The center of the circle
    color: str
      The color of the circle
  '''

  def __init__(self, center_tile, radius = 1):
    '''
    Parameters:
    ---------------
    center_tile: Tile
      The center of the circle
    radius: int
      The radius of the circle
    '''

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
    super().__init__(hexagons, from_hexagons = True)
    self.center_tile =  center_tile
    self.color = None

  def _show(self):
    print(f'{self.__class__.__name__} instance: linds = {self._linds}, size = {self._size}, center = {self.center_tile.offset}, color = {self.color}')

  def draw(self, color):
    '''Draw the circle in the given color.

    Parameters:
    ---------------
    color: str
      The color
    '''

    self.color = color
    super().draw(color)
    return self

class Triangle(Shape):
  '''A class to represent a triangle on the board.
  This is a Shape object with tiles that are along a triangle.

  Attributes:
   ---------------
     center_tile: Tile
       The center of the circle
     color: str
       The color of the circle
   '''

  def __init__(self, start_tile, point, start_tile_type, side_length = 2):
    '''
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
    '''

    tiles = []
    d_directions = {'left': ['up_right', 'down', 'up_left'], 'right': ['up_left', 'down', 'up_right']}
    types = ['side', 'top', 'bottom']
    tile = start_tile
    directions = _Vec.cyclic_permutation(d_directions[point], -types.index(start_tile_type))
    for i_edge in range(3):
      for _ in range(side_length - 1):
        tiles.append(tile)
        tile = tile.neighbor(directions[i_edge])
    super().__init__(tiles)
    self.point = point
    self.side_length = side_length
    self.color = None

  def _show(self):
    print(f'{self.__class__.__name__} instance: linds = {self._linds}, size = {self._size}, center = {self.center_tile.offset}, color = {self.color}')

  def draw(self, color):
    '''Draw the triangle in the given color

    Parameters:
    ---------------
    color: str
      The color
    '''

    self.color = color
    super().draw(color)
    return self

if __name__ == '__main__':
  HexagonsGame.start()

  HexagonsGame.record_step(1)
  l1 = Line(Tile(10, 5), direction = 'up_left')
  l1.draw('black')

  HexagonsGame.record_step(2)
  l2 = Line(Tile(1, -1), direction = 'up_right')
  l2.draw('black')

  HexagonsGame.record_step(3)
  HexagonsGame.get_record([1]).draw('red')

  HexagonsGame.plot()
