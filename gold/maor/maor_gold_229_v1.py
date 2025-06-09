# Created by maor

from utils.reading_tasks import read_task
from hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle

task_index = 229
gold_boards = list(read_task(task_index)['gold_boards'])

HexagonsGame.start()

# description:
# task index: 229, image: P01C08T07, collection round: 1, category: other, group: train
# agreement scores: [[1.0, 1.0, 1.0], [1.0, 0.92, 0.92], [0.96, 0.83, 0.83], [0.87, 0.79, 0.81], [0.84, 0.73, 0.65], [0.78, 0.68, 0.56]]

'''
1. Make a green line starting at the second tile of the first column and extending
to the bottom right tile.
'''
line=Line(start_tile=Tile(column=1,row=2), end_tile=Tile(-1,-1))
line.draw('green')

'''
2. Extend out from the second tile by coloring the third tile in the second column
and the second tile in the third column green.
'''
tile = Tile(3,2)
tile.draw('green')
tile = Tile(2,3)
tile.draw('green')

'''
3. Extend out from the center green line again by adding tiles to the fourth tile,
this time extending a bit further by adding two green tiles out from each side.
'''
fourth_tile = line.start_tile
for i in range(4-1):
  fourth_tile=fourth_tile.neighbor(direction='down_right')

tile = fourth_tile
for i in range(2):
  tile = tile.neighbor('up_right')
  tile.draw('green')

tile = fourth_tile
for i in range(2):
  tile = tile.neighbor('down')
  tile.draw('green')

'''
4. Extend out from the sixth tile with three green tiles on each side and then from
the eighth original tile with four green tiles one each side.
'''
sixth_tile = line.start_tile
for i in range(6-1):
  sixth_tile=sixth_tile.neighbor(direction='down_right')

tile = sixth_tile
for i in range(3):
  tile = tile.neighbor('up_right')
  tile.draw('green')

tile = sixth_tile
for i in range(3):
  tile = tile.neighbor('down')
  tile.draw('green')

eight_tile = line.start_tile
for i in range(8 - 1):
  eight_tile = eight_tile.neighbor(direction='down_right')

tile = eight_tile
for i in range(4):
  tile = tile.neighbor('up_right')
  tile.draw('green')

tile = eight_tile
for i in range(4):
  tile = tile.neighbor('down')
  tile.draw('green')

'''
5. Continue extending out from the center line at every other tile starting with
four tiles on each side and decreasing the number of tiles on each side back
down to one.
'''
for offset, length in zip(range(10-1,16,2), range(4,0,-1)):
  start_tile = line.start_tile
  for i in range(offset):
    start_tile=start_tile.neighbor(direction='down_right')

  tile = start_tile
  for i in range(length):
    tile = tile.neighbor('up_right')
    tile.draw('green')

  tile = start_tile
  for i in range(length):
    tile = tile.neighbor('down')
    tile.draw('green')

'''
6. Fill in the spaces between the green extensions with blue. There will be
extensions of blue increasing from one to four and then back down to one.
'''
for offset, length in zip(range(2,9,2), range(1,5,1)):
  start_tile = line.start_tile
  for i in range(offset):
    start_tile=start_tile.neighbor(direction='down_right')

  tile = start_tile
  for i in range(length):
    tile = tile.neighbor('up_right')
    tile.draw('blue')

  tile = start_tile
  for i in range(length):
    tile = tile.neighbor('down')
    tile.draw('blue')

for offset, length in zip(range(10,16,2), range(3,0,-1)):
  start_tile = line.start_tile
  for i in range(offset):
    start_tile=start_tile.neighbor(direction='down_right')

  tile = start_tile
  for i in range(length):
    tile = tile.neighbor('up_right')
    tile.draw('blue')

  tile = start_tile
  for i in range(length):
    tile = tile.neighbor('down')
    tile.draw('blue')

HexagonsGame.plot(gold_boards=gold_boards, multiple=0)
