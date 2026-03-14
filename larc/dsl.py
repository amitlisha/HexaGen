"""
ARC DSL — LLM-ready version.

This module provides grid and patch manipulation primitives for solving ARC tasks.
All names are exported flat at module level (see bottom of file) so that
``from dsl import *`` or namespace-injection via ``dir()`` works as expected.

The classes (GridOps, PatchOps, ColorOps, SearchOps, GeoOps) are used purely as
internal namespaces; LLM-generated code should call the module-level aliases.

─── Core Type Conventions ──────────────────────────────────────────────────────
  Grid     = list[list[int]]
             A 2-D grid of color integers, accessed as grid[row][col].
             Rows are 0-indexed top-to-bottom; columns 0-indexed left-to-right.

  Object   = dict[tuple[int, int], int]
             A mapping from (row, col) -> color for colored cells.
             Access a cell's color with obj[(r, c)] or obj.get((r, c)).

  Indices  = set[tuple[int, int]]
             A set of (row, col) positions with no color information.

  Patch    = Object | Indices
             Either an Object (dict) or Indices (set) — any collection of positions.

  Element  = Grid | Object
             Anything that contains color values (grid or object).

  Piece    = Grid | Patch
             Anything with spatial extent (grid, object, or plain indices).

  Color    = int
             Integer 0–9 representing a color (0 = background by convention).

  Index    = tuple[int, int]
             A single (row, col) grid coordinate.

─── Color Mapping ──────────────────────────────────────────────────────────────
  0=black  1=blue   2=red    3=green  4=yellow
  5=grey   6=pink   7=orange 8=cyan   9=maroon
  Background is typically the most common color in a grid (often 0).
"""

# ──────────────────────────────────────────────────────────────────────────────
# Private helpers (not exported)
# ──────────────────────────────────────────────────────────────────────────────

def _to_indices(patch):
    """Strip colors from an Object (dict) → set of keys; pass-through if already a set."""
    if isinstance(patch, dict):
        return set(patch.keys())
    return patch


def _boundary(patch, side):
    """Extreme row/col of a patch. side: 'top', 'bottom', 'left', 'right'."""
    idxs = _to_indices(patch)
    if side == 'top':    return min(i for i, j in idxs)
    if side == 'bottom': return max(i for i, j in idxs)
    if side == 'left':   return min(j for i, j in idxs)
    if side == 'right':  return max(j for i, j in idxs)


# ──────────────────────────────────────────────────────────────────────────────
# Shared dimension functions — work on Grid or Patch (Piece)
# ──────────────────────────────────────────────────────────────────────────────

def height(piece):
    """Grid row count, or bounding-box height of a patch (0 if empty)."""
    if isinstance(piece, list):
        return len(piece)
    if len(piece) == 0:
        return 0
    return _boundary(piece, 'bottom') - _boundary(piece, 'top') + 1


def width(piece):
    """Grid column count, or bounding-box width of a patch (0 if empty)."""
    if isinstance(piece, list):
        return len(piece[0]) if piece else 0
    if len(piece) == 0:
        return 0
    return _boundary(piece, 'right') - _boundary(piece, 'left') + 1


def dimensions(piece):
    """Return (height, width) for a grid or patch bounding box."""
    return (height(piece), width(piece))


def is_portrait(piece):
    """True iff height(piece) > width(piece)."""
    return height(piece) > width(piece)


def is_square(piece):
    """
    True iff:
    - Grid: row count == column count.
    - Patch: bounding box is square AND all bbox cells are occupied.
    """
    if isinstance(piece, list):
        return len(piece) == len(piece[0]) if piece else True
    return height(piece) == width(piece) and height(piece) * width(piece) == len(piece)


