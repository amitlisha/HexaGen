import sys
sys.path.append('../src')
from hexagons_classes import HexagonsGame, _Vec, _Hexagon, Tile, Shape, Line, Circle, Triangle

def func(pr = False):
  HexagonsGame.start()
  
  #Solution
  #1.
  start_tile = Tile(2, 2)
  shape = start_tile.neighbors()
  shape.draw('purple')
  
  #2.
  shift_direction = 'right'
  spacing = 2
  shape.copy_paste(shift_direction, spacing).grid(shift_direction, spacing, num_copies=3)

  if pr:
    HexagonsGame.plot()

  return HexagonsGame.board_state

if __name__ == '__main__':
  func(pr=True)
