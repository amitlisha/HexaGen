import sys
sys.path.append('../src')
from hexagons_classes import HexagonsGame, _Vec, _Hexagon, Tile, Shape, Line, Circle, Triangle

def func(pr = False):
  HexagonsGame.start()
  
  # Solution
  
  # Get the starting tile
  start_tile = Tile(2, 2)
  
  # Color the starting tile white
  start_tile.draw('white')
  
  # Get the neighbors of the starting tile
  neighbors = start_tile.neighbors()
  
  # Color the neighbors purple
  neighbors.draw('purple')
  
  # Create a grid of purple rings
  shape = neighbors.grid('right', 2, num_copies=4)
  
  # Leave a blank row between each ring
  shape.copy_paste('down', 2)

  if pr:
    HexagonsGame.plot()

  return HexagonsGame.board_state

if __name__ == '__main__':
  func(pr=True)
