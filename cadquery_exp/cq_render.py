"""Multi-view PNG rendering for normalised BREP shapes.

Mirrors the "multi-view images" step of the Text2CAD GPT-4V evaluation
protocol (paper Section 3 / Fig. 2), but renders locally via matplotlib
instead of Blender — headless-safe, no GPU or Xvfb required, so it can run
on the same machines as the rest of cadquery_exp.

Verified against the `from-a-to-a` conda env (cadquery 2.7.0): OCP's
Poly_Triangle.Get() returns a plain (n1, n2, n3) tuple of 1-based node
indices, consumed directly below.
"""
from __future__ import annotations

from pathlib import Path
from typing import List

import numpy as np

from cq_metrics import _load_shape  # reuse BREP deserialisation

# Canonical camera angles (elevation, azimuth in degrees), mirroring
# Text2CAD's "predetermined camera angles" for multi-view rendering.
VIEWS = [
    ("iso_front", 25, 45),
    ("iso_back", 25, 225),
    ("top", 89, 0),
    ("front", 0, 0),
]


def _triangulate(shape, linear_deflection: float = 0.02) -> np.ndarray:
    """Tessellate an OCC shape into an (N, 3, 3) array of triangle vertices."""
    from OCP.BRep import BRep_Tool
    from OCP.BRepMesh import BRepMesh_IncrementalMesh
    from OCP.TopAbs import TopAbs_FACE
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopLoc import TopLoc_Location
    from OCP.TopoDS import TopoDS_Face

    BRepMesh_IncrementalMesh(shape, linear_deflection)

    triangles: List[np.ndarray] = []
    explorer = TopExp_Explorer(shape, TopAbs_FACE)
    while explorer.More():
        cur = explorer.Current()
        face = TopoDS_Face()
        face.TShape(cur.TShape())
        face.Location(cur.Location())
        face.Orientation(cur.Orientation())

        loc = TopLoc_Location()
        tri = BRep_Tool.Triangulation_s(face, loc)
        if tri is not None:
            nodes = [tri.Node(i) for i in range(1, tri.NbNodes() + 1)]
            pts = [np.array([p.X(), p.Y(), p.Z()]) for p in nodes]
            for i in range(1, tri.NbTriangles() + 1):
                n1, n2, n3 = tri.Triangle(i).Get()
                triangles.append(np.stack([pts[n1 - 1], pts[n2 - 1], pts[n3 - 1]]))
        explorer.Next()

    return np.stack(triangles) if triangles else np.zeros((0, 3, 3))


_LIGHT_DIR = np.array([0.4, -0.5, 0.75])
_BASE_RGB = np.array([0.29, 0.56, 0.64])  # #4a90a4


def _shade_triangles(tris: np.ndarray) -> np.ndarray:
    """Per-triangle Lambertian shading against a fixed world-space light.

    Gives faces at different orientations visibly different brightness so a
    flat vs. slanted face reads as different in the render — without ever
    drawing triangle-edge outlines, which previously showed up as a fake
    diagonal "cut" across every tessellated flat face and led a VLM judge
    to (reasonably, given what it was shown) mistake plain boxes for wedges.
    """
    v0, v1, v2 = tris[:, 0], tris[:, 1], tris[:, 2]
    normals = np.cross(v1 - v0, v2 - v0)
    norms = np.linalg.norm(normals, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    normals = normals / norms

    light = _LIGHT_DIR / np.linalg.norm(_LIGHT_DIR)
    # abs(): shade front- and back-facing triangles the same way (normals
    # aren't consistently oriented after tessellation); floor keeps faces
    # perpendicular to the light from rendering as pure black.
    intensity = np.clip(np.abs(normals @ light), 0.35, 1.0)
    rgb = np.clip(np.outer(intensity, _BASE_RGB), 0, 1)
    return np.hstack([rgb, np.ones((len(tris), 1))])


def render_views(brep_str: str, out_dir: Path, prefix: str = "view") -> List[Path]:
    """Render canonical multi-view PNGs of a normalised BREP shape.

    `brep_str` is expected to already be centred and unit-diagonal-scaled
    (as produced by cq_executor.execute_cq), so a fixed axis range works
    for every shape without per-shape auto-scaling.

    Returns the list of written PNG paths, one per entry in VIEWS.
    """
    # Object-oriented Figure/Canvas API only — no matplotlib.pyplot import,
    # since pyplot's global figure registry (Gcf) isn't guaranteed
    # thread-safe and this is called concurrently from cq_compare.py's
    # worker pool. Figure()/FigureCanvasAgg() here are entirely local
    # objects with no shared global state between threads.
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    from matplotlib.figure import Figure
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection

    out_dir.mkdir(parents=True, exist_ok=True)
    shape = _load_shape(brep_str)
    tris = _triangulate(shape)

    paths = []
    for name, elev, azim in VIEWS:
        fig = Figure(figsize=(3, 3), dpi=100)
        FigureCanvasAgg(fig)
        ax = fig.add_subplot(projection="3d")
        if len(tris) > 0:
            mesh = Poly3DCollection(
                tris, facecolor=_shade_triangles(tris), edgecolor="none", antialiased=False
            )
            ax.add_collection3d(mesh)
        ax.set_xlim(-0.6, 0.6)
        ax.set_ylim(-0.6, 0.6)
        ax.set_zlim(-0.6, 0.6)
        ax.set_box_aspect((1, 1, 1))
        ax.set_axis_off()
        ax.view_init(elev=elev, azim=azim)

        out_path = out_dir / f"{prefix}_{name}.png"
        fig.savefig(out_path, bbox_inches="tight")
        paths.append(out_path)

    return paths
