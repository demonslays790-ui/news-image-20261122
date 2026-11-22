#!/usr/bin/env python3
"""Draw the v4 front page for make.fun news-image-20261122.

A single 1024x1024 newspaper front page summing up Sunday
22 November 2026: 35 verified stories in 6 regions, one dominant
lead, a richly drawn world map with 12 numbered markers, a markets
bar chart, a day-in-numbers strip, a quote panel and a briefs strip.
Everything is drawn from scratch with Pillow; no network, no
external assets, no timestamps, so repeated runs are byte-identical.
Run:  python3 generate_image.py   (writes entry.png beside this file)
"""

import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 26
GUTTER = 14
COLW = 232

PAPER = (250, 246, 236)
INK = (24, 22, 18)
RED = (178, 34, 28)
DARKRED = (128, 20, 16)
GREY = (96, 90, 80)
RULE = (40, 36, 30)
SEA = (206, 226, 238)
SEALINE = (168, 196, 214)
LAND = (233, 220, 189)
LANDLINE = (146, 116, 66)
LANDLABEL = (107, 84, 51)
PANEL = (244, 239, 226)
PANELLINE = (178, 168, 146)

FONTDIR = "/usr/share/fonts/truetype"


def _pick(*names):
    for name in names:
        path = os.path.join(FONTDIR, name)
        if os.path.exists(path):
            return path
    raise FileNotFoundError(names[0])


SERIF = _pick("liberation/LiberationSerif-Regular.ttf",
              "dejavu/DejaVuSerif.ttf")
SERIFB = _pick("liberation/LiberationSerif-Bold.ttf",
               "dejavu/DejaVuSerif-Bold.ttf")
SERIFI = _pick("liberation/LiberationSerif-Italic.ttf",
               "dejavu/DejaVuSerif-Italic.ttf")
SANS = _pick("liberation/LiberationSans-Regular.ttf",
             "dejavu/DejaVuSans.ttf")
SANSB = _pick("liberation/LiberationSans-Bold.ttf",
              "dejavu/DejaVuSans-Bold.ttf")

_cache = {}


def f(path, size):
    key = (path, size)
    if key not in _cache:
        _cache[key] = ImageFont.truetype(path, size)
    return _cache[key]


