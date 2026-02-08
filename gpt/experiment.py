from __future__ import annotations

import argparse
import random
import sys
from pathlib import Path
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

import matplotlib

from config import parse_args
from datasets import get_dataset
from runners.step_runner import run_step_code
from runners.full_runner import run_full
from runners.code_step_full_runner import run_code_step_full
from runners.tiles_runner import run_tile_step
from runners.tiles_full_runner import run_tiles_full
from runners.tiles_step_full_runner import run_tiles_step_full
from runners.python_full_runner import run_python_full
from utils.reading_tasks import read_task
from runner_utils import (
    generate_import_statement,
    DATA_DIR,
    get_results_dir_path,
    ensure_task_dir,
    save_json,
    timestamp,
)
from constants.constants import WIDTH, HEIGHT
from prompts import build_prompts
from metrics import f1_score

matplotlib.use("Agg")

# ──────────────────────────────────────────────────────────────────────────────
# Result summarization
# ──────────────────────────────────────────────────────────────────────────────


def summarize_logs(logs: List[Dict], mode: str, task_id: int) -> Dict:
    """Compute accuracy statistics for a single task."""
    if mode in ("code-step", "code-step-full", "tiles-step", "tiles-step-full"):
        total_steps = len(logs)
        valid_cnt = sum(l.get("valid", False) for l in logs)
        exact_cnt = sum(l.get("exact_board", False) for l in logs)
        exact_action_cnt = sum(l.get("exact_action", False) for l in logs)
        avg_f1_board = sum(l.get("f1_board", 0.0) for l in logs) / total_steps
        avg_f1_action = sum(l.get("f1_action", 0.0) for l in logs) / total_steps
    else:  # code-full, tiles-full, or python-full
        total_steps = 1
        valid_cnt = 1 if logs[0].get("valid", False) else 0
        exact_cnt = 1 if logs[0].get("exact_board", False) else 0
        exact_action_cnt = 1 if logs[0].get("exact_action", False) else 0
        avg_f1_board = logs[0].get("f1_board", 0.0)
        avg_f1_action = logs[0].get("f1_action", 0.0)

    successful_steps = [i + 1 for i, lg in enumerate(logs) if lg["correct"]]
    failed_steps = [i + 1 for i, lg in enumerate(logs) if not lg["correct"]]

    return {
        "task_id": task_id,
        "mode": mode,
        "steps": total_steps,
        "total_attempts": sum(l["attempt"] for l in logs),
        "valid": valid_cnt,
        "exact": exact_cnt,
        "exact_action": exact_action_cnt,
        "f1_board": avg_f1_board,
        "f1_action": avg_f1_action,
        "successful_steps": successful_steps,
        "failed_steps": failed_steps,
    }


