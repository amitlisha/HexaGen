# Created by maor

from utils.reading_tasks import read_task
from src.hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle

task_index = 537
gold_boards = list(read_task(task_index)['gold_boards'])

HexagonsGame.start()

# description:
# task index: 537, image: P01C04T04, collection round: 0, category: conditions, group: train
# agreement scores: [[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0]]

'''
1. Choose the color orange and fill in the topmost hexagon in column one from the
left.
'''
HexagonsGame.record_step(step_name='1')
tile = Tile(column=1, row=1)
tile.draw('orange')

'''
2. Choose the color purple and fill in the four hexagons directly below the orange
hexagon in column one.
'''
for r in range(4):
  tile=tile.neighbor('down')
  tile.draw('purple')
HexagonsGame.record_step(step_name='1_end')

'''
3. Repeat this color scheme exactly for columns nine, thirteen, fifteen, and
seventeen.
'''
shape = HexagonsGame.get_record(step_names=['1'])
for c in [9,13,15,17]:
  shape.copy_paste(source=shape[0], destination=Tile(column=c, row=shape[0].row))

'''
4. Choose the color green and fill in the topmost hexagon in column three from the
left.
'''
HexagonsGame.record_step(step_name='2')
tile = Tile(column=3, row=1)
tile.draw('green')

'''
5. Choose the color blue and fill in the four hexagons directly below the green
hexagon.
'''
for r in range(4):
  tile=tile.neighbor('down')
  tile.draw('blue')
HexagonsGame.record_step(step_name='2_end')

'''
6. Repeat the green/blue color scheme for columns five, seven, and eleven exactly
as column three.
'''
shape = HexagonsGame.get_record(step_names=['2'])
for c in [5,7,11]:
  shape.copy_paste(source=shape[0], destination=Tile(column=c, row=shape[0].row))

'''
7. Choose the color green and fill in the most bottom hexagon in column two from
the left.
'''
HexagonsGame.record_step(step_name='3')
tile = Tile(column=2, row=-1)
tile.draw('green')

'''
8. Choose the color blue and fill in the four hexagons directly above the green
hexagon in column two.
'''
for r in range(4):
  tile=tile.neighbor('up')
  tile.draw('blue')
HexagonsGame.record_step(step_name='3_end')

'''
9. Repeat the green/blue color scheme in the same fashion as column two for columns
six, eight, sixteen, and eighteen.
'''
shape = HexagonsGame.get_record(step_names=['3'])
for c in [6,8,16,18]:
  shape.copy_paste(source=shape[0], destination=Tile(column=c, row=shape[0].row))

'''
10. Choose the color orange and fill in the most bottom hexagon in column four from
the left.
'''
HexagonsGame.record_step(step_name='4')
tile = Tile(column=4, row=-1)
tile.draw('orange')

'''
11. choose the color purple and fill in the four hexagons directly above the orange
hexagon in column four.
'''
for r in range(4):
  tile=tile.neighbor('up')
  tile.draw('purple')

HexagonsGame.record_step(step_name='4_end')

'''
12. Repeat the orange/purple color scheme in the same fashion as column four for
columns ten, twelve, and fourteen.
'''
shape = HexagonsGame.get_record(step_names=['4'])
for c in[10, 12, 14]:
  shape.copy_paste(source=shape[0], destination=Tile(column=c, row=shape[0].row))

HexagonsGame.plot(gold_boards=gold_boards, multiple=0)
