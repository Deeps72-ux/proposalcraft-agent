import os
import time
import json
import logging
from typing import Dict, Any, Optional, List
from groq import Groq, RateLimitError
from app.core.config import settings

logger = logging.getLogger(__name__)

_client: Optional[Groq] = None

FALLBACK_MODELS = [
    "qwen/qwen3.8-27b",
    "openai/gpt-oss-20b",
    "groq/compound-mini",
]


def get_llm_client() -> Groq:
    global _client
    if _client is None:
        api_key = settings.GROQ_API_KEY or os.environ.get("GROQ_API_KEY", "")
        if not api_key:
            raise ValueError("GROQ_API_KEY is not set. Please provide it in .env.")
        _client = Groq(api_key=api_key)
    return _client


def call_llm_json(
    prompt: str,
    system_prompt: str = "You are an enterprise AI proposal consultant. Output valid, parseable JSON only.",
    model: Optional[str] = None,
    temperature: float = 0.2,
) -> Dict[str, Any]:
    """Call Groq LLM requesting structured JSON output with automatic rate-limit backoff and fallback models."""
    client = get_llm_client()
    primary_model = model or settings.GROQ_CHAT_MODEL or "qwen/qwen3.8-27b"

    candidate_models = [primary_model]
    for fb in FALLBACK_MODELS:
        if fb not in candidate_models:
            candidate_models.append(fb)

    messages = [
        {"role": "system", "content": system_prompt + " ALWAYS return pure, valid JSON."},
        {"role": "user", "content": prompt},
    ]

    last_error = None
    for target_model in candidate_models:
        for attempt in range(2):
            try:
                response = client.chat.completions.create(
                    model=target_model,
                    messages=messages,
                    response_format={"type": "json_object"},
                    temperature=temperature,
                )
                raw_content = response.choices[0].message.content or "{}"
                try:
                    return json.loads(raw_content)
                except json.JSONDecodeError:
                    clean = raw_content.strip()
                    if "```json" in clean:
                        clean = clean.split("```json", 1)[1].split("```", 1)[0].strip()
                    elif "```" in clean:
                        clean = clean.split("```", 1)[1].split("```", 1)[0].strip()
                    return json.loads(clean)
            except RateLimitError as rle:
                last_error = rle
                wait_time = 4.5 * (attempt + 1)
                logger.warning(f"Groq Rate limit on {target_model} (attempt {attempt+1}): {rle}. Waiting {wait_time}s...")
                time.sleep(wait_time)
            except Exception as e:
                last_error = e
                logger.warning(f"Groq invocation failed on {target_model}: {e}. Trying next candidate...")
                break

    logger.error(f"All candidate models exhausted. Last error: {last_error}")
    raise last_error


def call_llm_text(
    prompt: str,
    system_prompt: str = "You are an enterprise AI proposal consultant.",
    model: Optional[str] = None,
    temperature: float = 0.3,
) -> str:
    """Call Groq LLM for free-form text output with model fallback."""
    client = get_llm_client()
    primary_model = model or settings.GROQ_CHAT_MODEL or "qwen/qwen3.8-27b"

    candidate_models = [primary_model] + [m for m in FALLBACK_MODELS if m != primary_model]

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt},
    ]

    for target_model in candidate_models:
        try:
            response = client.chat.completions.create(
                model=target_model,
                messages=messages,
                temperature=temperature,
            )
            return (response.choices[0].message.content or "").strip()
        except Exception as e:
            logger.warning(f"Groq text call failed on {target_model}: {e}")
            continue

    return ""
