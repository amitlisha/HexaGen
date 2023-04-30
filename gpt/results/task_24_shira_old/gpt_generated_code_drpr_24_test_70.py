import sys
sys.path.append('../src')
from hexagons_classes import HexagonsGame, _Vec, _Hexagon, Tile, Shape, Line, Circle, Triangle

def func(pr = False):
  HexagonsGame.start()
  
  # Solution
  # 1.
  tile = Tile(2, 2)
  neighbors = tile.neighbors()
  neighbors.draw('purple')
  tile.draw('white')
  
  # 2.
  rings = 4
  for i in range(rings):
    # shift the shape one row to the right
    neighbors = neighbors.copy_paste('right', 1)
    neighbors.draw('purple')

  if pr:
    HexagonsGame.plot()

  return HexagonsGame.board_state

if __name__ == '__main__':
  func(pr=True)
