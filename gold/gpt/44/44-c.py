# Created by chat gpt

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle

task_index = 44
gold_boards = list(read_task(task_index)['gold_boards'])

with Game() as g:
    
    # Make a triangle from 9 red tiles
    red_tiles = []
    for row in range(3):
        for col in range(3-row):
            tile = Tile(3+col-1, row+1)
            tile.draw('red')
            red_tiles.append(tile)
    red_triangle = Shape(red_tiles)
    
    # repeat the red triangle with same orientation starting with one vertical white row between the triangles
    white_tile = Tile(1,1)
    white_tile.draw('white')
    spacing = 1
    final_shape = Shape([])
    for i in range(4):
        if i>0:
            white_tile = white_tile.neighbor('down')
            white_tile.draw('white')
        new_triangle = red_triangle.copy_paste('right', spacing*i, reference_shape=white_tile)
        # final_shape.tiles += new_triangle.tiles # FIX COMPLIATION ERROR
        final_shape += new_triangle
    # Draw the final pattern
    final_shape.draw('black')
    
    g.start()
    
    
    
    import os
    g.plot(gold_boards=None, multiple=0,file_name=os.path.basename(__file__).split('.')[0])
