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
      line = Line(start_tile=Tile(column=c, row=3), end_tile=Tile(column=c, row=4))
      line.draw('orange')
      line = Line(start_tile=Tile(column=c, row=6), end_tile=Tile(column=c, row=7))
      line.draw('purple')
      line = Line(start_tile=Tile(column=c, row=-1), direction='up', length=2)
      line.draw('blue')
    
    '''
    2. In columns, # 2 and 14 paint the second, fourth, and ninth tiles down orange,
    paint the third, fifth, and seventh tiles down purple, paint the sixth, eighth
    and tenth tiles down blue.
    '''
    tile = Tile(column=2, row=2)
    tile.draw('orange')
    tile = Tile(column=2, row=4)
    tile.draw('orange')
    tile = Tile(column=2, row=9)
    tile.draw('orange')
    tile = Tile(column=2, row=3)
    tile.draw('purple')
    tile = Tile(column=2, row=5)
    tile.draw('purple')
    tile = Tile(column=2, row=7)
    tile.draw('purple')
    tile = Tile(column=2, row=6)
    tile.draw('blue')
    tile = Tile(column=2, row=8)
    tile.draw('blue')
    tile = Tile(column=2, row=10)
    tile.draw('blue')
    tile = Tile(column=14, row=2)
    tile.draw('orange')
    tile = Tile(column=14, row=4)
    tile.draw('orange')
    tile = Tile(column=14, row=9)
    tile.draw('orange')
    tile = Tile(column=14, row=3)
    tile.draw('purple')
    tile = Tile(column=14, row=5)
    tile.draw('purple')
    tile = Tile(column=14, row=7)
    tile.draw('purple')
    tile = Tile(column=14, row=6)
    tile.draw('blue')
    tile = Tile(column=14, row=8)
    tile.draw('blue')
    tile = Tile(column=14, row=10)
    tile.draw('blue')
    
    '''
    3. In columns # 5, and 7 paint the third and fourth tile down blue, paint the sixth
    and seventh tiles down orange, and paint the 2 bottommost tiles purple.
    '''
    for c in [5,7]:
      line = Line(start_tile=Tile(column=c, row=3), end_tile=Tile(column=c, row=4))
      line.draw('blue')
      line = Line(start_tile=Tile(column=c, row=6), end_tile=Tile(column=c, row=7))
      line.draw('orange')
      line = Line(start_tile=Tile(column=c, row=-1), direction='up', length=2)
      line.draw('purple')
    
    '''
    4. In column # 6 paint the second, fourth, and ninth tiles down blue, paint the
    third, fifth, and seventh tiles down orange, paint the sixth, eighth and tenth
    tiles down purple.
    '''
    tile = Tile(column=6, row=2)
    tile.draw('blue')
    tile = Tile(column=6, row=4)
    tile.draw('blue')
    tile = Tile(column=6, row=9)
    tile.draw('blue')
    tile = Tile(column=6, row=3)
    tile.draw('orange')
    tile = Tile(column=6, row=5)
    tile.draw('orange')
    tile = Tile(column=6, row=7)
    tile.draw('orange')
    tile = Tile(column=6, row=6)
    tile.draw('purple')
    tile = Tile(column=6, row=8)
    tile.draw('purple')
    tile = Tile(column=6, row=10)
    tile.draw('purple')
    
    '''
    5. In columns, # 9, and 11 paint the third and fourth tile down purple, paint the
    sixth and seventh tiles down blue and paint the 2 bottommost tiles orange.
    '''
    for c in [9,11]:
      line = Line(start_tile=Tile(column=c, row=3), end_tile=Tile(column=c, row=4))
      line.draw('purple')
      line = Line(start_tile=Tile(column=c, row=6), end_tile=Tile(column=c, row=7))
      line.draw('blue')
      line = Line(start_tile=Tile(column=c, row=-1), direction='up', length=2)
      line.draw('orange')
    
    '''
    6. In column # 10 paint the second, fourth, and ninth tiles down purple, paint the
    third, fifth, and seventh tiles down blue, paint the sixth, eighth and tenth
    tiles down orange.
    '''
    tile = Tile(column=10, row=2)
    tile.draw('purple')
    tile = Tile(column=10, row=4)
    tile.draw('purple')
    tile = Tile(column=10, row=9)
    tile.draw('purple')
    tile = Tile(column=10, row=3)
    tile.draw('blue')
    tile = Tile(column=10, row=5)
    tile.draw('blue')
    tile = Tile(column=10, row=7)
    tile.draw('blue')
    tile = Tile(column=10, row=6)
    tile.draw('orange')
    tile = Tile(column=10, row=8)
    tile.draw('orange')
    tile = Tile(column=10, row=10)
    tile.draw('orange')
    
    g.plot(gold_boards=gold_boards, multiple=0)
