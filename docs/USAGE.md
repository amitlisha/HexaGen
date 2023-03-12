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

## Creating Tiles
To create a tile in Hexagons, use the Tile class. To paint it in a disired color, use the `draw` method. The `Tile` class requires two parameters: `column` and `row`. `column` is numbered from 1 (leftmost column) to 18 (rightmost column), while `row` is numbered from 1 (top row) to 10 (bottom row). If you use a negative value for column or row, the counting will start from the rightmost column or bottom row, respectively.
```python
Tile(column=1, row=1).draw('red')
Tile(column=1, row=-1).draw('blue')
Tile(column=-1, row=1).draw('green')
Tile(column=-1, row=-1).draw('orange')
```
<img src="board_examples/corners.png" alt="corners" width="40%" height="40%">

## Shape Class Methods
A shape in Hexagons is any set of tiles on the board, including the empty set and a single tile.
To create a shape in Hexagons, use the `Shape` class, which requires a single parameter: `tiles`. `tiles` is a list of Tile objects, that specifies the tiles composing the shape.
```python
shape = Shape(tiles=[Tile(9, 5), Tile(10, 5), Tile(9, 6)])
shape.draw('purple')
```
<img src="board_examples/simple_purple_shape.png" alt="simple purple shape" width="40%" height="40%">

The `Shape` class has three special subclasses that we will now describe: `Circle`, `Line` and `Triangle`.

### Circle
To create a circle in Hexagons, use the `Circle` class, which requires two parameters: `center_tile` and `radius`. `center_tile` is a tile object that specifies the center tile of the circle. `radius` is an integer that specifies the radius of the circle.  If you do not specify a `radius` value, it defaults to `1`.
```python
circle = Circle(center_tile = Tile(9, 5), radius = 3)
circle.draw('black')
```
<img src="board_examples/black_circle.png" alt="black circle" width="40%" height="40%">

### Line
To create a line in Hexagons, use the `Line` class.
There are several to instantiate a new `Line` object:

#### Using `start_tile` and `end_tile`
Specify `start_tile` and `end_tile` as `Tile` objects to define the start and end points of the line.
```python
line = Line(start_tile=Tile(3, 2), end_tile=Tile(-3, -3))
line.draw('blue')
```
<img src="board_examples/line_start_end.png" alt="line start end" width="40%" height="40%">

#### Using `start_tile`, `direction` and `length`
Use `direction` to specify the direction of the line, choosing from 'up', 'up_right', 'up_left', 'down', 'down_right', or 'down_left', and use `length` to specify the length of the line.
```python
line = Line(start_tile=Tile(3, 8), direction='up_right', length=5)
line.draw('blue')
```
<img src="board_examples/line_start_direction_length.png" alt="line start direction end" width="40%" height="40%">

#### Using `start_tile` and `direction`
If `length` is not specified, the line will extend until it reaches the edge of the board.
```python
line = Line(start_tile=Tile(3, 8), direction='up_right')
line.draw('blue')
```
<img src="board_examples/line_start_direction.png" alt="line start direction" width="40%" height="40%">

#### Using `start_tile`, `direction` and `end_tiles`
Specify a `Shape` object `end_tiles` to stop the line when it reaches any tile belonging to the shape.
```python
circle = Circle(center_tile=Tile(15, 8), radius=2)
circle.draw('red')
line = Line(start_tile=Tile(1, 1), direction='down_right', end_tiles=circle)
line.draw('blue')
```
<img src="board_examples/line_end_tiles.png" alt="line end tiles" width="40%" height="40%">

#### Additional: `include_start_tile` and `include_end_tile` flags
By default, `include_start_tile` and `include_end_tile` are both set to `True`, but you can set them to `False` to omit the starting or ending tile from the line, respectively.
```python
line = Line(start_tile=Tile(9, 1), end_tile=Tile(9, -1), include_start_tile=False, include_end_tile=False)
line.draw('blue')
```
<img src="board_examples/line_dont_include.png" alt="line dont include" width="40%" height="40%">

#### `Shape` class methods

The `Shape` class has many useful methods. We will now describe them in details.
Note that all these methods can be used on objects from any of the subclasses, and also on `Tile` objects.

##### `get` method
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

```python
?```
<img src="board_examples/?.png" alt="?" width="40%" height="40%">
