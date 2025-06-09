# Created by by maor

from utils.reading_tasks import read_task
from hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle

task_index = 35
gold_boards = list(read_task(task_index)['gold_boards'])

HexagonsGame.start()

# description:
# task index: 35, image: P01C02T09, collection round: 1, category: bounded iteration, group: train
# agreement scores: [[1, 1, 1], [0, 0, 1.0], [0.29, 0.29, 1.0], [0.2, 0.18, 0.8], [0.29, 0.09, 0.44], [0.32, 0.1, 0.34]]

'''
1. On the bottom of the board, count over to the 5th cell that extends down from
the body.
'''
r = -6

'''
2. Skip the first 5 cells in that column and color the 6th cell red.
'''
c = 10
tile = Tile(column=c,row=r)
tile.draw('red')

'''
3. Create a ring by coloring all cells touching the cell in the previous step blue.
'''
neighbors = tile.neighbors()
neighbors.draw('blue')

'''
4. From the bottom and top most cells in the previous step, skip the cell touching
the 2 diagonal edges and paint the next cell on the diagonal red.
'''
tiles = []
bottom_tile = neighbors.extreme(direction='down')
for d in ['down_right', 'down_left']:
  tile=bottom_tile.neighbors(d).neighbors(d)
  tile.draw('red')
  tiles.append(tile)
top_tile = neighbors.extreme(direction='up')

for d in ['up_right', 'up_left']:
  tile=top_tile.neighbors(d).neighbors(d)
  tile.draw('red')
  tiles.append(tile)
'''
5. Repeat step 3 for all four new red cells, but this time use orange.
'''
for tile in tiles:
  tile.neighbors().draw('orange')

'''
6. Uncolor all red cells.
'''
Shape.get_color('red').recolor({'red': 'white'})

HexagonsGame.plot(gold_boards=gold_boards, multiple=0)
