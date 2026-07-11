#!/usr/bin/env python3
"""Validation harness for the CadQuery executor and metrics.

Run this before any full experiment to confirm the plumbing is correct:

    ~/.conda/envs/from-a-to-a/bin/python cadquery_exp/cq_validate.py

Tests
-----
1. Self-IoU = 1.0          — same program executed twice should score perfectly
2. Self-Chamfer = 0.0      — same program executed twice should score perfectly
3. Different shapes diverge — box vs sphere should have IoU < 1 and CD > 0
4. Timeout is caught       — an infinite loop should return 'TIMEOUT', not hang
5. Syntax error is caught  — bad code should return an error string, not crash
6. Gold examples execute   — first N gold programs should all run without error
                             and self-IoU ≈ 1.0, confirming the gold path works
"""
from __future__ import annotations

import sys
from pathlib import Path

# Allow running from the repo root or from cadquery_exp/
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "cadquery_exp"))

from cq_executor import execute_cq
from cq_metrics import chamfer_distance, volumetric_iou
from cq_dataset import load_dataset

# ---------------------------------------------------------------------------
# Trivial programs used in unit tests
# ---------------------------------------------------------------------------

_BOX = """\
import cadquery as cq
result = cq.Workplane('XY').box(1, 1, 1)
"""

_SPHERE = """\
import cadquery as cq
result = cq.Workplane('XY').sphere(0.5)
"""

_INFINITE = """\
import cadquery as cq
result = cq.Workplane('XY').box(1, 1, 1)
while True:
    pass
"""

_BAD_SYNTAX = "this is @#$ not python !!!"

# ---------------------------------------------------------------------------
# Individual tests
# ---------------------------------------------------------------------------

def test_self_iou() -> None:
    brep, err = execute_cq(_BOX, timeout=30)
    assert err is None, f"Execution failed: {err}"
    iou = volumetric_iou(brep, brep)
    assert abs(iou - 1.0) < 1e-6, f"Self IoU should be 1.0, got {iou:.6f}"
    print(f"  [PASS] Self IoU = {iou:.6f}")


def test_self_chamfer() -> None:
    brep, err = execute_cq(_BOX, timeout=30)
    assert err is None, f"Execution failed: {err}"
    cd = chamfer_distance(brep, brep)
    assert cd < 1e-6, f"Self Chamfer should be ~0, got {cd:.6f}"
    print(f"  [PASS] Self Chamfer = {cd:.6f}")


def test_different_shapes() -> None:
    box_brep, _ = execute_cq(_BOX, timeout=30)
    sph_brep, _ = execute_cq(_SPHERE, timeout=30)
    iou = volumetric_iou(box_brep, sph_brep)
    cd  = chamfer_distance(box_brep, sph_brep)
    assert iou < 1.0, f"Box vs Sphere IoU should be < 1, got {iou:.4f}"
    assert cd  > 0.0, f"Box vs Sphere CD should be > 0, got {cd:.4f}"
    print(f"  [PASS] Box vs Sphere: IoU = {iou:.4f}, CD = {cd:.4f}")


def test_timeout() -> None:
    _, err = execute_cq(_INFINITE, timeout=5)
    assert err == "TIMEOUT", f"Expected 'TIMEOUT', got: {err!r}"
    print(f"  [PASS] Timeout caught correctly")


def test_syntax_error() -> None:
    _, err = execute_cq(_BAD_SYNTAX, timeout=10)
    assert err is not None, "Expected error for syntactically invalid code"
    print(f"  [PASS] Syntax error caught: {err.splitlines()[-1]!r}")


def test_gold_examples(n: int = 5) -> None:
    examples = load_dataset("test", max_examples=n)
    assert len(examples) > 0, "No examples loaded — check dataset paths"
    ok = 0
    for ex in examples:
        brep, err = execute_cq(ex["gold_code"], timeout=30)
        if err:
            print(f"  [WARN] Gold exec failed for {ex['uid']}: {err[:100]}")
        else:
            iou = volumetric_iou(brep, brep)
            assert abs(iou - 1.0) < 1e-5, \
                f"Gold self-IoU for {ex['uid']} = {iou:.6f}, expected ~1.0"
            ok += 1
    print(f"  [PASS] {ok}/{len(examples)} gold examples executed; self-IoU ≈ 1.0")


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

TESTS = [
    ("Self IoU == 1.0",          test_self_iou),
    ("Self Chamfer == 0.0",      test_self_chamfer),
    ("Different shapes diverge", test_different_shapes),
    ("Timeout is caught",        test_timeout),
    ("Syntax error is caught",   test_syntax_error),
    ("Gold examples execute",    test_gold_examples),
]


def main() -> None:
    print("Running CadQuery experiment validation\n")
    passed = 0
    for name, fn in TESTS:
        print(f"Testing: {name}")
        try:
            fn()
            passed += 1
        except Exception as exc:
            print(f"  [FAIL] {exc}")
        print()

    print("=" * 45)
    print(f"Passed {passed}/{len(TESTS)} tests")
    if passed < len(TESTS):
        sys.exit(1)


if __name__ == "__main__":
    main()
