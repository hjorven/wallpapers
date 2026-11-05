"""Shared helpers for the wallpaper generators. Needs numpy and pillow only."""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

SIZES = {"quer": (2160, 1620), "hoch": (1620, 2160)}


def hexrgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.float64)


def rgbhex(c):
    return "#" + "".join(f"{int(round(max(0, min(255, v)))):02x}" for v in c)


def mix(a, b, t):
    return np.asarray(a, float) * (1 - t) + np.asarray(b, float) * t


def value_noise(h, w, cell, rng):
    """Smooth value noise in [0, 1] with roughly `cell` pixels per feature."""
    gh, gw = int(h / cell) + 3, int(w / cell) + 3
    g = rng.random((gh, gw)).astype(np.float32)
    im = Image.fromarray((g * 65535).astype(np.uint16))
    im = im.resize((int(gw * cell), int(gh * cell)), Image.BICUBIC)
    a = np.asarray(im, dtype=np.float32)[:h, :w] / 65535
    return np.clip(a, 0, 1)


def fbm(h, w, rng, base=400, octaves=5, gain=0.5):
    out = np.zeros((h, w), np.float32)
    amp, tot, cell = 1.0, 0.0, base
    for _ in range(octaves):
        out += value_noise(h, w, max(cell, 2), rng) * amp
        tot += amp
        amp *= gain
        cell /= 2
    return out / tot


def grain(arr, rng, amount=6.0):
    n = rng.normal(0, amount, arr.shape[:2])[..., None]
    return arr + n


def to_image(arr):
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")


def canvas(w, h, colour, scale=2):
    """A supersampled drawing surface; call finish() to get the final image."""
    im = Image.new("RGB", (w * scale, h * scale), tuple(int(v) for v in hexrgb(colour)) if isinstance(colour, str) else tuple(int(v) for v in colour))
    return im, ImageDraw.Draw(im), scale


def finish(im, w, h):
    return im.resize((w, h), Image.LANCZOS)


def col(c):
    if isinstance(c, str):
        c = hexrgb(c)
    return tuple(int(round(max(0, min(255, v)))) for v in c)


def vignette(arr, strength=0.25):
    h, w = arr.shape[:2]
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.sqrt(((x - w / 2) / (w / 2)) ** 2 + ((y - h / 2) / (h / 2)) ** 2) / 1.414
    return arr * (1 - strength * d[..., None] ** 2)


def blur(im, r):
    return im.filter(ImageFilter.GaussianBlur(r))


def glow(arr, s, near=0.004, far=0.025, a_near=1.2, a_far=0.9):
    """Add a soft bloom around bright parts of a float RGB array (for neon and phosphor)."""
    im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    n = np.asarray(im.filter(ImageFilter.GaussianBlur(max(1, s * near))), np.float32)
    f = np.asarray(im.filter(ImageFilter.GaussianBlur(max(1, s * far))), np.float32)
    return arr + n * a_near + f * a_far


def stars(arr, rng, count, colour=(255, 255, 255), max_alpha=0.9, region=None):
    """Sprinkle single-pixel stars of random brightness into a float RGB array."""
    h, w = arr.shape[:2]
    y1 = h if region is None else int(region)
    ys = rng.integers(0, max(1, y1), count)
    xs = rng.integers(0, w, count)
    a = (rng.random(count) ** 3 * max_alpha)[:, None]
    arr[ys, xs] = arr[ys, xs] * (1 - a) + np.array(colour, np.float32) * a
    return arr
