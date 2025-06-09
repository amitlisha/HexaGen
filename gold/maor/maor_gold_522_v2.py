# Created by maor

from utils.reading_tasks import read_task
from hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle

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
grid1 = tile.grid(shift_direction='right', spacing=1, num_copies=3)
(grid1-tile).draw('green')

'''
3. Paint the next cell orange.
'''
tile = grid1.edge('right')
grid2=tile.grid(shift_direction='right', spacing=1, num_copies=1)
(grid2-tile).draw('orange')

'''
4. Paint the next cell green.
'''
tile = grid2.edge('right')
grid3=tile.grid(shift_direction='right', spacing=1, num_copies=1)
(grid3-tile).draw('green')

'''
5. Paint the rest of the row orange.
'''
tile = grid3.edge('right')
grid4=tile.grid(shift_direction='right', spacing=1)
(grid4-tile).draw('orange')

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
tile = Tile(column=-1, row=-1)
tile.draw('green')
tile = Tile(column=-3, row=-1)
tile.draw('green')

'''
9. Moving leftwards on the very bottom row, paint the next three cells orange.
'''
grid5=tile.grid(shift_direction='left', spacing=1, num_copies=3)
(grid5-tile).draw('orange')

'''
10. Paint the next two cells green.
'''
tile = grid5.edge('left')
grid6=tile.grid(shift_direction='left', spacing=1, num_copies=2)
(grid6-tile).draw('green')

'''
11. Paint the next cell orange.
'''
tile = grid6.edge('left')
grid7=tile.grid(shift_direction='left', spacing=1, num_copies=1)
(grid7-tile).draw('orange')

'''
12. Paint the next cell green.
'''
tile = grid7.edge('left')
grid8=tile.grid(shift_direction='left', spacing=1, num_copies=1)
(grid8-tile).draw('green')

'''
13. Above each green cell on the bottom row, paint the four cells above it blue.
'''
bottom_row = Shape.get_board_perimeter().edge(direction='down')
for t in Shape.get_color(color='green') * bottom_row:
  line = Line(start_tile=t, length=4, direction='up', include_start_tile=False)
  line.draw('blue')

'''
14. Above each orange cell on the bottom row, paint the four cells above it purple.
'''
for t in Shape.get_color(color='orange') * bottom_row:
  line = Line(start_tile=t, length=4, direction='up', include_start_tile=False)
  line.draw('purple')

HexagonsGame.plot(gold_boards=gold_boards, multiple=0)
