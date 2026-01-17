# Created by maor

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle

task_index = 221
gold_boards = list(read_task(task_index)['gold_boards'])

with Game() as g:
    
    # description:
    # task index: 221, image: P01C08T03, collection round: 1, category: other, group: train
    # agreement scores: [[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0]]
    
    '''
    1. In column four, paint tiles 3-8 green, omitting tile 6.
    '''
    for r in [3,4,5,7,8]:
      tile = Tile(row=r, column=4)
      tile.draw('green')
    
    '''
    2. In column five, paint tiles 4-9 red.
    '''
    for r in range(4,10):
      tile = Tile(row=r, column=5)
      tile.draw('red')
    
    '''
    3. In column six, paint tiles 4-8 purple.
    '''
    for r in range(4,9):
      tile = Tile(row=r, column=6)
      tile.draw('purple')
    
    '''
    4. In column seven, paint tiles 5-7 orange.
    '''
    for r in range(5,8):
      tile = Tile(row=r, column=7)
      tile.draw('orange')
    
    '''
    5. In column eight, paint tile 3 blue, and tiles 5-6 yellow.
    '''
    tile = Tile(row=3, column=8)
    tile.draw('blue')
    for r in range(5,7):
      tile = Tile(row=r, column=8)
      tile.draw('yellow')
    
    '''
    6. In column nine, paint tiles 4-8 blue.
    '''
    for r in range(4,9):
      tile = Tile(row=r, column=9)
      tile.draw('blue')
    
    '''
    7. In column ten, paint tile 3 blue, and tiles 5-6 yellow.
    '''
    tile = Tile(row=3, column=10)
    tile.draw('blue')
    for r in range(5,7):
      tile = Tile(row=r, column=10)
      tile.draw('yellow')
    
    '''
    8. In column eleven, paint tiles 5-7 orange.
    '''
    for r in range(5,8):
      tile = Tile(row=r, column=11)
      tile.draw('orange')
    
    '''
    9. In column twelve, paint tiles 4-8 purple.
    '''
    for r in range(4,9):
      tile = Tile(row=r, column=12)
      tile.draw('purple')
    
    '''
    10. In column thirteen, paint tiles 4-9 red.
    '''
    for r in range(4,10):
      tile = Tile(row=r, column=13)
      tile.draw('red')
    
    '''
    11. In column fourteen, paint tiles 3-8 green, omitting tile 6.
    '''
    for r in [3,4,5,7,8]:
      tile = Tile(row=r, column=14)
      tile.draw('green')
    
    
    g.plot(gold_boards=gold_boards, multiple=0)
