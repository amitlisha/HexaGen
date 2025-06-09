# Created by maor

from utils.reading_tasks import read_task
from hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle

task_index = 497
gold_boards = list(read_task(task_index)['gold_boards'])

HexagonsGame.start()

# description:
# task index: 497, image: P01C01T03, collection round: 0, category: simple, group: train
# agreement scores: [[1.0, 1.0, 1.0]]

'''
1. Draw an equilateral green triangle, where the sides are three tiles, and the
points are on the 8th column five tiles down, and on the 10th column, four and
six tiles down.
'''
tile1 = Tile(8, 5)
tile2 = Tile(10, 4)
tile3 = Tile(10, 6)

line1 = Line(start_tile=tile1, end_tile=tile2)
line2 = Line(start_tile=tile1, end_tile=tile3)
line3 = Line(start_tile=tile2, end_tile=tile3)

shape = Shape(line1 + line2 + line3)
shape.draw('green')

HexagonsGame.plot(gold_boards=gold_boards, multiple=0)
