# Created by maor

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle

task_index = 119
gold_boards = list(read_task(task_index)['gold_boards'])

with Game() as g:
    
    # description:
    # task index: 119, image: P01C03T11, collection round: 1, category: conditional iteration, group: train
    # agreement scores: [[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [0.78, 0.78, 1.0]]
    
    '''
    1. Paint the whole 7th column green.
    '''
    line = Line(start_tile=Tile(7,1), direction='down')
    line.draw('green')
    '''
    2. Now, switch to blue and paint the topmost tile on the 8th column.
    '''
    tile = Tile(8,1)
    tile.draw('blue')
    '''
    3. While still in the same column, paint every other tile using the same color.
    '''
    from constants import HEIGHT

    for i in range (3, HEIGHT+1, 2):
        Tile(8, i).draw('blue')
    
    '''
    4. After each blue tile, paint every other one downright till the end.
    '''
    from constants import WIDTH

    counter = 0
    for i in range (10, WIDTH+1, 2):
        for j in range (2 + counter, HEIGHT+1, 2):
            Tile(i, j).draw('blue')
        counter += 1

    g.plot(gold_boards=gold_boards, multiple=0)
