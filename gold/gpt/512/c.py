# Created by chat gpt

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle
from constants.constants import *

with Game() as g:
    # Define the tiles to be colored
    green_top = [Tile(3, 1), Tile(3, 2)]
    green_bottom = [Tile(7, HEIGHT), Tile(7, HEIGHT - 1)]
    blue_top = [Tile(15, 1), Tile(15, 2)]
    blue_bottom = [Tile(11, HEIGHT), Tile(11, HEIGHT - 1)]
    
    # Color in the tiles
    for tile in green_top:
      tile.draw('green')
    for tile in green_bottom:
      tile.draw('green')
    for tile in blue_top:
      tile.draw('blue')
    for tile in blue_bottom:
      tile.draw('blue')
    
    # Define the tiles to be colored purple
    purple_tiles = []
    
    # Find the white tiles directly adjacent to green tiles and color them purple
    for tile in green_top + green_bottom:
      for direction in DIRECTIONS:
        neighbor = tile.neighbor(direction)
        if neighbor.color == 'white' and neighbor not in purple_tiles:
          purple_tiles.append(neighbor)
          neighbor.draw('purple')
    
    # Find the white tiles directly adjacent to blue tiles and color them purple
    for tile in blue_top + blue_bottom:
      for direction in DIRECTIONS:
        neighbor = tile.neighbor(direction)
        if neighbor.color == 'white' and neighbor not in purple_tiles:
          purple_tiles.append(neighbor)
          neighbor.draw('purple')
    
    # Color in the tiles
    for tile in purple_tiles:
      tile.draw('purple')
    
    # Color in the specified tiles
    Tile(3, HEIGHT - 2).draw('green')
    Tile(3, HEIGHT - 1).draw('blue')
    Tile(7, 2).draw('green')
    Tile(7, 3).draw('blue')
    Tile(11, HEIGHT - 1).draw('blue')
    Tile(11, HEIGHT - 2).draw('green')
    
    # Define the tiles to be colored orange
    orange_tiles = []
    
    # Find the tiles adjacent to blue/green duos and color them orange
    for tile in green_top + green_bottom + blue_top + blue_bottom:
      for direction in DIRECTIONS:
        neighbor = tile.neighbor(direction)
        if neighbor.color == 'white' and neighbor not in orange_tiles:
          if (neighbor.neighbor('down').color == 'green' and tile.color == 'blue') or (
              neighbor.neighbor('up').color == 'blue' and tile.color == 'green'):
            orange_tiles.append(neighbor)
            neighbor.draw('orange')
    
    # Color in the tiles
    for tile in orange_tiles:
      tile.draw('orange')
    
    import os
    image = os.path.dirname(__file__).split('\\')[-1]
    variation = os.path.basename(__file__).split('.')[0]
    g.plot(gold_boards=None, multiple=0,file_name=f'{image}-{variation}')
