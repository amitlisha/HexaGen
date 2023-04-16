# Created by maor

from utils.reading_tasks import read_task
from src.hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle

task_index = 522
gold_boards = list(read_task(task_index)['gold_boards'])

HexagonsGame.start()

# description:
# task index: 522, image: P01C04T04, collection round: 0, category: conditions, group: train
# agreement scores: [[1.0, 1.0, 1.0], [0.5, 1.0, 0.5], [0.4, 1.0, 0.4], [0.33, 1.0, 0.33], [0.44, 1.0, 0.44], [0.5, 1.0, 0.5], [0.44, 1.0, 0.44], [0.45, 1.0, 0.45], [0.44, 1.0, 0.44], [0.43, 1.0, 0.43], [0.43, 1.0, 0.43], [0.41, 1.0, 0.41], [0.37, 1.0, 0.37], [0.36, 1.0, 0.36]]

'''
1. Paint the leftmost and topmost cell orange
'''
tile = Tile(column=1,row=1)
tile.draw('orange')

'''
2. Going to the right, paint the next three cells green.
'''
for c in [3,5,7]:
  tile = Tile(column=c, row=1)
  tile.draw('green')

'''
3. Paint the next cell orange.
'''
tile = Tile(column=9,row=1)
tile.draw('orange')

'''
4. Paint the next cell green.
'''
tile = Tile(column=11,row=1)
tile.draw('green')

'''
5. Paint the rest of the row orange.
'''
for c in [13,15,17]:
  tile = Tile(column=c, row=1)
  tile.draw('orange')

'''
6. Under each orange cell paint four purple cells.
'''
for t in Shape.get_color(color='orange'):
  line = Line(start_tile=t, length=4, direction='down', include_start_tile=False)
  line.draw('purple')

'''
7. Under each green cell paint four blue cells.
'''
for t in Shape.get_color(color='green'):
  line = Line(start_tile=t, length=4, direction='down', include_start_tile=False)
  line.draw('blue')

'''
8. Paint the cell on the very bottom right and the one to its left green.
'''
for c in [-1, -3]:
  tile = Tile(column=c, row=-1)
  tile.draw('green')

'''
9. Moving leftwards on the very bottom row, paint the next three cells orange.
'''
for c in [-5,-7,-9]:
  tile = Tile(column=c, row=-1)
  tile.draw('orange')

'''
10. Paint the next two cells green.
'''
for c in [-11,-13]:
  tile = Tile(column=c, row=-1)
  tile.draw('green')

'''
11. Paint the next cell orange.
'''
tile = Tile(column=-15, row=-1)
tile.draw('orange')

'''
12. Paint the next cell green.
'''
tile = Tile(column=-17, row=-1)
tile.draw('green')

'''
13. Above each green cell on the bottom row, paint the four cells above it blue.
'''
for t in Shape.get_color(color='green').edge('down'):
  line = Line(start_tile=t, length=4, direction='up', include_start_tile=False)
  line.draw('blue')

'''
14. Above each orange cell on the bottom row, paint the four cells above it purple.
'''
for t in Shape.get_color(color='orange').edge('down'):
  line = Line(start_tile=t, length=4, direction='up', include_start_tile=False)
  line.draw('purple')

HexagonsGame.plot(gold_boards=gold_boards, multiple=0)
