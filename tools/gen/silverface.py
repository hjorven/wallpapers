"""Silver Face: close-ups of late-1970s hi-fi vacuum fluorescent displays behind smoked glass."""
from pathlib import Path
import numpy as np
import common
from PIL import Image, ImageDraw, ImageFont
from common import hexrgb, mix, glow, grain, to_image, col

ID = "silverface"
NAME = "Silver Face"
TAGLINE = "Glowing VFD displays behind smoked glass"
DESCRIPTION = ("Close-ups of the vacuum fluorescent displays of late-1970s silver hi-fi: cyan-green "
               "phosphor segments under a fine metal mesh, thin filament wires, the ghost of unlit "
               "segments and printed scales on the smoked glass, framed by brushed aluminium.")
FORMAT = "jpg"

# slug, title, family, vfd colour, warm filter colour, frame, blocks top to bottom, motifs
VARIANTS = [
    ("peak-level", "Peak Level", "cyan", "#43ffd2", "#ff4a3a", "#c9ccd0", ["levels", "freq", "spectrum", "counter"], ["Level meter", "Cyan VFD"]),
    ("fm-stereo", "FM Stereo", "cyan", "#55f5e2", "#ffab3a", "#cfd1d3", ["freq", "signal", "levels", "clock"], ["Tuner", "Stereo"]),
    ("analyser", "Analyser", "blue", "#5fd2ff", "#ff4a6a", "#c8cbcf", ["spectrum", "levels", "freq", "signal"], ["Spectrum analyser"]),
    ("tape-counter", "Tape Counter", "green", "#6dff9e", "#ff4a3a", "#c4c7ca", ["counter", "levels", "spectrum", "clock"], ["Tape counter", "Green VFD"]),
    ("champagne", "Champagne", "yellow", "#43ffd2", "#ffb03a", "#d6c7a6", ["levels", "spectrum", "freq", "counter"], ["Champagne frame"]),
    ("amber", "Amber", "orange", "#ffb24a", "#ff4a3a", "#c9ccd0", ["freq", "levels", "signal", "spectrum"], ["Amber VFD"]),
    ("black-face", "Black Face", "mono", "#43ffd2", "#ff4a3a", "#2a2b2d", ["spectrum", "freq", "levels", "counter"], ["Black frame"]),
    ("midnight-blue", "Midnight Blue", "blue", "#6aa8ff", "#ff5a4a", "#bfc4ca", ["clock", "levels", "freq", "spectrum"], ["Blue VFD", "Clock"]),
    ("studio", "Studio", "cyan", "#2fffc4", "#ff2d2d", "#cdd0d2", ["levels", "counter", "levels", "spectrum"], ["Studio meters"]),
    ("night-green", "Night Green", "green", "#86ff6a", "#ffb03a", "#3a3c3f", ["signal", "freq", "spectrum", "levels"], ["Green VFD", "Dark frame"]),
]

SEG = {"0": "abcdef", "1": "bc", "2": "abged", "3": "abgcd", "4": "fgbc", "5": "afgcd",
       "6": "afgedc", "7": "abc", "8": "abcdefg", "9": "abcdfg", "-": "g", " ": ""}

