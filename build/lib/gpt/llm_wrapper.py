"""Generic LLM wrapper with support for OpenAI and Gemini models."""

from __future__ import annotations

import base64
import mimetypes
import re
from pathlib import Path
from typing import Any, Dict, List, Optional
import os
import argparse

from tenacity import retry, wait_exponential_jitter, stop_after_attempt

os.environ["GRPC_DNS_RESOLVER"] = "native"

# Global clients/state for persistence
_OPENAI_CLIENT: Optional[Any] = None
_GENAI_CLIENT: Optional[Any] = None
_ANTHROPIC_CLIENT: Optional[Any] = None


def _get_or_create_genai_client(api_key: Optional[str] = None) -> Any:
    """Get or create a google-genai Client, caching it globally.

    Supports both API key auth (GOOGLE_API_KEY / GEMINI_API_KEY) and
    Vertex AI auth (GCP_PROJECT_ID / VERTEX_PROJECT_ID).
    """
    global _GENAI_CLIENT
    if _GENAI_CLIENT is not None:
        return _GENAI_CLIENT

    from google import genai

    project_id = os.environ.get("GCP_PROJECT_ID") or os.environ.get("VERTEX_PROJECT_ID")
    if project_id:
        location = os.environ.get("VERTEX_LOCATION", "global")
        _GENAI_CLIENT = genai.Client(
            vertexai=True, project=project_id, location=location
        )
    else:
        api_key = (
            api_key
            or os.environ.get("GOOGLE_API_KEY")
            or os.environ.get("GEMINI_API_KEY")
        )
        if not api_key:
            raise ValueError(
                "Either GCP_PROJECT_ID/VERTEX_PROJECT_ID or GOOGLE_API_KEY/GEMINI_API_KEY "
                "environment variable must be set for Gemini"
            )
        _GENAI_CLIENT = genai.Client(api_key=api_key)

    return _GENAI_CLIENT


def init_llm(cfg: argparse.Namespace) -> None:
    """Initialize LLM clients based on configuration."""
    global _OPENAI_CLIENT, _GENAI_CLIENT, _ANTHROPIC_CLIENT

    # Claude Code (agentic, via Claude Agent SDK)
    if _is_claude_code_model(cfg.model):
        try:
            import claude_agent_sdk  # noqa: F401
        except ImportError as e:
            raise RuntimeError(
                "Claude Code requires `claude-agent-sdk`. "
                "Install with: pip install claude-agent-sdk"
            ) from e
        if not os.environ.get("ANTHROPIC_API_KEY"):
            print(
                "[init_llm] ANTHROPIC_API_KEY not set; SDK will use existing "
                "`claude login` credentials if available."
            )
        return

    # Anthropic Messages API (non-agentic)
    if _is_anthropic_model(cfg.model):
        from anthropic import Anthropic

        kwargs: Dict[str, Any] = {}
        if getattr(cfg, "api_key", None):
            kwargs["api_key"] = cfg.api_key
        _ANTHROPIC_CLIENT = Anthropic(**kwargs)
        return

    # Gemini / Vertex AI
    if _is_gemini_model(cfg.model):
        api_key = getattr(cfg, "api_key", None)
        _get_or_create_genai_client(api_key=api_key)
    else:
        # OpenAI / Local OpenAI-compatible
        from openai import OpenAI

        client_kwargs = {}
        if hasattr(cfg, "base_url") and cfg.base_url:
            client_kwargs["base_url"] = cfg.base_url
        if hasattr(cfg, "api_key") and cfg.api_key:
            client_kwargs["api_key"] = cfg.api_key
        elif hasattr(cfg, "base_url") and cfg.base_url:
            client_kwargs["api_key"] = "EMPTY"

        _OPENAI_CLIENT = OpenAI(**client_kwargs)


def _file_to_data_url(p: str | Path) -> str:
    """Convert a local image file to a data-URL string for vision models."""
    p = str(p)
    mime = mimetypes.guess_type(p)[0] or "image/png"
    data = Path(p).read_bytes()
    b64 = base64.b64encode(data).decode()
    return f"data:{mime};base64,{b64}"


def _file_to_bytes(p: str | Path) -> bytes:
    """Read file as bytes for Gemini."""
    return Path(p).read_bytes()


def _strip_thinking_tokens(text: str) -> str:
    """Strip <think>...</think> blocks from model output (e.g. Qwen3 thinking).

    Handles three cases:
    1. Complete <think>...</think> blocks
    2. Missing opening <think> (vLLM may consume it as a special token) -
       strips everything up to and including </think>
    """
    # Strip complete <think>...</think> blocks
    text = re.sub(r"<think>.*?</think>\s*", "", text, flags=re.DOTALL)
    # Handle missing opening <think> tag
    text = re.sub(r"^.*?</think>\s*", "", text, flags=re.DOTALL)
    return text.strip()


