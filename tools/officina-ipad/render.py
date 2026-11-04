"""Rendert klassisch-futuristische Objekte per Raymarching und rastert sie auf 1 Bit.
Ausgabe: PNGs mit zwei Farben (bzw. Farbe + transparent)."""
import numpy as np
from PIL import Image
import sys, os

OUT = sys.argv[1] if len(sys.argv) > 1 else "out"
os.makedirs(OUT, exist_ok=True)

def norm(v):
    return v / (np.linalg.norm(v, axis=-1, keepdims=True) + 1e-9)

def length(p):
    return np.linalg.norm(p, axis=-1)

# ---------- SDF-Bausteine ----------
def sd_sphere(p, r):
    return length(p) - r

def sd_box(p, b):
    q = np.abs(p) - b
    return length(np.maximum(q, 0)) + np.minimum(np.max(q, axis=-1), 0)

def sd_torus(p, R, r):
    q = np.stack([np.hypot(p[..., 0], p[..., 2]) - R, p[..., 1]], -1)
    return length(q) - r

def sd_cyl(p, r, h):
    d0 = np.hypot(p[..., 0], p[..., 2]) - r
    d1 = np.abs(p[..., 1]) - h
    d = np.stack([d0, d1], -1)
    return np.minimum(np.maximum(d0, d1), 0) + length(np.maximum(d, 0))

def sd_fluted(p, r, h, n=20, depth=0.035):
    ang = np.arctan2(p[..., 2], p[..., 0])
    rr = r - depth * np.clip(np.cos(ang * n), 0, 1) ** 0.6
    d0 = np.hypot(p[..., 0], p[..., 2]) - rr
    d1 = np.abs(p[..., 1]) - h
    d = np.stack([d0, d1], -1)
    return (np.minimum(np.maximum(d0, d1), 0) + length(np.maximum(d, 0))) * 0.8

PHI = (1 + 5 ** 0.5) / 2
def _ico_normals():
    v = []
    for a in (-1, 1):
        for b in (-1, 1):
            for c in (-1, 1):
                v.append((a, b, c))
            v.append((0, a / PHI, b * PHI)); v.append((a / PHI, b * PHI, 0)); v.append((a * PHI, 0, b / PHI))
    return norm(np.array(v, float))
ICO_N = _ico_normals()            # Flaechennormalen eines Ikosaeders
def _dode_normals():
    v = []
    for a in (-1, 1):
        for b in (-1, 1):
            v.append((0, a, b * PHI)); v.append((a, b * PHI, 0)); v.append((a * PHI, 0, b))
    return norm(np.array(v, float))
DODE_N = _dode_normals()

def sd_poly(p, r, normals):
    return np.max(p @ normals.T, axis=-1) - r

def rot_y(p, a):
    c, s = np.cos(a), np.sin(a)
    x, y, z = p[..., 0], p[..., 1], p[..., 2]
    return np.stack([c * x + s * z, y, -s * x + c * z], -1)

def rot_x(p, a):
    c, s = np.cos(a), np.sin(a)
    x, y, z = p[..., 0], p[..., 1], p[..., 2]
    return np.stack([x, c * y - s * z, s * y + c * z], -1)

def rot_z(p, a):
    c, s = np.cos(a), np.sin(a)
    x, y, z = p[..., 0], p[..., 1], p[..., 2]
    return np.stack([c * x - s * y, s * x + c * y, z], -1)

def T(p, x, y, z):
    return p - np.array([x, y, z])

# ---------- Szenen ----------
def scene_hero(p):
    # schwebendes Ikosaeder ueber einer kannelierten Saeule mit Kapitell und Sockel
    q = rot_x(rot_y(T(p, 0, 1.05, 0), 0.5), 0.35)
    ico = sd_poly(q, 0.62, ICO_N)
    ring = sd_torus(rot_x(rot_z(T(p, 0, 1.05, 0), 0.35), 1.25), 1.05, 0.018)
    ring2 = sd_torus(rot_x(rot_z(T(p, 0, 1.05, 0), -0.5), 1.0), 1.25, 0.012)
    col = sd_fluted(T(p, 0, -0.95, 0), 0.34, 0.95, n=18, depth=0.04)
    cap = sd_box(T(p, 0, 0.06, 0), np.array([0.48, 0.06, 0.48]))
    echinus = sd_cyl(T(p, 0, -0.02, 0), 0.42, 0.04)
    base = sd_box(T(p, 0, -1.95, 0), np.array([0.55, 0.07, 0.55]))
    base2 = sd_box(T(p, 0, -2.07, 0), np.array([0.7, 0.06, 0.7]))
    return np.minimum.reduce([ico, ring, ring2, col, cap, echinus, base, base2])

