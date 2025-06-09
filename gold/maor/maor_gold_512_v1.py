# Created by maor

from utils.reading_tasks import read_task
from hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle

task_index = 512
gold_boards = list(read_task(task_index)['gold_boards'])

HexagonsGame.start()

# description:
# task index: 512, image: P01C04T20, collection round: 0, category: conditions, group: train
# agreement scores: [[0, 1.0, 0], [1.0, 0.75, 0.75], [1.0, 0.83, 0.83], [0.46, 0.84, 0.43], [0.51, 0.85, 0.47], [0.55, 0.86, 0.52], [0.46, 0.91, 0.44], [0.47, 0.91, 0.45], [0.5, 0.91, 0.47], [0.51, 0.91, 0.49], [0.52, 0.91, 0.5], [0.53, 0.92, 0.51], [0.55, 0.92, 0.52], [0.46, 0.94, 0.45]]

'''
1. In the third column, colour in green tiles number two and three from the top.
'''
tile1 = Tile(column=3, row=2)
tile1.draw('green')
tile2 = Tile(column=3, row=3)
tile2.draw('green')

'''
2. In the seventh column, colour in green tiles number two and three from the
bottom.
'''
tile1 = Tile(column=7, row=-2)
tile1.draw('green')
tile2 = Tile(column=7, row=-3)
tile2.draw('green')

'''
3. In the fifteenth column, colour in green tiles number two and three from the
bottom.
'''
tile1 = Tile(column=15, row=-2)
tile1.draw('green')
tile2 = Tile(column=15, row=-3)
tile2.draw('green')

'''
4. Colour in purple all the white tiles directly adjacent to green tiles.
'''
Shape.get_color('green').neighbors().draw('purple')

'''
5. In the fifteenth column, colour in blue tiles number two and three from the top.
'''
tile1 = Tile(column=15, row=2)
tile1.draw('blue')
tile2 = Tile(column=15, row=3)
tile2.draw('blue')

'''
6. In the eleventh column, colour in blue tiles number two and three from the
bottom.
'''
tile1 = Tile(column=11, row=-2)
tile1.draw('blue')
tile2 = Tile(column=11, row=-3)
tile2.draw('blue')

'''
7. Colour in purple all the white tiles directly adjacent to blue tiles.
'''
Shape.get_color('blue').neighbors(criterion='white').draw('purple')

'''
8. In the third column, colour in green tile number three from the bottom.
'''
tile = Tile(column=3, row=-3)
tile.draw('green')

'''
9. In the third column, colour in blue tile number two from the bottom.
'''
tile = Tile(column=3, row=-2)
tile.draw('blue')

'''
10. In the seventh column, colour in green tile number two from the top.
'''
tile = Tile(column=7, row=2)
tile.draw('green')

'''
11. In the seventh column, colour in blue tile number 3 from the top.
'''
tile = Tile(column=7, row=3)
tile.draw('blue')

'''
12. In the eleventh column, colour in blue tile number two from the top.
'''
tile = Tile(column=11, row=2)
tile.draw('blue')

'''
13. In the eleventh column, colour in green tile number 3 from the top.
'''
tile = Tile(column=11, row=3)
tile.draw('green')

'''
14. Colour orange the tiles adjacent to the blue/green duos.
'''
Shape.get_color('green').neighbors(criterion='white').draw('orange')
Shape.get_color('blue').neighbors(criterion='white').draw('orange')

HexagonsGame.plot(gold_boards=gold_boards, multiple=0)
