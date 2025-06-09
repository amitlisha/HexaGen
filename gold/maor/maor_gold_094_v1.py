# Created by maor

from utils.reading_tasks import read_task
from hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle

task_index = 94
gold_boards = list(read_task(task_index)['gold_boards'])

HexagonsGame.start()

# description:
# task index: 94, image: P01C03T03, collection round: 1, category: conditional iteration, group: train
# agreement scores: [[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0]]

'''
1. Use purple to fill the top 3 spots of the 12th column.
'''

'''
2. make the 4th spot blue.
'''

'''
3. Create a purple diagonal line from the right side of the blue spot to the 7th
spot of the 18th column and from the left side to the last spot on the 1st
column.
'''

'''
4. Use yellow to fill the 3rd spot on the 5th column.
'''

'''
5. Make orange diagonal line from the yellow spot to the first spots on the 1st and
9th column.
'''

'''
6. Fill in the 4 spots below the yellow spot with orange.
'''

'''
7. make the next spot black
'''

'''
8. fill in the last two spots on that column with orange.
'''

HexagonsGame.plot(gold_boards=gold_boards, multiple=0)
