# Created by maor

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle

task_index = 555
gold_boards = list(read_task(task_index)['gold_boards'])

with Game() as g:
    
    # description:
    # task index: 555, image: P01C04T20, collection round: 0, category: conditions, group: train
    # agreement scores: [[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 0.69, 0.69], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0]]
    
    '''
    1. Leave the first column from the left blank, and paint the first three tiles of
    the second and fourth columns and the first and fourth tile of the third column
    purple. Then paint the second and third tiles of the third column green.
    '''
    g.record_step(step_name='1')
    
    for column in [2,4]:
      line = Line(start_tile=Tile(row=1, column=column), length=3, direction='down')
      line.draw('purple')
    
    for row in [1,4]:
      tile = Tile(row=row, column=3)
      tile.draw('purple')
    
    for row in [2,3]:
      tile = Tile(row=row, column=3)
      tile.draw('green')
    
    g.record_step(step_name='1_end')
    
    '''
    2. Paint the seventh, eighth, and ninth tiles of the second and fourth columns from
    the left orange. Paint the seventh and tenth tiles of the third column from the
    left orange. Then paint the eighth tile of the third column green and the ninth
    tile of the third column blue.
    '''
    g.record_step(step_name='2')
    
    for row in [7, 8, 9]:
      for column in [2,4]:
        tile = Tile(row=row, column=column)
        tile.draw('orange')
    
    for row in [7,10]:
      tile = Tile(row=row, column=3)
      tile.draw('orange')
    
    tile = Tile(row=8, column=3)
    tile.draw('green')
    
    tile = Tile(row=9, column=3)
    tile.draw('blue')
    
    g.record_step(step_name='2_end')
    
    '''
    3. Leave the fifth column from the left blank. Starting from the top of the sixth
    column make the same shape as the one from Step 2.
    '''
    shape = g.get_record(step_names=['2'])
    shape.copy_paste(source=shape[0], destination=Tile(1, 6))
    
    '''
    4. On the seventh tile of the sixth column from the left, make the same shape as
    the one from Step 1.
    '''
    shape = g.get_record(step_names=['1'])
    shape.copy_paste(source=shape[0], destination=Tile(7, 6))
    
    '''
    5. Leave the ninth column blank, and paint the same zero shape in orange starting
    on the first tile of tenth column from the left. This time, paint the second
    tile on the eleventh column blue and the third tile green.
    '''
    shape = g.get_record(step_names=['2'])
    shape.copy_paste(source=shape[0], destination=Tile(1, 10))
    
    tile = Tile(row=2, column=11)
    tile.draw('blue')
    
    tile = Tile(row=3, column=11)
    tile.draw('green')
    '''
    6. Paint a purple zero shape like the ones from Step 1 and 4 starting on seventh
    tile of the tenth column from the left. Paint the two tiles inside the zero
    blue.
    '''
    shape = g.get_record(step_names=['1'])
    shape.copy_paste(source=shape[0], destination=Tile(7, 10))
    tile = Tile(8, 11)
    tile.draw('blue')
    tile = Tile(9, 11)
    tile.draw('blue')
    
    '''
    7. Leave the thirteenth column from the left blank, and paint a purple zero shape
    starting on the first tile of the fourteenth column. Paint the tiles inside of
    the zero blue.
    '''
    shape = g.get_record(step_names=['1'])
    shape.copy_paste(source=shape[0], destination=Tile(1, 14))
    tile = Tile(2, 15)
    tile.draw('blue')
    tile = Tile(3, 15)
    tile.draw('blue')
    
    '''
    8. Paint another purple zero starting on the seventh tile of the fourteenth column
    from the left. Paint the tiles inside the zero green.
    '''
    shape = g.get_record(step_names=['1'])
    shape.copy_paste(source=shape[0], destination=Tile(7, 14))
    tile = Tile(8, 15)
    tile.draw('green')
    tile = Tile(9, 15)
    tile.draw('green')
    
    '''
    9. Leave the seventeenth and eighteenth columns blank.
    '''
    
    g.plot(gold_boards=gold_boards, multiple=0)