def wrap(d, text, font, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    lines, cur = [], ""
    for word in text.split():
        trial = word if not cur else cur + " " + word
        if d.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def para(d, x, y, text, font, max_w, fill=INK, leading=2):
    """Draw wrapped text; returns the y just below the last line."""
    for line in wrap(d, text, font, max_w):
        d.text((x, y), line, font=font, fill=fill)
        y += font.size + leading
    return y


def hline(d, x0, x1, y, fill=RULE, width=2):
    d.line([(x0, y), (x1, y)], fill=fill, width=width)


def section_head(d, x, y, w, title, glyph=None):
    """Red-ruled section header; returns y below it."""
    d.text((x, y), title, font=f(SANSB, 12), fill=RED)
    if glyph:
        glyph(d, x + w - 16, y + 1)
    y += 16
    hline(d, x, x + w, y, fill=RULE, width=2)
    return y + 6


# ---------------------------------------------------------------- flags
def flag_us(d, x, y, w=26, h=16):
    for i in range(7):
        d.rectangle([x, y + i * h / 7, x + w, y + (i + 1) * h / 7],
                    fill=RED if i % 2 == 0 else (255, 255, 255))
    d.rectangle([x, y, x + w * 0.42, y + h * 4 / 7], fill=(30, 50, 110))
    for r in range(3):
        for c in range(4):
            d.ellipse([x + 2 + c * 2.6, y + 2 + r * 3.4,
                       x + 3.6 + c * 2.6, y + 3.6 + r * 3.4],
                      fill=(255, 255, 255))


def flag_ua(d, x, y, w=26, h=16):
    d.rectangle([x, y, x + w, y + h / 2], fill=(0, 90, 170))
    d.rectangle([x, y + h / 2, x + w, y + h], fill=(255, 210, 0))


def flag_uk(d, x, y, w=26, h=16):
    d.rectangle([x, y, x + w, y + h], fill=(20, 40, 110))
    d.line([(x, y), (x + w, y + h)], fill=(255, 255, 255), width=3)
    d.line([(x + w, y), (x, y + h)], fill=(255, 255, 255), width=3)
    d.line([(x + w / 2, y), (x + w / 2, y + h)], fill=(255, 255, 255),
           width=5)
    d.line([(x, y + h / 2), (x + w, y + h / 2)], fill=(255, 255, 255),
           width=5)
    d.line([(x + w / 2, y), (x + w / 2, y + h)], fill=(200, 30, 30),
           width=2)
    d.line([(x, y + h / 2), (x + w, y + h / 2)], fill=(200, 30, 30),
           width=2)


def flag_fr(d, x, y, w=26, h=16):
    d.rectangle([x, y, x + w / 3, y + h], fill=(0, 60, 160))
    d.rectangle([x + w / 3, y, x + 2 * w / 3, y + h],
                fill=(255, 255, 255))
    d.rectangle([x + 2 * w / 3, y, x + w, y + h], fill=(200, 30, 40))


def flag_de(d, x, y, w=26, h=16):
    d.rectangle([x, y, x + w, y + h / 3], fill=(20, 20, 20))
    d.rectangle([x, y + h / 3, x + w, y + 2 * h / 3], fill=(200, 30, 30))
    d.rectangle([x, y + 2 * h / 3, x + w, y + h], fill=(255, 205, 0))


# ---------------------------------------------------------------- glyphs
def glyph_missile(d, x, y):
    d.polygon([(x + 7, y), (x + 11, y + 6), (x + 7, y + 14),
               (x + 3, y + 6)], fill=GREY)
    d.polygon([(x + 3, y + 10), (x, y + 15), (x + 5, y + 13)], fill=RED)
    d.polygon([(x + 11, y + 10), (x + 14, y + 15), (x + 9, y + 13)],
              fill=RED)


def glyph_quake(d, x, y):
    pts = [(x, y + 7), (x + 3, y + 7), (x + 5, y + 2), (x + 7, y + 12),
           (x + 9, y + 4), (x + 11, y + 10), (x + 14, y + 7)]
    d.line(pts, fill=DARKRED, width=2)


def glyph_storm(d, x, y):
    d.ellipse([x, y + 4, x + 7, y + 11], fill=GREY)
    d.ellipse([x + 4, y + 1, x + 12, y + 10], fill=GREY)
    d.ellipse([x + 8, y + 5, x + 15, y + 12], fill=GREY)
    d.rectangle([x + 1, y + 9, x + 14, y + 12], fill=GREY)
    d.line([(x + 5, y + 13), (x + 3, y + 17)], fill=(60, 110, 180),
           width=2)
    d.line([(x + 10, y + 13), (x + 8, y + 17)], fill=(60, 110, 180),
           width=2)


def glyph_scales(d, x, y):
    d.line([(x + 7, y + 1), (x + 7, y + 13)], fill=INK, width=2)
    d.line([(x + 1, y + 4), (x + 13, y + 4)], fill=INK, width=2)
    d.line([(x + 1, y + 4), (x + 1, y + 9)], fill=INK, width=1)
    d.line([(x + 13, y + 4), (x + 13, y + 9)], fill=INK, width=1)
    d.arc([x - 1, y + 7, x + 4, y + 12], 0, 180, fill=INK, width=1)
    d.arc([x + 11, y + 7, x + 16, y + 12], 0, 180, fill=INK, width=1)
    d.line([(x + 3, y + 13), (x + 11, y + 13)], fill=INK, width=2)


def glyph_ball(d, x, y):
    d.ellipse([x, y, x + 15, y + 15], outline=INK, width=2)
    d.polygon([(x + 7, y + 5), (x + 10, y + 7), (x + 9, y + 11),
               (x + 5, y + 11), (x + 4, y + 7)], fill=INK)
    d.line([(x + 7, y + 5), (x + 7, y + 1)], fill=INK, width=1)
    d.line([(x + 10, y + 7), (x + 14, y + 5)], fill=INK, width=1)
    d.line([(x + 5, y + 11), (x + 3, y + 15)], fill=INK, width=1)


def glyph_globe(d, x, y):
    d.ellipse([x, y, x + 15, y + 15], outline=INK, width=2)
    d.ellipse([x + 5, y, x + 10, y + 15], outline=INK, width=1)
    d.line([(x, y + 7), (x + 15, y + 7)], fill=INK, width=1)
    d.arc([x + 1, y + 2, x + 14, y + 13], 200, 340, fill=INK, width=1)


def glyph_badge(d, x, y):
    d.ellipse([x, y, x + 15, y + 15], outline=DARKRED, width=2)
    d.text((x + 4, y + 2), "$", font=f(SANSB, 10), fill=DARKRED)


def glyph_tanker(d, x, y):
    d.polygon([(x, y + 8), (x + 15, y + 8), (x + 13, y + 13),
               (x + 2, y + 13)], fill=(120, 40, 30))
    d.rectangle([x + 9, y + 3, x + 12, y + 8], fill=INK)
    d.line([(x, y + 14), (x + 15, y + 14)], fill=(60, 110, 180),
           width=1)


# ---------------------------------------------------------------- map
# Stylised continent outlines as (lon, lat) points, drawn in an
# equirectangular projection. Schematic but recognisable.

N_AMERICA = [(-166, 68), (-152, 70), (-140, 70), (-128, 71), (-115, 69),
             (-105, 68), (-95, 69), (-88, 70), (-82, 66), (-78, 69),
             (-72, 62), (-64, 60), (-56, 52), (-60, 47), (-65, 44),
             (-70, 43), (-75, 39), (-76, 35), (-80, 32), (-81, 26),
             (-84, 30), (-90, 29), (-94, 29), (-97, 26), (-97, 21),
             (-94, 17), (-90, 14), (-86, 12), (-83, 9), (-80, 8),
             (-78, 8), (-82, 13), (-87, 15), (-91, 18), (-96, 19),
             (-97, 22), (-105, 20), (-110, 23), (-114, 29), (-120, 34),
             (-124, 40), (-124, 48), (-130, 55), (-140, 60), (-152, 60),
             (-158, 58), (-162, 55), (-166, 60), (-168, 66)]
GREENLAND = [(-45, 60), (-40, 65), (-32, 68), (-25, 70), (-20, 74),
             (-25, 76), (-35, 77), (-50, 76), (-58, 74), (-55, 70),
             (-52, 64), (-48, 60)]
S_AMERICA = [(-80, 9), (-77, 4), (-80, -3), (-81, -6), (-77, -12),
             (-72, -18), (-70, -23), (-70, -30), (-72, -37), (-73, -44),
             (-74, -50), (-70, -54), (-66, -55), (-68, -50), (-65, -45),
             (-62, -41), (-58, -35), (-52, -32), (-48, -28), (-41, -23),
             (-39, -17), (-35, -9), (-35, -6), (-40, -3), (-44, -2),
             (-50, 0), (-55, 5), (-60, 8), (-68, 11), (-72, 12),
             (-77, 8)]
AFRICA = [(-6, 35), (-10, 31), (-15, 27), (-17, 21), (-17, 15),
          (-15, 11), (-13, 8), (-8, 5), (-4, 5), (0, 6), (6, 4),
          (9, 4), (9, -1), (12, -5), (13, -10), (12, -17), (14, -22),
          (15, -27), (17, -32), (20, -35), (26, -34), (32, -29),
          (35, -24), (40, -16), (40, -11), (41, -4), (46, -1), (51, 2),
          (51, 10), (48, 11), (44, 11), (40, 15), (38, 18), (37, 22),
          (34, 27), (32, 31), (30, 31), (25, 32), (20, 32), (15, 32),
          (11, 34), (10, 37), (5, 37), (0, 36), (-6, 35)]
MADAGASCAR = [(44, -16), (47, -15), (50, -16), (50, -22), (47, -25),
              (44, -25), (43, -20)]
EURASIA = [(-10, 36), (-9, 43), (-2, 44), (-1, 46), (-4, 48), (-2, 49),
           (0, 50), (3, 52), (5, 53), (8, 55), (8, 57), (10, 59),
           (12, 56), (18, 56), (21, 55), (24, 58), (28, 60), (30, 62),
           (32, 66), (35, 67), (40, 68), (45, 68), (55, 69), (65, 69),
           (70, 72), (75, 73), (80, 73), (85, 75), (95, 76), (105, 77),
           (110, 74), (115, 73), (120, 73), (130, 72), (140, 72),
           (150, 70), (158, 69), (162, 66), (170, 67), (178, 65),
           (170, 60), (162, 60), (158, 56), (156, 51), (150, 44),
           (142, 38), (140, 35), (135, 34), (130, 33), (127, 35),
           (126, 38), (122, 37), (120, 34), (118, 25), (112, 22),
           (109, 18), (106, 10), (104, 8), (100, 7), (98, 10),
           (97, 15), (94, 17), (92, 21), (89, 22), (86, 20), (83, 18),
           (80, 15), (80, 10), (77, 8), (75, 12), (73, 16), (70, 20),
           (68, 22), (66, 25), (62, 25), (58, 25), (57, 26), (55, 26),
           (52, 26), (50, 29), (48, 30), (50, 26), (52, 25), (54, 24),
           (57, 22), (59, 22), (58, 20), (55, 17), (52, 15), (48, 14),
           (44, 13), (43, 12), (40, 15), (38, 18), (37, 20), (35, 22),
           (34, 27), (33, 29), (32, 31), (30, 31), (28, 31), (26, 33),
           (23, 33), (20, 32), (18, 32), (15, 32), (12, 33), (10, 34),
           (8, 37), (10, 37), (12, 38), (14, 40), (16, 40), (18, 40),
           (16, 42), (14, 44), (12, 44), (8, 44), (6, 43), (3, 43),
           (0, 40), (-1, 38), (-2, 37), (-5, 36), (-8, 36), (-10, 36)]
BRITAIN = [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53),
           (1, 51)]
