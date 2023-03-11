import sys
sys.path.append('../src')
from hexagons_classes import HexagonsGame, _Vec, _Hexagon, Tile, Shape, Line, Circle, Triangle

def func(pr = False):
  HexagonsGame.start()
  
  # first step
  start_tile = Tile(2, 2) # second tile down in the second vertical row (from left)
  start_tile.draw('white') # leave that tile white
  neighbors = start_tile.neighbors() # get the neighbors of the start_tile
  neighbors.draw('purple') # color all tiles around it purple
  
  # second step
  for i in range(4):
    # copy the pattern to the right
    neighbors = neighbors.copy_paste('right', 2)
    neighbors.draw('purple') # color the ring purple
  
  # This code will draw four purple rings, spaced one row apart, with a blank row between each ring.

  if pr:
    HexagonsGame.plot()

  return HexagonsGame.board_state

if __name__ == '__main__':
  func(pr=True)
