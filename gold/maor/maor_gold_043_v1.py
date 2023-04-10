# Created by maor

from utils.reading_tasks import read_task
from src.hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle

task_index = 43
gold_boards = list(read_task(task_index)['gold_boards'])

HexagonsGame.start()

# description:
# task index: 43, image: P01C02T12, collection round: 1, category: bounded iteration, group: train
# agreement scores: [[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0]]

'''
1. With red, paint the cell at the 1st column on the left and 2nd row from top.
'''
tile = Tile(column=1, row=2)
tile.draw('red')

'''
2. With red, paint the top 2 cells of the 2nd column from left.
'''
line1 = Line(start_tile=Tile(2,1), direction='down', length=2)
line1.draw('red')

'''
3. With red, paint the top 3 rows of the 3rd column from the left.
'''
line2 = Line(start_tile=Tile(3,1), direction='down', length=3)
line2.draw('red')

'''
4. Repeat the triangle pattern 3 more times to the right of the 1st triangle,
making sure to leave one empty column between each triangle.
'''
shape = tile+line1+line2
shape.grid(shift_direction='right', spacing=1, num_copies=3)

HexagonsGame.plot(gold_boards=gold_boards, multiple=0)
