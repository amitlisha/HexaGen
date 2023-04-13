# Created by maor

from utils.reading_tasks import read_task
from src.hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle

task_index = 85
gold_boards = list(read_task(task_index)['gold_boards'])

HexagonsGame.start()

# description:
# task index: 85, image: P01C02T29, collection round: 1, category: bounded iteration, group: train
# agreement scores: [[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [0.83, 1.0, 0.83], [0.56, 1.0, 0.56], [0.47, 0.91, 0.43], [0.47, 0.83, 0.39]]

'''
1. In the 1st column from the left, color the bottom-most tile GREEN. Color the
tile down and to the right of this tile GREEN as well.
'''
tile1 = Tile(1,-1)
tile1.draw('green')

tile1.neighbor('down_right').draw('green')

'''
2. In the 4th column from the left, color the bottom-most tile YELLOW. Color the
tile up and to the right of this tile YELLOW as well.
'''
tile2 = Tile(4,-1)
tile2.draw('yellow')

tile2.neighbor('up_right').draw('yellow')

'''
3. In the 7th column from the left, color the two bottom-most tiles GREEN.
'''
line1 = Line(start_tile=Tile(7,-1), direction='up', length=2)
line1.draw('green')

'''
4. Take note of the three groups of shapes you've just drawn. This will be our base
pattern.
'''

'''
5. Copy and translate the base pattern UP by three tiles, but invert the colors;
the shapes which were green in the old pattern should be yellow in the new
pattern, and vice versa. The 4th and 5th tiles from the bottom in the 7th column
from the left should be filled in.
'''

tile1 = Tile(1,-1 - 3)
tile1.draw('yellow')

tile1.neighbor('down_right').draw('yellow')

tile2 = Tile(4,-1 - 3)
tile2.draw('green')

tile2.neighbor('up_right').draw('green')

line1 = Line(start_tile=Tile(7,-1 - 3), direction='up', length=2)
line1.draw('yellow')

'''
6. Copy and translate this new pattern UP by another three tiles, inverting the
color palette again (i.e., should match the first base pattern you drew). The
3rd and 4th tiles from the TOP of the 7th column from the left should be filled
in.
'''

tile1 = Tile(1,-1 - 6)
tile1.draw('green')

tile1.neighbor('down_right').draw('green')

tile2 = Tile(4,-1 - 6)
tile2.draw('yellow')

tile2.neighbor('up_right').draw('yellow')

line1 = Line(start_tile=Tile(7,-1 - 6), direction='up', length=2)
line1.draw('green')

'''
7. Reflect the diagonal shapes in the first 5 columns across horizontally, using
the 7th column as the line of symmetry. Note that color patterns should be
reflected symmetrically as well.
'''
shape1 = Shape.get_color('green')
shape1.reflect(axis_line=line1)

shape2 = Shape.get_color('yellow')
shape2.reflect(axis_line=line1)

'''
8. Copy and translate the vertical groupings of shapes (the 7th column from the
left) to the third column from the RIGHT, inverting the colors. These should
meet the bottom edge of the grid.
'''

line3 = Line(start_tile=Tile(-3, -1), length=2, direction='up')
line3.draw('yellow')

line4 = Line(start_tile=Tile(-3, -4), length=2, direction='up')
line4.draw('green')

line5 = Line(start_tile=Tile(-3, -7), length=2, direction='up')
line5.draw('yellow')

HexagonsGame.plot(gold_boards=gold_boards, multiple=0)
