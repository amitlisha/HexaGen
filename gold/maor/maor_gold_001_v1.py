# Created by by maor

from utils.reading_tasks import read_task
from src.hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle

task_index = 1
gold_boards = list(read_task(task_index)['gold_boards'])

HexagonsGame.start()

# description:
# task index: 1, image: P01C01T05, collection round: 1, category: simple, group: train
# agreement scores: [[1.0, 1.0, 1.0], [1.0, 0.67, 0.67], [1.0, 0.7, 0.7]]

'''
1. On the eighth row from the left, vertically, and the fifth tile down on that row, 
leave it blank but fill in all tiles that touch that with red.
'''
tile1 = Tile(8, 5)
neighbors = tile1.neighbors()
neighbors.draw('red')

'''
2.  Above the rightmost two red tiles, add another red tile touching the top of the top rightmost tile. 
Add below those three rightmost tiles one additional red tile, making a row of 4 red tiles.
'''
tile2 = tile1.neighbors(criterion='up_right').neighbors(criterion='up')
tile2.draw('red')

tile3 = tile1.neighbors(criterion='down_right').neighbors(criterion='down')
tile3.draw('red')

'''
3.  Color in the tile, immediate to the left of the leftmost two tiles, with red, 
this is the fifth tile from top and sixth from the left.
'''
down_tile = Tile(6, 5)
down_tile.draw('red')

HexagonsGame.plot(gold_boards=gold_boards, multiple=0)