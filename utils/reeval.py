from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Tuple

from constants.constants import WIDTH, HEIGHT
from utils.reading_tasks import read_task
from gpt.metrics import evaluate_prediction, f1_score


def _exec_script(code: str) -> Tuple[List[int], str | None]:
    """
    Run a generated step script and return (board_pred, err_msg).
    Falls back to an all-white board on error.
    """
    ns: Dict[str, object] = {}
    try:
        exec(code, ns)  # pylint: disable=exec-used
        board_pred = ns["board_state"]  # type: ignore[index]
        return board_pred, None
    except Exception as exc:  # pylint: disable=broad-except
        return [0] * (WIDTH * HEIGHT), str(exc)


def _latest_attempts(step_files: List[Path]) -> Dict[int, Path]:
    """
    Keep only the last attempt for every step index.
    """
    pat = re.compile(r"_step_(\d{2})_(\d{2})\.py$")
    latest: Dict[int, Tuple[int, Path]] = {}
    for p in step_files:
        m = pat.search(p.name)
        if not m:
            continue
        step, attempt = int(m.group(1)), int(m.group(2))
        # keep the highest attempt id
        if step not in latest or attempt > latest[step][0]:
            latest[step] = (attempt, p)
    # strip attempt from the dict
    return {step: pair[1] for step, pair in latest.items()}


def reevaluate_run(run_root: str | Path, timeout: int | None = None) -> Dict:
    """
    Re-compute board/action F1 for every step, every task, and the whole set.

    Parameters
    ----------
    run_root : str | Path
        Path produced by a previous experiment run (contains task folders).
    timeout : int | None
        Optional per-script soft timeout in seconds (``None`` = no timeout).
        Implement your own timeout logic if desired.

    Returns
    -------
    dict
        Aggregate results mirroring the structure of the original summary:
        {
            "aggregate": {...},
            "tasks": [
                {
                    "task_id": ...,
                    "steps": [
                        {"step": 1, "f1_board": 1.0, "f1_action": 1.0},
                        ...
                    ],
                    "f1_board": <task-average>,
                    "f1_action": <task-average>,
                },
                ...
            ],
        }
    """
    run_root = Path(run_root)
    if not run_root.is_dir():
        raise FileNotFoundError(run_root)

    # ---------- global counters for micro-F1 ----------
    board_tp = board_p = board_g = 0
    action_tp = action_p = action_g = 0

    tasks_payload: List[Dict] = []

    task_pat = re.compile(r"^(?:task_)?(\d+)$")  # matches "15" or "task_15"

    for task_dir in sorted(d for d in run_root.iterdir() if d.is_dir()):
        m = task_pat.match(task_dir.name)
        if not m:  # skip folders that aren’t tasks
            continue
        task_id = int(m.group(1))
        gold = read_task(task_id)  # -> {"gold_boards": [...], ...}
        gold_boards: List[List[int]] = gold["gold_boards"]

        # exactly ONE timestamp subfolder per task
        ts_dirs = [d for d in task_dir.iterdir() if d.is_dir()]
        if not ts_dirs:
            print(f"[WARN] No timestamp folder in {task_dir}")
            continue
        run_dir = ts_dirs[0]

        # pick last attempt of every step
        step_files = _latest_attempts(list(run_dir.glob("*_step_*.py")))

        prev_pred = [0] * (WIDTH * HEIGHT)
        prev_gold = [0] * (WIDTH * HEIGHT)
        step_metrics: List[Dict] = []

        for step_idx in sorted(step_files):
            code_path = step_files[step_idx]
            board_pred, err = _exec_script(code_path.read_text())

            m = evaluate_prediction(
                prev_pred,
                board_pred,
                prev_gold,
                gold_boards[step_idx - 1],
            )

            step_metrics.append(
                {
                    "step": step_idx,
                    "f1_board": m["f1_board"],
                    "f1_action": m["f1_action"],
                    "valid": err is None,
                }
            )

            # accumulate micro counts
            board_tp += m.get("board_tp", 0)
            board_p += m.get("board_p", 0)
            board_g += m.get("board_g", 0)
            action_tp += m.get("action_tp", 0)
            action_p += m.get("action_p", 0)
            action_g += m.get("action_g", 0)

            prev_pred = board_pred
            prev_gold = gold_boards[step_idx - 1]

        # task-level macro F1 (simple mean across steps)
        task_f1_board = (
            sum(s["f1_board"] for s in step_metrics) / len(step_metrics)
            if step_metrics
            else 0.0
        )
        task_f1_action = (
            sum(s["f1_action"] for s in step_metrics) / len(step_metrics)
            if step_metrics
            else 0.0
        )

        tasks_payload.append(
            {
                "task_id": task_id,
                "steps": step_metrics,
                "f1_board": task_f1_board,
                "f1_action": task_f1_action,
            }
        )

    # ---------- set-level micro-F1 ----------
    def _safe(num: int, den: int, alt: float) -> float:
        return num / den if den else alt

    prec_b = _safe(board_tp, board_p, 1.0 if board_g == 0 else 0.0)
    rec_b = _safe(board_tp, board_g, 1.0 if board_p == 0 else 0.0)
    set_f1_board = f1_score(prec_b, rec_b)

    prec_a = _safe(action_tp, action_p, 1.0 if action_g == 0 else 0.0)
    rec_a = _safe(action_tp, action_g, 1.0 if action_p == 0 else 0.0)
    set_f1_action = f1_score(prec_a, rec_a)

    return {
        "aggregate": {
            "n_tasks": len(tasks_payload),
            "board_tp": board_tp,
            "board_p": board_p,
            "board_g": board_g,
            "action_tp": action_tp,
            "action_p": action_p,
            "action_g": action_g,
            "f1_board": set_f1_board,
            "f1_action": set_f1_action,
        },
        "tasks": tasks_payload,
    }


# ---------------------------------------------------------------------------
# Convenience CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse, json

    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir", help="Folder produced by the original experiment")
    ap.add_argument("-o", "--out", help="Write JSON summary to this path")
    args = ap.parse_args()

    summary = reevaluate_run(args.run_dir)
    print(json.dumps(summary["aggregate"], indent=2))

    if args.out:
        Path(args.out).write_text(json.dumps(summary, indent=2))
        print(f"Wrote full summary → {args.out}")
