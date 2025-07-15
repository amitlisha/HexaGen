# Created by chat gpt

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle
from constants.constants import *

task_index = 34
gold_boards = list(read_task(task_index)['gold_boards'])

with Game() as g:
    
    # Define the color codes for the flowers
    blue = COLORS.index('blue')
    orange = COLORS.index('orange')
    
    # Draw the blue flower of six tiles surrounding the fifth tile in the tenth column
    center_tile = Tile(5, 10)
    flower_tiles = []
    for direction in DIRECTIONS:
        neighbor = center_tile.neighbor(direction)
        flower_tiles.append(neighbor)
        for i in range(1, 3):
            neighbor = neighbor.neighbor(direction)
            flower_tiles.append(neighbor)
    flower = Shape(flower_tiles)
    flower.draw(blue)
    g.record_step('blue flower')
    
    # Draw the orange flowers connecting to the original on the outermost corners,
    # leaving a white tile between each orange flower.
    spacing = 2
    for direction in ['up', 'down']:
        outer_tile = center_tile.neighbor(direction)
        for i in range(2):
            outer_tile = outer_tile.neighbor('down_right')
            flower_tiles = [outer_tile]
            # for j in range(1, 6):
            #     neighbor = outer_tile.neighbor(DIRECTIONS[j])
    
        for d in DIRECTIONS:
          neighbor = outer_tile.neighbor(d)
    
    import os
    g.plot(gold_boards=None, multiple=0,file_name=os.path.basename(__file__).split('.')[0])
