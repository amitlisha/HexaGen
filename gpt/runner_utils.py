from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Any, Dict, List
import ast
import traceback
import linecache
import multiprocessing as mp
import traceback
from typing import Tuple, List
import re
import uuid

from hexagen import Game

ROOT_DIR = Path(__file__).resolve().parent.parent
USER_FILE = "user_snippet.py"
DATA_DIR = ROOT_DIR / "data"
RUN_UID = uuid.uuid4()


def get_library_classes(lib_file: str) -> List[str]:
    """Extract public class names from a library file.

    Args:
        lib_file: Path to library file

    Returns:
        List of class names defined in the library (excluding private classes)
    """
    lib_path = Path(lib_file)
    if not lib_path.exists():
        raise FileNotFoundError(f"Library file not found: {lib_file}")

    lib_code = lib_path.read_text()

    # Parse the file to find class definitions
    import ast
    tree = ast.parse(lib_code)

    classes = []
    # Only look at top-level class definitions (node.body),
    # not nested classes inside methods (ast.walk would find those too)
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            # Only include public classes (not starting with _)
            if not node.name.startswith('_'):
                classes.append(node.name)

    return classes


def generate_import_statement(lib_file: str) -> str:
    """Generate the correct import statement for a library.

    Args:
        lib_file: Path to library file

    Returns:
        Import statement string, e.g. "from hexagen import Game, Tile, Shape"
    """
    classes = get_library_classes(lib_file)

    if not classes:
        # Fallback to default imports if no classes found
        return "from hexagen import Game, Tile, Shape, Line, Circle, Triangle"

    # Sort for consistency
    classes.sort()
    return f"from hexagen import {', '.join(classes)}"


def _inject_custom_lib(lib_file: str):
    """Inject a custom library file as the 'hexagen' module."""
    import sys
    import types

    lib_path = Path(lib_file)
    if not lib_path.exists():
        raise FileNotFoundError(f"Library file not found: {lib_file}")

    # Read and execute the library code
    lib_code = lib_path.read_text()
    lib_module = types.ModuleType("hexagen")
    lib_module.__file__ = str(lib_path)

    # Execute library code in the module's namespace
    exec(compile(lib_code, str(lib_path), "exec"), lib_module.__dict__)

    # Inject into sys.modules so 'from hexagen import ...' works
    sys.modules["hexagen"] = lib_module


def _timeout_worker(code: str, q, lib_file: str = None):
    """Executes `code` and returns ('ok', board_state) or ('err', traceback)."""
    try:
        # Inject custom library if provided
        if lib_file:
            _inject_custom_lib(lib_file)

        ns = {}
        exec_snippet(code, ns)
        q.put(("ok", ns.get("board_state")))
    except Exception as exc:
        q.put(("err", format_user_tb(exc)))


def timestamp() -> str:
    return time.strftime("%Y-%m-%dT%H-%M-%S", time.localtime())


def ensure_task_dir(experiment_name: str, task_id: int) -> Path:
    path = get_results_dir_path(experiment_name) / f"task_{task_id}"
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_json(obj: Dict[str, Any], path: Path) -> None:
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False))


def extract_code(raw: str) -> str:
    """Extract code from LLM response, removing imports and Game context."""
    m = re.search(r"```(?:python)?\s*([\s\S]+?)```", raw, re.I)
    src = m.group(1) if m else raw

    w = re.search(r"\bwith\s+Game\(\)\s+as\s+g\s*:\s*", src)
    body = src[w.end() :] if w else src
    if body.startswith("\n"):
        body = body[1:]

    lines = [
        ln
        for ln in body.splitlines()
        if not re.match(r"\s*(?:from\s+\S+\s+import|import\s+\S+)", ln)
        and not re.search(r"\bwith\s+Game\(\)\s+as\s+g\s*:\s*", ln)
    ]
    return "\n".join(lines).rstrip("\n")


def prepend_imports_and_context(code: str, lib_file: str = "hexagen/hexagen.py") -> str:
    """Prepend import statement and Game context to code.

    Args:
        code: Code snippet (without imports/context)
        lib_file: Path to library file (to determine what to import)

    Returns:
        Complete executable code with imports and Game context
    """
    import_stmt = generate_import_statement(lib_file)

    return f"""{import_stmt}

with Game() as g:
{code}"""


def save_plot(
    board_state: List[int], gold_board: List[int] | List[List[int]], out: Path
) -> None:
    """Plot board vs. gold and save PNG."""
    with Game() as g:
        g.board_state = board_state.copy()
        if gold_board:
            g.plot(
                gold_boards=gold_board, multiple=False, file_name=str(out), show=False
            )
        else:
            g.plot(multiple=False, file_name=str(out), show=False)


