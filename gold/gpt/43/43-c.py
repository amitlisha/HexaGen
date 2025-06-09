# Created by chat gpt

from utils.reading_tasks import read_task
from hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle

task_index = 43
gold_boards = list(read_task(task_index)['gold_boards'])

HexagonsGame.start()

# paint the cell at the 1st column on the left and 2nd row from top with red
tile = Tile(1, 2)
tile.draw('red')

# paint the top 2 cells of the 2nd column from left with red
for i in range(1, 3):
    tile = Tile(2, i)
    tile.draw('red')

# paint the top 3 rows of the 3rd column from the left with red
for i in range(1, 4):
    tile = Tile(3, i)
    tile.draw('red')

# repeat the triangle pattern 3 more times to the right of the 1st triangle
triangle = Shape([Tile(1, 1), Tile(1, 2), Tile(2, 2), Tile(3, 2), Tile(3, 1), Tile(2, 1)])
for i in range(1, 4):
    spacing = 1 + (i - 1) * 4
    triangle_copy = triangle.copy_paste('right', spacing)
    triangle_copy.draw('red')

import os
HexagonsGame.plot(gold_boards=None, multiple=0,file_name=os.path.basename(__file__).split('.')[0])
