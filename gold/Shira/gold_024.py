from utils.reading_tasks import read_task
from src.hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle

task_index = 24
gold_board = list(read_task(task_index)['gold_boards'][-1])

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

HexagonsGame.plot(gold_board=gold_board)
