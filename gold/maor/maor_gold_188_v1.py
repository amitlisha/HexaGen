# Created by maor

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle

task_index = 188
gold_boards = list(read_task(task_index)['gold_boards'])

with Game() as g:
    
    # description:
    # task index: 188, image: P01C04T18, collection round: 1, category: conditions, group: train
    # agreement scores: [[0.11, 0.67, 0.2], [0.31, 1.0, 0.31], [0.33, 1.0, 0.33], [1.0, 1.0, 1.0], [0.97, 1.0, 0.97], [0.94, 1.0, 0.94], [0.92, 1.0, 0.92], [0.89, 1.0, 0.89], [0.86, 1.0, 0.86], [0.84, 1.0, 0.84], [0.82, 1.0, 0.82], [0.78, 1.0, 0.78], [0.78, 0.99, 0.77], [0.79, 1.0, 0.79], [0.79, 1.0, 0.79], [0.8, 1.0, 0.8], [0.8, 1.0, 0.8], [0.81, 1.0, 0.81]]
    
    '''
    1. start a diagonal line from the bottom left hexagon to the top right hexagon by
    painting the bottom left tile blue.
    '''
    tile = Tile(column=1, row=-1)
    tile.draw('blue')
    
    '''
    2. working diagonally up from the bottom left, the next tiles should be painted
    blue, two oranges, one blue, two oranges, three blues, two oranges, one blue,
    two oranges, one blue, and two oranges.
    '''
    tile = tile.neighbor('up_right')
    tile.draw('blue')
    
    for i in range(2):
      tile = tile.neighbor('up_right')
      tile.draw('orange')
    
    tile = tile.neighbor('up_right')
    tile.draw('blue')
    
    for i in range(2):
      tile = tile.neighbor('up_right')
      tile.draw('orange')
    
    for i in range(3):
      tile = tile.neighbor('up_right')
      tile.draw('blue')
    
    for i in range(2):
      tile = tile.neighbor('up_right')
      tile.draw('orange')
    
    tile = tile.neighbor('up_right')
    tile.draw('blue')
    
    for i in range(2):
      tile = tile.neighbor('up_right')
      tile.draw('orange')
    
    tile = tile.neighbor('up_right')
    tile.draw('blue')
    
    for i in range(2):
      tile = tile.neighbor('up_right')
      tile.draw('orange')
    
    '''
    3. Create a second diagonal line by painting the fourth tile up from the bottom in
    the first column purple.
    '''
    tile = Tile(column=1, row=-4)
    tile.draw('purple')
    
    '''
    4. working diagonally up from that point, the next tiles should be painted one
    purple, one green, one purple, one green, three purples, two greens, two
    purples, and one green
    '''
    tile = tile.neighbor('up_right')
    tile.draw('purple')
    
    tile = tile.neighbor('up_right')
    tile.draw('green')
    
    tile = tile.neighbor('up_right')
    tile.draw('purple')
    
    tile = tile.neighbor('up_right')
    tile.draw('green')
    
    for i in range(3):
      tile = tile.neighbor('up_right')
      tile.draw('purple')
    
    for i in range(2):
      tile = tile.neighbor('up_right')
      tile.draw('green')
    
    for i in range(2):
      tile = tile.neighbor('up_right')
      tile.draw('purple')
    
    tile = tile.neighbor('up_right')
    tile.draw('green')
    
    '''
    5. in the 2nd column, paint the 4th tile up red
    '''
    tile = Tile(column=2, row=-4)
    tile.draw('red')
    
    '''
    6. in the 3rd column, paint the 3rd tile up red
    '''
    tile = Tile(column=3, row=-3)
    tile.draw('red')
    
    '''
    7. in the 4th column, paint the 5th tile up yellow
    '''
    tile = Tile(column=4, row=-5)
    tile.draw('yellow')
    
    '''
    8. in the 5th column, paint the 4th tile up yellow
    '''
    tile = Tile(column=5, row=-4)
    tile.draw('yellow')
    
    '''
    9. in the sixth column, paint the 6th column up red
    '''
    tile = Tile(column=6, row=-6)
    tile.draw('red')
    
    '''
    10. in the 7th column, paint the 5th tile up red
    '''
    tile = Tile(column=7, row=-5)
    tile.draw('red')
    
    '''
    11. in the 8th column, paint the 7th tile up yellow
    '''
    tile = Tile(column=8, row=-7)
    tile.draw('yellow')
    
    '''
    12. in the 9th column, paint the 6th tile up yellow
    '''
    tile = Tile(column=9, row=-6)
    tile.draw('yellow')
    
    '''
    13. in the 10th column, paint the 3rd tile down yellow
    '''
    tile = Tile(column=10, row=3)
    tile.draw('yellow')
    
    '''
    14. in the 11th column, paint the 4th tile down yellow
    '''
    tile = Tile(column=11, row=4)
    tile.draw('yellow')
    
    '''
    15. in the 12th column, paint the 2nd tile down red
    '''
    tile = Tile(column=12, row=2)
    tile.draw('red')
    
    '''
    16. in the 13th column, paint the 3rd tile down red
    '''
    tile = Tile(column=13, row=3)
    tile.draw('red')
    
    '''
    17. in the 14 column, paint the first tile red
    '''
    tile = Tile(column=14, row=1)
    tile.draw('red')
    
    '''
    18. in the 15th column, paint the 2nd tile down red
    '''
    tile = Tile(column=15, row=2)
    tile.draw('red')
    
    g.plot(gold_boards=gold_boards, multiple=0)
