import sys
sys.path.append('../src')
from hexagons_classes import HexagonsGame, _Vec, _Hexagon, Tile, Shape, Line, Circle, Triangle

def func(pr = False):
  HexagonsGame.start()
  
  # Solution
  # Step 1
  center_tile = Tile(2, 2)
  neighbors = center_tile.neighbors()
  neighbors.draw('purple')
  
  # Step 2
  shift_direction = 'right'
  spacing = 1
  reference_shape = neighbors
  neighbors.copy_paste(shift_direction, spacing, reference_shape)
  neighbors.copy_paste(shift_direction, spacing, reference_shape)
  neighbors.copy_paste(shift_direction, spacing, reference_shape)

  if pr:
    HexagonsGame.plot()

  return HexagonsGame.board_state

if __name__ == '__main__':
  func(pr=True)