def scene_armillary(p):
    s = sd_sphere(p, 0.42)
    r1 = sd_torus(rot_x(p, 1.5708), 1.0, 0.035)
    r2 = sd_torus(rot_z(rot_x(p, 1.5708), 0.9), 1.0, 0.035)
    r3 = sd_torus(rot_x(p, 0.3), 1.12, 0.05)
    axis = sd_cyl(rot_z(p, 0.4), 0.025, 1.45)
    stand = sd_cyl(T(p, 0, -1.55, 0), 0.5, 0.06)
    return np.minimum.reduce([s, r1, r2, r3, axis, stand])

def scene_dice(p):
    a = sd_box(rot_x(rot_y(T(p, -0.45, -0.25, 0.2), 0.7), 0.4), np.array([0.5, 0.5, 0.5])) - 0.06
    b = sd_poly(rot_y(rot_x(T(p, 0.65, 0.55, -0.2), 0.6), 0.3), 0.45, DODE_N)
    c = sd_sphere(T(p, 0.75, -0.55, 0.5), 0.28)
    return np.minimum.reduce([a, b, c])

def scene_temple(p):
    d = sd_box(T(p, 0, -1.1, 0), np.array([1.6, 0.08, 0.7]))
    d = np.minimum(d, sd_box(T(p, 0, -1.25, 0), np.array([1.75, 0.08, 0.85])))
    d = np.minimum(d, sd_box(T(p, 0, 0.62, 0), np.array([1.6, 0.1, 0.7])))
    # Giebel als Prisma
    q = T(p, 0, 0.72, 0)
    ped = np.maximum.reduce([(q[..., 1] + np.abs(q[..., 0]) * 0.3 - 0.45) * 0.95, -q[..., 1], np.abs(q[..., 2]) - 0.7])
    d = np.minimum(d, ped)
    for x in (-1.3, -0.78, -0.26, 0.26, 0.78, 1.3):
        d = np.minimum(d, sd_fluted(T(p, x, -0.24, -0.45), 0.14, 0.8, n=12, depth=0.02))
    return d

def scene_arch(p):
    # Aquaedukt: zwei Etagen mit Rundboegen
    d = 1e9
    for y0, h, r, xs in ((-0.55, 0.75, 0.32, (-1.5, -0.75, 0, 0.75, 1.5)), (0.55, 0.38, 0.17, (-1.5, -1.125, -0.75, -0.375, 0, 0.375, 0.75, 1.125, 1.5))):
        wall = sd_box(T(p, 0, y0, 0), np.array([1.9, h / 2 + 0.2, 0.22]))
        for x in xs:
            q = T(p, x + (0.375 if r > 0.2 else 0.1875), y0 - 0.05, 0)
            hole = np.minimum(sd_cyl(rot_x(T(q, 0, 0.05, 0), 1.5708), r, 0.4), sd_box(T(q, 0, -0.4, 0), np.array([r, 0.45, 0.4])))
            wall = np.maximum(wall, -hole)
        d = np.minimum(d, wall)
    d = np.minimum(d, sd_box(T(p, 0, 1.0, 0), np.array([1.95, 0.05, 0.27])))
    return np.maximum(d, np.abs(p[..., 0]) - 1.9)

def sd_hex(p, r, h):
    x = np.abs(p[..., 0]); z = np.abs(p[..., 2])
    d0 = np.maximum(x * 0.8660254 + z * 0.5, z) - r
    d1 = np.abs(p[..., 1]) - h
    d = np.stack([d0, d1], -1)
    return np.minimum(np.maximum(d0, d1), 0) + length(np.maximum(d, 0))

def sd_pyramid(p, w, h):
    # vierseitige Pyramide, Basis bei y=0
    q = np.abs(p)
    return np.maximum((q[..., 0] + q[..., 2]) * 0.7 + p[..., 1] * 0.7 * (w / h) - w * 0.7, -p[..., 1])

