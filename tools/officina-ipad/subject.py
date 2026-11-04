"""Rendert Säule + Ikosaeder (Bild F) direkt in Zielgröße, statt die Maske zu skalieren."""
import sys
import numpy as np
from PIL import Image
scale = float(sys.argv[1]); tag = sys.argv[2]
sys.argv = [sys.argv[0], 'out']
import render as R
src = open('hero_layers.py').read()
exec(src.split('import render as R  # noqa: E402')[1].split('# Säule (statisch)')[0])
W2, H2 = int(W * scale), int(H * scale)
F = 5
v = R.render(scene_column, W2, H2, **CAM); m, o = engrave_layer(v)
vi = R.render(scene_ico(np.pi * F / 24), W2, H2, **CAM); mi, oi = engrave_layer(vi)
oi_fill = R.binary_dilation(oi, iterations=2)
obj = (m & ~oi_fill) | mi                 # Ikosaeder vor der Säule
cover = o | oi
hc = int(HC * scale)
np.savez_compressed(f'subject-{tag}.npz', obj=obj[:hc], cover=cover[:hc])
print(tag, obj[:hc].shape)
