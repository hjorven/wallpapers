"""Zerlegt das Titelbild in Ebenen: Strahlen, Säule und ein drehendes Ikosaeder (Sprite).
Aufruf: python3 hero_layers.py <ausgabeordner> [frames]"""
import sys
import numpy as np
from PIL import Image

OUTDIR = sys.argv[1]
N = int(sys.argv[2]) if len(sys.argv) > 2 else 24
sys.argv = [sys.argv[0], OUTDIR]
import render as R  # noqa: E402

W, H, HC = 760, 900, 725           # Renderfläche und Zuschnitt wie beim bisherigen Titelbild
CAM = dict(cam=(0.9, 0.3, 7.2), target=(0, -0.35, 0), fov=0.95, light=(-0.7, 0.9, 0.7))

def scene_column(p):
    col = R.sd_fluted(R.T(p, 0, -0.95, 0), 0.34, 0.95, n=18, depth=0.04)
    cap = R.sd_box(R.T(p, 0, 0.06, 0), np.array([0.48, 0.06, 0.48]))
    echinus = R.sd_cyl(R.T(p, 0, -0.02, 0), 0.42, 0.04)
    base = R.sd_box(R.T(p, 0, -1.95, 0), np.array([0.55, 0.07, 0.55]))
    base2 = R.sd_box(R.T(p, 0, -2.07, 0), np.array([0.7, 0.06, 0.7]))
    return np.minimum.reduce([col, cap, echinus, base, base2])

def scene_ico(angle):
    def f(p):
        q = R.rot_y(R.rot_x(R.rot_y(R.T(p, 0, 1.05, 0), 0.5), 0.35), angle)  # Drehung um die eigene y-Achse
        ico = R.sd_poly(q, 0.62, R.ICO_N)
        ring = R.sd_torus(R.rot_x(R.rot_z(R.T(p, 0, 1.05, 0), 0.35), 1.25), 1.05, 0.018)
        ring2 = R.sd_torus(R.rot_x(R.rot_z(R.T(p, 0, 1.05, 0), -0.5), 1.0), 1.25, 0.012)
        return np.minimum.reduce([ico, ring, ring2])
    return f

def engrave_layer(v, off=(0, 0)):
    obj = ~np.isnan(v)
    vv = np.nan_to_num(v)
    m = R.engrave(vv ** 0.9, period=4.0, off=off) & obj
    H_, W_ = v.shape
    ys, xs = np.mgrid[off[1]:off[1] + H_, off[0]:off[0] + W_]
    th = R.BAYER[ys % 8, xs % 8]
    m |= (np.clip((vv - 0.75) * 3, 0, 1) > th) & obj
    edge = R.binary_dilation(obj, iterations=2) & ~obj
    return m | edge, obj

def save_mask(m, path):
    a = np.where(m, 255, 0).astype(np.uint8)
    Image.merge('LA', (Image.new('L', (m.shape[1], m.shape[0]), 0), Image.fromarray(a))).save(path, optimize=True)

# Säule (statisch)
v = R.render(scene_column, W, H, **CAM)
col_m, col_obj = engrave_layer(v)
save_mask(col_m[:HC], f"{OUTDIR}/hero-column.png")
print("Säule fertig", flush=True)

# Ikosaeder: Fenster bestimmen (Ringe reichen am weitesten)
probe = R.render(scene_ico(0.0), W // 4, H // 4, **CAM)
ys, xs = np.where(~np.isnan(probe))
x0, x1 = max(0, xs.min() * 4 - 16), min(W, xs.max() * 4 + 20)
y0, y1 = max(0, ys.min() * 4 - 16), min(HC, ys.max() * 4 + 20)
cw, ch = x1 - x0, y1 - y0
print("Fenster", x0, y0, cw, ch, flush=True)

frames, union = [], np.zeros((H, W), bool)
for k in range(N):
    ang = np.pi * k / N   # halbe Umdrehung: die y-Achse ist eine 2-zählige Symmetrieachse -> nahtlose Schleife
    v = R.render(scene_ico(ang), W, H, crop=(x0, y0, cw, ch), **CAM)
    m, obj = engrave_layer(v, off=(x0, y0))
    frames.append(m)
    union[y0:y0 + ch, x0:x0 + cw] |= obj
    print("Bild", k + 1, "von", N, flush=True)
sprite = np.concatenate(frames, axis=1)
save_mask(sprite, f"{OUTDIR}/hero-ico.png")

# Strahlen, ausgespart um Säule und Ikosaeder
r = R.rays(W, H, W * 0.5, H * 0.3, n=110)
r &= ~R.binary_dilation(col_obj | union, iterations=6)
save_mask(r[:HC], f"{OUTDIR}/hero-rays.png")

# Kontrollbild: alle Ebenen übereinander (Bild 0)
comp = col_m[:HC] | r[:HC]
comp[y0:y0 + ch, x0:x0 + cw] |= frames[0]
save_mask(comp, f"{OUTDIR}/hero-check.png")
print(f"WINDOW {x0} {y0} {cw} {ch} {W} {HC} {N}")
