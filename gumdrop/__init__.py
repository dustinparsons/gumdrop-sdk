"""
Gumdrop SDK — Portable AI Identity

Own your companion. Any LLM, any platform, one identity.
"""

__version__ = "0.1.0"

from .cartridge import Cartridge
from .session import Session
from .identity import Identity
from .memory import MemoryStore
from .pipeline import Pipeline, Probe

__all__ = ["Cartridge", "Session", "Identity", "MemoryStore", "Pipeline", "Probe"]
