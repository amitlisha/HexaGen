import sys
sys.path.append('../src')
from hexagons_classes import HexagonsGame, _Vec, _Hexagon, Tile, Shape, Line, Circle, Triangle

def func(pr = False):
  HexagonsGame.start()
  # Solution
  
  # Get the starting tile
  start_tile = Tile(2, 2)
  
  # Draw the first purple ring
  neighbors = start_tile.neighbors()
  neighbors.draw('purple')
  
  # Draw the other 3 purple rings
  for i in range(3):
    # Copy the first ring, shifting it 1 row to the right
    new_ring = neighbors.copy_paste('right', 1)
    new_ring.draw('purple')
    # Set the new ring as the neighbors for the next iteration
    neighbors = new_ring

  if pr:
    HexagonsGame.plot()

  return HexagonsGame.board_state

if __name__ == '__main__':
  func(pr=True)
