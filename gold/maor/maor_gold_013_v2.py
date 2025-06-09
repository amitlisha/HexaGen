# Created by maor

from utils.reading_tasks import read_task
from hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle

task_index = 13
gold_boards = list(read_task(task_index)['gold_boards'])

HexagonsGame.start()

# description:
# task index: 13, image: P01C01T12, collection round: 1, category: simple, group: train
# agreement scores: [[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0]]

'''
1. Use blue to fill the 2nd spot of the 12th and last columns.
'''
tile1 = Tile(column=12, row=2)
tile1.draw('blue')
tile2 = Tile(column=-1, row=2)
tile2.draw('blue')

'''
2. Fill in the 2nd and 3rd spots on the 13th and 17th columns.
'''
tile3 = Tile(column=13, row=2)
tile3.draw('blue')
tile4 = Tile(column=17, row=2)
tile4.draw('blue')

tile5 = Tile(column=13, row=3)
tile5.draw('blue')
tile6 = Tile(column=17, row=3)
tile6.draw('blue')

'''
3. Fill in the top 3 spots on the 14th and 16th columns.
'''
line1 = Line(start_tile=Tile(column=14,row=3), direction='up')
line1.draw('blue')
line2 = Line(start_tile=Tile(column=16,row=3), direction='up')
line2.draw('blue')

'''
4. Fill in the top 4 spots on the 15th column.
'''
line3 = Line(start_tile=Tile(column=15,row=4), direction='up')
line3.draw('blue')

HexagonsGame.plot(gold_boards=gold_boards, multiple=0)
