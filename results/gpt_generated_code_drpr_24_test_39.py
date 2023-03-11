import sys
sys.path.append('../src')
from hexagons_classes import HexagonsGame, _Vec, _Hexagon, Tile, Shape, Line, Circle, Triangle

def func(pr = False):
  HexagonsGame.start()
  
  # Solution
  # 1.
  tile = Tile(2, 2) # Get the tile
  neighbors = tile.neighbors() # Get the neighbors
  neighbors.draw('purple') # Draw the neighbors in purple
  tile.draw('white') # Draw the tile in white
  
  # 2.
  rings = 4 # Number of rings
  spacing = 1 # Number of rows between rings
  start_tile = Tile(2, 2) # Starting tile
  for i in range(rings):
    ring = start_tile.neighbors().copy_paste('right', spacing) # Copy the ring
    ring.draw('purple') # Draw the ring in purple
    start_tile = Tile(start_tile.column + spacing + 1, start_tile.row) # Move the starting tile to the right

  if pr:
    HexagonsGame.plot()

  return HexagonsGame.board_state

if __name__ == '__main__':
  func(pr=True)
