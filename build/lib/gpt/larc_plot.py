"""LARC rectangular grid plotting utilities."""

import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from typing import List, Optional


# ARC color palette (10 colors: 0-9)
ARC_COLORS = [
    "#000000",  # 0: black
    "#0074D9",  # 1: blue
    "#FF4136",  # 2: red
    "#2ECC40",  # 3: green
    "#FFDC00",  # 4: yellow
    "#AAAAAA",  # 5: grey
    "#F012BE",  # 6: fuchsia
    "#FF851B",  # 7: orange
    "#7FDBFF",  # 8: teal
    "#870C25",  # 9: brown
]


def plot_arc_grid(
    grid: List[int],
    width: int,
    height: int,
    ax=None,
    title: str = "",
) -> None:
    """Plot a single ARC-style rectangular grid.

    Args:
        grid: Flattened 1D list of color indices
        width: Grid width
        height: Grid height
        ax: Matplotlib axis to plot on (creates new if None)
        title: Optional title for the plot
    """
    if ax is None:
        _, ax = plt.subplots(1, 1, figsize=(width * 0.5, height * 0.5))

    # Reshape flat grid to 2D
    grid_2d = np.array(grid).reshape(height, width)

    # Create color array
    color_grid = np.zeros((height, width, 3))
    for i in range(height):
        for j in range(width):
            color_idx = grid_2d[i, j]
            if 0 <= color_idx < len(ARC_COLORS):
                hex_color = ARC_COLORS[color_idx]
                # Convert hex to RGB
                rgb = tuple(int(hex_color[i : i + 2], 16) / 255.0 for i in (1, 3, 5))
                color_grid[i, j] = rgb

    ax.imshow(color_grid, interpolation="nearest")
    ax.grid(True, which="both", color="lightgrey", linewidth=0.5)
    ax.set_xticks(np.arange(-0.5, width, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, height, 1), minor=True)
    ax.set_xticks(np.arange(0, width, 1))
    ax.set_yticks(np.arange(0, height, 1))
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.set_title(title)


def save_larc_plot(
    board_state: List[int],
    gold_board: Optional[List[int]],
    out: Path,
    width: int,
    height: int,
) -> None:
    """Plot LARC board vs. gold and save PNG.

    Args:
        board_state: Current board state (flattened)
        gold_board: Gold board state (flattened), or None
        out: Output path for plot
        width: Board width
        height: Board height
    """
    if gold_board is None:
        # Single plot
        fig, ax = plt.subplots(1, 1, figsize=(width * 0.5, height * 0.5))
        plot_arc_grid(board_state, width, height, ax=ax, title="Predicted")
    else:
        # Side-by-side comparison with difference
        fig, axes = plt.subplots(1, 3, figsize=(width * 1.5, height * 0.5))

        plot_arc_grid(board_state, width, height, ax=axes[0], title="Predicted")
        plot_arc_grid(gold_board, width, height, ax=axes[1], title="Gold")

        # Compute difference (1 where different, 0 where same)
        diff = [0 if x == y else 1 for x, y in zip(board_state, gold_board)]
        # For diff visualization, use binary colors
        diff_grid = np.array(diff).reshape(height, width)
        axes[2].imshow(diff_grid, cmap="RdYlGn_r", vmin=0, vmax=1, interpolation="nearest")
        axes[2].grid(True, which="both", color="lightgrey", linewidth=0.5)
        axes[2].set_xticks(np.arange(-0.5, width, 1), minor=True)
        axes[2].set_yticks(np.arange(-0.5, height, 1), minor=True)
        axes[2].set_xticks(np.arange(0, width, 1))
        axes[2].set_yticks(np.arange(0, height, 1))
        axes[2].set_xticklabels([])
        axes[2].set_yticklabels([])
        axes[2].set_title("Difference")

    plt.tight_layout()
    plt.savefig(out, dpi=100, bbox_inches="tight")
    plt.close(fig)
