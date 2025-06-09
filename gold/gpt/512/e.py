# Created by chat gpt

from utils.reading_tasks import read_task
from hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle
from constants.constants import *

HexagonsGame.start()
# create a hexagonal board with the specified dimensions
board = [[None] * WIDTH for _ in range(HEIGHT)]

# colour in green tiles in the specified locations
board[1][2] = "green"
board[2][2] = "green"
board[-3][2] = "green"
board[-2][2] = "green"
board[-3][7] = "green"
board[-2][7] = "green"
board[1][14] = "green"
board[2][14] = "green"
board[-3][14] = "blue"
board[-2][14] = "blue"
board[-3][-11] = "blue"
board[-2][-11] = "blue"

# colour in purple all white tiles adjacent to green and blue tiles
for row in range(HEIGHT):
  for col in range(WIDTH):
    if board[row][col] == "green" or board[row][col] == "blue":
      for i, j in ((-1, -1), (-1, 0), (0, -1), (0, 1), (1, 0), (1, 1)):
        x, y = row + i, col + j
        if 0 <= x < HEIGHT and 0 <= y < WIDTH and not board[x][y]:
          board[x][y] = "purple"

# colour in blue tiles in the specified locations
board[1][-11] = "blue"
board[2][-11] = "blue"
board[-3][-11] = "blue"
board[-2][-11] = "blue"
board[-3][6] = "blue"
board[-2][6] = "blue"

# colour in orange tiles adjacent to blue and green tiles
for row in range(HEIGHT):
  for col in range(WIDTH):
    if board[row][col] == "green" or board[row][col] == "blue":
      for i, j in ((-1, -1), (-1, 0), (0, -1), (0, 1), (1, 0), (1, 1)):
        x, y = row + i, col + j
        if 0 <= x < HEIGHT and 0 <= y < WIDTH and not board[x][y]:
          board[x][y] = "orange"

# colour in additional specified tiles
board[2][-3] = "green"
board[-3][-3] = "blue"
board[1][6] = "green"
board[-2][6] = "blue"
board[2][-9] = "blue"
board[-3][-9] = "green"

import os
image = os.path.dirname(__file__).split('\\')[-1]
variation = os.path.basename(__file__).split('.')[0]
HexagonsGame.plot(gold_boards=None, multiple=0,file_name=f'{image}-{variation}')
