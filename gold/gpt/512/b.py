# Created by chat gpt

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle
from constants.constants import *

with Game() as g:
    
    third_column = [Tile(2, 3), Tile(3, 3)]
    for tile in third_column:
        tile.draw('green')
    
    seventh_column_bottom = [Tile(-3, 7), Tile(-2, 7)]
    for tile in seventh_column_bottom:
        tile.draw('green')
    
    fifteenth_column_bottom = [Tile(-3, 15), Tile(-2, 15)]
    for tile in fifteenth_column_bottom:
        tile.draw('green')
    
    green_tiles = third_column + seventh_column_bottom + fifteenth_column_bottom
    for tile in green_tiles:
        neighbors = tile.neighbors()
        for neighbor in neighbors:
            if neighbor.color == 'white':
                neighbor.draw('purple')
    
    fifteenth_column_top = [Tile(2, 15), Tile(3, 15)]
    for tile in fifteenth_column_top:
        tile.draw('blue')
    
    eleventh_column_bottom = [Tile(-3, 11), Tile(-2, 11)]
    for tile in eleventh_column_bottom:
        tile.draw('blue')
    
    blue_tiles = fifteenth_column_top + eleventh_column_bottom
    for tile in blue_tiles:
        neighbors = tile.neighbors()
        for neighbor in neighbors:
            if neighbor.color == 'white':
                neighbor.draw('purple')
    
    Tile(-3, 3).draw('green')
    
    Tile(-2, 3).draw('blue')
    
    Tile(2, 7).draw('green')
    
    Tile(3, 7).draw('blue')
    
    Tile(2, 11).draw('blue')
    
    Tile(3, 11).draw('green')
    
    duos = [(Tile(-2, 3), Tile(-3, 3)),        (Tile(2, 7), Tile(3, 7)),        (Tile(2, 11), Tile(3, 11)),        (Tile(2, 15), Tile(3, 15))]
    for duo in duos:
        for tile in duo:
            neighbors = tile.neighbors()
            for neighbor in neighbors:
                if neighbor.color == 'white':
                    neighbor.draw('orange')
    
    
    
    import os
    image = os.path.dirname(__file__).split('\\')[-1]
    variation = os.path.basename(__file__).split('.')[0]
    g.plot(gold_boards=None, multiple=0,file_name=f'{image}-{variation}')
