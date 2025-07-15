# Created by chat gpt

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle
from constants.constants import *

with Game() as g:
    
    # 1. Starting from the bottom left count over 5 cells that stick down and up 5. Paint this cell purple.
    purple_tile = Tile(5, -5)
    purple_tile.draw('purple')
    
    # 2. Color all cells touching the purple cell red.
    red_ring = Shape(purple_tile.neighbors())
    red_ring.draw('red')
    
    # 3. Starting at the topmost edge of the red ring and working clockwise, color the cell adjacent to the top of the ring green and the next one green too.
    green_tiles = [red_ring.tiles[0].neighbor('up_left'), red_ring.tiles[1].neighbor('up_right')]
    for green_tile in green_tiles:
        green_tile.draw('green')
    
    # 4. Color the next 2 cells blue.
    blue_tiles = [red_ring.tiles[2].neighbor('up_right'), red_ring.tiles[2].neighbor('down_right')]
    for blue_tile in blue_tiles:
        blue_tile.draw('blue')
    
    # 5. Continue working around the red until back to the top.
    for i in range(3, len(red_ring.tiles)):
        if i % 2 == 0:  # Green cells
            green_tiles.append(red_ring.tiles[i].neighbor('down_right'))
            green_tiles.append(red_ring.tiles[i].neighbor('down_left'))
            for green_tile in [green_tiles[-2], green_tiles[-1]]:
                green_tile.draw('green')
        else:  # Blue cells
            blue_tiles.append(red_ring.tiles[i].neighbor('up_right'))
            blue_tiles.append(red_ring.tiles[i].neighbor('down_right'))
            for blue_tile in [blue_tiles[-2], blue_tiles[-1]]:
                blue_tile.draw('blue')
    
    # 6. For every green pair of cells outside the red ring, construct a green ring incorporating both cells around the blank cell touching both of them.
    for i in range(0, len(green_tiles), 2):
        green_ring_tiles = [green_tiles[i], green_tiles[i+1], green_tiles[i].neighbor('down_right')]
        green_ring = Shape(green_ring_tiles)
        green_ring.draw('green')
    
    # 7. Repeat step 6 for all blue cells.
    for i in range(0, len(blue_tiles), 2):
        blue_ring_tiles = [blue_tiles[i], blue_tiles[i+1], blue_tiles[i].neighbor('down_right')]
        blue_ring = Shape(blue_ring_tiles)
        blue_ring.draw('blue')
    
    # 8. Uncolor the purple cell.
    purple_tile.draw('white')
    
    import os
    image = os.path.dirname(__file__).split('\\')[-1]
    variation = os.path.basename(__file__).split('.')[0]
    g.plot(gold_boards=None, multiple=0,file_name=f'{image}-{variation}')
