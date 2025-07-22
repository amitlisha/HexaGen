# Created by maor

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle

task_index = 160
gold_boards = list(read_task(task_index)['gold_boards'])

with Game() as g:
    
    # description:
    # task index: 160, image: P01C04T02, collection round: 1, category: conditions, group: train
    # agreement scores: [[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0]]
    
    '''
    1. Leaving the center tile blank, draw a blue flower, using six tiles in the lower
    left corner.
    '''
    flower1 = Circle(center_tile=Tile(-2, 2))
    flower1.draw('blue')
    
    '''
    2. Directly above the blue flower, draw a purple flower in the same way, and an
    orange flower above that one, so that the three flowers touch forming a stack.
    '''
    flower2 = Circle(center_tile=Tile(-5, 2))
    flower2.draw('purple')
    
    flower3 = Circle(center_tile=Tile(-8, 2))
    flower3.draw('orange')
    
    '''
    3. Draw a similar stack of flowers with their blank centers in the sixth column
    from the left, starting with purple at the bottom, then orange, then blue, going
    up, so that there is a blank column between the two stacks of flowers.
    '''
    stack = flower1 + flower2 + flower3
    cpy = stack.copy_paste(source=Tile(1, 2), destination=Tile(1, 6))
    cpy.recolor({'orange': 'blue', 'purple': 'orange', 'blue': 'purple'})
    
    '''
    4. Repeat this shape pattern two more times using orange, blue, purple centered in
    the tenth column and blue, purple, orange centered in the fourteenth column,
    counting colors from bottom to top.
    '''
    cpy = stack.copy_paste(source=Tile(1, 2), destination=Tile(1, 10))
    cpy.recolor({'orange': 'purple', 'purple': 'blue', 'blue': 'orange'})
    
    cpy = stack.copy_paste(source=Tile(1, 2), destination=Tile(1, 14))
    
    '''
    5. Place an orange center in each blue flower, a blue center in each purple flower,
    and a purple center in each orange flower.
    '''
    tiles = Shape.get_color('blue').get(criterion='inside')
    tiles.draw('orange')
    
    tiles = Shape.get_color('purple').get(criterion='inside')
    tiles.draw('blue')
    
    tiles = Shape.get_color('orange').get(criterion='inside')
    tiles.draw('purple')
    
    g.plot(gold_boards=gold_boards, multiple=0)