def _is_gemini_model(model: str) -> bool:
    """Check if model is a Gemini model."""
    return "gemini" in model.lower()


def _is_claude_code_model(model: str) -> bool:
    """Check if model should be routed through the Claude Agent SDK (agentic)."""
    m = model.lower()
    return m.startswith("claude-code/") or m == "claude-code"


def _strip_claude_code_prefix(model: str) -> str:
    """Return the underlying Anthropic model name from a 'claude-code/<model>' string."""
    suffix = model.split("/", 1)[1] if "/" in model else ""
    return suffix or os.environ.get("CLAUDE_CODE_MODEL", "claude-opus-4-7")


def _is_anthropic_model(model: str) -> bool:
    """Direct Anthropic Messages API: claude-* names except the agentic claude-code/* prefix."""
    return model.lower().startswith("claude-") and not _is_claude_code_model(model)


def _is_openai_reasoning_model(model: str) -> bool:
    """Check if model is an OpenAI reasoning model (o1/o3 series)."""
    return any(
        prefix in model.lower()
        for prefix in ["o1", "o3", "gpt-5.1", "gpt-5.2", "gpt-5.4"]
    )


# Default request timeout in seconds for API calls (prevents indefinite hangs)
_REQUEST_TIMEOUT: int = 300


def _call_with_timeout(fn, args, kwargs, timeout):
    """Call fn(*args, **kwargs) with a timeout to prevent indefinite hangs.

    Uses a separate thread so it works even inside ThreadPoolExecutor workers
    (unlike signal.alarm which only works on the main thread).

    IMPORTANT: We must NOT use `with ThreadPoolExecutor` because its __exit__
    calls shutdown(wait=True), which blocks forever if the inner thread is hung
    on a socket read.  Instead we manage the executor manually and always use
    shutdown(wait=False) so the caller is never blocked.
    """
    from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout

    ex = ThreadPoolExecutor(max_workers=1)
    future = ex.submit(fn, *args, **kwargs)
    try:
        result = future.result(timeout=timeout)
    except FuturesTimeout:
        # Let the hung thread die with the process; don't wait for it
        ex.shutdown(wait=False, cancel_futures=True)
        raise TimeoutError(f"API request timed out after {timeout}s")
    else:
        ex.shutdown(wait=False)
        return result


def _log_retry(retry_state):
    """Log retry attempts so they're visible during parallel execution."""
    attempt = retry_state.attempt_number
    exc = retry_state.outcome.exception()
    exc_type = type(exc).__name__ if exc else "unknown"
    exc_msg = str(exc)[:120] if exc else ""
    wait = (
        retry_state.next_action.sleep
        if hasattr(retry_state, "next_action") and retry_state.next_action
        else 0
    )
    print(
        f"  [retry] call_llm attempt {attempt} failed ({exc_type}: {exc_msg}), retrying in {wait:.1f}s..."
    )


@retry(
    wait=wait_exponential_jitter(1, 30),
    stop=stop_after_attempt(3),
    reraise=True,
    before_sleep=_log_retry,
)
def call_llm(
    prompt: str,
    *,
    model: str = "gpt-4o",
    temperature: float = 0,
    max_tokens: Optional[int] = None,
    seed: Optional[int] = None,
    system_prompt: Optional[str] = None,
    images: Optional[List[str | Path]] = None,
    request_timeout: int = _REQUEST_TIMEOUT,
    reasoning_effort: Optional[str] = None,
    thinking_budget: Optional[int] = None,
    thinking_level: Optional[str] = None,
) -> Dict[str, Any]:
    """Send a chat completion request to OpenAI or Gemini.

    Args:
        prompt: The user prompt
        model: Model name (e.g., "gpt-4o", "gemini-2.0-flash-exp", "gemini-1.5-pro")
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate (None = no limit / API default)
        seed: Random seed for reproducibility (OpenAI only)
        system_prompt: System prompt
        images: List of image paths to attach to the user message
        reasoning_effort: Reasoning effort for OpenAI reasoning models ("low"/"medium"/"high")
        thinking_budget: Thinking budget (max tokens) for Gemini 2.5 thinking models
        thinking_level: Thinking level for Gemini 3.x models ("low"/"medium"/"high")

    Returns:
        Dictionary with keys:
            - text: Generated text response
            - usage: Token usage information
            - raw: Raw API response
    """
    if _is_claude_code_model(model):
        return _call_claude_code(
            prompt=prompt,
            model=model,
            system_prompt=system_prompt,
            request_timeout=request_timeout,
            max_turns=int(os.environ.get("CLAUDE_CODE_MAX_TURNS", "20")),
            sandbox_cwd=os.environ.get("CLAUDE_CODE_CWD"),
        )
    if _is_anthropic_model(model):
        return _call_anthropic(
            prompt=prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt=system_prompt,
            images=images,
            request_timeout=request_timeout,
        )
    if _is_gemini_model(model):
        return _call_gemini(
            prompt=prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            seed=seed,
            system_prompt=system_prompt,
            images=images,
            request_timeout=request_timeout,
            thinking_budget=thinking_budget,
            thinking_level=thinking_level,
        )
    else:
        return _call_openai(
            prompt=prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            seed=seed,
            system_prompt=system_prompt,
            images=images,
            request_timeout=request_timeout,
            reasoning_effort=reasoning_effort,
        )


