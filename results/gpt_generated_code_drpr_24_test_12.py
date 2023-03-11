import sys
sys.path.append('../src')
from hexagons_classes import HexagonsGame, _Vec, _Hexagon, Tile, Shape, Line, Circle, Triangle

def func(pr = False):
  HexagonsGame.start()
  
  # Solution
  
  # 1.
  center_tile = Tile(2, 2)
  circle = Circle(center_tile, 1)
  circle.draw('purple')
  
  # 2.
  start_tile = Tile(2, 4)
  circle1 = Circle(start_tile, 1)
  circle1.draw('purple')
  circle2 = circle1.copy_paste('right', 2)
  circle2.draw('purple')
  circle3 = circle2.copy_paste('right', 2)
  circle3.draw('purple')
  circle4 = circle3.copy_paste('right', 2)
  circle4.draw('purple')

  if pr:
    HexagonsGame.plot()

  return HexagonsGame.board_state

if __name__ == '__main__':
  func(pr=True)
