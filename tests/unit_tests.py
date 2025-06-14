import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from functools import wraps
import unittest
from hexagen import Game, Tile, Shape, Line, Circle, Triangle

class HexagonsTests(unittest.TestCase):
  def wrap_test(func):
    @wraps(func)
    def mod_test(*args, **kwargs):
      print(f'starting {func.__qualname__}')
      func(*args, **kwargs)
      print(f'finishing {func.__qualname__}')
    return mod_test

  def assertShapeLinds(self, S, linds):
    return self.assertEqual(set(S._linds), set(linds))

  def assertBoardNonZeros(self, game, indices):
    board_nz_indices = [
        i for i in range(len(game.board_state)) if game.board_state[i] != 0
    ]
    return self.assertEqual(set(board_nz_indices), set(indices))
  
class GameTests(HexagonsTests):
  @HexagonsTests.wrap_test
  def test(self):
    with Game() as g:
      g.record_step(step_name='1')
      Tile(column=7, row=5).draw(color='black')
      g.record_step(step_name='2')
      Tile(column=7, row=5).neighbors().draw(color='yellow')

    self.assertShapeLinds(g.get_record(step_names=['1','2']), [78, 77, 79, 96, 61, 59, 60])
    self.assertShapeLinds(g.get_record(step_names='2'), [77, 79, 96, 61, 59, 60])



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
#   def _compute_shift_from_spacing(self, direction, spacing, reference_shape=None):
#   def _shifted_shape_fits_board(self, shift):
#   def _center_of_mass(self):
  @HexagonsTests.wrap_test
  def test(self):

    with Game() as g:
      self.assertShapeLinds(Shape(tiles=[Tile(1, 1), Tile(2, 3)]), [0, 37])
      self.assertShapeLinds(Shape(tiles=[0, 5], from_linds=True), [0, 5])

    with Game() as g:
      self.assertShapeLinds((Shape([0, 1], from_linds=True) + Shape([1, 2], from_linds=True)), [0, 1, 2])
      self.assertShapeLinds((Shape([0, 1], from_linds=True) - Shape([1, 2], from_linds=True)), [0])
      self.assertShapeLinds((Shape([0, 1], from_linds=True) * Shape([1, 2], from_linds=True)), [1])
      self.assertTrue(Shape([0, 1], from_linds=True).overlaps(Shape([1, 2], from_linds=True)))
      self.assertFalse(Shape([0, 1], from_linds=True).overlaps(Shape([2, 3], from_linds=True)))
      self.assertFalse(Shape([0, 1], from_linds=True).is_empty())
      self.assertTrue(Shape([], from_linds=True).is_empty())

    with Game() as g:
      Shape([0, 2], from_linds=True).draw('black')
      self.assertBoardNonZeros(g, [0, 2])

    with Game() as g:
      self.assertShapeLinds(Shape([56, 37, 38], from_linds=True).grid(shift_direction='right', spacing=2), [64, 68, 37, 38, 41, 42, 45, 46, 49, 50, 56, 60])
      self.assertShapeLinds(Shape([56, 37, 38], from_linds=True).grid(shift_direction='right', spacing=2, num_copies=2), [64, 37, 38, 41, 42, 45, 46, 56, 60])

    with Game() as g:
      self.assertShapeLinds(Shape([60,41,42], from_linds=True).copy_paste(shift_direction='right', spacing=3), [65, 64, 47])
      self.assertShapeLinds(Shape([60,41,42], from_linds=True).copy_paste(shift_direction='down_right', spacing=2), [81, 82, 100])
      self.assertShapeLinds(Shape([60,41,42], from_linds=True).copy_paste(shift_direction='right', spacing=2, reference_shape=Tile(10, 5)), [85, 84, 67])

    with Game() as g:
      self.assertShapeLinds(Shape([40,41,42], from_linds=True).reflect(column=10), [48, 49, 50])
      self.assertShapeLinds(Shape([40,41,42], from_linds=True).reflect(axis_line=Line(Tile(7, 5), direction='down_left')), [97, 98, 115])
      self.assertShapeLinds(Shape([40,41,42], from_linds=True).reflect(axis_direction='down_left', tile_on_axis=Tile(7, 5)), [97, 98, 115])

    with Game() as g:
      self.assertShapeLinds(Shape([40,41,42], from_linds=True).rotate(Tile(9, 5), 120), [152, 115, 134])

    with Game(3, 2) as g:
      S=Shape([0, 1, 2], from_linds=True)
      S[0].draw('red')
      S[1].draw('blue')
      S[2].draw('black')
      S.recolor(color_map={'red': 'red', 'blue': 'green', 'black': 'red'})
      self.assertEqual(g.board_state, [4, 3, 4, 0, 0, 0])

    with Game() as g:
      S1=Shape([61, 117, 65], from_linds=True)
      S2=Shape([2, 17], from_linds=True)
      S1.draw('red')
      S2.draw('yellow')
      self.assertShapeLinds(Shape.get_color(color='red'), [61, 117, 65])
      self.assertShapeLinds(Shape.get_color(color='all'), [61, 117, 65, 2, 17])

    with Game() as g:
      self.assertShapeLinds(Shape.get_column(column=1), [0, 18, 36, 54, 72, 90, 108, 126, 144, 162])

    with Game() as g:
      S=Shape([61, 117, 65, 62, 116, 83, 118, 64, 79, 101, 45, 97], from_linds=True)
      self.assertShapeLinds(S.get(criterion='outside'), [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
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
      self.assertShapeLinds(S.get(criterion='inside'), [98, 99, 100, 80, 81, 82, 63])
      self.assertShapeLinds(S.get(criterion='above'), [7, 8, 9, 10, 43, 44, 11, 46, 47, 25, 26, 27, 28, 29])
      self.assertShapeLinds(S.get(criterion='below'), [133, 134, 135, 136, 169, 170, 171, 172, 137, 173, 115, 119, 151, 153, 154, 155, 152])
      self.assertShapeLinds(S.get(criterion='top'), [61, 62, 45, 64, 65])

    S=Shape([64, 65, 66, 134, 135, 136, 78, 79, 80, 82, 83, 84, 27, 96, 97, 98, 99, 100, 101, 102, 43, 44, 45, 46, 47, 114, 115, 116, 117, 118, 119, 120, 60, 61, 62, 63], from_linds=True)
    self.assertShapeLinds(S.get(criterion='corners'), [66, 135, 114, 120, 27, 60])
    S=Shape([38, 39, 58, 59, 78], from_linds=True)
    self.assertShapeLinds(S.get(criterion='endpoints'), [78, 38])

    S=Shape([64, 65, 66, 134, 135, 136, 78, 79, 80, 82, 83, 84, 27, 96, 97, 98, 99, 100, 101, 102, 43, 44, 45, 46, 47, 114, 115, 116, 117, 118, 119, 120, 60, 61, 62, 63], from_linds=True)
    self.assertShapeLinds(S.boundary(), [96, 66, 134, 102, 135, 136, 43, 44, 46, 47, 78, 114, 115, 84, 119, 120, 27, 60, 98, 99, 100, 80, 82, 63])
    self.assertShapeLinds(S.boundary(criterion='outer'), [96, 66, 134, 102, 135, 136, 43, 44, 46, 47, 78, 114, 115, 84, 119, 120, 27, 60])
    self.assertShapeLinds(S.boundary(criterion='inner'), [98, 99, 100, 80, 82, 63])

    S=Shape([61, 117, 65, 62, 116, 83, 118, 64, 79, 101, 45, 97], from_linds=True)
    self.assertShapeLinds(S.extreme(direction='up_right'), [65])

    S=Shape([61, 117, 65, 62, 116, 83, 118, 64, 79, 101, 45, 97], from_linds=True)
    self.assertShapeLinds(S.edge(direction='right'), [65, 83, 101])
    self.assertShapeLinds(S.edge(direction='top'), [61, 62, 45, 64, 65])

    S=Shape([61, 117, 65, 62, 116, 83, 118, 64, 79, 101, 45, 97], from_linds=True)
    self.assertShapeLinds(S.neighbors(), [134, 135, 136, 27, 43, 44, 46, 47, 60, 63, 66, 78, 80, 82, 84, 96, 98, 99, 100, 102, 114, 115, 119, 120])
    self.assertShapeLinds(S.neighbors(criterion='all'), [134, 135, 136, 27, 43, 44, 46, 47, 60, 63, 66, 78, 80, 82, 84, 96, 98, 99, 100, 102, 114, 115, 119, 120])
    self.assertShapeLinds(S.neighbors(criterion='right'), [84, 102])
    self.assertShapeLinds(S.neighbors(criterion='left'), [96, 78])
    self.assertShapeLinds(S.neighbors(criterion='below'), [134, 135, 136, 115, 119])
    self.assertShapeLinds(S.neighbors(criterion='outside'), [96, 66, 134, 135, 136, 102, 43, 44, 46, 47, 78, 114, 115, 84, 119, 120, 27, 60])
    self.assertShapeLinds(S.neighbors(criterion='inside'), [98, 99, 100, 80, 82, 63])
    with Game(18, 10) as g:
      S[0].neighbor('up').draw('black')
      self.assertShapeLinds(S.neighbors(criterion='white'), [134, 135, 136, 27, 44, 46, 47, 60, 63, 66, 78, 80, 82, 84, 96, 98, 99, 100, 102, 114, 115, 119, 120])

    with Game() as g:
      tiles=[Tile(5, 5), Tile(8, 3), Tile(5, 7), Tile(8, 8), Tile(13, 6)]
      self.assertShapeLinds(Shape.polygon(tiles), [43, 59, 60, 62, 63, 76, 82, 83, 94, 101, 102, 112, 113, 117, 118, 132, 133, 134])

    with Game() as g:
      self.assertEqual(Shape([Tile(4, 3), Tile(3, 5), Tile(4, 5), Tile(5, 5), Tile(3, 4), Tile(5, 4)]).center().offset, (4, 4))

class TileTests(HexagonsTests):
  @HexagonsTests.wrap_test
  def test(self):

    with Game() as g:
      self.assertTrue(Tile(1, 1).on_board())
      self.assertTrue(Tile(-3, -1).on_board())
      Tile(1, 1).draw('black')
      self.assertBoardNonZeros(g, [0])

    with Game() as g:
      self.assertEqual(Tile(1, 1).neighbor(direction='down')._lind, 18)
      self.assertEqual(Tile(1, 1).neighbor(direction='down').on_board(), True)
      self.assertEqual(Tile(1, 1).neighbor(direction='up').on_board(), False)


class LineTests(HexagonsTests):
  @HexagonsTests.wrap_test
  def test(self):
    with Game() as g:
      self.assertShapeLinds(Line(start_tile=Tile(1, 1), direction='down_right'),
                            [0, 1, 20, 21, 40, 41, 60, 61, 80, 81, 100, 101, 120, 121, 140, 141, 160, 161])
      self.assertShapeLinds(Line(start_tile=Tile(1, 1), direction='down_right', length=5), [0, 1, 20, 21, 40])
      self.assertShapeLinds(Line(start_tile=Tile(1, 1), direction='down_right', length=5, include_start_tile=False),
                            [1, 20, 21, 40, 41])
      self.assertShapeLinds(Line(start_tile=Tile(1, 1), direction='down_right', length=5, include_end_tile=False),
                            [0, 1, 20, 21, 40])
      self.assertShapeLinds(Line(start_tile=Tile(1, 1), end_tile=Tile(5, 3)), [0, 1, 20, 21, 40])

    with Game() as g:
      Line(start_tile=Tile(1, 1), direction='down_right', length=3).draw('black')
      self.assertBoardNonZeros(g, [0, 1, 20])

    with Game() as g:
      line = Line(start_tile=Tile(5, 5), direction='up_right', length=5)
      self.assertShapeLinds(line.parallel(shift_direction='down', spacing=3), [163, 164, 147, 148, 131, 132, 115, 116, 99, 100, 83, 84, 67, 68, 51, 52, 35])

class CircleTests(HexagonsTests):
  @HexagonsTests.wrap_test
  def test(self):
    with Game() as g:
      self.assertShapeLinds(Circle(center_tile=Tile(7, 6), radius=2),
                            [76, 132, 80, 59, 113, 98, 115, 61, 94, 116, 60, 112])

    with Game() as g:
      Circle(center_tile=Tile(7, 6)).draw('black')
      self.assertBoardNonZeros(g, [77, 114, 79, 97, 78, 95])

class TriangleTests(HexagonsTests):
  @HexagonsTests.wrap_test
  def test(self):
    with Game() as g:
      self.assertShapeLinds(Triangle(start_tile=Tile(8, 6), point='left', start_tile_type='bottom', side_length=3),
                            [97, 96, 77, 78, 61, 79])
      Triangle(start_tile=Tile(8, 6), point='left', start_tile_type='bottom', side_length=3).draw('black')
      self.assertBoardNonZeros(g, [97, 96, 77, 78, 61, 79])

if __name__ == '__main__':
  unittest.main()
