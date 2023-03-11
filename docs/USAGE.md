# Usage Guide
Welcome to the usage guide for Hexagons. This guide will provide you with detailed instructions on how to use the various features and functions of our code, including code examples.

## Basic Example

```python
from hexagons_classes import HexagonsGame, Tile, Shape, Line, Circle, Triangle

HexagonsGame.start()

tile = Tile(5,7)
tile.draw('blue')

HexagonsGame.plot()
```

![example](example_boards/01_single_blue_hex.png)
