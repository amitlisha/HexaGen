"""LARC dataset implementation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterator, List, Tuple, Dict, Any

import pandas as pd

from .base import Dataset


class LARCDataset(Dataset):
    """Dataset for LARC (Language-Annotated ARC) tasks.

    Loads tasks from CSVs (task, description, build, join) and all.jsonl.
    """

    def __init__(self, data_dir: Path = None):
        """Initialize LARC dataset.

        Args:
            data_dir: Path to data directory containing CSVs and all.jsonl.
                     If None, uses default DATA_DIR/LARC.
        """
        super().__init__(data_dir)
        if data_dir is None:
            from gpt.runner_utils import DATA_DIR
            self.data_dir = DATA_DIR / "LARC"
        else:
            self.data_dir = Path(data_dir)

    def iter_tasks(self, split: str) -> Iterator[Tuple[str, Dict[str, Any]]]:
        """Iterate over LARC tasks using CSV-first approach.

        Args:
            split: One of 'train' or 'test'
                  - 'train': task_id 0-199
                  - 'test': task_id 200-399

        Yields:
            Tuple of (task_id, task_data)
            - task_id: String like "42_abc123de"
            - task_data: Dict with description, grids, dimensions
        """
        # Step 1: Load and split task.csv
        task_df = pd.read_csv(self.data_dir / "task.csv")
        if split == "train":
            task_df = task_df[task_df["task_id"] < 200]
        elif split == "test":
            task_df = task_df[task_df["task_id"] >= 200]
        else:
            raise ValueError(f"Unknown split: {split}. Use 'train' or 'test'.")

        # Step 2: Get successful builds
        build_df = pd.read_csv(self.data_dir / "build.csv")
        successful_builds = build_df[build_df["is_success"] == True][
            "build_id"
        ].tolist()

        # Step 3: Join to get successful task+description pairs
        join_df = pd.read_csv(self.data_dir / "join.csv")
        join_df = join_df[join_df["build_id"].isin(successful_builds)]

        description_df = pd.read_csv(self.data_dir / "description.csv")
        description_df = description_df[description_df["is_verified"] == True]

        # Merge everything
        joined = join_df.merge(task_df, on="task_id")
        joined = joined.merge(description_df, on="description_id")

        # Deduplicate (same task+description can have multiple successful builds)
        joined = joined.drop_duplicates(subset=["task_id", "description_id"])

        # Select only one description per task (deterministically: first by description_id)
        joined = joined.sort_values("description_id").groupby("task_id").first().reset_index()

        # Step 4: Load all.jsonl into lookup dict
        all_tasks = {}
        with open(self.data_dir / "all.jsonl") as f:
            for line in f:
                task = json.loads(line)
                all_tasks[task["name"]] = task

        # Step 5: Yield combined tasks
        for _, row in joined.iterrows():
            task_name = row["task_name"]
            arc_task = all_tasks.get(task_name)

            if arc_task is None:
                print(f"Warning: Task {task_name} not found in all.jsonl, skipping")
                continue

            # Get the specific description
            desc_id = row["description_id"]
            if desc_id not in arc_task.get("descriptions", {}):
                print(
                    f"Warning: Description {desc_id} not found in task {task_name}, skipping"
                )
                continue

            description = arc_task["descriptions"][desc_id]

            # Extract test grids
            test_input = arc_task["test"][0]["input"]
            test_output = arc_task["test"][0]["output"]

            task_data = {
                "arc_task_name": task_name,
                "description": {
                    "see": description.get("see_description", ""),
                    "do": description.get("do_description", ""),
                    "grid_size": description.get("grid_description", ""),
                },
                "test_input": test_input,
                "test_output": test_output,
                "train_examples": arc_task.get("train", []),
                "output_height": len(test_output),
                "output_width": len(test_output[0]) if test_output else 0,
                "input_height": len(test_input),
                "input_width": len(test_input[0]) if test_input else 0,
            }

            # Create unique task ID
            unique_id = f"{row['task_id']}_{desc_id[:8]}"
            yield unique_id, task_data

    def get_instructions(self, task_data: Dict[str, Any]) -> List[str]:
        """Extract instruction from LARC task (single combined instruction).

        Args:
            task_data: Task data with 'description' dict

        Returns:
            List with one combined instruction string
        """
        desc = task_data["description"]
        # Combine see + grid_size + do into single instruction
        instruction = f"{desc['see']}\n{desc['grid_size']}\n{desc['do']}"
        return [instruction]

    def get_gold_boards(self, task_data: Dict[str, Any]) -> List[List[int]]:
        """Extract gold board state from LARC task (flattened output grid).

        Args:
            task_data: Task data with 'test_output' 2D grid

        Returns:
            List with one flattened board state
        """
        # Convert 2D grid to 1D flat list
        output = task_data["test_output"]
        flat = [cell for row in output for cell in row]
        return [flat]

    def get_initial_board(self, task_data: Dict[str, Any]) -> List[int]:
        """Get initial board from LARC task (flattened input grid).

        Args:
            task_data: Task data with 'test_input' 2D grid

        Returns:
            Flattened input grid as initial board state
        """
        # Use test input as initial board
        input_grid = task_data["test_input"]
        flat = [cell for row in input_grid for cell in row]
        return flat

    def get_board_dimensions(self, task_data: Dict[str, Any]) -> Tuple[int, int]:
        """Get output board dimensions for LARC task.

        Args:
            task_data: Task data with 'output_width' and 'output_height'

        Returns:
            Tuple of (width, height) for the output grid
        """
        return (task_data["output_width"], task_data["output_height"])
