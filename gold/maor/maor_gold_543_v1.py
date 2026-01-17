# Created by maor

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle

task_index = 543
gold_boards = list(read_task(task_index)['gold_boards'])

with Game() as g:
    
    # description:
    # task index: 543, image: P01C04T04, collection round: 0, category: conditions, group: train
    # agreement scores: [[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0]]
    
    '''
    1. The very top row starting from the left is orange, green, green, green, orange,
    green, orange, orange, orange.
    '''
    colors = ['orange','green','green','green','orange','green','orange','orange','orange']
    for color, column in zip(colors, range(1,19,2)):
      tile=Tile(row=1, column=column)
      tile.draw(color)
    
    '''
    2. The very bottom row is green, orange, green, green, orange, orange, orange,
    green, green, in that order.
    '''
    colors = ['green','orange','green','green','orange','orange','orange','green','green']
    for color, column in zip(colors, range(2,20,2)):
      tile=Tile(row=-1, column=column)
      tile.draw(color)
    
    '''
    3. At the top left you should have orange. The four tiles under it are purple.  Do
    this to all 5 orange tiles on the top row.
    '''
    top_row = Shape.get_board_perimeter().edge('up')
    orange_tiles = Shape.get_color(color='orange')
    for t in top_row * orange_tiles:
      line = Line(start_tile=t, include_start_tile=False, length=4, direction='down')
      line.draw('purple')
    
    '''
    4. On the top row, you should have 4 green tiles.  All of these tiles have 4 blue
    tiles under them.
    '''
    green_tiles = Shape.get_color(color='green')
    for t in top_row * green_tiles:
      line = Line(start_tile=t, include_start_tile=False, length=4, direction='down')
      line.draw('blue')
    
    '''
    5. At the bottom row, you should have 5 green tiles.  There are 4 blue tiles
    directly above each green tile.
    '''
    bottom_row = Shape.get_board_perimeter().edge('down')
    for t in bottom_row * green_tiles:
      line = Line(start_tile=t, include_start_tile=False, length=4, direction='up')
      line.draw('blue')
    
    '''
    6. At the bottom row, you should have 4 orange tiles.  There are 4 purple tiles
    directly above the orange tiles.
    '''
    for t in bottom_row * orange_tiles:
      line = Line(start_tile=t, include_start_tile=False, length=4, direction='up')
      line.draw('purple')
    
    g.plot(gold_boards=gold_boards, multiple=0)
