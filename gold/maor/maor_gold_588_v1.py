# Created by maor

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle

task_index = 588
gold_boards = list(read_task(task_index)['gold_boards'])

with Game() as g:
    
    # description:
    # task index: 588, image: P01C04T04, collection round: 0, category: conditions, group: train
    # agreement scores: [[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0]]
    
    '''
    1. Color tiles 2-5 purple in columns 1, 9, 13, 15, and 17. Also color tiles 6-9
    purple in columns 4, 10, 12, and 14.
    '''
    for c in [1,9, 13, 15, 17]:
      line = Line(start_tile=Tile(c, 2), end_tile=Tile(c, 5))
      line.draw('purple')
    
    for c in [4, 10, 12, 14]:
      line = Line(start_tile=Tile(c, 6), end_tile=Tile(c, 9))
      line.draw('purple')
    
    '''
    2. Color tiles 2-5 blue in columns 3, 5, 7, and 11. Also color tiles 6-9 blue in
    columns 2, 6, 8, 16, and 18.
    '''
    for c in [3, 5, 7, 11]:
      line = Line(start_tile=Tile(c, 2), end_tile=Tile(c, 5))
      line.draw('blue')
    
    for c in [2, 6, 8, 16, 18]:
      line = Line(start_tile=Tile(c, 6), end_tile=Tile(c, 9))
      line.draw('blue')
    
    '''
    3. Starting with column 1, color the first tile in every other column orange,
    EXCEPT columns 3, 5, 7, and 11, which you will color green. Starting with column
    2, color the last tile in every other column green, EXCEPT for columns 4, 10,
    12, and 14, which you will color orange.
    '''
    for i in range(1, 20, 2):
      tile = Tile(column=i, row=1)
      if i in [3, 5, 7, 11]:
        tile.draw('green')
      else:
        tile.draw('orange')
    
    for i in range(2, 20, 2):
      tile = Tile(column=i, row=-1)
      if i in [4, 10, 12, 14]:
        tile.draw('orange')
      else:
        tile.draw('green')
    
    g.plot(gold_boards=gold_boards, multiple=0)
