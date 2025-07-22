# Created by maor

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle

task_index = 537
gold_boards = list(read_task(task_index)['gold_boards'])

with Game() as g:
    
    # description:
    # task index: 537, image: P01C04T04, collection round: 0, category: conditions, group: train
    # agreement scores: [[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0]]
    
    '''
    1. Choose the color orange and fill in the topmost hexagon in column one from the
    left.
    '''
    g.record_step(step_name='1')
    tile = Tile(row=1, column=1)
    tile.draw('orange')
    
    '''
    2. Choose the color purple and fill in the four hexagons directly below the orange
    hexagon in column one.
    '''
    for r in range(4):
      tile=tile.neighbor('down')
      tile.draw('purple')
    g.record_step(step_name='1_end')
    
    '''
    3. Repeat this color scheme exactly for columns nine, thirteen, fifteen, and
    seventeen.
    '''
    shape = g.get_record(step_names=['1'])
    for c in [9,13,15,17]:
      shape.copy_paste(source=shape[0], destination=Tile(row=shape[0].row, column=c))
    
    '''
    4. Choose the color green and fill in the topmost hexagon in column three from the
    left.
    '''
    g.record_step(step_name='2')
    tile = Tile(row=1, column=3)
    tile.draw('green')
    
    '''
    5. Choose the color blue and fill in the four hexagons directly below the green
    hexagon.
    '''
    for r in range(4):
      tile=tile.neighbor('down')
      tile.draw('blue')
    g.record_step(step_name='2_end')
    
    '''
    6. Repeat the green/blue color scheme for columns five, seven, and eleven exactly
    as column three.
    '''
    shape = g.get_record(step_names=['2'])
    for c in [5,7,11]:
      shape.copy_paste(source=shape[0], destination=Tile(row=shape[0].row, column=c))
    
    '''
    7. Choose the color green and fill in the most bottom hexagon in column two from
    the left.
    '''
    g.record_step(step_name='3')
    tile = Tile(row=-1, column=2)
    tile.draw('green')
    
    '''
    8. Choose the color blue and fill in the four hexagons directly above the green
    hexagon in column two.
    '''
    for r in range(4):
      tile=tile.neighbor('up')
      tile.draw('blue')
    g.record_step(step_name='3_end')
    
    '''
    9. Repeat the green/blue color scheme in the same fashion as column two for columns
    six, eight, sixteen, and eighteen.
    '''
    shape = g.get_record(step_names=['3'])
    for c in [6,8,16,18]:
      shape.copy_paste(source=shape[0], destination=Tile(row=shape[0].row, column=c))
    
    '''
    10. Choose the color orange and fill in the most bottom hexagon in column four from
    the left.
    '''
    g.record_step(step_name='4')
    tile = Tile(row=-1, column=4)
    tile.draw('orange')
    
    '''
    11. choose the color purple and fill in the four hexagons directly above the orange
    hexagon in column four.
    '''
    for r in range(4):
      tile=tile.neighbor('up')
      tile.draw('purple')
    
    g.record_step(step_name='4_end')
    
    '''
    12. Repeat the orange/purple color scheme in the same fashion as column four for
    columns ten, twelve, and fourteen.
    '''
    shape = g.get_record(step_names=['4'])
    for c in[10, 12, 14]:
      shape.copy_paste(source=shape[0], destination=Tile(row=shape[0].row, column=c))
    
    g.plot(gold_boards=gold_boards, multiple=0)
