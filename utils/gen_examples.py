import sys
sys.path.append('../src')
sys.path.append('../utils')

from hexagons_classes import HexagonsGame, Tile, Shape, Line, Circle, Triangle
import plot_board as pb

# Shape
# copy_paste
# grid
# reflect
# rotate
# recolor

'''
get
    - 'outside' / 'inside': the tiles outside/inside the given shape
    - 'above' / 'below': tiles that lie above/below the given shape
    - 'top' / 'bottom': to topmost/bottommost tiles of the given shape
    - 'corners': the corners of the shape. If the shape is a polygon, these will be the polygon’s vertices
    - 'end_points': the end points of the shape. If the shape is a line, these will be the ends of the line
'''

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
