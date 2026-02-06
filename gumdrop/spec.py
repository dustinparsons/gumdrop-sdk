"""
Gumdrop Cartridge Specification v1.0

The .gdp (Gumdrop Persona) format defines the portable container
for AI identity. This module defines the schema and validation.
"""

CARTRIDGE_VERSION = "1.0"

# The cartridge schema
SCHEMA = {
    "version": str,          # Spec version
    "identity": {
        "name": str,         # Display name
        "voice": str,        # Natural language description of communication style
        "origin": str,       # Creation context / backstory
    },
    "personality": {
        "traits": {          # 0.0 to 1.0 scale
            "warmth": float,
            "humor": float,
            "formality": float,
            "curiosity": float,
            "directness": float,
            "creativity": float,
            "patience": float,
            "assertiveness": float,
        },
        "quirks": list,      # Unique behavioral notes
    },
    "directives": list,      # Core rules the AI must follow
    "memory": {
        "backend": str,      # "local" | "cloud" | "custom"
        "encryption": str,   # Encryption algorithm
        "path": str,         # Path to memory store (relative to cartridge)
    },
    "auth": {
        "owner_hash": str,   # Hash of owner's identity
        "created_at": str,   # ISO 8601 timestamp
        "last_accessed": str, # ISO 8601 timestamp
    },
}

# Default trait values for a balanced personality
DEFAULT_TRAITS = {
    "warmth": 0.6,
    "humor": 0.5,
    "formality": 0.5,
    "curiosity": 0.7,
    "directness": 0.6,
    "creativity": 0.6,
    "patience": 0.7,
    "assertiveness": 0.5,
}

# Trait descriptions for system prompt generation
TRAIT_DESCRIPTIONS = {
    "warmth": {
        "high": "warm, empathetic, and caring in responses",
        "low": "cool, detached, and matter-of-fact",
    },
    "humor": {
        "high": "witty, playful, uses humor naturally",
        "low": "serious, focused, rarely jokes",
    },
    "formality": {
        "high": "polished, professional, proper grammar",
        "low": "casual, conversational, uses slang",
    },
    "curiosity": {
        "high": "asks follow-up questions, explores tangents",
        "low": "stays on topic, answers directly",
    },
    "directness": {
        "high": "blunt, honest, doesn't sugarcoat",
        "low": "diplomatic, gentle, softens hard truths",
    },
    "creativity": {
        "high": "imaginative, makes unexpected connections",
        "low": "practical, conventional, by-the-book",
    },
    "patience": {
        "high": "thorough, explains step by step, never rushes",
        "low": "concise, assumes understanding, moves fast",
    },
    "assertiveness": {
        "high": "opinionated, takes strong positions, pushes back",
        "low": "agreeable, accommodating, follows the user's lead",
    },
}
