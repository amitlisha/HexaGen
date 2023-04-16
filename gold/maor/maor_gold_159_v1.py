# Created by maor

from utils.reading_tasks import read_task
from src.hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle

task_index = 159
gold_boards = list(read_task(task_index)['gold_boards'])

HexagonsGame.start()

# description:
# task index: 159, image: P01C04T02, collection round: 1, category: conditions, group: train
# agreement scores: [[0.91, 1.0, 0.91], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0]]

'''
1. In columns # 1, 3, 13, and 15 paint the third and fourth tile down orange paint
the sixth and seventh tiles down purple and paint the 2 bottommost tiles blue.
'''
for c in [1,3,13,15]:
  for r in [3,4]:
    tile = Tile(column=c, row=r)
    tile.draw('orange')
  for r in [6,7]:
    tile = Tile(column=c, row=r)
    tile.draw('purple')
  for r in [-1,-2]:
    tile = Tile(column=c, row=r)
    tile.draw('blue')

'''
2. In columns, # 2 and 14 paint the second, fourth, and ninth tiles down orange,
paint the third, fifth, and seventh tiles down purple, paint the sixth, eighth
and tenth tiles down blue.
'''
for c in [2,14]:
  for r in [2,4,9]:
    tile = Tile(column=c, row=r)
    tile.draw('orange')
  for r in [3,5,7]:
    tile = Tile(column=c, row=r)
    tile.draw('purple')
  for r in [6,8,10]:
    tile = Tile(column=c, row=r)
    tile.draw('blue')

'''
3. In columns # 5, and 7 paint the third and fourth tile down blue, paint the sixth
and seventh tiles down orange, and paint the 2 bottommost tiles purple.
'''
for c in [5,7]:
  for r in [3,4]:
    tile = Tile(column=c, row=r)
    tile.draw('blue')
  for r in [6,7]:
    tile = Tile(column=c, row=r)
    tile.draw('orange')
  for r in [-1,-2]:
    tile = Tile(column=c, row=r)
    tile.draw('purple')

'''
4. In column # 6 paint the second, fourth, and ninth tiles down blue, paint the
third, fifth, and seventh tiles down orange, paint the sixth, eighth and tenth
tiles down purple.
'''
for r in [2,4,9]:
  tile = Tile(column=6, row=r)
  tile.draw('blue')
for r in [3,5,7]:
  tile = Tile(column=6, row=r)
  tile.draw('orange')
for r in [6,8,10]:
  tile = Tile(column=6, row=r)
  tile.draw('purple')

'''
5. In columns, # 9, and 11 paint the third and fourth tile down purple, paint the
sixth and seventh tiles down blue and paint the 2 bottommost tiles orange.
'''
for c in [9,11]:
  for r in [3,4]:
    tile = Tile(column=c, row=r)
    tile.draw('purple')
  for r in [6,7]:
    tile = Tile(column=c, row=r)
    tile.draw('blue')
  for r in [-1,-2]:
    tile = Tile(column=c, row=r)
    tile.draw('orange')

'''
6. In column # 10 paint the second, fourth, and ninth tiles down purple, paint the
third, fifth, and seventh tiles down blue, paint the sixth, eighth and tenth
tiles down orange.
'''
for r in [2,4,9]:
  tile = Tile(column=10, row=r)
  tile.draw('purple')
for r in [3,5,7]:
  tile = Tile(column=10, row=r)
  tile.draw('blue')
for r in [6,8,10]:
  tile = Tile(column=10, row=r)
  tile.draw('orange')

HexagonsGame.plot(gold_boards=gold_boards, multiple=0)
