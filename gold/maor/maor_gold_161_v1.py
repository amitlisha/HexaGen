# Created by maor

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle

task_index = 161
gold_boards = list(read_task(task_index)['gold_boards'])

with Game() as g:
    
    # description:
    # task index: 161, image: P01C04T02, collection round: 1, category: conditions, group: train
    # agreement scores: [[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 0.83, 0.83]]
    
    '''
    1. Use purple to shade the 3rd spot in the 2nd column, 6th spot in the 6th column,
    9th spot in the 10th column, and the 3rd spot in the 14th column.
    '''
    for tile in [Tile(3, 2), Tile(6, 6), Tile(9, 10), Tile(3, 14)]:
      tile.draw('purple')
    
    '''
    2. Use blue to shade the 6th spot in the 2nd column, 9th spot in the 6th column,
    3rd spot in the 10th column, and 6th spot in the 14th column.
    '''
    for tile in [Tile(6, 2), Tile(9, 6), Tile(3, 10), Tile(6, 14)]:
      tile.draw('blue')
    
    '''
    3. Use orange to shade the 9th spot in the 2nd column, 3rd spot in the 6th column,
    6th spot in the 10th column, and 9th spot in the 14th column.
    '''
    for tile in [Tile(9, 2), Tile(3, 6), Tile(6, 10), Tile(9, 14)]:
      tile.draw('orange')
    
    '''
    4. Encircle the purple dots with orange, blue dots with purple, and orange dots
    with blue.
    '''
    purples = Shape.get_color('purple')
    blues = Shape.get_color('blue')
    oranges = Shape.get_color('orange')
    
    purples.neighbors().draw('orange')
    blues.neighbors().draw('purple')
    oranges.neighbors().draw('blue')
    
    g.plot(gold_boards=gold_boards, multiple=0)