FONT_DIR = Path(__file__).resolve().parent / "fonts"
FONT_PATHS = [str(FONT_DIR / "DejaVuSans-Bold.ttf"), "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]


def font(size):
    for p in FONT_PATHS:
        try:
            return ImageFont.truetype(p, int(size))
        except OSError:
            pass
    return ImageFont.load_default()


class Panel:
    """Three layers: lit phosphor, unlit phosphor (ghost) and printed legends."""

    def __init__(self, W, H):
        self.lit = Image.new("RGB", (W, H), (0, 0, 0))
        self.ghost = Image.new("L", (W, H), 0)
        self.ink = Image.new("L", (W, H), 0)
        self.dl, self.dg, self.di = ImageDraw.Draw(self.lit), ImageDraw.Draw(self.ghost), ImageDraw.Draw(self.ink)

    def seg(self, poly, on, c):
        self.dg.polygon(poly, fill=255)
        if on:
            self.dl.polygon(poly, fill=col(c))

    def rect(self, box, on, c):
        self.seg([(box[0], box[1]), (box[2], box[1]), (box[2], box[3]), (box[0], box[3])], on, c)

    def text(self, xy, s, size, anchor="la", fill=255):
        self.di.text(xy, s, font=font(size), fill=fill, anchor=anchor)

    def lit_text(self, xy, s, size, c, anchor="la"):
        self.dg.text(xy, s, font=font(size), fill=255, anchor=anchor)
        self.dl.text(xy, s, font=font(size), fill=col(c), anchor=anchor)


def digit(p, x, y, dw, dh, ch, c, slant=0.12):
    t = dw * 0.2
    g = t * 0.18  # gap between segments
    def P(px, py):  # italic: shift x by height
        return (px + (y + dh - py) * slant, py)
    a = [P(x + t + g, y), P(x + dw - t - g, y), P(x + dw - t * 1.5 - g, y + t), P(x + t * 1.5 + g, y + t)]
    dd = [P(x + t * 1.5 + g, y + dh - t), P(x + dw - t * 1.5 - g, y + dh - t), P(x + dw - t - g, y + dh), P(x + t + g, y + dh)]
    m = y + dh / 2
    gg = [P(x + t + g, m), P(x + t * 1.5 + g, m - t / 2), P(x + dw - t * 1.5 - g, m - t / 2), P(x + dw - t - g, m), P(x + dw - t * 1.5 - g, m + t / 2), P(x + t * 1.5 + g, m + t / 2)]
    f = [P(x, y + t + g), P(x + t, y + t * 1.5 + g), P(x + t, m - t * 0.5 - g), P(x, m - g)]
    e = [P(x, m + g), P(x + t, m + t * 0.5 + g), P(x + t, y + dh - t * 1.5 - g), P(x, y + dh - t - g)]
    b = [P(x + dw, y + t + g), P(x + dw - t, y + t * 1.5 + g), P(x + dw - t, m - t * 0.5 - g), P(x + dw, m - g)]
    cc = [P(x + dw, m + g), P(x + dw - t, m + t * 0.5 + g), P(x + dw - t, y + dh - t * 1.5 - g), P(x + dw, y + dh - t - g)]
    lit = SEG.get(ch, "")
    for k, poly in zip("abcdefg", (a, b, cc, dd, e, f, gg)):
        p.seg(poly, k in lit, c)


LIGHT = [str(FONT_DIR / "DejaVuSans.ttf")]


def lfont(size):
    try:
        return ImageFont.truetype(LIGHT[0], max(6, int(size)))
    except OSError:
        return font(size)


def dot(p, cx, cy, r, on, c):
    p.seg([(cx - r, cy - r * 0.6), (cx + r, cy - r * 0.6), (cx + r, cy + r * 0.6), (cx - r, cy + r * 0.6)], on, c)


def window(p, kind, x0, y0, x1, y1, V, R, rng):
    """Sparse VFD content inside one display window, sized like the real thing."""
    w, h = x1 - x0, y1 - y0
    small = h * 0.085
    if kind == "power":
        labels = [".01", ".05", ".1", ".5", "1", "3", "5", "10", "20", "50", "100"]
        n = len(labels)
        xs = np.linspace(x0 + w * 0.2, x1 - w * 0.12, n)
        for k, lab in enumerate(("L", "R")):
            cy = y0 + h * (0.34 + 0.3 * k)
            lvl = int(rng.integers(4, n))
            p.dg.text((x0 + w * 0.12, cy), lab, font=lfont(small * 1.2), fill=255, anchor="mm")
            p.dl.text((x0 + w * 0.12, cy), lab, font=lfont(small * 1.2), fill=col(V), anchor="mm")
            for i, x in enumerate(xs):
                dot(p, x, cy, h * 0.035, i < lvl, R if i == n - 1 else V)
        for x, lab in zip(xs, labels):
            p.dg.text((x, y0 + h * 0.49), lab, font=lfont(small), fill=255, anchor="mm")
            p.dl.text((x, y0 + h * 0.49), lab, font=lfont(small), fill=col(V * 0.85), anchor="mm")
        p.dg.text((x1 - w * 0.05, y0 + h * 0.49), "W", font=lfont(small), fill=255, anchor="mm")
        p.dl.text((x1 - w * 0.05, y0 + h * 0.49), "W", font=lfont(small), fill=col(V * 0.85), anchor="mm")
        for lab, yy in (("8Ω", 0.3), ("dB", 0.7)):
            p.dg.text((x1 - w * 0.05, y0 + h * yy), lab, font=lfont(small * 0.9), fill=255, anchor="mm")
    elif kind == "cd":
        dh = h * 0.34
        dw = dh * 0.5
        y = y0 + h * 0.18
        track, idx = int(rng.integers(1, 15)), 1
        mm, ss = int(rng.integers(0, 6)), int(rng.integers(0, 60))
        x = x0 + w * 0.22
        for ch in f"{track:2d}":
            digit(p, x, y, dw, dh, ch, V)
            x += dw * 1.3
        p.dl.text((x, y + dh), "track", font=lfont(small * 0.8), fill=col(V * 0.8), anchor="lb")
        p.dg.text((x, y + dh), "track", font=lfont(small * 0.8), fill=255, anchor="lb")
        x += w * 0.08
        digit(p, x, y, dw, dh, str(idx), V)
        p.dl.text((x + dw * 1.3, y + dh), "index", font=lfont(small * 0.8), fill=col(V * 0.8), anchor="lb")
        x += w * 0.12
        digit(p, x, y, dw, dh, str(mm), V)
        x += dw * 1.3
        r = dw * 0.09
        for fy in (0.3, 0.7):
            p.seg([(x, y + dh * fy - r), (x + 2 * r, y + dh * fy - r), (x + 2 * r, y + dh * fy + r), (x, y + dh * fy + r)], True, V)
        x += dw * 0.4
        for ch in f"{ss:02d}":
            digit(p, x, y, dw, dh, ch, V)
            x += dw * 1.3
        p.dl.text((x - dw * 3.2, y + dh + small * 0.9), "min", font=lfont(small * 0.8), fill=col(V * 0.8), anchor="lm")
        p.dl.text((x - dw * 1.2, y + dh + small * 0.9), "sec", font=lfont(small * 0.8), fill=col(V * 0.8), anchor="lm")
        # a red boxed indicator
        bx = x + w * 0.04
        on = rng.random() < 0.7
        p.seg([(bx, y), (bx + w * 0.09, y), (bx + w * 0.09, y + small * 1.5), (bx, y + small * 1.5)], on, R)
        p.di.text((bx + w * 0.045, y + small * 0.75), "random", font=lfont(small), fill=255 if on else 0, anchor="mm")
        # calendar of track numbers along the bottom
        n = 20
        cy = y0 + h * 0.8
        for i in range(n):
            xx = x0 + w * 0.14 + i * (w * 0.7) / n
            lit = i < track + int(rng.integers(3, 8))
            txt = str(i + 1)
            p.dg.text((xx, cy), txt, font=lfont(small * 1.1), fill=255, anchor="mm")
            if lit:
                p.dl.text((xx, cy), txt, font=lfont(small * 1.1), fill=col(V), anchor="mm")
        p.seg([(x0 + w * 0.86, cy - small * 0.6), (x0 + w * 0.86 + small, cy), (x0 + w * 0.86, cy + small * 0.6)], True, R)
    elif kind == "tuner":
        dh = h * 0.42
        dw = dh * 0.5
        y = y0 + h * 0.22
        x = x0 + w * 0.3
        for ch in f"{rng.uniform(87.5, 108):5.1f}":
            if ch == ".":
                r = dw * 0.1
                p.seg([(x - dw * 0.18, y + dh - 2 * r), (x - dw * 0.18 + 2 * r, y + dh - 2 * r), (x - dw * 0.18 + 2 * r, y + dh), (x - dw * 0.18, y + dh)], True, V)
                x += dw * 0.12
                continue
            digit(p, x, y, dw, dh, ch, V)
            x += dw * 1.3
        p.dl.text((x + dw * 0.2, y + dh), "MHz", font=lfont(small), fill=col(V * 0.9), anchor="lb")
        p.dg.text((x + dw * 0.2, y + dh), "MHz", font=lfont(small), fill=255, anchor="lb")
        p.dl.text((x0 + w * 0.12, y + dh * 0.3), "FM", font=lfont(small * 1.4), fill=col(V), anchor="lm")
        p.dg.text((x0 + w * 0.12, y + dh * 0.3), "FM", font=lfont(small * 1.4), fill=255, anchor="lm")
        p.dg.text((x0 + w * 0.12, y + dh * 0.8), "AM", font=lfont(small * 1.4), fill=255, anchor="lm")
        bx = x + dw * 0.2
        p.seg([(bx, y), (bx + w * 0.1, y), (bx + w * 0.1, y + small * 1.5), (bx, y + small * 1.5)], True, R)
        p.di.text((bx + w * 0.05, y + small * 0.75), "stereo", font=lfont(small), fill=255, anchor="mm")
        for i in range(7):  # signal dots
            dot(p, x0 + w * 0.3 + i * w * 0.035, y0 + h * 0.85, h * 0.025, i < int(rng.integers(3, 7)), V)
        p.dg.text((x0 + w * 0.3 + 7.3 * w * 0.035, y0 + h * 0.85), "signal", font=lfont(small * 0.8), fill=255, anchor="lm")
    elif kind == "deck":
        dh = h * 0.36
        dw = dh * 0.5
        y = y0 + h * 0.16
        x = x0 + w * 0.14
        for ch in f"{int(rng.integers(0, 999)):03d}":
            digit(p, x, y, dw, dh, ch, V)
            x += dw * 1.3
        p.dg.text((x0 + w * 0.14, y + dh + small * 1.1), "counter", font=lfont(small * 0.85), fill=255, anchor="lm")
        sx = x + w * 0.05
        sz = dh * 0.5
        playing = rng.random() < 0.7
        p.seg([(sx, y + dh * 0.2), (sx + sz, y + dh * 0.2 + sz / 2), (sx, y + dh * 0.2 + sz)], playing, V)
        p.seg([(sx + sz * 1.6, y + dh * 0.2), (sx + sz * 2.4, y + dh * 0.2), (sx + sz * 2.4, y + dh * 0.2 + sz), (sx + sz * 1.6, y + dh * 0.2 + sz)], not playing, V)
        p.seg([(sx + sz * 3.2, y + dh * 0.2), (sx + sz * 4.4, y + dh * 0.2), (sx + sz * 4.4, y + dh * 0.2 + small * 1.5), (sx + sz * 3.2, y + dh * 0.2 + small * 1.5)], rng.random() < 0.4, R)
        p.di.text((sx + sz * 3.8, y + dh * 0.2 + small * 0.75), "rec", font=lfont(small), fill=255, anchor="mm")
        # thin level dots L/R
        n = 24
        for k, lab in enumerate(("L", "R")):
            cy = y0 + h * (0.72 + 0.14 * k)
            lvl = int(rng.integers(10, 22))
            p.dg.text((x0 + w * 0.1, cy), lab, font=lfont(small), fill=255, anchor="mm")
            p.dl.text((x0 + w * 0.1, cy), lab, font=lfont(small), fill=col(V), anchor="mm")
            for i in range(n):
                dot(p, x0 + w * 0.16 + i * w * 0.028, cy, h * 0.02, i < lvl, R if i >= 20 else V)
    else:  # spectrum: thin columns, small
        ncol, nrow = 16, 9
        gx0, gx1 = x0 + w * 0.15, x1 - w * 0.15
        gy0, gy1 = y0 + h * 0.15, y1 - h * 0.28
        cw, rh = (gx1 - gx0) / ncol, (gy1 - gy0) / nrow
        prof = np.clip(0.3 + 0.45 * np.sin(np.linspace(0.3, 2.9, ncol)) + rng.normal(0, 0.12, ncol), 0.1, 1)
        for i in range(ncol):
            hgt = int(prof[i] * nrow)
            for j in range(nrow):
                yb = gy1 - (j + 1) * rh
                p.rect((gx0 + i * cw + cw * 0.3, yb + rh * 0.3, gx0 + (i + 1) * cw - cw * 0.3, yb + rh * 0.8), j < hgt, R if j == nrow - 1 else V)
        for k, b in enumerate(["63", "250", "1k", "4k", "16k"]):
            xx = gx0 + (k * 3.6 + 1) * cw
            p.dg.text((xx, y1 - h * 0.15), b, font=lfont(small), fill=255, anchor="mm")
            p.dl.text((xx, y1 - h * 0.15), b, font=lfont(small), fill=col(V * 0.8), anchor="mm")


UNIT_LABELS = {
    "power": ("Stereo Integrated Amplifier", "FL peak power meter"),
    "cd": ("Compact Disc Player", "Random Access Program"),
    "tuner": ("FM/AM Stereo Tuner", "Quartz Synthesizer"),
    "deck": ("Stereo Cassette Deck", "FL peak meter"),
    "spectrum": ("Graphic Equalizer", "Spectrum Display"),
}


def render(w, h, v, rng):
    slug, title, fam, vfd, warm, frame, blocks, motifs = v
    S = common.ss(w, h, 2)
    W, H = w * S, h * S
    s = min(W, H)
    V0, R, Fr = hexrgb(vfd), hexrgb(warm), hexrgb(frame)
    V = mix(V0, np.array([235, 255, 250.0]), 0.45)  # real VFDs look pale, almost white-cyan
    land = W > H
    n = int(np.clip(round(H / (W / 3.2)), 1, len(UNIT_LABELS)))  # 2 in landscape, 4 in portrait, more on tall phones
    alias = {"levels": "power", "freq": "tuner", "counter": "deck", "signal": "tuner", "clock": "cd", "spectrum": "spectrum"}
    kinds = []
    for k in [alias[b] for b in blocks] + list(UNIT_LABELS):
        if k not in kinds:
            kinds.append(k)
    kinds = kinds[:n]
    dark = sum(Fr) < 300
    gap = s * 0.012
    uh = (H - gap * (n + 1)) / n
    p = Panel(W, H)
    Y, X = np.mgrid[0:H, 0:W].astype(np.float32)
    img = np.ones((H, W, 3), np.float32) * np.array([14, 13, 12.0])
    win_mask = np.zeros((H, W), bool)
    plate_mask = np.zeros((H, W), bool)
    prints = Image.new("L", (W, H), 0)
    dp = ImageDraw.Draw(prints)
    badge = None
    for ui, kind in enumerate(kinds):
        x0, x1 = gap, W - gap
        if x1 - x0 > uh * 3.6:  # very wide screens: a centred unit with dark space beside it
            x0, x1 = W / 2 - uh * 1.8, W / 2 + uh * 1.8
        y0 = gap + ui * (uh + gap)
        y1 = y0 + uh
        uw = x1 - x0
        plate_mask[int(y0):int(y1), int(x0):int(x1)] = True
        # display window: wide and shallow, left of centre like on the real units
        wx0 = x0 + uw * 0.04
        wx1 = x1 - uw * 0.04
        wy0 = y0 + uh * 0.21
        wy1 = y0 + uh * 0.86
        win_mask[int(wy0):int(wy1), int(wx0):int(wx1)] = True
        window(p, kind, wx0, wy0, wx1, wy1, V, R, rng)
        # printed legends on the aluminium (no knobs, no buttons)
        f1 = lfont(uh * 0.05)
        brand, under = UNIT_LABELS[kind]
        dp.text((x0 + uw * 0.04, y0 + uh * 0.05), brand, font=f1, fill=255)
        dp.text((x0 + uw * 0.04 + uw * 0.0, y0 + uh * 0.115), f"Model {chr(65 + int(rng.integers(0, 20)))}-{int(rng.integers(100, 990))}", font=lfont(uh * 0.04), fill=200)
        dp.text(((wx0 + wx1) / 2, wy1 + uh * 0.065), under, font=lfont(uh * 0.045), fill=255, anchor="mm")
        # fine engraved lines across the plate
        dp.line([(x0, y1 - uh * 0.02), (x1, y1 - uh * 0.02)], fill=80, width=max(1, int(s * 0.002)))
        if kind == "power" and badge is None:
            bw = max(uw * 0.10, uh * 0.26)
            badge = (x1 - uw * 0.04 - bw, y0 + uh * 0.05, x1 - uw * 0.04, y0 + uh * 0.15)
    # aluminium
    nb = rng.random((H, max(4, W // 25))).astype(np.float32)
    br = np.asarray(Image.fromarray((nb * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR), np.float32) / 255
    alu = Fr * (0.9 + 0.07 * br[..., None]) * (1.04 - 0.08 * ((Y % (uh + gap)) / uh))[..., None]
    img = np.where(plate_mask[..., None], alu, img)
    # warm room light falling across the silver, like in a dim living room
    room = np.exp(-(((X - W * 0.8) / (W * 0.7)) ** 2 + ((Y - H * 0.9) / (H * 0.8)) ** 2))
    img = img * (0.62 + 0.38 * room[..., None]) * np.array([1.0, 0.97, 0.93])
    ink = np.asarray(prints, np.float32)[..., None] / 255
    img = img * (1 - ink * (0.45 if not dark else -0.8))
    # windows: recessed black glass with a lighter lip
    wm = win_mask.astype(np.float32)[..., None]
    lip = np.asarray(Image.fromarray((win_mask * 255).astype(np.uint8)).filter(__import__("PIL.ImageFilter", fromlist=["MaxFilter"]).MaxFilter(int(s * 0.006) | 1)), np.float32)[..., None] / 255 - wm
    img = img * (1 - lip * 0.55)
    glass = np.ones((H, W, 3), np.float32) * np.array([5, 7, 8.0])
    pitch = s * 0.003
    lw_ = pitch * 0.16
    mesh = ((np.abs((X + Y) % pitch - pitch / 2) < lw_) | (np.abs((X - Y) % pitch - pitch / 2) < lw_)).astype(np.float32)[..., None]
    ghost = np.asarray(p.ghost, np.float32)[..., None] / 255
    lit = np.asarray(p.lit, np.float32)
    glass = glass + ghost * np.array([170, 185, 180.0]) * 0.06
    glass = glass + lit * (1 - 0.25 * mesh) + mesh * 3
    pr = np.asarray(p.ink, np.float32)[..., None] / 255  # white print on the glass (e.g. text on red boxes)
    glass = glass * (1 - pr * 0.8)  # legends on lit boxes are cut out dark, like on the real glass
    sheen = np.clip(1 - np.abs((X / W * 1.6 - Y / H) - 0.1) / 0.25, 0, 1) ** 2
    glass = glass + sheen[..., None] * 9
    img = img * (1 - wm) + glass * wm
    # orange glowing badge, a small amber lamp behind printed glass
    if badge is not None:
        bx0, by0, bx1, by1 = badge
        bm = (X >= bx0) & (X < bx1) & (Y >= by0) & (Y < by1)
        bl = Image.new("L", (W, H), 0)
        ImageDraw.Draw(bl).text(((bx0 + bx1) / 2, (by0 + by1) / 2), "class A", font=font((by1 - by0) * 0.55), fill=255, anchor="mm")
        bt = np.asarray(bl, np.float32)[..., None] / 255
        amber = np.array([255, 150, 50.0])
        img = np.where(bm[..., None], amber * 0.22 + bt * amber * 0.9, img)
    img = glow(img * 1.0, s, 0.003, 0.02, 0.35, 0.3) * 0.72 + img * 0.28 if False else img + glow(lit * wm, s, 0.003, 0.02, 0.5, 0.45) - lit * wm
    img = grain(img, rng, 2.5)
    return to_image(img).resize((w, h), Image.LANCZOS)


def colour(v):
    return v[3]
