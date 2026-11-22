#!/usr/bin/env python3
"""v6 front page for make.fun news-image-20261122.

Renders one 1024x1024 front page summing up Sunday 22 November 2026's
world news and writes it ONLY to $MAKEFUN_OUTPUT_DIR/entry.png
(fallback /output/entry.png), mode 0644. The grader mounts the program
read-only, so nothing is ever written next to this script.

Visual-first leader pattern: 13 main stories, each with a large detailed
drawn scene filling its panel; huge date masthead; big-numbers strip;
31 dated stories across 6 regions. All facts verified against published
reports of 21-22 November 2026 (see stories-v4.md plus the v6 updates
in stories-v6.md). Pure PIL drawing, deterministic, no network.
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- output
# The grader collects outputs from $MAKEFUN_OUTPUT_DIR (mounted as
# /output). The program directory is read-only: NEVER write beside
# this script, and never use a tempfile/mkstemp path (0600) here.
OUT_DIR = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
OUT_PATH = os.path.join(OUT_DIR, "entry.png")

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (247, 242, 231)
INK = (22, 22, 26)
NAVY = (20, 38, 74)
NAVY2 = (28, 52, 96)
GOLD = (232, 182, 76)
CREAM = (250, 244, 224)
RED = (178, 34, 34)
DARKRED = (140, 20, 20)
GREY = (90, 88, 82)
LIGHTGREY = (210, 204, 190)
PANEL = (255, 253, 247)
BORDER = (120, 110, 92)
SKY_DAY = (135, 190, 225)
SKY_DUSK = (232, 140, 80)
SKY_NIGHT = (16, 24, 54)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    """Load a DejaVu truetype font; fall back to PIL's default bitmap."""
    try:
        return ImageFont.truetype(os.path.join(FONT_DIR, name), size)
    except OSError:
        return ImageFont.load_default()


SERIF_B = "DejaVuSerif-Bold.ttf"
SERIF = "DejaVuSerif.ttf"
SANS_B = "DejaVuSans-Bold.ttf"
SANS = "DejaVuSans.ttf"
SANS_O = "DejaVuSans-Oblique.ttf"


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def text_block(draw, x, y, lines, fnt, fill, leading=None):
    """Draw lines top-left at (x, y); returns the y below the block."""
    if leading is None:
        leading = fnt.size + 3
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def sky_band(draw, box, top, bottom):
    """Vertical gradient sky made of a few flat bands (deterministic)."""
    x0, y0, x1, y1 = box
    steps = 8
    for i in range(steps):
        t = i / (steps - 1)
        col = tuple(int(top[c] + (bottom[c] - top[c]) * t) for c in range(3))
        yy0 = y0 + (y1 - y0) * i // steps
        yy1 = y0 + (y1 - y0) * (i + 1) // steps
        draw.rectangle([x0, yy0, x1, yy1], fill=col)


def stars(draw, box, seed_points):
    """Fixed star positions (deterministic list of (fx, fy) fractions)."""
    x0, y0, x1, y1 = box
    for fx, fy, r in seed_points:
        cx = x0 + (x1 - x0) * fx
        cy = y0 + (y1 - y0) * fy
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 230))


def flame(draw, cx, cy, s):
    """A small stylised flame (orange outer, yellow inner)."""
    draw.polygon(
        [(cx, cy - 1.6 * s), (cx + 0.9 * s, cy + 0.6 * s),
         (cx, cy + 1.2 * s), (cx - 0.9 * s, cy + 0.6 * s)],
        fill=(240, 110, 20),
    )
    draw.polygon(
        [(cx, cy - 0.8 * s), (cx + 0.45 * s, cy + 0.6 * s),
         (cx, cy + 1.0 * s), (cx - 0.45 * s, cy + 0.6 * s)],
        fill=(250, 210, 60),
    )


def smoke(draw, cx, cy, s, col=(120, 118, 112)):
    """Three overlapping smoke puffs."""
    for dx, dy, r in ((0, 0, 1.0), (-0.9, -0.5, 0.8), (0.9, -0.6, 0.75)):
        draw.ellipse(
            [cx + dx * s - r * s, cy + dy * s - r * s,
             cx + dx * s + r * s, cy + dy * s + r * s],
            fill=col,
        )


def tag_chip(draw, x, y, label, fill=RED):
    """Small coloured region chip; returns its width."""
    f = font(SANS_B, 10)
    w = int(draw.textlength(label, font=f)) + 12
    draw.rounded_rectangle([x, y, x + w, y + 15], radius=3, fill=fill)
    draw.text((x + 6, y + 2), label, font=f, fill=(255, 255, 255))
    return w

# ================================================================ scenes
# Every scene draws inside its own box (x0, y0, x1, y1) with PIL shapes
# only. All positions are fractions of the box so panels stay correct
# at any size. No text inside scenes except where noted.


