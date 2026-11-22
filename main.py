#!/usr/bin/env python3
"""news-image-20261122 v5 — visual-first front page.

Renders entry.png (1024x1024, <=1MB): a visual-first newspaper front page
summing up Sunday 22 November 2026's world news. 13 main stories, each with
a large, detailed, full-colour drawn scene; a huge date masthead; a
big-numbers strip; 17 more stories in a compact "also on" list; a small
labelled world map. Every fact verified against published 22 Nov 2026
reporting (see stories-v4.md in the work directory; v5 keeps that verified
story base and re-presents it visually).

Run: python3 main.py  (writes entry.png next to this file)
"""

import math
import os
from PIL import Image, ImageDraw, ImageFont

W = H = 1024
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")

# ---------------------------------------------------------------- fonts
SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF_REG = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SANS_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
DEJAVU_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
DEJAVU = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

_cache = {}


def font(size, bold=False, serif=False):
    key = (size, bold, serif)
    if key in _cache:
        return _cache[key]
    paths = []
    if serif:
        paths = [SERIF if bold else SERIF_REG, DEJAVU_B if bold else DEJAVU]
    else:
        paths = [SANS_B if bold else SANS, DEJAVU_B if bold else DEJAVU]
    f = None
    for p in paths:
        try:
            f = ImageFont.truetype(p, size)
            break
        except Exception:
            continue
    if f is None:
        f = ImageFont.load_default()
    _cache[key] = f
    return f


