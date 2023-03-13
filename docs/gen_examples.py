# import sys
# sys.path.append('../src')

from src.hexagons_classes import HexagonsGame, Tile, Shape, Line, Circle, Triangle

HexagonsGame.start()

circle1 = Circle(center_tile=Tile(7, 5), radius=4)
circle1.draw('green')
circle2 = Circle(center_tile=Tile(-7, 5), radius=4)
circle2.draw('blue')
(circle1 * circle2).draw('red')

file_name = input('please enter file name\n')
if file_name == '':
  HexagonsGame.plot()
else:
  HexagonsGame.plot(file_name = 'board_examples/' + file_name)


# line attributes
# circle attributes

