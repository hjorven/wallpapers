"""Azulejo: hand-painted glazed tiles as found on Portuguese facades."""
import numpy as np
from PIL import Image, ImageDraw
from common import hexrgb, mix, fbm, grain, to_image, col

ID = "azulejo"
NAME = "Azulejo"
TAGLINE = "Painted tiles from Lisbon walls"
DESCRIPTION = ("Glazed ceramic tiles with a painted motif that joins up across the grout, as on "
               "the facades of Lisbon and Porto. Each set has its own motif and glaze.")
FORMAT = "jpg"

# slug, title, family, glaze, paint, second paint, motif, tile size (fraction of short side), motifs
VARIANTS = [
    ("lisboa", "Lisboa", "blue", "#f3f0e6", "#1f3f8f", "#6b8fd1", "rose", 0.20, ["Cobalt rose", "Corner quarters"]),
    ("porto", "Porto", "blue", "#f1efe8", "#203a7a", "#203a7a", "star", 0.17, ["Eight-point star"]),
    ("sintra", "Sintra", "yellow", "#f4ecd6", "#c58a1c", "#2d4f8e", "lattice", 0.18, ["Ochre lattice", "Blue knots"]),
    ("alfama", "Alfama", "green", "#eef0e4", "#2f6b4f", "#c99a2e", "leaf", 0.19, ["Green leaves", "Gold dots"]),
    ("manganese", "Manganese", "violet", "#f2ede6", "#5b3a5e", "#5b3a5e", "rose", 0.15, ["Purple-brown rose"]),
    ("aveiro", "Aveiro", "cyan", "#eef4f3", "#1f7a82", "#1b3a5c", "waves", 0.18, ["Teal waves"]),
    ("coimbra", "Coimbra", "orange", "#f6efe2", "#c4561f", "#2a3d6b", "star", 0.20, ["Orange star", "Blue centre"]),
    ("belem", "Belem", "blue", "#f5f2ea", "#14306b", "#d1a636", "lattice", 0.16, ["Navy lattice", "Gold"]),
    ("evora", "Evora", "red", "#f3ebe0", "#8f2a22", "#2b2b2b", "leaf", 0.17, ["Oxblood leaves"]),
    ("faro", "Faro", "mono", "#f2f1ed", "#232323", "#7a7a7a", "waves", 0.15, ["Black and white"]),
]


