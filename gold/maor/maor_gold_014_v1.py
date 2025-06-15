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
    tile1 = Tile(-1,2)
    tile1.draw('blue')
    
    '''
    2. In the second column from the right, color the 2nd and 3rd from the top blue.
    '''
    tile2 = Tile(-2,2)
    tile2.draw('blue')
    tile3 = Tile(-2,3)
    tile3.draw('blue')
    
    '''
    3. In the third column from the right, color the topmost 3 blue.
    '''
    line1 = Line(start_tile=Tile(column=-3,row=3), direction='up')
    line1.draw('blue')
    
    '''
    4. In the 4th column from the right, color the topmost 4 blue.
    '''
    line2 = Line(start_tile=Tile(column=-4,row=4), direction='up')
    line2.draw('blue')
    
    '''
    5. In the 5th column from the right, color the topmost 3 blue.
    '''
    line3 = Line(start_tile=Tile(column=-5,row=3), direction='up')
    line3.draw('blue')
    
    '''
    6. In the 6th column from the right, color the 2nd and 3rd from the top blue.
    '''
    tile4 = Tile(-6, 2)
    tile4.draw('blue')
    tile5 = Tile(-6, 3)
    tile5.draw('blue')
    
    '''
    7. In the 7th column from the right color the 2nd tile from the top.
    '''
    tile6 = Tile(-7, 2)
    tile6.draw('blue')
    
    g.plot(gold_boards=gold_boards, multiple=0)
