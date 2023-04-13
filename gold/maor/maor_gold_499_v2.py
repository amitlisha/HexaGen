# Created by maor

from utils.reading_tasks import read_task
from src.hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle

task_index = 499
gold_boards = list(read_task(task_index)['gold_boards'])

HexagonsGame.start()

# description:
# task index: 499, image: P01C01T09, collection round: 0, category: simple, group: train
# agreement scores: [[1, 0, 0], [1.0, 0, 0], [1.0, 1.0, 1.0]]

'''
1. Locate the center column (9 from the left or right
'''

'''
2. Color the fifth hex from the top in this column pink
'''
tile = Tile(9, 5)
tile.draw('purple')

'''
3. Color all surrounding hexes green, so that the pink hex is contained in a circle
'''
circle = Circle(center_tile=tile, radius=1)
circle.draw('green')

HexagonsGame.plot(gold_boards=gold_boards, multiple=0)
