# Created by chat gpt

from utils.reading_tasks import read_task
from src.hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle
from constants.constants import *

HexagonsGame.start()

# Step 1: Draw a red circle
HexagonsGame.record_step('step1')
blank_tile = Tile(10, 5) # the tile at (10, 5) is blank
blank_tile.draw('white') # leave it blank
for direction in DIRECTIONS:
    neighbor = blank_tile.neighbor(direction)
    if neighbor.on_board():
        neighbor.draw('red')

# Step 2: Draw a green circle
HexagonsGame.record_step('step2')
red_top = Tile(10, 3) # the topmost red tile
for i in range(6): # six-sided flower
    if i % 2 == 0: # every other tile is green
        color = 'green'
    else:
        color = 'white'
    # draw tiles around the red tile, starting from the top
    tile = red_top.neighbor('up').neighbor('up_left').neighbor('up_left').neighbor('up_left')
    for j in range(i+1):
        tile.draw(color)
        tile = tile.neighbor('down_left')
    # rotate the direction to draw the next set of tiles
    red_top = red_top.neighbor('down_left')

# Step 3: Draw a blue circle
HexagonsGame.record_step('step3')
red = Tile(10, 5) # the red tile
green_right = Tile(13, 5) # the rightmost green tile
for i in range(6):
    if i % 2 == 0: # every other tile is green
        color = 'green'
        green_right = green_right.neighbor('down_right')
    else:
        color = 'blue'
    # draw tiles around the red tile, starting from the top
    tile = red.neighbor('up').neighbor('up_left').neighbor('up_left').neighbor('up_left')
    for j in range(i+1):
        tile.draw(color)
        tile = tile.neighbor('down_left')
    # draw tiles around the green tile to the right of red
    tile = green_right.neighbor('up_left')
    for j in range(i+2):
        tile.draw(color)
        tile = tile.neighbor('down_left')
    # rotate the direction to draw the next set of tiles
    red = red.neighbor('down_left')

# Show the final result
HexagonsGame.get_record(['step1', 'step2', 'step3']).draw('black')

import os
image = os.path.dirname(__file__).split('\\')[-1]
variation = os.path.basename(__file__).split('.')[0]
HexagonsGame.plot(gold_boards=None, multiple=0,file_name=f'{image}-{variation}')
