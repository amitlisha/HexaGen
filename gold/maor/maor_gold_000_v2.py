# Created by maor

from utils.reading_tasks import read_task
from hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle

task_index = 0
gold_boards = list(read_task(task_index)['gold_boards'])

HexagonsGame.start()

# description:
# task index: 0, image: P01C01T05, collection round: 1, category: simple, group: train
# agreement scores: [[1.0, 0, 0], [1.0, 0.43, 0.43], [1.0, 0.44, 0.44]]

'''
1. Start by coloring the tile in the sixth column, fifth from the top red.
'''
tile = Tile(6, 5)
tile.draw('red')

'''
2. Create a less-than sign (<) using the original tile as the left-most point,
and coloring three more tiles red for each the top and bottom parts of the less-than sign.
     
'''

line2 = Line(start_tile=tile, direction='down_right', length=3, include_start_tile=False)
line2.draw('red')

line3 = Line(start_tile=tile, direction='up_right', length=3, include_start_tile=False)
line3.draw('red')

'''
3. Add two more red tiles to connect the ends of the less-than sign. 
The result will be a red triangle.
'''
line = Line(start_tile=line3.end_tile, end_tile=line2.end_tile, length=2, include_start_tile=False, include_end_tile=False)
line.draw('red')

HexagonsGame.plot(gold_boards=gold_boards, multiple=0)