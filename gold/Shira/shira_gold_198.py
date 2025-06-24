from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle

task_index = 198
gold_boards = list(read_task(task_index)['gold_boards'])

with Game() as g:
    
    # procedure 198, image P01C07T03, collection round 1, category composed objects, group train
    
    '''
    1. Color topmost leftmost tile red, leave the three tiles diagonally down to the
    right of that tile, white, then alternate making a red diagonal line (connect
    the third tile from top leftmost down, coloring the 5 tiles going upward
    diagonally from there, red. Repeat again this diagonal, white and red pattern
    Three times.
    '''
    red_tile = Tile(1, 1)
    red_tile.draw('red')

    line = Line(start_tile = Tile(1, 3), direction = 'up_right')
    line.draw('red')

    for i in range(5, 10, 2):
        line = Line(start_tile = Tile(1, i), direction = 'up_right')
        line.draw('red')
    '''
    2. Color purple every other row, below the longest hexagonal red line made in step
    one. Start this alternating pattern with Bottommost, left most tile, skipping
    the second row from left, but then on every other row to the right, (third,
    fifth, seventh, etc.) color the vertical line(s) purple.
    '''
    from constants import WIDTH

    line = Line(start_tile=Tile(1, 9), direction='up_right')
    
    for tile in line.tiles:
        if tile.column in range(1, WIDTH, 2):
            Line(start_tile=tile, direction='down', include_start_tile=False).draw('purple')

    g.plot(gold_boards=gold_boards)
