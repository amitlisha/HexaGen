# Created by chat gpt

from utils.reading_tasks import read_task
from hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle
from constants.constants import *

task_index = 35
gold_boards = list(read_task(task_index)['gold_boards'])

HexagonsGame.start()

# Step 1: Color all tiles orange around eighth vertical row from left, third tile from the top of that row, resulting in an orange circle there.
tile1 = Tile(7, 3)
shape1 = tile1.neighbors().copy_paste('down_right', 3).draw('orange')
HexagonsGame.record_step('step1')

# Step 2: On 12th vertical row from left, 3rd tile down, color all tiles touching that tile, orange.
tile2 = Tile(12, 3)
shape2 = tile2.neighbors().draw('orange')
HexagonsGame.record_step('step2')

# Step 3: On 8th vertical row 7th tile down, color all tiles touching that one orange, leaving it blank (as in other steps).
tile3 = Tile(7, 7)
shape3 = tile3.neighbors().draw('orange')
tile3.draw('white')
HexagonsGame.record_step('step3')

# Step 4: On 12th row, vertically from left, 7th tile down, color all tiles touching it orange, leaving it blank.
tile4 = Tile(12, 7)
shape4 = tile4.neighbors().draw('orange')
tile4.draw('white')
HexagonsGame.record_step('step4')

# Step 5: Form a blue circle to fit in between the 4 orange circles drawn, of the same number of tiles, same size (six tiles, as in others).
tile5 = Tile(9, 5)
shape5 = tile5.neighbors().copy_paste('down_right', 3).draw('blue')
HexagonsGame.record_step('step5')

# Display the final result
HexagonsGame.get_record(['step1', 'step2', 'step3', 'step4', 'step5']).draw('black')

import os
HexagonsGame.plot(gold_boards=None, multiple=0,file_name=os.path.basename(__file__).split('.')[0])