def scene_geneva(draw, box):
    """Lead: Geneva conference hall, US + Ukraine flags, dove, plan."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    sky_band(draw, box, (214, 196, 160), (240, 226, 196))
    # back wall
    draw.rectangle([x0, y0 + h * 0.30, x1, y1], fill=(196, 172, 128))
    # arched windows
    for i in range(4):
        wx = x0 + w * (0.08 + i * 0.23)
        ww = w * 0.15
        draw.rounded_rectangle(
            [wx, y0 + h * 0.08, wx + ww, y0 + h * 0.62],
            radius=int(ww / 2) - 4, fill=(168, 205, 228))
        draw.line([wx + ww / 2, y0 + h * 0.08, wx + ww / 2, y0 + h * 0.62],
                  fill=(120, 100, 70), width=2)
        draw.line([wx, y0 + h * 0.35, wx + ww, y0 + h * 0.35],
                  fill=(120, 100, 70), width=2)
    # columns between windows
    for i in range(5):
        cx = x0 + w * (0.02 + i * 0.235)
        draw.rectangle([cx, y0 + h * 0.05, cx + w * 0.035, y0 + h * 0.66],
                       fill=(150, 126, 88))
    # floor
    draw.rectangle([x0, y0 + h * 0.66, x1, y1], fill=(122, 96, 64))
    # long table
    draw.rectangle([x0 + w * 0.16, y0 + h * 0.68, x1 - w * 0.16, y0 + h * 0.80],
                   fill=(96, 62, 40))
    draw.rectangle([x0 + w * 0.16, y0 + h * 0.80, x1 - w * 0.16, y0 + h * 0.86],
                   fill=(70, 44, 28))
    # white plan document on the table
    dx, dy = x0 + w * 0.44, y0 + h * 0.60
    draw.rectangle([dx, dy, dx + w * 0.13, dy + h * 0.10], fill=(255, 255, 255),
                   outline=(60, 60, 60))
    for j in range(3):
        draw.line([dx + 6, dy + 8 + j * 7, dx + w * 0.13 - 6, dy + 8 + j * 7],
                  fill=(80, 80, 80), width=1)
    # US flag (left) and Ukraine flag (right) on poles, clear of columns
    for fx, (c1, c2) in ((0.10, ((178, 34, 52), (255, 255, 255))),
                         (0.82, ((0, 91, 187), (255, 215, 0)))):
        px = x0 + w * fx
        draw.line([px, y0 + h * 0.30, px, y0 + h * 0.68], fill=(60, 40, 20),
                  width=3)
        draw.rectangle([px, y0 + h * 0.32, px + w * 0.09, y0 + h * 0.42],
                       fill=c1)
        draw.rectangle([px, y0 + h * 0.42, px + w * 0.09, y0 + h * 0.52],
                       fill=c2)
        if fx < 0.5:  # stars-and-stripes hint on the US flag
            draw.rectangle([px, y0 + h * 0.32, px + w * 0.038, y0 + h * 0.40],
                           fill=(20, 38, 74))
            for sy in range(2):
                for sx in range(2):
                    draw.ellipse(
                        [px + 3 + sx * 8, y0 + h * 0.32 + 3 + sy * 7,
                         px + 6 + sx * 8, y0 + h * 0.32 + 6 + sy * 7],
                        fill=(255, 255, 255))
    # dove above the table
    cx, cy = x0 + w * 0.50, y0 + h * 0.20
    draw.ellipse([cx - 14, cy - 6, cx + 14, cy + 6], fill=(255, 255, 255))
    draw.ellipse([cx + 10, cy - 5, cx + 20, cy + 1], fill=(255, 255, 255))
    draw.polygon([(cx - 12, cy - 2), (cx - 26, cy - 10), (cx - 24, cy + 2)],
                 fill=(255, 255, 255))
    draw.ellipse([cx - 16, cy - 9, cx - 8, cy - 1], fill=(255, 255, 255))
    draw.polygon([(cx + 2, cy - 14), (cx + 8, cy - 26), (cx + 12, cy - 12)],
                 fill=(235, 235, 235))


def scene_poland(draw, box):
    """Night field, missile streak, explosion, Polish flag on a post."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    sky_band(draw, box, (10, 16, 40), (38, 52, 96))
    stars(draw, box, [(0.12, 0.15, 2), (0.3, 0.08, 1), (0.55, 0.12, 2),
                      (0.78, 0.2, 1), (0.9, 0.08, 2), (0.45, 0.22, 1)])
    # moon
    draw.ellipse([x0 + w * 0.80, y0 + h * 0.06, x0 + w * 0.90, y0 + h * 0.24],
                 fill=(240, 238, 210))
    # missile streak
    mx0, my0 = x0 + w * 0.12, y0 + h * 0.18
    mx1, my1 = x0 + w * 0.62, y0 + h * 0.55
    draw.line([mx0, my0, mx1, my1], fill=(250, 180, 60), width=4)
    draw.line([mx0, my0, mx1, my1], fill=(255, 240, 180), width=2)
    draw.ellipse([mx1 - 8, my1 - 8, mx1 + 8, my1 + 8], fill=(250, 200, 80))
    # explosion burst where it lands
    ex, ey = x0 + w * 0.66, y0 + h * 0.62
    for r, col in ((26, (240, 120, 30)), (17, (250, 190, 60)),
                   (9, (255, 240, 170))):
        draw.ellipse([ex - r, ey - r, ex + r, ey + r], fill=col)
    smoke(draw, ex + 16, ey - 26, 9, (90, 88, 96))
    # pine trees
    for tx in (0.06, 0.16, 0.86, 0.95):
        bx = x0 + w * tx
        draw.polygon([(bx - 12, y0 + h * 0.92), (bx, y0 + h * 0.62),
                      (bx + 12, y0 + h * 0.92)], fill=(12, 40, 22))
    # ground + flag post
    draw.rectangle([x0, y0 + h * 0.86, x1, y1], fill=(24, 34, 20))
    px = x0 + w * 0.44
    draw.line([px, y0 + h * 0.55, px, y0 + h * 0.88], fill=(200, 200, 200),
              width=2)
    draw.rectangle([px, y0 + h * 0.56, px + 26, y0 + h * 0.65],
                   fill=(255, 255, 255))
    draw.rectangle([px, y0 + h * 0.65, px + 26, y0 + h * 0.74],
                   fill=(220, 20, 60))