JAPAN = [(130, 31), (132, 33), (135, 34), (137, 35), (139, 37),
         (141, 39), (142, 42), (144, 44), (141, 45), (140, 42),
         (139, 38), (136, 36), (133, 34), (130, 31)]
AUSTRALIA = [(114, -22), (114, -30), (115, -35), (120, -34), (126, -32),
             (129, -32), (132, -32), (135, -35), (138, -35), (140, -38),
             (145, -38), (150, -37), (153, -32), (153, -27), (150, -22),
             (146, -19), (142, -15), (142, -11), (137, -12), (135, -15),
             (132, -12), (130, -13), (126, -14), (122, -17), (118, -20),
             (114, -22)]
NZ = [(167, -45), (170, -43), (173, -41), (175, -38), (177, -38),
      (175, -40), (172, -42), (168, -46)]
LANDS = [N_AMERICA, GREENLAND, S_AMERICA, AFRICA, MADAGASCAR, EURASIA,
         BRITAIN, JAPAN, AUSTRALIA, NZ]
# Small islands drawn as dots (lon, lat).
ISLANDS = [(-18, 65), (95, -5), (100, -2), (105, -6), (114, -3),
           (120, -1), (125, 1), (131, -1), (138, -4), (145, -5),
           (104, 1), (80, 7), (90, 22), (121, 25), (-155, 20),
           (-60, -3), (55, -20), (63, -18), (-70, 18), (-77, 21)]

