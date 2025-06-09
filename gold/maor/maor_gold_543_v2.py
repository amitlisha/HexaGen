# Created by maor

from utils.reading_tasks import read_task
from hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle

task_index = 543
gold_boards = list(read_task(task_index)['gold_boards'])

HexagonsGame.start()

# description:
# task index: 543, image: P01C04T04, collection round: 0, category: conditions, group: train
# agreement scores: [[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0]]

'''
1. The very top row starting from the left is orange, green, green, green, orange,
green, orange, orange, orange.
'''
tile=Tile(column=1, row=1)
tile.draw('orange')

tile=Tile(column=3, row=1)
tile.draw('green')

tile=Tile(column=5, row=1)
tile.draw('green')

tile=Tile(column=7, row=1)
tile.draw('green')

tile=Tile(column=9, row=1)
tile.draw('orange')

tile=Tile(column=11, row=1)
tile.draw('green')

tile=Tile(column=13, row=1)
tile.draw('orange')

tile=Tile(column=15, row=1)
tile.draw('orange')

tile=Tile(column=17, row=1)
tile.draw('orange')

'''
2. The very bottom row is green, orange, green, green, orange, orange, orange,
green, green, in that order.
'''
tile=Tile(column=2, row=-1)
tile.draw('green')

tile=Tile(column=4, row=-1)
tile.draw('orange')

tile=Tile(column=6, row=-1)
tile.draw('green')

tile=Tile(column=8, row=-1)
tile.draw('green')

tile=Tile(column=10, row=-1)
tile.draw('orange')

tile=Tile(column=12, row=-1)
tile.draw('orange')

tile=Tile(column=14, row=-1)
tile.draw('orange')

tile=Tile(column=16, row=-1)
tile.draw('green')

tile=Tile(column=18, row=-1)
tile.draw('green')

'''
3. At the top left you should have orange. The four tiles under it are purple.  Do
this to all 5 orange tiles on the top row.
'''
top_left = start_tile=Tile(1,1)
line = Line(top_left, length=4,include_start_tile=False, direction='down')
line.draw('purple')

for t in Shape.get_color('orange'):
  if t.row == 1:
    line.copy_paste(source=top_left, destination=t)

'''
4. On the top row, you should have 4 green tiles.  All of these tiles have 4 blue
tiles under them.
'''
for t in Shape.get_color('green'):
  if t.row == 1:
    line = Line(start_tile=t, include_start_tile=False, length=4, direction='down')
    line.draw('blue')

'''
5. At the bottom row, you should have 5 green tiles.  There are 4 blue tiles
directly above each green tile.
'''
for t in Shape.get_color('green'):
  if t.row == 10:
    line = Line(start_tile=t, include_start_tile=False, length=4, direction='up')
    line.draw('blue')

'''
6. At the bottom row, you should have 4 orange tiles.  There are 4 purple tiles
directly above the orange tiles.
'''
for t in Shape.get_color('orange'):
  if t.row == 10:
    line = Line(start_tile=t, include_start_tile=False, length=4, direction='up')
    line.draw('purple')

HexagonsGame.plot(gold_boards=gold_boards, multiple=0)
