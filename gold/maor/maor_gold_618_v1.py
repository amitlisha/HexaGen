# Created by maor

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle

task_index = 618
gold_boards = list(read_task(task_index)['gold_boards'])

with Game() as g:
    
    # description:
    # task index: 618, image: P01C04T20, collection round: 0, category: conditions, group: train
    # agreement scores: None
    
    '''
    1. On the second column, fill out the top three hexagons in purple.
    '''
    line = Line(start_tile=Tile(1, 2), length=3, direction='down')
    line.draw('purple')
    
    '''
    2. Leave three spaces and fill out the next three hexagons in orange.
    '''
    tile = line.end_tile
    for i in range(4):
      tile = tile.neighbor(direction='down')
    
    line = Line(start_tile=tile, length=3, direction='down')
    line.draw('orange')
    
    '''
    3. On the third column, fill out the first hexagon in purple, then two green, then
    one purple.
    '''
    tile = Tile(row=1, column=3)
    tile.draw('purple')
    
    line = Line(start_tile=tile, length=2, direction='down',include_start_tile=False)
    line.draw('green')
    
    tile = line.end_tile.neighbor(direction='down')
    tile.draw('purple')
    
    '''
    4. Leave two spaces, then fill out the next hexagon in orange, then green, purple,
    and orange.
    '''
    for i in range(3):
      tile = tile.neighbor(direction='down')
    
    tile.draw('orange')
    
    tile=tile.neighbor(direction='down')
    tile.draw('green')
    
    tile=tile.neighbor(direction='down')
    tile.draw('blue')
    
    tile=tile.neighbor(direction='down')
    tile.draw('orange')
    
    '''
    5. On the fourth column, fill out the top three hexagons in purple.
    '''
    line = Line(start_tile=Tile(1, 4), length=3, direction='down')
    line.draw('purple')
    
    '''
    6. Leave three spaces and fill out the next three hexagons in orange.
    '''
    tile = line.end_tile
    for i in range(4):
      tile = tile.neighbor(direction='down')
    
    line = Line(start_tile=tile, length=3, direction='down')
    line.draw('orange')
    
    '''
    7. The fifth column is left blank.
    '''
    
    '''
    8. On the sixth column, fill out the top three hexagons in orange.
    '''
    line = Line(start_tile=Tile(1, 6), length=3, direction='down')
    line.draw('orange')
    
    '''
    9. Leave three spaces and fill out the next three hexagons in purple.
    '''
    tile = line.end_tile
    for i in range(4):
      tile = tile.neighbor(direction='down')
    
    line = Line(start_tile=tile, length=3, direction='down')
    line.draw('purple')
    
    '''
    10. On the seventh column, fill out the first hexagon in orange, then green, then
    blue, then orange.
    '''
    tile = Tile(row=1, column=7)
    tile.draw('orange')
    
    tile=tile.neighbor(direction='down')
    tile.draw('green')
    
    tile=tile.neighbor(direction='down')
    tile.draw('blue')
    
    tile=tile.neighbor(direction='down')
    tile.draw('orange')
    
    '''
    11. Leave two spaces and then fill out the next hexagon in purple, then two green,
    then purple again.
    '''
    for i in range(3):
      tile = tile.neighbor(direction='down')
    
    tile.draw('purple')
    
    tile=tile.neighbor(direction='down')
    tile.draw('green')
    
    tile=tile.neighbor(direction='down')
    tile.draw('green')
    
    tile=tile.neighbor(direction='down')
    tile.draw('purple')
    
    '''
    12. On the eigth column, fill out the first three hexagons in orange.
    '''
    line = Line(start_tile=Tile(1, 8), length=3, direction='down')
    line.draw('orange')
    
    '''
    13. Leave three spaces and fill out the next three hexagons in purple.
    '''
    tile = line.end_tile
    for i in range(4):
      tile = tile.neighbor(direction='down')
    
    line = Line(start_tile=tile, length=3, direction='down')
    line.draw('purple')
    
    '''
    14. The ninth column is left blank.
    '''
    
    '''
    15. On the 10th column, fill out the top three hexagons in orange.
    '''
    line = Line(start_tile=Tile(1, 10), length=3, direction='down')
    line.draw('orange')
    
    '''
    16. Leave three spaces and then fill out the next three hexagons in purple.
    '''
    tile = line.end_tile
    for i in range(4):
      tile = tile.neighbor(direction='down')
    
    line = Line(start_tile=tile, length=3, direction='down')
    line.draw('purple')
    
    '''
    17. On the 11th column, fill out the first hexagon in orange, then blue, then green,
    then orange again.
    '''
    tile=Tile(row=1, column=11)
    tile.draw('orange')
    
    tile=tile.neighbor(direction='down')
    tile.draw('blue')
    
    tile=tile.neighbor(direction='down')
    tile.draw('green')
    
    tile=tile.neighbor(direction='down')
    tile.draw('orange')
    
    '''
    18. Leave two blank spaces and fill out the next hexagon in purple, then two blue,
    then one purple.
    '''
    for i in range(3):
      tile = tile.neighbor(direction='down')
    
    tile.draw('purple')
    
    tile=tile.neighbor(direction='down')
    tile.draw('blue')
    
    tile=tile.neighbor(direction='down')
    tile.draw('blue')
    
    tile=tile.neighbor(direction='down')
    tile.draw('purple')
    
    '''
    19. On the 12th column, fill out the first three hexagons in orange.
    '''
    line = Line(start_tile=Tile(1, 12), length=3, direction='down')
    line.draw('orange')
    
    '''
    20. Leave three spaces and fill out the next three hexagons in purple.
    '''
    tile = line.end_tile
    for i in range(4):
      tile = tile.neighbor(direction='down')
    
    line = Line(start_tile=tile, length=3, direction='down')
    line.draw('purple')
    
    '''
    21. The 13th column is left blank.
    '''
    
    '''
    22. On the 14th column, fill out the top three hexagons in purple.
    '''
    line = Line(start_tile=Tile(1, 14), length=3, direction='down')
    line.draw('purple')
    
    '''
    23. Leave three spaces and fill out the next three hexagons in purple.
    '''
    tile = line.end_tile
    for i in range(4):
      tile = tile.neighbor(direction='down')
    
    line = Line(start_tile=tile, length=3, direction='down')
    line.draw('purple')
    
    '''
    24. On the 15th column, fill out the first hexagon in purple, then two blue, then
    purple again.
    '''
    tile=Tile(row=1, column=15)
    tile.draw('purple')
    
    tile=tile.neighbor(direction='down')
    tile.draw('blue')
    
    tile=tile.neighbor(direction='down')
    tile.draw('blue')
    
    tile=tile.neighbor(direction='down')
    tile.draw('purple')
    
    '''
    25. Leave two blank spaces and fill out the next hexagon in purple, then two green,
    then one purple again.
    '''
    for i in range(3):
      tile = tile.neighbor(direction='down')
    
    tile.draw('purple')
    
    tile=tile.neighbor(direction='down')
    tile.draw('green')
    
    tile=tile.neighbor(direction='down')
    tile.draw('green')
    
    tile=tile.neighbor(direction='down')
    tile.draw('purple')
    
    '''
    26. On the 16th column, fill out the top three hexagons in purple.
    '''
    line = Line(start_tile=Tile(1, 16), length=3, direction='down')
    line.draw('purple')
    
    '''
    27. Leave three blank spaces and then fill out the next three hexagons in purple.
    '''
    tile = line.end_tile
    for i in range(4):
      tile = tile.neighbor(direction='down')
    
    line = Line(start_tile=tile, length=3, direction='down')
    line.draw('purple')
    
    g.plot(gold_boards=gold_boards, multiple=0)
