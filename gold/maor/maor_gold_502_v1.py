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
    line1 = Line(start_tile=Tile(-4,1), direction='down', length=4)
    line1.draw('blue')
    
    '''
    2. In the columns to either side of this (the 3rd and 5th columns) color the top
    three hexes blue
    '''
    line2 = Line(start_tile=line1.start_tile.neighbor(direction='down_right'), direction='down', length=3)
    line2.draw('blue')
    
    line3 = Line(start_tile=line1.start_tile.neighbor(direction='down_left'), direction='down', length=3)
    line3.draw('blue')
    
    '''
    3. In the next two columns out from this (the 2nd and 6th columns from the right)
    skip the first hex and color the 2nd and 3rd hexes blue.
    '''
    line4 = Line(start_tile=Tile(-2, 2), direction='down', length=2)
    line4.draw('blue')
    
    line5 = Line(start_tile=Tile(-6, 2), direction='down', length=2)
    line5.draw('blue')
    
    '''
    4. In the 1st and 7th columns from the right skip the first hex and color the 2nd
    hex only blue. A diamond shape should be drawn now.
    '''
    tile1 = Tile(-1, 2)
    tile1.draw('blue')
    
    tile2 = Tile(-7, 2)
    tile2.draw('blue')
    
    g.plot(gold_boards=gold_boards, multiple=0)
