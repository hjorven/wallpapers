#!/usr/bin/env python3
"""Render the generated wallpaper themes and register them in wallpapers.json.

    python3 tools/gen/run.py shanshui terrazzo     render these styles in full size
    python3 tools/gen/run.py all                   render every style
    python3 tools/gen/run.py --sheet shanshui      only a small contact sheet to look at (sheet-<style>.jpg)

Then run  python3 tools/build.py  for previews and ZIPs. Needs numpy and pillow.
Every image is reproducible: the seed comes from the style, the variant and the format.
"""
import importlib
import json
import sys
import zlib
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE))
from common import SIZES  # noqa: E402

STYLES = ["shanshui", "suminagashi", "terrazzo", "seigaiha", "azulejo",
          "artdeco", "memphis", "topo", "tessellae", "neonnoir"]
DEVICE = "ipad-9"
HOWTO = ["Tap Landscape or Portrait, then hold the image and choose Save to Photos.",
         "In Safari, open a new tab, tap Edit at the bottom of the start page and turn on Background Image.",
         "Tap + and pick the wallpaper."]


def seed(style, slug, tag):
    return zlib.crc32(f"{style}/{slug}/{tag}".encode())


def sheet(mod, scale=0.18):
    tiles = []
    for v in mod.VARIANTS:
        row = []
        for tag in ("quer", "hoch"):
            w, h = SIZES[tag]
            im = mod.render(int(w * scale), int(h * scale), v, np.random.default_rng(seed(mod.ID, v[0], tag)))
            row.append(im)
        tiles.append(row)
    qw, qh = tiles[0][0].size
    hw, hh = tiles[0][1].size
    cw, ch = qw + hw + 30, max(qh, hh) + 20
    cols = 2
    rows = (len(tiles) + 1) // cols
    out = Image.new("RGB", (cols * cw + 10, rows * ch + 10), (40, 40, 40))
    for i, (q, p) in enumerate(tiles):
        x, y = 10 + (i % cols) * cw, 10 + (i // cols) * ch
        out.paste(q, (x, y))
        out.paste(p, (x + qw + 10, y))
    path = HERE / f"sheet-{mod.ID}.jpg"
    out.save(path, quality=88)
    print("sheet", path)


def full(mod, data):
    ext = mod.FORMAT
    folder = ROOT / "themes" / mod.ID / "ipad" / "full"
    folder.mkdir(parents=True, exist_ok=True)
    entries = []
    for n, v in enumerate(mod.VARIANTS, 1):
        slug, title, fam = v[0], v[1], v[2]
        images = []
        for tag, orient in (("quer", "landscape"), ("hoch", "portrait")):
            w, h = SIZES[tag]
            name = f"{n:02d}-{slug}-{tag}.{ext}"
            im = mod.render(w, h, v, np.random.default_rng(seed(mod.ID, slug, tag)))
            assert im.size == (w, h), (name, im.size)
            if ext == "jpg":
                im.save(folder / name, quality=86, optimize=True, progressive=True)
            else:
                # flat artwork: a 64-colour palette keeps edges smooth and files small
                im.quantize(colors=64, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).save(folder / name, optimize=True)
            images.append({"orientation": orient, "width": w, "height": h,
                           "src": f"themes/{mod.ID}/ipad/full/{name}",
                           "thumb": f"themes/{mod.ID}/ipad/thumbs/{n:02d}-{slug}-{tag}.jpg"})
        colour = mod.colour(v) if hasattr(mod, "colour") else v[5 if len(v) > 5 else 3]
        entries.append({"id": f"{mod.ID}-{slug}", "theme": mod.ID, "device": DEVICE, "number": f"{n:02d}",
                        "title": title, "colour": colour, "colourFamily": fam, "motifs": v[-1], "images": images})
        print(mod.ID, n, slug, flush=True)
    data["wallpapers"] = [w for w in data["wallpapers"] if w["theme"] != mod.ID] + entries
    theme = {"id": mod.ID, "name": mod.NAME, "tagline": mod.TAGLINE, "description": mod.DESCRIPTION,
             "generator": f"tools/gen/{mod.ID}.py",
             "packs": [{"device": DEVICE, "zip": f"downloads/{mod.ID}-ipad.zip", "howto": HOWTO}]}
    old = [t for t in data["themes"] if t["id"] == mod.ID]
    if old:
        data["themes"][data["themes"].index(old[0])] = theme
    else:
        data["themes"].append(theme)


def main():
    args = sys.argv[1:]
    only_sheet = "--sheet" in args
    names = [a for a in args if not a.startswith("--")]
    if names == ["all"]:
        names = STYLES
    if not names:
        sys.exit(__doc__)
    path = ROOT / "wallpapers.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    for name in names:
        mod = importlib.import_module(name)
        if only_sheet:
            sheet(mod)
        else:
            full(mod, data)
    if not only_sheet:
        order = ["officina"] + STYLES
        data["themes"].sort(key=lambda t: order.index(t["id"]) if t["id"] in order else 99)
        data["wallpapers"].sort(key=lambda w: (order.index(w["theme"]) if w["theme"] in order else 99, w.get("number", "")))
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print("wallpapers.json updated")


if __name__ == "__main__":
    main()
