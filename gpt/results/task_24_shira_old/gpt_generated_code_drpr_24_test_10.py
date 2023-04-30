import sys
sys.path.append('../src')
from hexagons_classes import HexagonsGame, _Vec, _Hexagon, Tile, Shape, Line, Circle, Triangle

def func(pr = False):
  HexagonsGame.start()
  
  # Solution
  
  # Get the starting tile
  start_tile = Tile(2, 2)
  
  # Draw the first ring
  ring_shape = start_tile.neighbors()
  ring_shape.draw('purple')
  start_tile.draw('white')
  
  # Draw the other rings
  for i in range(3):
    # Shift the ring to the right
    ring_shape = ring_shape.copy_paste('right', 2, reference_shape=start_tile)
    # Draw the ring
    ring_shape.draw('purple')

  if pr:
    HexagonsGame.plot()

  return HexagonsGame.board_state

if __name__ == '__main__':
  func(pr=True)
