"""Run GPT step-wise code-completion for a single Hexagons task.

Usage
-----
$ python experiment.py --task 24 --model gpt-4o [--vision]
"""

from __future__ import annotations

import argparse
import random
import traceback
from pathlib import Path
from typing import Dict, List, Optional
import json

from openai_wrapper import call_gpt
from utils.reading_tasks import read_task
from runner_utils import (
    DATA_DIR,
    RESULTS_DIR,
    ensure_task_dir,
    extract_code,
    parse_tile_actions,
    save_json,
    save_plot,
    timestamp,
    f1_score,
)
from constants.constants import WIDTH, HEIGHT

# ──────────────────────────────────────────────────────────────────────────────
# CLI helpers
# ──────────────────────────────────────────────────────────────────────────────


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()

    grp = p.add_mutually_exclusive_group(required=True)
    grp.add_argument("--task", type=int, help="Run a single task ID (legacy mode)")
    grp.add_argument(
        "--set",
        choices=["train", "dev", "test"],
        help="Run every task listed in the chosen JSONL file",
    )
    p.add_argument("--model", default="gpt-4o")
    p.add_argument("--temperature", type=float, default=1)
    p.add_argument("--max-tokens", type=int, default=512)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument(
        "--history",
        dest="history",
        action="store_true",
        default=True,
        help="Include previous instructions in each prompt",
    )
    p.add_argument(
        "--no-history",
        dest="history",
        action="store_false",
        help="Send only the current instruction",
    )
    p.add_argument(
        "--retries", type=int, default=3, help="Max attempts per step (0 = unlimited)"
    )
    p.add_argument(
        "--mode",
        choices=["step", "full", "tiles"],
        default="step",
        help="step = one instruction at a time (default); "
        "full = send ALL instructions in one prompt; "
        "tiles = predict tiles step-by-step instead of code",
    )
    p.add_argument(
        "--vision",
        action="store_true",
        help="Attach current board image to each prompt",
    )
    return p.parse_args()


def iter_set_tasks(split: str):
    import json

    path = DATA_DIR / f"{split}.jsonl"
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            o = json.loads(line)
            proc = [r for r in o["drawing_procedure"] if r[1] != "NONE"]
            yield o["index"], {
                "steps": [r[1] for r in proc],
                "gold_boards": [r[2] for r in proc],
            }


# ──────────────────────────────────────────────────────────────────────────────
# Prompt helpers
# ──────────────────────────────────────────────────────────────────────────────


def build_prompts(mode: str) -> tuple[str, str]:
    """Load system & user templates for the selected mode."""
    if mode == "tiles":
        sys_p = DATA_DIR / "system_prompt_tiles.txt"
        user_p = DATA_DIR / "user_message_tiles.txt"
    else:
        sys_p = DATA_DIR / "system_prompt_01.txt"
        user_p = DATA_DIR / "user_message_01.txt"

    system_tmpl = sys_p.read_text()
    user_tmpl = user_p.read_text()

    tags = ["{HISTORY_BLOCK}", "{NEXT_STEP}"]
    if mode != "tiles":
        tags.append("{CODE_SO_FAR}")
    for tag in tags:
        if tag not in user_tmpl:
            raise ValueError(f"{user_p.name} missing placeholder {tag}")
    return system_tmpl, user_tmpl


def make_user_prompt(instr: str, history: List[str], template: str, code: str) -> str:
    hist_block = "\n".join(f"{i+1}. {h}" for i, h in enumerate(history)) or "(none yet)"
    return (
        template.replace("{HISTORY_BLOCK}", hist_block)
        .replace("{CODE_SO_FAR}", code.rstrip())
        .replace("{NEXT_STEP}", f"    # TODO: {instr.strip()}")
    )


def make_tile_prompt(instr: str, history: List[str], template: str) -> str:
    """Format prompt for tile prediction mode."""
    hist_block = "\n".join(f"{i+1}. {h}" for i, h in enumerate(history)) or "(none yet)"
    return template.replace("{HISTORY_BLOCK}", hist_block).replace(
        "{NEXT_STEP}", instr.strip()
    )


def _board_metrics(
    pred: List[int], gold: List[int]
) -> tuple[float, float, float, bool]:
    """Return precision, recall, F1 and exact match for two board states."""
    correct = sum(1 for p, g in zip(pred, gold) if p == g and g != 0)
    pred_colored = sum(1 for p in pred if p != 0)
    gold_colored = sum(1 for g in gold if g != 0)
    if pred_colored:
        precision = correct / pred_colored
    else:
        precision = 1.0 if gold_colored == 0 else 0.0
    if gold_colored:
        recall = correct / gold_colored
    else:
        recall = 1.0 if pred_colored == 0 else 0.0
    f1 = f1_score(precision, recall)
    exact = pred == gold
    return precision, recall, f1, exact


