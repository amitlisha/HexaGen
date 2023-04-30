# Created by chat gpt

from utils.reading_tasks import read_task
from src.hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle
from constants.constants import *

HexagonsGame.start()

# Constants
HEIGHT = 10 # number of rows
WIDTH = 18 # number of columns
COLORS = ['white', 'black', 'yellow', 'green', 'red', 'blue', 'purple', 'orange']
DIRECTIONS = ['up', 'down', 'down_right', 'up_left', 'down_left', 'up_right']

# Create the game object
# game = HexagonsGame()

# Starting at the upper left, in the third column, paint the second and third tiles from the top green and all the tiles adjacent to them purple.
tile = Tile(3, 2)
tile.draw('green')
for direction in DIRECTIONS:
    tile.neighbor(direction).draw('purple')

# Repeat this color pattern of green surrounded by purple, starting with green on the second and third tiles from the bottom in the fourth column from the right,
# and once more, starting with green on the second and third tiles from the bottom in the seventh column from the left.
tile = Tile(-4, -3)
tile.draw('green')
for direction in DIRECTIONS:
    tile.neighbor(direction).draw('purple')

tile = Tile(7, -3)
tile.draw('green')
for direction in DIRECTIONS:
    tile.neighbor(direction).draw('purple')

# Duplicate this shape, but beginning with blue in the second and third tiles from the top in the fourth column from the right
# and in the second and third tiles from the bottom in the eighth column from the right, surrounding each pair of blue tiles with a purple border.
shape = HexagonsGame.get_record('step1')
shift_direction = 'down_right'
spacing = (2, 7)

for i in range(2):
    new_shape = shape.copy_paste(shift_direction, spacing)
    tile1 = new_shape.tiles[1]
    tile2 = new_shape.tiles[2]
    tile1.draw('blue')
    tile2.draw('blue')
    for direction in DIRECTIONS:
        tile1.neighbor(direction).draw('purple')
        tile2.neighbor(direction).draw('purple')
    shift_direction = 'down_left'

# In the third column from the left, paint the second tile from the bottom blue and the one directly above it green.
tile = Tile(-3, -1)
tile.draw('blue')
tile.neighbor('up').draw('green')

# Paint the second tile from the top green and the tile directly below it blue in the seventh column from the left.
tile = Tile(7, 2)
tile.draw('green')
tile.neighbor('down').draw('blue')

# In the eighth column from the right, paint the second tile from the top blue and the one directly below it green.
tile = Tile(-8, 2)
tile.draw('blue')
tile.neighbor('down').draw('green')

# Paint each tile adjacent to the three pairs of blue and green tiles orange.
for i in range(2):
    shape = game.get_record('step2').copy_paste('down_right', (2, 7))
    for tile in shape.tiles:
        if tile.color == 'blue' or tile.color == 'green':
            for direction in DIRECTIONS:
                neighbor = tile.neighbor(direction)
                if neighbor and neighbor.color not in ['blue', 'green']:
                    neighbor.draw('orange')

import os
image = os.path.dirname(__file__).split('\\')[-1]
variation = os.path.basename(__file__).split('.')[0]
HexagonsGame.plot(gold_boards=None, multiple=0,file_name=f'{image}-{variation}')
