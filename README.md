# HexaGen

## Description
The HexaGen project is a component of the larger Hexagons project developed by the [ONLP lab](https://nlp.biu.ac.il/~rtsarfaty/onlp).
For more information about the project, please visit [here](https://onlplab.github.io/Hexagons/).

As a part of the Hexagons project, the Hexagons dataset was collected. 
This dataset consists of 4177 visually grounded instructions that occur naturally and contain a variety of abstraction levels and types. 
The instructions are written in natural language and describe drawings on a hexagonal tiled board.

The purpose of the HexaGen project is to provide a formalism that enables the expression of natural language instructions in executable Python code while maintaining the computational ideas present in the NL utterances. The formalism allows for accurate expression of these ideas using Python code, ensuring that the computational structure of the original NL instructions is preserved.

For instance, the instruction:
>"Draw a red flower with a yellow center, centered at the seventh column and fifth row"

Can be expressed by the following code: 
```python
center = Tile(row=5, column=7)
center.draw(color='yellow')
center.neighbors().draw(color='red')
```
This code uses a `Tile` object that represents a hexagonal tile on the board, the `draw` method that is used to color objects on the board, and the `neighbors` method which returns the six neighboring tiles of the current tile.

The code generates the following image:

<img src="docs/board_examples/red_flower_yellow_center.png" alt="red flower with yellow center" width="40%" height="40%">

## Philosophy
Our approach in developing the formalism was rooted in the analysis of the natural language instructions in the dataset. 
We focused on identifying the computational concepts expressed by users in these instructions and then formalizing them in a way that would allow for their expression in a concise and compact manner. 
We aimed to create a user-friendly formalism by prioritizing code that is easy to use.
In addition, we made an effort to ensure that the code was robust enough to handle potential errors related to data type mismatches between function parameters and their respective arguments.

## Requirements

Before you get started, make sure you have the following requirements installed:

- Python 3.x
- NumPy
- SciPy

## Installation

Clone the repository and install the package and its dependencies with `pip`:

```bash
pip install -e .
```

## Usage of the `hexagen` module
The `hexagen` package provides the main classes and constants for drawing on the
board. After installing the package you can simply write:

```python
from hexagen import Game, Tile, Shape, Line, Circle, Triangle
from hexagen import COLORS, WIDTH, HEIGHT, DIRECTIONS
```

To learn how to use these building blocks, consult our
[usage guide](docs/USAGE.md), which provides comprehensive instructions and
numerous code examples to help you get started.

## The Hexagons dataset
The dataset for Hexagons is stored in the [data](data/) folder as jsonl files. 
You can read the drawing procedures from these files using the methods provided in the [utils.reading_tasks](utils/reading_tasks.py) module.

## Gold files and parsing
The [gold](gold/) folder contains the so called gold files, which provide hand-crafted parsing of drawing procedures from the Hexagons dataset. 
Such a file includes the NL instructions, and a hand-crafted expression of these instructions in Python code, utilizing our formalism.

The tasks for the gold files are all taken from the 'train' group.
We randomly selected a single image from each category to create a set of tasks we call 'batch 3'.
We then parsed some of the drawing procedures in 'batch 3'.
To get more information about the images and drawing procedures in 'batch 3', 
and to see the parsing status of each drawing procedure, you can refer to 
 [gold parsing batch 3](https://docs.google.com/spreadsheets/d/1l89uCMCstFsVayHpcf_xUxGgsJrxM_TwE9AsUOrGgaw/edit?usp=sharing).

To facilitate parsing new instructions, the script [utils.gen_empty_gold](utils/gen_empty_gold.py) can be used to automatically generate starter files. 
When executed, it prompts the user to enter a task index and then creates a new file containing the instructions for that task (taken fram the Hexagons dataset), 
as well as any necessary imports and other commands. After the file is generated, the only remaining step is to fill in the parsing code.

## GPT
TODO

## License
This project is licensed under the [MIT License](LICENSE).

## Acknowledgments
I would like to express my gratitude to Professor Reut Tsarfaty, head of the ONLP lab, for her valuable guidance and support throughout this project. Her expertise and insights have been invaluable.

I would also like to thank my colleagues from the ONLP lab, Dr. Royi Lachmi and Avshalom Manevich, for their collaboration and teamwork. Working with them has been a great pleasure, and I am grateful for their contributions to this project.
