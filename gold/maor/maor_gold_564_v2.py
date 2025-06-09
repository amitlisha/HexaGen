# Created by maor

from utils.reading_tasks import read_task
from hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle

task_index = 564
gold_boards = list(read_task(task_index)['gold_boards'])

HexagonsGame.start()

# description:
# task index: 564, image: P01C04T20, collection round: 0, category: conditions, group: train
# agreement scores: [[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0]]

'''
1. Draw a purple "0" starting by filling the three pick squares at the top of the
second column from the left, the three purple squares at the top of the fourth
column from the left, and then two purple squares in between at the top and the
bottom.
'''
HexagonsGame.record_step(step_name='zero1')
line1 = Line(start_tile=Tile(column=2, row=1), length=3, direction='down')
line1.draw('purple')
line2 = Line(start_tile=Tile(column=4, row=1), length=3, direction='down')
line2.draw('purple')
tile1 = Tile(column=3,row=1)
tile1.draw('purple')
tile2 = Tile(column=3,row=4)
tile2.draw('purple')
HexagonsGame.record_step(step_name='zero1_end')

'''
2. Draw an orange "0" next to the first in the same manner with 1 empty column in
between (so starting with the 6th column from the left).
'''
zero1 = HexagonsGame.get_record(step_names=['zero1'])
zero2 = zero1.copy_paste(source=zero1[0], destination=Tile(6,1))
zero2.draw('orange')

'''
3. Using the same spacing, draw an orange "0" next to that, and a purple "0" next
to that, the last two columns will be blank.
'''
zero3 = zero1.copy_paste(reference_shape=zero2, shift_direction='right', spacing=1)
zero3.draw('orange')

zero4 = zero1.copy_paste(reference_shape=zero3, shift_direction='right', spacing=1)
zero4.draw('purple')

'''
4. Draw 4 "0"s directly underneath the first 4, but with two empty squares between
the bottom of the middle of the first "0"s and the top-middle of the new "0s".
For the new "0"s the first one on the left is orange, the next three are purple.
'''
zero5 = zero1.copy_paste(reference_shape=zero1, shift_direction='down', spacing=2)
zero5.draw('orange')

zero6 = zero1.copy_paste(reference_shape=zero2, shift_direction='down', spacing=2)
zero6.draw('purple')

zero7 = zero1.copy_paste(reference_shape=zero3, shift_direction='down', spacing=2)
zero7.draw('purple')

zero8 = zero1.copy_paste(reference_shape=zero4, shift_direction='down', spacing=2)
zero8.draw('purple')

'''
5. Fill the two empty spaces in the middle of the first "0" in the top-left with
Green. Do the same for the left-most and right-most purple "0" in the bottom
row.
'''
for zero in [zero1, zero6, zero8]:
  zero.neighbors(criterion='inside').draw('green')

'''
6. For the two remaining purple "0"s, fill the two empty spaces in the middle of
the "0" with blue.
'''
for zero in [zero4, zero7]:
  zero.neighbors(criterion='inside').draw('blue')

'''
7. For the orange "0" in the bottom row and the orange "0" on the left in the top
row, fill the top square in the middle with green and the bottom square in the
middle with blue.
'''
for zero in [zero2, zero5]:
  zero.neighbors(criterion='inside').edge(direction='top').draw('green')
  zero.neighbors(criterion='inside').edge(direction='down').draw('blue')

'''
8. For the last orange "0" do the inverse, filling the top square in the middle
with blue and the bottom square with green.
'''
zero3.neighbors(criterion='inside').edge(direction='top').draw('blue')
zero3.neighbors(criterion='inside').edge(direction='down').draw('green')

HexagonsGame.plot(gold_boards=gold_boards, multiple=0)
