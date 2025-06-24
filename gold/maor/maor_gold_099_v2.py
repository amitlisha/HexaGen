# Created by maor

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle

task_index = 99
gold_boards = list(read_task(task_index)['gold_boards'])

with Game() as g:
    
    # description:
    # task index: 99, image: P01C03T05, collection round: 1, category: conditional iteration, group: train
    # agreement scores: [[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [0.62, 0.14, 0.14]]
    
    '''
    1. Fill the 4th spot of the 7th column with orange.
    '''
    tile1 = Tile(column=7, row=4)
    tile1.draw('orange')
    
    '''
    2. circle around that with red.
    '''
    circle = Circle(center_tile=tile1, radius=1)
    circle.draw('red')
    
    '''
    3. Make diagonal lines that alternate red and yellow out from every spot
    surrounding the orange spot.
    '''
    from constants.constants import DIRECTIONS, WIDTH, HEIGHT
    
    for d in DIRECTIONS:
      tile2 = tile1.neighbor(direction=d)
      while tile2.row in range(1, HEIGHT+1) and tile2.column in range(1, WIDTH+1):
          tile2.draw('red')
          tile2 = tile2.neighbor(direction=d)
          tile2.draw('yellow')
          tile2 = tile2.neighbor(direction=d)
    
    g.plot(gold_boards=gold_boards, multiple=0)
