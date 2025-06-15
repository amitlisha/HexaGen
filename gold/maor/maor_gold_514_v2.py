# Created by maor

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle

task_index = 514
gold_boards = list(read_task(task_index)['gold_boards'])

with Game() as g:
    
    # description:
    # task index: 514, image: P01C07T03, collection round: 0, category: composed objects, group: train
    # agreement scores: [[1.0, 1.0, 1.0], [1.0, 0.91, 0.91], [0.77, 0.99, 0.75], [0.47, 0.99, 0.46]]
    
    '''
    1. With red, start at the top left tile and color it in.
    '''
    tile = Tile(column=1, row=1)
    tile.draw('red')
    
    '''
    2. Again with red and make an upward diagonal line beginning with the third tile
    down on the far left and ending with the topmost tile that is third from the
    left.
    '''
    line = Line(start_tile=Tile(column=1, row=3), direction='up_right')
    line.draw('red')
    
    '''
    3. Continuing diagonally, skip a diagonal row then make the next row down red from
    the leftmost to the topmost tile. Then continue for two more rows.
    '''
    for r in range(5,10,2):
      line = Line(start_tile=Tile(column=1, row=r), direction='up_right')
      line.draw('red')
    
    '''
    4. Using purple from now through the last column to be colored purple, color every
    other column beginning with the bottom leftmost tile. Every other column needs
    to be colored in starting just below the red tile in said column.
    '''
    for c in range(1, 19, 2):
      start_tile = (Shape.get_column(c) * Shape.get_color('red')).extreme(direction='down').neighbor('down')
      purple_line = Line(start_tile=start_tile, direction='down')
      purple_line.draw('purple')
    
    g.plot(gold_boards=gold_boards, multiple=0)
