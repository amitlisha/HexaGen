"""Dataset abstraction for different experiment datasets."""

from .base import Dataset
from .hexagons import HexagonsDataset
from .larc import LARCDataset


def get_dataset(dataset_name: str, data_dir=None) -> Dataset:
    """Factory function to get the appropriate dataset.

    Args:
        dataset_name: Name of the dataset ('hexagons' or 'larc')
        data_dir: Optional data directory path

    Returns:
        Dataset instance
    """
    if dataset_name == "hexagons":
        return HexagonsDataset(data_dir)
    elif dataset_name == "larc":
        return LARCDataset(data_dir)
    else:
        raise ValueError(f"Unknown dataset: {dataset_name}")


__all__ = ["Dataset", "HexagonsDataset", "LARCDataset", "get_dataset"]
