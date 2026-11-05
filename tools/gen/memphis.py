"""Memphis: loud 1980s Milan design. Squiggles, confetti, grids of dots and bold outlines."""
import numpy as np
import common
from PIL import Image, ImageDraw
from common import hexrgb, col

ID = "memphis"
NAME = "Memphis"
TAGLINE = "Squiggles and confetti, Milan 1981"
DESCRIPTION = ("Squiggles, confetti triangles, dot grids and zigzags with heavy black outlines, after "
               "the design collective that shocked Milan in 1981.")
FORMAT = "png"

# slug, title, family, background, palette, ink, density, motifs
VARIANTS = [
    ("milano", "Milano", "pink", "#f7d6d0", ["#2bb3b1", "#f5c52c", "#ef5b5b", "#3d5af1"], "#111111", 1.0, ["Teal", "Lemon", "Coral"]),
    ("bacterio", "Bacterio", "yellow", "#fff3c4", ["#ff6f61", "#00a6a6", "#6a4c93", "#ffb703"], "#151515", 1.0, ["Plum", "Tangerine"]),
    ("arcade-mint", "Arcade Mint", "green", "#cfeee0", ["#ff4f79", "#ffd23f", "#3a86ff", "#1b1b1e"], "#1b1b1e", 0.9, ["Mint ground"]),
    ("grape-soda", "Grape Soda", "violet", "#2d1b4e", ["#ff9ff3", "#feca57", "#48dbfb", "#ff6b6b"], "#f5f0ff", 1.0, ["Dark ground", "Neon pastels"]),
    ("terrazza", "Terrazza", "orange", "#ffd8b1", ["#2a9d8f", "#e76f51", "#264653", "#e9c46a"], "#1d1d1d", 0.9, ["Peach", "Petrol"]),
    ("blue-plate", "Blue Plate", "blue", "#3d5af1", ["#ffde59", "#ff66c4", "#ffffff", "#00d1b2"], "#0b0b0b", 1.0, ["Cobalt ground"]),
    ("chalk", "Chalk", "mono", "#f2f0eb", ["#111111", "#9a9a9a", "#d9d6cf", "#111111"], "#111111", 1.1, ["Black on chalk"]),
    ("lobster", "Lobster", "red", "#ef5b5b", ["#ffe66d", "#2ec4b6", "#ffffff", "#1a1a2e"], "#1a1a2e", 1.0, ["Coral ground"]),
    ("lagoon", "Lagoon", "cyan", "#a7e8e3", ["#ff5d8f", "#ffd166", "#5e60ce", "#06d6a0"], "#14213d", 0.9, ["Lagoon", "Pink"]),
    ("banana", "Banana", "yellow", "#ffe45e", ["#ff5e5b", "#00cecb", "#3d348b", "#ffffff"], "#111111", 1.0, ["Banana ground"]),
]


def squiggle(d, x, y, L, amp, ang, width, fill):
    t = np.linspace(0, 1, 60)
    xs = t * L
    ys = np.sin(t * np.pi * 4) * amp
    c, s = np.cos(ang), np.sin(ang)
    pts = [(x + a * c - b * s, y + a * s + b * c) for a, b in zip(xs, ys)]
    d.line(pts, fill=fill, width=width, joint="curve")


