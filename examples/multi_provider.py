"""
Multi-provider example — Same identity, different LLM brains.

Demonstrates the core Gumdrop value prop: switch providers
mid-conversation without losing personality or context.
"""

from gumdrop import Cartridge, Session

# Load existing cartridge
cart = Cartridge.load("atlas.gdp")
print(f"Loaded: {cart}")

# Start with Claude
session = Session(cart, provider="anthropic")
print(f"\n--- Using {session.get_provider_name()} ---")

response = session.chat("What's the best approach to learning Rust?")
print(f"Atlas: {response}\n")

# Switch to GPT mid-conversation — identity preserved
session.switch_provider("openai")
print(f"--- Switched to {session.get_provider_name()} ---")

response = session.chat("How does that compare to learning Go?")
print(f"Atlas: {response}\n")

# Switch to local model (Ollama) — still the same Atlas
session.switch_provider(
    "openai",
    base_url="http://localhost:11434/v1",
    api_key="ollama",
    model="llama3.2",
)
print(f"--- Switched to local Ollama ---")

response = session.chat("Which would you recommend I start with?")
print(f"Atlas: {response}\n")

print(f"Total messages: {len(session.history)}")
print("Same personality across 3 different LLMs ✓")
