"""Vectorwave: glowing wireframe landscapes on black, like early vector arcade games and 3D CAD."""
import numpy as np
from PIL import Image, ImageDraw
from common import hexrgb, mix, glow, stars, to_image, col

ID = "vectorwave"
NAME = "Vectorwave"
TAGLINE = "Wireframe worlds on a black screen"
DESCRIPTION = ("Glowing line landscapes on black: wireframe mountains, grids that run to the horizon "
               "and hollow suns, drawn the way vector arcade machines and early CAD screens did.")
FORMAT = "jpg"

# slug, title, family, line colour, sun colour, background low, terrain, motifs
VARIANTS = [
    ("cyan-valley", "Cyan Valley", "cyan", "#29f0ff", "#ff4fd8", "#07101a", "valley", ["Valley road", "Striped sun"]),
    ("green-peaks", "Green Peaks", "green", "#39ff6a", "#39ff6a", "#03100a", "peaks", ["Wire peaks", "Phosphor green"]),
    ("magenta-sea", "Magenta Sea", "pink", "#ff3fd0", "#ffd23f", "#12051a", "ocean", ["Rolling waves"]),
    ("amber-cad", "Amber CAD", "orange", "#ffab2e", "#ffab2e", "#120a02", "sphere", ["Wire globe", "Amber"]),
    ("blue-grid", "Blue Grid", "blue", "#4a7bff", "#9fe7ff", "#04061a", "flat", ["Endless grid"]),
    ("violet-ridge", "Violet Ridge", "violet", "#a46bff", "#ff6b9a", "#0b0518", "valley", ["Violet ridges"]),
    ("red-alert", "Red Alert", "red", "#ff3344", "#ff3344", "#140405", "peaks", ["Red wire", "Peaks"]),
    ("white-lines", "White Lines", "mono", "#e8eef2", "#e8eef2", "#060707", "ocean", ["White on black"]),
    ("teal-globe", "Teal Globe", "cyan", "#2effc4", "#2effc4", "#021210", "sphere", ["Rotating globe"]),
    ("yellow-dunes", "Yellow Dunes", "yellow", "#ffe03a", "#ff6a3a", "#100d02", "flat", ["Low dunes", "Grid"]),
]


def height(kind, X, Z, rng_off):
    if kind == "valley":
        side = np.clip(np.abs(X) - 2.5, 0, None)
        return side ** 1.3 * (0.5 + 0.5 * np.sin(Z * 0.7 + X * 0.9 + rng_off) ** 2) * 0.9
    if kind == "peaks":
        return (np.sin(X * 0.55 + rng_off) * np.cos(Z * 0.45 + rng_off * 2) + 1) ** 2.2 * 0.9 * np.clip((np.abs(X) - 0.8) / 3, 0.15, 1)
    if kind == "ocean":
        return 0.35 * np.sin(X * 0.6 + Z * 0.9 + rng_off) + 0.25 * np.sin(X * 1.3 - Z * 0.5)
    if kind == "flat":
        return 0.12 * np.sin(Z * 0.8 + rng_off) * np.sin(X * 0.5)
    return np.zeros_like(X)


