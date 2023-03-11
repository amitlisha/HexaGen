import sys
sys.path.append('../src')
from hexagons_classes import HexagonsGame, _Vec, _Hexagon, Tile, Shape, Line, Circle, Triangle

def func(pr = False):
  HexagonsGame.start()
  
  # Code
  # 1.
  start_tile = Tile(2, 2)
  ring_shape = Circle(start_tile)
  ring_shape.draw('purple')
  
  # 2.
  shift_direction = 'right'
  spacing = 2
  num_copies = 3
  ring_shape.grid(shift_direction, spacing, num_copies)

  if pr:
    HexagonsGame.plot()

  return HexagonsGame.board_state

if __name__ == '__main__':
  func(pr=True)
