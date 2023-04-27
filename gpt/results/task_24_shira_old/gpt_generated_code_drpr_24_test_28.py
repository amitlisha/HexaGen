import sys
sys.path.append('../src')
from hexagons_classes import HexagonsGame, _Vec, _Hexagon, Tile, Shape, Line, Circle, Triangle

def func(pr = False):
  HexagonsGame.start()
  
  # Solution
  
  # Get the starting tile
  start_tile = Tile(2, 2)
  
  # Get the neighbors of the starting tile
  neighbors = start_tile.neighbors()
  
  # Draw the first ring
  neighbors.draw('purple')
  
  # Get the neighbors of the neighbors
  neighbors_of_neighbors = neighbors.neighbors()
  
  # Draw the second ring
  neighbors_of_neighbors.draw('purple')
  
  # Get the neighbors of the neighbors of the neighbors
  neighbors_of_neighbors_of_neighbors = neighbors_of_neighbors.neighbors()
  
  # Draw the third ring
  neighbors_of_neighbors_of_neighbors.draw('purple')
  
  # Get the neighbors of the neighbors of the neighbors of the neighbors
  neighbors_of_neighbors_of_neighbors_of_neighbors = neighbors_of_neighbors_of_neighbors.neighbors()
  
  # Draw the fourth ring
  neighbors_of_neighbors_of_neighbors_of_neighbors.draw('purple')

  if pr:
    HexagonsGame.plot()

  return HexagonsGame.board_state

if __name__ == '__main__':
  func(pr=True)
