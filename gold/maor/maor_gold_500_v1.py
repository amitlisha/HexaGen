# Created by maor

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle

task_index = 500
gold_boards = list(read_task(task_index)['gold_boards'])

with Game() as g:
    
    # description:
    # task index: 500, image: P01C01T09, collection round: 0, category: simple, group: train
    # agreement scores: [[1.0, 1.0, 1.0], [0.83, 1.0, 0.83]]
    
    '''
    1. Draw a single purple tile in column 9, five tiles down.
    '''
    tile = Tile(9, 5)
    tile.draw('purple')
    
    '''
    2. Fill in green all tiles adjacent to the purple tile.
    '''
    tile.neighbors().draw('green')
    
    g.plot(gold_boards=gold_boards, multiple=0)
