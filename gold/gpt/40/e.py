# Created by chat gpt

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle
from constants.constants import *

with Game() as g:
    
    
    # In the 8th column from the left, the third tile down is your center. It is blank, and the 6 tiles around it are blue.
    center_left = Tile(3, 8)
    center_left.draw('blue')
    for direction in DIRECTIONS:
        center_left.neighbor(direction).draw('blue')
    
    # In the 8th column from the right, the third tile down is blank and the 6 surrounding tiles will be green.
    center_right = Tile(3, -8)
    for direction in DIRECTIONS:
        center_right.neighbor(direction).draw('green')
    
    # In the 6th column from the right, the 5th tile down is blank, and the 6 tiles surrounding it will be blue.
    five_down_six_right = Tile(5, -6)
    for direction in DIRECTIONS:
        five_down_six_right.neighbor(direction).draw('blue')
    
    # In the 7th column from the right, the 4th tile from the bottom is blank, and the 6 tiles surrounding it will be green.
    four_down_seven_right = Tile(-4, -7)
    for direction in DIRECTIONS:
        four_down_seven_right.neighbor(direction).draw('green')
    
    # In the 9th column from the left, the third tile from the bottom is blank, and the 6 surrounding tiles will be blue.
    three_down_nine_left = Tile(-3, 9)
    for direction in DIRECTIONS:
        three_down_nine_left.neighbor(direction).draw('blue')
    
    # In the 7th column from the left the 5th tile from the bottom is blank, and the 6 surrounding tiles are green.
    five_down_seven_left = Tile(-5, 7)
    for direction in DIRECTIONS:
        five_down_seven_left.neighbor(direction).draw('green')
    
    # In the 10th column from the left, the 5th tile down is blank, and the 6 surrounding tiles are red.
    five_down_ten_left = Tile(5, 10)
    for direction in DIRECTIONS:
        five_down_ten_left.neighbor(direction).draw('red')
    
    # Save the steps
    g.record_step(1)
    
    import os
    image = os.path.dirname(__file__).split('\\')[-1]
    variation = os.path.basename(__file__).split('.')[0]
    g.plot(gold_boards=None, multiple=0,file_name=f'{image}-{variation}')