# (number, lon, lat, short key label)
MARKERS = [(1, 30.5, 50.5, "Kyiv"), (2, 21.0, 52.2, "Warsaw"),
           (3, 30.7, 36.9, "Antalya"), (4, 24.9, 60.2, "Helsinki"),
           (5, 46.7, 24.6, "Riyadh"), (6, 28.0, -26.2, "Johannesburg"),
           (7, 92.0, 21.4, "Cox's Bazar"), (8, -53.8, -29.0, "Tupancireta"),
           (9, -77.0, -12.0, "Lima"), (10, 6.3, 4.9, "Bayelsa"),
           (11, 139.7, 35.7, "Tokyo"), (12, -115.1, 36.2, "Las Vegas")]


def draw_map(d, x0, y0, w, h):
    """Rich world map: shaded sea, graticule, detailed land, labels,
    12 numbered markers and three mini event icons."""
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=SEA)
    lat_top, lat_bot = 84.0, -58.0
    def px(lon, lat):
        return (x0 + (lon + 180.0) / 360.0 * w,
                y0 + (lat_top - lat) / (lat_top - lat_bot) * h)
    # Graticule every 30 degrees.
    for lon in range(-180, 181, 30):
        gx, _ = px(lon, 0)
        d.line([(gx, y0), (gx, y0 + h)], fill=SEALINE, width=1)
    for lat in range(-60, 91, 30):
        _, gy = px(0, lat)
        d.line([(x0, gy), (x0 + w, gy)], fill=SEALINE, width=1)
    # Sea shading: darker bands near the poles.
    d.rectangle([x0, y0, x0 + w, y0 + 8], fill=(196, 218, 232))
    d.rectangle([x0, y0 + h - 8, x0 + w, y0 + h], fill=(196, 218, 232))
    # Land masses.
    for poly in LANDS:
        pts = [px(lon, lat) for lon, lat in poly]
        d.polygon(pts, fill=LAND, outline=LANDLINE)
    for lon, lat in ISLANDS:
        ix, iy = px(lon, lat)
        d.ellipse([ix - 2, iy - 2, ix + 2, iy + 2], fill=LAND,
                  outline=LANDLINE)
    # Region labels.
    labels = [("NORTH AMERICA", -105, 52), ("SOUTH AMERICA", -105, -32),
              ("EUROPE", -30, 50), ("AFRICA", 18, 2),
              ("ASIA", 90, 52), ("OCEANIA", 140, -45),
              ("ATLANTIC", -32, 12), ("PACIFIC", -150, -8)]
    for name, lon, lat in labels:
        lx, ly = px(lon, lat)
        d.text((lx, ly), name, font=f(SANSB, 9), fill=LANDLABEL)
    # Event icons beside three markers (drawn first, markers on top).
    mx, my = px(46.7, 24.6)
    glyph_missile(d, int(mx) + 8, int(my) - 16)
    mx, my = px(-77.0, -12.0)
    glyph_quake(d, int(mx) - 22, int(my) - 6)
    mx, my = px(-53.8, -29.0)
    glyph_storm(d, int(mx) + 8, int(my) - 4)
    # Numbered markers. The four Europe markers sit within a few
    # pixels of each other, so their badges fan out from the true
    # point on a thin leader line; the rest sit on their point.
    offsets = {1: (18, -10), 2: (-22, -14), 3: (18, 14), 4: (-6, -12)}
    for num, lon, lat, _name in MARKERS:
        mx, my = px(lon, lat)
        mx, my = int(mx), int(my)
        bx, by = mx, my
        if num in offsets:
            dx, dy = offsets[num]
            bx, by = mx + dx, my + dy
            d.ellipse([mx - 2, my - 2, mx + 2, my + 2], fill=DARKRED)
            d.line([(mx, my), (bx, by)], fill=DARKRED, width=1)
        d.ellipse([bx - 8, by - 8, bx + 8, by + 8], fill=RED,
                  outline=(255, 255, 255), width=2)
        txt = str(num)
        tw = d.textlength(txt, font=f(SANSB, 10))
        d.text((bx - tw / 2, by - 7), txt, font=f(SANSB, 10),
               fill=(255, 255, 255))
    # Compass rose, top right.
    cx, cy = x0 + w - 26, y0 + 16
    d.polygon([(cx, cy - 9), (cx + 4, cy + 5), (cx, cy + 2),
               (cx - 4, cy + 5)], fill=INK)
    d.text((cx - 3, cy + 7), "N", font=f(SANSB, 9), fill=INK)
    d.rectangle([x0, y0, x0 + w, y0 + h], outline=RULE, width=2)


