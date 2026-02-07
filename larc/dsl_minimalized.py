from typing import Any, Callable


def merge(
    containers: tuple | frozenset
) -> tuple | frozenset:
    """ merging """
    return type(containers)(e for c in containers for e in c)


def sfilter(
    container: tuple | frozenset,
    condition: Callable
) -> tuple | frozenset:
    """ keep elements in container that satisfy condition """
    return type(container)(e for e in container if condition(e))


def mfilter(
    container: tuple | frozenset,
    function: Callable
) -> frozenset:
    """ filter and merge """
    return merge(sfilter(container, function))


def extract(
    container: tuple | frozenset,
    condition: Callable
) -> Any:
    """ first element of container that satisfies condition """
    return next(e for e in container if condition(e))


def compose(
    outer: Callable,
    inner: Callable
) -> Callable:
    """ function composition """
    return lambda x: outer(inner(x))


def chain(
    h: Callable,
    g: Callable,
    f: Callable,
) -> Callable:
    """ function composition with three functions """
    return lambda x: h(g(f(x)))


def matcher(
    function: Callable,
    target: Any
) -> Callable:
    """ construction of equality function """
    return lambda x: function(x) == target


def rbind(
    function: Callable,
    fixed: Any
) -> Callable:
    """ fix the rightmost argument """
    n = function.__code__.co_argcount
    if n == 2:
        return lambda x: function(x, fixed)
    elif n == 3:
        return lambda x, y: function(x, y, fixed)
    else:
        return lambda x, y, z: function(x, y, z, fixed)


def lbind(
    function: Callable,
    fixed: Any
) -> Callable:
    """ fix the leftmost argument """
    n = function.__code__.co_argcount
    if n == 2:
        return lambda y: function(fixed, y)
    elif n == 3:
        return lambda y, z: function(fixed, y, z)
    else:
        return lambda y, z, a: function(fixed, y, z, a)


def power(
    function: Callable,
    n: int
) -> Callable:
    """ power of function """
    if n == 1:
        return function
    return compose(function, power(function, n - 1))


def fork(
    outer: Callable,
    a: Callable,
    b: Callable
) -> Callable:
    """ creates a wrapper function """
    return lambda x: outer(a(x), b(x))


def apply(
    function: Callable,
    container: tuple | frozenset
) -> tuple | frozenset:
    """ apply function to each item in container """
    return type(container)(function(e) for e in container)


def rapply(
    functions: tuple | frozenset,
    value: Any
) -> tuple | frozenset:
    """ apply each function in container to value """
    return type(functions)(function(value) for function in functions)


def mapply(
    function: Callable,
    container: tuple | frozenset
) -> frozenset:
    """ apply and merge """
    return merge(apply(function, container))


def papply(
    function: Callable,
    a: tuple,
    b: tuple
) -> tuple:
    """ apply function on two vectors """
    return tuple(function(i, j) for i, j in zip(a, b))


def mpapply(
    function: Callable,
    a: tuple,
    b: tuple
) -> tuple:
    """ apply function on two vectors and merge """
    return merge(papply(function, a, b))


def prapply(
    function,
    a: tuple | frozenset,
    b: tuple | frozenset
) -> frozenset:
    """ apply function on cartesian product """
    return frozenset(function(i, j) for j in b for i in a)


# --- merged: mostcolor + leastcolor ---

def extremecolor(
    element: tuple | frozenset,
    kind: str = 'most'
) -> int:
    """ most or least common color (kind: 'most' or 'least') """
    values = [v for r in element for v in r] if isinstance(element, tuple) else [v for v, _ in element]
    func = max if kind == 'most' else min
    return func(set(values), key=values.count)


def height(
    piece: tuple | frozenset
) -> int:
    """ height of grid or patch """
    if len(piece) == 0:
        return 0
    if isinstance(piece, tuple):
        return len(piece)
    return boundary(piece, 'bottom') - boundary(piece, 'top') + 1


def width(
    piece: tuple | frozenset
) -> int:
    """ width of grid or patch """
    if len(piece) == 0:
        return 0
    if isinstance(piece, tuple):
        return len(piece[0])
    return boundary(piece, 'right') - boundary(piece, 'left') + 1


def shape(
    piece: tuple | frozenset
) -> tuple:
    """ height and width of grid or patch """
    return (height(piece), width(piece))


