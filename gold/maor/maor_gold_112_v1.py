# Created by maor

from utils.reading_tasks import read_task
from hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle

task_index = 112
gold_boards = list(read_task(task_index)['gold_boards'])

HexagonsGame.start()

# description:
# task index: 112, image: P01C03T09, collection round: 1, category: conditional iteration, group: train
# agreement scores: [[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0]]

'''
1. With purple, paint the 7th column from the left.
'''
line1 = Line(start_tile=Tile(7,1), direction='down')
line1.draw('purple')

'''
2. With blue, in the 8th column starting at the top row, paint every other cell.
'''
from constants.constants import HEIGHT

for r in range(1, HEIGHT, 2):
  tile = Tile(column=8, row=r)
  tile.draw('blue')

'''
3. For each of the blue cells from step 2, paint descending diagonal lines to the
end of the grid with blue paint.
'''
for tile in Shape.get_color('blue'):
  line = Line(start_tile=tile, direction='down_right')
  line.draw('blue')

HexagonsGame.plot(gold_boards=gold_boards, multiple=0)
