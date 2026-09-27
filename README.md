# atlas-assets

Public brand assets for Fly Media's knowledge base in Notion (covers and icons), plus the generator.
Notion page covers must be public URLs, which is why this repo is public. Nothing here is confidential:
page titles on a dark background in the brand palette.

- `brand/out/` — generated PNGs. Covers 1500×600, icons 280×280.
- `brand/make_assets.py` — regenerates everything (`python3 brand/make_assets.py`). Edit `PAGES` / `ICONS` to add an area.
- `brand/fonts/` — Saira, Geo, Rubik (Google Fonts, OFL).

Palette (Fly Studio design system): canvas `#0c0c0e`, violet `#8800e1` / `#c27aff` / `#a855f7`, lime `#90bc2a`.

Raw URL pattern used by Notion: `https://raw.githubusercontent.com/Fly-Media-AI/atlas-assets/main/brand/out/<file>.png`
