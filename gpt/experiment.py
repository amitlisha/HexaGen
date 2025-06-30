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

from openai_wrapper import call_gpt
from utils.reading_tasks import read_task
from runner_utils import (
    DATA_DIR,
    ensure_task_dir,
    extract_code,
    save_json,
    save_plot,
    timestamp,
)

# ──────────────────────────────────────────────────────────────────────────────
# CLI helpers
# ──────────────────────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--task", type=int, required=True)
    p.add_argument("--model", default="gpt-4o")
    p.add_argument("--temperature", type=float, default=1)
    p.add_argument("--max-tokens", type=int, default=512)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--history", dest="history", action="store_true", default=True,
                   help="Include previous instructions in each prompt")
    p.add_argument("--no-history", dest="history", action="store_false",
                   help="Send only the current instruction")
    p.add_argument("--retries", type=int, default=3,
                   help="Max attempts per step (0 = unlimited)")
    p.add_argument(
        "--mode",
        choices=["step", "full"],
        default="step",
        help="step = one instruction at a time (default); "
             "full = send ALL instructions in one prompt",
    )
    p.add_argument("--vision", action="store_true",
                   help="Attach current board image to each prompt")
    return p.parse_args()

# ──────────────────────────────────────────────────────────────────────────────
# Prompt helpers
# ──────────────────────────────────────────────────────────────────────────────

def build_prompts() -> tuple[str, str]:
    """Load system & user templates (checks required placeholders)."""
    system_tmpl = (DATA_DIR / "system_prompt_01.txt").read_text()
    user_tmpl   = (DATA_DIR / "user_message_01.txt").read_text()
    for tag in ("{HISTORY_BLOCK}", "{CODE_SO_FAR}", "{NEXT_STEP}"):
        if tag not in user_tmpl:
            raise ValueError(f"user_message_01.txt missing placeholder {tag}")
    return system_tmpl, user_tmpl


def make_user_prompt(instr: str, history: List[str], template: str, code: str) -> str:
    hist_block = "\n".join(f"{i+1}. {h}" for i, h in enumerate(history)) or "(none yet)"
    return (template
            .replace("{HISTORY_BLOCK}", hist_block)
            .replace("{CODE_SO_FAR}", code.rstrip())
            .replace("{NEXT_STEP}", f'    # TODO: {instr.strip()}'))

# ──────────────────────────────────────────────────────────────────────────────
# GPT ↔ execution loop
# ──────────────────────────────────────────────────────────────────────────────

def run_step(cfg: argparse.Namespace, sys_prompt: str, user_tmpl: str,
             instr: str, history: List[str], code: str, gold_board: List[int],
             image_path: Optional[Path], out_dir: Path,
             step_idx: int, run_ts: str) -> tuple[Dict, bool, str]:
    """
    Call GPT up to *retries* times until code executes; returns new script.
    For step-wise mode we append an indented  '# TODO: …'  comment so the
    first line the model writes is correctly inside the  with Game()  block.
    """
    attempt = 0
    while True:
        attempt += 1

        code_with_todo = f"{code.rstrip()}\n"
        prompt = make_user_prompt(
            instr     = instr,
            history   = history,
            template  = user_tmpl,
            code      = code_with_todo
        )

        resp = call_gpt(
            prompt        = prompt,
            system_prompt = sys_prompt,
            model         = cfg.model,
            temperature   = cfg.temperature,
            max_tokens    = cfg.max_tokens,
            seed          = cfg.seed,
            images        = [str(image_path)] if image_path else None,
        )

        append     = extract_code(resp["text"])
        new_script = f"{code.rstrip()}\n    {append}"

        if "board_state = g.board_state" not in new_script:
            new_script += "\nboard_state = g.board_state"

        log = {
            "step": step_idx,
            "attempt": attempt,
            "usage": resp["usage"],
            "code": append,
            "valid": False,
            "correct": False
        }

        ns: Dict[str, object] = {}
        try:
            exec(new_script, ns)
            pred = ns["board_state"]
            log["valid"]   = True
            log["correct"] = pred == gold_board
            plot_path = out_dir / f"{run_ts}_plot_{step_idx:02}_{attempt:02}.png"
            plot_with_gold_path = out_dir / f"{run_ts}_plot_{step_idx:02}_{attempt:02}_gold.png"
            save_plot(pred, None, plot_path)
            save_plot(pred, gold_board, plot_with_gold_path)
            return log, True, new_script, plot_path
        except Exception:
            log["traceback"] = traceback.format_exc()
            if cfg.retries and attempt >= cfg.retries:
                return log, False, code, image_path  # keep previous image