def scene_cop31(draw, box):
    """Globe, rising thermometer, conference hall, fossil-fuel placard."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    sky_band(draw, box, (120, 180, 215), (205, 228, 240))
    # conference hall silhouette
    draw.rectangle([x0 + w * 0.55, y0 + h * 0.55, x1 - w * 0.04, y1],
                   fill=(90, 100, 115))
    for i in range(4):
        wx = x0 + w * (0.59 + i * 0.10)
        draw.rectangle([wx, y0 + h * 0.62, wx + w * 0.06, y0 + h * 0.82],
                       fill=(250, 220, 130))
    draw.polygon([(x0 + w * 0.55, y0 + h * 0.55), (x0 + w * 0.76, y0 + h * 0.40),
                  (x1 - w * 0.04, y0 + h * 0.55)], fill=(70, 80, 95))
    # globe
    cx, cy, r = x0 + w * 0.30, y0 + h * 0.48, int(h * 0.36)
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(40, 110, 200),
                 outline=(20, 60, 120), width=2)
    draw.ellipse([cx - r * 0.55, cy - r * 0.75, cx - r * 0.05, cy - r * 0.15],
                 fill=(60, 160, 90))
    draw.ellipse([cx + r * 0.10, cy + r * 0.10, cx + r * 0.70, cy + r * 0.65],
                 fill=(60, 160, 90))
    draw.ellipse([cx - r * 0.35, cy + r * 0.45, cx + r * 0.05, cy + r * 0.80],
                 fill=(90, 180, 110))
    draw.arc([cx - r, cy - r, cx + r, cy + r], 200, 340, fill=(200, 230, 250),
             width=2)
    # thermometer, mercury high and red
    tx = x0 + w * 0.52
    draw.rounded_rectangle([tx - 6, y0 + h * 0.14, tx + 6, y0 + h * 0.78],
                           radius=6, fill=(255, 255, 255),
                           outline=(60, 60, 60))
    draw.rectangle([tx - 3, y0 + h * 0.30, tx + 3, y0 + h * 0.76],
                   fill=(220, 40, 30))
    draw.ellipse([tx - 11, y0 + h * 0.74, tx + 11, y0 + h * 0.94],
                 fill=(220, 40, 30))
    for j, yy in enumerate((0.20, 0.38, 0.56)):
        draw.line([tx + 6, y0 + h * yy, tx + 12, y0 + h * yy],
                  fill=(60, 60, 60), width=2)
    # ground
    draw.rectangle([x0, y0 + h * 0.88, x1, y1], fill=(70, 120, 70))


def scene_france(draw, box):
    """Eiffel Tower, crowd, tricolore placards, dusk sky."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    sky_band(draw, box, (250, 190, 120), (250, 220, 180))
    # sun low
    draw.ellipse([x0 + w * 0.78, y0 + h * 0.10, x0 + w * 0.92, y0 + h * 0.32],
                 fill=(250, 200, 90))
    # Eiffel Tower (left)
    tx = x0 + w * 0.20
    base = y0 + h * 0.92
    top = y0 + h * 0.10
    draw.polygon([(tx - w * 0.13, base), (tx, top), (tx + w * 0.13, base)],
                 fill=(120, 100, 80))
    draw.rectangle([x0 + w * 0.055, base - h * 0.06, x0 + w * 0.345,
                    base - h * 0.02], fill=(120, 100, 80))
    draw.rectangle([tx - 3, top - 8, tx + 3, top + 2], fill=(120, 100, 80))
    draw.rectangle([x0 + w * 0.10, y0 + h * 0.55, x0 + w * 0.30, y0 + h * 0.60],
                   fill=(250, 220, 180))
    # crowd
    for i in range(14):
        cx = x0 + w * (0.40 + i * 0.042)
        cy = y0 + h * (0.86 - (i % 3) * 0.02)
        draw.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=(40, 40, 60))
        draw.rectangle([cx - 6, cy + 4, cx + 6, cy + 16], fill=(60, 60, 90))
    # placards: tricolore stripes
    for px, py in ((0.52, 0.62), (0.72, 0.58), (0.88, 0.64)):
        bx, by = x0 + w * px, y0 + h * py
        draw.rectangle([bx, by, bx + 30, by + 16], fill=(255, 255, 255),
                       outline=(40, 40, 40))
        draw.rectangle([bx, by, bx + 10, by + 16], fill=(0, 85, 164))
        draw.rectangle([bx + 20, by, bx + 30, by + 16], fill=(239, 65, 53))
        draw.line([bx + 15, by + 16, bx + 15, by + 30], fill=(60, 40, 20),
                  width=2)
    # ground
    draw.rectangle([x0, y0 + h * 0.92, x1, y1], fill=(140, 130, 115))


def scene_mexico(draw, box):
    """Desert road, helicopter with searchlight, mountains, police lights."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    sky_band(draw, box, (30, 30, 70), (120, 70, 90))
    stars(draw, box, [(0.1, 0.12, 2), (0.35, 0.08, 1), (0.6, 0.15, 2),
                      (0.85, 0.1, 1)])
    # mountains
    draw.polygon([(x0, y0 + h * 0.62), (x0 + w * 0.25, y0 + h * 0.30),
                  (x0 + w * 0.5, y0 + h * 0.62)], fill=(70, 50, 70))
    draw.polygon([(x0 + w * 0.4, y0 + h * 0.62), (x0 + w * 0.68, y0 + h * 0.26),
                  (x0 + w * 0.95, y0 + h * 0.62)], fill=(55, 40, 58))
    draw.polygon([(x0 + w * 0.60, y0 + h * 0.36), (x0 + w * 0.68, y0 + h * 0.26),
                  (x0 + w * 0.76, y0 + h * 0.36)], fill=(240, 235, 220))
    # desert ground + road
    draw.rectangle([x0, y0 + h * 0.62, x1, y1], fill=(150, 110, 70))
    draw.polygon([(x0 + w * 0.42, y1), (x0 + w * 0.48, y0 + h * 0.62),
                  (x0 + w * 0.58, y0 + h * 0.62), (x0 + w * 0.66, y1)],
                 fill=(60, 55, 55))
    for i in range(3):
        yy = y0 + h * (0.70 + i * 0.09)
        draw.line([x0 + w * 0.50, yy, x0 + w * 0.545, yy],
                  fill=(240, 220, 80), width=3)
    # helicopter (larger, so it reads at panel size)
    hx, hy = x0 + w * 0.30, y0 + h * 0.22
    draw.ellipse([hx - 34, hy - 13, hx + 34, hy + 13], fill=(40, 60, 40))
    draw.rectangle([hx + 26, hy - 5, hx + 68, hy + 3], fill=(40, 60, 40))
    draw.ellipse([hx + 10, hy - 10, hx + 28, hy + 5], fill=(170, 215, 235))
    draw.line([hx - 44, hy - 20, hx + 44, hy - 20], fill=(30, 30, 30), width=3)
    draw.line([hx - 8, hy - 32, hx + 8, hy - 32], fill=(30, 30, 30), width=2)
    # searchlight cone
    draw.polygon([(hx + 12, hy + 10), (hx - 8, y0 + h * 0.62),
                  (hx + 56, y0 + h * 0.62)], fill=(255, 250, 190))
    draw.ellipse([hx + 4, y0 + h * 0.58, hx + 44, y0 + h * 0.66],
                 fill=(255, 250, 200))
    # police car lights on the road
    for lx, col in ((0.46, (220, 30, 30)), (0.56, (30, 90, 220))):
        draw.ellipse([x0 + w * lx - 4, y0 + h * 0.90, x0 + w * lx + 4,
                      y0 + h * 0.96], fill=col)


def scene_brazil(draw, box):
    """Supercell cloud, lightning, wrecked roofs, driving rain."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    sky_band(draw, box, (60, 70, 90), (140, 150, 165))
    # huge storm cloud
    for cx, cy, r in ((0.30, 0.22, 42), (0.55, 0.16, 52), (0.78, 0.24, 44),
                      (0.45, 0.30, 46)):
        draw.ellipse([x0 + w * cx - r, y0 + h * cy - r * 0.7,
                      x0 + w * cx + r, y0 + h * cy + r * 0.7],
                     fill=(52, 58, 72))
    draw.rectangle([x0, y0 + h * 0.28, x1, y0 + h * 0.42], fill=(52, 58, 72))
    # lightning bolt
    lx = x0 + w * 0.62
    draw.polygon([(lx, y0 + h * 0.40), (lx - 10, y0 + h * 0.58),
                  (lx + 2, y0 + h * 0.58), (lx - 8, y0 + h * 0.78),
                  (lx + 12, y0 + h * 0.52), (lx + 2, y0 + h * 0.52)],
                 fill=(255, 235, 90))
    # rain streaks
    for i in range(16):
        rx = x0 + w * (0.05 + i * 0.06)
        ry = y0 + h * (0.42 + (i % 4) * 0.08)
        draw.line([rx, ry, rx - 4, ry + 12], fill=(200, 215, 230), width=2)
    # wrecked houses: tilted roofs, broken walls
    for hx, tilt in ((0.12, -8), (0.38, 10), (0.72, -12)):
        bx, by = x0 + w * hx, y0 + h * 0.78
        draw.polygon([(bx - 34, by), (bx, by - 22 + tilt),
                      (bx + 34, by)], fill=(150, 60, 40))
        draw.rectangle([bx - 28, by, bx + 28, by + 22], fill=(190, 170, 140))
        draw.rectangle([bx - 8, by + 8, bx + 8, by + 22], fill=(90, 60, 40))
        draw.line([bx + 30, by - 20, bx + 44, by - 30], fill=(120, 90, 60),
                  width=3)
    draw.rectangle([x0, y0 + h * 0.96, x1, y1], fill=(90, 85, 75))

