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
    Tile(3, 2).draw('green')
    Tile(3, 3).draw('green')
    Tile(3, 1).neighbors().draw('purple')
    Tile(3, 4).neighbors().draw('purple')
    
    # Step 2
    Tile(-4, -3).draw('green')
    Tile(-4, -2).draw('green')
    Tile(-4, -4).neighbors().draw('purple')
    Tile(-4, -1).neighbors().draw('purple')
    Tile(2, -3).draw('green')
    Tile(2, -2).draw('green')
    Tile(2, -4).neighbors().draw('purple')
    Tile(2, -1).neighbors().draw('purple')
    Tile(7, 2).draw('green')
    Tile(7, 3).draw('green')
    Tile(7, 1).neighbors().draw('purple')
    Tile(7, 4).neighbors().draw('purple')
    
    # Step 3
    Shape([Tile(-4, -3), Tile(-4, -2), Tile(-3, -3), Tile(-3, -2)]).neighbors().draw('purple')
    Shape([Tile(7, 2), Tile(7, 3), Tile(8, 2), Tile(8, 3)]).neighbors().draw('purple')
    Tile(-4, -3).draw('blue')
    Tile(-4, -2).draw('blue')
    Tile(8, -3).draw('blue')
    Tile(8, -2).draw('blue')
    
    # Step 4
    Tile(3, -1).draw('green')
    Tile(3, -2).draw('blue')
    
    # Step 5
    Tile(7, 2).draw('green')
    Tile(7, 1).draw('blue')
    
    # Step 6
    Tile(8, -2).draw('green')
    Tile(8, -3).draw('blue')
    
    # Step 7
    Shape([Tile(3, 2), Tile(3, 1), Tile(3, 3), Tile(2, 2), Tile(2, 1), Tile(2, 3)]).neighbors().draw('orange')
    Shape([Tile(-4, -3), Tile(-4, -4), Tile(-4, -2), Tile(-3, -3), Tile(-3, -4), Tile(-3, -2)]).neighbors().draw('orange')
    Shape([Tile(7, 2), Tile(7, 1), Tile(7, 3), Tile(8, 2), Tile(8, 1), Tile(8, 3)]).neighbors().draw('orange')
    
    import os
    image = os.path.dirname(__file__).split('\\')[-1]
    variation = os.path.basename(__file__).split('.')[0]
    g.plot(gold_boards=None, multiple=0,file_name=f'{image}-{variation}')
