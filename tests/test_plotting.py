from utils.reading_tasks import read_task
from hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle

task_index = 24
gold_boards = list(read_task(task_index)['gold_boards'])

HexagonsGame.start()

# procedure 24, image P01C02T05, collection round 1, category bounded iteration, group train

'''
1. using the second tile down in the second vertical row (from left) leave that
tile white but color all tiles around it purple. This forms a purple ring.
'''
HexagonsGame.record_step('step 1')
ring = Tile(2, 2).neighbors()
ring.draw('purple')
'''
2. leaving a blank row next over to the right, repeat the pattern, making a ring of
6 purple tiles, continue this pattern until you have a total of 4 purple rings
spaced, leaving a row of vertical tiles between them.
'''
HexagonsGame.record_step('step 2')
four_rings = ring.grid('right', 1, num_copies = 3)
four_rings.draw('red')

HexagonsGame.plot(gold_boards=gold_boards)
# HexagonsGame.plot(gold_boards=gold_boards, multiple=True)

