'''
This script was used to create plots for the projects USAGE.md file
'''

from hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle

HexagonsGame.start()

shape = Circle(center_tile=Tile(10, 5), radius=2)
shape += Circle(center_tile=Tile(10, 5), radius=3)
shape += Circle(center_tile=Tile(10, 5), radius=4)
shape.draw('black')

file_name = input('please enter file name\n')
if file_name == '':
  HexagonsGame.plot()
else:
  HexagonsGame.plot(file_name = 'board_examples/' + file_name)

