import sys
sys.path.append('../src')
from hexagons_classes import HexagonsGame, _Vec, _Hexagon, Tile, Shape, Line, Circle, Triangle

def func(pr = False):
  HexagonsGame.start()
  
  # Solution
  # 1.
  start_tile = Tile(2, 2)
  start_tile.draw('white')
  
  neighbors = start_tile.neighbors()
  neighbors.draw('purple')
  
  # 2.
  for i in range(1, 5):
      neighbors.copy_paste('right', 2*i).draw('purple')

  if pr:
    HexagonsGame.plot()

  return HexagonsGame.board_state

if __name__ == '__main__':
  func(pr=True)
