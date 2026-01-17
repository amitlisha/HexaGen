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
    g.record_step(step_name='flower')
    tile1 = Tile(row=2, column=2)
    tile1.neighbors().draw('purple')
    
    '''
    2. In the 4th column, the 2nd tile from the top is orange. In the 5th column, the
    2nd and 3rd tile from the top are orange. In the 6th column the topmost 3 are
    colored orange. This makes a Triangle.
    '''
    g.record_step(step_name='triangle')
    for tile in [Tile(2, 4), Tile(2, 5), Tile(3, 5), Tile(1, 6), Tile(2, 6), Tile(3, 6)]:
      tile.draw('orange')
    
    '''
    3. Repeat this pattern all the way across to the right. It should be purple flower,
    orange triangle, purple flower, orange triangle, purple flower, orange triangle.
    Do not skip a column.
    '''
    g.record_step(step_name='row')
    
    flower = g.get_record(step_names=['flower'])
    triangle = g.get_record(step_names=['triangle'])
    
    for i in range(3):
      flower = flower.copy_paste(shift_direction='right', spacing=3)
      triangle = triangle.copy_paste(shift_direction='right', spacing=3)
    
    g.record_step(step_name='row_end')
    '''
    4. In the 2nd column from the left the 5th tile from the top will be blank. This is
    the starting point for the 2nd row of flowers and triangles. It is identical to
    the one above it.
    '''
    row = g.get_record(step_names=['flower', 'triangle', 'row'])
    row = row.copy_paste(shift_direction='down', spacing=0)
    
    '''
    5. In the 2nd column from the left the 3rd tile from the bottom will be blank. This
    is the starting point for the 3rd row of flowers and triangles. It is identical
    to the one above it.
    '''
    row.copy_paste(shift_direction='down', spacing=0)
    
    g.plot(gold_boards=gold_boards, multiple=0)