# ---------------------------------------------------------------- stories
# (kicker, headline, fact, glyph-or-None)
EUROPE = [
    ("POLAND · NATO", "Russian missiles land in Poland",
     "Kh-101 fell 50 km from the border; Tusk calls it an "
     "\u201cintentional provocation\u201d.", glyph_missile),
    ("UKRAINE · WAR", "Strike hits Zelensky\u2019s hometown",
     "Two missiles, then drones on rescuers: a boy of 7 and a "
     "paramedic killed, 73 hurt.", None),
    ("CLIMATE · COP31", "COP31 nears deal on day 14",
     "New package in Antalya; approval session Sunday, objections "
     "due 0300 GMT.", glyph_globe),
    ("FRANCE", "France protests, sixth weekend",
     "82,500 march by police count, 150,000 by organisers; turnout "
     "falls.", None),
    ("FINLAND", "Russian helicopter over Finland",
     "Helsinki probes a suspected 4.1 km airspace violation.", None),
]
AFRICA = [
    ("SOUTH AFRICA · G20", "G20 opens in Johannesburg",
     "First G20 in Africa: 122-point declaration approved despite "
     "US boycott.", glyph_globe),
    ("NIGERIA", "Nigeria boat disaster kills 24",
     "Boat carrying mourners overturns in Bayelsa; 24 rescued.", None),
    ("DR CONGO", "Ebola fight hampered in Congo",
     "Geography, violence and distrust slow the DR Congo response.",
     None),
]
AMERICAS = [
    ("MEXICO · CARTELS", "Mexico seizes \u201cEl Chapo Isidro\u201d",
     "Cartel boss caught in Sinaloa; 11 dead in raid and backlash; "
     "$5m reward.", glyph_badge),
    ("BRAZIL · STORM", "Supercell storm kills four",
     "Tupanciret\u00e3 torn apart in 40 minutes: 162 injured, 8,000 "
     "homes damaged.", glyph_storm),
    ("USA · ECONOMY", "Trump: cap card rates at 10%",
     "Vows a 10% cap, with Democrats\u2019 help.", None),
    ("PERU · QUAKE", "Peru quake rattles Lima",
     "Magnitude 6.7 strikes near Jun\u00edn; tremors felt in the "
     "capital, no deaths.", glyph_quake),
    ("USA · CANADA", "Pentagon curbs Canada ties",
     "US curbs defence ties; Ottawa unmoved.", None),
]
MIDEAST = [
    ("YEMEN · SAUDI ARABIA", "Houthis fire 3 missiles at Riyadh",
     "Coalition intercepts the barrage \u2014 the second strike on "
     "the capital in days.", glyph_missile),
    ("GULF", "Three tankers hit near Hormuz",
     "Two struck by projectiles, a third hits a mine and burns; no "
     "casualties.", glyph_tanker),
    ("BAHRAIN", "Bahrain facility fire blamed on Iran",
     "Ministry reports a fire at an industrial facility and "
     "attributes the strike to Iran.", None),
    ("IRAQ", "Iraq power station fire kills 4",
     "Blaze at Basra\u2019s Hartha plant; 30 hurt.", None),
]
ASIA = [
    ("MYANMAR · ICJ", "ICJ: Myanmar guilty of genocide",
     "World Court rules 9-6: 10,000 Rohingya killed in 2017; "
     "reparations ordered.", glyph_scales),
    ("INDIA", "Tainted alcohol kills 11",
     "Eleven die after drinking tainted alcohol in India\u2019s "
     "Manipur state.", None),
    ("SRI LANKA", "Sri Lanka landslide kills four",
     "Four die in a landslide in the Central Province on Saturday.",
     None),
    ("PAKISTAN", "Pakistan van crash kills six",
     "Six die as van falls into a ravine.", None),
    ("JAPAN", "Tokyo protests Takaichi remarks",
     "Hundreds demand the PM retract her remarks on Taiwan.", None),
]
SPORT = [
    ("PREMIER LEAGUE", "Arsenal held 2-2; Leeds stun Chelsea",
     "Madueke rescues Arsenal; Leeds win at the Bridge for the "
     "first time since 1999.", glyph_ball),
    ("CRICKET · TEST", "Pant 128 powers India to 629/6",
     "India lead New Zealand by 261 at lunch on day four in "
     "Wellington.", None),
    ("CRICKET · T20", "Australia edge England in T20",
     "Chaudhary\u2019s 66 seals a three-wicket win with a ball to "
     "spare at the MCG.", None),
    ("CRICKET · T10", "UAE Bulls retain T10 title",
     "Azam Khan\u2019s 52 off 22 beats Yas Lions by 24 runs in the "
     "Abu Dhabi final.", None),
    ("TENNIS · ATP FINALS", "Zverev beats Medvedev in Turin",
     "German wins the ATP Finals semi 7-6, 6-4.", None),
    ("FORMULA 1", "Verstappen on pole in Las Vegas",
     "Antonelli fastest in qualifying but takes a five-place grid "
     "penalty.", None),
]
MARKETS = [("S&P 500", -3.7), ("Nasdaq", -5.3), ("Dow", -1.9),
           ("Nikkei", -5.1)]