def mirror(piece, axis='horizontal'):
    """
    Reflect a grid or patch across the specified axis.

    axis (refers to the axis *of reflection*, not the direction of motion):
      'horizontal'     — flip top-to-bottom (reflects across a horizontal line)
      'vertical'       — flip left-to-right (reflects across a vertical line)
      'diagonal'       — reflect across the main diagonal (top-left → bottom-right)
      'counterdiagonal'— reflect across the anti-diagonal (top-right → bottom-left)

    For patches, reflection is relative to the patch's own bounding box.
    """
    if axis == 'horizontal':
        if isinstance(piece, list):
            return piece[::-1]
        d = _boundary(piece, 'top') + _boundary(piece, 'bottom')
        if isinstance(piece, dict):
            return {(d - i, j): v for (i, j), v in piece.items()}
        return {(d - i, j) for i, j in piece}

    elif axis == 'vertical':
        if isinstance(piece, list):
            return [row[::-1] for row in piece]
        d = _boundary(piece, 'left') + _boundary(piece, 'right')
        if isinstance(piece, dict):
            return {(i, d - j): v for (i, j), v in piece.items()}
        return {(i, d - j) for i, j in piece}

    elif axis == 'diagonal':
        if isinstance(piece, list):
            return [list(row) for row in zip(*piece)]
        a, b = _boundary(piece, 'top'), _boundary(piece, 'left')
        if isinstance(piece, dict):
            return {(j - b + a, i - a + b): v for (i, j), v in piece.items()}
        return {(j - b + a, i - a + b) for i, j in piece}

    elif axis == 'counterdiagonal':
        if isinstance(piece, list):
            return [list(row) for row in zip(*(r[::-1] for r in piece[::-1]))]
        return mirror(mirror(mirror(piece, 'vertical'), 'diagonal'), 'vertical')

    return piece


def upscale(element, factor):
    """
    Scale a grid or colored Object by `factor` in both dimensions.

    Grid:   each cell becomes a factor×factor block.
    Object: each cell (row,col)->color becomes factor² cells covering
            the factor×factor block starting at (i*factor, j*factor)
            (positions are relative to the object's upper-left corner).
    """
    if isinstance(element, list):
        g = []
        for row in element:
            upscaled_row = [v for v in row for _ in range(factor)]
            for _ in range(factor):
                g.append(list(upscaled_row))
        return g
    else:
        if len(element) == 0:
            return {}
        di_inv = _boundary(element, 'top')
        dj_inv = _boundary(element, 'left')
        normed = PatchOps.translate(element, (-di_inv, -dj_inv))
        o = {}
        for (i, j), value in normed.items():
            for io in range(factor):
                for jo in range(factor):
                    o[(i * factor + io, j * factor + jo)] = value
        return PatchOps.translate(o, (di_inv, dj_inv))


def upscale_along_axis(grid, factor, axis='horizontal'):
    """
    Stretch a grid along one axis only.

    axis='horizontal': each column is repeated `factor` times (wider grid).
    axis='vertical':   each row    is repeated `factor` times (taller grid).
    """
    if axis == 'horizontal':
        return [
            [v for v in row for _ in range(factor)]
            for row in grid
        ]
    else:
        g = []
        for row in grid:
            for _ in range(factor):
                g.append(list(row))
        return g


# ──────────────────────────────────────────────────────────────────────────────
# class GridOps — operations whose primary output or subject is a Grid
# ──────────────────────────────────────────────────────────────────────────────

