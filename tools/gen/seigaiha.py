"""Seigaiha: the Japanese pattern of overlapping waves, built from rows of concentric arcs."""
import numpy as np
from common import hexrgb, mix, grain, to_image, fbm

ID = "seigaiha"
NAME = "Seigaiha"
TAGLINE = "Blue ocean waves, row on row"
DESCRIPTION = ("Rows of overlapping concentric arcs, a wave pattern known in Japan since the Heian "
               "period. Some carry a moon or a fading tide.")
FORMAT = "png"

# slug, title, family, background, line colour, accent (moon or fade), rings, scale, variant, motifs
VARIANTS = [
    ("kaiyo", "Kaiyo", "blue", "#1f3b6e", "#e9e4d6", None, 4, 1.0, "plain", ["Classic waves"]),
    ("moon-tide", "Moon Tide", "blue", "#0f1a33", "#c8cfdc", "#f2ead2", 5, 0.9, "moon", ["Waves", "Full moon"]),
    ("vermilion", "Vermilion", "red", "#b8322a", "#f4e6d0", None, 4, 1.1, "plain", ["Shrine red"]),
    ("gold-thread", "Gold Thread", "yellow", "#15130f", "#c9a24a", None, 5, 1.05, "plain", ["Gold line", "Lacquer"]),
    ("sakura", "Sakura", "pink", "#f6e3e4", "#c76b7d", None, 4, 1.0, "fade", ["Pale tide"]),
    ("matsu", "Matsu", "green", "#20402f", "#d8dcc5", None, 3, 1.25, "fill", ["Filled waves", "Pine green"]),
    ("dusk-sea", "Dusk Sea", "violet", "#3a2a52", "#f0c7a4", "#f0c7a4", 4, 0.95, "sun", ["Waves", "Setting sun"]),
    ("indigo-dye", "Indigo Dye", "blue", "#24324f", "#9fb0cf", None, 6, 0.8, "dyed", ["Shibori blue"]),
    ("sumi-wave", "Sumi Wave", "mono", "#ece8de", "#1f1f1f", None, 4, 1.15, "fill", ["Ink on paper"]),
    ("teal-current", "Teal Current", "cyan", "#0f4c55", "#bfe2dc", None, 4, 1.0, "fade", ["Teal", "Fading tide"]),
]


def render(w, h, v, rng):
    slug, title, fam, bg, line, accent, rings, scale, kind, motifs = v
    S = 2
    W, H = w * S, h * S
    bg_c, ln_c = hexrgb(bg), hexrgb(line)
    R = min(w, h) * 0.075 * scale * S
    Y, X = np.mgrid[0:H, 0:W].astype(np.float32)
    # rows are R/2 apart, odd rows shifted by R. Later (lower) rows cover earlier ones,
    # so for each pixel the visible scale is the lowest row whose arc covers it.
    row_h = R / 2
    owner_d = np.full((H, W), np.inf, np.float32)
    owner_row = np.full((H, W), -1, np.int32)
    nrows = int(H / row_h) + 3
    for r in range(nrows):
        cy = r * row_h
        off = (r % 2) * R
        cx_idx = np.round((X - off) / (2 * R))
        cx = cx_idx * 2 * R + off
        d = np.sqrt((X - cx) ** 2 + (Y - cy) ** 2)
        cover = (d < R) & (Y <= cy + 1)
        owner_d = np.where(cover, d, owner_d)
        owner_row = np.where(cover, r, owner_row)
    t = owner_d / R  # 0 centre, 1 edge
    ring_pos = t * rings
    frac = ring_pos - np.floor(ring_pos)
    lw = 0.16 if kind != "fill" else 0.34
    ink = (np.abs(frac - 0.5) > 0.5 - lw / 2).astype(np.float32)
    if kind == "fill":
        ink = np.maximum(ink, (t < 1.0 / rings).astype(np.float32))
    ink = np.where(np.isfinite(owner_d), ink, 0)
    # thin outline where a scale sits on the one behind it
    edge = (np.abs(t - 1) < 0.03).astype(np.float32)
    ink = np.maximum(ink, edge)

    img = mix(bg_c, ln_c, ink[..., None])
    # downsample before the slower effects
    from PIL import Image
    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).resize((w, h), Image.LANCZOS)
    img = np.asarray(im, np.float32)
    Y, X = np.mgrid[0:h, 0:w].astype(np.float32)
    if kind == "fade":
        f = np.clip((Y / h - 0.15) / 0.55, 0, 1) ** 1.3
        img = mix(bg_c, img, f[..., None])
    if kind == "dyed":
        n = fbm(h, w, rng, base=min(w, h) * 0.12, octaves=4)
        img = mix(img, bg_c, (np.clip((n - 0.45) * 3, 0, 1) * 0.65)[..., None])
    if kind in ("moon", "sun"):
        ac = hexrgb(accent)
        cx, cy = w * (0.68 if w > h else 0.5), h * (0.3 if w > h else 0.26)
        r = min(w, h) * 0.17
        d = np.sqrt((X - cx) ** 2 + (Y - cy) ** 2)
        disc = np.clip(r - d + 1, 0, 1)
        if kind == "sun":
            # sun sinking behind the waves: only above the horizon line
            hor = h * (0.42 if w > h else 0.36)
            cy = hor
            d = np.sqrt((X - cx) ** 2 + (Y - cy) ** 2)
            disc = np.clip(r - d + 1, 0, 1) * (Y < hor)
            sky = np.clip(1 - Y / hor, 0, 1) * (Y < hor)
            img = np.where((Y < hor)[..., None], mix(bg_c, ac, (0.25 * (1 - sky))[..., None]), img)
            stripes = ((np.floor((hor - Y) / (h * 0.012)) % 3) != 0) | (Y < hor - r * 0.6)
            disc = disc * stripes
        else:
            # moon covers the waves above it, with a dark gap ring
            gap = np.clip(r * 1.06 - d + 1, 0, 1)
            img = mix(img, bg_c, gap[..., None])
        img = mix(img, ac, disc[..., None])
    return to_image(img)


def colour(v):
    return v[3] if v[2] != "mono" else v[4]
