import sys
sys.path.append('../src')
from hexagons_classes import HexagonsGame, _Vec, _Hexagon, Tile, Shape, Line, Circle, Triangle

def func(pr = False):
  HexagonsGame.start()
  
  # Solution
  # Step 1
  center_tile = Tile(2, 2)
  ring_shape = center_tile.neighbors()
  ring_shape.draw('purple')
  
  # Step 2
  shift_direction = 'right'
  spacing = 2
  reference_shape = center_tile
  rings_shape = ring_shape.grid(shift_direction, spacing, num_copies=4)
  rings_shape.draw('purple')

  if pr:
    HexagonsGame.plot()

  return HexagonsGame.board_state

if __name__ == '__main__':
  func(pr=True)
