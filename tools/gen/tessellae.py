"""Tessellae: Roman floor mosaics laid from small stone cubes."""
import numpy as np
import common
from PIL import Image, ImageDraw
from common import hexrgb, mix, col

ID = "tessellae"
NAME = "Tessellae"
TAGLINE = "Roman floors in stone cubes"
DESCRIPTION = ("Patterns from Roman villa floors, laid stone by stone: meanders, rosettes, running "
               "waves and stars, in marble, terracotta and slate with grey mortar between.")
FORMAT = "jpg"

# slug, title, family, mortar, ground, c1, c2, c3, motif, motifs
VARIANTS = [
    ("pompeii", "Pompeii", "red", "#8d857a", "#efe6d4", "#9e3b26", "#2b2623", "#d9b06a", "meander", ["Greek key", "Terracotta"]),
    ("ostia", "Ostia", "mono", "#7d7a75", "#f2efe8", "#1e1e1e", "#8a8a85", "#c9c3b6", "waves", ["Running waves", "Black and white"]),
    ("villa-rosa", "Villa Rosa", "pink", "#8b8079", "#efe3d6", "#b7525a", "#3e5b77", "#e3b77a", "rosette", ["Rosette", "Rose marble"]),
    ("antioch", "Antioch", "orange", "#857a6c", "#f3e5c9", "#c4672a", "#2f3b45", "#e2b25c", "sun", ["Sun rays", "Ochre"]),
    ("aquileia", "Aquileia", "blue", "#7f8287", "#e9e7e1", "#2f4f7d", "#9cb0c7", "#c58f4e", "scales", ["Fish scales", "Lapis"]),
    ("ravenna", "Ravenna", "yellow", "#6e6553", "#1d3a5f", "#d8b25a", "#f2e7c8", "#7a2b2b", "stars", ["Gold stars", "Night blue"]),
    ("carthage", "Carthage", "green", "#7c7a6c", "#ebe3cf", "#4f6b3a", "#a3452c", "#2a2a26", "guilloche", ["Guilloche", "Olive"]),
    ("lugdunum", "Lugdunum", "red", "#7b7068", "#f1e8da", "#7d2a22", "#c9a77a", "#2a2421", "labyrinth", ["Labyrinth"]),
    ("delos", "Delos", "cyan", "#7d8483", "#eef0ec", "#2d6f74", "#e3c79a", "#232b2b", "waves", ["Sea waves", "Teal"]),
    ("italica", "Italica", "violet", "#7c7480", "#ece6e3", "#5d3f6a", "#c48e6a", "#2b2530", "rosette", ["Porphyry rosette"]),
]