def scene_peru(draw, box):
    """Andes peaks, cracked ground, seismograph spike, adobe house."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    sky_band(draw, box, (150, 200, 230), (225, 235, 240))
    # Andes
    draw.polygon([(x0, y0 + h * 0.55), (x0 + w * 0.22, y0 + h * 0.10),
                  (x0 + w * 0.44, y0 + h * 0.55)], fill=(90, 100, 115))
    draw.polygon([(x0 + w * 0.16, y0 + h * 0.20), (x0 + w * 0.22, y0 + h * 0.10),
                  (x0 + w * 0.29, y0 + h * 0.21)], fill=(245, 245, 245))
    draw.polygon([(x0 + w * 0.36, y0 + h * 0.55), (x0 + w * 0.60, y0 + h * 0.06),
                  (x0 + w * 0.84, y0 + h * 0.55)], fill=(70, 82, 100))
    draw.polygon([(x0 + w * 0.54, y0 + h * 0.18), (x0 + w * 0.60, y0 + h * 0.06),
                  (x0 + w * 0.67, y0 + h * 0.19)], fill=(245, 245, 245))
    draw.polygon([(x0 + w * 0.76, y0 + h * 0.55), (x0 + w * 0.92, y0 + h * 0.22),
                  (x1, y0 + h * 0.55)], fill=(95, 105, 120))
    # ground with a jagged crack
    draw.rectangle([x0, y0 + h * 0.55, x1, y1], fill=(150, 120, 85))
    cx = x0 + w * 0.50
    draw.line([(cx, y0 + h * 0.55), (cx - 12, y0 + h * 0.70),
               (cx + 6, y0 + h * 0.82), (cx - 8, y1)],
              fill=(60, 40, 25), width=4)
    # adobe house, tilted
    hx, hy = x0 + w * 0.16, y0 + h * 0.80
    draw.polygon([(hx - 30, hy), (hx, hy - 18), (hx + 30, hy)],
                 fill=(170, 90, 50))
    draw.rectangle([hx - 26, hy, hx + 26, hy + 20], fill=(205, 170, 130))
    # seismograph paper with spike
    sx, sy = x0 + w * 0.68, y0 + h * 0.62
    draw.rectangle([sx, sy, sx + w * 0.26, sy + h * 0.30], fill=(255, 255, 255),
                   outline=(60, 60, 60))
    pts = [(sx + 4, sy + h * 0.15), (sx + 18, sy + h * 0.15),
           (sx + 24, sy + h * 0.04), (sx + 30, sy + h * 0.26),
           (sx + 36, sy + h * 0.10), (sx + 48, sy + h * 0.15),
           (sx + w * 0.26 - 4, sy + h * 0.15)]
    draw.line(pts, fill=(200, 30, 30), width=2)


def scene_riyadh(draw, box):
    """Riyadh skyline at night, Kingdom Centre tower, intercepted missiles."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    sky_band(draw, box, (12, 18, 48), (60, 70, 120))
    stars(draw, box, [(0.08, 0.12, 2), (0.3, 0.07, 1), (0.5, 0.14, 2),
                      (0.72, 0.08, 1), (0.92, 0.16, 2)])
    # missile trails arcing down, met by interceptor bursts
    for fx, fy in ((0.22, 0.30), (0.50, 0.22), (0.76, 0.34)):
        bx, by = x0 + w * fx, y0 + h * fy
        draw.line([bx - 26, by - 30, bx, by], fill=(255, 200, 90), width=3)
        draw.ellipse([bx - 9, by - 9, bx + 9, by + 9], fill=(255, 220, 120))
        draw.ellipse([bx - 4, by - 4, bx + 4, by + 4], fill=(255, 255, 255))
    # skyline
    base = y0 + h * 0.96
    for bx, bw, bh, col in ((0.02, 0.14, 0.34, (30, 36, 60)),
                            (0.18, 0.12, 0.44, (38, 44, 70)),
                            (0.62, 0.13, 0.40, (30, 36, 60)),
                            (0.77, 0.11, 0.50, (38, 44, 70)),
                            (0.89, 0.10, 0.30, (30, 36, 60))):
        draw.rectangle([x0 + w * bx, base - h * bh, x0 + w * (bx + bw), base],
                       fill=col)
        for wy in range(3):
            for wx in range(2):
                draw.rectangle(
                    [x0 + w * (bx + 0.02 + wx * 0.05), base - h * bh + 8 + wy * 12,
                     x0 + w * (bx + 0.05 + wx * 0.05), base - h * bh + 14 + wy * 12],
                    fill=(250, 210, 120))
    # Kingdom Centre tower with its arch opening
    kx = x0 + w * 0.36
    draw.rectangle([kx, y0 + h * 0.18, kx + w * 0.20, base], fill=(45, 52, 80))
    draw.polygon([(kx + w * 0.05, y0 + h * 0.18), (kx + w * 0.10, y0 + h * 0.34),
                  (kx + w * 0.15, y0 + h * 0.18)], fill=(12, 18, 48))
    draw.rectangle([kx + w * 0.05, y0 + h * 0.18, kx + w * 0.15, y0 + h * 0.34],
                   fill=(45, 52, 80))
    draw.rectangle([kx + 6, y0 + h * 0.40, kx + w * 0.20 - 6, y0 + h * 0.44],
                   fill=(250, 210, 120))


