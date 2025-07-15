# Created by maor

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle

task_index = 0
gold_boards = list(read_task(task_index)['gold_boards'])

with Game() as g:
    
    # description:
    # task index: 0, image: P01C01T05, collection round: 1, category: simple, group: train
    # agreement scores: [[1.0, 0, 0], [1.0, 0.43, 0.43], [1.0, 0.44, 0.44]]
    
    '''
    1. Start by coloring the tile in the sixth column, fifth from the top red.
    '''
    tile = Tile(5, 6)
    tile.draw('red')
    
    '''
    2. Create a less-than sign (<) using the original tile as the left-most point,
    and coloring three more tiles red for each the top and bottom parts of the less-than sign.
         
    '''
    line_up = Line(start_tile = tile, direction = 'up_right', length = 3, include_start_tile=False)
    line_up.draw('red')
    
    line_down = Line(start_tile = tile, direction = 'down_right', length = 3, include_start_tile=False)
    line_down.draw('red')
    
    '''
    3. Add two more red tiles to connect the ends of the less-than sign. 
    The result will be a red triangle.
    '''
    line = Line(start_tile=line_up.end_tile, end_tile=line_down.end_tile)
    line.draw('red')
    
    g.plot(gold_boards=gold_boards, multiple=0)
