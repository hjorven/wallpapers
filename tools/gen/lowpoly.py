"""Silicon Low-Poly: faceted digital landscapes, silicon wafers and gold circuit traces."""
import numpy as np
from PIL import Image, ImageDraw
from common import hexrgb, mix, fbm, glow, grain, to_image, col

ID = "lowpoly"
NAME = "Silicon Low-Poly"
TAGLINE = "Faceted terrain, wafers and gold traces"
DESCRIPTION = ("Sharp low-poly facets lit like cut crystal, some carrying gold circuit traces, others "
               "showing a silicon wafer full of dies shimmering under ultraviolet light.")
FORMAT = "png"

# slug, title, family, dark, mid, light, accent (traces, glow), overlay, motifs
VARIANTS = [
    ("uv-wafer", "UV Wafer", "violet", "#14082a", "#5a2a9a", "#c48aff", "#5ff2ff", "wafer", ["Silicon wafer", "Ultraviolet"]),
    ("gold-trace", "Gold Trace", "green", "#06140f", "#145a3a", "#3fae7a", "#f2c45a", "traces", ["Gold traces", "PCB green"]),
    ("crystal-dusk", "Crystal Dusk", "pink", "#1a0a24", "#a03a7a", "#ffa0c8", "#ffe08a", "none", ["Facets", "Dusk"]),
    ("ice-facets", "Ice Facets", "cyan", "#04161e", "#1f6a80", "#bff4ff", "#ffffff", "none", ["Ice facets"]),
    ("die-shot", "Die Shot", "blue", "#060c22", "#23409a", "#7aa8ff", "#ffcf5a", "die", ["Die shot", "Gold pads"]),
    ("ember-mesh", "Ember Mesh", "orange", "#1a0a04", "#9a3a12", "#ffb35a", "#fff0a0", "traces", ["Ember", "Traces"]),
    ("graphite", "Graphite", "mono", "#0e0f11", "#3a3d42", "#b8bec6", "#f2c45a", "die", ["Graphite", "Gold"]),
    ("teal-wafer", "Teal Wafer", "cyan", "#03141a", "#0f5a66", "#5fe0d0", "#ff7ad8", "wafer", ["Teal wafer"]),
    ("lime-chip", "Lime Chip", "green", "#0a1404", "#3a6a14", "#b8f25a", "#f2f2f2", "traces", ["Lime", "White traces"]),
    ("ruby-cut", "Ruby Cut", "red", "#1a0408", "#8a1424", "#ff6a7a", "#ffd0a0", "none", ["Ruby facets"]),
]


