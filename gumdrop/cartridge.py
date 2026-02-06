"""
Gumdrop Cartridge — The portable AI identity container.

A cartridge (.gdp file) is a user-owned, encrypted container holding
an AI companion's personality, memory pointers, and directives.
No cartridge, no personality. The user holds the key.
"""

import json
import hashlib
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field, asdict

from .spec import CARTRIDGE_VERSION, DEFAULT_TRAITS
from .identity import Identity
from .memory import MemoryStore


@dataclass
class CartridgeAuth:
    """Ownership and access tracking"""
    owner_hash: str = ""
    created_at: str = ""
    last_accessed: str = ""
    
    def touch(self):
        self.last_accessed = datetime.now(timezone.utc).isoformat()


@dataclass
class CartridgeData:
    """Raw cartridge data structure"""
    version: str = CARTRIDGE_VERSION
    identity: Dict[str, str] = field(default_factory=lambda: {
        "name": "Companion",
        "voice": "helpful and friendly",
        "origin": "Created with Gumdrop SDK",
    })
    personality: Dict[str, Any] = field(default_factory=lambda: {
        "traits": dict(DEFAULT_TRAITS),
        "quirks": [],
    })
    directives: List[str] = field(default_factory=lambda: [
        "Be helpful and honest.",
        "Maintain the user's privacy.",
    ])
    memory: Dict[str, str] = field(default_factory=lambda: {
        "backend": "local",
        "encryption": "none",
        "path": "",
    })
    auth: Dict[str, str] = field(default_factory=lambda: {
        "owner_hash": "",
        "created_at": "",
        "last_accessed": "",
    })


