# Created by chat gpt

from utils.reading_tasks import read_task
from hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle
from constants.constants import *

task_index = 34
gold_boards = list(read_task(task_index)['gold_boards'])

HexagonsGame.start()

# Create a blue flower of six tiles surrounding the fifth tile in the tenth column
center_tile = Tile(10, 5)
blue_flower_tiles = [center_tile]
for direction in ['up_right', 'down_right', 'down', 'down_left', 'up_left', 'up']:
    blue_flower_tiles.append(center_tile.neighbor(direction))
blue_flower = Shape(blue_flower_tiles)
blue_flower.draw('blue')

# Create four orange flowers connecting to the original on the outermost corners,
# leaving a white tile between each orange flower
for direction in ['up_right', 'down_right', 'down_left', 'up_left']:
    orange_flower_center_tile = center_tile.neighbor(direction)
    orange_flower_tiles = [orange_flower_center_tile]
    for direction2 in ['up_right', 'down_right', 'down', 'down_left', 'up_left', 'up']:
        tile = orange_flower_center_tile.neighbor(direction2)
        if tile.on_board() and tile not in blue_flower_tiles:
            orange_flower_tiles.append(tile)
    orange_flower = Shape(orange_flower_tiles)
    white_tile = orange_flower_center_tile.neighbor(direction)
    if white_tile.on_board() and white_tile not in blue_flower_tiles:
        white_tile.draw('white')
    orange_flower.draw('orange')


import os
HexagonsGame.plot(gold_boards=None, multiple=0,file_name=os.path.basename(__file__).split('.')[0])
