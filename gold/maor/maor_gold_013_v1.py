# Created by maor

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle

task_index = 13
gold_boards = list(read_task(task_index)['gold_boards'])

with Game() as g:
    
    # description:
    # task index: 13, image: P01C01T12, collection round: 1, category: simple, group: train
    # agreement scores: [[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0]]
    
    '''
    1. Use blue to fill the 2nd spot of the 12th and last columns.
    '''
    tile1 = Tile(row=2, column=12)
    tile1.draw('blue')
    tile2 = Tile(row=2, column=-1)
    tile2.draw('blue')
    
    '''
    2. Fill in the 2nd and 3rd spots on the 13th and 17th columns.
    '''
    tile3 = Tile(row=2, column=13)
    tile3.draw('blue')
    tile4 = Tile(row=3, column=13)
    tile4.draw('blue')
    
    tile5 = Tile(row=2, column=17)
    tile5.draw('blue')
    tile6 = Tile(row=3, column=17)
    tile6.draw('blue')
    
    '''
    3. Fill in the top 3 spots on the 14th and 16th columns.
    '''
    line1 = Line(start_tile=Tile(row=1, column=14), direction='down', length=3).draw('blue')
    line1.draw('blue')
    line2 = Line(start_tile=Tile(row=1, column=16), direction='down',length=3)
    line2.draw('blue')
    
    '''
    4. Fill in the top 4 spots on the 15th column.
    '''
    line3 = Line(start_tile=Tile(row=1, column=15), direction='down',length=4)
    line3.draw('blue')
    
    g.plot(gold_boards=gold_boards, multiple=0)
