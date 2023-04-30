# Created by chat gpt

from utils.reading_tasks import read_task
from src.hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle
from constants.constants import *

HexagonsGame.start()

# Define the location of the central tile
central_tile_row = 5
central_tile_column = 10

# Draw the red circle
red_tiles = []
red_center = Tile(central_tile_column, central_tile_row)
red_tiles.append(red_center)
for direction in DIRECTIONS:
    neighbor = red_center.neighbor(direction)
    if neighbor.on_board():
        neighbor.draw('red')
        red_tiles.append(neighbor)

# Draw the green circle
green_tiles = []
green_center = red_tiles[0].neighbor('up')
green_tiles.append(green_center)
left_tile = green_center.neighbor('up_left')
left_tile.draw('green')
green_tiles.append(left_tile)
for i in range(1, 6):
    previous_tile = green_tiles[i - 1]
    if i % 2 == 1:
        next_tile = previous_tile.neighbor('up_left')
    else:
        next_tile = previous_tile.neighbor('down_left')
    next_tile.draw('green')
    green_tiles.append(next_tile)

# Draw the blue circle
blue_tiles = []
blue_center = red_tiles[0].neighbor('down_right')
blue_tiles.append(blue_center)
for i in range(6):
    previous_tile = blue_tiles[i - 1]
    if i % 2 == 0:
        next_tile = previous_tile.neighbor('down_right')
    else:
        next_tile = previous_tile.neighbor('up_right')
    next_tile.draw('blue')
    blue_tiles.append(next_tile)


import os
image = os.path.dirname(__file__).split('\\')[-1]
variation = os.path.basename(__file__).split('.')[0]
HexagonsGame.plot(gold_boards=None, multiple=0,file_name=f'{image}-{variation}')
