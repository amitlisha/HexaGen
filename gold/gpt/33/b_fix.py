# Created by chat gpt

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle
from constants.constants import *

with Game() as g:
    
    orange_tiles1 = Shape([Tile(8, 3).neighbor(d) for d in DIRECTIONS]).draw('orange')
    g.record_step("Step 1")
    # save the orange tiles in the record
    
    # On 12th vertical row from left, 3rd tile down, color all tiles touching that tile, orange.
    orange_tiles2 = Tile(12, 3).neighbors().draw('orange')
    g.record_step("Step 2")
    # save the orange tiles in the record
    
    # On 8th vertical row 7th tile down, color all tiles touching that one orange, leaving it blank (as in other steps).
    Shape([Tile(8, 7)] + Tile(8, 7).neighbors().tiles).draw('orange')
    Tile(8, 7).draw('white')  # leave tile 8, 7 blank
    g.record_step("Step 3")
    # save the orange tiles and the blank tile in the record
    
    # on 12th row, vertically from left, 7th tile down, color all tiles touching it orange, leaving it blank.
    Shape([Tile(12, 7)] + Tile(12, 7).neighbors().tiles).draw('orange')
    Tile(12, 7).draw('white')  # leave tile 12, 7 blank
    g.record_step("Step 4")
    # save the orange tiles and the blank tile in the record
    
    # form a blue circle to fit in between the 4 orange circles drawn, of the same number of tiles, same size (six tiles, as in others).
    blue_tiles = Shape([Tile(10, 5).neighbor(d) for d in DIRECTIONS]).draw('blue')
    g.record_step("Step 5")
    # save the blue tiles in the record
    
    import os
    image = os.path.dirname(__file__).split('\\')[-1]
    variation = os.path.basename(__file__).split('.')[0]
    g.plot(gold_boards=None, multiple=0,file_name=f'{image}-{variation}')
