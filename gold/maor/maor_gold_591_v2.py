# Created by maor

from utils.reading_tasks import read_task
from hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle

task_index = 591
gold_boards = list(read_task(task_index)['gold_boards'])

HexagonsGame.start()

# description:
# task index: 591, image: P01C04T04, collection round: 0, category: conditions, group: train
# agreement scores: [[1.0, 1.0, 1.0], [0.57, 1.0, 0.57], [0.65, 1.0, 0.65], [0.8, 1.0, 0.8], [0.82, 1.0, 0.82], [0.87, 1.0, 0.87], [0.88, 1.0, 0.88], [0.91, 1.0, 0.91]]

'''
1. Add orange to the topmost tile in columns (from far left) one, nine, thirteen,
fifteen, and seventeen
'''
tiles = []
for c in [1, 9, 13, 15, 17]:
  tile = Tile(column=c, row=1)
  tile.draw('orange')
  tiles.append(tile)

'''
2. Add four purple tiles directly below the orange tiles mentioned above
'''
for t in tiles:
  line = Line(start_tile=t, direction='down', length=4, include_start_tile=False)
  line.draw('purple')

'''
3. Add orange to the bottom tiles in columns four, ten, twelve, and fourteen.
'''
tiles = []
for c in [4, 10, 12, 14]:
  tile = Tile(column=c, row=-1)
  tile.draw('orange')
  tiles.append(tile)

'''
4. Add four purple tiles directly above the orange tiles mentioned above
'''
for t in tiles:
  line = Line(start_tile=t, direction='up', length=4, include_start_tile=False)
  line.draw('purple')

'''
5. Add green to the topmost tile in columns (from far left) three, five, seven, and
eleven
'''
tiles = []
for c in [3, 5, 7, 11]:
  tile = Tile(column=c, row=1)
  tile.draw('green')
  tiles.append(tile)

'''
6. Add four blue tiles directly beneath the green tiles mentioned above
'''
for t in tiles:
  line = Line(start_tile=t, direction='down', length=4, include_start_tile=False)
  line.draw('blue')

'''
7. Add green to the bottom tiles in columns two, six, eight, sixteen, and eighteen
'''
tiles = []
for c in [2, 6, 8, 16, 18]:
  tile = Tile(column=c, row=-1)
  tile.draw('green')
  tiles.append(tile)

'''
8. Add four blue tiles directly above the green tiles mentioned above
'''
for t in tiles:
  line = Line(start_tile=t, direction='up', length=4, include_start_tile=False)
  line.draw('blue')

HexagonsGame.plot(gold_boards=gold_boards, multiple=0)
