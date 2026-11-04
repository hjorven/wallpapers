"""Safari-Startseite iPad 9. Gen. (2160 x 1620 / 1620 x 2160), 1-Bit-Gravurstil, Version 2.
Säule mit Ikosaeder auf einer gerasterten Bodenebene, Umlaufbahnen, Strahlen, Sterne.
Oben links bleibt ruhig für die Favoriten, die Mitte frei für den Bearbeiten-Knopf."""
import sys
import numpy as np
from PIL import Image
sys.argv = [sys.argv[0], 'out']
import render as R

NAVY = np.array([16, 17, 44]); BLUE = np.array([36, 36, 255]); PAPER = np.array([233, 233, 245])
DIM = (NAVY * 0.45 + BLUE * 0.55).astype(np.uint8)

def alpha(path): return np.array(Image.open(path).convert('LA'))[..., 1] > 127
col = alpha('hero-column.png')                                   # 725 x 760
F = 5
ico = alpha('hero-ico.png'); fw = ico.shape[1] // 24; ico = ico[:, F*fw:(F+1)*fw]
kn = alpha('hero-ico-knock.png')[:, F*fw:(F+1)*fw]
IX, IY = 196, 76
obj = col.copy(); obj[IY:IY+ico.shape[0], IX:IX+fw] |= ico
cover = R.binary_dilation(col, iterations=3); cover[IY:IY+kn.shape[0], IX:IX+fw] |= kn

def place(a, s, w, h, x0, y0):
    oh, ow = int(a.shape[0] * s), int(a.shape[1] * s)
    b = np.array(Image.fromarray(a.astype(np.uint8) * 255).resize((ow, oh), Image.NEAREST)) > 127
    full = np.zeros((h, w), bool)
    ys, xs = slice(max(0, y0), min(h, y0 + oh)), slice(max(0, x0), min(w, x0 + ow))
    full[ys, xs] = b[ys.start - y0:ys.stop - y0, xs.start - x0:xs.stop - x0]
    return full

def dotted(m, ys, xs, step=2):
    return m & (((xs + ys) % step) == 0)

def compose(W, H, cx, base, s, name, calm=(0.0, 0.0), tag=None):
    """cx: Mitte des Objekts (x), base: Unterkante der Säule (y), s: Maßstab, alles in Pixeln der Endgröße."""
    w, h = W // 2, H // 2; cx, base = cx / 2, base / 2; s = s / 2
    ow, oh = 760 * s, 725 * s
    x0, y0 = int(cx - ow / 2), int(base - oh * 0.975)
    icx, icy = cx, y0 + oh * 0.348                                 # Mitte des Ikosaeders
    ys, xs = np.mgrid[0:h, 0:w]
    th = R.BAYER[ys % 8, xs % 8]
    img = np.zeros((h, w, 3), np.uint8); img[:] = NAVY

    # Ruhezone oben links (Favoriten): dort alles abgeschwächt
    qx, qy = calm
    quiet = np.clip(np.hypot((xs - qx) / (w * 0.62), (ys - qy) / (h * 0.62)), 0, 1) ** 1.5

    # Himmel: weiches Licht hinter dem Ikosaeder
    glow = np.exp(-(((xs - icx) / (w * 0.30)) ** 2 + ((ys - icy) / (h * 0.42)) ** 2))
    sky = (0.03 + 0.20 * glow) * (ys < base)
    # Boden: Ebene ab Horizont, nach vorn dichter
    hz = base
    depth = np.clip((ys - hz) / (h - hz + 1), 0, 1)
    floor = (ys >= hz) * (0.10 + 0.30 * depth ** 1.3) * (0.55 + 0.45 * np.exp(-((xs - cx) / (w * 0.45)) ** 2))
    img[(sky + floor) * (0.4 + 0.6 * quiet) > th] = DIM

    # Bodenraster: Fluchtlinien zum Fußpunkt der Säule und Querlinien in Perspektive
    grid = np.zeros((h, w), bool)
    below = ys > hz + 1
    ang = np.arctan2(ys - hz, xs - cx)
    for a in np.linspace(0.04, np.pi - 0.04, 23):
        grid |= below & (np.abs(ang - a) < 0.6 / np.maximum(np.hypot(xs - cx, ys - hz), 1))
    k = 0
    while True:
        y = hz + 6 * (1.32 ** k); k += 1
        if y >= h: break
        grid |= below & (np.abs(ys - y) < 0.5)
    grid = dotted(grid, ys, xs, 2)
    img[grid & (quiet > th * 0.6 + 0.2)] = (NAVY * 0.25 + BLUE * 0.75).astype(np.uint8)
    img[(np.abs(ys - hz) < 0.5) & ~R.binary_dilation(place(cover, s, w, h, x0, y0), iterations=3)] = BLUE   # Horizont

    # Umlaufbahnen: gepunktete Ellipsen um das Ikosaeder
    orb = np.zeros((h, w), bool)
    for r, e, t in [(0.62, 0.30, -0.18), (0.86, 0.22, 0.12), (1.14, 0.16, -0.05)]:
        R_ = oh * r; c, sn = np.cos(t), np.sin(t)
        u = ((xs - icx) * c + (ys - icy) * sn) / R_
        v = (-(xs - icx) * sn + (ys - icy) * c) / (R_ * e)
        d = np.hypot(u, v)
        orb |= np.abs(d - 1) < 0.9 / (R_ * e) * np.maximum(np.abs(v), 0.2) ** 0 * 1.2
    orb = dotted(orb, ys, xs, 3) & (ys < hz)

    # Strahlen
    rays = R.rays(w, h, icx, icy, n=120, seed=11)
    rays &= ys < hz

    # Sterne: vereinzelte Punkte, nicht in der Ruhezone
    rng = np.random.default_rng(3)
    stars = (rng.random((h, w)) < 0.0016) & (ys < hz - 8) & (quiet > 0.75)

    z = np.load(f'subject-{tag}.npz')
    figure = place(z['obj'], 1, w, h, x0, y0)
    hide = R.binary_dilation(place(z['cover'], 1, w, h, x0, y0), iterations=4)
    fade = quiet > th * 0.9 + 0.1
    near = np.exp(-(np.hypot(xs - icx, ys - icy) / (oh * 0.9)) ** 2)
    img[(orb | rays) & ~hide & fade & (near * 0.7 + 0.3 > th)] = BLUE
    img[(orb | rays) & ~hide & fade & ~(near * 0.7 + 0.3 > th)] = DIM
    img[stars & ~hide] = PAPER
    img[figure] = PAPER
    out = Image.fromarray(img).resize((W, H), Image.NEAREST)
    out.save(f'out/{name}.png', optimize=True)
    print(name, out.size, flush=True)

compose(2160, 1620, cx=1530, base=1290, s=1.4, name='ipad-safari-quer', calm=(0, 0), tag='q')
compose(1620, 2160, cx=810, base=1880, s=1.2, name='ipad-safari-hoch', calm=(0, 0), tag='h')
