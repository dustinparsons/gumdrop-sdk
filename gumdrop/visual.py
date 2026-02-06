"""
Gumdrop Visual Identity — IC chip panels and ribbon renders.

Two visual representations of a cartridge:

1. **IC Panel** — A square chip with alphanumeric characters arranged like
   circuit traces. Background hue derived from personality. The public face
   of a cartridge — like an integrated circuit you plug into any system.

2. **Ribbon Panel** — Colored bands of varying width and length, derived
   from trait values. Evokes academic regalia, military ribbons, or the
   colored stripes on a resistor — each band tells you something about
   who this AI is.

Both output SVG for crisp rendering at any size.
"""

import hashlib
import math
from typing import Dict, List, Optional, Tuple


# ─── Color System ───────────────────────────────────────────────

def traits_to_hue(traits: Dict[str, float]) -> float:
    """
    Map personality traits to a dominant hue (0-360).
    
    The mapping is intentional, not random:
    - Warm personalities → warm hues (reds, oranges, golds)
    - Cool/analytical → cool hues (blues, teals)
    - Creative → purples, magentas
    - Balanced → greens
    """
    warmth = traits.get("warmth", 0.5)
    creativity = traits.get("creativity", 0.5)
    formality = traits.get("formality", 0.5)
    humor = traits.get("humor", 0.5)
    
    # Warmth pulls toward red/orange (0-60)
    # Creativity pulls toward purple/magenta (270-330)
    # Formality pulls toward blue (210-240)
    # Humor pulls toward yellow/green (60-120)
    
    # Weighted blend
    hue = (
        warmth * 30 +           # warm → orange
        (1 - formality) * 60 +  # casual → yellow shift
        creativity * 120 +      # creative → purple shift  
        humor * 40              # funny → green shift
    )
    
    # Normalize to 0-360
    hue = hue % 360
    return hue


def traits_to_saturation(traits: Dict[str, float]) -> float:
    """
    More extreme traits → more saturated colors.
    Balanced personalities are muted; strong ones are vivid.
    """
    extremity = 0
    for v in traits.values():
        extremity += abs(v - 0.5) * 2  # 0 at center, 1 at extremes
    extremity /= len(traits) if traits else 1
    return 0.3 + extremity * 0.5  # Range: 0.3 to 0.8


def traits_to_lightness(traits: Dict[str, float]) -> float:
    """Warmth and patience lighten; directness and assertiveness darken."""
    warm = traits.get("warmth", 0.5)
    patience = traits.get("patience", 0.5)
    direct = traits.get("directness", 0.5)
    assertive = traits.get("assertiveness", 0.5)
    
    lightness = 0.35 + (warm + patience - direct - assertive + 1) * 0.1
    return max(0.2, min(0.6, lightness))


def hsl_to_hex(h: float, s: float, l: float) -> str:
    """Convert HSL (h:0-360, s:0-1, l:0-1) to hex color."""
    c = (1 - abs(2 * l - 1)) * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = l - c / 2
    
    if h < 60:
        r, g, b = c, x, 0
    elif h < 120:
        r, g, b = x, c, 0
    elif h < 180:
        r, g, b = 0, c, x
    elif h < 240:
        r, g, b = 0, x, c
    elif h < 300:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x
    
    r, g, b = int((r + m) * 255), int((g + m) * 255), int((b + m) * 255)
    return f"#{r:02x}{g:02x}{b:02x}"


def get_palette(traits: Dict[str, float]) -> Dict[str, str]:
    """Generate a full color palette from traits."""
    hue = traits_to_hue(traits)
    sat = traits_to_saturation(traits)
    light = traits_to_lightness(traits)
    
    return {
        "bg": hsl_to_hex(hue, sat, light),
        "bg_light": hsl_to_hex(hue, sat * 0.6, light + 0.15),
        "fg": hsl_to_hex(hue, sat * 0.3, 0.9),
        "fg_dim": hsl_to_hex(hue, sat * 0.2, 0.7),
        "accent": hsl_to_hex((hue + 180) % 360, sat, 0.5),
        "hue": hue,
        "sat": sat,
        "light": light,
    }