def build_openai_messages(
    prompt: str,
    system_prompt: Optional[str] = None,
    images: Optional[List[str | Path]] = None,
) -> List[Dict[str, Any]]:
    """Build the messages list for an OpenAI chat completion request.

    Extracted from _call_openai so it can be reused by batch submission.
    """
    messages: List[Dict[str, Any]] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})

    if images:
        blocks = [{"type": "text", "text": prompt}] + [
            {"type": "image_url", "image_url": {"url": _file_to_data_url(img)}}
            for img in images
        ]
        messages.append({"role": "user", "content": blocks})
    else:
        messages.append({"role": "user", "content": prompt})
    return messages


def build_openai_request_body(
    messages: List[Dict[str, Any]],
    model: str,
    temperature: float,
    max_tokens: Optional[int] = None,
    seed: Optional[int] = None,
    reasoning_effort: Optional[str] = None,
) -> Dict[str, Any]:
    """Build the API params dict for a chat completion (used in batch JSONL body)."""
    is_reasoning = _is_openai_reasoning_model(model)
    body: Dict[str, Any] = {"model": model, "messages": messages}
    if seed is not None:
        body["seed"] = seed
    if not is_reasoning:
        body["temperature"] = temperature
        if max_tokens is not None:
            body["max_tokens"] = max_tokens
    if reasoning_effort and is_reasoning:
        body["reasoning_effort"] = reasoning_effort
    return body


def _call_openai(
    prompt: str,
    model: str,
    temperature: float,
    max_tokens: Optional[int],
    seed: Optional[int],
    system_prompt: Optional[str],
    images: Optional[List[str | Path]],
    request_timeout: int = _REQUEST_TIMEOUT,
    reasoning_effort: Optional[str] = None,
) -> Dict[str, Any]:
    """Call OpenAI API."""
    global _OPENAI_CLIENT
    if _OPENAI_CLIENT is None:
        from openai import OpenAI

        _OPENAI_CLIENT = OpenAI()

    messages = build_openai_messages(prompt, system_prompt, images)
    api_params = build_openai_request_body(
        messages, model, temperature, max_tokens, seed, reasoning_effort
    )

    resp = _OPENAI_CLIENT.chat.completions.create(**api_params, timeout=request_timeout)
    choice = resp.choices[0]
    text = choice.message.content.strip()
    text = _strip_thinking_tokens(text)
    return {
        "text": text,
        "usage": resp.usage.model_dump(exclude_none=True),
        "raw": resp.model_dump(exclude_none=True),
    }


def _call_gemini(
    prompt: str,
    model: str,
    temperature: float,
    max_tokens: Optional[int],
    seed: Optional[int],
    system_prompt: Optional[str],
    images: Optional[List[str | Path]],
    request_timeout: int = _REQUEST_TIMEOUT,
    thinking_budget: Optional[int] = None,
    thinking_level: Optional[str] = None,
) -> Dict[str, Any]:
    """Call Google Gemini API or Vertex AI using the unified google-genai SDK."""
    from google.genai import types

    client = _get_or_create_genai_client()

    # Build generation config
    config_kwargs: Dict[str, Any] = {
        "temperature": temperature,
    }
    if max_tokens is not None:
        config_kwargs["max_output_tokens"] = max_tokens
    if seed is not None:
        config_kwargs["seed"] = seed
    if system_prompt:
        config_kwargs["system_instruction"] = system_prompt

    # Thinking config — pass thinking_level or thinking_budget natively
    if thinking_level is not None:
        config_kwargs["thinking_config"] = types.ThinkingConfig(
            thinking_level=thinking_level.lower()
        )
    elif thinking_budget is not None:
        config_kwargs["thinking_config"] = types.ThinkingConfig(
            thinking_budget=thinking_budget
        )

    config = types.GenerateContentConfig(**config_kwargs)

    # Build content parts
    content_parts: list = []

    # Add images first if provided
    if images:
        for img_path in images:
            img_bytes = Path(img_path).read_bytes()
            mime = mimetypes.guess_type(str(img_path))[0] or "image/png"
            content_parts.append(types.Part.from_bytes(data=img_bytes, mime_type=mime))

    # Add text prompt
    content_parts.append(prompt)

    # Generate response (with timeout to prevent indefinite hangs)
    resp = _call_with_timeout(
        client.models.generate_content,
        (),
        {"model": model, "contents": content_parts, "config": config},
        request_timeout,
    )

    # Extract text from response, handling models with thinking/thoughts
    try:
        response_text = resp.text
    except ValueError:
        # Handle multi-part responses (thinking models)
        if resp.candidates and resp.candidates[0].content.parts:
            text_parts = []
            for part in resp.candidates[0].content.parts:
                if hasattr(part, "thought") and part.thought:
                    continue
                if hasattr(part, "text") and part.text:
                    text_parts.append(part.text)
            response_text = "".join(text_parts)
        else:
            response_text = ""

    # Extract usage information
    usage_metadata = resp.usage_metadata
    usage = {
        "prompt_tokens": getattr(usage_metadata, "prompt_token_count", 0),
        "completion_tokens": getattr(usage_metadata, "candidates_token_count", 0),
        "total_tokens": getattr(usage_metadata, "total_token_count", 0),
    }

    return {
        "text": response_text.strip(),
        "usage": usage,
        "raw": {
            "text": response_text,
            "usage_metadata": {
                "prompt_token_count": usage.get("prompt_tokens", 0),
                "candidates_token_count": usage.get("completion_tokens", 0),
                "total_token_count": usage.get("total_tokens", 0),
            },
            "finish_reason": (
                resp.candidates[0].finish_reason if resp.candidates else None
            ),
        },
    }


