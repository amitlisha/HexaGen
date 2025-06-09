# Created by maor

from utils.reading_tasks import read_task
from hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle

task_index = 40
gold_boards = list(read_task(task_index)['gold_boards'])

HexagonsGame.start()

# description:
# task index: 40, image: P01C02T11, collection round: 1, category: bounded iteration, group: train
# agreement scores: [[1.0, 0, 0], [1.0, 0.5, 0.5], [1.0, 0.67, 0.67], [1.0, 0.75, 0.75], [1.0, 0.89, 0.89], [1.0, 0.91, 0.91], [1.0, 1.0, 1.0]]

'''
1. This will be 7 connected flowers when we are done. In the 8th column from the
left, the third tile down is your center. It is blank, and the 6 tiles around it
are blue.
'''
circle1 = Circle(Tile(8, 3))
circle1.draw('blue')

'''
2. In the 8th column from the right, the third tile down is blank and the 6
surrounding tiles will be green.
'''
circle2 = Circle(Tile(-8, 3))
circle2.draw('green')

'''
3. In the 6th column from the right, the 5th tile down is blank, and the 6 tiles
surrounding it will be blue.
'''
circle3 = Circle(Tile(-6, 5))
circle3.draw('blue')

'''
4. In the 7th column from the right, the 4th tile from the bottom is blank, and the
6 tiles surrounding it will be green.
'''
circle4 = Circle(Tile(-7, -4))
circle4.draw('green')

'''
5. In the 9th column from the left, the third tile from the bottom is blank, and
the 6 surrounding tiles will be blue.
'''
circle5 = Circle(Tile(9, -3))
circle5.draw('blue')

'''
6. In the 7th column from the left the 5th tile from the bottom is blank, and the 6
surrounding tiles are green.
'''
circle6 = Circle(Tile(7, -5))
circle6.draw('green')

'''
7. In the 10th column from the left, the 5th tile down is blank, and the 6
surrounding tiles are red.
'''
circle7 = Circle(Tile(10, 5))
circle7.draw('red')

HexagonsGame.plot(gold_boards=gold_boards, multiple=0)
