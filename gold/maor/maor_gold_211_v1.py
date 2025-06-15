# Created by maor

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle

task_index = 211
gold_boards = list(read_task(task_index)['gold_boards'])

with Game() as g:
    
    # description:
    # task index: 211, image: P01C07T10, collection round: 1, category: composed objects, group: train
    # agreement scores: [[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 0.86, 0.86], [1.0, 0.67, 0.67]]
    
    '''
    1. This will be a pattern that repeats itself on different rows. Starting in the
    2nd column from the left, the 2nd tile down will be blank. The 6 tiles
    surrounding this blank tile will be purple. This makes a flower.
    '''
    g.record_step(step_name='1')
    tile1 = Tile(column=2, row=2)
    tile1.neighbors().draw('purple')
    
    '''
    2. In the 4th column, the 2nd tile from the top is orange. In the 5th column, the
    2nd and 3rd tile from the top are orange. In the 6th column the topmost 3 are
    colored orange. This makes a Triangle.
    '''
    tile2 = Tile(column=4, row=2)
    tile2.draw('orange')
    
    tile3 = Tile(column=5, row=2)
    tile3.draw('orange')
    
    tile4 = Tile(column=5, row=3)
    tile4.draw('orange')
    
    line = Line(start_tile=Tile(column=6, row=1), direction='down', length=3)
    line.draw('orange')
    
    '''
    3. Repeat this pattern all the way across to the right. It should be purple flower,
    orange triangle, purple flower, orange triangle, purple flower, orange triangle.
    Do not skip a column.
    '''
    pattern1 = g.get_record(step_names=['1'])
    pattern1.grid(shift_direction='right', spacing=0)
    
    '''
    4. In the 2nd column from the left the 5th tile from the top will be blank. This is
    the starting point for the 2nd row of flowers and triangles. It is identical to
    the one above it.
    '''
    pattern2 = pattern1.copy_paste(source=tile1, destination=Tile(column=2, row=5))
    pattern2.grid(shift_direction='right', spacing=0)
    
    '''
    5. In the 2nd column from the left the 3rd tile from the bottom will be blank. This
    is the starting point for the 3rd row of flowers and triangles. It is identical
    to the one above it.
    '''
    pattern3 = pattern1.copy_paste(source=tile1, destination=Tile(column=2, row=-3))
    pattern3.grid(shift_direction='right', spacing=0)
    
    g.plot(gold_boards=gold_boards, multiple=0)
