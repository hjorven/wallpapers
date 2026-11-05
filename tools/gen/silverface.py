"""Silver Face: late-1970s Japanese hi-fi. Brushed aluminium, cyan-green VFD readouts, red LEDs."""
import numpy as np
from PIL import Image, ImageDraw
from common import hexrgb, mix, glow, grain, to_image, col

ID = "silverface"
NAME = "Silver Face"
TAGLINE = "Brushed aluminium and glowing VFDs"
DESCRIPTION = ("The silver hi-fi stacks of the late 1970s: brushed aluminium fronts, vacuum fluorescent "
               "displays glowing cyan-green, level meters, red indicator LEDs and heavy knurled knobs.")
FORMAT = "jpg"

# slug, title, family, faceplate, vfd colour, led colour, units top to bottom, motifs
VARIANTS = [
    ("integrated", "Integrated", "cyan", "#c9ccd0", "#3dffd0", "#ff3b30", ["meters", "amp", "tuner", "eq"], ["Power meters", "Cyan VFD"]),
    ("receiver", "Receiver", "cyan", "#cfd1d3", "#5ff2e0", "#ff4a3a", ["dial", "meters", "amp", "deck"], ["Tuning dial", "Silver"]),
    ("tape-deck", "Tape Deck", "green", "#c4c7ca", "#6aff9a", "#ff3b30", ["deck", "levels", "tuner", "amp"], ["Cassette", "Level bars"]),
    ("spectrum", "Spectrum", "blue", "#c8cbcf", "#5fd8ff", "#ff3b6a", ["eq", "levels", "meters", "tuner"], ["Spectrum analyser"]),
    ("champagne", "Champagne", "yellow", "#d6c7a6", "#3dffd0", "#ff4a30", ["meters", "dial", "amp", "levels"], ["Champagne gold", "Cyan"]),
    ("amber-tuner", "Amber Tuner", "orange", "#c9ccd0", "#ffb04a", "#ff3b30", ["tuner", "dial", "levels", "amp"], ["Amber VFD"]),
    ("black-face", "Black Face", "mono", "#2a2b2d", "#3dffd0", "#ff3b30", ["amp", "eq", "deck", "meters"], ["Black front", "Cyan"]),
    ("blue-hour", "Blue Hour", "blue", "#bfc4ca", "#4fa8ff", "#ff5a4a", ["levels", "deck", "eq", "dial"], ["Blue VFD", "Deck"]),
    ("studio", "Studio", "cyan", "#cdd0d2", "#2fffc4", "#ff2d2d", ["meters", "levels", "eq", "amp"], ["VU meters", "Studio"]),
    ("midnight", "Midnight", "green", "#3a3c3f", "#7dff6a", "#ff3b30", ["dial", "tuner", "deck", "levels"], ["Dark grey", "Green VFD"]),
]

SEG = {  # seven-segment map: a b c d e f g
    "0": "abcdef", "1": "bc", "2": "abged", "3": "abgcd", "4": "fgbc", "5": "afgcd",
    "6": "afgedc", "7": "abc", "8": "abcdefg", "9": "abcdfg", ".": "", " ": "",
}


def digit(d, x, y, dw, dh, ch, on, off):
    t = dw * 0.18
    segs = {
        "a": [(x + t, y), (x + dw - t, y), (x + dw - t * 1.6, y + t), (x + t * 1.6, y + t)],
        "d": [(x + t * 1.6, y + dh - t), (x + dw - t * 1.6, y + dh - t), (x + dw - t, y + dh), (x + t, y + dh)],
        "g": [(x + t, y + dh / 2), (x + t * 1.6, y + dh / 2 - t / 2), (x + dw - t * 1.6, y + dh / 2 - t / 2), (x + dw - t, y + dh / 2), (x + dw - t * 1.6, y + dh / 2 + t / 2), (x + t * 1.6, y + dh / 2 + t / 2)],
        "f": [(x, y + t), (x + t, y + t * 1.6), (x + t, y + dh / 2 - t * 0.6), (x, y + dh / 2 - t * 0.2)],
        "e": [(x, y + dh / 2 + t * 0.2), (x + t, y + dh / 2 + t * 0.6), (x + t, y + dh - t * 1.6), (x, y + dh - t)],
        "b": [(x + dw, y + t), (x + dw - t, y + t * 1.6), (x + dw - t, y + dh / 2 - t * 0.6), (x + dw, y + dh / 2 - t * 0.2)],
        "c": [(x + dw, y + dh / 2 + t * 0.2), (x + dw - t, y + dh / 2 + t * 0.6), (x + dw - t, y + dh - t * 1.6), (x + dw, y + dh - t)],
    }
    lit = SEG.get(ch, "")
    for k, poly in segs.items():
        d.polygon(poly, fill=on if k in lit else off)


