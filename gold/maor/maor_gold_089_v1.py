# Created by maor

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle

task_index = 89
gold_boards = list(read_task(task_index)['gold_boards'])

with Game() as g:
    
    # description:
    # task index: 89, image: P01C03T01, collection round: 1, category: conditional iteration, group: train
    # agreement scores: [[1.0, 1.0, 1.0], [1.0, 0.73, 0.73], [1.0, 0.19, 0.19]]
    
    '''
    1. On the bottom most row, paint the 8th tile green.
    '''
    tile=Tile(row=-1, column=8)
    tile.draw('green')
    
    '''
    2. Using the same color paint the next two tiles above it, and finish the vertical
    column of four tiles with the blue one.
    '''
    tile=Tile(row=-2, column=8)
    tile.draw('green')
    tile=Tile(row=-3, column=8)
    tile.draw('green')
    tile=Tile(row=-4, column=8)
    tile.draw('blue')
    
    '''
    3. Starting from the blue tile, paint the upper left and the upper right tiles
    green, and continue with the same pattern to create two diagonals until you
    reach the end of the grid on both sides.
    '''
    line1 = Line(start_tile=tile, direction='up_left', include_start_tile=False)
    line1.draw('green')
    
    line2 = Line(start_tile=tile, direction='up_right', include_start_tile=False)
    line2.draw('green')
    
    g.plot(gold_boards=gold_boards, multiple=0)
