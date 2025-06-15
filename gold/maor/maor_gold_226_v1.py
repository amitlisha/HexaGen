# Created by maor

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle

task_index = 226
gold_boards = list(read_task(task_index)['gold_boards'])

with Game() as g:
    
    # description:
    # task index: 226, image: P01C08T06, collection round: 1, category: other, group: train
    # agreement scores: [[1.0, 1.0, 1.0], [1.0, 0.82, 0.82], [0.84, 0.68, 0.77]]
    
    '''
    1. Colour the hexagon in coloum one row two green. create a diagonal green line
    from this hexagon to column 18 row 10.
    '''
    tile = Tile(column=1,row=2)
    tile.draw('green')
    line = Line(start_tile=tile, end_tile=Tile(column=18,row=10))
    line.draw('green')
    
    '''
    2. create eight green lines radiating out of this diagonal line with one blank
    hexagon between each line. beginning with column three row two. add one green
    hexagon extending out to each line until you have four hexagons extended. the
    next raditating line should also have four hexagons extended. the reduce the
    number of hexagons extended by one. ending with one hexagon extended in row
    column 17 row nine.
    '''
    tile = Tile(column=3,row=2)
    
    for length in range(1,5,1):
      line = Line(start_tile=tile, direction='up_right', length=length)
      line.draw('green')
      tile = tile.neighbor('down_right').neighbor('down_right')
    
    for length in range(4,0,-1):
      line = Line(start_tile=tile, direction='up_right', length=length)
      line.draw('green')
      tile = tile.neighbor('down_right').neighbor('down_right')
    
    '''
    3. repeat this pattern of radiating lines on the other side of the orignal diagonal
    line extending the radiating line downwards. beginnning in column two row three
    and ending in column 16 row ten.
    '''
    tile = Tile(column=2,row=3)
    
    for length in range(1,5,1):
      line = Line(start_tile=tile, direction='down', length=length)
      line.draw('green')
      tile = tile.neighbor('down_right').neighbor('down_right')
    
    for length in range(4,0,-1):
      line = Line(start_tile=tile, direction='down', length=length)
      line.draw('green')
      tile = tile.neighbor('down_right').neighbor('down_right')
    
    g.plot(gold_boards=gold_boards, multiple=0)
