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
    vertices = [Tile(1, 2), Tile(1, 3), Tile(1, 4), Tile(3, 2), Tile(4, 3), Tile(3, 4)]
    shape = Shape.polygon(vertices=vertices)
    shape.draw('purple')
    shape.neighbors(criterion='inside').draw('green')
    
    '''
    2. skipping a single row, Starting at the top in the next row of hex boxes, create
    a zero shape "0" of 8 orange hex boxes with one green hex box on top of one blue
    hex box in the center.
    '''
    vertices = [Tile(1, 6), Tile(1, 7), Tile(1, 8), Tile(3, 6), Tile(4, 7), Tile(3, 8)]
    shape = Shape.polygon(vertices=vertices)
    shape.draw('orange')
    shape.neighbors(criterion='inside').extreme(direction='up').draw('green')
    shape.neighbors(criterion='inside').extreme(direction='down').draw('blue')
    
    '''
    3. skipping a single row, Starting at the top in the next row of hex boxes, create
    a zero shape "0" of 8 orange hex boxes with one blue hex box on top of one green
    hex box in the center.
    '''
    vertices = [Tile(1, 10), Tile(1, 11), Tile(1, 12), Tile(3, 10), Tile(4, 11), Tile(3, 12)]
    shape = Shape.polygon(vertices=vertices)
    shape.draw('orange')
    shape.neighbors(criterion='inside').extreme(direction='up').draw('blue')
    shape.neighbors(criterion='inside').extreme(direction='down').draw('green')
    
    '''
    4. skipping a single row, Starting at the top in the next row of hex boxes, create
    a zero shape "0" of 8 purple hex boxes with two blue hex boxes in the center.
    '''
    vertices = [Tile(1, -5), Tile(1, -4), Tile(1, -3), Tile(3, -5), Tile(4, -4), Tile(3, -3)]
    shape = Shape.polygon(vertices=vertices)
    shape.draw('purple')
    shape.neighbors(criterion='inside').draw('blue')
    
    '''
    5. Starting at the bottom in the second row of hex boxes, create a zero shape "0"
    of 8 orange hex boxes with one green hex box on top of one blue hex box in the
    center.
    '''
    vertices = [Tile(7, 2), Tile(7, 3), Tile(7, 4), Tile(9, 2), Tile(10, 3), Tile(9, 4)]
    shape = Shape.polygon(vertices=vertices)
    shape.draw('orange')
    shape.neighbors(criterion='inside').extreme(direction='up').draw('green')
    shape.neighbors(criterion='inside').extreme(direction='down').draw('blue')
    
    '''
    6. skipping a single row, Starting at the bottom in the next row of hex boxes,
    create a zero shape "0" of 8 purple hex boxes with two green hex boxes in the
    center.
    '''
    vertices = [Tile(7, 6), Tile(7, 7), Tile(7, 8), Tile(9, 6), Tile(10, 7), Tile(9, 8)]
    shape = Shape.polygon(vertices=vertices)
    shape.draw('purple')
    shape.neighbors(criterion='inside').draw('green')
    
    '''
    7. skipping a single row, Starting at the bottom in the next row of hex boxes,
    create a zero shape "0" of 8 purple hex boxes with two blue hex boxes in the
    center.
    '''
    vertices = [Tile(7, 10), Tile(7, 11), Tile(7, 12), Tile(9, 10), Tile(10, 11), Tile(9, 12)]
    shape = Shape.polygon(vertices=vertices)
    shape.draw('purple')
    shape.neighbors(criterion='inside').draw('blue')
    
    '''
    8. skipping a single row, Starting at the bottom in the next row of hex boxes,
    create a zero shape "0" of 8 purple hex boxes with two green hex boxes in the
    center.
    '''
    vertices = [Tile(7, 14), Tile(7, 15), Tile(7, 16), Tile(9, 14), Tile(10, 15), Tile(9, 16)]
    shape = Shape.polygon(vertices=vertices)
    shape.draw('purple')
    shape.neighbors(criterion='inside').draw('green')
    
    g.plot(gold_boards=gold_boards, multiple=0)
