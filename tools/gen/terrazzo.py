"""Terrazzo: chips of stone and glass set in a polished binder, the Venetian floor."""
import numpy as np
import common
from PIL import Image, ImageDraw
from common import hexrgb, mix, fbm, grain, to_image, col

ID = "terrazzo"
NAME = "Terrazzo"
TAGLINE = "Stone chips in polished binder"
DESCRIPTION = ("Broken marble, granite and glass set in a cement binder and ground smooth, the "
               "flooring of Venetian palazzi and Italian railway stations.")
FORMAT = "jpg"

# slug, title, family, binder, chip colours, chip density, motifs
VARIANTS = [
    ("venetian", "Venetian", "red", "#ece6dc", ["#b2533e", "#d9a07a", "#3a3532", "#f6f3ee", "#8a8580"], 1.0, ["Red marble", "Grey granite"]),
    ("forest-floor", "Forest Floor", "green", "#2c3b31", ["#d9d3c4", "#8aa17a", "#c48a4d", "#55705a", "#f0ebe0"], 1.0, ["Green binder", "Sand chips"]),
    ("pastel", "Pastel", "pink", "#f6efe9", ["#f2b8b0", "#a8c9d6", "#f5d38b", "#b9d3b0", "#e9e2da"], 0.9, ["Sugar chips", "Light binder"]),
    ("midnight", "Midnight", "blue", "#151a26", ["#d4cfc4", "#c6a15b", "#5d6f8e", "#9aa4b5", "#2c3550"], 1.1, ["Brass flecks", "Night binder"]),
    ("sorbet", "Sorbet", "orange", "#fbe3cf", ["#f07b3f", "#ffcf8b", "#e04f5f", "#f7f1e8", "#7d3c3c"], 1.0, ["Orange", "Raspberry"]),
    ("olive-grove", "Olive Grove", "green", "#d8d2bc", ["#6c7341", "#a6a06a", "#3f3a2a", "#f2efe3", "#b88b5b"], 1.0, ["Olive", "Bark"]),
    ("rosso", "Rosso", "red", "#8f2f28", ["#f0e1cf", "#d98a6c", "#3b1512", "#c45c47", "#ffffff"], 0.9, ["Red binder", "Cream chips"]),
    ("glacier", "Glacier", "cyan", "#e7eef0", ["#7fb2c0", "#2f5e6e", "#ffffff", "#c2d6dc", "#a0a8ab"], 1.0, ["Ice blue", "Slate"]),
    ("mustard", "Mustard", "yellow", "#e5b84a", ["#2b2723", "#f6eedb", "#a76b2a", "#f0d48b", "#6c6a5f"], 1.0, ["Mustard binder", "Black chips"]),
    ("lavender-stone", "Lavender Stone", "violet", "#e3dceb", ["#7b64a3", "#f6f2f8", "#c5a8d8", "#4a4058", "#e0b9a8"], 1.0, ["Lavender", "Clay"]),
]


def chip(cx, cy, r, rng):
    n = int(rng.integers(5, 10))
    ang = np.sort(rng.random(n)) * 2 * np.pi
    rad = r * (0.55 + 0.45 * rng.random(n))
    stretch = 0.6 + 0.8 * rng.random()
    rot = rng.random() * np.pi
    xs = np.cos(ang) * rad * stretch
    ys = np.sin(ang) * rad
    xr = xs * np.cos(rot) - ys * np.sin(rot)
    yr = xs * np.sin(rot) + ys * np.cos(rot)
    return list(zip(cx + xr, cy + yr))


def render(w, h, v, rng):
    slug, title, fam, binder, chips, dens, motifs = v
    S = common.ss(w, h, 2)
    W, H = w * S, h * S
    base = hexrgb(binder)
    # binder: fine speckle of sand plus slow cloudiness
    arr = np.ones((H // S, W // S, 3)) * base
    cloud = fbm(h, w, rng, base=min(w, h) * 0.5, octaves=3)
    arr = arr * (0.96 + 0.08 * cloud[..., None])
    speck = rng.random((h, w))
    dark = (speck < 0.06)[..., None] * 0.1
    light = (speck > 0.95)[..., None] * 0.1
    arr = arr * (1 - dark) + 255 * light * 0.4 + arr * light * 0.6
    im = to_image(arr).resize((W, H), Image.NEAREST)
    dr = ImageDraw.Draw(im)
    s = min(W, H)
    # big, medium and small chips
    area = max(W, H) / min(W, H)
    for size, count in ((0.045, 28), (0.022, 105), (0.01, 380), (0.0045, 1200)):
        for _ in range(int(count * dens * area)):
            cx, cy = rng.random() * W, rng.random() * H
            r = s * size * (0.6 + 0.8 * rng.random())
            c = hexrgb(chips[int(rng.integers(0, len(chips)))])
            c = c * (0.92 + 0.14 * rng.random())
            dr.polygon(chip(cx, cy, r, rng), fill=col(c))
            if size >= 0.025 and rng.random() < 0.5:
                # veins or inclusions in the larger chips
                c2 = mix(c, base, 0.35)
                dr.polygon(chip(cx + r * 0.2, cy - r * 0.1, r * 0.35, rng), fill=col(c2))
    im = im.resize((w, h), Image.LANCZOS)
    arr = np.asarray(im, np.float32)
    # polished surface: soft sheen
    Y, X = np.mgrid[0:h, 0:w].astype(np.float32)
    sheen = np.exp(-(((X - w * 0.3) / (w * 0.6)) ** 2 + ((Y - h * 0.25) / (h * 0.5)) ** 2))
    arr = arr + sheen[..., None] * 10
    arr = grain(arr, rng, 2.5)
    return to_image(arr)


def colour(v):
    return v[4][0]
