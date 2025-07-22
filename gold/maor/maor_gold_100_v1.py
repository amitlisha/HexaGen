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
    tile1 = Tile(row=4, column=7)
    tile1.draw('orange')
    tile1.neighbors().draw('red')
    
    '''
    2. Paint a diagonal line starting with the third hexagon yellow in column nine and
    alternating between red and yellow to end with a the first hexagon in column
    thirteen being yellow.
    '''
    for tile in [Tile(3, 9), Tile(2, 11), Tile(1, 13)]:
      tile.draw('yellow')
    for tile in [Tile(2, 10), Tile(1, 12)]:
      tile.draw('red')
    
    '''
    3. Copy this pattern of alternating between red and yellow, starting with yellow
    from hexagon five in column nine and ending in the second to last hexagon in the
    last column.
    '''
    for tile in [Tile(5, 9), Tile(6, 11), Tile(7, 13), Tile(8, 15), Tile(9, 17)]:
      tile.draw('yellow')
    for tile in [Tile(5, 10), Tile(6, 12), Tile(7, 14), Tile(8, 16), Tile(9, 18)]:
      tile.draw('red')
    
    '''
    4. Copy the same pattern starting with the sixth hexagon in the seventh column,
    alternating between red and yellow to complete the column, and again starting
    with both hexagon three and five in column five to make three more diagonal
    lines.
    '''
    for tile in [Tile(6, 7), Tile(8, 7), Tile(10, 7)]:
      tile.draw('yellow')
    for tile in [Tile(7, 7), Tile(9, 7)]:
      tile.draw('red')
    
    for tile in [Tile(3, 5), Tile(2, 3), Tile(1, 1)]:
      tile.draw('yellow')
    for tile in [Tile(2, 4), Tile(1, 2)]:
      tile.draw('red')
    
    for tile in [Tile(5, 5), Tile(6, 3), Tile(7, 1)]:
      tile.draw('yellow')
    for tile in [Tile(5, 4), Tile(6, 2)]:
      tile.draw('red')
    
    '''
    5. Paint the first hexagon in the seventh column red and the second hexagon in the
    same column yellow.
    '''
    tile = Tile(1, 7)
    tile.draw('red')
    tile = Tile(2, 7)
    tile.draw('yellow')
    
    g.plot(gold_boards=gold_boards, multiple=0)
