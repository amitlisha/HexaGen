# Created by chat gpt

from utils.reading_tasks import read_task
from hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle
from constants.constants import *

task_index = 34
gold_boards = list(read_task(task_index)['gold_boards'])

HexagonsGame.start()

# 1. Make a blue flower of six tiles surrounding the fifth tile in the tenth column.
# Create a central tile
central_tile = Tile(10, 5)
# Draw the central tile in blue
central_tile.draw('blue')
# Create a list of neighbor tiles
neighbor_tiles = [central_tile.neighbor('up_left'), central_tile.neighbor('up_right'),
                  central_tile.neighbor('down_left'), central_tile.neighbor('down_right'),
                  central_tile.neighbor('up'), central_tile.neighbor('down')]
# Draw neighbor tiles in blue
for tile in neighbor_tiles:
    tile.draw('blue')

# 2. Make four orange flowers connecting to the original on the outermost corners,
# leaving a white tile between each orange flower.
# Create a list of directions to create orange flowers
directions = ['up_left', 'up_right', 'down_left', 'down_right']
# Create a list of spacing values for orange flowers
spacings = [2, 3, 4, 5]
# Create a list of orange flowers
orange_flowers = []
# Draw orange flowers
for i in range(4):
    # Create a central tile for the orange flower
    central_tile = central_tile.neighbor(directions[i])# neighbor_tiles[DIRECTIONS.index(directions[i])]
    # Create a new orange flower shape
    orange_flower = Shape([central_tile])
    for j in range(6):
        # Draw a tile in the current direction
        tile = central_tile.neighbor(directions[i])
        tile.draw('orange')
        # Add the tile to the orange flower
        orange_flower = Shape(orange_flower.tiles + [tile])
        # Shift the tile in the current direction and add it to the orange flower
        tile = tile.neighbor(directions[i])
        orange_flower = Shape(orange_flower.tiles + [tile])
    # Store the orange flower
    orange_flowers.append(orange_flower)
    # Shift the orange flower in the current direction and leave a white tile between the flowers
    if i < 3:
        reference_shape = orange_flowers[i]
        orange_flower.copy_paste(directions[i], spacings[i], reference_shape=reference_shape)

import os
HexagonsGame.plot(gold_boards=None, multiple=0,file_name=os.path.basename(__file__).split('.')[0])
