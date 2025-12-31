# Standard Data Format for Library Generation

## Overview

The library generation system expects data in a standardized JSONL format. This format supports both:
- **Stateless tasks**: instruction → output (e.g., drawing from blank canvas)
- **Stateful tasks**: instruction + input → output (e.g., modifying existing state)

## Required Format

Each line in the JSONL file must be a JSON object representing one **task** (which may contain multiple steps):

```json
{
  "task_id": "unique_identifier",
  "steps": [
    {
      "instruction": "instruction text",
      "input_state": [...],  // Optional: state before this step
      "output_state": [...]  // Required: state after this step
    }
  ]
}
```

### Fields

#### Task Level
- **task_id** (string, required): Unique identifier for this task
- **steps** (list of objects, required): Sequence of steps in this task

#### Step Level
- **instruction** (string, required): Natural language instruction for this step
- **output_state** (any, required): Expected state/output after executing this instruction
- **input_state** (any, optional): State before this instruction
  - If omitted, assumes starting from initial/empty state
  - For step N>0, if omitted, assumed to be step N-1's output_state

### Examples

#### Example 1: Stateless Drawing (Hexagons-style)

```json
{
  "task_id": "hex_001",
  "steps": [
    {
      "instruction": "Draw a red tile at row 5, column 7",
      "output_state": [0, 0, 0, ..., 4, 0, ...]
    },
    {
      "instruction": "Draw neighbors in blue",
      "output_state": [0, 0, 5, ..., 4, 5, ...]
    }
  ]
}
```

#### Example 2: Stateful Transformation

```json
{
  "task_id": "edit_001",
  "steps": [
    {
      "instruction": "Change all red pixels to blue",
      "input_state": {"grid": [[255, 0, 0], [255, 0, 0]]},
      "output_state": {"grid": [[0, 0, 255], [0, 0, 255]]}
    }
  ]
}
```

#### Example 3: Robot Control

```json
{
  "task_id": "robot_001",
  "steps": [
    {
      "instruction": "Move forward 3 steps",
      "input_state": {"x": 0, "y": 0, "facing": "north"},
      "output_state": {"x": 0, "y": 3, "facing": "north"}
    },
    {
      "instruction": "Turn right and move forward 2 steps",
      "output_state": {"x": 2, "y": 3, "facing": "east"}
    }
  ]
}
```

## Optional Fields

You can include additional metadata:

```json
{
  "task_id": "task_001",
  "metadata": {
    "category": "simple",
    "difficulty": 1,
    "source": "human_annotation"
  },
  "steps": [...]
}
```

## State Format

The `input_state` and `output_state` fields can be **any JSON-serializable format** appropriate for your domain:

- **Flat list**: `[0, 0, 4, 5, 0, ...]` (e.g., hexagons board)
- **2D array**: `[[0, 1], [1, 0]]` (e.g., grid)
- **Object**: `{"position": [3, 5], "inventory": ["key"]}` (e.g., game state)
- **String**: `"RGBRGB"` (e.g., color sequence)

The library generation system will analyze instruction-state pairs to discover needed operations.

## Why This Format?

1. **General**: Works for any domain (drawing, robotics, data transformation, games, etc.)
2. **Explicit states**: LLM can see input/output relationships
3. **Step-by-step**: Supports multi-step tasks naturally
4. **Implicit chaining**: Steps inherit previous state if not specified
5. **Simple**: Easy to generate from any source dataset

## Usage in Library Generation

### Stage 1: API Discovery
The LLM will analyze:
- **Instructions**: What operations are requested?
- **State changes**: How do states transform?
- **Patterns**: What recurring transformations appear?

Example analysis:
```
Instruction: "Draw neighbors in blue"
Input:  [0, 0, 0, 4, 0, 0]  (one red tile)
Output: [0, 5, 5, 4, 5, 0]  (red + blue neighbors)
→ Need operation to find neighbors of a tile
```

### Stage 5: Validation
The system will:
1. Give LLM the instruction + input_state
2. Execute generated code
3. Compare output to expected output_state
4. Measure correctness (exact match, F1, etc.)

## Creating Preprocessors

If your dataset has a different format, create a preprocessor:

```python
# preprocess_mydataset.py
import json

def preprocess(input_file: str, output_file: str):
    with open(input_file) as f_in, open(output_file, 'w') as f_out:
        for line in f_in:
            old_obj = json.loads(line)

            # Convert to standard format
            new_obj = {
                "task_id": old_obj["id"],
                "steps": []
            }

            for step in old_obj["procedure"]:
                new_obj["steps"].append({
                    "instruction": step["text"],
                    "input_state": step.get("before"),  # Optional
                    "output_state": step["after"]
                })

            f_out.write(json.dumps(new_obj) + '\n')
```

See `preprocess_hexagons.py` for a complete example with the Hexagons dataset.

## Validation Requirements

For validation (Stage 5), you must provide:
- `output_state` for each step (required for correctness checking)
- Optionally `input_state` if your domain needs it

The system will compare generated states against expected `output_state` values.
