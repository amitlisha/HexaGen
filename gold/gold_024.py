import sys
sys.path.append('../src')
sys.path.append('../utils')

from get_procedure import get_procedure
from hexagons_classes import HexagonsGame, Tile, Shape, Line, Circle, Triangle
import plot_board as pb

drpr = 24
gold_bs, _ = get_procedure(drpr, plot = False)
gold_b = gold_bs[-1]

HexagonsGame.start()

# procedure 24, image P01C02T05, collection round 1, category bounded iteration, group train

'''
1. using the second tile down in the second vertical row (from left) leave that
tile white but color all tiles around it purple. This forms a purple ring.
'''
ring = Tile(2, 2).neighbors()
ring.draw('purple')
'''
2. leaving a blank row next over to the right, repeat the pattern, making a ring of
6 purple tiles, continue this pattern until you have a total of 4 purple rings
spaced, leaving a row of vertical tiles between them.
'''
four_rings = ring.grid('right', 1, num_copies = 3)
four_rings.draw('purple')

drawn_b = HexagonsGame.board_state

diff = list(map(lambda x, y: 0 if x == y else 1, gold_b, drawn_b))

pb.plot_boards([list(gold_b), drawn_b, diff])
