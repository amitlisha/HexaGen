from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle

task_index = 200
gold_boards = list(read_task(task_index)['gold_boards'])

with Game() as g:
    
    # procedure 200, image P01C07T03, collection round 1, category composed objects, group train
    
    '''
    1. Fill the top-left most hex red.
    '''
    top_left_hex = Tile(1, 1)
    top_left_hex.draw('red')
    '''
    2. Fill a red line from the first column on the left, 3rd hex from the top, to the
    top hex of the 5th column from the left.
    '''
    red_line = Line(start_tile = Tile(3, 1), end_tile = Tile(1, 5))
    red_line.draw('red')
    '''
    3. Fill three more parallel lines in red, with a white line between each, from the
    left edge of the grid to the top of the grid.
    '''
    start_tile = red_line.start_tile
    for i in range(3):
      start_tile = start_tile.neighbor('down').neighbor('down')
      parallel_red_line = Line(start_tile = start_tile, direction = 'up_right')
      parallel_red_line.draw('red')
    '''
    4. Fill the bottom-most hex in the first column on the left with purple.
    '''
    bottom_most_hex = Tile(-1, 1)
    bottom_most_hex.draw('purple')
    '''
    5. In the thirst column from the left, fill the bottom two hexes with purple.
    '''
    Tile(-1, 3).draw('purple')
    Tile(-2, 3).draw('purple')
    '''
    6. Draw 7 more parallel purple lines, starting from the bottom of alternating
    columns (a while line between each) and stopping when you touch the red line.
    '''
    column = 5
    for i in range(7):
      Line(start_tile = Tile(-1, column), direction = 'up', end_tiles = Shape.get_color('red')).draw('purple')
      column += 2
    
    g.plot(gold_boards=gold_boards)
