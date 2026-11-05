#!/usr/bin/env python3
"""Build a wallpaper for any resolution: the layout is rendered anew, not cropped.

    python3 tools/gen/make.py silverface-peak-level 1179x2556          one wallpaper
    python3 tools/gen/make.py silverface 2560x1440                     every wallpaper of a theme
    python3 tools/gen/make.py lowpoly-gold-trace 3840x2160 -o out.jpg  choose the file name

Files go to the current folder as <id>-<width>x<height>.jpg. The web page runs the same
function (make) in the browser through Pyodide. Needs numpy and pillow.
"""
import importlib
import io
import sys
import zlib
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402


def variant(style, slug):
    mod = importlib.import_module(style)
    for v in mod.VARIANTS:
        if v[0] == slug:
            return mod, v
    raise KeyError(f"{style} has no wallpaper {slug!r}")


def make(style, slug, w, h, budget=None):
    """Render one wallpaper at w x h. The seed matches the stored images, so 1620x2160 gives the same picture."""
    common.BUDGET = budget
    mod, v = variant(style, slug)
    tag = "quer" if w > h else "hoch"
    im = mod.render(w, h, v, np.random.default_rng(zlib.crc32(f"{style}/{slug}/{tag}".encode())))
    if im.size != (w, h):
        im = im.resize((w, h))
    return im.convert("RGB")


def jpeg(style, slug, w, h, budget=None, quality=92):
    buf = io.BytesIO()
    make(style, slug, w, h, budget).save(buf, "JPEG", quality=quality)
    return buf.getvalue()


def main():
    args = sys.argv[1:]
    out = None
    if "-o" in args:
        i = args.index("-o")
        out = args[i + 1]
        del args[i:i + 2]
    if len(args) != 2 or "x" not in args[1]:
        sys.exit(__doc__)
    name, size = args
    w, h = (int(n) for n in size.lower().split("x"))
    if not (64 <= w <= 12000 and 64 <= h <= 12000):
        sys.exit("Width and height must be between 64 and 12000 pixels.")
    if "-" in name:
        style, slug = name.split("-", 1)
        jobs = [(style, slug)]
    else:
        style = name
        jobs = [(style, v[0]) for v in importlib.import_module(style).VARIANTS]
    for style, slug in jobs:
        path = out if out and len(jobs) == 1 else f"{style}-{slug}-{w}x{h}.jpg"
        make(style, slug, w, h).save(path, quality=92)
        print(path, flush=True)


if __name__ == "__main__":
    main()