def motif(d, T, kind, p1, p2, rng):
    """Draw one tile of size T at origin with 4-fold symmetry (everything mirrored)."""
    c = T / 2
    lw = max(2, int(T * 0.018))
    def sym(points_fn):
        for sx in (1, -1):
            for sy in (1, -1):
                for swap in (False, True):
                    pts = [(c + (y if swap else x) * sx, c + (x if swap else y) * sy) for x, y in points_fn()]
                    yield pts
    if kind == "rose":
        # centre flower, petals, corner quarter circles that join with neighbours into rings
        for k in range(8):
            a = k * np.pi / 4
            pts = [(c + np.cos(a + t) * T * 0.22 * np.sin(np.pi * (t + 0.35) / 0.7), c + np.sin(a + t) * T * 0.22 * np.sin(np.pi * (t + 0.35) / 0.7)) for t in np.linspace(-0.35, 0.35, 16)]
            d.polygon([(c, c)] + pts, fill=col(p1))
        d.ellipse([c - T * 0.06, c - T * 0.06, c + T * 0.06, c + T * 0.06], fill=col(p2))
        d.ellipse([c - T * 0.03, c - T * 0.03, c + T * 0.03, c + T * 0.03], fill=col("#f3f0e6"))
        for cx, cy in ((0, 0), (T, 0), (0, T), (T, T)):
            d.ellipse([cx - T * 0.24, cy - T * 0.24, cx + T * 0.24, cy + T * 0.24], outline=col(p1), width=lw * 2)
            d.ellipse([cx - T * 0.14, cy - T * 0.14, cx + T * 0.14, cy + T * 0.14], fill=col(p2))
        for pts in sym(lambda: [(T * 0.30, T * 0.04), (T * 0.42, T * 0.10), (T * 0.36, T * 0.16)]):
            d.polygon(pts, fill=col(p1))
    elif kind == "star":
        r1, r2 = T * 0.40, T * 0.17
        pts = []
        for k in range(16):
            a = k * np.pi / 8 + np.pi / 8
            r = r1 if k % 2 == 0 else r2
            pts.append((c + np.cos(a) * r, c + np.sin(a) * r))
        d.polygon(pts, fill=col(p1))
        d.ellipse([c - T * 0.12, c - T * 0.12, c + T * 0.12, c + T * 0.12], fill=col("#f3f0e6"))
        d.ellipse([c - T * 0.08, c - T * 0.08, c + T * 0.08, c + T * 0.08], fill=col(p2))
        for cx, cy in ((0, 0), (T, 0), (0, T), (T, T)):
            d.polygon([(cx, cy - T * 0.16), (cx + T * 0.16, cy), (cx, cy + T * 0.16), (cx - T * 0.16, cy)], fill=col(p1))
        for x, y in ((c, 0), (0, c), (T, c), (c, T)):
            d.ellipse([x - T * 0.05, y - T * 0.05, x + T * 0.05, y + T * 0.05], fill=col(p2))
    elif kind == "lattice":
        for k in range(4):
            a = k * np.pi / 2
            # interlaced bands from centre to the edge midpoints
            ex, ey = c + np.cos(a) * c, c + np.sin(a) * c
            d.line([(c, c), (ex, ey)], fill=col(p1), width=int(T * 0.09))
        d.line([(0, 0), (T, T)], fill=col(p1), width=int(T * 0.05))
        d.line([(T, 0), (0, T)], fill=col(p1), width=int(T * 0.05))
        d.ellipse([c - T * 0.2, c - T * 0.2, c + T * 0.2, c + T * 0.2], outline=col(p1), width=int(T * 0.05))
        d.ellipse([c - T * 0.1, c - T * 0.1, c + T * 0.1, c + T * 0.1], fill=col(p2))
        for cx, cy in ((0, 0), (T, 0), (0, T), (T, T)):
            d.ellipse([cx - T * 0.13, cy - T * 0.13, cx + T * 0.13, cy + T * 0.13], fill=col(p2))
            d.ellipse([cx - T * 0.06, cy - T * 0.06, cx + T * 0.06, cy + T * 0.06], fill=col("#f3f0e6"))
    elif kind == "leaf":
        for k in range(4):
            a = k * np.pi / 2 + np.pi / 4
            pts = []
            for t in np.linspace(0, 1, 20):
                r = T * 0.44 * t
                wdt = T * 0.12 * np.sin(np.pi * t)
                pts.append((r, wdt))
            pts += [(x, -y) for x, y in reversed(pts)]
            pts = [(c + x * np.cos(a) - y * np.sin(a), c + x * np.sin(a) + y * np.cos(a)) for x, y in pts]
            d.polygon(pts, fill=col(p1))
            d.line([(c, c), (c + np.cos(a) * T * 0.4, c + np.sin(a) * T * 0.4)], fill=col("#f3f0e6"), width=lw)
        for k in range(4):
            a = k * np.pi / 2
            x, y = c + np.cos(a) * T * 0.3, c + np.sin(a) * T * 0.3
            d.ellipse([x - T * 0.035, y - T * 0.035, x + T * 0.035, y + T * 0.035], fill=col(p2))
        d.ellipse([c - T * 0.07, c - T * 0.07, c + T * 0.07, c + T * 0.07], fill=col(p2))
        for x, y in ((c, 0), (0, c), (T, c), (c, T)):
            d.ellipse([x - T * 0.1, y - T * 0.1, x + T * 0.1, y + T * 0.1], outline=col(p1), width=lw * 2)
    elif kind == "waves":
        for k in range(5):
            r = T * (0.12 + 0.09 * k)
            for cx, cy in ((0, T), (T, T)):
                d.arc([cx - r, cy - r, cx + r, cy + r], 180, 360, fill=col(p1 if k % 2 == 0 else p2), width=int(T * 0.035))
            d.arc([c - r, 0 - r, c + r, 0 + r], 0, 180, fill=col(p1 if k % 2 == 0 else p2), width=int(T * 0.035))
        d.ellipse([c - T * 0.05, c - T * 0.05, c + T * 0.05, c + T * 0.05], fill=col(p1))


def render(w, h, v, rng):
    slug, title, fam, glaze, p1, p2, kind, size, motifs = v
    S = 2
    s = min(w, h)
    T = int(round(s * size)) * S
    tile = Image.new("RGB", (T, T), col(glaze))
    motif(ImageDraw.Draw(tile), T, kind, hexrgb(p1), hexrgb(p2), rng)
    tile = tile.resize((T // S, T // S), Image.LANCZOS)
    t = T // S
    grout = max(2, int(t * 0.025))
    ox, oy = int((w % t) / 2), int((h % t) / 2)
    nx, ny = w // t + 2, h // t + 2
    out = np.zeros((h, w, 3), np.float32) + mix(hexrgb(glaze), np.array([150, 145, 135.0]), 0.55)
    tarr = np.asarray(tile, np.float32)
    for j in range(ny):
        for i in range(nx):
            x0, y0 = ox + (i - 1) * t, oy + (j - 1) * t
            # each tile hand-made: slight tint, uneven paint density, a little wear
            a = tarr.copy()
            paint = (np.abs(a - hexrgb(glaze)).sum(-1) > 30)[..., None]
            dens = 0.86 + 0.18 * rng.random()
            a = np.where(paint, mix(hexrgb(glaze), a, dens), a)
            a = a * (0.96 + 0.06 * rng.random())
            g = grout // 2
            xs, ys = max(0, x0 + g), max(0, y0 + g)
            xe, ye = min(w, x0 + t - g), min(h, y0 + t - g)
            if xs >= xe or ys >= ye:
                continue
            out[ys:ye, xs:xe] = a[ys - y0:ye - y0, xs - x0:xe - x0]
    # glaze: soft mottling and a faint craquelure
    out = out * (0.97 + 0.05 * fbm(h, w, rng, base=t * 0.4, octaves=3)[..., None])
    crack = fbm(h, w, rng, base=t * 0.25, octaves=4)
    lines = np.abs(crack - 0.5) < 0.004
    out = np.where(lines[..., None], out * 0.93, out)
    out = grain(out, rng, 2.0)
    return to_image(out)


def colour(v):
    return v[4]
