import sys
sys.path.append('../src')
sys.path.append('../utils')

from hexagons_classes import HexagonsGame, Tile, Shape, Line, Circle, Triangle

HexagonsGame.start()

circle = Circle(center_tile=Tile(10, 5), radius=3)
circle.draw('black')

circle.get('below').draw('red')
# circle.neighbors().draw('green')
# circle.neighbors(criterion='right').draw('green')
# circle.neighbors(criterion='left').draw('red')
# circle.neighbors(criterion='above').draw('green')
# circle.neighbors(criterion='below').draw('red')
# circle.neighbors(criterion='outside').draw('green')
# circle.neighbors(criterion='inside').draw('red')
# Tile(14, 6).draw('blue')
# circle.neighbors(criterion='white').draw('green')
# circle.neighbors(criterion='up_right').draw('green')

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
