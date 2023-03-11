import sys
sys.path.append('../src')
from hexagons_classes import HexagonsGame, _Vec, _Hexagon, Tile, Shape, Line, Circle, Triangle

def func(pr = False):
  HexagonsGame.start()
  
  # Code
  # Step 1
  start_tile = Tile(2, 2)
  ring = start_tile.neighbors()
  ring.draw('purple')
  
  # Step 2
  shift_direction = 'right'
  spacing = 1
  num_copies = 4
  ring.grid(shift_direction, spacing, num_copies)

  if pr:
    HexagonsGame.plot()

  return HexagonsGame.board_state

if __name__ == '__main__':
  func(pr=True)
