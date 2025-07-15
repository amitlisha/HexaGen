from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle

task_index = 512
gold_boards = list(read_task(task_index)['gold_boards'])

with Game() as g:
    
    # description:
    # task index: 512, image: P01C04T20, collection round: 0, category: conditions, group: train
    # agreement scores: [[0, 1.0, 0], [1.0, 0.75, 0.75], [1.0, 0.83, 0.83], [0.46, 0.84, 0.43], [0.51, 0.85, 0.47], [0.55, 0.86, 0.52], [0.46, 0.91, 0.44], [0.47, 0.91, 0.45], [0.5, 0.91, 0.47], [0.51, 0.91, 0.49], [0.52, 0.91, 0.5], [0.53, 0.92, 0.51], [0.55, 0.92, 0.52], [0.46, 0.94, 0.45]]
    
    '''
    1. In the third column, colour in green tiles number two and three from the top.
    '''
    Tile(2, 3).draw('green')
    Tile(3, 3).draw('green')
    '''
    2. In the seventh column, colour in green tiles number two and three from the
    bottom.
    '''
    Tile(-2, 7).draw('green')
    Tile(-3, 7).draw('green')
    '''
    3. In the fifteenth column, colour in green tiles number two and three from the
    bottom.
    '''
    Tile(-2, 15).draw('green')
    Tile(-3, 15).draw('green')
    '''
    4. Colour in purple all the white tiles directly adjacent to green tiles.
    '''
    green_tiles = Shape.get_color('green')
    green_tiles.neighbors(criterion='white').draw('purple')
    '''
    5. In the fifteenth column, colour in blue tiles number two and three from the top.
    '''
    Tile(2, 15).draw('blue')
    Tile(3, 15).draw('blue')
    '''
    6. In the eleventh column, colour in blue tiles number two and three from the
    bottom.
    '''
    Tile(-2, 11).draw('blue')
    Tile(-3, 11).draw('blue')
    '''
    7. Colour in purple all the white tiles directly adjacent to blue tiles.
    '''
    blue_tiles = Shape.get_color('blue')
    blue_tiles.neighbors(criterion='white').draw('purple')
    '''
    8. In the third column, colour in green tile number three from the bottom.
    '''
    Tile(-2, 3).draw('green')
    Tile(-3, 3).draw('green')
    '''
    9. In the third column, colour in blue tile number two from the bottom.
    '''
    Tile(-2, 3).draw('blue')
    '''
    10. In the seventh column, colour in green tile number two from the top.
    '''
    Tile(2, 7).draw('green')
    '''
    11. In the seventh column, colour in blue tile number 3 from the top.
    '''
    Tile(3, 7).draw('blue')
    '''
    12. In the eleventh column, colour in blue tile number two from the top.
    '''
    Tile(2, 11).draw('blue')
    '''
    13. In the eleventh column, colour in green tile number 3 from the top.
    '''
    Tile(3, 11).draw('green')
    '''
    14. Colour orange the tiles adjacent to the blue/green duos.
    '''
    for tile in Shape.get_entire_board():
      if tile.color in ['green', 'blue']:
        for tile2 in tile.neighbors():
          if tile2.color in ['green', 'blue'] and tile2.color != tile.color:
            (tile + tile2).neighbors('white').draw('orange')
    
    g.plot(gold_boards=gold_boards)
