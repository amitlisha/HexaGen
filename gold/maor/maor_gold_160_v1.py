# Created by maor

from utils.reading_tasks import read_task
from hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle

task_index = 160
gold_boards = list(read_task(task_index)['gold_boards'])

HexagonsGame.start()

# description:
# task index: 160, image: P01C04T02, collection round: 1, category: conditions, group: train
# agreement scores: [[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0]]

'''
1. Leaving the center tile blank, draw a blue flower, using six tiles in the lower
left corner.
'''
flower1 = Tile(2,-2).neighbors()
flower1.draw('blue')

'''
2. Directly above the blue flower, draw a purple flower in the same way, and an
orange flower above that one, so that the three flowers touch forming a stack.
'''
flower2 = flower1.copy_paste(shift_direction='up', spacing=0, reference_shape=flower1)
flower2.draw('purple')

flower3 = flower2.copy_paste(shift_direction='up', spacing=0, reference_shape=flower2)
flower3.draw('orange')

'''
3. Draw a similar stack of flowers with their blank centers in the sixth column
from the left, starting with purple at the bottom, then orange, then blue, going
up, so that there is a blank column between the two stacks of flowers.
'''
flower1 = Tile(6,-2).neighbors()
flower1.draw('purple')

flower2 = flower1.copy_paste(shift_direction='up', spacing=0, reference_shape=flower1)
flower2.draw('orange')

flower3 = flower2.copy_paste(shift_direction='up', spacing=0, reference_shape=flower2)
flower3.draw('blue')

'''
4. Repeat this shape pattern two more times using orange, blue, purple centered in
the tenth column and blue, purple, orange centered in the fourteenth column,
counting colors from bottom to top.
'''
flower1 = Tile(10,-2).neighbors()
flower1.draw('orange')

flower2 = flower1.copy_paste(shift_direction='up', spacing=0, reference_shape=flower1)
flower2.draw('blue')

flower3 = flower2.copy_paste(shift_direction='up', spacing=0, reference_shape=flower2)
flower3.draw('purple')

flower1 = Tile(14,-2).neighbors()
flower1.draw('blue')

flower2 = flower1.copy_paste(shift_direction='up', spacing=0, reference_shape=flower1)
flower2.draw('purple')

flower3 = flower2.copy_paste(shift_direction='up', spacing=0, reference_shape=flower2)
flower3.draw('orange')

'''
5. Place an orange center in each blue flower, a blue center in each purple flower,
and a purple center in each orange flower.
'''
blues = Shape.get_color('blue')
blues.neighbors(criterion='inside').draw('orange')

purples = Shape.get_color('purple')
purples.neighbors(criterion='inside').draw('blue')

oranges = Shape.get_color('orange')
oranges.neighbors(criterion='inside').draw('purple')

HexagonsGame.plot(gold_boards=gold_boards, multiple=0)
