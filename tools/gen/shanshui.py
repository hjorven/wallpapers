"""Shan shui: layered ink mountains fading into mist, after Chinese landscape painting."""
import numpy as np
from PIL import Image, ImageDraw
from common import hexrgb, mix, fbm, grain, to_image, value_noise

ID = "shanshui"
NAME = "Shan Shui"
TAGLINE = "Ink mountains in mist"
DESCRIPTION = ("Layer after layer of mountain ridges that fade into fog, in the manner of Chinese "
               "landscape painting. Each one has its own sky, paper tone and sun or moon.")
FORMAT = "jpg"

# slug, title, family, sky top, sky bottom/mist, ink (nearest ridge), sun colour, motifs
VARIANTS = [
    ("dawn-ink", "Dawn Ink", "mono", "#e9e4d8", "#f4efe4", "#1f1d1b", "#c8442c", ["Red sun", "Seven ridges"]),
    ("jade", "Jade", "green", "#cfe0d4", "#eef3ec", "#1d3b33", "#f3f0e2", ["Pale sun", "Pine ridges"]),
    ("persimmon", "Persimmon", "orange", "#f2c9a0", "#f8e6d2", "#4a2418", "#d9532b", ["Low sun", "Warm haze"]),
    ("indigo-night", "Indigo Night", "blue", "#0f1630", "#3a4670", "#05070f", "#e8e6d6", ["Full moon", "Night fog"]),
    ("first-snow", "First Snow", "mono", "#dfe5ea", "#f7f8f9", "#3b4650", "#ffffff", ["Hidden sun", "Snow peaks"]),
    ("ochre", "Ochre", "yellow", "#e8cf8f", "#f5ebcb", "#4b3a17", "#b5562a", ["Dust sun", "Loess hills"]),
    ("plum-dusk", "Plum Dusk", "violet", "#4d3555", "#c99aa8", "#1c1020", "#f5d6b8", ["Setting sun", "Dusk layers"]),
    ("moss", "Moss", "green", "#9fae8a", "#dfe3cf", "#1f2a17", "#efe9d2", ["Rain sun", "Wet slopes"]),
    ("ash", "Ash", "mono", "#8c8c8c", "#d9d9d6", "#151515", "#f0efe9", ["White disc", "Volcanic ridges"]),
    ("tea", "Tea", "red", "#c9a48a", "#efe1d2", "#3a1d14", "#8a1f17", ["Seal-red sun", "Tea hills"]),
]


def ridge(n, rng, rough, peak):
    """A 1D mountain profile in [0, 1]."""
    x = np.linspace(0, 1, n)
    y = np.zeros(n)
    amp, freq = 1.0, 2 + rng.random() * 2
    for _ in range(6):
        pts = rng.random(int(freq) + 3)
        xp = np.linspace(0, 1, len(pts))
        layer = np.interp(x * (len(pts) - 2) / (len(pts) - 1) + rng.random() / len(pts), xp, pts)
        y += amp * (1 - np.abs(layer * 2 - 1)) ** peak
        amp *= rough
        freq *= 2.1
    y -= y.min()
    return y / max(y.max(), 1e-6)


def render(w, h, v, rng):
    slug, title, fam, top, bottom, ink, sun, motifs = v
    top, bottom, ink, sun = map(hexrgb, (top, bottom, ink, sun))
    yy = np.linspace(0, 1, h)[:, None, None]
    img = mix(top, bottom, yy ** 0.8) * np.ones((h, w, 3))

    # sun or moon
    sx = w * (0.62 + 0.2 * rng.random()) if w > h else w * (0.5 + 0.25 * rng.random())
    sy = h * (0.18 + 0.1 * rng.random())
    sr = min(w, h) * (0.07 + 0.04 * rng.random())
    Y, X = np.mgrid[0:h, 0:w]
    d = np.sqrt((X - sx) ** 2 + (Y - sy) ** 2)
    disc = np.clip(sr - d + 1.5, 0, 1)[..., None]
    halo = np.exp(-((d / (sr * 3.2)) ** 2))[..., None] * 0.18
    img = mix(img, sun, halo)
    img = mix(img, sun, disc * 0.95)

    layers = 6 if w > h else 7
    mist_col = bottom
    for i in range(layers):
        t = i / (layers - 1)  # 0 far, 1 near
        depth_col = mix(mist_col, ink, 0.18 + 0.82 * t ** 1.6)
        base = h * (0.52 + 0.46 * t) if w > h else h * (0.50 + 0.48 * t)
        height = h * (0.13 + 0.10 * t) * (0.75 + 0.5 * rng.random())
        prof = ridge(w, rng, 0.36 + 0.08 * rng.random(), 1.3 + 0.8 * rng.random())
        top_y = base - prof * height
        mask = (Y >= top_y[None, :]).astype(np.float32)
        # soft brush edge + texture inside the mountain
        tex = value_noise(h, w, 6 + 10 * (1 - t), rng)
        shade = np.clip((Y - top_y[None, :]) / (height * 0.9 + 1), 0, 1)
        body = mix(depth_col, mist_col, (shade ** 0.7 * (0.55 - 0.35 * t))[..., None])
        body = body * (0.94 + 0.08 * tex[..., None])
        img = img * (1 - mask[..., None]) + body * mask[..., None]
        # mist band rising from below this ridge
        fog = np.clip(1 - (Y - (base - height * 0.15)) / (h * 0.06), 0, 1) * np.clip((Y - (base - height * 0.9)) / (height * 0.9), 0, 1)
        fog *= 0.55 * (1 - t * 0.5) * (0.6 + 0.4 * fbm(h, w, rng, base=500, octaves=3))
        img = mix(img, mist_col, fog[..., None] * mask[..., None])

    # a flight of birds in the far sky
    birds = Image.new("L", (w, h), 0)
    dr = ImageDraw.Draw(birds)
    bx, by = w * (0.18 + 0.25 * rng.random()), h * (0.22 + 0.08 * rng.random())
    for _ in range(int(5 + rng.random() * 6)):
        x, y = bx + rng.normal(0, w * 0.04), by + rng.normal(0, h * 0.02)
        s = min(w, h) * (0.006 + 0.004 * rng.random())
        dr.line([(x - s, y - s * 0.5), (x, y), (x + s, y - s * 0.6)], fill=255, width=max(2, int(s / 3)))
    bm = np.asarray(birds, np.float32)[..., None] / 255
    img = mix(img, ink, bm * 0.75)

    # paper grain and fibres
    paper = fbm(h, w, rng, base=3, octaves=2)
    img = img * (0.97 + 0.05 * paper[..., None])
    img = grain(img, rng, 3.5)
    return to_image(img)


def colour(v):
    from common import rgbhex
    return rgbhex(mix(hexrgb(v[3]), hexrgb(v[5]), 0.3))
