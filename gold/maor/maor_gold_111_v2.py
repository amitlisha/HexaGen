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
    line1 = Line(start_tile=Tile(1, 7), direction='down')
    line1.draw('purple')
    
    '''
    2. In column #8, paint topmost tile then third, fifth, seventh and ninth tiles from
    the top blue.
    '''
    tile = Tile(row=1, column=8)
    tile.draw('blue')
    
    tile = Tile(row=3, column=tile.column)
    tile.draw('blue')
    
    tile = Tile(row=5, column=tile.column)
    tile.draw('blue')
    
    tile = Tile(row=7, column=tile.column)
    tile.draw('blue')
    
    tile = Tile(row=9, column=tile.column)
    tile.draw('blue')
    
    '''
    3. In column # 9 paint second, fourth, sixth, eighth and tenth tiles from the top
    blue.
    '''
    tile = Tile(row=2, column=9)
    tile.draw('blue')
    
    tile = Tile(row=4, column=9)
    tile.draw('blue')
    
    tile = Tile(row=6, column=9)
    tile.draw('blue')
    
    tile = Tile(row=8, column=9)
    tile.draw('blue')
    
    tile = Tile(row=10, column=9)
    tile.draw('blue')
    
    '''
    4. In column # 10 paint second, fourth, sixth, eighth and tenth tiles from the top
    blue.
    '''
    tile = Tile(row=2, column=10)
    tile.draw('blue')
    
    tile = Tile(row=4, column=10)
    tile.draw('blue')
    
    tile = Tile(row=6, column=10)
    tile.draw('blue')
    
    tile = Tile(row=8, column=10)
    tile.draw('blue')
    
    tile = Tile(row=10, column=10)
    tile.draw('blue')
    
    '''
    5. In column # 11 paint third, fifth, seventh and ninth tiles from the top blue.
    '''
    tile = Tile(row=3, column=11)
    tile.draw('blue')
    
    tile = Tile(row=5, column=11)
    tile.draw('blue')
    
    tile = Tile(row=7, column=11)
    tile.draw('blue')
    
    tile = Tile(row=9, column=11)
    tile.draw('blue')
    
    '''
    6. In column # 12 paint third, fifth, seventh and ninth tiles from the top blue.
    '''
    tile = Tile(row=3, column=12)
    tile.draw('blue')
    
    tile = Tile(row=5, column=12)
    tile.draw('blue')
    
    tile = Tile(row=7, column=12)
    tile.draw('blue')
    
    tile = Tile(row=9, column=12)
    tile.draw('blue')
    
    '''
    7. In column # 13 paint fourth, sixth, eight and tenth tiles from the top blue.
    '''
    tile = Tile(row=4, column=13)
    tile.draw('blue')
    
    tile = Tile(row=6, column=13)
    tile.draw('blue')
    
    tile = Tile(row=8, column=13)
    tile.draw('blue')
    
    tile = Tile(row=10, column=13)
    tile.draw('blue')
    
    '''
    8. In column # 14 paint fourth, sixth, eight and tenth tiles from the top blue.
    '''
    tile = Tile(row=4, column=14)
    tile.draw('blue')
    
    tile = Tile(row=6, column=14)
    tile.draw('blue')
    
    tile = Tile(row=8, column=14)
    tile.draw('blue')
    
    tile = Tile(row=10, column=14)
    tile.draw('blue')
    
    '''
    9. In column # 15 paint fifth, seventh and ninth tiles from the top blue.
    '''
    tile = Tile(row=5, column=15)
    tile.draw('blue')
    
    tile = Tile(row=7, column=15)
    tile.draw('blue')
    
    tile = Tile(row=9, column=15)
    tile.draw('blue')
    
    '''
    10. In column # 16 paint fifth, seventh and ninth tiles from the top blue.
    '''
    tile = Tile(row=5, column=16)
    tile.draw('blue')
    
    tile = Tile(row=7, column=16)
    tile.draw('blue')
    
    tile = Tile(row=9, column=16)
    tile.draw('blue')
    
    '''
    11. In column # 17 paint sixth, eight and tenth tiles from the top blue.
    '''
    tile = Tile(row=6, column=17)
    tile.draw('blue')
    
    tile = Tile(row=8, column=17)
    tile.draw('blue')
    
    tile = Tile(row=10, column=17)
    tile.draw('blue')
    
    '''
    12. In column # 18 paint sixth, eight and tenth tiles from the top blue.
    '''
    tile = Tile(row=6, column=18)
    tile.draw('blue')
    
    tile = Tile(row=8, column=18)
    tile.draw('blue')
    
    tile = Tile(row=10, column=18)
    tile.draw('blue')
    
    g.plot(gold_boards=gold_boards, multiple=0)
