"""Pro Farbe ein eigener Himmelskörper (planet-*) und ein eigenes Bauwerk (model-*), einheitliche Kamera.
Aufruf: python3 parts2.py planet|model <name> <größe>"""
import sys
import numpy as np
kind, name, size = sys.argv[1], sys.argv[2], int(sys.argv[3])
sys.argv = [sys.argv[0], 'out']
import render as R
from render import T, rot_x, rot_y, rot_z, sd_sphere, sd_box, sd_torus, sd_cyl, sd_fluted, sd_poly, sd_pyramid
B3 = lambda x, y, z: np.array([x, y, z])
U = np.minimum.reduce

def eng(v, period=4.0):
    obj = ~np.isnan(v); vv = np.nan_to_num(v)
    H, W = v.shape; ys, xs = np.mgrid[0:H, 0:W]
    m = R.engrave(vv ** 0.9, period=period) & obj
    m |= (np.clip((vv - 0.75) * 3, 0, 1) > R.BAYER[ys % 8, xs % 8]) & obj
    edge = R.binary_dilation(obj, iterations=2) & ~obj
    return m | edge, obj

# ---------- Himmelskörper ----------
def ringed(p):
    q = rot_z(rot_x(p, 1.32), 0.38)
    return U([sd_sphere(p, 1.0), sd_torus(q, 1.7, 0.012), sd_torus(q, 1.55, 0.03)])
def moons(p):
    return U([sd_sphere(p, 0.85), sd_sphere(T(p, 1.3, 0.55, 0.3), 0.2), sd_sphere(T(p, -1.25, -0.75, 0.5), 0.13), sd_sphere(T(p, 0.9, -1.05, 0.6), 0.08)])
def crescent(p):
    return U([np.maximum(sd_sphere(p, 1.05), -sd_sphere(T(p, 0.62, 0.28, 0.05), 0.92)), sd_sphere(T(p, 0.55, -0.15, 0.2), 0.12)])
def tilted_rings(p):
    q = rot_z(rot_x(p, 0.75), 1.1)
    return U([sd_sphere(p, 0.8), sd_torus(q, 1.3, 0.012), sd_torus(q, 1.45, 0.02), sd_torus(q, 1.62, 0.01)])
_rng = np.random.default_rng(4)
_cr = [(d / np.linalg.norm(d), r) for d, r in zip(_rng.normal(size=(26, 3)), _rng.uniform(0.08, 0.28, 26))]
def cratered(p):
    d = sd_sphere(p, 1.0)
    for v, r in _cr:
        if v[2] < -0.2: continue
        d = np.maximum(d, -sd_sphere(T(p, *(v * (1.0 + r * 0.55))), r))
        d = np.minimum(d, sd_torus(rot_x(rot_y(T(p, *(v * 1.0)), -np.arctan2(v[0], v[2])), np.pi / 2 - np.arcsin(np.clip(v[1], -1, 1))), r * 1.02, 0.018))
    return d
def sun(p):
    rr = np.hypot(p[..., 0], p[..., 1]); a = np.arctan2(p[..., 1], p[..., 0])
    spike = 0.55 * np.clip(np.cos(a * 9), 0, 1) ** 10 + 0.3 * np.clip(np.cos(a * 9 + np.pi), 0, 1) ** 10
    flat = np.exp(-(p[..., 2] / 0.25) ** 2)
    return (np.linalg.norm(p, axis=-1) - 0.78 - spike * flat * np.clip(rr / 0.78, 0, 1)) * 0.5
def banded(p):
    return U([(sd_sphere(p, 1.0) + 0.018 * np.sin(p[..., 1] * 16 + 1.5 * np.sin(p[..., 0] * 3))) * 0.8, sd_sphere(T(p, -1.35, 0.7, 0.4), 0.17)])
def armillary(p): return R.scene_armillary(p * 1.15) / 1.15
def moon_ring(p):
    q = rot_z(rot_x(p, 1.15), -0.3)
    return U([sd_sphere(p, 0.78), sd_torus(q, 1.35, 0.022), sd_sphere(T(p, 1.18, -0.42, 0.55), 0.17)])
def torus_world(p):
    return U([sd_torus(rot_z(rot_x(p, 1.0), 0.3), 0.95, 0.4), sd_sphere(T(p, 0, 0, 0), 0.22)])
