import sys
sys.path.append('../src')
from hexagons_classes import HexagonsGame, _Vec, _Hexagon, Tile, Shape, Line, Circle, Triangle

def func(pr = False):
  HexagonsGame.start()
  
  # Solution
  
  # 1.
  center_tile = Tile(2, 2) # second tile down in the second vertical row (from left)
  center_tile.draw('white')
  neighbors = center_tile.neighbors() # neighbors of the center tile
  neighbors.draw('purple') # draw the neighbors in purple
  
  # 2.
  rings = 4 # total of 4 purple rings
  spacing = 2 # leaving a row of vertical tiles between them
  for i in range(rings):
    # copy_paste the ring of 6 purple tiles
    neighbors.copy_paste('right', spacing, reference_shape=neighbors) # shift right
    neighbors.copy_paste('down_right', spacing, reference_shape=neighbors) # shift down and right

  if pr:
    HexagonsGame.plot()

  return HexagonsGame.board_state

if __name__ == '__main__':
  func(pr=True)
