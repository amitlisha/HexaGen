"""Batch API orchestrator for HexaGen experiment runner.

Submits all first-attempt prompts as a single batch job (50% cost savings),
then evaluates results. Failed tasks are collected and retried in subsequent
batch rounds (up to cfg.retries total rounds).

Supports OpenAI and Gemini models with full-mode runners:
  - tiles-full  (fully batchable: no retries)
  - code-full   (all attempts batched across rounds)
  - python-full (all attempts batched across rounds)
"""

from __future__ import annotations

import argparse
import json
import textwrap
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from llm_wrapper import (
    _is_gemini_model,
    build_openai_messages,
    build_openai_request_body,
    submit_openai_batch,
    poll_openai_batch,
    parse_batch_results,
    build_gemini_batch_request,
    submit_gemini_batch,
    poll_gemini_batch,
    parse_gemini_batch_results,
)
from runner_utils import generate_import_statement, extract_code, DATA_DIR
from prompts import build_prompts
from datasets import get_dataset

_BATCHABLE_MODES = {"tiles-full", "code-full", "python-full"}


def _parse_local_batch_file(filepath: str) -> Dict[str, Dict[str, Any]]:
    """Parse a local merged JSONL file (same format as OpenAI batch output).

    Returns {custom_id: {"text": str, "usage": dict, "raw": dict, "error": str|None}}.
    """
    from llm_wrapper import _strip_thinking_tokens

    results: Dict[str, Dict[str, Any]] = {}
    for line in Path(filepath).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        item = json.loads(line)
        cid = item["custom_id"]
        if item.get("error"):
            results[cid] = {
                "text": None,
                "usage": {},
                "raw": {},
                "error": str(item["error"]),
            }
            continue
        resp_body = item["response"]["body"]
        choice = resp_body["choices"][0]
        text = choice["message"]["content"].strip()
        text = _strip_thinking_tokens(text)
        results[cid] = {
            "text": text,
            "usage": resp_body.get("usage", {}),
            "raw": resp_body,
            "error": None,
        }
    return results


def is_batch_compatible(cfg: argparse.Namespace) -> bool:
    """Return True if batch mode is valid for this configuration."""
    if cfg.mode not in _BATCHABLE_MODES:
        return False
    # Batch API not available with custom base_url (local models)
    if getattr(cfg, "base_url", None):
        return False
    return True


def _max_batch_rounds(cfg: argparse.Namespace) -> int:
    """Determine how many batch rounds to run.

    tiles-full has no retry logic, so always 1 round.
    For other modes: min(cfg.retries, 3), capped at 3 for unlimited (0).
    """
    if cfg.mode == "tiles-full":
        return 1
    retries = cfg.retries
    if not retries:  # 0 = unlimited -> cap at 3
        return 3
    return min(retries, 3)


def _build_retry_prompt(
    cfg: argparse.Namespace,
    base_prompt: str,
    last_code: str,
    last_error: str,
) -> str:
    """Append error feedback to the base prompt, mirroring runner formatting."""
    if cfg.mode == "code-full":
        # code-full: 3-space indented headers (matches full_runner.py)
        return base_prompt + (
            "\n\n"
            "   ### Your previous code\n"
            "   ```python\n"
            f"{textwrap.indent(last_code.strip(), '    ')}\n"
            "   ```\n\n"
            "   ### Previous execution error\n"
            f"{textwrap.indent(last_error.strip(), '    ')}\n\n"
            "   ### Fix instructions\n"
            "   Analyze the error in your previous code and fix it. Do NOT repeat the same mistake.\n"
        )
    else:
        # python-full: no header indent
        return base_prompt + (
            "\n\n"
            "### Your previous code\n"
            "```python\n"
            f"{last_code.strip()}\n"
            "```\n\n"
            "### Previous execution error\n"
            f"{textwrap.indent(last_error.strip(), '    ')}\n\n"
            "### Fix instructions\n"
            "    Analyze the error in your previous code and fix it. Do NOT repeat the same mistake.\n"
        )


