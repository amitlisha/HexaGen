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
    colors = ['orange','green','green','green','orange','green','orange','orange','orange']
    columns = range(1,19,2)
    for i in range(9):
      tile = Tile(row=1, column=columns[i])
      tile.draw(colors[i])
    
    '''
    2. For the columns with an orange top hexagon, color the 2nd, 3rd, 4th, and 5th
    columns from the top purple.
    '''
    for i in range(9):
      if colors[i] == 'orange':
        for r in [2,3,4,5]:
          tile=Tile(row=r, column=columns[i])
          tile.draw('purple')
    
    '''
    3. For the columns with a green top hexagon, color the 2nd, 3rd, 4th, and 5th
    columns from the top blue.
    '''
    for i in range(9):
      if colors[i] == 'green':
        for r in [2,3,4,5]:
          tile=Tile(row=r, column=columns[i])
          tile.draw('blue')
    
    '''
    4. Now starting from the bottom RIGHT corner, color the bottom hexagon of every
    other column in the following order (RIGHT TO LEFT): green, green, orange,
    orange, orange, green, green, orange, green. Note that these should not be in
    the same columns where there are already colored hexagons present.
    '''
    columns = range(18,0,-2)
    colors = ['green', 'green', 'orange', 'orange', 'orange', 'green', 'green', 'orange', 'green']
    
    for i in range(9):
      tile = Tile(row=-1, column=columns[i])
      tile.draw(colors[i])
    
    '''
    5. For the columns with an orange bottom hexagon, color the 2nd, 3rd, 4th, and 5th
    columns from the bottom purple.
    '''
    for i in range(9):
      if colors[i] == 'orange':
        for r in [-2,-3,-4,-5]:
          tile=Tile(row=r, column=columns[i])
          tile.draw('purple')
    
    '''
    6. For the columns with a green bottom hexagon, color the 2nd, 3rd, 4th, and 5th
    columns from the bottom blue.
    '''
    for i in range(9):
      if colors[i] == 'green':
        for r in [-2,-3,-4,-5]:
          tile=Tile(row=r, column=columns[i])
          tile.draw('blue')
    
    g.plot(gold_boards=gold_boards, multiple=0)
