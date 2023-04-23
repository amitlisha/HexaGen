# Created by maor

from utils.reading_tasks import read_task
from src.hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle

task_index = 119
gold_boards = list(read_task(task_index)['gold_boards'])

HexagonsGame.start()

# description:
# task index: 119, image: P01C03T11, collection round: 1, category: conditional iteration, group: train
# agreement scores: [[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [0.78, 0.78, 1.0]]

'''
1. Paint the whole 7th column green.
'''

'''
2. Now, switch to blue and paint the topmost tile on the 8th column.
'''

'''
3. While still in the same column, paint every other tile using the same color.
'''

'''
4. After each blue tile, paint every other one downright till the end.
'''

HexagonsGame.plot(gold_boards=gold_boards, multiple=0)
