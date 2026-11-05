"""Aero-Deco: streamlined towers, zeppelins and searchlights, the machine age dressed in chrome."""
import numpy as np
from PIL import Image, ImageDraw
from common import hexrgb, mix, grain, to_image, col

ID = "aerodeco"
NAME = "Aero-Deco"
TAGLINE = "Chrome towers and zeppelins"
DESCRIPTION = ("A symmetric machine-age city: streamlined chrome towers with vertical fins, airships "
               "drifting between them and searchlights sweeping a banded sky.")
FORMAT = "png"

# slug, title, family, sky top, sky low, metal light, metal dark, accent, motifs
VARIANTS = [
    ("metropolis", "Metropolis", "yellow", "#1a1712", "#6a5a3a", "#f2dca0", "#4a3a22", "#ffcf5a", ["Gold city", "Zeppelins"]),
    ("skyport", "Skyport", "blue", "#0d1a33", "#4a6a9a", "#e6eef7", "#2a3a55", "#ffd27a", ["Chrome", "Blue dusk"]),
    ("dawn-flight", "Dawn Flight", "pink", "#3a1f3a", "#f2a58a", "#fbe8dc", "#6a3a4a", "#ffe6a0", ["Pink dawn"]),
    ("emerald-city", "Emerald City", "green", "#0b1f1a", "#3a7a62", "#d8f0e2", "#1a3a30", "#f2d27a", ["Emerald", "Brass"]),
    ("night-shift", "Night Shift", "violet", "#0d0a1a", "#3a2a5a", "#d8d2ee", "#221a38", "#ff9ad0", ["Searchlights", "Violet"]),
    ("steel-noon", "Steel Noon", "mono", "#cfd2d4", "#f2f2ee", "#ffffff", "#5a5f66", "#2a2e33", ["Steel", "Bright sky"]),
    ("copper-hour", "Copper Hour", "orange", "#2a140a", "#d8823a", "#ffe0b8", "#5a2e16", "#fff0c8", ["Copper", "Sunset"]),
    ("ocean-liner", "Ocean Liner", "cyan", "#06202a", "#3a8a9a", "#e0f6f8", "#163a44", "#ff6a4a", ["Teal", "Red lights"]),
    ("crimson-air", "Crimson Air", "red", "#24070c", "#8a2a2a", "#ffd8c8", "#4a1418", "#ffd27a", ["Crimson"]),
    ("silver-mist", "Silver Mist", "blue", "#2a3448", "#b8c4d8", "#ffffff", "#4a5a74", "#f2c46a", ["Mist", "Silver"]),
]


def chrome(x0, x1, light, dark):
    """Horizontal metal gradient: bright stripe left of centre, dark edges."""
    def f(t):
        return mix(dark, light, np.clip(1 - np.abs(t - 0.35) * 2.2, 0, 1) ** 0.8)
    return f


def tower(d, cx, base, width, height, light, dark, accent, rng, S):
    L, D = np.asarray(light, float), np.asarray(dark, float)
    tiers = int(3 + rng.integers(0, 3))
    y = base
    wv = width
    seg_h = height / (tiers + 1.5)
    shade = chrome(0, 1, L, D)
    for t in range(tiers):
        x0, x1 = cx - wv / 2, cx + wv / 2
        y0 = y - seg_h * (1.4 if t == 0 else 1.0)
        n = 24
        for k in range(n):  # vertical strips for the metal shading
            xa = x0 + (x1 - x0) * k / n
            xb = x0 + (x1 - x0) * (k + 1) / n + 1
            d.rectangle([xa, y0, xb, y], fill=col(shade(k / (n - 1))))
        # vertical fins
        for fk in (0.2, 0.5, 0.8):
            fx = x0 + (x1 - x0) * fk
            d.line([(fx, y0 + seg_h * 0.05), (fx, y)], fill=col(D * 0.8), width=max(2, int(S * 1.5)))
        # rows of lit windows
        rows = int(seg_h / (wv * 0.06))
        for r in range(rows):
            yy = y0 + seg_h * 0.1 + r * wv * 0.06
            if yy > y - wv * 0.03:
                break
            for c_ in range(6):
                if rng.random() < 0.5:
                    wx = x0 + (x1 - x0) * (0.08 + c_ * 0.15)
                    d.rectangle([wx, yy, wx + (x1 - x0) * 0.06, yy + wv * 0.025], fill=col(accent))
        y = y0
        wv *= 0.72
    # rounded crown and spire
    x0, x1 = cx - wv / 2, cx + wv / 2
    d.pieslice([x0, y - wv * 0.7, x1, y + wv * 0.7], 180, 360, fill=col(shade(0.35)))
    for k in range(4):
        rr = wv / 2 * (1 - k * 0.22)
        d.arc([cx - rr, y - rr * 1.4, cx + rr, y + rr * 1.4], 180, 360, fill=col(D), width=max(1, int(S)))
    d.line([(cx, y - wv * 0.7), (cx, y - wv * 0.7 - height * 0.18)], fill=col(shade(0.3)), width=max(2, int(S * 2)))
    r = S * 3
    d.ellipse([cx - r, y - wv * 0.7 - height * 0.18 - r, cx + r, y - wv * 0.7 - height * 0.18 + r], fill=col(accent))


