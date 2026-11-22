#!/usr/bin/env python3
"""Render the 22 November 2026 world-news front page as a 1024x1024 PNG.

Original code written for the make.fun news-image-20261122 bounty.
All headlines and facts were verified against published reports (see
stories.md in the work directory). No network access at render time.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 36
CONTENT_W = W - 2 * MARGIN

PAPER = (248, 244, 233)   # warm newsprint
INK = (20, 20, 20)
RED = (155, 27, 27)       # section-label red
GREY = (90, 86, 78)
RULE = (60, 58, 52)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
SERIF_B = os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf")
SERIF = os.path.join(FONT_DIR, "DejaVuSerif.ttf")
SERIF_I = os.path.join(FONT_DIR, "DejaVuSerif.ttf")  # no italic face installed
SANS = os.path.join(FONT_DIR, "DejaVuSans.ttf")
SANS_B = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")


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


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    x0, x1 = MARGIN, W - MARGIN

    # ---- dateline bar -------------------------------------------------
    f_date = font(SANS_B, 20)
    d.text((x0, 26), "SUNDAY, 22 NOVEMBER 2026", font=f_date, fill=INK)
    right = "THE WORLD IN ONE PAGE"
    d.text((x1 - d.textlength(right, font=f_date), 26), right,
           font=f_date, fill=INK)
    rule(d, x0, 56, x1, 3)

    # ---- masthead ------------------------------------------------------
    f_mast = font(SERIF_B, 82)
    title = "THE WORLD TODAY"
    tw = d.textlength(title, font=f_mast)
    d.text(((W - tw) / 2, 66), title, font=f_mast, fill=INK)
    f_sub = font(SERIF_I, 22)
    sub = "Ten stories that sum up the day \u2014 verified against published reports"
    sw = d.textlength(sub, font=f_sub)
    d.text(((W - sw) / 2, 158), sub, font=f_sub, fill=GREY)
    rule(d, x0, 196, x1, 3)
    rule(d, x0, 201, x1, 1)

    # ---- lead story ----------------------------------------------------
    y = 218
    f_lead_label = font(SANS_B, 20)
    d.text((x0, y), "LEAD  \u00b7  UKRAINE PEACE TALKS", font=f_lead_label, fill=RED)
    y += 30
    f_lead_head = font(SERIF_B, 46)
    lead_head = "US hands Kyiv a 28-point peace plan"
    head_lines = wrap(d, lead_head, f_lead_head, CONTENT_W)
    assert len(head_lines) <= 2, "lead headline too long: %r" % head_lines
    y = draw_lines(d, head_lines, f_lead_head, x0, y, INK, 54)
    y += 6
    f_lead_fact = font(SANS, 22)
    lead_fact = ("Zelensky will discuss the draft with Trump in the coming days. "
                 "It asks Ukraine to give up the Donbas and shrink its army "
                 "in exchange for US-backed security guarantees.")
    fact_lines = wrap(d, lead_fact, f_lead_fact, CONTENT_W)
    assert len(fact_lines) <= 3, "lead fact too long: %r" % fact_lines
    y = draw_lines(d, fact_lines, f_lead_fact, x0, y, INK, 29)
    assert y <= 392, "lead block overflows: y=%d" % y
    rule(d, x0, 398, x1, 3)

    # ---- story grid: 3 x 3 ---------------------------------------------
    stories = [
        ("POLAND  \u00b7  NATO",
         "Russian missiles land in Poland",
         "Kh-101 cruise missile fell in the south-east; PM Tusk calls it an "
         "intentional provocation."),
        ("UKRAINE  \u00b7  WAR",
         "Missile hits Zelensky's hometown",
         "Russian ballistic strike on Kryvyi Rih kills 2 and wounds dozens."),
        ("CLIMATE  \u00b7  COP31",
         "COP31 deadlocked over fossil fuels",
         "Antalya talks run past deadline as the draft drops all mention of "
         "coal, oil and gas."),
        ("MEXICO  \u00b7  CARTELS",
         "Mexico captures FBI most-wanted kingpin",
         "El Chapo Isidro seized in Sinaloa; 11 dead as cartel gunmen hit back."),
        ("GULF  \u00b7  HORMUZ",
         "Three tankers hit near Hormuz",
         "Apparent Iranian strikes damage shipping; Bahrain reports a "
         "civilian site hit."),
        ("MARKETS",
         "Tech sell-off drags markets down",
         "S&P 500 falls 3.7% into correction; Nasdaq loses over 5%; "
         "Nikkei drops 5.06%."),
        ("PERU  \u00b7  QUAKE",
         "Strong quake shakes Peru",
         "A 6.7-magnitude earthquake strikes with no deaths reported."),
        ("NIGERIA",
         "Boat capsizes on way to funeral",
         "24 people die as a boat carrying mourners capsizes."),
        ("FRANCE  \u00b7  PROTESTS",
         "French protests enter sixth weekend",
         "Rallies over living costs and public services draw a lower turnout."),
    ]

    f_label = font(SANS_B, 16)
    f_head = font(SERIF_B, 24)
    f_fact = font(SANS, 17)
    gap_x, gap_y = 24, 14
    cell_w = (CONTENT_W - 2 * gap_x) // 3
    grid_top, grid_bottom = 414, 952
    cell_h = (grid_bottom - grid_top - 2 * gap_y) // 3

    for i, (label, head, fact) in enumerate(stories):
        r, c = divmod(i, 3)
        cx = x0 + c * (cell_w + gap_x)
        cy = grid_top + r * (cell_h + gap_y)
        rule(d, cx, cy, cx + cell_w, 2)
        cy += 10
        d.text((cx, cy), label, font=f_label, fill=RED)
        cy += 24
        head_lines = wrap(d, head, f_head, cell_w)
        assert len(head_lines) <= 3, "headline too long: %r" % head_lines
        cy = draw_lines(d, head_lines, f_head, cx, cy, INK, 29)
        cy += 4
        fact_lines = wrap(d, fact, f_fact, cell_w)
        assert len(fact_lines) <= 3, "fact too long: %r" % fact_lines
        cy = draw_lines(d, fact_lines, f_fact, cx, cy, (52, 50, 46), 22)
        assert cy <= grid_top + (r + 1) * (cell_h + gap_y) - gap_y, \
            "cell %d overflows: y=%d" % (i, cy)

    # ---- footer ---------------------------------------------------------
    rule(d, x0, 966, x1, 2)
    f_foot = font(SANS, 15)
    foot = ("Sources: CNN, AP, Reuters, Al Jazeera, Financial Times, "
            "Wall Street Journal, Times of Israel  \u00b7  22 Nov 2026")
    fw = d.textlength(foot, font=f_foot)
    d.text(((W - fw) / 2, 976), foot, font=f_foot, fill=GREY)

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out, "PNG", optimize=True)
    print("wrote", out, img.size, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
