# Created by maor

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle

task_index = 573
gold_boards = list(read_task(task_index)['gold_boards'])

with Game() as g:
    
    # description:
    # task index: 573, image: P01C04T04, collection round: 0, category: conditions, group: train
    # agreement scores: [[1.0, 0.89, 0.89], [1.0, 0.88, 0.88], [1.0, 0.92, 0.92], [1.0, 0.94, 0.94]]
    
    '''
    1. In the first, ninth, thirteenth, fifteenth and seventeenth columns color the top
    hex of each column orange and the next four hexes below them purple.
    '''
    for c in [1, 9, 13, 15, 17]:
      tile = Tile(row=1, column=c)
      tile.draw('orange')
      for i in range(4):
        tile = tile.neighbor('down')
        tile.draw('purple')
    
    '''
    2. In the third, fifth, seventh and eleventh columns, color the top cell green and
    the next four cells below it blue.
    '''
    for c in [3, 5, 7, 11]:
      tile = Tile(row=1, column=c)
      tile.draw('green')
      for i in range(4):
        tile = tile.neighbor('down')
        tile.draw('blue')
    
    '''
    3. In the second, sixth, eighth, sixteenth and eighteenth columns, start from the
    bottom and color the bottom hex green and the next four above it blue
    '''
    for c in [2, 6, 8, 16, 18]:
      tile = Tile(row=-1, column=c)
      tile.draw('green')
      for i in range(4):
        tile = tile.neighbor('up')
        tile.draw('blue')
    
    '''
    4. In the fourth, tenth, twelveth, and fourteenth columns, color the bottom hex
    orange and the next four hexes above it purple
    '''
    for c in [4, 10, 12, 14]:
      tile = Tile(row=-1, column=c)
      tile.draw('orange')
      for i in range(4):
        tile = tile.neighbor('up')
        tile.draw('purple')
    
    g.plot(gold_boards=gold_boards, multiple=0)
