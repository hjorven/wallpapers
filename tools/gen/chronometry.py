"""Mechanical Chronometry: gear trains and clockwork drawn in ink on old paper, notebook style."""
import numpy as np
from PIL import Image, ImageDraw
from common import hexrgb, mix, fbm, grain, to_image, col

ID = "chronometry"
NAME = "Mechanical Chronometry"
TAGLINE = "Clockwork sketched on old paper"
DESCRIPTION = ("Gear trains, escapements and springs drawn in ink like a Renaissance engineer's notebook, "
               "with construction circles, hatching and lines of mirrored notes on stained paper.")
FORMAT = "jpg"

# slug, title, family, paper, ink, wash (None = no tint), layout, motifs
VARIANTS = [
    ("codex", "Codex", "orange", "#e8d5ad", "#4a2e18", None, "train", ["Gear train", "Sepia"]),
    ("escapement", "Escapement", "yellow", "#efe0b8", "#3a2a1a", "#c9a24a", "escape", ["Escapement", "Brass wash"]),
    ("orrery", "Orrery", "blue", "#e6dcc4", "#1f2e4a", None, "orrery", ["Orbits", "Iron-gall ink"]),
    ("red-chalk", "Red Chalk", "red", "#ecd8c0", "#8a2f1e", None, "train", ["Red chalk"]),
    ("mainspring", "Mainspring", "orange", "#e3cfa6", "#3d2814", "#b0703a", "spring", ["Spiral spring", "Copper wash"]),
    ("night-study", "Night Study", "mono", "#2a2622", "#e6dcc8", None, "train", ["Chalk on dark"]),
    ("verdigris", "Verdigris", "green", "#e4dcc0", "#2a3a2a", "#6a9a7a", "escape", ["Verdigris wash"]),
    ("astrolabe", "Astrolabe", "yellow", "#1e2433", "#e0c27a", None, "orrery", ["Gold on navy"]),
    ("workshop", "Workshop", "orange", "#efe4cc", "#2e2620", "#c98a4a", "spring", ["Workshop sheet"]),
    ("blue-print", "Blue Print", "blue", "#1c3f6a", "#e6eef8", None, "escape", ["White lines", "Cyanotype"]),
]


def wobble(pts, rng, amt):
    pts = np.asarray(pts, float)
    n = len(pts)
    noise = np.cumsum(rng.normal(0, amt, (n, 2)), axis=0)
    noise -= np.linspace(0, 1, n)[:, None] * noise[-1]
    return [tuple(p) for p in pts + noise * 0.3]