def knob(base_d, cx, cy, R, face, rng):
    F = np.asarray(face, float)
    dark = sum(F) < 300
    base_d.ellipse([cx - R * 1.08, cy - R * 1.04, cx + R * 1.12, cy + R * 1.14], fill=col(F * 0.35))  # shadow
    # knurled skirt
    n = 72
    for k in range(n):
        a0, a1 = k * 360 / n, (k + 0.5) * 360 / n
        base_d.pieslice([cx - R, cy - R, cx + R, cy + R], a0, a1, fill=col(F * (0.55 if k % 2 else 0.75)))
    r2 = R * 0.84
    # top: radial brushed look made of thin wedges with varying light
    m = 90
    for k in range(m):
        a = k * 360 / m
        light = 0.75 + 0.3 * np.cos(np.radians(a * 2 - 90)) + 0.05 * rng.random()
        base_d.pieslice([cx - r2, cy - r2, cx + r2, cy + r2], a, a + 360 / m + 0.5, fill=col(np.clip(F * light * (1.1 if not dark else 1.6), 0, 255)))
    base_d.ellipse([cx - r2, cy - r2, cx + r2, cy + r2], outline=col(F * 0.5), width=max(1, int(R * 0.02)))
    # pointer
    a = np.radians(rng.uniform(-130, 40) - 90)
    base_d.line([(cx + np.cos(a) * r2 * 0.4, cy + np.sin(a) * r2 * 0.4), (cx + np.cos(a) * r2 * 0.85, cy + np.sin(a) * r2 * 0.85)], fill=col(F * 0.25), width=max(2, int(R * 0.05)))
    # scale ticks around
    for k in range(11):
        b = np.radians(-135 - 90 + k * 27)
        base_d.line([(cx + np.cos(b) * R * 1.15, cy + np.sin(b) * R * 1.15), (cx + np.cos(b) * R * 1.25, cy + np.sin(b) * R * 1.25)], fill=col(F * 0.4 if not dark else F * 2.5), width=max(1, int(R * 0.025)))


