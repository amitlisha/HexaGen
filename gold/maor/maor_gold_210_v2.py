# Created by maor

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle

task_index = 210
gold_boards = list(read_task(task_index)['gold_boards'])

with Game() as g:
    
    # description:
    # task index: 210, image: P01C07T10, collection round: 1, category: composed objects, group: train
    # agreement scores: [[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [0.5, 0.5, 1.0]]
    
    '''
    1. Make a purple circle with a center at the second tile of the second column.
    Leave the center blank.
    '''
    g.record_step(step_name='1')
    circle = Circle(center_tile=Tile(2,2))
    circle.draw('purple')
    
    '''
    2. Make a triangle pointing left with six colored orange tiles, with the leftmost
    point touching the right side of the purple circle.
    '''
    triangle = Triangle(start_tile=Tile(4,2), point='left', start_tile_type='side', side_length=3)
    triangle.draw('orange')
    
    '''
    3. Copy this pattern to the right and down leaving no spaces between the shapes.
    '''
    pattern = g.get_record(step_names=['1'])
    down_copy = pattern.grid(shift_direction='down', spacing=0)
    down_copy.grid(shift_direction='right', spacing=0)
    
    g.plot(gold_boards=gold_boards, multiple=0)
