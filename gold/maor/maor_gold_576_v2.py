# Created by maor

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle

task_index = 576
gold_boards = list(read_task(task_index)['gold_boards'])

with Game() as g:
    
    # description:
    # task index: 576, image: P01C04T04, collection round: 0, category: conditions, group: train
    # agreement scores: [[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0]]
    
    '''
    1. Starting at the top of the first column on the left, paint the first hexagon
    orange.
    '''
    tile = Tile(row=1, column=1)
    tile.draw('orange')
    
    '''
    2. Paint the next 4 hexagons down in the first column purple
    '''
    for i in range(4):
      tile = tile.neighbor('down')
      tile.draw('purple')
    
    '''
    3. Copy the same pattern from column 1 into columns 9, 13, 15, and 17.
    '''
    pattern = Shape.get_column(1)
    for c in [9, 13, 15, 17]:
      pattern.copy_paste(source=Tile(1, pattern[0].column), destination=Tile(1, c))
    
    '''
    4. In the second column from the left, paint the 6th through the 9th hexagons blue
    and the last hexagon green.
    '''
    for c in range(6,10):
      tile = Tile(row=c, column=2)
      tile.draw('blue')
    
    tile=Tile(row=10, column=2)
    tile.draw('green')
    
    '''
    5. Copy the same pattern from column 2 into columns 6, 8, 16, and 18.
    '''
    pattern = Shape.get_column(2)
    for c in [6, 8, 16, 18]:
      pattern.copy_paste(source=Tile(1, pattern[0].column), destination=Tile(1, c))
    
    '''
    6. In the 3rd column from the left, paint the top hexagon green and the next four
    hexagons blue.
    '''
    tile = Tile(row=1, column=3)
    tile.draw('green')
    
    for i in range(4):
      tile = tile.neighbor('down')
      tile.draw('blue')
    
    '''
    7. Copy the pattern from the 3rd column into columns 5, 7, and 11.
    '''
    pattern = Shape.get_column(3)
    for c in [5, 7, 11]:
      pattern.copy_paste(source=Tile(1, pattern[0].column), destination=Tile(1, c))
    
    '''
    8. In the 4th column from the left, paint the 6th through the 9th hexagons purple
    and the last hexagon orange.
    '''
    for c in range(6,10):
      tile = Tile(row=c, column=4)
      tile.draw('purple')
    
    tile=Tile(row=10, column=4)
    tile.draw('orange')
    
    '''
    9. Use the pattern from column 4 in columns 10, 12, and 14.
    '''
    pattern = Shape.get_column(4)
    for c in [10, 12, 14]:
      pattern.copy_paste(source=Tile(1, pattern[0].column), destination=Tile(1, c))
    
    g.plot(gold_boards=gold_boards, multiple=0)