BRIEFS = [
    ("Denmark expels a Russian diplomat", "over an alleged plot to "
     "kill a Ukrainian rapper."),
    ("Storms spawn historic flooding", "in Florida."),
    ("Israeli strike kills three", "in an aid vehicle in Gaza City, "
     "witnesses say."),
    ("EU and Indonesia sign", "trade and investment deals."),
    ("Taiwan warns Canada\u2019s Carney", "that deeper ties with "
     "China carry risks."),
]


# ---------------------------------------------------------------- layout
def col_x(i):
    return MARGIN + i * (COLW + GUTTER)


def story_block(d, x, y, w, head, fact, glyph=None, fact_lines=2,
                 head_size=13, fact_size=11):
    """One story: bold serif headline + sans fact. Returns y below."""
    hf = f(SERIFB, head_size)
    ff = f(SANS, fact_size)
    gw = 18 if glyph else 0
    lines = wrap(d, head, hf, w - gw)
    for ln in lines:
        d.text((x, y), ln, font=hf, fill=INK)
        y += head_size + 2
    if glyph:
        glyph(d, x + w - 16, y - (head_size + 2) * len(lines) + 1)
    flines = wrap(d, fact, ff, w)[:fact_lines]
    for ln in flines:
        d.text((x, y), ln, font=ff, fill=INK)
        y += fact_size + 2
    return y + 5


def markets_chart(d, x, y, w):
    """Horizontal red bars for the week's index falls."""
    d.text((x, y), "MARKETS \u2014 AI ROUT", font=f(SANSB, 11),
           fill=DARKRED)
    y += 15
    max_drop = 5.3
    bar_max = w - 108
    for name, drop in MARKETS:
        d.text((x, y), name, font=f(SANSB, 11), fill=INK)
        bw = int(bar_max * abs(drop) / max_drop)
        d.rectangle([x + 62, y + 1, x + 62 + bw, y + 10], fill=RED)
        d.text((x + 62 + bar_max + 4, y), "-%s%%" % drop,
               font=f(SANSB, 11), fill=DARKRED)
        y += 13
    d.text((x, y), "Nvidia \u221214%; worst week since April.",
           font=f(SANS, 11), fill=INK)
    return y + 13


def quote_panel(d, x, y, w, quote, attrib):
    d.rectangle([x, y, x + w, y + 78], fill=PANEL, outline=PANELLINE)
    yy = para(d, x + 10, y + 8, quote, f(SERIFI, 13), w - 20,
              fill=INK, leading=3)
    d.text((x + 10, y + 56), attrib, font=f(SANSB, 10), fill=GREY)
    return y + 78 + 8


def coming_up(d, x, y, w):
    y = section_head(d, x, y, w, "COMING UP")
    y = para(d, x, y, "Geneva talks resume Monday \u00b7 Liverpool v "
                      "Manchester United \u00b7 COP31: the deal, line "
                      "by line", f(SANS, 11), w, leading=2)
    return y


