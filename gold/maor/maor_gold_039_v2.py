# Created by maor

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle

task_index = 39
gold_boards = list(read_task(task_index)['gold_boards'])

with Game() as g:
    
    # description:
    # task index: 39, image: P01C02T11, collection round: 1, category: bounded iteration, group: train
    # agreement scores: [[1.0, 1.0, 1.0], [1.0, 0.58, 0.58], [1.0, 0.45, 0.45]]
    
    '''
    1. on fifth row down from top, and 10th row from left, leave that tile blank but
    color all tiles that touch it, red. This forms a red circle.
    '''
    tile = Tile(5, 10)
    neighbors = tile.neighbors()
    neighbors.draw('red')
    
    '''
    2. Repeat this design, but make it in green, use topmost red tile to organize the
    green circle, the two tiles directly on top of the uppermost red tile form the
    leftmost wall of the new green six sided flower, alternate this pattern all
    around the central red.
    '''
    circle1 = Circle(center_tile=Tile(3, 11))
    circle2 = Circle(center_tile=Tile(7, 12))
    circle3 = Circle(center_tile=Tile(6, 7))
    
    circle1.draw('green')
    circle2.draw('green')
    circle3.draw('green')
    
    '''
    3. Place a blue six sided circle that touches both the green and red, to the right
    of red, continue alternating green again, then blue, forming three total green
    and three total blue completely surrounding the original red circle with
    similarly designed circles, all with a white tile in the center.
    '''
    
    circle4 = Circle(center_tile=Tile(5, 13))
    circle5 = Circle(center_tile=Tile(3, 8))
    circle6 = Circle(center_tile=Tile(8, 9))
    
    circle4.draw('blue')
    circle5.draw('blue')
    circle6.draw('blue')
    
    g.plot(gold_boards=gold_boards, multiple=0)
