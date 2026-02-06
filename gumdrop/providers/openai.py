"""
OpenAI-compatible provider for Gumdrop.

Works with OpenAI, Azure OpenAI, and any OpenAI-compatible API
(Ollama, LMStudio, vLLM, etc.)
"""

import os
from typing import List, Dict, Optional, AsyncIterator
from .base import BaseProvider


class OpenAIProvider(BaseProvider):
    """OpenAI-compatible provider."""
    
    name = "openai"
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
    ):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
        self.base_url = base_url or os.environ.get("OPENAI_BASE_URL")
        self.model = model or self.get_default_model()
        self._client = None
    
    def _get_client(self):
        if self._client is None:
            try:
                from openai import OpenAI
                kwargs = {"api_key": self.api_key}
                if self.base_url:
                    kwargs["base_url"] = self.base_url
                self._client = OpenAI(**kwargs)
            except ImportError:
                raise ImportError(
                    "openai package required. Install with: pip install openai"
                )
        return self._client
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        system: str = "",
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> str:
        client = self._get_client()
        
        # Prepend system message
        full_messages = []
        if system:
            full_messages.append({"role": "system", "content": system})
        full_messages.extend(messages)
        
        response = client.chat.completions.create(
            model=model or self.model,
            messages=full_messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
        return response.choices[0].message.content
    
    async def chat_stream(
        self,
        messages: List[Dict[str, str]],
        system: str = "",
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> AsyncIterator[str]:
        client = self._get_client()
        
        full_messages = []
        if system:
            full_messages.append({"role": "system", "content": system})
        full_messages.extend(messages)
        
        stream = client.chat.completions.create(
            model=model or self.model,
            messages=full_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )
        
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    def get_default_model(self) -> str:
        return "gpt-4o"
