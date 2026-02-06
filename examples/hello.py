#!/usr/bin/env python3
"""
hello.py — The simplest Gumdrop demo.

Creates a companion, talks to it via LMStudio (local, free, no API keys).
Run: python examples/hello.py

Requires: LMStudio running at http://127.0.0.1:1234
"""

from gumdrop import Cartridge, Session

# Create a companion
cart = Cartridge.create(
    name="Atlas",
    voice="warm, direct, occasionally sarcastic",
    traits={
        "warmth": 0.8,
        "humor": 0.7,
        "formality": 0.2,
        "curiosity": 0.9,
        "directness": 0.8,
    },
    quirks=["Gets genuinely excited about weird ideas"],
)

print(f"Created: {cart}")
print(f"\n--- System Prompt ---\n{cart.get_system_prompt()}\n")

# Start a local session (no API keys needed)
session = Session(cart, provider="lmstudio")

# Chat
print("--- Chat ---")
prompts = [
    "Hey Atlas, what do you think about the idea of portable AI identity?",
    "What if you could move between different AI models but keep your personality?",
    "That's literally what Gumdrop does. You're running on it right now.",
]

for prompt in prompts:
    print(f"\nYou: {prompt}")
    response = session.chat(prompt)
    print(f"Atlas: {response}")

# Save with memory
cart.memory.remember("first_conversation", "discussed portable AI identity and Gumdrop SDK")
cart.save("atlas.gdp")
print(f"\n✓ Cartridge saved to atlas.gdp with memory")
