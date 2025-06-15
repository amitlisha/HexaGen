# Created by chat gpt

from utils.reading_tasks import read_task
from hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle
from constants.constants import *

task_index = 44
gold_boards = list(read_task(task_index)['gold_boards'])

HexagonsGame.start()

# draw the first red triangle
for i in range(3):
    Tile(i+6, i+1).draw('red')

for i in range(2):
    Tile(i+7, i+2).draw('red')

Tile(8, 3).draw('red')

# create the red triangle shape and add white row
red_triangle = Shape([Tile(i+6, i+1) for i in range(3)] +
                     [Tile(i+7, i+2) for i in range(2)] +
                     [Tile(8, 3)])

white_row = Shape([Tile(i+6, 4) for i in range(3)])

# create 4 red triangles with white row in between
for i in range(4):
    if i > 0:
        red_triangle.copy_paste('down', 4*i, reference_shape=white_row)
    red_triangle.copy_paste('down', 4*i)
    white_row.copy_paste('down', 4*i+3)

import os
HexagonsGame.plot(gold_boards=None, multiple=0,file_name=os.path.basename(__file__).split('.')[0])