def _action_metrics(
    prev_pred: List[int], pred: List[int], prev_gold: List[int], gold: List[int]
) -> tuple[float, float, float, bool]:
    """Metrics for changed tiles only (action-based)."""
    pred_diff = {i for i, (a, b) in enumerate(zip(prev_pred, pred)) if a != b}
    gold_diff = {i for i, (a, b) in enumerate(zip(prev_gold, gold)) if a != b}
    correct = {i for i in pred_diff if i in gold_diff and pred[i] == gold[i]}
    if pred_diff:
        precision = len(correct) / len(pred_diff)
    else:
        precision = 1.0 if not gold_diff else 0.0
    if gold_diff:
        recall = len(correct) / len(gold_diff)
    else:
        recall = 1.0 if not pred_diff else 0.0
    f1 = f1_score(precision, recall)
    exact = pred_diff == gold_diff and all(pred[i] == gold[i] for i in pred_diff)
    return precision, recall, f1, exact


# ──────────────────────────────────────────────────────────────────────────────
# GPT ↔ execution loop
# ──────────────────────────────────────────────────────────────────────────────


def run_step_code(
    cfg: argparse.Namespace,
    sys_prompt: str,
    user_tmpl: str,
    instruction: str,
    history: List[str],
    code: str,
    gold_board: List[int],
    prev_gold_board: List[int],
    image_path: Optional[Path],
    out_dir: Path,
    step_idx: int,
    run_ts: str,
) -> tuple[Dict, bool, str, Optional[Path]]:
    """Run one code-completion step and return updated script and log."""
    attempt = 0
    prev_pred_board: List[int]
    try:
        ns_prev: Dict[str, object] = {}
        exec(code, ns_prev)
        prev_pred_board = ns_prev["board_state"]
    except Exception:
        prev_pred_board = [0] * (WIDTH * HEIGHT)
    while True:
        attempt += 1

        code_with_todo = f"{code.rstrip()}\n"
        prompt = make_user_prompt(
            instr=instruction,
            history=history,
            template=user_tmpl,
            code=code_with_todo,
        )

        resp = call_gpt(
            prompt=prompt,
            system_prompt=sys_prompt,
            model=cfg.model,
            temperature=cfg.temperature,
            max_tokens=cfg.max_tokens,
            seed=cfg.seed,
            images=[str(image_path)] if image_path else None,
        )

        append = extract_code(resp["text"])
        new_script = f"{code.rstrip()}\n    {append}"

        if "board_state = g.board_state" not in new_script:
            new_script += "\nboard_state = g.board_state"

        log = {
            "step": step_idx,
            "attempt": attempt,
            "usage": resp["usage"],
            "code": append,
            "valid": False,
            "correct": False,
        }

        ns: Dict[str, object] = {}
        try:
            exec(new_script, ns)
            pred = ns["board_state"]
            log["valid"] = True
            b_prec, b_rec, b_f1, b_exact = _board_metrics(pred, gold_board)
            a_prec, a_rec, a_f1, a_exact = _action_metrics(
                prev_pred_board, pred, prev_gold_board, gold_board
            )
            log.update(
                {
                    "correct": b_exact,
                    "precision_board": b_prec,
                    "recall_board": b_rec,
                    "f1_board": b_f1,
                    "exact_board": b_exact,
                    "precision_action": a_prec,
                    "recall_action": a_rec,
                    "f1_action": a_f1,
                    "exact_action": a_exact,
                }
            )
            plot_path = out_dir / f"{run_ts}_plot_{step_idx:02}_{attempt:02}.png"
            plot_with_gold_path = (
                out_dir / f"{run_ts}_plot_{step_idx:02}_{attempt:02}_gold.png"
            )
            save_plot(pred, None, plot_path)
            save_plot(pred, gold_board, plot_with_gold_path)
            return log, True, new_script, plot_path
        except Exception:
            log["traceback"] = traceback.format_exc()
            if cfg.retries and attempt >= cfg.retries:
                return log, False, code, image_path  # keep previous image


