# Hexagons

## Purpose
The purpose of this project is to allow translation of instructions given in natural language into code. The instructions describe drawings on a hexagonal tiled board. For example, the instruction:

>draw a red flower with a yellow center, centered at the seventh column and fifth row

can be translated into the following code: 
```python
center = Tile(column=7, row=5)
center.draw(color='yellow')
center.neighbors().draw(color='red')
```
This code uses a `Tile` object that represents a hexagonal tile on the board, the `draw` method that is used to color objects on the board, and the `neighbors` method which returns the six neighboring tiles of the current tile.

The code generates the following image:

<img src="docs/board_examples/red_flower_yellow_center.png" alt="red flower with yellow center" width="40%" height="40%">

## Requirements

Before you get started, make sure you have the following requirements installed:

- Python 3.x
- NumPy
- SciPy

## Usage
See the file [Usage.md](docs/Usage.md) for a complete usage guide.

## License
TODO

## Acknowledgments
TODO