def _call_claude_code(
    prompt: str,
    model: str,
    system_prompt: Optional[str],
    request_timeout: int = _REQUEST_TIMEOUT,
    max_turns: int = 20,
    sandbox_cwd: Optional[str] = None,
) -> Dict[str, Any]:
    """Agentic Claude via the Claude Agent SDK.

    The agent may use Bash/Read/Edit/Write/Grep/Glob in a sandboxed cwd before
    emitting a final assistant message containing a fenced ```python``` block.
    WebSearch and WebFetch are disabled. Vision/temperature/seed/max_tokens/
    reasoning parameters are ignored.

    Requires the `claude` CLI binary on PATH; auth via ANTHROPIC_API_KEY env
    var or a prior `claude login` (Console subscription).
    """
    import asyncio
    import shutil
    import tempfile

    from claude_agent_sdk import ClaudeAgentOptions, query

    underlying_model = _strip_claude_code_prefix(model)
    final_system = (system_prompt or "") + (
        "\n\nIMPORTANT: After exploring with tools, your FINAL message must "
        "contain a single ```python ... ``` block with the solution. The "
        "harness extracts code from that block and executes it."
    )

    owns_sandbox = sandbox_cwd is None
    if owns_sandbox:
        sandbox_cwd = tempfile.mkdtemp(prefix="hexagen_cc_")

    try:
        opts = ClaudeAgentOptions(
            model=underlying_model,
            system_prompt=final_system,
            allowed_tools=["Bash", "Read", "Edit", "Write", "Grep", "Glob"],
            disallowed_tools=["WebSearch", "WebFetch"],
            permission_mode="bypassPermissions",
            max_turns=max_turns,
            cwd=sandbox_cwd,
        )

        async def _run():
            last_text = ""
            raw_usage: Dict[str, Any] = {}
            cost_usd = None
            trace: List[str] = []
            async for msg in query(prompt=prompt, options=opts):
                cls = type(msg).__name__
                trace.append(cls)
                if cls == "AssistantMessage":
                    for block in getattr(msg, "content", []):
                        if type(block).__name__ == "TextBlock":
                            last_text = getattr(block, "text", last_text)
                elif cls == "ResultMessage":
                    u = getattr(msg, "usage", {}) or {}
                    if hasattr(u, "model_dump"):
                        u = u.model_dump()
                    raw_usage = dict(u)
                    cost_usd = getattr(msg, "total_cost_usd", None)
                    final_result = getattr(msg, "result", None)
                    if final_result and not last_text:
                        last_text = final_result
            return last_text, raw_usage, cost_usd, trace

        try:
            text, raw_usage, cost_usd, trace = asyncio.run(
                asyncio.wait_for(_run(), timeout=request_timeout)
            )
        except asyncio.TimeoutError as e:
            raise TimeoutError(
                f"Claude Code request timed out after {request_timeout}s"
            ) from e

        prompt_tokens = (
            int(raw_usage.get("input_tokens", 0))
            + int(raw_usage.get("cache_read_input_tokens", 0))
            + int(raw_usage.get("cache_creation_input_tokens", 0))
        )
        completion_tokens = int(raw_usage.get("output_tokens", 0))
        return {
            "text": _strip_thinking_tokens(text.strip()),
            "usage": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
            },
            "raw": {
                "claude_code": {
                    "model": underlying_model,
                    "usage": raw_usage,
                    "cost_usd": cost_usd,
                    "message_trace": trace,
                    "sandbox_cwd": sandbox_cwd,
                    "max_turns": max_turns,
                }
            },
        }
    finally:
        if owns_sandbox:
            shutil.rmtree(sandbox_cwd, ignore_errors=True)


