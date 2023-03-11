import sys
sys.path.append('../src')
from hexagons_classes import HexagonsGame, _Vec, _Hexagon, Tile, Shape, Line, Circle, Triangle

def func(pr = False):
  HexagonsGame.start()
  # Solution
  
  # Get the center tile of the first ring
  center_tile = Tile(2, 2)
  
  # Create the first ring
  ring = Circle(center_tile, 1)
  
  # Draw the first ring in purple
  ring.draw('purple')
  
  # Create the second ring
  ring2 = Circle(center_tile.neighbor('right'), 1)
  
  # Draw the second ring in purple
  ring2.draw('purple')
  
  # Create the third ring
  ring3 = Circle(center_tile.neighbor('right', 2), 1)
  
  # Draw the third ring in purple
  ring3.draw('purple')
  
  # Create the fourth ring
  ring4 = Circle(center_tile.neighbor('right', 3), 1)
  
  # Draw the fourth ring in purple
  ring4.draw('purple')

  if pr:
    HexagonsGame.plot()

  return HexagonsGame.board_state

if __name__ == '__main__':
  func(pr=True)
