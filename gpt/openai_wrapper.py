"""OpenAI chat helper with retry & consistent return shape."""
from __future__ import annotations

from typing import Any, Dict, Optional

from openai import OpenAI
from tenacity import retry, wait_exponential_jitter, stop_after_attempt

_client = OpenAI()

@retry(wait=wait_exponential_jitter(1, 30), stop=stop_after_attempt(6), reraise=True)
def call_gpt(prompt: str, *, model: str = "gpt-4o", temperature: float = 0.2,
             max_tokens: int = 512, seed: Optional[int] = None,
             system_prompt: Optional[str] = None) -> Dict[str, Any]:
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    resp = _client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        seed=seed,
    )
    choice = resp.choices[0]
    return {
        "text" : choice.message.content.strip(),
        "usage": resp.usage.model_dump(exclude_none=True),
        "raw"  : resp.model_dump(exclude_none=True),
    }
