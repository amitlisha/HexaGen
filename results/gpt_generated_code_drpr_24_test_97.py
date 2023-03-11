import sys
sys.path.append('../src')
from hexagons_classes import HexagonsGame, _Vec, _Hexagon, Tile, Shape, Line, Circle, Triangle

def func(pr = False):
  HexagonsGame.start()
  
  # Solution
  
  # Get the start tile
  start_tile = Tile(2, 2)
  
  # Draw the first ring
  start_tile.draw('white')
  start_tile.neighbors().draw('purple')
  
  # Draw the remaining rings
  for i in range(3):
    start_tile.copy_paste('right', 2).neighbors().draw('purple')

  if pr:
    HexagonsGame.plot()

  return HexagonsGame.board_state

if __name__ == '__main__':
  func(pr=True)
