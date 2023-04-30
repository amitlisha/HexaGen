# Created by chat gpt

from utils.reading_tasks import read_task
from src.hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle

task_index = 44
gold_boards = list(read_task(task_index)['gold_boards'])

HexagonsGame.start()

# create the first triangle
row = 1
column = 3
for i in range(3):
    tile = Tile(column, row)
    tile.draw('red')
    column += 1
    row += 1

row = 2
column = 2
for i in range(2):
    tile = Tile(column, row)
    tile.draw('red')
    column += 1
    row += 1

row = 3
column = 1
tile = Tile(column, row)
tile.draw('red')

# create the second triangle
row = 6
column = 3
for i in range(3):
    tile = Tile(column, row)
    tile.draw('red')
    column += 1
    row += 1

row = 5
column = 2
for i in range(2):
    tile = Tile(column, row)
    tile.draw('red')
    column += 1
    row += 1

row = 4
column = 1
tile = Tile(column, row)
tile.draw('red')

# create the third triangle
row = 9
column = 3
for i in range(3):
    tile = Tile(column, row)
    tile.draw('red')
    column += 1
    row += 1

row = 8
column = 2
for i in range(2):
    tile = Tile(column, row)
    tile.draw('red')
    column += 1
    row += 1

row = 7
column = 1
tile = Tile(column, row)
tile.draw('red')

# create the fourth triangle
row = 12
column = 3
for i in range(3):
    tile = Tile(column, row)
    tile.draw('red')
    column += 1
    row += 1

row = 11
column = 2
for i in range(2):
    tile = Tile(column, row)
    tile.draw('red')
    column += 1
    row += 1

row = 10
column = 1
tile = Tile(column, row)
tile.draw('red')

# Save the record of the first triangle and retrieve it to make the remaining 3 triangles
# HexagonsGame.record_step('first triangle')
# triangle = HexagonsGame.get_record('first triangle')
#
# # create the remaining triangles
# for i in range(3):
#     triangle.copy_paste('down', 1)

import os
HexagonsGame.plot(gold_boards=None, multiple=0,file_name=os.path.basename(__file__).split('.')[0])
