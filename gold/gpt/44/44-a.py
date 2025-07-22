# Created by chat gpt

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle
from constants.constants import *

task_index = 44
gold_boards = list(read_task(task_index)['gold_boards'])

with Game() as g:
    
    # Create the board
    board = [[None for j in range(WIDTH)] for i in range(HEIGHT)]
    
    # Create the red triangles
    red_tile = Tile(1, 9)
    red_tile.draw('red')
    red_tile.neighbor('down_right').draw('red')
    red_tile.neighbor('down_left').draw('red')
    
    red_tile2 = Tile(4, 2)
    red_tile2.draw('red')
    red_tile2.neighbor('down_right').draw('red')
    red_tile2.neighbor('down_left').draw('red')
    
    red_tile3 = Tile(4, 14)
    red_tile3.draw('red')
    red_tile3.neighbor('down_right').draw('red')
    red_tile3.neighbor('down_left').draw('red')
    
    red_tile4 = Tile(7, 7)
    red_tile4.draw('red')
    red_tile4.neighbor('down_right').draw('red')
    red_tile4.neighbor('down_left').draw('red')
    
    # Create the white tiles between the red triangles
    white_tile = Tile(2, 9)
    white_tile.draw('white')
    
    white_tile2 = Tile(5, 2)
    white_tile2.draw('white')
    
    white_tile3 = Tile(5, 14)
    white_tile3.draw('white')
    
    white_tile4 = Tile(8, 7)
    white_tile4.draw('white')
    
    # Record the red triangles as a step
    g.record_step('step1')
    Shape([red_tile, red_tile.neighbor('down_right'), red_tile.neighbor('down_left')]).draw('red')
    g.record_step('step2')
    Shape([red_tile2, red_tile2.neighbor('down_right'), red_tile2.neighbor('down_left')]).draw('red')
    g.record_step('step3')
    Shape([red_tile3, red_tile3.neighbor('down_right'), red_tile3.neighbor('down_left')]).draw('red')
    g.record_step('step4')
    Shape([red_tile4, red_tile4.neighbor('down_right'), red_tile4.neighbor('down_left')]).draw('red')
    
    import os
    g.plot(gold_boards=None, multiple=0,file_name=os.path.basename(__file__).split('.')[0])
