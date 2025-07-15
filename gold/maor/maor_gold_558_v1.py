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
    tile1 = Tile(row=2, column=3)
    tile1.draw('green')
    tile2 = tile1.neighbor(direction='down')
    tile2.draw('green')
    
    '''
    2. Color each of the cells touching those cells purple to create an oval.
    '''
    neighbors = (tile1+ tile2).neighbors()
    neighbors.draw('purple')
    
    '''
    3. Starting from the next to last cell in column three, paint it blue and the one
    above it green.
    '''
    tile1 = Tile(row=-2, column=3)
    tile1.draw('blue')
    tile2 = tile1.neighbor(direction='up')
    tile2.draw('green')
    
    '''
    4. Repeat step 2 but in orange around these 2 cells.
    '''
    neighbors = (tile1+ tile2).neighbors()
    neighbors.draw('orange')
    
    '''
    5. Repeat steps 3 and 4 starting with the second cell of the 7th column.
    '''
    tile1 = Tile(row=2, column=7)
    tile1.draw('green')
    tile2 = tile1.neighbor(direction='down')
    tile2.draw('blue')
    
    neighbors = (tile1+ tile2).neighbors()
    neighbors.draw('orange')
    
    '''
    6. Repeat steps 3 and 4 starting with the second cell of the 11th column and switch
    the positions of the blue and green.
    '''
    
    tile1 = Tile(row=2, column=11)
    tile1.draw('blue')
    tile2 = tile1.neighbor(direction='down')
    tile2.draw('green')
    
    neighbors = (tile1+ tile2).neighbors()
    neighbors.draw('orange')
    
    '''
    7. Starting with the second cell from the top of column 15, repeat steps 1 and 2
    but substitute blue for the green.
    '''
    tile1 = Tile(row=2, column=15)
    tile1.draw('blue')
    tile2 = tile1.neighbor(direction='down')
    tile2.draw('blue')
    
    neighbors = (tile1+ tile2).neighbors()
    neighbors.draw('purple')
    
    '''
    8. Repeat steps 1 and 2 beginning with the second cell from the bottom of column 7.
    '''
    tile1 = Tile(row=-2, column=7)
    tile1.draw('green')
    tile2 = tile1.neighbor(direction='up')
    tile2.draw('green')
    
    neighbors = (tile1+ tile2).neighbors()
    neighbors.draw('purple')
    
    '''
    9. Repeat step 7 beginning with the second cell from the bottom of column 11.
    '''
    tile1 = Tile(row=-2, column=11)
    tile1.draw('blue')
    tile2 = tile1.neighbor(direction='up')
    tile2.draw('blue')
    
    neighbors = (tile1+ tile2).neighbors()
    neighbors.draw('purple')
    
    '''
    10. Repeat step 8 starting with the second cell from the bottom of column 15.
    '''
    tile1 = Tile(row=-2, column=15)
    tile1.draw('green')
    tile2 = tile1.neighbor(direction='up')
    tile2.draw('green')
    
    neighbors = (tile1+ tile2).neighbors()
    neighbors.draw('purple')
    
    g.plot(gold_boards=gold_boards, multiple=0)
