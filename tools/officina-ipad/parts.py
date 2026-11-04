"""Zusatzmotive für den iPad-Hintergrund v3, direkt in Zielgröße (halbe Auflösung) gerendert."""
import sys
import numpy as np
which, size = sys.argv[1], int(sys.argv[2])
sys.argv = [sys.argv[0], 'out']
import render as R

def eng(v, period=4.0):
    obj = ~np.isnan(v); vv = np.nan_to_num(v)
    H, W = v.shape; ys, xs = np.mgrid[0:H, 0:W]
    m = R.engrave(vv ** 0.9, period=period) & obj
    m |= (np.clip((vv - 0.75) * 3, 0, 1) > R.BAYER[ys % 8, xs % 8]) & obj
    edge = R.binary_dilation(obj, iterations=2) & ~obj
    return m | edge, obj

def planet(p):
    s = R.sd_sphere(p, 1.0)
    ring = R.sd_torus(R.rot_z(R.rot_x(p, 1.32), 0.38), 1.7, 0.012)
    ring2 = R.sd_torus(R.rot_z(R.rot_x(p, 1.32), 0.38), 1.55, 0.03)
    return np.minimum.reduce([s, ring, ring2])
def dode(p): return R.sd_poly(R.rot_y(R.rot_x(p, 0.6), 0.3), 0.8, R.DODE_N)
def cube(p): return R.sd_box(R.rot_x(R.rot_y(p, 0.7), 0.5), np.array([0.6, 0.6, 0.6])) - 0.05
def octa(p):
    q = np.abs(R.rot_y(R.rot_x(p, 0.4), 0.5)); return (q[..., 0] + q[..., 1] + q[..., 2] - 0.9) * 0.577

if which == 'planet':
    v = R.render(planet, size, size, cam=(0, 0.35, 4.6), fov=0.95, light=(-0.7, 0.9, 0.7))
elif which == 'temple':
    v = R.render(R.scene_temple, size, int(size * 0.62), cam=(0.85, -0.05, 7.2), target=(0, -0.3, 0), fov=0.55)
elif which == 'arch':
    v = R.render(R.scene_arch, size, int(size * 0.55), cam=(0.85, 0.35, 7.2), target=(0, 0.1, 0), fov=0.6, light=(-0.7, 0.9, 0.7))
else:
    v = R.render({'dode': dode, 'cube': cube, 'octa': octa}[which], size, size, cam=(0.4, 0.15, 3.2), fov=0.9, light=(-0.7, 0.9, 0.7))
m, o = eng(v)
np.savez_compressed(f'part-{which}-{size}.npz', obj=m, cover=o)
print(which, m.shape, flush=True)
