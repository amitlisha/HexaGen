# Created by chat gpt

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle
from constants.constants import *

task_index = 35
gold_boards = list(read_task(task_index)['gold_boards'])

with Game() as g:
    
    # create an orange circle around eighth vertical row from left, third tile from the top of that row
    g.record_step('orange_circle_1')
    tile1 = Tile(4, 4)
    tile1.draw('orange')
    for i in range(6):
        tile2 = tile1.neighbor('down_right')
        tile2.draw('orange')
        tile1 = tile2
    for i in range(5):
        tile2 = tile1.neighbor('down')
        tile2.draw('orange')
        tile1 = tile2
    for i in range(6):
        tile2 = tile1.neighbor('up_right')
        tile2.draw('orange')
        tile1 = tile2
    for i in range(5):
        tile2 = tile1.neighbor('up')
        tile2.draw('orange')
        tile1 = tile2
    
    # create an orange circle on 12th vertical row from left, 3rd tile down
    g.record_step('orange_circle_2')
    tile1 = Tile(12, 3)
    tile1.draw('orange')
    for i in range(6):
        tile2 = tile1.neighbor('down_right')
        tile2.draw('orange')
        tile1 = tile2
    for i in range(5):
        tile2 = tile1.neighbor('down')
        tile2.draw('orange')
        tile1 = tile2
    for i in range(6):
        tile2 = tile1.neighbor('up_right')
        tile2.draw('orange')
        tile1 = tile2
    for i in range(5):
        tile2 = tile1.neighbor('up')
        tile2.draw('orange')
        tile1 = tile2
    
    # color all tiles touching the 8th row, 7th tile down, orange
    g.record_step('orange_touching_1')
    tile1 = Tile(7, 8)
    for direction in DIRECTIONS:
        tile2 = tile1.neighbor(direction)
        tile2.draw('orange')
    
    # color all tiles touching the 12th row, 7th tile down, orange
    g.record_step('orange_touching_2')
    tile1 = Tile(7, 12)
    for direction in DIRECTIONS:
        tile2 = tile1.neighbor(direction)
        tile2.draw('orange')
    
    # create a blue circle to fit in between the 4 orange circles drawn, of the same number of tiles, same size (six tiles, as in others)
    g.record_step('blue_circle')
    tile1 = Tile(10, 5)
    tile1.draw('blue')
    for i in range(6):
        tile2 = tile1.neighbor('down_right')
        tile2.draw('blue')
        tile1 = tile2
    for i in range(5):
        tile2 = tile1.neighbor('down')
        tile2.draw('blue')
        tile1 = tile2
    for i in range(6):
        tile2 = tile1.neighbor('up_right')
        tile2.draw('blue')
        tile1 = tile2
    for i in range(5):
        tile2 = tile1.neighbor('up')
        tile2.draw('blue')
        tile1 = tile2
    
    
    import os
    g.plot(gold_boards=None, multiple=0,file_name=os.path.basename(__file__).split('.')[0])