def run_tile_step(
    cfg: argparse.Namespace,
    sys_prompt: str,
    user_tmpl: str,
    instruction: str,
    history: List[str],
    board: List[int],
    gold_board: List[int],
    prev_gold_board: List[int],
    image_path: Optional[Path],
    out_dir: Path,
    step_idx: int,
    run_ts: str,
) -> tuple[Dict, bool, List[int], Optional[Path]]:
    """Prompt GPT for tile predictions and update board state."""
    attempt = 0
    from constants.constants import COLORS, WIDTH, HEIGHT

    while True:
        attempt += 1
        prompt = make_tile_prompt(instruction, history, user_tmpl)
        resp = call_gpt(
            prompt=prompt,
            system_prompt=sys_prompt,
            model=cfg.model,
            temperature=cfg.temperature,
            max_tokens=cfg.max_tokens,
            seed=cfg.seed,
            images=[str(image_path)] if image_path else None,
        )

        tiles = parse_tile_actions(resp["text"])
        new_board = board.copy()
        for r, c, col in tiles:
            if 1 <= r <= HEIGHT and 1 <= c <= WIDTH and col in COLORS:
                idx = (r - 1) * WIDTH + (c - 1)
                new_board[idx] = COLORS.index(col)

        b_prec, b_rec, b_f1, b_exact = _board_metrics(new_board, gold_board)
        a_prec, a_rec, a_f1, a_exact = _action_metrics(
            board, new_board, prev_gold_board, gold_board
        )
        log = {
            "step": step_idx,
            "attempt": attempt,
            "usage": resp["usage"],
            "tiles": tiles,
            "valid": True,
            "correct": b_exact,
            "precision_board": b_prec,
            "recall_board": b_rec,
            "f1_board": b_f1,
            "exact_board": b_exact,
            "precision_action": a_prec,
            "recall_action": a_rec,
            "f1_action": a_f1,
            "exact_action": a_exact,
        }

        plot_path = out_dir / f"{run_ts}_plot_{step_idx:02}_{attempt:02}.png"
        plot_with_gold_path = out_dir / (
            f"{run_ts}_plot_{step_idx:02}_{attempt:02}_gold.png"
        )
        save_plot(new_board, None, plot_path)
        save_plot(new_board, gold_board, plot_with_gold_path)
        return log, True, new_board, plot_path


def run_full(
    cfg: argparse.Namespace,
    sys_prompt: str,
    user_tmpl: str,
    instructions: List[str],
    code_so_far: str,
    gold_final: List[int],
    image_path: Optional[Path],
    task_dir: Path,
    run_ts: str,
) -> Dict:
    """
    Single-shot prompt that passes ALL instructions as one indented block.
    """
    todo_block = "\n".join(f"    # TODO: {txt}" for txt in instructions)

    prompt = (
        user_tmpl.replace("{HISTORY_BLOCK}", "(none – full run)")
        .replace("{CODE_SO_FAR}", code_so_far.rstrip())
        .replace("{NEXT_STEP}", todo_block)
    )

    resp = call_gpt(
        prompt=prompt,
        system_prompt=sys_prompt,
        model=cfg.model,
        temperature=cfg.temperature,
        max_tokens=cfg.max_tokens,
        seed=cfg.seed,
        images=[str(image_path)] if image_path else None,
    )

    append = extract_code(resp["text"])
    new_code = f"{code_so_far.rstrip()}\n    {append}"

    if "board_state = g.board_state" not in new_code:
        new_code += "\nboard_state = g.board_state"

    log = {
        "attempt": 1,
        "code": new_code,
        "valid": False,
        "correct": False,
        "usage": resp["usage"],
    }

    ns = {}
    try:
        exec(new_code, ns)
        board_pred = ns["board_state"]
        log["valid"] = True
        b_prec, b_rec, b_f1, b_exact = _board_metrics(board_pred, gold_final)
        log.update(
            {
                "correct": b_exact,
                "precision_board": b_prec,
                "recall_board": b_rec,
                "f1_board": b_f1,
                "exact_board": b_exact,
                "precision_action": b_prec,
                "recall_action": b_rec,
                "f1_action": b_f1,
                "exact_action": b_exact,
            }
        )
        save_plot(board_pred, gold_final, task_dir / f"{run_ts}_plot_full.png")
    except Exception:
        log["traceback"] = traceback.format_exc()

    return log


def summarize_logs(logs: List[Dict], mode: str, task_id: int) -> Dict:
    """Compute accuracy statistics for a single task."""
    if mode in ("step", "tiles"):
        total_steps = len(logs)
        valid_cnt = sum(l["valid"] for l in logs)
        exact_cnt = sum(l["exact_board"] for l in logs)
        exact_action_cnt = sum(l["exact_action"] for l in logs)
        avg_f1_board = sum(l["f1_board"] for l in logs) / total_steps
        avg_f1_action = sum(l["f1_action"] for l in logs) / total_steps
    else:
        total_steps = 1
        valid_cnt = 1 if logs[0]["valid"] else 0
        exact_cnt = 1 if logs[0]["exact_board"] else 0
        exact_action_cnt = 1 if logs[0]["exact_board"] else 0
        avg_f1_board = logs[0]["f1_board"]
        avg_f1_action = logs[0]["f1_board"]

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


