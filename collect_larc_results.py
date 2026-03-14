"""Collect aggregate metrics from all LARC experiment result folders into a CSV.

Traverses results-larc* directories, reads all_*.json summary files,
and writes a flat CSV with experiment name, model, mode, date, metrics, etc.
"""

import csv
import datetime
import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent


def find_larc_jsons():
    """Yield (experiment_name, split, json_path) for every all_*.json in LARC results dirs."""
    for d in sorted(ROOT.iterdir()):
        if not d.is_dir() or not d.name.startswith("results-larc"):
            continue
        for sub in ("dev", "test"):
            sub_dir = d / sub
            if not sub_dir.is_dir():
                continue
            for f in sorted(sub_dir.glob("all_*.json")):
                yield d.name, sub, f


def process(json_path, split):
    """Extract summary info from a single all_*.json file."""
    with open(json_path) as f:
        data = json.load(f)

    config = data.get("config", {})
    agg = data.get("aggregate", {})

    date = datetime.datetime.fromtimestamp(json_path.stat().st_mtime).strftime("%Y-%m-%d")

    return {
        "experiment": None,  # filled by caller
        "run": json_path.stem,
        "date": date,
        "dataset": config.get("dataset", "larc"),
        "mode": config.get("mode", ""),
        "model": config.get("model", ""),
        "set": split,
        "vision": config.get("vision", False),
        "lib_file": config.get("lib_file", ""),
        "n_tasks": agg.get("n_tasks", 0),
        "total_steps": agg.get("total_steps", 0),
        "valid": agg.get("valid", 0),
        "exact": agg.get("exact", 0),
        "f1_board": agg.get("f1_board", 0.0),
        "f1_action": agg.get("f1_action", 0.0),
    }


def main():
    rows = []
    for exp_name, split, json_path in find_larc_jsons():
        row = process(json_path, split)
        row["experiment"] = exp_name
        rows.append(row)

    if not rows:
        print("No LARC experiments found.", file=sys.stderr)
        sys.exit(1)

    out_path = ROOT / "larc_results.csv"
    fieldnames = [
        "experiment", "run", "date", "dataset", "mode", "model", "set",
        "vision", "lib_file", "n_tasks", "total_steps", "valid", "exact",
        "f1_board", "f1_action",
    ]
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows to {out_path}")


if __name__ == "__main__":
    main()
