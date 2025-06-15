from utils.reading_tasks import read_task
from hexagen import Game, Tile, Shape, Line, Circle, Triangle

task_index = 596
gold_boards = list(read_task(task_index)['gold_boards'])

with Game() as g:
    
    # description:
    # task index: 596, image: P01C02T04, collection round: 0, category: bounded iteration, group: train
    # agreement scores: [[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0]]
    
    '''
    1. starting on top tile on leftmost vertical column, color the top three tiles
    blue, the fourth through sixth tiles from the top, color them purple. The
    seventh through ninth tiles on leftmost column should be colored yellow.
    '''
    column = 1
    line1 = Line(start_tile=Tile(column, 1), direction='down', length=3)
    line1.draw('blue')
    line2 = Line(start_tile=Tile(column, 4), end_tile=Tile(column, 6), direction='down')
    line2.draw('purple')
    line3 = Line(start_tile=Tile(column, 7), end_tile=Tile(column, 9), direction='down')
    line3.draw('yellow')
    '''
    2. on third vertical row from the left, color the first three tiles from the top,
    purple, the fourth through sixth tiles from the top should be colored yellow,
    the seventh through ninth tiles should be colored blue.
    '''
    column = 3
    line4 = Line(start_tile=Tile(column, 1), direction='down', length=3)
    line4.draw('purple')
    line5 = Line(start_tile=Tile(column, 4), end_tile=Tile(column, 6), direction='down')
    line5.draw('yellow')
    line6 = Line(start_tile=Tile(column, 7), end_tile=Tile(column, 9), direction='down')
    line6.draw('blue')
    '''
    3. On fifth row from the left, vertical row should be colored yellow on top three
    tiles downward, tiles four through six down should be blue. Tiles seven through
    nine from top should be purple.
    '''
    column = 5
    line7 = Line(start_tile=Tile(column, 1), direction='down', length=3)
    line7.draw('yellow')
    line8 = Line(start_tile=Tile(column, 4), end_tile=Tile(column, 6), direction='down')
    line8.draw('blue')
    line9 = Line(start_tile=Tile(column, 7), end_tile=Tile(column, 9), direction='down')
    line9.draw('purple')
    '''
    4. On The seventh vertical row from left, repeat all parts used in number 1.
    '''
    column = 7
    line1 = Line(start_tile=Tile(column, 1), direction='down', length=3)
    line1.draw('blue')
    line2 = Line(start_tile=Tile(column, 4), end_tile=Tile(column, 6), direction='down')
    line2.draw('purple')
    line3 = Line(start_tile=Tile(column, 7), end_tile=Tile(column, 9), direction='down')
    line3.draw('yellow')
    '''
    5. On the ninth vertical row from left, repeat all parts of Number 2.
    '''
    column = 9
    line4 = Line(start_tile=Tile(column, 1), direction='down', length=3)
    line4.draw('purple')
    line5 = Line(start_tile=Tile(column, 4), end_tile=Tile(column, 6), direction='down')
    line5.draw('yellow')
    line6 = Line(start_tile=Tile(column, 7), end_tile=Tile(column, 9), direction='down')
    line6.draw('blue')
    '''
    6. On the eleventh row, vertical, from the left, repeat all steps in number 3.
    '''
    column = 11
    line7 = Line(start_tile=Tile(column, 1), direction='down', length=3)
    line7.draw('yellow')
    line8 = Line(start_tile=Tile(column, 4), end_tile=Tile(column, 6), direction='down')
    line8.draw('blue')
    line9 = Line(start_tile=Tile(column, 7), end_tile=Tile(column, 9), direction='down')
    line9.draw('purple')
    '''
    7. On Thirteenth row, vertical from left, repeat All parts of number 1.
    '''
    column = 13
    line1 = Line(start_tile=Tile(column, 1), direction='down', length=3)
    line1.draw('blue')
    line2 = Line(start_tile=Tile(column, 4), end_tile=Tile(column, 6), direction='down')
    line2.draw('purple')
    line3 = Line(start_tile=Tile(column, 7), end_tile=Tile(column, 9), direction='down')
    line3.draw('yellow')
    '''
    8. On the Fifteenth vertical row from left, repeat all parts of number 2.
    '''
    column = 15
    line4 = Line(start_tile=Tile(column, 1), direction='down', length=3)
    line4.draw('purple')
    line5 = Line(start_tile=Tile(column, 4), end_tile=Tile(column, 6), direction='down')
    line5.draw('yellow')
    line6 = Line(start_tile=Tile(column, 7), end_tile=Tile(column, 9), direction='down')
    line6.draw('blue')
    '''
    9. On the seventeenth row from left, vertical, repeat all steps in number 3.
    '''
    column = 17
    line7 = Line(start_tile=Tile(column, 1), direction='down', length=3)
    line7.draw('yellow')
    line8 = Line(start_tile=Tile(column, 4), end_tile=Tile(column, 6), direction='down')
    line8.draw('blue')
    line9 = Line(start_tile=Tile(column, 7), end_tile=Tile(column, 9), direction='down')
    line9.draw('purple')
    '''
    10. 
    '''
    
    g.plot(gold_boards=gold_boards)
