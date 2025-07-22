# Created by maor

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle

task_index = 546
gold_boards = list(read_task(task_index)['gold_boards'])

with Game() as g:
    
    # description:
    # task index: 546, image: P01C04T04, collection round: 0, category: conditions, group: train
    # agreement scores: [[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0]]
    
    '''
    1. Starting from the top left corner, color every other top hexagon per column in
    the following order (left to right): orange, green, green, green, orange, green,
    orange, orange, orange. You should have 9 colored hexagons total.
    '''
    column = 1
    for color in ['orange','green','green','green','orange','green','orange','orange','orange']:
      tile = Tile(row=1, column=column)
      tile.draw(color)
      column += 2
    
    '''
    2. For the columns with an orange top hexagon, color the 2nd, 3rd, 4th, and 5th
    columns from the top purple.
    '''
    for tile in Shape.get_color('orange').edge('up'):
      line = Line(start_tile=tile, direction='down', length=4, include_start_tile=False)
      line.draw('purple')
    
    '''
    3. For the columns with a green top hexagon, color the 2nd, 3rd, 4th, and 5th
    columns from the top blue.
    '''
    for tile in Shape.get_color('green').edge('up'):
      line = Line(start_tile=tile, direction='down', length=4, include_start_tile=False)
      line.draw('blue')
    
    '''
    4. Now starting from the bottom RIGHT corner, color the bottom hexagon of every
    other column in the following order (RIGHT TO LEFT): green, green, orange,
    orange, orange, green, green, orange, green. Note that these should not be in
    the same columns where there are already colored hexagons present.
    '''
    column = -1
    for color in ['green', 'green', 'orange', 'orange', 'orange', 'green', 'green', 'orange', 'green']:
      tile = Tile(row=-1, column=column)
      tile.draw(color)
      column -= 2
    
    '''
    5. For the columns with an orange bottom hexagon, color the 2nd, 3rd, 4th, and 5th
    columns from the bottom purple.
    '''
    for tile in Shape.get_color('orange').edge('down'):
      line = Line(start_tile=tile, direction='up', length=4, include_start_tile=False)
      line.draw('purple')
    
    '''
    6. For the columns with a green bottom hexagon, color the 2nd, 3rd, 4th, and 5th
    columns from the bottom blue.
    '''
    for tile in Shape.get_color('green').edge('down'):
      line = Line(start_tile=tile, direction='up', length=4, include_start_tile=False)
      line.draw('blue')
    
    g.plot(gold_boards=gold_boards, multiple=0)
