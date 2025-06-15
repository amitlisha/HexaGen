# Created by chat gpt

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle
from constants.constants import *

with Game() as g:
    
    # Define colors for each tile
    blue = 'blue'
    green = 'green'
    red = 'red'
    
    # Create tiles for the first shape
    shape1_tiles = []
    
    # Add center tile
    center_tile = Tile(8, 3)
    shape1_tiles.append(center_tile)
    center_tile.draw(blue)
    
    # Add surrounding blue tiles
    for direction in DIRECTIONS:
        neighbor_tile = center_tile.neighbor(direction)
        shape1_tiles.append(neighbor_tile)
        neighbor_tile.draw(blue)
    
    # Create a Shape object for the first shape
    shape1 = Shape(shape1_tiles)
    
    # Draw the first shape
    shape1.draw(blue)
    
    # Create tiles for the second shape
    shape2_tiles = []
    
    # Add blank tile
    blank_tile = Tile(-8, 3)
    shape2_tiles.append(blank_tile)
    
    # Add surrounding green tiles
    for direction in DIRECTIONS:
        neighbor_tile = blank_tile.neighbor(direction)
        shape2_tiles.append(neighbor_tile)
        neighbor_tile.draw(green)
    
    # Create a Shape object for the second shape
    shape2 = Shape(shape2_tiles)
    
    # Draw the second shape
    shape2.draw(green)
    
    # Create tiles for the third shape
    shape3_tiles = []
    
    # Add blank tile
    blank_tile = Tile(-6, -5)
    shape3_tiles.append(blank_tile)
    
    # Add surrounding blue tiles
    for direction in DIRECTIONS:
        neighbor_tile = blank_tile.neighbor(direction)
        shape3_tiles.append(neighbor_tile)
        neighbor_tile.draw(blue)
    
    # Create a Shape object for the third shape
    shape3 = Shape(shape3_tiles)
    
    # Draw the third shape
    shape3.draw(blue)
    
    # Create tiles for the fourth shape
    shape4_tiles = []
    
    # Add blank tile
    blank_tile = Tile(-7, -4)
    shape4_tiles.append(blank_tile)
    
    # Add surrounding green tiles
    for direction in DIRECTIONS:
        neighbor_tile = blank_tile.neighbor(direction)
        shape4_tiles.append(neighbor_tile)
        neighbor_tile.draw(green)
    
    # Create a Shape object for the fourth shape
    shape4 = Shape(shape4_tiles)
    
    # Draw the fourth shape
    shape4.draw(green)
    
    # Create tiles for the fifth shape
    shape5_tiles = []
    
    # Add blank tile
    blank_tile = Tile(9, -3)
    shape5_tiles.append(blank_tile)
    
    # Add surrounding blue tiles
    for direction in DIRECTIONS:
        neighbor_tile = blank_tile.neighbor(direction)
        shape5_tiles.append(neighbor_tile)
        neighbor_tile.draw(blue)
    
    # Create a Shape object for the fifth shape
    shape5 = Shape(shape5_tiles)
    
    # Draw the fifth shape
    shape5.draw(blue)
    
    # Create tiles for the sixth shape
    shape6_tiles = []
    
    # Add blank tile
    blank_tile = Tile(7, -5)
    shape6_tiles.append(blank_tile)
    
    # Add surrounding green tiles
    for direction in DIRECTIONS:
        neighbor_tile = blank_tile.neighbor(direction)
        shape6_tiles.append(neighbor_tile)
        neighbor_tile.draw(green)
    
    # Create a Shape object for the sixth shape
    shape6 = Shape(shape6_tiles)
    
    # Draw the sixth shape
    shape6.draw(green)
    
    # Create tiles for the seventh shape
    
    import os
    image = os.path.dirname(__file__).split('\\')[-1]
    variation = os.path.basename(__file__).split('.')[0]
    g.plot(gold_boards=None, multiple=0,file_name=f'{image}-{variation}')
