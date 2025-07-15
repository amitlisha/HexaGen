# Created by maor

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle

task_index = 95
gold_boards = list(read_task(task_index)['gold_boards'])

with Game() as g:
    
    # description:
    # task index: 95, image: P01C03T03, collection round: 1, category: conditional iteration, group: train
    # agreement scores: [[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0]]
    
    '''
    1. In the 5th column from the left, color the 3rd tile down yellow.
    '''
    yellow_tile = Tile(row=3, column=5)
    yellow_tile.draw('yellow')
    
    '''
    2. In the 5th column from the left, color the third tile from the bottom black.
    '''
    black_tile = Tile(row=-3, column=5)
    black_tile.draw('black')
    
    '''
    3. In the 7th column from the right, color the 4th tile from the top blue.
    '''
    blue_tile = Tile(row=4, column=-7)
    blue_tile.draw('blue')
    
    '''
    4. In the first column from the left start at the top tile and create a straight
    line in orange tiles to the yellow tile.
    '''
    line1 = Line(start_tile=Tile(1, 1), end_tile=yellow_tile, include_end_tile=False)
    line1.draw('orange')
    
    '''
    5. In the 9th column from the left, start at the top tile and create a straight
    line in orange tiles to the yellow tile.
    '''
    line2 = Line(start_tile=Tile(1, 9), end_tile=yellow_tile, include_end_tile=False)
    line2.draw('orange')
    
    '''
    6. Starting at the black tile, create a straight line of orange tiles to the yellow
    tile. Leave the black and yellow tiles alone.
    '''
    line3 = Line(start_tile=black_tile, end_tile=yellow_tile, include_end_tile=False, include_start_tile=False)
    line3.draw('orange')
    
    '''
    7. Color the 2 tiles underneath the black tile orange.
    '''
    line4 = Line(start_tile=black_tile, direction='down', length=2, include_start_tile=False)
    line4.draw('orange')
    
    '''
    8. In the first column from the left, the bottom most tile will be purple. Draw a
    straight line from here to the blue tile. Leave the black tile black, and leave
    the blue tile blue.
    '''
    purple_tile = Tile(row=-1, column=1)
    purple_tile.draw('purple')
    
    line4 = Line(start_tile=purple_tile, end_tile=black_tile, include_end_tile=False, include_start_tile=False)
    line4.draw('purple')
    
    line5 = Line(start_tile=black_tile, end_tile=blue_tile, include_end_tile=False, include_start_tile=False)
    line5.draw('purple')
    
    '''
    9. Color the 3 tiles above the blue tile purple.
    '''
    line6 = Line(start_tile= blue_tile, direction='up', length=3, include_start_tile=False)
    line6.draw('purple')
    
    '''
    10. In the first column from the right, color the 4th tile from the bottom purple.
    '''
    purple_tile = Tile(row=-4, column=-1)
    purple_tile.draw('purple')
    
    '''
    11. Make a straight line of purple tiles to the blue tile from the last tile you
    colored, leave the blue tile blue.
    '''
    line7 = Line(start_tile=purple_tile, end_tile=blue_tile, include_end_tile=False, include_start_tile=False)
    line7.draw('purple')
    
    g.plot(gold_boards=gold_boards, multiple=0)
