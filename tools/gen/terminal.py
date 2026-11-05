"""Terminal Core: server halls, rack walls and blinking status lights in cold light."""
import numpy as np
import common
from PIL import Image, ImageDraw
from common import hexrgb, mix, glow, grain, to_image, col

ID = "terminal"
NAME = "Terminal Core"
TAGLINE = "Server halls and blinking racks"
DESCRIPTION = ("The hidden machine rooms: long corridors of server racks, rows of status lights, cable "
               "trays overhead and cold light at the end of the hall.")
FORMAT = "jpg"

# slug, title, family, room tone, rack tone, led colour, second led, layout, motifs
VARIANTS = [
    ("cold-aisle", "Cold Aisle", "blue", "#0a1220", "#141b26", "#4fa8ff", "#7dffb0", "corridor", ["Corridor", "Blue LEDs"]),
    ("green-status", "Green Status", "green", "#07110c", "#111a15", "#5dff8a", "#ffcf4a", "corridor", ["Green status"]),
    ("red-alarm", "Red Alarm", "red", "#140708", "#1c1012", "#ff3b3b", "#ff9a3b", "corridor", ["Alarm red"]),
    ("rack-wall", "Rack Wall", "cyan", "#06100f", "#101817", "#3dffe0", "#4f8cff", "wall", ["Rack front", "Cables"]),
    ("amber-core", "Amber Core", "orange", "#120b05", "#1b140d", "#ffa83d", "#ffe27a", "wall", ["Amber lights"]),
    ("violet-hall", "Violet Hall", "violet", "#0d0818", "#161021", "#b47bff", "#ff6bd0", "corridor", ["Violet hall"]),
    ("white-room", "White Room", "mono", "#cfd3d6", "#2a2e33", "#f2f6ff", "#6ad1ff", "corridor", ["Bright room", "Black racks"]),
    ("backbone", "Backbone", "yellow", "#0d0c06", "#17160f", "#ffe14a", "#5fd0ff", "wall", ["Yellow lights"]),
    ("deep-row", "Deep Row", "blue", "#04070f", "#0c1018", "#6a8bff", "#ff5a7a", "corridor", ["Long row"]),
    ("patch-bay", "Patch Bay", "pink", "#10060d", "#1a0f17", "#ff5fc0", "#5fffd8", "wall", ["Patch cables"]),
]


