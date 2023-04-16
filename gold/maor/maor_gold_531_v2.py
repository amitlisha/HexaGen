# Created by maor

from utils.reading_tasks import read_task
from src.hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle

task_index = 531
gold_boards = list(read_task(task_index)['gold_boards'])

HexagonsGame.start()

# description:
# task index: 531, image: P01C04T04, collection round: 0, category: conditions, group: train
# agreement scores: [[0.4, 0.4, 1.0], [0.33, 0.33, 1.0], [0.38, 0.38, 1.0], [1.0, 0.33, 0.33], [1.0, 0.32, 0.32], [1.0, 0.3, 0.3], [1.0, 0.24, 0.24], [1.0, 0.22, 0.22]]

'''
1. With orange, paint the top left cell, the top 5th cell, and the top cells 7-9.
'''
HexagonsGame.record_step(step_name='1')
for c in [1,9,13,15,17]:
  tile = Tile(column=c, row=1)
  tile.draw('orange')
HexagonsGame.record_step(step_name='1_end')

'''
2. With green, paint the top cells 2, 3, 4, and 6.
'''
HexagonsGame.record_step(step_name='2')
for c in [3,5,7,11]:
  tile = Tile(column=c, row=1)
  tile.draw('green')
HexagonsGame.record_step(step_name='2_end')

'''
3. With purple paint, paint the 4 cells right below each of the orange cells from
step 1.
'''
shape = HexagonsGame.get_record(step_names=['1'])
for tile in shape:
  for i in range(4):
    tile = tile.neighbor('down')
    tile.draw('purple')

'''
4. With blue paint, paint the 4 cells right below each of the green cells from step
2.
'''
shape = HexagonsGame.get_record(step_names=['2'])
for tile in shape:
  for i in range(4):
    tile = tile.neighbor('down')
    tile.draw('blue')

'''
5. With green paint, paint the very bottom left cell, bottom cells 3 4, 8, and 9.
'''
HexagonsGame.record_step(step_name='3')
for c in [2,6,8,16,18]:
  tile = Tile(column=c, row=-1)
  tile.draw('green')
HexagonsGame.record_step(step_name='3_end')

'''
6. With Orange, paint the bottom cells 2 and 5-7.
'''
HexagonsGame.record_step(step_name='4')
for c in [4,10,12,14]:
  tile = Tile(column=c, row=-1)
  tile.draw('orange')
HexagonsGame.record_step(step_name='4_end')

'''
7. With blue paint, paint the 4 cells right above each of the green cells from step
5.
'''
shape = HexagonsGame.get_record(step_names=['3'])
for tile in shape:
  for i in range(4):
    tile = tile.neighbor('up')
    tile.draw('blue')

'''
8. With purple paint, paint the 4 cells right above each of the orange cells from
step 6.
'''
shape = HexagonsGame.get_record(step_names=['4'])
for tile in shape:
  for i in range(4):
    tile = tile.neighbor('up')
    tile.draw('purple')

HexagonsGame.plot(gold_boards=gold_boards, multiple=0)
