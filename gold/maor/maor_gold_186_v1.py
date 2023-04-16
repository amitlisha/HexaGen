# Created by maor

from utils.reading_tasks import read_task
from src.hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle

task_index = 186
gold_boards = list(read_task(task_index)['gold_boards'])

HexagonsGame.start()

# description:
# task index: 186, image: P01C04T18, collection round: 1, category: conditions, group: train
# agreement scores: [[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 0.93, 0.93], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0]]

'''
1. In the first column from the left, color the 4th tile from the bottom purple.
'''
tile1 = Tile(column=1, row=-4)
tile1.draw('purple')

'''
2. In the 6th column from the right, color the top most tile green
'''
tile2 = Tile(column=-6, row=1)
tile2.draw('green')

'''
3. There is a straight line connecting these two points.  Starting with the purple
tile, the next tile in this line is purple.
'''
tile = tile1.neighbor(direction='up_right')
tile.draw('purple')

'''
4. The order of the whole line from left to right is purple, purple, green, purple,
green, purple, purple, purple, green, green, purple, purple, green.
'''
for c in ['green', 'purple', 'green', 'purple', 'purple', 'purple', 'green', 'green', 'purple', 'purple', 'green']:
  tile = tile.neighbor(direction='up_right')
  tile.draw(c)

'''
5. In the first column from the left, the lowermost tile is blue.
'''
tile1 = Tile(column=1, row=-1)
tile1.draw('blue')

'''
6. In the first column from the right, the topmost tile is orange.  There will be a
line connecting these two tiles.
'''
tile2 = Tile(column=-1, row=1)
tile2.draw('orange')

'''
7. The order of the tiles in this line from left to right is blue, blue, orange,
orange, blue, orange, orange, blue, blue, blue, orange, orange, blue, orange,
orange, blue, orange, orange.
'''
tile = tile1
for c in ['blue', 'orange', 'orange', 'blue', 'orange', 'orange', 'blue', 'blue', 'blue', 'orange', 'orange', 'blue', 'orange', 'orange', 'blue', 'orange', 'orange']:
  tile = tile.neighbor(direction='up_right')
  tile.draw(c)

'''
8. In the first column, 4th from the bottom is a purple tile.  In the 4th column,
3rd from the bottom is an orange tile. Connect these two tiles with two red
tiles, forming a straight line.
'''
line = Line(start_tile=Tile(1,-4), end_tile=Tile(4,-3), include_start_tile=False, include_end_tile=False)
line.draw('red')

'''
9. In the third column, 5th from the bottom is a green tile.  In the 6th column,
4th from the bottom is an orange tile. Connect these two tiles with two yellow
tiles, forming a straight line.
'''
line = Line(start_tile=Tile(3,-5), end_tile=Tile(6,-4), include_start_tile=False, include_end_tile=False)
line.draw('yellow')

'''
10. In the 5th column from the left, 6th from the bottom is a green tile.  In the
8th column, 5th from the bottom is a blue tile. Connect these two tiles with two
red tiles, forming a straight line.
'''
line = Line(start_tile=Tile(5,-6), end_tile=Tile(8,-5), include_start_tile=False, include_end_tile=False)
line.draw('red')

'''
11. In the 7th column from the left, 4th from the top is a purple tile. In the 10th
column from the left, the fifth tile down is blue. Connect these two tiles with
2 yellow tiles.
'''
line = Line(start_tile=Tile(7,4), end_tile=Tile(10,5), include_start_tile=False, include_end_tile=False)
line.draw('yellow')

'''
12. In the 9th column from the left, the third tile down is green. In the 12th
column from the left, the 4th tile down is orange.  Connect these tiles with 2
yellow lines to form a straight line.
'''
line = Line(start_tile=Tile(9,3), end_tile=Tile(12,4), include_start_tile=False, include_end_tile=False)
line.draw('yellow')

'''
13. In the 8th column from the right, the 2nd tile down is purple.  In the fifth
column from the right, third tile down is an orange tile.  Connect these tiles
with 2 red tiles to form a straight line.
'''
line = Line(start_tile=Tile(-8,2), end_tile=Tile(-5,3), include_start_tile=False, include_end_tile=False)
line.draw('red')

'''
14. In the 6th column from the right, the top most tile is green.  In the third row
from the right, the second tile down is blue.  Connect these two tiles with 2
red tiles to form a straight line.
'''
line = Line(start_tile=Tile(-6,1), end_tile=Tile(-3,2), include_start_tile=False, include_end_tile=False)
line.draw('red')

HexagonsGame.plot(gold_boards=gold_boards, multiple=0)
