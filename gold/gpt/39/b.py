# Created by chat gpt

from utils.reading_tasks import read_task
from hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle
from constants.constants import *

HexagonsGame.start()

# Step 1: Color all tiles that touch the center tile red
center_tile = Tile(column=10, row=5)
center_tile.draw('white')
red_tiles = Shape(center_tile.neighbors())
for tile in red_tiles.tiles:
    tile.draw('red')

# Step 2: Create a green six-sided flower around the central red circle
upper_red_tile = center_tile.neighbor('up')
green_tiles = Shape([upper_red_tile.neighbor('up_left'), upper_red_tile.neighbor('up_right')])
for i in range(6):
    if i % 2 == 0:
        # Alternate red and green
        red_tiles.draw('white')
        green_tiles.draw('green')
    else:
        red_tiles.draw('red')
        green_tiles.draw('white')
    # Rotate green_tiles around the center tile
    green_tiles = green_tiles.copy_paste('down_right', 1, reference_shape=red_tiles)

# Step 3: Create a blue six-sided circle around the central red circle
right_red_tile = center_tile.neighbor('down_right')
blue_tiles = Shape([right_red_tile.neighbor('up_right'), right_red_tile.neighbor('down_right')])
for i in range(6):
    if i % 2 == 0:
        # Alternate green and blue
        green_tiles.draw('white')
        blue_tiles.draw('blue')
    else:
        green_tiles.draw('green')
        blue_tiles.draw('white')
    # Rotate blue_tiles around the center tile
    blue_tiles = blue_tiles.copy_paste('down_right', 1, reference_shape=green_tiles)

    # Finish the last step
    blue_tiles.draw('blue')

import os
image = os.path.dirname(__file__).split('\\')[-1]
variation = os.path.basename(__file__).split('.')[0]
HexagonsGame.plot(gold_boards=None, multiple=0,file_name=f'{image}-{variation}')
