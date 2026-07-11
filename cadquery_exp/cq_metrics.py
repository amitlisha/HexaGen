"""Geometry metrics for comparing CadQuery shapes.

Both metrics operate on BREP strings produced by cq_executor.execute_cq(),
which have already been position- and scale-normalised.

Volumetric IoU
--------------
  IoU = Volume(A ∩ B) / Volume(A ∪ B)
  Range [0, 1]; 1 = identical shapes.
  Computed via exact OCC BRep boolean operations — no voxelisation needed.

Chamfer Distance
----------------
  CD = (mean d(A→B) + mean d(B→A)) / 2
  Lower = more similar; 0 = identical shapes.
  Computed from tessellated surface point clouds using scipy KDTree.
"""
from __future__ import annotations

import os
import tempfile
from typing import Dict, Optional

import numpy as np
from scipy.spatial import KDTree


# ---------------------------------------------------------------------------
# BREP deserialisation
# ---------------------------------------------------------------------------

def _load_shape(brep_str: str):
    """Deserialise a BREP string to an OCC TopoDS_Shape."""
    from OCP.BRep import BRep_Builder
    from OCP.BRepTools import BRepTools
    from OCP.TopoDS import TopoDS_Shape

    with tempfile.NamedTemporaryFile(suffix=".brep", delete=False, mode="w") as f:
        f.write(brep_str)
        fname = f.name
    shape = TopoDS_Shape()
    builder = BRep_Builder()
    BRepTools.Read_s(shape, fname, builder)
    os.unlink(fname)
    return shape


# ---------------------------------------------------------------------------
# Volumetric IoU
# ---------------------------------------------------------------------------

def volumetric_iou(brep_a: str, brep_b: str) -> float:
    """Volumetric IoU between two normalised BREP shapes.

    Returns a value in [0, 1] (1 = identical). Returns 0.0 if boolean
    operations fail or volumes are effectively zero.
    """
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Common, BRepAlgoAPI_Fuse
    from OCP.BRepGProp import BRepGProp
    from OCP.GProp import GProp_GProps

    shape_a = _load_shape(brep_a)
    shape_b = _load_shape(brep_b)

    try:
        inter_op = BRepAlgoAPI_Common(shape_a, shape_b)
        union_op = BRepAlgoAPI_Fuse(shape_a, shape_b)
        if not inter_op.IsDone() or not union_op.IsDone():
            return 0.0

        props = GProp_GProps()
        BRepGProp.VolumeProperties_s(inter_op.Shape(), props)
        v_inter = abs(props.Mass())
        BRepGProp.VolumeProperties_s(union_op.Shape(), props)
        v_union = abs(props.Mass())

        if v_union < 1e-12:
            return 0.0
        return float(min(1.0, v_inter / v_union))
    except Exception:
        return 0.0


# ---------------------------------------------------------------------------
# Chamfer distance
# ---------------------------------------------------------------------------

def _tessellate(shape, linear_deflection: float = 0.02) -> np.ndarray:
    """Tessellate an OCC shape and return an (N, 3) array of surface points."""
    from OCP.BRep import BRep_Tool
    from OCP.BRepMesh import BRepMesh_IncrementalMesh
    from OCP.TopAbs import TopAbs_FACE
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopLoc import TopLoc_Location
    from OCP.TopoDS import TopoDS_Face

    BRepMesh_IncrementalMesh(shape, linear_deflection)

    pts = []
    explorer = TopExp_Explorer(shape, TopAbs_FACE)
    while explorer.More():
        # Cast to TopoDS_Face so BRep_Tool.Triangulation_s accepts it
        cur = explorer.Current()
        face = TopoDS_Face()
        face.TShape(cur.TShape())
        face.Location(cur.Location())
        face.Orientation(cur.Orientation())

        loc = TopLoc_Location()
        tri = BRep_Tool.Triangulation_s(face, loc)
        if tri is not None:
            for i in range(1, tri.NbNodes() + 1):
                p = tri.Node(i)
                pts.append([p.X(), p.Y(), p.Z()])
        explorer.Next()

    return np.array(pts, dtype=np.float64) if pts else np.zeros((0, 3), dtype=np.float64)


def chamfer_distance(brep_a: str, brep_b: str, n_sample: int = 2048) -> float:
    """Symmetric Chamfer distance between two normalised BREP shapes.

    Tessellates both shapes, optionally subsamples, and computes:
        CD = (mean_d(A→B) + mean_d(B→A)) / 2

    Returns float('inf') if tessellation yields no points.
    """
    shape_a = _load_shape(brep_a)
    shape_b = _load_shape(brep_b)

    pts_a = _tessellate(shape_a)
    pts_b = _tessellate(shape_b)

    if len(pts_a) == 0 or len(pts_b) == 0:
        return float("inf")

    rng = np.random.default_rng(0)
    if len(pts_a) > n_sample:
        pts_a = pts_a[rng.choice(len(pts_a), n_sample, replace=False)]
    if len(pts_b) > n_sample:
        pts_b = pts_b[rng.choice(len(pts_b), n_sample, replace=False)]

    d_ab, _ = KDTree(pts_b).query(pts_a)
    d_ba, _ = KDTree(pts_a).query(pts_b)

    return float((d_ab.mean() + d_ba.mean()) / 2.0)


# ---------------------------------------------------------------------------
# Combined metric
# ---------------------------------------------------------------------------

def compute_metrics(brep_pred: str, brep_gold: str) -> Dict[str, float]:
    """Compute both metrics between a prediction and the gold shape.

    Returns dict with keys 'iou' and 'chamfer'.
    """
    return {
        "iou": volumetric_iou(brep_pred, brep_gold),
        "chamfer": chamfer_distance(brep_pred, brep_gold),
    }
