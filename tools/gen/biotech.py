"""Bio-Integrated: living technology. Glowing nerve networks, cells and helices in the dark."""
import numpy as np
import common
from PIL import Image, ImageDraw
from common import hexrgb, mix, glow, fbm, grain, to_image, col

ID = "biotech"
NAME = "Bio-Integrated"
TAGLINE = "Glowing nerves, cells and helices"
DESCRIPTION = ("Technology that grows: branching nerve cells, mycelium roots, floating cells and DNA "
               "strands that glow like bioluminescent circuits in dark tissue.")
FORMAT = "jpg"

# slug, title, family, background, main glow, second glow, layout, motifs
VARIANTS = [
    ("synapse", "Synapse", "cyan", "#02090d", "#3fe8ff", "#b05cff", "neurons", ["Nerve cells", "Cyan"]),
    ("mycel", "Mycel", "yellow", "#0b0805", "#ffd27a", "#ff7a3d", "roots", ["Mycelium", "Warm glow"]),
    ("helix", "Helix", "violet", "#07040f", "#c36bff", "#3fd8ff", "helix", ["DNA helix"]),
    ("culture", "Culture", "green", "#030a05", "#7dff8a", "#e4ff5a", "cells", ["Cell culture"]),
    ("cortex", "Cortex", "pink", "#0d0309", "#ff4fb8", "#ffb35a", "neurons", ["Pink neurons"]),
    ("deep-root", "Deep Root", "cyan", "#020a0a", "#4dffd1", "#4d9bff", "roots", ["Glowing roots"]),
    ("sequence", "Sequence", "blue", "#02040e", "#4f8cff", "#ff5fd2", "helix", ["Blue helix", "Base pairs"]),
    ("plasma", "Plasma", "red", "#0d0303", "#ff5a4a", "#ffc24a", "cells", ["Red cells"]),
    ("spore", "Spore", "orange", "#0b0602", "#ff9b3d", "#7dffd8", "neurons", ["Amber nerves"]),
    ("ghost-tissue", "Ghost Tissue", "mono", "#060606", "#e8f2f0", "#9fb5b0", "cells", ["Pale tissue"]),
]


def branch(d, x, y, ang, length, width, depth, rng, fill, nodes, droop=0.0):
    steps = int(6 + rng.integers(0, 6))
    seg = length / steps
    pts = [(x, y)]
    for _ in range(steps):
        ang += rng.normal(0, 0.22) + droop
        x += np.cos(ang) * seg
        y += np.sin(ang) * seg
        pts.append((x, y))
    for k in range(len(pts) - 1):
        wk = max(1, int(width * (1 - k / len(pts) * 0.6)))
        d.line([pts[k], pts[k + 1]], fill=fill, width=wk)
    if depth <= 0:
        nodes.append((x, y))
        return
    n = 2 if rng.random() < 0.8 else 3
    for _ in range(n):
        branch(d, x, y, ang + rng.normal(0, 0.6), length * (0.6 + 0.15 * rng.random()), width * 0.65,
               depth - 1, rng, fill, nodes, droop)


