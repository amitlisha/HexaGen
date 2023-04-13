# Created by maor

from utils.reading_tasks import read_task
from src.hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle

task_index = 33
gold_boards = list(read_task(task_index)['gold_boards'])

HexagonsGame.start()

# description:
# task index: 33, image: P01C02T09, collection round: 1, category: bounded iteration, group: train
# agreement scores: [[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 0.78, 0.78], [1.0, 0.67, 0.67], [1.0, 1.0, 1.0]]

'''
1. Color all tiles orange around eighth vertical row from left, third tile from the
top of that row, resulting in an orange circle there.
'''
tile=Tile(8,3)
tile.neighbors().draw('orange')

'''
2. On 12th vertical row from left, 3rd tile down, color all tiles touching that
tile, orange.
'''
tile=Tile(12,3)
tile.neighbors().draw('orange')

'''
3. On 8th vertical row 7th tile down, color all tiles touching that one orange,
leaving it blank (as in other steps).
'''
tile=Tile(8,7)
tile.neighbors().draw('orange')

'''
4. on 12th row, vertically from left, 7th tile down, color all tiles touching it
orange, leaving it blank.
'''
tile=Tile(12,7)
tile.neighbors().draw('orange')

'''
5. form a blue circle to fit in between the 4 orange circles drawn, of the same
number of tiles, same size (six tiles, as in others).
'''
tile=Tile(10,5)
tile.neighbors().draw('blue')

HexagonsGame.plot(gold_boards=gold_boards, multiple=0)
