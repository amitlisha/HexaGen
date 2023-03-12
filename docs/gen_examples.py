import sys
sys.path.append('../src')
sys.path.append('../utils')

from hexagons_classes import HexagonsGame, Tile, Shape, Line, Circle, Triangle

HexagonsGame.start()

vertices = [Tile(5, 5), Tile(8, 3), Tile(5, 7), Tile(8, 8), Tile(13, 6)]
Shape.polygon(vertices=vertices).draw('green')
Shape(vertices).draw('black')

file_name = input('please enter file name\n')
if file_name == '':
  HexagonsGame.plot()
else:
  HexagonsGame.plot(file_name = 'board_examples/' + file_name)


# edge

'''
neighbors
- ‘all’: all the neighbors of the shape
- ‘right’ / ‘left’: neighbors to the right/left of the shape
- ‘above’ / ‘below’: neighbors from above/below the shape
- ‘outside’ / ‘inside’: neighbors outside/inside the shape
- ‘white’: blank neighbors
'''

# polygon

# parallel

# triangle

# line attributes
# circle attributes

# tile neighbor