def _extract_last_code(cfg: argparse.Namespace, raw_llm_text: str) -> str:
    """Extract the code to include in retry prompts as 'Your previous code'.

    For code-full Hexagen, the retry prompt uses extract_code() (just the body).
    For all other modes, the raw LLM response text is used directly.
    """
    if cfg.mode == "code-full":
        return extract_code(raw_llm_text)
    return raw_llm_text


def _collect_failures(
    eval_items: List[Tuple[int, Any, Dict, Optional[Dict]]],
    payloads: Dict[int, Dict],
    batch_texts: Dict[int, str],
) -> List[Tuple[int, Any, Dict, Optional[str], Optional[str]]]:
    """Identify failed tasks from evaluation results.

    Returns list of (list_idx, task_id, task_data, raw_llm_text, error_msg).
    raw_llm_text and error_msg may be None for tasks that had batch-level errors
    (these will be resubmitted with first-attempt prompts in the next round).
    """
    failures = []
    for list_idx, task_id, task_data, prefetched in eval_items:
        payload = payloads.get(list_idx)
        if payload is None:
            continue
        runs = payload.get("runs", [])
        if not runs:
            continue
        log = runs[0]  # full modes have exactly one log entry
        if log.get("valid", False):
            continue
        # Task failed
        raw_text = batch_texts.get(list_idx)
        error_msg = log.get("error") or log.get("traceback") or "Unknown error"
        failures.append((list_idx, task_id, task_data, raw_text, error_msg))
    return failures


# ──────────────────────────────────────────────────────────────────────────────
# Public entry point
# ──────────────────────────────────────────────────────────────────────────────


def run_set_batch(
    cfg: argparse.Namespace,
    tasks_to_run: List[Tuple[int, Any, Dict]],
) -> Dict[int, Dict]:
    """Submit all tasks as a single batch, poll for completion,
    then evaluate each result via run_task with prefetched responses.
    Failed tasks are retried in subsequent batch rounds.

    Args:
        cfg: Config namespace (mode must be in _BATCHABLE_MODES)
        tasks_to_run: List of (list_idx, task_id, task_data) tuples

    Returns:
        Dict mapping list_idx -> run payload (same format as run_task())
    """
    is_gemini = _is_gemini_model(cfg.model)

    if is_gemini:
        return _run_set_batch_gemini(cfg, tasks_to_run)
    else:
        return _run_set_batch_openai(cfg, tasks_to_run)


# ──────────────────────────────────────────────────────────────────────────────
# OpenAI Batch API
# ──────────────────────────────────────────────────────────────────────────────


