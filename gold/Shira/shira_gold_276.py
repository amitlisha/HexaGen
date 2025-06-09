from utils.reading_tasks import read_task
from hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle

task_index = 276
gold_boards = list(read_task(task_index)['gold_boards'])

HexagonsGame.start()

# procedure 276, image P01C06T04, collection round 1, category symmetry, group train

'''
1. Paint the tile black that is fifth from the top in the ninth column from the
right.
'''
black_tile = Tile(-9, 5)
black_tile.draw('black')
'''
2. Paint the fifth tile from the top of the far right column red.
'''
red_tile = Tile(-1, 5)
red_tile.draw('red')
'''
3. Paint the four blank tiles that are touching the red tile purple.
'''
purple_tiles = red_tile.neighbors('white')
purple_tiles.draw('purple')
'''
4. Moving toward the center, paint the next tile to the left of the purple tiles
purple also.
'''
left_tile = purple_tiles.neighbors('left')
left_tile.draw('purple')
'''
5. Paint all the blank tiles that are touching these purple tiles green, adding one
more green tile between the two leftmost ones to form the point of a sideways V
shape.
'''
all_purple_tiles = Shape.get_color('purple')
green_tiles = all_purple_tiles.neighbors('white')
green_tiles = green_tiles + green_tiles.neighbors('left')
green_tiles.draw('green')
'''
6. Create a similar shape in blue around the green tiles.
'''
blue_tiles = green_tiles.neighbors('white')
blue_tiles.draw('blue')
'''
7. Create a symmetrical mirror image of the image formed in steps 2 through 6, to
the left of the center black tile.
'''
colored_tiles = Shape.get_color('all')
colored_tiles.reflect(column = black_tile.column)
'''
8. Starting in the tile directly above the black tile paint two diagonal lines to
form a V shape between the black tile and the upper edge of the grid.
'''
start_v_tile = black_tile.neighbor('up')
v_shape = Line(start_tile = start_v_tile, direction = 'up_right') +Line(start_tile = start_v_tile, direction = 'up_left')
v_shape.draw('black')
'''
9. Inside the V, paint the eleven tiles across the top of the V yellow.
'''
inside_v_shape = v_shape.get('above')
yellow_tiles = inside_v_shape.get('top')
yellow_tiles.draw('yellow')
'''
10. Paint the seven blank tiles directly touching the yellow ones orange.
'''
orange_tiles = yellow_tiles.neighbors('white')
orange_tiles.draw('orange')
'''
11. Paint the three blank tiles directly touching the orange ones red.
'''
red_tiles = orange_tiles.neighbors('white')
red_tiles.draw('red')
'''
12. Create a symmetrical mirror image of the figure created in steps 8 through 11,
below the center black tile.
'''
figure = v_shape + yellow_tiles + orange_tiles + red_tiles
figure.reflect(axis_direction = 'horizontal', tile_on_axis = black_tile)

HexagonsGame.plot(gold_boards=gold_boards)