def wrap(draw, text, f, max_w):
    """Greedy word wrap; returns list of lines that fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for w_ in words:
        trial = (cur + " " + w_).strip()
        if draw.textlength(trial, font=f) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def draw_lines(draw, x, y, lines, f, fill, leading=None):
    if leading is None:
        leading = f.size + 2
    for ln in lines:
        draw.text((x, y), ln, font=f, fill=fill)
        y += leading
    return y


def vgrad(draw, box, top, bottom):
    """Vertical gradient fill inside box (x0,y0,x1,y1)."""
    x0, y0, x1, y1 = box
    h = max(1, y1 - y0)
    for i in range(h):
        t = i / h
        c = tuple(int(top[j] + (bottom[j] - top[j]) * t) for j in range(3))
        draw.line([(x0, y0 + i), (x1, y0 + i)], fill=c)


def flame(d, x, y, s):
    """A flame of height ~s anchored at (x, y) = base centre."""
    d.polygon([(x - 0.42 * s, y), (x - 0.30 * s, y - 0.55 * s),
               (x - 0.10 * s, y - 0.75 * s), (x, y - 1.0 * s),
               (x + 0.18 * s, y - 0.72 * s), (x + 0.38 * s, y - 0.45 * s),
               (x + 0.42 * s, y)], fill=(214, 48, 28))
    d.polygon([(x - 0.26 * s, y), (x - 0.18 * s, y - 0.38 * s),
               (x - 0.05 * s, y - 0.55 * s), (x + 0.05 * s, y - 0.62 * s),
               (x + 0.20 * s, y - 0.35 * s), (x + 0.26 * s, y)],
              fill=(242, 140, 40))
    d.polygon([(x - 0.13 * s, y), (x - 0.08 * s, y - 0.22 * s),
               (x, y - 0.34 * s), (x + 0.10 * s, y - 0.18 * s),
               (x + 0.13 * s, y)], fill=(250, 210, 60))


def smoke(d, x, y, s, col=(88, 88, 94)):
    """Rising smoke column above (x, y); s = puff radius."""
    for i, r in enumerate((s, s * 0.85, s * 0.7, s * 0.55)):
        yy = y - i * s * 0.9
        xx = x + (i % 2) * s * 0.25 - s * 0.12
        d.ellipse([xx - r, yy - r, xx + r, yy + r], fill=col)


def cloud(d, x, y, s, col=(255, 255, 255)):
    d.ellipse([x, y, x + 2.2 * s, y + 0.9 * s], fill=col)
    d.ellipse([x + 0.4 * s, y - 0.5 * s, x + 1.6 * s, y + 0.6 * s], fill=col)
    d.ellipse([x + 1.2 * s, y - 0.35 * s, x + 2.2 * s, y + 0.7 * s], fill=col)


def sun(d, cx, cy, r, col=(250, 200, 60)):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
    for k in range(8):
        a = k * math.pi / 4
        x1 = cx + int(1.15 * r * math.cos(a))
        y1 = cy + int(1.15 * r * math.sin(a))
        x2 = cx + int(1.45 * r * math.cos(a))
        y2 = cy + int(1.45 * r * math.sin(a))
        d.line([(x1, y1), (x2, y2)], fill=col, width=3)


def sea(d, x, y, w, h, base=(23, 84, 130)):
    vgrad(d, (x, y, x + w, y + h), base, (10, 48, 84))
    for i in range(3):
        yy = y + int(h * (0.3 + 0.25 * i))
        for xx in range(x + 6, x + w - 6, 26):
            d.arc([xx, yy, xx + 22, yy + 10], 180, 360,
                  fill=(170, 210, 235), width=2)


def chip(d, x, y, text, bg, fg=(255, 255, 255), fsize=10):
    f = font(fsize, bold=True)
    tw = d.textlength(text, font=f)
    d.rounded_rectangle([x, y, x + tw + 12, y + fsize + 8], radius=4, fill=bg)
    d.text((x + 6, y + 4), text, font=f, fill=fg)
    return tw + 12

# ================================================================ scenes
# Each scene draws inside box (x, y, w, h) on draw object d.

def scene_geneva(d, x, y, w, h):
    """Lead: Geneva peace talks — hall, flags, table, 28-point plan."""
    vgrad(d, (x, y, x + w, y + h), (176, 208, 235), (120, 160, 205))
    sun(d, x + w - 60, y + 34, 20)
    cloud(d, x + 24, y + 14, 12)
    cloud(d, x + w - 170, y + 52, 9)
    # hall with columns + arched windows
    hx, hy, hw, hh = x + 30, y + h - 118, w - 60, 118
    d.rectangle([hx, hy, hx + hw, hy + hh], fill=(238, 228, 205))
    d.rectangle([hx, hy, hx + hw, hy + 14], fill=(148, 32, 32))
    for i in range(5):
        cx = hx + 26 + i * (hw - 52) // 4
        d.rectangle([cx - 7, hy + 14, cx + 7, hy + hh - 34], fill=(222, 206, 168),
                    outline=(100, 85, 60))
        if i < 4:
            wx = cx + 8
            d.rectangle([wx, hy + 26, wx + 34, hy + hh - 40], fill=(70, 100, 140),
                        outline=(90, 75, 55))
            d.ellipse([wx, hy + 16, wx + 34, hy + 34], fill=(70, 100, 140))
    d.rectangle([hx, hy + hh - 34, hx + hw, hy + hh - 26], fill=(120, 100, 70))
    # flags on poles above the hall
    for i, (c1, c2) in enumerate([((24, 64, 150), (255, 255, 255)),
                                  ((0, 90, 170), (255, 215, 0))]):
        fx = hx + 60 + i * 90
        d.line([(fx, hy - 34), (fx, hy)], fill=(60, 50, 40), width=3)
        d.rectangle([fx, hy - 34, fx + 46, hy - 12], fill=c1)
        if i == 0:  # US stars+stripes hint
            d.rectangle([fx, hy - 34, fx + 18, hy - 22], fill=(24, 64, 150))
            for sy in range(3):
                d.rectangle([fx, hy - 22 + sy * 4, fx + 46, hy - 20 + sy * 4],
                            fill=(255, 255, 255))
        else:  # Ukraine blue over yellow
            d.rectangle([fx, hy - 34, fx + 46, hy - 23], fill=(0, 90, 170))
            d.rectangle([fx, hy - 23, fx + 46, hy - 12], fill=(255, 215, 0))
    # table + document
    tx, ty = x + w // 2 - 130, y + h - 52
    d.rounded_rectangle([tx, ty, tx + 260, ty + 30], radius=6, fill=(96, 62, 32))
    d.rectangle([tx, ty, tx + 260, ty + 8], fill=(150, 105, 60))
    d.rounded_rectangle([tx + 82, ty - 32, tx + 178, ty + 2], radius=3,
                        fill=(255, 255, 255), outline=(150, 130, 90))
    f = font(12, bold=True)
    d.text((tx + 92, ty - 28), "28-POINT", font=f, fill=(148, 32, 32))
    d.text((tx + 108, ty - 14), "PLAN", font=f, fill=(148, 32, 32))
    # dove, larger
    dx, dy = x + 46, y + 74
    d.ellipse([dx, dy, dx + 48, dy + 20], fill=(255, 255, 255))
    d.ellipse([dx + 34, dy - 12, dx + 56, dy + 6], fill=(255, 255, 255))
    d.polygon([(dx + 50, dy - 8), (dx + 68, dy - 14), (dx + 62, dy + 2)],
              fill=(255, 255, 255))
    d.polygon([(dx + 2, dy + 6), (dx - 16, dy + 16), (dx + 6, dy + 16)],
              fill=(240, 240, 240))
    d.ellipse([dx + 48, dy - 9, dx + 52, dy - 5], fill=(30, 30, 30))
    d.polygon([(dx + 16, dy - 16), (dx + 30, dy - 36), (dx + 36, dy - 14)],
              fill=(255, 255, 255))
    # olive branch
    d.line([(dx + 56, dy + 2), (dx + 72, dy + 12)], fill=(60, 120, 60), width=3)
    d.ellipse([dx + 66, dy + 8, dx + 76, dy + 16], fill=(60, 140, 70))


def scene_tankers(d, x, y, w, h):
    """Gulf: three tankers burning near Hormuz at dusk."""
    vgrad(d, (x, y, x + w, y + h), (250, 150, 60), (190, 60, 40))
    sun(d, x + w - 52, y + 30, 18, col=(255, 220, 120))
    cloud(d, x + 18, y + 12, 10, col=(255, 200, 150))
    sea(d, x, y + h - 62, w, 62, base=(120, 50, 40))
    # distant tanker (left)
    for (tx, tw_, fl) in [(x + 14, 62, False), (x + w - 92, 66, False),
                          (x + w // 2 - 44, 92, True)]:
        ty = y + h - 62
        d.rectangle([tx, ty - 16, tx + tw_, ty - 2], fill=(40, 36, 34))
        d.rectangle([tx + tw_ - 16, ty - 30, tx + tw_ - 4, ty - 16],
                    fill=(52, 48, 44))
        d.rectangle([tx + 6, ty - 26, tx + 12, ty - 16], fill=(180, 60, 40))
        d.line([(tx, ty - 2), (tx + tw_, ty - 2)], fill=(20, 18, 16), width=2)
        if fl:
            flame(d, tx + tw_ // 2, ty - 16, 26)
            flame(d, tx + 16, ty - 16, 16)
            smoke(d, tx + tw_ // 2, ty - 44, 9, col=(70, 60, 60))
            smoke(d, tx + 20, ty - 30, 7, col=(80, 70, 70))
    # reflection streaks
    for i in range(4):
        d.line([(x + w // 2 - 30 + i * 18, y + h - 40),
                (x + w // 2 - 30 + i * 18, y + h - 8)],
               fill=(255, 170, 80), width=3)


def scene_riyadh(d, x, y, w, h):
    """Riyadh: night sky, missile trails, city skyline, intercepts."""
    vgrad(d, (x, y, x + w, y + h), (8, 16, 44), (24, 44, 88))
    import random
    random.seed(7)
    for _ in range(26):
        sx = x + random.randint(4, w - 4)
        sy = y + random.randint(4, h // 2)
        d.ellipse([sx, sy, sx + 2, sy + 2], fill=(220, 225, 255))
    d.ellipse([x + w - 46, y + 14, x + w - 18, y + 42], fill=(235, 235, 210))
    # missile trails arcing down
    for (mx, my, mdx) in [(x + 40, y + 8, 26), (x + w // 2, y + 2, -8),
                          (x + w - 70, y + 12, -30)]:
        pts = [(mx + mdx * t / 10, my + (h * 0.55) * (t / 10) ** 2)
               for t in range(11)]
        d.line(pts, fill=(255, 190, 90), width=3)
        ex, ey = pts[-1]
        d.ellipse([ex - 5, ey - 5, ex + 5, ey + 5], fill=(255, 220, 120))
        d.ellipse([ex - 10, ey - 10, ex + 10, ey + 10], outline=(255, 190, 90))
    # skyline with Kingdom Centre tower (arched top)
    base_y = y + h
    d.rectangle([x, base_y - 34, x + w, base_y], fill=(12, 14, 26))
    towers = [(x + 8, 52, 22), (x + 36, 66, 18), (x + 60, 44, 20),
              (x + 150, 58, 24), (x + 180, 70, 18), (x + 204, 48, 22)]
    for (tx, th, tw_) in towers:
        d.rectangle([tx, base_y - th, tx + tw_, base_y - 34], fill=(30, 34, 58))
        for wy in range(base_y - th + 6, base_y - 38, 10):
            for wx in range(tx + 4, tx + tw_ - 3, 7):
                d.rectangle([wx, wy, wx + 3, wy + 4], fill=(255, 210, 110))
    # Kingdom Centre: tall tower with inverted arch opening
    kx = x + 92
    d.rectangle([kx, base_y - 108, kx + 44, base_y - 34], fill=(56, 64, 100),
                outline=(120, 130, 180))
    d.polygon([(kx + 8, base_y - 108), (kx + 22, base_y - 82),
               (kx + 36, base_y - 108)], fill=(8, 16, 44))
    for wy in range(base_y - 80, base_y - 38, 10):
        d.rectangle([kx + 5, wy, kx + 10, wy + 4], fill=(255, 210, 110))
        d.rectangle([kx + 34, wy, kx + 39, wy + 4], fill=(255, 210, 110))


def scene_cop31(d, x, y, w, h):
    """COP31: big globe, thermometer, green shoots, Antalya coast."""
    vgrad(d, (x, y, x + w, y + h), (140, 200, 235), (205, 232, 245))
    sun(d, x + w - 40, y + 26, 16)
    cloud(d, x + 12, y + 10, 9)
    # sea strip at bottom
    d.rectangle([x, y + h - 18, x + w, y + h], fill=(46, 130, 180))
    d.line([(x, y + h - 18), (x + w, y + h - 18)], fill=(20, 90, 140), width=2)
    # globe
    cx, cy, r = x + w // 2 - 18, y + h // 2 - 6, 52
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(38, 110, 190),
              outline=(20, 70, 140), width=3)
    d.ellipse([cx - r + 8, cy - r + 6, cx - 6, cy - 6], fill=(46, 150, 90))
    d.ellipse([cx + 2, cy + 12, cx + r - 8, cy + r - 10], fill=(46, 150, 90))
    d.ellipse([cx - r + 16, cy + r - 26, cx - 2, cy + r - 6], fill=(46, 150, 90))
    d.arc([cx - r, cy - r, cx + r, cy + r], 200, 340, fill=(120, 190, 235), width=2)
    d.arc([cx - r, cy - r, cx + r, cy + r], 20, 160, fill=(120, 190, 235), width=2)
    d.line([(cx - r, cy), (cx + r, cy)], fill=(120, 190, 235), width=2)
    # thermometer at right
    tx = x + w - 34
    d.rounded_rectangle([tx, y + 22, tx + 12, y + h - 40], radius=6,
                        fill=(255, 255, 255), outline=(150, 40, 40), width=2)
    d.ellipse([tx - 5, y + h - 52, tx + 17, y + h - 30], fill=(220, 50, 40))
    d.rectangle([tx + 3, y + 34, tx + 9, y + h - 40], fill=(220, 50, 40))
    for i in range(4):
        yy = y + 34 + i * 14
        d.line([(tx + 12, yy), (tx + 18, yy)], fill=(150, 40, 40), width=2)
    # green shoot sprouting from globe base
    gx, gy = cx - 30, cy + r - 4
    d.line([(gx, gy), (gx, gy - 22)], fill=(30, 120, 60), width=3)
    d.ellipse([gx - 16, gy - 26, gx, gy - 12], fill=(60, 170, 90))
    d.ellipse([gx, gy - 24, gx + 16, gy - 10], fill=(46, 150, 80))


def scene_peru(d, x, y, w, h):
    """Peru quake: Andes peaks, cracked ground, seismograph trace."""
    vgrad(d, (x, y, x + w, y + h), (200, 225, 240), (150, 180, 200))
    sun(d, x + 34, y + 24, 15, col=(255, 225, 130))
    # Andes
    peaks = [(x, y + h - 46), (x + 52, y + 22), (x + 96, y + h - 46),
             (x + 118, y + h - 46), (x + 168, y + 8), (x + 224, y + h - 46)]
    d.polygon(peaks, fill=(96, 110, 140))
    d.polygon([(x + 52, y + 22), (x + 36, y + 44), (x + 68, y + 44)],
              fill=(255, 255, 255))
    d.polygon([(x + 168, y + 8), (x + 150, y + 34), (x + 186, y + 34)],
              fill=(255, 255, 255))
    # ground + crack
    gy = y + h - 46
    d.rectangle([x, gy, x + w, y + h], fill=(122, 94, 66))
    d.line([(x + 20, gy), (x + 60, gy + 14), (x + 90, gy + 4),
            (x + 130, gy + 20), (x + 170, gy + 8), (x + 210, gy + 18),
            (x + w - 8, gy + 6)], fill=(40, 26, 16), width=3)
    # tilted house
    hx, hy = x + 30, gy - 26
    d.polygon([(hx, hy), (hx + 34, hy), (hx + 40, hy + 16), (hx - 4, hy + 16)],
              fill=(170, 60, 40))
    d.rectangle([hx + 2, hy + 16, hx + 32, hy + 34], fill=(235, 220, 190))
    d.rectangle([hx + 13, hy + 24, hx + 21, hy + 34], fill=(90, 60, 40))
    # fallen tree
    d.line([(x + 190, gy + 2), (x + 214, gy - 16)], fill=(70, 50, 30), width=5)
    d.ellipse([x + 208, gy - 24, x + 232, gy - 6], fill=(60, 120, 60))
    # seismograph strip top-right
    sx, sy = x + w - 92, y + 8
    d.rectangle([sx, sy, sx + 84, sy + 26], fill=(255, 255, 255),
                outline=(30, 30, 30))
    pts = [(sx + 4 + i * 4, sy + 13) for i in range(6)]
    pts += [(sx + 28, sy + 4), (sx + 32, sy + 22), (sx + 36, sy + 5),
            (sx + 40, sy + 20), (sx + 44, sy + 8)]
    pts += [(sx + 48 + i * 4, sy + 13) for i in range(8)]
    d.line(pts, fill=(200, 30, 30), width=2)


def scene_brazil(d, x, y, w, h):
    """Brazil storm: supercell cloud, lightning, wrecked roofs, wind."""
    vgrad(d, (x, y, x + w, y + h), (70, 80, 110), (150, 160, 185))
    # supercell: dark stacked cloud mass
    d.ellipse([x + 8, y + 6, x + 130, y + 44], fill=(52, 58, 82))
    d.ellipse([x + 60, y - 2, x + 200, y + 36], fill=(44, 50, 72))
    d.ellipse([x + 130, y + 8, x + w - 6, y + 46], fill=(58, 64, 88))
    d.ellipse([x + 40, y + 30, x + 150, y + 58], fill=(70, 76, 100))
    d.ellipse([x + 70, y + 2, x + 170, y + 26], fill=(96, 102, 128))
    # lightning
    lx = x + w // 2 + 20
    d.polygon([(lx, y + 40), (lx - 12, y + 66), (lx - 2, y + 66),
               (lx - 14, y + 92), (lx + 2, y + 66), (lx + 12, y + 66)],
              fill=(255, 235, 90))
    # rain streaks
    for i in range(14):
        rx = x + 10 + i * 17
        d.line([(rx, y + 52), (rx - 6, y + 78)], fill=(200, 215, 235), width=2)
    # ground + wrecked houses
    gy = y + h - 30
    d.rectangle([x, gy, x + w, y + h], fill=(110, 130, 90))
    # house 1: roof torn off, tilted
    d.rectangle([x + 16, gy - 22, x + 62, gy], fill=(225, 210, 175))
    d.polygon([(x + 12, gy - 22), (x + 40, gy - 38), (x + 58, gy - 30),
               (x + 66, gy - 22)], fill=(150, 50, 40))
    d.polygon([(x + 70, gy - 40), (x + 92, gy - 52), (x + 104, gy - 34)],
              fill=(150, 50, 40))  # flying roof piece
    # house 2: leaning
    d.polygon([(x + 150, gy), (x + 154, gy - 26), (x + 196, gy - 22),
               (x + 200, gy)], fill=(235, 220, 190))
    d.polygon([(x + 150, gy - 26), (x + 176, gy - 42), (x + 200, gy - 22)],
              fill=(120, 40, 35))
    # wind gust lines
    for (wy, wl) in [(y + 84, 60), (y + 96, 80), (y + 70, 44)]:
        d.line([(x + w - wl - 8, wy), (x + w - 8, wy)], fill=(255, 255, 255),
               width=2)
        d.line([(x + w - wl - 8, wy), (x + w - wl + 6, wy - 6)],
               fill=(255, 255, 255), width=2)

def scene_g20(d, x, y, w, h):
    """G20 Johannesburg: gold sky, skyline, G20 emblem, flag ribbon."""
    vgrad(d, (x, y, x + w, y + h), (255, 190, 90), (220, 120, 50))
    sun(d, x + w - 46, y + 28, 18, col=(255, 240, 180))
    cloud(d, x + 14, y + 12, 10, col=(255, 225, 180))
    # skyline
    base_y = y + h - 26
    skyline = [(x + 6, 46, 20), (x + 30, 66, 16), (x + 50, 38, 22),
               (x + 76, 58, 18), (x + 170, 62, 18), (x + 192, 44, 20),
               (x + 216, 56, 16)]
    for (tx, th, tw_) in skyline:
        d.rectangle([tx, base_y - th, tx + tw_, base_y], fill=(90, 55, 30))
        for wy in range(base_y - th + 6, base_y - 4, 9):
            d.rectangle([tx + 4, wy, tx + tw_ - 4, wy + 3],
                        fill=(255, 215, 130))
    # tall tower with spire (Hillbrow-like)
    d.rectangle([x + 100, base_y - 84, x + 132, base_y], fill=(70, 42, 24))
    d.polygon([(x + 112, base_y - 84), (x + 116, base_y - 104),
               (x + 120, base_y - 84)], fill=(70, 42, 24))
    for wy in range(base_y - 78, base_y - 4, 9):
        d.rectangle([x + 105, wy, x + 127, wy + 3], fill=(255, 215, 130))
    d.rectangle([x, base_y, x + w, y + h], fill=(60, 40, 22))
    # G20 gold emblem disc
    cx, cy, r = x + w // 2, y + 52, 34
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 225, 140),
              outline=(140, 100, 20), width=3)
    f = font(24, bold=True, serif=True)
    d.text((cx - 24, cy - 16), "G20", font=f, fill=(120, 70, 10))
    # ribbon
    d.polygon([(cx - 44, cy + 30), (cx + 44, cy + 30), (cx + 36, cy + 46),
               (cx - 36, cy + 46)], fill=(0, 90, 60))
    f2 = font(10, bold=True)
    d.text((cx - 34, cy + 33), "JOBURG 2026", font=f2, fill=(255, 255, 255))


def scene_icj(d, x, y, w, h):
    """ICJ verdict: courtroom columns, scales of justice, gavel, 9-6."""
    vgrad(d, (x, y, x + w, y + h), (58, 74, 110), (28, 38, 66))
    # columns
    for i in range(4):
        cx = x + 22 + i * 62
        d.rectangle([cx - 9, y + 8, cx + 9, y + h - 30], fill=(228, 212, 172),
                    outline=(120, 100, 70))
        d.rectangle([cx - 13, y + 4, cx + 13, y + 12], fill=(240, 226, 196))
        d.rectangle([cx - 13, y + h - 38, cx + 13, y + h - 30],
                    fill=(240, 226, 196))
    # bench
    d.rectangle([x, y + h - 30, x + w, y + h], fill=(96, 62, 32))
    d.rectangle([x, y + h - 34, x + w, y + h - 30], fill=(150, 105, 60))
    # scales of justice (gold), centre
    cx, cy = x + w // 2, y + 44
    d.line([(cx, cy - 22), (cx, cy + 34)], fill=(240, 200, 90), width=4)
    d.line([(cx - 34, cy - 16), (cx + 34, cy - 16)], fill=(240, 200, 90),
           width=4)
    d.ellipse([cx - 5, cy - 27, cx + 5, cy - 17], fill=(240, 200, 90))
    for sgn in (-1, 1):
        px = cx + sgn * 34
        d.line([(px, cy - 16), (px, cy + 6)], fill=(240, 200, 90), width=2)
        d.polygon([(px - 14, cy + 6), (px + 14, cy + 6), (px, cy + 20)],
                  fill=(240, 200, 90))
    d.rectangle([cx - 16, cy + 34, cx + 16, cy + 40], fill=(240, 200, 90))
    # gavel at right
    gx, gy = x + w - 52, y + h - 52
    d.rectangle([gx, gy - 4, gx + 34, gy + 6], fill=(120, 80, 40),
                outline=(70, 45, 20))
    d.line([(gx + 17, gy + 6), (gx + 8, gy + 24)], fill=(90, 60, 30), width=5)
    # verdict board 9-6
    bx, by = x + 12, y + h - 62
    d.rounded_rectangle([bx, by, bx + 46, by + 24], radius=4,
                        fill=(255, 255, 255), outline=(20, 20, 20))
    f = font(14, bold=True)
    d.text((bx + 6, by + 4), "9 – 6", font=f, fill=(148, 32, 32))


def scene_mexico(d, x, y, w, h):
    """Mexico capture: dawn sky, Sinaloa mountains, helicopter searchlight."""
    vgrad(d, (x, y, x + w, y + h), (255, 170, 90), (140, 60, 80))
    sun(d, x + 40, y + h - 66, 20, col=(255, 230, 150))
    # mountains
    d.polygon([(x, y + h - 34), (x + 50, y + 34), (x + 110, y + h - 34)],
              fill=(96, 60, 70))
    d.polygon([(x + 80, y + h - 34), (x + 150, y + 18), (x + 220, y + h - 34)],
              fill=(74, 46, 56))
    d.rectangle([x, y + h - 34, x + w, y + h], fill=(58, 38, 44))
    # cactus
    d.line([(x + 200, y + h - 34), (x + 200, y + h - 58)], fill=(40, 120, 60),
           width=5)
    d.line([(x + 200, y + h - 50), (x + 190, y + h - 50),
            (x + 190, y + h - 42)], fill=(40, 120, 60), width=4)
    # helicopter
    hx, hy = x + w // 2 - 10, y + 26
    d.ellipse([hx - 34, hy, hx + 30, hy + 20], fill=(30, 34, 40))
    d.ellipse([hx + 18, hy + 4, hx + 36, hy + 14], fill=(70, 110, 160))
    d.line([(hx - 34, hy + 10), (hx - 62, hy + 4)], fill=(30, 34, 40), width=4)
    d.line([(hx + 4, hy - 2), (hx - 46, hy - 8)], fill=(30, 34, 40), width=3)
    d.line([(hx + 4, hy - 2), (hx + 54, hy - 8)], fill=(30, 34, 40), width=3)
    d.line([(hx - 10, hy + 20), (hx - 14, hy + 32)], fill=(30, 34, 40), width=4)
    d.line([(hx + 10, hy + 20), (hx + 14, hy + 32)], fill=(30, 34, 40), width=4)
    # searchlight cone (narrow beam to the ground)
    d.polygon([(hx - 4, hy + 22), (hx + 18, hy + 22), (hx + 44, y + h - 34),
               (hx + 8, y + h - 34)], fill=(255, 240, 160))
    d.line([(hx + 18, hy + 22), (hx + 44, y + h - 34)], fill=(230, 210, 110),
           width=2)
    # badge star
    bx, by = x + 18, y + 14
    d.polygon([(bx, by - 10), (bx + 3, by - 3), (bx + 10, by - 3),
               (bx + 5, by + 2), (bx + 7, by + 9), (bx, by + 5),
               (bx - 7, by + 9), (bx - 5, by + 2), (bx - 10, by - 3),
               (bx - 3, by - 3)], fill=(240, 200, 90),
              outline=(140, 100, 20))


def scene_france(d, x, y, w, h):
    """France protests: Eiffel Tower, crowd, placards, tricolore."""
    vgrad(d, (x, y, x + w, y + h), (190, 205, 230), (150, 165, 200))
    # tricolore band top
    d.rectangle([x, y, x + w // 3, y + 8], fill=(0, 85, 164))
    d.rectangle([x + w // 3, y, x + 2 * w // 3, y + 8], fill=(255, 255, 255))
    d.rectangle([x + 2 * w // 3, y, x + w, y + 8], fill=(239, 65, 53))
    # Eiffel Tower silhouette
    tx = x + w - 78
    ty = y + h - 30
    d.polygon([(tx, ty), (tx + 14, y + 16), (tx + 22, y + 16), (tx + 36, ty)],
              fill=(60, 64, 76))
    d.polygon([(tx + 14, y + 16), (tx + 18, y + 8), (tx + 22, y + 16)],
              fill=(60, 64, 76))
    d.rectangle([tx + 4, y + 52, tx + 32, y + 58], fill=(245, 245, 245))
    d.rectangle([tx + 8, y + 76, tx + 28, y + 82], fill=(245, 245, 245))
    # crowd: rows of heads + shoulders
    import random
    random.seed(11)
    for row, (ry, r) in enumerate([(y + h - 44, 9), (y + h - 30, 10)]):
        for i in range(9):
            cx = x + 14 + i * 17 + (row * 8)
            d.ellipse([cx - r, ry - r, cx + r, ry + r],
                      fill=random.choice([(220, 180, 140), (160, 110, 80),
                                          (240, 205, 170), (110, 75, 50)]))
            d.pieslice([cx - r - 2, ry + r - 6, cx + r + 2, ry + r + 14],
                       180, 360, fill=random.choice(
                           [(180, 40, 40), (40, 90, 160), (240, 200, 60),
                            (60, 140, 80), (120, 60, 140)]))
    # placards
    for (px, py, col) in [(x + 30, y + 52, (255, 255, 255)),
                          (x + 96, y + 44, (255, 240, 150)),
                          (x + 150, y + 56, (255, 255, 255))]:
        d.line([(px + 10, py + 18), (px + 10, py + 44)], fill=(90, 70, 50),
               width=3)
        d.rectangle([px, py, px + 34, py + 18], fill=col,
                    outline=(60, 60, 60))
        d.line([(px + 5, py + 6), (px + 29, py + 6)], fill=(30, 30, 30),
               width=2)
        d.line([(px + 5, py + 12), (px + 24, py + 12)], fill=(30, 30, 30),
               width=2)


def scene_markets(d, x, y, w, h):
    """Markets rout: red candlesticks plunging, big down arrow, tickers."""
    vgrad(d, (x, y, x + w, y + h), (250, 245, 235), (235, 220, 205))
    # grid
    for i in range(1, 4):
        gy = y + 14 + i * 24
        d.line([(x + 8, gy), (x + w - 8, gy)], fill=(220, 205, 185), width=1)
    # candlesticks falling left to right
    base = y + h - 34
    candles = [(22, 30, 58), (58, 26, 50), (94, 34, 66), (130, 30, 74),
               (166, 38, 88), (202, 34, 96)]
    for (cxx, top, bot) in candles:
        cx = x + cxx
        d.line([(cx, y + top), (cx, y + bot)], fill=(190, 30, 30), width=2)
        d.rectangle([cx - 7, y + top + 6, cx + 7, y + bot - 4],
                    fill=(200, 35, 35))
    # big red down arrow
    ax, ay = x + w - 66, y + 16
    d.polygon([(ax, ay), (ax + 26, ay), (ax + 26, ay + 26),
               (ax + 40, ay + 26), (ax + 13, ay + 62), (ax - 14, ay + 26),
               (ax, ay + 26)], fill=(200, 30, 30))
    # ticker strip
    d.rectangle([x, base, x + w, y + h], fill=(24, 24, 28))
    f = font(11, bold=True)
    d.text((x + 8, base + 6), "S&P -3.7%", font=f, fill=(255, 90, 80))
    d.text((x + 86, base + 6), "NASDAQ -5.3%", font=f, fill=(255, 90, 80))
    d.text((x + 178, base + 6), "NVDA -14%", font=f, fill=(255, 200, 60))
    # small chip square (Nvidia)
    d.rectangle([x + 12, y + 12, x + 40, y + 34], fill=(30, 40, 50),
                outline=(120, 200, 80))
    d.text((x + 15, y + 16), "NV", font=font(10, bold=True),
           fill=(120, 200, 80))


def scene_f1(d, x, y, w, h):
    """F1 Las Vegas: neon skyline, race car, checkered flag."""
    vgrad(d, (x, y, x + w, y + h), (20, 10, 50), (70, 20, 90))
    # stars
    import random
    random.seed(3)
    for _ in range(18):
        sx = x + random.randint(4, w - 4)
        sy = y + random.randint(4, 40)
        d.ellipse([sx, sy, sx + 2, sy + 2], fill=(255, 255, 255))
    # neon skyline: Stratosphere needle + Luxor pyramid + towers
    base_y = y + h - 34
    d.rectangle([x + 16, base_y - 66, x + 24, base_y], fill=(20, 20, 40),
                outline=(255, 80, 200))
    d.ellipse([x + 12, base_y - 74, x + 28, base_y - 62], fill=(255, 80, 200))
    d.polygon([(x + 44, base_y), (x + 66, base_y - 52), (x + 88, base_y)],
              fill=(20, 20, 40), outline=(255, 200, 60))
    for (tx, th, tw_, col) in [(x + 100, 40, 18, (0, 220, 255)),
                               (x + 124, 52, 16, (255, 80, 120)),
                               (x + 146, 34, 20, (140, 255, 120)),
                               (x + 172, 46, 16, (255, 180, 60)),
                               (x + 194, 38, 18, (0, 220, 255))]:
        d.rectangle([tx, base_y - th, tx + tw_, base_y], fill=(20, 20, 40),
                    outline=col)
        for wy in range(base_y - th + 5, base_y - 4, 8):
            d.rectangle([tx + 3, wy, tx + tw_ - 3, wy + 3], fill=col)
    # track
    d.rectangle([x, base_y, x + w, y + h], fill=(30, 30, 36))
    d.line([(x, base_y + 14), (x + w, base_y + 14)], fill=(255, 255, 255),
           width=2)
    for xx in range(x + 6, x + w - 6, 30):
        d.line([(xx, base_y + 14), (xx + 16, base_y + 14)],
               fill=(255, 220, 60), width=3)
    # race car (low, sleek)
    cx, cy = x + 52, base_y - 2
    d.polygon([(cx, cy - 12), (cx + 26, cy - 16), (cx + 62, cy - 14),
               (cx + 84, cy - 6), (cx + 88, cy), (cx, cy)],
              fill=(200, 20, 40))
    d.polygon([(cx + 28, cy - 16), (cx + 44, cy - 24), (cx + 58, cy - 14)],
              fill=(40, 40, 50))
    d.ellipse([cx + 12, cy - 8, cx + 30, cy + 8], fill=(15, 15, 18),
              outline=(200, 200, 200))
    d.ellipse([cx + 62, cy - 8, cx + 80, cy + 8], fill=(15, 15, 18),
              outline=(200, 200, 200))
    d.line([(cx + 88, cy - 4), (cx + 100, cy - 4)], fill=(255, 220, 60),
           width=3)
    # checkered flag top-right
    fx, fy = x + w - 44, y + 10
    d.line([(fx, fy), (fx, fy + 34)], fill=(200, 200, 200), width=3)
    for r in range(3):
        for c in range(4):
            col = (20, 20, 20) if (r + c) % 2 == 0 else (255, 255, 255)
            d.rectangle([fx + 2 + c * 8, fy + r * 8, fx + 10 + c * 8,
                         fy + 8 + r * 8], fill=col)


def scene_football(d, x, y, w, h):
    """Premier League: floodlit stadium, green pitch, scoreboard."""
    vgrad(d, (x, y, x + w, y + h), (30, 50, 90), (90, 120, 170))
    # floodlight pylons
    for fx in (x + 18, x + w - 18):
        d.line([(fx, y + 8), (fx, y + 52)], fill=(220, 220, 220), width=4)
        d.rectangle([fx - 12, y + 4, fx + 12, y + 16], fill=(255, 250, 200),
                    outline=(200, 180, 100))
        for lx in range(fx - 10, fx + 11, 6):
            d.ellipse([lx, y + 6, lx + 3, y + 9], fill=(255, 255, 220))
    # stands
    d.rectangle([x, y + 52, x + w, y + 72], fill=(120, 30, 40))
    import random
    random.seed(5)
    for _ in range(60):
        sx = x + random.randint(4, w - 4)
        sy = y + random.randint(54, 70)
        d.ellipse([sx, sy, sx + 3, sy + 3],
                  fill=random.choice([(255, 255, 255), (255, 220, 90),
                                      (180, 220, 255)]))
    # pitch
    d.rectangle([x, y + 72, x + w, y + h], fill=(40, 140, 60))
    for i in range(5):
        d.rectangle([x + i * (w // 5), y + 72, x + (i + 1) * (w // 5), y + h],
                    fill=(46, 150, 66) if i % 2 else (40, 140, 60))
    d.ellipse([x + w // 2 - 26, y + 84, x + w // 2 + 26, y + 108],
              outline=(255, 255, 255), width=2)
    d.line([(x, y + 96), (x + w, y + 96)], fill=(255, 255, 255), width=2)
    # ball
    bx, by = x + w // 2 + 52, y + h - 22
    d.ellipse([bx - 9, by - 9, bx + 9, by + 9], fill=(255, 255, 255),
              outline=(30, 30, 30))
    d.polygon([(bx, by - 5), (bx + 5, by - 1), (bx + 3, by + 5),
               (bx - 3, by + 5), (bx - 5, by - 1)], fill=(30, 30, 30))
    # scoreboard
    sx, sy = x + w // 2 - 72, y + 76
    d.rounded_rectangle([sx, sy, sx + 144, sy + 24], radius=4,
                        fill=(20, 20, 24), outline=(255, 255, 255))
    f = font(12, bold=True)
    d.text((sx + 8, sy + 5), "LEEDS 4–1 CHELSEA", font=f, fill=(255, 220, 60))

# ================================================================ mini map
CONTINENTS = {
    "na": [(-168, 66), (-140, 70), (-120, 71), (-100, 68), (-85, 66),
           (-75, 62), (-65, 60), (-55, 47), (-60, 43), (-70, 41), (-76, 35),
           (-80, 26), (-86, 30), (-90, 21), (-97, 16), (-105, 20),
           (-114, 29), (-124, 40), (-124, 49), (-140, 60), (-158, 58),
           (-168, 60)],
    "sa": [(-80, 10), (-72, 12), (-62, 10), (-52, 5), (-50, -5), (-35, -8),
           (-40, -20), (-48, -28), (-58, -35), (-65, -41), (-70, -52),
           (-74, -40), (-73, -20), (-80, -5), (-81, 5)],
    "af": [(-17, 15), (-10, 30), (-5, 35), (10, 37), (20, 32), (32, 31),
           (35, 28), (43, 12), (51, 11), (48, 0), (40, -10), (35, -18),
           (28, -33), (18, -35), (12, -18), (8, 4), (-8, 5), (-17, 15)],
    "eu": [(-10, 36), (-9, 43), (-2, 48), (-5, 50), (0, 51), (5, 53),
           (8, 57), (10, 59), (18, 56), (21, 55), (24, 59), (28, 60),
           (30, 62), (32, 70), (40, 68), (44, 66), (40, 60), (48, 58),
           (42, 52), (40, 47), (36, 45), (30, 46), (28, 44), (23, 40),
           (20, 40), (16, 44), (12, 44), (8, 44), (3, 42), (-2, 37),
           (-9, 37)],
    "as": [(30, 62), (40, 68), (55, 68), (70, 72), (90, 75), (110, 76),
           (130, 72), (160, 69), (178, 66), (170, 60), (162, 56),
           (158, 52), (142, 50), (140, 40), (135, 35), (127, 33),
           (122, 30), (120, 22), (110, 20), (105, 10), (100, 8), (98, 15),
           (92, 21), (88, 22), (80, 15), (77, 8), (72, 20), (66, 25),
           (60, 25), (57, 26), (52, 28), (48, 30), (44, 29), (40, 36),
           (36, 36), (30, 36)],
    "au": [(113, -22), (114, -30), (115, -35), (124, -33), (132, -32),
           (137, -35), (140, -38), (147, -39), (150, -37), (153, -27),
           (146, -19), (142, -11), (135, -12), (130, -13), (126, -14),
           (122, -17), (114, -22)],
}

MARKERS = [("Kyiv", 30.5, 50.5), ("Riyadh", 46.7, 24.6),
           ("Antalya", 30.7, 36.9), ("Lima", -77.0, -12.0),
           ("Johannesburg", 28.0, -26.2), ("Tupancireta", -53.8, -29.0),
           ("Tokyo", 139.7, 35.7), ("Las Vegas", -115.1, 36.2)]


def draw_map(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(188, 214, 232),
                outline=(120, 140, 160))
    for lon in range(-150, 181, 30):
        mx = x + (lon + 180) / 360 * w
        d.line([(mx, y), (mx, y + h)], fill=(160, 190, 210), width=1)
    for lat in (-60, -30, 0, 30, 60):
        my = y + (90 - lat) / 180 * h
        d.line([(x, my), (x + w, my)], fill=(160, 190, 210), width=1)

    def px(lon, lat):
        return (x + (lon + 180) / 360 * w, y + (90 - lat) / 180 * h)

    for poly in CONTINENTS.values():
        d.polygon([px(lon, lat) for lon, lat in poly], fill=(232, 220, 192),
                  outline=(138, 125, 90))
    for i, (_, lon, lat) in enumerate(MARKERS, 1):
        mx, my = px(lon, lat)
        d.ellipse([mx - 6, my - 6, mx + 6, my + 6], fill=(200, 30, 30),
                  outline=(255, 255, 255), width=2)
        f = font(8, bold=True)
        tw = d.textlength(str(i), font=f)
        d.text((mx - tw / 2, my - 4), str(i), font=f, fill=(255, 255, 255))


# ================================================================ panels
REGION_COLORS = {
    "EUROPE": (31, 78, 121), "AMERICAS": (139, 26, 26),
    "MIDDLE EAST": (122, 74, 0), "AFRICA": (15, 107, 74),
    "ASIA": (91, 45, 142), "SPORT": (18, 63, 42), "MARKETS": (122, 31, 31),
}

PANELS = [
    (scene_tankers, "MIDDLE EAST", "Tankers ablaze off Hormuz",
     "Two hit by projectiles, a third strikes a mine and burns; no casualties."),
    (scene_riyadh, "MIDDLE EAST", "Three missiles downed over Riyadh",
     "Coalition intercepts Houthi ballistic missiles; second strike on capital in days."),
    (scene_cop31, "EUROPE", "COP31: deal at last, day 14",
     "New package lands in Antalya; approval vote Sunday after fossil-fuel fight."),
    (scene_peru, "AMERICAS", "6.7 quake shakes Peru's Andes",
     "Epicentre near Junín; felt in Lima; minor damage, no deaths reported."),
    (scene_brazil, "AMERICAS", "Storm wipes out a Brazilian town",
     "Supercell hits Tupancireta in 40 minutes: 4 dead, 162 hurt, 8,000 homes damaged."),
    (scene_g20, "AFRICA", "G20 opens in Africa — first time",
     "Johannesburg: leaders back a 122-point declaration despite the US boycott."),
    (scene_icj, "ASIA", "World court: Myanmar guilty of genocide",
     "ICJ rules 9–6 on the 2017 Rohingya killings; reparations ordered. A first."),
    (scene_mexico, "AMERICAS", "'El Chapo Isidro' captured",
     "Sinaloa raid: drug lord seized; 11 dead in the raid and cartel backlash."),
    (scene_france, "EUROPE", "France marches, sixth weekend",
     "82,500 by police count, 150,000 by organisers; turnout falls from last week."),
    (scene_markets, "MARKETS", "Markets rout: worst week since April",
     "Nasdaq -5.3%, S&P -3.7%; Nvidia sinks 14% as SEC-probe reports hit."),
    (scene_f1, "SPORT", "Verstappen on pole in Las Vegas",
     "Antonelli fastest but takes a five-place penalty; new champion, 20, starts behind."),
    (scene_football, "SPORT", "Leeds stun Chelsea 4–1",
     "First win at Stamford Bridge since 1999; Arsenal held 2–2 at Newcastle."),
]

BRIEFS = [
    "Poland: Russian missile lands ~50 km from border",
    "Kryvyi Rih: boy, 7, and paramedic, 20, killed; 73 hurt",
    "Finland probes Russian helicopter incursion of 4.1 km",
    "Trump vows to cap credit-card rates at 10%",
    "Pentagon moves to curb US–Canada defence ties",
    "Bahrain: defences intercept Iranian aerial attacks",
    "Basra: Hartha power-station fire kills 4, injures 30",
    "Nigeria: boat of mourners overturns; 24 dead, 24 rescued",
    "DR Congo Ebola fight hit by violence and distrust",
    "Manipur: tainted alcohol kills 11",
    "Sri Lanka landslide kills four in Central Province",
    "Japan: hundreds protest PM Takaichi's Taiwan remarks",
    "India 629/6 at lunch, Pant 128, lead 261 — 1st Test",
    "Australia edge England by 3 wickets in 1st T20",
    "Denmark expels Russian diplomat over murder plot",
    "Gaza: strike kills three in aid vehicle, witnesses say",
    "EU–Indonesia sign trade and investment deals",
]

NUMBERS = [
    ("600,000", "KYIV ARMY CAP IN US PLAN"),
    ("6.7", "PERU QUAKE MAGNITUDE"),
    ("122", "G20 DECLARATION POINTS"),
    ("8,000", "HOMES WRECKED, BRAZIL STORM"),
    ("10,000+", "ROHINGYA KILLED IN 2017 — ICJ"),
]


def panel(d, x, y, scene_fn, region, headline, fact):
    d.rectangle([x, y, x + 245, y + 192], fill=(255, 253, 246),
                outline=(170, 160, 135))
    scene_fn(d, x + 1, y + 1, 243, 116)
    chip(d, x + 6, y + 6, region, REGION_COLORS[region], fsize=9)
    hf = font(13, bold=True)
    lines = wrap(d, headline, hf, 233)[:2]
    draw_lines(d, x + 6, y + 122, lines, hf, (20, 20, 20), leading=16)
    ff = font(10)
    flines = wrap(d, fact, ff, 233)[:2]
    draw_lines(d, x + 6, y + 156, flines, ff, (60, 60, 60), leading=13)


def build():
    img = Image.new("RGB", (W, H), (248, 243, 230))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W - 1, H - 1], outline=(40, 35, 25), width=3)

    # ---- masthead
    d.text((14, 8), "THE WORLD TODAY", font=font(20, bold=True, serif=True),
           fill=(139, 26, 26))
    _ed = "SUNDAY EDITION · No. 326"
    _ef = font(10, bold=True)
    d.text((W - 14 - d.textlength(_ed, font=_ef), 12), _ed, font=_ef,
           fill=(90, 85, 70))
    d.text((14, 30), "SUNDAY 22 NOVEMBER 2026",
           font=font(42, bold=True, serif=True), fill=(20, 20, 20))
    d.text((14, 70),
           "Gulf strikes · Peru quake · COP31 day 14 · G20 opens in Africa — "
           "30 dated stories, 6 regions",
           font=font(14, bold=True), fill=(60, 55, 45))
    d.line([(10, 87), (W - 10, 87)], fill=(40, 35, 25), width=2)

    # ---- big-numbers strip
    d.rectangle([10, 88, W - 10, 132], fill=(18, 38, 62))
    cw = (W - 20) / 5
    for i, (num, label) in enumerate(NUMBERS):
        cx = 10 + i * cw
        if i:
            d.line([(cx, 92), (cx, 128)], fill=(90, 110, 140), width=1)
        nf = font(22, bold=True)
        tw = d.textlength(num, font=nf)
        d.text((cx + (cw - tw) / 2, 91), num, font=nf, fill=(242, 193, 78))
        lf = font(9, bold=True)
        lw = d.textlength(label, font=lf)
        d.text((cx + (cw - lw) / 2, 116), label, font=lf,
               fill=(230, 235, 245))

    # ---- lead story
    d.rectangle([10, 132, W - 10, 306], fill=(255, 253, 246),
                outline=(170, 160, 135))
    d.text((16, 140), "LEAD — UKRAINE PEACE PLAN",
           font=font(12, bold=True), fill=(139, 26, 26))
    hf = font(26, bold=True, serif=True)
    hl = wrap(d, "Trump: 28-point plan is “not my final offer”", hf, 424)[:3]
    y = draw_lines(d, 16, 160, hl, hf, (20, 20, 20), leading=30)
    bf = font(12)
    body = ("Zelensky spoke to Trump on Saturday; security teams meet in "
            "Geneva on Sunday. The draft caps Kyiv’s army at 600,000, bars "
            "NATO and asks it to cede the Donbas. Trump’s deadline: 27 Nov "
            "— “flexible”.")
    bl = wrap(d, body, bf, 424)[:4]
    y = draw_lines(d, 16, y + 4, bl, bf, (50, 50, 50), leading=15)
    cx = 16
    for t in ["ARMY 600,000", "NO NATO", "CEDE DONBAS", "GENEVA SUN"]:
        cx += chip(d, cx, 276, t, (31, 78, 121), fsize=10) + 6
    scene_geneva(d, 452, 136, 558, 166)

    # ---- grid of 12 visual panels
    xs = [10, 263, 516, 769]
    ys = [312, 510, 708]
    for i, (fn, region, head, fact) in enumerate(PANELS):
        panel(d, xs[i % 4], ys[i // 4], fn, region, head, fact)

    # ---- bottom band: also-on list + mini map
    d.line([(10, 902), (W - 10, 902)], fill=(40, 35, 25), width=2)
    d.text((14, 908), "ALSO ON — 17 MORE STORIES", font=font(12, bold=True),
           fill=(139, 26, 26))
    bf = font(10)
    for i, b in enumerate(BRIEFS):
        col = 0 if i < 9 else 1
        row = i if i < 9 else i - 9
        bx = 14 if col == 0 else 336
        by = 926 + row * 11
        d.text((bx, by), "• " + b, font=bf, fill=(45, 45, 45))
    d.text((664, 908), "WHERE IT HAPPENED", font=font(12, bold=True),
           fill=(139, 26, 26))
    kf = font(8)
    d.text((664, 926), "1 Kyiv · 2 Riyadh · 3 Antalya · 4 Lima", font=kf,
           fill=(60, 60, 60))
    d.text((664, 936), "5 Johannesburg · 6 Tupancireta · 7 Tokyo · 8 Las Vegas",
           font=kf, fill=(60, 60, 60))
    draw_map(d, 664, 946, 350, 62)
    d.text((664, 1011),
           "Sources: Reuters · AP · AFP · BBC · CNN · Al Jazeera · UKMTO · "
           "USGS · The Times",
           font=font(8), fill=(90, 85, 70))
    return img


def run():
    img = build()
    img.save(OUT, "PNG", optimize=True)
    size = os.path.getsize(OUT)
    print("wrote %s (%dx%d, %d bytes)" % (OUT, W, H, size))
    assert size <= 1024 * 1024, "entry.png over 1 MB"


if __name__ == "__main__":
    run()
