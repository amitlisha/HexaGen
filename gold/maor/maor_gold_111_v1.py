# Created by maor

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle

task_index = 111
gold_boards = list(read_task(task_index)['gold_boards'])

with Game() as g:
    
    # description:
    # task index: 111, image: P01C03T09, collection round: 1, category: conditional iteration, group: train
    # agreement scores: [[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0]]
    
    '''
    1. In column #7 starting at topmost tile fill all tiles downward purple.
    '''
    line1 = Line(start_tile=Tile(7,1), direction='down')
    line1.draw('purple')
    
    '''
    2. In column #8, paint topmost tile then third, fifth, seventh and ninth tiles from
    the top blue.
    '''
    for r in [1, 3, 5, 7, 9]:
      tile = Tile(column=8, row=r)
      tile.draw('blue')
    
    '''
    3. In column # 9 paint second, fourth, sixth, eighth and tenth tiles from the top
    blue.
    '''
    for r in [2, 4, 6, 8, 10]:
      tile = Tile(column=9, row=r)
      tile.draw('blue')
    
    '''
    4. In column # 10 paint second, fourth, sixth, eighth and tenth tiles from the top
    blue.
    '''
    for r in [2, 4, 6, 8, 10]:
      tile = Tile(column=10, row=r)
      tile.draw('blue')
    
    '''
    5. In column # 11 paint third, fifth, seventh and ninth tiles from the top blue.
    '''
    for r in [3, 5, 7, 9]:
      tile = Tile(column=11, row=r)
      tile.draw('blue')
    
    '''
    6. In column # 12 paint third, fifth, seventh and ninth tiles from the top blue.
    '''
    for r in [3, 5, 7, 9]:
      tile = Tile(column=12, row=r)
      tile.draw('blue')
    
    '''
    7. In column # 13 paint fourth, sixth, eight and tenth tiles from the top blue.
    '''
    for r in [4, 6, 8, 10]:
      tile = Tile(column=13, row=r)
      tile.draw('blue')
    
    '''
    8. In column # 14 paint fourth, sixth, eight and tenth tiles from the top blue.
    '''
    for r in [4, 6, 8, 10]:
      tile = Tile(column=14, row=r)
      tile.draw('blue')
    
    '''
    9. In column # 15 paint fifth, seventh and ninth tiles from the top blue.
    '''
    for r in [5, 7, 9]:
      tile = Tile(column=15, row=r)
      tile.draw('blue')
    
    '''
    10. In column # 16 paint fifth, seventh and ninth tiles from the top blue.
    '''
    for r in [5, 7, 9]:
      tile = Tile(column=16, row=r)
      tile.draw('blue')
    
    '''
    11. In column # 17 paint sixth, eight and tenth tiles from the top blue.
    '''
    for r in [6, 8, 10]:
      tile = Tile(column=17, row=r)
      tile.draw('blue')
    
    '''
    12. In column # 18 paint sixth, eight and tenth tiles from the top blue.
    '''
    for r in [6, 8, 10]:
      tile = Tile(column=18, row=r)
      tile.draw('blue')
    
    g.plot(gold_boards=gold_boards, multiple=0)