def render(w, h, v, rng):
    slug, title, fam, line, sunc, low, kind, motifs = v
    S = 2
    W, H = w * S, h * S
    s = min(W, H)
    L, Sun, Bg = hexrgb(line), hexrgb(sunc), hexrgb(low)
    Y = np.mgrid[0:H, 0:W][0].astype(np.float32)
    hor = H * (0.52 if W > H else 0.56)
    img = mix(np.zeros(3), Bg, np.clip(1 - np.abs(Y - hor) / (H * 0.5), 0, 1)[..., None] ** 2)
    img = stars(img, rng, int(W * H / 900), region=hor * 0.95)

    layer = Image.new("RGB", (W, H), (0, 0, 0))
    d = ImageDraw.Draw(layer)
    lw = max(2, int(s * 0.0022))
    cx = W / 2
    off = rng.random() * 6

    # the sun or globe sits on the horizon
    R = s * (0.2 if kind != "sphere" else 0.26)
    sy = hor - R * (0.55 if kind != "sphere" else 0.9)
    if kind == "sphere":
        tilt = 0.35 + rng.random() * 0.3
        for k in range(1, 12):  # meridians as ellipses
            a = np.pi * k / 12
            rx = R * abs(np.cos(a))
            d.ellipse([cx - rx, sy - R, cx + rx, sy + R], outline=col(Sun), width=lw)
        for k in range(-5, 6):  # parallels
            yy = sy + R * np.sin(k / 6 * np.pi / 2 + tilt * 0.2)
            rx = np.sqrt(max(R * R - (yy - sy) ** 2, 0))
            d.ellipse([cx - rx, yy - rx * 0.18, cx + rx, yy + rx * 0.18], outline=col(Sun), width=lw)
    else:
        sun = Image.new("L", (W, H), 0)
        ds = ImageDraw.Draw(sun)
        ds.ellipse([cx - R, sy - R, cx + R, sy + R], fill=255)
        for k in range(7):  # cut stripes in the lower half
            yy = sy + R * (0.1 + k * 0.14)
            ds.rectangle([cx - R, yy, cx + R, yy + R * 0.025 * (k + 1)], fill=0)
        m = np.asarray(sun, np.float32)[..., None] / 255
        grad = mix(Sun, L, np.clip((Y - (sy - R)) / (2 * R), 0, 1)[..., None])
        img = img * (1 - m) + grad * m * 0.8
        d.ellipse([cx - R, sy - R, cx + R, sy + R], outline=col(Sun), width=lw)

    # terrain grid in perspective
    f = W * 0.55 if W > H else W * 0.75
    cam = 1.6
    xs = np.linspace(-14, 14, 57)
    zs = np.geomspace(1.2, 60, 46)
    Xg, Zg = np.meshgrid(xs, zs)
    Hg = height(kind, Xg, Zg, off)
    px = cx + Xg / Zg * f
    py = hor + (cam - Hg) / Zg * f
    occl = np.full(W // 4 + 2, H * 2.0)  # simple painter: draw far to near, black fill below each row
    for j in range(len(zs) - 1, -1, -1):
        fade = np.clip(1.2 - zs[j] / 60, 0.15, 1)
        c = col(L * fade)
        row = list(zip(px[j], py[j]))
        if j < len(zs) - 1:
            # fill the band between this row and the farther one to hide lines behind hills
            poly = row + list(zip(px[j + 1], py[j + 1]))[::-1]
            d.polygon(poly, fill=(0, 0, 0))
            for i in range(len(xs)):
                d.line([(px[j, i], py[j, i]), (px[j + 1, i], py[j + 1, i])], fill=col(L * np.clip(1.2 - zs[j + 1] / 60, 0.15, 1)), width=lw)
            d.line(list(zip(px[j + 1], py[j + 1])), fill=col(L * np.clip(1.2 - zs[j + 1] / 60, 0.15, 1)), width=lw)
        d.line(row, fill=c, width=lw)
    a = np.asarray(layer, np.float32)
    # terrain mask: everything drawn below the far edge hides the sky
    mask = np.zeros((H, W), np.float32)
    top = np.interp(np.arange(W), px[-1], py[-1])
    mask[Y > top[None, :]] = 1
    img = img * (1 - mask[..., None]) + a * mask[..., None] + a * (1 - mask[..., None])
    img = glow(img, s, 0.003, 0.02, 0.9, 0.6)
    # scanlines
    img = img * (0.88 + 0.12 * (np.arange(H) % 4 < 2))[:, None, None]
    im = to_image(img).resize((w, h), Image.LANCZOS)
    return im


def colour(v):
    return v[3]
