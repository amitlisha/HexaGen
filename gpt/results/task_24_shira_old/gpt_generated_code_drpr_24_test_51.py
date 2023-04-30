import sys
sys.path.append('../src')
from hexagons_classes import HexagonsGame, _Vec, _Hexagon, Tile, Shape, Line, Circle, Triangle

def func(pr = False):
  HexagonsGame.start()
  
  # Solution
  # 1.
  center_tile = Tile(2, 2)  # Second tile down in the second vertical row (from left)
  neighbors = center_tile.neighbors()  # Get all neighbors of the center tile
  neighbors.draw('purple')  # Draw the neighbors in purple
  center_tile.draw('white')  # Leave the center tile white
  
  # 2.
  start_tile = Tile(2, 2)  # Second tile down in the second vertical row (from left)
  rings = start_tile.grid('right', 2, 4)  # Create 4 rings of 6 purple tiles, spaced by 2 tiles
  rings.draw('purple')  # Draw the rings in purple

  if pr:
    HexagonsGame.plot()

  return HexagonsGame.board_state

if __name__ == '__main__':
  func(pr=True)
