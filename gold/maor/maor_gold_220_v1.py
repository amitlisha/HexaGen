# Created by by maor

from utils.reading_tasks import read_task
from hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle

task_index = 220
gold_boards = list(read_task(task_index)['gold_boards'])

HexagonsGame.start()

# description:
# task index: 220, image: P01C08T03, collection round: 1, category: other, group: train
# agreement scores: [[1.0, 1.0, 1.0], [1.0, 0.73, 0.73], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 0.95, 0.95]]

'''
1. Fill the 3rd-5th, 7th, and 8th spots in the 4th and 14th columns with green.
'''
for column in [4,14]:
  for row in list(range(3,6)) + [7, 8, 4, 14]:
    tile = Tile(column=column, row=row)
    tile.draw('green')

'''
2. Fill the 4th-9th spots in the 5th and 13th columns with red.
'''
for column in [5,13]:
  for row in range(4,10):
    tile = Tile(column=column, row=row)
    tile.draw('red')

'''
3. Fill the 4th-8th spots in columns 6 and 12 with purple.
'''
for column in [6,12]:
  for row in range(4,9):
    tile = Tile(column=column, row=row)
    tile.draw('purple')

'''
4. fill spots 5-7 on the 7th and 11th columns with orange.
'''
for column in [7,11]:
  for row in range(5,8):
    tile = Tile(column=column, row=row)
    tile.draw('orange')

'''
5. Make the 5th and 6th spots in the 8th and 10th columns yellow.
'''
for column in [8,10]:
  tile = Tile(column=column, row=5)
  tile.draw('yellow')
  tile = Tile(column=column, row=6)
  tile.draw('yellow')

'''
6. Use blue to fill the 3rd spots in the 8th and 10th columns, and the 4th-8th
spots in the 9th column.
'''
tile = Tile(column=8, row=3)
tile.draw('blue')
tile = Tile(column=10, row=3)
tile.draw('blue')

for r in range(4,9):
  tile = Tile(column=9, row=r)
  tile.draw('blue')

HexagonsGame.plot(gold_boards=gold_boards, multiple=0)
