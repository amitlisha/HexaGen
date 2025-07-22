# Created by maor

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle

task_index = 87
gold_boards = list(read_task(task_index)['gold_boards'])

with Game() as g:
    
    # description:
    # task index: 87, image: P01C03T01, collection round: 1, category: conditional iteration, group: train
    # agreement scores: [[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0]]
    
    '''
    1. Paint the cell located at the 8th column from the left and 4th row from the
    bottom with blue.
    '''
    tile1=Tile(row=-4, column=8)
    tile1.draw('blue')
    
    '''
    2. Paint the 3 cells below the blue cell with green.
    '''
    line1 = Line(start_tile=tile1, length=3, direction='down', include_start_tile=False)
    line1.draw('green')
    
    '''
    3. Paint the cell located at the 1st column on left and the 4th row from top with
    green.
    '''
    tile2=Tile(row=4, column=1)
    tile2.draw('green')
    
    '''
    4. Paint a straight line between the green cell from step 3 with the blue cell with
    green paint.
    '''
    line2 = Line(start_tile=tile1, end_tile=tile2, include_end_tile=False, include_start_tile=False)
    line2.draw('green')
    
    '''
    5. Paint the cell located at the 1st column on right and the 2nd row from top with
    green.
    '''
    tile3=Tile(row=2, column=-1)
    tile3.draw('green')
    
    '''
    6. Paint a straight line between the green cell from step 5 with the blue cell with
    green paint.
    '''
    line3 = Line(start_tile=tile1, end_tile=tile3, include_end_tile=False, include_start_tile=False)
    line3.draw('green')
    
    g.plot(gold_boards=gold_boards, multiple=0)
