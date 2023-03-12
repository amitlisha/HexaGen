import sys
sys.path.append('../src')
sys.path.append('../utils')

from hexagons_classes import HexagonsGame, Tile, Shape, Line, Circle, Triangle

HexagonsGame.start()

circle = Circle(center_tile=Tile(15, 8), radius=2)
circle.draw('red')
line = Line(start_tile=Tile(1, 1), direction='down_right', end_tiles=circle)
line.draw('blue')

file_name = 'board_examples/' + input('please enter file name\n')
HexagonsGame.plot(file_name = file_name)
# HexagonsGame.plot()

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