def masthead(d):
    y = 10
    d.text((MARGIN, y), "SUNDAY, 22 NOVEMBER 2026",
           font=f(SANSB, 13), fill=INK)
    right = "THE WORLD IN ONE PAGE"
    tw = d.textlength(right, font=f(SANSB, 13))
    d.text((W - MARGIN - tw, y), right, font=f(SANSB, 13), fill=INK)
    y += 20
    hline(d, MARGIN, W - MARGIN, y, width=3)
    y += 6
    title = "THE WORLD TODAY"
    tf = f(SERIFB, 58)
    tw = d.textlength(title, font=tf)
    d.text(((W - tw) / 2, y), title, font=tf, fill=INK)
    y += 66
    tag = ("35 dated stories \u00b7 6 regions \u2014 Gulf strikes, "
           "Peru quake, COP31 day 14")
    tgf = f(SERIFI, 14)
    tw = d.textlength(tag, font=tgf)
    d.text(((W - tw) / 2, y), tag, font=tgf, fill=GREY)
    y += 22
    hline(d, MARGIN, W - MARGIN, y, width=3)
    return y + 8


def lead(d, y):
    x = MARGIN
    w = 972
    # Kicker + Ukraine flag.
    flag_ua(d, x, y + 1, 26, 16)
    d.text((x + 32, y), "LEAD \u00b7 UKRAINE PEACE TALKS",
           font=f(SANSB, 12), fill=RED)
    y += 20
    # Headline, two lines, left; plan box on the right.
    left_w = 640
    head = "Trump: 28-point Ukraine plan \u201cnot my final offer\u201d"
    yy = para(d, x, y, head, f(SERIFB, 34), left_w, leading=2)
    deck = ("Zelensky spoke to Trump on Saturday; security teams meet "
            "in Geneva on Sunday. The draft caps Kyiv\u2019s army at "
            "600,000, bars NATO and asks it to cede the Donbas "
            "\u2014 deadline 27 Nov, flexible.")
    yy = para(d, x, yy + 4, deck, f(SANS, 14), left_w - 20, leading=3)
    # Plan box.
    bx = x + left_w + 16
    bw = w - left_w - 16
    by = y - 20
    bh = 108
    d.rectangle([bx, by, bx + bw, by + bh], fill=PANEL,
                outline=PANELLINE)
    d.text((bx + 12, by + 8), "THE PLAN IN BRIEF",
           font=f(SANSB, 12), fill=DARKRED)
    items = ["Army capped at 600,000 troops",
             "No NATO membership for Kyiv",
             "Cede the Donbas, freeze the front",
             "Geneva talks Sun 22 / Mon 23 Nov"]
    iy = by + 30
    for it in items:
        d.rectangle([bx + 12, iy + 4, bx + 18, iy + 10], fill=RED)
        d.text((bx + 24, iy), it, font=f(SANS, 12), fill=INK)
        iy += 19
    # Geneva flag row under the box.
    fy = by + bh + 8
    d.text((bx, fy), "GENEVA TALKS \u00b7 MON 23 NOV",
           font=f(SANSB, 11), fill=INK)
    fx = bx + 178
    for fl in (flag_us, flag_ua, flag_uk, flag_fr, flag_de):
        fl(d, fx, fy - 2, 24, 15)
        fx += 28
    return max(yy, fy + 18)


def map_panel(d, y):
    x = MARGIN
    w = 972
    d.text((x, y), "THE DAY ON THE MAP \u2014 12 STORIES, ONE PLANET",
           font=f(SANSB, 12), fill=RED)
    y += 17
    map_h = 118
    draw_map(d, x, y, w, map_h)
    y += map_h + 6
    # Key: two lines, six markers each.
    key = ["1 Kyiv", "2 Warsaw", "3 Antalya", "4 Helsinki",
           "5 Riyadh", "6 Johannesburg", "7 Cox\u2019s Bazar",
           "8 Tupancireta", "9 Lima", "10 Bayelsa", "11 Tokyo",
           "12 Las Vegas"]
    for row in range(2):
        kx = x
        for item in key[row * 6:(row + 1) * 6]:
            d.text((kx, y), item, font=f(SANS, 11), fill=INK)
            kx += d.textlength(item, font=f(SANS, 11)) + 26
        y += 14
    return y


