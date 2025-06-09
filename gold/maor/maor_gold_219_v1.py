# Created by maor

from utils.reading_tasks import read_task
from hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle

task_index = 219
gold_boards = list(read_task(task_index)['gold_boards'])

HexagonsGame.start()

# description:
# task index: 219, image: P01C08T03, collection round: 1, category: other, group: train
# agreement scores: [[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0]]

'''
1. From the left, count nine columns over and three hexagons down. Color blue the
next five hexagons down.
'''
tile = Tile(column=9, row=3)
blue_line = Line(start_tile=tile.neighbor(direction='down'), length=5, direction='down')
blue_line.draw('blue')

'''
2. From the top blue hexagon, color the upper left and upper right attached
hexagons in blue as well.
'''
tile1 = blue_line.edge(direction='up').neighbor('up_left')
tile1.draw('blue')
tile2 = blue_line.edge(direction='up').neighbor('up_right')
tile2.draw('blue')

'''
3. Looking at the last two hexagons colored, skip the next hexagon underneath each
and color the next two on each column in yellow.
'''
left_yellow = Line(start_tile=tile1.neighbor(direction='down').neighbor(direction='down'), direction='down', length=2)
left_yellow.draw('yellow')

right_yellow = Line(start_tile=tile2.neighbor(direction='down').neighbor(direction='down'), direction='down', length=2)
right_yellow.draw('yellow')

'''
4. On each yellow, opposite the blue, color in three orange hexagons, such that all
three touch only yellow. Be sure to do so on both lines of yellow.
'''
left_orange = Line(start_tile=left_yellow.edge('up').neighbor('up_left'), direction='down', length=3)
left_orange.draw('orange')

right_orange = Line(start_tile=right_yellow.edge('up').neighbor('up_right'), direction='down', length=3)
right_orange.draw('orange')

'''
5. Going out from there, starting at the topmost hexagon touching only orange,
color in purple five hexagons total going down. Do so for both orange lines.
'''
left_purple = Line(start_tile=left_orange.edge('up').neighbor('up_left'), direction='down', length=5)
left_purple.draw('purple')

right_purple = Line(start_tile=right_orange.edge('up').neighbor('up_right'), direction='down', length=5)
right_purple.draw('purple')

'''
6. On the other side of both purple lines, color a line of six red hexagons
straight down connected to all the purple hexagons.
'''
left_red = Line(start_tile=left_purple.edge('up').neighbor('up_left'), direction='down', length=6)
left_red.draw('red')

right_red = Line(start_tile=right_purple.edge('up').neighbor('up_right'), direction='down', length=6)
right_red.draw('red')

'''
7. On the next columns out from each red, skip the top two hexagons, color the next
three green, skip one then color two more. Be sure this is mirrored on each
side.
'''
left_green1 = Line(start_tile=left_red.edge('up').neighbor('up_left'), direction='down', length=3)
left_green1.draw('green')

left_green2 = Line(start_tile=left_green1.end_tile.neighbor(direction='down').neighbor(direction='down'), direction='down', length=2)
left_green2.draw('green')

Shape.get_color('green').reflect(axis_line=blue_line)

HexagonsGame.plot(gold_boards=gold_boards, multiple=0)
