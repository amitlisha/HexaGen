# Created by maor

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle

task_index = 513
gold_boards = list(read_task(task_index)['gold_boards'])

with Game() as g:
    
    # description:
    # task index: 513, image: P01C04T20, collection round: 0, category: conditions, group: train
    # agreement scores: [[0.13, 0, 0], [0.04, 0, 0], [0.44, 0, 0], [0.46, 0, 0], [0.48, 0, 0], [0.49, 0, 0], [0.39, 0, 0]]
    
    '''
    1. Starting at the upper left, in the third column, paint the second and third
    tiles from the top green and all the tiles adjacent to them purple.
    '''
    def pattern1(c, r, color):
      tile1 = Tile(row=r, column=c)
      tile1.draw(color)
      tile2 = Tile(row=r+1, column=c)
      tile2.draw(color)
    
      tiles = tile1+tile2
      tiles.neighbors().draw('purple')
    
    pattern1(3, 2, 'green')
    
    '''
    2. Repeat this color pattern of green surrounded by purple, starting with green on
    the second and third tiles from the bottom in the fourth column from the right,
    and once more, starting with green on the second and third tiles from the bottom
    in the seventh column from the left.
    '''
    pattern1(-4, -3, 'green')
    
    pattern1(7, -3, 'green')
    
    '''
    3. Duplicate this shape, but beginning with blue in the second and third tiles from
    the top in the fourth column from the right and in the second and third tiles
    from the bottom in the eighth column from the right, surrounding each pair of
    blue tiles with a purple border.
    '''
    pattern1(-4, 2, 'blue')
    
    pattern1(-8, -3, 'blue')
    
    '''
    4. In the third column from the left, paint the second tile from the bottom blue
    and the one directly above it green.
    '''
    
    def patterns2(c, r, color1, color2):
      tile1 = Tile(row=r, column=c)
      tile1.draw(color1)
      tile2 = Tile(row=r-1, column=c)
      tile2.draw(color2)
      pair = tile1+tile2
    
    patterns2(3,-2,'blue', 'green')
    
    '''
    5. Paint the second tile from the top green and the tile directly below it blue in
    the seventh column from the left.
    '''
    patterns2(7, 3, 'blue', 'green')
    
    '''
    6. In the eighth column from the right, paint the second tile from the top blue and
    the one directly below it green.
    '''
    patterns2(-8, 3, 'green', 'blue')
    
    '''
    7. Paint each tile adjacent to the three pairs of blue and green tiles orange.
    '''
    neighbours = Shape.get_color('green').neighbors(criterion='white') + Shape.get_color('blue').neighbors(criterion='white')
    neighbours.draw('orange')
    
    g.plot(gold_boards=gold_boards, multiple=0)
