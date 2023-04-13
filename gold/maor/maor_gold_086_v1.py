# Created by maor

from utils.reading_tasks import read_task
from src.hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle

task_index = 86
gold_boards = list(read_task(task_index)['gold_boards'])

HexagonsGame.start()

# description:
# task index: 86, image: P01C02T29, collection round: 1, category: bounded iteration, group: train
# agreement scores: [[0, 1.0, 0], [0.5, 1.0, 0.5], [0.51, 0.94, 0.45], [0.5, 1.0, 0.5], [0.5, 0.88, 0.56], [0.43, 0.74, 0.53], [0.37, 0.71, 0.49]]

'''
1. Begin at third column from right side. Starting from bottom, make hexagons 1, 2,
7, and 8 yellow. Make 4 and 5 green.
'''
tile1 = Tile(-3, -1)
tile2 = Tile(-3, -2)
tile3 = Tile(-3, -7)
tile4 = Tile(-3, -8)

tile5 = Tile(-3, -4)
tile6 = Tile(-3, -5)

tile1.draw('yellow')
tile2.draw('yellow')
tile3.draw('yellow')
tile4.draw('yellow')

tile5.draw('green')
tile6.draw('green')

'''
2. Keep the colors and spacing the same, but reverse the color scheme in column 7
from the left side.
'''
tile1 = Tile(7, -1)
tile2 = Tile(7, -2)
tile3 = Tile(7, -7)
tile4 = Tile(7, -8)

tile5 = Tile(7, -4)
tile6 = Tile(7, -5)

tile1.draw('green')
tile2.draw('green')
tile3.draw('green')
tile4.draw('green')

tile5.draw('yellow')
tile6.draw('yellow')

'''
3. In bottom left corner color two hexagons green. continue on bottom row to the
right and leave next hexagon white, the two after that should be yellow.
'''
HexagonsGame.record_step('1')

tile7 = Tile(5, -1)
tile8 = Tile(4, -1)

tile7.draw('yellow')
tile8.draw('yellow')

tile9 = Tile(2, -1)
tile10 = Tile(1, -1)

tile9.draw('green')
tile10.draw('green')

HexagonsGame.record_step('2') # for recording stop

'''
4. Make a mirror image of this scheme on the other side of the two green hexagons
at the bottom of column 7 from the left.
'''

shape = Shape([tile7, tile8, tile9, tile10])
shape.reflect(column=7)

'''
5. Go back to first column on left side. make fourth hexagon from bottom of columns
1 and 2 yellow, then the 4th and 5th hexagons in same row green.
'''
tile11 = Tile(1,-4)
tile12 = Tile(2,-4)

tile11.draw('yellow')
tile12.draw('yellow')

tile13 = Tile(4,-4)
tile14 = Tile(5,-4)

tile13.draw('green')
tile14.draw('green')

'''
6. do a mirror image of this scheme on the other side of the two yellow hexagons on
the 7th column from the left.
'''

shape = Shape([tile11, tile12, tile13, tile14])
shape.reflect(column=7)

'''
7. repeat what you did in step three on the fourth row from the top left side with
the same mirror image on other side of the two green hexagons in column 7.
'''
shape = HexagonsGame.get_record(step_names=['1'])
cpy = shape.copy_paste(shift_direction='up', spacing=5)
cpy.reflect(column=7)

HexagonsGame.plot(gold_boards=gold_boards, multiple=0)
