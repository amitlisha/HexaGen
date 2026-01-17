# Created by maor

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle

task_index = 94
gold_boards = list(read_task(task_index)['gold_boards'])

with Game() as g:
    
    # description:
    # task index: 94, image: P01C03T03, collection round: 1, category: conditional iteration, group: train
    # agreement scores: [[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0]]
    
    '''
    1. Use purple to fill the top 3 spots of the 12th column.
    '''
    line1 = Line(start_tile=Tile(1, 12), direction='down', length=3)
    line1.draw('purple')
    '''
    2. make the 4th spot blue.
    '''
    tile1 = Tile(4, 12)
    tile1.draw('blue')
    '''
    3. Create a purple diagonal line from the right side of the blue spot to the 7th
    spot of the 18th column and from the left side to the last spot on the 1st
    column.
    '''
    line2 = Line(start_tile=Tile(5, 13), end_tile=Tile(7, 18))
    line3 = Line(start_tile=Tile(5, 11), end_tile=Tile(-1, 1))
    line2.draw('purple')
    line3.draw('purple')
    '''
    4. Use yellow to fill the 3rd spot on the 5th column.
    '''
    tile2 = Tile(3, 5)
    tile2.draw('yellow')
    '''
    5. Make orange diagonal line from the yellow spot to the first spots on the 1st and
    9th column.
    '''
    line4 = Line(start_tile=tile2, end_tile=Tile(1, 1), include_start_tile=False)
    line5 = Line(start_tile=tile2, end_tile=Tile(1, 9), include_start_tile=False)
    line4.draw('orange')
    line5.draw('orange')
    '''
    6. Fill in the 4 spots below the yellow spot with orange.
    '''
    line6 = Line(start_tile=tile2, direction='down', length=4, include_start_tile=False)
    line6.draw('orange')
    '''
    7. make the next spot black
    '''
    tile3 = Tile(8, 5)
    tile3.draw('black')
    '''
    8. fill in the last two spots on that column with orange.
    '''
    tile4 = Tile(9, 5)
    tile5 = Tile(10, 5)
    tile4.draw('orange')
    tile5.draw('orange')
    
    g.plot(gold_boards=gold_boards, multiple=0)
