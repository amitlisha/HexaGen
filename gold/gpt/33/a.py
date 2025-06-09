# Created by chat gpt

from utils.reading_tasks import read_task
from hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle
from constants.constants import *

HexagonsGame.start()

# create Tile objects for each location and color them appropriately
HexagonsGame.record_step('step1')
for i in range(7, 10):
    tile = Tile(8, i)
    tile.draw('orange')

HexagonsGame.record_step('step2')
for i in range(2, 6):
    tile = Tile(12, i)
    tile.draw('orange')

HexagonsGame.record_step('step3')
tile = Tile(8, 7)
tile.draw('orange')
neighbors = tile.neighbors()
neighbors.draw('white')

HexagonsGame.record_step('step4')
tile = Tile(12, 7)
tile.draw('orange')
neighbors = tile.neighbors()
neighbors.draw('white')

# create a Shape object for the blue circle and draw it on the board
HexagonsGame.record_step('step5')
blue_tiles = []
for i in range(4):
    tile = Tile(10 + i, 4 + i)
    tile.draw('blue')
    blue_tiles.append(tile)
for i in range(4):
    tile = Tile(14 - i, 4 + i)
    tile.draw('blue')
    blue_tiles.append(tile)
blue_circle = Shape(blue_tiles)


import os
image = os.path.dirname(__file__).split('\\')[-1]
variation = os.path.basename(__file__).split('.')[0]
HexagonsGame.plot(gold_boards=None, multiple=0,file_name=f'{image}-{variation}')