def scene_hex(p):
    r = 0.36; g = 0.03
    d = 1e9
    heights = {(0,0):0.35,(1,0):0.2,(-1,0):0.12,(0,1):0.18,(0,-1):0.26,(1,-1):0.1,(-1,1):0.3,(2,-1):0.14,(-2,1):0.08,(1,1):0.12,(-1,-1):0.2,(2,0):0.06,(-2,0):0.16,(0,2):0.05,(0,-2):0.1,(1,-2):0.07,(-1,2):0.09}
    for (a, b), h in heights.items():
        cx = a * 1.7320508 * (r + g); cz = a * (r + g) + b * 2 * (r + g)
        d = np.minimum(d, sd_hex(T(p, cx, h - 0.4, cz), r, h) - 0.01)
    # Stadt: Turm + Pyramide auf dem hoechsten Feld
    d = np.minimum(d, sd_box(T(p, 0, 0.5, 0), np.array([0.12, 0.2, 0.12])))
    d = np.minimum(d, sd_pyramid(T(p, 0, 0.7, 0), 0.18, 0.28) * 0.8)
    # Bäume als Kegel auf anderen Feldern
    for cx, cz, base in ((-1 * 1.7320508 * 0.39, -1 * 0.39 + 2 * 0.39, 0.2), (0, -0.78, 0.12)):
        d = np.minimum(d, sd_pyramid(T(p, cx, base, cz), 0.12, 0.35) * 0.8)
    d = np.minimum(d, sd_sphere(T(p, 1.7320508 * 0.39, -0.05, -0.39), 0.1))
    return d

def scene_rack(p):
    d = 1e9
    for x, h in ((-0.95, 1.1), (0.0, 1.3), (0.95, 0.95)):
        q = T(p, x, h - 1.0, 0)
        body = sd_box(q, np.array([0.4, h, 0.45]))
        # Einschuebe als Rillen
        y = np.mod(q[..., 1] + h, 0.16) - 0.08
        slot = sd_box(np.stack([q[..., 0], y, q[..., 2] - 0.45], -1), np.array([0.33, 0.025, 0.04]))
        body = np.maximum(body, -slot)
        d = np.minimum(d, body)
    # Kabel als Torusboegen zwischen den Racks
    d = np.minimum(d, sd_torus(rot_x(T(p, -0.47, 1.0, 0.25), 1.5708), 0.35, 0.03))
    d = np.minimum(d, sd_torus(rot_x(T(p, 0.47, 0.95, 0.3), 1.5708), 0.3, 0.03))
    d = np.minimum(d, sd_box(T(p, 0, -1.03, 0), np.array([1.6, 0.03, 0.8])))
    return d

def scene_torus(p):
    q = rot_x(rot_z(p, 0.5), 0.9)
    t = sd_torus(q, 0.85, 0.32)
    s = sd_sphere(T(p, 0.0, 0.0, 0.0), 0.3)
    return np.minimum(t, s)

def scene_head(p):
    # stilisierter Kopf einer Statue: Schaedel, Gesicht, Nase, Hals, Brust
    skull = sd_sphere(T(p, 0, 0.55, -0.05) * np.array([1, 0.92, 1.05]), 0.62)
    face = sd_sphere(T(p, 0, 0.25, 0.18) * np.array([1.25, 0.8, 1.1]), 0.45)
    nose = sd_box(rot_x(T(p, 0, 0.28, 0.66), -0.35), np.array([0.06, 0.16, 0.06])) - 0.03
    brow = sd_torus(rot_x(T(p, 0, 0.45, 0.2), 1.35), 0.4, 0.05)
    neck = sd_cyl(T(p, 0, -0.35, -0.05), 0.3, 0.4)
    chest = sd_sphere(T(p, 0, -1.25, -0.1) * np.array([0.55, 1.1, 0.9]), 0.7)
    hair = sd_sphere(T(p, 0, 0.75, -0.2), 0.58)
    k = 0.15
    def smin(a, b):
        h = np.clip(0.5 + 0.5 * (b - a) / k, 0, 1)
        return b * (1 - h) + a * h - k * h * (1 - h)
    d = smin(skull, face); d = smin(d, nose); d = smin(d, neck); d = smin(d, chest); d = smin(d, hair)
    d = np.maximum(d, -brow + 0.02) if False else d
    # Lorbeerkranz aus kleinen Kugeln
    q = T(p, 0, 0.72, -0.08)
    ang = np.arctan2(q[..., 2], q[..., 0])
    leaf = np.hypot(np.hypot(q[..., 0], q[..., 2]) - 0.6, q[..., 1] - 0.05 * np.sin(ang * 14)) - 0.055
    leaf = np.maximum(leaf, -(q[..., 2] + 0.45))
    return np.minimum(d, leaf)

