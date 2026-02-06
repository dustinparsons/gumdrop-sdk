"""
LMStudio provider for Gumdrop.

Supports both LMStudio's native API (/api/v1/chat) and
OpenAI-compatible endpoint (/v1/chat/completions).
Defaults to native API for richer metadata.
"""

import os
from typing import List, Dict, Optional, AsyncIterator
from .base import BaseProvider

try:
    import httpx
except ImportError:
    httpx = None


class LMStudioProvider(BaseProvider):
    """LMStudio local inference provider."""

    name = "lmstudio"

    def __init__(
        self,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        api_format: str = "native",  # "native" or "openai"
    ):
        self.base_url = (
            base_url
            or os.environ.get("LMSTUDIO_BASE_URL", "http://127.0.0.1:1234")
        ).rstrip("/")
        self.model = model or self.get_default_model()
        self.api_format = api_format

        if httpx is None:
            raise ImportError("httpx required for LMStudio provider. pip install httpx")
        self._client = httpx.Client(timeout=120.0)

    def chat(
        self,
        messages: List[Dict[str, str]],
        system: str = "",
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> str:
        # Use native API for single-turn, OpenAI-compat for multi-turn
        if self.api_format == "native" and len(messages) <= 1:
            return self._chat_native(messages, system, model, temperature, max_tokens)
        return self._chat_openai(messages, system, model, temperature, max_tokens)

    def _chat_native(self, messages, system, model, temperature, max_tokens) -> str:
        """LMStudio native API: /api/v1/chat"""
        # Build input from messages (native API takes a single input string
        # or we can use the last user message)
        last_user = ""
        context_parts = []
        for msg in messages:
            if msg["role"] == "user":
                last_user = msg["content"]
            context_parts.append(f"[{msg['role']}]: {msg['content']}")

        # For multi-turn, pack context into system_prompt and last message as input
        full_system = system
        if len(messages) > 1:
            context = "\n".join(context_parts[:-1])
            full_system = f"{system}\n\n--- Conversation so far ---\n{context}"

        payload = {
            "model": model or self.model,
            "system_prompt": full_system,
            "input": last_user,
        }

        resp = self._client.post(f"{self.base_url}/api/v1/chat", json=payload)
        resp.raise_for_status()
        data = resp.json()

        # Extract text from response
        output = data.get("output", [])
        if output and isinstance(output, list):
            for item in output:
                if item.get("type") == "message":
                    return item.get("content", "")
        # Fallback
        return str(data)

    def _chat_openai(self, messages, system, model, temperature, max_tokens) -> str:
        """OpenAI-compatible API: /v1/chat/completions"""
        full_messages = []
        if system:
            full_messages.append({"role": "system", "content": system})
        full_messages.extend(messages)

        payload = {
            "model": model or self.model,
            "messages": full_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        resp = self._client.post(
            f"{self.base_url}/v1/chat/completions",
            json=payload,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]

    async def chat_stream(
        self,
        messages: List[Dict[str, str]],
        system: str = "",
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> AsyncIterator[str]:
        # Streaming via OpenAI-compatible endpoint
        full_messages = []
        if system:
            full_messages.append({"role": "system", "content": system})
        full_messages.extend(messages)

        payload = {
            "model": model or self.model,
            "messages": full_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/v1/chat/completions",
                json=payload,
            ) as resp:
                async for line in resp.aiter_lines():
                    if line.startswith("data: ") and line != "data: [DONE]":
                        import json
                        chunk = json.loads(line[6:])
                        delta = chunk.get("choices", [{}])[0].get("delta", {})
                        if "content" in delta:
                            yield delta["content"]

    def get_default_model(self) -> str:
        return "google/gemma-3n-e4b:2"
