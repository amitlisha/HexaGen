# Created by maor

from utils.reading_tasks import read_task
from hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle

task_index = 200
gold_boards = list(read_task(task_index)['gold_boards'])

HexagonsGame.start()

# description:
# task index: 200, image: P01C07T03, collection round: 1, category: composed objects, group: train
# agreement scores: [[1.0, 1.0, 1.0], [1.0, 0.33, 0.33], [1.0, 0.39, 0.39], [1.0, 0.4, 0.4], [1.0, 0.44, 0.44], [1.0, 0.56, 0.56]]

'''
1. Fill the top-left most hex red.
'''
tile = Tile(column=1, row=1)
tile.draw('red')

'''
2. Fill a red line from the first column on the left, 3rd hex from the top, to the
top hex of the 5th column from the left.
'''
line = Line(start_tile=Tile(1,3), end_tile=Tile(5,1))
line.draw('red')

'''
3. Fill three more parallel lines in red, with a white line between each, from the
left edge of the grid to the top of the grid.
'''
for i in range(3):
  tile = line.start_tile.neighbor('down').neighbor('down')
  line = Line(start_tile=tile, direction='up_right')
  line.draw('red')

'''
4. Fill the bottom-most hex in the first column on the left with purple.
'''
tile = Tile(column=1, row=-1)
tile.draw('purple')

'''
5. In the thirst column from the left, fill the bottom two hexes with purple.
'''
tile1 = Tile(column=3, row=-1)
tile1.draw('purple')
tile2 = Tile(column=3, row=-2)
tile2.draw('purple')

'''
6. Draw 7 more parallel purple lines, starting from the bottom of alternating
columns (a while line between each) and stopping when you touch the red line.
'''
for c, r in zip(range(5,18,2), range(-3,-12,-1)):
  line = Line(start_tile=Tile(c,r), direction='down')
  line.draw('purple')


HexagonsGame.plot(gold_boards=gold_boards, multiple=0)
