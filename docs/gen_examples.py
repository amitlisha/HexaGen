# import sys
# sys.path.append('../src')

from src.hexagons_classes import HexagonsGame, Tile, Shape, Line, Circle, Triangle

HexagonsGame.start()

center = Tile(column=7, row=5)
center.draw(color='yellow')
center.neighbors().draw(color='red')

file_name = input('please enter file name\n')
if file_name == '':
  HexagonsGame.plot()
else:
  HexagonsGame.plot(file_name = 'board_examples/' + file_name)


# line attributes
# circle attributes

