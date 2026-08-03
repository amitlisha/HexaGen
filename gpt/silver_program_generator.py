"""Generate REGAL-style "silver programs" for Hexagons tasks: sample a model, execute, keep
whatever verifies (exact board match) — no gold-board feedback of any kind, ever.

This differs from REGAL's original recipe in one way on purpose: instead of one shot per task
(sample once with GPT, keep it if correct, discard otherwise), this script samples the model
--k times per task (1-5) and keeps EVERY verified program, not just the first. The point is to
measure two things REGAL didn't:
  1. Does trying k>1 times solve strictly more tasks than k=1 (a pass@k curve)?
  2. Does having multiple diverse correct programs per task (vs. a single one) help whatever
     downstream library-learning process consumes this data?

Two retry strategies for k>1 (both withhold the gold board and any diff — the model is only
ever told pass/fail, never *why* it failed):

  --strategy independent      Each of the k samples is drawn independently from the same blind
                               prompt at temperature > 0. Fully parallel: all k*n_tasks requests
                               go out in a single batch round. This is the cheap, simple default.

  --strategy sequential-blind Round r's prompt shows the model its own previous-round code and
                               says only "that was incorrect, try a meaningfully different
                               approach" (or, after a success, "that was correct — now try a
                               different approach for diversity"). Requires k sequential rounds
                               (each round still batches across all tasks). Costs more latency;
                               may or may not beat independent sampling — that's the open
                               question this script is meant to let you test empirically.

With k=1, both strategies are identical and reduce to the REGAL baseline: one shot, keep if
correct.

Usage:
    python -m gpt.silver_program_generator --data data/train.jsonl --output silver_programs.jsonl \
        --k 5 --strategy independent --batch
"""

from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from llm_wrapper import (
    call_llm,
    build_gemini_batch_request,
    submit_gemini_batch,
    poll_gemini_batch,
    parse_gemini_batch_results,
)
from runners.python_full_runner import extract_and_execute_python
from constants.constants import COLORS, WIDTH, HEIGHT


SYSTEM_PROMPT = """\
# Role
  - You are an expert Python programmer solving tasks for a hexagonal drawing game.

# Task
  - You will be given a full, ordered list of natural-language drawing instructions for one task.
  - Write ONE pure Python program that computes the tiles to color by implementing each
    instruction in order, step by step.

# Constraints
  - Pure Python only (loops, conditions, functions, list comprehensions, arithmetic). No drawing
    DSL or external library.
  - The board has 10 rows and 18 columns, both 1-indexed.
  - Allowed colors: ['white','black','yellow','green','red','blue','purple','orange'].

# Hex adjacency (CRITICAL — this is an offset hex grid, not a square grid)
  - Tiles are hexagons laid out in offset coordinates. The neighbor in each of the 6 hex
    directions depends on whether the CURRENT tile's column is even or odd:
      From an EVEN column: up=(row-1,col)      down=(row+1,col)
                            up_left=(row,col-1) down_left=(row+1,col-1)
                            up_right=(row,col+1) down_right=(row+1,col+1)
      From an ODD column:  up=(row-1,col)      down=(row+1,col)
                            up_left=(row-1,col-1) down_left=(row,col-1)
                            up_right=(row-1,col+1) down_right=(row,col+1)
  - Whenever an instruction implies moving to an adjacent tile in one of these 6 directions,
    you MUST use this table — recompute the parity at each step, since it can flip as you move
    across columns.

# Return format
  - Define a function `get_tiles()` that returns a list of (row, col, color) tuples.
  - Directly above the code implementing instruction N, add a comment `# Instruction N: <short paraphrase>`.
  - Reply with Python code only — no prose, no markdown code fences.
"""

DIVERSITY_NOTE_CORRECT = (
    "# Note\n"
    "  Your previous attempt (shown below) was CORRECT. For this attempt, solve the SAME task "
    "again but using a meaningfully different approach/algorithm than before — different "
    "control flow, different helper structure, a different way of deriving the same tiles. "
    "Do not just rename variables or reorder lines.\n\n"
)

DIVERSITY_NOTE_INCORRECT = (
    "# Note\n"
    "  Your previous attempt (shown below) was INCORRECT — its output did not match the "
    "required result. You are NOT told which cells were wrong. Do not just tweak constants; "
    "reconsider your interpretation of the instructions and try a meaningfully different "
    "approach this time.\n\n"
)


