# Created by chat gpt

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle
from constants.constants import *

with Game() as g:
    
    
    # set the color for the orange circle
    orange = 'orange'
    
    # set the color for the blue circle
    blue = 'blue'
    
    # draw an orange circle at 8th row, 3rd tile from the top
    tile = Tile(8, 3)
    tile.draw(orange)
    neighbors = tile.neighbors()
    for n in neighbors:
        if n.on_board():
            n.draw(orange)
    
    # draw an orange rectangle around the tile at 12th row, 3rd tile down
    tile = Tile(12, 3)
    neighbors = tile.neighbors()
    for n in neighbors:
        if n.on_board():
            n.draw(orange)
    
    # draw an orange circle around the tile at 8th row, 7th tile down
    tile = Tile(8, 7)
    tile.draw(orange)
    neighbors = tile.neighbors()
    for n in neighbors:
        if n.on_board():
            n.draw(orange)
    
    # draw an orange rectangle around the tile at 12th row, 7th tile down
    tile = Tile(12, 7)
    neighbors = tile.neighbors()
    for n in neighbors:
        if n.on_board():
            n.draw(orange)
    
    # draw a blue circle to fit between the 4 orange circles
    # first, find the center tile of the four orange tiles
    center_tile = Tile(10, 5)
    
    # draw the blue circle centered at the center_tile
    circle = []
    for i in range(6):
        tile = center_tile.neighbor(['up', 'down', 'down_right', 'up_left', 'down_left', 'up_right'][i])
        if tile.on_board():
            circle.append(tile)
    tile.draw(blue)
    for t in circle:
        t.draw(blue)
    
    import os
    image = os.path.dirname(__file__).split('\\')[-1]
    variation = os.path.basename(__file__).split('.')[0]
    g.plot(gold_boards=None, multiple=0,file_name=f'{image}-{variation}')
