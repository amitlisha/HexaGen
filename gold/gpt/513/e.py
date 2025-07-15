# Created by chat gpt

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle
from constants.constants import *

with Game() as g:
    
    # Step 1
    tile = Tile(2, 3)
    tile.draw('green')
    for direction in ['up', 'down_right', 'down_left']:
        tile.neighbor(direction).draw('purple')
    
    # Step 2
    tile = Tile(9, 15)
    tile.draw('green')
    for direction in ['up', 'down_right', 'down_left']:
        tile.neighbor(direction).draw('purple')
    
    tile = Tile(9, 12)
    tile.draw('green')
    for direction in ['up', 'down_right', 'down_left']:
        tile.neighbor(direction).draw('purple')
    
    # Step 3
    tile = Tile(2, 15)
    tile.draw('blue')
    for direction in ['up', 'down_right', 'down_left']:
        tile.neighbor(direction).draw('purple')
    
    tile = Tile(2, 17)
    tile.draw('blue')
    for direction in ['up', 'down_right', 'down_left']:
        tile.neighbor(direction).draw('purple')
    
    tile = Tile(9, 15)
    tile.draw('blue')
    for direction in ['up', 'down_right', 'down_left']:
        tile.neighbor(direction).draw('purple')
    
    tile = Tile(9, 17)
    tile.draw('blue')
    for direction in ['up', 'down_right', 'down_left']:
        tile.neighbor(direction).draw('purple')
    
    # Step 4
    tile = Tile(9, 3)
    tile.neighbor('up').draw('green')
    tile.draw('blue')
    
    # Step 5
    tile = Tile(2, 12)
    tile.neighbor('down').draw('blue')
    tile.draw('green')
    
    # Step 6
    tile = Tile(2, 17)
    tile.neighbor('down').draw('green')
    tile.draw('blue')
    
    # Step 7
    for tile_coord in [(3, 8), (3, 9), (4, 8), (4, 10), (5, 8), (5, 10), (12, 1), (13, 1), (11, 2), (13, 2), (11, 9), (13, 9), (17, 1), (18, 1), (16, 2), (18, 2), (16, 9), (18, 9)]:
        tile = Tile(*tile_coord)
        for direction in ['up', 'down', 'down_right', 'up_left', 'down_left', 'up_right']:
            neighbor = tile.neighbor(direction)
            if neighbor.on_board():
                neighbor.draw('orange')
    
    import os
    image = os.path.dirname(__file__).split('\\')[-1]
    variation = os.path.basename(__file__).split('.')[0]
    g.plot(gold_boards=None, multiple=0,file_name=f'{image}-{variation}')
