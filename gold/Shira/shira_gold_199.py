from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle

task_index = 199
gold_boards = list(read_task(task_index)['gold_boards'])

with Game() as g:
    
    # procedure 199, image P01C07T03, collection round 1, category composed objects, group train
    
    '''
    1. Color the top left-most tile RED.
    '''
    red_tile = Tile(1, 1)
    red_tile.draw('red')
    '''
    2. Note the three tiles immediately below/to the right of the tile you just filled.
    Leave these unfilled, but color all tiles below/to the right of these RED.
    '''
    line1 = Line(start_tile=Tile(3, 1), direction='up_right').draw('red')
    '''
    3. Repeat step 2 three more times. You should have five solid red diagonal stripes
    (including the corner tile) in the top left half of the grid.
    '''
    line2 = Line(start_tile=Tile(5, 1), direction='up_right').draw('red')
    line3 = Line(start_tile=Tile(7, 1), direction='up_right').draw('red')
    line4 = Line(start_tile=Tile(9, 1), direction='up_right').draw('red')
    '''
    4. In the bottom row of tiles, starting from the leftmost edge, color every other
    tile PURPLE.
    '''
    from constants import WIDTH

    for i in range(1, WIDTH, 2):
        Tile(-1, i).draw('purple')
    '''
    5. Extend the purple tiles up into solid purple columns, up to where they meet the
    largest red stripe.
    '''
    for i in range(1, WIDTH, 2):
        Line(start_tile=Tile(-1, i), direction='up', end_tiles=line4).draw('purple')
    g.plot(gold_boards=gold_boards)
