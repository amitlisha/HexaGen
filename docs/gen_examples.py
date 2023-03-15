# import sys
# sys.path.append('../src')

from src.hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle

HexagonsGame.start()

HexagonsGame.record_step(step_name='1')
Tile(column=7, row=5).neighbors().draw(color='yellow')

print(HexagonsGame.get_record(step_names=['1'])._linds)

file_name = input('please enter file name\n')
if file_name == '':
  HexagonsGame.plot()
else:
  HexagonsGame.plot(file_name = 'board_examples/' + file_name)

