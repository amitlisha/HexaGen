import sys
sys.path.append('../src')
from hexagons_classes import HexagonsGame, _Vec, _Hexagon, Tile, Shape, Line, Circle, Triangle

def func(pr = False):
  HexagonsGame.start()
  
  # Solution
  # 1.
  start_tile = Tile(2, 2)
  shape = start_tile.neighbors()
  shape.draw('purple')
  
  # 2.
  rings = 4
  for i in range(rings):
    shape = start_tile.copy_paste('right', (i + 1) * 2 + 1)
    shape.draw('purple')

  if pr:
    HexagonsGame.plot()

  return HexagonsGame.board_state

if __name__ == '__main__':
  func(pr=True)
