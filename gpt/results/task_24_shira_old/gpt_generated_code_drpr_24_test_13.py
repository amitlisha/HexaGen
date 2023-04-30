import sys
sys.path.append('../src')
from hexagons_classes import HexagonsGame, _Vec, _Hexagon, Tile, Shape, Line, Circle, Triangle

def func(pr = False):
  HexagonsGame.start()
  
  # Solution
  # 1.
  start_tile = Tile(2, 2)
  neighbors = start_tile.neighbors()
  neighbors.draw('purple')
  
  # 2.
  shift_direction = 'right'
  spacing = 2
  copied_neighbors = neighbors.copy_paste(shift_direction, spacing)
  copied_neighbors.draw('purple')
  
  for i in range(3):
      copied_neighbors = copied_neighbors.copy_paste(shift_direction, spacing)
      copied_neighbors.draw('purple')

  if pr:
    HexagonsGame.plot()

  return HexagonsGame.board_state

if __name__ == '__main__':
  func(pr=True)
