"""Base dataset interface for experiments."""

from abc import ABC, abstractmethod
from typing import Iterator, List, Tuple, Dict, Any
from pathlib import Path


class Dataset(ABC):
    """Abstract base class for experiment datasets.

    Each dataset provides task iteration and data extraction methods.
    Tasks can have different structures, but this interface standardizes
    how we access instructions, gold boards, and board dimensions.
    """

    def __init__(self, data_dir: Path = None):
        """Initialize dataset with optional data directory.

        Args:
            data_dir: Path to data directory. If None, uses default.
        """
        self.data_dir = data_dir

    @abstractmethod
    def iter_tasks(self, split: str) -> Iterator[Tuple[Any, Dict[str, Any]]]:
        """Iterate over tasks in a dataset split.

        Args:
            split: Dataset split name (e.g., 'train', 'dev', 'test')

        Yields:
            Tuple of (task_id, task_data)
            - task_id: Unique identifier for the task
            - task_data: Dict containing all task information
        """
        pass

    @abstractmethod
    def get_instructions(self, task_data: Dict[str, Any]) -> List[str]:
        """Extract instruction steps from task data.

        Args:
            task_data: Task data dict from iter_tasks

        Returns:
            List of instruction strings, one per step
        """
        pass

    @abstractmethod
    def get_gold_boards(self, task_data: Dict[str, Any]) -> List[List[int]]:
        """Extract gold board states after each instruction step.

        Args:
            task_data: Task data dict from iter_tasks

        Returns:
            List of board states (each is a flat list of integers)
            Length should match get_instructions()
        """
        pass

    @abstractmethod
    def get_initial_board(self, task_data: Dict[str, Any]) -> List[int]:
        """Get the initial board state before any instructions.

        Args:
            task_data: Task data dict from iter_tasks

        Returns:
            Initial board state as flat list of integers
        """
        pass

    @abstractmethod
    def get_board_dimensions(self, task_data: Dict[str, Any]) -> Tuple[int, int]:
        """Get board dimensions for this task.

        Args:
            task_data: Task data dict from iter_tasks

        Returns:
            Tuple of (width, height)
        """
        pass