def zeppelin(d, cx, cy, L, light, dark, accent, flip):
    Lh, Dk = np.asarray(light, float), np.asarray(dark, float)
    hh = L * 0.16
    for k in range(10):  # body shading from top to bottom
        t = k / 9
        c = mix(Lh, Dk, t ** 1.2)
        d.ellipse([cx - L / 2, cy - hh + t * hh * 0.9, cx + L / 2, cy + hh - t * hh * 0.15], fill=col(c)) if k == 0 else None
    d.ellipse([cx - L / 2, cy - hh, cx + L / 2, cy + hh], fill=col(mix(Lh, Dk, 0.25)))
    d.chord([cx - L / 2, cy - hh, cx + L / 2, cy + hh], 0, 180, fill=col(mix(Lh, Dk, 0.6)))
    d.ellipse([cx - L * 0.45, cy - hh * 0.85, cx + L * 0.4, cy - hh * 0.25], fill=col(mix(Lh, Dk, 0.05)))
    for k in range(1, 6):
        x = cx - L / 2 + L * k / 6
        d.line([(x, cy - hh * np.sqrt(1 - ((x - cx) / (L / 2)) ** 2)), (x, cy + hh * np.sqrt(1 - ((x - cx) / (L / 2)) ** 2))], fill=col(mix(Lh, Dk, 0.5)), width=1)
    tail = cx + (L * 0.42 if not flip else -L * 0.42)
    sg = 1 if not flip else -1
    for fy in (-1, 1):
        d.polygon([(tail - sg * L * 0.08, cy + fy * hh * 0.4), (tail + sg * L * 0.1, cy + fy * hh * 1.25), (tail + sg * L * 0.1, cy + fy * hh * 0.25)], fill=col(mix(Lh, Dk, 0.45)))
    d.rounded_rectangle([cx - L * 0.1, cy + hh * 0.9, cx + L * 0.08, cy + hh * 1.3], radius=hh * 0.15, fill=col(Dk))
    for k in range(4):
        wx = cx - L * 0.08 + k * L * 0.04
        d.rectangle([wx, cy + hh * 1.0, wx + L * 0.02, cy + hh * 1.12], fill=col(accent))


def render(w, h, v, rng):
    slug, title, fam, top, low, light, dark, accent, motifs = v
    S = 2
    W, H = w * S, h * S
    s = min(W, H)
    T, Lo, Li, Dk, Ac = (hexrgb(c) for c in (top, low, light, dark, accent))
    Y = np.mgrid[0:H, 0:W][0].astype(np.float32)
    steps = 9
    t = np.floor(np.clip(Y / (H * 0.85), 0, 0.999) * steps) / (steps - 1)
    img = mix(T, Lo, t[..., None] ** 1.2)
    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
    # searchlight beams (translucent)
    beams = Image.new("L", (W, H), 0)
    db = ImageDraw.Draw(beams)
    base = H * 0.97
    for k in range(4):
        bx = W * (0.15 + 0.7 * k / 3)
        a = np.radians(-90 + (k - 1.5) * 14 + rng.normal(0, 6))
        Lb = H * 1.2
        sp = np.radians(3)
        db.polygon([(bx, base), (bx + np.cos(a - sp) * Lb, base + np.sin(a - sp) * Lb), (bx + np.cos(a + sp) * Lb, base + np.sin(a + sp) * Lb)], fill=40)
    a = np.asarray(im, np.float32)
    b = np.asarray(beams, np.float32)[..., None] / 255
    a = a * (1 - b) + mix(Ac, (255, 255, 255), 0.5) * b
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(im)
    # far skyline in a flat tone
    far = col(mix(Lo, Dk, 0.4))
    x = 0
    while x < W:
        bw = s * (0.04 + 0.05 * rng.random())
        bh = H * (0.15 + 0.25 * rng.random())
        d.rectangle([x, H - bh, x + bw, H], fill=far)
        d.rectangle([x + bw * 0.25, H - bh - bh * 0.08, x + bw * 0.75, H - bh], fill=far)
        x += bw * 1.05
    # mirrored side towers and one big centre tower
    cx = W / 2
    pairs = 2 if W > H else 1
    for k in range(pairs, 0, -1):
        off = (W * 0.36 if W > H else W * 0.36) * k / pairs
        wd = s * (0.12 - 0.02 * k)
        ht = H * (0.48 - 0.06 * k)
        seed_k = int(rng.integers(0, 1 << 30))
        ht = ht * (0.8 + 0.4 * rng.random())
        for sgn in (-1, 1):  # same seed on both sides keeps the pair symmetric
            tower(d, cx + sgn * off, H, wd, ht, mix(Li, Lo, 0.3), Dk, Ac, np.random.default_rng(seed_k), S)
    tower(d, cx, H, s * (0.17 + 0.06 * rng.random()), H * (0.6 + 0.14 * rng.random()), Li, Dk, Ac, rng, S)
    # airships
    n = 2 if W > H else 2
    for k in range(n):
        zx = W * (0.22 + 0.56 * k) + rng.normal(0, s * 0.04)
        zy = H * (0.18 + 0.12 * rng.random())
        zeppelin(d, zx, zy, s * (0.3 - 0.06 * k), Li, Dk, Ac, flip=(k == 1))
    # speed lines across the sky
    for k in range(6):
        yy = H * (0.08 + 0.05 * k)
        x0 = W * rng.random() * 0.4
        d.line([(x0, yy), (x0 + W * (0.15 + 0.2 * rng.random()), yy)], fill=col(mix(T, Li, 0.35)), width=max(2, int(S * 1.5)))
    a = np.asarray(im, np.float32)
    a = grain(a, rng, 3)
    return to_image(a).resize((w, h), Image.LANCZOS)


def colour(v):
    return v[7]
