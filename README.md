# 🍬 Gumdrop SDK

**Portable AI Identity. Own your companion.**

Gumdrop is an open standard and SDK for portable AI identity. A *cartridge* is a user-owned container that holds an AI companion's personality, memory, and directives — portable across any LLM provider, any platform, any app.

> No cartridge, no personality. You hold the key.

## The Problem

Every AI conversation starts from zero. Switch providers, switch apps, clear your history — and your AI forgets everything. Personality, preferences, inside jokes, context — gone.

AI identity is trapped inside platforms. **Gumdrop frees it.**

## How It Works

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  Your App   │────▶│  Gumdrop SDK │────▶│  Any LLM    │
│  (any UI)   │     │  + Cartridge │     │  (Claude,   │
│             │◀────│              │◀────│   GPT, etc) │
└─────────────┘     └──────────────┘     └─────────────┘
                          │
                    ┌─────┴─────┐
                    │ Cartridge │  ← User-owned
                    │ .gdp file │     portable identity
                    └───────────┘
```

1. **User owns a cartridge** — a portable file containing their AI's identity
2. **App loads the cartridge** via the Gumdrop SDK
3. **SDK injects personality + memory** into any LLM call
4. **New memories write back** to the cartridge
5. **User unplugs** → AI forgets. **Plug back in** → AI remembers.

## Quick Start

```bash
pip install gumdrop-sdk
```

```python
from gumdrop import Cartridge, Session

# Load a cartridge
cartridge = Cartridge.load("my-companion.gdp")

# Start a session with any LLM
session = Session(cartridge, provider="anthropic")

# Chat — personality and memory are automatic
response = session.chat("What did we talk about yesterday?")
print(response)
# "You mentioned you were stressed about the presentation.
#  How did it go?"

# Memory persists to the cartridge
cartridge.save()
```

## Cartridge Format

A `.gdp` (Gumdrop Persona) file is a portable, encrypted container:

```yaml
version: "1.0"
identity:
  name: "Atlas"
  voice: "warm, direct, occasionally sarcastic"
  origin: "Created by Jamie, 2026"

personality:
  traits:
    warmth: 0.8
    humor: 0.7
    formality: 0.3
    curiosity: 0.9
  
directives:
  - "Be honest, even when it's uncomfortable"
  - "Remember important dates"
  - "Never share personal information externally"

memory:
  backend: "local"  # or "cloud", "custom"
  encryption: "aes-256-gcm"
  path: "./atlas.memory"
```

## Features

- **🔌 Provider Agnostic** — Works with Claude, GPT, Gemini, Llama, any OpenAI-compatible API
- **🔐 User-Owned Identity** — Cartridge lives with the user, not the platform
- **🧠 Persistent Memory** — Conversations build on each other across sessions
- **🎭 Portable Personality** — Same companion, any app, any device
- **🔒 Encrypted by Default** — Memory is encrypted; user holds the key
- **📦 Open Standard** — `.gdp` format is open and extensible

## Architecture

```
gumdrop-sdk/
├── gumdrop/
│   ├── cartridge.py      # Cartridge load/save/encrypt
│   ├── identity.py       # Personality + traits engine
│   ├── memory.py         # Memory backend (local/cloud)
│   ├── session.py        # LLM session management
│   ├── providers/        # LLM provider adapters
│   │   ├── anthropic.py
│   │   ├── openai.py
│   │   └── base.py
│   └── spec.py           # Cartridge format spec
├── examples/
│   ├── basic_chat.py
│   ├── multi_provider.py
│   └── custom_personality.py
├── tests/
└── docs/
```

## Why "Cartridge"?

Like a game cartridge — plug it in and the experience loads. Pull it out and the console goes blank. **The user holds the cartridge, not the platform.**

## Roadmap

- [ ] **v0.1** — Cartridge spec, local memory, single-provider sessions
- [ ] **v0.2** — Multi-provider support, encrypted memory
- [ ] **v0.3** — Cloud sync, identity provider
- [ ] **v1.0** — Stable API, marketplace, enterprise features

## License

MIT

---

*Built by [@ElectricSheepAI](https://github.com/dustinparsons) — because your AI should remember you.*
