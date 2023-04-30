import sys
sys.path.append('../src')
from hexagons_classes import HexagonsGame, _Vec, _Hexagon, Tile, Shape, Line, Circle, Triangle

def func(pr = False):
  HexagonsGame.start()
  
  # Solution
  
  # Get the starting tile
  start_tile = Tile(2,2)
  
  # Draw the first purple ring
  ring = start_tile.neighbors()
  ring.draw('purple')
  
  # Draw the remaining 3 purple rings
  for i in range(3):
    # Get the starting tile for the next ring
    start_tile = start_tile.neighbor('right', 2)
    # Draw the next ring
    ring = start_tile.neighbors()
    ring.draw('purple')

  if pr:
    HexagonsGame.plot()

  return HexagonsGame.board_state

if __name__ == '__main__':
  func(pr=True)
