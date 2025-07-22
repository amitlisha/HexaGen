# Created by maor

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle

task_index = 537
gold_boards = list(read_task(task_index)['gold_boards'])

with Game() as g:
    
    # description:
    # task index: 537, image: P01C04T04, collection round: 0, category: conditions, group: train
    # agreement scores: [[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0]]
    
    '''
    1. Choose the color orange and fill in the topmost hexagon in column one from the
    left.
    '''
    tile = Tile(row=1, column=1)
    tile.draw('orange')
    
    '''
    2. Choose the color purple and fill in the four hexagons directly below the orange
    hexagon in column one.
    '''
    line = Line(start_tile=tile, include_start_tile=False, length=4, direction='down')
    line.draw('purple')
    
    '''
    3. Repeat this color scheme exactly for columns nine, thirteen, fifteen, and
    seventeen.
    '''
    shape = tile + line
    for c in[9,13,15,17]:
      shape.copy_paste(source=tile, destination=Tile(row=tile.row, column=c))
    
    '''
    4. Choose the color green and fill in the topmost hexagon in column three from the
    left.
    '''
    tile = Tile(row=1, column=3)
    tile.draw('green')
    
    '''
    5. Choose the color blue and fill in the four hexagons directly below the green
    hexagon.
    '''
    line = Line(start_tile=tile, include_start_tile=False, length=4, direction='down')
    line.draw('blue')
    
    '''
    6. Repeat the green/blue color scheme for columns five, seven, and eleven exactly
    as column three.
    '''
    shape = tile + line
    for c in[5,7,11]:
      shape.copy_paste(source=tile, destination=Tile(row=tile.row, column=c))
    
    '''
    7. Choose the color green and fill in the most bottom hexagon in column two from
    the left.
    '''
    tile = Tile(row=-1, column=2)
    tile.draw('green')
    
    '''
    8. Choose the color blue and fill in the four hexagons directly above the green
    hexagon in column two.
    '''
    line = Line(start_tile=tile, include_start_tile=False, length=4, direction='up')
    line.draw('blue')
    
    '''
    9. Repeat the green/blue color scheme in the same fashion as column two for columns
    six, eight, sixteen, and eighteen.
    '''
    shape = tile + line
    for c in[6,8,16,18]:
      shape.copy_paste(source=tile, destination=Tile(row=tile.row, column=c))
    
    '''
    10. Choose the color orange and fill in the most bottom hexagon in column four from
    the left.
    '''
    tile = Tile(row=-1, column=4)
    tile.draw('orange')
    
    '''
    11. choose the color purple and fill in the four hexagons directly above the orange
    hexagon in column four.
    '''
    line = Line(start_tile=tile, include_start_tile=False, length=4, direction='up')
    line.draw('purple')
    
    '''
    12. Repeat the orange/purple color scheme in the same fashion as column four for
    columns ten, twelve, and fourteen.
    '''
    shape = tile + line
    for c in[10, 12, 14]:
      shape.copy_paste(source=tile, destination=Tile(row=tile.row, column=c))
    
    g.plot(gold_boards=gold_boards, multiple=0)
