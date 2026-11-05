"""Industrial Heavy Metal: riveted steel plates, welds, gauges and hazard paint from the diesel age."""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from common import hexrgb, mix, fbm, grain, to_image, col

ID = "heavymetal"
NAME = "Industrial Heavy Metal"
TAGLINE = "Riveted steel and diesel-age paint"
DESCRIPTION = ("Close-ups of heavy machinery: riveted steel plates with brushed grain, weld seams, rust "
               "creeping from the joints, worn paint, pressure gauges and hazard stripes.")
FORMAT = "jpg"

# slug, title, family, metal, paint (None = bare steel), rust amount, feature, motifs
VARIANTS = [
    ("gunmetal", "Gunmetal", "mono", "#5a5f66", None, 0.25, "gauge", ["Bare steel", "Gauge"]),
    ("locomotive", "Locomotive", "red", "#4a4644", "#7a2a22", 0.35, "plates", ["Oxide red paint"]),
    ("olive-drab", "Olive Drab", "green", "#4a4a40", "#4f5a34", 0.3, "hazard", ["Olive drab", "Hazard stripes"]),
    ("foundry", "Foundry", "orange", "#3e3a36", None, 0.75, "pipes", ["Dark iron", "Pipes"]),
    ("navy-hull", "Navy Hull", "blue", "#4a5058", "#2f4a66", 0.3, "plates", ["Navy grey", "Hull plates"]),
    ("caution", "Caution", "yellow", "#4a4844", "#d9a52a", 0.4, "hazard", ["Yellow paint", "Hazard"]),
    ("boiler-room", "Boiler Room", "orange", "#46403a", "#8a5a2a", 0.5, "gauge", ["Copper paint", "Gauge"]),
    ("teal-machine", "Teal Machine", "cyan", "#4a504e", "#2f6a66", 0.3, "pipes", ["Machine teal"]),
    ("black-iron", "Black Iron", "mono", "#2e2f31", None, 0.45, "plates", ["Black iron", "Rivets"]),
    ("signal-red", "Signal Red", "red", "#4a4644", "#a8291f", 0.25, "gauge", ["Signal red", "Gauge"]),
]


