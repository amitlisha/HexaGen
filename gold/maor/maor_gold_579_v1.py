# Created by maor

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle

task_index = 579
gold_boards = list(read_task(task_index)['gold_boards'])

with Game() as g:
    
    # description:
    # task index: 579, image: P01C04T04, collection round: 0, category: conditions, group: train
    # agreement scores: [[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 0.57, 0.57], [1.0, 0.67, 0.67], [1.0, 0.76, 0.76], [1.0, 0.8, 0.8]]
    
    '''
    1. On the leftmost column, paint the top tile orange and the four tiles below it
    purple.
    '''
    tile = Tile(column=1, row=1)
    tile.draw('orange')
    
    line = Line(start_tile=tile, direction='down', length=4, include_start_tile=False)
    line.draw('purple')
    
    '''
    2. On the next column, paint the bottom tile green and the four tiles above it
    blue.
    '''
    tile = Tile(column=line.end_tile.neighbor('down_right').column, row=-1)
    tile.draw('green')
    
    line = Line(start_tile=tile, direction='up', length=4, include_start_tile=False)
    line.draw('blue')
    
    '''
    3. On the next column, paint the top tile green and the four tiles below it blue.
    '''
    tile = Tile(column=line.end_tile.neighbor('down_right').column, row=1)
    tile.draw('green')
    
    line = Line(start_tile=tile, direction='down', length=4, include_start_tile=False)
    line.draw('blue')
    
    '''
    4. On the next column, paint the bottom tile orange and the four tiles above it
    purple.
    '''
    tile = Tile(column=line.end_tile.neighbor('down_right').column, row=-1)
    tile.draw('orange')
    
    line = Line(start_tile=tile, direction='up', length=4, include_start_tile=False)
    line.draw('purple')
    
    '''
    5. Paint the fifth, seventh, and eleventh columns from the left as you painted the
    third column from the left.
    '''
    pattern = Shape.get_column(3)
    for c in [5, 7, 11]:
      pattern.copy_paste(source=Tile(3,1), destination=Tile(c,1))
    
    '''
    6. Paint the second, fourth, sixth, and tenth columns from the right as you painted
    the leftmost column.
    '''
    pattern = Shape.get_column(1)
    for c in [-2, -4, -6, -10]:
      pattern.copy_paste(source=Tile(1,1), destination=Tile(c,1))
    
    '''
    7. Paint the sixth, eighth, sixteenth, and last columns from the left as you
    painted the second column from the left.
    '''
    pattern = Shape.get_column(2)
    for c in [6, 8, 16, -1]:
      pattern.copy_paste(source=Tile(2,1), destination=Tile(c,1))
    
    '''
    8. Paint the fifth, seventh, and ninth columns from the right as you painted the
    fourth column from the left.
    '''
    pattern = Shape.get_column(4)
    for c in [-5, -7, -9]:
      pattern.copy_paste(source=Tile(4,1), destination=Tile(c,1))
    
    g.plot(gold_boards=gold_boards, multiple=0)
