# Wallpapers

A growing collection of 1-bit engraving wallpapers by [hjorven](https://github.com/hjorven), free to download.

Live: https://hjorven.github.io/wallpapers/

## Sets

| Set | Device | Resolution | Images |
| --- | --- | --- | --- |
| Officina · iPad Safari | iPad (9th generation), Safari start page | 2160 × 1620 and 1620 × 2160 | 12 colours, 24 images |

## Layout

```
index.html                      gallery page, one <section> per set
sets/<set>/full/                full-size images
sets/<set>/thumbs/              480 px wide JPEG previews
sets/<set>/<set>-all.zip        every image of the set in one ZIP
tools/<set>/                    scripts the set was made with
```

## Adding a set

1. Put the images into `sets/<set>/full/`.
2. Make the previews and the ZIP:

```bash
SET=my-new-set
cd sets/$SET
mkdir -p thumbs
for f in full/*.png; do python3 -c "import sys; from PIL import Image; im = Image.open(sys.argv[1]).convert('RGB'); im.thumbnail((480, 480)); im.save(sys.argv[2], quality=85)" "$f" "thumbs/$(basename "${f%.png}").jpg"; done
(cd full && zip -q -X "../$SET-all.zip" *.png)
```

3. Copy the `<section class="set">` block in `index.html`, change the texts and paths, and add a line to the list at the top.

## Run locally

```bash
git clone https://github.com/hjorven/wallpapers.git
cd wallpapers
python3 -m http.server 8000
```

Then open http://localhost:8000.

## Licence of the fonts

Instrument Serif and IBM Plex Mono are under the SIL Open Font License, bundled from Fontsource.