def load_tasks(path: Path) -> List[Dict[str, Any]]:
    tasks = []
    with path.open() as f:
        for line in f:
            line = line.strip()
            if line:
                tasks.append(json.loads(line))
    return tasks


def task_instructions(task: Dict[str, Any]) -> List[str]:
    return [step[1] for step in task["drawing_procedure"] if step[1] != "NONE"]


def task_gold_board(task: Dict[str, Any]) -> List[int]:
    return task["drawing_procedure"][-1][2]


def board_from_tiles(tiles: List[tuple]) -> List[int]:
    board = [0] * (WIDTH * HEIGHT)
    for r, c, col in tiles:
        if 1 <= r <= HEIGHT and 1 <= c <= WIDTH and col in COLORS:
            idx = (r - 1) * WIDTH + (c - 1)
            board[idx] = COLORS.index(col)
    return board


def execute_and_score(code: Optional[str], gold_board: List[int], exec_timeout: int) -> Tuple[List[int], Optional[str], bool]:
    if code is None:
        return [0] * (WIDTH * HEIGHT), "no response from model", False
    try:
        tiles = extract_and_execute_python(code, timeout=exec_timeout)
        pred_board = board_from_tiles(tiles)
        return pred_board, None, pred_board == gold_board
    except Exception as e:
        return [0] * (WIDTH * HEIGHT), str(e), False


def build_first_prompt(instructions: List[str], sample_note: str = "") -> str:
    instructions_block = "\n".join(f"{i + 1}. {txt}" for i, txt in enumerate(instructions))
    return f"# Instructions\n{instructions_block}\n{sample_note}\nWrite `get_tiles()` now."


def build_diversity_prompt(instructions: List[str], prev_code: str, prev_match: bool) -> str:
    instructions_block = "\n".join(f"{i + 1}. {txt}" for i, txt in enumerate(instructions))
    note = DIVERSITY_NOTE_CORRECT if prev_match else DIVERSITY_NOTE_INCORRECT
    return (
        f"{note}"
        f"# Instructions\n{instructions_block}\n\n"
        f"### Your previous code\n```python\n{prev_code.strip()}\n```\n\n"
        "Return your new, differently-derived full program now."
    )


def _run_prompts_batch(prompts: List[str], model: str, temperature: float, max_tokens: Optional[int]) -> List[Optional[str]]:
    """One Gemini batch job, one request per prompt. Returns generated text (or None on error)."""
    requests = [
        build_gemini_batch_request(prompt=p, system_prompt=SYSTEM_PROMPT, temperature=temperature, max_tokens=max_tokens)
        for p in prompts
    ]
    job_name = submit_gemini_batch(requests, model=model, display_name="silver-programs")
    batch_job = poll_gemini_batch(job_name)
    parsed = parse_gemini_batch_results(batch_job, requests)
    return [
        (parsed[i]["text"] if i in parsed and not parsed[i].get("error") else None)
        for i in range(len(prompts))
    ]


def _run_prompts_sync(
    prompts: List[str], model: str, temperature: float, max_tokens: Optional[int], workers: int
) -> List[Optional[str]]:
    """Live call_llm per prompt, concurrent via a thread pool. Works for any model."""
    texts: List[Optional[str]] = [None] * len(prompts)

    def _call(i: int, prompt: str) -> Tuple[int, Optional[str]]:
        try:
            resp = call_llm(prompt=prompt, system_prompt=SYSTEM_PROMPT, model=model, temperature=temperature, max_tokens=max_tokens)
            return i, resp["text"]
        except Exception:
            return i, None

    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = [ex.submit(_call, i, p) for i, p in enumerate(prompts)]
        for fut in as_completed(futures):
            i, text = fut.result()
            texts[i] = text
    return texts


