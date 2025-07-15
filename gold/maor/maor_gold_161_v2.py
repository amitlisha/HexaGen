# Created by maor

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle

task_index = 161
gold_boards = list(read_task(task_index)['gold_boards'])

with Game() as g:
    
    # description:
    # task index: 161, image: P01C04T02, collection round: 1, category: conditions, group: train
    # agreement scores: [[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 0.83, 0.83]]
    
    '''
    1. Use purple to shade the 3rd spot in the 2nd column, 6th spot in the 6th column,
    9th spot in the 10th column, and the 3rd spot in the 14th column.
    '''
    purple_tiles = []
    
    tile = Tile(row=3, column=2)
    tile.draw('purple')
    purple_tiles.append(tile)
    
    tile = Tile(row=6, column=6)
    tile.draw('purple')
    purple_tiles.append(tile)
    
    tile = Tile(row=9, column=10)
    tile.draw('purple')
    purple_tiles.append(tile)
    
    tile = Tile(row=3, column=14)
    tile.draw('purple')
    purple_tiles.append(tile)
    
    '''
    2. Use blue to shade the 6th spot in the 2nd column, 9th spot in the 6th column,
    3rd spot in the 10th column, and 6th spot in the 14th column.
    '''
    blue_tiles = []
    
    tile = Tile(row=6, column=2)
    tile.draw('blue')
    blue_tiles.append(tile)
    
    tile = Tile(row=9, column=6)
    tile.draw('blue')
    blue_tiles.append(tile)
    
    tile = Tile(row=3, column=10)
    tile.draw('blue')
    blue_tiles.append(tile)
    
    tile = Tile(row=6, column=14)
    tile.draw('blue')
    blue_tiles.append(tile)
    
    '''
    3. Use orange to shade the 9th spot in the 2nd column, 3rd spot in the 6th column,
    6th spot in the 10th column, and 9th spot in the 14th column.
    '''
    orange_tiles = []
    
    tile = Tile(row=9, column=2)
    tile.draw('orange')
    orange_tiles.append(tile)
    
    tile = Tile(row=3, column=6)
    tile.draw('orange')
    orange_tiles.append(tile)
    
    tile = Tile(row=6, column=10)
    tile.draw('orange')
    orange_tiles.append(tile)
    
    tile = Tile(row=9, column=14)
    tile.draw('orange')
    orange_tiles.append(tile)
    
    '''
    4. Encircle the purple dots with orange, blue dots with purple, and orange dots
    with blue.
    '''
    for tiles, color in zip ([purple_tiles, blue_tiles, orange_tiles], ['orange','purple','blue']):
      Shape(tiles).neighbors().draw(color)
    
    g.plot(gold_boards=gold_boards, multiple=0)
