#!/usr/bin/env python3
"""Generate Fly Media knowledge-base brand assets (Notion covers + icons).
Palette from the Fly Studio design system: canvas #0c0c0e, violet #8800e1 / #c27aff / #a855f7,
lime #90bc2a, text #e5e5e5 / #a1a1a1. Type: Saira (display, wide), Rubik (eyebrow/body), Geo (accent).
Usage: python3 make_assets.py            -> writes out/cover-<slug>.png and out/icon-<slug>.png
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "fonts")
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)

CANVAS = (12, 12, 14)        # #0c0c0e
VIOLET = (136, 0, 225)       # #8800e1
VIOLET_T = (194, 122, 255)   # #c27aff
VIOLET_M = (168, 85, 247)    # #a855f7
LIME = (144, 188, 42)        # #90bc2a
TXT = (229, 229, 229)        # #e5e5e5
TXT2 = (161, 161, 161)       # #a1a1a1
TXT3 = (115, 115, 115)       # #737373

def font(name, size, wght=None, wdth=None):
    f = ImageFont.truetype(os.path.join(FONTS, name), size)
    try:
        axes = f.get_variation_axes()
        vals = []
        for ax in axes:
            nm = ax.get("name", b"")
            nm = nm.decode() if isinstance(nm, bytes) else str(nm)
            tag = ax.get("tag", b"")
            tag = tag.decode() if isinstance(tag, bytes) else str(tag)
            key = (nm + tag).lower()
            if ("weight" in key or "wght" in key) and wght is not None: vals.append(wght)
            elif ("width" in key or "wdth" in key) and wdth is not None: vals.append(wdth)
            else: vals.append(ax["default"])
        if vals: f.set_variation_by_axes(vals)
    except Exception:
        pass
    return f

def glow(img, center, radius, color, strength=1.0):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    steps = 40
    for i in range(steps, 0, -1):
        r = radius * i / steps
        a = int(90 * strength * (1 - i / steps) ** 1.6)
        d.ellipse([center[0]-r, center[1]-r, center[0]+r, center[1]+r], fill=color + (a,))
    layer = layer.filter(ImageFilter.GaussianBlur(radius * 0.18))
    img.alpha_composite(layer)

def cover(slug, eyebrow, title, subtitle=None, accent=VIOLET_M):
    """Banner for Notion covers. Notion scales the image to the page width and crops a thin
    strip (~7:1 on wide screens) from the vertical middle, with the page icon over the
    bottom-centre. So: 3000x600 (5:1), every element inside the middle band (y 40%-60%),
    nothing in the lower-centre, and modest type; the page title is shown below anyway."""
    W, H = 3000, 600
    img = Image.new("RGBA", (W, H), CANVAS + (255,))
    glow(img, (int(W * 0.82), H // 2), 700, accent, 1.0)
    glow(img, (int(W * 0.12), H // 2), 520, VIOLET, 0.45)
    grid = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grid)
    for x in range(0, W, 120):
        gd.line([(x, 0), (x, H)], fill=(255, 255, 255, 9))
    for y in range(0, H, 120):
        gd.line([(0, y), (W, y)], fill=(255, 255, 255, 9))
    img.alpha_composite(grid)
    d = ImageDraw.Draw(img)
    cy = H // 2
    x = int(W * 0.08)
    # accent bar + eyebrow + title on one line, vertically centred
    f_eye = font("Rubik[wght].ttf", 30, wght=700)
    f_title = font("Saira[wdth,wght].ttf", 64, wght=600, wdth=112)
    d.rounded_rectangle([x, cy - 4, x + 56, cy + 4], radius=4, fill=accent)
    cx = x + 84
    eb = d.textbbox((0, 0), "A", font=f_eye)
    for ch in eyebrow.upper():
        d.text((cx, cy - (eb[3] - eb[1]) // 2 - eb[1]), ch, font=f_eye, fill=TXT3)
        cx += d.textlength(ch, font=f_eye) + 6
    cx += 40
    tb = d.textbbox((0, 0), title, font=f_title)
    d.text((cx, cy - (tb[3] - tb[1]) // 2 - tb[1]), title, font=f_title, fill=TXT)
    # wordmark, right, same band
    f_mark = font("Geo-Regular.ttf", 40)
    mark = "FLY MEDIA"
    mw = d.textlength(mark, font=f_mark)
    mb = d.textbbox((0, 0), mark, font=f_mark)
    d.text((W - int(W * 0.08) - mw, cy - (mb[3] - mb[1]) // 2 - mb[1]), mark, font=f_mark, fill=VIOLET_T)
    img.convert("RGB").save(os.path.join(OUT, f"cover-{slug}.png"), optimize=True)

def icon(slug, glyph, accent=None):
    S = 280
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    base = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(base)
    # radial violet gradient inside rounded square
    grad = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grad)
    for i in range(S, 0, -2):
        t = i / S
        c = tuple(int(VIOLET_M[k] * (1 - t) + VIOLET[k] * t) for k in range(3))
        gd.ellipse([S/2 - i, S/2 - i, S/2 + i, S/2 + i], fill=c + (255,))
    mask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, S-1, S-1], radius=64, fill=255)
    img.paste(grad, (0, 0), mask)
    d = ImageDraw.Draw(img)
    f = font("Saira[wdth,wght].ttf", 168, wght=700, wdth=110)
    bbox = d.textbbox((0, 0), glyph, font=f)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    d.text(((S - tw) / 2 - bbox[0], (S - th) / 2 - bbox[1] - 6), glyph, font=f, fill=(255, 255, 255, 255))
    if accent:
        d.ellipse([S - 70, S - 70, S - 34, S - 34], fill=accent + (255,), outline=CANVAS + (255,), width=6)
    img.save(os.path.join(OUT, f"icon-{slug}.png"), optimize=True)

PAGES = [
    ("home", "Company", "Fly Media", "Who we are, how we are organised, how we work"),
    ("leadership", "Leadership", "Leadership", "Weekly meeting, agenda, tracker"),
    ("engineering", "Area", "Engineering", "Development and Data"),
    ("updates", "Company database", "Updates", "One row per area per week"),
    ("decisions", "Company database", "Decisions", "What changed how another area works"),
    ("requests", "Company database", "Requests", "Asking another area for something"),
    ("meetings", "Leadership", "Meetings", "The weekly page"),
    ("agenda", "Leadership", "Agenda", "Four selections and one sentence"),
    ("tracker", "Leadership", "Tracker", "One owner, one deadline"),
    ("onboarding", "Start here", "Onboarding", "Your first week"),
    ("templates", "Company", "Templates", "How each page and row is written"),
    ("area", "Area", "<Area>", "Template cover for any area"),
    ("rd", "Area", "R&D", "Applied Research and AI Creative"),
    ("setup", "Start here", "Set up your area", "Your teamspace in 45 minutes"),
    ("people", "Area", "People", "Hiring, onboarding, careers, culture"),
    ("legal", "Area", "Legal", "Contracts, IP rights, corporate"),
    ("preboarding", "Welcome", "Before day one", "What to read, watch and set up"),
]
ICONS = [("home", "F", LIME), ("leadership", "L", None), ("engineering", "E", None), ("updates", "U", None),
         ("decisions", "D", None), ("requests", "R", None), ("meetings", "M", None), ("agenda", "A", None),
         ("tracker", "T", None), ("onboarding", "S", LIME), ("templates", "Tp", None), ("rd", "R", None), ("setup", "S", None), ("people", "P", None), ("legal", "Lg", None), ("preboarding", "W", LIME)]

if __name__ == "__main__":
    for slug, eye, title, sub in PAGES:
        cover(slug, eye, title, sub)
    for slug, g, acc in ICONS:
        icon(slug, g, acc)
    print("\n".join(sorted(os.listdir(OUT))))
