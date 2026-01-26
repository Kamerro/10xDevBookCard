from __future__ import annotations

import json
import os
from typing import Any

import httpx


class OpenRouterError(Exception):
    pass


class OpenRouterAuthError(OpenRouterError):
    pass


class OpenRouterRateLimitError(OpenRouterError):
    pass


class OpenRouterTimeoutError(OpenRouterError):
    pass


class OpenRouterUpstreamError(OpenRouterError):
    pass


class OpenRouterInvalidResponseError(OpenRouterError):
    pass


def _get_openrouter_base_url() -> str:
    return os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")


def _get_openrouter_model() -> str:
    return os.environ.get("OPENROUTER_MODEL", "openai/gpt-4o-mini")


def _get_timeout_seconds() -> float:
    raw = os.environ.get("OPENROUTER_TIMEOUT_SECONDS", "30")
    try:
        return float(raw)
    except ValueError:
        return 30.0


def _get_api_key() -> str:
    key = os.environ.get("OPENROUTER_API_KEY", "")
    if not key:
        raise OpenRouterAuthError("OPENROUTER_API_KEY is not set")
    return key


async def chat_completion(
    *,
    model: str | None = None,
    messages: list[dict[str, Any]],
    response_format: dict[str, Any] | None = None,
) -> dict[str, Any]:
    base_url = _get_openrouter_base_url()
    api_key = _get_api_key()
    timeout_seconds = _get_timeout_seconds()

    payload: dict[str, Any] = {
        "model": model or _get_openrouter_model(),
        "messages": messages,
    }
    if response_format is not None:
        payload["response_format"] = response_format

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=timeout_seconds) as client:
            resp = await client.post(
                f"{base_url}/chat/completions",
                headers=headers,
                json=payload,
            )
    except httpx.TimeoutException as exc:
        raise OpenRouterTimeoutError("OpenRouter request timed out") from exc
    except httpx.HTTPError as exc:
        raise OpenRouterUpstreamError("OpenRouter request failed") from exc

    if resp.status_code in (401, 403):
        raise OpenRouterAuthError("OpenRouter authentication failed")
    if resp.status_code == 429:
        raise OpenRouterRateLimitError("OpenRouter rate limit exceeded")
    if 500 <= resp.status_code:
        raise OpenRouterUpstreamError(f"OpenRouter upstream error: {resp.status_code}")
    if 400 <= resp.status_code:
        raise OpenRouterUpstreamError(f"OpenRouter request rejected: {resp.status_code}")

    try:
        data = resp.json()
    except ValueError as exc:
        raise OpenRouterInvalidResponseError("OpenRouter returned non-JSON response") from exc

    try:
        _ = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise OpenRouterInvalidResponseError("OpenRouter returned invalid response shape") from exc

    return data


async def structured_output(
    *,
    messages: list[dict[str, Any]],
    schema_name: str,
    json_schema: dict[str, Any],
    model: str | None = None,
) -> dict[str, Any]:
    response_format = {
        "type": "json_schema",
        "json_schema": {
            "name": schema_name,
            "strict": True,
            "schema": json_schema,
        },
    }

    data = await chat_completion(
        model=model,
        messages=messages,
        response_format=response_format,
    )

    content = data["choices"][0]["message"]["content"]
    if not isinstance(content, str) or not content.strip():
        raise OpenRouterInvalidResponseError("OpenRouter returned empty content")

    try:
        parsed = json.loads(content)
    except json.JSONDecodeError as exc:
        raise OpenRouterInvalidResponseError("OpenRouter content is not valid JSON") from exc

    if not isinstance(parsed, dict):
        raise OpenRouterInvalidResponseError("Structured output must be a JSON object")

    return parsed
