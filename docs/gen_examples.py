# import sys
# sys.path.append('../src')

from src.hexagons_classes import HexagonsGame, Tile, Shape, Line, Circle, Triangle

HexagonsGame.start()

# 1. Draw a purple circle centered at the tile on
triangle = Triangle(start_tile=Tile(3, 5), point='left', start_tile_type='side', side_length=5)
triangle.draw('purple')

record_step(step):
get_record(steps)

file_name = input('please enter file name\n')
if file_name == '':
  HexagonsGame.plot()
else:
  HexagonsGame.plot(file_name = 'board_examples/' + file_name)


# line attributes
# circle attributes

