# Created by chat gpt

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle
from constants.constants import *

with Game() as g:
    
    # Step 1
    for row in range(2, 4):
        g.record_step('Step 1')
        tile = Tile(row, 3)
        tile.draw('green')
        for direction in ['up', 'down', 'down_right', 'up_left', 'down_left', 'up_right']:
            neighbor = tile.neighbor(direction)
            if neighbor and neighbor.on_board():
                neighbor.draw('purple')
    
    # Step 2
    for column in [14, 11]:
        for row in range(2, 4):
            g.record_step('Step 2')
            tile = Tile(row, column)
            tile.draw('green')
            for direction in ['up', 'down', 'down_right', 'up_left', 'down_left', 'up_right']:
                neighbor = tile.neighbor(direction)
                if neighbor and neighbor.on_board():
                    neighbor.draw('purple')
            tile2 = Tile(HEIGHT - row + 1, column)
            tile2.draw('green')
            for direction in ['up', 'down', 'down_right', 'up_left', 'down_left', 'up_right']:
                neighbor = tile2.neighbor(direction)
                if neighbor and neighbor.on_board():
                    neighbor.draw('purple')
    
    # Step 3
    for column in [11, 15]:
        for row in range(2, 4):
            g.record_step('Step 3')
            tile = Tile(row, column)
            tile.draw('blue')
            for direction in ['up', 'down', 'down_right', 'up_left', 'down_left', 'up_right']:
                neighbor = tile.neighbor(direction)
                if neighbor and neighbor.on_board():
                    neighbor.draw('purple')
            tile2 = Tile(HEIGHT - row + 1, column)
            tile2.draw('blue')
            for direction in ['up', 'down', 'down_right', 'up_left', 'down_left', 'up_right']:
                neighbor = tile2.neighbor(direction)
                if neighbor and neighbor.on_board():
                    neighbor.draw('purple')
    
    # Step 4
    g.record_step('Step 4')
    tile = Tile(HEIGHT - 1, 3)
    tile.draw('green')
    tile2 = tile.neighbor('down')
    tile2.draw('blue')
    
    # Step 5
    g.record_step('Step 5')
    tile = Tile(2, 7)
    tile.draw('green')
    tile2 = tile.neighbor('down')
    tile2.draw('blue')
    
    # Step 6
    g.record_step('Step 6')
    tile = Tile(2, 15)
    tile.draw('blue')
    tile2 = tile.neighbor('down')
    tile2.draw('green')
    
    # Step 7
    for column, row in [(3, HEIGHT - 1), (7, 2), (15, 2)]:
        g.record_step('Step 7')
        for direction in ['up', 'down', 'down_right', 'up_left', 'down_left', 'up_right']:
            tile = Tile(row, column)
            neighbor = tile.neighbor(direction)
            if neighbor and neighbor.on_board():
                neighbor.draw('orange')
    
    import os
    image = os.path.dirname(__file__).split('\\')[-1]
    variation = os.path.basename(__file__).split('.')[0]
    g.plot(gold_boards=None, multiple=0,file_name=f'{image}-{variation}')
