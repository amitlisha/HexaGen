# Created by maor

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle

task_index = 85
gold_boards = list(read_task(task_index)['gold_boards'])

with Game() as g:
    
    # description:
    # task index: 85, image: P01C02T29, collection round: 1, category: bounded iteration, group: train
    # agreement scores: [[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [0.83, 1.0, 0.83], [0.56, 1.0, 0.56], [0.47, 0.91, 0.43], [0.47, 0.83, 0.39]]
    
    '''
    1. In the 1st column from the left, color the bottom-most tile GREEN. Color the
    tile down and to the right of this tile GREEN as well.
    '''
    tile1 = Tile(-1, 1)
    tile1.draw('green')
    
    tile2 = tile1.neighbor('down_right')
    tile2.draw('green')
    
    shape1 = Shape([tile1, tile2])
    
    '''
    2. In the 4th column from the left, color the bottom-most tile YELLOW. Color the
    tile up and to the right of this tile YELLOW as well.
    '''
    tile3 = Tile(-1, 4)
    tile3.draw('yellow')
    
    tile4= tile3.neighbor('up_right')
    tile4.draw('yellow')
    
    shape2 = Shape([tile3, tile4])
    
    '''
    3. In the 7th column from the left, color the two bottom-most tiles GREEN.
    '''
    line1 = Line(start_tile=Tile(-1, 7), direction='up', length=2)
    line1.draw('green')
    
    '''
    4. Take note of the three groups of shapes you've just drawn. This will be our base
    pattern.
    '''
    
    '''
    5. Copy and translate the base pattern UP by three tiles, but invert the colors;
    the shapes which were green in the old pattern should be yellow in the new
    pattern, and vice versa. The 4th and 5th tiles from the bottom in the 7th column
    from the left should be filled in.
    '''
    shape3 = shape1.copy_paste(shift_direction='up', spacing=2, reference_shape=shape1)
    shape3.recolor({'green': 'yellow'})
    shape4 = shape2.copy_paste(shift_direction='up', spacing=2, reference_shape=shape2)
    shape4.recolor({'yellow': 'green'})
    line2 = line1.copy_paste(shift_direction='up', spacing=1, reference_shape=line1)
    line2.recolor({'green': 'yellow'})
    
    '''
    6. Copy and translate this new pattern UP by another three tiles, inverting the
    color palette again (i.e., should match the first base pattern you drew). The
    3rd and 4th tiles from the TOP of the 7th column from the left should be filled
    in.
    '''
    shape5 = shape3.copy_paste(shift_direction='up', spacing=2, reference_shape=shape3)
    shape5.recolor({'yellow': 'green'})
    shape6 = shape4.copy_paste(shift_direction='up', spacing=2, reference_shape=shape4)
    shape6.recolor({'green': 'yellow'})
    line3 = line2.copy_paste(shift_direction='up', spacing=1, reference_shape=line2)
    line3.recolor({'yellow': 'green'})
    
    '''
    7. Reflect the diagonal shapes in the first 5 columns across horizontally, using
    the 7th column as the line of symmetry. Note that color patterns should be
    reflected symmetrically as well.
    '''
    shape1.reflect(column=7)
    shape2.reflect(column=7)
    shape3.reflect(column=7)
    shape4.reflect(column=7)
    shape5.reflect(column=7)
    shape6.reflect(column=7)
    
    '''
    8. Copy and translate the vertical groupings of shapes (the 7th column from the
    left) to the third column from the RIGHT, inverting the colors. These should
    meet the bottom edge of the grid.
    '''
    line4 = Shape.get_column(column=7).copy_paste(shift_direction='right', spacing=8)
    line4.recolor({'green': 'yellow', 'yellow': 'green', 'white': 'white'})
    
    g.plot(gold_boards=gold_boards, multiple=0)
