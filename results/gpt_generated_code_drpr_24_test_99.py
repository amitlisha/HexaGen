import sys
sys.path.append('../src')
from hexagons_classes import HexagonsGame, _Vec, _Hexagon, Tile, Shape, Line, Circle, Triangle

def func(pr = False):
  HexagonsGame.start()
  
  # Solution
  # 1.
  center_tile = Tile(2, 2)
  neighbor_shape = center_tile.neighbors()
  neighbor_shape.draw('purple')
  
  # 2.
  shift_direction = 'right'
  spacing = 2
  reference_shape = center_tile.neighbors()
  copied_shape = reference_shape.copy_paste(shift_direction, spacing, reference_shape)
  grid_shape = copied_shape.grid(shift_direction, spacing, num_copies=4)
  grid_shape.draw('purple')

  if pr:
    HexagonsGame.plot()

  return HexagonsGame.board_state

if __name__ == '__main__':
  func(pr=True)