def geodesic(p):
    return np.maximum(sd_poly(p, 1.0, R.ICO_N), sd_poly(p, 1.0, R.DODE_N))
def ocean(p):
    q = rot_z(rot_x(p, 1.4), 0.15)
    rip = 0.022 * np.sin(p[..., 0] * 9 + p[..., 2] * 4) * np.sin(p[..., 1] * 7)
    return U([(sd_sphere(p, 0.95) + rip) * 0.8, sd_torus(q, 1.5, 0.014), sd_torus(q, 1.62, 0.008)])

PLANETS = dict(ringed=(ringed, None), moons=(moons, None), crescent=(crescent, None), tilted_rings=(tilted_rings, None),
               cratered=(cratered, (-0.9, 0.6, 0.5)), sun=(sun, (-0.3, 0.4, 1.0)), banded=(banded, None), armillary=(armillary, None),
               moon_ring=(moon_ring, None), torus_world=(torus_world, None), geodesic=(geodesic, None), ocean=(ocean, None))

# ---------- Bauwerke (Unterkante y = -1.33) ----------
def temple(p): return R.scene_temple(p)
def obelisk(p):
    base = U([sd_box(T(p, 0, -1.25, 0), B3(0.55, 0.08, 0.55)), sd_box(T(p, 0, -1.09, 0), B3(0.42, 0.08, 0.42))])
    y = p[..., 1]; w = 0.27 - 0.06 * np.clip((y + 1.0) / 3.0, 0, 1)
    q = np.abs(p); shaft = np.maximum.reduce([q[..., 0] - w, q[..., 2] - w, -(y + 1.01), y - 2.0]) * 0.9
    tip = sd_pyramid(T(p, 0, 2.0, 0), 0.21, 0.32)
    return U([base, shaft, tip])
def ziggurat(p):
    d = 1e9
    for i, (w, h) in enumerate([(1.6, 0.28), (1.25, 0.26), (0.92, 0.24), (0.62, 0.22)]):
        y0 = -1.33 + sum([0.56, 0.52, 0.48, 0.44][:i]) + h
        d = np.minimum(d, sd_box(T(p, 0, y0, 0), B3(w, h, w * 0.8)))
    stair = sd_box(rot_x(T(p, 0, -0.7, 1.1), 0.62), B3(0.22, 0.05, 0.9))
    shrine = sd_box(T(p, 0, 0.83, 0), B3(0.32, 0.2, 0.28))
    return U([d, np.maximum(stair, -(p[..., 1] + 1.33)), shrine])
def arch(p):
    body = sd_box(T(p, 0, -0.38, 0), B3(1.25, 0.95, 0.38))
    hole = U([sd_cyl(rot_x(T(p, 0, -0.35, 0), np.pi / 2), 0.42, 0.6), sd_box(T(p, 0, -0.95, 0), B3(0.42, 0.6, 0.6))])
    side = U([sd_cyl(rot_x(T(p, s, -0.65, 0), np.pi / 2), 0.17, 0.6) for s in (-0.85, 0.85)] + [sd_box(T(p, s, -1.05, 0), B3(0.17, 0.4, 0.6)) for s in (-0.85, 0.85)])
    body = np.maximum(np.maximum(body, -hole), -side)
    attic = sd_box(T(p, 0, 0.78, 0), B3(1.18, 0.22, 0.34))
    cornice = sd_box(T(p, 0, 0.55, 0), B3(1.32, 0.04, 0.42))
    cols = U([sd_fluted(T(p, x, -0.42, 0.43), 0.09, 0.9, n=10, depth=0.015) for x in (-1.12, -0.55, 0.55, 1.12)])
    return U([body, attic, cornice, cols])
def ruins(p):
    plinth = U([sd_box(T(p, 0, -1.25, 0), B3(1.6, 0.08, 0.7)), sd_box(T(p, 0, -1.1, 0), B3(1.45, 0.07, 0.55))])
    d = plinth
    for x, z, h, tilt in [(-0.95, 0, 1.6, 0.35), (0.0, -0.1, 0.95, -0.5), (0.9, 0.05, 0.45, 0.25)]:
        c = sd_fluted(T(p, x, -1.03 + h / 2, z), 0.17, h / 2, n=12, depth=0.025)
        cut = (rot_z(T(p, x, -1.03 + h, z), tilt))[..., 1]
        c = np.maximum(c, cut)
        cap = sd_box(T(p, x, -1.03 + 1.6 + 0.07, z), B3(0.26, 0.07, 0.26)) if h > 1.5 else 1e9
        d = U([d, c, np.maximum(cap, cut + 0.2) if h > 1.5 else c])
    drum = sd_cyl(rot_z(T(p, 0.55, -0.85, 0.55), np.pi / 2 - 0.3), 0.17, 0.22)
    return U([d, drum])
