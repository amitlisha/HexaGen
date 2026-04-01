#!/usr/bin/env python3
"""Resubmit only failed requests from a completed OpenAI batch, then merge outputs.

Usage:
    # Just list failures
    python gpt/resume_batch.py batch_69c96eb8... --dry-run

    # Resubmit failures, poll, and merge outputs into a local file
    python gpt/resume_batch.py batch_69c96eb8... --poll

    # Resubmit without polling (prints new batch ID for later)
    python gpt/resume_batch.py batch_69c96eb8...

    # Merge a previously-resubmitted retry batch with the original
    python gpt/resume_batch.py batch_ORIGINAL... --merge-from batch_RETRY...

After merging, continue the experiment with:
    python gpt/experiment.py <same flags> --batch --batch-resume-file merged_batch_output.jsonl
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from llm_wrapper import (
    parse_batch_results,
    submit_openai_batch,
    poll_openai_batch,
)


def _get_client():
    from openai import OpenAI
    return OpenAI()


def _download_raw_output(client, file_id: str) -> list[str]:
    """Download a batch output/error file as raw JSONL lines."""
    raw = client.files.content(file_id)
    return [l for l in raw.text.splitlines() if l.strip()]


def _get_succeeded_and_failed(client, batch_id: str):
    """Returns (batch_obj, succeeded_lines, failed_request_lines).

    succeeded_lines: raw output JSONL lines for requests that succeeded
    failed_request_lines: raw input JSONL lines for requests that failed
    """
    batch = client.batches.retrieve(batch_id)
    print(f"Batch {batch_id}")
    print(f"  status:    {batch.status}")
    print(f"  total:     {batch.request_counts.total}")
    print(f"  completed: {batch.request_counts.completed}")
    print(f"  failed:    {batch.request_counts.failed}")

    if batch.status not in ("completed", "failed", "expired"):
        print(f"  Batch is still {batch.status} — nothing to resume yet.")
        return batch, [], []

    # Download succeeded output lines (raw JSONL, not parsed)
    succeeded_output_lines: list[str] = []
    succeeded_ids: set[str] = set()
    if batch.output_file_id:
        output_lines = _download_raw_output(client, batch.output_file_id)
        for line in output_lines:
            item = json.loads(line)
            cid = item["custom_id"]
            if not item.get("error"):
                succeeded_ids.add(cid)
                succeeded_output_lines.append(line)
        print(f"  succeeded results: {len(succeeded_ids)}")

    # Download the original input file to find failed requests
    failed_request_lines: list[str] = []
    if batch.input_file_id:
        raw_input = client.files.content(batch.input_file_id)
        for line in raw_input.text.splitlines():
            if not line.strip():
                continue
            item = json.loads(line)
            if item["custom_id"] not in succeeded_ids:
                failed_request_lines.append(line)

    total = len(succeeded_ids) + len(failed_request_lines)
    print(f"  total requests:    {total}")
    print(f"  to resubmit:       {len(failed_request_lines)}")

    return batch, succeeded_output_lines, failed_request_lines


def _merge_and_save(
    succeeded_lines: list[str],
    retry_lines: list[str],
    output_path: str = "merged_batch_output.jsonl",
) -> str:
    """Merge succeeded lines from original batch with retry batch output.
    Returns the output file path."""
    # Deduplicate by custom_id (retry results take precedence)
    by_cid: dict[str, str] = {}
    for line in succeeded_lines:
        item = json.loads(line)
        by_cid[item["custom_id"]] = line
    for line in retry_lines:
        item = json.loads(line)
        by_cid[item["custom_id"]] = line  # overwrite with retry result

    path = Path(output_path)
    with open(path, "w", encoding="utf-8") as f:
        for line in by_cid.values():
            f.write(line + "\n")

    print(f"\nMerged {len(by_cid)} results → {path}")
    return str(path)


def main():
    parser = argparse.ArgumentParser(
        description="Resubmit failed requests from a completed OpenAI batch"
    )
    parser.add_argument("batch_id", help="The OpenAI batch ID to resume")
    parser.add_argument(
        "--poll", action="store_true",
        help="Poll the new batch and merge outputs when done",
    )
    parser.add_argument(
        "--poll-interval", type=int, default=60,
        help="Seconds between polls (default: 60)",
    )
    parser.add_argument(
        "--merge-from", type=str, default=None,
        help="Merge results from this retry batch ID with the original "
        "(skip resubmission, just merge)",
    )
    parser.add_argument(
        "--output", type=str, default="merged_batch_output.jsonl",
        help="Output path for merged JSONL (default: merged_batch_output.jsonl)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Just list failed custom_ids without resubmitting",
    )
    args = parser.parse_args()

    client = _get_client()
    batch, succeeded_lines, failed_lines = _get_succeeded_and_failed(
        client, args.batch_id
    )

    if not failed_lines:
        print("\nNo failed requests — nothing to resubmit.")
        return

    if args.dry_run:
        print("\n[dry-run] Failed custom_ids:")
        for line in failed_lines:
            item = json.loads(line)
            print(f"  {item['custom_id']}")
        return

    # ── Merge from an existing retry batch ────────────────────────────
    if args.merge_from:
        print(f"\nMerging with retry batch {args.merge_from}...")
        retry_batch = client.batches.retrieve(args.merge_from)
        if retry_batch.status not in ("completed", "failed", "expired"):
            print(f"  Retry batch is still {retry_batch.status} — cannot merge yet.")
            return
        retry_output_lines = []
        if retry_batch.output_file_id:
            retry_output_lines = _download_raw_output(
                client, retry_batch.output_file_id
            )
        merged_path = _merge_and_save(succeeded_lines, retry_output_lines, args.output)
        print(f"\nContinue with:")
        print(f"  python gpt/experiment.py <flags> --batch --batch-resume-file {merged_path}")
        return

    # ── Resubmit failed requests ──────────────────────────────────────
    print(f"\nSubmitting {len(failed_lines)} failed requests as new batch...")
    new_batch_id = submit_openai_batch(failed_lines)
    print(f"New batch ID: {new_batch_id}")

    if not args.poll:
        print(f"\nTo poll and merge later:")
        print(f"  python gpt/resume_batch.py {args.batch_id} --merge-from {new_batch_id}")
        return

    # ── Poll and merge ────────────────────────────────────────────────
    print(f"\nPolling new batch (interval={args.poll_interval}s)...")
    retry_obj = poll_openai_batch(new_batch_id, args.poll_interval)
    print(f"\nRetry batch finished: status={retry_obj.status}")
    print(f"  completed: {retry_obj.request_counts.completed}")
    print(f"  failed:    {retry_obj.request_counts.failed}")

    retry_output_lines = []
    if retry_obj.output_file_id:
        retry_output_lines = _download_raw_output(client, retry_obj.output_file_id)

    merged_path = _merge_and_save(succeeded_lines, retry_output_lines, args.output)
    print(f"\nContinue with:")
    print(f"  python gpt/experiment.py <flags> --batch --batch-resume-file {merged_path}")


if __name__ == "__main__":
    main()