import sys
sys.path.append('../src')
from hexagons_classes import HexagonsGame, _Vec, _Hexagon, Tile, Shape, Line, Circle, Triangle

def func(pr = False):
  HexagonsGame.start()
  
  # Solution
  
  # Step 1
  start_tile = Tile(2, 2)
  ring = start_tile.neighbors()
  ring.draw('purple')
  start_tile.draw('white')
  
  # Step 2
  reference_shape = ring
  shift_direction = 'right'
  spacing = 2
  num_copies = 3
  rings = reference_shape.grid(shift_direction, spacing, num_copies)
  rings.draw('purple')

  if pr:
    HexagonsGame.plot()

  return HexagonsGame.board_state

if __name__ == '__main__':
  func(pr=True)
