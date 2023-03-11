# Usage Guide
Welcome to the usage guide for Hexagons. This guide will provide you with detailed instructions on how to use the various features and functions of our code, including code examples.

## Basic Example: Single Blue Hexagon
This is the code 'frame':
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
![example](board_examples/single_blue_hex.png)
From now on we omit the code frame.
## Creating Tiles
```python
Tile(1,1).draw('red')
Tile(1,-1).draw('blue')
Tile(-1,1).draw('green')
Tile(-1,-1).draw('orange')
```
![example](board_examples/corners.png)
## Circle
```python
circle = Circle(center_tile = Tile(9, 5), radius = 3)
circle.draw('black')
```
![example](board_examples/black_circle.png)
## Shape Class Methods
### Get method
```python
circle = Circle(center_tile = Tile(9, 5), radius = 3)
circle.draw('black')
circle.get(criterion = 'outside').draw('red')
circle.get(criterion = 'inside').draw('green')
```
![example](board_examples/get_outside_inside.png)
```python
circle = Circle(center_tile = Tile(9, 5), radius = 3)
circle.draw('black')
circle.get(criterion = 'above').draw('red')
circle.get(criterion = 'below').draw('green')
```
![example](board_examples/get_above_below)
```python
circle = Circle(center_tile = Tile(9, 5), radius = 3)
circle.draw('black')
circle.get(criterion = 'top').draw('red')
circle.get(criterion = 'bottom').draw('green')
```
![example](board_examples/get_top_bottom)
```python
circle = Circle(center_tile = Tile(9, 5), radius = 3)
circle.draw('black')
circle.get(criterion = 'corners').draw('red')
```
![example](board_examples/get_corners)
```python
circle = Circle(center_tile = Tile(9, 5), radius = 3) + Tile(-6, -4) + Tile(-5, -4) + Tile(-4, -3)
circle.draw('black')
circle.get(criterion = 'end_points').draw('red')
```
![example](board_examples/get_end_points)

```python
?```
![example](board_examples/?)