def scene_hormuz(draw, box):
    """Dusk strait, two tankers burning, mine buoy, orange sky."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    sky_band(draw, box, (240, 150, 70), (250, 205, 130))
    draw.ellipse([x0 + w * 0.70, y0 + h * 0.10, x0 + w * 0.84, y0 + h * 0.30],
                 fill=(255, 230, 160))
    # sea
    draw.rectangle([x0, y0 + h * 0.58, x1, y1], fill=(30, 70, 110))
    for i in range(5):
        yy = y0 + h * (0.64 + i * 0.07)
        draw.line([x0 + w * 0.05, yy, x1 - w * 0.05, yy],
                  fill=(90, 140, 180), width=2)
    # tanker 1 (left), hull + deck, fire on deck
    tx, ty = x0 + w * 0.08, y0 + h * 0.52
    draw.rectangle([tx, ty, tx + w * 0.36, ty + h * 0.14], fill=(40, 40, 45))
    draw.rectangle([tx + w * 0.05, ty - h * 0.10, tx + w * 0.13, ty],
                   fill=(200, 200, 200))
    flame(draw, tx + w * 0.24, ty - h * 0.06, 10)
    flame(draw, tx + w * 0.30, ty - h * 0.02, 7)
    smoke(draw, tx + w * 0.26, ty - h * 0.24, 10, (70, 70, 75))
    # tanker 2 (right), listing, fire at bow
    tx2, ty2 = x0 + w * 0.58, y0 + h * 0.56
    draw.polygon([(tx2, ty2), (tx2 + w * 0.36, ty2 - h * 0.04),
                  (tx2 + w * 0.36, ty2 + h * 0.10), (tx2, ty2 + h * 0.14)],
                 fill=(60, 30, 30))
    flame(draw, tx2 + w * 0.30, ty2 - h * 0.08, 9)
    smoke(draw, tx2 + w * 0.30, ty2 - h * 0.26, 9, (70, 70, 75))
    # mine buoy with spikes
    mx, my = x0 + w * 0.48, y0 + h * 0.74
    draw.ellipse([mx - 8, my - 8, mx + 8, my + 8], fill=(25, 25, 25))
    for dx, dy in ((-1, -1), (1, -1), (-1, 1), (1, 1), (0, -1.4)):
        draw.line([mx, my, mx + dx * 13, my + dy * 13], fill=(25, 25, 25),
                  width=2)


def scene_g20(draw, box):
    """Johannesburg skyline at dawn, gold G20 emblem, flags."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    sky_band(draw, box, (250, 200, 110), (255, 235, 190))
    draw.ellipse([x0 + w * 0.42, y0 + h * 0.06, x0 + w * 0.58, y0 + h * 0.30],
                 fill=(255, 215, 90))
    # skyline
    base = y0 + h * 0.96
    for bx, bw, bh in ((0.00, 0.12, 0.42), (0.13, 0.10, 0.55),
                       (0.24, 0.12, 0.36), (0.62, 0.11, 0.48),
                       (0.74, 0.12, 0.38), (0.87, 0.13, 0.52)):
        draw.rectangle([x0 + w * bx, base - h * bh, x0 + w * (bx + bw), base],
                       fill=(70, 62, 90))
        for wy in range(3):
            draw.rectangle(
                [x0 + w * (bx + 0.03), base - h * bh + 8 + wy * 12,
                 x0 + w * (bx + 0.06), base - h * bh + 14 + wy * 12],
                fill=(255, 220, 130))
    # gold G20 emblem (centre)
    cx, cy, r = x0 + w * 0.50, y0 + h * 0.52, int(h * 0.30)
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(212, 175, 55),
                 outline=(140, 105, 20), width=3)
    draw.ellipse([cx - r + 5, cy - r + 5, cx + r - 5, cy + r - 5],
                 outline=(255, 235, 160), width=2)
    f = font(SANS_B, 26)
    tw = draw.textlength("G20", font=f)
    draw.text((cx - tw / 2, cy - 15), "G20", font=f, fill=(90, 65, 10))
    # small flags row along the bottom
    cols = [(0, 91, 187), (220, 20, 60), (0, 150, 80), (250, 200, 40),
            (120, 60, 160)]
    for i, col in enumerate(cols):
        fx = x0 + w * (0.10 + i * 0.16)
        draw.line([fx, base - h * 0.22, fx, base - h * 0.02], fill=(60, 50, 40),
                  width=2)
        draw.rectangle([fx, base - h * 0.22, fx + 20, base - h * 0.13],
                       fill=col)


