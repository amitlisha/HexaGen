# Created by by maor

from utils.reading_tasks import read_task
from src.hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle

task_index = 221
gold_boards = list(read_task(task_index)['gold_boards'])

HexagonsGame.start()

# description:
# task index: 221, image: P01C08T03, collection round: 1, category: other, group: train
# agreement scores: [[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0]]

'''
1. In column four, paint tiles 3-8 green, omitting tile 6.
'''
Line(start_tile=Tile(4,3), end_tile=Tile(4,8)).draw('green')
Tile(4,6).draw('white')

'''
2. In column five, paint tiles 4-9 red.
'''
Line(start_tile=Tile(5,4), end_tile=Tile(5,9)).draw('red')

'''
3. In column six, paint tiles 4-8 purple.
'''
Line(start_tile=Tile(6,4), end_tile=Tile(6,8)).draw('purple')

'''
4. In column seven, paint tiles 5-7 orange.
'''
Line(start_tile=Tile(7,5), end_tile=Tile(7,7)).draw('orange')

'''
5. In column eight, paint tile 3 blue, and tiles 5-6 yellow.
'''
Tile(8,3).draw('blue')
Line(start_tile=Tile(8,5), end_tile=Tile(8,6)).draw('yellow')

'''
6. In column nine, paint tiles 4-8 blue.
'''
Line(start_tile=Tile(9,4), end_tile=Tile(9,8)).draw('blue')

'''
7. In column ten, paint tile 3 blue, and tiles 5-6 yellow.
'''
Tile(10,3).draw('blue')
Line(start_tile=Tile(10,5), end_tile=Tile(10,6)).draw('yellow')

'''
8. In column eleven, paint tiles 5-7 orange.
'''
Line(start_tile=Tile(11,5), end_tile=Tile(11,7)).draw('orange')

'''
9. In column twelve, paint tiles 4-8 purple.
'''
Line(start_tile=Tile(12,4), end_tile=Tile(12,8)).draw('purple')

'''
10. In column thirteen, paint tiles 4-9 red.
'''
Line(start_tile=Tile(13,4), end_tile=Tile(13,9)).draw('red')

'''
11. In column fourteen, paint tiles 3-8 green, omitting tile 6.
'''
Line(start_tile=Tile(14,3), end_tile=Tile(14,8)).draw('green')
Tile(14,6).draw('white')

HexagonsGame.plot(gold_boards=gold_boards, multiple=0)
