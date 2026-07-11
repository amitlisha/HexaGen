"""Preprocessor for Hexagons dataset.

Converts the Hexagons JSONL format to the standard library generation format.

Original format:
{
  "index": 0,
  "drawing_procedure": [
    [0, "NONE", [0, 0, 0, ...]],           // Initial empty state
    [1, "Draw a red tile...", [0, 0, 4, ...]],      // State after step 1
    [2, "Add blue neighbors...", [0, 5, 4, ...]]    // State after step 2
  ],
  ...
}

Standard format:
{
  "task_id": "hex_000",
  "steps": [
    {
      "instruction": "Draw a red tile...",
      "input_state": [0, 0, 0, ...],     // Empty board
      "output_state": [0, 0, 4, ...]     // After instruction
    },
    {
      "instruction": "Add blue neighbors...",
      "input_state": [0, 0, 4, ...],     // Previous output
      "output_state": [0, 5, 4, ...]     // After instruction
    }
  ]
}
"""

from __future__ import annotations

import json
import argparse
from pathlib import Path


def preprocess_hexagons(input_file: str, output_file: str, include_metadata: bool = False):
    """Convert Hexagons dataset to standard format.

    Args:
        input_file: Path to original Hexagons JSONL file
        output_file: Path to output standardized JSONL file
        include_metadata: Whether to include original metadata fields
    """
    input_path = Path(input_file)
    output_path = Path(output_file)

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    processed_count = 0
    skipped_count = 0

    with open(input_path, "r", encoding="utf-8") as f_in, \
         open(output_path, "w", encoding="utf-8") as f_out:

        for line_num, line in enumerate(f_in, 1):
            try:
                obj = json.loads(line)

                # Extract task ID
                task_id = f"hex_{obj['index']:06d}"

                # Extract steps with input/output states
                procedure = obj["drawing_procedure"]
                steps = []

                # Find initial state (first entry with "NONE")
                initial_state = None
                start_idx = 0
                for i, (step_num, instruction, board_state) in enumerate(procedure):
                    if instruction == "NONE":
                        initial_state = board_state
                        start_idx = i + 1
                        break

                # If no NONE found, use empty board (all zeros)
                if initial_state is None:
                    # Assume board size from first state
                    if procedure:
                        board_size = len(procedure[0][2])
                        initial_state = [0] * board_size
                    else:
                        skipped_count += 1
                        continue

                # Process each instruction
                previous_state = initial_state
                for step_num, instruction, output_state in procedure[start_idx:]:
                    if instruction == "NONE":
                        # Skip any additional NONE entries
                        continue

                    steps.append({
                        "instruction": instruction,
                        "input_state": previous_state,
                        "output_state": output_state
                    })

                    # Next step's input is this step's output
                    previous_state = output_state

                # Skip tasks with no valid instructions
                if not steps:
                    skipped_count += 1
                    continue

                # Build standardized object
                standard_obj = {
                    "task_id": task_id,
                    "steps": steps
                }

                # Optionally include metadata
                if include_metadata:
                    standard_obj["metadata"] = {
                        "original_index": obj["index"],
                        "category": obj.get("category", ""),
                        "image_id": obj.get("image_id", ""),
                        "annotation_round": obj.get("annotation_round"),
                        "instructor_id": obj.get("instructor_id"),
                        "number_of_steps": len(steps),
                        "agreement_tags": obj.get("agreement_tags", []),
                        "agreement_scores": obj.get("agreement_scores", [])
                    }

                f_out.write(json.dumps(standard_obj) + "\n")
                processed_count += 1

            except json.JSONDecodeError as e:
                print(f"Warning: Invalid JSON on line {line_num}: {e}")
                skipped_count += 1
            except KeyError as e:
                print(f"Warning: Missing field on line {line_num}: {e}")
                skipped_count += 1
            except Exception as e:
                print(f"Warning: Error on line {line_num}: {e}")
                skipped_count += 1

    print(f"\nPreprocessing complete!")
    print(f"  Input:  {input_path}")
    print(f"  Output: {output_path}")
    print(f"  Processed: {processed_count} tasks")
    print(f"  Skipped:   {skipped_count} tasks")

    # Show example
    if processed_count > 0:
        print(f"\nExample output (first task):")
        with open(output_path, "r") as f:
            first_line = f.readline()
            example = json.loads(first_line)
            print(f"  Task ID: {example['task_id']}")
            print(f"  Steps: {len(example['steps'])}")
            if example['steps']:
                print(f"  First instruction: {example['steps'][0]['instruction'][:60]}...")


def main():
    parser = argparse.ArgumentParser(
        description="Preprocess Hexagons dataset to standard library generation format"
    )
    parser.add_argument(
        "input_file",
        help="Path to original Hexagons JSONL file (e.g., data/train.jsonl)"
    )
    parser.add_argument(
        "output_file",
        help="Path to output standardized JSONL file (e.g., data/train_standard.jsonl)"
    )
    parser.add_argument(
        "--include-metadata",
        action="store_true",
        help="Include original metadata in output"
    )

    args = parser.parse_args()

    preprocess_hexagons(args.input_file, args.output_file, args.include_metadata)


if __name__ == "__main__":
    main()
