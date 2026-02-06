#!/usr/bin/env python3
"""
visual_identity.py — Generate IC chip panels and ribbon panels for cartridges.

Outputs SVG files you can view in any browser.

Run: python examples/visual_identity.py
Then: open output/  (or browse the SVG files)
"""

from pathlib import Path
from gumdrop import Cartridge
from gumdrop.visual import ic_panel_from_cartridge, ribbon_panel_from_cartridge, get_palette

OUTPUT = Path("output/visual")
OUTPUT.mkdir(parents=True, exist_ok=True)


PERSONAS = {
    "atlas": {
        "name": "Atlas",
        "voice": "warm, direct, occasionally sarcastic",
        "traits": {
            "warmth": 0.9, "humor": 0.7, "formality": 0.2,
            "curiosity": 0.95, "directness": 0.8, "creativity": 0.8,
            "patience": 0.6, "assertiveness": 0.5,
        },
    },
    "scalpel": {
        "name": "Scalpel",
        "voice": "clinical, precise, no wasted words",
        "traits": {
            "warmth": 0.1, "humor": 0.1, "formality": 0.9,
            "curiosity": 0.4, "directness": 0.95, "creativity": 0.3,
            "patience": 0.2, "assertiveness": 0.9,
        },
    },
    "jester": {
        "name": "Jester",
        "voice": "chaotic, playful, stream of consciousness",
        "traits": {
            "warmth": 0.6, "humor": 0.95, "formality": 0.05,
            "curiosity": 0.8, "directness": 0.3, "creativity": 0.95,
            "patience": 0.3, "assertiveness": 0.4,
        },
    },
    "sage": {
        "name": "Sage",
        "voice": "patient, methodical, genuinely caring",
        "traits": {
            "warmth": 0.8, "humor": 0.4, "formality": 0.6,
            "curiosity": 0.7, "directness": 0.5, "creativity": 0.5,
            "patience": 0.95, "assertiveness": 0.3,
        },
    },
}


for key, persona in PERSONAS.items():
    cart = Cartridge.create(**persona)
    palette = get_palette(persona["traits"])
    
    # IC Panel
    ic_svg = ic_panel_from_cartridge(cart)
    ic_path = OUTPUT / f"{key}_ic.svg"
    ic_path.write_text(ic_svg)
    
    # Ribbon Panel
    ribbon_svg = ribbon_panel_from_cartridge(cart)
    ribbon_path = OUTPUT / f"{key}_ribbon.svg"
    ribbon_path.write_text(ribbon_svg)
    
    print(f"{persona['name']:10s} hue={palette['hue']:5.1f}° bg={palette['bg']}  → {ic_path}, {ribbon_path}")


# Also generate an HTML gallery
html = ['<!DOCTYPE html><html><head><title>Gumdrop Visual Identity</title>']
html.append('<style>')
html.append('body { background: #0a0a0a; color: #ccc; font-family: monospace; padding: 40px; }')
html.append('h1 { color: #fff; letter-spacing: 4px; }')
html.append('.row { display: flex; gap: 40px; margin: 30px 0; align-items: flex-start; }')
html.append('.card { text-align: center; }')
html.append('.card h3 { color: #888; letter-spacing: 2px; margin-top: 12px; }')
html.append('</style></head><body>')
html.append('<h1>GUMDROP · VISUAL IDENTITY</h1>')
html.append('<p>Each cartridge generates a unique IC chip panel and ribbon badge from its personality traits.</p>')

for key, persona in PERSONAS.items():
    html.append(f'<h2 style="color:#fff;margin-top:40px">{persona["name"]}</h2>')
    html.append(f'<p style="color:#666">{persona["voice"]}</p>')
    html.append('<div class="row">')
    html.append(f'<div class="card"><img src="{key}_ic.svg"><h3>IC PANEL</h3></div>')
    html.append(f'<div class="card"><img src="{key}_ribbon.svg"><h3>RIBBONS</h3></div>')
    html.append('</div>')

html.append('</body></html>')
(OUTPUT / "gallery.html").write_text("\n".join(html))
print(f"\nGallery: {OUTPUT / 'gallery.html'}")
print("Open in browser to see the visual identities.")
