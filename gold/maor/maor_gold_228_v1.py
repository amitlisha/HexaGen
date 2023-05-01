# Created by maor
import constants.constants
from constants.constants import *
from utils.reading_tasks import read_task
from src.hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle

task_index = 228
gold_boards = list(read_task(task_index)['gold_boards'])

HexagonsGame.start()

# description:
# task index: 228, image: P01C08T07, collection round: 1, category: other, group: train
# agreement scores: [[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [0.74, 0.78, 0.96], [0.84, 0.88, 0.96], [0.65, 0.52, 0.72]]

'''
1. Starting with the second tile from the top of the leftmost column, color a
connected line of tiles green, descending to the bottom tile of the rightmost
column.
'''
line=Line(start_tile=Tile(column=1,row=2), end_tile=Tile(-1,-1))
line.draw('green')

'''
2. Alternate putting green and blue tiles along the lower edge of the original
green line, starting with green in the space between the second and third tiles
of the green line, working from upper left toward lower right, ending with green
in the space between the second and third tiles from the right at the bottom.
'''
tile = Tile(2,3)
while tile.column <= WIDTH and tile.row <= HEIGHT:
  tile.draw('green')
  tile = tile.neighbor('down_right')
  tile.draw('blue')
  tile = tile.neighbor('down_right')


'''
3. Beginning in the fourth column from the left, descending along the bottom edge
or the colored tiles, place a green tile directly below each green tile and a
blue tile directly below each blue tile, as far as the grid will allow.
'''
tile = Tile(4,5)
while tile.column <= WIDTH and tile.row <= HEIGHT:
  tile.draw('green')
  tile = tile.neighbor('down_right')
  tile.draw('blue')
  tile = tile.neighbor('down_right')

'''
4. Repeat the action of step 3 two more times, starting with the sixth and eighth
columns from the left.
'''
tile = Tile(6,7)
while tile.column <= WIDTH and tile.row <= HEIGHT:
  tile.draw('green')
  tile = tile.neighbor('down_right')
  tile.draw('blue')
  tile = tile.neighbor('down_right')

tile = Tile(8,9)
while tile.column <= WIDTH and tile.row <= HEIGHT:
  tile.draw('green')
  tile = tile.neighbor('down_right')
  tile.draw('blue')
  tile = tile.neighbor('down_right')

'''
5. Duplicate this color pattern symmetrically along the upper edge of the original
green line.
'''
shape = Shape.get_color('green') + Shape.get_color('blue')
shape.reflect(axis_line=line)

HexagonsGame.plot(gold_boards=gold_boards, multiple=0)