def _call_anthropic(
    prompt: str,
    model: str,
    temperature: float,
    max_tokens: Optional[int],
    system_prompt: Optional[str],
    images: Optional[List[str | Path]],
    request_timeout: int = _REQUEST_TIMEOUT,
) -> Dict[str, Any]:
    """Direct Anthropic Messages API. Parallel to _call_openai/_call_gemini."""
    global _ANTHROPIC_CLIENT
    if _ANTHROPIC_CLIENT is None:
        from anthropic import Anthropic

        _ANTHROPIC_CLIENT = Anthropic()

    if images:
        content_blocks: List[Dict[str, Any]] = []
        for img in images:
            mime = mimetypes.guess_type(str(img))[0] or "image/png"
            data = base64.b64encode(Path(img).read_bytes()).decode()
            content_blocks.append(
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": mime,
                        "data": data,
                    },
                }
            )
        content_blocks.append({"type": "text", "text": prompt})
        user_content: Any = content_blocks
    else:
        user_content = prompt

    api_kwargs: Dict[str, Any] = {
        "model": model,
        "messages": [{"role": "user", "content": user_content}],
        "max_tokens": max_tokens if max_tokens is not None else 4096,
        "temperature": temperature,
        "timeout": request_timeout,
    }
    if system_prompt:
        api_kwargs["system"] = system_prompt

    resp = _ANTHROPIC_CLIENT.messages.create(**api_kwargs)

    text_parts = [
        b.text for b in resp.content if getattr(b, "type", "") == "text"
    ]
    text = _strip_thinking_tokens("".join(text_parts).strip())

    u = resp.usage
    prompt_tokens = (
        (getattr(u, "input_tokens", 0) or 0)
        + (getattr(u, "cache_read_input_tokens", 0) or 0)
        + (getattr(u, "cache_creation_input_tokens", 0) or 0)
    )
    completion_tokens = getattr(u, "output_tokens", 0) or 0
    return {
        "text": text,
        "usage": {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
        },
        "raw": resp.model_dump(),
    }


# ── OpenAI Batch API helpers ──────────────────────────────────────────────────


def submit_openai_batch(jsonl_lines: List[str]) -> str:
    """Upload a JSONL file and create an OpenAI batch. Returns the batch_id."""
    import io

    global _OPENAI_CLIENT
    if _OPENAI_CLIENT is None:
        from openai import OpenAI

        _OPENAI_CLIENT = OpenAI()

    content = "\n".join(jsonl_lines).encode("utf-8")
    file_obj = io.BytesIO(content)
    file_obj.name = "batch_requests.jsonl"

    uploaded = _OPENAI_CLIENT.files.create(file=file_obj, purpose="batch")
    batch = _OPENAI_CLIENT.batches.create(
        input_file_id=uploaded.id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
    )
    return batch.id


def poll_openai_batch(
    batch_id: str, poll_interval: int = 60, timeout: int = 86400
) -> Any:
    """Poll until the batch reaches a terminal state. Returns the batch object."""
    import time

    global _OPENAI_CLIENT
    terminal = {"completed", "failed", "expired", "cancelled"}
    start = time.monotonic()
    while True:
        batch = _OPENAI_CLIENT.batches.retrieve(batch_id)
        status = batch.status
        counts = batch.request_counts
        print(
            f"  [batch {batch_id[:20]}...] status={status} "
            f"completed={counts.completed}/{counts.total} failed={counts.failed}"
        )
        if status in terminal:
            return batch
        elapsed = time.monotonic() - start
        if elapsed + poll_interval > timeout:
            raise TimeoutError(
                f"Batch {batch_id} did not complete within {timeout}s "
                f"(status={status})"
            )
        time.sleep(poll_interval)


def parse_batch_results(file_id: str) -> Dict[str, Dict[str, Any]]:
    """Download and parse batch output JSONL.

    Returns {custom_id: {"text": str, "usage": dict, "raw": dict, "error": str|None}}.
    """
    import json

    global _OPENAI_CLIENT
    raw_content = _OPENAI_CLIENT.files.content(file_id)
    results: Dict[str, Dict[str, Any]] = {}
    for line in raw_content.text.splitlines():
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


# ── Gemini Batch API helpers ──────────────────────────────────────────────────


