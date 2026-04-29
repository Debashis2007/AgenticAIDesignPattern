"""OpenAI-compatible LLM helpers.

Supports hosted OpenAI APIs and local Ollama (OpenAI-compatible mode).
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any
from urllib import error, request


@dataclass
class OpenAICompatibleClient:
    """Small client for OpenAI-compatible `/chat/completions` endpoint."""

    base_url: str
    model: str
    api_key: str
    timeout_seconds: float = 12.0

    def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = json.dumps(
            {
                "model": self.model,
                "messages": messages,
                "temperature": 0.2,
            }
        ).encode("utf-8")

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        req = request.Request(
            url=f"{self.base_url.rstrip('/')}/chat/completions",
            data=payload,
            headers=headers,
            method="POST",
        )

        with request.urlopen(req, timeout=self.timeout_seconds) as response:
            body = response.read().decode("utf-8")

        parsed: dict[str, Any] = json.loads(body)
        choices = parsed.get("choices", [])
        if not choices:
            return ""
        message = choices[0].get("message", {})
        return str(message.get("content", "")).strip()


def llm_enabled() -> bool:
    enabled = os.getenv("LLM_ENABLED", "true").strip().lower()
    return enabled in {"1", "true", "yes", "on"}


def get_openai_compatible_client() -> OpenAICompatibleClient:
    provider = os.getenv("LLM_PROVIDER", "openai").strip().lower()
    if provider == "ollama":
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
        model = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
        api_key = os.getenv("OLLAMA_API_KEY", "ollama")
    else:
        base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        api_key = os.getenv("OPENAI_API_KEY", "")

    return OpenAICompatibleClient(
        base_url=base_url,
        model=model,
        api_key=api_key,
        timeout_seconds=float(os.getenv("LLM_TIMEOUT_SECONDS", "12")),
    )


def try_llm_prompt(prompt: str, system_prompt: str | None = None) -> str | None:
    """Attempt an LLM call and return None on connectivity/runtime errors."""
    if not llm_enabled():
        return None

    try:
        result = get_openai_compatible_client().generate(prompt, system_prompt=system_prompt)
    except (ValueError, OSError, TimeoutError, error.URLError, json.JSONDecodeError):
        return None

    return result or None