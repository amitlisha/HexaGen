import sys
sys.path.append('../src')
from hexagons_classes import HexagonsGame, _Vec, _Hexagon, Tile, Shape, Line, Circle, Triangle

def func(pr = False):
  HexagonsGame.start()
  
  # Solution
  # Step 1
  tile = Tile(2, 2)
  tile.draw('white')
  tile.neighbors().draw('purple')
  
  # Step 2
  for i in range(1, 5):
    tile.copy_paste('right', 2).neighbors().draw('purple')

  if pr:
    HexagonsGame.plot()

  return HexagonsGame.board_state

if __name__ == '__main__':
  func(pr=True)
