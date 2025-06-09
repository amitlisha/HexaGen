# Created by maor

from utils.reading_tasks import read_task
from hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle

task_index = 210
gold_boards = list(read_task(task_index)['gold_boards'])

HexagonsGame.start()

# description:
# task index: 210, image: P01C07T10, collection round: 1, category: composed objects, group: train
# agreement scores: [[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [0.5, 0.5, 1.0]]

'''
1. Make a purple circle with a center at the second tile of the second column.
Leave the center blank.
'''
circle = Circle(center_tile=Tile(2,2))
circle.draw('purple')

'''
2. Make a triangle pointing left with six colored orange tiles, with the leftmost
point touching the right side of the purple circle.
'''
start_tile = circle.edge('down_right').neighbor('up_right')

triangle = Triangle(start_tile=start_tile, point='left', start_tile_type='side', side_length=3)
triangle.draw('orange')

'''
3. Copy this pattern to the right and down leaving no spaces between the shapes.
'''
pattern = circle + triangle
right_copy = pattern.grid(shift_direction='right', spacing=0)
right_copy.grid(shift_direction='down', spacing=0)

HexagonsGame.plot(gold_boards=gold_boards, multiple=0)