def run_independent(
    tasks: List[Dict[str, Any]], model: str, k: int, temperature: float, max_tokens: Optional[int],
    exec_timeout: int, use_batch: bool, workers: int, funnel: bool = False,
    checkpoint_output: Optional[Path] = None, checkpoint_summary: Optional[Path] = None,
) -> List[Dict[str, Any]]:
    """All k*n_tasks samples drawn independently in one shot (one batch round if --batch).

    funnel and checkpoint_output/checkpoint_summary are accepted but have no effect here: all k
    samples per task fire in the same single round regardless (there's no later round to funnel
    out of, or checkpoint between). Only sequential-blind uses them.
    """
    instructions_list = [task_instructions(t) for t in tasks]
    gold_boards = [task_gold_board(t) for t in tasks]

    prompts, owners = [], []  # owners[i] = (task_idx, sample_idx)
    for ti, instr in enumerate(instructions_list):
        for si in range(k):
            note = f"\n(Independent sampling attempt {si + 1} of {k} — produce your own solution.)" if k > 1 else ""
            prompts.append(build_first_prompt(instr, sample_note=note))
            owners.append((ti, si))

    print(f"Sampling {len(prompts)} candidates ({len(tasks)} tasks x k={k}) in a single round...")
    texts = _run_prompts_batch(prompts, model, temperature, max_tokens) if use_batch else \
        _run_prompts_sync(prompts, model, temperature, max_tokens, workers)

    silver = []
    for (ti, si), text in zip(owners, texts):
        pred, err, match = execute_and_score(text, gold_boards[ti], exec_timeout)
        if match:
            silver.append(_silver_record(tasks[ti], instructions_list[ti], text, si, "independent"))
    return silver


def run_sequential_blind(
    tasks: List[Dict[str, Any]], model: str, k: int, temperature: float, max_tokens: Optional[int],
    exec_timeout: int, use_batch: bool, workers: int, funnel: bool = False,
    checkpoint_output: Optional[Path] = None, checkpoint_summary: Optional[Path] = None,
) -> List[Dict[str, Any]]:
    """k sequential rounds; each round's prompt only says pass/fail on the model's own previous
    code, never gold info.

    funnel=False (default): runs the FULL k rounds for every task regardless of success, to keep
    gathering diverse correct programs even for tasks already solved.
    funnel=True: once a task verifies, it's dropped from all later rounds — each round only
    re-samples tasks still unsolved, like a funnel narrowing down to the hard residual. Cheaper
    (fewer requests per round) but yields at most one silver program per task.

    If checkpoint_output/checkpoint_summary are given, the accumulated silver programs (and
    summary stats) are written to disk after EVERY round, not just at the end — so killing the
    process early (or just reading the file mid-run) never loses already-completed rounds, and
    the pass@1 subset (sample_idx==0) is durably available as soon as round 1 finishes, without
    waiting for the rest of k to complete.
    """
    instructions_list = [task_instructions(t) for t in tasks]
    gold_boards = [task_gold_board(t) for t in tasks]
    prev_code: List[Optional[str]] = [None] * len(tasks)
    prev_match: List[bool] = [False] * len(tasks)

    silver = []
    active = list(range(len(tasks)))
    for round_i in range(k):
        if not active:
            print(f"\n=== Round {round_i + 1}/{k}: all tasks funneled out, stopping early ===")
            break
        print(f"\n=== Round {round_i + 1}/{k}: {len(active)} task(s) ===")
        prompts = []
        for ti in active:
            instr = instructions_list[ti]
            if prev_code[ti] is None:
                prompts.append(build_first_prompt(instr))
            else:
                prompts.append(build_diversity_prompt(instr, prev_code[ti], prev_match[ti]))

        texts = _run_prompts_batch(prompts, model, temperature, max_tokens) if use_batch else \
            _run_prompts_sync(prompts, model, temperature, max_tokens, workers)

        n_match = 0
        still_active = []
        for ti, text in zip(active, texts):
            pred, err, match = execute_and_score(text, gold_boards[ti], exec_timeout)
            if match:
                n_match += 1
                silver.append(_silver_record(tasks[ti], instructions_list[ti], text, round_i, "sequential-blind"))
            prev_code[ti] = text if text is not None else prev_code[ti]
            prev_match[ti] = match
            if not (funnel and match):
                still_active.append(ti)
        print(f"  round {round_i + 1}: {n_match}/{len(active)} verified this round"
              + (f", {len(still_active)} advancing to next round" if funnel else ""))
        active = still_active

        if checkpoint_output is not None:
            with checkpoint_output.open("w") as f:
                for s in silver:
                    f.write(json.dumps(s, ensure_ascii=False) + "\n")
            if checkpoint_summary is not None:
                checkpoint_summary.write_text(json.dumps(summarize(tasks, silver), indent=2))
            print(f"  checkpoint saved: {len(silver)} silver program(s) so far -> {checkpoint_output}")

    return silver


