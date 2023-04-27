# Created by maor

from utils.reading_tasks import read_task
from src.hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle

task_index = 552
gold_boards = list(read_task(task_index)['gold_boards'])

HexagonsGame.start()

# description:
# task index: 552, image: P01C04T20, collection round: 0, category: conditions, group: train
# agreement scores: [[0.2, 0.2, 1.0], [0.1, 0.2, 0.5], [0.08, 0.2, 0.4], [0.07, 0.2, 0.33], [0.18, 0.16, 0.89], [0.16, 0.13, 0.8], [0.14, 0.11, 0.73], [0.13, 0.25, 0.67]]

'''
1. Starting at the top in the second row of hex boxes, create a zero shape "0" of 8
purple hex boxes with two green hex boxes in the center.
'''
def zero_from_top(start_tile):
  tiles = []

  tile = start_tile
  tiles.append(tile)

  tile = tile.neighbor(direction='up_right')
  tiles.append(tile)

  tile = tile.neighbor(direction='down_right')
  tiles.append(tile)

  tile = tile.neighbor(direction='down')
  tiles.append(tile)

  tile = tile.neighbor(direction='down')
  tiles.append(tile)

  tile = tile.neighbor(direction='down_left')
  tiles.append(tile)

  tile = tile.neighbor(direction='up_left')
  tiles.append(tile)

  tile = tile.neighbor(direction='up')
  tiles.append(tile)

  return Shape(tiles)

zero1 = zero_from_top(start_tile=Tile(2, 1))
zero1.draw('purple')
zero1.neighbors(criterion='inside').draw('green')

'''
2. skipping a single row, Starting at the top in the next row of hex boxes, create
a zero shape "0" of 8 orange hex boxes with one green hex box on top of one blue
hex box in the center.
'''
zero2 = zero_from_top(start_tile=zero1.extreme(direction='up_right').neighbor(direction='up_right').neighbor(direction='down_right'))
zero2.draw('orange')
zero2.neighbors(criterion='inside').edge(direction='up').draw('green')
zero2.neighbors(criterion='inside').edge(direction='down').draw('blue')

'''
3. skipping a single row, Starting at the top in the next row of hex boxes, create
a zero shape "0" of 8 orange hex boxes with one blue hex box on top of one green
hex box in the center.
'''
zero3 = zero_from_top(start_tile=zero2.extreme(direction='up_right').neighbor(direction='up_right').neighbor(direction='down_right'))
zero3.draw('orange')
zero3.neighbors(criterion='inside').edge(direction='up').draw('blue')
zero3.neighbors(criterion='inside').edge(direction='down').draw('green')

'''
4. skipping a single row, Starting at the top in the next row of hex boxes, create
a zero shape "0" of 8 purple hex boxes with two blue hex boxes in the center.
'''
zero4 = zero_from_top(start_tile=zero3.extreme(direction='up_right').neighbor(direction='up_right').neighbor(direction='down_right'))
zero4.draw('purple')
zero4.neighbors(criterion='inside').draw('blue')

'''
5. Starting at the bottom in the second row of hex boxes, create a zero shape "0"
of 8 orange hex boxes with one green hex box on top of one blue hex box in the
center.
'''
def zero_from_bottom(start_tile):
  tiles = []

  tile = start_tile
  tiles.append(tile)

  tile = tile.neighbor(direction='up')
  tiles.append(tile)

  tile = tile.neighbor(direction='up')
  tiles.append(tile)

  tile = tile.neighbor(direction='up_right')
  tiles.append(tile)

  tile = tile.neighbor(direction='down_right')
  tiles.append(tile)

  tile = tile.neighbor(direction='down')
  tiles.append(tile)

  tile = tile.neighbor(direction='down')
  tiles.append(tile)

  tile = tile.neighbor(direction='down_left')
  tiles.append(tile)

  return Shape(tiles)

zero5 = zero_from_bottom(start_tile=Tile(2,-2))
zero5.draw('orange')
zero5.neighbors(criterion='inside').edge(direction='up').draw('green')
zero5.neighbors(criterion='inside').edge(direction='down').draw('blue')

'''
6. skipping a single row, Starting at the bottom in the next row of hex boxes,
create a zero shape "0" of 8 purple hex boxes with two green hex boxes in the
center.
'''
zero6 = zero_from_bottom(start_tile=zero5.extreme(direction='down_right').neighbor(direction='up_right').neighbor(direction='down_right'))
zero6.draw('purple')
zero6.neighbors(criterion='inside').draw('green')

'''
7. skipping a single row, Starting at the bottom in the next row of hex boxes,
create a zero shape "0" of 8 purple hex boxes with two blue hex boxes in the
center.
'''
zero7 = zero_from_bottom(start_tile=zero6.extreme(direction='down_right').neighbor(direction='up_right').neighbor(direction='down_right'))
zero7.draw('purple')
zero7.neighbors(criterion='inside').draw('blue')

'''
8. skipping a single row, Starting at the bottom in the next row of hex boxes,
create a zero shape "0" of 8 purple hex boxes with two green hex boxes in the
center.
'''
zero8 = zero_from_bottom(start_tile=zero7.extreme(direction='down_right').neighbor(direction='up_right').neighbor(direction='down_right'))
zero8.draw('purple')
zero8.neighbors(criterion='inside').draw('green')

HexagonsGame.plot(gold_boards=gold_boards, multiple=0)
