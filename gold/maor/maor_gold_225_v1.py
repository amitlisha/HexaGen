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
    tile = Tile(row=2, column=1)
    tile.draw('green')
    
    '''
    2. Fill in the 2nd and 3rd spots on the next column.
    '''
    tile = Tile(row=2, column=2)
    tile.draw('green')
    
    tile = Tile(row=3, column=2)
    tile.draw('green')
    
    '''
    3. Move to the next column and fill in the 2nd and 3rd spots.
    '''
    tile = Tile(row=2, column=3)
    tile.draw('green')
    
    tile = Tile(row=3, column=3)
    tile.draw('green')
    
    '''
    4. Fill in the 3rd - 5th spots on the next column.
    '''
    line = Line(start_tile=Tile(3, 4), end_tile=Tile(5, 4))
    line.draw('green')
    
    '''
    5. Move to the next column and fill in the 3rd and 4th spots.
    '''
    tile = Tile(row=3, column=5)
    tile.draw('green')
    
    tile = Tile(row=4, column=5)
    tile.draw('green')
    
    '''
    6. Fill in the 2nd, and 4th - 7th spots on the next column.
    '''
    tile = Tile(row=2, column=6)
    tile.draw('green')
    
    line = Line(start_tile=Tile(row=4, column=6), end_tile=Tile(row=7, column=6))
    line.draw('green')
    
    '''
    7. On the next column fill in the 4th and 5th spots.
    '''
    tile = Tile(row=4, column=7)
    tile.draw('green')
    
    tile = Tile(row=5, column=7)
    tile.draw('green')
    
    '''
    8. Fill in the 3rd, and 5th - 9th spots on the next column.
    '''
    tile = Tile(row=3, column=8)
    tile.draw('green')
    
    line = Line(start_tile=Tile(row=5, column=8), end_tile=Tile(row=9, column=8))
    line.draw('green')
    
    '''
    9. Move to the next column and fill in the 3rd, 5th, and 6th spots.
    '''
    tile = Tile(row=3, column=9)
    tile.draw('green')
    
    tile = Tile(row=5, column=9)
    tile.draw('green')
    
    tile = Tile(row=6, column=9)
    tile.draw('green')
    
    '''
    10. Fill in the 4th spot, skip a spot, and fill in the rest on the next column.
    '''
    tile = Tile(row=4, column=10)
    tile.draw('green')
    
    line = Line(start_tile=Tile(row=6, column=10), direction='down')
    line.draw('green')
    
    '''
    11. Move to the next column, and fill in the 4th, 6th, and 7th spots.
    '''
    tile = Tile(row=4, column=11)
    tile.draw('green')
    
    tile = Tile(row=6, column=11)
    tile.draw('green')
    
    tile = Tile(row=7, column=11)
    tile.draw('green')
    
    '''
    12. Fill in the 3rd, 5th, and 7th-10th spots.
    '''
    
    tile = Tile(row=3, column=12)
    tile.draw('green')
    
    tile = Tile(row=5, column=12)
    tile.draw('green')
    
    line = Line(start_tile=Tile(row=7, column=12), end_tile=Tile(row=10, column=12))
    line.draw('green')
    
    '''
    13. On the next column fill in the 5th, 7th, and 8th spots.
    '''
    tile = Tile(row=5, column=13)
    tile.draw('green')
    
    tile = Tile(row=7, column=13)
    tile.draw('green')
    
    tile = Tile(row=8, column=13)
    tile.draw('green')
    
    '''
    14. Move to the next column, and fill in the 4th, 6th, and 8th-10th spots.
    '''
    
    tile = Tile(row=4, column=14)
    tile.draw('green')
    
    tile = Tile(row=6, column=14)
    tile.draw('green')
    
    line = Line(start_tile=Tile(row=8, column=14), end_tile=Tile(row=10, column=14))
    line.draw('green')
    
    '''
    15. Fill in the 6th, 8th, and 9th spot on the next column.
    '''
    
    tile = Tile(row=6, column=15)
    tile.draw('green')
    
    tile = Tile(row=8, column=15)
    tile.draw('green')
    
    tile = Tile(row=9, column=15)
    tile.draw('green')
    
    '''
    16. On the next column fill in the 7th, 9th and 10th spots.
    '''
    
    tile = Tile(row=7, column=16)
    tile.draw('green')
    
    tile = Tile(row=9, column=16)
    tile.draw('green')
    
    tile = Tile(row=10, column=16)
    tile.draw('green')
    
    '''
    17. Move to the next column and fill in the last two spots.
    '''
    tile = Tile(row=-2, column=17)
    tile.draw('green')
    
    tile = Tile(row=-1, column=17)
    tile.draw('green')
    
    '''
    18. On the last column fill in only the last spot.
    '''
    
    tile = Tile(row=-1, column=-1)
    tile.draw('green')
    
    g.plot(gold_boards=gold_boards, multiple=0)