def render(w, h, v, rng):
    slug, title, fam, room, rack, led, led2, layout, motifs = v
    S = common.ss(w, h, 2)
    W, H = w * S, h * S
    s = min(W, H)
    Rm, Rk, L1, L2 = (hexrgb(c) for c in (room, rack, led, led2))
    bright = sum(Rm) > 400
    img = np.ones((H, W, 3), np.float32) * Rm
    base = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(base)
    gl = Image.new("RGB", (W, H), (0, 0, 0))
    dg = ImageDraw.Draw(gl)
    lw = max(1, int(s * 0.0015))
    if layout == "corridor":
        cx, cy = W / 2, H * 0.48
        f = s * 0.9
        half = 1.0  # aisle half width in metres
        ceil, floor = 1.25, -1.0  # relative to eye height
        def P(x, y, z):
            return (cx + x / z * f, cy - y / z * f)
        zs = np.arange(1.0, 26.0, 0.6)
        # floor tiles and ceiling
        for z0 in np.arange(0.6, 40, 0.6):
            a = P(-half * 3, floor, z0)
            b = P(half * 3, floor, z0)
            fade = np.clip(1.4 - z0 / 20, 0.1, 1)
            d.line([a, b], fill=col(mix(Rm, Rk * 0.5 if not bright else Rm * 0.8, 0.6) * (0.6 + 0.4 * fade)), width=lw)
        for x in np.arange(-half, half + 0.01, 0.5):
            d.line([P(x, floor, 0.4), P(x, floor, 60)], fill=col(Rm * (0.75 if not bright else 0.85)), width=lw)
        # end of the hall: a cold light
        Y, X = np.mgrid[0:H, 0:W].astype(np.float32)
        img = np.asarray(base, np.float32)
        ex = np.exp(-(((X - cx) / (s * 0.12)) ** 2 + ((Y - cy) / (s * 0.16)) ** 2))
        img = img + ex[..., None] * mix(L1, (255, 255, 255), 0.6) * 0.8
        base = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
        d = ImageDraw.Draw(base)
        # racks on both sides, drawn far to near
        rack_depth = 0.6
        units = 22
        for z0 in zs[::-1]:
            z1 = z0 + rack_depth * 0.95
            fade = np.clip(1.25 - z0 / 22, 0.08, 1)
            for side in (-1, 1):
                xf = side * half
                quad = [P(xf, floor, z0), P(xf, ceil * 0.82, z0), P(xf, ceil * 0.82, z1), P(xf, floor, z1)]
                face = Rk * (1.4 + 0.3 * rng.random()) * (0.5 + 0.5 * fade) + Rm * (1 - fade) * 0.4
                d.polygon(quad, fill=col(face), outline=col(face * 0.6))
                # LEDs in a few columns of each rack
                for u in range(units):
                    if rng.random() < 0.55:
                        yy = floor + (ceil * 0.82 - floor) * (u + 0.5) / units
                        for k in range(int(rng.integers(1, 4))):
                            zz = z0 + rack_depth * (0.12 + 0.25 * k + 0.05 * rng.random())
                            x0, y0 = P(xf, yy, zz)
                            r = max(1, s * 0.006 / zz)
                            c = L1 if rng.random() < 0.8 else L2
                            dg.ellipse([x0 - r, y0 - r * 0.7, x0 + r, y0 + r * 0.7], fill=col(c * fade))
                # vent lines
                for k in range(3):
                    yy = floor + 0.1 + k * 0.05
                    d.line([P(xf, yy, z0 + 0.05), P(xf, yy, z1 - 0.05)], fill=col(face * 0.6), width=lw)
        # cable trays along the ceiling with hanging bundles
        for side in (-0.55, 0.55):
            for z0 in np.arange(1.0, 30, 0.4):
                a, b = P(side, ceil, z0), P(side, ceil, z0 + 0.4)
                d.line([a, b], fill=col(Rk * 1.6 + 6), width=max(1, int(s * 0.012 / z0)))
            for k in range(4):
                t = np.linspace(0, 1, 40)
                z = 1.0 + t * 25
                sag = 0.12 * np.abs(np.sin(t * 30 + k))
                pts = [P(side + (k - 1.5) * 0.04, ceil - 0.05 - sg, zz) for zz, sg in zip(z, sag)]
                d.line(pts, fill=col(mix(Rk, L2, 0.12) * 1.2), width=max(1, lw))
        # strip lights on the ceiling centre
        for z0 in np.arange(2.8, 30, 1.6):
            a, b = P(-0.08, ceil, z0), P(0.08, ceil, z0 + 0.5)
            dg.rectangle([min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1])], fill=col(mix(L1, (255, 255, 255), 0.7) * np.clip(1.2 - z0 / 30, 0.2, 1)))
    else:  # wall: racks seen from the front, filling the frame
        n = int(W / (s * 0.24)) + 1
        rw = W / n
        for i in range(n):
            x0 = i * rw + s * 0.006
            x1 = (i + 1) * rw - s * 0.006
            d.rectangle([x0, 0, x1, H], fill=col(Rk))
            d.rectangle([x0, 0, x0 + s * 0.01, H], fill=col(Rk * 1.5))
            d.rectangle([x1 - s * 0.01, 0, x1, H], fill=col(Rk * 0.6))
            y = s * 0.03
            while y < H - s * 0.03:
                uh = s * (0.022 * int(rng.choice([1, 1, 2, 2, 3, 4])))
                face = Rk * (1.1 + 0.5 * rng.random())
                d.rectangle([x0 + s * 0.015, y, x1 - s * 0.015, y + uh - s * 0.003], fill=col(face))
                kind = rng.random()
                if kind < 0.45:  # drive bays
                    nb = 8
                    for k in range(nb):
                        bx = x0 + s * 0.02 + k * (x1 - x0 - s * 0.04) / nb
                        d.rectangle([bx, y + s * 0.004, bx + (x1 - x0 - s * 0.04) / nb - s * 0.003, y + uh - s * 0.007], fill=col(face * 0.7))
                        if rng.random() < 0.7:
                            c = L1 if rng.random() < 0.85 else L2
                            dg.rectangle([bx + s * 0.002, y + uh - s * 0.012, bx + s * 0.006, y + uh - s * 0.009], fill=col(c))
                elif kind < 0.75:  # switch with port rows and patch cables
                    np_ = 16
                    for k in range(np_):
                        px = x0 + s * 0.025 + k * (x1 - x0 - s * 0.05) / np_
                        d.rectangle([px, y + uh * 0.35, px + s * 0.006, y + uh * 0.65], fill=col(face * 0.4))
                        if rng.random() < 0.6:
                            dg.point((px + s * 0.003, y + uh * 0.25), fill=col(L1 if rng.random() < 0.7 else L2))
                            if slug == "patch-bay" or rng.random() < 0.25:
                                cc = [L1, L2, (230, 230, 230), (90, 90, 90)][int(rng.integers(0, 4))]
                                drop = s * (0.03 + 0.08 * rng.random())
                                t = np.linspace(0, 1, 12)
                                pts = list(zip(px + s * 0.003 + t * s * 0.03 * (rng.random() - 0.5), y + uh * 0.5 + np.sin(t * np.pi / 2) * drop))
                                d.line(pts, fill=col(np.asarray(cc, float) * 0.55), width=max(2, int(s * 0.003)))
                else:  # blank panel with a row of status lights
                    for k in range(int(rng.integers(2, 7))):
                        lx = x1 - s * 0.03 - k * s * 0.012
                        c = L1 if rng.random() < 0.7 else L2
                        dg.ellipse([lx - s * 0.003, y + uh / 2 - s * 0.003, lx + s * 0.003, y + uh / 2 + s * 0.003], fill=col(c))
                    for k in range(4):
                        d.line([(x0 + s * 0.03, y + uh * (0.25 + k * 0.15)), (x0 + (x1 - x0) * 0.45, y + uh * (0.25 + k * 0.15))], fill=col(face * 0.75), width=lw)
                y += uh
        img = np.asarray(base, np.float32)
        Y, X = np.mgrid[0:H, 0:W].astype(np.float32)
        img = img * (0.75 + 0.35 * np.exp(-((Y - H * 0.4) / (H * 0.6)) ** 2))[..., None]
        base = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
    img = np.asarray(base, np.float32)
    g = np.asarray(gl, np.float32)
    img = img + glow(g, s, 0.003, 0.015, 1.0, 0.6)
    img = grain(img, rng, 3)
    return to_image(img).resize((w, h), Image.LANCZOS)


def colour(v):
    return v[5]
