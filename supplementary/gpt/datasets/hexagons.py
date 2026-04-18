"""Hexagons dataset implementation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterator, List, Tuple, Dict, Any

from .base import Dataset
from constants.constants import WIDTH, HEIGHT


class HexagonsDataset(Dataset):
    """Dataset for Hexagons drawing tasks.

    Uses JSONL files with drawing procedures and board states.
    """

    def __init__(self, data_dir: Path = None):
        """Initialize Hexagons dataset.

        Args:
            data_dir: Path to data directory containing JSONL files.
                     If None, uses default DATA_DIR from runner_utils.
        """
        super().__init__(data_dir)
        if data_dir is None:
            from gpt.runner_utils import DATA_DIR
            self.data_dir = DATA_DIR
        else:
            self.data_dir = Path(data_dir)

    def iter_tasks(self, split: str) -> Iterator[Tuple[int, Dict[str, Any]]]:
        """Iterate over Hexagons tasks from JSONL file.

        Args:
            split: One of 'train', 'dev', 'test', '4-samples'

        Yields:
            Tuple of (task_id, task_data)
            - task_id: Integer task ID
            - task_data: Dict with 'steps' and 'gold_boards' keys
        """
        path = self.data_dir / f"{split}.jsonl"
        with path.open("r", encoding="utf-8") as fh:
            for line in fh:
                obj = json.loads(line)
                # Filter out NONE steps
                proc = [r for r in obj["drawing_procedure"] if r[1] != "NONE"]
                yield obj["index"], {
                    "steps": [r[1] for r in proc],
                    "gold_boards": [r[2] for r in proc],
                }

    def get_instructions(self, task_data: Dict[str, Any]) -> List[str]:
        """Extract instruction steps from Hexagons task.

        Args:
            task_data: Task data with 'steps' key

        Returns:
            List of instruction strings
        """
        return task_data["steps"]

    def get_gold_boards(self, task_data: Dict[str, Any]) -> List[List[int]]:
        """Extract gold board states from Hexagons task.

        Args:
            task_data: Task data with 'gold_boards' key

        Returns:
            List of board states (already flat lists)
        """
        return task_data["gold_boards"]

    def get_initial_board(self, task_data: Dict[str, Any]) -> List[int]:
        """Get initial empty board for Hexagons.

        Args:
            task_data: Task data (not used for Hexagons)

        Returns:
            Empty board (all zeros)
        """
        return [0] * (WIDTH * HEIGHT)

    def get_board_dimensions(self, task_data: Dict[str, Any]) -> Tuple[int, int]:
        """Get board dimensions for Hexagons (always constant).

        Args:
            task_data: Task data (not used for Hexagons)

        Returns:
            Tuple of (WIDTH, HEIGHT) from constants
        """
        return (WIDTH, HEIGHT)
