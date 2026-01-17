# Created by maor

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle

task_index = 502
gold_boards = list(read_task(task_index)['gold_boards'])

with Game() as g:
    
    # description:
    # task index: 502, image: P01C01T12, collection round: 0, category: simple, group: train
    # agreement scores: [[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 0.71, 0.71], [1.0, 1.0, 1.0]]
    
    '''
    1. Start in the 4th column from the right, and color the top four hexes of the
    column blue
    '''
    line1 = Line(start_tile=Tile(4, -4), direction='up')
    line1.draw('blue')
    
    '''
    2. In the columns to either side of this (the 3rd and 5th columns) color the top
    three hexes blue
    '''
    line2 = Line(start_tile=Tile(3, -3), direction='up')
    line2.draw('blue')
    
    line3 = Line(start_tile=Tile(3, -5), direction='up')
    line3.draw('blue')
    
    '''
    3. In the next two columns out from this (the 2nd and 6th columns from the right)
    skip the first hex and color the 2nd and 3rd hexes blue.
    '''
    tile1 = Tile(2, -2)
    tile1.draw('blue')
    
    tile2 = Tile(3, -2)
    tile2.draw('blue')
    
    tile3 = Tile(2, -6)
    tile3.draw('blue')
    
    tile4 = Tile(3, -6)
    tile4.draw('blue')
    
    '''
    4. In the 1st and 7th columns from the right skip the first hex and color the 2nd
    hex only blue. A diamond shape should be drawn now.
    '''
    tile7 = Tile(2, -1)
    tile7.draw('blue')
    
    tile8 = Tile(2, -7)
    tile8.draw('blue')
    
    g.plot(gold_boards=gold_boards, multiple=0)
