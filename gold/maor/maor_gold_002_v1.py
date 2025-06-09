# Created by maor

from utils.reading_tasks import read_task
from hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle

task_index = 2
gold_boards = list(read_task(task_index)['gold_boards'])

HexagonsGame.start()

# description:
# task index: 2, image: P01C01T05, collection round: 1, category: simple, group: train
# agreement scores: [[1.0, 0, 0], [1.0, 0, 0], [0.57, 0, 0], [0.63, 0.21, 0.1]]

'''
1. In the sixth column from the left, paint the fifth tile from the top red
'''
tile = Tile(6, 5)
tile.draw('red')

'''
2. Paint the next three tiles diagonally to the top right red
'''
line1 = Line(start_tile=tile, direction='up_right', length= 3, include_start_tile=False)
line1.draw('red')

'''
3.  Paint the next three tiles downward red
'''
line2 = Line(start_tile=line1.end_tile, direction='down', length=3, include_start_tile=False)
line2.draw('red')

'''
4.  Paint the empty tiles in between the last step and the first step to form equal triangular red tiles painting
'''
line = Line(start_tile=line2.end_tile, end_tile=tile)
line.draw('red')


HexagonsGame.plot(gold_boards=gold_boards, multiple=0)
