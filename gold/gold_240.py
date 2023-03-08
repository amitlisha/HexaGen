import sys
sys.path.append('../src')
sys.path.append('../utils')

from reading_tasks import read_task
from hexagons_classes import HexagonsGame, Tile, Shape, Line, Circle, Triangle
import plot_board as pb

task_index = 240
gold_b = read_task(task_index)['gold_boards'][-1]

HexagonsGame.start()

# procedure 240, image P01C05T10, collection round 1, category recursion, group train

'''
1. In the 9th column from the left, the 5th tile from the top will be blue. This
will be our center.
'''
center_tile = Tile(9, 5)
center_tile.draw('blue')
'''
2. There are 6 tiles surrounding (and touching) our center, color them red.
'''
red_tiles = center_tile.neighbors()
red_tiles.draw('red')
'''
3. There are 12 tiles touching and surrounding these red tiles. Color them yellow.
'''
yellow_tiles = red_tiles.neighbors('outside')
yellow_tiles.draw('yellow')
'''
4. There are 18 tiles surrounding these yellow tiles. Color them green.
'''
green_tiles = yellow_tiles.neighbors('outside')
green_tiles.draw('green')
'''
5. There are 24 tiles surrounding these green tiles. Color them orange and we are
done!
'''
orange_tiles = green_tiles.neighbors('outside')
orange_tiles.draw('orange')

drawn_b = HexagonsGame.board_state

diff = list(map(lambda x, y: 0 if x == y else 1, gold_b, drawn_b))

pb.plot_boards([list(gold_b), drawn_b, diff], titles = ['gold', 'code generated', 'difference'])