class GridOps:
    """
    Operations on Grids (list[list[int]]). Accessed as grid[row][col].
    Methods here accept a Grid as their first or primary argument.
    """

    @staticmethod
    def create_grid(color, size):
        """
        Create a uniform grid filled with `color`.
        size = (num_rows, num_cols).
        """
        rows, cols = size
        return [[color for _ in range(cols)] for _ in range(rows)]

    @staticmethod
    def color_at(grid, location):
        """Return the color at (row, col), or None if out of bounds."""
        i, j = location
        if 0 <= i < len(grid) and 0 <= j < len(grid[0]):
            return grid[i][j]
        return None

    @staticmethod
    def crop(grid, start, size):
        """
        Extract a rectangular subgrid.
        start = (row, col) top-left corner; size = (height, width).
        """
        r0, c0 = start
        h, w = size
        return [row[c0:c0 + w] for row in grid[r0:r0 + h]]

    @staticmethod
    def all_indices(grid):
        """Return all (row, col) positions in the grid as Indices."""
        return {
            (i, j) for i in range(len(grid)) for j in range(len(grid[0]))
        }

    @staticmethod
    def grid_to_object(grid):
        """Convert the entire grid into an Object (dict mapping (row,col)->color)."""
        return {
            (i, j): v
            for i, row in enumerate(grid)
            for j, v in enumerate(row)
        }

    @staticmethod
    def extract_subgrid(patch, grid):
        """Return the smallest subgrid that contains the patch's bounding box."""
        return GridOps.crop(
            grid,
            (_boundary(patch, 'top'), _boundary(patch, 'left')),
            dimensions(patch),
        )

    @staticmethod
    def fill(grid, color, patch, background_only=False):
        """
        Set all patch positions to `color`.
        background_only=True: only overwrites cells currently equal to
        dominant_color(grid).
        """
        h, w = len(grid), len(grid[0])
        bg = ColorOps.dominant_color(grid) if background_only else None
        g = [list(row) for row in grid]
        for i, j in _to_indices(patch):
            if 0 <= i < h and 0 <= j < w:
                if bg is None or g[i][j] == bg:
                    g[i][j] = color
        return g

    @staticmethod
    def paint(grid, obj, background_only=False):
        """
        Stamp an Object (with its colors) onto the grid.
        background_only=True: only overwrites background-colored cells.
        """
        h, w = len(grid), len(grid[0])
        bg = ColorOps.dominant_color(grid) if background_only else None
        g = [list(row) for row in grid]
        for (i, j), color in obj.items():
            if 0 <= i < h and 0 <= j < w:
                if bg is None or g[i][j] == bg:
                    g[i][j] = color
        return g

    @staticmethod
    def erase(grid, patch):
        """Fill patch positions with the dominant (background) color."""
        return GridOps.fill(grid, ColorOps.dominant_color(grid), _to_indices(patch))

    @staticmethod
    def move_object(grid, obj, offset):
        """Erase `obj` from `grid` then repaint it shifted by `offset`."""
        return GridOps.paint(GridOps.erase(grid, obj), PatchOps.translate(obj, offset))

    @staticmethod
    def replace_color(grid, old_color, new_color):
        """Replace every occurrence of `old_color` with `new_color`."""
        return [
            [new_color if v == old_color else v for v in row]
            for row in grid
        ]

    @staticmethod
    def swap_colors(grid, color_a, color_b):
        """Swap `color_a` and `color_b` everywhere in the grid."""
        swap = {color_a: color_b, color_b: color_a}
        return [[swap.get(v, v) for v in row] for row in grid]

    @staticmethod
    def cellwise_combine(a, b, fallback_color):
        """
        Compare two same-sized grids cell by cell.
        Keep the color where both grids agree; use `fallback_color` where they differ.
        """
        return [
            [va if va == vb else fallback_color for va, vb in zip(ra, rb)]
            for ra, rb in zip(a, b)
        ]

    @staticmethod
    def rotate(grid, angle=90):
        """
        Rotate grid clockwise. angle must be 90, 180, or 270.
        Other values return the grid unchanged.
        """
        if angle == 90:
            return [list(row) for row in zip(*grid[::-1])]
        elif angle == 180:
            return [list(row[::-1]) for row in grid[::-1]]
        elif angle == 270:
            return [list(row) for row in zip(*grid[::-1])][::-1]
        return grid

    @staticmethod
    def concatenate(a, b, axis='horizontal'):
        """
        Join two grids.
        axis='horizontal': side by side (same height required).
        axis='vertical':   stacked top-to-bottom (same width required).
        """
        if axis == 'horizontal':
            return [ra + rb for ra, rb in zip(a, b)]
        else:
            return a + b

    @staticmethod
    def split_grid(grid, parts, axis='horizontal'):
        """
        Split grid into `parts` equal pieces.
        axis='horizontal': left-to-right splits.
        axis='vertical':   top-to-bottom splits.
        Returns a list of sub-grids.
        Note: if grid size is not divisible by parts, a 1-cell separator is assumed
        between parts (implementation skips 1 row/col per boundary).
        """
        if axis == 'horizontal':
            h, w = len(grid), len(grid[0]) // parts
            offset = int(len(grid[0]) % parts != 0)
            return [
                GridOps.crop(grid, (0, w * i + i * offset), (h, w))
                for i in range(parts)
            ]
        else:
            h, w = len(grid) // parts, len(grid[0])
            offset = int(len(grid) % parts != 0)
            return [
                GridOps.crop(grid, (h * i + i * offset, 0), (h, w))
                for i in range(parts)
            ]

    @staticmethod
    def get_half(grid, side='top'):
        """
        Return one half of the grid.
        side: 'top', 'bottom', 'left', 'right'.
        """
        if side == 'top':
            return grid[:len(grid) // 2]
        elif side == 'bottom':
            return grid[len(grid) // 2 + len(grid) % 2:]
        elif side == 'left':
            return GridOps.rotate(GridOps.get_half(GridOps.rotate(grid, 90), 'top'), 270)
        elif side == 'right':
            return GridOps.rotate(GridOps.get_half(GridOps.rotate(grid, 90), 'bottom'), 270)

    @staticmethod
    def downscale(grid, factor):
        """
        Shrink a grid by keeping every factor-th row and column.
        Keeps cells where row_index % factor == 0 and col_index % factor == 0.
        """
        return [
            [grid[i][j] for j in range(0, len(grid[0]), factor)]
            for i in range(0, len(grid), factor)
        ]

    @staticmethod
    def trim_border(grid):
        """Remove the outermost 1-cell border on all four sides."""
        return [row[1:-1] for row in grid[1:-1]]

    @staticmethod
    def find_frontiers(grid):
        """
        Return all 'frontier' objects: full rows or columns that are a single color.
        Each frontier is returned as a colored Object (dict).
        """
        h, w = len(grid), len(grid[0])
        uniform_rows = [i for i, row in enumerate(grid) if len(set(row)) == 1]
        uniform_cols = [j for j, col in enumerate(zip(*grid)) if len(set(col)) == 1]
        frontiers = []
        for i in uniform_rows:
            frontiers.append({(i, j): grid[i][j] for j in range(w)})
        for j in uniform_cols:
            frontiers.append({(i, j): grid[i][j] for i in range(h)})
        return frontiers

    @staticmethod
    def remove_frontiers(grid):
        """Remove all uniform-color full rows and columns from the grid."""
        uniform_rows = {i for i, row in enumerate(grid) if len(set(row)) == 1}
        uniform_cols = {j for j, col in enumerate(zip(*grid)) if len(set(col)) == 1}
        return [
            [v for j, v in enumerate(row) if j not in uniform_cols]
            for i, row in enumerate(grid)
            if i not in uniform_rows
        ]


# ──────────────────────────────────────────────────────────────────────────────
# class PatchOps — operations whose primary subject is a Patch (Object/Indices)
# ──────────────────────────────────────────────────────────────────────────────

class PatchOps:
    """
    Operations on Patches.

    Object  = dict[(row, col) -> color]  — colored cells
    Indices = set[(row, col)]            — position-only cells
    Patch   = Object | Indices
    """

    @staticmethod
    def to_indices(patch):
        """
        Strip colors from an Object (dict) → plain set of (row, col).
        Pass-through if patch is already a set.
        """
        return _to_indices(patch)

    @staticmethod
    def to_colored_object(patch, grid):
        """
        Look up the color for each position in `patch` from `grid`.
        Out-of-bounds positions are silently dropped.
        Returns an Object (dict).
        """
        h, w = len(grid), len(grid[0])
        return {
            (i, j): grid[i][j]
            for i, j in _to_indices(patch)
            if 0 <= i < h and 0 <= j < w
        }

    @staticmethod
    def recolor(color, patch):
        """Assign `color` to every position in `patch`, returning an Object (dict)."""
        return {idx: color for idx in _to_indices(patch)}

    @staticmethod
    def translate(patch, offset):
        """
        Shift every position in `patch` by `offset` = (row_delta, col_delta).
        Preserves whether the patch is a colored Object (dict) or plain Indices (set).
        """
        if len(patch) == 0:
            return patch
        di, dj = offset
        if isinstance(patch, dict):
            return {(i + di, j + dj): v for (i, j), v in patch.items()}
        return {(i + di, j + dj) for i, j in patch}

    @staticmethod
    def normalize_to_origin(patch):
        """Shift `patch` so its upper-left bounding-box corner is at (0, 0)."""
        if len(patch) == 0:
            return patch
        return PatchOps.translate(
            patch,
            (-_boundary(patch, 'top'), -_boundary(patch, 'left')),
        )

    @staticmethod
    def get_boundary(patch, side):
        """
        Boundary index of the patch's bounding box.
        side: 'top' (min row), 'bottom' (max row), 'left' (min col), 'right' (max col).
        Patch must be non-empty.
        """
        return _boundary(patch, side)

    @staticmethod
    def get_corner(patch, position='upper_left'):
        """
        One corner (row, col) of the patch's bounding box.
        position: 'upper_left', 'upper_right', 'lower_left', 'lower_right'.
        Patch must be non-empty.
        """
        idxs = _to_indices(patch)
        rows = [i for i, j in idxs]
        cols = [j for i, j in idxs]
        row_fn = {'upper_left': min, 'upper_right': min,
                  'lower_left': max, 'lower_right': max}
        col_fn = {'upper_left': min, 'upper_right': max,
                  'lower_left': min, 'lower_right': max}
        return (row_fn[position](rows), col_fn[position](cols))

    @staticmethod
    def get_center(patch):
        """Center (row, col) of the patch's bounding box (integer division)."""
        return (
            _boundary(patch, 'top') + height(patch) // 2,
            _boundary(patch, 'left') + width(patch) // 2,
        )

    @staticmethod
    def all_corners(patch):
        """Return the four bounding-box corner indices as Indices (set)."""
        return {
            PatchOps.get_corner(patch, pos)
            for pos in ('upper_left', 'upper_right', 'lower_left', 'lower_right')
        }

    @staticmethod
    def filled_bounding_box(patch):
        """All (row, col) positions within the patch's bounding box (filled rectangle)."""
        if len(patch) == 0:
            return set()
        si, sj = PatchOps.get_corner(patch, 'upper_left')
        ei, ej = PatchOps.get_corner(patch, 'lower_right')
        return {(i, j) for i in range(si, ei + 1) for j in range(sj, ej + 1)}

    @staticmethod
    def bounding_box_complement(patch):
        """Positions inside the bounding box that are NOT part of the patch (holes)."""
        if len(patch) == 0:
            return set()
        return PatchOps.filled_bounding_box(patch) - _to_indices(patch)

    @staticmethod
    def bounding_box_outline(patch, offset=0):
        """
        Perimeter of the patch's bounding box, with optional offset.

        offset=0:  exact bounding-box outline.
        offset=1:  one cell inside (inbox — shrinks the outline by 1 on each side).
        offset=-1: one cell outside (outbox — expands by 1 on each side).

        Works even if the offset inverts corners (uses min/max to normalise).
        """
        if len(patch) == 0:
            return set()
        ai = _boundary(patch, 'top') + offset
        aj = _boundary(patch, 'left') + offset
        bi = _boundary(patch, 'bottom') - offset
        bj = _boundary(patch, 'right') - offset
        si, sj = min(ai, bi), min(aj, bj)
        ei, ej = max(ai, bi), max(aj, bj)
        top_row    = {(si, j) for j in range(sj, ej + 1)}
        bottom_row = {(ei, j) for j in range(sj, ej + 1)}
        left_col   = {(i, sj) for i in range(si, ei + 1)}
        right_col  = {(i, ej) for i in range(si, ei + 1)}
        return top_row | bottom_row | left_col | right_col

    @staticmethod
    def is_line(patch, axis='vertical'):
        """
        True iff `patch` forms a straight filled line.
        axis='vertical':   single column (width==1, height==len(patch)).
        axis='horizontal': single row    (height==1, width==len(patch)).
        """
        if axis == 'vertical':
            return height(patch) == len(patch) and width(patch) == 1
        else:
            return width(patch) == len(patch) and height(patch) == 1

    @staticmethod
    def shares_axis(a, b, axis='row'):
        """
        True iff patches `a` and `b` share at least one row or column.
        axis='row':    checks for a shared row index.
        axis='column': checks for a shared column index.
        """
        if axis == 'row':
            return bool(
                {i for i, j in _to_indices(a)} & {i for i, j in _to_indices(b)}
            )
        else:
            return bool(
                {j for i, j in _to_indices(a)} & {j for i, j in _to_indices(b)}
            )

    @staticmethod
    def manhattan_distance(a, b):
        """Minimum Manhattan distance between any cell in `a` and any cell in `b`."""
        return min(
            abs(ai - bi) + abs(aj - bj)
            for ai, aj in _to_indices(a)
            for bi, bj in _to_indices(b)
        )

    @staticmethod
    def are_adjacent(a, b):
        """True iff manhattan_distance(a, b) == 1."""
        return PatchOps.manhattan_distance(a, b) == 1

    @staticmethod
    def touches_border(patch, grid):
        """True iff `patch` touches any edge of `grid`."""
        return (
            _boundary(patch, 'top') == 0
            or _boundary(patch, 'left') == 0
            or _boundary(patch, 'bottom') == len(grid) - 1
            or _boundary(patch, 'right') == len(grid[0]) - 1
        )

    @staticmethod
    def center_of_mass(patch):
        """
        Mean (row, col) of all patch cells (integer division).
        Unlike get_center, this is the true centroid rather than the bbox midpoint.
        """
        idxs = list(_to_indices(patch))
        n = len(idxs)
        return (sum(i for i, j in idxs) // n, sum(j for i, j in idxs) // n)

    @staticmethod
    def relative_direction(a, b):
        """
        Direction from patch `a` to patch `b` as (row_sign, col_sign).
        Each component is in {-1, 0, 1}.
        Example: (1, -1) means `b` is below and to the left of `a`.
        """
        ia, ja = PatchOps.get_center(_to_indices(a))
        ib, jb = PatchOps.get_center(_to_indices(b))
        if ia == ib:
            return (0, 1 if ja < jb else -1)
        elif ja == jb:
            return (1 if ia < ib else -1, 0)
        elif ia < ib:
            return (1, 1 if ja < jb else -1)
        else:
            return (-1, 1 if ja < jb else -1)

    @staticmethod
    def gravitate_toward(source, destination):
        """
        Compute the (row_delta, col_delta) offset to slide `source` step-by-step
        until it is adjacent to `destination` (stops after 42 steps max).

        Movement axis: along rows if the patches share a column; otherwise along columns.
        Returns the accumulated offset at the last non-adjacent position.
        """
        si, sj = PatchOps.get_center(source)
        di, dj = PatchOps.get_center(destination)
        if PatchOps.shares_axis(source, destination, 'column'):
            dr, dc = (1 if si < di else -1), 0
        else:
            dr, dc = 0, (1 if sj < dj else -1)

        gi, gj = dr, dc
        steps = 0
        while not PatchOps.are_adjacent(source, destination) and steps < 42:
            steps += 1
            gi += dr
            gj += dc
            source = PatchOps.translate(source, (dr, dc))
        return (gi - dr, gj - dc)

    @staticmethod
    def find_period(obj, axis='horizontal'):
        """
        Smallest repeating period of `obj` along the given axis.

        Detects period p when shifting by -p (left for horizontal, up for vertical)
        and pruning negative-coordinate cells yields a subset of the original.
        Returns the full width/height if no smaller period exists.

        axis: 'horizontal' (period along columns) or 'vertical' (period along rows).
        """
        normalized = PatchOps.normalize_to_origin(obj)
        total = width(normalized) if axis == 'horizontal' else height(normalized)
        for p in range(1, total):
            if axis == 'horizontal':
                shifted = PatchOps.translate(normalized, (0, -p))
                pruned = {(i, j): c for (i, j), c in shifted.items() if j >= 0}
            else:
                shifted = PatchOps.translate(normalized, (-p, 0))
                pruned = {(i, j): c for (i, j), c in shifted.items() if i >= 0}
            if pruned.items() <= normalized.items():
                return p
        return total


# ──────────────────────────────────────────────────────────────────────────────
# class ColorOps — color analysis on grids and objects
# ──────────────────────────────────────────────────────────────────────────────

class ColorOps:
    """Color queries on any Element (Grid or Object)."""

    @staticmethod
    def dominant_color(element, mode='most'):
        """
        Most or least common color in a grid or object.
        mode='most'  → most common (background heuristic).
        mode='least' → least common.
        Tie-breaking is non-deterministic (iterates over a set).
        """
        values = (
            [v for row in element for v in row]
            if isinstance(element, list)
            else list(element.values())
        )
        def tie_breaker(color):
            # Prioritize color 0 (background), then sort by color value
            return (values.count(color), color == 0, color)
        
        fn = max if mode == 'most' else min
        # sorted(set) ensures deterministic tie breaks. fn uses tie_breaker key.
        return fn(sorted(set(values)), key=tie_breaker)

    @staticmethod
    def count_color(element, color):
        """Count how many cells equal `color` (works on grid or object)."""
        if isinstance(element, list):
            return sum(row.count(color) for row in element)
        return sum(v == color for v in element.values())

    @staticmethod
    def unique_colors(element):
        """Set of all distinct colors present in a grid or object."""
        if isinstance(element, list):
            return {v for row in element for v in row}
        return set(element.values())

    @staticmethod
    def count_unique_colors(element):
        """Number of distinct colors in a grid or object."""
        return len(ColorOps.unique_colors(element))

    @staticmethod
    def get_color(obj):
        """
        Color of a (assumed) single-color object.
        Returns the color of the first cell; behaviour undefined for multi-color objects.
        """
        return next(iter(obj.values()))


# ──────────────────────────────────────────────────────────────────────────────
# class SearchOps — finding objects and patterns in grids
# ──────────────────────────────────────────────────────────────────────────────

class SearchOps:
    """Finding connected components, color regions, and pattern occurrences."""

    @staticmethod
    def find_objects(grid, univalued, diagonal, without_background):
        """
        Connected-component extraction from a grid.

        univalued=True:          only group cells of the same color together.
        univalued=False:         group any non-background cells together.
        diagonal=True:           use 8-connectivity (includes diagonals).
        diagonal=False:          use 4-connectivity (orthogonal only).
        without_background=True: ignore cells with dominant_color(grid).

        Returns a list of Objects (each Object is a dict mapping (row,col)->color).
        """
        bg = ColorOps.dominant_color(grid) if without_background else None
        h, w = len(grid), len(grid[0])
        neighbor_fn = GeoOps.all_neighbors if diagonal else GeoOps.orthogonal_neighbors
        occupied = set()
        objs = []

        for r in range(h):
            for c in range(w):
                loc = (r, c)
                if loc in occupied:
                    continue
                val = grid[r][c]
                if val == bg:
                    continue
                obj = {loc: val}
                frontier = {loc}
                while frontier:
                    next_frontier = set()
                    for cand in frontier:
                        v = grid[cand[0]][cand[1]]
                        if (v == val) if univalued else (v != bg):
                            obj[cand] = v
                            occupied.add(cand)
                            next_frontier |= {
                                nb for nb in neighbor_fn(cand)
                                if 0 <= nb[0] < h and 0 <= nb[1] < w
                            }
                    frontier = next_frontier - occupied
                objs.append(obj)

        return objs

    @staticmethod
    def partition_by_color(grid, without_background=False):
        """
        Group all grid cells by color. Each color → one Object (dict).
        without_background=True: exclude cells with dominant_color(grid).
        Returns list[Object].
        """
        colors = ColorOps.unique_colors(grid)
        if without_background:
            colors = colors - {ColorOps.dominant_color(grid)}
        return [
            {
                (i, j): v
                for i, row in enumerate(grid)
                for j, v in enumerate(row)
                if v == c
            }
            for c in colors
        ]

    @staticmethod
    def indices_with_color(grid, color):
        """All (row, col) positions in the grid where the cell equals `color`."""
        return {
            (i, j)
            for i, row in enumerate(grid)
            for j, v in enumerate(row)
            if v == color
        }

    @staticmethod
    def filter_by_color(objects, color):
        """Keep only objects whose (assumed single) color equals `color`."""
        return [
            obj for obj in objects
            if next(iter(obj.values())) == color
        ]

    @staticmethod
    def filter_by_size(container, size):
        """Keep only items where len(item) == size."""
        return [item for item in container if len(item) == size]

    @staticmethod
    def find_occurrences(grid, obj):
        """
        Find all top-left (row, col) positions where `obj`'s colored cells match `grid`.
        Matches only the cells in obj; does not require specific values elsewhere.
        Returns Indices (a set of (row, col) positions).
        """
        normed = PatchOps.normalize_to_origin(obj)
        oh, ow = dimensions(obj)
        h, w = len(grid), len(grid[0])
        occs = set()
        for i in range(h - oh + 1):
            for j in range(w - ow + 1):
                placed = PatchOps.translate(normed, (i, j))
                if all(
                    0 <= r < h and 0 <= c < w and grid[r][c] == v
                    for (r, c), v in placed.items()
                ):
                    occs.add((i, j))
        return occs


# ──────────────────────────────────────────────────────────────────────────────
# class GeoOps — geometric relationships and index generation
# ──────────────────────────────────────────────────────────────────────────────

class GeoOps:
    """Geometric constructs: neighbors, lines, rays, and coordinate generation."""

    @staticmethod
    def orthogonal_neighbors(location):
        """The 4 orthogonally adjacent (row, col) positions (unbounded)."""
        r, c = location
        return {(r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)}

    @staticmethod
    def diagonal_neighbors(location):
        """The 4 diagonally adjacent (row, col) positions (unbounded)."""
        r, c = location
        return {(r-1, c-1), (r-1, c+1), (r+1, c-1), (r+1, c+1)}

    @staticmethod
    def all_neighbors(location):
        """All 8 adjacent positions: orthogonal ∪ diagonal (unbounded)."""
        return GeoOps.orthogonal_neighbors(location) | GeoOps.diagonal_neighbors(location)

    @staticmethod
    def line_between(point_a, point_b):
        """
        Indices forming a straight line between two points.
        Works for horizontal, vertical, and 45-degree diagonal lines.
        Returns an empty set if the points don't form any of those.
        """
        ai, aj = point_a
        bi, bj = point_b
        si, ei = min(ai, bi), max(ai, bi) + 1
        sj, ej = min(aj, bj), max(aj, bj) + 1
        if ai == bi:
            return {(ai, j) for j in range(sj, ej)}
        elif aj == bj:
            return {(i, aj) for i in range(si, ei)}
        elif bi - ai == bj - aj:
            return {(i, j) for i, j in zip(range(si, ei), range(sj, ej))}
        elif bi - ai == aj - bj:
            return {(i, j) for i, j in zip(range(si, ei), range(ej - 1, sj - 1, -1))}
        return set()

    @staticmethod
    def cast_ray(start, direction):
        """
        Indices along a ray from `start` in `direction` for up to 42 steps.
        direction = (row_delta, col_delta), e.g. (1, 0) for downward.
        Uses line_between internally, so only works for H/V/diagonal directions.
        """
        r, c = start
        dr, dc = direction
        return GeoOps.line_between(start, (r + 42 * dr, c + 42 * dc))

    @staticmethod
    def full_line_through(location, axis='vertical'):
        """
        A full line of 30 positions passing through `location`.
        axis='vertical':   all rows in the same column as location (a column slice).
        axis='horizontal': all columns in the same row as location (a row slice).
        Note: always uses range(30), independent of actual grid size.
        """
        r, c = location
        if axis == 'vertical':
            return {(i, c) for i in range(30)}
        else:
            return {(r, j) for j in range(30)}


# ──────────────────────────────────────────────────────────────────────────────
# Flat module-level exports
# (allows `from dsl import *` and dir()-based namespace injection)
# ──────────────────────────────────────────────────────────────────────────────

# Color queries
dominant_color    = ColorOps.dominant_color
count_color       = ColorOps.count_color
unique_colors     = ColorOps.unique_colors
count_unique_colors = ColorOps.count_unique_colors
get_color         = ColorOps.get_color

# Shared geometry (Piece = Grid | Patch)
# height, width, dimensions, is_portrait, is_square — already module-level
# mirror, upscale, upscale_along_axis — already module-level

# Grid construction / lookup / cropping
create_grid       = GridOps.create_grid
color_at          = GridOps.color_at
crop              = GridOps.crop
all_indices       = GridOps.all_indices
grid_to_object    = GridOps.grid_to_object
extract_subgrid   = GridOps.extract_subgrid

# Grid painting / erasing
fill              = GridOps.fill
paint             = GridOps.paint
erase             = GridOps.erase
move_object       = GridOps.move_object
replace_color     = GridOps.replace_color
swap_colors       = GridOps.swap_colors
cellwise_combine  = GridOps.cellwise_combine

# Grid transformations
rotate            = GridOps.rotate
concatenate       = GridOps.concatenate
split_grid        = GridOps.split_grid
get_half          = GridOps.get_half
downscale         = GridOps.downscale
trim_border       = GridOps.trim_border
find_frontiers    = GridOps.find_frontiers
remove_frontiers  = GridOps.remove_frontiers

# Patch / object construction & conversion
to_indices          = PatchOps.to_indices
to_colored_object   = PatchOps.to_colored_object
recolor             = PatchOps.recolor
translate           = PatchOps.translate
normalize_to_origin = PatchOps.normalize_to_origin

# Index / corner / boundary helpers
get_boundary        = PatchOps.get_boundary
get_corner          = PatchOps.get_corner
get_center          = PatchOps.get_center
all_corners         = PatchOps.all_corners

# Bounding-box geometry
filled_bounding_box     = PatchOps.filled_bounding_box
bounding_box_complement = PatchOps.bounding_box_complement
bounding_box_outline    = PatchOps.bounding_box_outline

# Relations between patches
is_line            = PatchOps.is_line
shares_axis        = PatchOps.shares_axis
manhattan_distance = PatchOps.manhattan_distance
are_adjacent       = PatchOps.are_adjacent
touches_border     = PatchOps.touches_border
center_of_mass     = PatchOps.center_of_mass
relative_direction = PatchOps.relative_direction
gravitate_toward   = PatchOps.gravitate_toward

# Pattern matching / periodicity
find_occurrences = SearchOps.find_occurrences
find_period      = PatchOps.find_period

# Connected components / partitioning / filtering
find_objects        = SearchOps.find_objects
partition_by_color  = SearchOps.partition_by_color
indices_with_color  = SearchOps.indices_with_color
filter_by_color     = SearchOps.filter_by_color
filter_by_size      = SearchOps.filter_by_size

# Neighborhoods / lines / rays
orthogonal_neighbors = GeoOps.orthogonal_neighbors
diagonal_neighbors   = GeoOps.diagonal_neighbors
all_neighbors        = GeoOps.all_neighbors
line_between         = GeoOps.line_between
cast_ray             = GeoOps.cast_ray
full_line_through    = GeoOps.full_line_through
