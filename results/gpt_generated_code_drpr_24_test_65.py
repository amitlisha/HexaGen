import sys
sys.path.append('../src')
from hexagons_classes import HexagonsGame, _Vec, _Hexagon, Tile, Shape, Line, Circle, Triangle

def func(pr = False):
  HexagonsGame.start()
  
  # Solution
  # 1.
  center_tile = Tile(2, 2)
  neighbors = center_tile.neighbors()
  neighbors.draw('purple')
  
  # 2.
  rings = []
  for i in range(4):
      shift_direction = 'right'
      spacing = 2
      reference_shape = rings[i-1] if i > 0 else center_tile
      rings.append(neighbors.copy_paste(shift_direction, spacing, reference_shape))
  rings.draw('purple')

  if pr:
    HexagonsGame.plot()

  return HexagonsGame.board_state

if __name__ == '__main__':
  func(pr=True)
