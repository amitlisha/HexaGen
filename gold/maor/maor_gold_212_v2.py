# Created by maor

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle

task_index = 212
gold_boards = list(read_task(task_index)['gold_boards'])

with Game() as g:
    
    # description:
    # task index: 212, image: P01C07T10, collection round: 1, category: composed objects, group: train
    # agreement scores: [[1.0, 1.0, 1.0], [1.0, 0.67, 0.67], [1.0, 0.8, 0.8], [1.0, 1.0, 1.0]]
    
    '''
    1. On the second line from the left, second tile down, leave that tile blank, but
    color in all tiles that touch it purple. Repeat this step twice, forming 2
    purple circles directly and abutting the first one, total of 3 circles made in
    left side of the grid.
    '''
    tile = Tile(column=2, row=2)
    circle = tile.neighbors()
    circle.draw('purple')
    
    circle = circle.copy_paste(source=tile.neighbor('up'), destination=tile.neighbor('down').neighbor('down'))
    circle.draw('purple')
    
    circle = circle.copy_paste(source=tile.neighbor('up'), destination=tile.neighbor('down').neighbor('down'))
    circle.draw('purple')
    
    '''
    2. on sixth tile from the left, starting at the top, color top three tiles orange
    and the two centered tiles to the left of those three, and the one centered to
    the left of those, orange. This will make an Orange triangle, repeat this,
    making two more triangles abutting the bottom of the first triangle to the top
    of the second, etc.
    '''
    triangle = Shape([Tile(6,1), Tile(6,2), Tile(6,3), Tile(5,2), Tile(5,3), Tile(4,2)])
    triangle.draw('orange')
    
    triangle = triangle.copy_paste(source=tile.neighbor('up'), destination=tile.neighbor('down').neighbor('down'))
    triangle.draw('orange')
    
    triangle = triangle.copy_paste(source=tile.neighbor('up'), destination=tile.neighbor('down').neighbor('down'))
    triangle.draw('orange')
    
    '''
    3. Repeat these first 2 steps twice more forming three sets of each shape, the
    rings of purple then the orange triangle, the point of the triangles leftmost.
    For clarity the second set of purple rings begins on the 7th vertical row.
    '''
    shape = Shape.get_color('purple') + Shape.get_color('orange')
    shape = shape.copy_paste(shift_direction='right', spacing=0)
    shape = shape.copy_paste(shift_direction='right', spacing=0)
    
    '''
    4. Each row will consist of First Purple rings, next orange triangles, repeat the
    whole thing twice.
    '''
    
    g.plot(gold_boards=gold_boards, multiple=0)
