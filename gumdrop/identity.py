"""
Gumdrop Identity — Personality traits and voice.

Converts trait values (0.0-1.0) into natural language descriptions
that get injected into LLM system prompts.
"""

from typing import Dict, Any, Optional, List
from .spec import DEFAULT_TRAITS, TRAIT_DESCRIPTIONS


class Identity:
    """
    Represents an AI companion's personality and voice.
    
    Traits are floats from 0.0 to 1.0:
      - 0.0-0.3: Low (opposite end of spectrum)
      - 0.3-0.7: Moderate (balanced)
      - 0.7-1.0: High (strong expression)
    """
    
    def __init__(
        self,
        name: str,
        voice: str = "",
        origin: str = "",
        traits: Optional[Dict[str, float]] = None,
        quirks: Optional[List[str]] = None,
    ):
        self.name = name
        self.voice = voice
        self.origin = origin
        self.traits = traits or dict(DEFAULT_TRAITS)
        self.quirks = quirks or []
    
    @classmethod
    def from_dict(cls, identity_dict: Dict[str, str], personality_dict: Dict[str, Any]) -> "Identity":
        """Create an Identity from cartridge data dicts."""
        return cls(
            name=identity_dict.get("name", "Companion"),
            voice=identity_dict.get("voice", ""),
            origin=identity_dict.get("origin", ""),
            traits=personality_dict.get("traits", dict(DEFAULT_TRAITS)),
            quirks=personality_dict.get("quirks", []),
        )
    
    def get_trait(self, trait: str) -> float:
        """Get a trait value (0.0-1.0)."""
        return self.traits.get(trait, 0.5)
    
    def set_trait(self, trait: str, value: float):
        """Set a trait value (clamped to 0.0-1.0)."""
        self.traits[trait] = max(0.0, min(1.0, value))
    
    def describe_traits(self) -> str:
        """Generate natural language description of personality."""
        descriptions = []
        
        for trait, value in self.traits.items():
            if trait not in TRAIT_DESCRIPTIONS:
                continue
            
            desc = TRAIT_DESCRIPTIONS[trait]
            if value >= 0.7:
                descriptions.append(desc["high"])
            elif value <= 0.3:
                descriptions.append(desc["low"])
            # Moderate values (0.3-0.7) are omitted — they're unremarkable
        
        if not descriptions:
            return "balanced and adaptable"
        
        return "; ".join(descriptions)
    
    def __repr__(self) -> str:
        return f"Identity(name='{self.name}')"
