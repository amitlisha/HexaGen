def dominant_color(
    element: tuple | frozenset,
    mode: str = 'most'
) -> int:
    """ Return the most or least common color (mode: 'most' or 'least'). """
    values = [v for r in element for v in r] if isinstance(element, tuple) else [v for v, _ in element]
    func = max if mode == 'most' else min
    return func(set(values), key=values.count)


def height(
    piece: tuple | frozenset
) -> int:
    """ Height of a grid (number of rows) or patch (bounding box height). """
    if len(piece) == 0:
        return 0
    if isinstance(piece, tuple):
        return len(piece)
    return get_boundary(piece, 'bottom') - get_boundary(piece, 'top') + 1


def width(
    piece: tuple | frozenset
) -> int:
    """ Width of a grid (number of columns) or patch (bounding box width). """
    if len(piece) == 0:
        return 0
    if isinstance(piece, tuple):
        return len(piece[0])
    return get_boundary(piece, 'right') - get_boundary(piece, 'left') + 1


def dimensions(
    piece: tuple | frozenset
) -> tuple:
    """ Return (height, width) of a grid or patch. """
    return (height(piece), width(piece))


def is_portrait(
    piece: tuple | frozenset
) -> bool:
    """ Return True if height is greater than width. """
    return height(piece) > width(piece)


def count_color(
    element: tuple | frozenset,
    color: int
) -> int:
    """ Count the number of cells with the given color. """
    if isinstance(element, tuple):
        return sum(row.count(color) for row in element)
    return sum(v == color for v, _ in element)


def filter_by_color(
    objects: frozenset,
    color: int
) -> frozenset:
    """ Keep only objects whose color matches the given color. """
    return frozenset(obj for obj in objects if next(iter(obj))[0] == color)


def filter_by_size(
    container: tuple | frozenset,
    size: int
) -> frozenset:
    """ Keep only items whose length equals the given size. """
    return frozenset(item for item in container if len(item) == size)


def all_indices(
    grid: tuple
) -> frozenset:
    """ Return all (row, col) indices of a grid. """
    return frozenset((i, j) for i in range(len(grid)) for j in range(len(grid[0])))


def indices_with_color(
    grid: tuple,
    color: int
) -> frozenset:
    """ Return all (row, col) indices where the grid cell equals the given color. """
    return frozenset((i, j) for i, r in enumerate(grid) for j, v in enumerate(r) if v == color)


def get_corner(
    patch: frozenset,
    position: str = 'upper_left'
) -> tuple:
    """ Return the corner index of a patch's bounding box (position: 'upper_left', 'upper_right', 'lower_left', 'lower_right'). """
    indices = to_indices(patch)
    rows, cols = zip(*indices)
    row_funcs = {'upper_left': min, 'upper_right': min, 'lower_left': max, 'lower_right': max}
    col_funcs = {'upper_left': min, 'upper_right': max, 'lower_left': min, 'lower_right': max}
    return (row_funcs[position](rows), col_funcs[position](cols))


def crop(
    grid: tuple,
    start: tuple,
    size: tuple
) -> tuple:
    """ Extract a subgrid at the given start (row, col) with the given size (height, width). """
    return tuple(r[start[1]:start[1]+size[1]] for r in grid[start[0]:start[0]+size[0]])


def to_indices(
    patch: frozenset
) -> frozenset:
    """ Strip colors from an object to get plain (row, col) indices. Pass-through if already indices. """
    if len(patch) == 0:
        return frozenset()
    if isinstance(next(iter(patch))[1], tuple):
        return frozenset(index for value, index in patch)
    return patch


def recolor(
    color: int,
    patch: frozenset
) -> frozenset:
    """ Assign a new color to every cell in a patch. """
    return frozenset((color, index) for index in to_indices(patch))


