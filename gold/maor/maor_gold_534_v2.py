# Created by maor

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle

task_index = 534
gold_boards = list(read_task(task_index)['gold_boards'])

with Game() as g:
    
    # description:
    # task index: 534, image: P01C04T04, collection round: 0, category: conditions, group: train
    # agreement scores: [[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [0.99, 1.0, 0.99], [0.96, 1.0, 0.96], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0]]
    
    '''
    1. Color tiles 2 through 5 in column 1 purple.
    '''
    g.record_step(step_name='1')
    for r in range(2,6):
      tile=Tile(column=1, row=r)
      tile.draw('purple')
    g.record_step(step_name='1_end')
    '''
    2. Repeat step 1 in columns 9, 13, 15 and 17.
    '''
    shape = g.get_record(step_names=['1'])
    for c in [9,13,15,17]:
      shape.copy_paste(source=Tile(1,2), destination=Tile(c,2))
    
    '''
    3. Color tiles 2 through 5 in column 3 blue.
    '''
    g.record_step(step_name='3')
    for r in range(2,6):
      tile=Tile(column=3, row=r)
      tile.draw('blue')
    g.record_step(step_name='3_end')
    
    '''
    4. Repeat step 3 in columns 5, 7 and 11.
    '''
    shape = g.get_record(step_names=['3'])
    for c in [3,5,7,11]:
      shape.copy_paste(source=Tile(3,2), destination=Tile(c,2))
    
    '''
    5. Color the tile above each purple column orange.
    '''
    Shape.get_color('purple').neighbor(direction='up').draw('orange')
    
    '''
    6. Color the tile above each blue column green.
    '''
    Shape.get_color('blue').neighbor(direction='up').draw('green')
    
    '''
    7. Color tiles 6 through 9 in column 2 blue and then tile 10 green.
    '''
    g.record_step(step_name='7')
    for r in range(6,10):
      tile=Tile(column=2, row=r)
      tile.draw('blue')
    
    tile=Tile(column=2, row=10)
    tile.draw('green')
    
    g.record_step(step_name='7_end')
    
    '''
    8. Repeat step 7 for columns 6, 8, 16 and 18.
    '''
    shape = g.get_record(step_names=['7'])
    
    for c in [6,8,16,18]:
      shape.copy_paste(source=Tile(column=2,row=6), destination=Tile(column=c, row=6))
    
    '''
    9. Color tiles 6 through 9 in column 4 purple and then tile 10 orange.
    '''
    g.record_step(step_name='9')
    for r in range(6,10):
      tile=Tile(column=4, row=r)
      tile.draw('purple')
    
    tile=Tile(column=4, row=10)
    tile.draw('orange')
    
    g.record_step(step_name='9_end')
    
    '''
    10. Repeat step 9 for columns 10, 12 and 14.
    '''
    shape = g.get_record(step_names=['9'])
    
    for c in [10,12,14]:
      shape.copy_paste(source=Tile(column=4,row=6), destination=Tile(column=c, row=6))
    
    g.plot(gold_boards=gold_boards, multiple=0)
