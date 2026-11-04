"""Art Deco: fans, sunbursts and stepped towers in metal lines on lacquer."""
import numpy as np
from PIL import Image, ImageDraw
from common import hexrgb, mix, grain, to_image, col

ID = "artdeco"
NAME = "Art Deco"
TAGLINE = "Fans, sunbursts, stepped towers"
DESCRIPTION = ("Thin metal lines on deep lacquer: scalloped fans, rising suns and stepped towers, "
               "the ornament of 1920s cinemas, liners and lobbies.")
FORMAT = "png"

# slug, title, family, ground, metal, second tone, layout, motifs
VARIANTS = [
    ("gatsby", "Gatsby", "yellow", "#101416", "#c9a45c", "#1d2a2e", "fans", ["Gold fans", "Black lacquer"]),
    ("chrysler", "Chrysler", "mono", "#14161a", "#d7d9dc", "#2a2e35", "tower", ["Steel crown", "Sunburst"]),
    ("emerald-lobby", "Emerald Lobby", "green", "#0f2e26", "#d9b56a", "#174238", "sunrise", ["Rising sun", "Emerald"]),
    ("normandie", "Normandie", "blue", "#0e1a33", "#e2c88f", "#16284d", "chevrons", ["Ziggurat chevrons"]),
    ("rose-cinema", "Rose Cinema", "pink", "#2b1420", "#e7b7a3", "#3d1d2d", "arches", ["Nested arches"]),
    ("ivory-fan", "Ivory Fan", "yellow", "#efe7d6", "#8a6a2f", "#e2d6bd", "fans", ["Bronze on ivory"]),
    ("oxblood", "Oxblood", "red", "#3a0f12", "#d6a85c", "#511a1d", "tower", ["Gold tower", "Oxblood"]),
    ("peacock", "Peacock", "cyan", "#0b2a30", "#c7b07a", "#123c44", "sunrise", ["Peacock sun"]),
    ("onyx", "Onyx", "mono", "#0c0c0d", "#bfa16a", "#1b1b1d", "chevrons", ["Onyx", "Brass"]),
    ("violet-hour", "Violet Hour", "violet", "#1e1530", "#d9c3a0", "#2c2045", "arches", ["Violet arches"]),
]


