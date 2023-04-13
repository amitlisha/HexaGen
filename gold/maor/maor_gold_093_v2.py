# Created by maor

from utils.reading_tasks import read_task
from src.hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle

task_index = 93
gold_boards = list(read_task(task_index)['gold_boards'])

HexagonsGame.start()

# description:
# task index: 93, image: P01C03T03, collection round: 1, category: conditional iteration, group: train
# agreement scores: [[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [0.56, 1.0, 0.56], [0.69, 1.0, 0.69], [0.71, 1.0, 0.71], [0.75, 1.0, 0.75], [0.8, 1.0, 0.8], [0.85, 1.0, 0.85], [0.85, 1.0, 0.85], [0.87, 1.0, 0.87], [0.89, 1.0, 0.89]]

'''
1. Starting with the cell in the upper leftmost corner, create a line of 4 cells
extending from the lower right edge orange.
'''
line1 = Line(start_tile=Tile(1,1), direction='down_right', length=4)
line1.draw('orange')

'''
2. From the last cell in the previous step color the next cell in line yellow.
'''
tile1 = Tile(column=5,row=3)
tile1.draw('yellow')

'''
3. Building on the cell in step 2 color 4 cells extending from the upper right side
of it orange.
'''
line2 = Line(start_tile=Tile(column=6,row=2), direction='up_right', length=4)
line2.draw('orange')

'''
4. Paint 4 cells orange extending straight down from the yellow cell in step 2.
'''
line3 = Line(start_tile=Tile(column=5,row=4), direction='down', length=4)
line3.draw('orange')

'''
5. Paint the cell directly below the line created in step 4 black.
'''
tile2 = Tile(column=5, row=8)
tile2.draw('black')

'''
6. From the bottom edge of the cell in step 5 add 2 orange cells directly beneath
it.
'''
line4 = Line(start_tile=Tile(column=5, row=9), direction='down', length=2)
line4.draw('orange')

'''
7. From the bottom left of the black cell, create a diagonal line going down and to
the left of 4 purple cells.
'''
line5 = Line(start_tile=Tile(column=4, row=8), direction='down_left', length=4)
line5.draw('purple')

'''
8. From the black cell, create a line of 6 purple cells extending from the top
right of the black cell.
'''
line5 = Line(start_tile=Tile(column=6, row=7), direction='up_right', length=6)
line5.draw('purple')

'''
9. Extend the line in step 8 by adding 1 blue cell.
'''
tile3 = Tile(column=12, row=4)
tile3.draw('blue')

'''
10. From the top of the blue cell, color 3 cells purple going straight up.
'''
line6 = Line(start_tile= Tile(column=12, row=3), direction='up', length=3)
line6.draw('purple')

'''
11. From the bottom right edge of the blue cell create a line of 6 purple extending
down and to the right.
'''
line7 = Line(start_tile= Tile(column=13, row=5), direction='down_right', length=6)
line7.draw('purple')

HexagonsGame.plot(gold_boards=gold_boards, multiple=0)