def run_full(cfg: argparse.Namespace, sys_prompt: str, user_tmpl: str,
             instructions: List[str], code_so_far: str, gold_final: List[int],
             image_path: Optional[Path], task_dir: Path,
             run_ts: str) -> Dict:
    """
    Single-shot prompt that passes ALL instructions as one indented block.
    """
    todo_block = "\n".join(
        f"    # TODO: {txt}"
        for txt in instructions
    )

    prompt = (user_tmpl
              .replace("{HISTORY_BLOCK}", "(none – full run)")
              .replace("{CODE_SO_FAR}", code_so_far.rstrip())
              .replace("{NEXT_STEP}", todo_block))

    resp = call_gpt(
        prompt        = prompt,
        system_prompt = sys_prompt,
        model         = cfg.model,
        temperature   = cfg.temperature,
        max_tokens    = cfg.max_tokens,
        seed          = cfg.seed,
        images        = [str(image_path)] if image_path else None,
    )

    append   = extract_code(resp["text"])
    new_code = f"{code_so_far.rstrip()}\n    {append}"

    if "board_state = g.board_state" not in new_code:
        new_code += "\nboard_state = g.board_state"

    log = {"attempt": 1, "code": new_code, "valid": False, "correct": False,
           "usage": resp["usage"]}

    ns = {}
    try:
        exec(new_code, ns)
        board_pred = ns["board_state"]
        log["valid"] = True
        log["correct"] = board_pred == gold_final
        save_plot(board_pred, gold_final, task_dir / f"{run_ts}_plot_full.png")
    except Exception:
        log["traceback"] = traceback.format_exc()

    return log

# ──────────────────────────────────────────────────────────────────────────────
# Main entry
# ──────────────────────────────────────────────────────────────────────────────

def main() -> None:
    cfg = parse_args()
    random.seed(cfg.seed)

    sys_prompt, user_tmpl = build_prompts()
    task          = read_task(cfg.task)
    instructions  = task["steps"]
    gold_boards   = task["gold_boards"]
    out_dir       = ensure_task_dir(cfg.task)
    run_ts        = timestamp()
    run_dir       = out_dir / run_ts

    code_so_far = (
        "from hexagen import Game, Tile, Shape, Line, Circle, Triangle\n"
        "with Game() as g:\n"
    )

    run_dir.mkdir(parents=True, exist_ok=True)

    # Image to send with the very first prompt (only used if --vision set)
    current_img: Optional[Path]
    if cfg.vision:
        current_img = DATA_DIR / "empty_board.png"  # you must have this file
    else:
        current_img = None

    history: List[str] = []
    logs:    List[Dict] = []

    if cfg.mode == "step":
        for idx, instr in enumerate(instructions, 1):
            gold_current = gold_boards[idx - 1]
            log, _, code_so_far, plot_path = run_step(
                cfg, sys_prompt, user_tmpl, instr,
                history, code_so_far, gold_current,
                current_img, run_dir, idx, run_ts)
            logs.append(log)
            history.append(instr)

            # update image for next step
            if cfg.vision and log["valid"]:
                current_img = plot_path

            print(f"[step {idx}/{len(instructions)}] "
                  f"{'✓✓' if log['correct'] else ('✓' if log['valid'] else '✗')}"
                  f" (try {log['attempt']})")
    else:
        log = run_full(
            cfg, sys_prompt, user_tmpl,
            instructions, code_so_far,
            gold_boards[-1], current_img,
            run_dir, run_ts
        )
        logs = [log]
        print("FULL RUN →",
              "✓✓" if log["correct"] else ("✓" if log["valid"] else "✗"))

    if cfg.mode == "step":
        total_steps = len(instructions)
        valid_cnt   = sum(l["valid"]   for l in logs)
        exact_cnt   = sum(l["correct"] for l in logs)
    else:
        total_steps = 1
        valid_cnt   = 1 if logs[0]["valid"]   else 0
        exact_cnt   = 1 if logs[0]["correct"] else 0

    stats = {
        "task_id"        : cfg.task,
        "mode"           : cfg.mode,
        "steps"          : total_steps,
        "total_attempts" : sum(l["attempt"] for l in logs),
        "valid"          : valid_cnt,
        "exact"          : exact_cnt,
    }

    print(f"\nFinished task {cfg.task}")
    print(f"  • valid code : {stats['valid']}/{stats['steps']}")
    print(f"  • exact match: {stats['exact']}/{stats['steps']}")

    save_json({"stats": stats, "runs": logs},
              run_dir / f"run_{timestamp()}.json")

if __name__ == "__main__":
    main()
