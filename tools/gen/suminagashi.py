"""Suminagashi: Japanese floating-ink marbling. Rings of ink dropped on water, then stirred."""
import numpy as np
from common import hexrgb, mix, fbm, grain, to_image, rgbhex

ID = "suminagashi"
NAME = "Suminagashi"
TAGLINE = "Floating ink on water"
DESCRIPTION = ("Rings of ink dropped onto still water and stirred with a breath, then lifted onto "
               "paper. The Japanese marbling technique is older than the European one.")
FORMAT = "jpg"

# slug, title, family, paper, inks (cycled ring colours), swirl strength, motifs
VARIANTS = [
    ("sumi", "Sumi", "mono", "#f1ece1", ["#1b1b1d", "#f1ece1", "#5d5c5a", "#f1ece1"], 1.0, ["Black ink", "Three drops"]),
    ("indigo", "Indigo", "blue", "#efece4", ["#1d2d5c", "#efece4", "#4f6aa6", "#efece4"], 1.2, ["Indigo rings", "Wide stir"]),
    ("beni", "Beni", "red", "#f4ece2", ["#a3202b", "#f4ece2", "#1d1a1a", "#f4ece2"], 0.9, ["Safflower red", "Ink black"]),
    ("matcha", "Matcha", "green", "#eef0e4", ["#4a6b2f", "#eef0e4", "#9bb06a", "#eef0e4"], 1.1, ["Tea green", "Slow swirl"]),
    ("night-pond", "Night Pond", "blue", "#0f1420", ["#d8d3c4", "#0f1420", "#5c7392", "#0f1420"], 1.0, ["Pale ink", "Dark water"]),
    ("kohaku", "Kohaku", "orange", "#f6efe3", ["#d65a1f", "#f6efe3", "#f6efe3", "#2a2421"], 1.3, ["Koi orange", "Two-tone"]),
    ("wisteria", "Wisteria", "violet", "#f2eef3", ["#6b4f8e", "#f2eef3", "#b89cd0", "#f2eef3"], 1.0, ["Wisteria", "Soft rings"]),
    ("rust-tide", "Rust Tide", "red", "#ece3d6", ["#7a321c", "#ece3d6", "#c27b4b", "#2b3a44"], 1.4, ["Rust", "Slate"]),
    ("gold-leaf", "Gold Leaf", "yellow", "#1a1814", ["#c9a245", "#1a1814", "#7d6a3a", "#1a1814"], 1.1, ["Gold ink", "Black lacquer"]),
    ("sea-glass", "Sea Glass", "cyan", "#edf3f1", ["#1f6f72", "#edf3f1", "#7ab8b0", "#edf3f1"], 1.2, ["Teal rings", "Shallow water"]),
]


def render(w, h, v, rng):
    slug, title, fam, paper, inks, swirl, motifs = v
    paper_c = hexrgb(paper)
    ink_cols = [hexrgb(c) for c in inks if c.lower() != paper.lower()]
    s = min(w, h)
    Y, X = np.mgrid[0:h, 0:w].astype(np.float32)

    # the last thing that happened was the stir, so trace it back first
    px = X + (fbm(h, w, rng, base=s * 0.8, octaves=4) - 0.5) * s * 0.55 * swirl
    py = Y + (fbm(h, w, rng, base=s * 0.8, octaves=4) - 0.5) * s * 0.55 * swirl
    px += (fbm(h, w, rng, base=s * 0.2, octaves=3) - 0.5) * s * 0.04 * swirl
    py += (fbm(h, w, rng, base=s * 0.2, octaves=3) - 0.5) * s * 0.04 * swirl

    # drops: a few centres, each gets a series of alternating ink and water drops
    centres = [(rng.uniform(0.05, 0.95) * w, rng.uniform(0.05, 0.95) * h) for _ in range(int(2 + rng.integers(0, 3)))]
    drops = []
    for ci, (cx, cy) in enumerate(centres):
        n = int(44 + rng.integers(0, 30))
        R = s * (0.045 + 0.03 * rng.random())
        for k in range(n):
            is_ink = k % 2 == 0
            r = R * (0.5 if is_ink else 0.9 + 0.5 * rng.random())
            col = ink_cols[(k // 2 + ci) % len(ink_cols)] if is_ink else paper_c
            drops.append((cx, cy, r, col, is_ink))
    # interleave centres a little, as when two people drop ink at once
    order = sorted(range(len(drops)), key=lambda i: i % 7 + rng.random() * 3)
    drops = [drops[i] for i in order]

    img = np.zeros((h, w, 3), np.float32) + paper_c
    open_ = np.ones((h, w), bool)
    ink_mask = np.zeros((h, w), np.float32)
    for cx, cy, r, col, is_ink in reversed(drops):
        dx, dy = px - cx, py - cy
        d2 = dx * dx + dy * dy
        inside = open_ & (d2 < r * r)
        if inside.any():
            img[inside] = col
            if is_ink:
                ink_mask[inside] = 1
            open_ &= ~inside
        f = np.sqrt(np.clip(1 - (r * r) / np.maximum(d2, 1e-6), 0, 1))
        px = np.where(open_, cx + dx * f, px)
        py = np.where(open_, cy + dy * f, py)

    # ink is never perfectly even: slight density changes
    dens = 0.85 + 0.2 * fbm(h, w, rng, base=s * 0.06, octaves=3)
    img = mix(paper_c, img, np.clip(dens, 0, 1)[..., None] * ink_mask[..., None] + (1 - ink_mask[..., None]))
    img = img * (0.975 + 0.04 * fbm(h, w, rng, base=4, octaves=2)[..., None])
    img = grain(img, rng, 3.0)
    return to_image(img)


def colour(v):
    return v[4][0] if v[0] not in ("night-pond", "gold-leaf") else v[4][0]
