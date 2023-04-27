# Created by maor

from utils.reading_tasks import read_task
from src.hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle

task_index = 212
gold_boards = list(read_task(task_index)['gold_boards'])

HexagonsGame.start()

# description:
# task index: 212, image: P01C07T10, collection round: 1, category: composed objects, group: train
# agreement scores: [[1.0, 1.0, 1.0], [1.0, 0.67, 0.67], [1.0, 0.8, 0.8], [1.0, 1.0, 1.0]]

'''
1. On the second line from the left, second tile down, leave that tile blank, but
color in all tiles that touch it purple. Repeat this step twice, forming 2
purple circles directly and abutting the first one, total of 3 circles made in
left side of the grid.
'''
tile = Tile(2,2)
pattern = tile.neighbors()
pattern.draw('purple')

for i in range(2):
  pattern = pattern.copy_paste(shift_direction='down', spacing=0)

'''
2. on sixth tile from the left, starting at the top, color top three tiles orange
and the two centered tiles to the left of those three, and the one centered to
the left of those, orange. This will make an Orange triangle, repeat this,
making two more triangles abutting the bottom of the first triangle to the top
of the second, etc.
'''
line1 = Line(start_tile=Tile(6,1), length=3, direction='down')
line1.draw('orange')
line2 = Line(start_tile=Tile(5,2), length=2, direction='down')
line2.draw('orange')
tile = Tile(4,2)
tile.draw('orange')

triangle = line1 + line2 + tile
for i in range(2):
  triangle = triangle.copy_paste(shift_direction='down', spacing=0)

'''
3. Repeat these first 2 steps twice more forming three sets of each shape, the
rings of purple then the orange triangle, the point of the triangles leftmost.
For clarity the second set of purple rings begins on the 7th vertical row.
'''
all = Shape.get_color('purple') + Shape.get_color('orange')
for i in range(2):
  all = all.copy_paste(shift_direction='right', spacing=0)
'''
4. Each row will consist of First Purple rings, next orange triangles, repeat the
whole thing twice.
'''

HexagonsGame.plot(gold_boards=gold_boards, multiple=0)