# ---------- Renderer ----------
def render(scene, W, H, cam=(0, 0, 5.5), target=(0, 0, 0), fov=1.0, light=(-0.6, 0.8, 0.6), steps=90, crop=None):
    cam = np.array(cam, float); target = np.array(target, float)
    f = norm(target - cam); r = norm(np.cross(f, [0, 1, 0])); u = np.cross(r, f)
    if crop:
        x0, y0, cw, ch = crop
        ys, xs = np.mgrid[y0:y0 + ch, x0:x0 + cw]
    else:
        ys, xs = np.mgrid[0:H, 0:W]
    SH = xs.shape
    uvx = (xs - W / 2) / H * fov; uvy = -(ys - H / 2) / H * fov
    rd = norm(f[None, None] + uvx[..., None] * r + uvy[..., None] * u)
    t = np.zeros(SH); hit = np.zeros(SH, bool)
    for _ in range(steps):
        pos = cam + rd * t[..., None]
        d = scene(pos)
        hit |= d < 0.002
        t = np.where(hit, t, t + d * 0.9)
        if np.all(hit | (t > 20)):
            break
    pos = cam + rd * t[..., None]
    e = 0.002
    n = norm(np.stack([scene(pos + [e, 0, 0]) - scene(pos - [e, 0, 0]),
                       scene(pos + [0, e, 0]) - scene(pos - [0, e, 0]),
                       scene(pos + [0, 0, e]) - scene(pos - [0, 0, e])], -1))
    L = norm(np.array(light, float))
    diff = np.clip(n @ L, 0, 1)
    # weiche Schatten
    sh = np.ones(SH); ts = np.full(SH, 0.02)
    for _ in range(40):
        d = scene(pos + n * 0.004 + L * ts[..., None])
        sh = np.minimum(sh, 8 * d / ts)
        ts += np.clip(d, 0.02, 0.25)
    sh = np.clip(sh, 0, 1)
    # Umgebungsverdeckung
    ao = np.zeros(SH)
    for i in range(1, 6):
        h = 0.06 * i
        ao += (h - scene(pos + n * h)) / (2 ** i)
    ao = np.clip(1 - 3 * ao, 0, 1)
    rim = np.clip(1 + (n * rd).sum(-1), 0, 1) ** 3
    spec = np.clip((norm(L - rd) * n).sum(-1), 0, 1) ** 40
    v = 0.08 + 0.85 * diff * (0.35 + 0.65 * sh) * ao + 0.25 * rim + 0.4 * spec
    v = np.clip(v, 0, 1)
    return np.where(hit, v, np.nan)

BAYER = np.array([[0, 48, 12, 60, 3, 51, 15, 63], [32, 16, 44, 28, 35, 19, 47, 31],
                  [8, 56, 4, 52, 11, 59, 7, 55], [40, 24, 36, 20, 43, 27, 39, 23],
                  [2, 50, 14, 62, 1, 49, 13, 61], [34, 18, 46, 30, 33, 17, 45, 29],
                  [10, 58, 6, 54, 9, 57, 5, 53], [42, 26, 38, 22, 41, 25, 37, 21]]) / 64 + 1 / 128

