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
    
    line = Line(start_tile=Tile(column=2,row=1), length=3, direction='down')
    line.draw('purple')
    
    line = Line(start_tile=Tile(column=4,row=1), length=3, direction='down')
    line.draw('purple')
    
    tile = Tile(column=3, row=1)
    tile.draw('purple')
    
    tile = Tile(column=3, row=4)
    tile.draw('purple')
    
    tile = Tile(column=3, row=2)
    tile.draw('green')
    
    tile = Tile(column=3, row=3)
    tile.draw('green')
    
    g.record_step(step_name='1_end')
    
    '''
    2. Paint the seventh, eighth, and ninth tiles of the second and fourth columns from
    the left orange. Paint the seventh and tenth tiles of the third column from the
    left orange. Then paint the eighth tile of the third column green and the ninth
    tile of the third column blue.
    '''
    g.record_step(step_name='2')
    
    line = Line(start_tile=Tile(column=2, row=7), end_tile=Tile(column=2, row=9))
    line.draw('orange')
    
    line = Line(start_tile=Tile(column=4, row=7), end_tile=Tile(column=4, row=9))
    line.draw('orange')
    
    tile = Tile(column=3, row=7)
    tile.draw('orange')
    
    tile = Tile(column=3, row=10)
    tile.draw('orange')
    
    tile = Tile(column=3, row=8)
    tile.draw('green')
    
    tile = Tile(column=3, row=9)
    tile.draw('blue')
    
    g.record_step(step_name='2_end')
    
    '''
    3. Leave the fifth column from the left blank. Starting from the top of the sixth
    column make the same shape as the one from Step 2.
    '''
    shape = g.get_record(step_names=['2'])
    shape.copy_paste(source=shape[0], destination=Tile(6,1))
    
    '''
    4. On the seventh tile of the sixth column from the left, make the same shape as
    the one from Step 1.
    '''
    shape = g.get_record(step_names=['1'])
    shape.copy_paste(source=shape[0], destination=Tile(6,7))
    
    '''
    5. Leave the ninth column blank, and paint the same zero shape in orange starting
    on the first tile of tenth column from the left. This time, paint the second
    tile on the eleventh column blue and the third tile green.
    '''
    shape = g.get_record(step_names=['2'])
    shape = shape.copy_paste(source=shape[0], destination=Tile(10,1))
    
    tile = Tile(column=11, row=2)
    tile.draw('blue')
    
    tile = Tile(column=11, row=3)
    tile.draw('green')
    '''
    6. Paint a purple zero shape like the ones from Step 1 and 4 starting on seventh
    tile of the tenth column from the left. Paint the two tiles inside the zero
    blue.
    '''
    shape = g.get_record(step_names=['1'])
    shape = shape.copy_paste(source=shape[0], destination=Tile(10,7))
    
    edges = Shape([])
    for d in ['up', 'down', 'right', 'left', 'down_left', 'up_right', 'up_left', 'down_right']:
       edges += shape.edge(direction=d)
    inside = shape - edges
    inside.draw('blue')
    
    '''
    7. Leave the thirteenth column from the left blank, and paint a purple zero shape
    starting on the first tile of the fourteenth column. Paint the tiles inside of
    the zero blue.
    '''
    
    shape = g.get_record(step_names=['1'])
    shape = shape.copy_paste(source=shape[0], destination=Tile(14,1))
    edges = Shape([])
    for d in ['up', 'down', 'right', 'left', 'down_left', 'up_right', 'up_left', 'down_right']:
       edges += shape.edge(direction=d)
    inside = shape - edges
    inside.draw('blue')
    
    '''
    8. Paint another purple zero starting on the seventh tile of the fourteenth column
    from the left. Paint the tiles inside the zero green.
    '''
    shape = g.get_record(step_names=['1'])
    shape = shape.copy_paste(source=shape[0], destination=Tile(14,7))
    
    edges = Shape([])
    for d in ['up', 'down', 'right', 'left', 'down_left', 'up_right', 'up_left', 'down_right']:
       edges += shape.edge(direction=d)
    inside = shape - edges
    inside.draw('green')
    
    '''
    9. Leave the seventeenth and eighteenth columns blank.
    '''
    
    g.plot(gold_boards=gold_boards, multiple=0)
