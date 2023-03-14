# import sys
# sys.path.append('../src')

from src.hexagons_classes import HexagonsGame, Tile, Shape, Line, Circle, Triangle

HexagonsGame.start()

HexagonsGame.start(width=8, height=4)
tile = Tile(4, 2)
tile.draw('orange')
tile.neighbors().draw('purple')
gold_board = HexagonsGame.board_state

HexagonsGame.start(width=8, height=4)
tile = Tile(5, 2)
tile.draw('orange')
tile.neighbors().draw('purple')
HexagonsGame.plot(gold_board=gold_board, file_name='hexagonsgame_plot_gold')

file_name = input('please enter file name\n')
if file_name == '':
  HexagonsGame.plot()
else:
  HexagonsGame.plot(file_name = 'board_examples/' + file_name)


# line attributes
# circle attributes

