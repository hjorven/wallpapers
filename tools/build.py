#!/usr/bin/env python3
"""Check wallpapers.json and build what the page needs from it.

    python3 tools/build.py           check, make missing thumbnails, rebuild ZIPs
    python3 tools/build.py --check   only check, change nothing (exit code 1 on errors)

Needs Pillow:  pip install pillow
"""
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
THUMB = 480  # longest side of a preview in pixels
ORIENTATIONS = {"landscape", "portrait", "square"}


def main():
    check_only = "--check" in sys.argv[1:]
    try:
        from PIL import Image
    except ImportError:
        sys.exit("Pillow is missing: pip install pillow")

    data = json.loads((ROOT / "wallpapers.json").read_text(encoding="utf-8"))
    errors, made = [], []
    changed = [False]

    def need(cond, msg):
        if not cond:
            errors.append(msg)
        return cond

    colours = {c["id"] for c in data["colours"]}
    devices = {d["id"] for d in data["devices"]}
    themes = {t["id"]: t for t in data["themes"]}
    ids = set()

    for w in data["wallpapers"]:
        wid = w.get("id", "?")
        need(wid not in ids, f"{wid}: id is used twice")
        ids.add(wid)
        for key in ("theme", "device", "title", "colour", "colourFamily", "images"):
            need(key in w, f"{wid}: field '{key}' is missing")
        need(w.get("theme") in themes, f"{wid}: unknown theme '{w.get('theme')}'")
        need(w.get("device") in devices, f"{wid}: unknown device '{w.get('device')}'")
        need(w.get("colourFamily") in colours, f"{wid}: unknown colourFamily '{w.get('colourFamily')}'")
        for img in w.get("images", []):
            src = ROOT / img["src"]
            need(img.get("orientation") in ORIENTATIONS, f"{wid}: orientation must be one of {sorted(ORIENTATIONS)}")
            if not need(src.is_file(), f"{wid}: file not found: {img['src']}"):
                continue
            size = src.stat().st_size
            if img.get("bytes") != size:
                if check_only:
                    need(False, f"{wid}: bytes for {img['src']} is out of date (run without --check)")
                else:
                    img["bytes"] = size
                    changed[0] = True
            with Image.open(src) as im:
                need(im.size == (img["width"], img["height"]),
                     f"{wid}: {img['src']} is {im.size[0]}x{im.size[1]}, wallpapers.json says {img['width']}x{img['height']}")
                thumb = ROOT / img["thumb"]
                if not thumb.is_file():
                    if check_only:
                        need(False, f"{wid}: preview missing: {img['thumb']} (run without --check to make it)")
                    else:
                        thumb.parent.mkdir(parents=True, exist_ok=True)
                        t = im.convert("RGB")
                        t.thumbnail((THUMB, THUMB))
                        t.save(thumb, quality=85, optimize=True)
                        made.append(img["thumb"])

    for t in data["themes"]:
        for pack in t.get("packs", []):
            need(pack.get("device") in devices, f"theme {t['id']}: unknown device '{pack.get('device')}' in packs")
            for ov in pack.get("overviews", []):
                need((ROOT / ov["src"]).is_file(), f"theme {t['id']}: overview not found: {ov['src']}")
            files = [ROOT / i["src"] for w in data["wallpapers"]
                     if w.get("theme") == t["id"] and w.get("device") == pack.get("device")
                     for i in w.get("images", [])]
            if not pack.get("zip"):
                continue
            z = ROOT / pack["zip"]
            if check_only:
                need(z.is_file(), f"theme {t['id']}: ZIP missing: {pack['zip']}")
            elif files and all(f.is_file() for f in files):
                z.parent.mkdir(parents=True, exist_ok=True)
                with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
                    for f in sorted(files):
                        info = zipfile.ZipInfo(f.name, date_time=(2026, 1, 1, 0, 0, 0))
                        info.compress_type = zipfile.ZIP_DEFLATED
                        zf.writestr(info, f.read_bytes())
                made.append(pack["zip"])

    if changed[0]:
        (ROOT / "wallpapers.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        made.append("wallpapers.json (file sizes)")
    for m in made:
        print("made", m)
    if errors:
        print(f"\n{len(errors)} problem(s):")
        for e in errors:
            print("  -", e)
        sys.exit(1)
    print(f"ok: {len(data['themes'])} theme(s), {len(data['wallpapers'])} wallpaper(s), "
          f"{sum(len(w['images']) for w in data['wallpapers'])} image(s)")


if __name__ == "__main__":
    main()