def gear(d, cx, cy, R, teeth, ink, lw, rng, spokes=5, rot=0.0):
    a = np.linspace(0, 2 * np.pi, teeth * 8 + 1) + rot
    tooth = (np.sin(a * teeth - rot * teeth) > 0).astype(float)
    # trapezoid teeth: soften the square wave
    tooth = np.clip(np.sin(a * teeth - rot * teeth) * 2.2, -1, 1) * 0.5 + 0.5
    r = R * (0.9 + 0.1 * tooth)
    pts = list(zip(cx + np.cos(a) * r, cy + np.sin(a) * r))
    d.line(wobble(pts, rng, R * 0.0015), fill=ink, width=lw)
    for f in (0.78, 0.7):
        rr = R * f
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=ink, width=max(1, lw // 2 if f < 0.75 else lw))
    hub = R * 0.16
    d.ellipse([cx - hub, cy - hub, cx + hub, cy + hub], outline=ink, width=lw)
    d.ellipse([cx - hub * 0.35, cy - hub * 0.35, cx + hub * 0.35, cy + hub * 0.35], fill=ink)
    for k in range(spokes):
        b = rot + k * 2 * np.pi / spokes
        for off in (-0.05, 0.05):
            d.line([(cx + np.cos(b + off * 3) * hub, cy + np.sin(b + off * 3) * hub),
                    (cx + np.cos(b + off) * R * 0.7, cy + np.sin(b + off) * R * 0.7)], fill=ink, width=max(1, lw // 2 + 1))
    # hatching on the lower right of the rim
    for k in range(int(teeth * 1.5)):
        b = np.pi * 0.05 + k * (np.pi * 0.7) / (teeth * 1.5)
        d.line([(cx + np.cos(b) * R * 0.72, cy + np.sin(b) * R * 0.72), (cx + np.cos(b + 0.06) * R * 0.86, cy + np.sin(b + 0.06) * R * 0.86)], fill=ink, width=1)


def notes(d, x, y, width, rows, ink, rng, size):
    for r in range(rows):
        xx = x
        yy = y + r * size * 1.9
        end = x + width * (0.5 + 0.5 * rng.random())
        while xx < end:
            L = size * (1.5 + 4 * rng.random())
            t = np.linspace(0, 1, int(L / size * 6) + 2)
            pts = list(zip(xx + t * L, yy + np.sin(t * L / size * 3.1 + rng.random() * 6) * size * 0.35 + rng.normal(0, size * 0.05, len(t))))
            d.line(pts, fill=ink, width=1)
            xx += L + size * 0.9


def render(w, h, v, rng):
    slug, title, fam, paper, ink, wash, layout, motifs = v
    S = 2
    W, H = w * S, h * S
    s = min(W, H)
    Pp, Ik = hexrgb(paper), hexrgb(ink)
    dark = sum(Pp) < 300
    stain = fbm(H, W, rng, base=s * 0.4, octaves=5)
    img = Pp * (1 - (0.1 if not dark else -0.12) * (stain[..., None] - 0.5) * 2)
    Y, X = np.mgrid[0:H, 0:W].astype(np.float32)
    edge = np.sqrt(((X - W / 2) / (W / 2)) ** 2 + ((Y - H / 2) / (H / 2)) ** 2)
    img = img * (1 - 0.18 * np.clip(edge - 0.7, 0, 1)[..., None] * (1 if not dark else -0.5))
    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
    lay = Image.new("L", (W, H), 0)  # ink drawn as coverage, then blended
    d = ImageDraw.Draw(lay)
    lw = max(2, int(s * 0.0034))
    faint, mid, full = 70, 150, 235
    gears = []
    if layout == "train":
        cx, cy = W * 0.5, H * 0.5
        R0 = s * 0.25
        gears.append((cx - s * 0.06, cy - s * 0.02, R0, 36))
        a = rng.random() * np.pi * 2
        x, y, r = gears[0][:3]
        for k in range(5):
            r2 = R0 * (0.3 + 0.45 * rng.random())
            for _try in range(20):
                a2 = a + rng.normal(1.0, 0.7)
                x2, y2 = x + np.cos(a2) * (r + r2) * 0.9, y + np.sin(a2) * (r + r2) * 0.9
                ok = (r2 < x2 < W - r2) and (r2 < y2 < H - r2) and all(np.hypot(x2 - gx, y2 - gy) > (r2 + gr) * 0.92 for gx, gy, gr, _ in gears[:-1])
                if ok:
                    break
            a = a2
            gears.append((x2, y2, r2, max(10, int(32 * r2 / R0))))
            x, y, r = x2, y2, r2
    elif layout == "escape":
        cx, cy = W * 0.45, H * 0.52
        R0 = s * 0.24
        gears.append((cx, cy, R0, 30))
        gears.append((cx + R0 * 1.45, cy - R0 * 0.6, R0 * 0.55, 18))
        # anchor and pendulum
        ax, ay = cx, cy - R0 * 1.25
        d.line([(ax, ay), (ax - R0 * 0.75, cy - R0 * 0.8)], fill=full, width=lw)
        d.line([(ax, ay), (ax + R0 * 0.75, cy - R0 * 0.8)], fill=full, width=lw)
        d.ellipse([ax - R0 * 0.08, ay - R0 * 0.08, ax + R0 * 0.08, ay + R0 * 0.08], outline=full, width=lw)
        L = H * 0.75
        ang = np.radians(rng.uniform(-8, 8))
        bx, by = ax + np.sin(ang) * L, ay + np.cos(ang) * L * 0.6
        d.line([(ax, ay), (bx, by)], fill=full, width=lw)
        rb = s * 0.06
        d.ellipse([bx - rb, by - rb, bx + rb, by + rb], outline=full, width=lw)
        for k in range(-3, 4):  # swing arc
            b = np.radians(k * 5)
            d.line([(ax + np.sin(b) * L * 0.55, ay + np.cos(b) * L * 0.55 * 0.6), (ax + np.sin(b) * L * 0.58, ay + np.cos(b) * L * 0.58 * 0.6)], fill=mid, width=1)
        d.arc([ax - L * 0.6, ay - L * 0.6 * 0.6, ax + L * 0.6, ay + L * 0.6 * 0.6], 70, 110, fill=faint, width=1)
    elif layout == "orrery":
        cx, cy = W / 2, H * 0.5
        R = s * 0.42
        for k in range(1, 7):
            rr = R * k / 6
            d.ellipse([cx - rr, cy - rr * 0.95, cx + rr, cy + rr * 0.95], outline=mid if k % 2 else faint, width=1 if k % 2 == 0 else lw // 2 + 1)
            a = rng.random() * np.pi * 2
            px, py = cx + np.cos(a) * rr, cy + np.sin(a) * rr * 0.95
            pr = s * (0.012 + 0.02 * rng.random())
            d.ellipse([px - pr, py - pr, px + pr, py + pr], outline=full, width=lw)
            d.line([(cx, cy), (px, py)], fill=faint, width=1)
        for k in range(72):  # degree scale
            a = k * np.pi / 36
            l = 0.03 if k % 6 == 0 else 0.015
            d.line([(cx + np.cos(a) * R * 1.03, cy + np.sin(a) * R * 1.03 * 0.95), (cx + np.cos(a) * R * (1.03 + l), cy + np.sin(a) * R * (1.03 + l) * 0.95)], fill=mid, width=1)
        gears.append((cx, cy, s * 0.1, 16))
        sun = s * 0.03
        for k in range(16):
            a = k * np.pi / 8
            d.line([(cx + np.cos(a) * sun * 1.3, cy + np.sin(a) * sun * 1.3), (cx + np.cos(a) * sun * 2.2, cy + np.sin(a) * sun * 2.2)], fill=mid, width=1)
    else:  # spring
        cx, cy = W * 0.42, H * 0.5
        R = s * 0.3
        t = np.linspace(0, 1, 2000)
        turns = 9
        rr = R * (0.08 + 0.92 * t)
        a = t * turns * 2 * np.pi
        d.line(wobble(list(zip(cx + np.cos(a) * rr, cy + np.sin(a) * rr)), rng, s * 0.0004), fill=full, width=lw)
        d.ellipse([cx - R * 1.05, cy - R * 1.05, cx + R * 1.05, cy + R * 1.05], outline=full, width=lw)
        gears.append((cx + R * 1.6, cy - R * 0.4, R * 0.5, 20))
        gears.append((cx + R * 1.5, cy + R * 0.75, R * 0.32, 14))
    for (x, y, r, n) in gears:
        gear(d, x, y, r, n, full, lw, rng, spokes=int(rng.choice([4, 5, 6])), rot=rng.random())
        # construction: a faint circle and centre cross
        d.ellipse([x - r * 1.12, y - r * 1.12, x + r * 1.12, y + r * 1.12], outline=faint, width=1)
        d.line([(x - r * 1.3, y), (x + r * 1.3, y)], fill=faint, width=1)
        d.line([(x, y - r * 1.3), (x, y + r * 1.3)], fill=faint, width=1)
    # guide lines and notes in the margins
    for _ in range(3):
        y0 = rng.random() * H
        d.line([(0, y0), (W, y0 + rng.normal(0, s * 0.05))], fill=40, width=1)
    size = s * 0.007
    blocks = [(W * 0.06, H * 0.06), (W * 0.62, H * 0.78), (W * 0.06, H * 0.82)] if W > H else [(W * 0.08, H * 0.05), (W * 0.5, H * 0.86), (W * 0.08, H * 0.9)]
    for bx, by in blocks:
        notes(d, bx, by, W * 0.3, int(4 + rng.integers(0, 4)), mid, rng, size)
    # small detail sketch: a cross-section
    sx, sy = (W * 0.84, H * 0.18) if W > H else (W * 0.78, H * 0.12)
    sr = s * 0.05
    d.rectangle([sx - sr, sy - sr * 0.3, sx + sr, sy + sr * 0.3], outline=mid, width=1)
    for k in range(10):
        d.line([(sx - sr + k * sr * 0.2, sy - sr * 0.3), (sx - sr + k * sr * 0.2 + sr * 0.15, sy + sr * 0.3)], fill=faint, width=1)
    d.line([(sx, sy - sr * 0.9), (sx, sy + sr * 0.9)], fill=mid, width=1)
    cov = np.asarray(lay, np.float32)[..., None] / 255
    a = np.asarray(im, np.float32)
    if wash is not None:
        # a watercolour wash inside the biggest gear, slightly off register
        x, y, r, _ = gears[0]
        m = np.clip(1 - np.sqrt((X - x - s * 0.01) ** 2 + (Y - y + s * 0.01) ** 2) / (r * 0.95), 0, 1) ** 0.3
        m = m * (0.75 + 0.5 * fbm(H, W, rng, base=s * 0.05, octaves=3))
        a = a * (1 - 0.35 * m[..., None]) + hexrgb(wash) * 0.35 * m[..., None]
    a = a * (1 - cov * 0.92) + Ik * cov * 0.92
    a = grain(a, rng, 4)
    return to_image(a).resize((w, h), Image.LANCZOS)


def colour(v):
    return v[4] if sum(hexrgb(v[3])) > 300 else v[4]
