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
  rings = 4
  spacing = 2
  
  for i in range(rings):
    center_tile = Tile(2 + (i + 1) * spacing, 2)
    neighbors = center_tile.neighbors()
    neighbors.draw('purple')

  if pr:
    HexagonsGame.plot()

  return HexagonsGame.board_state

if __name__ == '__main__':
  func(pr=True)