def portrait(
    piece: tuple | frozenset
) -> bool:
    """ whether height is greater than width """
    return height(piece) > width(piece)


def colorcount(
    element: tuple | frozenset,
    value: int
) -> int:
    """ number of cells with color """
    if isinstance(element, tuple):
        return sum(row.count(value) for row in element)
    return sum(v == value for v, _ in element)


def colorfilter(
    objs: frozenset,
    value: int
) -> frozenset:
    """ filter objects by color """
    return frozenset(obj for obj in objs if next(iter(obj))[0] == value)


def sizefilter(
    container: tuple | frozenset,
    n: int
) -> frozenset:
    """ filter items by size """
    return frozenset(item for item in container if len(item) == n)


def asindices(
    grid: tuple
) -> frozenset:
    """ indices of all grid cells """
    return frozenset((i, j) for i in range(len(grid)) for j in range(len(grid[0])))


def ofcolor(
    grid: tuple,
    value: int
) -> frozenset:
    """ indices of all grid cells with value """
    return frozenset((i, j) for i, r in enumerate(grid) for j, v in enumerate(r) if v == value)


# --- merged: ulcorner + urcorner + llcorner + lrcorner ---

def corner(
    patch: frozenset,
    position: str = 'ul'
) -> tuple:
    """ corner index of patch (position: 'ul', 'ur', 'll', 'lr') """
    indices = toindices(patch)
    rows, cols = zip(*indices)
    row_funcs = {'ul': min, 'ur': min, 'll': max, 'lr': max}
    col_funcs = {'ul': min, 'ur': max, 'll': min, 'lr': max}
    return (row_funcs[position](rows), col_funcs[position](cols))


def crop(
    grid: tuple,
    start: tuple,
    dims: tuple
) -> tuple:
    """ subgrid specified by start and dimension """
    return tuple(r[start[1]:start[1]+dims[1]] for r in grid[start[0]:start[0]+dims[0]])


def toindices(
    patch: frozenset
) -> frozenset:
    """ indices of object cells """
    if len(patch) == 0:
        return frozenset()
    if isinstance(next(iter(patch))[1], tuple):
        return frozenset(index for value, index in patch)
    return patch


def recolor(
    value: int,
    patch: frozenset
) -> frozenset:
    """ recolor patch """
    return frozenset((value, index) for index in toindices(patch))


def shift(
    patch: frozenset,
    directions: tuple
) -> frozenset:
    """ shift patch """
    if len(patch) == 0:
        return patch
    di, dj = directions
    if isinstance(next(iter(patch))[1], tuple):
        return frozenset((value, (i + di, j + dj)) for value, (i, j) in patch)
    return frozenset((i + di, j + dj) for i, j in patch)


def normalize(
    patch: frozenset
) -> frozenset:
    """ moves upper left corner to origin """
    if len(patch) == 0:
        return patch
    return shift(patch, (-boundary(patch, 'top'), -boundary(patch, 'left')))


def dneighbors(
    loc: tuple
) -> frozenset:
    """ directly adjacent indices """
    return frozenset({(loc[0] - 1, loc[1]), (loc[0] + 1, loc[1]), (loc[0], loc[1] - 1), (loc[0], loc[1] + 1)})


def ineighbors(
    loc: tuple
) -> frozenset:
    """ diagonally adjacent indices """
    return frozenset({(loc[0] - 1, loc[1] - 1), (loc[0] - 1, loc[1] + 1), (loc[0] + 1, loc[1] - 1), (loc[0] + 1, loc[1] + 1)})


def neighbors(
    loc: tuple
) -> frozenset:
    """ adjacent indices """
    return dneighbors(loc) | ineighbors(loc)


def objects(
    grid: tuple,
    univalued: bool,
    diagonal: bool,
    without_bg: bool
) -> frozenset:
    """ objects occurring on the grid """
    bg = extremecolor(grid) if without_bg else None
    objs = set()
    occupied = set()
    h, w = len(grid), len(grid[0])
    unvisited = asindices(grid)
    diagfun = neighbors if diagonal else dneighbors
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
                        (i, j) for i, j in diagfun(cand) if 0 <= i < h and 0 <= j < w
                    }
            cands = neighborhood - occupied
        objs.add(frozenset(obj))
    return frozenset(objs)


# --- merged: partition + fgpartition ---

