# Created by maor

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle

task_index = 44
gold_boards = list(read_task(task_index)['gold_boards'])

with Game() as g:
    
    # description:
    # task index: 44, image: P01C02T12, collection round: 1, category: bounded iteration, group: train
    # agreement scores: [[0.5, 0.67, 0.67], [0.62, 0.62, 1.0]]
    
    '''
    1. Make a triangle from 9 red tiles, longest side is on the third row from the
    left, starting at the top downwards, the long side will have 3 tiles.
    '''
    start_tile = Tile(1, 2)
    triangle = Triangle(start_tile=start_tile, point='left', start_tile_type='side', side_length=3)
    triangle.draw('red')
    
    '''
    2. repeat the red triangle with same orientation starting with one vertical white
    row between the triangles. Do this to make a total of 4 red triangles. For
    clarity and reference, the longest rows (3 tiles each) are vertical (from left
    to right) 3, 7, 11, 15.
    '''
    for r in [3,7,11,15]:
      start_tile = Tile(r-2, 2)
      triangle = Triangle(start_tile=start_tile, point='left', start_tile_type='side', side_length=3)
      triangle.draw('red')
    
    g.plot(gold_boards=gold_boards, multiple=0)
