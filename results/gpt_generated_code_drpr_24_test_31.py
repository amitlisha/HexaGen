import sys
sys.path.append('../src')
from hexagons_classes import HexagonsGame, _Vec, _Hexagon, Tile, Shape, Line, Circle, Triangle

def func(pr = False):
  HexagonsGame.start()
  
  # 1.
  start_tile = Tile(2, 2)
  neighbors = start_tile.neighbors()
  neighbors.draw('purple')
  start_tile.draw('white')
  
  # 2.
  spacing = 2
  num_copies = 4
  shift_direction = 'right'
  reference_shape = start_tile.neighbors()
  copies = reference_shape.grid(shift_direction, spacing, num_copies)
  copies.draw('purple')

  if pr:
    HexagonsGame.plot()

  return HexagonsGame.board_state

if __name__ == '__main__':
  func(pr=True)
