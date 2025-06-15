# Created by maor

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle

task_index = 552
gold_boards = list(read_task(task_index)['gold_boards'])

with Game() as g:
    
    # description:
    # task index: 552, image: P01C04T20, collection round: 0, category: conditions, group: train
    # agreement scores: [[0.2, 0.2, 1.0], [0.1, 0.2, 0.5], [0.08, 0.2, 0.4], [0.07, 0.2, 0.33], [0.18, 0.16, 0.89], [0.16, 0.13, 0.8], [0.14, 0.11, 0.73], [0.13, 0.25, 0.67]]
    
    '''
    1. Starting at the top in the second row of hex boxes, create a zero shape "0" of 8
    purple hex boxes with two green hex boxes in the center.
    '''
    vertices = [Tile(2, 1), Tile(3, 1), Tile(4, 1), Tile(2, 3), Tile(3, 4), Tile(4, 3)]
    shape = Shape.polygon(vertices=vertices)
    shape.draw('purple')
    shape.neighbors(criterion='inside').draw('green')
    
    '''
    2. skipping a single row, Starting at the top in the next row of hex boxes, create
    a zero shape "0" of 8 orange hex boxes with one green hex box on top of one blue
    hex box in the center.
    '''
    vertices = [Tile(6, 1), Tile(7, 1), Tile(8, 1), Tile(6, 3), Tile(7, 4), Tile(8, 3)]
    shape = Shape.polygon(vertices=vertices)
    shape.draw('orange')
    shape.neighbors(criterion='inside').extreme(direction='up').draw('green')
    shape.neighbors(criterion='inside').extreme(direction='down').draw('blue')
    
    '''
    3. skipping a single row, Starting at the top in the next row of hex boxes, create
    a zero shape "0" of 8 orange hex boxes with one blue hex box on top of one green
    hex box in the center.
    '''
    vertices = [Tile(10, 1), Tile(11, 1), Tile(12, 1), Tile(10, 3), Tile(11, 4), Tile(12, 3)]
    shape = Shape.polygon(vertices=vertices)
    shape.draw('orange')
    shape.neighbors(criterion='inside').extreme(direction='up').draw('blue')
    shape.neighbors(criterion='inside').extreme(direction='down').draw('green')
    
    '''
    4. skipping a single row, Starting at the top in the next row of hex boxes, create
    a zero shape "0" of 8 purple hex boxes with two blue hex boxes in the center.
    '''
    vertices = [Tile(-5, 1), Tile(-4, 1), Tile(-3, 1), Tile(-5, 3), Tile(-4, 4), Tile(-3, 3)]
    shape = Shape.polygon(vertices=vertices)
    shape.draw('purple')
    shape.neighbors(criterion='inside').draw('blue')
    
    '''
    5. Starting at the bottom in the second row of hex boxes, create a zero shape "0"
    of 8 orange hex boxes with one green hex box on top of one blue hex box in the
    center.
    '''
    vertices = [Tile(2, 7), Tile(3, 7), Tile(4, 7), Tile(2, 9), Tile(3, 10), Tile(4, 9)]
    shape = Shape.polygon(vertices=vertices)
    shape.draw('orange')
    shape.neighbors(criterion='inside').extreme(direction='up').draw('green')
    shape.neighbors(criterion='inside').extreme(direction='down').draw('blue')
    
    '''
    6. skipping a single row, Starting at the bottom in the next row of hex boxes,
    create a zero shape "0" of 8 purple hex boxes with two green hex boxes in the
    center.
    '''
    vertices = [Tile(6, 7), Tile(7, 7), Tile(8, 7), Tile(6, 9), Tile(7, 10), Tile(8, 9)]
    shape = Shape.polygon(vertices=vertices)
    shape.draw('purple')
    shape.neighbors(criterion='inside').draw('green')
    
    '''
    7. skipping a single row, Starting at the bottom in the next row of hex boxes,
    create a zero shape "0" of 8 purple hex boxes with two blue hex boxes in the
    center.
    '''
    vertices = [Tile(10, 7), Tile(11, 7), Tile(12, 7), Tile(10, 9), Tile(11, 10), Tile(12, 9)]
    shape = Shape.polygon(vertices=vertices)
    shape.draw('purple')
    shape.neighbors(criterion='inside').draw('blue')
    
    '''
    8. skipping a single row, Starting at the bottom in the next row of hex boxes,
    create a zero shape "0" of 8 purple hex boxes with two green hex boxes in the
    center.
    '''
    vertices = [Tile(14, 7), Tile(15, 7), Tile(16, 7), Tile(14, 9), Tile(15, 10), Tile(16, 9)]
    shape = Shape.polygon(vertices=vertices)
    shape.draw('purple')
    shape.neighbors(criterion='inside').draw('green')
    
    g.plot(gold_boards=gold_boards, multiple=0)
