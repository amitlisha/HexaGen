import sys
sys.path.append('../src')
from hexagons_classes import HexagonsGame, _Vec, _Hexagon, Tile, Shape, Line, Circle, Triangle

def func(pr = False):
  HexagonsGame.start()
  
  # Solution
  # 1. using the second tile down in the second vertical row (from left) leave that tile white but color all tiles around it purple. This forms a purple ring.
  center_tile = Tile(2,2)
  neighbors = center_tile.neighbors()
  neighbors.draw('purple')
  
  # 2. leaving a blank row next over to the right, repeat the pattern, making a ring of 6 purple tiles, continue this pattern until you have a total of 4 purple rings spaced, leaving a row of vertical tiles between them.
  for i in range(4):
      center_tile = center_tile.neighbor('right').neighbor('down')
      neighbors = center_tile.neighbors()
      neighbors.draw('purple')

  if pr:
    HexagonsGame.plot()

  return HexagonsGame.board_state

if __name__ == '__main__':
  func(pr=True)
