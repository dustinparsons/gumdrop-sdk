#!/usr/bin/env python3
"""
thumbprints.py — Visualize cartridge identities.

Each cartridge gets a unique visual fingerprint based on its personality.
No two cartridges look the same (unless they have identical traits + name + owner).

Run: python examples/thumbprints.py
"""

from gumdrop import Cartridge
from gumdrop.thumbprint import from_cartridge, compact


def show(cart):
    """Display a cartridge's thumbprint."""
    print(from_cartridge(cart))
    print(f"  compact: {compact(cart.identity.traits, cart.identity.name, cart._data.auth.get('owner_hash', ''))}")
    print()


# A warm, curious companion
atlas = Cartridge.create(
    name="Atlas",
    voice="warm, direct, occasionally sarcastic",
    traits={
        "warmth": 0.9,
        "humor": 0.7,
        "formality": 0.2,
        "curiosity": 0.95,
        "directness": 0.8,
        "creativity": 0.8,
        "patience": 0.6,
        "assertiveness": 0.5,
    },
)

# A cold, precise analyst
scalpel = Cartridge.create(
    name="Scalpel",
    voice="clinical, precise, no wasted words",
    traits={
        "warmth": 0.1,
        "humor": 0.1,
        "formality": 0.9,
        "curiosity": 0.4,
        "directness": 0.95,
        "creativity": 0.3,
        "patience": 0.2,
        "assertiveness": 0.9,
    },
)

# A chaotic creative
jester = Cartridge.create(
    name="Jester",
    voice="chaotic, playful, stream of consciousness",
    traits={
        "warmth": 0.6,
        "humor": 0.95,
        "formality": 0.05,
        "curiosity": 0.8,
        "directness": 0.3,
        "creativity": 0.95,
        "patience": 0.3,
        "assertiveness": 0.4,
    },
)

# A patient teacher
sage = Cartridge.create(
    name="Sage",
    voice="patient, methodical, genuinely caring",
    traits={
        "warmth": 0.8,
        "humor": 0.4,
        "formality": 0.6,
        "curiosity": 0.7,
        "directness": 0.5,
        "creativity": 0.5,
        "patience": 0.95,
        "assertiveness": 0.3,
    },
)

print("=" * 40)
print("  CARTRIDGE THUMBPRINTS")
print("=" * 40)
print()

for cart in [atlas, scalpel, jester, sage]:
    show(cart)
