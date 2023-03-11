import sys
sys.path.append('../src')
from hexagons_classes import HexagonsGame, _Vec, _Hexagon, Tile, Shape, Line, Circle, Triangle

def func(pr = False):
  HexagonsGame.start()
  
  # Solution
  
  #1
  # Get the starting tile
  start_tile = Tile(2, 2)
  
  # Get the neighbors of the starting tile
  neighbors = start_tile.neighbors()
  
  # Draw the starting tile in white
  start_tile.draw('white')
  
  # Draw the neighbors in purple
  neighbors.draw('purple')
  
  #2
  # Get the starting tile
  start_tile = Tile(2, 2)
  
  # Get the neighbors of the starting tile
  neighbors = start_tile.neighbors()
  
  # Copy-paste the pattern 
  pattern = neighbors.copy_paste('right', 2)
  
  # Draw the pattern in purple
  pattern.draw('purple')
  
  # Repeat the pattern
  pattern = pattern.grid('right', 2, 4)
  
  # Draw the pattern in purple
  pattern.draw('purple')

  if pr:
    HexagonsGame.plot()

  return HexagonsGame.board_state

if __name__ == '__main__':
  func(pr=True)