def partition(
    grid: tuple,
    without_bg: bool = False
) -> frozenset:
    """ partition grid by color (without_bg: exclude background color) """
    colors = palette(grid)
    if without_bg:
        colors = colors - {extremecolor(grid)}
    return frozenset(
        frozenset(
            (v, (i, j)) for i, r in enumerate(grid) for j, v in enumerate(r) if v == value
        ) for value in colors
    )


# --- merged: uppermost + lowermost + leftmost + rightmost ---

def boundary(
    patch: frozenset,
    side: str
) -> int:
    """ boundary index of patch (side: 'top', 'bottom', 'left', 'right') """
    indices = toindices(patch)
    if side == 'top':
        return min(i for i, j in indices)
    elif side == 'bottom':
        return max(i for i, j in indices)
    elif side == 'left':
        return min(j for i, j in indices)
    elif side == 'right':
        return max(j for i, j in indices)


def square(
    piece: tuple | frozenset
) -> bool:
    """ whether the piece forms a square """
    return len(piece) == len(piece[0]) if isinstance(piece, tuple) else height(piece) * width(piece) == len(piece) and height(piece) == width(piece)


# --- merged: vline + hline ---

def isline(
    patch: frozenset,
    axis: str = 'vertical'
) -> bool:
    """ whether patch forms a line (axis: 'vertical' or 'horizontal') """
    if axis == 'vertical':
        return height(patch) == len(patch) and width(patch) == 1
    else:
        return width(patch) == len(patch) and height(patch) == 1


# --- merged: hmatching + vmatching ---

def matching(
    a: frozenset,
    b: frozenset,
    axis: str = 'row'
) -> bool:
    """ whether patches share a row or column (axis: 'row' or 'column') """
    if axis == 'row':
        return len(set(i for i, j in toindices(a)) & set(i for i, j in toindices(b))) > 0
    else:
        return len(set(j for i, j in toindices(a)) & set(j for i, j in toindices(b))) > 0


def manhattan(
    a: frozenset,
    b: frozenset
) -> int:
    """ closest manhattan distance between two patches """
    return min(abs(ai - bi) + abs(aj - bj) for ai, aj in toindices(a) for bi, bj in toindices(b))


def adjacent(
    a: frozenset,
    b: frozenset
) -> bool:
    """ whether two patches are adjacent """
    return manhattan(a, b) == 1


def bordering(
    patch: frozenset,
    grid: tuple
) -> bool:
    """ whether a patch is adjacent to a grid border """
    return boundary(patch, 'top') == 0 or boundary(patch, 'left') == 0 or boundary(patch, 'bottom') == len(grid) - 1 or boundary(patch, 'right') == len(grid[0]) - 1


