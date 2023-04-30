# Created by chat gpt

from utils.reading_tasks import read_task
from src.hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle
from constants.constants import *

HexagonsGame.start()

# create the red circle
tile = Tile(10, 5)  # create a new Tile instance at column 10, row 5
tile.draw('red')    # color the tile red
neighbors = tile.neighbors()  # get all the neighbors of the tile
for neighbor in neighbors:
    neighbor.draw('red')  # color all the neighbors red

# create the green six-sided flower
red_top = Tile(10, 3)   # create a new Tile instance at column 10, row 3 (top of the red circle)
green_left = red_top.neighbor('up_left')   # get the neighbor tile in the up_left direction
green_left.draw('green')   # color the green_left tile green
green_neighbors = green_left.neighbors()  # get all the neighbors of the green_left tile
for i, neighbor in enumerate(green_neighbors):
    if i % 2 == 0:
        neighbor.draw('green')   # color every other neighbor green

# create the blue six-sided circle
blue_left = red_top.neighbor('down_right')   # get the neighbor tile in the down_right direction
blue_left.draw('blue')   # color the blue_left tile blue
blue_neighbors = blue_left.neighbors()   # get all the neighbors of the blue_left tile
for i, neighbor in enumerate(blue_neighbors):
    if i % 2 == 1:
        neighbor.draw('blue')   # color every other neighbor blue

# color the white center tiles
center_tiles = Shape([tile, green_left, blue_left])
for i in range(3):
    center_tiles.draw('white')

import os
image = os.path.dirname(__file__).split('\\')[-1]
variation = os.path.basename(__file__).split('.')[0]
HexagonsGame.plot(gold_boards=None, multiple=0,file_name=f'{image}-{variation}')