def motif(kind, U, V, w_, h_):
    """Return an int index map: 0 ground, 1..3 colours. U, V in tessera units."""
    idx = np.zeros(U.shape, np.int32)
    cx, cy = w_ / 2, h_ / 2
    X, Y = U - cx, V - cy
    r = np.sqrt(X ** 2 + Y ** 2)
    a = np.arctan2(Y, X)
    m = min(w_, h_)
    # a border band on all sides
    edge = np.minimum.reduce([U, V, w_ - 1 - U, h_ - 1 - V])
    border = edge < 6
    if kind == "meander":
        # Greek key in the border, plain field with a central medallion
        bu = np.where(np.minimum(U, w_ - 1 - U) < np.minimum(V, h_ - 1 - V), V, U).astype(int)
        bv = edge.astype(int)
        cell = bu % 6
        key = ((bv == 0) | (bv == 5) & (cell < 5) | (cell == 0) & (bv < 5) | (bv == 2) & (cell >= 2) & (cell < 5) | (cell == 4) & (bv >= 2) & (bv < 5) | (cell == 2) & (bv == 3))
        idx = np.where(border & key, 2, idx)
        idx = np.where(border & ~key, 0, idx)
        ring = (np.abs(r - m * 0.28) < 1.2) | (np.abs(r - m * 0.22) < 0.7)
        idx = np.where(~border & ring, 2, idx)
        idx = np.where(~border & (r < m * 0.2) & ((np.floor(a / (np.pi / 8)) % 2) == 0) & (r > m * 0.06), 1, idx)
        idx = np.where(~border & (r <= m * 0.06), 3, idx)
        # checker of small crosses in the field
        cross = ((U.astype(int) % 10 == 5) & (V.astype(int) % 10 >= 4) & (V.astype(int) % 10 <= 6)) | ((V.astype(int) % 10 == 5) & (U.astype(int) % 10 >= 4) & (U.astype(int) % 10 <= 6))
        idx = np.where(~border & (r > m * 0.32) & cross & (edge > 9), 1, idx)
    elif kind == "waves":
        per = 14
        rows = np.floor(V / per)
        lv = V - rows * per
        phase = (U + rows * per / 2) % per
        crest = per * 0.5 + np.sin(phase / per * 2 * np.pi) * per * 0.28
        idx = np.where(lv > crest, 1, 0)
        curl = np.sqrt((phase - per * 0.75) ** 2 + (lv - per * 0.45) ** 2) < per * 0.16
        idx = np.where(curl, 1 - idx, idx)
        idx = np.where(np.abs(lv - crest) < 0.6, 2, idx)
        idx = np.where(border, np.where(edge % 3 == 0, 3, 0), idx)
    elif kind == "rosette":
        rr = r / (m * 0.45)
        pet = (np.cos(a * 8) * 0.5 + 0.5) ** 0.6
        idx = np.where(rr < 0.35 * (0.6 + 0.4 * pet) + 0.15, 1, idx)
        idx = np.where((rr > 0.55) & (rr < 0.62), 2, idx)
        idx = np.where((rr > 0.62) & (rr < 0.82) & (np.floor(a / (np.pi / 12)) % 2 == 0), 3, idx)
        idx = np.where((rr > 0.86) & (rr < 0.92), 2, idx)
        idx = np.where(rr < 0.08, 2, idx)
        corner = (np.minimum(U, w_ - U) < m * 0.18) & (np.minimum(V, h_ - V) < m * 0.18)
        idx = np.where(corner & (rr > 1.0) & ((U + V).astype(int) % 6 < 3), 1, idx)
        idx = np.where(border, np.where(edge < 2, 2, np.where((U + V).astype(int) % 4 < 2, 3, 0)), idx)
    elif kind == "sun":
        rays = (np.floor((a + np.pi) / (np.pi / 12)) % 2 == 0)
        idx = np.where(rays & (r > m * 0.12), 3, 0)
        idx = np.where(r < m * 0.12, 1, idx)
        idx = np.where(np.abs(r - m * 0.12) < 0.8, 2, idx)
        idx = np.where((r > m * 0.4) & (np.floor(r / 3) % 2 == 0), np.where(rays, 1, 0), idx)
        idx = np.where(border, np.where(edge < 2, 2, 1), idx)
    elif kind == "scales":
        R = 7.0
        row = np.floor(V / (R * 0.8))
        off = (row % 2) * R
        cxs = np.round((U - off) / (2 * R)) * 2 * R + off
        cys = row * R * 0.8
        d = np.sqrt((U - cxs) ** 2 + (V - cys) ** 2)
        idx = np.where(d < R * 0.95, np.where(d < R * 0.45, 2, 1), 0)
        idx = np.where(np.abs(d - R * 0.95) < 0.7, 3, idx)
        idx = np.where(border, np.where(edge < 2, 3, 0), idx)
    elif kind == "stars":
        P = 16
        u, v = (U % P) - P / 2, (V % P) - P / 2
        rr = np.sqrt(u ** 2 + v ** 2)
        aa = np.arctan2(v, u)
        star = rr < (P * 0.22) * (1 + 0.55 * (np.cos(aa * 4) ** 8 + np.sin(aa * 4) ** 8) * 0)  # base
        star = (np.abs(u) + np.abs(v) < P * 0.34) | ((np.abs(u) < P * 0.24) & (np.abs(v) < P * 0.24))
        idx = np.where(star, 1, 0)
        idx = np.where(rr < P * 0.08, 3, idx)
        idx = np.where(((np.abs(u) + np.abs(v) < P * 0.40) & ~star), 2, idx)
        idx = np.where(border, np.where(edge < 2, 1, 0), idx)
    elif kind == "guilloche":
        P = 12
        band = np.floor(V / (P * 1.4))
        lv = V - band * P * 1.4 - P * 0.7
        ph = U / P * 2 * np.pi
        s1 = np.abs(lv - np.sin(ph) * P * 0.32) < 1.5
        s2 = np.abs(lv + np.sin(ph) * P * 0.32) < 1.5
        over = np.cos(ph) > 0
        idx = np.where(s2, 2, 0)
        idx = np.where(s1 & (over | ~s2), 1, idx)
        idx = np.where((np.abs(lv) < 0.6) & ~s1 & ~s2 & (np.floor(U) % 3 == 0), 3, idx)
        idx = np.where(border, np.where(edge < 2, 3, 0), idx)
    elif kind == "labyrinth":
        k = np.floor(np.maximum(np.abs(X) / w_ * m, np.abs(Y) / h_ * m) / 3)
        wall = (k % 2 == 0)
        # doors that shift around each ring
        door = (np.abs(np.sin(a * 2 + k * 1.3)) < 0.18)
        idx = np.where(wall & ~door, 1, 0)
        idx = np.where(np.maximum(np.abs(X), np.abs(Y)) < 4, 2, idx)
        idx = np.where(border, np.where(edge < 2, 3, 0), idx)
    return idx


