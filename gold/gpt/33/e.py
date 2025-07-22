# Created by chat gpt

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle
from constants.constants import *

with Game() as g:
    
    
    # Color all tiles orange around eighth vertical row from left, third tile from the top of that row
    tile1 = Tile(3, 8)
    tile1.draw('orange')
    neighbors1 = tile1.neighbors()
    for tile in neighbors1:
        tile.draw('orange')
    
    # On 12th vertical row from left, 3rd tile down, color all tiles touching that tile, orange.
    tile2 = Tile(3, 12)
    tile2.draw('orange')
    neighbors2 = tile2.neighbors()
    for tile in neighbors2:
        tile.draw('orange')
    
    # On 8th vertical row 7th tile down, color all tiles touching that one orange, leaving it blank (as in other steps).
    tile3 = Tile(7, 8)
    tile3.draw('orange')
    neighbors3 = tile3.neighbors()
    for tile in neighbors3:
        if tile != tile3:
            tile.draw('orange')
        else:
            tile.draw('white')
    
    # On 12th row, vertically from left, 7th tile down, color all tiles touching it orange, leaving it blank.
    tile4 = Tile(7, 12)
    tile4.draw('orange')
    neighbors4 = tile4.neighbors()
    for tile in neighbors4:
        if tile != tile4:
            tile.draw('orange')
        else:
            tile.draw('white')
    
    # form a blue circle to fit in between the 4 orange circles drawn, of the same number of tiles, same size (six tiles, as in others).
    tile5_center = Tile(9, 10)
    tile5_center.draw('blue')
    neighbors5 = tile5_center.neighbors()
    for i in range(5):
        tile5 = neighbors5[i]
        tile5.draw('orange')
        neighbors5b = tile5.neighbors()
        for tile in neighbors5b:
            if tile != tile5 and tile not in neighbors1 and tile not in neighbors2 and tile not in neighbors3 and tile not in neighbors4:
                tile.draw('orange')
    
    import os
    image = os.path.dirname(__file__).split('\\')[-1]
    variation = os.path.basename(__file__).split('.')[0]
    g.plot(gold_boards=None, multiple=0,file_name=f'{image}-{variation}')
