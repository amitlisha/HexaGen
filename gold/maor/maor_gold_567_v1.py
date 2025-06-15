# Created by maor

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle

task_index = 567
gold_boards = list(read_task(task_index)['gold_boards'])

with Game() as g:
    
    # description:
    # task index: 567, image: P01C04T20, collection round: 0, category: conditions, group: train
    # agreement scores: [[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0]]
    
    '''
    1. You are going to make a drawing with eight flower-like shapes arranged in rows
    of four. Start by coloring the top three hexagons in the second column purple.
    '''
    line1 = Line(start_tile=Tile(column=2, row=1), direction='down', length=3)
    line1.draw('purple')
    
    '''
    2. Next, color the top three hexagons in the fourth column purple.
    '''
    line2 = Line(start_tile=Tile(column=4, row=1), direction='down', length=3)
    line2.draw('purple')
    
    '''
    3. Now, color the first and fourth hexagon in the third column purple.
    '''
    tile3= Tile(column=3, row=1)
    tile3.draw('purple')
    tile4= Tile(column=3, row=4)
    tile4.draw('purple')
    
    '''
    4. Now, you will see an oval with two white hexagons in the middle. Color both
    hexagons in the middle green.
    '''
    oval1 = line1+line2+tile3+tile4
    oval1.get(criterion='inside').draw('green')
    
    '''
    5. Next, make a similar flower shape directly to the right of this one using
    columns six, seven, and eight. There will be one empty column between the
    flowers. Make the outside of the flower orange, make the top hexagon in the
    center green, and make the bottom hexagon in the center blue.
    '''
    oval2 = oval1.copy_paste(shift_direction='right', spacing=1)
    oval2.draw('orange')
    oval2.get(criterion='inside').edge(direction='top').draw('green')
    oval2.get(criterion='inside').edge(direction='down').draw('blue')
    
    '''
    6. Make another flower to the right of the last one using columns ten through 12.
    This flower looks exactly like the last one with orange on the outside but the
    center colors are switched, with blue on the top and green on the bottom.
    '''
    oval3 = oval2.copy_paste(shift_direction='right', spacing=1)
    oval3.draw('orange')
    oval3.get(criterion='inside').edge(direction='top').draw('blue')
    oval3.get(criterion='inside').edge(direction='down').draw('green')
    
    '''
    7. Make one more flower to the right leaving an empty column in between. This
    flower is purple on the outside and both inside hexagons are blue.
    '''
    oval4 = oval3.copy_paste(shift_direction='right', spacing=1)
    oval4.draw('purple')
    oval4.get(criterion='inside').draw('blue')
    
    '''
    8. Now, you are going to make four more flowers directly below the ones you already
    made using the same columns as above, but leave two blank hexagons between the
    lowest petal on the top flower and the highest petal on the bottom flower. Make
    the first flower exactly like the second one from above, with orange, green on
    the top center, and blue on the bottom center.
    '''
    oval5=oval2.copy_paste(shift_direction='down', spacing=2, reference_shape=oval1)
    oval5.draw('orange')
    oval5.get(criterion='inside').edge(direction='top').draw('green')
    oval5.get(criterion='inside').edge(direction='down').draw('blue')
    
    '''
    9. Draw the second and fourth flowers exactly like the first flower from above,
    with purple on the outside and green on the inside.
    '''
    oval6=oval1.copy_paste(shift_direction='down', spacing=2, reference_shape=oval2)
    oval6.draw('purple')
    oval6.get(criterion='inside').draw('green')
    
    oval7=oval1.copy_paste(shift_direction='down', spacing=2, reference_shape=oval4)
    oval7.draw('purple')
    oval7.get(criterion='inside').draw('green')
    
    '''
    10. Draw the third flower exactly like the fourth one from above with purple on the
    outside and blue on the inside.
    '''
    oval8=oval4.copy_paste(shift_direction='down', spacing=2, reference_shape=oval3)
    oval8.draw('purple')
    oval8.get(criterion='inside').draw('blue')
    
    g.plot(gold_boards=gold_boards, multiple=0)
