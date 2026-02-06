"""
Gumdrop Thumbprint — Visual identity for cartridges.

A thumbprint is a character matrix generated from a cartridge's personality
traits, name, and owner hash. It serves as:

  1. A visual "fingerprint" — unique to each cartridge
  2. A public introduction — the part you show before sharing the cartridge
  3. An integrity check — if the thumbprint changes, the identity changed

The matrix is deterministic: same cartridge always produces same thumbprint.

Example output:

    ╭──────────────────╮
    │ ▓░▒█▓░▒░▓█▒░▓▒█░ │
    │ ░▒▓░█▒▓█░▒▓░█▒▓░ │
    │ ▒█░▓▒░█▓▒░█▓░▒█▓ │
    │ █▓▒░▓█░▒█▓░▒▓█░▒ │
    │ ░▒█▓░▒▓░█▒▓░▒█▓░ │
    │ ▓░▒█▓░▒░▓█▒░▓▒█░ │
    │                    │
    │  Atlas · warm/direct │
    │  a3f8·curious·sharp  │
    ╰──────────────────╯

The character palette is chosen per-trait. High warmth uses rounder
characters. High directness uses sharper ones. The interplay creates
a texture that's visually distinct per personality.
"""

import hashlib
from typing import Dict, List, Optional, Tuple


# Character palettes mapped to trait dimensions
# Each trait influences which characters appear in the matrix
PALETTES = {
    "warmth": {
        "high": "○◎●◉◍◐◑◒◓",
        "mid":  "·∙•◦∘",
        "low":  "□■▪▫▬▭▮",
    },
    "humor": {
        "high": "~≈∿∾⌇⌁",
        "mid":  "·-—–",
        "low":  "│┃║┊┋",
    },
    "formality": {
        "high": "╋╬╪╫┼┿╀",
        "mid":  "┤├┬┴",
        "low":  "╮╯╰╭",
    },
    "curiosity": {
        "high": "⟐⟑◇◆◈◊⬦⬧",
        "mid":  "△▽▷◁",
        "low":  "▣▤▥▦▧▨",
    },
    "directness": {
        "high": "▶▸►▷→⟶⟹",
        "mid":  "↗↘↙↖",
        "low":  "↺↻⟲⟳∞",
    },
    "creativity": {
        "high": "✦✧★☆⊛⊕⊗",
        "mid":  "⊙⊚⊝⊜",
        "low":  "⊞⊟⊠⊡",
    },
    "patience": {
        "high": "░▒▓█▉▊▋▌",
        "mid":  "▍▎▏",
        "low":  "⚡↯⟐↝",
    },
    "assertiveness": {
        "high": "▲▼◀▶⏏⏩⏪",
        "mid":  "△▽◁▷",
        "low":  "∘∙·。",
    },
}

# Box drawing characters for the frame
FRAME = {
    "tl": "╭", "tr": "╮", "bl": "╰", "br": "╯",
    "h": "─", "v": "│",
}


def _trait_band(value: float) -> str:
    """Map a trait value to high/mid/low band."""
    if value >= 0.7:
        return "high"
    elif value <= 0.3:
        return "low"
    return "mid"


def _hash_bytes(data: str) -> bytes:
    """Get deterministic hash bytes from a string."""
    return hashlib.sha256(data.encode("utf-8")).digest()


