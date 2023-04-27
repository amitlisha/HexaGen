# Created by maor

from utils.reading_tasks import read_task
from src.hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle

task_index = 576
gold_boards = list(read_task(task_index)['gold_boards'])

HexagonsGame.start()

# description:
# task index: 576, image: P01C04T04, collection round: 0, category: conditions, group: train
# agreement scores: [[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0]]

'''
1. Starting at the top of the first column on the left, paint the first hexagon
orange.
'''
tile = Tile(column=1, row=1)
tile.draw('orange')

'''
2. Paint the next 4 hexagons down in the first column purple
'''
line = Line(start_tile=tile, direction='down', length=4, include_start_tile=False)
line.draw('purple')

'''
3. Copy the same pattern from column 1 into columns 9, 13, 15, and 17.
'''
pattern = Shape.get_column(1)
for c in [9, 13, 15, 17]:
  pattern.copy_paste(source=Tile(1,1), destination=Tile(c,1))

'''
4. In the second column from the left, paint the 6th through the 9th hexagons blue
and the last hexagon green.
'''
line = Line(start_tile=Tile(column=2, row=6), end_tile=Tile(column=2, row=9))
line.draw('blue')
tile=Tile(column=2, row=-1)
tile.draw('green')

'''
5. Copy the same pattern from column 2 into columns 6, 8, 16, and 18.
'''
pattern = Shape.get_column(2)
for c in [6, 8, 16, 18]:
  pattern.copy_paste(source=Tile(2,1), destination=Tile(c,1))

'''
6. In the 3rd column from the left, paint the top hexagon green and the next four
hexagons blue.
'''
tile = Tile(column=3, row=1)
tile.draw('green')

line = Line(start_tile=tile, direction='down', length=4, include_start_tile=False)
line.draw('blue')

'''
7. Copy the pattern from the 3rd column into columns 5, 7, and 11.
'''
pattern = Shape.get_column(3)
for c in [5, 7, 11]:
  pattern.copy_paste(source=Tile(3,1), destination=Tile(c,1))

'''
8. In the 4th column from the left, paint the 6th through the 9th hexagons purple
and the last hexagon orange.
'''
line = Line(start_tile=Tile(column=4, row=6), end_tile=Tile(column=4, row=9))
line.draw('purple')
tile=Tile(column=4, row=-1)
tile.draw('orange')

'''
9. Use the pattern from column 4 in columns 10, 12, and 14.
'''
pattern = Shape.get_column(4)
for c in [10, 12, 14]:
  pattern.copy_paste(source=Tile(4,1), destination=Tile(c,1))

HexagonsGame.plot(gold_boards=gold_boards, multiple=0)
