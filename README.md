# Wallpapers

A growing collection of 1-bit engraving wallpapers by [hjorven](https://github.com/hjorven), sorted by theme, free to download.

Live: https://hjorven.github.io/wallpapers/

The page shows every theme as a card, then all wallpapers grouped by theme and device. They can be filtered by theme, device and colour, and shown as landscape or portrait. The filter state sits in the URL, so a filtered view can be shared, for example `https://hjorven.github.io/wallpapers/#colour=red&o=portrait`.

## Themes

| Theme | Device | Resolution | Wallpapers |
| --- | --- | --- | --- |
| Officina: planets over ancient buildings | iPad (9th generation), Safari start page | 2160 × 1620 and 1620 × 2160 | 12 colours, 24 images |

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

