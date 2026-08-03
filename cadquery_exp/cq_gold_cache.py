"""Persistent, uid-keyed cache for gold CadQuery BREP execution.

Gold code depends only on `uid` — never on level, condition, or model — so
there is no reason to re-execute it once per task or once per experiment
run. Re-executing it redundantly multiplies exposure to a flaky ~30s
subprocess timeout on a shared/contended machine, which produces different
"gold failed" denominators across two runs of the *identical* gold program.
That's exactly the mismatch found comparing two Gemini pilot runs over the
same 120 examples (98 vs. 105 scored) — 7 uids timed out in one run's gold
execution but not the other's, purely due to machine load at call time.

This module makes gold execution a one-time, durable fact: once a uid's
gold program is confirmed to execute, its normalised BREP is cached to disk
and reused by any future run over the same dataset. Failures are NOT
cached — a timeout is not proof a program is unrunnable — so a later call
gets a fresh attempt (with retries) rather than being permanently poisoned
by one bad race.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional, Tuple

from cq_executor import execute_cq

CACHE_DIR = Path(__file__).resolve().parent.parent / "data" / "gold_brep_cache"
KNOWN_BAD_PATH = CACHE_DIR.parent / "gold_known_bad.json"


def _cache_path(uid: str) -> Path:
    return CACHE_DIR / f"{uid.replace('/', '_')}.brep"


def seed_gold_cache(uid: str, brep: str) -> None:
    """Manually seed the cache for a uid with an already-known-good BREP."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    _cache_path(uid).write_text(brep, encoding="utf-8")


def _load_known_bad() -> Dict[str, str]:
    if not KNOWN_BAD_PATH.exists():
        return {}
    return json.loads(KNOWN_BAD_PATH.read_text())


def mark_known_bad(uid: str, error: str) -> None:
    """Persist a uid as permanently gold-failing, skipping execution entirely
    on all future calls (any model, any run) instead of re-attempting and
    waiting out retries/timeouts on a program already proven unrunnable.

    Only call this once a failure has been independently reproduced (e.g.
    identical across two separate runs) — a single failure is not enough
    evidence, since get_gold_brep's own TIMEOUT retries exist precisely
    because one bad race isn't proof a program can't run.
    """
    bad = _load_known_bad()
    bad[uid] = error
    KNOWN_BAD_PATH.write_text(json.dumps(bad, indent=2))


def get_gold_brep(
    uid: str,
    gold_code: str,
    timeout: int = 30,
    retries: int = 2,
) -> Tuple[Optional[str], Optional[str]]:
    """Return (brep_str, None) or (None, error) for a uid's gold program.

    Checks the known-permanently-bad list first (instant, no subprocess
    spawned), then the on-disk success cache. On a genuine cache miss,
    executes gold_code, retrying up to `retries` extra times specifically
    on TIMEOUT (transient contention) before giving up — non-timeout errors
    (syntax, etc.) are real and won't fix themselves on retry, so those fail
    immediately. Successful results are cached permanently.
    """
    known_bad = _load_known_bad()
    if uid in known_bad:
        return None, known_bad[uid]

    path = _cache_path(uid)
    if path.exists():
        return path.read_text(encoding="utf-8"), None

    last_err: Optional[str] = None
    for _attempt in range(1 + retries):
        brep, err = execute_cq(gold_code, timeout=timeout)
        if err is None:
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
            path.write_text(brep, encoding="utf-8")
            return brep, None
        last_err = err
        if err != "TIMEOUT":
            break
    return None, last_err
