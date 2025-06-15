# Created by chat gpt

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle
from constants.constants import *

task_index = 35
gold_boards = list(read_task(task_index)['gold_boards'])

with Game() as g:
    
    # Color all tiles orange around eighth vertical row from left, third tile from the top of that row, resulting in an orange circle there.
    tile = Tile(8, 3)
    shape = tile.neighbors().neighbors().draw('orange')
    
    # On 12th vertical row from left, 3rd tile down, color all tiles touching that tile, orange.
    tile = Tile(12, 3)
    shape = tile.neighbors().draw('orange')
    
    # On 8th vertical row 7th tile down, color all tiles touching that one orange, leaving it blank (as in other steps).
    tile = Tile(8, 7)
    shape = tile.neighbors().draw('orange')
    
    # on 12th row, vertically from left, 7th tile down, color all tiles touching it orange, leaving it blank.
    tile = Tile(12, 7)
    shape = tile.neighbors().draw('orange')
    
    # form a blue circle to fit in between the 4 orange circles drawn, of the same number of tiles, same size (six tiles, as in others).
    tile = Tile(10, 5)
    shape = tile.neighbors().neighbors().neighbors().neighbors().draw('blue')
    
    import os
    g.plot(gold_boards=None, multiple=0,file_name=os.path.basename(__file__).split('.')[0])
