'''
This script was used to create plots for the projects USAGE.md file
'''

from src.hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle

HexagonsGame.start()

center_tile1 = Tile(4, 4)
circle1 = Circle(center_tile=center_tile1, radius=2)
circle1.draw('black')
center_tile2=Tile(14, 6)
circle2 = circle1.copy_paste(source=center_tile1, destination=center_tile2)
center_tile1.draw('yellow')
center_tile2.draw('red')

file_name = input('please enter file name\n')
if file_name == '':
  HexagonsGame.plot()
else:
  HexagonsGame.plot(file_name = 'board_examples/' + file_name)

