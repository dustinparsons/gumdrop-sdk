"""
Gumdrop Session — The bridge between cartridge and LLM.

A session loads identity from a cartridge, injects it into every LLM call,
and writes new memories back to the cartridge.
"""

from typing import Optional, List, Dict
from .cartridge import Cartridge
from .providers.base import BaseProvider
from .providers.anthropic import AnthropicProvider
from .providers.openai import OpenAIProvider
from .providers.lmstudio import LMStudioProvider


PROVIDER_MAP = {
    "anthropic": AnthropicProvider,
    "claude": AnthropicProvider,
    "openai": OpenAIProvider,
    "gpt": OpenAIProvider,
    "lmstudio": LMStudioProvider,
    "local": LMStudioProvider,
}


class Session:
    """
    A conversation session powered by a cartridge and LLM provider.
    
    The session:
    1. Loads identity from the cartridge
    2. Builds system prompt with personality + memory
    3. Manages conversation history
    4. Sends messages to the LLM with identity injected
    5. Extracts and stores new memories
    
    Usage:
        cart = Cartridge.load("companion.gdp")
        session = Session(cart, provider="anthropic")
        
        response = session.chat("Hello!")
        print(response)
        
        # Switch providers mid-conversation
        session.switch_provider("openai")
        response = session.chat("Same conversation, different brain")
    """
    
    def __init__(
        self,
        cartridge: Cartridge,
        provider: str | BaseProvider = "anthropic",
        model: Optional[str] = None,
        **provider_kwargs,
    ):
        self.cartridge = cartridge
        self.history: List[Dict[str, str]] = []
        self._model = model
        
        if isinstance(provider, BaseProvider):
            self._provider = provider
        else:
            provider_cls = PROVIDER_MAP.get(provider.lower())
            if not provider_cls:
                raise ValueError(
                    f"Unknown provider '{provider}'. "
                    f"Available: {', '.join(PROVIDER_MAP.keys())}"
                )
            self._provider = provider_cls(model=model, **provider_kwargs)
    
    def chat(self, message: str) -> str:
        """
        Send a message and get a response.
        Identity and memory are automatically injected.
        """
        # Add user message to history
        self.history.append({"role": "user", "content": message})
        
        # Build system prompt from cartridge
        system = self.cartridge.get_system_prompt()
        
        # Send to LLM
        response = self._provider.chat(
            messages=self.history,
            system=system,
            model=self._model,
        )
        
        # Add assistant response to history
        self.history.append({"role": "assistant", "content": response})
        
        return response
    
    def switch_provider(
        self,
        provider: str | BaseProvider,
        model: Optional[str] = None,
        **provider_kwargs,
    ):
        """
        Switch LLM provider mid-conversation.
        History and identity are preserved — only the brain changes.
        """
        if isinstance(provider, BaseProvider):
            self._provider = provider
        else:
            provider_cls = PROVIDER_MAP.get(provider.lower())
            if not provider_cls:
                raise ValueError(f"Unknown provider '{provider}'")
            self._provider = provider_cls(model=model, **provider_kwargs)
        
        self._model = model
    
    def get_provider_name(self) -> str:
        """Get the current provider name."""
        return self._provider.name
    
    def clear_history(self):
        """Clear conversation history (memory persists in cartridge)."""
        self.history.clear()
    
    def summarize_and_compress(self):
        """
        Compress conversation history by summarizing older messages.
        Keeps recent messages verbatim, summarizes older ones.
        """
        if len(self.history) < 20:
            return
        
        # Keep last 10 messages verbatim
        recent = self.history[-10:]
        older = self.history[:-10]
        
        # Build summary of older messages
        summary_parts = []
        for msg in older:
            role = msg["role"]
            content = msg["content"][:100]
            summary_parts.append(f"[{role}]: {content}...")
        
        summary = "Previous conversation summary:\n" + "\n".join(summary_parts)
        
        # Replace history with summary + recent
        self.history = [
            {"role": "user", "content": summary},
            {"role": "assistant", "content": "I remember our earlier conversation. Let's continue."},
        ] + recent
    
    def __repr__(self) -> str:
        return (
            f"Session(cartridge={self.cartridge!r}, "
            f"provider='{self._provider.name}', "
            f"messages={len(self.history)})"
        )
