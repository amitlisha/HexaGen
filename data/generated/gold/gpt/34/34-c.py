# Created by chat gpt

from utils.reading_tasks import read_task
from hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle
from constants.constants import *

task_index = 34
gold_boards = list(read_task(task_index)['gold_boards'])

HexagonsGame.start()

start_tile = Tile(10, 5)

# Make a blue flower of six tiles surrounding the starting tile
blue_flower = [start_tile]
for i in range(6):
    blue_flower.append(blue_flower[-1].neighbor('down_right'))
blue_shape = Shape(blue_flower)
blue_shape.draw('blue')

# Make four orange flowers connecting to the original on the outermost corners, leaving a white tile between each orange flower
orange_shape = Shape([])
for direction in ['up_right', 'down_right', 'up_left', 'down_left']:
    orange_flower = [start_tile.neighbor(direction)]
    for i in range(6):
        #orange_flower.append(orange_flower[-1].neighbor('down_right'))
        orange_flower += orange_flower[-1].neighbor('down_right')
    orange_shape = orange_shape.copy_paste(direction, 1)
    orange_shape.draw('white')
    orange_shape = orange_shape.copy_paste(direction, 1)
    orange_shape.draw('orange')

import os
HexagonsGame.plot(gold_boards=None, multiple=0,file_name=os.path.basename(__file__).split('.')[0])