def render(w, h, v, rng):
    slug, title, fam, bg, g1, g2, layout, motifs = v
    S = common.ss(w, h, 2)
    W, H = w * S, h * S
    s = min(W, H)
    Bg, C1, C2 = hexrgb(bg), hexrgb(g1), hexrgb(g2)
    # tissue background: a faint cloudy membrane in the second colour
    cloud = fbm(H, W, rng, base=s * 0.4, octaves=4)
    img = Bg + mix(np.zeros(3), C2, (np.clip(cloud - 0.45, 0, 1) * 0.25)[..., None])
    l1 = Image.new("L", (W, H), 0)
    l2 = Image.new("L", (W, H), 0)
    d1, d2 = ImageDraw.Draw(l1), ImageDraw.Draw(l2)
    lw = s * 0.006
    nodes = []
    if layout == "neurons":
        n = 3 if W > H else 3
        somas = []
        for i in range(n):
            cx = W * (0.2 + 0.6 * (i + rng.random() * 0.6) / n)
            cy = H * (0.2 + 0.6 * rng.random())
            somas.append((cx, cy))
        for cx, cy in somas:
            for k in range(int(5 + rng.integers(0, 3))):
                a = k / 6 * 2 * np.pi + rng.normal(0, 0.3)
                branch(d1, cx, cy, a, s * (0.12 + 0.05 * rng.random()), lw * 1.6, 3, rng, 255, nodes)
            r = s * 0.025
            d1.ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
            d2.ellipse([cx - r * 2.2, cy - r * 2.2, cx + r * 2.2, cy + r * 2.2], outline=150, width=int(lw * 0.6))
        # synapse sparks at the branch tips
        for x, y in nodes:
            r = s * (0.003 + 0.004 * rng.random())
            d2.ellipse([x - r, y - r, x + r, y + r], fill=255)
    elif layout == "roots":
        for i in range(int(4 + rng.integers(0, 3))):
            x = W * (0.1 + 0.8 * rng.random())
            branch(d1, x, -s * 0.02, np.pi / 2 + rng.normal(0, 0.2), s * 0.2, lw * 2.0, 4, rng, 255, nodes, droop=0.0)
            x = W * (0.1 + 0.8 * rng.random())
            branch(d1, x, H + s * 0.02, -np.pi / 2 + rng.normal(0, 0.2), s * 0.16, lw * 1.6, 4, rng, 180, nodes)
        for x, y in nodes:
            r = s * (0.004 + 0.008 * rng.random())
            d2.ellipse([x - r, y - r, x + r, y + r], fill=255)
            if rng.random() < 0.3:
                r2 = r * 2.5
                d2.ellipse([x - r2, y - r2, x + r2, y + r2], outline=140, width=max(1, int(lw * 0.4)))
    elif layout == "helix":
        # one long diagonal double helix with base pairs
        ang = np.radians(62 if H > W else 28) * (1 if rng.random() < 0.5 else -1)
        L = np.hypot(W, H) * 1.1
        t = np.linspace(-0.5, 0.5, 1400)
        R = s * 0.09
        turns = 7
        ph = t * turns * 2 * np.pi
        cx, cy = W / 2, H / 2
        ux, uy = np.cos(ang), np.sin(ang)
        px, py = -uy, ux
        for k, off in enumerate((0, np.pi)):
            o = np.sin(ph + off) * R
            depth = np.cos(ph + off)
            xs = cx + t * L * ux + o * px
            ys = cy + t * L * uy + o * py
            for i in range(len(t) - 1):
                b = int(130 + 125 * (depth[i] * 0.5 + 0.5))
                d1.line([(xs[i], ys[i]), (xs[i + 1], ys[i + 1])], fill=b, width=int(lw * (1.2 + 0.8 * (depth[i] * 0.5 + 0.5))))
        for i in range(0, len(t), 18):
            o1, o2 = np.sin(ph[i]) * R, np.sin(ph[i] + np.pi) * R
            x0, y0 = cx + t[i] * L * ux, cy + t[i] * L * uy
            d2.line([(x0 + o1 * px, y0 + o1 * py), (x0 + o2 * px, y0 + o2 * py)], fill=200, width=int(lw * 0.8))
        # small free cells around
        for _ in range(40):
            x, y, r = rng.random() * W, rng.random() * H, s * (0.004 + 0.012 * rng.random())
            d2.ellipse([x - r, y - r, x + r, y + r], outline=160, width=max(1, int(lw * 0.4)))
    else:  # cells
        placed = []
        for _ in range(int(38 * W * H / (s * s))):
            r = s * (0.02 + 0.07 * rng.random() ** 2)
            for _try in range(30):
                x, y = rng.random() * W, rng.random() * H
                if all((x - a) ** 2 + (y - b) ** 2 > (r + c) ** 2 for a, b, c in placed):
                    break
            placed.append((x, y, r))
            # wobbly membrane
            a = np.linspace(0, 2 * np.pi, 80)
            wob = 1 + 0.06 * np.sin(a * int(rng.integers(3, 7)) + rng.random() * 6)
            pts = list(zip(x + np.cos(a) * r * wob, y + np.sin(a) * r * wob))
            d1.line(pts + [pts[0]], fill=200, width=max(2, int(lw * 0.9)))
            nr = r * (0.25 + 0.15 * rng.random())
            nx, ny = x + r * 0.2 * rng.normal(), y + r * 0.2 * rng.normal()
            d2.ellipse([nx - nr, ny - nr, nx + nr, ny + nr], fill=130)
            for _ in range(int(4 + r / s * 80)):  # organelles
                rr, aa = r * 0.75 * np.sqrt(rng.random()), rng.random() * 2 * np.pi
                ox, oy = x + rr * np.cos(aa), y + rr * np.sin(aa)
                orr = s * 0.002
                d1.ellipse([ox - orr, oy - orr, ox + orr, oy + orr], fill=150)
        # a few filaments linking near neighbours
        for i, (x, y, r) in enumerate(placed[:60]):
            j = int(rng.integers(0, len(placed)))
            x2, y2, r2 = placed[j]
            if 0 < np.hypot(x2 - x, y2 - y) < s * 0.25:
                d2.line([(x, y), (x2, y2)], fill=60, width=max(1, int(lw * 0.3)))
    a1 = np.asarray(l1, np.float32)[..., None] / 255
    a2 = np.asarray(l2, np.float32)[..., None] / 255
    light = a1 * C1 + a2 * C2
    light = glow(light, s, 0.004, 0.03, 1.0, 0.9)
    img = img + light
    img = grain(img, rng, 3)
    return to_image(img).resize((w, h), Image.LANCZOS)


def colour(v):
    return v[4]
