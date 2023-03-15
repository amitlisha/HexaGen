from utils.reading_tasks import read_task
from src.hexagen import HexagonsGame, Tile, Shape, Line, Circle, Triangle

task_index = 549
gold_board = list(read_task(task_index)['gold_boards'][-1])

HexagonsGame.start()

# description:
# task index: 549, image: P01C04T20, collection round: 0, category: conditions, group: train
# agreement scores: [[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 0.72, 0.72], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 0.92, 0.92], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0]]

'''
1. Start from the top left corner of the board and move over one column to the
right. Fill in the top tile in this column purple.
'''
tile1 = Tile(2, 1)
tile1.draw('purple')
'''
2. Make the next 2 tiles down purple also
'''
tile2 = tile1.neighbor(direction='down')
tile2.draw('purple')
tile3 = tile2.neighbor(direction='down')
tile3.draw('purple')
'''
3. Fill in the tile that is to the right and slightly down from the bottom purple
tile, making it purple as well.
'''
tile4 = tile3.neighbor(direction='down_right')
tile4.draw('purple')
'''
4. Make the tile 1 column to the right and slightly up purple too
'''
tile5 = tile4.neighbor(direction='up_right')
tile5.draw('purple')

'''
5. Now fill in the 2 tiles directly above this one with purple.
'''
tile6 = tile5.neighbor(direction='up')
tile6.draw('purple')
tile7 = tile6.neighbor(direction='up')
tile7.draw('purple')
'''
6. Then go over to the left one column and fill the top tile purple
'''
column = tile7.column - 1
tile8 = Tile(column, 1)
tile8.draw('purple')
'''
7. The shape should have 2 blank tiles in the middle - color these green.
'''
shape1 = Shape.get_color('all')
shape1_inside = shape1.get(criterion='inside')
shape1_inside.draw('green')
'''
8. Leave one column to the right of this shape blank and recreate the purple shape
with orange tiles.
'''
shape2 = shape1.copy_paste(shift_direction='right', spacing=1)
shape2.draw('orange')
'''
9. Fill the 2 blank tiles inside the shape with green on the top and blue on the
bottom
'''
shape2_inside = shape2.get(criterion='inside')
shape2_inside.get('top').draw('green')
shape2_inside.get('bottom').draw('blue')
'''
10. Leave another column to the right blank and recreate the frame of the shape in
orange again.
'''
shape3 = shape2.copy_paste(shift_direction='right', spacing=1)
shape3.draw('orange')
'''
11. The top blank tile inside the frame should be blue and the tile below it should
be green.
'''
shape3_inside = shape3.get(criterion='inside')
shape3_inside.get('top').draw('blue')
shape3_inside.get('bottom').draw('green')
'''
12. Leave one more column to the right blank. Create the frame of the shape again in
purple.
'''
shape4 = shape3.copy_paste(shift_direction='right', spacing=1)
shape4.draw('purple')
'''
13. Fill in the inside tiles with blue.
'''
shape4_inside = shape4.get(criterion='inside')
shape4_inside.draw('blue')
'''
14. Move to the bottom left corner of the board and go one column over to the right
and one tile up. Make this tile orange.
'''
tile9 = Tile(2, -2)
tile9.draw('orange')
'''
15. Recreate the frame of the same shape as above in orange using this newest orange
tile as the bottom left-most tile.
'''
bottom_left_most1 = shape1.extreme(direction='down_left')
bottom_left_most2 = tile9
shift = bottom_left_most1.shift(bottom_left_most2)
shape5 = shape1.copy_paste(shift=shift)
shape5.draw('orange')
'''
16. Fill in the top blank tile inside the shape with green and the bottom inside
tile with blue.
'''
shape5_inside = shape5.get(criterion='inside')
shape5_inside.get('top').draw('green')
shape5_inside.get('bottom').draw('blue')
'''
17. Recreate the frame of the shape 3 more times in purple, leaving one column to
the right of each shape blank so each new shape is in line with the shape above
it.
'''
# shapes = shape5.grid(shift_direction='right', spacing=1, num_copies=3)
shapes = []
shape = shape5
for _ in range(3):
  shape = shape.copy_paste(shift_direction='right', spacing=1)
  shape.draw('purple')
  shapes.append(shape)
'''
18. Fill in the first new purple shape's inside tiles with green.
'''
shape_inside = shapes[0].get(criterion='inside')
shape_inside.draw('green')
'''
19. Fill in the next shape's blank tiles blue.
'''
shape_inside = shapes[1].get(criterion='inside')
shape_inside.draw('blue')
'''
20. Color in the last shape's blank tiles with green.
'''
shape_inside = shapes[2].get(criterion='inside')
shape_inside.draw('green')

HexagonsGame.plot(gold_board=gold_board)
