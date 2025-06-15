# Created by chat gpt

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle
from constants.constants import *

with Game() as g:
    
    # initialize board
    board = [[Tile(col + 1, row + 1) for col in range(WIDTH)] for row in range(HEIGHT)]
    
    # step 1
    board[1][2].draw('green')
    board[2][2].draw('green')
    
    # step 2
    board[7][7].draw('green')
    board[8][7].draw('green')
    
    # step 3
    board[14][7].draw('green')
    board[15][7].draw('green')
    
    # step 4
    for row in range(HEIGHT):
      for col in range(WIDTH):
        if board[row][col].color == 'white':
          for neighbor in board[row][col].neighbors():
            if neighbor.color == 'green':
              board[row][col].draw('purple')
    
    # step 5
    board[1][14].draw('blue')
    board[2][14].draw('blue')
    
    # step 6
    board[9][10].draw('blue')
    board[8][10].draw('blue')
    
    # step 7
    for row in range(HEIGHT):
      for col in range(WIDTH):
        if board[row][col].color == 'white':
          for neighbor in board[row][col].neighbors():
            if neighbor.color == 'blue':
              board[row][col].draw('purple')
    
    # step 8
    board[8][2].draw('green')
    
    # step 9
    board[9][2].draw('blue')
    
    # step 10
    board[1][7].draw('green')
    
    # step 11
    board[7][2].draw('blue')
    
    # step 12
    board[9][10].draw('blue')
    
    # step 13
    board[1][10].draw('green')
    
    # step 14
    for row in range(HEIGHT):
      for col in range(WIDTH):
        if board[row][col].color in ['blue', 'green']:
          for neighbor in board[row][col].neighbors():
            if neighbor.color == 'white':
              neighbor.draw('orange')
    
    # save the steps and retrieve them
    g.record_step('my_steps')
    my_steps = g.get_record('my_steps')
    
    import os
    image = os.path.dirname(__file__).split('\\')[-1]
    variation = os.path.basename(__file__).split('.')[0]
    g.plot(gold_boards=None, multiple=0,file_name=f'{image}-{variation}')
