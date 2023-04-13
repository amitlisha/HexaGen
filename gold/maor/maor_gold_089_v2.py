# Created by maor

from utils.reading_tasks import read_task
from src.hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle

task_index = 89
gold_boards = list(read_task(task_index)['gold_boards'])

HexagonsGame.start()

# description:
# task index: 89, image: P01C03T01, collection round: 1, category: conditional iteration, group: train
# agreement scores: [[1.0, 1.0, 1.0], [1.0, 0.73, 0.73], [1.0, 0.19, 0.19]]

'''
1. On the bottom most row, paint the 8th tile green.
'''
tile=Tile(column=8, row=-1)
tile.draw('green')

'''
2. Using the same color paint the next two tiles above it, and finish the vertical
column of four tiles with the blue one.
'''
line1 = Line(start_tile=tile.neighbor(direction='up'), direction='up', length=2)
line1.draw('green')
tile=line1.end_tile.neighbor(direction='up')
tile.draw('blue')

'''
3. Starting from the blue tile, paint the upper left and the upper right tiles
green, and continue with the same pattern to create two diagonals until you
reach the end of the grid on both sides.
'''

line2 = Line(start_tile=tile, direction='up_left', include_start_tile=False)
line2.draw('green')

line3 = Line(start_tile=tile, direction='up_right', include_start_tile=False)
line3.draw('green')

HexagonsGame.plot(gold_boards=gold_boards, multiple=0)