def render(w, h, v, rng):
    slug, title, fam, mortar, ground, c1, c2, c3, kind, motifs = v
    S = common.ss(w, h, 2)
    W, H = w * S, h * S
    s = min(W, H)
    t = s / 66.0  # tessera pitch
    nu, nv = int(W / t) + 1, int(H / t) + 1
    U, V = np.meshgrid(np.arange(nu, dtype=np.float32), np.arange(nv, dtype=np.float32))
    idx = motif(kind, U, V, nu, nv)
    pal = [hexrgb(c) for c in (ground, c1, c2, c3)]
    im = Image.new("RGB", (W, H), col(mortar))
    d = ImageDraw.Draw(im)
    gap = t * 0.12
    for j in range(nv):
        for i in range(nu):
            c = pal[idx[j, i]] * (0.86 + 0.2 * rng.random())
            c = c + rng.normal(0, 4, 3)
            x0, y0 = i * t + rng.normal(0, t * 0.04), j * t + rng.normal(0, t * 0.04)
            sz = t - gap
            # slightly irregular quadrilateral
            pts = [(x0 + rng.normal(0, t * 0.03), y0 + rng.normal(0, t * 0.03)),
                   (x0 + sz + rng.normal(0, t * 0.03), y0 + rng.normal(0, t * 0.03)),
                   (x0 + sz + rng.normal(0, t * 0.03), y0 + sz + rng.normal(0, t * 0.03)),
                   (x0 + rng.normal(0, t * 0.03), y0 + sz + rng.normal(0, t * 0.03))]
            d.polygon(pts, fill=col(c))
    im = im.resize((w, h), Image.LANCZOS)
    a = np.asarray(im, np.float32)
    # worn surface: light from the top left, a little dust
    Y, X = np.mgrid[0:h, 0:w].astype(np.float32)
    a = a * (1.03 - 0.08 * (X / w + Y / h) / 2)[..., None]
    a = a + rng.normal(0, 3, a.shape[:2])[..., None]
    from common import to_image
    return to_image(a)


def colour(v):
    return v[5]
