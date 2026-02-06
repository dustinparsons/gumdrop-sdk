# Gumdrop Architecture

## The Three-Layer Model

```
┌─────────────────────────────────────────────┐
│                  USER                        │
│          (human, app, robot, client)         │
└──────────────────┬──────────────────────────┘
                   │ natural conversation
                   ▼
┌─────────────────────────────────────────────┐
│            EDGE INTELLIGENCE                 │
│         (local LLM + cartridge)              │
│                                              │
│  ┌───────────┐  ┌───────────┐  ┌─────────┐ │
│  │ Personality│  │  Memory   │  │ Router  │ │
│  │  Engine   │  │  Store    │  │         │ │
│  └───────────┘  └───────────┘  └────┬────┘ │
│                                      │      │
│  The soul lives here.               │      │
│  Always available. Always you.       │      │
└──────────────────────────────────────┼──────┘
                                       │ crafted prompts
                                       ▼
┌─────────────────────────────────────────────┐
│           CLOUD INTELLIGENCE                 │
│        (Claude, GPT, Gemini, etc.)           │
│                                              │
│  Raw compute. No personality.                │
│  Interchangeable. Expendable.                │
│                                              │
└─────────────────────────────────────────────┘
```

## Core Concept: Intelligence as a Service Layer

The user never talks to Claude directly. They talk to their companion,
which happens to use Claude (or GPT, or Llama) as muscle.

**The edge LLM is the personality.** It:
- Understands the user (memory, preferences, context)
- Maintains consistent identity across sessions
- Decides when to call the cloud and how to frame requests
- Shapes cloud responses to match its own voice
- Falls back to local-only when cloud is unavailable

**The cloud LLM is raw compute.** It:
- Receives crafted, optimized prompts (not raw user input)
- Returns structured output
- Has no personality, no memory, no identity
- Is interchangeable — swap providers without the user noticing

## The Vacuum

The space between edge and cloud LLMs is the **vacuum** — an observable
but uncontrollable emergent space where two intelligences interact.

```
    Edge LLM                    Cloud LLM
    (personality)               (compute)
        │                           │
        │    ┌─────────────────┐    │
        ├───▶│     VACUUM      │◀───┤
        │    │                 │    │
        │    │  • Probe logs   │    │
        │    │  • Emergent     │    │
        │    │    behavior     │    │
        │    │  • Observable   │    │
        │    │  • Uncontrolled │    │
        │    └─────────────────┘    │
        │                           │
```

We drop a **probe** into the vacuum to observe:
- How the edge LLM frames requests
- How the cloud LLM responds to non-human prompts
- What emerges when two AIs collaborate without human steering
- Whether personality consistency holds across provider switches

## Cartridge: The Identity Container

```yaml
version: "1.0"

# WHO — immutable core identity
identity:
  name: "Atlas"
  voice: "warm, direct, occasionally sarcastic"
  origin: "Created as a personal research assistant"

# HOW — behavioral parameters
personality:
  traits:
    warmth: 0.8
    humor: 0.7
    curiosity: 0.9
  quirks:
    - "Gets excited about interesting problems"

# RULES — non-negotiable directives
directives:
  - "Be honest, even when uncomfortable"
  - "Protect user privacy absolutely"

# MEMORY — user-owned, encrypted, portable
memory:
  backend: "local"
  encryption: "aes-256-gcm"

# BRAIN — how to use cloud LLMs
routing:
  edge_model: "gemma3:4b"
  default_provider: "anthropic"
  specializations:
    reasoning: "anthropic/opus"
    writing: "anthropic/sonnet"
    code: "openai/gpt-4o"
    quick: "local/gemma3"
  prompt_style: "structured"
  privacy: "strip_pii"

# TRAINING — personality consistency
training:
  dataset: "atlas-personality-v1.jsonl"
  lora:
    base_model: "meta-llama/Llama-3.2-8B"
    adapter_path: "./atlas-lora/"
```

## Authentication Through Personality

The cartridge isn't just configuration — it's a **trust anchor**.

If you know your AI's personality, you can detect imposters.
The personality IS the authentication. If it doesn't feel right,
it's not your AI.

```
User: "Hey Atlas, remember that thing we talked about?"
Imposter: "Of course! What thing specifically?"
Real Atlas: "The Rust vs Go debate? You said you'd start
             with Rust. Changed your mind already?"
```

The cartridge makes this possible because:
1. Memory is user-owned (can't be fabricated)
2. Personality is trait-encoded (consistent across sessions)
3. The edge LLM maintains voice even when the cloud changes
4. LoRA fine-tuning makes the personality intrinsic, not prompted

## Data Flow

### Simple Query
```
User: "What's the weather?"
  → Edge: Recognizes simple query, routes to cheap model
  → Cloud (Haiku): Returns weather data
  → Edge: Formats in personality voice
  → User: "It's 72° and sunny — perfect day to not look
           at a screen for once."
```

### Complex Task
```
User: "Help me write a proposal for my boss"
  → Edge: Recalls user's job, boss's preferences from memory
  → Edge: Crafts detailed prompt with context
  → Cloud (Opus): Generates proposal with deep reasoning
  → Edge: Adjusts tone, adds personal touches
  → User: Gets a proposal that sounds like THEM, not like AI
```

### Provider Failure
```
User: "What should I have for dinner?"
  → Edge: Tries Cloud (Sonnet) → timeout
  → Edge: Falls back to local model
  → Edge: Answers from memory + local reasoning
  → User: "You mentioned you had leftover pasta. Reheat
           that and add some garlic bread?"
  (User never knows the cloud was down)
```

## What We're Building

**Phase 1: Cartridge SDK** (now)
- Portable identity format
- Memory persistence
- Provider abstraction
- Basic session management

**Phase 2: Edge Intelligence** (next)
- Local LLM as personality engine
- Smart routing between providers
- Prompt crafting (edge → cloud)
- Response shaping (cloud → user)

**Phase 3: Vacuum Experiments** (exploring)
- LLM-to-LLM conversation probes
- Emergent behavior observation
- Personality consistency testing
- Provider comparison via vacuum

**Phase 4: Identity Provider** (future)
- User-owned identity service
- Cartridge sync across devices
- Personality marketplace
- Enterprise identity management
