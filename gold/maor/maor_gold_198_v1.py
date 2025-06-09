# Created by maor

from utils.reading_tasks import read_task
from hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle

task_index = 198
gold_boards = list(read_task(task_index)['gold_boards'])

HexagonsGame.start()

# description:
# task index: 198, image: P01C07T03, collection round: 1, category: composed objects, group: train
# agreement scores: [[0.68, 0.23, 0.22], [0.45, 0.52, 0.11]]

'''
1. Color topmost leftmost tile red, leave the three tiles diagonally down to the
right of that tile, white, then alternate making a red diagonal line (connect
the third tile from top leftmost down, coloring the 5 tiles going upward
diagonally from there, red. Repeat again this diagonal, white and red pattern
Three times.
'''
tile = Tile(column=1, row=1)
tile.draw('red')

line1 = Line(start_tile=Tile(column=1, row=2), length=3, direction='up_right')
line1.draw('white')

line2 = Line(start_tile=Tile(column=1, row=3), length=5, direction='up_right')
line2.draw('red')

for i in range(3):
  line1 = Line(start_tile=line2.start_tile.neighbor('down'), direction='up_right')
  line1.draw('white')

  line2 = Line(start_tile=line1.start_tile.neighbor('down'), direction='up_right')
  line2.draw('red')

'''
2. Color purple every other row, below the longest hexagonal red line made in step
one. Start this alternating pattern with Bottommost, left most tile, skipping
the second row from left, but then on every other row to the right, (third,
fifth, seventh, etc.) color the vertical line(s) purple.
'''
for c in range(1,19,2):
  start_tile = Tile(column=c, row=-1)
  end_tile = Shape.get_column(c) * line2
  line = Line(start_tile=start_tile, end_tile=end_tile, include_end_tile=False)
  line.draw('purple')

HexagonsGame.plot(gold_boards=gold_boards, multiple=0)
