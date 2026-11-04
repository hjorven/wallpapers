"""Safari-Startseite iPad 9. Gen., Version 3: Planet mit Ring, Wolkenbänke statt Boden,
Tempelruine und Aquädukt, schwebende Körper, Plattenrahmen mit Inschrift."""
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.argv = [sys.argv[0], 'out']
import render as R

NAVY = np.array([16, 17, 44]); BLUE = np.array([36, 36, 255]); PAPER = np.array([233, 233, 245])
def mix(a, b, t): return (a * (1 - t) + b * t).astype(np.uint8)
DIM = mix(NAVY, BLUE, 0.45); MID = mix(NAVY, BLUE, 0.75); PALE = mix(BLUE, PAPER, 0.55)
FONT = '/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Regular.ttf'

def load(name):
    z = np.load(name); return z['obj'], z['cover']

def place(a, w, h, x0, y0):
    full = np.zeros((h, w), bool); oh, ow = a.shape
    ys, xs = slice(max(0, y0), min(h, y0 + oh)), slice(max(0, x0), min(w, x0 + ow))
    if ys.start < ys.stop and xs.start < xs.stop:
        full[ys, xs] = a[ys.start - y0:ys.stop - y0, xs.start - x0:xs.stop - x0]
    return full

def noise(h, w, seed, scales=(64, 32, 16, 8)):
    rng = np.random.default_rng(seed); out = np.zeros((h, w))
    for i, s in enumerate(scales):
        g = rng.random((h // s + 2, w // s + 2))
        out += np.array(Image.fromarray((g * 255).astype(np.uint8)).resize((w + 2 * s, h + 2 * s), Image.BICUBIC))[s:s + h, s:s + w] / 255 * 0.5 ** i
    return out / sum(0.5 ** i for i in range(len(scales)))

def clouds(w, h, y_c, seed, n, rmin, rmax, xs_range=None):
    """Kumulus-Bank aus Halbkreisen: liefert Füllung, Kante und Schraffur."""
    rng = np.random.default_rng(seed)
    ys, xs = np.mgrid[0:h, 0:w]
    top = np.full(w, float(h)); x = np.arange(w)
    lo, hi = xs_range or (-rmax, w + rmax)
    for cx in np.linspace(lo, hi, n) + rng.normal(0, (hi - lo) / n * 0.3, n):
        r = rng.uniform(rmin, rmax); cy = y_c + rng.uniform(-0.3, 0.6) * r
        rx = r * rng.uniform(1.15, 1.6); ry = r * 0.92
        d = 1 - ((x - cx) / rx) ** 2
        top = np.minimum(top, np.where(d > 0, cy - ry * np.sqrt(np.maximum(d, 0)), h))
    top = np.minimum(top, y_c + rmin * 0.6)
    fill = ys >= top[None, :]
    depth = ys - top[None, :]
    v = np.clip(1 - depth / (rmax * 0.8), 0, 1) ** 1.8
    hatch = R.engrave(v, period=4.0) & fill
    edge = fill & ~np.roll(fill, 2, axis=0)
    return fill, hatch | edge

def compose(W, H, name, L):
    w, h = W // 2, H // 2
    ys, xs = np.mgrid[0:h, 0:w]; th = R.BAYER[ys % 8, xs % 8]
    img = np.zeros((h, w, 3), np.uint8); img[:] = NAVY
    qx, qy = 0, 0
    quiet = np.clip(np.hypot((xs - qx) / (w * 0.55), (ys - qy) / (h * 0.55)), 0, 1) ** 1.4

    sx, sy = L['subject']                         # Säulenmitte, Säulenfuß (halbe Auflösung)
    so, sc = load(L['subject_file']); oh, ow = so.shape
    x0, y0 = int(sx - ow / 2), int(sy - oh * 0.975)
    icx, icy = sx, y0 + oh * 0.348

    # Himmel: Nebel + Licht hinter dem Ikosaeder + Horizontschein über den Wolken
    neb = noise(h, w, 5)
    glow = np.exp(-(((xs - icx) / (w * 0.32)) ** 2 + ((ys - icy) / (h * 0.45)) ** 2))
    horizon = np.exp(-((ys - L['cloud_y'][0]) / (h * 0.18)) ** 2)
    sky = 0.02 + 0.16 * glow + 0.14 * horizon + 0.22 * np.clip(neb - 0.5, 0, 1) * 2 * (1 - 0.6 * (1 - quiet))
    img[sky * (0.35 + 0.65 * quiet) > th] = DIM

    # Sterne in zwei Helligkeiten
    rng = np.random.default_rng(3); r = rng.random((h, w))
    img[(r < 0.0022) & (quiet > 0.6)] = MID
    img[(r < 0.0007) & (quiet > 0.7)] = PAPER

    # Planet mit Ring (hinten)
    po, pc = load(L['planet_file']); px, py = L['planet']
    pcov = place(pc, w, h, px, py); pob = place(po, w, h, px, py)
    img[pcov] = NAVY; img[pob & (quiet > th * 0.5)] = MID

    # Strahlen und Umlaufbahnen
    hide = R.binary_dilation(place(sc, w, h, x0, y0), iterations=4)
    rays = R.rays(w, h, icx, icy, n=130, seed=11) & ~hide
    orb = np.zeros((h, w), bool)
    for rr, e, t in [(0.62, 0.30, -0.18), (0.88, 0.22, 0.12), (1.2, 0.15, -0.06)]:
        Rr = oh * rr; c, s_ = np.cos(t), np.sin(t)
        u = ((xs - icx) * c + (ys - icy) * s_) / Rr; v = (-(xs - icx) * s_ + (ys - icy) * c) / (Rr * e)
        orb |= np.abs(np.hypot(u, v) - 1) < 1.1 / (Rr * e)
    orb &= ((xs + ys) % 3 == 0) & ~hide
    near = np.exp(-(np.hypot(xs - icx, ys - icy) / (oh * 0.95)) ** 2)
    fade = quiet > th * 0.9 + 0.1
    strong = near * 0.7 + 0.3 > th
    img[(rays | orb) & fade & strong] = BLUE
    img[(rays | orb) & fade & ~strong] = DIM

    # Ferne Wolkenbank, Aquädukt dahinter, Tempel auf eigener Wolke
    f, hch = clouds(w, h, L['cloud_y'][0], 21, 16, 18, 44)
    ao, ac = load(L['arch_file']); ax, ay = L['arch']
    acov = place(ac, w, h, ax, ay); img[acov] = NAVY; img[place(ao, w, h, ax, ay)] = DIM
    img[f] = NAVY; img[hch] = DIM

    # Säule mit Ikosaeder
    img[place(sc, w, h, x0, y0)] = NAVY
    img[place(so, w, h, x0, y0)] = PAPER

    to, tc = load(L['temple_file']); tx, ty = L['temple']
    f2, h2 = clouds(w, h, L['cloud_y'][1], 7, 14, 18, 46)
    img[place(tc, w, h, tx, ty)] = NAVY; img[place(to, w, h, tx, ty)] = PALE
    img[f2] = NAVY; img[h2] = MID

    # Schwebende Körper
    for fn, (bx, by), col in L['solids']:
        o, c = load(fn); img[place(c, w, h, bx, by)] = NAVY; img[place(o, w, h, bx, by)] = col

    # Vordere Wolkenbank, verdeckt den Säulenfuß
    f3, h3 = clouds(w, h, L['cloud_y'][2], 33, 13, 22, 60)
    img[f3] = NAVY; img[h3] = MID

    # Plattenrahmen mit Eckmarken und Inschrift
    m = 14
    frame = np.zeros((h, w), bool)
    frame[m, m:w - m] = frame[h - m - 1, m:w - m] = True; frame[m:h - m, m] = frame[m:h - m, w - m - 1] = True
    frame &= ((xs + ys) % 2 == 0)
    frame &= ~((ys < 140) & (xs < w))              # oben verdeckt die Safari-Leiste ohnehin
    img[frame] = MID
    out = Image.fromarray(img).resize((W, H), Image.NEAREST)
    d = ImageDraw.Draw(out); ft = ImageFont.truetype(FONT, 22)
    txt = 'OFFICINA HJORVEN  ·  MMXXVI  ·  HJORVEN.GITHUB.IO'
    tw = d.textlength(txt, font=ft)
    d.rectangle([W - 2 * m - tw - 40, H - 2 * m - 18, W - 2 * m - 8, H - 2 * m + 18], fill=tuple(NAVY))
    d.text((W - 2 * m - tw - 24, H - 2 * m - 13), txt, font=ft, fill=tuple(PALE))
    out = out.convert('1', dither=Image.NONE) if False else out
    out.save(f'out/{name}.png', optimize=True)
    print(name, out.size, flush=True)

compose(2160, 1620, 'v3-quer', dict(
    subject=(780, 700), subject_file='subject-q.npz',
    planet=(700, -170), planet_file='part-planet-620.npz',
    arch=(650, 500), arch_file='part-arch-420.npz',
    temple=(90, 455), temple_file='part-temple-380.npz',
    cloud_y=(640, 690, 760),
    solids=[('part-dode-120.npz', (520, 250), PAPER), ('part-octa-100.npz', (960, 470), PALE), ('part-cube-90.npz', (420, 400), MID)]))
compose(1620, 2160, 'v3-hoch', dict(
    subject=(430, 960), subject_file='subject-h.npz',
    planet=(380, 60), planet_file='part-planet-520.npz',
    arch=(500, 760), arch_file='part-arch-420.npz',
    temple=(-40, 760), temple_file='part-temple-320.npz',
    cloud_y=(900, 950, 1020),
    solids=[('part-dode-120.npz', (120, 520), PAPER), ('part-octa-100.npz', (650, 700), PALE), ('part-cube-90.npz', (90, 330), MID)]))
