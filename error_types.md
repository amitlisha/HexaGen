# Error Types

## spatial_reasoning
Fails to compute positions, directions, distances, or geometric relationships on the hex grid. Includes coordinate resolution, relative placement, and transformations. E.g. off-by-one, wrong direction, mirroring errors, misplaced shapes.

## compositional_reasoning
Fails to build complex structures from simpler parts or chain multiple steps together. Includes pattern repetition, cross-step references, and multi-object assembly. E.g. "repeat steps 1–3", "starting with the cell from step 3", "X of flowers".

## instruction_misunderstanding
Correctly reasons spatially but misinterprets what the instruction is asking for. E.g. wrong shape type, wrong color, wrong target object.

## hexagen_misuse
The model's spatial and compositional reasoning is correct but it uses a HexaGen API method in a seemingly logical way that produces wrong results due to the method's actual implementation. **Only applies to code experiments.**

## execution_failure
Mechanically fails to produce valid output. Code crash, syntax error, or unparseable tiles. Not a reasoning failure.
