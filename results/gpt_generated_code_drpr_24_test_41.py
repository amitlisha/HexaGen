import sys
sys.path.append('../src')
from hexagons_classes import HexagonsGame, _Vec, _Hexagon, Tile, Shape, Line, Circle, Triangle

def func(pr = False):
  HexagonsGame.start()
  
  # Solution
  
  # Get the starting tile
  start_tile = Tile(2, 2)
  
  # Set the color of the starting tile to white
  start_tile.draw('white')
  
  # Get the neighbors of the starting tile
  neighbors = start_tile.neighbors()
  
  # Draw the first ring of purple tiles
  neighbors.draw('purple')
  
  # Create a grid of purple rings
  neighbors.grid('right', 2, 4)

  if pr:
    HexagonsGame.plot()

  return HexagonsGame.board_state

if __name__ == '__main__':
  func(pr=True)