def translate(
    patch: frozenset,
    offset: tuple
) -> frozenset:
    """ Translate (shift) a patch by the given (row_offset, col_offset). """
    if len(patch) == 0:
        return patch
    di, dj = offset
    if isinstance(next(iter(patch))[1], tuple):
        return frozenset((value, (i + di, j + dj)) for value, (i, j) in patch)
    return frozenset((i + di, j + dj) for i, j in patch)


def normalize_to_origin(
    patch: frozenset
) -> frozenset:
    """ Translate the patch so its upper-left corner is at (0, 0). """
    if len(patch) == 0:
        return patch
    return translate(patch, (-get_boundary(patch, 'top'), -get_boundary(patch, 'left')))


def orthogonal_neighbors(
    location: tuple
) -> frozenset:
    """ Return the 4 orthogonally adjacent indices (up, down, left, right). """
    return frozenset({(location[0] - 1, location[1]), (location[0] + 1, location[1]), (location[0], location[1] - 1), (location[0], location[1] + 1)})


def diagonal_neighbors(
    location: tuple
) -> frozenset:
    """ Return the 4 diagonally adjacent indices. """
    return frozenset({(location[0] - 1, location[1] - 1), (location[0] - 1, location[1] + 1), (location[0] + 1, location[1] - 1), (location[0] + 1, location[1] + 1)})


def all_neighbors(
    location: tuple
) -> frozenset:
    """ Return all 8 adjacent indices (orthogonal + diagonal). """
    return orthogonal_neighbors(location) | diagonal_neighbors(location)


def find_objects(
    grid: tuple,
    univalued: bool,
    diagonal: bool,
    without_background: bool
) -> frozenset:
    """ Find connected-component objects on the grid.
    univalued: only group same-color cells.
    diagonal: use 8-connectivity (otherwise 4-connectivity).
    without_background: ignore the most common (background) color.
    """
    bg = dominant_color(grid) if without_background else None
    objs = set()
    occupied = set()
    h, w = len(grid), len(grid[0])
    unvisited = all_indices(grid)
    neighbor_fn = all_neighbors if diagonal else orthogonal_neighbors
    for loc in unvisited:
        if loc in occupied:
            continue
        val = grid[loc[0]][loc[1]]
        if val == bg:
            continue
        obj = {(val, loc)}
        cands = {loc}
        while len(cands) > 0:
            neighborhood = set()
            for cand in cands:
                v = grid[cand[0]][cand[1]]
                if (val == v) if univalued else (v != bg):
                    obj.add((v, cand))
                    occupied.add(cand)
                    neighborhood |= {
                        (i, j) for i, j in neighbor_fn(cand) if 0 <= i < h and 0 <= j < w
                    }
            cands = neighborhood - occupied
        objs.add(frozenset(obj))
    return frozenset(objs)


def partition_by_color(
    grid: tuple,
    without_background: bool = False
) -> frozenset:
    """ Partition grid cells by color. Each partition is a frozenset of (color, (row, col)).
    without_background: exclude the most common (background) color.
    """
    colors = unique_colors(grid)
    if without_background:
        colors = colors - {dominant_color(grid)}
    return frozenset(
        frozenset(
            (v, (i, j)) for i, r in enumerate(grid) for j, v in enumerate(r) if v == c
        ) for c in colors
    )


def get_boundary(
    patch: frozenset,
    side: str
) -> int:
    """ Return the boundary index of a patch (side: 'top', 'bottom', 'left', 'right'). """
    indices = to_indices(patch)
    if side == 'top':
        return min(i for i, j in indices)
    elif side == 'bottom':
        return max(i for i, j in indices)
    elif side == 'left':
        return min(j for i, j in indices)
    elif side == 'right':
        return max(j for i, j in indices)


def is_square(
    piece: tuple | frozenset
) -> bool:
    """ Return True if the piece forms a filled square. """
    return len(piece) == len(piece[0]) if isinstance(piece, tuple) else height(piece) * width(piece) == len(piece) and height(piece) == width(piece)


