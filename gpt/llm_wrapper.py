"""Generic LLM wrapper with support for OpenAI and Gemini models."""

from __future__ import annotations

import base64
import mimetypes
from pathlib import Path
from typing import Any, Dict, List, Optional
import os
import argparse

from tenacity import retry, wait_exponential_jitter, stop_after_attempt

os.environ["GRPC_DNS_RESOLVER"] = "native"

# Global clients/state for persistence
_OPENAI_CLIENT: Optional[Any] = None
_GEMINI_CONFIGURED: bool = False
_VERTEX_CONFIGURED: bool = False

def init_llm(cfg: argparse.Namespace) -> None:
    """Initialize LLM clients based on configuration."""
    global _OPENAI_CLIENT, _GEMINI_CONFIGURED, _VERTEX_CONFIGURED
    
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

    # Gemini / Vertex AI
    if _is_gemini_model(cfg.model):
        project_id = os.environ.get("GCP_PROJECT_ID") or os.environ.get("VERTEX_PROJECT_ID")
        
        if project_id:
            import vertexai
            location = os.environ.get("VERTEX_LOCATION", "global")
            vertexai.init(project=project_id, location=location)
            _VERTEX_CONFIGURED = True
        else:
            import google.generativeai as genai
            api_key = (getattr(cfg, "api_key", None) or 
                       os.environ.get("GOOGLE_API_KEY") or 
                       os.environ.get("GEMINI_API_KEY"))
            if api_key:
                genai.configure(api_key=api_key)
                _GEMINI_CONFIGURED = True


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


def _is_gemini_model(model: str) -> bool:
    """Check if model is a Gemini model."""
    return "gemini" in model.lower()


def _is_openai_reasoning_model(model: str) -> bool:
    """Check if model is an OpenAI reasoning model (o1/o3 series)."""
    return any(prefix in model.lower() for prefix in ["o1", "o3", "gpt-5.1"])


@retry(wait=wait_exponential_jitter(1, 30), stop=stop_after_attempt(5), reraise=True)
def call_llm(
    prompt: str,
    *,
    model: str = "gpt-4o",
    temperature: float = 0.2,
    max_tokens: int = 512,
    seed: Optional[int] = None,
    system_prompt: Optional[str] = None,
    images: Optional[List[str | Path]] = None,
) -> Dict[str, Any]:
    """Send a chat completion request to OpenAI or Gemini.

    Args:
        prompt: The user prompt
        model: Model name (e.g., "gpt-4o", "gemini-2.0-flash-exp", "gemini-1.5-pro")
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate
        seed: Random seed for reproducibility (OpenAI only)
        system_prompt: System prompt
        images: List of image paths to attach to the user message

    Returns:
        Dictionary with keys:
            - text: Generated text response
            - usage: Token usage information
            - raw: Raw API response
    """
    if _is_gemini_model(model):
        return _call_gemini(
            prompt=prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt=system_prompt,
            images=images,
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
        )


def _call_openai(
    prompt: str,
    model: str,
    temperature: float,
    max_tokens: int,
    seed: Optional[int],
    system_prompt: Optional[str],
    images: Optional[List[str | Path]],
) -> Dict[str, Any]:
    """Call OpenAI API."""
    global _OPENAI_CLIENT
    if _OPENAI_CLIENT is None:
        from openai import OpenAI
        _OPENAI_CLIENT = OpenAI()

    # Build messages
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

    # Call API
    is_reasoning_model = _is_openai_reasoning_model(model)

    api_params = {
        "model": model,
        "messages": messages,
        "seed": seed,
    }

    if not is_reasoning_model:
        api_params["temperature"] = temperature
        api_params["max_tokens"] = max_tokens

    resp = _OPENAI_CLIENT.chat.completions.create(**api_params)
    choice = resp.choices[0]
    return {
        "text": choice.message.content.strip(),
        "usage": resp.usage.model_dump(exclude_none=True),
        "raw": resp.model_dump(exclude_none=True),
    }


def _call_gemini(
    prompt: str,
    model: str,
    temperature: float,
    max_tokens: int,
    system_prompt: Optional[str],
    images: Optional[List[str | Path]],
) -> Dict[str, Any]:
    """Call Google Gemini API or Vertex AI."""
    import os
    
    global _VERTEX_CONFIGURED, _GEMINI_CONFIGURED

    # Check for Vertex preference first
    project_id = os.environ.get("GCP_PROJECT_ID") or os.environ.get("VERTEX_PROJECT_ID")

    if project_id:
        return _call_vertex_ai(
            prompt=prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt=system_prompt,
            images=images,
            project_id=project_id,
        )
    else:
        return _call_gemini_api(
            prompt=prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt=system_prompt,
            images=images,
        )


