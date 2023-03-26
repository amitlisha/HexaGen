'''
This script was used to create plots for the projects USAGE.md file
'''

from src.hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle

HexagonsGame.start()


file_name = input('please enter file name\n')
if file_name == '':
  HexagonsGame.plot()
else:
  HexagonsGame.plot(file_name = 'board_examples/' + file_name)

