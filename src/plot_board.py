# Plot a hexagon board / boards

from matplotlib.cm import get_cmap
from matplotlib.collections import PatchCollection
from matplotlib.colors import ListedColormap
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numbers
import numpy as np
from typing import List, Union

from constants.constants import COLORS, COLORS_RGB_INT

MAX_INPUT_LEN = 512
MAX_OUTPUT_LEN = 512

hexa_cmap = ListedColormap([[val / 255. for val in COLORS_RGB_INT[color]] for color in COLORS])
gray_cmap = get_cmap('gray')

def plot_boards(boards, fig_size=(5, 5), width=18, height=10, max_in_row=6, edge_color='k', color_map='hexa', titles = None,
                show=True):
  '''Plot a hexagon board / boards

  'boards' should be any one of:
  - list of length 180 / list of such lists
  - np.array with shape [180] / list of such arrays
  - np.array with shape [W,H] / list of such arrays

  'titles' is optional, should be a list of string, containing a title for each board
  '''

  if not isinstance(boards, list):
    boards = [boards]
  if isinstance(boards[0], numbers.Number):
    boards = [boards]
  boards = [np.array(_) for _ in boards]

  num_boards = len(boards)
  num_rows = int(np.ceil(num_boards / max_in_row))
  num_cols = np.min([num_boards, max_in_row])
  fig = plt.figure(figsize=[fig_size[0] * num_cols, fig_size[1] * num_rows])
  axes = fig.subplots(num_rows, num_cols)
  if num_rows > 1:
    axes = [_ for ls in axes for _ in ls]
    unused_axes = axes[num_boards:]
    for ax in unused_axes:
      ax.axis('off')
  if num_boards == 1:
    axes = [axes]
  # remove the x and y ticks and add subplot titles
  for i in range(num_boards):
    axes[i].set_xticks([])
    axes[i].set_yticks([])
    if titles is None:
      axes[i].set_title(str(i + 1))
    else:
      axes[i].set_title(titles[i])

  for i in range(num_boards):

    board = boards[i]

    if not isinstance(board, list) and len(board.shape) == 2:
      H = board.shape[0]
      W = board.shape[1]
      board = board.reshape(-1)
      print('reshaped board from 2 dim to 1 dim')
    else:
      board = board.reshape(height, width)
      board = board.transpose()
      board = board.reshape(-1)

    create_hex_grid(fig_size,
                    nx=height,
                    ny=width,
                    rotate_deg=90, edge_color=edge_color,
                    do_plot=True, face_color=board, align_to_origin=False,
                    ax=axes[i], color_map=color_map)
  fig.tight_layout(h_pad=0, w_pad=2)

  if show:
    plt.show()

  return fig

def create_hex_grid(fig_size,
                    color_map='hexa',
                    nx: int = 4,
                    ny: int = 5,
                    min_diam: float = 1.,
                    n: int = 0,
                    align_to_origin: bool = True,
                    face_color: Union[List[float], str] = None,
                    edge_color: Union[List[float], str] = None,
                    plotting_gap: float = 0.,
                    crop_circ: float = 0.,
                    do_plot: bool = False,
                    rotate_deg: float = 0.,
                    keep_x_sym: bool = True,
                    ax: plt.Axes = None) -> (np.ndarray, plt.Axes):
  """
  called by plot_board
  Creates and prints hexagonal lattices.
  :param nx: Number of horizontal hexagons in rectangular grid, [nx * ny]
  :param ny: Number of vertical hexagons in rectangular grid, [nx * ny]
  :param min_diam: Minimal diameter of each hexagon.
  :param n: Alternative way to create rectangular grid. The final grid might have less hexagons
  :param align_to_origin: Shift the grid s.t. the central tile will center at the origin
  :param face_color: Provide RGB triplet, valid abbreviation (e.g. 'k') or RGB+alpha
  :param edge_color: Provide RGB triplet, valid abbreviation (e.g. 'k') or RGB+alpha
  :param plotting_gap: Gap between the edges of adjacent tiles, in fraction of min_diam
  :param crop_circ: Disabled if 0. If >0 a circle of central tiles will be kept, with radius r=crop_circ
  :param do_plot: Add the hexagon to an axes. If h_ax not provided a new figure will be opened.
  :param rotate_deg: Rotate the grid around the center of the central tile, by rotate_deg degrees
  :param keep_x_sym: NOT YET IMPLEMENTED
  :param h_ax: Handle to axes. If provided the grid will be added to it, if not a new figure will be opened.
  :return:
  """
  coord_x, coord_y = make_grid(nx, ny, min_diam, n, crop_circ, rotate_deg, align_to_origin)
  if do_plot:
    plot_single_lattice(fig_size, coord_x, coord_y, face_color, edge_color, min_diam, plotting_gap, rotate_deg,
                        color_map, ax)

