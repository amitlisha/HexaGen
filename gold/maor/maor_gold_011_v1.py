# Created by maor

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle

task_index = 11
gold_boards = list(read_task(task_index)['gold_boards'])

with Game() as g:
    
    # description:
    # task index: 11, image: P01C01T09, collection round: 1, category: simple, group: train
    # agreement scores: [[1.0, 1.0, 1.0], [1.0, 1.0, 1.0]]
    
    '''
    1. Color the 5th tile from the top of the 9th column from the left PURPLE.
    '''
    tile = Tile(row=5, column=9)
    tile.draw('purple')
    
    '''
    2. Color all tiles adjacent to this tile GREEN.
    '''
    tile.neighbors().draw('green')
    
    g.plot(gold_boards=gold_boards, multiple=0)