def _call_gemini_api(
    prompt: str,
    model: str,
    temperature: float,
    max_tokens: int,
    system_prompt: Optional[str],
    images: Optional[List[str | Path]],
) -> Dict[str, Any]:
    """Call Google Gemini API (non-Vertex)."""
    import google.generativeai as genai
    import os

    global _GEMINI_CONFIGURED
    if not _GEMINI_CONFIGURED:
        # Configure API key if not already done
        api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError(
                "GOOGLE_API_KEY or GEMINI_API_KEY environment variable must be set for Gemini API"
            )
        genai.configure(api_key=api_key)
        _GEMINI_CONFIGURED = True

    # Create model instance
    generation_config = {
        "temperature": temperature,
        "max_output_tokens": max_tokens,
    }

    # System instruction (system prompt) is set at model level in Gemini
    client = genai.GenerativeModel(
        model_name=model,
        generation_config=generation_config,
        system_instruction=system_prompt,
    )

    # Build content parts
    content_parts = []

    # Add images first if provided
    if images:
        from PIL import Image

        for img_path in images:
            img = Image.open(img_path)
            content_parts.append(img)

    # Add text prompt
    content_parts.append(prompt)

    # Generate response
    resp = client.generate_content(content_parts)

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
        "prompt_tokens": usage_metadata.prompt_token_count,
        "completion_tokens": usage_metadata.candidates_token_count,
        "total_tokens": usage_metadata.total_token_count,
    }

    return {
        "text": response_text.strip(),
        "usage": usage,
        "raw": {
            "text": response_text,
            "usage_metadata": {
                "prompt_token_count": usage_metadata.prompt_token_count,
                "candidates_token_count": usage_metadata.candidates_token_count,
                "total_token_count": usage_metadata.total_token_count,
            },
            "finish_reason": (
                resp.candidates[0].finish_reason if resp.candidates else None
            ),
        },
    }


def _call_vertex_ai(
    prompt: str,
    model: str,
    temperature: float,
    max_tokens: int,
    system_prompt: Optional[str],
    images: Optional[List[str | Path]],
    project_id: str,
) -> Dict[str, Any]:
    """Call Google Vertex AI."""
    import vertexai
    from vertexai.preview.generative_models import GenerativeModel, Part
    import os
    
    global _VERTEX_CONFIGURED
    if not _VERTEX_CONFIGURED:
        # Fallback initialization if init_llm wasn't called or didn't find the project_id
        location = os.environ.get("VERTEX_LOCATION", "global")
        vertexai.init(project=project_id, location=location)
        _VERTEX_CONFIGURED = True

    # Create model instance
    generation_config = {
        "temperature": temperature,
    }

    # Initialize model with system instruction
    client = GenerativeModel(
        model_name=model,
        generation_config=generation_config,
        system_instruction=system_prompt,
    )

    # Build content parts
    content_parts = []

    # Add images first if provided
    if images:
        from PIL import Image
        import io

        for img_path in images:
            img = Image.open(img_path)
            # Convert to bytes
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format=img.format or "PNG")
            img_bytes = img_byte_arr.getvalue()

            # Determine mime type
            mime_type = f"image/{(img.format or 'png').lower()}"
            content_parts.append(Part.from_data(data=img_bytes, mime_type=mime_type))

    # Add text prompt
    content_parts.append(prompt)

    # Generate response
    resp = client.generate_content(content_parts)

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
        "prompt_tokens": usage_metadata.prompt_token_count,
        "completion_tokens": usage_metadata.candidates_token_count,
        "total_tokens": usage_metadata.total_token_count,
    }

    return {
        "text": response_text.strip(),
        "usage": usage,
        "raw": {
            "text": response_text,
            "usage_metadata": {
                "prompt_token_count": usage_metadata.prompt_token_count,
                "candidates_token_count": usage_metadata.candidates_token_count,
                "total_token_count": usage_metadata.total_token_count,
            },
            "finish_reason": (
                resp.candidates[0].finish_reason if resp.candidates else None
            ),
        },
    }


# Backwards compatibility alias
call_gpt = call_llm
