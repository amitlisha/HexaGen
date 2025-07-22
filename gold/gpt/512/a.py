# Created by chat gpt

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle
from constants.constants import *

with Game() as g:
    
    # In the third column, colour in green tiles number two and three from the top
    top_2 = Tile(2, -3)
    top_2.draw('green')
    top_3 = top_2.neighbor('down')
    top_3.draw('green')
    
    # In the seventh column, colour in green tiles number two and three from the bottom
    bottom_2 = Tile(-2, 7)
    bottom_2.draw('green')
    bottom_3 = bottom_2.neighbor('up')
    bottom_3.draw('green')
    
    # In the fifteenth column, colour in green tiles number two and three from the bottom
    bottom_2_fifteenth = Tile(-2, 15)
    bottom_2_fifteenth.draw('green')
    bottom_3_fifteenth = bottom_2_fifteenth.neighbor('up')
    bottom_3_fifteenth.draw('green')
    
    # Colour in purple all the white tiles directly adjacent to green tiles
    for tile in [top_2, top_3, bottom_2, bottom_3, bottom_2_fifteenth, bottom_3_fifteenth]:
        for neighbor in tile.neighbors().tiles:
            if neighbor.color == 'white':
                neighbor.draw('purple')
    
    # In the fifteenth column, colour in blue tiles number two and three from the top
    top_2_blue_fifteenth = Tile(2, 15)
    top_2_blue_fifteenth.draw('blue')
    top_3_blue_fifteenth = top_2_blue_fifteenth.neighbor('down')
    top_3_blue_fifteenth.draw('blue')
    
    # In the eleventh column, colour in blue tiles number two and three from the bottom
    bottom_2_blue_eleventh = Tile(-2, 11)
    bottom_2_blue_eleventh.draw('blue')
    bottom_3_blue_eleventh = bottom_2_blue_eleventh.neighbor('up')
    bottom_3_blue_eleventh.draw('blue')
    
    # Colour in purple all the white tiles directly adjacent to blue tiles
    for tile in [top_2_blue_fifteenth, top_3_blue_fifteenth, bottom_2_blue_eleventh, bottom_3_blue_eleventh]:
        for neighbor in tile.neighbors().tiles:
            if neighbor.color == 'white':
                neighbor.draw('purple')
    
    # In the third column, colour in green tile number three from the bottom
    bottom_3_green_third = Tile(-3, -3)
    bottom_3_green_third.draw('green')
    
    # In the third column, colour in blue tile number two from the bottom
    bottom_2_blue_third = Tile(-2, -3)
    bottom_2_blue_third.draw('blue')
    
    # In the seventh column, colour in green tile number two from the top
    top_2_green_seventh = Tile(2, 7)
    top_2_green_seventh.draw('green')
    
    # In the seventh column, colour in blue tile number 3 from the top
    top_3_blue_seventh = Tile(3, 7)
    top_3_blue_seventh.draw('blue')
    
    # In the eleventh column, colour in blue tile number two from the top
    top_2_blue_eleventh = Tile(2, 11)
    top_2_blue_eleventh.draw('blue')
    
    # In the eleventh column, colour in green tile number 3 from the top
    top_3_green_eleventh = Tile(3, 11)
    top_3_green_eleventh.draw('green')
    
    # Colour orange the tiles adjacent to the blue/green duos
    
    import os
    image = os.path.dirname(__file__).split('\\')[-1]
    variation = os.path.basename(__file__).split('.')[0]
    g.plot(gold_boards=None, multiple=0,file_name=f'{image}-{variation}')
