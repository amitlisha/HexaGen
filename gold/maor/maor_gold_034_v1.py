# Created by maor

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle

task_index = 34
gold_boards = list(read_task(task_index)['gold_boards'])

with Game() as g:
    
    # description:
    # task index: 34, image: P01C02T09, collection round: 1, category: bounded iteration, group: train
    # agreement scores: [[1.0, 1.0, 1.0], [1.0, 0.87, 0.87]]
    
    '''
    1. Make a blue flower of six tiles surrounding the fifth tile in the tenth column.
    '''
    tile = Tile(column=10, row=5)
    tile.neighbors().draw('blue')
    
    '''
    2. Make four orange flowers connecting to the original on the outermost corners,
    leaving a white tile between each orange flower.
    '''
    for row in [3,7]:
      for column in [8,12]:
        tile = Tile(column, row)
        tile.neighbors().draw('orange')
    g.plot(gold_boards=gold_boards, multiple=0)
