import sys
sys.path.append('../src')
from hexagons_classes import HexagonsGame, _Vec, _Hexagon, Tile, Shape, Line, Circle, Triangle

def func(pr = False):
  HexagonsGame.start()
  
  # Solution
  start_tile = Tile(2, 2)
  start_tile.draw('white')
  
  for i in range(4):
      purple_ring = start_tile.neighbors().copy_paste('right', i+1)
      purple_ring.draw('purple')

  if pr:
    HexagonsGame.plot()

  return HexagonsGame.board_state

if __name__ == '__main__':
  func(pr=True)
