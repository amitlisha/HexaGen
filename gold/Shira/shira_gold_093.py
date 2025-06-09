from utils.reading_tasks import read_task
from hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle

task_index = 93
gold_boards = list(read_task(task_index)['gold_boards'])

HexagonsGame.start()

# procedure 93, image P01C03T03, collection round 1, category conditional iteration, group train

'''
1. Starting with the cell in the upper leftmost corner, create a line of 4 cells
extending from the lower right edge orange.
'''
start_cell = Tile(1, 1)
line = Line(start_tile = start_cell, length = 4, direction = 'down_right')
line.draw('orange')
'''
2. From the last cell in the previous step color the next cell in line yellow.
'''
last_cell = line.end_tile
yellow_cell = last_cell.neighbor('down_right')
yellow_cell.draw('yellow')
'''
3. Building on the cell in step 2 color 4 cells extending from the upper right side
of it orange.
'''
line = Line(start_tile = yellow_cell, length = 4, direction = 'up_right', include_start_tile = False)
line.draw('orange')
'''
4. Paint 4 cells orange extending straight down from the yellow cell in step 2.
'''
line = Line(start_tile = yellow_cell, length = 4, direction = 'down', include_start_tile = False)
line.draw('orange')
'''
5. Paint the cell directly below the line created in step 4 black.
'''
black_cell = line.neighbors('down')
black_cell.draw('black')
'''
6. From the bottom edge of the cell in step 5 add 2 orange cells directly beneath
it.
'''
orange_cell_1 = black_cell.neighbor('down')
orange_cell_1.draw('orange')
orange_cell_2 = orange_cell_1.neighbor('down')
orange_cell_2.draw('orange')
'''
7. From the bottom left of the black cell, create a diagonal line going down and to
the left of 4 purple cells.
'''
line = Line(start_tile = black_cell, length = 4, direction = 'down_left', include_start_tile = False)
line.draw('purple')
'''
8. From the black cell, create a line of 6 purple cells extending from the top
right of the black cell.
'''
line = Line(start_tile = black_cell, length = 6, direction = 'up_right', include_start_tile = False)
line.draw('purple')
'''
9. Extend the line in step 8 by adding 1 blue cell.
'''
blue_cell = line.end_tile.neighbor('up_right')
blue_cell.draw('blue')
'''
10. From the top of the blue cell, color 3 cells purple going straight up.
'''
line = Line(start_tile = blue_cell, length = 3, direction = 'up', include_start_tile = False)
line.draw('purple')
'''
11. From the bottom right edge of the blue cell create a line of 6 purple extending
down and to the right.
'''
line = Line(start_tile = blue_cell, length = 6, direction = 'down_right', include_start_tile = False)
line.draw('purple')

HexagonsGame.plot(gold_boards=gold_boards)
