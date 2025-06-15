# Created by chat gpt

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle
from constants.constants import *

with Game() as g:
    
    center_tile = Tile(column=-8, row=3)
    
    # Draw the tiles for the first flower
    for direction in DIRECTIONS:
        center_tile.neighbor(direction).draw('blue')
    center_tile.draw('white')
    
    # Define the center tile of the second flower
    center_tile = Tile(column=8, row=3)
    
    # Draw the tiles for the second flower
    for direction in DIRECTIONS:
        center_tile.neighbor(direction).draw('green')
    center_tile.draw('white')
    
    # Define the center tile of the third flower
    center_tile = Tile(column=-6, row=5)
    
    # Draw the tiles for the third flower
    for direction in DIRECTIONS:
        center_tile.neighbor(direction).draw('blue')
    center_tile.draw('white')
    
    # Define the center tile of the fourth flower
    center_tile = Tile(column=-7, row=-4)
    
    # Draw the tiles for the fourth flower
    for direction in DIRECTIONS:
        center_tile.neighbor(direction).draw('green')
    center_tile.draw('white')
    
    # Define the center tile of the fifth flower
    center_tile = Tile(column=-9, row=-3)
    
    # Draw the tiles for the fifth flower
    for direction in DIRECTIONS:
        center_tile.neighbor(direction).draw('blue')
    center_tile.draw('white')
    
    # Define the center tile of the sixth flower
    center_tile = Tile(column=-7, row=-5)
    
    # Draw the tiles for the sixth flower
    for direction in DIRECTIONS:
        center_tile.neighbor(direction).draw('green')
    center_tile.draw('white')
    
    # Define the center tile of the seventh flower
    center_tile = Tile(column=-10, row=5)
    
    # Draw the tiles for the seventh flower
    for direction in DIRECTIONS:
        center_tile.neighbor(direction).draw('red')
    center_tile.draw('white')
    
    import os
    image = os.path.dirname(__file__).split('\\')[-1]
    variation = os.path.basename(__file__).split('.')[0]
    g.plot(gold_boards=None, multiple=0,file_name=f'{image}-{variation}')