def render(w, h, v, rng):
    slug, title, fam, ground, metal, tone, layout, motifs = v
    S = 3
    W, H = w * S, h * S
    im = Image.new("RGB", (W, H), col(ground))
    d = ImageDraw.Draw(im)
    m, t2 = col(metal), col(tone)
    s = min(W, H)
    lw = max(2, int(s * 0.0022))

    if layout == "fans":
        R = s * 0.11
        rows = int(H / (R * 0.5)) + 3
        for r in range(rows):
            cy = r * R * 0.5
            off = (r % 2) * R
            for i in range(-1, int(W / (2 * R)) + 2):
                cx = i * 2 * R + off
                d.pieslice([cx - R, cy - R, cx + R, cy + R], 180, 360, fill=col(ground), outline=m, width=lw * 2)
                for k in range(1, 12):
                    a = np.pi + k * np.pi / 12
                    d.line([(cx, cy), (cx + np.cos(a) * R * 0.97, cy + np.sin(a) * R * 0.97)], fill=m, width=lw)
                d.pieslice([cx - R * 0.32, cy - R * 0.32, cx + R * 0.32, cy + R * 0.32], 180, 360, fill=t2, outline=m, width=lw)
                d.arc([cx - R * 0.7, cy - R * 0.7, cx + R * 0.7, cy + R * 0.7], 180, 360, fill=m, width=lw)
    elif layout in ("sunrise", "tower"):
        cx = W / 2
        cy = H * (0.62 if layout == "sunrise" else 0.55)
        L = max(W, H) * 1.2
        n = 36
        for k in range(n):
            a0 = np.pi + k * np.pi / n
            a1 = a0 + np.pi / n
            if k % 2 == 0:
                d.polygon([(cx, cy), (cx + np.cos(a0) * L, cy + np.sin(a0) * L), (cx + np.cos(a1) * L, cy + np.sin(a1) * L)], fill=t2)
        for k in range(n + 1):
            a = np.pi + k * np.pi / n
            d.line([(cx, cy), (cx + np.cos(a) * L, cy + np.sin(a) * L)], fill=m, width=lw)
        for rr in (0.16, 0.22, 0.27):
            r = s * rr
            d.arc([cx - r, cy - r, cx + r, cy + r], 180, 360, fill=m, width=lw * (3 if rr == 0.16 else 1))
        r = s * 0.15
        d.pieslice([cx - r, cy - r, cx + r, cy + r], 180, 360, fill=col(ground))
        for k in range(7):
            yy = cy - r + k * r / 7
            half = np.sqrt(max(r * r - (cy - yy) ** 2, 0))
            d.line([(cx - half, yy), (cx + half, yy)], fill=m, width=lw)
        d.rectangle([0, cy, W, H], fill=col(ground))
        for k in range(16):
            y = cy + (k + 1) ** 1.6 * s * 0.006
            d.line([(0, y), (W, y)], fill=m, width=lw)
        if layout == "tower":
            # stepped tower with a crown of arches
            tw = s * 0.26
            base_y = H
            steps = [(1.0, 0.30), (0.78, 0.40), (0.58, 0.50), (0.4, 0.58)]
            for fw, fh in steps:
                x0, x1 = cx - tw * fw / 2, cx + tw * fw / 2
                y0 = H - (H - cy) - s * fh * 0.6 + s * 0.2
                d.rectangle([x0, y0, x1, base_y], fill=col(ground), outline=m, width=lw * 2)
                for k in range(1, int(fw * 10)):
                    x = x0 + k * (x1 - x0) / int(fw * 10)
                    d.line([(x, y0 + s * 0.02), (x, base_y)], fill=m, width=lw)
            top = H - (H - cy) - s * 0.58 * 0.6 + s * 0.2
            for k in range(5):
                r = tw * 0.2 * (1 - k * 0.18)
                d.arc([cx - r, top - r, cx + r, top + r], 180, 360, fill=m, width=lw * 2)
            d.line([(cx, top - tw * 0.2), (cx, top - tw * 0.55)], fill=m, width=lw * 2)
    elif layout == "chevrons":
        step = s * 0.05
        for k in range(-2, int((H + W) / step) + 2):
            y = k * step
            pts = []
            n = int(W / (s * 0.18)) + 2
            for i in range(n + 1):
                x = i * s * 0.18
                pts.append((x, y - (s * 0.09 if i % 2 else 0)))
            d.line(pts, fill=m if k % 3 else t2, width=lw * (3 if k % 3 == 0 else 1))
        # central medallion
        cx, cy = W / 2, H * 0.42
        r = s * 0.2
        d.ellipse([cx - r * 1.08, cy - r * 1.08, cx + r * 1.08, cy + r * 1.08], fill=col(ground), outline=m, width=lw * 2)
        for k in range(24):
            a = k * np.pi / 12
            d.line([(cx + np.cos(a) * r * 0.3, cy + np.sin(a) * r * 0.3), (cx + np.cos(a) * r, cy + np.sin(a) * r)], fill=m, width=lw)
        d.ellipse([cx - r * 0.3, cy - r * 0.3, cx + r * 0.3, cy + r * 0.3], fill=t2, outline=m, width=lw * 2)
    elif layout == "arches":
        cols_ = 5 if W > H else 3
        aw = W / cols_
        for i in range(cols_):
            cx = aw * (i + 0.5)
            for k in range(9):
                f = 1 - k * 0.1
                hw = aw * 0.42 * f
                top = H * 0.18 + (1 - f) * H * 0.25
                d.rectangle([cx - hw, top + hw, cx + hw, H], outline=m, width=lw)
                d.arc([cx - hw, top, cx + hw, top + 2 * hw], 180, 360, fill=m, width=lw)
                if k == 4:
                    d.rectangle([cx - hw + lw, top + hw, cx + hw - lw, H], fill=t2)
                    d.pieslice([cx - hw + lw, top + lw, cx + hw - lw, top + 2 * hw - lw], 180, 360, fill=t2)
            d.ellipse([cx - aw * 0.05, H * 0.12 - aw * 0.05, cx + aw * 0.05, H * 0.12 + aw * 0.05], outline=m, width=lw * 2)
    # double frame
    mg = s * 0.035
    d.rectangle([mg, mg, W - mg, H - mg], outline=m, width=lw * 3)
    d.rectangle([mg * 1.5, mg * 1.5, W - mg * 1.5, H - mg * 1.5], outline=m, width=lw)
    im = im.resize((w, h), Image.LANCZOS)
    return im


def colour(v):
    return v[4] if v[2] in ("yellow", "mono") else v[3]
