# Created by maor

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle

task_index = 198
gold_boards = list(read_task(task_index)['gold_boards'])

with Game() as g:
    
    # description:
    # task index: 198, image: P01C07T03, collection round: 1, category: composed objects, group: train
    # agreement scores: [[0.68, 0.23, 0.22], [0.45, 0.52, 0.11]]
    
    '''
    1. Color topmost leftmost tile red, leave the three tiles diagonally down to the
    right of that tile, white, then alternate making a red diagonal line (connect
    the third tile from top leftmost down, coloring the 5 tiles going upward
    diagonally from there, red. Repeat again this diagonal, white and red pattern
    Three times.
    '''
    tile = Tile(row=1, column=1)
    tile.draw('red')
    lines = []
    
    r = 3
    
    for i in range(4):
      start_tile = Tile(row=r, column=1)
    
      line = Line(start_tile=start_tile, direction='up_right')
      line.draw('red')
    
      lines.append(line)
    
      r+= 2
    
    '''
    2. Color purple every other row, below the longest hexagonal red line made in step
    one. Start this alternating pattern with Bottommost, left most tile, skipping
    the second row from left, but then on every other row to the right, (third,
    fifth, seventh, etc.) color the vertical line(s) purple.
    '''
    
    tile = Tile(row=-1, column=1)
    tile.draw('purple')
    
    longest_line = max(lines, key=lambda x: x.length)
    
    for c in [3, 5, 7, 9, 11, 13, 15, 17]:
      start_tile = Tile(row=-1, column=c)
      end_tile = Shape.get_column(c) * longest_line
      line = Line(start_tile=start_tile, end_tile=end_tile, include_end_tile=False)
      line.draw('purple')
    
    g.plot(gold_boards=gold_boards, multiple=0)
