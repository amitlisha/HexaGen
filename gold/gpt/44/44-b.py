# Created by chat gpt

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle
from constants.constants import *

task_index = 44
gold_boards = list(read_task(task_index)['gold_boards'])

with Game() as g:
    
    # draw the first red triangle
    for i in range(3):
        Tile(i+1, i+6).draw('red')
    
    for i in range(2):
        Tile(i+2, i+7).draw('red')
    
    Tile(3, 8).draw('red')
    
    # create the red triangle shape and add white row
    red_triangle = Shape([Tile(i+1, i+6) for i in range(3)] +
                         [Tile(i+2, i+7) for i in range(2)] +
                         [Tile(3, 8)])
    
    white_row = Shape([Tile(4, i+6) for i in range(3)])
    
    # create 4 red triangles with white row in between
    for i in range(4):
        if i > 0:
            red_triangle.copy_paste('down', 4*i, reference_shape=white_row)
        red_triangle.copy_paste('down', 4*i)
        white_row.copy_paste('down', 4*i+3)
    
    import os
    g.plot(gold_boards=None, multiple=0,file_name=os.path.basename(__file__).split('.')[0])
