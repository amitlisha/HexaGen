#!/usr/bin/env python3
"""Pairwise VLM comparison between two completed cq_experiment.py runs.

Mimics the Text2CAD GPT-4V evaluation protocol (paper Section 5.1.B, Table 2):
for each matched task, render both candidates' predicted shapes, show a local
VLM the two candidates + the text instruction (no ground truth), and tally a
per-level win rate (Setup A % / Setup B % / Undecided %).

Generation is decoupled from comparison on purpose: run cq_experiment.py once
per setup (e.g. two different --model values, or two different --conditions)
to produce two `results-*/` directories, then point this script at both. This
avoids baking "setup" into the Cartesian-product runner, since a setup can be
a different model, checkpoint, or condition — orthogonal axes the runner
doesn't need to know about.

Usage
-----
    python cadquery_exp/cq_compare.py \\
        --run-a results-<setup-a>-<uuid> \\
        --run-b results-<setup-b>-<uuid> \\
        --vlm-model <local-vlm-name> [--base-url ...] [--api-key ...] \\
        [--levels abstract beginner intermediate expert] \\
        [--max-per-level N] [--seed 42]

Only tasks present in both runs are compared, and only where both
candidates executed successfully (status == "ok"); gold/exec failures on
either side are excluded and counted separately, mirroring how Table 2
reports "Undecided" separately from the win-rate split.
"""
from __future__ import annotations

import argparse
import json
import random
import sys
import threading
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List, Optional

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "gpt"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from llm_wrapper import init_llm  # noqa: E402

from cq_dataset import ABSTRACTION_LEVELS  # noqa: E402
from cq_render import render_views  # noqa: E402
from cq_vlm_judge import pairwise_judge  # noqa: E402


# ---------------------------------------------------------------------------
# Loading a completed run
# ---------------------------------------------------------------------------

def _latest_results_json(run_dir: Path) -> Path:
    candidates = sorted(run_dir.glob("*_results.json"))
    if not candidates:
        raise FileNotFoundError(f"No *_results.json found in {run_dir}")
    return candidates[-1]


def _index_run(run_dir: Path) -> Dict[tuple, Dict]:
    """Load a run's results, indexed by (uid, level, condition).

    Excludes only gold_failed tasks (gold execution is a property of the
    dataset, not of this setup, so those never belong in a comparison
    between setups). Prediction-side failures (error/timeout/exception) are
    KEPT — a setup that failed to even produce executable geometry is a
    real, comparison-worthy outcome, not something to silently drop.
    """
    path = _latest_results_json(run_dir)
    data = json.loads(path.read_text())
    index: Dict[tuple, Dict] = {}
    for r in data["results"]:
        if r.get("status") == "gold_failed":
            continue
        key = (r["uid"], r["level"], r["condition"])
        index[key] = r
    return index


# ---------------------------------------------------------------------------
# Comparison
# ---------------------------------------------------------------------------

def _render_cache_dir(base: Path) -> Path:
    d = base / "_cq_compare_renders"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _write_incremental(out_path: Path, config: Dict, tallies: Dict, judgments: List[Dict], matched_total: int) -> None:
    """Overwrite out_path with current progress — safe to call after every task
    so a crash or kill mid-run loses at most the one in-flight judgment."""
    out_path.write_text(json.dumps(
        {"config": config, "tallies": tallies, "judgments": judgments,
         "matched_total": matched_total, "complete": False},
        indent=2, default=str,
    ))


