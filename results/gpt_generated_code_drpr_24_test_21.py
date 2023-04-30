import sys
sys.path.append('../src')
from hexagons_classes import HexagonsGame, _Vec, _Hexagon, Tile, Shape, Line, Circle, Triangle

def func(pr = False):
  HexagonsGame.start()
  
  # Solution
  # 1.
  start_tile = Tile(2, 2) # second tile down in the second vertical row (from left)
  start_tile.draw('white')
  start_tile.neighbors().draw('purple') # color all tiles around it purple
  
  # 2.
  for i in range(4):
    start_tile.copy_paste('right', 2).neighbors().draw('purple') # make a ring of 6 purple tiles

  if pr:
    HexagonsGame.plot()

  return HexagonsGame.board_state

if __name__ == '__main__':
  func(pr=True)