def run_task(cfg: argparse.Namespace, task_id: int, task: Dict) -> Dict:
    """
    Execute ONE Hexagons task and return its stats dictionary.
    This is the original single-task logic extracted from main().
    """
    sys_prompt, user_tmpl = build_prompts(cfg.mode)
    instructions = task["steps"]
    gold_boards = task["gold_boards"]

    out_dir = ensure_task_dir(task_id)
    run_ts = timestamp()
    run_dir = out_dir / run_ts
    run_dir.mkdir(parents=True, exist_ok=True)

    code_so_far = (
        "from hexagen import Game, Tile, Shape, Line, Circle, Triangle\n"
        "with Game() as g:\n"
    )

    current_img: Optional[Path] = DATA_DIR / "empty_board.png" if cfg.vision else None

    history: List[str] = []
    logs: List[Dict] = []
    board_state: List[int] = [0] * (WIDTH * HEIGHT)

    if cfg.mode == "step":
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

    elif cfg.mode == "full":
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
        )
        logs = [log]
        print(
            f"[task {task_id}] FULL RUN →",
            "✓✓" if log["correct"] else ("✓" if log["valid"] else "✗"),
        )

    else:  # cfg.mode == "tiles"
        for idx, instruction in enumerate(instructions, 1):
            gold_current = gold_boards[idx - 1]
            prev_gold = gold_boards[idx - 2] if idx > 1 else [0] * (WIDTH * HEIGHT)
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

    # save per-task log
    save_json({"stats": stats, "runs": logs}, run_dir / f"run_{timestamp()}.json")

    print(f"\nFinished task {task_id}")
    print(f"  • valid code    : {stats['valid']}/{stats['steps']}")
    print(f"  • exact match   : {stats['exact']}/{stats['steps']}")
    print(f"  • action exact  : {stats['exact_action']}/{stats['steps']}")
    print(f"  • board F1      : {stats['f1_board']:.3f}")
    print(f"  • action F1     : {stats['f1_action']:.3f}")
    return stats


# ──────────────────────────────────────────────────────────────────────────────
# Main entry
# ──────────────────────────────────────────────────────────────────────────────


def _run_set(cfg: argparse.Namespace) -> None:
    """Run and summarise all tasks from a dataset split."""
    print(f"Running full set: {cfg.set}")
    per_task_stats = []
    for tid, tsk in iter_set_tasks(cfg.set):
        print(f"\n=== TASK {tid} ===")
        st = run_task(cfg, tid, tsk)
        per_task_stats.append(st)

    total_steps = sum(s["steps"] for s in per_task_stats)
    valid_total = sum(s["valid"] for s in per_task_stats)
    exact_total = sum(s["exact"] for s in per_task_stats)
    exact_action_total = sum(s["exact_action"] for s in per_task_stats)
    f1_board_total = (
        sum(s["f1_board"] * s["steps"] for s in per_task_stats) / total_steps
        if total_steps
        else 0.0
    )
    f1_action_total = (
        sum(s["f1_action"] * s["steps"] for s in per_task_stats) / total_steps
        if total_steps
        else 0.0
    )

    print("\n=== SET SUMMARY ===")
    print(f"  • tasks         : {len(per_task_stats)}")
    print(f"  • valid code    : {valid_total}/{total_steps}")
    print(f"  • exact match   : {exact_total}/{total_steps}")
    print(f"  • action exact  : {exact_action_total}/{total_steps}")
    print(f"  • board F1      : {f1_board_total:.3f}")
    print(f"  • action F1     : {f1_action_total:.3f}")

    out_dir = RESULTS_DIR / cfg.set
    out_dir.mkdir(parents=True, exist_ok=True)

    summary_payload = [
        {
            "task_id": s["task_id"],
            "successful_steps": s["successful_steps"],
            "failed_steps": s["failed_steps"],
            "f1_board": s["f1_board"],
            "f1_action": s["f1_action"],
            "exact": s["exact"],
            "exact_action": s["exact_action"],
        }
        for s in per_task_stats
    ]
    save_json(summary_payload, out_dir / f"summary_{timestamp()}.json")

    save_json(
        {
            "aggregate": {
                "set": cfg.set,
                "n_tasks": len(per_task_stats),
                "total_steps": total_steps,
                "valid": valid_total,
                "exact": exact_total,
                "exact_action": exact_action_total,
                "f1_board": f1_board_total,
                "f1_action": f1_action_total,
            },
            "per_task": per_task_stats,
        },
        out_dir / f"runs_{timestamp()}.json",
    )


def main() -> None:
    cfg = parse_args()
    random.seed(cfg.seed)

    if cfg.set:
        _run_set(cfg)
    else:
        _ = run_task(cfg, cfg.task, read_task(cfg.task))


if __name__ == "__main__":
    main()
