# Created by maor

from utils.reading_tasks import read_task
from hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle

task_index = 534
gold_boards = list(read_task(task_index)['gold_boards'])

HexagonsGame.start()

# description:
# task index: 534, image: P01C04T04, collection round: 0, category: conditions, group: train
# agreement scores: [[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [0.99, 1.0, 0.99], [0.96, 1.0, 0.96], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0]]

'''
1. Color tiles 2 through 5 in column 1 purple.
'''
line = Line(start_tile=Tile(column=1,row=2), end_tile=Tile(column=1,row=5))
line.draw('purple')
'''
2. Repeat step 1 in columns 9, 13, 15 and 17.
'''
for c in [9,13,15,17]:
  line = Line(start_tile=Tile(column=c, row=2), end_tile=Tile(column=c, row=5))
  line.draw('purple')

'''
3. Color tiles 2 through 5 in column 3 blue.
'''
line = Line(start_tile=Tile(column=3,row=2), end_tile=Tile(column=3,row=5))
line.draw('purple')

'''
4. Repeat step 3 in columns 5, 7 and 11.
'''
for c in [3,5,7,11]:
  line = Line(start_tile=Tile(column=c, row=2), end_tile=Tile(column=c, row=5))
  line.draw('blue')

'''
5. Color the tile above each purple column orange.
'''
Shape.get_color('purple').neighbors(criterion='above').draw('orange')

'''
6. Color the tile above each blue column green.
'''
Shape.get_color('blue').neighbors(criterion='above').draw('green')

'''
7. Color tiles 6 through 9 in column 2 blue and then tile 10 green.
'''
HexagonsGame.record_step(step_name='step_7')
line = Line(start_tile=Tile(column=2,row=6), end_tile=Tile(column=2,row=9))
line.draw('blue')

tile=Tile(column=2, row=10)
tile.draw('green')

HexagonsGame.record_step(step_name='step_7_end')

'''
8. Repeat step 7 for columns 6, 8, 16 and 18.
'''
shape = HexagonsGame.get_record(step_names=['step_7'])

for c in [6,8,16,18]:
  shape.copy_paste(source=Tile(column=2,row=6), destination=Tile(column=c, row=6))

'''
9. Color tiles 6 through 9 in column 4 purple and then tile 10 orange.
'''
HexagonsGame.record_step(step_name='step_9')
line = Line(start_tile=Tile(column=4,row=6), end_tile=Tile(column=4,row=9))
line.draw('purple')

tile=Tile(column=4, row=10)
tile.draw('orange')

HexagonsGame.record_step(step_name='step_9_end')

'''
10. Repeat step 9 for columns 10, 12 and 14.
'''
shape = HexagonsGame.get_record(step_names=['step_9'])

for c in [10,12,14]:
  shape.copy_paste(source=Tile(column=4,row=6), destination=Tile(column=c, row=6))

HexagonsGame.plot(gold_boards=gold_boards, multiple=0)