def bayer(v):
    H, W = v.shape
    th = np.tile(BAYER, (H // 8 + 1, W // 8 + 1))[:H, :W]
    return v > th

def floyd(v):
    v = v.copy(); H, W = v.shape; out = np.zeros_like(v, bool)
    for y in range(H):
        row = v[y]
        for x in range(W):
            o = row[x] > 0.5; out[y, x] = o; err = row[x] - o
            if x + 1 < W: row[x + 1] += err * 7 / 16
            if y + 1 < H:
                if x > 0: v[y + 1, x - 1] += err * 3 / 16
                v[y + 1, x] += err * 5 / 16
                if x + 1 < W: v[y + 1, x + 1] += err * 1 / 16
    return out

def engrave(v, period=5.0, off=(0, 0)):
    """Kupferstich-Linienraster: Linien werden in hellen Bereichen dicker."""
    H, W = v.shape
    ys, xs = np.mgrid[off[1]:off[1] + H, off[0]:off[0] + W]
    phase = (ys + 6 * np.sin(xs / 37.0) + 3 * np.sin(xs / 11.0 + ys / 23.0)) / period
    dist = np.abs(phase - np.round(phase))          # 0 in Linienmitte, 0.5 dazwischen
    return dist < v * 0.5

def save(mask, path, fg, bg=None, scale=1):
    H, W = mask.shape
    img = np.zeros((H, W, 4), np.uint8)
    img[mask] = (*fg, 255)
    if bg is not None:
        img[~mask] = (*bg, 255)
    im = Image.fromarray(img, "RGBA")
    if scale != 1:
        im = im.resize((W * scale, H * scale), Image.NEAREST)
    # auf Palette reduzieren (klein!)
    im = im.convert("RGBA")
    im.save(path, optimize=True)

def binary_dilation(m, iterations=1):
    m = m.copy()
    for _ in range(iterations):
        n = m.copy()
        n[1:] |= m[:-1]; n[:-1] |= m[1:]; n[:, 1:] |= m[:, :-1]; n[:, :-1] |= m[:, 1:]
        m = n
    return m

def rays(W, H, cx, cy, n=90, seed=1):
    """Feine Strahlen hinter dem Objekt (Gravur-Glorie)."""
    rng = np.random.default_rng(seed)
    ys, xs = np.mgrid[0:H, 0:W]
    ang = np.arctan2(ys - cy, xs - cx)
    rad = np.hypot(xs - cx, ys - cy)
    m = np.zeros((H, W), bool)
    for a in np.linspace(-np.pi, np.pi, n, endpoint=False) + rng.normal(0, 0.01, n):
        width = 0.0025 + 0.004 * rng.random()
        L = rng.uniform(0.45, 1.0) * min(W, H) * 0.62
        m |= (np.abs(np.angle(np.exp(1j * (ang - a)))) < width * 120 / np.maximum(rad, 1)) & (rad < L) & (rad > 30)
    return m

WHITE = (233, 233, 245)
BLUE = (36, 36, 255)
INK = (16, 17, 44)

def grain_bg(H, W, level, seed=0):
    rng = np.random.default_rng(seed)
    ys = np.linspace(0, 1, H)[:, None]
    return np.clip(level + 0.12 * (ys - 0.5) + rng.normal(0, 0.03, (H, W)), 0, 1)

def make_hero():
    W, H = 760, 900
    v = render(scene_hero, W, H, cam=(0.9, 0.3, 7.2), target=(0, -0.35, 0), fov=0.95, light=(-0.7, 0.9, 0.7))
    obj = ~np.isnan(v)
    m = engrave(np.nan_to_num(v) ** 0.9, period=4.0) & obj
    # zusaetzlich Bayer fuer Glanzlichter
    m |= bayer(np.clip((np.nan_to_num(v) - 0.75) * 3, 0, 1)) & obj
    # Kontur
    edge = binary_dilation(obj, iterations=2) & ~obj
    r = rays(W, H, W * 0.5, H * 0.3, n=110)
    r &= ~binary_dilation(obj, iterations=6)
    save((m | edge | r)[:760], f"{OUT}/hero.png", WHITE)

def make_card(name, scene, cam, target=(0, 0, 0), fov=1.0, light=(-0.6, 0.8, 0.6), method="bayer", bgl=0.2, seed=0):
    W, H = 240, 240   # grobes Raster, wird 2x hochskaliert: bleibt bei jeder Pixeldichte scharf
    v = render(scene, W, H, cam=cam, target=target, fov=fov, light=light)
    obj = ~np.isnan(v)
    bg = grain_bg(H, W, bgl, seed)
    full = np.where(obj, np.clip(np.nan_to_num(v) ** 0.75 * 1.1, 0, 1), bg)
    m = floyd(full) if method == "floyd" else bayer(full)
    save(m, f"{OUT}/{name}.png", BLUE, INK, scale=2)

if __name__ == "__main__":
    which = sys.argv[2:] or ["hero", "armillary", "dice", "temple", "torus", "arch"]
    if "hero" in which: make_hero()
    if "armillary" in which: make_card("armillary", scene_armillary, (1.2, 0.8, 5.2), fov=0.95, seed=1)
    if "dice" in which: make_card("dice", scene_dice, (0.5, 1.2, 5.0), fov=0.95, method="floyd", seed=2)
    if "temple" in which: make_card("temple", scene_temple, (2.6, 0.9, 6.4), target=(0, -0.2, 0), fov=0.85, seed=3)
    if "hex" in which: make_card("hex", scene_hex, (2.2, 2.6, 3.6), target=(0, -0.2, 0), fov=0.95, light=(-0.5, 0.9, 0.5), seed=6)
    if "rack" in which: make_card("rack", scene_rack, (2.4, 1.0, 5.2), target=(0, 0.05, 0), fov=0.9, light=(-0.6, 0.8, 0.7), seed=7)
    if "torus" in which: make_card("torus", scene_torus, (0, 0.4, 4.6), fov=0.95, method="floyd", seed=4)
    if "arch" in which: make_card("arch", scene_arch, (2.4, 0.4, 6.0), target=(0, 0.1, 0), fov=0.85, light=(-0.5, 0.7, 0.8), seed=5)
