"""CadQuery subprocess executor with timeout.

Each call to execute_cq() spawns a fresh process (mp.get_context('spawn')),
executes the given CadQuery code inside it, extracts the 'result' variable,
normalises the shape (centred at origin, bounding-box diagonal = 1), and
serialises it as a BREP string for transport back to the caller.

Failures (syntax errors, runtime errors, timeout, missing 'result') are
captured and returned as an error string; they never abort the calling process.

Mirrors the run_with_timeout / _timeout_worker pattern in gpt/runner_utils.py.
For condition (b), the user's abstraction layer is injected as a named module
before the generated code is exec'd — mirroring _inject_custom_lib in
runner_utils.py.
"""
from __future__ import annotations

import math
import multiprocessing as mp
import os
import re
import sys
import tempfile
import traceback
from pathlib import Path
from typing import Optional, Tuple


# ---------------------------------------------------------------------------
# Helpers that run inside the subprocess
# ---------------------------------------------------------------------------

def _strip_side_effects(code: str) -> str:
    """Remove lines that write files or call show() — safe to drop from gold code."""
    out = []
    for line in code.splitlines():
        # Match both `cq.exporters.export(` and bare `exporters.export(`
        if re.search(r"(?:cq\.)?exporters\.export\s*\(", line):
            continue
        if re.search(r"\bshow\s*\(", line):
            continue
        out.append(line)
    return "\n".join(out)


def _extract_from_markdown(raw: str) -> str:
    """Pull code out of a ```python ... ``` fence if present."""
    m = re.search(r"```(?:python)?\s*([\s\S]+?)```", raw, re.IGNORECASE)
    return m.group(1).strip() if m else raw.strip()


def _inject_module(module_name: str, file_path: str) -> None:
    """Inject a Python file as a named module into sys.modules.

    Mirrors gpt/runner_utils._inject_custom_lib.
    """
    import types

    path = Path(file_path)
    code = path.read_text()
    mod = types.ModuleType(module_name)
    mod.__file__ = file_path
    exec(compile(code, file_path, "exec"), mod.__dict__)
    sys.modules[module_name] = mod


def _normalize_shape(shape, BRepBndLib, Bnd_Box, BRepGProp, GProp_GProps,
                     BRepBuilderAPI_Transform, gp_Trsf, gp_Vec, gp_Pnt):
    """Translate shape centroid to origin and scale bounding-box diagonal to 1."""
    # Centre of mass → translate to origin
    props = GProp_GProps()
    BRepGProp.VolumeProperties_s(shape, props)
    cm = props.CentreOfMass()

    t1 = gp_Trsf()
    t1.SetTranslation(gp_Vec(-cm.X(), -cm.Y(), -cm.Z()))
    shape = BRepBuilderAPI_Transform(shape, t1, True).Shape()

    # Bounding-box diagonal → scale to 1
    box = Bnd_Box()
    BRepBndLib.Add_s(shape, box)
    xmin, ymin, zmin, xmax, ymax, zmax = box.Get()
    diag = math.sqrt((xmax - xmin) ** 2 + (ymax - ymin) ** 2 + (zmax - zmin) ** 2)

    if diag > 1e-9:
        t2 = gp_Trsf()
        t2.SetScale(gp_Pnt(0.0, 0.0, 0.0), 1.0 / diag)
        shape = BRepBuilderAPI_Transform(shape, t2, True).Shape()

    return shape


def _cq_worker(code: str, queue: mp.Queue, abstraction_layer_path: Optional[str]) -> None:
    """Worker executed in a spawned subprocess.

    Puts ('ok', brep_str) or ('err', error_text) onto queue.
    """
    try:
        import cadquery as cq
        from OCP.BRepBndLib import BRepBndLib
        from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
        from OCP.BRepGProp import BRepGProp
        from OCP.BRepTools import BRepTools
        from OCP.Bnd import Bnd_Box
        from OCP.GProp import GProp_GProps
        from OCP.gp import gp_Pnt, gp_Trsf, gp_Vec

        # Inject abstraction layer for condition (b)
        if abstraction_layer_path:
            layer_name = Path(abstraction_layer_path).stem
            _inject_module(layer_name, abstraction_layer_path)

        # Execute the CadQuery program
        ns: dict = {"cq": cq}
        exec(compile(code, "user_cq.py", "exec"), ns)

        # Try common names first, then fall back to the last Workplane in ns
        _PRIORITY = ("result", "assembly", "final_result", "final_assembly",
                     "final_part", "part", "solid", "shape", "model", "body")
        result = None
        for _name in _PRIORITY:
            if _name in ns and ns[_name] is not None:
                result = ns[_name]
                break
        if result is None:
            # Last-resort: find the last variable assigned a cq.Workplane
            for _val in reversed(list(ns.values())):
                if isinstance(_val, cq.Workplane):
                    result = _val
                    break
        if result is None:
            queue.put(("err", "Code executed but no result variable found"))
            return

        # Extract OCC shape
        if hasattr(result, "val"):
            occ_shape = result.val().wrapped
        elif hasattr(result, "wrapped"):
            occ_shape = result.wrapped
        else:
            queue.put(("err", f"Cannot extract OCC shape from type {type(result).__name__}"))
            return

        # Normalise: centre + unit diagonal
        occ_shape = _normalize_shape(
            occ_shape,
            BRepBndLib, Bnd_Box, BRepGProp, GProp_GProps,
            BRepBuilderAPI_Transform, gp_Trsf, gp_Vec, gp_Pnt,
        )

        # Serialise as BREP string via a temp file
        with tempfile.NamedTemporaryFile(suffix=".brep", delete=False) as f:
            fname = f.name
        BRepTools.Write_s(occ_shape, fname)
        with open(fname) as f:
            brep_str = f.read()
        os.unlink(fname)

        queue.put(("ok", brep_str))

    except Exception:
        queue.put(("err", traceback.format_exc()))


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def execute_cq(
    code: str,
    timeout: int = 30,
    abstraction_layer_path: Optional[str] = None,
    from_llm: bool = False,
) -> Tuple[Optional[str], Optional[str]]:
    """Execute CadQuery code in an isolated subprocess with a timeout.

    Parameters
    ----------
    code:
        The CadQuery program to execute. Must assign the final shape to a
        variable named ``result``.
    timeout:
        Wall-clock seconds before the subprocess is killed.
    abstraction_layer_path:
        Path to the abstraction layer .py file (condition b). If given, the
        file is injected as a module named after its stem before the code runs.
    from_llm:
        If True, first attempt to unwrap a ```python``` code fence, then strip
        side-effect lines. For gold code set False (already clean-ish).

    Returns
    -------
    (brep_str, None)   on success — normalised shape as BREP text
    (None, error_msg)  on failure — human-readable error / 'TIMEOUT'
    """
    if from_llm:
        code = _extract_from_markdown(code)
    code = _strip_side_effects(code)

    ctx = mp.get_context("spawn")
    q = ctx.Queue()
    p = ctx.Process(target=_cq_worker, args=(code, q, abstraction_layer_path), daemon=True)
    p.start()
    p.join(timeout)

    if p.is_alive():
        p.terminate()
        p.join()
        return None, "TIMEOUT"

    try:
        status, payload = q.get(timeout=5)
    except Exception:
        return None, "Worker process died without returning a result"

    if status == "ok":
        return payload, None
    return None, payload
