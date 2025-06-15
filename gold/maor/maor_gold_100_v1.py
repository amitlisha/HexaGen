# Created by maor

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle

task_index = 100
gold_boards = list(read_task(task_index)['gold_boards'])

with Game() as g:
    
    # description:
    # task index: 100, image: P01C03T05, collection round: 1, category: conditional iteration, group: train
    # agreement scores: [[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [0.92, 1.0, 0.92], [1.0, 1.0, 1.0]]
    
    '''
    1. Paint the fourth hexagon in the seventh column orange and paint all of the
    hexagons surrounding it red.
    '''
    tile1 = Tile(column=7, row=4)
    tile1.draw('orange')
    tile1.neighbors().draw('red')
    
    '''
    2. Paint a diagonal line starting with the third hexagon yellow in column nine and
    alternating between red and yellow to end with a the first hexagon in column
    thirteen being yellow.
    '''
    for tile in [Tile(9,3), Tile(11,2), Tile(13,1)]:
      tile.draw('yellow')
    for tile in [Tile(10,2), Tile(12,1)]:
      tile.draw('red')
    
    '''
    3. Copy this pattern of alternating between red and yellow, starting with yellow
    from hexagon five in column nine and ending in the second to last hexagon in the
    last column.
    '''
    for tile in [Tile(9,5), Tile(11,6), Tile(13,7), Tile(15,8), Tile(17,9)]:
      tile.draw('yellow')
    for tile in [Tile(10,5), Tile(12,6), Tile(14,7), Tile(16,8), Tile(18,9)]:
      tile.draw('red')
    
    '''
    4. Copy the same pattern starting with the sixth hexagon in the seventh column,
    alternating between red and yellow to complete the column, and again starting
    with both hexagon three and five in column five to make three more diagonal
    lines.
    '''
    for tile in [Tile(7,6), Tile(7,8), Tile(7,10)]:
      tile.draw('yellow')
    for tile in [Tile(7,7), Tile(7,9)]:
      tile.draw('red')
    
    for tile in [Tile(5, 3), Tile(3, 2), Tile(1, 1)]:
      tile.draw('yellow')
    for tile in [Tile(4, 2), Tile(2, 1)]:
      tile.draw('red')
    
    for tile in [Tile(5, 5), Tile(3, 6), Tile(1, 7)]:
      tile.draw('yellow')
    for tile in [Tile(4, 5), Tile(2, 6)]:
      tile.draw('red')
    
    '''
    5. Paint the first hexagon in the seventh column red and the second hexagon in the
    same column yellow.
    '''
    tile = Tile(7,1)
    tile.draw('red')
    tile = Tile(7,2)
    tile.draw('yellow')
    
    g.plot(gold_boards=gold_boards, multiple=0)
