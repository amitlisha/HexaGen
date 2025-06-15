# Created by chat gpt

from utils.reading_tasks import read_task
from hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle

task_index = 43
gold_boards = list(read_task(task_index)['gold_boards'])

HexagonsGame.start()

# Paint the cell at the 1st column on the left and 2nd row from top in red
Tile(1, 2).draw('red')

# Paint the top 2 cells of the 2nd column from left in red
for i in range(1, 3):
    Tile(2, i).draw('red')

# Paint the top 3 rows of the 3rd column from the left in red
for i in range(1, 4):
    Tile(3, i).draw('red')

# Define a function to draw the triangle pattern
def draw_triangle(column, row, size, color):
    for i in range(size):
        for j in range(i+1):
            Tile(column + j, row + i).draw(color)

# Draw the first triangle
draw_triangle(5, 1, 4, 'red')

# Draw the second triangle
draw_triangle(11, 1, 4, 'red')

# Draw the third triangle
draw_triangle(17, 1, 4, 'red')

# Draw the remaining triangles to the right of the first one
for i in range(3):
    draw_triangle(23 + i*6, 1, 4, 'red')

import os
HexagonsGame.plot(gold_boards=None, multiple=0,file_name=os.path.basename(__file__).split('.')[0])
