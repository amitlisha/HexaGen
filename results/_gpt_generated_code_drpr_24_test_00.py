import sys
sys.path.append('../src')
from hexagons_classes import HexagonsGame, _Vec, _Hexagon, Tile, Shape, Line, Circle, Triangle

def func(pr = False):
  HexagonsGame.start()
  
  '''
  3. Now draw a horizontal line of white tiles in the middle of the board.
  '''
  
  
  '''
  4. From the right end of the white line draw a vertical line of green tiles up to the top of the board.
  '''
  
  
  '''
  5. From the left end of the white line draw a vertical line of green tiles up to the top of the board.
  '''
  
  
  '''
  6. Now draw a horizontal line of white tiles in the middle of the board.
  '''
  
  
  '''
  7. From the right end of the white line draw a vertical line of green tiles up to the top of the board.
  '''
  
  
  '''
  8. From the left end of the white line draw a vertical line of green tiles up to the top of the board.
  '''
  
  
  '''
  9. Now draw a horizontal line of white tiles in the middle of the board.
  '''
  
  
  '''
  10. From the right end of the white line draw a vertical line of green tiles up to the top of the board.
  '''
  
  
  '''
  11. From the left end of the white line draw a vertical line of green tiles up to the top of the board.
  '''
  
  
  '''
  12. Now draw a horizontal line of white tiles in the middle of the board.
  '''
  
  
  '''
  13. From the right end of the white line draw a vertical line of green tiles up to the top of the board.
  '''
  
  
  '''
  14. From the left end of the white line draw a vertical line of green tiles up to the top of the board.
  '''
  
  
  '''
  15. Now draw a horizontal line of white tiles in the middle of the board.
  '''
  
  
  '''
  16. From the right end of the white line draw a vertical line of green tiles up to the top of the board.
  '''
  
  
  '''
  17. From the left end of the white line draw a vertical line of green tiles up to the top of the board.
  '''
  
  
  '''
  18. Now draw a horizontal line of white tiles in the middle of the board.
  '''
  
  

  if pr:
    HexagonsGame.plot()

  return HexagonsGame.board_state

if __name__ == '__main__':
  func(pr=True)
