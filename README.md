# Hexagen

This project is part of the larger `Hexagons` project developed at the [ONLP lab](https://nlp.biu.ac.il/~rtsarfaty/onlp).
You can read more about the project [here](https://onlplab.github.io/Hexagons/).

The purpose of this project is to allow translation of instructions given in natural language into code. The instructions describe drawings on a hexagonal tiled board. 

For example, the instruction:

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
See our [usage guide](docs/USAGE.md).

## Reading Tasks
TODO

## Examples
TODO

## GPT
TODO

## License
TODO

## Acknowledgments
I would like to express my gratitude to Professor Reut Tsarfaty, head of the ONLP lab, for her valuable guidance and support throughout this project. Her expertise and insights have been invaluable.

I would also like to thank my colleagues from the ONLP lab, Dr. Royi Lachmi and Avshalom Manevich, for their collaboration and teamwork. Working with them has been a great pleasure, and I am grateful for their contributions to this project.
