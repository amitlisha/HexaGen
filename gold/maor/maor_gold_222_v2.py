# Created by maor

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle

task_index = 222
gold_boards = list(read_task(task_index)['gold_boards'])

with Game() as g:
    
    # description:
    # task index: 222, image: P01C08T04, collection round: 1, category: other, group: train
    # agreement scores: [[1.0, 1.0, 1.0], [0.95, 1.0, 0.95], [0.97, 1.0, 0.97], [0.97, 1.0, 0.97], [0.98, 1.0, 0.98], [0.98, 1.0, 0.98], [0.99, 1.0, 0.99], [0.99, 1.0, 0.99], [0.99, 1.0, 0.99]]
    
    '''
    1. in the 6th column from the left, paint the 3rd and 4th tiles down yellow, the
    7th tile red, and the 8th tile orange
    '''
    line = Line(start_tile=Tile(6,3), end_tile=Tile(6,4))
    line.draw('yellow')
    
    tile = Tile(column=6, row=7)
    tile.draw('red')
    tile = Tile(column=6, row=8)
    tile.draw('orange')
    
    
    '''
    2. in the 7th column, pain the 3rd and 5th tiles down yellow, the 4th and 8th tiles
    orange, and the 7th and 9th tiles red
    '''
    column = 7
    for row in [3,5]:
      tile = Tile(column=column, row=row)
      tile.draw('yellow')
    
    for row in [4,8]:
      tile = Tile(column=column, row=row)
      tile.draw('orange')
    
    for row in [7,9]:
      tile = Tile(column=column, row=row)
      tile.draw('red')
    
    '''
    3. in the 8th column, paint the 3rd, 4th, and 5th tiles down yellow, the 6th and
    8th tiles red, and the 7th tile orange
    '''
    column = 8
    line = Line(start_tile=Tile(column,3), end_tile=Tile(column,5))
    line.draw('yellow')
    
    for row in [6,8]:
      tile = Tile(column=column, row=row)
      tile.draw('red')
    
    tile = Tile(column=column, row=7)
    tile.draw('orange')
    
    '''
    4. in the 9th column, paint the 2nd tile down purple, the 4th, 5th, and 6th tiles
    yellow, and the 7th and 8th tiles red
    '''
    column=9
    
    tile = Tile(column=column, row=2)
    tile.draw('purple')
    
    for row in [4,5,6]:
      tile = Tile(column=column, row=row)
      tile.draw('yellow')
    
    for row in [7,8]:
      tile = Tile(column=column, row=row)
      tile.draw('red')
    
    '''
    5. in the 10th column, paint the 2nd through 8th tiles purple
    '''
    line=Line(start_tile=Tile(column=10, row=2), end_tile=Tile(column=10,row=8))
    line.draw('purple')
    
    '''
    6. in the 11th column, paint the 2nd tile down purple, the 4th, 5th, and 6th tiles
    yellow, and the 7th and 8th tiles red
    '''
    column=11
    
    tile = Tile(column=column, row=2)
    tile.draw('purple')
    
    for row in [4,5,6]:
      tile = Tile(column=column, row=row)
      tile.draw('yellow')
    
    for row in [7,8]:
      tile = Tile(column=column, row=row)
      tile.draw('red')
    
    '''
    7. in the 12th column, paint the 3rd, 4th, and 5th tiles down yellow, the 6th and
    8th tiles red, and the 7th tile orange
    '''
    column = 12
    line = Line(start_tile=Tile(column,3), end_tile=Tile(column,5))
    line.draw('yellow')
    
    for row in [6,8]:
      tile = Tile(column=column, row=row)
      tile.draw('red')
    
    tile = Tile(column=column, row=7)
    tile.draw('orange')
    
    '''
    8. in the 13th column, paint the 3rd and 5th tiles down yellow, the 4th and 8th
    tiles orange, and the 7th and 9th tiles red
    '''
    column = 13
    for row in [3,5]:
      tile = Tile(column=column, row=row)
      tile.draw('yellow')
    
    for row in [4,8]:
      tile = Tile(column=column, row=row)
      tile.draw('orange')
    
    for row in [7,9]:
      tile = Tile(column=column, row=row)
      tile.draw('red')
    
    '''
    9. in the 14th column, paint the 3rd and 4th tiles down yellow, the 7th tile red,
    and the 8th tile orange
    '''
    line = Line(start_tile=Tile(14,3), end_tile=Tile(14,4))
    line.draw('yellow')
    
    tile = Tile(column=14, row=7)
    tile.draw('red')
    tile = Tile(column=14, row=8)
    tile.draw('orange')
    
    g.plot(gold_boards=gold_boards, multiple=0)
