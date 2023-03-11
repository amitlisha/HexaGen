import sys
sys.path.append('../src')
from hexagons_classes import HexagonsGame, _Vec, _Hexagon, Tile, Shape, Line, Circle, Triangle

def func(pr = False):
  HexagonsGame.start()
  
  # Solution
  # 1.
  # Get the starting tile
  start_tile = Tile(2, 2)
  
  # Get the neighbors of the tile
  neighbors = start_tile.neighbors()
  
  # Draw the tile white
  start_tile.draw('white')
  
  # Draw the neighbors purple
  neighbors.draw('purple')
  
  # 2.
  # Get the starting tile
  start_tile = Tile(2, 4)
  
  # Create a shape from the start tile
  shape = Shape([start_tile])
  
  # Copy paste the shape with a spacing of 1
  shape_copy_pasted = shape.copy_paste('right', 1)
  
  # Create a grid of the shape with a spacing of 1
  shape_grid = shape.grid('right', 1, 4)
  
  # Draw the grid purple
  shape_grid.draw('purple')

  if pr:
    HexagonsGame.plot()

  return HexagonsGame.board_state

if __name__ == '__main__':
  func(pr=True)
