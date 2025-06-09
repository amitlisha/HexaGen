# Created by chat gpt

from utils.reading_tasks import read_task
from hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle
from constants.constants import *

HexagonsGame.start()

# Step 1
for row in range(2, 4):
    HexagonsGame.record_step('Step 1')
    tile = Tile(3, row)
    tile.draw('green')
    for direction in ['up', 'down', 'down_right', 'up_left', 'down_left', 'up_right']:
        neighbor = tile.neighbor(direction)
        if neighbor and neighbor.on_board():
            neighbor.draw('purple')

# Step 2
for column in [14, 11]:
    for row in range(2, 4):
        HexagonsGame.record_step('Step 2')
        tile = Tile(column, row)
        tile.draw('green')
        for direction in ['up', 'down', 'down_right', 'up_left', 'down_left', 'up_right']:
            neighbor = tile.neighbor(direction)
            if neighbor and neighbor.on_board():
                neighbor.draw('purple')
        tile2 = Tile(column, HEIGHT - row + 1)
        tile2.draw('green')
        for direction in ['up', 'down', 'down_right', 'up_left', 'down_left', 'up_right']:
            neighbor = tile2.neighbor(direction)
            if neighbor and neighbor.on_board():
                neighbor.draw('purple')

# Step 3
for column in [11, 15]:
    for row in range(2, 4):
        HexagonsGame.record_step('Step 3')
        tile = Tile(column, row)
        tile.draw('blue')
        for direction in ['up', 'down', 'down_right', 'up_left', 'down_left', 'up_right']:
            neighbor = tile.neighbor(direction)
            if neighbor and neighbor.on_board():
                neighbor.draw('purple')
        tile2 = Tile(column, HEIGHT - row + 1)
        tile2.draw('blue')
        for direction in ['up', 'down', 'down_right', 'up_left', 'down_left', 'up_right']:
            neighbor = tile2.neighbor(direction)
            if neighbor and neighbor.on_board():
                neighbor.draw('purple')

# Step 4
HexagonsGame.record_step('Step 4')
tile = Tile(3, HEIGHT - 1)
tile.draw('green')
tile2 = tile.neighbor('down')
tile2.draw('blue')

# Step 5
HexagonsGame.record_step('Step 5')
tile = Tile(7, 2)
tile.draw('green')
tile2 = tile.neighbor('down')
tile2.draw('blue')

# Step 6
HexagonsGame.record_step('Step 6')
tile = Tile(15, 2)
tile.draw('blue')
tile2 = tile.neighbor('down')
tile2.draw('green')

# Step 7
for column, row in [(3, HEIGHT - 1), (7, 2), (15, 2)]:
    HexagonsGame.record_step('Step 7')
    for direction in ['up', 'down', 'down_right', 'up_left', 'down_left', 'up_right']:
        tile = Tile(column, row)
        neighbor = tile.neighbor(direction)
        if neighbor and neighbor.on_board():
            neighbor.draw('orange')

import os
image = os.path.dirname(__file__).split('\\')[-1]
variation = os.path.basename(__file__).split('.')[0]
HexagonsGame.plot(gold_boards=None, multiple=0,file_name=f'{image}-{variation}')
