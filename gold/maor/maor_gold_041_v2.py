# Created by maor

from utils.reading_tasks import read_task
from src.hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle

task_index = 41
gold_boards = list(read_task(task_index)['gold_boards'])

HexagonsGame.start()

# description:
# task index: 41, image: P01C02T11, collection round: 1, category: bounded iteration, group: train
# agreement scores: [[0, 0, 0], [0.29, 0, 0], [0.22, 0, 0], [0.27, 0, 0], [0.21, 0, 0], [0.29, 0.03, 0.06], [0.33, 0.07, 0.07], [0.33, 0.07, 0.07]]

'''
1. Starting from the bottom left count over 5 cells that stick down and up 5. Paint
this cell purple.
'''
tile1 = Tile(10, 5)
tile1.draw('purple')

'''
2. Color all cells touching the purple cell red.
'''
neighbors = tile1.neighbors()
neighbors.draw('red')

'''
3. Starting at the topmost edge of the red ring and working clockwise, color the
cell adjacent to the top of the ring green and the next one green too.
'''
top_tile = neighbors.extreme(direction='up')

tile2 = top_tile.neighbor('up')
tile2.draw('green')

tile3 = top_tile.neighbor('up_right')
tile3.draw('green')

'''
4. Color the next 2 cells blue.
'''
tile4 = tile3.neighbor('down_right')
tile4.draw('blue')

tile5 = tile4.neighbor('down')
tile5.draw('blue')

'''
5. Continue working around the red until back to the top.
'''
down_right_tile = neighbors.extreme(direction='down_right')

tile6 = down_right_tile.neighbor('down_right')
tile6.draw('green')

tile7 = down_right_tile.neighbor('down')
tile7.draw('green')

down_tile = neighbors.extreme(direction='down')

tile8 = down_tile.neighbor('down')
tile8.draw('blue')

tile9 = down_tile.neighbor('down_left')
tile9.draw('blue')

down_left_tile = neighbors.extreme(direction='down_left')

tile10 = down_left_tile.neighbor('down_left')
tile10.draw('green')

tile11 = down_left_tile.neighbor('up_left')
tile11.draw('green')

top_left_tile = neighbors.extreme(direction='up_left')

tile12 = top_left_tile.neighbor('up_left')
tile12.draw('blue')

tile13 = top_left_tile.neighbor('up')
tile13.draw('blue')

'''
6. For every green pair of cells outside the red ring, construct a green ring
incorporating both cells around the blank cell touching both of them.
'''
for t1, t2 in [(tile2, tile3), (tile6,tile7), (tile10,tile11)]:
  tile = t1.neighbors(criterion='white') * t2.neighbors(criterion='white')
  tile.neighbors().draw('green')

'''
7. Repeat step 6 for all blue cells.
'''
for t1, t2 in [(tile4, tile5), (tile8,tile9), (tile12,tile13)]:
  tile = t1.neighbors(criterion='white') * t2.neighbors(criterion='white')
  tile.neighbors().draw('blue')

'''
8. Uncolor the purple cell.
'''
tile1.draw('white')

HexagonsGame.plot(gold_boards=gold_boards, multiple=0)
