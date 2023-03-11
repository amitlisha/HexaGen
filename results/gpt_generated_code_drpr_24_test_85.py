import sys
sys.path.append('../src')
from hexagons_classes import HexagonsGame, _Vec, _Hexagon, Tile, Shape, Line, Circle, Triangle

def func(pr = False):
  HexagonsGame.start()
  
  # Solution
  # 1.
  tile = Tile(2, 2)
  tile.neighbors().draw('purple')
  
  # 2.
  tile = Tile(2, 2)
  shift_direction = 'right'
  spacing = 2
  for _ in range(4):
      tile.neighbors().copy_paste(shift_direction, spacing).draw('purple')
      shift_direction = 'down'
      spacing = 1

  if pr:
    HexagonsGame.plot()

  return HexagonsGame.board_state

if __name__ == '__main__':
  func(pr=True)