def lighthouse(p):
    y = p[..., 1]; r = 0.46 - 0.12 * np.clip((y + 1.1) / 2.6, 0, 1)
    tower = np.maximum(np.hypot(p[..., 0], p[..., 2]) - r, np.abs(y - 0.2) - 1.3) * 0.9
    bands = sd_torus(T(p, 0, -0.3, 0), 0.43, 0.025)
    gallery = sd_cyl(T(p, 0, 1.55, 0), 0.5, 0.05)
    rail = sd_torus(T(p, 0, 1.75, 0), 0.47, 0.018)
    lantern = sd_cyl(T(p, 0, 1.82, 0), 0.24, 0.22)
    dome = np.maximum(sd_sphere(T(p, 0, 2.04, 0), 0.27), -(y - 2.04))
    base = sd_box(T(p, 0, -1.22, 0), B3(0.7, 0.11, 0.7))
    door = sd_box(T(p, 0.1, -0.85, 0.45), B3(0.09, 0.17, 0.12))
    return np.maximum(U([tower, bands, gallery, rail, lantern, dome, base]), -door)
def pyramids(p):
    a = sd_pyramid(rot_y(T(p, 0.25, -1.33, 0), 0.55), 1.25, 1.55)
    b = sd_pyramid(rot_y(T(p, -1.35, -1.33, -0.6), 0.55), 0.62, 0.78)
    c = sd_pyramid(rot_y(T(p, 1.55, -1.33, 0.7), 0.55), 0.38, 0.48)
    return U([a, b, c])
def tholos(p):
    plat = U([sd_cyl(T(p, 0, -1.26, 0), 1.15, 0.07), sd_cyl(T(p, 0, -1.13, 0), 1.03, 0.06)])
    cols = U([sd_fluted(T(p, 0.88 * np.cos(a), -0.42, 0.88 * np.sin(a)), 0.085, 0.65, n=8, depth=0.012) for a in np.linspace(0, 2 * np.pi, 12, endpoint=False)])
    ent = sd_cyl(T(p, 0, 0.32, 0), 1.02, 0.1)
    drum = sd_cyl(T(p, 0, 0.5, 0), 0.8, 0.12)
    dome = np.maximum(sd_sphere(T(p, 0, 0.6, 0), 0.82), -(p[..., 1] - 0.6))
    lantern = sd_cyl(T(p, 0, 1.47, 0), 0.1, 0.07)
    cella = sd_cyl(T(p, 0, -0.42, 0), 0.6, 0.65)
    return U([plat, cols, ent, drum, dome, lantern, cella])
def colosseum(p):
    rr = np.hypot(p[..., 0], p[..., 2] * 1.25)
    a = np.arctan2(p[..., 2] * 1.25, p[..., 0]); n = 22
    wall = np.maximum(np.abs(rr - 1.3) - 0.14, np.abs(p[..., 1] + 0.65) - 0.68) * 0.8
    ac = (a / (2 * np.pi / n)); fr = (ac - np.round(ac)) * (2 * np.pi / n) * 1.3
    holes = 1e9
    for yc in (-1.0, -0.42):
        holes = np.minimum(holes, np.maximum(np.abs(fr) - 0.11, np.abs(p[..., 1] - yc) - 0.2))
    wall = np.maximum(wall, -holes)
    broken = p[..., 1] - (0.05 - 0.55 * np.clip(p[..., 0] + 0.2, 0, 2))
    wall = np.maximum(wall, broken)
    base = sd_cyl(T(p, 0, -1.29, 0) * B3(1, 1, 1.25), 1.5, 0.04) * 0.8
    return U([wall, base])