def _run_set_batch_openai(
    cfg: argparse.Namespace,
    tasks_to_run: List[Tuple[int, Any, Dict]],
) -> Dict[int, Dict]:
    """OpenAI Batch API path with multi-round retries."""
    dataset = get_dataset()
    sys_prompt, user_tmpl = build_prompts(
        cfg.mode, cfg.vision, cfg.api_spec_file
    )

    batch_resume_id = getattr(cfg, "batch_resume", None)
    batch_resume_file = getattr(cfg, "batch_resume_file", None)
    poll_interval = getattr(cfg, "batch_poll_interval", 60)
    batch_timeout = getattr(cfg, "batch_timeout", 86400)

    max_rounds = _max_batch_rounds(cfg)
    final_payloads: Dict[int, Dict] = {}

    # Current round's tasks: list of (list_idx, task_id, task_data)
    current_tasks = list(tasks_to_run)
    # Retry info from previous round: list_idx -> (raw_llm_text, error_msg)
    retry_info: Dict[int, Tuple[str, str]] = {}

    for round_num in range(1, max_rounds + 1):
        if not current_tasks:
            break

        print(f"\n[batch] ═══ Round {round_num}/{max_rounds} — "
              f"{len(current_tasks)} tasks ═══")

        # ── 1. Build per-task prompts and JSONL request lines ─────────
        task_info: Dict[str, Tuple[int, Any, Dict]] = {}
        jsonl_lines: List[str] = []

        for list_idx, task_id, task_data in current_tasks:
            custom_id = f"task_{task_id}"
            task_info[custom_id] = (list_idx, task_id, task_data)

            instructions = dataset.get_instructions(task_data)
            input_grid_2d = task_data.get("test_input")

            # Build base prompt
            base_prompt = _build_first_prompt(
                cfg, user_tmpl, instructions, input_grid_2d
            )

            # Append error feedback for retry rounds (if we have a previous response)
            if list_idx in retry_info:
                raw_text, error_msg = retry_info[list_idx]
                if raw_text and error_msg:
                    last_code = _extract_last_code(cfg, raw_text)
                    prompt = _build_retry_prompt(cfg, base_prompt, last_code, error_msg)
                else:
                    prompt = base_prompt  # batch error — resubmit first prompt
            else:
                prompt = base_prompt

            # Build image path for vision mode
            image_path = DATA_DIR / "empty_board.png" if cfg.vision else None

            messages = build_openai_messages(
                prompt=prompt,
                system_prompt=sys_prompt,
                images=[str(image_path)] if image_path else None,
            )
            body = build_openai_request_body(
                messages=messages,
                model=cfg.model,
                temperature=cfg.temperature,
                max_tokens=cfg.max_tokens,
                seed=cfg.seed,
                reasoning_effort=getattr(cfg, "reasoning_effort", None),
            )

            jsonl_lines.append(json.dumps({
                "custom_id": custom_id,
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": body,
            }))

        # ── 2. Get batch results ─────────────────────────────────────
        batch_results: Dict[str, Dict[str, Any]] = {}
        error_results: Dict[str, Dict[str, Any]] = {}

        if round_num == 1 and batch_resume_file:
            # Load pre-merged results from local JSONL file
            print(f"[batch] Loading results from {batch_resume_file}...")
            batch_results = _parse_local_batch_file(batch_resume_file)
            print(f"[batch] Loaded {len(batch_results)} results from file")

        elif round_num == 1 and batch_resume_id:
            print(f"[batch] Resuming existing batch: {batch_resume_id}")
            batch_obj = poll_openai_batch(
                batch_resume_id, poll_interval, batch_timeout
            )
            if batch_obj.status != "completed":
                print(
                    f"[batch] WARNING: Batch ended with status={batch_obj.status}. "
                    f"Partial results may be available."
                )
            if batch_obj.output_file_id:
                print(f"[batch] Downloading results...")
                batch_results = parse_batch_results(batch_obj.output_file_id)
            if batch_obj.error_file_id:
                error_results = parse_batch_results(batch_obj.error_file_id)

        else:
            print(f"[batch] Submitting {len(jsonl_lines)} requests to OpenAI Batch API...")
            batch_id = submit_openai_batch(jsonl_lines)
            print(f"[batch] Created batch: {batch_id}")
            if round_num == 1:
                print(f"[batch] To resume polling later, re-run with: --batch-resume {batch_id}")
            batch_obj = poll_openai_batch(batch_id, poll_interval, batch_timeout)

            if batch_obj.status != "completed":
                print(
                    f"[batch] WARNING: Batch ended with status={batch_obj.status}. "
                    f"Partial results may be available."
                )
            if batch_obj.output_file_id:
                print(f"[batch] Downloading results...")
                batch_results = parse_batch_results(batch_obj.output_file_id)
            if batch_obj.error_file_id:
                error_results = parse_batch_results(batch_obj.error_file_id)

        print(
            f"[batch] Got {len(batch_results)} results, "
            f"{len(error_results)} errors"
        )

        # ── 4. Build eval_items and track raw texts ───────────────────
        eval_items: List[Tuple[int, Any, Dict, Optional[Dict]]] = []
        batch_texts: Dict[int, str] = {}  # list_idx -> raw LLM text

        for custom_id, (list_idx, task_id, task_data) in task_info.items():
            result = batch_results.get(custom_id) or error_results.get(custom_id)

            if result is None or result.get("error"):
                err_msg = (result or {}).get("error", "missing from batch output")
                print(f"[batch] Task {task_id} batch error: {err_msg}")
                prefetched = None
            else:
                prefetched = {
                    "text": result["text"],
                    "usage": result["usage"],
                    "raw": result["raw"],
                }
                batch_texts[list_idx] = result["text"]

            eval_items.append((list_idx, task_id, task_data, prefetched))

        # ── 5. Evaluate with retries=1 (no sync retries) ─────────────
        original_retries = cfg.retries
        cfg.retries = 1
        try:
            round_payloads = _evaluate_parallel(cfg, dataset, eval_items)
        finally:
            cfg.retries = original_retries

        # ── 6. Separate successes from failures ──────────────────────
        is_last_round = round_num >= max_rounds
        failures = [] if is_last_round else _collect_failures(
            eval_items, round_payloads, batch_texts
        )
        failed_idxs = {f[0] for f in failures}

        # Store all results: successes go to final, failures get retried
        for list_idx, task_id, task_data, _ in eval_items:
            payload = round_payloads.get(list_idx)
            if payload is None:
                continue
            if list_idx not in failed_idxs or is_last_round:
                final_payloads[list_idx] = payload

        n_success = len(eval_items) - len(failures)
        print(
            f"[batch] Round {round_num} complete: "
            f"{n_success} succeeded, {len(failures)} failed"
        )

        if not failures:
            break

        # ── 7. Prepare next round ────────────────────────────────────
        retry_info = {}
        current_tasks = []
        for list_idx, task_id, task_data, raw_text, error_msg in failures:
            retry_info[list_idx] = (raw_text, error_msg)
            current_tasks.append((list_idx, task_id, task_data))

    return final_payloads


