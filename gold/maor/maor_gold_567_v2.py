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
    g.record_step(step_name='flower')
    
    for i in range(1,4):
      tile = Tile(column=2, row=i)
      tile.draw('purple')
    
    '''
    2. Next, color the top three hexagons in the fourth column purple.
    '''
    for i in range(1,4):
      tile = Tile(column=4, row=i)
      tile.draw('purple')
    
    
    '''
    3. Now, color the first and fourth hexagon in the third column purple.
    '''
    tile= Tile(column=3, row=1)
    tile.draw('purple')
    
    tile= Tile(column=3, row=4)
    tile.draw('purple')
    
    g.record_step(step_name='flower_end')
    '''
    4. Now, you will see an oval with two white hexagons in the middle. Color both
    hexagons in the middle green.
    '''
    oval = Shape.get_color('purple')
    oval.get(criterion='inside').draw('green')
    
    '''
    5. Next, make a similar flower shape directly to the right of this one using
    columns six, seven, and eight. There will be one empty column between the
    flowers. Make the outside of the flower orange, make the top hexagon in the
    center green, and make the bottom hexagon in the center blue.
    '''
    flower_shape = g.get_record(step_names=['flower'])
    flower1 = flower_shape.copy_paste(shift_direction='right', spacing=1)
    flower1.recolor({'purple': 'orange'})
    flower1.get(criterion='inside').edge(direction='top').draw('green')
    flower1.get(criterion='inside').edge(direction='down').draw('blue')
    
    '''
    6. Make another flower to the right of the last one using columns ten through 12.
    This flower looks exactly like the last one with orange on the outside but the
    center colors are switched, with blue on the top and green on the bottom.
    '''
    flower2 = flower_shape.copy_paste(shift_direction='right', reference_shape=flower1, spacing=1)
    flower2.draw('orange')
    flower2.get(criterion='inside').edge(direction='top').draw('blue')
    flower2.get(criterion='inside').edge(direction='down').draw('green')
    
    '''
    7. Make one more flower to the right leaving an empty column in between. This
    flower is purple on the outside and both inside hexagons are blue.
    '''
    flower3 = flower_shape.copy_paste(shift_direction='right', reference_shape=flower2, spacing=1)
    flower3.draw('purple')
    flower3.get(criterion='inside').edge(direction='top').draw('blue')
    flower3.get(criterion='inside').edge(direction='down').draw('blue')
    
    '''
    8. Now, you are going to make four more flowers directly below the ones you already
    made using the same columns as above, but leave two blank hexagons between the
    lowest petal on the top flower and the highest petal on the bottom flower. Make
    the first flower exactly like the second one from above, with orange, green on
    the top center, and blue on the bottom center.
    '''
    flower4=flower_shape.copy_paste(shift_direction='down', reference_shape=flower_shape, spacing=2)
    flower4.draw('orange')
    flower4.get(criterion='inside').edge(direction='top').draw('green')
    flower4.get(criterion='inside').edge(direction='down').draw('blue')
    
    '''
    9. Draw the second and fourth flowers exactly like the first flower from above,
    with purple on the outside and green on the inside.
    '''
    flower5=flower_shape.copy_paste(shift_direction='right', spacing=1, reference_shape=flower4)
    flower5.draw('purple')
    flower5.get(criterion='inside').draw('green')
    
    flower6=flower_shape.copy_paste(shift_direction='right', spacing=9, reference_shape=flower4)
    flower6.draw('purple')
    flower6.get(criterion='inside').draw('green')
    
    '''
    10. Draw the third flower exactly like the fourth one from above with purple on the
    outside and blue on the inside.
    '''
    flower7=flower_shape.copy_paste(shift_direction='right', spacing=1, reference_shape=flower5)
    flower7.draw('purple')
    flower7.get(criterion='inside').draw('blue')
    
    g.plot(gold_boards=gold_boards, multiple=0)