def scene_icj(draw, box):
    """Courtroom: scales of justice, gavel, 9-6 verdict board."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    sky_band(draw, box, (200, 185, 160), (232, 222, 200))
    # wood panelling
    draw.rectangle([x0, y0 + h * 0.55, x1, y1], fill=(120, 85, 55))
    for i in range(6):
        draw.line([x0 + w * i / 5, y0 + h * 0.55, x0 + w * i / 5, y1],
                  fill=(95, 65, 40), width=2)
    # verdict board
    bx, by = x0 + w * 0.62, y0 + h * 0.10
    draw.rectangle([bx, by, bx + w * 0.32, by + h * 0.34], fill=(20, 38, 74))
    f = font(SANS_B, 26)
    tw = draw.textlength("9-6", font=f)
    draw.text((bx + (w * 0.32 - tw) / 2, by + 8), "9-6", font=f,
              fill=(255, 255, 255))
    # scales of justice
    cx, cy = x0 + w * 0.32, y0 + h * 0.42
    draw.line([cx, cy - h * 0.22, cx, cy + h * 0.30], fill=(180, 150, 60),
              width=4)
    draw.line([cx - w * 0.16, cy - h * 0.18, cx + w * 0.16, cy - h * 0.18],
              fill=(180, 150, 60), width=3)
    draw.ellipse([cx - 6, cy - h * 0.26, cx + 6, cy - h * 0.18],
                 fill=(200, 170, 70))
    for sx in (-w * 0.16, w * 0.16):
        draw.line([cx + sx, cy - h * 0.18, cx + sx, cy - h * 0.02],
                  fill=(150, 120, 50), width=2)
        draw.polygon([(cx + sx - 16, cy - h * 0.02), (cx + sx + 16, cy - h * 0.02),
                      (cx + sx, cy + h * 0.10)], fill=(200, 170, 70))
    draw.rectangle([cx - 20, cy + h * 0.30, cx + 20, cy + h * 0.36],
                   fill=(140, 105, 45))
    # gavel on the bench
    gx, gy = x0 + w * 0.70, y0 + h * 0.62
    draw.rectangle([gx, gy, gx + 44, gy + 12], fill=(110, 75, 45))
    draw.line([gx + 22, gy + 12, gx + 22, gy + 34], fill=(90, 60, 35), width=5)
    draw.ellipse([gx + 12, gy + 34, gx + 32, gy + 42], fill=(110, 75, 45))


def scene_indonesia(draw, box):
    """Candy factory at night, flames, smoke, fire engine lights."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    sky_band(draw, box, (20, 22, 50), (70, 60, 90))
    stars(draw, box, [(0.1, 0.1, 1), (0.4, 0.14, 2), (0.7, 0.08, 1),
                      (0.9, 0.18, 2)])
    # factory block
    fx, fy = x0 + w * 0.08, y0 + h * 0.42
    draw.rectangle([fx, fy, fx + w * 0.62, y0 + h * 0.92], fill=(120, 110, 100))
    draw.rectangle([fx, fy - h * 0.10, fx + w * 0.62, fy], fill=(90, 82, 74))
    for i in range(4):
        wx = fx + w * (0.06 + i * 0.14)
        draw.rectangle([wx, fy + h * 0.08, wx + w * 0.08, fy + h * 0.22],
                       fill=(250, 200, 90))
    # chimney
    draw.rectangle([fx + w * 0.66, fy - h * 0.28, fx + w * 0.74, y0 + h * 0.92],
                   fill=(100, 90, 82))
    smoke(draw, fx + w * 0.70, fy - h * 0.34, 12, (110, 108, 105))
    # flames bursting from the roof
    for i, s in enumerate((14, 11, 9)):
        flame(draw, fx + w * (0.22 + i * 0.14), fy - h * 0.06, s)
    # fire engine (small, bottom right)
    ex, ey = x0 + w * 0.74, y0 + h * 0.82
    draw.rectangle([ex, ey, ex + w * 0.22, ey + h * 0.10], fill=(200, 30, 30))
    draw.rectangle([ex + w * 0.16, ey - h * 0.06, ex + w * 0.22, ey],
                   fill=(200, 30, 30))
    draw.ellipse([ex + 6, ey + h * 0.10 - 4, ex + 14, ey + h * 0.10 + 4],
                 fill=(20, 20, 20))
    draw.ellipse([ex + w * 0.22 - 16, ey + h * 0.10 - 4,
                  ex + w * 0.22 - 8, ey + h * 0.10 + 4], fill=(20, 20, 20))
    draw.ellipse([ex + w * 0.09, ey - h * 0.05, ex + w * 0.09 + 8,
                  ey - h * 0.05 + 8], fill=(255, 220, 60))
    draw.rectangle([x0, y0 + h * 0.94, x1, y1], fill=(50, 48, 48))


def scene_markets(draw, box):
    """Red candlestick chart falling, big down arrow, ticker strip."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    draw.rectangle(box, fill=(18, 20, 28))
    # grid lines
    for i in range(4):
        yy = y0 + h * (0.15 + i * 0.2)
        draw.line([x0 + 8, yy, x1 - 8, yy], fill=(50, 55, 70), width=1)
    # falling red candles
    tops = [0.18, 0.22, 0.30, 0.28, 0.40, 0.46, 0.56, 0.62]
    for i, t in enumerate(tops):
        cx = x0 + w * (0.08 + i * 0.11)
        draw.line([cx, y0 + h * (t - 0.06), cx, y0 + h * (t + 0.20)],
                  fill=(230, 60, 50), width=2)
        draw.rectangle([cx - 7, y0 + h * t, cx + 7, y0 + h * (t + 0.14)],
                       fill=(230, 60, 50))
    # one green candle (brief bounce) then red again
    cx = x0 + w * (0.08 + 3 * 0.11)
    draw.rectangle([cx - 7, y0 + h * 0.28, cx + 7, y0 + h * 0.40],
                   fill=(60, 180, 90))
    # big down arrow
    ax, ay = x0 + w * 0.78, y0 + h * 0.30
    draw.polygon([(ax - 22, ay - 18), (ax + 22, ay - 18), (ax + 22, ay + 2),
                  (ax + 38, ay + 2), (ax, ay + 34), (ax - 38, ay + 2),
                  (ax - 22, ay + 2)], fill=(230, 60, 50))
    # ticker strip
    draw.rectangle([x0, y0 + h * 0.82, x1, y1], fill=(230, 60, 50))
    f = font(SANS_B, 13)
    draw.text((x0 + 8, y0 + h * 0.85), "S&P -3.7%   NASDAQ -5.3%",
              font=f, fill=(255, 255, 255))

# ================================================================ map
# Simplified world map: rough continent blobs, graticule, numbered pins.
# Coordinates are fractions of the map box (equirectangular-ish).


def scene_map(draw, box, pins):
    """Small labelled world map with numbered story pins."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    draw.rectangle(box, fill=(190, 215, 235))
    # graticule
    for i in range(1, 6):
        gx = x0 + w * i / 6
        draw.line([gx, y0, gx, y1], fill=(160, 190, 215), width=1)
    for i in range(1, 4):
        gy = y0 + h * i / 4
        draw.line([x0, gy, x1, gy], fill=(160, 190, 215), width=1)
    # continents as rough polygons (fractions of the box)
    land = (150, 165, 120)
    polys = [
        # North America
        [(0.06, 0.10), (0.20, 0.06), (0.30, 0.14), (0.28, 0.28),
         (0.18, 0.38), (0.08, 0.30)],
        # South America
        [(0.24, 0.44), (0.33, 0.42), (0.36, 0.58), (0.30, 0.78),
         (0.25, 0.62)],
        # Europe
        [(0.44, 0.12), (0.52, 0.08), (0.56, 0.18), (0.50, 0.24),
         (0.44, 0.20)],
        # Africa
        [(0.44, 0.34), (0.56, 0.32), (0.60, 0.50), (0.54, 0.72),
         (0.47, 0.58)],
        # Asia
        [(0.57, 0.08), (0.78, 0.06), (0.92, 0.14), (0.88, 0.30),
         (0.72, 0.34), (0.60, 0.26), (0.57, 0.18)],
        # Australia
        [(0.78, 0.66), (0.88, 0.64), (0.90, 0.76), (0.80, 0.78)],
    ]
    for poly in polys:
        pts = [(x0 + w * fx, y0 + h * fy) for fx, fy in poly]
        draw.polygon(pts, fill=land, outline=(120, 130, 95))
    # pins
    f = font(SANS_B, 10)
    for num, fx, fy in pins:
        px, py = x0 + w * fx, y0 + h * fy
        draw.ellipse([px - 8, py - 8, px + 8, py + 8], fill=RED,
                     outline=(255, 255, 255), width=2)
        tw = draw.textlength(str(num), font=f)
        draw.text((px - tw / 2, py - 7), str(num), font=f,
                  fill=(255, 255, 255))


