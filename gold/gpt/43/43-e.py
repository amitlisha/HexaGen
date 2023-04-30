# Created by chat gpt

from utils.reading_tasks import read_task
from src.hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle

task_index = 43
gold_boards = list(read_task(task_index)['gold_boards'])

HexagonsGame.start()

# Constants
HEIGHT = 10 # number of rows
WIDTH = 18 # number of columns
COLORS = ['white', 'black', 'yellow', 'green', 'red', 'blue', 'purple', 'orange']
DIRECTIONS = ['up', 'down', 'down_right', 'up_left', 'down_left', 'up_right']

# # Create a HexagonsGame instance
# game = HexagonsGame()

# 1. With red, paint the cell at the 1st column on the left and 2nd row from top.
HexagonsGame.record_step('step1')
Tile(1, 2).draw('red')

# 2. With red, paint the top 2 cells of the 2nd column from left.
HexagonsGame.record_step('step2')
Tile(2, 1).draw('red')
Tile(2, 2).draw('red')

# 3. With red, paint the top 3 rows of the 3rd column from the left.
HexagonsGame.record_step('step3')
for i in range(1, 4):
    Tile(3, i).draw('red')

# 4. Repeat the triangle pattern 3 more times to the right of the 1st triangle,
#    making sure to leave one empty column between each triangle.
HexagonsGame.record_step('step4')
for j in range(1, 4):
    for i in range(1, 4):
        Tile(j * 4 + i, i).draw('red')

HexagonsGame.get_record(['step1', 'step2', 'step3', 'step4']).draw('purple')

import os
HexagonsGame.plot(gold_boards=None, multiple=0,file_name=os.path.basename(__file__).split('.')[0])
