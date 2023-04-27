import sys
sys.path.append('../src')
from hexagons_classes import HexagonsGame, _Vec, _Hexagon, Tile, Shape, Line, Circle, Triangle

def func(pr = False):
  HexagonsGame.start()
  
  # Solution
  # 1.
  center_tile = Tile(2, 2) # second tile down in the second vertical row (from left)
  center_tile.draw('white') # leave that tile white
  
  # create a shape from the neighbors of the center tile
  neighbors = center_tile.neighbors()
  
  # draw the shape in purple
  neighbors.draw('purple')
  
  # 2.
  # create a shape with the tiles of the first ring
  first_ring = neighbors.copy_paste('right', 1)
  
  # create a grid of the first ring
  rings = first_ring.grid('right', 2, 4)
  
  # draw the grid in purple
  rings.draw('purple')

  if pr:
    HexagonsGame.plot()

  return HexagonsGame.board_state

if __name__ == '__main__':
  func(pr=True)