def run_task(cfg: argparse.Namespace, task_id, task_data: Dict) -> Dict:
    """
    Execute ONE task (Hexagons or LARC) and return its stats dictionary.

    Args:
        cfg: Configuration namespace
        task_id: Task identifier (int for Hexagons, str for LARC)
        task_data: Task data from dataset
    """
    dataset = get_dataset(cfg.dataset)

    sys_prompt, user_tmpl = build_prompts(cfg.mode, cfg.vision, cfg.api_spec_file, cfg.dataset)
    instructions = dataset.get_instructions(task_data)
    gold_boards = dataset.get_gold_boards(task_data)

    # Get output board dimensions (used only for validation/plotting, NOT passed to LLM for LARC)
    board_width, board_height = dataset.get_board_dimensions(task_data)

    # For LARC: keep the 2D input grid for prompt formatting
    input_grid_2d = task_data.get("test_input")

    out_dir = ensure_task_dir(cfg.experiment_name, task_id)
    run_ts = timestamp()
    run_dir = out_dir / run_ts
    run_dir.mkdir(parents=True, exist_ok=True)

    # Only generate code template for code-generation modes
    code_so_far = ""
    if cfg.mode in ("code-step", "code-full", "code-step-full"):
        if cfg.dataset == "larc":
            code_so_far = ""
        else:
            code_so_far = (
                f"{generate_import_statement(cfg.lib_file)}\n"
                "from constants import HEIGHT, WIDTH\n"
                "with Game() as g:\n"
            )

    current_img: Optional[Path] = DATA_DIR / "empty_board.png" if cfg.vision else None

    history: List[str] = []
    logs: List[Dict] = []
    board_state: List[int] = dataset.get_initial_board(task_data)

    if cfg.mode == "code-step":
        for idx, instruction in enumerate(instructions, 1):
            gold_current = gold_boards[idx - 1]
            prev_gold = gold_boards[idx - 2] if idx > 1 else [0] * (WIDTH * HEIGHT)
            log, _, code_so_far, plot_path = run_step_code(
                cfg,
                sys_prompt,
                user_tmpl,
                instruction,
                history,
                code_so_far,
                gold_current,
                prev_gold,
                current_img,
                run_dir,
                idx,
                run_ts,
            )
            logs.append(log)
            history.append(instruction)

            if cfg.vision and log["valid"]:
                current_img = plot_path

            print(
                f"[task {task_id}] [step {idx}/{len(instructions)}] "
                f"{'✓✓' if log['correct'] else ('✓' if log['valid'] else '✗')}"
                f" (try {log['attempt']})"
            )

    elif cfg.mode == "code-full":
        log = run_full(
            cfg,
            sys_prompt,
            user_tmpl,
            instructions,
            code_so_far,
            gold_boards[-1],
            current_img,
            run_dir,
            run_ts,
            input_grid_2d=input_grid_2d,
            width=board_width,
            height=board_height,
        )
        logs = [log]
        print(
            f"[task {task_id}] CODE-FULL RUN →",
            "✓✓" if log["correct"] else ("✓" if log["valid"] else "✗"),
        )

    elif cfg.mode == "code-step-full":
        for idx, instruction in enumerate(instructions, 1):
            gold_current = gold_boards[idx - 1]
            prev_gold = gold_boards[idx - 2] if idx > 1 else [0] * (WIDTH * HEIGHT)
            log, _, code_so_far, plot_path = run_code_step_full(
                cfg,
                sys_prompt,
                user_tmpl,
                instruction,
                instructions,  # pass all instructions
                history,
                code_so_far,
                gold_current,
                prev_gold,
                current_img,
                run_dir,
                idx,
                run_ts,
            )
            logs.append(log)
            history.append(instruction)

            if cfg.vision and log["valid"]:
                current_img = plot_path

            print(
                f"[task {task_id}] [step {idx}/{len(instructions)}] "
                f"{'✓✓' if log['correct'] else ('✓' if log['valid'] else '✗')}"
                f" (try {log['attempt']})"
            )

    elif cfg.mode == "tiles-full":
        log = run_tiles_full(
            cfg,
            sys_prompt,
            user_tmpl,
            instructions,
            gold_boards[-1],
            current_img,
            run_dir,
            run_ts,
            dataset.get_initial_board(task_data),
            board_width,
            board_height,
            input_grid_2d,
        )
        logs = [log]
        print(
            f"[task {task_id}] TILES-FULL RUN →",
            "✓✓" if log["correct"] else ("✓" if log["valid"] else "✗"),
        )

    elif cfg.mode == "python-full":
        log = run_python_full(
            cfg,
            sys_prompt,
            user_tmpl,
            instructions,
            gold_boards[-1],
            current_img,
            run_dir,
            run_ts,
            dataset.get_initial_board(task_data),
            board_width,
            board_height,
            input_grid_2d,
        )
        logs = [log]
        print(
            f"[task {task_id}] PYTHON-FULL RUN →",
            "✓✓" if log["correct"] else ("✓" if log["valid"] else "✗"),
        )

    elif cfg.mode == "tiles-step-full":
        for idx, instruction in enumerate(instructions, 1):
            gold_current = gold_boards[idx - 1]
            prev_gold = gold_boards[idx - 2] if idx > 1 else dataset.get_initial_board(task_data)
            log, _, board_state, plot_path = run_tiles_step_full(
                cfg,
                sys_prompt,
                user_tmpl,
                instruction,
                instructions,  # pass all instructions
                history,
                board_state,
                gold_current,
                prev_gold,
                current_img,
                run_dir,
                idx,
                run_ts,
                board_width,
                board_height,
                input_grid_2d,
            )
            logs.append(log)
            history.append(instruction)

            if cfg.vision and log["valid"]:
                current_img = plot_path

            print(
                f"[task {task_id}] [step {idx}/{len(instructions)}] "
                f"{'✓✓' if log['correct'] else ('✓' if log['valid'] else '✗')}"
                f" (try {log['attempt']})"
            )

    else:  # cfg.mode == "tiles-step"
        for idx, instruction in enumerate(instructions, 1):
            gold_current = gold_boards[idx - 1]
            prev_gold = gold_boards[idx - 2] if idx > 1 else dataset.get_initial_board(task_data)
            log, _, board_state, plot_path = run_tile_step(
                cfg,
                sys_prompt,
                user_tmpl,
                instruction,
                history,
                board_state,
                gold_current,
                prev_gold,
                current_img,
                run_dir,
                idx,
                run_ts,
                board_width,
                board_height,
                input_grid_2d,
            )
            logs.append(log)
            history.append(instruction)

            if cfg.vision and log["valid"]:
                current_img = plot_path

            print(
                f"[task {task_id}] [step {idx}/{len(instructions)}] "
                f"{'✓✓' if log['correct'] else ('✓' if log['valid'] else '✗')}"
                f" (try {log['attempt']})"
            )

    stats = summarize_logs(logs, cfg.mode, task_id)

    run_log_path = run_dir / f"run_{timestamp()}.json"
    save_json({"stats": stats, "runs": logs}, run_log_path)

    print(f"\nFinished task {task_id}")
    print(f"  • valid code    : {stats['valid']}/{stats['steps']}")
    print(f"  • exact match   : {stats['exact']}/{stats['steps']}")
    print(f"  • action exact  : {stats['exact_action']}/{stats['steps']}")
    print(f"  • board F1      : {stats['f1_board']:.3f}")
    print(f"  • action F1     : {stats['f1_action']:.3f}")

    return {
        "stats": stats,
        "runs": logs,
        "run_dir": str(run_dir),
        "run_log_path": str(run_log_path),
    }


