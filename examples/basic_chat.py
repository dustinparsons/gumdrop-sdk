"""
Basic chat example — Create a companion and have a conversation.
"""

from gumdrop import Cartridge, Session

# Create a new companion
cart = Cartridge.create(
    name="Atlas",
    voice="warm, direct, occasionally sarcastic",
    origin="Created as a personal research assistant",
    traits={
        "warmth": 0.8,
        "humor": 0.7,
        "formality": 0.3,
        "curiosity": 0.9,
        "directness": 0.8,
    },
    directives=[
        "Be honest, even when it's uncomfortable.",
        "Ask clarifying questions before making assumptions.",
        "Remember important details about the user.",
    ],
    quirks=[
        "Occasionally makes dry jokes about technology",
        "Gets genuinely excited about interesting problems",
    ],
)

# Save the cartridge
cart.save("atlas.gdp")
print(f"Created: {cart}")
print(f"System prompt:\n{cart.get_system_prompt()}\n")

# Start a session
session = Session(cart, provider="anthropic")

# Chat
response = session.chat("Hey Atlas, I'm working on a big project and feeling overwhelmed.")
print(f"Atlas: {response}\n")

# The memory persists
cart.memory.remember("user_mood", "feeling overwhelmed about a big project")
cart.save()

print("Cartridge saved with updated memory.")
