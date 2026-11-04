# Tools for the Officina iPad set

The scripts the twelve iPad wallpapers were made with, kept for reference. They need `numpy` and `pillow`.

- `render.py`: raymarching in NumPy plus Bayer, Floyd–Steinberg and line-screen dithering (the same file as in the portfolio repo).
- `parts.py`, `parts2.py`, `subject.py`: render single objects (planets, buildings, solids) into `.npz` masks.
- `safari_bg_farben.py`: composes the masks into the 24 final images, one landscape and one portrait per accent colour.
- `safari_bg2.py`, `safari_bg3.py`, `hero_layers.py`: earlier versions and helpers.

The parts have to exist as `.npz` files in the working directory before `safari_bg_farben.py` runs.
