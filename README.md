# Wallpapers

A growing collection of 1-bit engraving wallpapers by [hjorven](https://github.com/hjorven), sorted by theme, free to download.

Live: https://hjorven.github.io/wallpapers/

The page shows every theme as a card, then all wallpapers grouped by theme and device. They can be filtered by theme, device and colour, and shown as landscape or portrait. The filter state sits in the URL, so a filtered view can be shared, for example `https://hjorven.github.io/wallpapers/#colour=red&o=portrait`.

## Themes

All themes are made for the iPad (9th generation) Safari start page, 2160 × 1620 landscape and 1620 × 2160 portrait.

| Theme | What it is | Wallpapers |
| --- | --- | --- |
| Officina | 1-bit engravings: planets over ancient buildings | 12 |
| Shan Shui | Ink mountains fading into mist | 10 |
| Suminagashi | Japanese floating-ink marbling | 10 |
| Terrazzo | Stone chips in polished binder | 10 |
| Seigaiha | Japanese wave pattern of overlapping arcs | 10 |
| Azulejo | Painted Portuguese tiles | 10 |
| Art Deco | Fans, sunbursts and stepped towers in metal lines | 10 |
| Memphis | 1980s Milan squiggles and confetti | 10 |
| Topographic | Contour lines of invented terrain | 10 |
| Tessellae | Roman floor mosaics in stone cubes | 10 |
| Neon Noir | A rainy city at night in neon | 10 |
| Cassette Futurism | Phosphor screens in beige plastic | 10 |
| Bio-Integrated | Glowing nerves, cells and helices | 10 |
| Moonlit Circuits | Glowing plants and silver lines under the moon | 10 |
| Vectorwave | Wireframe worlds on a black screen | 10 |
| Space Age | Finned rockets and ringed planets | 10 |
| Terminal Core | Server halls and blinking racks | 10 |
| Aero-Deco | Chrome towers and zeppelins | 10 |
| Mechanical Chronometry | Clockwork sketched on old paper | 10 |
| Industrial Heavy Metal | Riveted steel and diesel-age paint | 10 |
| Silicon Low-Poly | Faceted terrain, wafers and gold traces | 10 |
| Silver Face | Late-1970s hi-fi: brushed aluminium and VFDs | 10 |

Every theme has landscape and portrait versions of each wallpaper and a ZIP with all of them.

## Generated themes

Everything except Officina is drawn by code in `tools/gen/`, one file per theme, with numpy and pillow only. Each file lists its ten variants (name, colours, motifs) at the top and has one `render()` function. The images are reproducible: the random seed comes from the theme, the variant and the format.

```bash
pip install numpy pillow
python3 tools/gen/run.py --sheet terrazzo   # quick contact sheet to look at: tools/gen/sheet-terrazzo.jpg
python3 tools/gen/run.py terrazzo           # render in full size and update wallpapers.json
python3 tools/gen/run.py all                # every generated theme
python3 tools/build.py                      # previews, ZIPs, file sizes
```

A new generated theme is a new file in `tools/gen/` with `ID`, `NAME`, `TAGLINE`, `DESCRIPTION`, `FORMAT`, `VARIANTS`, `render()` and `colour()`, plus its name in the `STYLES` list in `run.py`.

## Layout

```
index.html                         the page; it renders everything from wallpapers.json
wallpapers.json                    themes, devices, colours and every wallpaper
themes/<theme>/<device>/full/      full-size images
themes/<theme>/<device>/thumbs/    previews, longest side 480 px (made by tools/build.py)
themes/<theme>/<device>/overview-* optional overview images
themes/<theme>/tools/              scripts the theme was made with
downloads/<theme>-<device>.zip     every image of a theme for one device (made by tools/build.py)
tools/build.py                     checks wallpapers.json, makes previews and ZIPs
```

## Adding wallpapers

1. Put the images into `themes/<theme>/<device>/full/`.
2. Add to `wallpapers.json`:
   - a new device under `devices` if it is not there yet,
   - a new theme under `themes` if it is not there yet, with one entry in `packs` per device (ZIP path, optional overview images and setup steps),
   - one entry per wallpaper under `wallpapers`. `colourFamily` must be one of the ids under `colours`; `images` lists every orientation with its size.

   One wallpaper entry looks like this:

   ```json
   {
     "id": "officina-cobalt",
     "theme": "officina",
     "device": "ipad-9",
     "number": "01",
     "title": "Cobalt",
     "colour": "#2424ff",
     "colourFamily": "blue",
     "motifs": ["Ringed planet", "Temple"],
     "images": [
       { "orientation": "landscape", "width": 2160, "height": 1620,
         "src": "themes/officina/ipad/full/01-cobalt-quer.png",
         "thumb": "themes/officina/ipad/thumbs/01-cobalt-quer.jpg" },
       { "orientation": "portrait", "width": 1620, "height": 2160,
         "src": "themes/officina/ipad/full/01-cobalt-hoch.png",
         "thumb": "themes/officina/ipad/thumbs/01-cobalt-hoch.jpg" }
     ]
   }
   ```

3. Build and check:

   ```bash
   pip install pillow
   python3 tools/build.py
   ```

   It makes the missing previews, rebuilds the ZIPs and stops with a list of problems if a file is missing, a size does not match or an id is unknown. `python3 tools/build.py --check` only checks.

4. Look at it locally, then commit and push. The page picks up new themes, devices and colours on its own; a filter only shows up once it has at least two choices.

## Run locally

```bash
git clone https://github.com/hjorven/wallpapers.git
cd wallpapers
python3 -m http.server 8000
```

Then open http://localhost:8000. Opening `index.html` straight from the disk does not work, because the page loads `wallpapers.json`.

