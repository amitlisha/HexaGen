from utils.reading_tasks import read_task
from src.hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle

task_index = 432
gold_board = list(read_task(task_index)['gold_boards'][-1])

HexagonsGame.start()

# procedure 432, image P02M08T04, collection round 2, category NONE, group train

'''
1. Fill in all but the last spots with purple in columns 3 and 17.
'''
purple_tiles = Shape.get_column(3) - Tile(3, -1) + Shape.get_column(17) - Tile(17, -1)
purple_tiles.draw('purple')
'''
2. Fill in the top and next to last spots of the 5th, 7th, 9th, 11th, 13, and 15th
columns with purple.
'''
for column in [5, 7, 9, 11, 13, 15]:
  Tile(column, 1).draw('purple')
  Tile(column, -2).draw('purple')
'''
3. Use red to fill the 3rd-7th spots in the 5th and 15th columns, and the 3rd and
7th spots in the 7th, 9th, 11th, and 13th columns.
'''
for column in [5, 15]:
  for row in range(3, 8):
    Tile(column, row).draw('red')
for column in [7, 9, 11, 13]:
  for row in [3, 7]:
    Tile(column, row).draw('red')
'''
4. Fill the 4th spots in the 6th-14th columns with blue.
'''
for column in range(6, 15):
  Tile(column, 4).draw('blue')
'''
5. Use orange to fill the 6th spots in the 6th-14th columns.
'''
for column in range(6, 15):
  Tile(column, 6).draw('orange')

HexagonsGame.plot(gold_board=gold_board)
