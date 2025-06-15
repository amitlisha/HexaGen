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
    g.record_step('1')
    tile = Tile(column=1, row=1)
    tile.draw('orange')
    
    for i in range(4):
      tile = tile.neighbor('down')
      tile.draw('purple')
    g.record_step('1_end')
    
    '''
    2. On the next column, paint the bottom tile green and the four tiles above it
    blue.
    '''
    g.record_step('2')
    tile = Tile(column=tile.neighbor('down_right').column, row=-1)
    tile.draw('green')
    
    for i in range(4):
      tile = tile.neighbor('up')
      tile.draw('blue')
    g.record_step('2_end')
    '''
    3. On the next column, paint the top tile green and the four tiles below it blue.
    '''
    g.record_step('3')
    tile = Tile(column=tile.neighbor('up_right').column, row=1)
    tile.draw('green')
    
    for i in range(4):
      tile = tile.neighbor('down')
      tile.draw('blue')
    g.record_step('3_end')
    '''
    4. On the next column, paint the bottom tile orange and the four tiles above it
    purple.
    '''
    g.record_step('4')
    tile = Tile(column=tile.neighbor('up_right').column, row=-1)
    tile.draw('orange')
    
    for i in range(4):
      tile = tile.neighbor('up')
      tile.draw('purple')
    g.record_step('4_end')
    '''
    5. Paint the fifth, seventh, and eleventh columns from the left as you painted the
    third column from the left.
    '''
    pattern = g.get_record(['3'])
    r = pattern.edge('top').row
    for c in [5, 7, 11]:
      pattern.copy_paste(source=pattern.edge('top'), destination=Tile(c,r))
    
    '''
    6. Paint the second, fourth, sixth, and tenth columns from the right as you painted
    the leftmost column.
    '''
    pattern = g.get_record(['1'])
    r = pattern.edge('top').row
    for c in [-2, -4, -6, -10]:
      pattern.copy_paste(source=pattern.edge('top'), destination=Tile(c,r))
    
    '''
    7. Paint the sixth, eighth, sixteenth, and last columns from the left as you
    painted the second column from the left.
    '''
    pattern = g.get_record(['2'])
    r = pattern.edge('top').row
    for c in [6, 8, 16, -1]:
      pattern.copy_paste(source=pattern.edge('top'), destination=Tile(c,r))
    
    '''
    8. Paint the fifth, seventh, and ninth columns from the right as you painted the
    fourth column from the left.
    '''
    pattern = g.get_record(['4'])
    r = pattern.edge('top').row
    for c in [-5, -7, -9]:
      pattern.copy_paste(source=pattern.edge('top'), destination=Tile(c,r))
    
    g.plot(gold_boards=gold_boards, multiple=0)
