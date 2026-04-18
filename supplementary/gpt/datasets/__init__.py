"""Dataset abstraction for different experiment datasets."""

from .base import Dataset
from .hexagons import HexagonsDataset


def get_dataset(data_dir=None) -> Dataset:
    """Get the Hexagons dataset.

    Args:
        data_dir: Optional data directory path

    Returns:
        Dataset instance
    """
    return HexagonsDataset(data_dir)


__all__ = ["Dataset", "HexagonsDataset", "get_dataset"]
