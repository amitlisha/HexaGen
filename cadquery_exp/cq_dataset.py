"""Dataset loader for the Text2CAD CadQuery experiment."""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Dict, List, Optional

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
CQ_DIR = DATA_DIR / "CQ"
CSV_PATH = DATA_DIR / "text2cad_v1.1" / "text2cad_v1.1.csv"
SPLIT_PATH = DATA_DIR / "text2cad_v1.1" / "train_test_val.json"

# Column names in the CSV that correspond to abstraction levels used as prompt input.
# "abstract"    — one-sentence shape description (highest abstraction)
# "beginner"    — paragraph describing overall shape and key dimensions
# "intermediate"— paragraph describing construction steps at a medium level
# "expert"      — detailed step-by-step construction instructions
ABSTRACTION_LEVELS = ["abstract", "beginner", "intermediate", "expert"]


def _uid_to_cq_path(uid: str) -> Path:
    """Map a uid like '0035/00359148' to data/CQ/0035/00359148.py."""
    folder, name = uid.split("/")
    return CQ_DIR / folder / f"{name}.py"


def load_dataset(
    split: str = "test",
    max_examples: Optional[int] = None,
    abstraction_levels: Optional[List[str]] = None,
    seed: int = 42,
) -> List[Dict]:
    """Load dataset examples that have corresponding gold CQ files.

    Returns a list of dicts with keys:
        uid         — dataset identifier (e.g. '0035/00359148')
        split       — which split this example belongs to
        gold_code   — contents of the gold CadQuery .py file
        abstract    — one-sentence prompt
        beginner    — beginner-level prompt
        intermediate — intermediate-level prompt
        expert      — expert-level prompt
    """
    if abstraction_levels is None:
        abstraction_levels = ABSTRACTION_LEVELS

    import random as _random
    with open(SPLIT_PATH) as f:
        splits = json.load(f)
    split_uids = list(splits[split])
    _random.Random(seed).shuffle(split_uids)

    with open(CSV_PATH, newline="") as f:
        uid_to_row: Dict[str, Dict] = {row["uid"]: row for row in csv.DictReader(f)}

    examples = []
    for uid in split_uids:
        if uid not in uid_to_row:
            continue
        cq_path = _uid_to_cq_path(uid)
        if not cq_path.exists():
            continue
        row = uid_to_row[uid]
        examples.append(
            {
                "uid": uid,
                "split": split,
                "gold_code": cq_path.read_text(),
                **{lvl: row[lvl] for lvl in abstraction_levels},
            }
        )
        if max_examples is not None and len(examples) >= max_examples:
            break

    return examples


def dataset_coverage_report(splits: Optional[List[str]] = None) -> Dict:
    """Report how many examples per split have gold CQ files and CSV entries."""
    if splits is None:
        splits = ["train", "validation", "test"]

    with open(SPLIT_PATH) as f:
        split_data = json.load(f)
    with open(CSV_PATH, newline="") as f:
        csv_uids = {row["uid"] for row in csv.DictReader(f)}

    report = {}
    for split in splits:
        uids = split_data[split]
        in_csv = sum(1 for u in uids if u in csv_uids)
        has_cq = sum(1 for u in uids if _uid_to_cq_path(u).exists())
        report[split] = {
            "total_in_split": len(uids),
            "in_csv": in_csv,
            "has_gold_cq": has_cq,
            "usable": has_cq,  # usable = has both CSV entry and gold file
        }
    return report
