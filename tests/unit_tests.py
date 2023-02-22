import sys
import unittest
sys.path.append('../src')
from hexagons_classes import HexagonsGame, _Vec, _Hexagon, Tile, Shape, Line, Circle, Triangle

class HexagonsTests(unittest.TestCase):

  def assertShapeLinds(self, S, linds):
    return self.assertEqual(set(S._linds), set(linds))

  def assertBoardNonZeros(self, indices):
    board_nz_indices = [i for i in range(len(HexagonsGame.board_state)) if HexagonsGame.board_state[i] != 0]
    return self.assertEqual(set(board_nz_indices), set(indices))

class _VecTests(unittest.TestCase):
  def test(self):
    self.assertEqual(_Vec('up')._cube, [0, -1, 1])
    self.assertEqual(_Vec(1, 1, -2)._cube, [1, 1, -2])
    self.assertEqual(_Vec(2, 3)._cube, [2, 2, -4])
    self.assertEqual(_Vec.cyclic_permutation([0,1,2,3], 2), [2, 3, 0, 1])
    self.assertEqual(_Vec.cyclic_permutation([0,1,2,3], -1), [1, 2, 3, 0])
    self.assertEqual(_Vec(.7, .8, -1.5)._round()._cube, [1, 1, -2])
    self.assertEqual(_Vec(.2, .3, -.5)._round()._cube, [0, 0, 0])
    self.assertEqual(_Vec(5.3, -2.1, -3.2)._norm(), 5.3)
    self.assertEqual(_Vec(1,0,-1)._scale(3)._cube, [3, 0, -3])
    self.assertEqual((_Vec(-3, -4, 7) - _Vec(1, -6, 5))._cube, [-4, 2, 2])
    self.assertEqual((_Vec(-3, -4, 7) + _Vec(1, -6, 5))._cube, [-2, -10, 12])
    self.assertEqual(_Vec(-4, 0, 4)._direction_str(), 'up_left')
    self.assertEqual(_Vec(-4, 0, 4)._normalize()._cube, [-1, 0, 1])
    self.assertEqual(_Vec(0, -3, 3)._has_direction(), True)
    self.assertEqual(_Vec(1, -4, 3)._has_direction(), False)
    self.assertEqual(_Vec(0, -3, 3)._has_direction(), True)
    print('finished _Vec testing')