def centerofmass(
    patch: frozenset
) -> tuple:
    """ center of mass """
    return tuple(map(lambda x: sum(x) // len(patch), zip(*toindices(patch))))


def palette(
    element: tuple | frozenset
) -> frozenset:
    """ colors occurring in object or grid """
    if isinstance(element, tuple):
        return frozenset({v for r in element for v in r})
    return frozenset({v for v, _ in element})


def numcolors(
    element: tuple | frozenset
) -> int:
    """ number of colors occurring in object or grid """
    return len(palette(element))


def color(
    obj: frozenset
) -> int:
    """ color of object """
    return next(iter(obj))[0]


def toobject(
    patch: frozenset,
    grid: tuple
) -> frozenset:
    """ object from patch and grid """
    h, w = len(grid), len(grid[0])
    return frozenset((grid[i][j], (i, j)) for i, j in toindices(patch) if 0 <= i < h and 0 <= j < w)


def asobject(
    grid: tuple
) -> frozenset:
    """ conversion of grid to object """
    return frozenset((v, (i, j)) for i, r in enumerate(grid) for j, v in enumerate(r))


# --- merged: rot90 + rot180 + rot270 ---

def rotate(
    grid: tuple,
    angle: int = 90
) -> tuple:
    """ rotate grid clockwise (angle: 90, 180, 270) """
    if angle == 90:
        return tuple(row for row in zip(*grid[::-1]))
    elif angle == 180:
        return tuple(tuple(row[::-1]) for row in grid[::-1])
    elif angle == 270:
        return tuple(tuple(row[::-1]) for row in zip(*grid[::-1]))[::-1]
    return grid


# --- merged: hmirror + vmirror + dmirror + cmirror ---

def mirror(
    piece: tuple | frozenset,
    axis: str = 'horizontal'
) -> tuple | frozenset:
    """ mirror piece (axis: 'horizontal', 'vertical', 'diagonal', 'counterdiagonal') """
    if axis == 'horizontal':
        if isinstance(piece, tuple):
            return piece[::-1]
        d = corner(piece, 'ul')[0] + corner(piece, 'lr')[0]
        if isinstance(next(iter(piece))[1], tuple):
            return frozenset((v, (d - i, j)) for v, (i, j) in piece)
        return frozenset((d - i, j) for i, j in piece)
    elif axis == 'vertical':
        if isinstance(piece, tuple):
            return tuple(row[::-1] for row in piece)
        d = corner(piece, 'ul')[1] + corner(piece, 'lr')[1]
        if isinstance(next(iter(piece))[1], tuple):
            return frozenset((v, (i, d - j)) for v, (i, j) in piece)
        return frozenset((i, d - j) for i, j in piece)
    elif axis == 'diagonal':
        if isinstance(piece, tuple):
            return tuple(zip(*piece))
        a, b = corner(piece, 'ul')
        if isinstance(next(iter(piece))[1], tuple):
            return frozenset((v, (j - b + a, i - a + b)) for v, (i, j) in piece)
        return frozenset((j - b + a, i - a + b) for i, j in piece)
    elif axis == 'counterdiagonal':
        if isinstance(piece, tuple):
            return tuple(zip(*(r[::-1] for r in piece[::-1])))
        return mirror(mirror(mirror(piece, 'vertical'), 'diagonal'), 'vertical')


# --- merged: fill + underfill ---

def fill(
    grid: tuple,
    value: int,
    patch: frozenset,
    bg_only: bool = False
) -> tuple:
    """ fill value at indices (bg_only: only fill background cells) """
    h, w = len(grid), len(grid[0])
    bg = extremecolor(grid) if bg_only else None
    g = list(list(row) for row in grid)
    for i, j in toindices(patch):
        if 0 <= i < h and 0 <= j < w:
            if not bg_only or g[i][j] == bg:
                g[i][j] = value
    return tuple(tuple(row) for row in g)


# --- merged: paint + underpaint ---

def paint(
    grid: tuple,
    obj: frozenset,
    bg_only: bool = False
) -> tuple:
    """ paint object to grid (bg_only: only paint over background cells) """
    h, w = len(grid), len(grid[0])
    bg = extremecolor(grid) if bg_only else None
    g = list(list(row) for row in grid)
    for value, (i, j) in obj:
        if 0 <= i < h and 0 <= j < w:
            if not bg_only or g[i][j] == bg:
                g[i][j] = value
    return tuple(tuple(row) for row in g)


# --- merged: hupscale + vupscale ---

def axis_upscale(
    grid: tuple,
    factor: int,
    axis: str = 'horizontal'
) -> tuple:
    """ upscale grid along one axis (axis: 'horizontal' or 'vertical') """
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
    """ upscale object or grid """
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
        di_inv, dj_inv = corner(element, 'ul')
        di, dj = (-di_inv, -dj_inv)
        normed_obj = shift(element, (di, dj))
        o = set()
        for value, (i, j) in normed_obj:
            for io in range(factor):
                for jo in range(factor):
                    o.add((value, (i * factor + io, j * factor + jo)))
        return shift(frozenset(o), (di_inv, dj_inv))


def downscale(
    grid: tuple,
    factor: int
) -> tuple:
    """ downscale grid """
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


# --- merged: hconcat + vconcat ---

def concat(
    a: tuple,
    b: tuple,
    axis: str = 'horizontal'
) -> tuple:
    """ concatenate two grids (axis: 'horizontal' or 'vertical') """
    if axis == 'horizontal':
        return tuple(i + j for i, j in zip(a, b))
    else:
        return a + b


def subgrid(
    patch: frozenset,
    grid: tuple
) -> tuple:
    """ smallest subgrid containing object """
    return crop(grid, corner(patch, 'ul'), shape(patch))


# --- merged: hsplit + vsplit ---

def split(
    grid: tuple,
    n: int,
    axis: str = 'horizontal'
) -> tuple:
    """ split grid into n parts (axis: 'horizontal' or 'vertical') """
    if axis == 'horizontal':
        h, w = len(grid), len(grid[0]) // n
        offset = len(grid[0]) % n != 0
        return tuple(crop(grid, (0, w * i + i * offset), (h, w)) for i in range(n))
    else:
        h, w = len(grid) // n, len(grid[0])
        offset = len(grid) % n != 0
        return tuple(crop(grid, (h * i + i * offset, 0), (h, w)) for i in range(n))


def cellwise(
    a: tuple,
    b: tuple,
    fallback: int
) -> tuple:
    """ cellwise match of two grids """
    h, w = len(a), len(a[0])
    resulting_grid = tuple()
    for i in range(h):
        row = tuple()
        for j in range(w):
            a_value = a[i][j]
            value = a_value if a_value == b[i][j] else fallback
            row = row + (value,)
        resulting_grid = resulting_grid + (row, )
    return resulting_grid


def replace(
    grid: tuple,
    replacee: int,
    replacer: int
) -> tuple:
    """ color substitution """
    return tuple(tuple(replacer if v == replacee else v for v in r) for r in grid)


def switch(
    grid: tuple,
    a: int,
    b: int
) -> tuple:
    """ color switching """
    return tuple(tuple(v if (v != a and v != b) else {a: b, b: a}[v] for v in r) for r in grid)


def center(
    patch: frozenset
) -> tuple:
    """ center of the patch """
    return (boundary(patch, 'top') + height(patch) // 2, boundary(patch, 'left') + width(patch) // 2)


def position(
    a: frozenset,
    b: frozenset
) -> tuple:
    """ relative position between two patches """
    ia, ja = center(toindices(a))
    ib, jb = center(toindices(b))
    if ia == ib:
        return (0, 1 if ja < jb else -1)
    elif ja == jb:
        return (1 if ia < ib else -1, 0)
    elif ia < ib:
        return (1, 1 if ja < jb else -1)
    elif ia > ib:
        return (-1, 1 if ja < jb else -1)


def index(
    grid: tuple,
    loc: tuple
) -> int:
    """ color at location """
    i, j = loc
    h, w = len(grid), len(grid[0])
    if not (0 <= i < h and 0 <= j < w):
        return None
    return grid[loc[0]][loc[1]]


def canvas(
    value: int,
    dimensions: tuple
) -> tuple:
    """ grid construction """
    return tuple(tuple(value for j in range(dimensions[1])) for i in range(dimensions[0]))


def corners(
    patch: frozenset
) -> frozenset:
    """ indices of corners """
    return frozenset({corner(patch, pos) for pos in ('ul', 'ur', 'll', 'lr')})


def connect(
    a: tuple,
    b: tuple
) -> frozenset:
    """ line between two points """
    ai, aj = a
    bi, bj = b
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


def cover(
    grid: tuple,
    patch: frozenset
) -> tuple:
    """ remove object from grid """
    return fill(grid, extremecolor(grid), toindices(patch))


def trim(
    grid: tuple
) -> tuple:
    """ trim border of grid """
    return tuple(r[1:-1] for r in grid[1:-1])


def move(
    grid: tuple,
    obj: frozenset,
    offset: tuple
) -> tuple:
    """ move object on grid """
    return paint(cover(grid, obj), shift(obj, offset))


# --- merged: tophalf + bottomhalf + lefthalf + righthalf ---

def half(
    grid: tuple,
    side: str = 'top'
) -> tuple:
    """ half of grid (side: 'top', 'bottom', 'left', 'right') """
    if side == 'top':
        return grid[:len(grid) // 2]
    elif side == 'bottom':
        return grid[len(grid) // 2 + len(grid) % 2:]
    elif side == 'left':
        return rotate(half(rotate(grid, 90), 'top'), 270)
    elif side == 'right':
        return rotate(half(rotate(grid, 90), 'bottom'), 270)


# --- merged: vfrontier + hfrontier ---

def frontier(
    location: tuple,
    axis: str = 'vertical'
) -> frozenset:
    """ frontier line through location (axis: 'vertical' or 'horizontal') """
    if axis == 'vertical':
        return frozenset((i, location[1]) for i in range(30))
    else:
        return frozenset((location[0], j) for j in range(30))


def backdrop(
    patch: frozenset
) -> frozenset:
    """ indices in bounding box of patch """
    if len(patch) == 0:
        return frozenset({})
    indices = toindices(patch)
    si, sj = corner(indices, 'ul')
    ei, ej = corner(patch, 'lr')
    return frozenset((i, j) for i in range(si, ei + 1) for j in range(sj, ej + 1))


def delta(
    patch: frozenset
) -> frozenset:
    """ indices in bounding box but not part of patch """
    if len(patch) == 0:
        return frozenset({})
    return backdrop(patch) - toindices(patch)


def gravitate(
    source: frozenset,
    destination: frozenset
) -> tuple:
    """ direction to move source until adjacent to destination """
    si, sj = center(source)
    di, dj = center(destination)
    i, j = 0, 0
    if matching(source, destination, 'column'):
        i = 1 if si < di else -1
    else:
        j = 1 if sj < dj else -1
    gi, gj = i, j
    c = 0
    while not adjacent(source, destination) and c < 42:
        c += 1
        gi += i
        gj += j
        source = shift(source, (i, j))
    return (gi - i, gj - j)


# --- merged: inbox + outbox + box ---

def boundbox(
    patch: frozenset,
    delta: int = 0
) -> frozenset:
    """ bounding box outline with offset (delta: 0=exact, 1=inner, -1=outer) """
    if len(patch) == 0:
        return frozenset()
    ai = boundary(patch, 'top') + delta
    aj = boundary(patch, 'left') + delta
    bi = boundary(patch, 'bottom') - delta
    bj = boundary(patch, 'right') - delta
    si, sj = min(ai, bi), min(aj, bj)
    ei, ej = max(ai, bi), max(aj, bj)
    vlines = {(i, sj) for i in range(si, ei + 1)} | {(i, ej) for i in range(si, ei + 1)}
    hlines = {(si, j) for j in range(sj, ej + 1)} | {(ei, j) for j in range(sj, ej + 1)}
    return frozenset(vlines | hlines)


def shoot(
    start: tuple,
    direction: tuple
) -> frozenset:
    """ line from starting point and direction """
    return connect(start, (start[0] + 42 * direction[0], start[1] + 42 * direction[1]))


def occurrences(
    grid: tuple,
    obj: frozenset
) -> frozenset:
    """ locations of occurrences of object in grid """
    occs = set()
    normed = normalize(obj)
    h, w = len(grid), len(grid[0])
    oh, ow = shape(obj)
    h2, w2 = h - oh + 1, w - ow + 1
    for i in range(h2):
        for j in range(w2):
            occurs = True
            for v, (a, b) in shift(normed, (i, j)):
                if not (0 <= a < h and 0 <= b < w and grid[a][b] == v):
                    occurs = False
                    break
            if occurs:
                occs.add((i, j))
    return frozenset(occs)


def frontiers(
    grid: tuple
) -> frozenset:
    """ set of frontiers """
    h, w = len(grid), len(grid[0])
    row_indices = tuple(i for i, r in enumerate(grid) if len(set(r)) == 1)
    column_indices = tuple(j for j, c in enumerate(mirror(grid, 'diagonal')) if len(set(c)) == 1)
    hfrontiers = frozenset({frozenset({(grid[i][j], (i, j)) for j in range(w)}) for i in row_indices})
    vfrontiers = frozenset({frozenset({(grid[i][j], (i, j)) for i in range(h)}) for j in column_indices})
    return hfrontiers | vfrontiers


def compress(
    grid: tuple
) -> tuple:
    """ removes frontiers from grid """
    ri = tuple(i for i, r in enumerate(grid) if len(set(r)) == 1)
    ci = tuple(j for j, c in enumerate(mirror(grid, 'diagonal')) if len(set(c)) == 1)
    return tuple(tuple(v for j, v in enumerate(r) if j not in ci) for i, r in enumerate(grid) if i not in ri)


# --- merged: hperiod + vperiod ---

def period(
    obj: frozenset,
    axis: str = 'horizontal'
) -> int:
    """ periodicity along axis (axis: 'horizontal' or 'vertical') """
    normalized = normalize(obj)
    size = width(normalized) if axis == 'horizontal' else height(normalized)
    for p in range(1, size):
        if axis == 'horizontal':
            offsetted = shift(normalized, (0, -p))
            pruned = frozenset({(c, (i, j)) for c, (i, j) in offsetted if j >= 0})
        else:
            offsetted = shift(normalized, (-p, 0))
            pruned = frozenset({(c, (i, j)) for c, (i, j) in offsetted if i >= 0})
        if pruned.issubset(normalized):
            return p
    return size
