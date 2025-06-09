from utils.reading_tasks import read_task
from hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle

task_index = 593
gold_boards = list(read_task(task_index)['gold_boards'])

HexagonsGame.start()

# description:
# task index: 593, image: P01C02T04, collection round: 0, category: bounded iteration, group: train
# agreement scores: [[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0]]

'''
1. Begin at the leftmost column and paint the top 3 tiles blue.
'''
line1 = Line(start_tile=Tile(1, 1), direction='down', length=3)
line1.draw('blue')
'''
2. Directly below the 3 blue tiles, paint the following 3 tiles purple.
'''
line2 = Line(start_tile=line1.neighbors('down'), direction='down', length=3)
line2.draw('purple')
'''
3. Following the same pattern as before, paint the 3 tiles directly below the
previous step yellow.
'''
line3 = Line(start_tile=line2.neighbors('down'), direction='down', length=3)
line3.draw('yellow')
'''
4. Following the same grouping pattern, paint the top 3 tiles of the 3rd column
purple.
'''
line4 = Line(start_tile=Tile(3, 1), direction='down', length=3)
line4.draw('purple')
'''
5. Directly below the purple tiles, paint the next 3 tiles below that yellow.
'''
line5 = Line(start_tile=line4.neighbors('down'), direction='down', length=3)
line5.draw('yellow')
'''
6. Fill in the the following 3 tiles below that blue.
'''
line6 = Line(start_tile=line5.neighbors('down'), direction='down', length=3)
line6.draw('blue')
'''
7. Paint the top 3 tiles of the fifth column yellow.
'''
line7 = Line(start_tile=Tile(5, 1), direction='down', length=3)
line7.draw('yellow')
'''
8. Paint the next 3 tiles immediately under that blue.
'''
line8 = Line(start_tile=line7.neighbors('down'), direction='down', length=3)
line8.draw('blue')
'''
9. Color the next group of 3 tiles below the first two groups purple.
'''
line9 = Line(start_tile=line8.neighbors('down'), direction='down', length=3)
line9.draw('purple')
'''
10. Repeat steps one through nine two more times, leaving an empty column between
each colored column.
'''
column = 5
for _ in range(2):
  column += 2
  line1 = Line(start_tile=Tile(column, 1), direction='down', length=3)
  line1.draw('blue')
  line2 = Line(start_tile=line1.neighbors('down'), direction='down', length=3)
  line2.draw('purple')
  line3 = Line(start_tile=line2.neighbors('down'), direction='down', length=3)
  line3.draw('yellow')

  column += 2
  line4 = Line(start_tile=Tile(column, 1), direction='down', length=3)
  line4.draw('purple')
  line5 = Line(start_tile=line4.neighbors('down'), direction='down', length=3)
  line5.draw('yellow')
  line6 = Line(start_tile=line5.neighbors('down'), direction='down', length=3)
  line6.draw('blue')

  column += 2
  line7 = Line(start_tile=Tile(column, 1), direction='down', length=3)
  line7.draw('yellow')
  line8 = Line(start_tile=line7.neighbors('down'), direction='down', length=3)
  line8.draw('blue')
  line9 = Line(start_tile=line8.neighbors('down'), direction='down', length=3)
  line9.draw('purple')


HexagonsGame.plot(gold_boards=gold_boards)
