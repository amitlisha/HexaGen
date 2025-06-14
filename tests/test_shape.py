import unittest
from hexagen import Game, Tile, Shape, Line
from .base import HexagonsTests

class ShapeTests(HexagonsTests):
    @HexagonsTests.wrap_test
    def test_init(self):
        self.assertShapeLinds(Shape(tiles=[Tile(1, 1), Tile(2, 3)]), [0, 37])
        self.assertShapeLinds(Shape(tiles=[0, 5], from_linds=True), [0, 5])

    @HexagonsTests.wrap_test
    def test_arithmetic(self):
        self.assertShapeLinds((Shape([0, 1], from_linds=True) + Shape([1, 2], from_linds=True)), [0, 1, 2])
        self.assertShapeLinds((Shape([0, 1], from_linds=True) - Shape([1, 2], from_linds=True)), [0])
        self.assertShapeLinds((Shape([0, 1], from_linds=True) * Shape([1, 2], from_linds=True)), [1])
        self.assertTrue(Shape([0, 1], from_linds=True).overlaps(Shape([1, 2], from_linds=True)))
        self.assertFalse(Shape([0, 1], from_linds=True).overlaps(Shape([2, 3], from_linds=True)))
        self.assertFalse(Shape([0, 1], from_linds=True).is_empty())
        self.assertTrue(Shape([], from_linds=True).is_empty())

    @HexagonsTests.wrap_test
    def test_draw(self):
        Shape([0, 2], from_linds=True).draw('black')
        self.assertBoardNonZeros([0, 2])

    @HexagonsTests.wrap_test
    def test_grid(self):
        self.assertShapeLinds(Shape([56, 37, 38], from_linds=True).grid(shift_direction='right', spacing=2),
                              [64, 68, 37, 38, 41, 42, 45, 46, 49, 50, 56, 60])
        self.assertShapeLinds(Shape([56, 37, 38], from_linds=True).grid(shift_direction='right', spacing=2, num_copies=2),
                              [64, 37, 38, 41, 42, 45, 46, 56, 60])

    @HexagonsTests.wrap_test
    def test_copy_paste(self):
        self.assertShapeLinds(Shape([60,41,42], from_linds=True).copy_paste(shift_direction='right', spacing=3), [65, 64, 47])
        self.assertShapeLinds(Shape([60,41,42], from_linds=True).copy_paste(shift_direction='down_right', spacing=2), [81, 82, 100])
        self.assertShapeLinds(Shape([60,41,42], from_linds=True).copy_paste(shift_direction='right', spacing=2, reference_shape=Tile(10, 5)), [85, 84, 67])

    @HexagonsTests.wrap_test
    def test_reflect(self):
        self.assertShapeLinds(Shape([40,41,42], from_linds=True).reflect(column=10), [48, 49, 50])
        self.assertShapeLinds(Shape([40,41,42], from_linds=True).reflect(axis_line=Line(Tile(7, 5), direction='down_left')), [97, 98, 115])
        self.assertShapeLinds(Shape([40,41,42], from_linds=True).reflect(axis_direction='down_left', tile_on_axis=Tile(7, 5)), [97, 98, 115])

    @HexagonsTests.wrap_test
    def test_rotate(self):
        self.assertShapeLinds(Shape([40,41,42], from_linds=True).rotate(Tile(9, 5),120), [152, 115, 134])

    @HexagonsTests.wrap_test
    def test_recolor(self):
        with Game(3, 2) as g:
            S = Shape([0, 1, 2], from_linds=True)
            S[0].draw('red')
            S[1].draw('blue')
            S[2].draw('black')
            S.recolor(color_map={'red': 'red', 'blue': 'green', 'black': 'red'})
            self.assertEqual(g.board_state, [4, 3, 4, 0, 0, 0])

    @HexagonsTests.wrap_test
    def test_get_color(self):
        S1 = Shape([61, 117, 65], from_linds=True)
        S2 = Shape([2, 17], from_linds=True)
        S1.draw('red')
        S2.draw('yellow')
        self.assertShapeLinds(Shape.get_color(color='red'), [61, 117, 65])
        self.assertShapeLinds(Shape.get_color(color='all'), [61, 117, 65, 2, 17])

    @HexagonsTests.wrap_test
    def test_get_column(self):
        self.assertShapeLinds(Shape.get_column(column=1), [0, 18, 36, 54, 72, 90,108, 126, 144, 162])

    @HexagonsTests.wrap_test
    def test_get_criterion(self):
        S = Shape([61, 117, 65, 62, 116, 83, 118, 64, 79, 101, 45, 97], from_linds=True)
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
        self.assertShapeLinds(S.get(criterion='above'), [7, 8, 9, 10, 43, 44, 11,46, 47, 25, 26, 27, 28, 29])
        self.assertShapeLinds(S.get(criterion='below'), [133, 134, 135, 136, 169,170, 171, 172, 137, 173, 115, 119, 151, 153, 154, 155, 152])
        self.assertShapeLinds(S.get(criterion='top'), [61, 62, 45, 64, 65])

    @HexagonsTests.wrap_test
    def test_corners_endpoints(self):
        S = Shape([64, 65, 66, 134, 135, 136, 78, 79, 80, 82, 83, 84, 27, 96, 97, 98,99, 100, 101, 102, 43, 44, 45, 46, 47, 114, 115, 116, 117, 118, 119, 120, 60, 61, 62, 63], from_linds=True)
        self.assertShapeLinds(S.get(criterion='corners'), [66, 135, 114, 120, 27, 60])
        S2 = Shape([38, 39, 58, 59, 78], from_linds=True)
        self.assertShapeLinds(S2.get(criterion='endpoints'), [78, 38])

    @HexagonsTests.wrap_test
    def test_boundary(self):
        S = Shape([64, 65, 66, 134, 135, 136, 78, 79, 80, 82, 83, 84, 27, 96, 97, 98,99, 100, 101, 102, 43, 44, 45, 46, 47, 114, 115, 116, 117, 118, 119, 120, 60, 61, 62, 63], from_linds=True)
        self.assertShapeLinds(S.boundary(), [96, 66, 134, 102, 135, 136, 43, 44, 46, 47, 78, 114, 115, 84, 119, 120, 27, 60, 98, 99, 100, 80, 82, 63])
        self.assertShapeLinds(S.boundary(criterion='outer'), [96, 66, 134, 102, 135, 136, 43, 44, 46, 47, 78, 114, 115, 84, 119, 120, 27, 60])
        self.assertShapeLinds(S.boundary(criterion='inner'), [98, 99, 100, 80, 82, 63])

    @HexagonsTests.wrap_test
    def test_extreme_edge(self):
        S = Shape([61, 117, 65, 62, 116, 83, 118, 64, 79, 101, 45, 97], from_linds=True)
        self.assertShapeLinds(S.extreme(direction='up_right'), [65])
        self.assertShapeLinds(S.edge(direction='right'), [65, 83, 101])
        self.assertShapeLinds(S.edge(direction='top'), [61, 62, 45, 64, 65])

    @HexagonsTests.wrap_test
    def test_neighbors(self):
        S = Shape([61, 117, 65, 62, 116, 83, 118, 64, 79, 101, 45, 97], from_linds=True)
        self.assertShapeLinds(S.neighbors(), [134, 135, 136, 27, 43, 44, 46, 47, 60, 63, 66, 78, 80, 82, 84, 96, 98, 99, 100, 102, 114, 115, 119, 120])
        self.assertShapeLinds(S.neighbors(criterion='all'), [134, 135, 136, 27, 43,44, 46, 47, 60, 63, 66, 78, 80, 82, 84, 96, 98, 99, 100, 102, 114, 115, 119, 120])
        self.assertShapeLinds(S.neighbors(criterion='right'), [84, 102])
        self.assertShapeLinds(S.neighbors(criterion='left'), [96, 78])
        self.assertShapeLinds(S.neighbors(criterion='below'), [134, 135, 136, 115, 119])
        self.assertShapeLinds(S.neighbors(criterion='outside'), [96, 66, 134, 135, 136, 102, 43, 44, 46, 47, 78, 114, 115, 84, 119, 120, 27, 60])
        self.assertShapeLinds(S.neighbors(criterion='inside'), [98, 99, 100, 80, 82, 63])
        with Game(18, 10) as g:
            S[0].neighbor('up').draw('black')
            self.assertShapeLinds(S.neighbors(criterion='white'), [134, 135, 136, 27,44, 46, 47, 60, 63, 66, 78, 80, 82, 84, 96, 98, 99, 100, 102, 114, 115, 119, 120])

    @HexagonsTests.wrap_test
    def test_polygon(self):
        tiles = [Tile(5, 5), Tile(8, 3), Tile(5, 7), Tile(8, 8), Tile(13, 6)]
        self.assertShapeLinds(Shape.polygon(tiles), [43, 59, 60, 62, 63, 76, 82, 83, 94, 101, 102, 112, 113, 117, 118, 132, 133, 134])

    @HexagonsTests.wrap_test
    def test_center(self):
        self.assertEqual(Shape([Tile(4, 3), Tile(3, 5), Tile(4, 5), Tile(5, 5), Tile(3, 4), Tile(5, 4)]).center().offset, (4, 4))

def load_tests(loader, tests, pattern):
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(ShapeTests))
    return suite
