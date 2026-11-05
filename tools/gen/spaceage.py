"""Space Age: the cheerful rocket future of 1930s to 1950s pulp covers and travel posters."""
import numpy as np
from PIL import Image, ImageDraw
from common import hexrgb, mix, grain, to_image, col

ID = "spaceage"
NAME = "Space Age"
TAGLINE = "Finned rockets and ringed planets"
DESCRIPTION = ("The optimistic space future of old pulp covers and travel posters: chrome rockets with "
               "tail fins, ringed planets, sparkling stars and little domed moon bases, in flat print colours.")
FORMAT = "png"

# slug, title, family, sky top, sky low, planet, rocket body, accent, scene, motifs
VARIANTS = [
    ("launch-day", "Launch Day", "cyan", "#0e3b4a", "#f2b35c", "#e0603a", "#e9e4d8", "#d8402f", "launch", ["Launch", "Smoke clouds"]),
    ("saturn-run", "Saturn Run", "orange", "#16123a", "#3c2a6a", "#f0a54a", "#e9e4d8", "#e04a3a", "planet", ["Ringed planet", "Rocket"]),
    ("moonbase", "Moonbase", "blue", "#0b1838", "#26457a", "#cfd8e0", "#e9e4d8", "#f2c14e", "base", ["Domes", "Moon"]),
    ("red-planet", "Red Planet", "red", "#2a0f1a", "#a8402f", "#e86a3a", "#efe8da", "#2f8a8a", "planet", ["Mars", "Teal fins"]),
    ("atomic", "Atomic", "yellow", "#f3e3b5", "#f3c46a", "#2f6f73", "#e9e4d8", "#d8402f", "atom", ["Atom", "Cream sky"]),
    ("saucer", "Saucer", "green", "#0f2f2a", "#4a8a6a", "#d9c46a", "#d8dcd4", "#e04a6a", "saucer", ["Flying saucer"]),
    ("orbit-hotel", "Orbit Hotel", "violet", "#1a1238", "#6a3a7a", "#5fc4d0", "#efe8da", "#f2a03a", "station", ["Wheel station"]),
    ("tin-moon", "Tin Moon", "mono", "#151515", "#4a4a4a", "#dcdcdc", "#f0f0f0", "#9a9a9a", "base", ["Silver"]),
    ("comet-tail", "Comet Tail", "pink", "#2a1238", "#e46a8a", "#f2d06a", "#efe8da", "#2f6fb0", "launch", ["Pink dusk"]),
    ("jet-blue", "Jet Blue", "blue", "#0a2a5a", "#5fa8d8", "#f2e6c8", "#e04a3a", "#f2e6c8", "planet", ["Red rocket", "Blue"]),
]


def sparkle(d, x, y, r, fill):
    d.polygon([(x, y - r), (x + r * 0.18, y - r * 0.18), (x + r, y), (x + r * 0.18, y + r * 0.18),
               (x, y + r), (x - r * 0.18, y + r * 0.18), (x - r, y), (x - r * 0.18, y - r * 0.18)], fill=fill)


def rocket(d, x, y, L, ang, body, accent, ink, flame=True):
    """A classic finned rocket, nose pointing along `ang` (radians), centre at x, y."""
    ca, sa = np.cos(ang), np.sin(ang)
    def P(u, v):  # u along the body, v across
        return (x + u * ca - v * sa, y + u * sa + v * ca)
    wd = L * 0.13
    if flame:
        d.polygon([P(-L * 0.45, -wd * 0.55), P(-L * 0.95, 0), P(-L * 0.45, wd * 0.55)], fill=col(accent))
        d.polygon([P(-L * 0.45, -wd * 0.3), P(-L * 0.72, 0), P(-L * 0.45, wd * 0.3)], fill=col((255, 236, 170)))
    # fins
    for sgn in (-1, 1):
        d.polygon([P(-L * 0.12, sgn * wd), P(-L * 0.5, sgn * wd * 2.4), P(-L * 0.46, sgn * wd * 0.6)], fill=col(accent))
    # body: a lens shape built from points
    us = np.linspace(-L * 0.45, L * 0.5, 40)
    prof = wd * np.sqrt(np.clip(1 - ((us - L * 0.0) / (L * 0.52)) ** 2, 0, 1)) ** 0.8
    top = [P(u, -p) for u, p in zip(us, prof)]
    bot = [P(u, p) for u, p in zip(us[::-1], prof[::-1])]
    d.polygon(top + bot, fill=col(body))
    # shading stripe and nose cone
    shade = [P(u, p * 0.35) for u, p in zip(us, prof)] + [P(u, p) for u, p in zip(us[::-1], prof[::-1])]
    d.polygon(shade, fill=col(np.asarray(body, float) * 0.82))
    nose = [P(u, -p) for u, p in zip(us[30:], prof[30:])] + [P(u, p) for u, p in zip(us[30:][::-1], prof[30:][::-1])]
    d.polygon(nose, fill=col(accent))
    # porthole
    px, py = P(L * 0.12, 0)
    r = wd * 0.45
    d.ellipse([px - r, py - r, px + r, py + r], fill=col(ink))
    d.ellipse([px - r * 0.65, py - r * 0.65, px + r * 0.65, py + r * 0.65], fill=col((150, 210, 225)))
    # middle fin seen edge-on
    d.line([P(-L * 0.12, 0), P(-L * 0.5, 0)], fill=col(np.asarray(accent, float) * 0.7), width=max(2, int(wd * 0.25)))