def render(w, h, v, rng):
    slug, title, fam, face, vfd, ledc, units, motifs = v
    S = 2
    W, H = w * S, h * S
    s = min(W, H)
    F, V, L = hexrgb(face), hexrgb(vfd), hexrgb(ledc)
    dark = sum(F) < 300
    n_units = 2 if W > H else 4
    units = units[:n_units]
    gap = s * 0.018
    # rack background (dark wood-ish shadow between units)
    img = np.ones((H, W, 3), np.float32) * np.array([16, 14, 13.0])
    base = Image.fromarray(img.astype(np.uint8))
    d = ImageDraw.Draw(base)
    gl = Image.new("RGB", (W, H), (0, 0, 0))
    dg = ImageDraw.Draw(gl)
    uh = (H - gap * (n_units + 1)) / n_units
    off_v = col(V * 0.07 + 6)
    for ui, kind in enumerate(units):
        x0, x1 = gap, W - gap
        y0 = gap + ui * (uh + gap)
        y1 = y0 + uh
        uw = x1 - x0
        # brushed aluminium faceplate
        hh, ww = int(y1 - y0), int(uw)
        n = rng.random((hh, max(4, ww // 60))).astype(np.float32)
        br = np.asarray(Image.fromarray((n * 255).astype(np.uint8)).resize((ww, hh), Image.BILINEAR), np.float32) / 255
        yy = np.linspace(0, 1, hh)[:, None, None]
        plate = F * (0.92 + 0.1 * br[..., None]) * (1.06 - 0.12 * yy)
        if not dark:
            plate = plate + 12 * np.exp(-((yy - 0.18) / 0.08) ** 2)  # sheen line
        arr = np.asarray(base, np.float32)
        arr[int(y0):int(y0) + hh, int(x0):int(x0) + ww] = plate
        base = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
        d = ImageDraw.Draw(base)
        # bevel and rack ears with screws
        d.line([(x0, y0), (x1, y0)], fill=col(F * 1.15 + 10), width=2)
        d.line([(x0, y1), (x1, y1)], fill=col(F * 0.5), width=3)
        for sx in (x0 + s * 0.025, x1 - s * 0.025):
            for sy in (y0 + uh * 0.15, y1 - uh * 0.15):
                r = s * 0.008
                d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=col(F * 0.6))
                d.line([(sx - r * 0.7, sy), (sx + r * 0.7, sy)], fill=col(F * 0.3), width=2)
        tc = col(F * 0.45 if not dark else F * 2.6)  # label "text" colour
        def label(x, y, L_, hgt=None):
            hgt = hgt or uh * 0.025
            xx = x
            while xx < x + L_:
                seg = L_ * (0.15 + 0.3 * rng.random())
                d.rectangle([xx, y, min(x + L_, xx + seg), y + hgt], fill=tc)
                xx += seg + hgt * 1.5
        # brand plate (fake lettering bars) top left
        label(x0 + s * 0.05, y0 + uh * 0.08, uw * 0.08, uh * 0.035)
        # power button and red LED bottom left
        pb = s * 0.022
        d.rounded_rectangle([x0 + s * 0.05, y1 - uh * 0.22, x0 + s * 0.05 + pb * 2.2, y1 - uh * 0.22 + pb], radius=pb * 0.2, fill=col(F * 0.75))
        lx, ly = x0 + s * 0.05 + pb * 2.8, y1 - uh * 0.22 + pb / 2
        dg.ellipse([lx - s * 0.004, ly - s * 0.004, lx + s * 0.004, ly + s * 0.004], fill=col(L))
        label(x0 + s * 0.05, y1 - uh * 0.1, uw * 0.06)
        # display window (black glass)
        wx0, wx1 = x0 + uw * 0.16, x0 + uw * (0.66 if kind not in ("dial",) else 0.86)
        wy0, wy1 = y0 + uh * 0.16, y1 - uh * 0.2
        d.rounded_rectangle([wx0 - s * 0.006, wy0 - s * 0.006, wx1 + s * 0.006, wy1 + s * 0.006], radius=s * 0.006, fill=col(F * 0.55))
        d.rectangle([wx0, wy0, wx1, wy1], fill=(10, 12, 13))
        ww_, wh_ = wx1 - wx0, wy1 - wy0
        lw = max(2, int(s * 0.002))
        if kind == "meters":
            # two analogue power meters, backlit cyan-green
            for k in range(2):
                mx0 = wx0 + ww_ * (0.02 + 0.5 * k)
                mx1 = mx0 + ww_ * 0.46
                d.rectangle([mx0, wy0 + wh_ * 0.06, mx1, wy1 - wh_ * 0.06], fill=col(V * 0.18 + 8))
                cx, cy = (mx0 + mx1) / 2, wy1 - wh_ * 0.1
                R = min(wh_ * 0.72, ww_ * 0.3)
                for t in range(31):
                    a = np.radians(-90 - 45 + t * 3)
                    l = 0.08 if t % 5 == 0 else 0.04
                    c = L if t > 24 else V
                    dg.line([(cx + np.cos(a) * R, cy + np.sin(a) * R), (cx + np.cos(a) * R * (1 - l), cy + np.sin(a) * R * (1 - l))], fill=col(c * 0.9), width=lw)
                dg.arc([cx - R, cy - R, cx + R, cy + R], 225, 315, fill=col(V * 0.7), width=lw)
                a = np.radians(-90 - 45 + rng.uniform(20, 75))
                d.line([(cx, cy), (cx + np.cos(a) * R * 1.02, cy + np.sin(a) * R * 1.02)], fill=(20, 20, 20), width=lw * 2)
                d.pieslice([cx - R * 0.12, cy - R * 0.12, cx + R * 0.12, cy + R * 0.12], 180, 360, fill=(25, 25, 25))
                for j in range(3):
                    label(mx0 + ww_ * 0.05, wy1 - wh_ * 0.22 + j * 0, ww_ * 0.12, wh_ * 0.03)
        elif kind == "levels":
            # segmented peak level bars L and R, with a dB scale
            nseg = 32
            for k in range(2):
                by = wy0 + wh_ * (0.25 + 0.35 * k)
                lvl = int(nseg * (0.55 + 0.35 * rng.random()))
                peak = min(nseg - 1, lvl + int(rng.integers(1, 4)))
                for i in range(nseg):
                    bx = wx0 + ww_ * 0.08 + i * ww_ * 0.85 / nseg
                    on = i < lvl or i == peak
                    c = (L if i > nseg * 0.8 else V)
                    (dg if on else d).rectangle([bx, by, bx + ww_ * 0.85 / nseg * 0.7, by + wh_ * 0.18], fill=col(c) if on else off_v)
                digit(dg if True else d, wx0 + ww_ * 0.02, by, ww_ * 0.025, wh_ * 0.18, "8", off_v, off_v)
            for i in range(9):
                bx = wx0 + ww_ * 0.08 + i * ww_ * 0.85 / 8
                dg.rectangle([bx, wy0 + wh_ * 0.12, bx + ww_ * 0.012, wy0 + wh_ * 0.16], fill=col(V * 0.6))
        elif kind == "tuner":
            # seven-segment frequency readout plus signal strength
            freq = f"{rng.uniform(87.5, 108):.1f}".rjust(5)
            dw = min(wh_ * 0.3, ww_ * 0.1)
            dh = dw * 2
            xx = wx0 + ww_ * 0.06
            for ch in freq:
                if ch == ".":
                    dg.rectangle([xx - dw * 0.15, wy0 + wh_ * 0.2 + dh - dw * 0.18, xx + dw * 0.05, wy0 + wh_ * 0.2 + dh], fill=col(V))
                    xx += dw * 0.3
                    continue
                digit(dg, xx, wy0 + wh_ * 0.2, dw, dh, ch, col(V), off_v)
                xx += dw * 1.35
            # MHz label and stereo indicator
            dg.rectangle([xx + dw * 0.2, wy0 + wh_ * 0.62, xx + dw * 1.3, wy0 + wh_ * 0.7], fill=col(V * 0.8))
            dg.rectangle([wx1 - ww_ * 0.2, wy0 + wh_ * 0.2, wx1 - ww_ * 0.06, wy0 + wh_ * 0.3], fill=col(L))
            for i in range(8):
                bx = wx1 - ww_ * 0.2 + i * ww_ * 0.017
                bhh = wh_ * 0.05 * (i + 1)
                (dg if i < 6 else d).rectangle([bx, wy1 - wh_ * 0.15 - bhh, bx + ww_ * 0.011, wy1 - wh_ * 0.15], fill=col(V) if i < 6 else off_v)
        elif kind == "eq":
            # spectrum analyser: columns of segments
            ncol, nrow = 18, 12
            for i in range(ncol):
                hgt = int(nrow * np.clip(0.25 + 0.6 * np.sin(i / ncol * np.pi) * rng.uniform(0.6, 1.1) + rng.normal(0, 0.1), 0.1, 1))
                for j in range(nrow):
                    bx = wx0 + ww_ * 0.05 + i * ww_ * 0.9 / ncol
                    byy = wy1 - wh_ * 0.1 - (j + 1) * wh_ * 0.78 / nrow
                    on = j < hgt
                    c = L if j >= nrow - 2 else V
                    (dg if on else d).rectangle([bx, byy, bx + ww_ * 0.9 / ncol * 0.75, byy + wh_ * 0.78 / nrow * 0.7], fill=col(c) if on else off_v)
        elif kind == "dial":
            # long tuning scale with a red pointer, backlit
            d.rectangle([wx0, wy0, wx1, wy1], fill=col(V * 0.08 + 6))
            for row, (lo, hi) in enumerate(((88, 108), (53, 160))):
                yy0 = wy0 + wh_ * (0.3 + 0.35 * row)
                dg.line([(wx0 + ww_ * 0.04, yy0), (wx1 - ww_ * 0.04, yy0)], fill=col(V * 0.6), width=lw)
                for t in range(41):
                    xx = wx0 + ww_ * 0.04 + t * (ww_ * 0.92) / 40
                    l = wh_ * (0.1 if t % 5 == 0 else 0.05)
                    dg.line([(xx, yy0 - l), (xx, yy0)], fill=col(V * 0.8), width=lw)
                    if t % 5 == 0:
                        dg.rectangle([xx - ww_ * 0.008, yy0 - wh_ * 0.2, xx + ww_ * 0.008, yy0 - wh_ * 0.16], fill=col(V * 0.6))
            px = wx0 + ww_ * rng.uniform(0.15, 0.85)
            dg.line([(px, wy0 + wh_ * 0.06), (px, wy1 - wh_ * 0.06)], fill=col(L), width=lw * 2)
        elif kind == "deck":
            # cassette window: two reels and a tape counter
            cw0, cw1 = wx0 + ww_ * 0.05, wx0 + ww_ * 0.62
            d.rounded_rectangle([cw0, wy0 + wh_ * 0.1, cw1, wy1 - wh_ * 0.1], radius=wh_ * 0.05, fill=(40, 40, 42))
            d.rectangle([cw0 + (cw1 - cw0) * 0.15, wy0 + wh_ * 0.22, cw1 - (cw1 - cw0) * 0.15, wy1 - wh_ * 0.3], fill=(70, 55, 45))
            for k in range(2):
                rx = cw0 + (cw1 - cw0) * (0.3 + 0.4 * k)
                ry = wy0 + wh_ * 0.45
                rr = wh_ * (0.24 if k == 0 else 0.17)
                d.ellipse([rx - rr, ry - rr, rx + rr, ry + rr], fill=(38, 30, 26))
                rh = wh_ * 0.09
                d.ellipse([rx - rh, ry - rh, rx + rh, ry + rh], fill=(220, 220, 215))
                for j in range(6):
                    a = j * np.pi / 3
                    d.line([(rx, ry), (rx + np.cos(a) * rh, ry + np.sin(a) * rh)], fill=(60, 60, 60), width=lw)
            d.rectangle([cw0 + (cw1 - cw0) * 0.1, wy1 - wh_ * 0.24, cw1 - (cw1 - cw0) * 0.1, wy1 - wh_ * 0.16], fill=(230, 226, 214))
            cnt = f"{int(rng.integers(0, 999)):03d}"
            dw = min(wh_ * 0.2, ww_ * 0.07)
            dh = dw * 2
            xx = cw1 + ww_ * 0.06
            for ch in cnt:
                digit(dg, xx, wy0 + wh_ * 0.15, dw, dh, ch, col(V), off_v)
                xx += dw * 1.35
            for k in range(3):  # play / rec indicators
                c = L if k == 1 else V
                dg.rectangle([cw1 + ww_ * 0.06 + k * ww_ * 0.09, wy1 - wh_ * 0.28, cw1 + ww_ * 0.12 + k * ww_ * 0.09, wy1 - wh_ * 0.2], fill=col(c) if rng.random() < 0.7 else off_v)
        else:  # amp: input selector LEDs and a row of small push buttons inside the window area
            for k in range(6):
                bx = wx0 + ww_ * (0.06 + k * 0.155)
                d.rectangle([bx, wy0 + wh_ * 0.15, bx + ww_ * 0.12, wy0 + wh_ * 0.5], fill=(22, 24, 25))
                on = k == int(rng.integers(0, 6))
                dg.rectangle([bx + ww_ * 0.02, wy0 + wh_ * 0.25, bx + ww_ * 0.1, wy0 + wh_ * 0.4], fill=col(V) if on else off_v)
                dg.rectangle([bx + ww_ * 0.03, wy0 + wh_ * 0.62, bx + ww_ * 0.09, wy0 + wh_ * 0.68], fill=col(V * 0.5))
            dg.ellipse([wx1 - ww_ * 0.05, wy1 - wh_ * 0.25, wx1 - ww_ * 0.03, wy1 - wh_ * 0.25 + ww_ * 0.02], fill=col(L))
        # row of small toggles under the window
        for k in range(8):
            tx = wx0 + k * ww_ / 8 + ww_ * 0.02
            ty = wy1 + uh * 0.05
            if ty + uh * 0.06 < y1 - s * 0.005:
                d.rounded_rectangle([tx, ty, tx + ww_ * 0.06, ty + uh * 0.06], radius=s * 0.003, fill=col(F * (0.7 if not dark else 1.6)))
        # knobs on the right
        if kind != "dial":
            kx = x0 + uw * 0.82
            R = min(uh * 0.32, uw * 0.09)
            knob(d, kx, (y0 + y1) / 2, R, F, rng)
            r2 = R * 0.45
            knob(d, x0 + uw * 0.71, y0 + uh * 0.32, r2, F, rng)
            knob(d, x0 + uw * 0.71, y1 - uh * 0.32, r2, F, rng)
            label(kx - R * 0.6, y1 - uh * 0.08, R * 1.2)
    img = np.asarray(base, np.float32)
    img = img + glow(np.asarray(gl, np.float32), s, 0.002, 0.012, 0.8, 0.6)
    img = grain(img, rng, 2)
    return to_image(img).resize((w, h), Image.LANCZOS)


def colour(v):
    return v[4]