# ================================================================ data
# (region chip, headline, fact, scene). Headlines fit two lines at
# 15px bold in a 243px panel; facts fit two lines at 11px.
PANELS = [
    ("EUROPE", "Russian missile crashes in Poland",
     "Kh-101 falls 50 km from border; Tusk calls it an \u201cintentional provocation\u201d.",
     scene_poland),
    ("CLIMATE", "COP31 deadlocked as EU rejects draft",
     "Deal omits fossil fuels; talks run 44 hours past deadline in Antalya.",
     scene_cop31),
    ("EUROPE", "France protests enter sixth weekend",
     "82,500 march by police count; turnout falls from 106,000 a week ago.",
     scene_france),
    ("AMERICAS", "Mexico captures \u201cEl Chapo Isidro\u201d",
     "Cartel boss seized in Sinaloa; 11 dead in raid and backlash; $5m reward.",
     scene_mexico),
    ("AMERICAS", "Supercell storm kills four in Brazil",
     "Tupancireta wrecked in 40 minutes: 162 hurt, ~8,000 homes damaged.",
     scene_brazil),
    ("AMERICAS", "Peru quake: 6.7 shakes Jun\u00edn region",
     "Tremors felt in Lima; no deaths reported, USGS says depth 108 km.",
     scene_peru),
    ("MID EAST", "Three missiles fired at Riyadh",
     "Coalition intercepts all three \u2014 second strike on capital in days.",
     scene_riyadh),
    ("MID EAST", "Three tankers hit near Hormuz",
     "Two struck by projectiles, third hits a mine and burns; no casualties.",
     scene_hormuz),
    ("AFRICA", "G20 opens in Johannesburg",
     "First G20 in Africa; leaders approve 122-point declaration at outset.",
     scene_g20),
    ("ASIA", "ICJ: Myanmar committed genocide",
     "World Court rules 9\u20136 over 2017 Rohingya killings; reparations ordered.",
     scene_icj),
    ("ASIA", "Factory fire kills 3 in Indonesia",
     "36 missing after blaze at Cikande candy factory in Banten.",
     scene_indonesia),
    ("MARKETS", "Markets rout in AI sell-off",
     "S&P 500 \u22123.7%, Nasdaq \u22125.3%; Nvidia sinks 14% on SEC-probe reports.",
     scene_markets),
]

NUMBERS = [
    ("600,000", "Kyiv army cap in the 28-point plan"),
    ("6.7", "Peru quake magnitude, Jun\u00edn"),
    ("122", "points in the G20 declaration"),
    ("8,000", "homes wrecked in Brazil storm"),
    ("10,000+", "Rohingya killed in 2017, ICJ finds"),
]

ALSO_ON = [
    "F1 Las Vegas: Verstappen on pole; Antonelli penalised",
    "Premier League: Leeds stun Chelsea 4\u20131 at the Bridge",
    "India v NZ: Pant 128 as India reach 629/6, lead 261",
    "Australia edge England in 1st T20 by three wickets",
    "UAE Bulls retain Abu Dhabi T10 title, beat Yas Lions",
    "Zverev beats Medvedev 7\u20136, 6\u20134 in ATP Finals semi",
    "Finland probes Russian helicopter incursion, 4.1 km",
    "Kryvyi Rih: boy, 7, and paramedic, 20, killed; 73 hurt",
    "Bahrain: defences intercept Iranian aerial attacks",
    "Basra power station fire kills 4, injures 30",
    "Nigeria boat disaster: 24 die as mourners\u2019 boat capsizes",
    "DR Congo Ebola fight hit by violence and distrust",
    "Tainted alcohol kills 11 in India\u2019s Manipur",
    "Tokyo protests demand Takaichi retract Taiwan remarks",
    "Denmark expels Russian diplomat over alleged murder plot",
    "BepiColombo probe enters orbit around Mercury",
]

MAP_PINS = [
    (1, 0.47, 0.14),   # Kyiv
    (2, 0.54, 0.26),   # Antalya
    (3, 0.59, 0.28),   # Riyadh
    (4, 0.67, 0.37),   # Hormuz
    (5, 0.52, 0.62),   # Johannesburg
    (6, 0.27, 0.58),   # Lima
    (7, 0.31, 0.68),   # Tupancireta
    (8, 0.12, 0.22),   # Las Vegas
]
MAP_KEY = ("1 Kyiv  2 Antalya  3 Riyadh  4 Hormuz",
           "5 Johannesburg  6 Lima  7 Tupancireta  8 Las Vegas")

LEAD_HEADLINE = "Trump: 28-point Ukraine plan \u201cnot my final offer\u201d"
LEAD_FACT = ("Zelensky spoke to Trump on Saturday; security teams meet in "
             "Geneva on Sunday. Deadline 27 Nov, flexible.")
LEAD_PLAN = ("THE 28-POINT PLAN: 600,000-troop cap \u00b7 No NATO \u00b7 "
             "Cede Donbas, freeze lines")


