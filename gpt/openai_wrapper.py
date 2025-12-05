"""OpenAI chat helper with retry, vision support & consistent return shape."""

from __future__ import annotations

import base64
import mimetypes
from pathlib import Path
from typing import Any, Dict, List, Optional

from openai import OpenAI
from tenacity import retry, wait_exponential_jitter, stop_after_attempt

_client = OpenAI()


def _file_to_data_url(p: str | Path) -> str:
    """Convert a local image file to a data-URL string for vision models."""
    p = str(p)
    mime = mimetypes.guess_type(p)[0] or "image/png"
    data = Path(p).read_bytes()
    b64 = base64.b64encode(data).decode()
    return f"data:{mime};base64,{b64}"


@retry(wait=wait_exponential_jitter(1, 30), stop=stop_after_attempt(6), reraise=True)
def call_gpt(
    prompt: str,
    *,
    model: str = "gpt-4o",
    temperature: float = 0.2,
    max_tokens: int = 512,
    seed: Optional[int] = None,
    system_prompt: Optional[str] = None,
    images: Optional[List[str | Path]] = None,
) -> Dict[str, Any]:
    """Send a chat completion request.
    If *images* is supplied, they are attached to the user message."""
    # Build messages ---------------------------------------------
    messages: List[Dict[str, Any]] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})

    if images:
        # multimodal user message
        blocks = [{"type": "text", "text": prompt}] + [
            {"type": "image_url", "image_url": {"url": _file_to_data_url(img)}}
            for img in images
        ]
        messages.append({"role": "user", "content": blocks})
    else:
        messages.append({"role": "user", "content": prompt})

    # Call API ----------------------------------------------------
    # Reasoning models (o1/o3 series) don't support temperature parameter
    is_reasoning_model = any(prefix in model.lower() for prefix in ["o1", "o3"])

    api_params = {
        "model": model,
        "messages": messages,
        "seed": seed,
    }

    if not is_reasoning_model:
        api_params["temperature"] = temperature
        api_params["max_tokens"] = max_tokens

    resp = _client.chat.completions.create(**api_params)
    choice = resp.choices[0]
    return {
        "text": choice.message.content.strip(),
        "usage": resp.usage.model_dump(exclude_none=True),
        "raw": resp.model_dump(exclude_none=True),
    }