# ──────────────────────────────────────────────────────────────────────────────
# Gemini Batch API
# ──────────────────────────────────────────────────────────────────────────────


def _run_set_batch_gemini(
    cfg: argparse.Namespace,
    tasks_to_run: List[Tuple[int, Any, Dict]],
) -> Dict[int, Dict]:
    """Gemini Batch API path with multi-round retries."""
    dataset = get_dataset()
    sys_prompt, user_tmpl = build_prompts(
        cfg.mode, cfg.vision, cfg.api_spec_file
    )

    batch_resume_id = getattr(cfg, "batch_resume", None)
    poll_interval = getattr(cfg, "batch_poll_interval", 30)
    batch_timeout = getattr(cfg, "batch_timeout", 86400)

    max_rounds = _max_batch_rounds(cfg)
    final_payloads: Dict[int, Dict] = {}

    # Current round's tasks: list of (list_idx, task_id, task_data)
    current_tasks = list(tasks_to_run)
    # Retry info from previous round: list_idx -> (raw_llm_text, error_msg)
    retry_info: Dict[int, Tuple[str, str]] = {}

    for round_num in range(1, max_rounds + 1):
        if not current_tasks:
            break

        print(f"\n[batch] ═══ Round {round_num}/{max_rounds} — "
              f"{len(current_tasks)} tasks ═══")

        # ── 1. Build per-task inline requests ─────────────────────────
        # Ordered list for index-based matching with Gemini inline responses
        task_order: List[Tuple[int, Any, Dict]] = []
        gemini_requests: List[Dict[str, Any]] = []

        for list_idx, task_id, task_data in current_tasks:
            task_order.append((list_idx, task_id, task_data))

            instructions = dataset.get_instructions(task_data)
            input_grid_2d = task_data.get("test_input")

            # Build base prompt
            base_prompt = _build_first_prompt(
                cfg, user_tmpl, instructions, input_grid_2d
            )

            # Append error feedback for retry rounds (if we have a previous response)
            if list_idx in retry_info:
                raw_text, error_msg = retry_info[list_idx]
                if raw_text and error_msg:
                    last_code = _extract_last_code(cfg, raw_text)
                    prompt = _build_retry_prompt(cfg, base_prompt, last_code, error_msg)
                else:
                    prompt = base_prompt  # batch error — resubmit first prompt
            else:
                prompt = base_prompt

            # Build image path for vision mode
            image_path = DATA_DIR / "empty_board.png" if cfg.vision else None

            request = build_gemini_batch_request(
                prompt=prompt,
                system_prompt=sys_prompt,
                images=[str(image_path)] if image_path else None,
                temperature=cfg.temperature,
                max_tokens=cfg.max_tokens,
                thinking_budget=getattr(cfg, "thinking_budget", None),
                thinking_level=getattr(cfg, "thinking_level", None),
            )
            gemini_requests.append(request)

        # ── 2. Submit batch (round 1 supports --batch-resume) ────────
        if round_num == 1 and batch_resume_id:
            print(f"[batch] Resuming existing Gemini batch: {batch_resume_id}")
            batch_job = poll_gemini_batch(
                batch_resume_id, poll_interval, batch_timeout
            )
        else:
            experiment_name = getattr(cfg, "experiment_name", "hexagen")
            display_name = f"{experiment_name}-{cfg.mode}-{cfg.model}-r{round_num}"
            print(f"[batch] Submitting {len(gemini_requests)} requests to Gemini Batch API...")
            job_name = submit_gemini_batch(gemini_requests, cfg.model, display_name)
            print(f"[batch] Created Gemini batch: {job_name}")
            if round_num == 1:
                print(f"[batch] To resume polling later, re-run with: --batch-resume {job_name}")
            batch_job = poll_gemini_batch(job_name, poll_interval, batch_timeout)

        state = batch_job.state.name if hasattr(batch_job.state, "name") else str(batch_job.state)
        if state != "JOB_STATE_SUCCEEDED":
            print(
                f"[batch] WARNING: Gemini batch ended with state={state}. "
                f"Partial results may be available."
            )

        # ── 3. Parse inline results ───────────────────────────────────
        print(f"[batch] Parsing Gemini batch results...")
        batch_results = parse_gemini_batch_results(batch_job, gemini_requests)
        num_errors = sum(1 for r in batch_results.values() if r.get("error"))
        print(
            f"[batch] Got {len(batch_results)} results, "
            f"{num_errors} errors"
        )

        # ── 4. Build eval_items and track raw texts ───────────────────
        eval_items: List[Tuple[int, Any, Dict, Optional[Dict]]] = []
        batch_texts: Dict[int, str] = {}  # list_idx -> raw LLM text

        for i, (list_idx, task_id, task_data) in enumerate(task_order):
            result = batch_results.get(i)

            if result is None or result.get("error"):
                err_msg = (result or {}).get("error", "missing from batch output")
                print(f"[batch] Task {task_id} batch error: {err_msg}")
                prefetched = None
            else:
                prefetched = {
                    "text": result["text"],
                    "usage": result["usage"],
                    "raw": result["raw"],
                }
                batch_texts[list_idx] = result["text"]

            eval_items.append((list_idx, task_id, task_data, prefetched))

        # ── 5. Evaluate with retries=1 (no sync retries) ─────────────
        original_retries = cfg.retries
        cfg.retries = 1
        try:
            round_payloads = _evaluate_parallel(cfg, dataset, eval_items)
        finally:
            cfg.retries = original_retries

        # ── 6. Separate successes from failures ──────────────────────
        is_last_round = round_num >= max_rounds
        failures = [] if is_last_round else _collect_failures(
            eval_items, round_payloads, batch_texts
        )
        failed_idxs = {f[0] for f in failures}

        # Store all results: successes go to final, failures get retried
        for list_idx, task_id, task_data, _ in eval_items:
            payload = round_payloads.get(list_idx)
            if payload is None:
                continue
            if list_idx not in failed_idxs or is_last_round:
                final_payloads[list_idx] = payload

        n_success = len(eval_items) - len(failures)
        print(
            f"[batch] Round {round_num} complete: "
            f"{n_success} succeeded, {len(failures)} failed"
        )

        if not failures:
            break

        # ── 7. Prepare next round ────────────────────────────────────
        retry_info = {}
        current_tasks = []
        for list_idx, task_id, task_data, raw_text, error_msg in failures:
            retry_info[list_idx] = (raw_text, error_msg)
            current_tasks.append((list_idx, task_id, task_data))

    return final_payloads


