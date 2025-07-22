# Created by maor

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle

task_index = 501
gold_boards = list(read_task(task_index)['gold_boards'])

with Game() as g:
    
    # description:
    # task index: 501, image: P01C01T12, collection round: 0, category: simple, group: train
    # agreement scores: [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]]
    
    '''
    1. Using blue for all steps, color the second topmost tile from the right.
    '''
    color = 'blue'
    
    tile1 = Tile(1, -4)
    tile1.draw(color)
    
    '''
    2. From the tile create a left diagonal row and a right diagonal row for a total of
    four tiles long.
    '''
    line1 = Line(start_tile=tile1, direction='down_left', length=4)
    line1.draw(color)
    
    line2 = Line(start_tile=tile1, direction='down_right', length=4)
    line2.draw(color)
    
    '''
    3. From the ending tile in each row, color in a left diagonal row and a right
    diagonal row for a total of tour tiles long.
    '''
    line3 = Line(start_tile=line2.end_tile, direction='down_left', length=4)
    line3.draw(color)
    
    line4 = Line(start_tile=line1.end_tile, direction='down_right', length=4)
    line4.draw(color)
    
    '''
    4. Color all tiles with the rows just created.
    '''
    shape1 = Shape(line1 + line2 + line3 + line4)
    shape2 = shape1.get(criterion='inside')
    shape2.draw('blue')
    
    g.plot(gold_boards=gold_boards, multiple=0)
