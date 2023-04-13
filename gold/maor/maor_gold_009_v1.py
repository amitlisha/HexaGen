# Created by by maor

from utils.reading_tasks import read_task
from src.hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle

task_index = 9
gold_boards = list(read_task(task_index)['gold_boards'])

HexagonsGame.start()

# description:
# task index: 9, image: P01C01T09, collection round: 1, category: simple, group: train
# agreement scores: [[1.0, 1.0, 1.0], [0.14, 1.0, 0.14]]

'''
1. on fifth row from top, 9th row from left, color the tile purple.
'''
tile = Tile(column=9, row=5)
tile.draw('purple')

'''
2. color all tiles touching the purple tile, green to create a sort of flower.
'''
tile.neighbors().draw('green')

HexagonsGame.plot(gold_boards=gold_boards, multiple=0)