def is_line(
    patch: frozenset,
    axis: str = 'vertical'
) -> bool:
    """ Return True if the patch forms a straight line (axis: 'vertical' or 'horizontal'). """
    if axis == 'vertical':
        return height(patch) == len(patch) and width(patch) == 1
    else:
        return width(patch) == len(patch) and height(patch) == 1


def shares_axis(
    a: frozenset,
    b: frozenset,
    axis: str = 'row'
) -> bool:
    """ Return True if two patches share any row or column (axis: 'row' or 'column'). """
    if axis == 'row':
        return len(set(i for i, j in to_indices(a)) & set(i for i, j in to_indices(b))) > 0
    else:
        return len(set(j for i, j in to_indices(a)) & set(j for i, j in to_indices(b))) > 0


def manhattan_distance(
    a: frozenset,
    b: frozenset
) -> int:
    """ Return the closest Manhattan distance between any two cells of two patches. """
    return min(abs(ai - bi) + abs(aj - bj) for ai, aj in to_indices(a) for bi, bj in to_indices(b))


def are_adjacent(
    a: frozenset,
    b: frozenset
) -> bool:
    """ Return True if the closest Manhattan distance between two patches is exactly 1. """
    return manhattan_distance(a, b) == 1


def touches_border(
    patch: frozenset,
    grid: tuple
) -> bool:
    """ Return True if the patch touches any edge of the grid. """
    return get_boundary(patch, 'top') == 0 or get_boundary(patch, 'left') == 0 or get_boundary(patch, 'bottom') == len(grid) - 1 or get_boundary(patch, 'right') == len(grid[0]) - 1


