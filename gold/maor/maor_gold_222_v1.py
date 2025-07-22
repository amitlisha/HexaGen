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
    tile = Tile(row=3, column=6)
    tile.draw('yellow')
    tile = Tile(row=4, column=6)
    tile.draw('yellow')
    
    tile = Tile(row=7, column=6)
    tile.draw('red')
    tile = Tile(row=8, column=6)
    tile.draw('orange')
    
    
    '''
    2. in the 7th column, pain the 3rd and 5th tiles down yellow, the 4th and 8th tiles
    orange, and the 7th and 9th tiles red
    '''
    tile = Tile(row=3, column=7)
    tile.draw('yellow')
    tile = Tile(row=5, column=7)
    tile.draw('yellow')
    
    tile = Tile(row=4, column=7)
    tile.draw('orange')
    tile = Tile(row=8, column=7)
    tile.draw('orange')
    
    tile = Tile(row=7, column=7)
    tile.draw('red')
    tile = Tile(row=9, column=7)
    tile.draw('red')
    
    '''
    3. in the 8th column, paint the 3rd, 4th, and 5th tiles down yellow, the 6th and
    8th tiles red, and the 7th tile orange
    '''
    tile = Tile(row=3, column=8)
    tile.draw('yellow')
    tile = Tile(row=4, column=8)
    tile.draw('yellow')
    tile = Tile(row=5, column=8)
    tile.draw('yellow')
    
    tile = Tile(row=6, column=8)
    tile.draw('red')
    tile = Tile(row=8, column=8)
    tile.draw('red')
    
    tile = Tile(row=7, column=8)
    tile.draw('orange')
    
    '''
    4. in the 9th column, paint the 2nd tile down purple, the 4th, 5th, and 6th tiles
    yellow, and the 7th and 8th tiles red
    '''
    tile = Tile(row=2, column=9)
    tile.draw('purple')
    
    tile = Tile(row=4, column=9)
    tile.draw('yellow')
    tile = Tile(row=5, column=9)
    tile.draw('yellow')
    tile = Tile(row=6, column=9)
    tile.draw('yellow')
    
    tile = Tile(row=7, column=9)
    tile.draw('red')
    tile = Tile(row=8, column=9)
    tile.draw('red')
    
    '''
    5. in the 10th column, paint the 2nd through 8th tiles purple
    '''
    line=Line(start_tile=Tile(row=2, column=10), end_tile=Tile(row=8, column=10))
    line.draw('purple')
    
    '''
    6. in the 11th column, paint the 2nd tile down purple, the 4th, 5th, and 6th tiles
    yellow, and the 7th and 8th tiles red
    '''
    tile = Tile(row=2, column=11)
    tile.draw('purple')
    
    tile = Tile(row=4, column=11)
    tile.draw('yellow')
    tile = Tile(row=5, column=11)
    tile.draw('yellow')
    tile = Tile(row=6, column=11)
    tile.draw('yellow')
    
    tile = Tile(row=7, column=11)
    tile.draw('red')
    tile = Tile(row=8, column=11)
    tile.draw('red')
    
    '''
    7. in the 12th column, paint the 3rd, 4th, and 5th tiles down yellow, the 6th and
    8th tiles red, and the 7th tile orange
    '''
    tile = Tile(row=3, column=12)
    tile.draw('yellow')
    tile = Tile(row=4, column=12)
    tile.draw('yellow')
    tile = Tile(row=5, column=12)
    tile.draw('yellow')
    
    tile = Tile(row=6, column=12)
    tile.draw('red')
    tile = Tile(row=8, column=12)
    tile.draw('red')
    
    tile = Tile(row=7, column=12)
    tile.draw('orange')
    
    '''
    8. in the 13th column, paint the 3rd and 5th tiles down yellow, the 4th and 8th
    tiles orange, and the 7th and 9th tiles red
    '''
    
    tile = Tile(row=3, column=13)
    tile.draw('yellow')
    tile = Tile(row=5, column=13)
    tile.draw('yellow')
    
    tile = Tile(row=4, column=13)
    tile.draw('orange')
    tile = Tile(row=8, column=13)
    tile.draw('orange')
    
    tile = Tile(row=7, column=13)
    tile.draw('red')
    tile = Tile(row=9, column=13)
    tile.draw('red')
    
    '''
    9. in the 14th column, paint the 3rd and 4th tiles down yellow, the 7th tile red,
    and the 8th tile orange
    '''
    tile = Tile(row=3, column=14)
    tile.draw('yellow')
    tile = Tile(row=4, column=14)
    tile.draw('yellow')
    
    tile = Tile(row=7, column=14)
    tile.draw('red')
    tile = Tile(row=8, column=14)
    tile.draw('orange')
    
    g.plot(gold_boards=gold_boards, multiple=0)
