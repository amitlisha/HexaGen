# Created by maor

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle

task_index = 223
gold_boards = list(read_task(task_index)['gold_boards'])

with Game() as g:
    
    # description:
    # task index: 223, image: P01C08T04, collection round: 1, category: other, group: train
    # agreement scores: [[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [0.89, 1.0, 0.89], [0.85, 1.0, 0.85], [0.81, 1.0, 0.81], [0.79, 1.0, 0.79], [0.71, 1.0, 0.71], [0.62, 1.0, 0.62], [0.62, 0.98, 0.64], [0.63, 0.97, 0.65], [0.63, 0.96, 0.66]]
    
    '''
    1. Start in the center on the 10th column, and make the 2nd - 8th spots purple.
    '''
    column = 10
    line=Line(start_tile=Tile(column=column, row=2), end_tile=Tile(column=column,row=8))
    line.draw('purple')
    
    '''
    2. Move out to the next column on the left and right, and make the second spots
    purple.
    '''
    columns = [9,11]
    for c in columns:
      tile = Tile(column=c, row=2).draw('purple')
    
    '''
    3. The 4th - 6th spots should be yellow.
    '''
    for c in columns:
      tile = Tile(column=c, row=4)
      tile.draw('yellow')
      tile = Tile(column=c, row=5)
      tile.draw('yellow')
      tile = Tile(column=c, row=6)
      tile.draw('yellow')
    
    '''
    4. The 7th and 8th spots should be red.
    '''
    for c in columns:
      tile = Tile(column=c, row=7)
      tile.draw('red')
      tile = Tile(column=c, row=8)
      tile.draw('red')
    
    '''
    5. Move to the next columns, and make the 3rd - 5th spots yellow.
    '''
    columns = [12, 8]
    for c in columns:
      tile = Tile(column=c, row=3)
      tile.draw('yellow')
      tile = Tile(column=c, row=4)
      tile.draw('yellow')
      tile = Tile(column=c, row=5)
      tile.draw('yellow')
    
    '''
    6. The next three spots should be red, orange, and red.
    '''
    for c in columns:
      tile=Tile(column=c, row=6)
      tile.draw('red')
      tile=Tile(column=c, row=7)
      tile.draw('orange')
      tile=Tile(column=c, row=8)
      tile.draw('red')
    
    '''
    7. Move to the next columns, and make the 3rd - 5th spots yellow, orange, yellow.
    '''
    columns = [13, 7]
    for c in columns:
      tile=Tile(column=c, row=3)
      tile.draw('yellow')
      tile=Tile(column=c, row=4)
      tile.draw('orange')
      tile=Tile(column=c, row=5)
      tile.draw('yellow')
    
    '''
    8. The 7th - 9th spots should be red, orange, red.
    '''
    for c in columns:
      tile=Tile(column=c, row=7)
      tile.draw('red')
      tile=Tile(column=c, row=8)
      tile.draw('orange')
      tile=Tile(column=c, row=9)
      tile.draw('red')
    
    '''
    9. Move to the next columns, and make the 3rd and 4th spots yellow.
    '''
    columns = [14, 6]
    for c in columns:
      tile=Tile(column=c, row=3)
      tile.draw('yellow')
      tile=Tile(column=c, row=4)
      tile.draw('yellow')
    
    '''
    10. Make the 7th spot red.
    '''
    for c in columns:
      tile=Tile(column=c, row=7)
      tile.draw('red')
    
    '''
    11. Make the 8th spot orange.
    '''
    for c in columns:
      tile=Tile(column=c, row=8)
      tile.draw('orange')
    
    g.plot(gold_boards=gold_boards, multiple=0)
