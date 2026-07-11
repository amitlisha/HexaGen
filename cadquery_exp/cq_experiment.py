#!/usr/bin/env python3
"""CadQuery condition-comparison experiment.

Generates CadQuery programs from natural-language prompts under two conditions
and compares the resulting geometry to the gold shape:

  (a) direct   — generate raw CadQuery
  (b) abstraction — generate against a user-supplied abstraction layer

Results are broken down by abstraction level (abstract / beginner /
intermediate / expert) so that the per-level Δ(b − a) is surfaced.

Usage
-----
    python cadquery_exp/cq_experiment.py \\
        --model <model-name> \\
        [--split test] [--max-examples N] \\
        [--levels abstract beginner intermediate expert] \\
        [--conditions direct abstraction] \\
        [--workers 8] [--timeout 30]

Run cq_validate.py first to verify the executor and metrics before a full run.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "gpt"))

from llm_wrapper import call_llm, init_llm  # noqa: E402

from cq_dataset import ABSTRACTION_LEVELS, load_dataset  # noqa: E402
from cq_executor import execute_cq  # noqa: E402
from cq_metrics import compute_metrics  # noqa: E402

# ---------------------------------------------------------------------------
# Paths and constants
# ---------------------------------------------------------------------------

PROMPTS_DIR = Path(__file__).parent / "prompts"
CONDITIONS = ["direct", "abstraction"]


# ---------------------------------------------------------------------------
# Tiny utility helpers (avoid importing runner_utils which pulls in hexagen)
# ---------------------------------------------------------------------------

def _timestamp() -> str:
    return time.strftime("%Y-%m-%dT%H-%M-%S", time.localtime())


def _save_json(obj: dict, path: Path) -> None:
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False))


def _results_dir(experiment_name: str) -> Path:
    import uuid
    return ROOT_DIR / f"results-{experiment_name}-{uuid.uuid4()}"


# ---------------------------------------------------------------------------
# Prompt loading
# ---------------------------------------------------------------------------

def load_prompts(prompts_dir: Path = PROMPTS_DIR) -> Dict[str, str]:
    """Load prompt templates for both conditions.

    System prompts are assembled from a shared overview + a condition-specific
    section, mirroring how shared_system_prompt.txt is used in the hexagons
    experiments.
    """
    def _read(name: str) -> str:
        p = prompts_dir / name
        if not p.exists():
            raise FileNotFoundError(
                f"Missing prompt file: {p}\n"
                "Fill in the placeholder files in cadquery_exp/prompts/ before running."
            )
        return p.read_text()

    shared = _read("shared_system_prompt.txt")

    return {
        "direct_system":       shared + "\n\n" + _read("system_direct.txt"),
        "direct_user":         _read("user_direct.txt"),
        "abstraction_system":  shared + "\n\n" + _read("system_abstraction.txt"),
        "abstraction_user":    _read("user_abstraction.txt"),
    }


def _fill_prompt(template: str, prompt_text: str) -> str:
    """Replace the {PROMPT} placeholder with the natural-language description."""
    return template.replace("{PROMPT}", prompt_text)


# ---------------------------------------------------------------------------
# Per-example worker
# ---------------------------------------------------------------------------

def run_one(
    example: Dict,
    level: str,
    condition: str,
    prompts: Dict[str, str],
    cfg: argparse.Namespace,
    out_dir: Path,
) -> Dict:
    """Run one (example × level × condition) triple and return a result dict."""
    uid = example["uid"]
    prompt_text = example[level]
    run_ts = _timestamp()

    task_dir = out_dir / uid.replace("/", "_") / level / condition
    task_dir.mkdir(parents=True, exist_ok=True)

    result: Dict = {
        "uid": uid,
        "level": level,
        "condition": condition,
        "instruction": prompt_text,
        "gold_status": None,
        "status": None,
        "error": None,
        "iou": None,
        "chamfer": None,
        "usage": {},
    }

    # 1. Execute gold through the same CadQuery path used for predictions
    gold_brep, gold_err = execute_cq(example["gold_code"], timeout=cfg.timeout)
    result["gold_status"] = "error" if gold_err else "ok"
    if gold_err:
        result["status"] = "gold_failed"
        result["error"] = f"Gold execution failed: {gold_err[:300]}"
        _save_json(result, task_dir / f"{run_ts}_result.json")
        return result

    # 2. LLM generation + execution with retry on failure (mirrors full_runner.py)
    system_prompt = prompts[f"{condition}_system"]
    base_user_prompt = _fill_prompt(prompts[f"{condition}_user"], prompt_text)

    abstraction_layer_path: Optional[str] = None
    if condition == "abstraction":
        abstraction_layer_path = str(PROMPTS_DIR / "abstraction_layer.py")

    max_attempts = cfg.retries
    last_err: Optional[str] = None
    last_code: Optional[str] = None
    total_usage: Dict = {}

    for attempt in range(1, max_attempts + 1):
        # Build prompt — on retries append the previous code + error
        if last_err is None:
            user_prompt = base_user_prompt
        else:
            user_prompt = (
                base_user_prompt
                + "\n\n"
                "### Your previous code\n"
                "```python\n"
                f"{last_code.strip()}\n"
                "```\n\n"
                "### Execution error\n"
                f"{last_err.strip()}\n\n"
                "### Fix instructions\n"
                "Analyze the error above and fix your code. Do NOT repeat the same mistake.\n"
            )

        resp = call_llm(
            user_prompt,
            model=cfg.model,
            system_prompt=system_prompt,
            temperature=cfg.temperature,
            max_tokens=cfg.max_tokens,
            seed=cfg.seed,
        )
        # Accumulate token usage across attempts
        for k, v in resp.get("usage", {}).items():
            total_usage[k] = total_usage.get(k, 0) + v

        generated_code = resp["text"]
        (task_dir / f"{run_ts}_generated_{attempt:02}.py").write_text(
            generated_code, encoding="utf-8"
        )

        pred_brep, pred_err = execute_cq(
            generated_code,
            timeout=cfg.timeout,
            abstraction_layer_path=abstraction_layer_path,
            from_llm=True,
        )

        if pred_err is None:
            break  # success — exit retry loop

        last_code = generated_code
        last_err = pred_err

    result["usage"] = total_usage
    result["attempts"] = attempt

    if pred_err:
        result["status"] = "timeout" if pred_err == "TIMEOUT" else "error"
        result["error"] = pred_err[:500]
        _save_json(result, task_dir / f"{run_ts}_result.json")
        return result

    # 3. Compute geometry metrics
    metrics = compute_metrics(pred_brep, gold_brep)
    result["status"] = "ok"
    result["iou"] = metrics["iou"]
    result["chamfer"] = metrics["chamfer"]

    _save_json(result, task_dir / f"{run_ts}_result.json")
    return result


# ---------------------------------------------------------------------------
# Aggregation and reporting
# ---------------------------------------------------------------------------

def aggregate(results: List[Dict]) -> Dict:
    """Aggregate per-example results into per-(level, condition) summaries.

    Execution failures are counted as IoU=0 in the mean. Gold failures are
    excluded from the denominator entirely.
    """
    groups: Dict = defaultdict(lambda: {
        "iou": [], "chamfer": [], "n_exec_fail": 0, "n_gold_fail": 0, "n": 0
    })

    for r in results:
        g = groups[(r["level"], r["condition"])]
        g["n"] += 1
        if r["status"] == "gold_failed":
            g["n_gold_fail"] += 1
        elif r["status"] in ("error", "timeout", "exception"):
            g["n_exec_fail"] += 1
            g["iou"].append(0.0)  # penalize failures as IoU=0
        else:
            if r["iou"] is not None:
                g["iou"].append(r["iou"])
            if r["chamfer"] is not None and r["chamfer"] != float("inf"):
                g["chamfer"].append(r["chamfer"])

    summary = {}
    for (level, condition), g in groups.items():
        n = g["n"]
        n_scored = n - g["n_gold_fail"]  # denominator excludes gold failures
        summary[f"{level}|{condition}"] = {
            "level": level,
            "condition": condition,
            "n_total": n,
            "n_scored": n_scored,
            "exec_failure_rate": g["n_exec_fail"] / n_scored if n_scored else 0.0,
            "gold_failure_rate": g["n_gold_fail"] / n if n else 0.0,
            "mean_iou": float(np.mean(g["iou"])) if g["iou"] else None,
            "mean_chamfer": float(np.mean(g["chamfer"])) if g["chamfer"] else None,
        }
    return summary


def print_report(summary: Dict, levels: List[str], conditions: List[str]) -> None:
    """Print a comparison table with per-level Δ(b − a)."""
    bar = "=" * 82
    print(f"\n{bar}")
    print("RESULTS  —  Condition (a) Direct CadQuery  vs.  (b) Abstraction Layer")
    print(bar)
    hdr = f"{'Level':<15} {'Condition':<13} {'N':>5} {'IoU(fail=0)':>11} {'Chamfer':>10} {'Exec-fail%':>11}"
    print(hdr)
    print("-" * 82)

    for level in levels:
        for cond in conditions:
            key = f"{level}|{cond}"
            if key not in summary:
                continue
            s = summary[key]
            iou_s = f"{s['mean_iou']:.4f}" if s["mean_iou"] is not None else "    N/A  "
            cd_s  = f"{s['mean_chamfer']:.4f}" if s["mean_chamfer"] is not None else "  N/A   "
            fail_pct = s["exec_failure_rate"] * 100
            print(f"{level:<15} {cond:<13} {s['n_scored']:>5} {iou_s:>11} {cd_s:>10} {fail_pct:>10.1f}%")

        # Δ row (only when both conditions were run)
        key_a = f"{level}|direct"
        key_b = f"{level}|abstraction"
        if key_a in summary and key_b in summary:
            sa, sb = summary[key_a], summary[key_b]
            if sa["mean_iou"] is not None and sb["mean_iou"] is not None:
                d_iou = sb["mean_iou"] - sa["mean_iou"]
                if sa["mean_chamfer"] is not None and sb["mean_chamfer"] is not None:
                    d_cd_s = f"{sb['mean_chamfer'] - sa['mean_chamfer']:>+10.4f}"
                else:
                    d_cd_s = "      N/A "
                print(f"{'':>15} {'Δ(b − a)':<13} {'':>5} {d_iou:>+8.4f} {d_cd_s}")
        print()

    print(bar)


# ---------------------------------------------------------------------------
# CSV export
# ---------------------------------------------------------------------------

def write_csv(summary: Dict, path: Path) -> None:
    """Write summary rows to a CSV file."""
    fieldnames = [
        "level", "condition", "n_total", "n_scored",
        "exec_failure_rate", "gold_failure_rate", "mean_iou", "mean_chamfer",
    ]
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in summary.values():
            writer.writerow({k: row.get(k) for k in fieldnames})


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="CadQuery condition-comparison experiment")
    p.add_argument("--model", required=True, help="LLM model name")
    p.add_argument("--split", default="test", choices=["train", "validation", "test"])
    p.add_argument("--max-examples", type=int, default=None,
                   help="Cap number of examples (useful for debugging)")
    p.add_argument("--levels", nargs="+", default=ABSTRACTION_LEVELS,
                   choices=ABSTRACTION_LEVELS)
    p.add_argument("--conditions", nargs="+", default=CONDITIONS, choices=CONDITIONS)
    p.add_argument("--workers", type=int, default=8)
    p.add_argument("--timeout", type=int, default=30,
                   help="Seconds per CadQuery execution")
    p.add_argument("--retries", type=int, default=3,
                   help="Max LLM attempts per example (1 = no retry)")
    p.add_argument("--temperature", type=float, default=0.0)
    p.add_argument("--max-tokens", type=int, default=4096)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--base-url", default=None)
    p.add_argument("--api-key", default=None)
    p.add_argument("--experiment-name", default="cq-experiment")
    p.add_argument("--batch", action="store_true",
                   help="Use Gemini batch API with up to --retries rounds (default 3)")
    p.add_argument("--coverage-only", action="store_true",
                   help="Print dataset coverage report and exit")
    return p.parse_args()


def _build_retry_prompt(base_user_prompt: str, last_code: str, last_error: str) -> str:
    """Append error feedback to the base prompt, mirroring run_one retry format."""
    return (
        base_user_prompt
        + "\n\n"
        "### Your previous code\n"
        "```python\n"
        f"{last_code.strip()}\n"
        "```\n\n"
        "### Execution error\n"
        f"{last_error.strip()}\n\n"
        "### Fix instructions\n"
        "Analyze the error above and fix your code. Do NOT repeat the same mistake.\n"
    )


def run_batch_gemini(
    work_items: List[tuple],
    prompts: Dict[str, str],
    cfg: argparse.Namespace,
    out_dir: Path,
) -> List[Dict]:
    """Run all work items using the Gemini batch API with multi-round retries.

    Round 1: all items. Round 2: failures from round 1 (with error feedback).
    Round 3: failures from round 2. Mirrors the hexagons batch_runner pattern.
    """
    from llm_wrapper import (
        build_gemini_batch_request,
        submit_gemini_batch,
        poll_gemini_batch,
        parse_gemini_batch_results,
    )

    # ── Step 1: Execute gold programs (deduplicated by uid) ───────────────────
    unique_examples = {ex["uid"]: ex for ex, *_ in work_items}
    print(f"  [batch] Executing {len(unique_examples)} gold programs...")
    gold_cache: Dict[str, tuple] = {}

    def _exec_gold(uid_ex):
        uid, ex = uid_ex
        return uid, execute_cq(ex["gold_code"], timeout=cfg.timeout)

    with ThreadPoolExecutor(max_workers=cfg.workers) as pool:
        futures = {pool.submit(_exec_gold, item): item[0] for item in unique_examples.items()}
        for future in as_completed(futures):
            uid, result = future.result()
            gold_cache[uid] = result

    # ── Step 2: Identify non-gold-failed items as the initial round ───────────
    # all_batch_items: full ordered list of (ex, lvl, cond, gold_brep) to process
    all_batch_items: List[tuple] = []
    for ex, lvl, cond in work_items:
        gold_brep, gold_err = gold_cache[ex["uid"]]
        if not gold_err:
            all_batch_items.append((ex, lvl, cond, gold_brep))

    n_gold_failed = len(work_items) - len(all_batch_items)
    print(f"  [batch] {len(all_batch_items)} items to process ({n_gold_failed} gold-failed excluded)")

    max_rounds = min(cfg.retries, 3) if cfg.retries else 3

    # final_results: key (uid, lvl, cond) -> result dict (populated as rounds complete)
    final_results: Dict[tuple, Dict] = {}

    # current_items: items going into the next batch round
    current_items = list(all_batch_items)
    # retry_info: key -> (raw_generated_code, exec_error) from previous round
    retry_info: Dict[tuple, tuple] = {}

    for round_num in range(1, max_rounds + 1):
        if not current_items:
            break

        print(f"\n  [batch] ═══ Round {round_num}/{max_rounds} — {len(current_items)} items ═══")

        # ── Build requests ────────────────────────────────────────────────────
        requests: List[Dict] = []
        for ex, lvl, cond, gold_brep in current_items:
            key = (ex["uid"], lvl, cond)
            base_user_prompt = _fill_prompt(prompts[f"{cond}_user"], ex[lvl])
            if key in retry_info:
                raw_code, exec_error = retry_info[key]
                if raw_code and exec_error:
                    user_prompt = _build_retry_prompt(base_user_prompt, raw_code, exec_error)
                else:
                    user_prompt = base_user_prompt  # batch-level error: resubmit fresh
            else:
                user_prompt = base_user_prompt
            requests.append(build_gemini_batch_request(
                prompt=user_prompt,
                system_prompt=prompts[f"{cond}_system"],
                temperature=cfg.temperature,
                max_tokens=cfg.max_tokens,
            ))

        # ── Submit and poll ───────────────────────────────────────────────────
        display_name = f"{cfg.experiment_name}-r{round_num}"
        print(f"  [batch] Submitting {len(requests)} requests (display={display_name})...")
        job_name = submit_gemini_batch(requests, model=cfg.model, display_name=display_name)
        print(f"  [batch] Job: {job_name}")
        batch_job = poll_gemini_batch(job_name, poll_interval=60)
        llm_results = parse_gemini_batch_results(batch_job, requests)
        n_errors = sum(1 for r in llm_results.values() if r.get("error"))
        print(f"  [batch] Got {len(llm_results)} results, {n_errors} batch-level errors")

        # ── Execute generated code in parallel ────────────────────────────────
        print(f"  [batch] Executing {len(current_items)} generated programs...")
        n_done = 0

        def _exec_pred(args):
            idx, (ex, lvl, cond, gold_brep) = args
            br = llm_results.get(idx)
            result: Dict = {
                "uid": ex["uid"], "level": lvl, "condition": cond,
                "instruction": ex[lvl], "gold_status": "ok",
                "status": None, "error": None,
                "iou": None, "chamfer": None, "usage": {}, "attempts": round_num,
            }
            if br is None or br.get("error"):
                result["status"] = "error"
                result["error"] = (br["error"] if br else "missing batch result")[:500]
                return idx, result, None  # no generated code to use in retry
            result["usage"] = br.get("usage", {})
            generated_code = br.get("text") or ""
            abstraction_layer_path = (
                str(PROMPTS_DIR / "abstraction_layer.py") if cond == "abstraction" else None
            )
            pred_brep, pred_err = execute_cq(
                generated_code, timeout=cfg.timeout,
                abstraction_layer_path=abstraction_layer_path,
                from_llm=True,
            )
            if pred_err:
                result["status"] = "timeout" if pred_err == "TIMEOUT" else "error"
                result["error"] = pred_err[:500]
            else:
                metrics = compute_metrics(pred_brep, gold_brep)
                result["status"] = "ok"
                result["iou"] = metrics["iou"]
                result["chamfer"] = metrics["chamfer"]
            return idx, result, generated_code

        exec_results: Dict[int, tuple] = {}  # idx -> (result, generated_code)
        with ThreadPoolExecutor(max_workers=cfg.workers) as pool:
            futures = {
                pool.submit(_exec_pred, (i, item)): i
                for i, item in enumerate(current_items)
            }
            for future in as_completed(futures):
                idx, r, code = future.result()
                exec_results[idx] = (r, code)
                n_done += 1
                iou_s = f"{r['iou']:.3f}" if r.get("iou") is not None else "N/A"
                print(f"  [{n_done}/{len(current_items)}] {r['uid']} | {r['level']} | {r['condition']} → {r['status']}  IoU={iou_s}")

        # ── Separate successes from failures ──────────────────────────────────
        is_last_round = round_num >= max_rounds
        next_items: List[tuple] = []
        next_retry_info: Dict[tuple, tuple] = {}

        n_success = 0
        for i, (ex, lvl, cond, gold_brep) in enumerate(current_items):
            key = (ex["uid"], lvl, cond)
            r, generated_code = exec_results[i]
            failed = r["status"] in ("error", "timeout")

            if failed and not is_last_round:
                next_items.append((ex, lvl, cond, gold_brep))
                next_retry_info[key] = (generated_code, r["error"])
            else:
                final_results[key] = r
                n_success += 1

        print(
            f"  [batch] Round {round_num} complete: "
            f"{n_success} done, {len(next_items)} will retry"
        )

        current_items = next_items
        retry_info = next_retry_info

    # ── Assemble all results in original work_items order ─────────────────────
    all_results: List[Dict] = []
    for ex, lvl, cond in work_items:
        uid = ex["uid"]
        gold_brep, gold_err = gold_cache[uid]
        if gold_err:
            all_results.append({
                "uid": uid, "level": lvl, "condition": cond,
                "instruction": ex[lvl],
                "gold_status": "error", "status": "gold_failed",
                "error": f"Gold execution failed: {gold_err[:300]}",
                "iou": None, "chamfer": None, "usage": {}, "attempts": 0,
            })
        else:
            all_results.append(final_results[(uid, lvl, cond)])

    return all_results


def main() -> None:
    cfg = parse_args()

    if cfg.coverage_only:
        from cq_dataset import dataset_coverage_report
        print(json.dumps(dataset_coverage_report(), indent=2))
        return

    # Initialise the LLM client (mirrors experiment.py pattern)
    init_llm(cfg)

    out_dir = _results_dir(cfg.experiment_name)
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"Results dir: {out_dir}")

    print(f"Loading dataset  split={cfg.split}  max={cfg.max_examples} ...")
    examples = load_dataset(cfg.split, cfg.max_examples, cfg.levels)
    print(f"  {len(examples)} examples with gold CQ files")

    prompts = load_prompts()

    # Cartesian product: example × level × condition
    work_items = [
        (ex, lvl, cond)
        for ex in examples
        for lvl in cfg.levels
        for cond in cfg.conditions
    ]
    total = len(work_items)
    print(f"  {total} total tasks  ({len(examples)} examples × {len(cfg.levels)} levels × {len(cfg.conditions)} conditions)")

    # Parallel execution (threads — LLM calls are I/O-bound; CadQuery runs in
    # subprocesses spawned by execute_cq inside each thread)
    all_results: List[Dict] = []
    if getattr(cfg, "batch", False):
        all_results = run_batch_gemini(work_items, prompts, cfg, out_dir)
    else:
        with ThreadPoolExecutor(max_workers=cfg.workers) as pool:
            futures = {
                pool.submit(run_one, ex, lvl, cond, prompts, cfg, out_dir): (ex["uid"], lvl, cond)
                for ex, lvl, cond in work_items
            }
            for i, future in enumerate(as_completed(futures), 1):
                uid, lvl, cond = futures[future]
                try:
                    r = future.result()
                    all_results.append(r)
                    iou_s = f"{r['iou']:.3f}" if r.get("iou") is not None else "N/A"
                    cd_s  = f"{r['chamfer']:.4f}" if r.get("chamfer") is not None else "N/A"
                    attempts = r.get("attempts", 1)
                    print(f"[{i}/{total}] {uid} | {lvl} | {cond} → {r['status']} (attempt {attempts})  IoU={iou_s}  CD={cd_s}")
                except Exception as exc:
                    print(f"[{i}/{total}] {uid} | {lvl} | {cond} → EXCEPTION: {exc}")
                    all_results.append({
                        "uid": uid, "level": lvl, "condition": cond,
                        "gold_status": None, "status": "exception", "error": str(exc),
                        "iou": None, "chamfer": None, "usage": {},
                    })

    # Save full results + summary
    ts = _timestamp()
    summary = aggregate(all_results)
    _save_json(
        {"config": vars(cfg), "summary": summary, "results": all_results},
        out_dir / f"{ts}_results.json",
    )
    write_csv(summary, out_dir / f"{ts}_summary.csv")

    print_report(summary, cfg.levels, cfg.conditions)
    print(f"Full results → {out_dir}")


if __name__ == "__main__":
    main()
