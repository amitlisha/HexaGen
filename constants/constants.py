WIDTH = 18 # the board's width
HEIGHT = 10 # the board's height

COLORS = ['white', 'black', 'yellow', 'green', 'red', 'blue', 'purple', 'orange'] # the supported colors

COLORS_RGB_INT = {
  'white': [255, 255, 255],
  'black': [0, 0, 0],
  'yellow': [255, 255, 0],
  'green': [0, 255, 0],
  'red': [255, 0, 0],
  'blue': [0, 0, 255],
  'purple': [221, 160, 221],
  'orange': [255, 165, 0],
}

DIRECTIONS = {'up': (0, -1, 1), 'down': (0, 1, -1), 'down_right': (1, 0, -1), 'up_left': (-1, 0, 1),
              'down_left': (-1, 1, 0), 'up_right': (1, -1, 0)} # do not change