# ─── Character Generation ──────────────────────────────────────

# Characters that look good in monospace on a "chip"
IC_CHARS = "0123456789ABCDEF"
IC_CHARS_EXTENDED = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdef"


def _seed_bytes(name: str, owner_hash: str = "") -> bytes:
    return hashlib.sha256(f"gumdrop:{name}:{owner_hash}".encode()).digest()


def generate_ic_characters(
    name: str,
    owner_hash: str = "",
    grid_size: int = 8,
    charset: str = IC_CHARS,
) -> List[List[str]]:
    """
    Generate the character grid for the IC panel.
    Deterministic based on name + owner hash.
    """
    seed = _seed_bytes(name, owner_hash)
    seed_ints = list(seed) * 4  # extend for larger grids
    
    grid = []
    for y in range(grid_size):
        row = []
        for x in range(grid_size):
            idx = seed_ints[(x * 7 + y * 13 + x * y) % len(seed_ints)] % len(charset)
            row.append(charset[idx])
        grid.append(row)
    return grid


# ─── IC Panel SVG ───────────────────────────────────────────────

def render_ic_panel(
    traits: Dict[str, float],
    name: str,
    voice: str = "",
    owner_hash: str = "",
    grid_size: int = 8,
    cell_size: int = 40,
    padding: int = 20,
    pin_count: int = 8,
) -> str:
    """
    Render an IC chip panel as SVG.
    
    Square chip body with:
    - Alphanumeric characters in a grid (the "circuitry")
    - Hue-mapped background from personality
    - Pin-like notches on edges
    - Name and hash label
    - Corner notch (pin 1 indicator)
    """
    palette = get_palette(traits)
    grid = generate_ic_characters(name, owner_hash, grid_size)
    
    chip_size = grid_size * cell_size
    total_size = chip_size + padding * 2
    pin_width = 8
    pin_length = 16
    
    # SVG dimensions include pins
    svg_w = total_size + pin_length * 2
    svg_h = total_size + pin_length * 2 + 60  # extra for label
    
    chip_x = pin_length + padding
    chip_y = pin_length + padding
    
    parts = []
    parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_w}" height="{svg_h}" viewBox="0 0 {svg_w} {svg_h}">')
    
    # Background
    parts.append(f'<rect width="{svg_w}" height="{svg_h}" fill="#0a0a0a"/>')
    
    # Pins on all four sides
    pin_spacing = chip_size / pin_count
    for i in range(pin_count):
        offset = padding + pin_spacing * (i + 0.5)
        # Top pins
        parts.append(f'<rect x="{pin_length + offset - pin_width/2}" y="{pin_length - pin_length + padding}" '
                     f'width="{pin_width}" height="{pin_length}" fill="{palette["fg_dim"]}" rx="1"/>')
        # Bottom pins
        parts.append(f'<rect x="{pin_length + offset - pin_width/2}" y="{pin_length + padding + chip_size}" '
                     f'width="{pin_width}" height="{pin_length}" fill="{palette["fg_dim"]}" rx="1"/>')
        # Left pins
        parts.append(f'<rect x="{pin_length - pin_length + padding}" y="{pin_length + offset - pin_width/2}" '
                     f'width="{pin_length}" height="{pin_width}" fill="{palette["fg_dim"]}" rx="1"/>')
        # Right pins
        parts.append(f'<rect x="{pin_length + padding + chip_size}" y="{pin_length + offset - pin_width/2}" '
                     f'width="{pin_length}" height="{pin_width}" fill="{palette["fg_dim"]}" rx="1"/>')
    
    # Chip body
    parts.append(f'<rect x="{chip_x}" y="{chip_y}" width="{chip_size}" height="{chip_size}" '
                 f'fill="{palette["bg"]}" rx="4" stroke="{palette["bg_light"]}" stroke-width="2"/>')
    
    # Pin 1 notch (top-left corner)
    notch_r = 8
    parts.append(f'<circle cx="{chip_x + 16}" cy="{chip_y + 16}" r="{notch_r}" '
                 f'fill="{palette["bg_light"]}" opacity="0.6"/>')
    
    # Character grid
    font_size = int(cell_size * 0.55)
    for y, row in enumerate(grid):
        for x, char in enumerate(row):
            cx = chip_x + x * cell_size + cell_size // 2
            cy = chip_y + y * cell_size + cell_size // 2 + font_size // 3
            
            # Vary opacity slightly based on position for depth
            seed = _seed_bytes(name, owner_hash)
            opacity = 0.6 + (seed[(x + y) % 32] % 40) / 100
            
            parts.append(
                f'<text x="{cx}" y="{cy}" font-family="monospace, Courier" '
                f'font-size="{font_size}" fill="{palette["fg"]}" '
                f'text-anchor="middle" opacity="{opacity:.2f}">{char}</text>'
            )
    
    # Subtle grid lines
    for i in range(1, grid_size):
        gx = chip_x + i * cell_size
        gy = chip_y + i * cell_size
        parts.append(f'<line x1="{gx}" y1="{chip_y}" x2="{gx}" y2="{chip_y + chip_size}" '
                     f'stroke="{palette["bg_light"]}" stroke-width="0.5" opacity="0.3"/>')
        parts.append(f'<line x1="{chip_x}" y1="{gy}" x2="{chip_x + chip_size}" y2="{gy}" '
                     f'stroke="{palette["bg_light"]}" stroke-width="0.5" opacity="0.3"/>')
    
    # Label below chip
    label_y = chip_y + chip_size + pin_length + 24
    short_hash = owner_hash[:8] if owner_hash else "00000000"
    voice_short = voice.split(",")[0].strip()[:20] if voice else ""
    
    parts.append(
        f'<text x="{svg_w // 2}" y="{label_y}" font-family="monospace, Courier" '
        f'font-size="14" fill="{palette["fg"]}" text-anchor="middle">'
        f'{name.upper()}</text>'
    )
    parts.append(
        f'<text x="{svg_w // 2}" y="{label_y + 18}" font-family="monospace, Courier" '
        f'font-size="10" fill="{palette["fg_dim"]}" text-anchor="middle">'
        f'{short_hash}</text>'
    )
    
    parts.append('</svg>')
    return "\n".join(parts)


