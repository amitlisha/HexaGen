# Created by maor

from utils.reading_tasks import read_task
from src.hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle

task_index = 227
gold_boards = list(read_task(task_index)['gold_boards'])

HexagonsGame.start()

# description:
# task index: 227, image: P01C08T06, collection round: 1, category: other, group: train
# agreement scores: [[1.0, 1.0, 1.0], [0.98, 0.83, 0.84], [0.99, 0.92, 0.94], [0.9, 0.83, 0.76], [1.0, 0.76, 0.76]]

'''
1. Paint a diagonal row of green hexagons starting with the second hexagon in
column one and ending with the last hexagon in the column furthest to the right.
'''
line = Line(start_tile=Tile(column=1,row=2), end_tile=Tile(column=-1,row=-1))
line.draw('green')

'''
2. Starting in column two, paint the third hexagon green, the fourth and fifth
hexagon in column four green, and continue the pattern moving to the right,
skipping a row in between each, with four being painted green in the eighth and
tenth columns and finishing the columns in the subsequent columns moving to the
right.
'''
column = 2
row = 3

for i in range(1,5,1):
  for j in range(row, row+i):
    tile = Tile(column=column, row=j)
    tile.draw('green')

  column +=2
  row += 1

for i in range(5,1,-1):
  for j in range(row, row+i):
    tile = Tile(column=column, row=j)
    tile.draw('green')

  column +=2
  row += 1


'''
3. Paint the second hexagon in the third column green, the third in column five,
and the second hexagon in column six all green.
'''
for c, r in [(3,2), (5,3), (6,2)]:
  tile = Tile(column=c, row=r)
  tile.draw('green')

'''
4. Paint the third hexagon in column nine, the third hexagon in column twelve, and
the fourth hexagon in column fourteen, the sixth hexagon in column fifteen, the
seventh in column sixteen, and the ninth in column seventeen.
'''
for c, r in [(9,3), (12,3), (14,4), (15,6), (16,7), (17,9)]:
  tile = Tile(column=c, row=r)
  tile.draw('green')

'''
5. Paint the hexagons in between the center diagonal line and the single green
hexagons to make diagonal lines.
'''
for c, r in [(9,3), (12,3), (14,4), (15,6), (16,7), (17,9)]:
  tile = Tile(column=c, row=r)
  end_tile = Line(start_tile=tile, direction='down_left') * line
  Line(start_tile=tile, end_tile=end_tile, include_end_tile=False, include_start_tile=False).draw('green')

HexagonsGame.plot(gold_boards=gold_boards, multiple=0)
