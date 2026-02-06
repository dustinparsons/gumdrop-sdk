"""
Base provider interface for LLM backends.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, AsyncIterator


class BaseProvider(ABC):
    """
    Abstract base class for LLM providers.
    
    Implement this to add support for any LLM backend.
    The provider handles raw API communication — the Session
    handles identity injection and memory management.
    """
    
    name: str = "base"
    
    @abstractmethod
    def chat(
        self,
        messages: List[Dict[str, str]],
        system: str = "",
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> str:
        """Send a chat completion request and return the response text."""
        ...
    
    @abstractmethod
    async def chat_stream(
        self,
        messages: List[Dict[str, str]],
        system: str = "",
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> AsyncIterator[str]:
        """Stream a chat completion, yielding text chunks."""
        ...
    
    def get_default_model(self) -> str:
        """Return the default model for this provider."""
        return "unknown"
