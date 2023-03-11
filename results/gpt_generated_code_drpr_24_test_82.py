import sys
sys.path.append('../src')
from hexagons_classes import HexagonsGame, _Vec, _Hexagon, Tile, Shape, Line, Circle, Triangle

def func(pr = False):
  HexagonsGame.start()
  
  # Solution
  # Step 1
  start_tile = Tile(2, 2)
  outer_ring = start_tile.neighbors()
  outer_ring.draw('purple')
  
  # Step 2
  for i in range(4):
      shift_direction = 'right'
      spacing = 1
      reference_shape = start_tile
      outer_ring = outer_ring.copy_paste(shift_direction, spacing, reference_shape)
      outer_ring.draw('purple')

  if pr:
    HexagonsGame.plot()

  return HexagonsGame.board_state

if __name__ == '__main__':
  func(pr=True)
