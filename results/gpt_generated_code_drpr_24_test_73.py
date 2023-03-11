import sys
sys.path.append('../src')
from hexagons_classes import HexagonsGame, _Vec, _Hexagon, Tile, Shape, Line, Circle, Triangle

def func(pr = False):
  HexagonsGame.start()
  
  # Solution
  
  # Get the starting tile
  start_tile = Tile(2, 2)
  
  # Draw the first ring
  start_tile.draw('white')
  start_tile.neighbors().draw('purple')
  
  # Create the remaining rings
  start_tile.copy_paste('right', 2).neighbors().draw('purple')
  start_tile.copy_paste('right', 4).neighbors().draw('purple')
  start_tile.copy_paste('right', 6).neighbors().draw('purple')

  if pr:
    HexagonsGame.plot()

  return HexagonsGame.board_state

if __name__ == '__main__':
  func(pr=True)