def render(w, h, v, rng):
    slug, title, fam, bg, pal, ink, dens, motifs = v
    S = common.ss(w, h, 2)
    W, H = w * S, h * S
    im = Image.new("RGB", (W, H), col(bg))
    d = ImageDraw.Draw(im)
    s = min(W, H)
    lw = int(s * 0.007)
    K = col(ink)
    P = [col(c) for c in pal]

    # background textures: a dot grid patch and a stripe patch
    gx, gy = rng.random() * W * 0.6, rng.random() * H * 0.6
    gs = s * 0.035
    for i in range(10):
        for j in range(8):
            r = s * 0.005
            cx, cy = gx + i * gs, gy + j * gs
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=K)
    sx, sy = rng.random() * W * 0.7, rng.random() * H * 0.7
    for k in range(9):
        d.line([(sx + k * s * 0.022, sy), (sx + k * s * 0.022 + s * 0.12, sy + s * 0.22)], fill=P[1], width=lw)

    # big shapes
    shapes = int(9 * dens * (W * H) / (s * s) ** 1 * 1.0)
    placed = []
    for _ in range(shapes):
        kind = rng.choice(["circle", "tri", "rect", "semi"])
        r = s * (0.06 + 0.07 * rng.random())
        for _try in range(40):
            cx, cy = rng.random() * W, rng.random() * H
            if all((cx - px) ** 2 + (cy - py) ** 2 > (r + pr) ** 2 * 0.9 for px, py, pr in placed):
                break
        placed.append((cx, cy, r))
        fill = P[int(rng.integers(0, len(P)))]
        off = s * 0.012
        if kind == "circle":
            d.ellipse([cx - r + off, cy - r + off, cx + r + off, cy + r + off], fill=K)
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill, outline=K, width=lw)
        elif kind == "tri":
            a = rng.random() * np.pi * 2
            pts = [(cx + np.cos(a + k * 2.094) * r, cy + np.sin(a + k * 2.094) * r) for k in range(3)]
            d.polygon([(x + off, y + off) for x, y in pts], fill=K)
            d.polygon(pts, fill=fill, outline=K, width=lw)
        elif kind == "rect":
            a = rng.random() * np.pi
            ww, hh = r * 1.3, r * 0.45
            pts = [(cx + x * np.cos(a) - y * np.sin(a), cy + x * np.sin(a) + y * np.cos(a)) for x, y in ((-ww, -hh), (ww, -hh), (ww, hh), (-ww, hh))]
            d.polygon(pts, fill=fill, outline=K, width=lw)
            for k in range(1, 6):
                x0 = -ww + k * 2 * ww / 6
                p0 = (cx + x0 * np.cos(a) + hh * np.sin(a), cy + x0 * np.sin(a) - hh * np.cos(a))
                p1 = (cx + x0 * np.cos(a) - hh * np.sin(a), cy + x0 * np.sin(a) + hh * np.cos(a))
                d.line([p0, p1], fill=K, width=max(2, lw // 2))
        else:
            a0 = rng.integers(0, 4) * 90
            d.pieslice([cx - r, cy - r, cx + r, cy + r], a0, a0 + 180, fill=fill, outline=K, width=lw)

    # squiggles, zigzags, confetti
    for _ in range(int(10 * dens * W * H / (s * s))):
        squiggle(d, rng.random() * W, rng.random() * H, s * (0.12 + 0.1 * rng.random()), s * 0.018,
                 rng.random() * np.pi, lw, P[int(rng.integers(0, len(P)))] if rng.random() < 0.5 else K)
    for _ in range(int(5 * dens * W * H / (s * s))):
        x, y, a = rng.random() * W, rng.random() * H, rng.random() * np.pi
        pts = []
        for k in range(7):
            pts.append((x + np.cos(a) * k * s * 0.02 - np.sin(a) * (s * 0.015 if k % 2 else 0),
                        y + np.sin(a) * k * s * 0.02 + np.cos(a) * (s * 0.015 if k % 2 else 0)))
        d.line(pts, fill=K, width=lw)
    for _ in range(int(60 * dens * W * H / (s * s))):
        x, y, a = rng.random() * W, rng.random() * H, rng.random() * np.pi * 2
        r = s * 0.012
        pts = [(x + np.cos(a + k * 2.094) * r, y + np.sin(a + k * 2.094) * r) for k in range(3)]
        d.polygon(pts, fill=P[int(rng.integers(0, len(P)))] if rng.random() < 0.7 else K)
    for _ in range(int(40 * dens * W * H / (s * s))):
        x, y = rng.random() * W, rng.random() * H
        r = s * 0.006
        d.ellipse([x - r, y - r, x + r, y + r], fill=K)
    return im.resize((w, h), Image.LANCZOS)


def colour(v):
    return v[3]
