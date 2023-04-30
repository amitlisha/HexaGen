import sys
sys.path.append('../src')
from hexagons_classes import HexagonsGame, _Vec, _Hexagon, Tile, Shape, Line, Circle, Triangle

def func(pr = False):
  HexagonsGame.start()
  
  # Solution
  # 1.
  # Get the tile
  tile = Tile(2, 2)
  
  # Get the neighbors of the tile
  neighbors = tile.neighbors()
  
  # Draw the tile
  tile.draw('white')
  
  # Draw the neighbors
  neighbors.draw('purple')
  
  # 2.
  # Get the start tile
  start_tile = Tile(2, 2)
  
  # Create an empty Shape
  shape = Shape([])
  
  # Create the purple rings
  for i in range(4):
    # Create a ring of purple tiles
    ring = Circle(start_tile, 3)
    ring.draw('purple')
  
    # Add the ring to the Shape
    shape.add(ring)
  
    # Move the start tile one row to the right
    start_tile = start_tile.neighbor('right')
  
  # Draw the vertical tiles between the rings
  vertical_tiles = shape.neighbors('right')
  vertical_tiles.draw('white')

  if pr:
    HexagonsGame.plot()

  return HexagonsGame.board_state

if __name__ == '__main__':
  func(pr=True)