def build_gemini_batch_request(
    prompt: str,
    system_prompt: Optional[str] = None,
    images: Optional[List[str | Path]] = None,
    temperature: float = 0,
    max_tokens: Optional[int] = None,
    thinking_budget: Optional[int] = None,
    thinking_level: Optional[str] = None,
) -> Dict[str, Any]:
    """Build a single inline request dict for the Gemini Batch API."""
    # Build content parts
    parts = []
    if images:
        import base64 as b64mod

        for img_path in images:
            img_bytes = Path(img_path).read_bytes()
            mime = mimetypes.guess_type(str(img_path))[0] or "image/png"
            parts.append(
                {
                    "inline_data": {
                        "mime_type": mime,
                        "data": base64.b64encode(img_bytes).decode(),
                    }
                }
            )
    parts.append({"text": prompt})

    request: Dict[str, Any] = {
        "contents": [{"parts": parts, "role": "user"}],
        "config": {
            "temperature": temperature,
        },
    }

    if max_tokens is not None:
        request["config"]["max_output_tokens"] = max_tokens

    if system_prompt:
        request["config"]["system_instruction"] = {"parts": [{"text": system_prompt}]}

    # Thinking config
    if thinking_level is not None:
        request["config"]["thinking_config"] = {
            "thinking_level": thinking_level.lower()
        }
    elif thinking_budget is not None:
        request["config"]["thinking_config"] = {"thinking_budget": thinking_budget}

    return request


def _get_gemini_genai_client() -> Any:
    """Get or create a google-genai Client for batch operations.

    Reuses the globally cached client from _get_or_create_genai_client.
    """
    return _get_or_create_genai_client()


def _is_vertex_batch() -> bool:
    """Check if batch operations should use Vertex AI (GCS-based) path."""
    return bool(os.environ.get("GCP_PROJECT_ID") or os.environ.get("VERTEX_PROJECT_ID"))


def _upload_batch_jsonl_to_gcs(
    requests: List[Dict[str, Any]], display_name: str
) -> str:
    """Upload batch requests as JSONL to GCS. Returns the gs:// URI."""
    import json
    import datetime
    from google.cloud import storage as gcs

    project_id = os.environ.get("GCP_PROJECT_ID") or os.environ.get("VERTEX_PROJECT_ID")
    bucket_name = os.environ.get("BATCH_GCS_BUCKET", f"hexagons-experiments")

    client = gcs.Client(project=project_id)

    # Create bucket if it doesn't exist
    try:
        bucket = client.get_bucket(bucket_name)
    except Exception:
        location = os.environ.get("VERTEX_LOCATION", "global")
        bucket = client.create_bucket(bucket_name, location=location)
        print(f"  [batch] Created GCS bucket: gs://{bucket_name}")

    # Upload JSONL — each line is {"request": <GenerateContentRequest>}
    timestamp = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")
    blob_path = f"batch-input/{display_name}-{timestamp}.jsonl"

    lines = []
    for req in requests:
        # Vertex expects {"request": {contents, generationConfig, systemInstruction, ...}}
        vertex_req: Dict[str, Any] = {"contents": req["contents"]}
        cfg = req.get("config", {})
        gen_config: Dict[str, Any] = {}
        if "temperature" in cfg:
            gen_config["temperature"] = cfg["temperature"]
        if "max_output_tokens" in cfg:
            gen_config["maxOutputTokens"] = cfg["max_output_tokens"]
        if "thinking_config" in cfg:
            tc = cfg["thinking_config"]
            thinking_cfg: Dict[str, Any] = {}
            if "thinking_level" in tc:
                thinking_cfg["thinkingLevel"] = tc["thinking_level"].upper()
            if "thinking_budget" in tc:
                thinking_cfg["thinkingBudget"] = tc["thinking_budget"]
            gen_config["thinkingConfig"] = thinking_cfg
        if gen_config:
            vertex_req["generationConfig"] = gen_config
        if "system_instruction" in cfg:
            vertex_req["systemInstruction"] = cfg["system_instruction"]
        lines.append(json.dumps({"request": vertex_req}))

    content = "\n".join(lines)
    blob = bucket.blob(blob_path)
    blob.upload_from_string(content, content_type="application/jsonl")

    gcs_uri = f"gs://{bucket_name}/{blob_path}"
    print(f"  [batch] Uploaded {len(lines)} requests to {gcs_uri}")
    return gcs_uri


def submit_gemini_batch(
    requests: List[Dict[str, Any]], model: str, display_name: str = "hexagen-batch"
) -> str:
    """Submit batch requests to the Gemini Batch API. Returns the job name.

    For Vertex AI: uploads JSONL to GCS, submits with GCS source/dest.
    For Gemini API: submits inline requests directly.
    """
    client = _get_gemini_genai_client()

    if _is_vertex_batch():
        gcs_input_uri = _upload_batch_jsonl_to_gcs(requests, display_name)
        # Output goes to a unique subdirectory
        job_id = gcs_input_uri.split("/")[-1].replace(".jsonl", "")
        gcs_output_uri = (
            gcs_input_uri.rsplit("/batch-input/", 1)[0] + f"/batch-output/{job_id}/"
        )
        batch_job = client.batches.create(
            model=model,
            src=gcs_input_uri,
            config={
                "display_name": display_name,
                "dest": gcs_output_uri,
            },
        )
    else:
        batch_job = client.batches.create(
            model=model,
            src=requests,
            config={"display_name": display_name},
        )
    return batch_job.name


