import sys
sys.path.append('../src')
sys.path.append('../utils')

from get_procedure import get_procedure
from hexagons_classes import HexagonsGame, Tile, Shape, Line, Circle, Triangle
import plot_board as pb

drpr = 199
gold_bs, _ = get_procedure(drpr, plot = False)
gold_b = gold_bs[-1]

HexagonsGame.start()

# procedure 199, image P01C07T03, collection round 1, category composed objects, group train

'''
1. Color the top left-most tile RED.
'''
red_tile = Tile(1, 1)
red_tile.draw('red')
'''
2. Note the three tiles immediately below/to the right of the tile you just filled.
Leave these unfilled, but color all tiles below/to the right of these RED.
'''
white_tiles = Shape([red.tile.neighbor('down'), red.tile.neighbor('down_right')])
draw
'''
3. Repeat step 2 three more times. You should have five solid red diagonal stripes
(including the corner tile) in the top left half of the grid.
'''

'''
4. In the bottom row of tiles, starting from the leftmost edge, color every other
tile PURPLE.
'''

'''
5. Extend the purple tiles up into solid purple columns, up to where they meet the
largest red stripe.
'''

drawn_b = HexagonsGame.board_state

diff = list(map(lambda x, y: 0 if x == y else 1, gold_b, drawn_b))

pb.plot_boards([list(gold_b), drawn_b, diff])
