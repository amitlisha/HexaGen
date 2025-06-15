# Created by chat gpt

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle

task_index = 43
gold_boards = list(read_task(task_index)['gold_boards'])

with Game() as g:
    
    # Paint the cell at the 1st column on the left and 2nd row from top with red
    tile = Tile(1, 2)
    tile.draw('red')
    g.record_step('step1')
    
    # Paint the top 2 cells of the 2nd column from left with red
    tile = Tile(2, 1)
    tile.draw('red')
    tile.neighbor('down').draw('red')
    g.record_step('step2')
    
    # Paint the top 3 rows of the 3rd column from the left with red
    tile = Tile(3, 1)
    tile.draw('red')
    for i in range(2, 5):
      tile.neighbor('down').draw('red')
      tile = tile.neighbor('down')
    g.record_step('step3')
    
    # Repeat the triangle pattern 3 more times to the right of the 1st triangle,
    # making sure to leave one empty column between each triangle
    for i in range(1, 4):
      # First triangle
      tile = Tile(6 + i * 4, 2)
      tile.draw('red')
      tile.neighbor('down_right').draw('red')
      tile.neighbor('down_left').draw('red')
      tile.neighbor('down_right').neighbor('down').draw('red')
      tile.neighbor('down_left').neighbor('down').draw('red')
      g.record_step(f'step4_{i}_1')
    
      # Second triangle
      tile = Tile(8 + i * 4, 1)
      tile.draw('red')
      tile.neighbor('down_right').draw('red')
      tile.neighbor('down_left').draw('red')
      tile.neighbor('down_right').neighbor('down').draw('red')
      tile.neighbor('down_left').neighbor('down').draw('red')
      g.record_step(f'step4_{i}_2')
    
      # Third triangle
      tile = Tile(10 + i * 4, 1)
      tile.draw('red')
      tile.neighbor('down_right').draw('red')
      tile.neighbor('down_left').draw('red')
      tile.neighbor('down_right').neighbor('down').draw('red')
      tile.neighbor('down_left').neighbor('down').draw('red')
      g.record_step(f'step4_{i}_3')
    
    import os
    g.plot(gold_boards=None, multiple=0,file_name=os.path.basename(__file__).split('.')[0])
