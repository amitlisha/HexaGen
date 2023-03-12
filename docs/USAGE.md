# Usage Guide
Welcome to the Hexagons usage guide. In this guide, we'll provide you with detailed instructions on how to use the most important features of our Python package, complete with code examples.

## Basic Example: Single Blue Hexagon
This is the code so-called 'frame':
```python
from hexagons_classes import HexagonsGame, Tile, Shape, Line, Circle, Triangle
HexagonsGame.start()

# insert code here

HexagonsGame.plot()
```
For example:
```python
from hexagons_classes import HexagonsGame, Tile, Shape, Line, Circle, Triangle
HexagonsGame.start()

tile = Tile(5,7)
tile.draw('blue')

HexagonsGame.plot()
```
<img src="board_examples/single_blue_hex.png" alt="single blue hexagon" width="40%" height="40%">

From now on we omit the code frame.

## `Tile` Class
To create a tile in Hexagons, use the Tile class. To paint it in a desired color, use the `draw` method. The `Tile` class requires two parameters: `column` and `row`. `column` is numbered from 1 (leftmost column) to 18 (rightmost column), while `row` is numbered from 1 (top row) to 10 (bottom row). If you use a negative value for column or row, the counting will start from the rightmost column or bottom row, respectively.
```python
Tile(column=1, row=1).draw('red')
Tile(column=1, row=-1).draw('blue')
Tile(column=-1, row=1).draw('green')
Tile(column=-1, row=-1).draw('orange')
```
<img src="board_examples/corners.png" alt="corners" width="40%" height="40%">

## `Shape` Class 
A shape in Hexagons is any set of tiles on the board, including the empty set and a single tile.
To create a shape in Hexagons, use the `Shape` class, which requires a single parameter: `tiles`. `tiles` is a list of Tile objects, that specifies the tiles composing the shape.
```python
shape = Shape(tiles=[Tile(9, 5), Tile(10, 5), Tile(9, 6)])
shape.draw('purple')
```
<img src="board_examples/simple_purple_shape.png" alt="simple purple shape" width="40%" height="40%">

### Attributes
...

### Subclasses
The `Shape` class has three special subclasses that we will now describe: `Circle`, `Line` and `Triangle`.

#### Circle
To create a circle in Hexagons, use the `Circle` class, which requires two parameters: `center_tile` and `radius`. `center_tile` is a tile object that specifies the center tile of the circle. `radius` is an integer that specifies the radius of the circle.  If you do not specify a `radius` value, it defaults to `1`.
```python
circle = Circle(center_tile = Tile(9, 5), radius = 3)
circle.draw('black')
```
<img src="board_examples/black_circle.png" alt="black circle" width="40%" height="40%">

#### Line
To create a line in Hexagons, use the `Line` class.
There are several to instantiate a new `Line` object:

##### Using `start_tile` and `end_tile`
Specify `start_tile` and `end_tile` as `Tile` objects to define the start and end points of the line.
```python
line = Line(start_tile=Tile(3, 2), end_tile=Tile(-3, -3))
line.draw('blue')
```
<img src="board_examples/line_start_end.png" alt="line start end" width="40%" height="40%">

##### Using `start_tile`, `direction` and `length`
Use `direction` to specify the direction of the line, choosing from 'up', 'up_right', 'up_left', 'down', 'down_right', or 'down_left', and use `length` to specify the length of the line.
```python
line = Line(start_tile=Tile(3, 8), direction='up_right', length=5)
line.draw('blue')
```
<img src="board_examples/line_start_direction_length.png" alt="line start direction end" width="40%" height="40%">

##### Using `start_tile` and `direction`
If `length` is not specified, the line will extend until it reaches the edge of the board.
```python
line = Line(start_tile=Tile(3, 8), direction='up_right')
line.draw('blue')
```
<img src="board_examples/line_start_direction.png" alt="line start direction" width="40%" height="40%">

