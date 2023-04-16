# Created by maor

from utils.reading_tasks import read_task
from src.hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle

task_index = 187
gold_boards = list(read_task(task_index)['gold_boards'])

HexagonsGame.start()

# description:
# task index: 187, image: P01C04T18, collection round: 1, category: conditions, group: train
# agreement scores: [[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0]]

'''
1. Beginning with the bottom cell of the left-most column and working in a diagonal
to the top of the rightmost column paint the first 2 cells blue, then 2 orange,
1 blue, 2 orange, 3 blue, 2 orange, 1 blue, 2 orange, 1 blue and 2 orange to
finish the line.
'''
tile = Tile(1,-1)
tile.draw('blue')
tile = tile.neighbor('up_right')
tile.draw('blue')
tile = tile.neighbor('up_right')
tile.draw('orange')
tile = tile.neighbor('up_right')
tile.draw('orange')
tile = tile.neighbor('up_right')
tile.draw('blue')
tile = tile.neighbor('up_right')
tile.draw('orange')
tile = tile.neighbor('up_right')
tile.draw('orange')
tile = tile.neighbor('up_right')
tile.draw('blue')
tile = tile.neighbor('up_right')
tile.draw('blue')
tile = tile.neighbor('up_right')
tile.draw('blue')
tile = tile.neighbor('up_right')
tile.draw('orange')
tile = tile.neighbor('up_right')
tile.draw('orange')
tile = tile.neighbor('up_right')
tile.draw('blue')
tile = tile.neighbor('up_right')
tile.draw('orange')
tile = tile.neighbor('up_right')
tile.draw('orange')
tile = tile.neighbor('up_right')
tile.draw('blue')
tile = tile.neighbor('up_right')
tile.draw('orange')
tile = tile.neighbor('up_right')
tile.draw('orange')

'''
2. From the first cell colored in step 1, skip the 2 cells directly above it and
color the third cell purple to begin constructing a line parallel to the one in
step 1.
'''
tile = Tile(1,-4)
tile.draw('purple')

'''
3. Color the cell to the right and up from the one in step 2 purple then add 1
green, 1 purple, 1 green, 3 purple, 2 green, 2 purple, and one green on the end.
'''
tile = tile.neighbor('up_right')
tile.draw('purple')
tile = tile.neighbor('up_right')
tile.draw('green')
tile = tile.neighbor('up_right')
tile.draw('purple')
tile = tile.neighbor('up_right')
tile.draw('green')
tile = tile.neighbor('up_right')
tile.draw('purple')
tile = tile.neighbor('up_right')
tile.draw('purple')
tile = tile.neighbor('up_right')
tile.draw('purple')
tile = tile.neighbor('up_right')
tile.draw('green')
tile = tile.neighbor('up_right')
tile.draw('green')
tile = tile.neighbor('up_right')
tile.draw('purple')
tile = tile.neighbor('up_right')
tile.draw('purple')
tile = tile.neighbor('up_right')
tile.draw('green')

'''
4. Beginning from the first cell in step 2, color the next 2 cells to its bottom
right red to connect to the other line creating the rung of a ladder.
'''
start_tile = Tile(1,-4)
tile = start_tile.neighbor('down_right')
tile.draw('red')
tile = tile.neighbor('down_right')
tile.draw('red')

'''
5. Skip the next cell and color 2 yellow cells from the bottom right of the one
after that.
'''
start_tile = start_tile.neighbor('up_right').neighbor('up_right')
tile = start_tile.neighbor('down_right')
tile.draw('yellow')
tile = tile.neighbor('down_right')
tile.draw('yellow')

'''
6. Skip the next cell and color the next 2 cells to its bottom right red to connect
to the other line.
'''
start_tile = start_tile.neighbor('up_right').neighbor('up_right')
tile = start_tile.neighbor('down_right')
tile.draw('red')
tile = tile.neighbor('down_right')
tile.draw('red')


'''
7. Repeat step 5 twice.
'''
for i in range(2):
  start_tile = start_tile.neighbor('up_right').neighbor('up_right')
  tile = start_tile.neighbor('down_right')
  tile.draw('yellow')
  tile = tile.neighbor('down_right')
  tile.draw('yellow')

'''
8. Repeat step 6 twice.
'''
for i in range(2):
  start_tile = start_tile.neighbor('up_right').neighbor('up_right')
  tile = start_tile.neighbor('down_right')
  tile.draw('red')
  tile = tile.neighbor('down_right')
  tile.draw('red')

HexagonsGame.plot(gold_boards=gold_boards, multiple=0)
