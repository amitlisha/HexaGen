import sys
sys.path.append('../src')
sys.path.append('../utils')

from hexagons_classes import HexagonsGame, Tile, Shape, Line, Circle, Triangle

HexagonsGame.start()

circle1 = Circle(center_tile = Tile(4, 4), radius = 2)
ref_shape = Shape([Tile(11, 6), Tile(11, 7), Tile(12, 6)])
circle1.draw('black')
ref_shape.draw('purple')
circle2 = circle1.copy_paste(shift_direction='right', spacing=1, reference_shape=ref_shape)

file_name = input('please enter file name\n')
if file_name == '':
  HexagonsGame.plot()
else:
  HexagonsGame.plot(file_name = 'board_examples/' + file_name)

# Shape
# copy_paste
# grid
# reflect
# rotate
# recolor

# boundary: outer / inner

# extreme: direction

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

# Line

# parallel

# circle

# triangle