class Cartridge:
    """
    A portable AI identity container.
    
    Usage:
        # Create a new cartridge
        cart = Cartridge.create("Atlas", voice="warm and direct")
        cart.save("atlas.gdp")
        
        # Load an existing cartridge
        cart = Cartridge.load("atlas.gdp")
        
        # Access identity
        print(cart.identity.name)        # "Atlas"
        print(cart.identity.get_trait("warmth"))  # 0.8
        
        # Access memory
        cart.memory.remember("user_name", "Dustin")
        name = cart.memory.recall("user_name")
    """
    
    def __init__(self, data: CartridgeData, filepath: Optional[Path] = None):
        self._data = data
        self._filepath = Path(filepath) if filepath else None
        self._identity = Identity.from_dict(data.identity, data.personality)
        self._memory: Optional[MemoryStore] = None
        self._signature: Optional[Dict] = None
        self._dirty = False
    
    @classmethod
    def create(
        cls,
        name: str,
        voice: str = "helpful and friendly",
        origin: str = "Created with Gumdrop SDK",
        traits: Optional[Dict[str, float]] = None,
        directives: Optional[List[str]] = None,
        quirks: Optional[List[str]] = None,
    ) -> "Cartridge":
        """Create a new cartridge with the given identity."""
        now = datetime.now(timezone.utc).isoformat()
        owner_hash = hashlib.sha256(secrets.token_bytes(32)).hexdigest()[:16]
        
        merged_traits = dict(DEFAULT_TRAITS)
        if traits:
            merged_traits.update(traits)
        
        data = CartridgeData(
            identity={
                "name": name,
                "voice": voice,
                "origin": origin,
            },
            personality={
                "traits": merged_traits,
                "quirks": quirks or [],
            },
            directives=directives or [
                "Be helpful and honest.",
                "Maintain the user's privacy.",
            ],
            auth={
                "owner_hash": owner_hash,
                "created_at": now,
                "last_accessed": now,
            },
        )
        
        return cls(data)
    
    @classmethod
    def load(cls, filepath: str | Path) -> "Cartridge":
        """Load a cartridge from a .gdp file."""
        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"Cartridge not found: {filepath}")
        
        with open(filepath, "r") as f:
            raw = json.load(f)
        
        data = CartridgeData(
            version=raw.get("version", CARTRIDGE_VERSION),
            identity=raw.get("identity", {}),
            personality=raw.get("personality", {"traits": dict(DEFAULT_TRAITS), "quirks": []}),
            directives=raw.get("directives", []),
            memory=raw.get("memory", {"backend": "local", "encryption": "none", "path": ""}),
            auth=raw.get("auth", {}),
        )
        
        # Touch access time
        data.auth["last_accessed"] = datetime.now(timezone.utc).isoformat()
        
        cart = cls(data, filepath)
        
        # Load signature if present
        cart._signature = raw.get("signature", None)
        
        return cart
    
    def sign(self, keypair) -> "Cartridge":
        """
        Sign the cartridge with a keypair.
        
        The signature covers identity, personality, and directives.
        Memory is NOT signed (it changes over time).
        The public key becomes part of the cartridge — it's what
        generates the IC panel visual.
        
        Usage:
            from gumdrop.keyring import Keyring
            kr = Keyring()
            kp = kr.generate()
            cart.sign(kp).save("signed.gdp")
        """
        from .keyring import Signer
        sig_block = Signer.sign(asdict(self._data), keypair)
        self._data.auth["owner_hash"] = keypair.fingerprint
        self._data.auth["public_key"] = keypair.public_key.hex()
        self._signature = sig_block
        self._dirty = True
        return self  # chainable
    
    def verify(self, keypair=None) -> bool:
        """
        Verify the cartridge signature.
        
        Without keypair: structural check only.
        With keypair: full cryptographic verification.
        """
        if not hasattr(self, "_signature") or not self._signature:
            return False
        from .keyring import Signer
        if keypair:
            return Signer.verify_with_key(asdict(self._data), self._signature, keypair)
        return Signer.verify(asdict(self._data), self._signature)
    
    @property
    def is_signed(self) -> bool:
        """Check if this cartridge has been signed."""
        return hasattr(self, "_signature") and bool(self._signature)
    
    @property
    def public_key_hex(self) -> str:
        """Get the public key if signed, or empty string."""
        return self._data.auth.get("public_key", "")

    def save(self, filepath: Optional[str | Path] = None):
        """Save cartridge to a .gdp file."""
        target = Path(filepath) if filepath else self._filepath
        if not target:
            raise ValueError("No filepath specified. Use save('path.gdp')")
        
        self._filepath = target
        self._data.auth["last_accessed"] = datetime.now(timezone.utc).isoformat()
        
        # Set memory path relative to cartridge
        if not self._data.memory.get("path"):
            self._data.memory["path"] = str(target.with_suffix(".memory"))
        
        output = asdict(self._data)
        
        # Include signature if present
        if hasattr(self, "_signature") and self._signature:
            output["signature"] = self._signature
        
        with open(target, "w") as f:
            json.dump(output, f, indent=2)
        
        # Save memory if loaded
        if self._memory:
            self._memory.save()
        
        self._dirty = False
    
    @property
    def identity(self) -> Identity:
        """Access the cartridge's identity."""
        return self._identity
    
    @property
    def memory(self) -> MemoryStore:
        """Access the cartridge's memory store."""
        if self._memory is None:
            memory_path = self._data.memory.get("path", "")
            if memory_path:
                self._memory = MemoryStore(Path(memory_path))
            else:
                self._memory = MemoryStore()
        return self._memory
    
    @property
    def directives(self) -> List[str]:
        """Get the cartridge's core directives."""
        return self._data.directives
    
    @directives.setter
    def directives(self, value: List[str]):
        self._data.directives = value
        self._dirty = True
    
    def get_system_prompt(self) -> str:
        """
        Generate a complete system prompt from the cartridge.
        This is injected into every LLM call to maintain identity.
        """
        parts = []
        
        # Identity
        parts.append(f"You are {self._identity.name}.")
        if self._identity.voice:
            parts.append(f"Your communication style: {self._identity.voice}")
        if self._identity.origin:
            parts.append(f"Background: {self._identity.origin}")
        
        # Personality traits
        trait_desc = self._identity.describe_traits()
        if trait_desc:
            parts.append(f"\nPersonality: {trait_desc}")
        
        # Quirks
        quirks = self._data.personality.get("quirks", [])
        if quirks:
            parts.append("\nQuirks:")
            for q in quirks:
                parts.append(f"- {q}")
        
        # Directives
        if self._data.directives:
            parts.append("\nCore directives:")
            for d in self._data.directives:
                parts.append(f"- {d}")
        
        # Memory context
        if self._memory and self._memory.has_memories():
            parts.append("\nWhat you remember about the user:")
            for fact in self._memory.get_recent_facts(limit=20):
                parts.append(f"- {fact}")
        
        return "\n".join(parts)
    
    def __repr__(self) -> str:
        return f"Cartridge(name='{self._identity.name}', version='{self._data.version}')"
