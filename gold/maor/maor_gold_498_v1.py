# Created by maor

from utils.reading_tasks import read_task
from src.hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle

task_index = 498
gold_boards = list(read_task(task_index)['gold_boards'])

HexagonsGame.start()

# description:
# task index: 498, image: P01C01T03, collection round: 0, category: simple, group: train
# agreement scores: [[1, 1, 1], [0, 1.0, 0], [0, 1.0, 0], [0, 1.0, 0]]

'''
1. Count the lower hexagons - starting with the second column until you get to the
4th column down.
'''

'''
2. Go down five hexagons in the 4th lower column and color that hexagon green.
'''
tile1 = Tile(column=4*2,row=5)
tile1.draw('green')

'''
3. Now, go to the right and color the two hexagons touching the green hexagons
right two sides the same color green.
'''
tile2 = tile1.neighbor('up_right')
tile2.draw('green')

tile3 = tile1.neighbor('down_right')
tile3.draw('green')

'''
4. Continue to go to the right and color the three hexagons that are touching the
right sides green.
'''
tile4 = tile2.neighbor('up_right')
tile4.draw('green')

tile5 = tile2.neighbor('down_right')
tile5.draw('green')

tile6 = tile3.neighbor('up_right')
tile6.draw('green')

tile7 = tile3.neighbor('down_right')
tile7.draw('green')

HexagonsGame.plot(gold_boards=gold_boards, multiple=0)