def _silver_record(task: Dict[str, Any], instructions: List[str], program: Optional[str], sample_idx: int, strategy: str) -> Dict[str, Any]:
    return {
        "image_id": task.get("image_id"),
        "index": task.get("index"),
        "instructions": instructions,
        "program": program,
        "sample_idx": sample_idx,
        "strategy": strategy,
    }


def summarize(tasks: List[Dict[str, Any]], silver: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Includes a pass@1-vs-pass@k breakdown: sample_idx == 0 is generated by the exact same
    blind first-attempt code path a standalone k=1 run would use (for both strategies), so
    filtering to it reconstructs a k=1 run's results without having to run it separately.
    """
    by_task: Dict[Tuple[Any, Any], int] = {}
    solved_at_1: set = set()
    for s in silver:
        key = (s["image_id"], s["index"])
        by_task[key] = by_task.get(key, 0) + 1
        if s["sample_idx"] == 0:
            solved_at_1.add(key)

    n_tasks = len(tasks)
    n_solved = len(by_task)
    counts = list(by_task.values())
    n_silver_at_1 = sum(1 for s in silver if s["sample_idx"] == 0)
    return {
        "n_tasks": n_tasks,
        "pass_at_1": {
            "n_solved": len(solved_at_1),
            "solve_rate": len(solved_at_1) / n_tasks if n_tasks else 0.0,
            "n_silver_programs": n_silver_at_1,
        },
        "pass_at_k": {
            "n_solved": n_solved,
            "solve_rate": n_solved / n_tasks if n_tasks else 0.0,
            "n_silver_programs": len(silver),
        },
        "n_solved_by_retrying_beyond_try_1": n_solved - len(solved_at_1),
        "avg_verified_per_solved_task": (sum(counts) / len(counts)) if counts else 0.0,
        "max_verified_for_one_task": max(counts) if counts else 0,
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--data", type=Path, default=Path("data/train.jsonl"))
    p.add_argument("--output", type=Path, default=Path("silver_programs.jsonl"))
    p.add_argument("--summary", type=Path, default=Path("silver_programs_summary.json"))
    p.add_argument("--model", type=str, default="gemini-2.5-flash")
    p.add_argument("--k", type=int, default=5, help="Number of tries per task (1-5 recommended). k=1 == REGAL baseline.")
    p.add_argument(
        "--strategy", choices=["independent", "sequential-blind"], default="independent",
        help="independent: k parallel temperature samples, no shared context (cheap, one batch round). "
        "sequential-blind: k rounds, each told only pass/fail on its own previous code (no gold info ever).",
    )
    p.add_argument("--temperature", type=float, default=0.8, help="Use 0.0 for a deterministic k=1 REGAL-equivalent run.")
    p.add_argument("--max-tokens", type=int, default=None)
    p.add_argument("--exec-timeout", type=int, default=10)
    p.add_argument("--offset", type=int, default=0)
    p.add_argument("--limit", type=int, default=None)
    p.add_argument("--batch", action="store_true", help="Use the Gemini Batch API (Gemini/Vertex-Gemini models only).")
    p.add_argument("--workers", type=int, default=8, help="Concurrent live calls when not using --batch.")
    p.add_argument(
        "--funnel", action="store_true",
        help="(sequential-blind only) Once a task verifies, drop it from later rounds instead of "
        "continuing to sample diversity for it — each round only re-tries the still-unsolved "
        "residual, like a funnel. Cheaper, but yields at most one silver program per task. "
        "Default (off) keeps re-sampling every task for the full k rounds regardless of success.",
    )
    args = p.parse_args()

    tasks = load_tasks(args.data)
    if args.offset:
        tasks = tasks[args.offset:]
    if args.limit:
        tasks = tasks[: args.limit]

    run_fn = run_independent if args.strategy == "independent" else run_sequential_blind
    silver = run_fn(
        tasks, args.model, args.k, args.temperature, args.max_tokens, args.exec_timeout, args.batch, args.workers,
        funnel=args.funnel, checkpoint_output=args.output, checkpoint_summary=args.summary,
    )

    with args.output.open("w") as f:
        for s in silver:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")

    summary = summarize(tasks, silver)
    args.summary.write_text(json.dumps(summary, indent=2))

    print(f"\n{json.dumps(summary, indent=2)}")
    print(f"Wrote {len(silver)} silver program(s) to {args.output}")
    print(f"Wrote summary to {args.summary}")


if __name__ == "__main__":
    main()
