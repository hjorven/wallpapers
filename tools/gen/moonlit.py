"""Moonlit Circuits: the quiet night side of a green future. Moon, glowing plants and silver networks."""
import numpy as np
import common
from PIL import Image, ImageDraw
from common import hexrgb, mix, glow, stars, fbm, grain, to_image, col

ID = "moonlit"
NAME = "Moonlit Circuits"
TAGLINE = "Glowing plants and silver lines under the moon"
DESCRIPTION = ("A calm night landscape where technology and nature have grown together: crystal panels "
               "catching moonlight, bioluminescent plants and fine silver networks running over the hills.")
FORMAT = "jpg"

# slug, title, family, sky top, sky low, hills, plant glow, metal, motifs
VARIANTS = [
    ("blue-hour", "Blue Hour", "blue", "#050a1f", "#1d3566", "#0a1428", "#5ff2ff", "#c9d6ea", ["Blue night", "Cyan flora"]),
    ("lantern-field", "Lantern Field", "yellow", "#0a0a18", "#2a2a48", "#0e0f1c", "#ffd86a", "#d9d2c0", ["Golden lanterns"]),
    ("violet-glade", "Violet Glade", "violet", "#0b061a", "#33215a", "#120b24", "#d38bff", "#d9cfee", ["Violet glade"]),
    ("moss-light", "Moss Light", "green", "#030d0b", "#16372f", "#06140f", "#8dff9a", "#c6dccf", ["Green glow", "Moss"]),
    ("silver-night", "Silver Night", "mono", "#06070a", "#262a33", "#0c0d11", "#e8f0ff", "#e8ecf2", ["Silver", "White moon"]),
    ("rose-dusk", "Rose Dusk", "pink", "#120717", "#4a2140", "#160a18", "#ff8fd0", "#ecd3e0", ["Pink flora"]),
    ("tide-garden", "Tide Garden", "cyan", "#02101a", "#0f3d4a", "#041a20", "#4dffe1", "#cfe6ea", ["Teal garden"]),
    ("ember-moon", "Ember Moon", "orange", "#100804", "#3d1d10", "#140a06", "#ffa04d", "#ead7c8", ["Orange moon", "Embers"]),
    ("frost-circuit", "Frost Circuit", "blue", "#040814", "#22345a", "#0a1020", "#9fc3ff", "#f0f4ff", ["Frost", "Panels"]),
    ("firefly", "Firefly", "green", "#040806", "#1b2a1e", "#070d09", "#d5ff5c", "#d0dcc8", ["Fireflies"]),
]


def ridge(w, rng, base, amp, freq):
    x = np.arange(w, dtype=np.float32)
    y = np.zeros(w, np.float32)
    a = amp
    f = freq
    for _ in range(4):
        ph = rng.random() * 100
        y += np.sin(x * f + ph) * a + np.sin(x * f * 2.3 + ph * 1.7) * a * 0.4
        a *= 0.45
        f *= 2.1
    return base + y


