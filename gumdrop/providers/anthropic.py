"""
Anthropic (Claude) provider for Gumdrop.
"""

import os
from typing import List, Dict, Optional, AsyncIterator
from .base import BaseProvider


class AnthropicProvider(BaseProvider):
    """Claude provider via the Anthropic API."""
    
    name = "anthropic"
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        self.model = model or self.get_default_model()
        self._client = None
    
    def _get_client(self):
        if self._client is None:
            try:
                import anthropic
                self._client = anthropic.Anthropic(api_key=self.api_key)
            except ImportError:
                raise ImportError(
                    "anthropic package required. Install with: pip install anthropic"
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
        
        response = client.messages.create(
            model=model or self.model,
            system=system,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
        return response.content[0].text
    
    async def chat_stream(
        self,
        messages: List[Dict[str, str]],
        system: str = "",
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> AsyncIterator[str]:
        client = self._get_client()
        
        with client.messages.stream(
            model=model or self.model,
            system=system,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        ) as stream:
            for text in stream.text_stream:
                yield text
    
    def get_default_model(self) -> str:
        return "claude-sonnet-4-5-20241022"
