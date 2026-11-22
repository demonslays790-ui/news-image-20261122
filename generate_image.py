#!/usr/bin/env python3
"""Render the 22 November 2026 world-news front page (v2) as a 1024x1024 PNG.

Original code written for the make.fun news-image-20261122 bounty, v2 rebuild.
Replaces the v1 text-only page: fresh lead (Trump's 22 Nov "not my final
offer"), COP31 reframed as nearing a deal, accurate hand-drawn flag chips,
a markets bar chart, a "THE PLAN IN BRIEF" box and a "DAY IN NUMBERS" strip.
Every headline and fact was verified against published reports (see
stories-v2.md in the work directory). No network access at render time.
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 36
CONTENT_W = W - 2 * MARGIN

PAPER = (250, 246, 236)   # warm newsprint
INK = (18, 18, 18)
RED = (158, 28, 28)       # section-label red
GREY = (96, 92, 84)
RULE = (58, 56, 50)
BAR_RED = (178, 34, 34)
BOX_BG = (244, 238, 226)

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


# ---------------------------------------------------------------- flags
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


def flag_peru(d, x, y, w=30, h=20):
    d.rectangle([x, y, x + w // 3 - 1, y + h - 1], fill=(216, 30, 44))
    d.rectangle([x + w // 3, y, x + 2 * w // 3 - 1, y + h - 1],
                fill=(255, 255, 255))
    d.rectangle([x + 2 * w // 3, y, x + w - 1, y + h - 1], fill=(216, 30, 44))
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


def reward_badge(d, x, y):
    """Small '$5M REWARD' tag for the Mexico cell."""
    f = font(SANS_B, 11)
    txt = "$5M REWARD"
    tw = d.textlength(txt, font=f)
    d.rectangle([x, y, x + tw + 10, y + 19], outline=RED, width=1)
    d.text((x + 5, y + 3), txt, font=f, fill=RED)
    return tw + 10


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    x0, x1 = MARGIN, W - MARGIN

    # ---- dateline bar -------------------------------------------------
    f_date = font(SANS_B, 19)
    d.text((x0, 24), "SUNDAY, 22 NOVEMBER 2026", font=f_date, fill=INK)
    right = "THE WORLD IN ONE PAGE"
    d.text((x1 - d.textlength(right, font=f_date), 24), right,
           font=f_date, fill=INK)
    rule(d, x0, 52, x1, 3)

    # ---- masthead ------------------------------------------------------
    f_mast = font(SERIF_B, 84)
    title = "THE WORLD TODAY"
    tw = d.textlength(title, font=f_mast)
    d.text(((W - tw) / 2, 60), title, font=f_mast, fill=INK)
    f_sub = font(SERIF_I, 21)
    sub = ("Ten stories that sum up the day \u2014 every fact checked "
           "against published reports")
    sw = d.textlength(sub, font=f_sub)
    d.text(((W - sw) / 2, 150), sub, font=f_sub, fill=GREY)
    rule(d, x0, 186, x1, 3)
    rule(d, x0, 191, x1, 1)

    # ---- lead story ----------------------------------------------------
    lead_w = 636                       # x0 .. x0+lead_w
    box_x0, box_x1 = x0 + lead_w + 24, x1   # plan box on the right
    y = 206
    flag_ukraine(d, x0, y + 1)
    f_lead_label = font(SANS_B, 19)
    d.text((x0 + 38, y), "LEAD  \u00b7  UKRAINE PEACE TALKS",
           font=f_lead_label, fill=RED)
    y += 28
    f_lead_head = font(SERIF_B, 40)
    lead_head_lines = ["Trump: 28-point Ukraine plan",
                       "\u201cnot my final offer\u201d"]
    for line in lead_head_lines:
        assert d.textlength(line, font=f_lead_head) <= lead_w, \
            "lead headline line too long: %r" % line
    y = draw_lines(d, lead_head_lines, f_lead_head, x0, y, INK, 47)
    y += 6
    f_lead_fact = font(SANS, 18)
    lead_fact = ("Zelensky spoke to Trump on Saturday; talks move to Geneva "
                 "on Monday. The draft caps the army at 600,000, bars NATO, "
                 "demands the Donbas.")
    fact_lines = wrap(d, lead_fact, f_lead_fact, lead_w)
    assert len(fact_lines) <= 3, "lead fact too long: %r" % fact_lines
    y = draw_lines(d, fact_lines, f_lead_fact, x0, y, INK, 24)
    assert y <= 386, "lead block overflows: y=%d" % y

    # ---- plan-in-brief box --------------------------------------------
    d.rectangle([box_x0, 206, box_x1, 384], fill=BOX_BG, outline=RULE, width=1)
    bx, by = box_x0 + 12, 214
    f_box_title = font(SANS_B, 15)
    d.text((bx, by), "THE PLAN IN BRIEF", font=f_box_title, fill=RED)
    by += 26
    rule(d, bx, by, box_x1 - 12, 1)
    by += 10
    f_box = font(SANS, 15)
    box_items = [
        "Army capped at 600,000 troops",
        "No NATO membership for Kyiv",
        "Cede the Donbas; freeze the front lines",
        "Geneva talks Mon 23 Nov; Trump deadline 27 Nov",
    ]
    for item in box_items:
        lines = wrap(d, item, f_box, box_x1 - box_x0 - 36)
        for li, line in enumerate(lines):
            if li == 0:
                d.rectangle([bx, by + 5, bx + 6, by + 11], fill=RED)
            d.text((bx + 12, by), line, font=f_box, fill=INK)
            by += 19
        by += 4
    assert by <= 380, "plan box overflows: y=%d" % by

    rule(d, x0, 396, x1, 3)

    # ---- story grid: 3 x 3 ---------------------------------------------
    # (label, flag, headline, fact) — flag is a callable or None
    stories = [
        ("POLAND  \u00b7  NATO", flag_poland,
         "Two Russian missiles land in Poland",
         "Kh-101 falls 50 km from the border; Tusk calls it an "
         "\u201cintentional provocation\u201d; Rutte in Warsaw."),
        ("UKRAINE  \u00b7  WAR", flag_ukraine,
         "\u201cTriple-tap\u201d strike hits Zelensky\u2019s hometown",
         "Two missiles, then drones on rescuers: a boy of 7 and a "
         "20-year-old paramedic killed, 73 wounded."),
        ("CLIMATE  \u00b7  COP31", flag_turkiye,
         "COP31 nears deal after all-night talks",
         "A new package lands in Antalya; approval session set for Sunday "
         "morning after the fossil-fuel fight."),
        ("MEXICO  \u00b7  CARTELS", "badge",
         "Mexico captures FBI most-wanted kingpin",
         "\u201cEl Chapo Isidro\u201d seized in Sinaloa; 11 dead in the raid "
         "and cartel backlash; $5m US reward."),
        ("GULF  \u00b7  HORMUZ", "tanker",
         "Three tankers hit near Hormuz",
         "Two struck by projectiles, a third hits a mine and burns; no "
         "casualties; Iran claims a US drone downed."),
        ("MARKETS", "chart",
         "AI rout: Nvidia \u221214%, S&P in correction",
         ""),
        ("PERU  \u00b7  QUAKE", flag_peru,
         "Strong quake shakes Peru",
         "Magnitude 6.7 strikes near Jun\u00edn; tremors felt in Lima; no "
         "deaths reported."),
        ("NIGERIA", flag_nigeria,
         "Boat capsizes on way to funeral",
         "24 die in Bayelsa State as a boat carrying mourners overturns; "
         "24 rescued."),
        ("FRANCE  \u00b7  PROTESTS", flag_france,
         "French protests enter sixth weekend",
         "82,500 march by police count, 150,000 by organisers; turnout "
         "falls from 106,000 a week ago."),
    ]

    f_label = font(SANS_B, 15)
    f_head = font(SERIF_B, 23)
    f_fact = font(SANS, 16)
    gap_x, gap_y = 24, 12
    cell_w = (CONTENT_W - 2 * gap_x) // 3
    grid_top, grid_bottom = 410, 936
    cell_h = (grid_bottom - grid_top - 2 * gap_y) // 3

    for i, (label, flag, head, fact) in enumerate(stories):
        r, c = divmod(i, 3)
        cx = x0 + c * (cell_w + gap_x)
        cy = grid_top + r * (cell_h + gap_y)
        cell_bottom = cy + cell_h
        rule(d, cx, cy, cx + cell_w, 2)
        cy += 9
        if callable(flag):
            flag(d, cx, cy + 1)
            d.text((cx + 38, cy), label, font=f_label, fill=RED)
        elif flag == "badge":
            reward_badge(d, cx, cy)
            d.text((cx + 108, cy), label, font=f_label, fill=RED)
        elif flag == "tanker":
            tanker_glyph(d, cx, cy + 1)
            d.text((cx + 38, cy), label, font=f_label, fill=RED)
        else:  # markets: no icon, label alone
            d.text((cx, cy), label, font=f_label, fill=RED)
        cy += 25
        head_lines = wrap(d, head, f_head, cell_w)
        assert len(head_lines) <= 3, "headline too long: %r" % head_lines
        cy = draw_lines(d, head_lines, f_head, cx, cy, INK, 28)
        cy += 4
        if flag == "chart":
            f_chart_lab = font(SANS_B, 13)
            f_chart_val = font(SANS_B, 13)
            bars = [("S&P 500", 3.7), ("Nasdaq", 5.3),
                    ("Dow", 1.9), ("Nikkei", 5.1)]
            bar_x = cx + 78
            bar_max = cell_w - 78 - 52
            for name, drop in bars:
                d.text((cx, cy), name, font=f_chart_lab, fill=INK)
                bw = int(bar_max * drop / 5.3)
                d.rectangle([bar_x, cy + 2, bar_x + bw, cy + 12],
                            fill=BAR_RED)
                d.text((bar_x + bar_max + 6, cy),
                       "-%s%%" % drop, font=f_chart_val, fill=BAR_RED)
                cy += 17
            # chart carries the cell: no separate fact paragraph
        else:
            fact_lines = wrap(d, fact, f_fact, cell_w)
            assert len(fact_lines) <= 3, "fact too long: %r" % fact_lines
            cy = draw_lines(d, fact_lines, f_fact, cx, cy, (52, 50, 46), 21)
        assert cy <= cell_bottom, "cell %d overflows: y=%d" % (i, cy)

    # ---- day in numbers -------------------------------------------------
    rule(d, x0, 948, x1, 2)
    f_num = font(SANS_B, 14)
    f_num_lab = font(SANS, 14)
    nums = [("28", "points"), ("600,000", "troops"),
            ("3", "tankers"), ("73", "wounded"),
            ("11", "dead"), ("24", "drowned"),
            ("M6.7", "quake"), ("82,500", "marching")]
    # build spans: value (bold) + " label" (regular), separated by middots
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
    nx = x0 + (CONTENT_W - total_w) // 2
    ny = 958
    d.text((nx, ny), head_txt, font=f_num, fill=RED)
    nx += head_w
    for w, txt, bold in spans:
        d.text((nx, ny), txt, font=f_num if bold else f_num_lab,
               fill=INK if bold else GREY)
        nx += w

    # ---- footer ---------------------------------------------------------
    f_foot = font(SANS, 13)
    foot = ("Sources: Reuters, AP, CNN, Al Jazeera, The Straits Times, "
            "Times of Israel, Wall Street Journal  \u00b7  22 Nov 2026")
    fw = d.textlength(foot, font=f_foot)
    d.text(((W - fw) / 2, 992), foot, font=f_foot, fill=GREY)

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out, "PNG", optimize=True)
    print("wrote", out, img.size, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
