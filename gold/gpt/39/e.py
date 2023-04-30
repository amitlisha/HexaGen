# Created by chat gpt

from utils.reading_tasks import read_task
from src.hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle
from constants.constants import *

HexagonsGame.start()

# create game board
board = [[Tile(col, row) for col in range(1, WIDTH+1)] for row in range(1, HEIGHT+1)]

# get the tile on the fifth row down from the top and tenth row from the left
tile = board[5-1][10-1]

# color all tiles that touch it red
shape = tile.neighbors()
shape.draw('red')

red_tile = board[5-1][10-1]

# get the two tiles directly on top of the uppermost red tile
left_tile = red_tile.neighbor('up_left')
right_tile = red_tile.neighbor('up_right')

# create a green six-sided flower
for i in range(6):
    # create a shape starting from the leftmost wall of the new green six-sided flower
    shape = left_tile.neighbors()

    # draw the shape in green color
    shape.draw('green')

    # get the tile at the opposite end of the shape
    right_tile = shape.tiles[-1]

    # update the leftmost wall of the new green six-sided flower
    left_tile = right_tile.neighbor('down_right')

red_shape = HexagonsGame.get_record('red_circle')

# get the tile to the right of the red circle
tile = board[5-1][10]

# create a blue six-sided circle that touches both the green and red
for i in range(6):
    # create a shape that touches both the green and red
    shape = tile.neighbors() & red_shape

    # draw the shape in blue color
    shape.draw('blue')

    # get the tile at the opposite end of the shape
    tile = shape.tiles[-1]

    # alternate between green and blue
    if i % 2 == 0:
        color = 'green'
    else:
        color = 'blue'

    # create a new shape with the color
    shape = tile.neighbors()
    shape.draw(color)

import os
image = os.path.dirname(__file__).split('\\')[-1]
variation = os.path.basename(__file__).split('.')[0]
HexagonsGame.plot(gold_boards=None, multiple=0,file_name=f'{image}-{variation}')
