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
    tile1 = Tile(1, 1)
    tile1.draw('red')
    '''
    2. Again with red and make an upward diagonal line beginning with the third tile
    down on the far left and ending with the topmost tile that is third from the
    left.
    '''
    line1 = Line(start_tile=Tile(1, 3), end_tile=Tile(5, 1))
    line1.draw('red')
    '''
    3. Continuing diagonally, skip a diagonal row then make the next row down red from
    the leftmost to the topmost tile. Then continue for two more rows.
    '''
    line2 = line1.parallel(shift_direction='down', spacing=1)
    line2.draw('red')
    line = line2
    for i in range(2):
      line = line.parallel(shift_direction='down', spacing=1)
      line.draw('red')
    '''
    4. Using purple from now through the last column to be colored purple, color every
    other column beginning with the bottom leftmost tile. Every other column needs
    to be colored in starting just below the red tile in said column.
    '''
    column = 1
    red_tiles = Shape.get_color('red')
    while column <= g.width:
      red_tiles_in_column = Shape.get_column(column=column) * red_tiles
      start_tile = red_tiles_in_column.get('bottom').neighbor('down')
      Line(start_tile=start_tile, direction='down').draw('purple')
      column += 2
    
    g.plot(gold_boards=gold_boards)
