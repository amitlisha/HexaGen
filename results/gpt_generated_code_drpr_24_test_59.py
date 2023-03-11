import sys
sys.path.append('../src')
from hexagons_classes import HexagonsGame, _Vec, _Hexagon, Tile, Shape, Line, Circle, Triangle

def func(pr = False):
  HexagonsGame.start()
  tile = Tile(2, 2) # get the starting tile
  
  # draw the first ring
  shape = tile.neighbors()
  shape.draw('purple')
  
  # draw the remaining rings
  for i in range(3):
    # shift the shape one row to the right
    shape = shape.copy_paste('right', 1)
    shape.draw('purple')

  if pr:
    HexagonsGame.plot()

  return HexagonsGame.board_state

if __name__ == '__main__':
  func(pr=True)
