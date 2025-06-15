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
    c = 3
    r = 2
    
    tile1 = Tile(column=c, row=r)
    tile1.draw('green')
    tile2 = Tile(column=c, row=r+1)
    tile2.draw('green')
    
    tiles = tile1+tile2
    tiles.neighbors().draw('purple')
    
    '''
    2. Repeat this color pattern of green surrounded by purple, starting with green on
    the second and third tiles from the bottom in the fourth column from the right,
    and once more, starting with green on the second and third tiles from the bottom
    in the seventh column from the left.
    '''
    c = -4
    r = -3
    
    tile1 = Tile(column=c, row=r)
    tile1.draw('green')
    tile2 = Tile(column=c, row=r+1)
    tile2.draw('green')
    
    tiles = tile1+tile2
    tiles.neighbors().draw('purple')
    
    c = 7
    r = -3
    
    tile1 = Tile(column=c, row=r)
    tile1.draw('green')
    tile2 = Tile(column=c, row=r+1)
    tile2.draw('green')
    
    tiles = tile1+tile2
    tiles.neighbors().draw('purple')
    
    '''
    3. Duplicate this shape, but beginning with blue in the second and third tiles from
    the top in the fourth column from the right and in the second and third tiles
    from the bottom in the eighth column from the right, surrounding each pair of
    blue tiles with a purple border.
    '''
    c = -4
    r = 2
    
    tile1 = Tile(column=c, row=r)
    tile1.draw('blue')
    tile2 = Tile(column=c, row=r+1)
    tile2.draw('blue')
    
    tiles = tile1+tile2
    tiles.neighbors().draw('purple')
    
    c = -8
    r = -3
    
    tile1 = Tile(column=c, row=r)
    tile1.draw('blue')
    tile2 = Tile(column=c, row=r+1)
    tile2.draw('blue')
    
    tiles = tile1+tile2
    tiles.neighbors().draw('purple')
    
    '''
    4. In the third column from the left, paint the second tile from the bottom blue
    and the one directly above it green.
    '''
    tile1 = Tile(column=3, row=-2)
    tile1.draw('blue')
    tile2 = Tile(column=3, row=-3)
    tile2.draw('green')
    
    pair1 = tile1+tile2
    
    '''
    5. Paint the second tile from the top green and the tile directly below it blue in
    the seventh column from the left.
    '''
    tile1 = Tile(column=7, row=2)
    tile1.draw('green')
    tile2 = Tile(column=7, row=3)
    tile2.draw('blue')
    
    pair2 = tile1+tile2
    
    '''
    6. In the eighth column from the right, paint the second tile from the top blue and
    the one directly below it green.
    '''
    tile1 = Tile(column=-8, row=2)
    tile1.draw('blue')
    tile2 = Tile(column=-8, row=3)
    tile2.draw('green')
    
    pair3 = tile1+tile2
    
    '''
    7. Paint each tile adjacent to the three pairs of blue and green tiles orange.
    '''
    for pair in [pair1, pair2, pair3]:
      pair.neighbors().draw('orange')
    
    g.plot(gold_boards=gold_boards, multiple=0)
