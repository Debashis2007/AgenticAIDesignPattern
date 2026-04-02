"""LLM client abstraction supporting multiple providers."""

from abc import ABC, abstractmethod
from typing import Any, Optional
import asyncio


class LLMClient(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    async def complete(self, prompt: str, **kwargs) -> str:
        """Generate a completion from a prompt."""
        pass

    @abstractmethod
    async def chat_with_tools(
        self, messages: list[dict], tools: list[dict], **kwargs
    ) -> dict:
        """Generate a chat completion with tool use capabilities."""
        pass


class OpenAIClient(LLMClient):
    """OpenAI API client."""

    def __init__(self, api_key: str, model: str = "gpt-4-turbo-preview"):
        self.api_key = api_key
        self.model = model
        self.client = None  # Lazy initialization

    def _get_client(self):
        """Lazy initialize OpenAI client."""
        if self.client is None:
            try:
                from openai import AsyncOpenAI

                self.client = AsyncOpenAI(api_key=self.api_key)
            except ImportError:
                raise ImportError("openai package required: pip install openai")
        return self.client

    async def complete(self, prompt: str, **kwargs) -> str:
        """Generate completion from OpenAI."""
        client = self._get_client()
        response = await client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            **kwargs,
        )
        return response.choices[0].message.content

    async def chat_with_tools(
        self, messages: list[dict], tools: list[dict], **kwargs
    ) -> dict:
        """Generate chat completion with tool use."""
        client = self._get_client()
        response = await client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=[{"type": "function", "function": tool} for tool in tools],
            tool_choice="auto",
            **kwargs,
        )
        return {
            "content": response.choices[0].message.content,
            "tool_calls": response.choices[0].message.tool_calls,
        }


class AnthropicClient(LLMClient):
    """Anthropic API client."""

    def __init__(self, api_key: str, model: str = "claude-3-opus-20240229"):
        self.api_key = api_key
        self.model = model
        self.client = None  # Lazy initialization

    def _get_client(self):
        """Lazy initialize Anthropic client."""
        if self.client is None:
            try:
                from anthropic import AsyncAnthropic

                self.client = AsyncAnthropic(api_key=self.api_key)
            except ImportError:
                raise ImportError("anthropic package required: pip install anthropic")
        return self.client

    async def complete(self, prompt: str, **kwargs) -> str:
        """Generate completion from Anthropic."""
        client = self._get_client()
        response = await client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
            **kwargs,
        )
        return response.content[0].text

    async def chat_with_tools(
        self, messages: list[dict], tools: list[dict], **kwargs
    ) -> dict:
        """Generate chat completion with tool use."""
        client = self._get_client()
        response = await client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=messages,
            tools=tools,
            **kwargs,
        )
        return {
            "content": response.content[0].text if response.content else "",
            "tool_calls": [
                tc for tc in response.content if tc.type == "tool_use"
            ],
        }


async def get_llm_client(provider: str = "openai", **kwargs) -> LLMClient:
    """Factory function to get LLM client."""
    if provider == "openai":
        return OpenAIClient(**kwargs)
    elif provider == "anthropic":
        return AnthropicClient(**kwargs)
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")
