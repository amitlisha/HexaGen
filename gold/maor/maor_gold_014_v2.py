# Created by by maor

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle

task_index = 14
gold_boards = list(read_task(task_index)['gold_boards'])

with Game() as g:
    
    # description:
    # task index: 14, image: P01C01T12, collection round: 1, category: simple, group: train
    # agreement scores: [[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0]]
    
    '''
    1. This will be a blue diamond when done. Starting in the rightmost column, color
    the 2nd tile from the top blue.
    '''
    tile1 = Tile(2, -1)
    tile1.draw('blue')
    
    '''
    2. In the second column from the right, color the 2nd and 3rd from the top blue.
    '''
    line1 = Line(start_tile=Tile(row=2, column=-2), direction='down', length=2)
    line1.draw('blue')
    
    '''
    3. In the third column from the right, color the topmost 3 blue.
    '''
    line2 = Line(start_tile=Tile(row=1, column=-3), direction='down', length=3)
    line2.draw('blue')
    
    '''
    4. In the 4th column from the right, color the topmost 4 blue.
    '''
    line3 = Line(start_tile=Tile(row=1, column=-4), direction='down', length=4)
    line3.draw('blue')
    
    '''
    5. In the 5th column from the right, color the topmost 3 blue.
    '''
    line4 = Line(start_tile=Tile(row=1, column=-5), direction='down', length=3)
    line4.draw('blue')
    
    '''
    6. In the 6th column from the right, color the 2nd and 3rd from the top blue.
    '''
    line5 = Line(start_tile=Tile(row=2, column=-6), direction='down', length=2)
    line5.draw('blue')
    
    '''
    7. In the 7th column from the right color the 2nd tile from the top.
    '''
    tile2 = Tile(2, -7)
    tile2.draw('blue')
    
    g.plot(gold_boards=gold_boards, multiple=0)