def render(w, h, v, rng):
    slug, title, fam, top, low, hill, plant, metal, motifs = v
    S = common.ss(w, h, 2)
    W, H = w * S, h * S
    s = min(W, H)
    T, Lo, Hi, P, M = (hexrgb(c) for c in (top, low, hill, plant, metal))
    Y, X = np.mgrid[0:H, 0:W].astype(np.float32)
    img = mix(T, Lo, np.clip(Y / (H * 0.75), 0, 1)[..., None] ** 1.4)
    img = stars(img, rng, int(W * H / 700), region=H * 0.7)
    # moon with halo
    mx, my = W * (0.25 + 0.5 * rng.random()), H * (0.16 + 0.1 * rng.random())
    R = s * 0.07
    dist = np.sqrt((X - mx) ** 2 + (Y - my) ** 2)
    halo = np.exp(-(dist / (s * 0.35)) ** 2) * 0.35 + np.exp(-(dist / (s * 0.12)) ** 2) * 0.3
    img = img + halo[..., None] * M * 0.5
    craters = fbm(H, W, rng, base=s * 0.02, octaves=3)
    disc = np.clip(R - dist + 1, 0, 1)[..., None]
    img = img * (1 - disc) + (M * (0.92 + 0.12 * craters[..., None]) + 18) * disc

    lw = max(2, int(s * 0.0022))
    glowL = Image.new("RGB", (W, H), (0, 0, 0))
    dg = ImageDraw.Draw(glowL)
    base = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(base)
    layers = 4
    for li in range(layers):
        depth = li / (layers - 1)
        yb = H * (0.58 + 0.11 * li)
        r = ridge(W, rng, yb, s * (0.07 - 0.01 * li), 1.0 / (s * (0.3 - 0.05 * li)))
        c = mix(mix(Lo, M, 0.18), Hi * 0.55, depth ** 0.8)
        poly = [(0, H)] + list(zip(range(W), r)) + [(W, H)]
        d.polygon(poly, fill=col(c))
        # moonlit rim along the ridge
        d.line(list(zip(range(0, W, 4), r[::4])), fill=col(mix(c, M, 0.25)), width=lw)
        # silver cable between a few masts, sagging like power lines
        if li in (1, 2):
            n = int(3 + rng.integers(0, 2))
            xs = np.sort((np.arange(n) + 0.2 + 0.6 * rng.random(n)) / n * W)
            mast = s * (0.05 + 0.03 * depth)
            tops = []
            for x in xs:
                gy = r[min(W - 1, int(x))]
                d.line([(x, gy), (x, gy - mast)], fill=col(mix(c, M, 0.4)), width=lw)
                d.line([(x - mast * 0.18, gy - mast * 0.85), (x + mast * 0.18, gy - mast * 0.85)], fill=col(mix(c, M, 0.4)), width=lw)
                tops.append((x, gy - mast * 0.85))
                rr = s * 0.003
                dg.ellipse([x - rr, gy - mast - rr, x + rr, gy - mast + rr], fill=col(P))
            for (x0, y0), (x1, y1) in zip(tops, tops[1:]):
                t_ = np.linspace(0, 1, 40)
                xx = x0 + (x1 - x0) * t_
                yy = y0 + (y1 - y0) * t_ + np.sin(t_ * np.pi) * s * 0.025
                d.line(list(zip(xx, yy)), fill=col(mix(c, M, 0.55)), width=max(1, lw // 2))
        # crystal panels on the nearer slopes
        if li == 2:
            for _ in range(int(1 + rng.integers(0, 2))):
                px = W * (0.15 + 0.7 * rng.random())
                gy = r[min(W - 1, int(px))]
                ph_ = s * 0.04
                pw = s * 0.09
                d.line([(px, gy), (px, gy - ph_)], fill=col(c * 0.6), width=lw * 2)
                quad = [(px - pw / 2, gy - ph_), (px + pw / 2, gy - ph_ - pw * 0.2),
                        (px + pw / 2 + pw * 0.1, gy - ph_ - pw * 0.55), (px - pw / 2 + pw * 0.1, gy - ph_ - pw * 0.35)]
                d.polygon(quad, fill=col(mix(Lo, M, 0.3)), outline=col(M * 0.9))
                for k in (1, 2, 3):
                    f = k / 4
                    a0 = (quad[0][0] + (quad[1][0] - quad[0][0]) * f, quad[0][1] + (quad[1][1] - quad[0][1]) * f)
                    a1 = (quad[3][0] + (quad[2][0] - quad[3][0]) * f, quad[3][1] + (quad[2][1] - quad[3][1]) * f)
                    d.line([a0, a1], fill=col(mix(Lo, M, 0.55)), width=max(1, lw // 2))
                d.line([quad[3], quad[2]], fill=col(M), width=lw)
        # glowing plants rising from the ridge: few, tall and soft
        nplants = int((2 + 5 * depth) * W / s)
        for _ in range(nplants):
            px = rng.random() * W
            gy = r[min(W - 1, int(px))] + s * 0.004
            hgt = s * (0.04 + 0.07 * rng.random()) * (0.5 + 0.9 * depth)
            for stem_i in range(int(1 + rng.integers(0, 3))):
                bend = rng.normal(0, 0.35)
                hh = hgt * (0.6 + 0.4 * rng.random())
                t_ = np.linspace(0, 1, 20)
                sx = px + np.sin(t_ * 1.6) * bend * hh
                sy = gy - t_ * hh
                d.line(list(zip(sx, sy)), fill=col(mix(c, P, 0.2 + 0.15 * depth)), width=max(1, int(lw * (0.5 + depth))))
                rr = s * (0.003 + 0.005 * rng.random()) * (0.6 + depth)
                dg.ellipse([sx[-1] - rr, sy[-1] - rr, sx[-1] + rr, sy[-1] + rr], fill=col(P))
        a = np.asarray(base, np.float32)
        band = np.exp(-((Y - yb) / (s * 0.06)) ** 2)[..., None] * 0.18 * (1 - depth)
        a = mix(a, Lo + 25, band)
        base = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
        d = ImageDraw.Draw(base)
    img = np.asarray(base, np.float32)
    gl = np.asarray(glowL, np.float32)
    img = img + glow(gl, s, 0.004, 0.02, 1.0, 0.8)
    # fireflies / floating spores
    for _ in range(int(25 * W / s)):
        x, y = int(rng.random() * W), int(H * (0.45 + 0.5 * rng.random()))
        rr = int(s * 0.002) + 1
        img[max(0, y - rr):y + rr, max(0, x - rr):x + rr] += P * 0.6
    img = grain(img, rng, 3)
    return to_image(img).resize((w, h), Image.LANCZOS)


def colour(v):
    return v[6]