# ──────────────────────────────────────────────────────────────────────────────
# Main entry
# ──────────────────────────────────────────────────────────────────────────────


def _run_set(cfg: argparse.Namespace) -> None:
    """Run and summarise all tasks from a dataset split, then emit ONE JSON."""
    print(f"Running full set: {cfg.set}")
    dataset = get_dataset(cfg.dataset)
    tasks = list(dataset.iter_tasks(cfg.set))

    per_task_payloads: List[Dict] = [None] * len(tasks)

    if cfg.workers <= 1:
        for idx, (tid, task_data) in enumerate(tasks):
            print(f"\n=== TASK {tid} ===")
            payload = run_task(cfg, tid, task_data)
            per_task_payloads[idx] = payload
    else:
        from concurrent.futures import ThreadPoolExecutor, as_completed

        with ThreadPoolExecutor(max_workers=cfg.workers) as ex:
            futures = {
                ex.submit(run_task, cfg, tid, task_data): i
                for i, (tid, task_data) in enumerate(tasks)
            }
            for fut in as_completed(futures):
                idx = futures[fut]
                try:
                    per_task_payloads[idx] = fut.result()
                except Exception as exc:
                    tid = tasks[idx][0]
                    print(f"Task {tid} failed: {exc}")
                    per_task_payloads[idx] = {
                        "stats": {
                            "task_id": tid,
                            "mode": cfg.mode,
                            "steps": 0,
                            "total_attempts": 0,
                            "valid": 0,
                            "exact": 0,
                            "exact_action": 0,
                            "f1_board": 0.0,
                            "f1_action": 0.0,
                            "successful_steps": [],
                            "failed_steps": [],
                        },
                        "runs": [],
                        "run_dir": None,
                        "run_log_path": None,
                    }

    # ---------- aggregate ----------
    stats_list = [p["stats"] for p in per_task_payloads]
    total_steps = sum(s["steps"] for s in stats_list) or 0
    valid_total = sum(s["valid"] for s in stats_list)
    exact_total = sum(s["exact"] for s in stats_list)
    exact_action_total = sum(s["exact_action"] for s in stats_list)

    # accumulate raw tile counts from every step log
    board_tp = board_p = board_g = 0
    action_tp = action_p = action_g = 0

    for payload in per_task_payloads:
        for lg in payload["runs"]:
            board_tp += lg.get("board_tp", 0)
            board_p += lg.get("board_p", 0)
            board_g += lg.get("board_g", 0)
            action_tp += lg.get("action_tp", 0)
            action_p += lg.get("action_p", 0)
            action_g += lg.get("action_g", 0)

    def _safe_ratio(num: int, den: int, alt: float) -> float:
        return num / den if den else alt

    # board micro-F1
    prec_b = _safe_ratio(board_tp, board_p, 1.0 if board_g == 0 else 0.0)
    rec_b = _safe_ratio(board_tp, board_g, 1.0 if board_p == 0 else 0.0)
    f1_board_total = f1_score(prec_b, rec_b)

    # action micro-F1
    prec_a = _safe_ratio(action_tp, action_p, 1.0 if action_g == 0 else 0.0)
    rec_a = _safe_ratio(action_tp, action_g, 1.0 if action_p == 0 else 0.0)
    f1_action_total = f1_score(prec_a, rec_a)

    print("\n=== SET SUMMARY ===")
    print(f"  • tasks         : {len(stats_list)}")
    print(f"  • valid code    : {valid_total}/{total_steps}")
    print(f"  • exact match   : {exact_total}/{total_steps}")
    print(f"  • action exact  : {exact_action_total}/{total_steps}")
    print(f"  • board F1      : {f1_board_total:.3f}")
    print(f"  • action F1     : {f1_action_total:.3f}")

    out_dir = get_results_dir_path(cfg.experiment_name) / cfg.set
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = timestamp()

    single_payload = {
        "config": vars(cfg),
        "aggregate": {
            "set": cfg.set,
            "n_tasks": len(stats_list),
            "total_steps": total_steps,
            "valid": valid_total,
            "exact": exact_total,
            "exact_action": exact_action_total,
            "f1_board": f1_board_total,
            "f1_action": f1_action_total,
        },
        "tasks": [
            {
                **p["stats"],
                "runs": p["runs"],
                "run_dir": p["run_dir"],
                "run_log_path": p["run_log_path"],
            }
            for p in per_task_payloads
        ],
    }

    single_path = out_dir / f"all_{ts}.json"
    save_json(single_payload, single_path)
    print(f"\nSingle JSON written to: {single_path}")


def main() -> None:
    cfg = parse_args()
    random.seed(cfg.seed)

    if cfg.set:
        _run_set(cfg)
    else:
        dataset = get_dataset(cfg.dataset)
        task_data = read_task(cfg.task) if cfg.dataset == "hexagons" else None
        if task_data is None:
            raise ValueError(f"Single task mode (--task) requires hexagons dataset")
        _ = run_task(cfg, cfg.task, task_data)


if __name__ == "__main__":
    main()
