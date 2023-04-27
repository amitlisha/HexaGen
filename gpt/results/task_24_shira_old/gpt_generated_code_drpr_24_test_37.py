import sys
sys.path.append('../src')
from hexagons_classes import HexagonsGame, _Vec, _Hexagon, Tile, Shape, Line, Circle, Triangle

def func(pr = False):
  HexagonsGame.start()
  
  # Solution
  # 1.
  start_tile = Tile(2, 2) # second tile down in the second vertical row (from left)
  neighbors = start_tile.neighbors() # get all the neighbors of the start tile
  neighbors.draw('purple') # draw all the neighbors in purple
  start_tile.draw('white') # draw the start tile in white
  
  # 2.
  for i in range(4): # repeat 4 times
    neighbors.copy_paste('right', 1) # copy the ring one tile to the right
    neighbors.draw('purple') # draw the copied ring in purple
    neighbors.copy_paste('right', 2) # leave a blank row between the rings

  if pr:
    HexagonsGame.plot()

  return HexagonsGame.board_state

if __name__ == '__main__':
  func(pr=True)
