# Created by maor

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle

task_index = 558
gold_boards = list(read_task(task_index)['gold_boards'])

with Game() as g:
    
    # description:
    # task index: 558, image: P01C04T20, collection round: 0, category: conditions, group: train
    # agreement scores: [[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 0.98, 0.98], [0.87, 1.0, 0.87], [0.76, 1.0, 0.76]]
    
    '''
    1. Paint the second cell of the third column green and also the one below it.
    '''
    g.record_step('1+2')
    tile1 = Tile(column=3, row=2)
    tile1.draw('green')
    tile2 = tile1.neighbor(direction='down')
    tile2.draw('green')
    
    '''
    2. Color each of the cells touching those cells purple to create an oval.
    '''
    neighbors = (tile1+ tile2).neighbors()
    neighbors.draw('purple')
    
    g.record_step('1+2-end')
    
    '''
    3. Starting from the next to last cell in column three, paint it blue and the one
    above it green.
    '''
    g.record_step('3+4')
    tile1 = Tile(column=3, row=-2)
    tile1.draw('blue')
    tile2 = tile1.neighbor(direction='up')
    tile2.draw('green')
    
    '''
    4. Repeat step 2 but in orange around these 2 cells.
    '''
    neighbors = (tile1+ tile2).neighbors()
    neighbors.draw('orange')
    g.record_step('3+4-end')
    
    '''
    5. Repeat steps 3 and 4 starting with the second cell of the 7th column.
    '''
    shape = g.get_record('3+4')
    shape.copy_paste(source=shape[1], destination=Tile(7,2))
    
    '''
    6. Repeat steps 3 and 4 starting with the second cell of the 11th column and switch
    the positions of the blue and green.
    '''
    shape = g.get_record('3+4')
    shape = shape.copy_paste(source=shape[1], destination=Tile(11,2))
    shape.recolor({'green': 'blue', 'blue': 'green', 'orange': 'orange'})
    
    '''
    7. Starting with the second cell from the top of column 15, repeat steps 1 and 2
    but substitute blue for the green.
    '''
    g.record_step('7')
    shape = g.get_record('1+2')
    shape = shape.copy_paste(source=shape[0], destination=Tile(15,2))
    shape.recolor({'green': 'blue', 'purple': 'purple'})
    g.record_step('7_end')
    
    '''
    8. Repeat steps 1 and 2 beginning with the second cell from the bottom of column 7.
    '''
    g.record_step('8')
    shape = g.get_record('1+2')
    shape = shape.copy_paste(source=shape[1], destination=Tile(7,-2))
    g.record_step('8_end')
    
    '''
    9. Repeat step 7 beginning with the second cell from the bottom of column 11.
    '''
    shape = g.get_record(step_names=['7'])
    shape = shape.copy_paste(source=shape[1], destination=Tile(11,-2))
    
    '''
    10. Repeat step 8 starting with the second cell from the bottom of column 15.
    '''
    shape = g.get_record(step_names=['8'])
    shape = shape.copy_paste(source=shape[1], destination=Tile(15,-2))
    
    g.plot(gold_boards=gold_boards, multiple=0)
