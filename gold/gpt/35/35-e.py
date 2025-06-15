# Created by chat gpt

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle
from constants.constants import *

task_index = 35
gold_boards = list(read_task(task_index)['gold_boards'])

with Game() as g:
    
    
    # Define a function to color all tiles touching a given tile
    def color_touching(tile, color):
        neighbors = tile.neighbors()
        shape = Shape(neighbors)
        shape.draw(color)
    
    # Create the game board
    board = [[Tile(col, row) for col in range(1, WIDTH + 1)] for row in range(1, HEIGHT + 1)]
    
    # Step 1
    row = 8
    col = 3
    tile = board[row - 1][col - 1]
    color_touching(tile, 'orange')
    
    # Step 2
    row = 12
    col = 3
    tile = board[row - 1][col - 1]
    color_touching(tile, 'orange')
    
    # Step 3
    row = 8
    col = 7
    tile = board[row - 1][col - 1]
    color_touching(tile, 'orange')
    tile.draw('white')
    
    # Step 4
    row = 12
    col = 7
    tile = board[row - 1][col - 1]
    color_touching(tile, 'orange')
    tile.draw('white')
    
    # Step 5
    shapes = []
    for row in range(1, HEIGHT + 1):
        for col in range(1, WIDTH + 1):
            tile = board[row - 1][col - 1]
            if tile.color == 'orange':
                shapes.append(Shape(tile.neighbors()))
    if len(shapes) == 4:
        center_tile = shapes[0].tiles[3]
        center_shape = Shape([center_tile] + center_tile.neighbors())
        shape = center_shape.copy_paste('up_left', 2)
        shape.draw('blue')
    else:
        print('Error: could not find 4 orange circles on the board')
    
    import os
    g.plot(gold_boards=None, multiple=0,file_name=os.path.basename(__file__).split('.')[0])