# ================================================================ build
def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- masthead (navy band, huge date) ----
    d.rectangle([0, 0, W, 118], fill=NAVY)
    d.rectangle([0, 114, W, 118], fill=GOLD)
    f_name = font(SERIF_B, 25)
    name = "THE WORLD TODAY"
    tw = d.textlength(name, font=f_name)
    d.text(((W - tw) / 2, 8), name, font=f_name, fill=GOLD)
    f_date = font(SERIF_B, 44)
    date = "SUNDAY 22 NOVEMBER 2026"
    tw = d.textlength(date, font=f_date)
    d.text(((W - tw) / 2, 38), date, font=f_date, fill=(255, 255, 255))
    f_sub = font(SANS_O, 13)
    sub = "Gulf strikes  \u00b7  Peru quake  \u00b7  COP31 deadlocked  \u00b7  G20 opens in Africa"
    tw = d.textlength(sub, font=f_sub)
    d.text(((W - tw) / 2, 92), sub, font=f_sub, fill=(210, 215, 230))

    # ---- big-numbers strip ----
    d.rectangle([0, 118, W, 166], fill=CREAM)
    d.line([0, 166, W, 166], fill=BORDER, width=1)
    cell = W / 5
    f_num = font(SANS_B, 28)
    f_lab = font(SANS, 10)
    for i, (num, lab) in enumerate(NUMBERS):
        cx = cell * i + cell / 2
        tw = d.textlength(num, font=f_num)
        d.text((cx - tw / 2, 124), num, font=f_num, fill=RED)
        tw = d.textlength(lab, font=f_lab)
        d.text((cx - tw / 2, 154), lab, font=f_lab, fill=GREY)
        if i:
            d.line([cell * i, 124, cell * i, 162], fill=LIGHTGREY, width=1)

    # ---- lead story ----
    ly0, ly1 = 176, 356
    d.rectangle([14, ly0, 1010, ly1], fill=PANEL, outline=BORDER, width=1)
    scene_geneva(d, (15, ly0 + 1, 640, ly1 - 1))
    d.line([640, ly0, 640, ly1], fill=BORDER, width=1)
    tx = 656
    f_kick = font(SANS_B, 11)
    d.text((tx, ly0 + 10), "LEAD \u2014 GENEVA PEACE TALKS", font=f_kick,
           fill=RED)
    f_head = font(SANS_B, 21)
    y = text_block(d, tx, ly0 + 30,
                   wrap(d, LEAD_HEADLINE, f_head, 1010 - tx - 12),
                   f_head, INK, leading=25)
    f_fact = font(SANS, 12)
    y = text_block(d, tx, y + 6,
                   wrap(d, LEAD_FACT, f_fact, 1010 - tx - 12),
                   f_fact, INK, leading=16)
    # plan box
    py = y + 10
    d.rounded_rectangle([tx, py, 1010 - 12, ly1 - 10], radius=4,
                        fill=(240, 232, 210), outline=BORDER)
    f_plan = font(SANS_B, 11)
    text_block(d, tx + 8, py + 7,
               wrap(d, LEAD_PLAN, f_plan, 1010 - tx - 28),
               f_plan, NAVY, leading=15)

    # ---- 12-panel grid: 4 columns x 3 rows ----
    gy0 = 366
    col_w, row_h, gut = 243, 168, 8
    f_head2 = font(SANS_B, 15)
    f_fact2 = font(SANS, 11)
    for idx, (tag, head, fact, scene) in enumerate(PANELS):
        r, c = divmod(idx, 4)
        x0 = 14 + c * (col_w + gut)
        y0 = gy0 + r * (row_h + gut)
        x1, y1 = x0 + col_w, y0 + row_h
        d.rectangle([x0, y0, x1, y1], fill=PANEL, outline=BORDER, width=1)
        scene(d, (x0 + 1, y0 + 1, x1 - 1, y0 + 97))
        tag_chip(d, x0 + 5, y0 + 5, tag,
                 fill=RED if tag in ("MID EAST", "MARKETS") else NAVY)
        text_block(d, x0 + 6, y0 + 102,
                   wrap(d, head, f_head2, col_w - 12), f_head2, INK,
                   leading=18)
        text_block(d, x0 + 6, y0 + 140,
                   wrap(d, fact, f_fact2, col_w - 12), f_fact2, GREY,
                   leading=13)

    # ---- bottom band: also-on list + map ----
    by0 = 886
    d.line([0, by0, W, by0], fill=BORDER, width=2)
    f_sec = font(SANS_B, 13)
    d.text((14, by0 + 6), "ALSO ON \u2014 16 MORE STORIES, 22 NOVEMBER",
           font=f_sec, fill=NAVY)
    d.text((700, by0 + 6), "WHERE IT HAPPENED", font=f_sec, fill=NAVY)
    f_item = font(SANS, 11)
    col2_x = 362
    for i, item in enumerate(ALSO_ON):
        col = 0 if i < 8 else 1
        row = i if i < 8 else i - 8
        x = 14 if col == 0 else col2_x
        y = by0 + 26 + row * 12
        d.text((x, y), "\u2022  " + item, font=f_item, fill=INK)
    scene_map(d, (700, by0 + 26, 1010, 960), MAP_PINS)
    f_key = font(SANS, 9)
    yk = 964
    for line in MAP_KEY:
        d.text((700, yk), line, font=f_key, fill=GREY)
        yk += 12
    # footer sources line
    f_src = font(SANS, 9)
    d.text((14, 1012),
           "Sources: Reuters \u00b7 AP \u00b7 AFP \u00b7 BBC \u00b7 CNN \u00b7 Al Jazeera \u00b7 "
           "The Times \u00b7 Xinhua \u00b7 Gulf News \u00b7 Manila Times \u2014 all stories "
           "reported 21\u201322 Nov 2026. Drawn scenes; no photographs.",
           font=f_src, fill=GREY)
    return img


def main():
    img = build()
    os.makedirs(OUT_DIR, exist_ok=True)
    img.save(OUT_PATH, format="PNG")
    os.chmod(OUT_PATH, 0o644)
    size = os.path.getsize(OUT_PATH)
    print(f"wrote {OUT_PATH} ({size} bytes, {W}x{H})")
    if size > 1048576:
        print("ERROR: entry.png exceeds the 1 MiB cap", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
