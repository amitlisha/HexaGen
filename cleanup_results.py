#!/usr/bin/env python3
"""Delete results* folders that contain no all*.json files (anywhere in the subtree)."""

import argparse
import shutil
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--dry-run", action="store_true", help="Print folders that would be deleted without deleting them")
args = parser.parse_args()

base = Path(__file__).parent

results_dirs = sorted(base.glob("results*/"))

to_delete = []
for d in results_dirs:
    has_summary = any(d.rglob("all*.json"))
    if not has_summary:
        to_delete.append(d)

if not to_delete:
    print("No folders to delete.")
elif args.dry_run:
    print(f"[dry-run] {len(to_delete)} folder(s) would be deleted:")
    for d in to_delete:
        print(f"  {d.name}")
else:
    print(f"Found {len(to_delete)} folder(s) with no all*.json files:")
    for d in to_delete:
        print(f"  {d.name}")

    confirm = input(f"\nDelete all {len(to_delete)} folder(s)? [y/N] ").strip().lower()
    if confirm == "y":
        for d in to_delete:
            shutil.rmtree(d)
            print(f"Deleted: {d.name}")
        print("Done.")
    else:
        print("Aborted.")