# ──────────────────────────────────────────────────────────────────────────────
# Shared evaluation helpers
# ──────────────────────────────────────────────────────────────────────────────


def _evaluate_parallel(
    cfg: argparse.Namespace,
    dataset: Any,
    eval_items: List[Tuple[int, Any, Dict, Optional[Dict]]],
) -> Dict[int, Dict]:
    """Evaluate batch results, using workers for parallelism when available."""
    workers = getattr(cfg, "workers", 1) or 1
    payloads: Dict[int, Dict] = {}

    if workers <= 1:
        for list_idx, task_id, task_data, prefetched in eval_items:
            payloads[list_idx] = _run_task_safe(cfg, dataset, task_id, task_data, prefetched)
    else:
        from concurrent.futures import ThreadPoolExecutor, as_completed

        print(f"[batch] Evaluating {len(eval_items)} tasks with {workers} workers...")
        with ThreadPoolExecutor(max_workers=workers) as ex:
            futures = {
                ex.submit(_run_task_safe, cfg, dataset, task_id, task_data, prefetched): list_idx
                for list_idx, task_id, task_data, prefetched in eval_items
            }
            for fut in as_completed(futures):
                list_idx = futures[fut]
                payloads[list_idx] = fut.result()

    return payloads


def _run_task_safe(
    cfg: argparse.Namespace,
    dataset: Any,
    task_id: Any,
    task_data: Dict,
    prefetched: Optional[Dict],
) -> Dict:
    """Run a single task with error handling."""
    from experiment import run_task, _gold_failed_runs

    try:
        return run_task(cfg, task_id, task_data, prefetched_response=prefetched)
    except Exception as exc:
        print(f"Task {task_id} failed: {exc}")
        try:
            gold_boards = dataset.get_gold_boards(task_data)
            failed_runs = _gold_failed_runs(
                {"gold_boards": gold_boards}, cfg.mode
            )
        except Exception:
            failed_runs = []
        return {
            "stats": {
                "task_id": task_id,
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
            "runs": failed_runs,
            "run_dir": None,
            "run_log_path": None,
        }


def _build_first_prompt(
    cfg: argparse.Namespace,
    user_tmpl: str,
    instructions: List[str],
    input_grid_2d: Optional[List[List[int]]],
) -> str:
    """Dispatch to the per-mode prompt builder."""
    if cfg.mode == "tiles-full":
        from runners.tiles_full_runner import build_tiles_full_prompt

        return build_tiles_full_prompt(cfg, user_tmpl, instructions, input_grid_2d)
    elif cfg.mode == "code-full":
        from runners.full_runner import build_code_full_prompt

        code_so_far = (
            f"{generate_import_statement(cfg.lib_file)}\n"
            "from constants import HEIGHT, WIDTH, COLORS, DIRECTIONS\n"
            "with Game() as g:\n"
        )
        return build_code_full_prompt(
            cfg, user_tmpl, instructions, code_so_far, input_grid_2d
        )
    elif cfg.mode == "python-full":
        from runners.python_full_runner import build_python_full_prompt

        return build_python_full_prompt(cfg, user_tmpl, instructions, input_grid_2d)
    else:
        raise ValueError(f"Mode {cfg.mode!r} is not batchable")
