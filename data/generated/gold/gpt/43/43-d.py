# Created by chat gpt

from utils.reading_tasks import read_task
from hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle

task_index = 43
gold_boards = list(read_task(task_index)['gold_boards'])

HexagonsGame.start()

# Paint the cell at the 1st column on the left and 2nd row from top
tile1 = Tile(1, 2)
tile1.draw('red')

# Paint the top 2 cells of the 2nd column from left
tile2 = Tile(2, 1)
tile2.draw('red')
tile2.neighbor('down').draw('red')

# Paint the top 3 rows of the 3rd column from left
tile3 = Tile(3, 1)
tile3.draw('red')
tile3.neighbor('down').draw('red')
tile3.neighbor('down').neighbor('down').draw('red')

# Repeat the triangle pattern 3 more times to the right of the 1st triangle,
# making sure to leave one empty column between each triangle
for i in range(3):
    shape = Shape([tile1, tile2, tile3])
    shape.draw('red')
    tile1 = tile1.neighbor('down_right')
    tile2 = tile2.neighbor('down_right')
    tile3 = tile3.neighbor('down_right')
    tile1 = tile1.neighbor('down')
    tile2 = tile2.neighbor('down')
    tile3 = tile3.neighbor('down')

import os
HexagonsGame.plot(gold_boards=None, multiple=0,file_name=os.path.basename(__file__).split('.')[0])
