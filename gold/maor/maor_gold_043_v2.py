# Created by maor

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle

task_index = 43
gold_boards = list(read_task(task_index)['gold_boards'])

with Game() as g:
    
    # description:
    # task index: 43, image: P01C02T12, collection round: 1, category: bounded iteration, group: train
    # agreement scores: [[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0]]
    
    '''
    1. With red, paint the cell at the 1st column on the left and 2nd row from top.
    '''
    tile1 = Tile(row=2, column=1)
    tile1.draw('red')
    
    '''
    2. With red, paint the top 2 cells of the 2nd column from left.
    '''
    tile2 = Tile(row=1, column=2)
    tile2.draw('red')
    tile3 = Tile(row=2, column=2)
    tile3.draw('red')
    
    '''
    3. With red, paint the top 3 rows of the 3rd column from the left.
    '''
    tile4 = Tile(row=1, column=3)
    tile4.draw('red')
    tile5 = Tile(row=2, column=3)
    tile5.draw('red')
    tile6 = Tile(row=3, column=3)
    tile6.draw('red')
    
    '''
    4. Repeat the triangle pattern 3 more times to the right of the 1st triangle,
    making sure to leave one empty column between each triangle.
    '''
    shape = Shape([tile1, tile2, tile3, tile4, tile5, tile6])
    shape.grid(shift_direction='right', spacing=1, num_copies=3)
    
    g.plot(gold_boards=gold_boards, multiple=0)
