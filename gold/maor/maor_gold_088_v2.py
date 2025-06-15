# Created by maor

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle

task_index = 88
gold_boards = list(read_task(task_index)['gold_boards'])

with Game() as g:
    
    # description:
    # task index: 88, image: P01C03T01, collection round: 1, category: conditional iteration, group: train
    # agreement scores: [[1, 1, 1], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0]]
    
    '''
    1. Locate the eighth column from the leftmost side.
    '''
    column = 8
    
    '''
    2. Starting from the bottom paint three tiles green in a vertical line.
    '''
    line1 = Line(start_tile=Tile(column=column, row=-3), direction='down')
    line1.draw('green')
    
    '''
    3. Paint the next tile above blue.
    '''
    tile = Tile(column=column, row=-4)
    tile.draw('blue')
    
    '''
    4. Draw a green diagonal line that goes from the left of the blue tile to the
    leftmost column.
    '''
    line2 = Line(start_tile=tile, direction='up_left', include_start_tile=False)
    line2.draw('green')
    
    '''
    5. Draw a green diagonal line that goes from the right of the blue tile to the
    rightmost column.
    '''
    line3 = Line(start_tile=tile, direction='up_right', include_start_tile=False)
    line3.draw('green')
    
    '''
    6. The drawing is complete, check to see if it resembles an asymmetrical Y shape.
    '''
    
    g.plot(gold_boards=gold_boards, multiple=0)
