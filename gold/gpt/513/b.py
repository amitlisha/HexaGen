# Created by chat gpt

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle
from constants.constants import *

with Game() as g:
    
    # Constants
    HEIGHT = 10 # number of rows
    WIDTH = 18 # number of columns
    COLORS = ['white', 'black', 'yellow', 'green', 'red', 'blue', 'purple', 'orange']
    DIRECTIONS = ['up', 'down', 'down_right', 'up_left', 'down_left', 'up_right']
    
    # Step 1
    Tile(2, 3).draw('green')
    Tile(3, 3).draw('green')
    Tile(1, 3).neighbors().draw('purple')
    Tile(4, 3).neighbors().draw('purple')
    
    # Step 2
    Tile(-3, -4).draw('green')
    Tile(-2, -4).draw('green')
    Tile(-4, -4).neighbors().draw('purple')
    Tile(-1, -4).neighbors().draw('purple')
    Tile(-3, 2).draw('green')
    Tile(-2, 2).draw('green')
    Tile(-4, 2).neighbors().draw('purple')
    Tile(-1, 2).neighbors().draw('purple')
    Tile(2, 7).draw('green')
    Tile(3, 7).draw('green')
    Tile(1, 7).neighbors().draw('purple')
    Tile(4, 7).neighbors().draw('purple')
    
    # Step 3
    Shape([Tile(-3, -4), Tile(-2, -4), Tile(-3, -3), Tile(-2, -3)]).neighbors().draw('purple')
    Shape([Tile(2, 7), Tile(3, 7), Tile(2, 8), Tile(3, 8)]).neighbors().draw('purple')
    Tile(-3, -4).draw('blue')
    Tile(-2, -4).draw('blue')
    Tile(-3, 8).draw('blue')
    Tile(-2, 8).draw('blue')
    
    # Step 4
    Tile(-1, 3).draw('green')
    Tile(-2, 3).draw('blue')
    
    # Step 5
    Tile(2, 7).draw('green')
    Tile(1, 7).draw('blue')
    
    # Step 6
    Tile(-2, 8).draw('green')
    Tile(-3, 8).draw('blue')
    
    # Step 7
    Shape([Tile(2, 3), Tile(1, 3), Tile(3, 3), Tile(2, 2), Tile(1, 2), Tile(3, 2)]).neighbors().draw('orange')
    Shape([Tile(-3, -4), Tile(-4, -4), Tile(-2, -4), Tile(-3, -3), Tile(-4, -3), Tile(-2, -3)]).neighbors().draw('orange')
    Shape([Tile(2, 7), Tile(1, 7), Tile(3, 7), Tile(2, 8), Tile(1, 8), Tile(3, 8)]).neighbors().draw('orange')
    
    import os
    image = os.path.dirname(__file__).split('\\')[-1]
    variation = os.path.basename(__file__).split('.')[0]
    g.plot(gold_boards=None, multiple=0,file_name=f'{image}-{variation}')
