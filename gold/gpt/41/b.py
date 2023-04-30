# Created by chat gpt

from utils.reading_tasks import read_task
from src.hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle
from constants.constants import *

HexagonsGame.start()

tile = Tile(1, 1)

# Count over 5 cells down and up
for i in range(5):
    tile = tile.neighbor('down')
for i in range(5):
    tile = tile.neighbor('up')

# Color the cell purple
tile.draw('purple')

# Get a Shape object containing all the neighbors of the purple tile
red_shape = tile.neighbors()

# Color all the tiles in the shape red
for red_tile in red_shape.tiles:
    red_tile.draw('red')

# Find the topmost red tile in the red shape
top_red_tile = min(red_shape.tiles, key=lambda t: t.row)

# Find the two green tiles adjacent to the top of the ring
top_green_tile = top_red_tile.neighbor('up_right')
next_green_tile = top_green_tile.neighbor('up_right')

# Color the two green tiles
top_green_tile.draw('green')
next_green_tile.draw('green')
    
import os
image = os.path.dirname(__file__).split('\\')[-1]
variation = os.path.basename(__file__).split('.')[0]
HexagonsGame.plot(gold_boards=None, multiple=0,file_name=f'{image}-{variation}')
