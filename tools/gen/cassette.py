"""Cassette Futurism: chunky 1970s and 80s consoles with glowing phosphor screens."""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from common import hexrgb, mix, glow, grain, to_image, col

ID = "cassette"
NAME = "Cassette Futurism"
TAGLINE = "Phosphor screens in beige plastic"
DESCRIPTION = ("The future as imagined around 1979: a curved tube screen set in a chunky plastic console, "
               "with radar sweeps, wire terrain and readouts glowing in green or amber phosphor.")
FORMAT = "jpg"

# slug, title, family, phosphor, bezel, panel accent, layout, motifs
VARIANTS = [
    ("nostromo", "Nostromo", "green", "#5dff7a", "#cfc6b0", "#e2632b", "radar", ["Radar sweep", "Green phosphor"]),
    ("amber-terminal", "Amber Terminal", "orange", "#ffb02e", "#3a3633", "#d8452b", "readout", ["Readouts", "Amber"]),
    ("orbit-plot", "Orbit Plot", "cyan", "#5ff0ff", "#d9d2bf", "#2b6fd8", "orbits", ["Orbit plot"]),
    ("deep-scan", "Deep Scan", "green", "#9cff3f", "#2c2f2a", "#ffcf2e", "terrain", ["Wire terrain", "Scan"]),
    ("signal", "Signal", "yellow", "#ffe24a", "#c9bfa7", "#2e8c6a", "wave", ["Oscilloscope", "Signal"]),
    ("crimson-ops", "Crimson Ops", "red", "#ff4a3d", "#2e2a2a", "#ffb02e", "radar", ["Red radar"]),
    ("ice-console", "Ice Console", "blue", "#7fb2ff", "#e3e0d6", "#e2632b", "orbits", ["Star chart", "Pale blue"]),
    ("mother", "Mother", "mono", "#e8f2e8", "#1f1f1f", "#9a9a9a", "readout", ["White phosphor"]),
    ("tracking", "Tracking", "orange", "#ff8a1e", "#bdb39a", "#2b2b2b", "terrain", ["Amber terrain"]),
    ("lab-scope", "Lab Scope", "cyan", "#3dffd5", "#cfd4cc", "#d83a6b", "wave", ["Lab scope", "Teal"]),
]


