#!/usr/bin/env python3
"""Render the 22 November 2026 world-news front page (v3) as a 1024x1024 PNG.

Original code written for the make.fun news-image-20261122 bounty, v3 rebuild.
Density leap over v2 (10 stories): 42 stories on the page — lead + 33
column stories + 8 one-line briefs — with a drawn world map (12 numbered
story markers), a Geneva flag row, drawn glyphs (storm, seismograph,
scales of justice, football, tanker, globe, $5M badge) and a markets bar
chart. Every headline and fact was verified against published reports
(see stories-v3.md in the work directory). No network access at render time.
Deterministic: the same input always writes the same bytes.
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 36
CONTENT_W = W - 2 * MARGIN          # 952
X0, X1 = MARGIN, W - MARGIN

PAPER = (250, 246, 236)   # warm newsprint
INK = (18, 18, 18)
RED = (158, 28, 28)       # section-label red
GREY = (96, 92, 84)
RULE = (58, 56, 50)
BAR_RED = (178, 34, 34)
BOX_BG = (244, 238, 226)
SEA = (211, 226, 236)     # pale blue sea for the map panel
LAND = (233, 221, 197)    # tan land
LAND_LINE = (120, 110, 88)

FONT_DIR = "/usr/share/fonts/truetype"
SERIF_B = os.path.join(FONT_DIR, "liberation", "LiberationSerif-Bold.ttf")
SERIF_I = os.path.join(FONT_DIR, "liberation", "LiberationSerif-Italic.ttf")
SANS = os.path.join(FONT_DIR, "noto", "NotoSans-Regular.ttf")
SANS_B = os.path.join(FONT_DIR, "noto", "NotoSans-Bold.ttf")


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_width):
    """Greedy word wrap; returns a list of lines that all fit max_width."""
    lines, cur = [], ""
    for word in text.split():
        trial = word if not cur else cur + " " + word
        if draw.textlength(trial, font=fnt) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_lines(draw, lines, fnt, x, y, fill, leading):
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def rule(draw, x0, y, x1, width=2):
    draw.line([(x0, y), (x1, y)], fill=RULE, width=width)


def flag_border(d, x, y, w, h):
    d.rectangle([x, y, x + w - 1, y + h - 1], outline=(90, 86, 78), width=1)


def flag_ukraine(d, x, y, w=30, h=20):
    d.rectangle([x, y, x + w - 1, y + h // 2 - 1], fill=(0, 91, 187))
    d.rectangle([x, y + h // 2, x + w - 1, y + h - 1], fill=(255, 213, 0))
    flag_border(d, x, y, w, h)


def flag_poland(d, x, y, w=30, h=20):
    d.rectangle([x, y, x + w - 1, y + h // 2 - 1], fill=(255, 255, 255))
    d.rectangle([x, y + h // 2, x + w - 1, y + h - 1], fill=(220, 20, 60))
    flag_border(d, x, y, w, h)


def flag_france(d, x, y, w=30, h=20):
    d.rectangle([x, y, x + w // 3 - 1, y + h - 1], fill=(0, 85, 164))
    d.rectangle([x + w // 3, y, x + 2 * w // 3 - 1, y + h - 1],
                fill=(255, 255, 255))
    d.rectangle([x + 2 * w // 3, y, x + w - 1, y + h - 1], fill=(239, 65, 53))
    flag_border(d, x, y, w, h)


def flag_nigeria(d, x, y, w=30, h=20):
    d.rectangle([x, y, x + w // 3 - 1, y + h - 1], fill=(0, 135, 81))
    d.rectangle([x + w // 3, y, x + 2 * w // 3 - 1, y + h - 1],
                fill=(255, 255, 255))
    d.rectangle([x + 2 * w // 3, y, x + w - 1, y + h - 1], fill=(0, 135, 81))
    flag_border(d, x, y, w, h)


def flag_germany(d, x, y, w=24, h=16):
    d.rectangle([x, y, x + w - 1, y + h // 3 - 1], fill=(0, 0, 0))
    d.rectangle([x, y + h // 3, x + w - 1, y + 2 * h // 3 - 1],
                fill=(221, 0, 0))
    d.rectangle([x, y + 2 * h // 3, x + w - 1, y + h - 1],
                fill=(255, 206, 0))
    flag_border(d, x, y, w, h)


def flag_usa(d, x, y, w=24, h=16):
    # Simplified Stars and Stripes: 7 stripes + blue canton.
    for i in range(7):
        col = (179, 25, 66) if i % 2 == 0 else (255, 255, 255)
        y0 = y + i * h // 7
        y1 = y + (i + 1) * h // 7 - 1
        d.rectangle([x, y0, x + w - 1, y1], fill=col)
    d.rectangle([x, y, x + 9, y + 8], fill=(10, 49, 97))
    d.ellipse([x + 4, y + 3, x + 6, y + 5], fill=(255, 255, 255))
    flag_border(d, x, y, w, h)


def flag_uk(d, x, y, w=24, h=16):
    # Simplified Union Jack: blue field, white saltire, red cross.
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=(0, 36, 125))
    d.line([(x, y), (x + w - 1, y + h - 1)], fill=(255, 255, 255), width=3)
    d.line([(x + w - 1, y), (x, y + h - 1)], fill=(255, 255, 255), width=3)
    d.rectangle([x + w // 2 - 2, y, x + w // 2 + 1, y + h - 1],
                fill=(200, 16, 46))
    d.rectangle([x, y + h // 2 - 2, x + w - 1, y + h // 2 + 1],
                fill=(200, 16, 46))
    flag_border(d, x, y, w, h)


def star_points(cx, cy, r_out, r_in):
    pts = []
    for i in range(10):
        r = r_out if i % 2 == 0 else r_in
        a = -math.pi / 2 + i * math.pi / 5
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def flag_turkiye(d, x, y, w=30, h=20):
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=(227, 10, 23))
    cx, cy = x + 11, y + 10
    d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=(255, 255, 255))
    d.ellipse([cx - 4, cy - 5, cx + 7, cy + 5], fill=(227, 10, 23))
    d.polygon(star_points(x + 21, y + 10, 4.5, 1.8), fill=(255, 255, 255))
    flag_border(d, x, y, w, h)


def tanker_glyph(d, x, y):
    """Tiny oil-tanker silhouette, 30x20."""
    d.polygon([(x, y + 12), (x + 28, y + 12), (x + 24, y + 19), (x + 3, y + 19)],
              fill=INK)
    d.rectangle([x + 4, y + 4, x + 14, y + 12], fill=INK)
    d.rectangle([x + 20, y + 2, x + 24, y + 12], fill=RED)


def storm_glyph(d, x, y):
    """Storm cloud with a lightning bolt, 30x20."""
    d.ellipse([x + 1, y + 2, x + 13, y + 12], fill=(90, 90, 92))
    d.ellipse([x + 8, y, x + 22, y + 11], fill=(110, 110, 114))
    d.ellipse([x + 16, y + 4, x + 29, y + 13], fill=(90, 90, 92))
    d.rectangle([x + 1, y + 8, x + 29, y + 13], fill=(100, 100, 103))
    d.polygon([(x + 17, y + 12), (x + 12, y + 20), (x + 16, y + 20),
               (x + 13, y + 20), (x + 19, y + 12)], fill=(255, 200, 0))


def seismo_glyph(d, x, y):
    """Seismograph squiggle, 30x20."""
    pts = [(x, y + 10), (x + 5, y + 10), (x + 7, y + 4), (x + 9, y + 16),
           (x + 11, y + 10), (x + 14, y + 10), (x + 16, y + 2),
           (x + 18, y + 18), (x + 20, y + 10), (x + 24, y + 10),
           (x + 26, y + 6), (x + 28, y + 14), (x + 30, y + 10)]
    d.line(pts, fill=RED, width=2)


def scales_glyph(d, x, y):
    """Scales of justice, 30x20."""
    d.line([(x + 15, y + 1), (x + 15, y + 19)], fill=INK, width=2)
    d.line([(x + 3, y + 4), (x + 27, y + 4)], fill=INK, width=2)
    d.line([(x + 3, y + 4), (x + 1, y + 13)], fill=INK, width=1)
    d.line([(x + 3, y + 4), (x + 5, y + 13)], fill=INK, width=1)
    d.line([(x + 1, y + 13), (x + 5, y + 13)], fill=INK, width=1)
    d.line([(x + 27, y + 4), (x + 25, y + 13)], fill=INK, width=1)
    d.line([(x + 27, y + 4), (x + 29, y + 13)], fill=INK, width=1)
    d.line([(x + 25, y + 13), (x + 29, y + 13)], fill=INK, width=1)
    d.line([(x + 8, y + 19), (x + 22, y + 19)], fill=INK, width=2)


def football_glyph(d, x, y):
    """Football: white ball, black patches, 30x20 (drawn as a circle)."""
    d.ellipse([x + 5, y, x + 25, y + 20], outline=INK, width=2,
              fill=(255, 255, 255))
    d.polygon(star_points(x + 15, y + 10, 5, 2), fill=INK)
    for px, py in [(x + 8, y + 4), (x + 22, y + 4), (x + 15, y + 17)]:
        d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=INK)


def globe_glyph(d, x, y):
    """Globe: circle with meridians, 30x20."""
    d.ellipse([x + 5, y, x + 25, y + 20], outline=INK, width=2)
    d.ellipse([x + 12, y, x + 18, y + 20], outline=INK, width=1)
    d.line([(x + 5, y + 10), (x + 25, y + 10)], fill=INK, width=1)
    d.arc([x + 5, y - 6, x + 25, y + 10], 200, 340, fill=INK, width=1)
    d.arc([x + 5, y + 10, x + 25, y + 26], 20, 160, fill=INK, width=1)


def missile_glyph(d, x, y):
    """Small missile on a diagonal, 30x20."""
    d.polygon([(x + 26, y + 2), (x + 29, y + 5), (x + 20, y + 10),
               (x + 17, y + 7)], fill=RED)
    d.polygon([(x + 17, y + 7), (x + 20, y + 10), (x + 8, y + 16),
               (x + 5, y + 13)], fill=INK)
    d.polygon([(x + 8, y + 16), (x + 5, y + 13), (x + 2, y + 18),
               (x + 6, y + 19)], fill=(255, 140, 0))
    d.line([(x + 12, y + 12), (x + 16, y + 8)], fill=INK, width=2)


def reward_badge(d, x, y):
    """Small '$5M REWARD' tag, 30x20 row height."""
    f = font(SANS_B, 11)
    txt = "$5M REWARD"
    tw = d.textlength(txt, font=f)
    d.rectangle([x, y, x + tw + 10, y + 19], outline=RED, width=1)
    d.text((x + 5, y + 3), txt, font=f, fill=RED)
    return tw + 10


GLYPHS = {
    "ukraine": flag_ukraine, "poland": flag_poland,
    "france": flag_france, "nigeria": flag_nigeria,
    "turkiye": flag_turkiye, "tanker": tanker_glyph,
    "storm": storm_glyph, "seismo": seismo_glyph,
    "scales": scales_glyph, "football": football_glyph,
    "globe": globe_glyph, "missile": missile_glyph,
}


def draw_glyph(d, name, x, y):
    if name == "badge":
        return reward_badge(d, x, y)
    GLYPHS[name](d, x, y)
    return 30


# ---------------------------------------------------------------- map
# Simplified continent outlines as (lon, lat) points, equirectangular.
NORTH_AMERICA = [(-168, 66), (-150, 70), (-135, 69), (-125, 71), (-115, 73),
                 (-105, 72), (-95, 80), (-85, 80), (-80, 73), (-75, 72),
                 (-70, 68), (-65, 60), (-60, 52), (-55, 47), (-60, 44),
                 (-65, 44), (-70, 42), (-74, 39), (-76, 35), (-80, 32),
                 (-81, 26), (-84, 30), (-89, 29), (-91, 21), (-94, 17),
                 (-97, 16), (-100, 18), (-105, 20), (-110, 23), (-114, 28),
                 (-117, 33), (-122, 37), (-124, 42), (-124, 48), (-128, 52),
                 (-135, 58), (-145, 60), (-155, 58), (-162, 58), (-168, 66)]
GREENLAND = [(-55, 60), (-45, 60), (-40, 64), (-42, 70), (-50, 74),
             (-58, 76), (-65, 76), (-60, 70), (-55, 60)]
SOUTH_AMERICA = [(-79, 9), (-77, 7), (-72, 11), (-64, 10), (-60, 8),
                 (-54, 6), (-51, 4), (-50, 0), (-44, -3), (-38, -5),
                 (-35, -8), (-37, -13), (-39, -18), (-41, -23), (-48, -27),
                 (-52, -32), (-57, -38), (-62, -41), (-65, -45), (-68, -50),
                 (-70, -54), (-73, -53), (-72, -48), (-72, -40), (-71, -30),
                 (-70, -20), (-75, -15), (-79, -8), (-81, -4), (-80, 2),
                 (-79, 9)]
AFRICA = [(-17, 15), (-16, 21), (-10, 29), (-6, 33), (-2, 35), (3, 37),
          (10, 37), (11, 34), (15, 32), (20, 32), (25, 32), (30, 31),
          (32, 31), (34, 28), (36, 24), (38, 20), (39, 15), (41, 11),
          (44, 11), (48, 11), (51, 12), (48, 5), (44, 0), (41, -5),
          (40, -10), (38, -15), (36, -18), (34, -22), (32, -26), (28, -30),
          (26, -34), (20, -35), (17, -32), (15, -27), (13, -22), (12, -18),
          (12, -12), (10, -6), (9, -1), (9, 4), (4, 6), (-2, 5), (-8, 5),
          (-13, 8), (-17, 12), (-17, 15)]
EURASIA = [(-10, 36), (-9, 38), (-9, 43), (-4, 44), (-2, 47), (-4, 48),
           (-1, 49), (2, 51), (4, 53), (7, 54), (8, 57), (10, 59),
           (12, 58), (18, 56), (21, 55), (24, 58), (26, 59), (28, 60),
           (30, 62), (30, 66), (32, 70), (36, 68), (40, 67), (44, 68),
           (48, 69), (52, 69), (56, 69), (60, 69), (64, 70), (68, 71),
           (72, 72), (76, 73), (80, 73), (85, 74), (90, 75), (95, 76),
           (100, 76), (105, 76), (110, 74), (115, 73), (120, 73), (125, 72),
           (130, 71), (135, 71), (140, 72), (145, 72), (150, 71), (155, 70),
           (160, 70), (165, 69), (170, 67), (175, 65), (178, 64), (175, 62),
           (170, 60), (165, 60), (162, 56), (160, 53), (158, 50), (156, 52),
           (152, 56), (150, 59), (145, 59), (142, 55), (141, 50), (140, 45),
           (138, 43), (135, 42), (132, 43), (130, 42), (128, 38), (126, 38),
           (124, 40), (122, 38), (121, 34), (120, 30), (118, 26), (116, 23),
           (114, 22), (111, 21), (109, 18), (108, 13), (106, 10), (104, 9),
           (101, 7), (100, 9), (99, 12), (98, 14), (96, 16), (94, 17),
           (92, 21), (90, 22), (88, 22), (86, 20), (84, 19), (82, 16),
           (80, 13), (79, 9), (77, 8), (76, 10), (74, 14), (72, 20),
           (70, 21), (68, 22), (66, 25), (64, 25), (62, 25), (60, 25),
           (58, 26), (56, 26), (54, 26), (52, 27), (50, 29), (49, 30),
           (47, 30), (44, 29), (42, 29), (40, 31), (38, 33), (36, 36),
           (34, 36), (32, 36), (30, 36), (28, 37), (26, 38), (24, 37),
           (22, 37), (20, 39), (18, 40), (16, 41), (14, 42), (12, 44),
           (10, 44), (8, 44), (6, 43), (4, 43), (2, 42), (0, 40),
           (-2, 37), (-4, 36), (-6, 36), (-9, 37), (-10, 36)]
UNITED_KINGDOM = [(-5, 50), (-3, 50), (-2, 52), (0, 53), (-1, 55),
                   (-3, 57), (-5, 58), (-6, 56), (-5, 50)]
JAPAN = [(130, 31), (132, 33), (134, 34), (136, 35), (138, 35), (140, 36),
         (141, 39), (141, 41), (140, 44), (138, 44), (136, 42), (133, 38),
         (131, 34), (130, 31)]
AUSTRALIA = [(113, -22), (114, -26), (115, -32), (116, -35), (119, -34),
             (122, -34), (124, -33), (127, -32), (130, -32), (132, -32),
             (134, -33), (136, -35), (138, -35), (140, -37), (142, -38),
             (145, -38), (147, -39), (150, -37), (152, -35), (153, -32),
             (153, -28), (152, -25), (150, -22), (148, -20), (146, -19),
             (144, -16), (142, -14), (142, -11), (140, -10), (138, -12),
             (136, -12), (134, -12), (132, -11), (130, -12), (128, -14),
             (126, -14), (124, -16), (122, -17), (120, -19), (118, -20),
             (116, -21), (113, -22)]
NEW_ZEALAND = [(167, -45), (169, -43), (171, -42), (173, -41), (175, -38),
               (177, -38), (178, -37), (176, -40), (174, -41), (172, -43),
               (170, -44), (168, -46), (167, -45)]
CONTINENTS = [NORTH_AMERICA, GREENLAND, SOUTH_AMERICA, AFRICA, EURASIA,
              UNITED_KINGDOM, JAPAN, AUSTRALIA, NEW_ZEALAND]
REGION_LABELS = [("NORTH AMERICA", -100, 56), ("SOUTH AMERICA", -70, -12),
                 ("EUROPE", 25, 62), ("AFRICA", 18, -4), ("ASIA", 95, 56),
                 ("AUSTRALIA", 134, -27)]
# (number, lon, lat, caption name) — Antalya nudged so its dot clears Kyiv.
MARKERS = [(1, 30.5, 50.4, "Kyiv"), (2, 21.0, 52.2, "Warsaw"),
           (3, 34.0, 33.0, "Antalya"), (4, 46.7, 24.7, "Riyadh"),
           (5, 28.0, -26.2, "Johannesburg"), (6, 92.0, 21.4, "Cox's Bazar"),
           (7, -53.8, -29.0, "Tupancireta"), (8, -77.0, -12.0, "Lima"),
           (9, 6.3, 4.9, "Bayelsa"), (10, -174.8, -41.3, "Wellington"),
           (11, 139.7, 35.7, "Tokyo"), (12, -115.1, 36.2, "Las Vegas")]

# ---------------------------------------------------------------- layout
LEAD_BOTTOM = 308
MAP_TOP, MAP_BOTTOM = 348, 448
COL_TOP, COL_BOTTOM = 464, 868
BRIEF_Y = 876
NUM_Y = 916
FOOT_Y = 948


def mixed_wrap(draw, words, max_width):
    """Greedy wrap over (word, font) pairs; returns list of word lists."""
    lines, cur, cur_w = [], [], 0
    space_w = draw.textlength(" ", font=font(SANS, 12))
    for word, fnt in words:
        ww = draw.textlength(word, font=fnt)
        add = ww if not cur else space_w + ww
        if cur_w + add <= max_width:
            cur.append((word, fnt))
            cur_w += add
        else:
            if cur:
                lines.append(cur)
            cur, cur_w = [(word, fnt)], ww
    if cur:
        lines.append(cur)
    return lines


def draw_mixed(draw, lines, x, y, leading):
    for line in lines:
        cx = x
        for i, (word, fnt) in enumerate(line):
            if i:
                cx += draw.textlength(" ", font=fnt)
            draw.text((cx, y), word, font=fnt, fill=INK)
            cx += draw.textlength(word, font=fnt)
        y += leading
    return y


def draw_featured(d, cx, cy, item, cell_w):
    """Featured story: glyph + label, serif headline, sans fact.

    Returns the y just below the item (before the gap)."""
    f_label = font(SANS_B, 11)
    f_head = font(SERIF_B, 15)
    f_fact = font(SANS, 12)
    glyph_w = draw_glyph(d, item["glyph"], cx, cy + 1)
    d.text((cx + glyph_w + 8, cy + 3), item["label"], font=f_label, fill=RED)
    cy += 22
    head_lines = wrap(d, item["head"], f_head, cell_w)
    assert len(head_lines) <= 2, "headline too long: %r" % head_lines
    cy = draw_lines(d, head_lines, f_head, cx, cy, INK, 16)
    cy += 2
    fact_lines = wrap(d, item["fact"], f_fact, cell_w)
    assert len(fact_lines) <= 2, "fact too long: %r" % fact_lines
    cy = draw_lines(d, fact_lines, f_fact, cx, cy, (52, 50, 46), 14)
    return cy


def draw_brief(d, cx, cy, item, cell_w):
    """One brief: bold headline + regular fact in a single 2-line paragraph."""
    words = [(w, font(SANS_B, 12)) for w in item["head"].split()]
    words.append(("\u2014", font(SANS_B, 12)))
    words += [(w, font(SANS, 12)) for w in item["fact"].split()]
    lines = mixed_wrap(d, words, cell_w)
    assert len(lines) <= 2, "brief too long: %r" % item
    return draw_mixed(d, lines, cx, cy, 14)


def draw_chart_item(d, cx, cy, cell_w):
    """Markets cell: label + headline + 4-bar chart. Returns y below."""
    f_label = font(SANS_B, 11)
    f_head = font(SERIF_B, 15)
    d.text((cx, cy), "MARKETS", font=f_label, fill=RED)
    cy += 16
    head_lines = wrap(d, "AI rout: Nvidia \u221214%, S&P in correction",
                      f_head, cell_w)
    assert len(head_lines) <= 2, "chart headline too long"
    cy = draw_lines(d, head_lines, f_head, cx, cy, INK, 16)
    cy += 3
    f_lab = font(SANS_B, 12)
    bars = [("S&P 500", 3.7), ("Nasdaq", 5.3), ("Dow", 1.9), ("Nikkei", 5.1)]
    bar_x = cx + 64
    bar_max = cell_w - 64 - 46
    for name, drop in bars:
        d.text((cx, cy), name, font=f_lab, fill=INK)
        bw = int(bar_max * drop / 5.3)
        d.rectangle([bar_x, cy + 1, bar_x + bw, cy + 11], fill=BAR_RED)
        d.text((bar_x + bar_max + 5, cy), "-%s%%" % drop, font=f_lab,
               fill=BAR_RED)
        cy += 14
    return cy


def draw_map(d, x0, y0, x1, y1):
    """Stylised world map: pale sea, tan continents, numbered markers."""
    d.rectangle([x0, y0, x1, y1], fill=SEA)
    lat_top, lat_bot = 80.0, -55.0

    def proj(lon, lat):
        px = x0 + (lon + 180.0) / 360.0 * (x1 - x0)
        py = y0 + (lat_top - lat) / (lat_top - lat_bot) * (y1 - y0)
        return px, py

    for poly in CONTINENTS:
        pts = [proj(lon, lat) for lon, lat in poly]
        d.polygon(pts, fill=LAND, outline=LAND_LINE)
    f_reg = font(SANS_B, 9)
    for name, lon, lat in REGION_LABELS:
        px, py = proj(lon, lat)
        tw = d.textlength(name, font=f_reg)
        d.text((px - tw / 2, py - 5), name, font=f_reg, fill=(110, 106, 96))
    f_num = font(SANS_B, 9)
    for num, lon, lat, _name in MARKERS:
        px, py = proj(lon, lat)
        d.ellipse([px - 6, py - 6, px + 6, py + 6], fill=RED,
                  outline=(255, 255, 255), width=1)
        txt = str(num)
        tw = d.textlength(txt, font=f_num)
        d.text((px - tw / 2, py - 5), txt, font=f_num, fill=(255, 255, 255))
    d.rectangle([x0, y0, x1, y1], outline=RULE, width=1)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- dateline bar -------------------------------------------------
    f_date = font(SANS_B, 18)
    d.text((X0, 18), "SUNDAY, 22 NOVEMBER 2026", font=f_date, fill=INK)
    right = "THE WORLD IN ONE PAGE"
    d.text((X1 - d.textlength(right, font=f_date), 18), right,
           font=f_date, fill=INK)
    rule(d, X0, 46, X1, 3)

    # ---- masthead ------------------------------------------------------
    f_mast = font(SERIF_B, 58)
    title = "THE WORLD TODAY"
    tw = d.textlength(title, font=f_mast)
    d.text(((W - tw) / 2, 48), title, font=f_mast, fill=INK)
    f_sub = font(SERIF_I, 18)
    sub = ("42 stories that sum up the day \u2014 every fact checked "
           "against published reports")
    sw = d.textlength(sub, font=f_sub)
    d.text(((W - sw) / 2, 110), sub, font=f_sub, fill=GREY)
    rule(d, X0, 132, X1, 3)
    rule(d, X0, 137, X1, 1)

    # ---- lead story ----------------------------------------------------
    lead_w = 620
    box_x0, box_x1 = X0 + lead_w + 24, X1
    y = 146
    flag_ukraine(d, X0, y + 1)
    f_lead_label = font(SANS_B, 16)
    d.text((X0 + 38, y + 2), "LEAD  \u00b7  UKRAINE PEACE TALKS",
           font=f_lead_label, fill=RED)
    y += 26
    f_lead_head = font(SERIF_B, 34)
    lead_head_lines = ["Trump: 28-point Ukraine plan",
                       "\u201cnot my final offer\u201d"]
    for line in lead_head_lines:
        assert d.textlength(line, font=f_lead_head) <= lead_w, \
            "lead headline line too long: %r" % line
    y = draw_lines(d, lead_head_lines, f_lead_head, X0, y, INK, 40)
    y += 6
    f_lead_fact = font(SANS, 15)
    lead_fact = ("Zelensky spoke to Trump on Saturday; talks move to Geneva "
                 "on Sunday. Army capped at 600,000; no NATO membership.")
    fact_lines = wrap(d, lead_fact, f_lead_fact, lead_w)
    assert len(fact_lines) <= 2, "lead fact too long: %r" % fact_lines
    y = draw_lines(d, fact_lines, f_lead_fact, X0, y, INK, 20)
    assert y <= LEAD_BOTTOM, "lead block overflows: y=%d" % y

    # ---- plan-in-brief box --------------------------------------------
    d.rectangle([box_x0, 146, box_x1, LEAD_BOTTOM], fill=BOX_BG,
                outline=RULE, width=1)
    bx, by = box_x0 + 12, 154
    f_box_title = font(SANS_B, 14)
    d.text((bx, by), "THE PLAN IN BRIEF", font=f_box_title, fill=RED)
    by += 22
    rule(d, bx, by, box_x1 - 12, 1)
    by += 8
    f_box = font(SANS, 14)
    box_items = [
        "Army capped at 600,000 troops",
        "No NATO membership for Kyiv",
        "Cede the Donbas; freeze the front lines",
        "G20 backs draft; borders \u201cnot by force\u201d",
    ]
    for item in box_items:
        lines = wrap(d, item, f_box, box_x1 - box_x0 - 36)
        assert len(lines) <= 2, "plan box item too long: %r" % lines
        for li, line in enumerate(lines):
            if li == 0:
                d.rectangle([bx, by + 5, bx + 6, by + 11], fill=RED)
            d.text((bx + 12, by), line, font=f_box, fill=INK)
            by += 18
        by += 3
    assert by <= LEAD_BOTTOM - 4, "plan box overflows: y=%d" % by

    rule(d, X0, 312, X1, 1)

    # ---- Geneva flag strip --------------------------------------------
    strip_label = "GENEVA TALKS  \u00b7  MON 23 NOV"
    f_strip = font(SANS_B, 12)
    lw = d.textlength(strip_label, font=f_strip)
    flags = [flag_usa, flag_ukraine, flag_uk, flag_france, flag_germany]
    fw, gap = 24, 10
    total = lw + 14 + len(flags) * fw + (len(flags) - 1) * gap
    sx = (W - total) / 2
    sy = 316
    d.text((sx, sy + 1), strip_label, font=f_strip, fill=INK)
    fx = sx + lw + 14
    for fl in flags:
        fl(d, fx, sy, fw, 16)
        fx += fw + gap

    # ---- world map band -------------------------------------------------
    f_map_title = font(SANS_B, 12)
    d.text((X0, 336), "THE DAY ON THE MAP  \u2014  12 STORIES, ONE PLANET",
           font=f_map_title, fill=RED)
    draw_map(d, X0, MAP_TOP, X1, MAP_BOTTOM)
    f_cap = font(SANS, 11)
    cap = ("1 Kyiv  \u00b7  2 Warsaw  \u00b7  3 Antalya  \u00b7  4 Riyadh  "
           "\u00b7  5 Johannesburg  \u00b7  6 Cox\u2019s Bazar  \u00b7  "
           "7 Tupancireta  \u00b7  8 Lima  \u00b7  9 Bayelsa  \u00b7  "
           "10 Wellington  \u00b7  11 Tokyo  \u00b7  12 Las Vegas")
    cw = d.textlength(cap, font=f_cap)
    assert cw <= CONTENT_W, "map caption too wide: %d" % cw
    d.text(((W - cw) / 2, 450), cap, font=f_cap, fill=GREY)

    # ---- story columns --------------------------------------------------
    columns = [
        ("EUROPE", [
            {"kind": "featured", "glyph": "poland",
             "label": "POLAND  \u00b7  NATO",
             "head": "Two Russian missiles land in Poland",
             "fact": "Kh-101 falls 50 km from border; Tusk: "
                     "\u201cintentional provocation\u201d."},
            {"kind": "featured", "glyph": "ukraine",
             "label": "UKRAINE  \u00b7  WAR",
             "head": "\u201cTriple-tap\u201d strike hits Zelensky\u2019s hometown",
             "fact": "Missiles, then drones on rescuers: boy, 7, and a "
                     "paramedic killed; 73 hurt."},
            {"kind": "brief", "head": "COP31 nears deal",
             "fact": "New Antalya package; approval vote set for Sunday."},
            {"kind": "brief", "head": "France protests",
             "fact": "Sixth weekend; 82,500 march by police count."},
            {"kind": "brief", "head": "Belgium air shutdown",
             "fact": "National strike grounds flights on Monday."},
            {"kind": "brief", "head": "Wildberries CEO quits",
             "fact": "Steps down days after EU sanctions."},
            {"kind": "brief", "head": "De Gennaro dies",
             "fact": "Ex-Italian police chief dies amid mafia probe."},
            {"kind": "brief", "head": "Starmer calls leaders",
             "fact": "PM phones Zelensky and Trump from the G20."},
        ]),
        ("AMERICAS", [
            {"kind": "featured", "glyph": "badge",
             "label": "MEXICO  \u00b7  CARTELS",
             "head": "Mexico captures FBI most-wanted kingpin",
             "fact": "\u201cEl Chapo Isidro\u201d seized in Sinaloa; 11 dead "
                     "in the raid and backlash."},
            {"kind": "featured", "glyph": "storm",
             "label": "BRAZIL  \u00b7  STORM",
             "head": "Supercell storm kills four in Brazil",
             "fact": "Tupancireta torn apart in 40 minutes; 162 injured, "
                     "5,000 homes damaged."},
            {"kind": "brief", "head": "Card rates capped",
             "fact": "Trump vows 10% cap with Democrats\u2019 help."},
            {"kind": "brief", "head": "Senate Democrats",
             "fact": "Leadership vote tests the new majority."},
            {"kind": "brief", "head": "Nvidia probe",
             "fact": "US accounting probe amid the AI rout."},
            {"kind": "brief", "head": "Pentagon curbs Canada ties",
             "fact": "Ottawa: \u201cno change\u201d on defence."},
            {"kind": "brief", "head": "Peru quake",
             "fact": "M6.7 near Junin; tremors felt in Lima."},
            {"kind": "brief", "head": "US hosts 2026 G20",
             "fact": "Next summit at Trump\u2019s Florida golf club."},
        ]),
        ("MIDDLE EAST  \u00b7  AFRICA  \u00b7  ASIA", [
            {"kind": "featured", "glyph": "missile",
             "label": "YEMEN  \u00b7  SAUDI ARABIA",
             "head": "Houthis fire 3 missiles at Riyadh",
             "fact": "Coalition intercepts all three; second strike on "
                     "the capital in days."},
            {"kind": "featured", "glyph": "globe",
             "label": "G20  \u00b7  SOUTH AFRICA",
             "head": "G20 opens in Johannesburg",
             "fact": "First G20 in Africa; 122-point declaration "
                     "approved despite US boycott."},
            {"kind": "brief", "head": "Hormuz tankers hit",
             "fact": "Two struck, a third hits a mine; no deaths."},
            {"kind": "brief", "head": "ICJ: Myanmar guilty",
             "fact": "Rohingya genocide; 10,000 killed, 9-6 vote."},
            {"kind": "brief", "head": "Nigeria boat sinks",
             "fact": "24 die on way to a funeral; 24 rescued."},
            {"kind": "brief", "head": "Manipur hooch deaths",
             "fact": "11 die after drinking tainted alcohol."},
            {"kind": "brief", "head": "Sri Lanka landslide",
             "fact": "Four die in the Central Province."},
            {"kind": "brief", "head": "Pakistan van crash",
             "fact": "Six die as van falls into a ravine."},
            {"kind": "brief", "head": "Japan protests",
             "fact": "Hundreds demand Takaichi retract Taiwan remarks."},
        ]),
        ("SPORT  &  MARKETS", [
            {"kind": "chart"},
            {"kind": "featured", "glyph": "football",
             "label": "PREMIER LEAGUE",
             "head": "Arsenal held 2-2; Leeds stun Chelsea 4-1",
             "fact": "Madueke rescues Arsenal; Leeds win at the Bridge "
                     "for first time since 1999."},
            {"kind": "brief", "head": "India v NZ",
             "fact": "Pant 128; India 629/6 at lunch, lead 261."},
            {"kind": "brief", "head": "Australia edge England",
             "fact": "Chaudhary 66 wins 1st T20 by 3 wickets."},
            {"kind": "brief", "head": "UAE Bulls retain T10",
             "fact": "Azam Khan 52 off 22; Yas Lions beaten."},
            {"kind": "brief", "head": "Zverev wins semi",
             "fact": "Beats Medvedev 7-6, 6-4 at ATP Finals."},
            {"kind": "brief", "head": "NBA: 76ers 132-129",
             "fact": "Philadelphia edge Milwaukee."},
            {"kind": "brief", "head": "Real Madrid 2-1",
             "fact": "Beat Celta; Napoli edge Torino 1-0."},
        ]),
    ]

    f_section = font(SANS_B, 13)
    gap_x = 16
    cell_w = (CONTENT_W - 3 * gap_x) // 4
    for ci, (section, items) in enumerate(columns):
        cx = X0 + ci * (cell_w + gap_x)
        cy = COL_TOP
        d.text((cx, cy), section, font=f_section, fill=RED)
        cy += 17
        rule(d, cx, cy, cx + cell_w, 2)
        cy += 6
        for item in items:
            if item["kind"] == "featured":
                cy = draw_featured(d, cx, cy, item, cell_w)
            elif item["kind"] == "chart":
                cy = draw_chart_item(d, cx, cy, cell_w)
            else:
                cy = draw_brief(d, cx, cy, item, cell_w)
            cy += 3
        assert cy - 3 <= COL_BOTTOM, \
            "column %d overflows: y=%d" % (ci, cy)

    # ---- also in brief --------------------------------------------------
    f_brief_line = font(SANS, 12)
    brief1 = ("ALSO IN BRIEF  \u2014  Taiwan warns Carney on China  \u00b7  "
              "Kim tours factories after \u201cTrump snub\u201d  \u00b7  Seoul: "
              "speed wins the AI race  \u00b7  Meta offices hit by India "
              "protests")
    brief2 = ("F1: Russell and Verstappen clash in Vegas  \u00b7  India A v "
              "Pakistan Shaheens in Doha  \u00b7  Lyon 1-0 Lille  \u00b7  "
              "Sri Lanka A beat Hong Kong by 24")
    for line, ly in ((brief1, BRIEF_Y), (brief2, BRIEF_Y + 16)):
        assert d.textlength(line, font=f_brief_line) <= CONTENT_W, \
            "brief line too wide: %r" % line
        d.text((X0, ly), line, font=f_brief_line, fill=(52, 50, 46))

    # ---- day in numbers -------------------------------------------------
    rule(d, X0, 908, X1, 2)
    f_num = font(SANS_B, 14)
    f_num_lab = font(SANS, 14)
    nums = [("600,000", "troops"), ("122", "G20 points"),
            ("10,000", "killed"), ("3", "missiles"),
            ("162", "injured"), ("M6.7", "quake"),
            ("82,500", "marching")]
    spans = []
    for k, (val, lab) in enumerate(nums):
        spans.append((d.textlength(val, font=f_num), val, True))
        spans.append((d.textlength(" " + lab, font=f_num_lab),
                      " " + lab, False))
        if k < len(nums) - 1:
            spans.append((d.textlength("  \u00b7  ", font=f_num_lab),
                          "  \u00b7  ", False))
    total_w = sum(w for w, _, _ in spans)
    head_txt = "THE DAY IN NUMBERS   "
    head_w = d.textlength(head_txt, font=f_num)
    total_w += head_w
    assert total_w <= CONTENT_W, "numbers strip too wide: %d" % total_w
    nx = X0 + (CONTENT_W - total_w) // 2
    ny = NUM_Y
    d.text((nx, ny), head_txt, font=f_num, fill=RED)
    nx += head_w
    for w, txt, bold in spans:
        d.text((nx, ny), txt, font=f_num if bold else f_num_lab,
               fill=INK if bold else GREY)
        nx += w

    # ---- footer ---------------------------------------------------------
    f_foot = font(SANS, 13)
    foot = ("Sources: Reuters, AP, AFP, BBC, CNN, Al Jazeera, The Times, "
            "The Hindu, The Straits Times, Times of Israel  \u00b7  "
            "22 Nov 2026  \u00b7  42 stories, every fact checked")
    fw = d.textlength(foot, font=f_foot)
    assert fw <= CONTENT_W, "footer too wide: %d" % fw
    d.text(((W - fw) / 2, FOOT_Y), foot, font=f_foot, fill=GREY)

    # ---- coming up ------------------------------------------------------
    f_up = font(SANS, 12)
    up = ("COMING UP  \u2014  Geneva talks resume on Monday  \u00b7  "
          "Liverpool v Manchester United  \u00b7  COP31: the deal, "
          "line by line")
    uw = d.textlength(up, font=f_up)
    assert uw <= CONTENT_W, "coming-up line too wide: %d" % uw
    d.text(((W - uw) / 2, 972), up, font=f_up, fill=GREY)

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out, "PNG", optimize=True)
    print("wrote", out, img.size, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