def render(w, h, v, rng):
    slug, title, fam, dark, midc, light, accent, overlay, motifs = v
    S = 2
    W, H = w * S, h * S
    s = min(W, H)
    Dk, Md, Lt, Ac = (hexrgb(c) for c in (dark, midc, light, accent))
    # jittered grid of points and a height field
    cell = s / 11
    nx, ny = int(W / cell) + 3, int(H / cell) + 3
    gx, gy = np.meshgrid(np.arange(nx) - 1.0, np.arange(ny) - 1.0)
    px = (gx + rng.uniform(-0.38, 0.38, gx.shape)) * cell
    py = (gy + rng.uniform(-0.38, 0.38, gy.shape)) * cell
    hf = fbm(H + int(cell * 4), W + int(cell * 4), rng, base=s * 0.5, octaves=3)
    hz = hf[np.clip((py + cell * 2).astype(int), 0, hf.shape[0] - 1), np.clip((px + cell * 2).astype(int), 0, hf.shape[1] - 1)] * s * 0.6
    light_dir = np.array([-0.5, -0.6, 0.62])
    light_dir /= np.linalg.norm(light_dir)
    im = Image.new("RGB", (W, H), col(Dk))
    d = ImageDraw.Draw(im)
    Y_centre = H * 0.4
    for j in range(ny - 1):
        for i in range(nx - 1):
            q = [(i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1)]
            tris = [(q[0], q[1], q[2]), (q[0], q[2], q[3])] if (i + j) % 2 == 0 else [(q[0], q[1], q[3]), (q[1], q[2], q[3])]
            for t in tris:
                P = np.array([[px[b, a], py[b, a], hz[b, a]] for a, b in t])
                n = np.cross(P[1] - P[0], P[2] - P[0])
                n = n / (np.linalg.norm(n) + 1e-9)
                if n[2] < 0:
                    n = -n
                lam = np.clip(np.dot(n, light_dir), 0, 1)
                cy = P[:, 1].mean()
                cx = P[:, 0].mean()
                # base colour by height and a soft radial glow around the upper middle
                hgt = P[:, 2].mean() / (s * 0.6)
                rad = np.clip(1 - np.hypot(cx - W / 2, cy - Y_centre) / (s * 0.9), 0, 1)
                base = mix(Dk, Md, np.clip(hgt * 1.2 + rad * 0.4, 0, 1))
                c = mix(base * (0.55 + 0.6 * lam), Lt, np.clip((lam - 0.75) * 2.5, 0, 1) * (0.4 + 0.6 * rad))
                d.polygon([(p[0], p[1]) for p in P], fill=col(c))
    a = np.asarray(im, np.float32)
    gl = Image.new("RGB", (W, H), (0, 0, 0))
    dg = ImageDraw.Draw(gl)
    lw = max(2, int(s * 0.0025))
    if overlay == "traces":
        pitch = s * 0.035
        for _ in range(int(14 * W * H / (s * s))):
            x = round(rng.random() * W / pitch) * pitch
            y = round(rng.random() * H / pitch) * pitch
            pts = [(x, y)]
            dirn = rng.integers(0, 4)
            for _seg in range(int(rng.integers(2, 6))):
                L = pitch * int(rng.integers(2, 7))
                dx, dy = [(1, 0), (0, 1), (-1, 0), (0, -1)][dirn]
                x, y = x + dx * L, y + dy * L
                pts.append((x, y))
                # bend 45 degrees then straighten
                if rng.random() < 0.7:
                    ddx, ddy = [(1, 1), (-1, 1), (-1, -1), (1, -1)][int(rng.integers(0, 4))]
                    x, y = x + ddx * pitch, y + ddy * pitch
                    pts.append((x, y))
                dirn = (dirn + rng.choice([-1, 1])) % 4
            dg.line(pts, fill=col(Ac * 0.8), width=lw)
            for (ex, ey) in (pts[0], pts[-1]):
                r = pitch * 0.22
                dg.ellipse([ex - r, ey - r, ex + r, ey + r], outline=col(Ac), width=lw)
        a = a + glow(np.asarray(gl, np.float32), s, 0.002, 0.012, 0.6, 0.4)
    elif overlay == "wafer":
        cx, cy = W / 2, H / 2
        R = s * 0.42
        wafer = Image.new("L", (W, H), 0)
        dw = ImageDraw.Draw(wafer)
        dw.ellipse([cx - R, cy - R, cx + R, cy + R], fill=255)
        dw.rectangle([cx - R * 0.3, cy + R * 0.97, cx + R * 0.3, cy + R * 1.1], fill=0)  # flat edge
        m = np.asarray(wafer, np.float32)[..., None] / 255
        Yg, Xg = np.mgrid[0:H, 0:W].astype(np.float32)
        # thin-film rainbow sheen across the wafer
        ang = np.arctan2(Yg - cy, Xg - cx)
        rr = np.hypot(Xg - cx, Yg - cy) / R
        sheen = np.stack([np.sin(ang * 2 + rr * 6 + k * 2.1) * 0.5 + 0.5 for k in range(3)], -1)
        wcol = mix(Md * 0.6, mix(Lt, Ac, sheen), 0.55)
        a = a * (1 - m * 0.92) + wcol * m * 0.92
        die = s * 0.045
        for yy in np.arange(cy - R, cy + R, die):
            for xx in np.arange(cx - R, cx + R, die):
                if np.hypot(xx + die / 2 - cx, yy + die / 2 - cy) < R * 0.95:
                    dg.rectangle([xx, yy, xx + die, yy + die], outline=col(Lt * 0.5), width=1)
                    if rng.random() < 0.15:
                        dg.rectangle([xx + die * 0.3, yy + die * 0.3, xx + die * 0.7, yy + die * 0.7], fill=col(Ac * 0.6))
        dg.ellipse([cx - R, cy - R, cx + R, cy + R], outline=col(Lt), width=lw)
        a = a + glow(np.asarray(gl, np.float32), s, 0.002, 0.02, 0.5, 0.6)
    elif overlay == "die":
        # a chip die: blocks of logic, a pad ring and bond wires
        cx, cy = W / 2, H / 2
        D = s * 0.3
        x0, y0, x1, y1 = cx - D, cy - D, cx + D, cy + D
        d2 = ImageDraw.Draw(im)
        dg.rectangle([x0, y0, x1, y1], outline=col(Ac), width=lw * 2)
        blk = Image.new("RGB", (W, H), (0, 0, 0))
        db = ImageDraw.Draw(blk)
        for _ in range(28):
            bw, bh = D * (0.1 + 0.4 * rng.random()), D * (0.1 + 0.4 * rng.random())
            bx, by = x0 + D * 0.15 + rng.random() * (2 * D * 0.85 - bw), y0 + D * 0.15 + rng.random() * (2 * D * 0.85 - bh)
            c = mix(Md, Lt, rng.random() * 0.6)
            db.rectangle([bx, by, bx + bw, by + bh], fill=col(c * 0.5), outline=col(c), width=1)
            for k in range(int(bh / (s * 0.006))):
                db.line([(bx + 2, by + k * s * 0.006), (bx + bw - 2, by + k * s * 0.006)], fill=col(c * 0.7), width=1)
        bm = (np.asarray(blk, np.float32).sum(-1, keepdims=True) > 0).astype(np.float32)
        a = a * (1 - bm * 0.85) + np.asarray(blk, np.float32) * 0.85 * bm
        n_ = 14
        for k in range(n_):
            t = (k + 0.5) / n_
            for (px_, py_, ox, oy) in ((x0 + 2 * D * t, y0, 0, -1), (x0 + 2 * D * t, y1, 0, 1), (x0, y0 + 2 * D * t, -1, 0), (x1, y0 + 2 * D * t, 1, 0)):
                r = s * 0.008
                dg.rectangle([px_ - r - ox * r * 2, py_ - r - oy * r * 2, px_ + r - ox * r * 2, py_ + r - oy * r * 2], fill=col(Ac))
                ex, ey = px_ + ox * s * 0.12, py_ + oy * s * 0.12
                ex += (px_ - cx) * 0.25 * abs(oy)
                ey += (py_ - cy) * 0.25 * abs(ox)
                dg.line([(px_ - ox * r * 2, py_ - oy * r * 2), (ex, ey)], fill=col(Ac * 0.8), width=max(1, lw // 2))
                dg.rectangle([ex - r * 1.5, ey - r * 1.5, ex + r * 1.5, ey + r * 1.5], outline=col(Ac), width=1)
        a = a + glow(np.asarray(gl, np.float32), s, 0.002, 0.015, 0.7, 0.5)
    a = grain(a, rng, 2)
    return to_image(a).resize((w, h), Image.LANCZOS)


def colour(v):
    return v[5]
