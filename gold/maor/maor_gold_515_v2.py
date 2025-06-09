# Created by maor

from utils.reading_tasks import read_task
from hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle

task_index = 515
gold_boards = list(read_task(task_index)['gold_boards'])

HexagonsGame.start()

# description:
# task index: 515, image: P01C07T03, collection round: 0, category: composed objects, group: train
# agreement scores: [[1.0, 1.0, 1.0], [0.14, 0.14, 1.0], [0.02, 0.02, 1.0], [0.02, 0.02, 1.0], [0.01, 0.01, 0.69]]

'''
1. Colour in red the very first tile.
'''
tile = Tile(column=1, row=1)
tile.draw('red')

'''
2. Draw a red line from the third tile down, going diagonally up and right.
'''
line = Line(start_tile=Tile(column=1, row=3), direction='up_right')
line.draw('red')

'''
3. Draw three more red lines parallel to this one, leaving a blank line in betweem
each.
'''
for i in range(3):
  start_tile = line.start_tile.neighbor('down').neighbor('down')
  line = Line(start_tile=start_tile, direction='up_right')
  line.draw('red')
'''
4. colour in purple the bottomleft tile.
'''
tile = Tile(column=1, row=-1)
tile.draw('purple')

'''
5. Colour purple all tiles in every other column, from the last red tile in that
column all the way to the bottom.
'''
for c in range(3, 19, 2):
  start_tile = (Shape.get_column(c) * Shape.get_color('red')).edge(direction='down')
  start_tile.get(criterion='below').draw('purple')

HexagonsGame.plot(gold_boards=gold_boards, multiple=0)