def poll_gemini_batch(
    job_name: str, poll_interval: int = 30, timeout: int = 86400
) -> Any:
    """Poll until the Gemini batch reaches a terminal state. Returns the batch job."""
    import time

    client = _get_gemini_genai_client()
    terminal = {
        "JOB_STATE_SUCCEEDED",
        "JOB_STATE_FAILED",
        "JOB_STATE_CANCELLED",
        "JOB_STATE_EXPIRED",
    }
    start = time.monotonic()
    while True:
        batch_job = client.batches.get(name=job_name)
        state = (
            batch_job.state.name
            if hasattr(batch_job.state, "name")
            else str(batch_job.state)
        )
        print(f"  [gemini-batch {job_name}] state={state}")
        if state in terminal:
            return batch_job
        elapsed = time.monotonic() - start
        if elapsed + poll_interval > timeout:
            raise TimeoutError(
                f"Gemini batch {job_name} did not complete within {timeout}s "
                f"(state={state})"
            )
        time.sleep(poll_interval)


def parse_gemini_batch_results(
    batch_job: Any, requests: Optional[List[Dict[str, Any]]] = None
) -> Dict[int, Dict[str, Any]]:
    """Parse responses from a completed Gemini batch job.

    Handles both:
    - Inline responses (Gemini API): batch_job.dest.inlined_responses
    - GCS output (Vertex AI): batch_job.dest.gcs_uri -> JSONL files

    Returns {index: {"text": str, "usage": dict, "raw": dict, "error": str|None}}.
    Index corresponds to the position in the original request list.
    """
    if _is_vertex_batch():
        return _parse_vertex_batch_results(batch_job, requests)
    return _parse_inline_batch_results(batch_job)


def _parse_inline_batch_results(batch_job: Any) -> Dict[int, Dict[str, Any]]:
    """Parse inline responses from a Gemini API batch job."""
    results: Dict[int, Dict[str, Any]] = {}

    if not hasattr(batch_job, "dest") or not hasattr(
        batch_job.dest, "inlined_responses"
    ):
        return results

    for i, inline_response in enumerate(batch_job.dest.inlined_responses):
        if hasattr(inline_response, "error") and inline_response.error:
            results[i] = {
                "text": None,
                "usage": {},
                "raw": {},
                "error": str(inline_response.error),
            }
            continue

        resp = inline_response.response
        if resp is None:
            results[i] = {
                "text": None,
                "usage": {},
                "raw": {},
                "error": "empty response",
            }
            continue

        # Extract text - handle thinking models with multiple parts
        try:
            response_text = resp.text
        except (ValueError, AttributeError):
            if resp.candidates and resp.candidates[0].content.parts:
                text_parts = []
                for part in resp.candidates[0].content.parts:
                    if hasattr(part, "thought") and part.thought:
                        continue
                    if hasattr(part, "text") and part.text:
                        text_parts.append(part.text)
                response_text = "".join(text_parts)
            else:
                response_text = ""

        response_text = _strip_thinking_tokens(response_text.strip())

        # Extract usage
        usage = {}
        if hasattr(resp, "usage_metadata") and resp.usage_metadata:
            um = resp.usage_metadata
            usage = {
                "prompt_tokens": getattr(um, "prompt_token_count", 0),
                "completion_tokens": getattr(um, "candidates_token_count", 0),
                "total_tokens": getattr(um, "total_token_count", 0),
            }

        results[i] = {
            "text": response_text,
            "usage": usage,
            "raw": {"text": response_text},
            "error": None,
        }

    return results


