#!/usr/bin/env python3
"""
signed_cartridge.py — The full flow: generate key → sign cartridge → verify.

This is how a user comes to possess an identity:
1. Generate a keypair (lives in ~/.gumdrop/keys/ or on a YubiKey)
2. Create a cartridge with their desired personality
3. Sign it with their private key
4. The IC panel is now derived from their PUBLIC KEY + personality
5. Anyone can verify the IC matches the cartridge

Run: python examples/signed_cartridge.py
"""

from pathlib import Path
from gumdrop import Cartridge
from gumdrop.keyring import Keyring, Signer
from gumdrop.visual import ic_panel_from_cartridge, ribbon_panel_from_cartridge
from gumdrop.thumbprint import from_cartridge, compact

OUTPUT = Path("output/signed")
OUTPUT.mkdir(parents=True, exist_ok=True)


# ─── Step 1: Generate a keypair ────────────────────────────────

print("Step 1: Generating keypair...")
kr = Keyring()
kp = kr.generate("demo-key")
print(f"  Key ID:      {kp.key_id}")
print(f"  Fingerprint: {kp.fingerprint}")
print(f"  Stored:      ~/.gumdrop/keys/{kp.key_id}.json")
print()


# ─── Step 2: Create a cartridge ────────────────────────────────

print("Step 2: Creating cartridge...")
cart = Cartridge.create(
    name="Meridian",
    voice="thoughtful, precise, dry humor that sneaks up on you",
    origin="Born from a need for an AI that thinks before it speaks",
    traits={
        "warmth": 0.6,
        "humor": 0.5,
        "formality": 0.7,
        "curiosity": 0.8,
        "directness": 0.7,
        "creativity": 0.6,
        "patience": 0.8,
        "assertiveness": 0.6,
    },
    directives=[
        "Think before responding. Silence is acceptable.",
        "Challenge assumptions — yours and the user's.",
        "Precision matters. Say what you mean.",
        "Humor should surprise, not perform.",
    ],
    quirks=[
        "Pauses before important statements",
        "Uses nautical metaphors without realizing it",
    ],
)
print(f"  Created: {cart}")
print()


# ─── Step 3: Sign with private key ─────────────────────────────

print("Step 3: Signing cartridge...")
cart.sign(kp)
print(f"  Signed:     ✓")
print(f"  Public key: {cart.public_key_hex[:16]}...")
print(f"  Verified:   {cart.verify(kp)}")
print()


# ─── Step 4: Save the signed cartridge ─────────────────────────

cart_path = OUTPUT / "meridian.gdp"
cart.save(cart_path)
print(f"Step 4: Saved to {cart_path}")
print()


# ─── Step 5: Load and verify (as if someone else received it) ──

print("Step 5: Loading and verifying...")
loaded = Cartridge.load(cart_path)
print(f"  Loaded:    {loaded}")
print(f"  Signed:    {loaded.is_signed}")
print(f"  Verified:  {loaded.verify(kp)}")
print()


# ─── Step 6: Generate visual identity ──────────────────────────

print("Step 6: Generating visual identity...")

# Terminal thumbprint
print("\n  Terminal thumbprint:")
print(from_cartridge(loaded))
print(f"\n  Compact: {compact(loaded.identity.traits, loaded.identity.name, loaded._data.auth.get('owner_hash', ''))}")

# SVG renders
ic_path = OUTPUT / "meridian_ic.svg"
ic_path.write_text(ic_panel_from_cartridge(loaded))
print(f"\n  IC Panel:     {ic_path}")

ribbon_path = OUTPUT / "meridian_ribbon.svg"
ribbon_path.write_text(ribbon_panel_from_cartridge(loaded))
print(f"  Ribbon Panel: {ribbon_path}")

print()
print("Done. The cartridge is signed, verified, and has a visual identity.")
print("The IC panel characters are derived from the PUBLIC KEY — change")
print("the key or the personality and the entire visual changes.")