def screen_content(d, x0, y0, x1, y1, layout, rng, lw, s):
    """Draw the phosphor picture as white lines on black; colour is added later."""
    W, H = x1 - x0, y1 - y0
    cx, cy = x0 + W / 2, y0 + H / 2
    m = min(W, H)
    on, dim = 255, 90
    # frame of small fake text rows and boxes
    def text_rows(x, y, n, width):
        for k in range(n):
            xx = x
            while xx < x + width * (0.4 + 0.6 * rng.random()):
                L = m * (0.008 + 0.03 * rng.random())
                d.rectangle([xx, y + k * m * 0.03, xx + L, y + k * m * 0.03 + m * 0.012], fill=dim + int(120 * rng.random()))
                xx += L + m * 0.01
    if layout == "radar":
        R = m * 0.4
        for k in range(1, 5):
            d.ellipse([cx - R * k / 4, cy - R * k / 4, cx + R * k / 4, cy + R * k / 4], outline=dim, width=lw)
        d.line([(cx - R, cy), (cx + R, cy)], fill=dim, width=lw)
        d.line([(cx, cy - R), (cx, cy + R)], fill=dim, width=lw)
        a0 = rng.random() * 360
        for k in range(60):  # fading sweep
            d.pieslice([cx - R, cy - R, cx + R, cy + R], a0 - k, a0 - k + 1.2, fill=int(200 * (1 - k / 60) ** 2))
        d.line([(cx, cy), (cx + R * np.cos(np.radians(a0)), cy + R * np.sin(np.radians(a0)))], fill=on, width=lw * 2)
        for _ in range(9):
            r, a = R * (0.2 + 0.75 * rng.random()), rng.random() * 2 * np.pi
            px, py = cx + r * np.cos(a), cy + r * np.sin(a)
            b = m * 0.008
            d.rectangle([px - b, py - b, px + b, py + b], fill=on)
            d.line([(px + b * 2, py), (px + m * 0.05, py - m * 0.03)], fill=dim, width=lw)
        text_rows(x0 + m * 0.04, y0 + m * 0.05, 5, W * 0.25)
        text_rows(x1 - W * 0.28, y1 - m * 0.2, 5, W * 0.25)
    elif layout == "terrain":
        hor = y0 + H * 0.38
        f = W * 0.6
        xs = np.linspace(-8, 8, 33)
        zs = np.geomspace(1.0, 30, 26)
        X, Z = np.meshgrid(xs, zs)
        Hh = (np.sin(X * 0.7 + rng.random() * 5) * np.cos(Z * 0.5) + 1) ** 2 * 0.5 * np.clip(np.abs(X) / 3, 0.2, 1)
        px = cx + X / Z * f
        py = hor + (1.4 - Hh) / Z * f
        for j in range(len(zs)):
            d.line(list(zip(px[j], py[j])), fill=int(on * np.clip(1.3 - zs[j] / 30, 0.3, 1)), width=lw)
        for i in range(len(xs)):
            d.line(list(zip(px[:, i], py[:, i])), fill=int(on * 0.6), width=lw)
        d.rectangle([x0, y0, x1, hor - m * 0.02], fill=0)
        # target box
        tx, ty = cx + W * (rng.random() - 0.5) * 0.4, hor + H * 0.25
        b = m * 0.06
        for k in (1, 1.6):
            d.rectangle([tx - b * k, ty - b * k, tx + b * k, ty + b * k], outline=on, width=lw)
        text_rows(x0 + m * 0.04, y0 + m * 0.05, 6, W * 0.4)
        # range bar
        for k in range(24):
            hh = m * 0.02 * (1 + (k % 4 == 0))
            d.line([(x0 + W * 0.55 + k * W * 0.017, y0 + m * 0.1), (x0 + W * 0.55 + k * W * 0.017, y0 + m * 0.1 - hh)], fill=dim, width=lw)
    elif layout == "orbits":
        R = m * 0.42
        d.ellipse([cx - m * 0.05, cy - m * 0.05, cx + m * 0.05, cy + m * 0.05], outline=on, width=lw * 2)
        for k in range(5):
            rx = R * (0.25 + 0.18 * k)
            ry = rx * (0.35 + 0.15 * rng.random())
            d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], outline=dim + 40, width=lw)
            a = rng.random() * 2 * np.pi
            px, py = cx + rx * np.cos(a), cy + ry * np.sin(a)
            b = m * 0.012
            d.ellipse([px - b, py - b, px + b, py + b], fill=on)
        for _ in range(int(160)):
            x, y = x0 + rng.random() * W, y0 + rng.random() * H
            d.point((x, y), fill=dim + int(150 * rng.random()))
        for gx in np.linspace(x0, x1, 13):
            for gy in np.linspace(y0, y1, 9):
                d.line([(gx - m * 0.006, gy), (gx + m * 0.006, gy)], fill=dim, width=lw)
                d.line([(gx, gy - m * 0.006), (gx, gy + m * 0.006)], fill=dim, width=lw)
        text_rows(x1 - W * 0.3, y0 + m * 0.05, 4, W * 0.26)
    elif layout == "wave":
        for gy in np.linspace(y0, y1, 9)[1:-1]:
            d.line([(x0, gy), (x1, gy)], fill=60, width=lw)
        for gx in np.linspace(x0, x1, 13)[1:-1]:
            d.line([(gx, y0), (gx, y1)], fill=60, width=lw)
        t = np.linspace(0, 1, 800)
        for k, (yc, amp, fr) in enumerate([(0.3, 0.12, 5), (0.55, 0.08, 11), (0.78, 0.1, 3)]):
            ph = rng.random() * 6
            yy = y0 + H * yc + np.sin(t * fr * 2 * np.pi + ph) * H * amp * (np.sin(t * np.pi * (1 + k)) * 0.5 + 0.6)
            d.line(list(zip(x0 + t * W, yy)), fill=on if k == 0 else 170, width=lw * 2 if k == 0 else lw)
        text_rows(x0 + m * 0.04, y0 + m * 0.04, 3, W * 0.3)
    else:  # readout: panels of bars, numbers and a big gauge
        cols = 3 if W > H else 2
        rows = 2 if W > H else 3
        pw, ph = W / cols, H / rows
        for i in range(cols):
            for j in range(rows):
                px0, py0 = x0 + i * pw + m * 0.02, y0 + j * ph + m * 0.02
                px1, py1 = px0 + pw - m * 0.04, py0 + ph - m * 0.04
                d.rectangle([px0, py0, px1, py1], outline=dim, width=lw)
                kind = (i + j * cols + int(rng.integers(0, 3))) % 4
                if kind == 0:
                    n = 10
                    for k in range(n):
                        bh = (py1 - py0) * 0.75 * rng.random()
                        bx = px0 + (px1 - px0) * (0.08 + k * 0.088)
                        d.rectangle([bx, py1 - m * 0.02 - bh, bx + (px1 - px0) * 0.05, py1 - m * 0.02], fill=on)
                elif kind == 1:
                    r = min(px1 - px0, py1 - py0) * 0.38
                    gx, gy = (px0 + px1) / 2, (py0 + py1) / 2 + r * 0.3
                    d.arc([gx - r, gy - r, gx + r, gy + r], 180, 360, fill=on, width=lw * 2)
                    for k in range(11):
                        a = np.pi + k * np.pi / 10
                        d.line([(gx + r * 0.85 * np.cos(a), gy + r * 0.85 * np.sin(a)), (gx + r * np.cos(a), gy + r * np.sin(a))], fill=on, width=lw)
                    a = np.pi + rng.random() * np.pi
                    d.line([(gx, gy), (gx + r * 0.9 * np.cos(a), gy + r * 0.9 * np.sin(a))], fill=on, width=lw * 2)
                elif kind == 2:
                    text_rows(px0 + m * 0.02, py0 + m * 0.03, int((py1 - py0) / (m * 0.03)) - 1, px1 - px0 - m * 0.04)
                else:
                    t = np.linspace(0, 1, 200)
                    yy = py0 + (py1 - py0) * (0.5 - 0.35 * np.cumsum(rng.normal(0, 0.08, 200)) / 3)
                    d.line(list(zip(px0 + t * (px1 - px0), np.clip(yy, py0, py1))), fill=on, width=lw)