def render(w, h, v, rng):
    slug, title, fam, metal, paint, rust, feature, motifs = v
    W, H = w, h
    s = min(W, H)
    Mt = hexrgb(metal)
    # brushed steel: stretched noise
    n = rng.random((H, max(4, W // 40))).astype(np.float32)
    brushed = np.asarray(Image.fromarray((n * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR), np.float32) / 255
    mottled = fbm(H, W, rng, base=s * 0.25, octaves=4)
    base = Mt * (0.85 + 0.12 * brushed[..., None] + 0.2 * (mottled[..., None] - 0.5))
    if paint is not None:
        Pt = hexrgb(paint)
        wear = fbm(H, W, rng, base=s * 0.08, octaves=5)
        painted = np.clip((wear - 0.3) * 10, 0, 1)[..., None]  # chipped where noise is low
        base = mix(base, Pt * (0.9 + 0.15 * mottled[..., None]), painted * 0.95)
    img = base.copy()
    # plate layout: a grid with random splits
    cols = 3 if W > H else 2
    rows = 2 if W > H else 3
    xs = np.sort(np.concatenate([[0, W], (np.arange(1, cols) + rng.uniform(-0.15, 0.15, cols - 1)) * W / cols]))
    ys = np.sort(np.concatenate([[0, H], (np.arange(1, rows) + rng.uniform(-0.15, 0.15, rows - 1)) * H / rows]))
    shade = Image.new("L", (W, H), 128)  # 128 neutral, darker shadow, lighter highlight
    ds = ImageDraw.Draw(shade)
    rustmask = Image.new("L", (W, H), 0)
    dr = ImageDraw.Draw(rustmask)
    gap = max(2, int(s * 0.004))
    rv = s * 0.011  # rivet radius
    for i in range(len(xs) - 1):
        for j in range(len(ys) - 1):
            x0, x1, y0, y1 = xs[i], xs[i + 1], ys[j], ys[j + 1]
            # seam: dark groove with light edge below and right
            ds.rectangle([x0, y0, x1, y0 + gap], fill=40)
            ds.rectangle([x0, y0 + gap, x1, y0 + gap * 2], fill=170)
            ds.rectangle([x0, y0, x0 + gap, y1], fill=40)
            ds.rectangle([x0 + gap, y0, x0 + gap * 2, y1], fill=170)
            # plate bevel: slight light on top-left, dark on bottom-right
            ds.rectangle([x0 + gap * 2, y1 - gap * 3, x1, y1], fill=100)
            # rivets along all edges
            step = rv * 4.2
            for (ax, ay, bx, by) in ((x0, y0, x1, y0), (x0, y1, x1, y1), (x0, y0, x0, y1), (x1, y0, x1, y1)):
                L = np.hypot(bx - ax, by - ay)
                for k in range(1, int(L / step)):
                    t = k * step / L
                    px, py = ax + (bx - ax) * t, ay + (by - ay) * t
                    px += rv * 2.2 if ax == bx and ax == x0 else (-rv * 2.2 if ax == bx else 0)
                    py += rv * 2.2 if ay == by and ay == y0 else (-rv * 2.2 if ay == by else 0)
                    if not (rv < px < W - rv and rv < py < H - rv):
                        continue
                    ds.ellipse([px - rv * 1.15 + rv * 0.25, py - rv * 1.15 + rv * 0.3, px + rv * 1.15 + rv * 0.25, py + rv * 1.15 + rv * 0.3], fill=50)
                    ds.ellipse([px - rv, py - rv, px + rv, py + rv], fill=150)
                    ds.ellipse([px - rv * 0.7, py - rv * 0.75, px + rv * 0.3, py + rv * 0.25], fill=205)
                    if rng.random() < rust * 0.3:
                        rr = rv * (1.0 + 1.2 * rng.random())
                        dr.ellipse([px - rr, py - rr * 0.6, px + rr, py + rr * 0.8], fill=int(110 + 100 * rng.random()))
                        dr.line([(px, py), (px + rng.normal(0, rv * 0.3), py + rv * (4 + 10 * rng.random()))], fill=90, width=max(1, int(rv * 0.5)))
            for _ in range(int(rust * 6)):  # thin rust streaks running down from a seam
                sx = x0 + (x1 - x0) * rng.random()
                dr.line([(sx, y0), (sx + rng.normal(0, s * 0.004), y0 + (y1 - y0) * (0.1 + 0.4 * rng.random()))], fill=80, width=max(1, int(s * 0.003)))
    # feature
    fl = Image.new("RGB", (W, H), (0, 0, 0))
    fm = Image.new("L", (W, H), 0)
    df, dm = ImageDraw.Draw(fl), ImageDraw.Draw(fm)
    if feature == "hazard":
        band = s * 0.14
        y0 = H * (0.62 if W > H else 0.7)
        stripe = s * 0.06
        dm.rectangle([0, y0, W, y0 + band], fill=255)
        df.rectangle([0, y0, W, y0 + band], fill=(222, 170, 30))
        k = -band
        while k < W + band:
            df.polygon([(k, y0 + band), (k + stripe, y0 + band), (k + stripe + band, y0), (k + band, y0)], fill=(25, 24, 22))
            k += stripe * 2
        ds.rectangle([0, y0 + band, W, y0 + band + gap * 2], fill=60)
    elif feature == "gauge":
        cx, cy = W * (0.68 if W > H else 0.5), H * (0.4 if W > H else 0.36)
        R = s * 0.2
        ds.ellipse([cx - R * 1.2 + R * 0.06, cy - R * 1.2 + R * 0.08, cx + R * 1.2 + R * 0.06, cy + R * 1.2 + R * 0.08], fill=40)
        dm.ellipse([cx - R * 1.2, cy - R * 1.2, cx + R * 1.2, cy + R * 1.2], fill=255)
        df.ellipse([cx - R * 1.2, cy - R * 1.2, cx + R * 1.2, cy + R * 1.2], fill=col(Mt * 1.35))
        df.ellipse([cx - R * 1.08, cy - R * 1.08, cx + R * 1.08, cy + R * 1.08], fill=col(Mt * 0.7))
        df.ellipse([cx - R, cy - R, cx + R, cy + R], fill=(232, 226, 210))
        for k in range(41):
            a = np.radians(135 + k * 270 / 40)
            l = 0.14 if k % 5 == 0 else 0.07
            df.line([(cx + np.cos(a) * R * 0.88, cy + np.sin(a) * R * 0.88), (cx + np.cos(a) * R * (0.88 - l), cy + np.sin(a) * R * (0.88 - l))], fill=(30, 30, 30), width=max(2, int(s * (0.004 if k % 5 == 0 else 0.002))))
        df.arc([cx - R * 0.8, cy - R * 0.8, cx + R * 0.8, cy + R * 0.8], 330, 405, fill=(190, 40, 30), width=int(s * 0.012))
        a = np.radians(135 + 270 * (0.3 + 0.5 * rng.random()))
        df.line([(cx - np.cos(a) * R * 0.15, cy - np.sin(a) * R * 0.15), (cx + np.cos(a) * R * 0.78, cy + np.sin(a) * R * 0.78)], fill=(180, 30, 25), width=int(s * 0.008))
        r = R * 0.08
        df.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(40, 40, 40))
        for k in range(6):  # bolts on the bezel
            a = k * np.pi / 3 + 0.3
            bx, by = cx + np.cos(a) * R * 1.14, cy + np.sin(a) * R * 1.14
            df.ellipse([bx - rv * 0.7, by - rv * 0.7, bx + rv * 0.7, by + rv * 0.7], fill=col(Mt * 1.6))
    elif feature == "pipes":
        n = 3
        for k in range(n):
            if W > H:
                px = W * (0.12 + 0.1 * k)
                R = s * (0.05 - 0.008 * k)
                ds.rectangle([px - R + R * 0.4, 0, px + R + R * 0.4, H], fill=45)
                dm.rectangle([px - R, 0, px + R, H], fill=255)
                for q in range(24):
                    t = q / 23
                    c = Mt * (0.6 + 0.9 * np.clip(1 - abs(t - 0.3) * 2, 0, 1))
                    df.rectangle([px - R + 2 * R * t, 0, px - R + 2 * R * (t + 1 / 23) + 1, H], fill=col(c))
                for yy in np.arange(H * 0.2, H, H * 0.35):  # flanges
                    df.rectangle([px - R * 1.25, yy, px + R * 1.25, yy + R * 0.4], fill=col(Mt * 1.15))
                    df.rectangle([px - R * 1.25, yy + R * 0.32, px + R * 1.25, yy + R * 0.4], fill=col(Mt * 0.6))
            else:
                py = H * (0.12 + 0.08 * k)
                R = s * (0.05 - 0.008 * k)
                ds.rectangle([0, py - R + R * 0.4, W, py + R + R * 0.4], fill=45)
                dm.rectangle([0, py - R, W, py + R], fill=255)
                for q in range(24):
                    t = q / 23
                    c = Mt * (0.6 + 0.9 * np.clip(1 - abs(t - 0.3) * 2, 0, 1))
                    df.rectangle([0, py - R + 2 * R * t, W, py - R + 2 * R * (t + 1 / 23) + 1], fill=col(c))
                for xx in np.arange(W * 0.2, W, W * 0.4):
                    df.rectangle([xx, py - R * 1.25, xx + R * 0.4, py + R * 1.25], fill=col(Mt * 1.15))
    # vertical weld bead somewhere
    wx = W * (0.45 + 0.1 * rng.random())
    for yy in np.arange(0, H, s * 0.012):
        r = s * 0.008
        ds.ellipse([wx - r, yy - r * 0.6, wx + r, yy + r * 0.6], fill=170)
        ds.arc([wx - r, yy - r * 0.6, wx + r, yy + r * 0.6], 0, 180, fill=70, width=max(1, int(s * 0.002)))
    sh = np.asarray(shade.filter(ImageFilter.GaussianBlur(max(1, s * 0.0015))), np.float32)[..., None]
    img = img * (sh / 128) ** 0.9
    rm = np.asarray(rustmask.filter(ImageFilter.GaussianBlur(s * 0.003)), np.float32)[..., None] / 255
    rn = fbm(H, W, rng, base=s * 0.03, octaves=4)[..., None]
    rm = np.clip(rm * (0.4 + rn) * 1.1, 0, 1) * 0.8
    rust_c = mix(np.array([110, 52, 24.0]), np.array([170, 90, 40.0]), rn)
    img = mix(img, rust_c * (0.7 + 0.5 * brushed[..., None]), rm * 0.85)
    m = np.asarray(fm, np.float32)[..., None] / 255
    img = img * (1 - m) + np.asarray(fl, np.float32) * m * (0.9 + 0.15 * mottled[..., None])
    # overall grime and soft top light
    Y = np.mgrid[0:H, 0:W][0].astype(np.float32)
    img = img * (1.08 - 0.25 * (Y / H) ** 1.5)[..., None]
    img = grain(img, rng, 5)
    return to_image(img)


def colour(v):
    return v[4] if v[4] else v[3]
