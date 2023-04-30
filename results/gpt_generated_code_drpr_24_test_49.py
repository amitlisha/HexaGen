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
  center_tile.draw('white')
  
  # 2.
  num_rings = 4
  for i in range(num_rings):
      neighbors.copy_paste('right', 2).draw('purple')

  if pr:
    HexagonsGame.plot()

  return HexagonsGame.board_state

if __name__ == '__main__':
  func(pr=True)