def parse_tile_actions(raw: str) -> Tuple[Optional[Tuple[int, int]], List[Tuple[int, int, any]]]:
    """Parse tile actions from raw model output.

    For LARC: First tuple is (height, width), rest are (row, col, color) with int colors
    For Hexagons: No dimensions, just (row, col, color) with string colors

    Returns:
        Tuple of (dimensions, tiles)
        - dimensions: (height, width) for LARC, None for Hexagons
        - tiles: List of (row, col, color) tuples
    """
    raw = raw.strip()
    try:
        data = ast.literal_eval(raw)
        if isinstance(data, Tuple):
            data = [data]
        if isinstance(data, list) and len(data) > 0:
            dimensions = None
            tiles = []

            # Check if first tuple is dimensions (LARC format)
            first_item = data[0]
            start_idx = 0

            if isinstance(first_item, (list, Tuple)) and len(first_item) == 2:
                # Could be dimensions (height, width) or a tile (row, col) without color
                # Dimensions are always at index 0 and both values should be positive integers
                if all(isinstance(x, int) and x > 0 for x in first_item):
                    # Check if this looks like dimensions vs a partial tile
                    # If there are more tuples and they have 3 elements, first is likely dimensions
                    if len(data) > 1 and isinstance(data[1], (list, Tuple)) and len(data[1]) == 3:
                        dimensions = (int(first_item[0]), int(first_item[1]))
                        start_idx = 1

            # Parse remaining tiles
            for item in data[start_idx:]:
                if isinstance(item, (list, Tuple)) and len(item) == 3:
                    r, c, col = item
                    # Preserve int colors (LARC), convert string colors to lowercase (Hexagons)
                    if isinstance(col, int):
                        tiles.append((int(r), int(c), col))
                    else:
                        tiles.append((int(r), int(c), str(col).lower()))

            if tiles:
                return dimensions, tiles
    except Exception:
        pass

    # Fallback regex for Hexagons color names
    pattern = r"\(\s*(\d+)\s*,\s*(\d+)\s*,\s*['\"]?([a-zA-Z]+)['\"]?\s*\)"
    tiles = [(int(r), int(c), col.lower()) for r, c, col in re.findall(pattern, raw)]
    return None, tiles


def format_user_tb(exc: BaseException, user_file: str = USER_FILE) -> str:
    """Return only the traceback frames that belong to the compiled user snippet."""
    tb = exc.__traceback__
    # Skip frames until we reach the snippet we compiled ourselves
    while tb and tb.tb_frame.f_code.co_filename != user_file:
        tb = tb.tb_next
    return "".join(traceback.format_exception(type(exc), exc, tb))


def exec_snippet(src: str, globals_ns: dict, filename: str = "user_snippet.py"):
    """Execute `src` so that tracebacks include the actual source lines."""
    linecache.cache[filename] = (
        len(src),  # length of source
        None,  # mtime (None = unknown / don’t check file)
        src.splitlines(True),  # list of lines *with* \n
        filename,
    )
    exec(compile(src, filename, "exec"), globals_ns)


import multiprocessing as mp


def run_with_timeout(
    src: str,
    timeout_sec: int = 10,
    lib_file: str = None,
):
    ctx = mp.get_context("spawn")
    q = ctx.Queue()
    p = ctx.Process(target=_timeout_worker, args=(src, q, lib_file), daemon=True)
    p.start()
    p.join(timeout_sec)

    if p.is_alive():
        p.terminate()
        p.join()
        return None, "TIMEOUT"

    status, payload = q.get()
    return (payload, None) if status == "ok" else (None, payload)


def save_script(
    out_dir: Path, run_ts: str, step: int, attempt: int, code: str, kind: str = "step"
) -> Path:
    path = out_dir / f"{run_ts}_{kind}_{step:02}_{attempt:02}.py"
    path.write_text(code, encoding="utf-8")
    return path


def fix_missing_tail_indent(
    src: str,
    anchor_pattern=r"^\s*with\s+Game\(\)\s+as\s+g\s*:\s*$",
    indent_unit: str = "    ",
) -> str:
    lines = src.splitlines()
    if not lines:
        return src

    anchor_idx = next(
        (i for i, l in enumerate(lines) if re.match(anchor_pattern, l)), None
    )
    if anchor_idx is None:
        return src

    triggered = False
    for i in range(anchor_idx + 1, len(lines)):
        line = lines[i]
        if not line.strip():
            continue
        if not triggered and not line.startswith(indent_unit):
            triggered = True
        if triggered:
            lines[i] = indent_unit + line  # prepend, no stripping

    return "\n".join(lines)


def get_results_dir_path(experiment_name: str):
    return ROOT_DIR / f"results-{experiment_name}-{RUN_UID}"
