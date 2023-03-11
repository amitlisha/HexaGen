import sys
sys.path.append('../src')
from hexagons_classes import HexagonsGame, _Vec, _Hexagon, Tile, Shape, Line, Circle, Triangle

def func(pr = False):
  HexagonsGame.start()
  
  # Solution:
  
  # Get the starting tile
  start_tile = Tile(2, 2)
  
  # Draw the purple rings
  for i in range(4):
    # Create a shape object that contains the tiles of the ring
    ring_shape = start_tile.neighbors().copy_paste('right', i+1)
    
    # Draw the ring
    ring_shape.draw('purple')

  if pr:
    HexagonsGame.plot()

  return HexagonsGame.board_state

if __name__ == '__main__':
  func(pr=True)
