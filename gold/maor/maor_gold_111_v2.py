# Created by maor

from utils.reading_tasks import read_task
from src.hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle

task_index = 111
gold_boards = list(read_task(task_index)['gold_boards'])

HexagonsGame.start()

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
tile = Tile(column=8, row=1)
tile.draw('blue')

tile = Tile(column=tile.column, row=3)
tile.draw('blue')

tile = Tile(column=tile.column, row=5)
tile.draw('blue')

tile = Tile(column=tile.column, row=7)
tile.draw('blue')

tile = Tile(column=tile.column, row=9)
tile.draw('blue')

'''
3. In column # 9 paint second, fourth, sixth, eighth and tenth tiles from the top
blue.
'''
tile = Tile(column=9, row=2)
tile.draw('blue')

tile = Tile(column=9, row=4)
tile.draw('blue')

tile = Tile(column=9, row=6)
tile.draw('blue')

tile = Tile(column=9, row=8)
tile.draw('blue')

tile = Tile(column=9, row=10)
tile.draw('blue')

'''
4. In column # 10 paint second, fourth, sixth, eighth and tenth tiles from the top
blue.
'''
tile = Tile(column=10, row=2)
tile.draw('blue')

tile = Tile(column=10, row=4)
tile.draw('blue')

tile = Tile(column=10, row=6)
tile.draw('blue')

tile = Tile(column=10, row=8)
tile.draw('blue')

tile = Tile(column=10, row=10)
tile.draw('blue')

'''
5. In column # 11 paint third, fifth, seventh and ninth tiles from the top blue.
'''
tile = Tile(column=11, row=3)
tile.draw('blue')

tile = Tile(column=11, row=5)
tile.draw('blue')

tile = Tile(column=11, row=7)
tile.draw('blue')

tile = Tile(column=11, row=9)
tile.draw('blue')

'''
6. In column # 12 paint third, fifth, seventh and ninth tiles from the top blue.
'''
tile = Tile(column=12, row=3)
tile.draw('blue')

tile = Tile(column=12, row=5)
tile.draw('blue')

tile = Tile(column=12, row=7)
tile.draw('blue')

tile = Tile(column=12, row=9)
tile.draw('blue')

'''
7. In column # 13 paint fourth, sixth, eight and tenth tiles from the top blue.
'''
tile = Tile(column=13, row=4)
tile.draw('blue')

tile = Tile(column=13, row=6)
tile.draw('blue')

tile = Tile(column=13, row=8)
tile.draw('blue')

tile = Tile(column=13, row=10)
tile.draw('blue')

'''
8. In column # 14 paint fourth, sixth, eight and tenth tiles from the top blue.
'''
tile = Tile(column=14, row=4)
tile.draw('blue')

tile = Tile(column=14, row=6)
tile.draw('blue')

tile = Tile(column=14, row=8)
tile.draw('blue')

tile = Tile(column=14, row=10)
tile.draw('blue')

'''
9. In column # 15 paint fifth, seventh and ninth tiles from the top blue.
'''
tile = Tile(column=15, row=5)
tile.draw('blue')

tile = Tile(column=15, row=7)
tile.draw('blue')

tile = Tile(column=15, row=9)
tile.draw('blue')

'''
10. In column # 16 paint fifth, seventh and ninth tiles from the top blue.
'''
tile = Tile(column=16, row=5)
tile.draw('blue')

tile = Tile(column=16, row=7)
tile.draw('blue')

tile = Tile(column=16, row=9)
tile.draw('blue')

'''
11. In column # 17 paint sixth, eight and tenth tiles from the top blue.
'''
tile = Tile(column=17, row=6)
tile.draw('blue')

tile = Tile(column=17, row=8)
tile.draw('blue')

tile = Tile(column=17, row=10)
tile.draw('blue')

'''
12. In column # 18 paint sixth, eight and tenth tiles from the top blue.
'''
tile = Tile(column=17, row=6)
tile.draw('blue')

tile = Tile(column=17, row=8)
tile.draw('blue')

tile = Tile(column=17, row=10)
tile.draw('blue')

HexagonsGame.plot(gold_boards=gold_boards, multiple=0)
