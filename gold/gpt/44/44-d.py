# Created by chat gpt

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle

task_index = 44
gold_boards = list(read_task(task_index)['gold_boards'])

with Game() as g:
    
    # make the first triangle
    for i in range(3):
        tile = Tile(i + 1, i)
        tile.draw("red")
    for i in range(2):
        tile = Tile(i + 3, i + 1)
        tile.draw("red")
    for i in range(1):
        tile = Tile(i + 4, i + 2)
        tile.draw("red")
    
    # record the first triangle
    g.record_step("triangle_1")
    
    # make the second triangle
    for i in range(3):
        tile = Tile(i + 1, i + 5)
        tile.draw("red")
    for i in range(2):
        tile = Tile(i + 3, i + 6)
        tile.draw("red")
    for i in range(1):
        tile = Tile(i + 4, i + 7)
        tile.draw("red")
    
    # record the second triangle
    g.record_step("triangle_2")
    
    # make the third triangle
    for i in range(3):
        tile = Tile(i + 1, i + 9)
        tile.draw("red")
    for i in range(2):
        tile = Tile(i + 3, i + 10)
        tile.draw("red")
    for i in range(1):
        tile = Tile(i + 4, i + 11)
        tile.draw("red")
    
    # record the third triangle
    g.record_step("triangle_3")
    
    # make the fourth triangle
    for i in range(3):
        tile = Tile(i + 1, i + 13)
        tile.draw("red")
    for i in range(2):
        tile = Tile(i + 3, i + 14)
        tile.draw("red")
    for i in range(1):
        tile = Tile(i + 4, i + 15)
        tile.draw("red")
    
    # record the fourth triangle
    g.record_step("triangle_4")
    
    # repeat the triangles with white row between them
    for i in range(4):
        g.get_record(f"triangle_{i+1}")
        g.record_step(f"triangle_{i+1}_white_row")
    
    # draw the resulting shape
    # g.get_record("start").draw("black")
    
    
    import os
    g.plot(gold_boards=None, multiple=0,file_name=os.path.basename(__file__).split('.')[0])