def trilithons(p):
    d = sd_box(T(p, 0, -1.29, 0), B3(1.9, 0.04, 0.9))
    for x, z, a, s in [(-1.1, 0.0, 0.45, 0.85), (0.15, -0.35, 0.0, 1.0), (1.3, 0.1, -0.5, 0.8)]:
        q = rot_y(T(p, x, -1.33, z), a)
        up = U([sd_box(T(q, sx * 0.33 * s, 0.85 * s, 0), B3(0.16 * s, 0.85 * s, 0.13 * s)) - 0.02 for sx in (-1, 1)])
        lin = sd_box(T(q, 0, 1.78 * s, 0), B3(0.55 * s, 0.1 * s, 0.14 * s)) - 0.02
        d = U([d, up, lin])
    stone = sd_box(rot_z(T(p, 0.65, -1.18, 0.75), 1.3), B3(0.12, 0.35, 0.1)) - 0.02
    return U([d, stone])
def observatory(p):
    base = U([sd_box(T(p, 0, -1.2, 0), B3(1.1, 0.13, 0.9)), sd_cyl(T(p, 0, -0.6, 0), 0.82, 0.48)])
    dome = np.maximum(sd_sphere(T(p, 0, -0.12, 0), 0.86), -(p[..., 1] + 0.12))
    slit = sd_box(rot_z(T(p, 0.15, 0.35, 0.5), -0.35), B3(0.12, 0.6, 0.6))
    dome = np.maximum(dome, -slit)
    scope = sd_cyl(rot_z(T(p, 0.35, 0.55, 0.15), -0.6), 0.1, 0.65)
    ring = sd_torus(T(p, 0, -0.12, 0), 0.86, 0.035)
    return U([base, dome, scope, ring])
def portal(p):
    steps = U([sd_box(T(p, 0, -1.27, 0), B3(1.3, 0.06, 0.6)), sd_box(T(p, 0, -1.15, 0), B3(1.0, 0.06, 0.45)), sd_box(T(p, 0, -1.03, 0), B3(0.7, 0.06, 0.32))])
    q = rot_x(T(p, 0, 0.0, 0), np.pi / 2)
    ring = sd_torus(q, 0.92, 0.1); inner = sd_torus(q, 0.72, 0.03)
    q2 = np.abs(rot_y(T(p, 0, 0, 0), 0)); spokes = 1e9
    for a in np.linspace(0, np.pi, 4, endpoint=False):
        r2 = rot_z(p, a); spokes = np.minimum(spokes, np.maximum(sd_box(r2, B3(0.03, 0.82, 0.03)), -(np.hypot(p[..., 0], p[..., 1]) - 0.74) * -1 if False else sd_box(r2, B3(0.03, 0.82, 0.03))))
    spokes = np.maximum(spokes, 0.72 - np.hypot(p[..., 0], p[..., 1]))
    stand = sd_box(T(p, 0, -0.95, 0), B3(0.25, 0.06, 0.18))
    gem = sd_poly(rot_y(p, 0.4), 0.16, R.ICO_N)
    return U([steps, ring, inner, spokes, stand, gem])

MODELS = dict(temple=temple, obelisk=obelisk, ziggurat=ziggurat, arch=arch, ruins=ruins, lighthouse=lighthouse,
              pyramids=pyramids, tholos=tholos, colosseum=colosseum, trilithons=trilithons, observatory=observatory, portal=portal)

if kind == 'planet':
    f, light = PLANETS[name]
    v = R.render(f, size, size, cam=(0, 0.35, 4.6), fov=0.95, light=light or (-0.7, 0.9, 0.7))
else:
    # gleiche Pixelgröße wie der Tempel (235 px hoch bei fov 0.55), aber hohes Format für Türme
    H = int(size * 1.3); fov = 0.55 * H / (size * 0.62)
    v = R.render(MODELS[name], size, H, cam=(0.85, -0.05 + 0.6, 7.2), target=(0, 0.3, 0), fov=fov)
m, o = eng(v)
ys, xs = np.where(o)
if kind == 'model':
    y0, y1, x0, x1 = ys.min(), ys.max() + 3, max(0, xs.min() - 3), xs.max() + 3
    m, o = m[y0:y1, x0:x1], o[y0:y1, x0:x1]
np.savez_compressed(f'p2-{kind}-{name}-{size}.npz', obj=m, cover=o)
print(kind, name, size, m.shape, flush=True)
