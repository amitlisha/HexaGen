# Created by chat gpt

from utils.reading_tasks import read_task
from hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle
from constants.constants import *

HexagonsGame.start()

third_column = [Tile(3, 2), Tile(3, 3)]
for tile in third_column:
    tile.draw('green')

seventh_column_bottom = [Tile(7, -3), Tile(7, -2)]
for tile in seventh_column_bottom:
    tile.draw('green')

fifteenth_column_bottom = [Tile(15, -3), Tile(15, -2)]
for tile in fifteenth_column_bottom:
    tile.draw('green')

green_tiles = third_column + seventh_column_bottom + fifteenth_column_bottom
for tile in green_tiles:
    neighbors = tile.neighbors()
    for neighbor in neighbors:
        if neighbor.color == 'white':
            neighbor.draw('purple')

fifteenth_column_top = [Tile(15, 2), Tile(15, 3)]
for tile in fifteenth_column_top:
    tile.draw('blue')

eleventh_column_bottom = [Tile(11, -3), Tile(11, -2)]
for tile in eleventh_column_bottom:
    tile.draw('blue')

blue_tiles = fifteenth_column_top + eleventh_column_bottom
for tile in blue_tiles:
    neighbors = tile.neighbors()
    for neighbor in neighbors:
        if neighbor.color == 'white':
            neighbor.draw('purple')

Tile(3, -3).draw('green')

Tile(3, -2).draw('blue')

Tile(7, 2).draw('green')

Tile(7, 3).draw('blue')

Tile(11, 2).draw('blue')

Tile(11, 3).draw('green')

duos = [(Tile(3, -2), Tile(3, -3)),        (Tile(7, 2), Tile(7, 3)),        (Tile(11, 2), Tile(11, 3)),        (Tile(15, 2), Tile(15, 3))]
for duo in duos:
    for tile in duo:
        neighbors = tile.neighbors()
        for neighbor in neighbors:
            if neighbor.color == 'white':
                neighbor.draw('orange')



import os
image = os.path.dirname(__file__).split('\\')[-1]
variation = os.path.basename(__file__).split('.')[0]
HexagonsGame.plot(gold_boards=None, multiple=0,file_name=f'{image}-{variation}')
