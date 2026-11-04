"""Topographic: contour lines of imaginary terrain, as on a survey map."""
import numpy as np
from common import hexrgb, mix, fbm, to_image, value_noise

ID = "topo"
NAME = "Topographic"
TAGLINE = "Contour lines of places that do not exist"
DESCRIPTION = ("Contour lines of invented islands, ridges and valleys, drawn like a survey map with "
               "every fifth line heavier. Some sheets tint the land by height.")
FORMAT = "png"

# slug, title, family, paper, line, low tint, high tint (None = no tint), feature, motifs
VARIANTS = [
    ("survey", "Survey", "mono", "#f3efe4", "#7a5a3a", None, None, "hills", ["Brown contours", "Rolling hills"]),
    ("blueprint", "Blueprint", "blue", "#1b3a6b", "#cfe0ff", None, None, "ridge", ["White on blue", "Ridge"]),
    ("archipelago", "Archipelago", "cyan", "#cfe8e8", "#2a5d67", "#cfe8e8", "#e9e1c9", "islands", ["Islands", "Shallows"]),
    ("dune-sea", "Dune Sea", "orange", "#f0d2a8", "#a3532a", None, None, "dunes", ["Dunes", "Long ridges"]),
    ("night-chart", "Night Chart", "green", "#0d1512", "#5fd39a", None, None, "peaks", ["Glow lines", "Peaks"]),
    ("alpine", "Alpine", "mono", "#ffffff", "#3a3a3a", "#e6efe6", "#ffffff", "peaks", ["Glaciers", "Peaks"]),
    ("canyon", "Canyon", "red", "#2a1410", "#e0896a", None, None, "canyon", ["Canyon", "Terraces"]),
    ("moorland", "Moorland", "violet", "#ece6ef", "#6c4f86", "#ece6ef", "#d3c4de", "hills", ["Heather tint"]),
    ("lagoon-chart", "Lagoon Chart", "blue", "#0e2238", "#7fb6d9", "#0e2238", "#1f4a63", "islands", ["Deep water", "Atolls"]),
    ("ochre-plateau", "Ochre Plateau", "yellow", "#e9c46a", "#5b3b12", None, None, "canyon", ["Mesa", "Ochre"]),
]


def terrain(h, w, rng, feature):
    s = min(w, h)
    Y, X = np.mgrid[0:h, 0:w].astype(np.float32)
    base = fbm(h, w, rng, base=s * 0.7, octaves=4, gain=0.42)
    if feature == "hills":
        z = base
    elif feature == "ridge":
        z = 1 - np.abs(fbm(h, w, rng, base=s * 0.9, octaves=4, gain=0.42) * 2 - 1)
        z = z * 0.7 + base * 0.3
    elif feature == "islands":
        z = base
        for _ in range(int(3 + rng.integers(0, 3))):
            cx, cy = rng.random() * w, rng.random() * h
            r = s * (0.12 + 0.15 * rng.random())
            z = z + 0.55 * np.exp(-(((X - cx) ** 2 + (Y - cy) ** 2) / (r * r)))
        z = z - 0.25
    elif feature == "dunes":
        warp = fbm(h, w, rng, base=s * 0.5, octaves=3) * s * 0.4
        ang = rng.random() * np.pi
        u = (X * np.cos(ang) + Y * np.sin(ang) + warp) / (s * 0.09)
        z = (np.sin(u) * 0.5 + 0.5) ** 1.5 * 0.4 + base * 0.6
    elif feature == "peaks":
        z = base ** 2 * 1.4
        for _ in range(int(2 + rng.integers(0, 3))):
            cx, cy = rng.random() * w, rng.random() * h
            r = s * (0.1 + 0.12 * rng.random())
            z = z + 0.7 * np.exp(-np.sqrt((X - cx) ** 2 + (Y - cy) ** 2) / r)
    else:  # canyon / plateau: terraces
        z = base
        z = (z - z.min()) / (z.max() - z.min() + 1e-6)
        q = np.floor(z * 7) / 7
        f = (z - q) * 7
        z = q + (f ** 4) / 7
    z = (z - z.min()) / (z.max() - z.min() + 1e-6)
    return z


def render(w, h, v, rng):
    slug, title, fam, paper, line, low, high, feature, motifs = v
    S = 2
    W, H = w * S, h * S
    z = terrain(H, W, rng, feature)
    paper_c, line_c = hexrgb(paper), hexrgb(line)
    if low is not None:
        img = mix(hexrgb(low), hexrgb(high), np.clip(z, 0, 1)[..., None])
        if feature == "islands":
            water = z < 0.42
            img = np.where(water[..., None], mix(paper_c, line_c, 0.08), img)
    else:
        img = np.ones((H, W, 3), np.float32) * paper_c
    levels = 34
    q = z * levels
    gy, gx = np.gradient(q)
    grad = np.sqrt(gx ** 2 + gy ** 2) + 1e-6
    dist = np.abs(q - np.round(q)) / grad  # distance to nearest contour in pixels
    idx = np.round(q).astype(int)
    width = np.where(idx % 5 == 0, 2.4 * S, 1.0 * S)
    a = np.clip(width / 2 + 0.5 - dist, 0, 1)
    a = a * np.clip(1.6 - grad, 0, 1) * np.clip(grad * 25, 0, 1)  # skip flat areas where lines would merge
    img = mix(img, line_c, a[..., None] * 0.9)
    from PIL import Image
    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).resize((w, h), Image.LANCZOS)
    return im


def colour(v):
    return v[4] if v[2] != "mono" else v[4]
