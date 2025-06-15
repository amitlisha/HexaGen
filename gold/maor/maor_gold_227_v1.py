# Created by maor

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle

task_index = 227
gold_boards = list(read_task(task_index)['gold_boards'])

with Game() as g:
    
    # description:
    # task index: 227, image: P01C08T06, collection round: 1, category: other, group: train
    # agreement scores: [[1.0, 1.0, 1.0], [0.98, 0.83, 0.84], [0.99, 0.92, 0.94], [0.9, 0.83, 0.76], [1.0, 0.76, 0.76]]
    
    '''
    1. Paint a diagonal row of green hexagons starting with the second hexagon in
    column one and ending with the last hexagon in the column furthest to the right.
    '''
    line = Line(start_tile=Tile(column=1,row=2), end_tile=Tile(column=-1,row=-1))
    line.draw('green')
    
    '''
    2. Starting in column two, paint the third hexagon green, the fourth and fifth
    hexagon in column four green, and continue the pattern moving to the right,
    skipping a row in between each, with four being painted green in the eighth and
    tenth columns and finishing the columns in the subsequent columns moving to the
    right.
    '''
    tile = Tile(column=2, row=3)
    tile.draw('green')
    
    for r in [4,5]:
      tile = Tile(column=4, row=r)
      tile.draw('green')
    
    for r in [5,6,7]:
      tile = Tile(column=6, row=r)
      tile.draw('green')
    
    for r in [6,7,8,9]:
      tile = Tile(column=8, row=r)
      tile.draw('green')
    
    for r in [7,8,9,10]:
      tile = Tile(column=10, row=r)
      tile.draw('green')
    
    
    for r in [8,9,10]:
      tile = Tile(column=12, row=r)
      tile.draw('green')
    
    for r in [9,10]:
      tile = Tile(column=14, row=r)
      tile.draw('green')
    
    tile = Tile(column=16, row=10)
    tile.draw('green')
    
    '''
    3. Paint the second hexagon in the third column green, the third in column five,
    and the second hexagon in column six all green.
    '''
    tile = Tile(column=3, row=2)
    tile.draw('green')
    
    tile = Tile(column=5, row=3)
    tile.draw('green')
    
    tile = Tile(column=6, row=2)
    tile.draw('green')
    
    '''
    4. Paint the third hexagon in column nine, the third hexagon in column twelve, and
    the fourth hexagon in column fourteen, the sixth hexagon in column fifteen, the
    seventh in column sixteen, and the ninth in column seventeen.
    '''
    tiles = []
    
    tile = Tile(column=9, row=3)
    tile.draw('green')
    tiles.append(tile)
    
    tile = Tile(column=12, row=3)
    tile.draw('green')
    tiles.append(tile)
    
    tile = Tile(column=14, row=4)
    tile.draw('green')
    tiles.append(tile)
    
    tile = Tile(column=15, row=6)
    tile.draw('green')
    tiles.append(tile)
    
    tile = Tile(column=16, row=7)
    tile.draw('green')
    tiles.append(tile)
    
    tile = Tile(column=17, row=9)
    tile.draw('green')
    tiles.append(tile)
    
    '''
    5. Paint the hexagons in between the center diagonal line and the single green
    hexagons to make diagonal lines.
    '''
    for tile in tiles:
      end_tile = Line(start_tile=tile, direction='down_left') * line
      Line(start_tile=tile, end_tile=end_tile).draw('green')
    
    g.plot(gold_boards=gold_boards, multiple=0)
