from utils.reading_tasks import read_task
from hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle

task_index = 228
gold_boards = list(read_task(task_index)['gold_boards'])

HexagonsGame.start()

# procedure 228, image P01C08T07, collection round 1, category other, group train

'''
1. Starting with the second tile from the top of the leftmost column, color a
connected line of tiles green, descending to the bottom tile of the rightmost
column.
'''
green_line = Line(start_tile = Tile(1, 2), end_tile = Tile(-1, -1))
green_line.draw('green')
'''
2. Alternate putting green and blue tiles along the lower edge of the original
green line, starting with green in the space between the second and third tiles
of the green line, working from upper left toward lower right, ending with green
in the space between the second and third tiles from the right at the bottom.
'''
upper_tiles = green_line.tiles[1:-3]
color = 'green'
for upper_tile in upper_tiles:
  upper_tile.neighbor('down').draw(color)
  color = 'blue' if color == 'green' else 'green'
'''
3. Beginning in the fourth column from the left, descending along the bottom edge
or the colored tiles, place a green tile directly below each green tile and a
blue tile directly below each blue tile, as far as the grid will allow.
'''
colored_tiles = Shape.get_color('all')
column = 4
while column <= HexagonsGame.width:
  column_tiles = Shape.get_column(column)
  colored_column_tiles = colored_tiles * column_tiles
  lowest_tile = colored_column_tiles.extreme(direction = 'down')
  lowest_tile.neighbor('down').draw(lowest_tile.color)
  column += 1
'''
4. Repeat the action of step 3 two more times, starting with the sixth and eighth
columns from the left.
'''
colored_tiles = Shape.get_color('all')
column = 6
while column <= HexagonsGame.width:
  column_tiles = Shape.get_column(column)
  colored_column_tiles = colored_tiles * column_tiles
  lowest_tile = colored_column_tiles.extreme(direction = 'down')
  lowest_tile.neighbor('down').draw(lowest_tile.color)
  column += 1

colored_tiles = Shape.get_color('all')
column = 8
while column <= HexagonsGame.width:
  column_tiles = Shape.get_column(column)
  colored_column_tiles = colored_tiles * column_tiles
  lowest_tile = colored_column_tiles.extreme(direction = 'down')
  lowest_tile.neighbor('down').draw(lowest_tile.color)
  column += 1
'''
5. Duplicate this color pattern symmetrically along the upper edge of the original
green line.
'''
colored_tiles = Shape.get_color('all')
colored_tiles.reflect(axis_line = green_line)

HexagonsGame.plot(gold_boards=gold_boards)
