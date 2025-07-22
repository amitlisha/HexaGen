# Created by chat gpt

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle
from constants.constants import *

with Game() as g:
    
    
    # Starting at the upper left, in the third column, paint the second and third
    # tiles from the top green and all the tiles adjacent to them purple.
    for r in range(2, 4):
        t = Tile(r, 3)
        t.draw('green')
        t.neighbors().draw('purple')
    
    # Repeat this color pattern of green surrounded by purple, starting with green on
    # the second and third tiles from the bottom in the fourth column from the right,
    # and once more, starting with green on the second and third tiles from the bottom
    # in the seventh column from the left.
    for c in [14, 11]:
        for r in range(7, 9):
            t = Tile(r, c)
            t.draw('green')
            t.neighbors().draw('purple')
    
    # Duplicate this shape, but beginning with blue in the second and third tiles from
    # the top in the fourth column from the right and in the second and third tiles
    # from the bottom in the eighth column from the right, surrounding each pair of
    # blue tiles with a purple border.
    for c in [14, 17]:
        for r in range(2, 4):
            t = Tile(r, c)
            t.draw('blue')
            t.neighbors().draw('purple')
    
    # In the third column from the left, paint the second tile from the bottom blue
    # and the one directly above it green.
    t = Tile(-2, 3)
    t.draw('blue')
    t.neighbor('up').draw('green')
    
    # Paint the second tile from the top green and the tile directly below it blue in
    # the seventh column from the left.
    t = Tile(2, 7)
    t.draw('green')
    t.neighbor('down').draw('blue')
    
    # In the eighth column from the right, paint the second tile from the top blue and
    # the one directly below it green.
    t = Tile(2, -8)
    t.draw('blue')
    t.neighbor('down').draw('green')
    
    # Paint each tile adjacent to the three pairs of blue and green tiles orange.
    for c in [-3, 7, -8]:
        for r in range(1, 6):
            t = Tile(r, c)
            if t.color in ['blue', 'green'] or any(n.color in ['blue', 'green'] for n in t.neighbors()):
                t.draw('orange')
    
    import os
    image = os.path.dirname(__file__).split('\\')[-1]
    variation = os.path.basename(__file__).split('.')[0]
    g.plot(gold_boards=None, multiple=0,file_name=f'{image}-{variation}')
