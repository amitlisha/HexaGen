# Created by chat gpt

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle
from constants.constants import *

with Game() as g:
    
    # define colors for blue, green, and red tiles
    blue = 'blue'
    green = 'green'
    red = 'red'
    
    # create a new tile object for the center tile in the 8th column from the left
    # and draw it in blue
    center_tile = Tile(3, 8)
    center_tile.draw(blue)
    
    # create new tile objects for the 6 surrounding tiles and draw them in blue
    for direction in ['up', 'down', 'down_right', 'up_left', 'down_left', 'up_right']:
        neighbor_tile = center_tile.neighbor(direction)
        neighbor_tile.draw(blue)
    
    # create a new tile object for the center tile in the 8th column from the right
    # and draw it in white
    center_tile = Tile(3, -8)
    center_tile.draw('white')
    
    # create new tile objects for the 6 surrounding tiles and draw them in green
    for direction in ['up', 'down', 'down_right', 'up_left', 'down_left', 'up_right']:
        neighbor_tile = center_tile.neighbor(direction)
        neighbor_tile.draw(green)
    
    # create a new tile object for the tile in the 6th column from the right and 5th
    # row down and draw it in white
    tile = Tile(-5, -6)
    tile.draw('white')
    
    # create new tile objects for the 6 surrounding tiles and draw them in blue
    for direction in ['up', 'down', 'down_right', 'up_left', 'down_left', 'up_right']:
        neighbor_tile = tile.neighbor(direction)
        neighbor_tile.draw(blue)
    
    # create a new tile object for the tile in the 7th column from the right and 4th
    # row from the bottom and draw it in white
    tile = Tile(4, -7)
    tile.draw('white')
    
    # create new tile objects for the 6 surrounding tiles and draw them in green
    for direction in ['up', 'down', 'down_right', 'up_left', 'down_left', 'up_right']:
        neighbor_tile = tile.neighbor(direction)
        neighbor_tile.draw(green)
    
    # create a new tile object for the tile in the 9th column from the left and 3rd
    # row from the bottom and draw it in white
    tile = Tile(-3, 9)
    tile.draw('white')
    
    # create new tile objects for the 6 surrounding tiles and draw them in blue
    for direction in ['up', 'down', 'down_right', 'up_left', 'down_left', 'up_right']:
        neighbor_tile = tile.neighbor(direction)
        neighbor_tile.draw(blue)
    
    # create a new tile object for the tile in the 7th column from the left and 5th
    # row from the bottom and draw it in white
    tile = Tile(-5, 7)
    tile.draw('white')
    
    # create new tile objects for the 6 surrounding tiles and draw them in green
    for direction in ['up', 'down', 'down_right', 'up_left', 'down_left', 'up_right']:
        neighbor_tile = tile.neighbor(direction)
        neighbor_tile.draw(green)
    
    # create a new tile object for the tile in the 10th column from the left and 5th
    # row from the bottom and draw it in red
    tile = Tile(-5, 10)
    tile.draw(red)
    
    # create new tile objects for the 6 surrounding tiles and draw them in red
    for direction in ['up', 'down', 'down_right', 'up_left', 'down_left', 'up_right']:
        neighbor_tile = tile.neighbor(direction)
        neighbor_tile.draw(red)
    
    import os
    image = os.path.dirname(__file__).split('\\')[-1]
    variation = os.path.basename(__file__).split('.')[0]
    g.plot(gold_boards=None, multiple=0,file_name=f'{image}-{variation}')
