# Created by chat gpt

from utils.reading_tasks import read_task
from src.hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle

task_index = 44
gold_boards = list(read_task(task_index)['gold_boards'])

HexagonsGame.start()

# make the first triangle
for i in range(3):
    tile = Tile(i, i + 1)
    tile.draw("red")
for i in range(2):
    tile = Tile(i + 1, i + 3)
    tile.draw("red")
for i in range(1):
    tile = Tile(i + 2, i + 4)
    tile.draw("red")

# record the first triangle
HexagonsGame.record_step("triangle_1")

# make the second triangle
for i in range(3):
    tile = Tile(i + 5, i + 1)
    tile.draw("red")
for i in range(2):
    tile = Tile(i + 6, i + 3)
    tile.draw("red")
for i in range(1):
    tile = Tile(i + 7, i + 4)
    tile.draw("red")

# record the second triangle
HexagonsGame.record_step("triangle_2")

# make the third triangle
for i in range(3):
    tile = Tile(i + 9, i + 1)
    tile.draw("red")
for i in range(2):
    tile = Tile(i + 10, i + 3)
    tile.draw("red")
for i in range(1):
    tile = Tile(i + 11, i + 4)
    tile.draw("red")

# record the third triangle
HexagonsGame.record_step("triangle_3")

# make the fourth triangle
for i in range(3):
    tile = Tile(i + 13, i + 1)
    tile.draw("red")
for i in range(2):
    tile = Tile(i + 14, i + 3)
    tile.draw("red")
for i in range(1):
    tile = Tile(i + 15, i + 4)
    tile.draw("red")

# record the fourth triangle
HexagonsGame.record_step("triangle_4")

# repeat the triangles with white row between them
for i in range(4):
    HexagonsGame.get_record(f"triangle_{i+1}")
    HexagonsGame.record_step(f"triangle_{i+1}_white_row")

# draw the resulting shape
# HexagonsGame.get_record("start").draw("black")


import os
HexagonsGame.plot(gold_boards=None, multiple=0,file_name=os.path.basename(__file__).split('.')[0])
