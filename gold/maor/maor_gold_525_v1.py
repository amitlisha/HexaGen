# Created by maor

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle

task_index = 525
gold_boards = list(read_task(task_index)['gold_boards'])

with Game() as g:
    
    # description:
    # task index: 525, image: P01C04T04, collection round: 0, category: conditions, group: train
    # agreement scores: [[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 0.95, 0.95], [1.0, 1.0, 1.0], [1.0, 0.95, 0.95], [1.0, 1.0, 1.0], [1.0, 0.99, 0.99], [1.0, 0.95, 0.95], [1.0, 0.96, 0.96], [1.0, 1.0, 1.0], [1.0, 0.96, 0.96], [1.0, 1.0, 1.0], [1.0, 0.97, 0.97], [1.0, 1.0, 1.0], [1.0, 0.97, 0.97], [1.0, 1.0, 1.0], [1.0, 0.97, 0.97], [1.0, 1.0, 1.0], [1.0, 0.97, 0.97], [1.0, 1.0, 1.0], [1.0, 0.97, 0.97], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0]]
    
    '''
    1. Paint the leftmost tile at the top orange
    '''
    tile = Tile(row=1, column=1)
    tile.draw('orange')
    
    '''
    2. Paint the next four tiles directly below it purple.
    '''
    line = Line(start_tile=tile, length=4, direction='down', include_start_tile=False)
    line.draw('purple')
    
    '''
    3. Move to the next column, and paint the tile at the bottom green.
    '''
    tile = Tile(row=-1, column=2)
    tile.draw('green')
    
    '''
    4. Paint the next four tiles directly above it blue.
    '''
    line = Line(start_tile=tile, length=4, direction='up', include_start_tile=False)
    line.draw('blue')
    
    '''
    5. Move to the next column, and paint the tile at the top green.
    '''
    tile = Tile(row=1, column=3)
    tile.draw('green')
    
    '''
    6. Paint the next four tiles directly below it blue.
    '''
    line = Line(start_tile=tile, length=4, direction='down', include_start_tile=False)
    line.draw('blue')
    
    '''
    7. Move to the next column, and paint the tile at the bottom orange.
    '''
    tile = Tile(row=-1, column=4)
    tile.draw('orange')
    
    '''
    8. Paint the next four tiles directly above it purple.
    '''
    line = Line(start_tile=tile, length=4, direction='up', include_start_tile=False)
    line.draw('purple')
    
    '''
    9. Move to the next column, and paint the tile at the top green.
    '''
    tile = Tile(row=1, column=5)
    tile.draw('green')
    
    '''
    10. Paint the next four tiles directly below it blue.
    '''
    line = Line(start_tile=tile, length=4, direction='down', include_start_tile=False)
    line.draw('blue')
    
    '''
    11. Move to the next column, and paint the tile at the bottom green.
    '''
    tile = Tile(row=-1, column=6)
    tile.draw('green')
    
    '''
    12. Paint the next four tiles directly above it blue.
    '''
    line = Line(start_tile=tile, length=4, direction='up', include_start_tile=False)
    line.draw('blue')
    
    '''
    13. Move to the next column, and paint the tile at the top green.
    '''
    tile = Tile(row=1, column=7)
    tile.draw('green')
    
    '''
    14. Paint the next four tiles directly below it blue.
    '''
    line = Line(start_tile=tile, length=4, direction='down', include_start_tile=False)
    line.draw('blue')
    
    '''
    15. Move to the next column, and paint the tile at the bottom green.
    '''
    tile = Tile(row=-1, column=8)
    tile.draw('green')
    
    '''
    16. Paint the next four tiles directly above it blue.
    '''
    line = Line(start_tile=tile, length=4, direction='up', include_start_tile=False)
    line.draw('blue')
    
    '''
    17. Move to the next column, and paint the tile at the top orange.
    '''
    tile = Tile(row=1, column=9)
    tile.draw('orange')
    
    '''
    18. Paint the next four tiles directly below it purple.
    '''
    line = Line(start_tile=tile, length=4, direction='down', include_start_tile=False)
    line.draw('purple')
    
    '''
    19. Move to the next column, and paint the tile at the bottom orange.
    '''
    tile = Tile(row=-1, column=10)
    tile.draw('orange')
    
    '''
    20. Paint the next four tiles directly above it purple.
    '''
    line = Line(start_tile=tile, length=4, direction='up', include_start_tile=False)
    line.draw('purple')
    
    '''
    21. Move to the next column, and paint the tile at the top green.
    '''
    tile = Tile(row=1, column=11)
    tile.draw('green')
    
    '''
    22. Paint the next four tiles directly below it blue.
    '''
    line = Line(start_tile=tile, length=4, direction='down', include_start_tile=False)
    line.draw('blue')
    
    '''
    23. Move to the next column, and paint the tile at the bottom orange.
    '''
    tile = Tile(row=-1, column=12)
    tile.draw('orange')
    
    '''
    24. Paint the next four tiles directly above it purple.
    '''
    line = Line(start_tile=tile, length=4, direction='up', include_start_tile=False)
    line.draw('purple')
    
    '''
    25. Move to the next column, and paint the tile at the top orange.
    '''
    tile = Tile(row=1, column=13)
    tile.draw('orange')
    
    '''
    26. Paint the next four tiles directly below it purple.
    '''
    line = Line(start_tile=tile, length=4, direction='down', include_start_tile=False)
    line.draw('purple')
    
    '''
    27. Move to the next column, and paint the tile at the bottom orange.
    '''
    tile = Tile(row=-1, column=14)
    tile.draw('orange')
    
    '''
    28. Paint the next four tiles directly above it purple.
    '''
    line = Line(start_tile=tile, length=4, direction='up', include_start_tile=False)
    line.draw('purple')
    
    '''
    29. Move to the next column, and paint the tile at the top orange.
    '''
    tile = Tile(row=1, column=15)
    tile.draw('orange')
    
    '''
    30. Paint the next four tiles directly below it purple.
    '''
    line = Line(start_tile=tile, length=4, direction='down', include_start_tile=False)
    line.draw('purple')
    
    '''
    31. Move to the next column, and paint the tile at the bottom green.
    '''
    tile = Tile(row=-1, column=16)
    tile.draw('green')
    
    '''
    32. Paint the next four tiles directly above it blue.
    '''
    line = Line(start_tile=tile, length=4, direction='up', include_start_tile=False)
    line.draw('blue')
    
    '''
    33. Move to the next column, and paint the tile at the top orange.
    '''
    tile = Tile(row=1, column=17)
    tile.draw('orange')
    
    '''
    34. Paint the next four tiles directly below it purple.
    '''
    line = Line(start_tile=tile, length=4, direction='down', include_start_tile=False)
    line.draw('purple')
    
    '''
    35. Move to the final column, and paint the tile at the bottom green.
    '''
    tile = Tile(row=-1, column=18)
    tile.draw('green')
    
    '''
    36. Paint the next four tiles directly above it blue.
    '''
    line = Line(start_tile=tile, length=4, direction='up', include_start_tile=False)
    line.draw('blue')
    
    g.plot(gold_boards=gold_boards, multiple=0)