def center_of_mass(
    patch: frozenset
) -> tuple:
    """ Return the mean (row, col) position of all cells in the patch (integer division). """
    return tuple(map(lambda x: sum(x) // len(patch), zip(*to_indices(patch))))


def unique_colors(
    element: tuple | frozenset
) -> frozenset:
    """ Return the set of all distinct colors in a grid or object. """
    if isinstance(element, tuple):
        return frozenset({v for r in element for v in r})
    return frozenset({v for v, _ in element})


def count_unique_colors(
    element: tuple | frozenset
) -> int:
    """ Return the number of distinct colors in a grid or object. """
    return len(unique_colors(element))


def get_color(
    obj: frozenset
) -> int:
    """ Return the color of a single-color object. """
    return next(iter(obj))[0]


def to_colored_object(
    patch: frozenset,
    grid: tuple
) -> frozenset:
    """ Look up colors from the grid for each index in the patch, returning a colored object. """
    h, w = len(grid), len(grid[0])
    return frozenset((grid[i][j], (i, j)) for i, j in to_indices(patch) if 0 <= i < h and 0 <= j < w)


def grid_to_object(
    grid: tuple
) -> frozenset:
    """ Convert an entire grid into an object (frozenset of (color, (row, col))). """
    return frozenset((v, (i, j)) for i, r in enumerate(grid) for j, v in enumerate(r))


def rotate(
    grid: tuple,
    angle: int = 90
) -> tuple:
    """ Rotate a grid clockwise (angle: 90, 180, or 270 degrees). """
    if angle == 90:
        return tuple(row for row in zip(*grid[::-1]))
    elif angle == 180:
        return tuple(tuple(row[::-1]) for row in grid[::-1])
    elif angle == 270:
        return tuple(tuple(row[::-1]) for row in zip(*grid[::-1]))[::-1]
    return grid


def mirror(
    piece: tuple | frozenset,
    axis: str = 'horizontal'
) -> tuple | frozenset:
    """ Mirror/reflect a piece (axis: 'horizontal', 'vertical', 'diagonal', 'counterdiagonal').
    horizontal: flip top-to-bottom.
    vertical: flip left-to-right.
    diagonal: transpose along main diagonal.
    counterdiagonal: transpose along counter-diagonal.
    """
    if axis == 'horizontal':
        if isinstance(piece, tuple):
            return piece[::-1]
        d = get_corner(piece, 'upper_left')[0] + get_corner(piece, 'lower_right')[0]
        if isinstance(next(iter(piece))[1], tuple):
            return frozenset((v, (d - i, j)) for v, (i, j) in piece)
        return frozenset((d - i, j) for i, j in piece)
    elif axis == 'vertical':
        if isinstance(piece, tuple):
            return tuple(row[::-1] for row in piece)
        d = get_corner(piece, 'upper_left')[1] + get_corner(piece, 'lower_right')[1]
        if isinstance(next(iter(piece))[1], tuple):
            return frozenset((v, (i, d - j)) for v, (i, j) in piece)
        return frozenset((i, d - j) for i, j in piece)
    elif axis == 'diagonal':
        if isinstance(piece, tuple):
            return tuple(zip(*piece))
        a, b = get_corner(piece, 'upper_left')
        if isinstance(next(iter(piece))[1], tuple):
            return frozenset((v, (j - b + a, i - a + b)) for v, (i, j) in piece)
        return frozenset((j - b + a, i - a + b) for i, j in piece)
    elif axis == 'counterdiagonal':
        if isinstance(piece, tuple):
            return tuple(zip(*(r[::-1] for r in piece[::-1])))
        return mirror(mirror(mirror(piece, 'vertical'), 'diagonal'), 'vertical')


def fill(
    grid: tuple,
    color: int,
    patch: frozenset,
    background_only: bool = False
) -> tuple:
    """ Set all patch positions to the given color.
    background_only: only fill cells that currently have the background color.
    """
    h, w = len(grid), len(grid[0])
    bg = dominant_color(grid) if background_only else None
    g = list(list(row) for row in grid)
    for i, j in to_indices(patch):
        if 0 <= i < h and 0 <= j < w:
            if not background_only or g[i][j] == bg:
                g[i][j] = color
    return tuple(tuple(row) for row in g)


def paint(
    grid: tuple,
    obj: frozenset,
    background_only: bool = False
) -> tuple:
    """ Stamp an object (with its colors) onto the grid.
    background_only: only paint over cells that have the background color.
    """
    h, w = len(grid), len(grid[0])
    bg = dominant_color(grid) if background_only else None
    g = list(list(row) for row in grid)
    for value, (i, j) in obj:
        if 0 <= i < h and 0 <= j < w:
            if not background_only or g[i][j] == bg:
                g[i][j] = value
    return tuple(tuple(row) for row in g)


def upscale_along_axis(
    grid: tuple,
    factor: int,
    axis: str = 'horizontal'
) -> tuple:
    """ Upscale a grid along one axis (axis: 'horizontal' stretches columns, 'vertical' stretches rows). """
    if axis == 'horizontal':
        g = tuple()
        for row in grid:
            r = tuple()
            for value in row:
                r = r + tuple(value for num in range(factor))
            g = g + (r,)
        return g
    else:
        g = tuple()
        for row in grid:
            g = g + tuple(row for num in range(factor))
        return g


def upscale(
    element: tuple | frozenset,
    factor: int
) -> tuple | frozenset:
    """ Scale a grid or object by the given factor in both directions. """
    if isinstance(element, tuple):
        g = tuple()
        for row in element:
            upscaled_row = tuple()
            for value in row:
                upscaled_row = upscaled_row + tuple(value for num in range(factor))
            g = g + tuple(upscaled_row for num in range(factor))
        return g
    else:
        if len(element) == 0:
            return frozenset()
        di_inv, dj_inv = get_corner(element, 'upper_left')
        di, dj = (-di_inv, -dj_inv)
        normed_obj = translate(element, (di, dj))
        o = set()
        for value, (i, j) in normed_obj:
            for io in range(factor):
                for jo in range(factor):
                    o.add((value, (i * factor + io, j * factor + jo)))
        return translate(frozenset(o), (di_inv, dj_inv))


def downscale(
    grid: tuple,
    factor: int
) -> tuple:
    """ Shrink a grid by sampling every factor-th cell. """
    h, w = len(grid), len(grid[0])
    g = tuple()
    for i in range(h):
        r = tuple()
        for j in range(w):
            if j % factor == 0:
                r = r + (grid[i][j],)
        g = g + (r, )
    h = len(g)
    dsg = tuple()
    for i in range(h):
        if i % factor == 0:
            dsg = dsg + (g[i],)
    return dsg


def concatenate(
    a: tuple,
    b: tuple,
    axis: str = 'horizontal'
) -> tuple:
    """ Concatenate two grids (axis: 'horizontal' = side by side, 'vertical' = top to bottom). """
    if axis == 'horizontal':
        return tuple(i + j for i, j in zip(a, b))
    else:
        return a + b


def extract_subgrid(
    patch: frozenset,
    grid: tuple
) -> tuple:
    """ Extract the smallest subgrid that contains the patch's bounding box. """
    return crop(grid, get_corner(patch, 'upper_left'), dimensions(patch))


def split_grid(
    grid: tuple,
    parts: int,
    axis: str = 'horizontal'
) -> tuple:
    """ Split a grid into N equal parts (axis: 'horizontal' = left-to-right, 'vertical' = top-to-bottom). """
    if axis == 'horizontal':
        h, w = len(grid), len(grid[0]) // parts
        offset = len(grid[0]) % parts != 0
        return tuple(crop(grid, (0, w * i + i * offset), (h, w)) for i in range(parts))
    else:
        h, w = len(grid) // parts, len(grid[0])
        offset = len(grid) % parts != 0
        return tuple(crop(grid, (h * i + i * offset, 0), (h, w)) for i in range(parts))


def cellwise_combine(
    a: tuple,
    b: tuple,
    fallback_color: int
) -> tuple:
    """ Combine two grids cell-by-cell: keep the value where they agree, use fallback_color where they differ. """
    h, w = len(a), len(a[0])
    resulting_grid = tuple()
    for i in range(h):
        row = tuple()
        for j in range(w):
            a_value = a[i][j]
            value = a_value if a_value == b[i][j] else fallback_color
            row = row + (value,)
        resulting_grid = resulting_grid + (row, )
    return resulting_grid


def replace_color(
    grid: tuple,
    old_color: int,
    new_color: int
) -> tuple:
    """ Replace all occurrences of old_color with new_color in the grid. """
    return tuple(tuple(new_color if v == old_color else v for v in r) for r in grid)


def swap_colors(
    grid: tuple,
    color_a: int,
    color_b: int
) -> tuple:
    """ Swap two colors everywhere in the grid. """
    return tuple(tuple(v if (v != color_a and v != color_b) else {color_a: color_b, color_b: color_a}[v] for v in r) for r in grid)


def get_center(
    patch: frozenset
) -> tuple:
    """ Return the center (row, col) of the patch's bounding box (integer division). """
    return (get_boundary(patch, 'top') + height(patch) // 2, get_boundary(patch, 'left') + width(patch) // 2)


def relative_direction(
    a: frozenset,
    b: frozenset
) -> tuple:
    """ Return the relative direction from patch a to patch b as (row_sign, col_sign).
    Each component is -1, 0, or 1. E.g. (1, -1) means b is below and to the left of a.
    """
    ia, ja = get_center(to_indices(a))
    ib, jb = get_center(to_indices(b))
    if ia == ib:
        return (0, 1 if ja < jb else -1)
    elif ja == jb:
        return (1 if ia < ib else -1, 0)
    elif ia < ib:
        return (1, 1 if ja < jb else -1)
    elif ia > ib:
        return (-1, 1 if ja < jb else -1)


def color_at(
    grid: tuple,
    location: tuple
) -> int:
    """ Return the color at the given (row, col) location. Returns None if out of bounds. """
    i, j = location
    h, w = len(grid), len(grid[0])
    if not (0 <= i < h and 0 <= j < w):
        return None
    return grid[location[0]][location[1]]


def create_grid(
    color: int,
    size: tuple
) -> tuple:
    """ Create a uniform grid filled with the given color and size (rows, cols). """
    return tuple(tuple(color for j in range(size[1])) for i in range(size[0]))


def all_corners(
    patch: frozenset
) -> frozenset:
    """ Return the four corner indices of the patch's bounding box. """
    return frozenset({get_corner(patch, pos) for pos in ('upper_left', 'upper_right', 'lower_left', 'lower_right')})


def line_between(
    point_a: tuple,
    point_b: tuple
) -> frozenset:
    """ Return the indices forming a straight line between two points.
    Works for horizontal, vertical, and 45-degree diagonal lines. Returns empty set otherwise.
    """
    ai, aj = point_a
    bi, bj = point_b
    si = min(ai, bi)
    ei = max(ai, bi) + 1
    sj = min(aj, bj)
    ej = max(aj, bj) + 1
    if ai == bi:
        return frozenset((ai, j) for j in range(sj, ej))
    elif aj == bj:
        return frozenset((i, aj) for i in range(si, ei))
    elif bi - ai == bj - aj:
        return frozenset((i, j) for i, j in zip(range(si, ei), range(sj, ej)))
    elif bi - ai == aj - bj:
        return frozenset((i, j) for i, j in zip(range(si, ei), range(ej - 1, sj - 1, -1)))
    return frozenset()


def erase(
    grid: tuple,
    patch: frozenset
) -> tuple:
    """ Erase a patch from the grid by filling it with the background (most common) color. """
    return fill(grid, dominant_color(grid), to_indices(patch))


def trim_border(
    grid: tuple
) -> tuple:
    """ Remove the one-cell border on all sides of the grid. """
    return tuple(r[1:-1] for r in grid[1:-1])


def move_object(
    grid: tuple,
    obj: frozenset,
    offset: tuple
) -> tuple:
    """ Remove an object from the grid, then paint it back shifted by the given offset. """
    return paint(erase(grid, obj), translate(obj, offset))


def get_half(
    grid: tuple,
    side: str = 'top'
) -> tuple:
    """ Return half of the grid (side: 'top', 'bottom', 'left', 'right'). """
    if side == 'top':
        return grid[:len(grid) // 2]
    elif side == 'bottom':
        return grid[len(grid) // 2 + len(grid) % 2:]
    elif side == 'left':
        return rotate(get_half(rotate(grid, 90), 'top'), 270)
    elif side == 'right':
        return rotate(get_half(rotate(grid, 90), 'bottom'), 270)


def full_line_through(
    location: tuple,
    axis: str = 'vertical'
) -> frozenset:
    """ Return a full line of indices through the given location (axis: 'vertical' or 'horizontal'). """
    if axis == 'vertical':
        return frozenset((i, location[1]) for i in range(30))
    else:
        return frozenset((location[0], j) for j in range(30))


def filled_bounding_box(
    patch: frozenset
) -> frozenset:
    """ Return all indices inside the bounding box of the patch. """
    if len(patch) == 0:
        return frozenset({})
    indices = to_indices(patch)
    si, sj = get_corner(indices, 'upper_left')
    ei, ej = get_corner(patch, 'lower_right')
    return frozenset((i, j) for i in range(si, ei + 1) for j in range(sj, ej + 1))


def bounding_box_complement(
    patch: frozenset
) -> frozenset:
    """ Return indices inside the bounding box that are NOT part of the patch. """
    if len(patch) == 0:
        return frozenset({})
    return filled_bounding_box(patch) - to_indices(patch)


def gravitate_toward(
    source: frozenset,
    destination: frozenset
) -> tuple:
    """ Return the offset needed to move source until it is adjacent to destination. """
    si, sj = get_center(source)
    di, dj = get_center(destination)
    i, j = 0, 0
    if shares_axis(source, destination, 'column'):
        i = 1 if si < di else -1
    else:
        j = 1 if sj < dj else -1
    gi, gj = i, j
    c = 0
    while not are_adjacent(source, destination) and c < 42:
        c += 1
        gi += i
        gj += j
        source = translate(source, (i, j))
    return (gi - i, gj - j)


def bounding_box_outline(
    patch: frozenset,
    offset: int = 0
) -> frozenset:
    """ Return the perimeter indices of the bounding box.
    offset=0: exact bounding box outline.
    offset=1: outline one cell inside (inbox).
    offset=-1: outline one cell outside (outbox).
    """
    if len(patch) == 0:
        return frozenset()
    ai = get_boundary(patch, 'top') + offset
    aj = get_boundary(patch, 'left') + offset
    bi = get_boundary(patch, 'bottom') - offset
    bj = get_boundary(patch, 'right') - offset
    si, sj = min(ai, bi), min(aj, bj)
    ei, ej = max(ai, bi), max(aj, bj)
    vlines = {(i, sj) for i in range(si, ei + 1)} | {(i, ej) for i in range(si, ei + 1)}
    hlines = {(si, j) for j in range(sj, ej + 1)} | {(ei, j) for j in range(sj, ej + 1)}
    return frozenset(vlines | hlines)


def cast_ray(
    start: tuple,
    direction: tuple
) -> frozenset:
    """ Cast a ray from the starting point in the given direction (up to 42 cells). """
    return line_between(start, (start[0] + 42 * direction[0], start[1] + 42 * direction[1]))


def find_occurrences(
    grid: tuple,
    obj: frozenset
) -> frozenset:
    """ Find all (row, col) positions where the given object appears in the grid. """
    occs = set()
    normed = normalize_to_origin(obj)
    h, w = len(grid), len(grid[0])
    oh, ow = dimensions(obj)
    h2, w2 = h - oh + 1, w - ow + 1
    for i in range(h2):
        for j in range(w2):
            occurs = True
            for v, (a, b) in translate(normed, (i, j)):
                if not (0 <= a < h and 0 <= b < w and grid[a][b] == v):
                    occurs = False
                    break
            if occurs:
                occs.add((i, j))
    return frozenset(occs)


def find_frontiers(
    grid: tuple
) -> frozenset:
    """ Find all uniform-color full rows and columns in the grid. """
    h, w = len(grid), len(grid[0])
    row_indices = tuple(i for i, r in enumerate(grid) if len(set(r)) == 1)
    column_indices = tuple(j for j, c in enumerate(mirror(grid, 'diagonal')) if len(set(c)) == 1)
    hfrontiers = frozenset({frozenset({(grid[i][j], (i, j)) for j in range(w)}) for i in row_indices})
    vfrontiers = frozenset({frozenset({(grid[i][j], (i, j)) for i in range(h)}) for j in column_indices})
    return hfrontiers | vfrontiers


def remove_frontiers(
    grid: tuple
) -> tuple:
    """ Remove all uniform-color full rows and columns from the grid. """
    ri = tuple(i for i, r in enumerate(grid) if len(set(r)) == 1)
    ci = tuple(j for j, c in enumerate(mirror(grid, 'diagonal')) if len(set(c)) == 1)
    return tuple(tuple(v for j, v in enumerate(r) if j not in ci) for i, r in enumerate(grid) if i not in ri)


def find_period(
    obj: frozenset,
    axis: str = 'horizontal'
) -> int:
    """ Find the smallest repeating period of the object along the given axis (axis: 'horizontal' or 'vertical'). """
    normalized = normalize_to_origin(obj)
    total = width(normalized) if axis == 'horizontal' else height(normalized)
    for p in range(1, total):
        if axis == 'horizontal':
            offsetted = translate(normalized, (0, -p))
            pruned = frozenset({(c, (i, j)) for c, (i, j) in offsetted if j >= 0})
        else:
            offsetted = translate(normalized, (-p, 0))
            pruned = frozenset({(c, (i, j)) for c, (i, j) in offsetted if i >= 0})
        if pruned.issubset(normalized):
            return p
    return total
