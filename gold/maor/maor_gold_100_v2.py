# Created by maor

from utils.reading_tasks import read_task
from src.hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle

task_index = 100
gold_boards = list(read_task(task_index)['gold_boards'])

HexagonsGame.start()

# description:
# task index: 100, image: P01C03T05, collection round: 1, category: conditional iteration, group: train
# agreement scores: [[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [0.92, 1.0, 0.92], [1.0, 1.0, 1.0]]

'''
1. Paint the fourth hexagon in the seventh column orange and paint all of the
hexagons surrounding it red.
'''
tile = Tile(column=7, row=4)
tile.draw('orange')
tile.neighbors().draw('red')

'''
2. Paint a diagonal line starting with the third hexagon yellow in column nine and
alternating between red and yellow to end with a the first hexagon in column
thirteen being yellow.
'''
for c, r in [(9,3), (11,2), (13,1)]:
  tile = Tile(column=c, row=r)
  tile.draw('yellow')
for c, r in [(10,2), (12,1)]:
  tile = Tile(column=c, row=r)
  tile.draw('red')

'''
3. Copy this pattern of alternating between red and yellow, starting with yellow
from hexagon five in column nine and ending in the second to last hexagon in the
last column.
'''
for c, r in [(9,5), (11,6), (13,7), (15,8), (17,9)]:
  tile = Tile(column=c, row=r)
  tile.draw('yellow')
for c, r in [(10,5), (12,6), (14,7), (16,8), (18,9)]:
  tile = Tile(column=c, row=r)
  tile.draw('red')

'''
4. Copy the same pattern starting with the sixth hexagon in the seventh column,
alternating between red and yellow to complete the column, and again starting
with both hexagon three and five in column five to make three more diagonal
lines.
'''
for c, r in [(7,6), (7,8), (7,10)]:
  tile = Tile(column=c, row=r)
  tile.draw('yellow')
for c, r in [(7,7), (7,9)]:
  tile = Tile(column=c, row=r)
  tile.draw('red')

for c, r in [(5, 3), (3, 2), (1, 1)]:
  tile = Tile(column=c, row=r)
  tile.draw('yellow')
for c, r in [(4, 2), (2, 1)]:
  tile = Tile(column=c, row=r)
  tile.draw('red')

for c, r in [(5, 5), (3, 6), (1, 7)]:
  tile = Tile(column=c, row=r)
  tile.draw('yellow')
for c, r in [(4, 5), (2, 6)]:
  tile = Tile(column=c, row=r)
  tile.draw('red')

'''
5. Paint the first hexagon in the seventh column red and the second hexagon in the
same column yellow.
'''
tile = Tile(column=7,row=1)
tile.draw('red')
tile = Tile(column=7,row=2)
tile.draw('yellow')

HexagonsGame.plot(gold_boards=gold_boards, multiple=0)
