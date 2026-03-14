# Error Types

## pattern_generalization
The model fails to extrapolate, repeat, or extend a spatial pattern. Examples: “repeat steps 1–3”, “tile the pattern across the board”, “draw more triangles leaving a gap each time”, alternating patterns.

## spatial_reference_resolution
The model fails to resolve complex coordinate references or relative positions. Examples: “5th from bottom”, “9th column from the right”, “counting from the right”, mixing up row vs column, off-by-one in index calculation, wrong anchor point.

## shape_composition
The model fails to compose an abstract shape from primitive elements. Examples: “make an X of flowers”, “draw a hollow hexagon”, “V-shaped line”, “concentric circles”, “triangle pointing right”. The shape concept is understood but the spatial assembly is wrong.

## relational_reasoning
The model fails to reason about relationships between objects or regions. Examples: “all tiles adjacent to TWO black tiles”, “tiles touching the cluster”, “connect the two points from previous steps”, “fill between the lines”.

## geometric_transformation
The model fails to apply a geometric transformation correctly. Examples: symmetry/mirroring, filling a region bounded by existing shapes, “leaving the green line intact” (overwriting), rotating a pattern, scaling a shape up or down.

## counting_and_arithmetic
The model fails at precise counting, intervals, or arithmetic over tile positions. Examples: “every other spot”, “skip one column then repeat 3 times”, drawing a line of 9 tiles but getting 7, wrong number of repetitions.

## multi_step_dependency
The model fails to correctly chain steps where later steps depend on earlier results. Examples: “starting with the cell in line with step 3”, “color all remaining tiles”, references to “the tiles you just drew” that are resolved incorrectly.

## other
Use this ONLY if the error genuinely does not fit any of the above categories. Provide a specific description of what type of abstract reasoning failed.