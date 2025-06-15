# Created by maor

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle

task_index = 225
gold_boards = list(read_task(task_index)['gold_boards'])

with Game() as g:
    
    # description:
    # task index: 225, image: P01C08T06, collection round: 1, category: other, group: train
    # agreement scores: [[0, 0, 0], [1.0, 0.67, 0.67], [1.0, 0.8, 0.8], [1.0, 0.88, 0.88], [1.0, 0.9, 0.9], [0.96, 0.93, 0.9], [0.97, 0.94, 0.91], [0.98, 0.96, 0.93], [0.98, 0.96, 0.94], [0.98, 0.97, 0.95], [0.98, 0.97, 0.95], [0.99, 0.98, 0.96], [0.96, 0.98, 0.94], [0.99, 0.93, 0.92], [0.99, 0.93, 0.93], [0.99, 0.91, 0.89], [0.99, 0.91, 0.9], [0.99, 1.0, 0.99]]
    
    '''
    1. Use green to fill in the second spot on the 1st column.
    '''
    tile = Tile(column=1, row=2)
    tile.draw('green')
    
    '''
    2. Fill in the 2nd and 3rd spots on the next column.
    '''
    c = tile.neighbor('up_right').column
    for r in [2,3]:
      tile = Tile(column=c, row=r)
      tile.draw('green')
    
    '''
    3. Move to the next column and fill in the 2nd and 3rd spots.
    '''
    c = tile.neighbor('up_right').column
    for r in [2,3]:
      tile = Tile(column=c, row=r)
      tile.draw('green')
    
    '''
    4. Fill in the 3rd - 5th spots on the next column.
    '''
    c = tile.neighbor('up_right').column
    for r in range(3,6):
      tile = Tile(column=c, row=r)
      tile.draw('green')
    
    '''
    5. Move to the next column and fill in the 3rd and 4th spots.
    '''
    c = tile.neighbor('up_right').column
    for r in [3,4]:
      tile = Tile(column=c, row=r)
      tile.draw('green')
    
    '''
    6. Fill in the 2nd, and 4th - 7th spots on the next column.
    '''
    c = tile.neighbor('up_right').column
    for r in [2] + list(range(4,8)):
      tile = Tile(column=c, row=r)
      tile.draw('green')
    
    '''
    7. On the next column fill in the 4th and 5th spots.
    '''
    c = tile.neighbor('up_right').column
    for r in [4,5]:
      tile = Tile(column=c, row=r)
      tile.draw('green')
    
    '''
    8. Fill in the 3rd, and 5th - 9th spots on the next column.
    '''
    c = tile.neighbor('up_right').column
    for r in [3] + list(range(5,10)):
      tile = Tile(column=c, row=r)
      tile.draw('green')
    
    '''
    9. Move to the next column and fill in the 3rd, 5th, and 6th spots.
    '''
    c = tile.neighbor('up_right').column
    for r in [3,5,6]:
      tile = Tile(column=c, row=r)
      tile.draw('green')
    
    '''
    10. Fill in the 4th spot, skip a spot, and fill in the rest on the next column.
    '''
    c = tile.neighbor('up_right').column
    
    tile = Tile(column=c, row=4)
    tile.draw('green')
    
    line = Line(start_tile=Tile(column=c, row=6), direction='down')
    line.draw('green')
    
    '''
    11. Move to the next column, and fill in the 4th, 6th, and 7th spots.
    '''
    c = tile.neighbor('up_right').column
    for r in [4,6,7]:
      tile = Tile(column=c, row=r)
      tile.draw('green')
    
    '''
    12. Fill in the 3rd, 5th, and 7th-10th spots.
    '''
    
    c = tile.neighbor('up_right').column
    for r in [3,5] + list(range(7,11)):
      tile = Tile(column=c, row=r)
      tile.draw('green')
    
    '''
    13. On the next column fill in the 5th, 7th, and 8th spots.
    '''
    c = tile.neighbor('up_right').column
    for r in [5,7,8]:
      tile = Tile(column=c, row=r)
      tile.draw('green')
    
    '''
    14. Move to the next column, and fill in the 4th, 6th, and 8th-10th spots.
    '''
    
    c = tile.neighbor('up_right').column
    for r in [4,6]+list(range(8,11)):
      tile = Tile(column=c, row=r)
      tile.draw('green')
    
    '''
    15. Fill in the 6th, 8th, and 9th spot on the next column.
    '''
    
    c = tile.neighbor('up_right').column
    for r in [6,8,9]:
      tile = Tile(column=c, row=r)
      tile.draw('green')
    
    '''
    16. On the next column fill in the 7th, 9th and 10th spots.
    '''
    
    c = tile.neighbor('up_right').column
    for r in [7,9,10]:
      tile = Tile(column=c, row=r)
      tile.draw('green')
    
    '''
    17. Move to the next column and fill in the last two spots.
    '''
    c = tile.neighbor('up_right').column
    for r in range(-1,-3,-1):
      tile = Tile(column=c, row=r)
      tile.draw('green')
    
    '''
    18. On the last column fill in only the last spot.
    '''
    c = tile.neighbor('up_right').column
    tile = Tile(column=c, row=-1)
    tile.draw('green')
    
    g.plot(gold_boards=gold_boards, multiple=0)
