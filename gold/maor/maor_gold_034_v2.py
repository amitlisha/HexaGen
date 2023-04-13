# Created by maor

from utils.reading_tasks import read_task
from src.hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle

task_index = 34
gold_boards = list(read_task(task_index)['gold_boards'])

HexagonsGame.start()

# description:
# task index: 34, image: P01C02T09, collection round: 1, category: bounded iteration, group: train
# agreement scores: [[1.0, 1.0, 1.0], [1.0, 0.87, 0.87]]

'''
1. Make a blue flower of six tiles surrounding the fifth tile in the tenth column.
'''
circle = Circle(center_tile=Tile(column=10, row=5), radius=1)
circle.draw('blue')

'''
2. Make four orange flowers connecting to the original on the outermost corners,
leaving a white tile between each orange flower.
'''
circle = Circle(center_tile=Tile(column=8, row=3), radius=1)
circle.draw('orange')
circle = Circle(center_tile=Tile(column=8, row=7), radius=1)
circle.draw('orange')
circle = Circle(center_tile=Tile(column=12, row=3), radius=1)
circle.draw('orange')
circle = Circle(center_tile=Tile(column=12, row=7), radius=1)
circle.draw('orange')

HexagonsGame.plot(gold_boards=gold_boards, multiple=0)
