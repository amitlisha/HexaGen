# Created by by maor

from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle

task_index = 221
gold_boards = list(read_task(task_index)['gold_boards'])

with Game() as g:
    
    # description:
    # task index: 221, image: P01C08T03, collection round: 1, category: other, group: train
    # agreement scores: [[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0]]
    
    '''
    1. In column four, paint tiles 3-8 green, omitting tile 6.
    '''
    Line(start_tile=Tile(3, 4), end_tile=Tile(8, 4)).draw('green')
    Tile(6, 4).draw('white')
    
    '''
    2. In column five, paint tiles 4-9 red.
    '''
    Line(start_tile=Tile(4, 5), end_tile=Tile(9, 5)).draw('red')
    
    '''
    3. In column six, paint tiles 4-8 purple.
    '''
    Line(start_tile=Tile(4, 6), end_tile=Tile(8, 6)).draw('purple')
    
    '''
    4. In column seven, paint tiles 5-7 orange.
    '''
    Line(start_tile=Tile(5, 7), end_tile=Tile(7, 7)).draw('orange')
    
    '''
    5. In column eight, paint tile 3 blue, and tiles 5-6 yellow.
    '''
    Tile(3, 8).draw('blue')
    Line(start_tile=Tile(5, 8), end_tile=Tile(6, 8)).draw('yellow')
    
    '''
    6. In column nine, paint tiles 4-8 blue.
    '''
    Line(start_tile=Tile(4, 9), end_tile=Tile(8, 9)).draw('blue')
    
    '''
    7. In column ten, paint tile 3 blue, and tiles 5-6 yellow.
    '''
    Tile(3, 10).draw('blue')
    Line(start_tile=Tile(5, 10), end_tile=Tile(6, 10)).draw('yellow')
    
    '''
    8. In column eleven, paint tiles 5-7 orange.
    '''
    Line(start_tile=Tile(5, 11), end_tile=Tile(7, 11)).draw('orange')
    
    '''
    9. In column twelve, paint tiles 4-8 purple.
    '''
    Line(start_tile=Tile(4, 12), end_tile=Tile(8, 12)).draw('purple')
    
    '''
    10. In column thirteen, paint tiles 4-9 red.
    '''
    Line(start_tile=Tile(4, 13), end_tile=Tile(9, 13)).draw('red')
    
    '''
    11. In column fourteen, paint tiles 3-8 green, omitting tile 6.
    '''
    Line(start_tile=Tile(3, 14), end_tile=Tile(8, 14)).draw('green')
    Tile(6, 14).draw('white')
    
    g.plot(gold_boards=gold_boards, multiple=0)