# ─── Ribbon Panel SVG ──────────────────────────────────────────

# Each trait maps to a ribbon color family
RIBBON_HUES = {
    "warmth":       15,    # warm red-orange
    "humor":        50,    # gold/yellow
    "formality":    220,   # navy blue
    "curiosity":    280,   # purple
    "directness":   0,     # red
    "creativity":   310,   # magenta
    "patience":     160,   # teal/green
    "assertiveness": 35,   # amber
}


def render_ribbon_panel(
    traits: Dict[str, float],
    name: str,
    owner_hash: str = "",
    width: int = 300,
    height: int = 400,
    perspective: bool = True,
) -> str:
    """
    Render a 3D ribbon panel as SVG.
    
    Ribbons represent traits:
    - Width = trait value (stronger traits are wider bands)
    - Color = trait-specific hue
    - Saturation = how extreme the value is
    - Length varies slightly for visual interest
    
    The panel evokes academic regalia or military ribbons —
    each band earned, each color meaningful.
    """
    sorted_traits = sorted(traits.items(), key=lambda x: -x[1])
    
    ribbon_area_w = width - 60
    ribbon_area_h = height - 100
    start_y = 50
    
    # Calculate ribbon heights proportional to value
    total_value = sum(v for _, v in sorted_traits) or 1
    
    parts = []
    parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">')
    
    # Dark background panel
    parts.append(f'<rect width="{width}" height="{height}" fill="#0a0a0a" rx="8"/>')
    
    # Panel border (subtle)
    parts.append(f'<rect x="4" y="4" width="{width-8}" height="{height-8}" '
                 f'fill="none" stroke="#222" stroke-width="1" rx="6"/>')
    
    # Name header
    parts.append(
        f'<text x="{width//2}" y="30" font-family="monospace" font-size="12" '
        f'fill="#666" text-anchor="middle" letter-spacing="4">'
        f'{name.upper()}</text>'
    )
    
    # Render ribbons
    y_cursor = start_y
    seed = _seed_bytes(name, owner_hash)
    
    for i, (trait, value) in enumerate(sorted_traits):
        if value < 0.05:
            continue
        
        # Ribbon dimensions
        ribbon_h = max(12, int((value / total_value) * ribbon_area_h * 1.5))
        ribbon_h = min(ribbon_h, 60)  # cap height
        ribbon_w = int(30 + value * (ribbon_area_w - 30))  # width from value
        ribbon_x = (width - ribbon_w) // 2
        
        # Color from trait
        hue = RIBBON_HUES.get(trait, 180)
        sat = 0.4 + abs(value - 0.5) * 0.8
        light = 0.3 + value * 0.25
        
        color = hsl_to_hex(hue, sat, light)
        color_light = hsl_to_hex(hue, sat * 0.8, light + 0.1)
        color_dark = hsl_to_hex(hue, sat, light - 0.1)
        
        # 3D perspective skew (subtle)
        if perspective:
            skew_x = (i - len(sorted_traits) / 2) * 0.3
            transform = f'transform="skewX({skew_x})"'
        else:
            transform = ""
        
        # Ribbon body
        parts.append(f'<g {transform}>')
        
        # Shadow
        parts.append(
            f'<rect x="{ribbon_x + 2}" y="{y_cursor + 2}" '
            f'width="{ribbon_w}" height="{ribbon_h}" '
            f'fill="#000" opacity="0.3" rx="2"/>'
        )
        
        # Main ribbon
        parts.append(
            f'<rect x="{ribbon_x}" y="{y_cursor}" '
            f'width="{ribbon_w}" height="{ribbon_h}" '
            f'fill="{color}" rx="2"/>'
        )
        
        # Highlight stripe (top edge)
        parts.append(
            f'<rect x="{ribbon_x}" y="{y_cursor}" '
            f'width="{ribbon_w}" height="3" '
            f'fill="{color_light}" rx="1" opacity="0.6"/>'
        )
        
        # Trait label (on ribbon if wide enough)
        if ribbon_w > 100 and ribbon_h > 16:
            label = trait[:3].upper()
            val_str = f"{value:.1f}"
            parts.append(
                f'<text x="{ribbon_x + 10}" y="{y_cursor + ribbon_h//2 + 4}" '
                f'font-family="monospace" font-size="10" fill="{color_light}" '
                f'opacity="0.8">{label}</text>'
            )
            parts.append(
                f'<text x="{ribbon_x + ribbon_w - 10}" y="{y_cursor + ribbon_h//2 + 4}" '
                f'font-family="monospace" font-size="9" fill="{color_light}" '
                f'text-anchor="end" opacity="0.6">{val_str}</text>'
            )
        
        parts.append('</g>')
        
        y_cursor += ribbon_h + 4  # gap between ribbons
    
    # Hash footer
    short_hash = owner_hash[:8] if owner_hash else "00000000"
    parts.append(
        f'<text x="{width//2}" y="{height - 16}" font-family="monospace" '
        f'font-size="9" fill="#444" text-anchor="middle">{short_hash}</text>'
    )
    
    parts.append('</svg>')
    return "\n".join(parts)


# ─── Convenience ────────────────────────────────────────────────

def ic_panel_from_cartridge(cartridge, **kwargs) -> str:
    """Generate IC panel SVG from a Cartridge object."""
    return render_ic_panel(
        traits=cartridge.identity.traits,
        name=cartridge.identity.name,
        voice=cartridge.identity.voice,
        owner_hash=cartridge._data.auth.get("owner_hash", ""),
        **kwargs,
    )


def ribbon_panel_from_cartridge(cartridge, **kwargs) -> str:
    """Generate ribbon panel SVG from a Cartridge object."""
    return render_ribbon_panel(
        traits=cartridge.identity.traits,
        name=cartridge.identity.name,
        owner_hash=cartridge._data.auth.get("owner_hash", ""),
        **kwargs,
    )
