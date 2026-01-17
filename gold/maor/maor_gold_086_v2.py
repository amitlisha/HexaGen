# Created by maor

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle

task_index = 86
gold_boards = list(read_task(task_index)['gold_boards'])

with Game() as g:
    
    # description:
    # task index: 86, image: P01C02T29, collection round: 1, category: bounded iteration, group: train
    # agreement scores: [[0, 1.0, 0], [0.5, 1.0, 0.5], [0.51, 0.94, 0.45], [0.5, 1.0, 0.5], [0.5, 0.88, 0.56], [0.43, 0.74, 0.53], [0.37, 0.71, 0.49]]
    
    '''
    1. Begin at third column from right side. Starting from bottom, make hexagons 1, 2,
    7, and 8 yellow. Make 4 and 5 green.
    '''
    g.record_step('1')
    tile1 = Tile(-1, -3)
    tile2 = Tile(-2, -3)
    tile3 = Tile(-7, -3)
    tile4 = Tile(-8, -3)
    
    tile5 = Tile(-4, -3)
    tile6 = Tile(-5, -3)
    
    tile1.draw('yellow')
    tile2.draw('yellow')
    tile3.draw('yellow')
    tile4.draw('yellow')
    
    tile5.draw('green')
    tile6.draw('green')
    
    '''
    2. Keep the colors and spacing the same, but reverse the color scheme in column 7
    from the left side.
    '''
    tile1 = Tile(-1, 7)
    tile2 = Tile(-2, 7)
    tile3 = Tile(-7, 7)
    tile4 = Tile(-8, 7)
    
    tile5 = Tile(-4, 7)
    tile6 = Tile(-5, 7)
    
    tile1.draw('green')
    tile2.draw('green')
    tile3.draw('green')
    tile4.draw('green')
    
    tile5.draw('yellow')
    tile6.draw('yellow')
    
    '''
    3. In bottom left corner color two hexagons green. continue on bottom row to the
    right and leave next hexagon white, the two after that should be yellow.
    '''
    
    tile7 = Tile(-1, 5)
    tile8 = Tile(-1, 4)
    
    tile7.draw('yellow')
    tile8.draw('yellow')
    
    tile9 = Tile(-1, 2)
    tile10 = Tile(-1, 1)
    
    tile9.draw('green')
    tile10.draw('green')
    
    '''
    4. Make a mirror image of this scheme on the other side of the two green hexagons
    at the bottom of column 7 from the left.
    '''
    
    tile7 = Tile(-1, 9)
    tile8 = Tile(-1, 10)
    
    tile7.draw('yellow')
    tile8.draw('yellow')
    
    tile9 = Tile(-1, 12)
    tile10 = Tile(-1, 13)
    
    tile9.draw('green')
    tile10.draw('green')
    
    
    '''
    5. Go back to first column on left side. make fourth hexagon from bottom of columns
    1 and 2 yellow, then the 4th and 5th hexagons in same row green.
    '''
    
    tile11 = Tile(-4, 1)
    tile12 = Tile(-4, 2)
    
    tile11.draw('yellow')
    tile12.draw('yellow')
    
    tile13 = Tile(-4, 4)
    tile14 = Tile(-4, 5)
    
    tile13.draw('green')
    tile14.draw('green')
    
    '''
    6. do a mirror image of this scheme on the other side of the two yellow hexagons on
    the 7th column from the left.
    '''
    
    tile11 = Tile(-4, 12)
    tile12 = Tile(-4, 13)
    
    tile11.draw('yellow')
    tile12.draw('yellow')
    
    tile13 = Tile(-4, 9)
    tile14 = Tile(-4, 10)
    
    tile13.draw('green')
    tile14.draw('green')
    
    
    '''
    7. repeat what you did in step three on the fourth row from the top left side with
    the same mirror image on other side of the two green hexagons in column 7.
    '''
    
    # step 3
    
    tile7 = Tile(4, 5)
    tile8 = Tile(4, 4)
    
    tile7.draw('yellow')
    tile8.draw('yellow')
    
    tile9 = Tile(4, 2)
    tile10 = Tile(4, 1)
    
    tile9.draw('green')
    tile10.draw('green')
    
    # mirroring from step 4
    
    tile7 = Tile(4, 9)
    tile8 = Tile(4, 10)
    
    tile7.draw('yellow')
    tile8.draw('yellow')
    
    tile9 = Tile(4, 12)
    tile10 = Tile(4, 13)
    
    tile9.draw('green')
    tile10.draw('green')
    
    
    
    g.plot(gold_boards=gold_boards, multiple=0)