def render(w, h, v, rng):
    slug, title, fam, phos, bezel, accent, layout, motifs = v
    S = 2
    W, H = w * S, h * S
    s = min(W, H)
    P, B, A = hexrgb(phos), hexrgb(bezel), hexrgb(accent)
    Y, X = np.mgrid[0:H, 0:W].astype(np.float32)
    # plastic console: soft vertical light, thin moulding lines
    img = B * (1.08 - 0.22 * (Y / H))[..., None]
    img = grain(img, rng, 3)
    lw = max(2, int(s * 0.0022))
    landscape = W > H
    m = s * 0.07
    # screen rectangle; leave room for a control strip
    if landscape:
        sx0, sy0, sx1, sy1 = m, m, W - m - s * 0.22, H - m
        strip = (sx1 + m * 0.6, m, W - m * 0.7, H - m)
    else:
        sx0, sy0, sx1, sy1 = m, m, W - m, H - m - s * 0.3
        strip = (m, sy1 + m * 0.6, W - m, H - m * 0.7)
    base = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(base)
    rad = s * 0.06
    # recess shadow and screen glass
    d.rounded_rectangle([sx0 - s * 0.018, sy0 - s * 0.018, sx1 + s * 0.018, sy1 + s * 0.018], rad * 1.2, fill=col(B * 0.55))
    d.rounded_rectangle([sx0, sy0, sx1, sy1], rad, fill=(8, 10, 9))
    # control strip: buttons, slots and a stripe of accent colour
    x0, y0, x1, y1 = strip
    d.rounded_rectangle(strip, s * 0.02, fill=col(B * 0.82))
    if landscape:
        d.rectangle([x0, y0 + (y1 - y0) * 0.06, x1, y0 + (y1 - y0) * 0.09], fill=col(A))
        for k in range(6):
            yy = y0 + (y1 - y0) * (0.16 + k * 0.08)
            d.rounded_rectangle([x0 + (x1 - x0) * 0.15, yy, x1 - (x1 - x0) * 0.15, yy + (y1 - y0) * 0.05], s * 0.006, fill=col(B * 0.5 if k % 3 else A * 0.9))
        cx, cy, r = (x0 + x1) / 2, y0 + (y1 - y0) * 0.78, (x1 - x0) * 0.3
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col(B * 0.45))
        d.ellipse([cx - r * 0.7, cy - r * 0.7, cx + r * 0.7, cy + r * 0.7], fill=col(B * 0.9))
        for k in range(10):  # speaker grille
            yy = y1 - (y1 - y0) * 0.04 - k * s * 0.008
        d.rectangle([x0 + (x1 - x0) * 0.2, y1 - (y1 - y0) * 0.06, x1 - (x1 - x0) * 0.2, y1 - (y1 - y0) * 0.045], fill=col(B * 0.35))
    else:
        d.rectangle([x0 + (x1 - x0) * 0.03, y0, x0 + (x1 - x0) * 0.05, y1], fill=col(A))
        for k in range(8):
            xx = x0 + (x1 - x0) * (0.1 + k * 0.065)
            d.rounded_rectangle([xx, y0 + (y1 - y0) * 0.2, xx + (x1 - x0) * 0.045, y0 + (y1 - y0) * 0.55], s * 0.006, fill=col(B * 0.5 if k % 3 else A * 0.9))
        cx, cy, r = x0 + (x1 - x0) * 0.82, (y0 + y1) / 2, (y1 - y0) * 0.32
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col(B * 0.45))
        d.ellipse([cx - r * 0.7, cy - r * 0.7, cx + r * 0.7, cy + r * 0.7], fill=col(B * 0.9))
        d.rectangle([x0 + (x1 - x0) * 0.1, y0 + (y1 - y0) * 0.7, x0 + (x1 - x0) * 0.6, y0 + (y1 - y0) * 0.78], fill=col(B * 0.35))
    # small LEDs
    for k in range(3):
        lx = sx0 + k * s * 0.03 + s * 0.01
        ly = sy1 + s * 0.035 if landscape else sy1 + s * 0.03
        if ly + s * 0.01 < H:
            d.ellipse([lx, ly, lx + s * 0.012, ly + s * 0.012], fill=col(P if k == 0 else A))
    img = np.asarray(base, np.float32)

    # phosphor picture
    pic = Image.new("L", (W, H), 0)
    dp = ImageDraw.Draw(pic)
    pad = s * 0.035
    screen_content(dp, sx0 + pad, sy0 + pad, sx1 - pad, sy1 - pad, layout, rng, lw, s)
    p = np.asarray(pic, np.float32)[..., None] / 255
    scr = np.asarray(Image.new("L", (W, H), 0), np.float32)
    mask_im = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask_im).rounded_rectangle([sx0, sy0, sx1, sy1], rad, fill=255)
    mask = np.asarray(mask_im, np.float32)[..., None] / 255
    light = p * P
    light = glow(light, s, 0.003, 0.02, 0.8, 0.5)
    # scanlines and tube curvature: darker towards the corners
    scan = (0.75 + 0.25 * ((Y / S).astype(int) % 3 != 0))[..., None]
    u = (X - (sx0 + sx1) / 2) / ((sx1 - sx0) / 2)
    v_ = (Y - (sy0 + sy1) / 2) / ((sy1 - sy0) / 2)
    curve = np.clip(1 - 0.35 * (u ** 2 + v_ ** 2) ** 1.5, 0, 1)[..., None]
    glass = np.array([8, 10, 9.0]) + P * 0.05 + light * scan
    glass = glass * curve
    # a soft reflection on the glass
    refl = np.clip(1 - np.sqrt(((u + 0.45) / 0.5) ** 2 + ((v_ + 0.55) / 0.35) ** 2), 0, 1)[..., None] ** 2 * 26
    glass = glass + refl
    img = img * (1 - mask) + glass * mask
    return to_image(img).resize((w, h), Image.LANCZOS)


def colour(v):
    return v[3]
