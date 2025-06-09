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
Shape.polygon([Tile(8, 5), Tile(10, 4), Tile(10, 6)]).draw('green')

HexagonsGame.plot(gold_boards=gold_boards)