def ringed_planet(d, cx, cy, R, colour, ring, sky, tilt=0.28, bands=True):
    c = np.asarray(colour, float)
    # back half of the ring
    d.arc([cx - R * 2, cy - R * 2 * tilt, cx + R * 2, cy + R * 2 * tilt], 180, 360, fill=col(ring), width=int(R * 0.09))
    d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=col(c))
    if bands:
        for k, f in enumerate((-0.45, -0.1, 0.3, 0.6)):
            hh = R * 0.08
            yy = cy + R * f
            half = np.sqrt(max(R * R - (R * f) ** 2, 0))
            d.rectangle([cx - half, yy - hh, cx + half, yy + hh], fill=col(c * (0.85 if k % 2 else 1.1)))
    # front half of the ring
    d.arc([cx - R * 2, cy - R * 2 * tilt, cx + R * 2, cy + R * 2 * tilt], 0, 180, fill=col(ring), width=int(R * 0.09))


def render(w, h, v, rng):
    slug, title, fam, top, low, planet, body, accent, scene, motifs = v
    S = 2
    W, H = w * S, h * S
    s = min(W, H)
    T, Lo, Pl, Bo, Ac = (hexrgb(c) for c in (top, low, planet, body, accent))
    ink = np.array([25, 22, 30.0])
    Y = np.mgrid[0:H, 0:W][0].astype(np.float32)
    # banded poster sky (flat steps, not a smooth gradient)
    steps = 7
    t = np.floor(np.clip(Y / (H * 0.9), 0, 0.999) * steps) / (steps - 1)
    img = mix(T, Lo, t[..., None])
    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(im)
    light = sum(T) > 450
    star_c = col(mix(T, (40, 40, 60) if light else (255, 250, 230), 0.85))
    for _ in range(int(55 * W * H / (s * s))):
        x, y = rng.random() * W, rng.random() * H * 0.75
        r = s * (0.004 + 0.014 * rng.random() ** 3)
        sparkle(d, x, y, r, star_c)
    for _ in range(int(160 * W * H / (s * s))):
        x, y = rng.random() * W, rng.random() * H * 0.8
        r = s * 0.0016
        d.ellipse([x - r, y - r, x + r, y + r], fill=star_c)
    land = col(mix(Lo, ink, 0.55))
    land2 = col(mix(Lo, ink, 0.75))
    if scene == "launch":
        # launch tower, rocket rising, puffy smoke
        cx = W * (0.5 + 0.1 * (rng.random() - 0.5))
        d.polygon([(0, H * 0.82), (W * 0.3, H * 0.79), (W * 0.7, H * 0.8), (W, H * 0.78), (W, H), (0, H)], fill=land)
        tx = cx - s * 0.16
        for k in range(12):
            yy = H * 0.8 - k * s * 0.035
            d.line([(tx, yy), (tx + s * 0.06, yy - s * 0.035)], fill=col(ink), width=int(s * 0.004))
            d.line([(tx + s * 0.06, yy), (tx, yy - s * 0.035)], fill=col(ink), width=int(s * 0.004))
        d.line([(tx, H * 0.8), (tx, H * 0.8 - 12 * s * 0.035)], fill=col(ink), width=int(s * 0.006))
        d.line([(tx + s * 0.06, H * 0.8), (tx + s * 0.06, H * 0.8 - 12 * s * 0.035)], fill=col(ink), width=int(s * 0.006))
        ry = H * 0.42
        rocket(d, cx, ry, s * 0.42, -np.pi / 2, Bo, Ac, ink)
        cloud = col(mix((250, 245, 235), Lo, 0.2))
        for k in range(26):
            px = cx + rng.normal(0, s * 0.12)
            py = H * 0.8 - abs(rng.normal(0, s * 0.05))
            r = s * (0.04 + 0.05 * rng.random())
            d.ellipse([px - r, py - r, px + r, py + r], fill=cloud)
        d.line([(cx, ry + s * 0.42 * 0.95), (cx, H * 0.72)], fill=cloud, width=int(s * 0.03))
    elif scene == "planet":
        R = s * 0.22
        px, py = W * (0.3 if rng.random() < 0.5 else 0.7), H * 0.32
        ringed_planet(d, px, py, R, Pl, mix(Pl, (255, 255, 255), 0.5), T)
        # small moon
        mx, my = W - px + (rng.random() - 0.5) * s * 0.2, H * 0.18
        r = s * 0.04
        d.ellipse([mx - r, my - r, mx + r, my + r], fill=col(mix(Pl, (255, 255, 255), 0.6)))
        rocket(d, W * 0.5, H * 0.66, s * 0.36, -np.pi / 2 + (0.5 if px > W / 2 else -0.5), Bo, Ac, ink)
        # speed lines behind the rocket
        for k in range(5):
            a = np.pi / 2 + (0.5 if px > W / 2 else -0.5)
            ox = W * 0.5 + np.cos(a) * s * (0.25 + 0.04 * k) + (k - 2) * s * 0.025 * np.cos(a + np.pi / 2)
            oy = H * 0.66 + np.sin(a) * s * (0.25 + 0.04 * k) + (k - 2) * s * 0.025 * np.sin(a + np.pi / 2)
            d.line([(ox, oy), (ox + np.cos(a) * s * 0.15, oy + np.sin(a) * s * 0.15)], fill=star_c, width=int(s * 0.004))
    elif scene == "base":
        # earth in the sky, cratered ground, domes with lit windows, a parked rocket
        ex, ey, er = W * (0.25 + 0.5 * rng.random()), H * 0.2, s * 0.1
        d.ellipse([ex - er, ey - er, ex + er, ey + er], fill=col(Ac))
        d.chord([ex - er, ey - er, ex + er, ey + er], 300, 120, fill=col(mix(Ac, T, 0.5)))
        gy = H * 0.68
        xs = np.linspace(0, W, 60)
        ys = gy + np.sin(xs / s * 6 + rng.random() * 5) * s * 0.012
        d.polygon([(0, H)] + list(zip(xs, ys)) + [(W, H)], fill=col(Pl))
        for _ in range(int(14 * W / s)):
            x, y = rng.random() * W, gy + s * 0.04 + rng.random() * (H - gy)
            r = s * (0.02 + 0.05 * rng.random()) * (0.5 + (y - gy) / (H - gy))
            d.ellipse([x - r, y - r * 0.3, x + r, y + r * 0.3], fill=col(Pl * 0.82))
            d.ellipse([x - r * 0.8, y - r * 0.2, x + r * 0.9, y + r * 0.28], fill=col(Pl * 0.9))
        bx = W * (0.25 + 0.2 * rng.random())
        for k, (dx, r) in enumerate(((0, 0.11), (0.17, 0.07), (-0.13, 0.06), (0.28, 0.045))):
            cx, rr = bx + dx * s, r * s
            d.pieslice([cx - rr, gy + s * 0.02 - rr, cx + rr, gy + s * 0.02 + rr], 180, 360, fill=col(Bo))
            d.pieslice([cx - rr * 0.7, gy + s * 0.02 - rr * 0.7, cx + rr * 0.7, gy + s * 0.02 + rr * 0.7], 180, 270, fill=col(Bo * 1.04))
            for j in range(3):
                wx = cx - rr * 0.5 + j * rr * 0.5
                d.ellipse([wx - rr * 0.08, gy + s * 0.02 - rr * 0.35, wx + rr * 0.08, gy + s * 0.02 - rr * 0.19], fill=col(Ac))
        d.line([(bx - 0.13 * s, gy + s * 0.01), (bx + 0.28 * s, gy + s * 0.01)], fill=col(Bo * 0.8), width=int(s * 0.012))
        rocket(d, W * 0.78 if bx < W * 0.4 else W * 0.2, gy - s * 0.12, s * 0.3, -np.pi / 2, Bo, Ac, ink, flame=False)
    elif scene == "atom":
        cx, cy = W / 2, H * 0.42
        R = s * 0.3
        wd = int(s * 0.012)
        for k in range(3):
            a = k * np.pi / 3
            pts = []
            for tt in np.linspace(0, 2 * np.pi, 120):
                x0, y0 = np.cos(tt) * R, np.sin(tt) * R * 0.32
                pts.append((cx + x0 * np.cos(a) - y0 * np.sin(a), cy + x0 * np.sin(a) + y0 * np.cos(a)))
            d.line(pts + [pts[0]], fill=col(Pl), width=wd)
            tt = rng.random() * 2 * np.pi
            x0, y0 = np.cos(tt) * R, np.sin(tt) * R * 0.32
            ex, ey = cx + x0 * np.cos(a) - y0 * np.sin(a), cy + x0 * np.sin(a) + y0 * np.cos(a)
            r = s * 0.025
            d.ellipse([ex - r, ey - r, ex + r, ey + r], fill=col(Ac))
        r = s * 0.06
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col(Ac))
        sparkle(d, cx, cy, r * 0.7, col(Bo))
        # skyline of the future along the bottom
        gy = H * 0.82
        x = 0
        while x < W:
            bw = s * (0.05 + 0.06 * rng.random())
            bh = s * (0.06 + 0.2 * rng.random())
            d.rectangle([x, gy - bh, x + bw, H], fill=col(Pl * 0.75))
            if rng.random() < 0.4:
                d.ellipse([x - bw * 0.2, gy - bh - bw * 0.35, x + bw * 1.2, gy - bh + bw * 0.35], fill=col(Pl * 0.75))
                d.line([(x + bw / 2, gy - bh - bw * 0.3), (x + bw / 2, gy - bh - bw * 0.9)], fill=col(Pl * 0.75), width=int(s * 0.005))
            x += bw * (1.1 + 0.4 * rng.random())
        d.rectangle([0, gy, W, H], fill=col(Pl * 0.6))
    elif scene == "saucer":
        gy = H * 0.76
        # desert mesas
        d.polygon([(0, gy), (W * 0.12, gy - s * 0.12), (W * 0.24, gy - s * 0.12), (W * 0.3, gy), (W * 0.62, gy),
                   (W * 0.7, gy - s * 0.18), (W * 0.86, gy - s * 0.18), (W * 0.92, gy), (W, gy), (W, H), (0, H)], fill=land)
        d.rectangle([0, gy + s * 0.05, W, H], fill=land2)
        cx, cy = W * (0.4 + 0.2 * rng.random()), H * 0.4
        R = s * 0.22
        # tractor beam
        beam = Image.new("L", (W, H), 0)
        ImageDraw.Draw(beam).polygon([(cx - R * 0.2, cy), (cx + R * 0.2, cy), (cx + R * 0.7, gy + s * 0.04), (cx - R * 0.7, gy + s * 0.04)], fill=90)
        a = np.asarray(im, np.float32)
        b = np.asarray(beam, np.float32)[..., None] / 255
        a = a * (1 - b) + np.asarray(col(Pl), np.float32) * b
        im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
        d = ImageDraw.Draw(im)
        d.ellipse([cx - R * 0.45, cy - R * 0.55, cx + R * 0.45, cy + R * 0.1], fill=col((170, 220, 230)))
        d.ellipse([cx - R, cy - R * 0.18, cx + R, cy + R * 0.22], fill=col(Bo))
        d.ellipse([cx - R, cy - R * 0.06, cx + R, cy + R * 0.22], fill=col(Bo * 0.8))
        for k in range(7):
            lx = cx - R * 0.75 + k * R * 0.25
            d.ellipse([lx - R * 0.045, cy + R * 0.03, lx + R * 0.045, cy + R * 0.12], fill=col(Ac))
    else:  # station: a wheel in orbit above a planet's curve
        er = s * 1.2
        ex, ey = W / 2, H + er * 0.72
        d.ellipse([ex - er, ey - er, ex + er, ey + er], fill=col(Pl))
        d.ellipse([ex - er * 0.98, ey - er * 0.98, ex + er * 0.98, ey + er * 0.98], fill=col(Pl * 0.85))
        cx, cy = W / 2, H * 0.38
        R = s * 0.26
        d.ellipse([cx - R, cy - R * 0.42, cx + R, cy + R * 0.42], outline=col(Bo), width=int(s * 0.04))
        d.ellipse([cx - R, cy - R * 0.42, cx + R, cy + R * 0.42], outline=col(Bo * 0.8), width=int(s * 0.012))
        for k in range(6):
            a = k * np.pi / 3
            d.line([(cx, cy), (cx + np.cos(a) * R, cy + np.sin(a) * R * 0.42)], fill=col(Bo * 0.9), width=int(s * 0.01))
        r = s * 0.05
        d.ellipse([cx - r, cy - r * 0.6, cx + r, cy + r * 0.6], fill=col(Ac))
        for k in range(16):
            a = k * np.pi / 8
            wx, wy = cx + np.cos(a) * R, cy + np.sin(a) * R * 0.42
            d.ellipse([wx - s * 0.006, wy - s * 0.006, wx + s * 0.006, wy + s * 0.006], fill=col(Ac))
        rocket(d, W * 0.22, H * 0.62, s * 0.2, -np.pi / 2 + 0.9, Bo, Ac, ink)
    a = np.asarray(im, np.float32)
    a = grain(a, rng, 4)  # a little print texture
    return to_image(a).resize((w, h), Image.LANCZOS)


def colour(v):
    return v[5]