def generate_matrix(
    traits: Dict[str, float],
    name: str,
    owner_hash: str = "",
    width: int = 18,
    height: int = 6,
) -> List[str]:
    """
    Generate the character matrix from traits and identity data.
    
    The matrix is built by:
    1. Hashing the name + owner_hash for a seed
    2. Walking through each cell, selecting a character from the
       trait palette that corresponds to that cell's position
    3. The trait used for each column cycles through all traits
    4. The specific character is chosen via the hash seed
    
    Returns a list of strings (one per row).
    """
    # Seed from identity
    seed = _hash_bytes(f"{name}:{owner_hash}")
    seed_ints = list(seed)  # 32 bytes of deterministic randomness
    
    # Build palette for this personality
    trait_names = list(PALETTES.keys())
    active_palettes = []
    for t in trait_names:
        band = _trait_band(traits.get(t, 0.5))
        chars = PALETTES[t][band]
        active_palettes.append(chars)
    
    rows = []
    for y in range(height):
        row = []
        for x in range(width):
            # Which trait palette to use for this cell
            palette_idx = (x + y * 3) % len(active_palettes)
            palette = active_palettes[palette_idx]
            
            # Which character from that palette
            seed_idx = (x * 7 + y * 13 + seed_ints[(x + y) % 32]) % len(palette)
            row.append(palette[seed_idx])
        rows.append("".join(row))
    
    return rows


def generate_label(
    name: str,
    voice: str = "",
    owner_hash: str = "",
) -> List[str]:
    """Generate the text label below the matrix."""
    lines = []
    
    # Name + short voice descriptor
    voice_short = voice.split(",")[0].strip() if voice else ""
    if voice_short:
        lines.append(f" {name} · {voice_short}")
    else:
        lines.append(f" {name}")
    
    # Short hash + dominant traits
    short_hash = owner_hash[:4] if owner_hash else "0000"
    lines.append(f" {short_hash}")
    
    return lines


def render(
    traits: Dict[str, float],
    name: str,
    voice: str = "",
    owner_hash: str = "",
    width: int = 18,
    height: int = 6,
    framed: bool = True,
) -> str:
    """
    Render a complete thumbprint with optional frame.
    
    Returns a multi-line string ready for display.
    """
    matrix = generate_matrix(traits, name, owner_hash, width, height)
    label = generate_label(name, voice, owner_hash)
    
    if not framed:
        return "\n".join(matrix + [""] + label)
    
    # Calculate frame width
    content_width = max(width, max(len(l) for l in label) if label else 0) + 2
    
    lines = []
    # Top border
    lines.append(f"{FRAME['tl']}{FRAME['h'] * content_width}{FRAME['tr']}")
    
    # Matrix rows
    for row in matrix:
        padded = f" {row}".ljust(content_width)
        lines.append(f"{FRAME['v']}{padded}{FRAME['v']}")
    
    # Separator
    lines.append(f"{FRAME['v']}{' ' * content_width}{FRAME['v']}")
    
    # Label rows
    for label_line in label:
        padded = label_line.ljust(content_width)
        lines.append(f"{FRAME['v']}{padded}{FRAME['v']}")
    
    # Bottom border
    lines.append(f"{FRAME['bl']}{FRAME['h'] * content_width}{FRAME['br']}")
    
    return "\n".join(lines)


def from_cartridge(cartridge, **kwargs) -> str:
    """
    Generate a thumbprint directly from a Cartridge object.
    
    Usage:
        from gumdrop.thumbprint import from_cartridge
        print(from_cartridge(cart))
    """
    traits = cartridge.identity.traits
    name = cartridge.identity.name
    voice = cartridge.identity.voice
    owner_hash = cartridge._data.auth.get("owner_hash", "")
    
    return render(
        traits=traits,
        name=name,
        voice=voice,
        owner_hash=owner_hash,
        **kwargs,
    )


def compact(
    traits: Dict[str, float],
    name: str,
    owner_hash: str = "",
    width: int = 12,
    height: int = 3,
) -> str:
    """
    Generate a compact single-line or few-line thumbprint.
    Good for inline display, chat headers, etc.
    
    Example: ◎~╮◆►✦░△ Atlas [a3f8]
    """
    matrix = generate_matrix(traits, name, owner_hash, width, height)
    short_hash = owner_hash[:4] if owner_hash else "0000"
    
    # Take just the first row for ultra-compact
    signature = matrix[0][:width]
    return f"{signature} {name} [{short_hash}]"
