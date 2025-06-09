# Created by maor

from utils.reading_tasks import read_task
from hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle

task_index = 618
gold_boards = list(read_task(task_index)['gold_boards'])

HexagonsGame.start()

# description:
# task index: 618, image: P01C04T20, collection round: 0, category: conditions, group: train
# agreement scores: None

'''
1. On the second column, fill out the top three hexagons in purple.
'''
line = Line(start_tile=Tile(2,1), length=3, direction='down')
line.draw('purple')

'''
2. Leave three spaces and fill out the next three hexagons in orange.
'''
line = Line(start_tile=Tile(2,7), length=3, direction='down')
line.draw('orange')

'''
3. On the third column, fill out the first hexagon in purple, then two green, then
one purple.
'''
tile = Tile(column=3, row=1)
tile.draw('purple')

tile = Tile(column=3, row=2)
tile.draw('green')

tile = Tile(column=3, row=3)
tile.draw('green')

tile = Tile(column=3, row=4)
tile.draw('purple')

'''
4. Leave two spaces, then fill out the next hexagon in orange, then green, purple,
and orange.
'''
tile = Tile(column=3, row=7)
tile.draw('orange')

tile = Tile(column=3, row=8)
tile.draw('green')

tile = Tile(column=3, row=9)
tile.draw('blue')

tile = Tile(column=3, row=10)
tile.draw('orange')

'''
5. On the fourth column, fill out the top three hexagons in purple.
'''
line = Line(start_tile=Tile(4,1), length=3, direction='down')
line.draw('purple')

'''
6. Leave three spaces and fill out the next three hexagons in orange.
'''
line = Line(start_tile=Tile(4,7), length=3, direction='down')
line.draw('orange')

'''
7. The fifth column is left blank.
'''

'''
8. On the sixth column, fill out the top three hexagons in orange.
'''
line = Line(start_tile=Tile(6,1), length=3, direction='down')
line.draw('orange')

'''
9. Leave three spaces and fill out the next three hexagons in purple.
'''
line = Line(start_tile=Tile(6,7), length=3, direction='down')
line.draw('purple')

'''
10. On the seventh column, fill out the first hexagon in orange, then green, then
blue, then orange.
'''
tile = Tile(column=7, row=1)
tile.draw('orange')

tile = Tile(column=7, row=2)
tile.draw('green')

tile = Tile(column=7, row=3)
tile.draw('blue')

tile = Tile(column=7, row=4)
tile.draw('orange')

'''
11. Leave two spaces and then fill out the next hexagon in purple, then two green,
then purple again.
'''
tile = Tile(column=7, row=7)
tile.draw('purple')

tile = Tile(column=7, row=8)
tile.draw('green')

tile = Tile(column=7, row=9)
tile.draw('green')

tile = Tile(column=7, row=10)
tile.draw('purple')

'''
12. On the eigth column, fill out the first three hexagons in orange.
'''
line = Line(start_tile=Tile(8,1), length=3, direction='down')
line.draw('orange')

'''
13. Leave three spaces and fill out the next three hexagons in purple.
'''
line = Line(start_tile=Tile(8,7), length=3, direction='down')
line.draw('purple')

'''
14. The ninth column is left blank.
'''

'''
15. On the 10th column, fill out the top three hexagons in orange.
'''
line = Line(start_tile=Tile(10,1), length=3, direction='down')
line.draw('orange')

'''
16. Leave three spaces and then fill out the next three hexagons in purple.
'''
line = Line(start_tile=Tile(10,7), length=3, direction='down')
line.draw('purple')

'''
17. On the 11th column, fill out the first hexagon in orange, then blue, then green,
then orange again.
'''
tile=Tile(column=11, row=1)
tile.draw('orange')

tile=Tile(column=11, row=2)
tile.draw('blue')

tile=Tile(column=11, row=3)
tile.draw('green')

tile=Tile(column=11, row=4)
tile.draw('orange')

'''
18. Leave two blank spaces and fill out the next hexagon in purple, then two blue,
then one purple.
'''
tile=Tile(column=11, row=7)
tile.draw('purple')

tile=Tile(column=11, row=8)
tile.draw('blue')

tile=Tile(column=11, row=9)
tile.draw('blue')

tile=Tile(column=11, row=10)
tile.draw('purple')

'''
19. On the 12th column, fill out the first three hexagons in orange.
'''
line = Line(start_tile=Tile(12,1), length=3, direction='down')
line.draw('orange')

'''
20. Leave three spaces and fill out the next three hexagons in purple.
'''
line = Line(start_tile=Tile(12,7), length=3, direction='down')
line.draw('purple')

'''
21. The 13th column is left blank.
'''

'''
22. On the 14th column, fill out the top three hexagons in purple.
'''
line = Line(start_tile=Tile(14,1), length=3, direction='down')
line.draw('purple')

'''
23. Leave three spaces and fill out the next three hexagons in purple.
'''
line = Line(start_tile=Tile(14,7), length=3, direction='down')
line.draw('purple')

'''
24. On the 15th column, fill out the first hexagon in purple, then two blue, then
purple again.
'''
tile=Tile(column=15, row=1)
tile.draw('purple')

tile=Tile(column=15, row=2)
tile.draw('blue')

tile=Tile(column=15, row=3)
tile.draw('blue')

tile=Tile(column=15, row=4)
tile.draw('purple')

'''
25. Leave two blank spaces and fill out the next hexagon in purple, then two green,
then one purple again.
'''
tile=Tile(column=15, row=7)
tile.draw('purple')

tile=Tile(column=15, row=8)
tile.draw('green')

tile=Tile(column=15, row=9)
tile.draw('green')

tile=Tile(column=15, row=10)
tile.draw('purple')

'''
26. On the 16th column, fill out the top three hexagons in purple.
'''
line = Line(start_tile=Tile(16,1), length=3, direction='down')
line.draw('purple')

'''
27. Leave three blank spaces and then fill out the next three hexagons in purple.
'''
line = Line(start_tile=Tile(16,7), length=3, direction='down')
line.draw('purple')

HexagonsGame.plot(gold_boards=gold_boards, multiple=0)
