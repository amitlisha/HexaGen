# Created by by maor

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle

task_index = 10
gold_boards = list(read_task(task_index)['gold_boards'])

with Game() as g:
    
    # description:
    # task index: 10, image: P01C01T09, collection round: 1, category: simple, group: train
    # agreement scores: [[1.0, 1.0, 1.0], [1.0, 1.0, 1.0]]
    
    '''
    1. With purple, paint the cell located at the 9th column from left and 5th row from
    top.
    '''
    tile = Tile(row=5, column=9)
    tile.draw('purple')
    
    '''
    2. With green, paint the 6 cells around the purple cell in step 1.
    '''
    tile.neighbors().draw('green')
    
    g.plot(gold_boards=gold_boards, multiple=0)
