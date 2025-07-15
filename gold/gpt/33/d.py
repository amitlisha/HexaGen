# Created by chat gpt

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle
from constants.constants import *

with Game() as g:
    
    # Define the colors that we'll use
    ORANGE = COLORS[7]
    BLUE = COLORS[5]
    
    # Color all tiles orange around eighth vertical row from left, third tile from the top of that row
    tile1 = Tile(3, -6)
    shape1 = tile1.neighbors().neighbors().neighbors().neighbors().neighbors()
    shape1.draw(ORANGE)
    
    # On 12th vertical row from left, 3rd tile down, color all tiles touching that tile, orange
    tile2 = Tile(12, 3)
    shape2 = tile2.neighbors().neighbors().neighbors().neighbors().neighbors().neighbors().neighbors().neighbors()
    shape2.draw(ORANGE)
    
    # On 8th vertical row 7th tile down, color all tiles touching that one orange, leaving it blank
    tile3 = Tile(7, -6)
    shape3 = tile3.neighbors().neighbors().neighbors().neighbors().neighbors().neighbors().neighbors()
    shape3.draw(ORANGE)
    tile3.draw('white')
    
    # on 12th row, vertically from left, 7th tile down, color all tiles touching it orange, leaving it blank
    tile4 = Tile(12, 7)
    shape4 = tile4.neighbors().neighbors().neighbors().neighbors().neighbors().neighbors().neighbors()
    shape4.draw(ORANGE)
    tile4.draw('white')
    
    # form a blue circle to fit in between the 4 orange circles drawn, of the same number of tiles, same size
    tile5 = Tile(7, -3)
    shape5 = tile5.neighbors().neighbors().neighbors().neighbors().neighbors().neighbors()
    shape5.draw(BLUE)
    
    
    import os
    image = os.path.dirname(__file__).split('\\')[-1]
    variation = os.path.basename(__file__).split('.')[0]
    g.plot(gold_boards=None, multiple=0,file_name=f'{image}-{variation}')