def make_grid(nx, ny, min_diam, n, crop_circ, rotate_deg, align_to_origin) -> (np.ndarray, np.ndarray):
  """
  called by create_hex_grid
  Computes the coordinates of the hexagon centers, given the size rotation and layout specifications
  :return:
  """
  # print('start make_grid')
  # ratio = (2. / 3.) * np.sin(np.radians(60))
  ratio = np.sqrt(3) / 2.
  if n > 0:  # n variable overwrites (nx, ny) in case all three were provided
    ny = int(np.sqrt(n / ratio))
    nx = n // ny

  coord_x, coord_y = np.meshgrid(np.arange(nx), np.arange(ny), sparse=False, indexing='xy')
  coord_y = coord_y * ratio
  coord_x = coord_x.astype(float)
  coord_x[1::2, :] += 0.5
  coord_x = coord_x.reshape(-1, 1)
  coord_y = coord_y.reshape(-1, 1)

  coord_x *= min_diam  # Scale to requested size
  coord_y = coord_y.astype(float) * min_diam

  mid_x = (np.ceil(nx / 2) - 1) + 0.5 * (
      np.ceil(ny / 2) % 2 == 0)  # Pick center of some hexagon as origin for rotation or crop...
  mid_y = (np.ceil(ny / 2) - 1) * ratio  # np.median() averages center 2 values for even arrays :\
  mid_x *= min_diam
  mid_y *= min_diam

  # mid_x = (nx // 2 - (nx % 2 == 1)) * min_diam + 0.5 * (ny % 2 == 1)
  # mid_y = (ny // 2 - (ny % 2)) * min_diam * ratio

  if crop_circ > 0:
    rad = ((coord_x - mid_x) ** 2 + (coord_y - mid_y) ** 2) ** 0.5
    coord_x = coord_x[rad.flatten() <= crop_circ, :]
    coord_y = coord_y[rad.flatten() <= crop_circ, :]

  if not np.isclose(rotate_deg, 0):  # Check if rotation is not 0, with tolerance due to float format
    # Clockwise, 2D rotation matrix
    RotMatrix = np.array([[np.cos(np.deg2rad(rotate_deg)), np.sin(np.deg2rad(rotate_deg))],
                          [-np.sin(np.deg2rad(rotate_deg)), np.cos(np.deg2rad(rotate_deg))]])
    rot_locs = np.hstack((coord_x - mid_x, coord_y - mid_y)) @ RotMatrix.T
    coord_x, coord_y = np.hsplit(rot_locs + np.array([mid_x, mid_y]), 2)

  if align_to_origin:
    coord_x -= mid_x
    coord_y -= mid_y

  return coord_x, coord_y


def plot_single_lattice(fig_size, coord_x, coord_y, face_color, edge_color, min_diam, plotting_gap, rotate_deg,
                        color_map, h_ax=None):
  """
  called by create_hex_grid
  Adds a single lattice to the axes canvas. Multiple calls can be made to overlay few lattices.
  :return:
  """
  if face_color is None:
    face_color = (1, 1, 1, 0)  # Make the face transparent
  if edge_color is None:
    edge_color = 'w'

  if h_ax is None:
    h_fig = plt.figure(figsize=fig_size)
    h_ax = h_fig.add_axes([0.05, 0.05, 0.9, 0.9])

  patches = []
  for curr_x, curr_y in zip(coord_x, coord_y):
    polygon = mpatches.RegularPolygon((curr_x, curr_y), numVertices=6,
                                      radius=min_diam / np.sqrt(3) * (1 - plotting_gap),
                                      orientation=np.deg2rad(-rotate_deg))
    patches.append(polygon)
  if color_map == 'hexa':
    collection = PatchCollection(patches, edgecolor=edge_color, cmap=hexa_cmap)
    collection.set_array(face_color)
    collection.set_clim([0, hexa_cmap.N])
  elif color_map == 'gray':
    collection = PatchCollection(patches, edgecolor=edge_color, cmap=gray_cmap)
    collection.set_array(face_color)
  h_ax.add_collection(collection)

  h_ax.set_aspect('equal')
  h_ax.axis([coord_x.min() - 2 * min_diam, coord_x.max() + 2 * min_diam, coord_y.min() - 2 * min_diam,
             coord_y.max() + 2 * min_diam])

  return h_ax