def _judge_task(
    uid: str, level: str, ra: Dict, rb: Dict, vlm_model: str,
    render_cache: Path, task_seed: int,
) -> Dict:
    """Resolve one (uid, level) task. Runs in a worker thread — must not
    touch any shared mutable state; returns a plain result dict instead.

    A setup that failed to produce executable geometry at all loses the
    comparison outright — no VLM call needed, and no reason to silently
    drop the sample just because it can't be visually judged. The VLM is
    only invoked when both sides actually produced a valid shape to render.
    """
    base = {
        "uid": uid, "level": level,
        "condition_a": ra["condition"], "condition_b": rb["condition"],
    }
    a_ok = ra.get("status") == "ok"
    b_ok = rb.get("status") == "ok"

    if a_ok and not b_ok:
        return {**base, "winner": "a", "raw_verdict": "AUTO_ONLY_A_SUCCEEDED",
                "note": f"b status={rb.get('status')}"}
    if b_ok and not a_ok:
        return {**base, "winner": "b", "raw_verdict": "AUTO_ONLY_B_SUCCEEDED",
                "note": f"a status={ra.get('status')}"}
    if not a_ok and not b_ok:
        return {**base, "winner": "both_failed",
                "note": f"a status={ra.get('status')}, b status={rb.get('status')}"}

    instruction = ra["instruction"]
    try:
        uid_flat = uid.replace("/", "_")
        imgs_a = render_views(
            Path(ra["pred_brep_path"]).read_text(),
            render_cache / uid_flat / level / "a",
            prefix="a",
        )
        imgs_b = render_views(
            Path(rb["pred_brep_path"]).read_text(),
            render_cache / uid_flat / level / "b",
            prefix="b",
        )
        # Independent RNG per task (not a shared Random across threads) so
        # the left/right swap decision is race-free and reproducible
        # regardless of thread scheduling / completion order.
        verdict = pairwise_judge(
            instruction, imgs_a, imgs_b, model=vlm_model,
            rng=random.Random(task_seed),
        )
        return {**base, **verdict}
    except Exception as exc:
        return {**base, "winner": "error", "error": str(exc)}


def _load_resume_judgments(resume_from: Optional[Path]) -> List[Dict]:
    """Load already-completed judgments from a prior (possibly killed
    mid-run) cq_compare.py output, so re-running never throws away real,
    already-paid-for judge calls just to change scope (e.g. drop a level)."""
    if resume_from is None:
        return []
    data = json.loads(resume_from.read_text())
    judgments = data.get("judgments", [])
    print(f"Resuming from {resume_from}: {len(judgments)} prior judgments loaded", flush=True)
    return judgments


def compare_runs(
    run_a: Path,
    run_b: Path,
    vlm_model: str,
    levels: List[str],
    max_per_level: Optional[int],
    seed: int,
    out_path: Path,
    config: Dict,
    workers: int = 4,
    resume_from: Optional[Path] = None,
) -> Dict:
    idx_a = _index_run(run_a)
    idx_b = _index_run(run_b)

    # Match by (uid, level) regardless of condition — a "setup" may hold
    # condition fixed and vary model, or vice versa; whichever condition
    # each run actually used is preserved in the per-task record for context.
    def _by_uid_level(index: Dict[tuple, Dict]) -> Dict[tuple, Dict]:
        out: Dict[tuple, Dict] = {}
        for (uid, level, _cond), r in index.items():
            out[(uid, level)] = r  # last condition wins if a run has >1
        return out

    a_by_ul = _by_uid_level(idx_a)
    b_by_ul = _by_uid_level(idx_b)

    matched_keys = sorted(set(a_by_ul) & set(b_by_ul))

    rng = random.Random(seed)
    render_cache = _render_cache_dir(ROOT_DIR / f"_compare_cache_{run_a.name}_vs_{run_b.name}")

    per_level_keys: Dict[str, List[tuple]] = defaultdict(list)
    for uid, level in matched_keys:
        if level in levels:
            per_level_keys[level].append((uid, level))
    if max_per_level is not None:
        for level in per_level_keys:
            rng.shuffle(per_level_keys[level])
            per_level_keys[level] = per_level_keys[level][:max_per_level]

    all_keys: List[tuple] = [
        (uid, lvl) for lvl in levels for (uid, lvl) in per_level_keys.get(lvl, [])
    ]

    tallies: Dict[str, Dict[str, int]] = {
        lvl: {"a": 0, "b": 0, "undecided": 0, "error": 0, "both_failed": 0} for lvl in levels
    }

    # Seed from a prior (possibly interrupted) run's output: already-judged
    # (uid, level) pairs are skipped rather than re-judged from scratch.
    prior = [j for j in _load_resume_judgments(resume_from) if j["level"] in levels]
    already_judged = {(j["uid"], j["level"]) for j in prior}
    judgments: List[Dict] = list(prior)
    for j in prior:
        tallies[j["level"]][j["winner"]] += 1
    all_keys = [k for k in all_keys if k not in already_judged]

    lock = threading.Lock()

    for level in levels:
        print(f"Level: {level}  ({len(per_level_keys.get(level, []))} matched tasks)", flush=True)
    if prior:
        print(f"Skipping {len(already_judged)} already-judged tasks from resume", flush=True)
    print(f"\nRunning {len(all_keys)} judge calls with {workers} concurrent workers...", flush=True)

    total = len(all_keys)
    done = 0
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {
            pool.submit(
                _judge_task, uid, lvl, a_by_ul[(uid, lvl)], b_by_ul[(uid, lvl)],
                vlm_model, render_cache,
                # deterministic per-task seed, independent of thread timing
                hash((seed, uid, lvl)) & 0xFFFFFFFF,
            ): (uid, lvl)
            for uid, lvl in all_keys
        }
        for future in as_completed(futures):
            uid, lvl = futures[future]
            r = future.result()  # _judge_task never raises — always returns a dict
            with lock:
                done += 1
                tallies[lvl][r["winner"]] += 1
                judgments.append(r)
                _write_incremental(out_path, config, tallies, judgments, len(matched_keys))
            if "raw_verdict" in r:
                extra = f"(raw={r['raw_verdict']}" + (f", swapped={r['swapped']})" if "swapped" in r else ")")
            elif r["winner"] == "both_failed":
                extra = f"({r.get('note')})"
            else:
                extra = f"ERROR: {r.get('error')}"
            print(f"  [{done}/{total}] {lvl}/{uid} -> {r['winner']}  {extra}", flush=True)

    return {"tallies": tallies, "judgments": judgments, "matched_total": len(matched_keys)}


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def print_report(result: Dict, label_a: str, label_b: str, levels: List[str]) -> None:
    bar = "=" * 72
    print(f"\n{bar}")
    print(f"PAIRWISE VLM COMPARISON  —  (a) {label_a}  vs.  (b) {label_b}")
    print(bar)
    print(f"{'Level':<15} {'N':>5} {label_a[:14]+'%':>16} {label_b[:14]+'%':>16} {'Undecided%':>11} {'BothFail':>9} {'Errors':>7}")
    print("-" * 72)
    for level in levels:
        t = result["tallies"].get(level)
        if not t:
            continue
        n = t["a"] + t["b"] + t["undecided"] + t.get("error", 0) + t.get("both_failed", 0)
        if n == 0:
            continue
        print(f"{level:<15} {n:>5} {100*t['a']/n:>15.1f}% {100*t['b']/n:>15.1f}% {100*t['undecided']/n:>10.1f}% "
              f"{t.get('both_failed', 0):>9} {t.get('error', 0):>7}")
    print(bar)


