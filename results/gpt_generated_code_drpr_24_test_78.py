import sys
sys.path.append('../src')
from hexagons_classes import HexagonsGame, _Vec, _Hexagon, Tile, Shape, Line, Circle, Triangle

def func(pr = False):
  HexagonsGame.start()
  
  # 1.
  center_tile = Tile(2, 2)
  ring = center_tile.neighbors().draw('purple')
  
  # 2.
  for i in range(4):
      ring.copy_paste('right', WIDTH + 1).draw('purple')

  if pr:
    HexagonsGame.plot()

  return HexagonsGame.board_state

if __name__ == '__main__':
  func(pr=True)