def _parse_vertex_batch_results(
    batch_job: Any, requests: Optional[List[Dict[str, Any]]] = None
) -> Dict[int, Dict[str, Any]]:
    """Parse GCS output JSONL from a Vertex AI batch job."""
    import json
    from google.cloud import storage as gcs

    results: Dict[int, Dict[str, Any]] = {}

    # Build prompt_to_index mapping to handle out-of-order Vertex responses
    prompt_to_index = {}
    if requests:
        for req_idx, req in enumerate(requests):
            req_parts = req.get("contents", [{}])[0].get("parts", [])
            for part in reversed(req_parts):
                if "text" in part:
                    prompt_to_index[part["text"].strip()] = req_idx
                    break

    # Get output GCS URI from the batch job
    if not hasattr(batch_job, "dest") or not hasattr(batch_job.dest, "gcs_uri"):
        print("  [batch] WARNING: No GCS output URI found on batch job")
        return results

    output_uri = batch_job.dest.gcs_uri  # e.g. gs://bucket/batch-output/
    if not output_uri:
        return results

    # Parse bucket and prefix from gs:// URI
    parts = output_uri.replace("gs://", "").split("/", 1)
    bucket_name = parts[0]
    prefix = parts[1] if len(parts) > 1 else ""

    project_id = os.environ.get("GCP_PROJECT_ID") or os.environ.get("VERTEX_PROJECT_ID")
    client = gcs.Client(project=project_id)
    bucket = client.bucket(bucket_name)

    # List and download all JSONL output files under the prefix
    # Vertex creates a subdirectory `prediction-<model>-<timestamp>` inside the dest directory.
    # Group blobs by their parent directory to ensure we only read the latest job output.
    import datetime

    blob_dirs = {}
    for blob in bucket.list_blobs(prefix=prefix):
        if blob.name.endswith(".jsonl"):
            dirname = "/".join(blob.name.split("/")[:-1])
            if dirname not in blob_dirs:
                blob_dirs[dirname] = []
            blob_dirs[dirname].append(blob)

    all_lines: List[str] = []
    latest_dir = ""
    if blob_dirs:
        # If the destination URI ends with a job ID, it's a new isolated job and we take the latest directory inside it.
        # If it's a legacy generic 'batch-output/' job, we should try to match the directory timestamp to the job's update time.
        is_legacy = output_uri.strip("/").endswith("batch-output")

        def _dir_time(d):
            times = [b.updated for b in blob_dirs[d] if b.updated]
            return (
                max(times)
                if times
                else datetime.datetime.min.replace(tzinfo=datetime.timezone.utc)
            )

        if is_legacy and hasattr(batch_job, "update_time") and batch_job.update_time:
            # For legacy jobs, find the directory updated closest to the job's update_time
            job_time = batch_job.update_time

            # update_time is already UTC aware usually
            def _time_diff(d):
                dt = _dir_time(d)
                return abs((dt - job_time).total_seconds())

            latest_dir = min(blob_dirs.keys(), key=_time_diff)
        else:
            # For isolated jobs (or if we can't find update_time), just take the latest
            latest_dir = max(blob_dirs.keys(), key=_dir_time)

        for blob in blob_dirs[latest_dir]:
            content = blob.download_as_text()
            all_lines.extend(content.strip().splitlines())

    print(
        f"  [batch] Downloaded {len(all_lines)} result lines from {output_uri} (dir: {latest_dir})"
    )

    for i, line in enumerate(all_lines):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            results[i] = {
                "text": None,
                "usage": {},
                "raw": {},
                "error": f"invalid JSON in output line {i}",
            }
            continue

        target_idx = i
        if requests:
            prompt_text = ""
            item_parts = (
                item.get("request", {}).get("contents", [{}])[0].get("parts", [])
            )
            for part in reversed(item_parts):
                if "text" in part:
                    prompt_text = part["text"]
                    break

            if prompt_text:
                prompt_text_clean = prompt_text.strip()
                if prompt_text_clean in prompt_to_index:
                    target_idx = prompt_to_index[prompt_text_clean]
                else:
                    print(
                        f"  [batch] WARNING: Could not find original request index for out-of-order prompt. Skipping line {i}."
                    )
                    continue
            else:
                print(
                    f"  [batch] WARNING: Prompt text not found in response item. Skipping line {i}."
                )
                continue

        # Check for error status
        status = item.get("status", "")
        if status:
            results[target_idx] = {
                "text": None,
                "usage": {},
                "raw": {},
                "error": str(status),
            }
            continue

        resp = item.get("response", {})
        if not resp:
            results[target_idx] = {
                "text": None,
                "usage": {},
                "raw": {},
                "error": "empty response",
            }
            continue

        # Extract text from candidates
        response_text = ""
        candidates = resp.get("candidates", [])
        if candidates:
            parts = candidates[0].get("content", {}).get("parts", [])
            text_parts = []
            for part in parts:
                # Skip thinking parts
                if part.get("thought"):
                    continue
                if "text" in part:
                    text_parts.append(part["text"])
            response_text = "".join(text_parts)

        response_text = _strip_thinking_tokens(response_text.strip())

        # Extract usage
        usage = {}
        usage_meta = resp.get("usageMetadata", {})
        if usage_meta:
            usage = {
                "prompt_tokens": usage_meta.get("promptTokenCount", 0),
                "completion_tokens": usage_meta.get("candidatesTokenCount", 0),
                "total_tokens": usage_meta.get("totalTokenCount", 0),
            }

        results[target_idx] = {
            "text": response_text,
            "usage": usage,
            "raw": resp,
            "error": None,
        }

    return results


# Backwards compatibility alias
call_gpt = call_llm
