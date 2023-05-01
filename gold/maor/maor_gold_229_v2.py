# Created by maor

from utils.reading_tasks import read_task
from src.hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle

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
line=Line(start_tile=Tile(column=1,row=2), direction='down_right')
line.draw('green')

'''
2. Extend out from the second tile by coloring the third tile in the second column
and the second tile in the third column green.
'''
start_tile = line.start_tile.neighbor(direction='down_right')
Line(start_tile=start_tile, direction='up_right', length=1, include_start_tile=False).draw('green')
Line(start_tile=start_tile, direction='down', length=1, include_start_tile=False).draw('green')

'''
3. Extend out from the center green line again by adding tiles to the fourth tile,
this time extending a bit further by adding two green tiles out from each side.
'''
start_tile = start_tile.neighbor(direction='down_right').neighbor(direction='down_right')
Line(start_tile=start_tile, direction='up_right', length=2, include_start_tile=False).draw('green')
Line(start_tile=start_tile, direction='down', length=2, include_start_tile=False).draw('green')

'''
4. Extend out from the sixth tile with three green tiles on each side and then from
the eighth original tile with four green tiles one each side.
'''
start_tile = start_tile.neighbor(direction='down_right').neighbor(direction='down_right')
Line(start_tile=start_tile, direction='up_right', length=3, include_start_tile=False).draw('green')
Line(start_tile=start_tile, direction='down', length=3, include_start_tile=False).draw('green')

start_tile = start_tile.neighbor(direction='down_right').neighbor(direction='down_right')
Line(start_tile=start_tile, direction='up_right', length=4, include_start_tile=False).draw('green')
Line(start_tile=start_tile, direction='down', length=4, include_start_tile=False).draw('green')

'''
5. Continue extending out from the center line at every other tile starting with
four tiles on each side and decreasing the number of tiles on each side back
down to one.
'''
for length in range(4,0,-1):
  start_tile = start_tile.neighbor(direction='down_right').neighbor(direction='down_right')
  Line(start_tile=start_tile, direction='up_right', length=length, include_start_tile=False).draw('green')
  Line(start_tile=start_tile, direction='down', length=length, include_start_tile=False).draw('green')

'''
6. Fill in the spaces between the green extensions with blue. There will be
extensions of blue increasing from one to four and then back down to one.
'''
start_tile = line.start_tile.neighbor(direction='down_right').neighbor(direction='down_right')
for length in range(1,5,1):
  Line(start_tile=start_tile, direction='up_right', length=length, include_start_tile=False).draw('blue')
  Line(start_tile=start_tile, direction='down', length=length, include_start_tile=False).draw('blue')
  start_tile = start_tile.neighbor(direction='down_right').neighbor(direction='down_right')

for length in range(3,0,-1):
  Line(start_tile=start_tile, direction='up_right', length=length, include_start_tile=False).draw('blue')
  Line(start_tile=start_tile, direction='down', length=length, include_start_tile=False).draw('blue')
  start_tile = start_tile.neighbor(direction='down_right').neighbor(direction='down_right')

HexagonsGame.plot(gold_boards=gold_boards, multiple=0)
