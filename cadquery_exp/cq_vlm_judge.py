"""Pairwise VLM judge, mirroring the Text2CAD GPT-4V evaluation protocol.

Text2CAD (Section 5.1.B): renders of two candidate models + the input text
prompt are given to GPT-4V, which picks whichever candidate better matches
the prompt in shape/geometry, or "Undecided" if they're indistinguishable.
Judging is comparative and text-grounded only — the ground-truth render is
never shown (per the faithfulness decision recorded for this experiment).

This module reproduces that protocol with any VLM reachable through
gpt/llm_wrapper.call_llm (local OpenAI-compatible server, Gemini, Claude,
etc.), and cancels left/right position bias by randomising which candidate
is shown as "Model 1" on each call.
"""
from __future__ import annotations

import random
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "gpt"))

from llm_wrapper import call_llm, _file_to_data_url  # noqa: E402

JUDGE_SYSTEM_PROMPT = """\
You are an expert CAD reviewer. You will be shown a natural-language design \
instruction, followed by several multi-view renders of "Model 1" and then \
several multi-view renders of "Model 2" — both are candidate 3D CAD shapes \
generated from the same instruction. Text labels mark exactly where each
model's images start and end — trust those labels; do not recount or
re-verify the image grouping yourself.

Judge ONLY whether each model's overall shape and geometry match the \
instruction. Ignore color, rendering style, and exact numeric dimensions — \
focus on shape, topology, and proportions.

Respond with exactly one line in this format, nothing else:
VERDICT: <MODEL_1 | MODEL_2 | UNDECIDED>
"""

_FINAL_REMINDER = (
    "You have now seen all of Model 1's views followed by all of Model 2's "
    "views, as labelled above. Based on shape and geometry alone, respond "
    "with exactly one line:\nVERDICT: <MODEL_1 | MODEL_2 | UNDECIDED>"
)

_VERDICT_RE = re.compile(r"VERDICT:\s*(MODEL_1|MODEL_2|UNDECIDED)", re.IGNORECASE)


def _img_block(path: Path) -> Dict:
    return {"type": "image_url", "image_url": {"url": _file_to_data_url(path)}}


def _build_interleaved_messages(
    instruction: str, images_first: List[Path], images_second: List[Path]
) -> List[Dict]:
    """One user turn with explicit text labels marking where each model's
    image block starts/ends — unlike a flat image list, this removes any
    need for the judge to infer grouping from image order alone, which was
    observed to send a reasoning-heavy local model into unproductive
    recounting loops even when it had already correctly read the shapes.
    """
    content: List[Dict] = [{
        "type": "text",
        "text": f"Design instruction:\n{instruction.strip()}\n\n"
                f"Model 1's views ({len(images_first)} images) below:",
    }]
    content += [_img_block(p) for p in images_first]
    content.append({
        "type": "text",
        "text": f"--- End of Model 1's images. "
                f"Model 2's views ({len(images_second)} images) below: ---",
    })
    content += [_img_block(p) for p in images_second]
    content.append({"type": "text", "text": "--- End of Model 2's images. ---"})
    return [{"role": "user", "content": content}]


def _parse_verdict(text: str) -> str:
    m = _VERDICT_RE.search(text or "")
    return m.group(1).upper() if m else "UNDECIDED"


def pairwise_judge(
    instruction: str,
    images_a: List[Path],
    images_b: List[Path],
    model: str,
    *,
    temperature: float = 0.0,
    max_tokens: int = 8192,
    rng: Optional[random.Random] = None,
) -> Dict:
    """Judge candidate A vs. candidate B for one (instruction, level) task.

    Randomises which candidate is shown as "Model 1" to cancel position
    bias, then maps the raw verdict back to {"a", "b", "undecided"}.

    The VLM backend (local server, Gemini, Claude, ...) is selected the same
    way as everywhere else in this repo: via `--model`/`--base-url`/`--api-key`
    passed to `init_llm(cfg)` once at process start, not per call.

    Returns a dict: {"winner": "a"|"b"|"undecided", "raw_verdict": str,
    "swapped": bool, "response_text": str}.
    """
    rng = rng or random
    swapped = rng.random() < 0.5

    first_images, second_images = (
        (images_b, images_a) if swapped else (images_a, images_b)
    )
    messages = _build_interleaved_messages(instruction, first_images, second_images)

    resp = call_llm(
        _FINAL_REMINDER,
        model=model,
        system_prompt=JUDGE_SYSTEM_PROMPT,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )

    raw = _parse_verdict(resp.get("text", ""))
    if raw == "UNDECIDED":
        winner = "undecided"
    elif raw == "MODEL_1":
        winner = "b" if swapped else "a"
    else:  # MODEL_2
        winner = "a" if swapped else "b"

    return {
        "winner": winner,
        "raw_verdict": raw,
        "swapped": swapped,
        "response_text": resp.get("text", ""),
    }
