# Created by chat gpt

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle
from constants.constants import *

task_index = 34
gold_boards = list(read_task(task_index)['gold_boards'])

with Game() as g:
    
    center_tile = Tile(10, 5)
    
    # get all neighbors of the center tile and group them into a shape
    neighbors = center_tile.neighbors()
    blue_flower = Shape(neighbors)
    
    # set the color of the shape to blue and draw it
    blue_flower.draw('blue')
    
    # create copies of the blue flower in the desired locations
    down_right_flower = blue_flower.copy_paste('down_right', spacing=1)
    up_right_flower = blue_flower.copy_paste('up_right', spacing=1)
    down_left_flower = blue_flower.copy_paste('down_left', spacing=1)
    up_left_flower = blue_flower.copy_paste('up_left', spacing=1)
    
    # group the tiles of the four flowers into a shape
    orange_flowers = Shape(down_right_flower.tiles + up_right_flower.tiles +
                            down_left_flower.tiles + up_left_flower.tiles)
    
    # set the color of the shape to orange and draw it
    orange_flowers.draw('orange')
    
    import os
    g.plot(gold_boards=None, multiple=0,file_name=os.path.basename(__file__).split('.')[0])