def main() -> None:
    # Force line-buffering even when stdout is redirected to a file/log, so
    # progress is visible in real time rather than only on process exit.
    sys.stdout.reconfigure(line_buffering=True)

    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--run-a", required=True, type=Path)
    p.add_argument("--run-b", required=True, type=Path)
    p.add_argument("--label-a", default=None)
    p.add_argument("--label-b", default=None)
    p.add_argument("--vlm-model", required=True)
    p.add_argument("--base-url", default=None)
    p.add_argument("--api-key", default=None)
    p.add_argument("--levels", nargs="+", default=ABSTRACTION_LEVELS, choices=ABSTRACTION_LEVELS)
    p.add_argument("--max-per-level", type=int, default=None)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--workers", type=int, default=4,
                   help="Concurrent judge calls in flight at once")
    p.add_argument("--resume-from", type=Path, default=None,
                   help="Path to a prior compare-*.json (complete or "
                        "interrupted). Already-judged (uid, level) pairs are "
                        "skipped rather than re-judged from scratch.")
    cfg = p.parse_args()

    init_llm(argparse.Namespace(model=cfg.vlm_model, base_url=cfg.base_url, api_key=cfg.api_key))

    label_a = cfg.label_a or cfg.run_a.name
    label_b = cfg.label_b or cfg.run_b.name

    ts = time.strftime("%Y-%m-%dT%H-%M-%S", time.localtime())
    out_path = ROOT_DIR / f"compare-{label_a}-vs-{label_b}-{ts}.json"
    print(f"Writing progress incrementally to {out_path}", flush=True)

    result = compare_runs(
        cfg.run_a, cfg.run_b, cfg.vlm_model, cfg.levels, cfg.max_per_level, cfg.seed,
        out_path=out_path, config=vars(cfg), workers=cfg.workers,
        resume_from=cfg.resume_from,
    )

    out_path.write_text(json.dumps(
        {"config": vars(cfg), **result, "complete": True},
        indent=2, default=str,
    ))
    print(f"\nFull judgments -> {out_path}")

    print_report(result, label_a, label_b, cfg.levels)


if __name__ == "__main__":
    main()