##### Using `start_tile`, `direction` and `end_tiles`
Specify a `Shape` object `end_tiles` to stop the line when it reaches any tile belonging to the shape.
```python
circle = Circle(center_tile=Tile(15, 8), radius=2)
circle.draw('red')
line = Line(start_tile=Tile(1, 1), direction='down_right', end_tiles=circle)
line.draw('blue')
```
<img src="board_examples/line_end_tiles.png" alt="line end tiles" width="40%" height="40%">

##### Additional: `include_start_tile` and `include_end_tile` flags
By default, `include_start_tile` and `include_end_tile` are both set to `True`, but you can set them to `False` to omit the starting or ending tile from the line, respectively.
```python
line = Line(start_tile=Tile(9, 1), end_tile=Tile(9, -1), include_start_tile=False, include_end_tile=False)
line.draw('blue')
```
<img src="board_examples/line_dont_include.png" alt="line dont include" width="40%" height="40%">

### Methods

The `Shape` class has many useful methods that can be used on any `Shape` object, including objects from any of its subclasses, as well as on `Tile` objects. In the following sections, we will describe these methods in detail.

#### Set

##### Iteration
The Shape class implements the iterator protocol, which means that you can iterate over the tiles in a shape using a for loop or a list comprehension. For example, the code for tile in shape: will iterate over all the tiles in the Shape object shape, and you can perform operations on each tile inside the loop body.

##### `add`, `subtract` and `multiply`
It is possible to use the plus, minus, and asterisk signs to compute the union, difference, and intersection of shapes respectively.
For example, to compute the union of two Shape objects `shape1` and `shape2` use: `shape3 = shape1 + shape2`.
The resulting shape3 object will be a new `Shape` object.

##### `self.is_empty()`
The `is_empty` method returns `True` if `self` is empty.

##### `self.overlaps(other)`
The `overlaps` method returns `True` if `self` and `other` overlap.

#### 'Get' methods

##### Shape.get_entire_board() and Shape.get_board_perimeter()
These two methods return the entire board and the perimeter of the board, respectively.
```python
Shape.get_entire_board().draw('green')
Shape.get_board_perimeter().draw('blue')
```
<img src="board_examples/get_board.png" alt="get entire board and get board perimeter" width="40%" height="40%">

##### Shape.get_color(color) and Shape.get_column(column)
These methods return all the tiles with a specific color, and all the tiles in a specific column, respectively.

##### self.get(criterion)
```python
circle = Circle(center_tile = Tile(9, 5), radius = 3)
circle.draw('black')
circle.get(criterion = 'outside').draw('red')
circle.get(criterion = 'inside').draw('green')
```
<img src="board_examples/get_outside_inside.png" alt="get outside inside" width="40%" height="40%">

```python
circle = Circle(center_tile = Tile(9, 5), radius = 3)
circle.draw('black')
circle.get(criterion = 'above').draw('red')
circle.get(criterion = 'below').draw('green')
```
<img src="board_examples/get_above_below.png" alt="get above below" width="40%" height="40%">

```python
circle = Circle(center_tile = Tile(9, 5), radius = 3)
circle.draw('black')
circle.get(criterion = 'top').draw('red')
circle.get(criterion = 'bottom').draw('green')
```
<img src="board_examples/get_top_bottom.png" alt="get top bottom" width="40%" height="40%">

```python
circle = Circle(center_tile = Tile(9, 5), radius = 3)
circle.draw('black')
circle.get(criterion = 'corners').draw('red')
```
<img src="board_examples/get_corners.png" alt="get corners" width="40%" height="40%">

```python
circle = Circle(center_tile = Tile(9, 5), radius = 3) + Tile(-6, -4) + Tile(-5, -4) + Tile(-4, -3)
circle.draw('black')
circle.get(criterion = 'end_points').draw('red')
```
<img src="board_examples/get_end_points.png" alt="get end points" width="40%" height="40%">

