#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Small stdlib DeepSeek client for paper-notes automation."""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any


DEFAULT_BASE_URL = "https://api.deepseek.com"
DEFAULT_TIMEOUT_SECONDS = 120


class DeepSeekError(RuntimeError):
    """Raised when a DeepSeek API call fails or returns an unexpected shape."""


@dataclass(frozen=True)
class DeepSeekConfig:
    api_key: str
    base_url: str = DEFAULT_BASE_URL
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS

    @classmethod
    def from_env(cls) -> "DeepSeekConfig":
        api_key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
        if not api_key:
            raise DeepSeekError("DEEPSEEK_API_KEY is not set")
        return cls(
            api_key=api_key,
            base_url=os.environ.get("DEEPSEEK_BASE_URL", DEFAULT_BASE_URL).rstrip("/"),
            timeout_seconds=int(os.environ.get("DEEPSEEK_TIMEOUT_SECONDS", DEFAULT_TIMEOUT_SECONDS)),
        )


def chat_completion(
    *,
    messages: list[dict[str, str]],
    model: str = "deepseek-v4-flash",
    temperature: float = 0.2,
    max_tokens: int = 4096,
    thinking: str = "disabled",
    reasoning_effort: str | None = None,
    config: DeepSeekConfig | None = None,
    retries: int = 2,
) -> dict[str, Any]:
    """Call DeepSeek's OpenAI-compatible chat completion endpoint."""
    config = config or DeepSeekConfig.from_env()
    payload: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False,
        "response_format": {"type": "json_object"},
    }
    if thinking in {"enabled", "disabled"}:
        payload["thinking"] = {"type": thinking}
    if reasoning_effort:
        payload["reasoning_effort"] = reasoning_effort

    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        f"{config.base_url}/chat/completions",
        data=body,
        headers={
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    last_error: Exception | None = None
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(request, timeout=config.timeout_seconds) as response:
                raw = response.read().decode("utf-8")
            return json.loads(raw)
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError) as exc:
            last_error = exc
            if attempt >= retries:
                break
            time.sleep(1.5 * (attempt + 1))
    raise DeepSeekError(f"DeepSeek call failed after {retries + 1} attempt(s): {last_error}")


def completion_text(response: dict[str, Any]) -> str:
    try:
        return str(response["choices"][0]["message"]["content"])
    except (KeyError, IndexError, TypeError) as exc:
        raise DeepSeekError("DeepSeek response did not include choices[0].message.content") from exc


def parse_json_object(text: str) -> dict[str, Any]:
    """Parse a model JSON object, tolerating fenced JSON wrappers."""
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        stripped = "\n".join(lines).strip()
    try:
        data = json.loads(stripped)
    except json.JSONDecodeError as exc:
        start = stripped.find("{")
        end = stripped.rfind("}")
        if start < 0 or end <= start:
            print("--- FAILED TO PARSE MODEL OUTPUT ---")
            print(text)
            print("-----------------------------------")
            raise DeepSeekError("Model output did not contain a JSON object") from exc
        try:
            data = json.loads(stripped[start : end + 1])
        except json.JSONDecodeError as exc2:
            print("--- FAILED TO PARSE MODEL OUTPUT (SUBSTRING) ---")
            print(stripped[start : end + 1])
            print("-----------------------------------------------")
            raise exc2
    if not isinstance(data, dict):
        raise DeepSeekError("Model output JSON must be an object")
    return data
