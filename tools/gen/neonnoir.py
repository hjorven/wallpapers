"""Neon Noir: a rain-soaked city at night, lit by neon signs and reflected in the street."""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from common import hexrgb, mix, fbm, grain, to_image, col

ID = "neonnoir"
NAME = "Neon Noir"
TAGLINE = "Rain, towers and neon at night"
DESCRIPTION = ("A city skyline at night in the rain: towers with lit windows, glowing signs and the "
               "whole scene mirrored in the wet street below.")
FORMAT = "jpg"

# slug, title, family, sky top, sky low, neon colours, motifs
VARIANTS = [
    ("magenta-rain", "Magenta Rain", "pink", "#07060f", "#2a0f33", ["#ff2bd6", "#21e6ff", "#ffcf3f"], ["Magenta", "Cyan signs"]),
    ("harbor-blue", "Harbor Blue", "blue", "#03060f", "#0e2a4a", ["#3fa9ff", "#7affd4", "#ff5470"], ["Blue haze", "Harbor"]),
    ("acid-green", "Acid Green", "green", "#040805", "#10251a", ["#7dff4a", "#00ffc8", "#ff3df2"], ["Green neon"]),
    ("red-district", "Red District", "red", "#0a0405", "#3a0a12", ["#ff2d3c", "#ff9a3c", "#ffd9e0"], ["Red glow", "Warm signs"]),
    ("violet-smog", "Violet Smog", "violet", "#07040f", "#2b1450", ["#b14bff", "#ff5fd2", "#5ad1ff"], ["Violet smog"]),
    ("amber-night", "Amber Night", "orange", "#080503", "#33190a", ["#ffa53c", "#ffe066", "#3cc8ff"], ["Sodium lamps", "Amber"]),
    ("ice-city", "Ice City", "cyan", "#02080b", "#0d3440", ["#5df2ff", "#e8fbff", "#ff6ad5"], ["Ice blue", "White signs"]),
    ("tokyo-mono", "Mono", "mono", "#050505", "#202020", ["#f2f2f2", "#9a9a9a", "#ff3b3b"], ["White neon", "One red sign"]),
    ("sunset-strip", "Sunset Strip", "orange", "#100318", "#6a1c3a", ["#ff7b3c", "#ff3c8e", "#ffe14d"], ["Late dusk", "Orange"]),
    ("deep-teal", "Deep Teal", "cyan", "#020807", "#08302e", ["#2fffe0", "#ff4fa3", "#fff36b"], ["Teal fog"]),
]


