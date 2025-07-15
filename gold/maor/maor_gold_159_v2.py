# Created by maor

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle

task_index = 159
gold_boards = list(read_task(task_index)['gold_boards'])

with Game() as g:
    
    # description:
    # task index: 159, image: P01C04T02, collection round: 1, category: conditions, group: train
    # agreement scores: [[0.91, 1.0, 0.91], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0]]
    
    '''
    1. In columns # 1, 3, 13, and 15 paint the third and fourth tile down orange paint
    the sixth and seventh tiles down purple and paint the 2 bottommost tiles blue.
    '''
    for c in [1,3,13,15]:
      line = Line(start_tile=Tile(row=3, column=c), end_tile=Tile(row=4, column=c))
      line.draw('orange')
      line = Line(start_tile=Tile(row=6, column=c), end_tile=Tile(row=7, column=c))
      line.draw('purple')
      line = Line(start_tile=Tile(row=-1, column=c), direction='up', length=2)
      line.draw('blue')
    
    '''
    2. In columns, # 2 and 14 paint the second, fourth, and ninth tiles down orange,
    paint the third, fifth, and seventh tiles down purple, paint the sixth, eighth
    and tenth tiles down blue.
    '''
    tile = Tile(row=2, column=2)
    tile.draw('orange')
    tile = Tile(row=4, column=2)
    tile.draw('orange')
    tile = Tile(row=9, column=2)
    tile.draw('orange')
    tile = Tile(row=3, column=2)
    tile.draw('purple')
    tile = Tile(row=5, column=2)
    tile.draw('purple')
    tile = Tile(row=7, column=2)
    tile.draw('purple')
    tile = Tile(row=6, column=2)
    tile.draw('blue')
    tile = Tile(row=8, column=2)
    tile.draw('blue')
    tile = Tile(row=10, column=2)
    tile.draw('blue')
    tile = Tile(row=2, column=14)
    tile.draw('orange')
    tile = Tile(row=4, column=14)
    tile.draw('orange')
    tile = Tile(row=9, column=14)
    tile.draw('orange')
    tile = Tile(row=3, column=14)
    tile.draw('purple')
    tile = Tile(row=5, column=14)
    tile.draw('purple')
    tile = Tile(row=7, column=14)
    tile.draw('purple')
    tile = Tile(row=6, column=14)
    tile.draw('blue')
    tile = Tile(row=8, column=14)
    tile.draw('blue')
    tile = Tile(row=10, column=14)
    tile.draw('blue')
    
    '''
    3. In columns # 5, and 7 paint the third and fourth tile down blue, paint the sixth
    and seventh tiles down orange, and paint the 2 bottommost tiles purple.
    '''
    for c in [5,7]:
      line = Line(start_tile=Tile(row=3, column=c), end_tile=Tile(row=4, column=c))
      line.draw('blue')
      line = Line(start_tile=Tile(row=6, column=c), end_tile=Tile(row=7, column=c))
      line.draw('orange')
      line = Line(start_tile=Tile(row=-1, column=c), direction='up', length=2)
      line.draw('purple')
    
    '''
    4. In column # 6 paint the second, fourth, and ninth tiles down blue, paint the
    third, fifth, and seventh tiles down orange, paint the sixth, eighth and tenth
    tiles down purple.
    '''
    tile = Tile(row=2, column=6)
    tile.draw('blue')
    tile = Tile(row=4, column=6)
    tile.draw('blue')
    tile = Tile(row=9, column=6)
    tile.draw('blue')
    tile = Tile(row=3, column=6)
    tile.draw('orange')
    tile = Tile(row=5, column=6)
    tile.draw('orange')
    tile = Tile(row=7, column=6)
    tile.draw('orange')
    tile = Tile(row=6, column=6)
    tile.draw('purple')
    tile = Tile(row=8, column=6)
    tile.draw('purple')
    tile = Tile(row=10, column=6)
    tile.draw('purple')
    
    '''
    5. In columns, # 9, and 11 paint the third and fourth tile down purple, paint the
    sixth and seventh tiles down blue and paint the 2 bottommost tiles orange.
    '''
    for c in [9,11]:
      line = Line(start_tile=Tile(row=3, column=c), end_tile=Tile(row=4, column=c))
      line.draw('purple')
      line = Line(start_tile=Tile(row=6, column=c), end_tile=Tile(row=7, column=c))
      line.draw('blue')
      line = Line(start_tile=Tile(row=-1, column=c), direction='up', length=2)
      line.draw('orange')
    
    '''
    6. In column # 10 paint the second, fourth, and ninth tiles down purple, paint the
    third, fifth, and seventh tiles down blue, paint the sixth, eighth and tenth
    tiles down orange.
    '''
    tile = Tile(row=2, column=10)
    tile.draw('purple')
    tile = Tile(row=4, column=10)
    tile.draw('purple')
    tile = Tile(row=9, column=10)
    tile.draw('purple')
    tile = Tile(row=3, column=10)
    tile.draw('blue')
    tile = Tile(row=5, column=10)
    tile.draw('blue')
    tile = Tile(row=7, column=10)
    tile.draw('blue')
    tile = Tile(row=6, column=10)
    tile.draw('orange')
    tile = Tile(row=8, column=10)
    tile.draw('orange')
    tile = Tile(row=10, column=10)
    tile.draw('orange')
    
    g.plot(gold_boards=gold_boards, multiple=0)
