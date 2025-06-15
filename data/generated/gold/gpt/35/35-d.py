# Created by chat gpt

from utils.reading_tasks import read_task
from hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle
from constants.constants import *

task_index = 35
gold_boards = list(read_task(task_index)['gold_boards'])

HexagonsGame.start()


# color all tiles orange around eighth vertical row from left, third tile from the top of that row
tile = Tile(5, 3)
shape = tile.neighbors()
shape.draw('orange')

# on 12th vertical row from left, 3rd tile down, color all tiles touching that tile, orange
tile = Tile(9, 3)
shape = tile.neighbors()
shape.draw('orange')

# on 8th vertical row 7th tile down, color all tiles touching that one orange, leaving it blank
tile = Tile(5, 7)
shape = tile.neighbors()
shape.draw('orange')
tile.draw('white')

# on 12th row, vertically from left, 7th tile down, color all tiles touching it orange, leaving it blank
tile = Tile(9, 7)
shape = tile.neighbors()
shape.draw('orange')
tile.draw('white')

# form a blue circle to fit in between the 4 orange circles drawn, of the same number of tiles, same size (six tiles, as in others)
tile = Tile(7, 5)
shape = tile.neighbors()
shape = shape.neighbors()
shape.draw('blue')

import os
HexagonsGame.plot(gold_boards=None, multiple=0,file_name=os.path.basename(__file__).split('.')[0])