##### self.boundary(self, criterion='all')
We start with the following shape:
<!--
```python
shape = Circle(center_tile = Tile(10, 5), radius = 2) + Circle(center_tile = Tile(10, 5), radius = 3) + Circle(center_tile = Tile(10, 5), radius = 4)
shape.draw('black')
```
-->
<img src="board_examples/shape_boundary_0.png" alt="shape" width="40%" height="40%">

```python
shape.boundary().draw('purple')
```
<img src="board_examples/shape_boundary_all.png" alt="shape boundary all" width="40%" height="40%">

```python
shape.boundary(criterion='outer').draw('red')
shape.boundary(criterion='inner').draw('green')
```
<img src="board_examples/shape_boundary_inner_outer.png" alt="shape boundary inner and outer" width="40%" height="40%">

##### self.extreme(direction)
```python
circle = Circle(center_tile=Tile(10, 5), radius=3)
circle.draw('black')
circle.extreme(direction='up').draw('green')
circle.extreme(direction='down_right').draw('red')
```
<img src="board_examples/shape_extreme.png" alt="shape extreme" width="40%" height="40%">

##### self.edge(criterion)
```python
circle = Circle(center_tile=Tile(10, 5), radius=3)
circle.draw('black')
circle.edge(criterion='up').draw('green')
circle.edge(criterion='right').draw('red')
```
<img src="board_examples/shape_edge.png" alt="shape edge" width="40%" height="40%">

##### self.neighbors(criterion)

```python
circle = Circle(center_tile=Tile(10, 5), radius=3)
circle.draw('black')
circle.neighbors().draw('green')
```
<img src="board_examples/shape_neighbors_all.png" alt="shape neighbors" width="40%" height="40%">

```python
circle = Circle(center_tile=Tile(10, 5), radius=3)
circle.draw('black')
circle.neighbors(criterion='right').draw('green')
circle.neighbors(criterion='left').draw('red')
```
<img src="board_examples/shape_neighbors_right_left.png" alt="shape neighbors right and left" width="40%" height="40%">

```python
circle = Circle(center_tile=Tile(10, 5), radius=3)
circle.draw('black')
circle.neighbors(criterion='above').draw('green')
circle.neighbors(criterion='below').draw('red')
```
<img src="board_examples/shape_neighbors_above_below.png" alt="shape neighbors above and below" width="40%" height="40%">

```python
circle = Circle(center_tile=Tile(10, 5), radius=3)
circle.draw('black')
circle.neighbors(criterion='outside').draw('green')
circle.neighbors(criterion='inside').draw('red')
```
<img src="board_examples/shape_neighbors_outside_inside.png" alt="shape neighbors outside and inside" width="40%" height="40%">

```python
circle = Circle(center_tile=Tile(10, 5), radius=3)
circle.draw('black')
Tile(14, 6).draw('blue')
circle.neighbors(criterion='white').draw('green')
```
<img src="board_examples/shape_neighbors_white.png" alt="shape neighbors white" width="40%" height="40%">

```python
circle = Circle(center_tile=Tile(10, 5), radius=3)
circle.draw('black')
circle.neighbors(criterion='up_right').draw('green')
```
<img src="board_examples/shape_neighbors_up_right.png" alt="shape neighbors up_right" width="40%" height="40%">

#### Draw something methods

##### self.draw(color)
Draw the tiles of self in the given color.

##### copy_paste(self, shift_direction=None, spacing=None, reference_shape=None, shift=None)
Draw a copy of self in a new location.
```python
circle1 = Circle(center_tile = Tile(4, 4), radius = 2)
circle1.draw('black')
circle2 = circle1.copy_paste(shift_direction='down_right', spacing=2)
```
<img src="board_examples/shape_copy_paste.png" alt="shape copy_paste" width="40%" height="40%">

With reference shape:
```python
circle1 = Circle(center_tile = Tile(4, 4), radius = 2)
ref_shape = Shape([Tile(11, 6), Tile(11, 7), Tile(12, 6)])
circle1.draw('black')
ref_shape.draw('purple')
circle2 = circle1.copy_paste(shift_direction='right', spacing=1, reference_shape=ref_shape)
```
<img src="board_examples/shape_copy_paste.png" alt="shape copy_paste reference_shape" width="40%" height="40%">