class _HexagonTests(HexagonsTests):

  def test(self):

    HexagonsGame.start()
    self.assertEqual(_Hexagon._from_lind(17)._offset, [18, 1])
    self.assertIs(_Hexagon._from_lind(180)._lind, None)

    HexagonsGame.start()
    self.assertTrue(_Hexagon(-7, 6)._on_board())
    self.assertFalse(_Hexagon(0, 0, 0)._on_board())

    HexagonsGame.start()
    self.assertEqual((_Hexagon(7, 6) - _Hexagon(8, 5))._cube, [-1, 1, 0])

    HexagonsGame.start(2, 2)
    _Hexagon(1,2)._draw('black')
    _Hexagon(1,2)._copy_paste(_Vec('up'))
    self.assertEqual(HexagonsGame.board_state, [1, 0, 1, 0])
    HexagonsGame.start(2, 2)
    _Hexagon(1, 2)._draw('black')
    _Hexagon(1, 2)._copy_paste(_Vec('up'), color = 'yellow')
    self.assertEqual(HexagonsGame.board_state, [2, 0, 1, 0])

    HexagonsGame.start()
    self.assertEqual(_Hexagon(1,2)._shift(_Vec(-2, 3))._offset, [-1, 5])
    self.assertEqual(_Hexagon(1,2)._shift(_Vec(0, -1, 1))._offset, [1, 1])
    self.assertEqual(_Hexagon(1,2)._shift(0, -1, 1)._offset, [1, 1])

    HexagonsGame.start(4, 6)
    # self.assertEqual() Line!
    self.assertEqual(_Hexagon(1,2)._reflect(axis_direction = 'up_right', hexagon_on_axis = _Hexagon(2, 3))._cube, [2, 3, -5])
    self.assertEqual(_Hexagon(1,2)._reflect(column = 3)._offset, [5, 2])
    self.assertEqual(_Hexagon(2,2)._rotate(2, _Hexagon(3,3))._offset, [3, 4])
    _Hexagon(3,1)._draw('black')
    self.assertEqual(HexagonsGame.board_state, [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    self.assertEqual(_Hexagon(3,1)._neighbor('up')._offset, [3, 0])
    self.assertEqual(_Hexagon(3,1)._neighbor('down')._offset, [3, 2])
    self.assertShapeLinds(_Hexagon(3,1)._neighbors(), [6, 3, 1])

    print('finished HexagonsGame testing')

class ShapeTests(HexagonsTests):
#   def _size(self):
#   def _linds(self):
#   def tiles(self):
#   def colors(self):
#   def columns(self):
#   def rows(self):
#   def _cubes(self):
#   def _qs(self):
#   def _rs(self):
#   def _ss(self):
#   def _show(self):
#   def __iter__(self):
#   def __next__(self):
#   def __getitem__(self, item):
#   def _compute_shift_from_spacing(self, direction, spacing, reference_shape = None):
#   def _shifted_shape_fits_board(self, shift):
#   def _center_of_mass(self):

  def test(self):

    HexagonsGame.start()
    self.assertShapeLinds(Shape(tiles = [Tile(1, 1), Tile(2, 3)]), [0, 37])
    self.assertShapeLinds(Shape(tiles = [0, 5], from_linds = True), [0, 5])
    self.assertShapeLinds(Shape(tiles = [_Hexagon(1, 1), _Hexagon(2, 3)], from_hexagons = True), [0, 37])

    HexagonsGame.start()
    self.assertShapeLinds((Shape([0, 1], from_linds = True) + Shape([1, 2], from_linds = True)), [0, 1, 2])
    self.assertShapeLinds((Shape([0, 1], from_linds = True) - Shape([1, 2], from_linds = True)), [0])
    self.assertShapeLinds((Shape([0, 1], from_linds = True) * Shape([1, 2], from_linds = True)), [1])
    self.assertTrue(Shape([0, 1], from_linds = True).overlaps(Shape([1, 2], from_linds = True)))
    self.assertFalse(Shape([0, 1], from_linds = True).overlaps(Shape([2, 3], from_linds = True)))
    self.assertFalse(Shape([0, 1], from_linds = True).is_empty())
    self.assertTrue(Shape([], from_linds = True).is_empty())

    HexagonsGame.start()
    Shape([0, 2], from_linds = True).draw('black')
    self.assertBoardNonZeros([0, 2])

    HexagonsGame.start()
    self.assertShapeLinds(Shape([56, 37, 38], from_linds = True).grid(shift_direction = 'right', spacing = 2), [64, 68, 37, 38, 41, 42, 45, 46, 49, 50, 56, 60])
    self.assertShapeLinds(Shape([56, 37, 38], from_linds = True).grid(shift_direction = 'right', spacing = 2, num_copies = 2), [64, 37, 38, 41, 42, 45, 46, 56, 60])

    HexagonsGame.start()
    self.assertShapeLinds(Shape([60,41,42], from_linds = True).copy_paste(shift_direction = 'right', spacing = 3), [64, 45, 46])
    self.assertShapeLinds(Shape([60,41,42], from_linds = True).copy_paste(shift_direction = 'down_right', spacing = 2), [81, 82, 100])
    self.assertShapeLinds(Shape([60,41,42], from_linds = True).copy_paste(shift_direction = 'right', spacing = 2, reference_shape = Tile(10, 5)), [85, 84, 67])

    HexagonsGame.start()
    self.assertShapeLinds(Shape([40,41,42], from_linds = True).reflect(column = 10), [48, 49, 50])
    self.assertShapeLinds(Shape([40,41,42], from_linds = True).reflect(axis_line = Line(Tile(7, 5), direction = 'down_left')), [97, 98, 115])
    self.assertShapeLinds(Shape([40,41,42], from_linds = True).reflect(axis_direction = 'down_left', tile_on_axis = Tile(7, 5)), [97, 98, 115])

    HexagonsGame.start()
    self.assertShapeLinds(Shape([40,41,42], from_linds = True).rotate(2, Tile(9, 5)), [152, 115, 134])

    HexagonsGame.start(3, 2)
    S = Shape([0, 1, 2], from_linds = True)
    S[0].draw('red')
    S[1].draw('blue')
    S[2].draw('black')
    S.recolor(color_map = {'red': 'red', 'blue': 'green', 'black': 'red'})
    self.assertEqual(HexagonsGame.board_state, [4, 3, 4, 0, 0, 0])

    HexagonsGame.start()
    self.assertShapeLinds(Shape([38, 39, 58, 59, 78], from_linds = True)._shift(_Vec(6, -2, -4)), [102, 82, 83, 62, 63])

    S = Shape([61, 117, 65, 62, 116, 83, 118, 64, 79, 101, 45, 97], from_linds = True)
    self.assertShapeLinds(S.get(criterion = 'outside'), [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
                                                             20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36,
                                                             37, 38, 39, 40, 41, 42, 43, 44, 46, 47, 48, 49, 50, 51, 52, 53, 54,
                                                             55, 56, 57, 58, 59, 60, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76,
                                                             77, 78, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 102, 103,
                                                             104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 119, 120,
                                                             121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134,
                                                             135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148,
                                                             149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162,
                                                             163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176,
                                                             177, 178, 179])
    self.assertShapeLinds(S.get(criterion = 'inside'), [98, 99, 100, 80, 81, 82, 63])
    self.assertShapeLinds(S.get(criterion = 'above'), [7, 8, 9, 10, 43, 44, 11, 46, 47, 25, 26, 27, 28, 29])
    self.assertShapeLinds(S.get(criterion = 'below'), [133, 134, 135, 136, 169, 170, 171, 172, 137, 173, 115, 119, 151, 153, 154, 155, 152])
    self.assertShapeLinds(S.get(criterion = 'top'), [61, 62, 45, 64, 65])

    S = Shape([64, 65, 66, 134, 135, 136, 78, 79, 80, 82, 83, 84, 27, 96, 97, 98, 99, 100, 101, 102, 43, 44, 45, 46, 47, 114, 115, 116, 117, 118, 119, 120, 60, 61, 62, 63], from_linds = True)
    self.assertShapeLinds(S.get(criterion = 'corners'), [66, 135, 114, 120, 27, 60])
    S = Shape([38, 39, 58, 59, 78], from_linds = True)
    self.assertShapeLinds(S.get(criterion = 'end_points'), [78, 38])

    S = Shape([64, 65, 66, 134, 135, 136, 78, 79, 80, 82, 83, 84, 27, 96, 97, 98, 99, 100, 101, 102, 43, 44, 45, 46, 47, 114, 115, 116, 117, 118, 119, 120, 60, 61, 62, 63], from_linds = True)
    self.assertShapeLinds(S.boundary(), [96, 66, 134, 102, 135, 136, 43, 44, 46, 47, 78, 114, 115, 84, 119, 120, 27, 60, 98, 99, 100, 80, 82, 63])
    self.assertShapeLinds(S.boundary(criterion = 'outer'), [96, 66, 134, 102, 135, 136, 43, 44, 46, 47, 78, 114, 115, 84, 119, 120, 27, 60])
    self.assertShapeLinds(S.boundary(criterion = 'inner'), [98, 99, 100, 80, 82, 63])

    S = Shape([61, 117, 65, 62, 116, 83, 118, 64, 79, 101, 45, 97], from_linds = True)
    self.assertShapeLinds(S.extreme(direction = 'up_right'), [65])

    S = Shape([61, 117, 65, 62, 116, 83, 118, 64, 79, 101, 45, 97], from_linds = True)
    self.assertShapeLinds(S.edge(criterion = 'right'), [65, 83, 101])
    self.assertShapeLinds(S.edge(criterion = 'top'), [61, 62, 45, 64, 65])

    S = Shape([61, 117, 65, 62, 116, 83, 118, 64, 79, 101, 45, 97], from_linds = True)
    self.assertShapeLinds(S.neighbors(), [134, 135, 136, 27, 43, 44, 46, 47, 60, 63, 66, 78, 80, 82, 84, 96, 98, 99, 100, 102, 114, 115, 119, 120])
    self.assertShapeLinds(S.neighbors(criterion = 'all'), [134, 135, 136, 27, 43, 44, 46, 47, 60, 63, 66, 78, 80, 82, 84, 96, 98, 99, 100, 102, 114, 115, 119, 120])
    self.assertShapeLinds(S.neighbors(criterion = 'right'), [84, 102])
    self.assertShapeLinds(S.neighbors(criterion = 'left'), [96, 78])
    self.assertShapeLinds(S.neighbors(criterion = 'below'), [134, 135, 136, 115, 119])
    self.assertShapeLinds(S.neighbors(criterion = 'outside'), [96, 66, 134, 135, 136, 102, 43, 44, 46, 47, 78, 114, 115, 84, 119, 120, 27, 60])
    self.assertShapeLinds(S.neighbors(criterion = 'inside'), [98, 99, 100, 80, 82, 63])
    HexagonsGame.start(18, 10)
    S[0].neighbor('up').draw('black')
    self.assertShapeLinds(S.neighbors(criterion = 'white'), [134, 135, 136, 27, 44, 46, 47, 60, 63, 66, 78, 80, 82, 84, 96, 98, 99, 100, 102, 114, 115, 119, 120])

    HexagonsGame.start()
    tiles = [Tile(5, 5), Tile(8, 3), Tile(5, 7), Tile(8, 8), Tile(13, 6)]
    self.assertShapeLinds(Shape.polygon(tiles), [43, 59, 60, 62, 63, 76, 82, 83, 94, 101, 102, 112, 113, 117, 118, 132, 133, 134])

    HexagonsGame.start()
    self.assertEqual(Shape([Tile(4, 3), Tile(3, 5), Tile(4, 5), Tile(5, 5), Tile(3, 4), Tile(5, 4)]).center().offset, [4, 4])

    print('finished Shape testing')

class TileTests(HexagonsTests):

  def test(self):

    HexagonsGame.start()
    Tile(1, 1).draw('black')
    self.assertBoardNonZeros([0])

    HexagonsGame.start()
    self.assertEqual(Tile(1, 1).neighbor(direction = 'down')._lind, 18)
    self.assertEqual(Tile(1, 1).neighbor(direction = 'down').on_board(), True)
    self.assertEqual(Tile(1, 1).neighbor(direction = 'up').on_board(), False)

    print('finished Tile testing')


class LineTests(HexagonsTests):

  def test(self):
    HexagonsGame.start()
    self.assertShapeLinds(Line(start_tile=Tile(1, 1), direction='down_right'),
                          [0, 1, 20, 21, 40, 41, 60, 61, 80, 81, 100, 101, 120, 121, 140, 141, 160, 161])
    self.assertShapeLinds(Line(start_tile=Tile(1, 1), direction='down_right', length=5), [0, 1, 20, 21, 40])
    self.assertShapeLinds(Line(start_tile=Tile(1, 1), direction='down_right', length=5, include_start_tile=False),
                          [1, 20, 21, 40, 41])
    self.assertShapeLinds(Line(start_tile=Tile(1, 1), direction='down_right', length=5, include_end_tile=False),
                          [0, 1, 20, 21, 40])
    self.assertShapeLinds(Line(start_tile=Tile(1, 1), end_tile=Tile(5, 3)), [0, 1, 20, 21, 40])

    HexagonsGame.start()
    Line(start_tile=Tile(1, 1), direction='down_right', length=3).draw('black')
    self.assertBoardNonZeros([0, 1, 20])

    print('finished Line testing')

class CircleTests(HexagonsTests):

  def test(self):
    HexagonsGame.start()
    self.assertShapeLinds(Circle(center_tile=Tile(7, 6), radius=2),
                          [76, 132, 80, 59, 113, 98, 115, 61, 94, 116, 60, 112])

    HexagonsGame.start()
    Circle(center_tile=Tile(7, 6)).draw('black')
    self.assertBoardNonZeros([77, 114, 79, 97, 78, 95])

    print('finished Circle testing')

class TriangleTests(HexagonsTests):

  def test(self):
    HexagonsGame.start()
    self.assertShapeLinds(Triangle(start_tile=Tile(8, 6), point='left', start_tile_type='bottom', side_length=3),
                          [97, 96, 77, 78, 61, 79])
    Triangle(start_tile=Tile(8, 6), point='left', start_tile_type='bottom', side_length=3).draw('black')
    self.assertBoardNonZeros([97, 96, 77, 78, 61, 79])

    print('finished Triangle testing')

if __name__ == '__main__':
  unittest.main()
