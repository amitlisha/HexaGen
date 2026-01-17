# Created by chat gpt

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle
from constants.constants import *

with Game() as g:
    
    # set up the board by creating tiles and drawing them in the specified colors
    center = Tile(3, 8)
    center.draw('white')
    for direction in ['up', 'down', 'down_right', 'up_left', 'down_left', 'up_right']:
        neighbor = center.neighbor(direction)
        neighbor.draw('blue')
    
    right_center = Tile(3, -8)
    right_center.draw('white')
    for direction in ['up', 'down', 'down_right', 'up_left', 'down_left', 'up_right']:
        neighbor = right_center.neighbor(direction)
        neighbor.draw('green')
    
    right_five = Tile(5, -6)
    right_five.draw('white')
    for direction in ['up', 'down', 'down_right', 'up_left', 'down_left', 'up_right']:
        neighbor = right_five.neighbor(direction)
        neighbor.draw('blue')
    
    right_four = Tile(-4, -7)
    right_four.draw('white')
    for direction in ['up', 'down', 'down_right', 'up_left', 'down_left', 'up_right']:
        neighbor = right_four.neighbor(direction)
        neighbor.draw('green')
    
    left_nine = Tile(-3, 9)
    left_nine.draw('white')
    for direction in ['up', 'down', 'down_right', 'up_left', 'down_left', 'up_right']:
        neighbor = left_nine.neighbor(direction)
        neighbor.draw('blue')
    
    left_five = Tile(-5, 7)
    left_five.draw('white')
    for direction in ['up', 'down', 'down_right', 'up_left', 'down_left', 'up_right']:
        neighbor = left_five.neighbor(direction)
        neighbor.draw('green')
    
    left_ten = Tile(-5, 10)
    left_ten.draw('white')
    for direction in ['up', 'down', 'down_right', 'up_left', 'down_left', 'up_right']:
        neighbor = left_ten.neighbor(direction)
        neighbor.draw('red')
    
    
    import os
    image = os.path.dirname(__file__).split('\\')[-1]
    variation = os.path.basename(__file__).split('.')[0]
    g.plot(gold_boards=None, multiple=0,file_name=f'{image}-{variation}')