def render(w, h, v, rng):
    slug, title, fam, top, low, neons, motifs = v
    top_c, low_c = hexrgb(top), hexrgb(low)
    neon = [hexrgb(c) for c in neons]
    hor = int(h * (0.70 if w > h else 0.72))  # street line
    Y, X = np.mgrid[0:h, 0:w].astype(np.float32)
    sky = mix(top_c, low_c, np.clip(Y / hor, 0, 1)[..., None] ** 1.8)
    img = sky.copy()

    city = Image.new("RGB", (w, hor), (0, 0, 0))
    mask = Image.new("L", (w, hor), 0)
    glow = Image.new("RGB", (w, hor), (0, 0, 0))
    dc, dm, dg = ImageDraw.Draw(city), ImageDraw.Draw(mask), ImageDraw.Draw(glow)
    s = min(w, h)
    for layer in range(3):
        depth = layer / 2  # 0 far, 1 near
        body = mix(low_c * 1.35 + 10, top_c, 0.25 + 0.75 * depth) * (1 - 0.4 * depth)
        x = -rng.random() * s * 0.1
        while x < w:
            bw = s * (0.06 + 0.08 * rng.random()) * (0.8 + 0.6 * depth)
            bh = hor * (0.3 + 0.5 * rng.random() ** 1.5) * (0.85 + 0.3 * depth)
            y0 = hor - bh
            dc.rectangle([x, y0, x + bw, hor], fill=col(body))
            dm.rectangle([x, y0, x + bw, hor], fill=255)
            if rng.random() < 0.25:  # stepped top or antenna
                dc.rectangle([x + bw * 0.25, y0 - bh * 0.08, x + bw * 0.75, y0], fill=col(body))
                dc.line([(x + bw / 2, y0 - bh * 0.08), (x + bw / 2, y0 - bh * 0.18)], fill=col(body), width=max(2, int(s * 0.003)))
                rr_ = max(1, s * 0.0015)
                dg.ellipse([x + bw / 2 - rr_, y0 - bh * 0.18 - rr_, x + bw / 2 + rr_, y0 - bh * 0.18 + rr_], fill=(255, 60, 60))
            # windows
            ww = max(2, int(s * 0.006 * (0.7 + 0.5 * depth)))
            gx, gy = ww * 2.2, ww * 2.6
            lit_rate = 0.06 + 0.16 * rng.random()
            warm = mix(np.array([255, 214, 150.0]), neon[int(rng.integers(0, 3))], 0.35)
            yy = y0 + gy
            while yy < hor - gy:
                xx = x + gx * 0.6
                while xx < x + bw - gx * 0.6:
                    if rng.random() < lit_rate:
                        c = warm * (0.5 + 0.5 * rng.random()) * (0.55 + 0.45 * depth)
                        dc.rectangle([xx, yy, xx + ww, yy + ww * 1.3], fill=col(c))
                    xx += gx
                yy += gy
            # neon sign on some near buildings
            if depth > 0.4 and rng.random() < 0.55:
                nc = neon[int(rng.integers(0, len(neon)))]
                if rng.random() < 0.5:  # vertical sign
                    sx = x + bw * (0.1 if rng.random() < 0.5 else 0.8)
                    sy = y0 + bh * (0.1 + 0.3 * rng.random())
                    sh, swd = bh * 0.35, bw * 0.16
                    dg.rectangle([sx, sy, sx + swd, sy + sh], outline=col(nc), width=max(2, int(s * 0.003)))
                    for k in range(4):
                        dg.rectangle([sx + swd * 0.25, sy + sh * (0.08 + k * 0.23), sx + swd * 0.75, sy + sh * (0.2 + k * 0.23)], fill=col(nc))
                else:  # horizontal band or ring
                    sy = y0 + bh * (0.15 + 0.3 * rng.random())
                    if rng.random() < 0.5:
                        dg.rectangle([x + bw * 0.1, sy, x + bw * 0.9, sy + s * 0.012], fill=col(nc))
                    else:
                        r = bw * 0.28
                        dg.ellipse([x + bw / 2 - r, sy - r, x + bw / 2 + r, sy + r], outline=col(nc), width=max(3, int(s * 0.004)))
            x += bw + s * 0.004 * rng.random()
    c = np.asarray(city, np.float32)
    m = np.asarray(mask, np.float32)[..., None] / 255
    g = np.asarray(glow, np.float32)
    g_soft = np.asarray(glow.filter(ImageFilter.GaussianBlur(s * 0.012)), np.float32)
    g_wide = np.asarray(glow.filter(ImageFilter.GaussianBlur(s * 0.05)), np.float32)
    up = img[:hor] * (1 - m) + c * m
    up = up + g + g_soft * 1.6 + g_wide * 1.2
    # haze rising from the street
    haze = np.clip((Y[:hor] / hor - 0.55) / 0.45, 0, 1)[..., None] ** 2
    up = mix(up, low_c * 1.4 + 10, haze * 0.5)
    img[:hor] = up

    # wet street: blurred, rippled mirror image
    refl_h = h - hor
    src = np.clip(up[::-1][:refl_h], 0, 255)
    ripple = (fbm(refl_h, w, rng, base=s * 0.03, octaves=2) - 0.5) * s * 0.03
    xi = np.clip((X[:refl_h] + ripple).astype(int), 0, w - 1)
    yi = np.clip(Y[:refl_h].astype(int), 0, refl_h - 1)
    refl = src[yi, xi]
    refl = np.asarray(Image.fromarray(refl.astype(np.uint8)).filter(ImageFilter.GaussianBlur(s * 0.004)), np.float32)
    # streaks: stretch vertically
    refl = np.asarray(Image.fromarray(refl.astype(np.uint8)).resize((w, max(1, refl_h // 6))).resize((w, refl_h), Image.BILINEAR), np.float32) * 0.5 + refl * 0.5
    fade = np.clip(1 - Y[:refl_h] / refl_h * 0.9, 0, 1)[..., None]
    street = low_c * 0.35
    img[hor:] = mix(street, refl, 0.75 * fade)
    img[hor:hor + 2] = img[hor:hor + 2] * 0.6

    # rain
    rain = Image.new("L", (w, h), 0)
    dr = ImageDraw.Draw(rain)
    ang = 0.18
    for _ in range(int(w * h / 2600)):
        x0, y0 = rng.random() * w, rng.random() * h
        L = s * (0.015 + 0.03 * rng.random())
        dr.line([(x0, y0), (x0 + L * ang, y0 + L)], fill=int(40 + 70 * rng.random()), width=1)
    r = np.asarray(rain, np.float32)[..., None] / 255
    img = img + r * 90
    img = grain(img, rng, 4.0)
    return to_image(img)


def colour(v):
    return v[5][0]
