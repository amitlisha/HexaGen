# Created by maor

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle

task_index = 42
gold_boards = list(read_task(task_index)['gold_boards'])

with Game() as g:
    
    # description:
    # task index: 42, image: P01C02T12, collection round: 1, category: bounded iteration, group: train
    # agreement scores: [[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0]]
    
    '''
    1. Fill the top three hexes in the 3rd column from the left with red.
    '''
    line = Line(start_tile=Tile(3,1), direction='down', length=3)
    line.draw('red')
    '''
    2. Fill 3 hexes to the left with red to form a triangle pointing left.
    '''
    triangle = Triangle(start_tile=Tile(1, 2), point='left', start_tile_type='side', side_length=2)
    triangle.draw('red')
    
    '''
    3. Repeat this triangle shape 3 times in red, at the same vertical height but with
    a empty column between the base of each triangle and the point of the next
    triangle. The 3 columns on the far right should remain empty.
    '''
    shape = line + triangle
    
    for i in range(3):
      shape = shape.copy_paste(shift_direction='right', spacing=1)
    
    g.plot(gold_boards=gold_boards, multiple=0)
