# Created by maor

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle

task_index = 84
gold_boards = list(read_task(task_index)['gold_boards'])

with Game() as g:
    
    # description:
    # task index: 84, image: P01C02T29, collection round: 1, category: bounded iteration, group: train
    # agreement scores: [[1.0, 0.88, 0.88], [1.0, 0.88, 0.88], [1.0, 0.9, 0.9], [1.0, 0.92, 0.92], [1.0, 0.93, 0.93], [0.98, 0.94, 0.93]]
    
    '''
    1. Using green shade the 4th and 10th spots in the 1st, 2nd, 12th, and 13th
    columns.
    '''
    for c in [1, 2, 12, 13]:
      tile = Tile(column=c, row=4)
      tile.draw('green')
    
    for c in [1, 2, 12, 13]:
      tile = Tile(column=c, row=10)
      tile.draw('green')
    
    '''
    2. Use yellow to shade the 4th and 10th spots in the 4th, 5th, 9th, and 10th
    columns.
    '''
    for c in [4, 5, 9, 10]:
      tile = Tile(column=c, row=4)
      tile.draw('yellow')
    
    for c in [4, 5, 9, 10]:
      tile = Tile(column=c, row=10)
      tile.draw('yellow')
    
    '''
    3. Use green to shade the 7th spots in the 4th, 5th, 9th, and 10th columns.
    '''
    for c in [4, 5, 9, 10]:
      tile = Tile(column=c, row=7)
      tile.draw('green')
    
    '''
    4. Use yellow to shade the 7th spots in the 1st, 2nd, 12th, and 13th columns.
    '''
    for c in [1, 2, 12, 13]:
      tile = Tile(column=c, row=7)
      tile.draw('yellow')
    
    '''
    5. Shade the 3rd, 4th, 9th, and 10th spots green, and the 6th and 7th spots yellow
    in the 7th column.
    '''
    for r in [3, 4, 9, 10]:
      tile = Tile(column=7, row=r)
      tile.draw('green')
    
    for r in [6, 7]:
      tile = Tile(column=7, row=r)
      tile.draw('yellow')
    
    '''
    6. Shade the 3rd, 4th, 9th, and 10th spots yellow, and the 6th and 7th spots green
    in the 16th column.
    '''
    for r in [3, 4, 9, 10]:
      tile = Tile(column=16, row=r)
      tile.draw('yellow')
    
    for r in [6, 7]:
      tile = Tile(column=16, row=r)
      tile.draw('green')
    
    g.plot(gold_boards=gold_boards, multiple=0)