##### self.grid(self, shift_direction, spacing, length=None)
```python
shape = Shape([Tile(1, 4), Tile(1, 5), Tile(2, 4)])
shape.draw('black')
shape.grid(shift_direction='right', spacing=2, length=3)
```
<img src="board_examples/shape_grid.png" alt="shape grid" width="40%" height="40%">

If `length` is not specified, the maximal possible number of complete copies will be created.
```python
shape = Shape([Tile(1, 4), Tile(1, 5), Tile(2, 4)])
shape.draw('black')
shape.grid(shift_direction='right', spacing=2)
```
<img src="board_examples/shape_grid_without_length.png" alt="shape grid length not specified" width="40%" height="40%">

##### reflect(self, axis_line=None, column=None, axis_direction=None, tile_on_axis=None)
```python
blue = Tile(3, 3)
blue.draw('blue')
green = Line(start_tile=Tile(3, 4), direction='up_right', length=2)
green.draw('green')
purple = Line(start_tile=Tile(3, 5), direction='up_right', length=3)
purple.draw('purple')
shape = blue + green + purple
line = Line(start_tile=Tile(4, 7), direction='up_right')
line.draw('black')
shape.reflect(axis_line=line)
```
<img src="board_examples/shape_reflect_line.png" alt="shape reflect through axis_line" width="40%" height="40%">

```python
blue = Tile(3, 3)
blue.draw('blue')
green = Line(start_tile=Tile(3, 4), direction='up_right', length=2)
green.draw('green')
purple = Line(start_tile=Tile(3, 5), direction='up_right', length=3)
purple.draw('purple')
shape = blue + green + purple
shape.reflect(column=8)
```
<img src="board_examples/shape_reflect_column.png" alt="shape reflect through column" width="40%" height="40%">

```python
blue = Tile(3, 3)
blue.draw('blue')
green = Line(start_tile=Tile(3, 4), direction='up_right', length=2)
green.draw('green')
purple = Line(start_tile=Tile(3, 5), direction='up_right', length=3)
purple.draw('purple')
shape = blue + green + purple
tile = Tile(8, 4)
tile.draw('black')
shape.reflect(axis_direction='up_left', tile_on_axis=tile)
```
<img src="board_examples/shape_reflect_direction_and_tile.png" alt="shape reflect through direction and tile" width="40%" height="40%">


##### self.rotate(rotation, center_tile)
```python
blue = Tile(10, 2)
blue.draw('blue')
green = Tile(10, 3)
green.draw('green')
purple = Tile(10, 4)
purple.draw('purple')
center_tile = Tile(10, 6)
center_tile.draw('black')
(blue + green + purple).rotate(1, center_tile)
```
<img src="board_examples/shape_rotate.png" alt="shape rotate" width="40%" height="40%">

##### self.recolor(color_map)
In the example, we create the left shape with blue, green and purple tiles. Then we copy it and recolor, using the mapping: blue -> red, green -> orange, purple -> green, red -> black.
```python
blue = Tile(6, 2)
blue.draw('blue')
green = Tile(6, 3)
green.draw('green')
purple = Tile(6, 4)
purple.draw('purple')
shape = (blue + green + purple).copy_paste(shift_direction='right', spacing=3)
shape.recolor({'blue':'red', 'green':'orange', 'purple':'green', 'red':'black'})
```
<img src="board_examples/shape_recolor.png" alt="shape recolor" width="40%" height="40%">

##### Shape.polygon(vertices)
```python
vertices = [Tile(5, 5), Tile(8, 3), Tile(5, 7), Tile(8, 8), Tile(13, 6)]
Shape.polygon(vertices=vertices).draw('green')
Shape(vertices).draw('black')
```
<img src="board_examples/shape_vertices.png" alt="shape vertices" width="40%" height="40%">



##### 
```python
?
```
<img src="board_examples/?.png" alt="?" width="40%" height="40%">

