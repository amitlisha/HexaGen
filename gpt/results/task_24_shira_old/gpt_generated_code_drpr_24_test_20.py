import sys
sys.path.append('../src')
from hexagons_classes import HexagonsGame, _Vec, _Hexagon, Tile, Shape, Line, Circle, Triangle

def func(pr = False):
  HexagonsGame.start()
  
  # Solution
  
  # Get the starting tile
  start_tile = Tile(2, 2)
  
  # Draw the first ring
  ring = start_tile.neighbors()
  ring.draw('purple')
  start_tile.draw('white')
  
  # Draw the other rings
  for i in range(3):
    ring = ring.copy_paste('right', 2)
    ring.draw('purple')

  if pr:
    HexagonsGame.plot()

  return HexagonsGame.board_state

if __name__ == '__main__':
  func(pr=True)