def columns(d, y, bottom):
    """Four columns; returns the lowest y used (for overflow check)."""
    xs = [col_x(i) for i in range(4)]
    used = []
    # Column A: Europe + Africa.
    yy = section_head(d, xs[0], y, COLW, "EUROPE")
    for item in EUROPE:
        yy = story_block(d, xs[0], yy, COLW, item[1], item[2],
                         glyph=item[3])
    yy = section_head(d, xs[0], yy + 2, COLW, "AFRICA")
    for item in AFRICA:
        yy = story_block(d, xs[0], yy, COLW, item[1], item[2],
                         glyph=item[3])
    used.append(("A", yy))
    # Column B: Americas + Middle East.
    yy = section_head(d, xs[1], y, COLW, "AMERICAS")
    for item in AMERICAS:
        yy = story_block(d, xs[1], yy, COLW, item[1], item[2],
                         glyph=item[3])
    yy = section_head(d, xs[1], yy + 2, COLW, "MIDDLE EAST")
    for item in MIDEAST:
        yy = story_block(d, xs[1], yy, COLW, item[1], item[2],
                         glyph=item[3])
    used.append(("B", yy))
    # Column C: Asia + Sport & Markets (chart + 2 stories).
    yy = section_head(d, xs[2], y, COLW, "ASIA")
    for item in ASIA:
        yy = story_block(d, xs[2], yy, COLW, item[1], item[2],
                         glyph=item[3])
    yy = section_head(d, xs[2], yy + 2, COLW, "SPORT & MARKETS",
                      glyph=glyph_ball)
    yy = markets_chart(d, xs[2], yy, COLW) + 2
    yy = story_block(d, xs[2], yy, COLW, SPORT[0][1], SPORT[0][2],
                     glyph=SPORT[0][3], fact_lines=1)
    yy = story_block(d, xs[2], yy, COLW, SPORT[1][1], SPORT[1][2],
                     fact_lines=1)
    used.append(("C", yy))
    # Column D: rest of sport + quote panels + coming up.
    yy = section_head(d, xs[3], y, COLW, "SPORT")
    for item in SPORT[2:]:
        yy = story_block(d, xs[3], yy, COLW, item[1], item[2],
                         glyph=item[3], fact_lines=1)
    yy = quote_panel(d, xs[3], yy + 4, COLW,
                     "\u201cWe believe that we have put forward a text "
                     "which all the parties can agree upon.\u201d",
                     "\u2014 Murat Kurum, COP31 president, Antalya")
    yy = quote_panel(d, xs[3], yy, COLW,
                     "\u201cThe town is gone.\u201d",
                     "\u2014 Mayor of Tupanciret\u00e3, after the storm")
    yy = coming_up(d, xs[3], yy + 2, COLW)
    used.append(("D", yy))
    for name, end in used:
        print("column", name, "ends at y =", end,
              "OVERFLOW" if end > bottom else "ok")
    return max(end for _n, end in used)


def briefs_strip(d, y):
    x = MARGIN
    d.text((x, y), "ALSO IN BRIEF",
           font=f(SANSB, 11), fill=RED)
    parts = []
    for head, tail in BRIEFS:
        parts.append(head + " " + tail)
    text = "  \u00b7  ".join(parts)
    yy = para(d, x + 118, y, text, f(SANS, 11), W - MARGIN - x - 118,
              leading=2)
    return yy


def numbers_strip(d, y):
    items = [("600,000", "troops"), ("122", "G20 points"),
             ("10,000", "killed"), ("3", "missiles"),
             ("162", "injured"), ("M6.7", "quake"),
             ("82,500", "marching")]
    x = MARGIN
    d.text((x, y), "THE DAY IN NUMBERS",
           font=f(SANSB, 12), fill=RED)
    x += 172
    for num, lab in items:
        d.text((x, y), num, font=f(SANSB, 14), fill=DARKRED)
        x += d.textlength(num, font=f(SANSB, 14)) + 5
        d.text((x, y + 2), lab, font=f(SANS, 11), fill=INK)
        x += d.textlength(lab, font=f(SANS, 11)) + 18
    return y + 20


def footer(d, y):
    hline(d, MARGIN, W - MARGIN, y, width=2)
    y += 6
    d.text((MARGIN, y), "Sources: Reuters, AP, AFP, BBC, CNN, "
                        "Al Jazeera, The Times, The Hindu, The Straits "
                        "Times, Times of Israel, Dawn \u2014 22 Nov "
                        "2026 \u00b7 35 stories, every fact checked",
           font=f(SANS, 11), fill=GREY)
    return y + 16


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    y = masthead(d)
    y = lead(d, y)
    y = map_panel(d, y + 6)
    col_bottom = 872
    used = columns(d, y + 6, col_bottom)
    print("columns end:", used, "bottom:", col_bottom)
    y = briefs_strip(d, 880)
    hline(d, MARGIN, W - MARGIN, 908, width=2)
    y = numbers_strip(d, 916)
    footer(d, 946)
    return img


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "entry.png")
    build().save(out, "PNG")
    print("wrote", out)
