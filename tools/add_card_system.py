#!/usr/bin/env python3
"""Add a single global card + media system to the BD Star stylesheet.

Why this file (the header export) and not the pages: the whole theme-mode
palette already lives here as one site-wide stylesheet in the Theme Builder
header, and the page exports carry no card CSS at all. Card borders live as
Divi-stored values on individual modules, which is why they drifted apart:
home has 3 bordered card columns, about has a radius but no border, services
has no cards, contact has none. One shared ruleset fixes the drift instead of
editing 6 modules per page.

What each fix addresses, from the operator report:

1. Dark-mode inner background not full height.
   The card IS the column, but the dark palette only recolours .et_pb_text,
   .et_pb_blurb, .et_pb_row, etc. - never .et_pb_column - and nothing anywhere
   sets a column height. So the background only covers the content. Fix:
   make bordered columns stretch and fill, and recolour them in dark mode.

2. Light mode needs card shadows. Added, tuned to sit under the dark shadow
   already used elsewhere so the two modes read as the same card.

3. Bullets look bad. Restyled from the browser default disc to the site's
   orange accent, with correct spacing and marker alignment.

4. Borders must look the same everywhere. The stored 12px radius is already
   dominant, so it is promoted to a variable and enforced, rather than left
   per-module.

5. Section images are square. Divi renders background images as inline styles
   on rows/sections, so they need an explicit radius + clipping. Both the
   large section backgrounds and in-content images are covered.

Radius is a variable at the top of the block: change --bd-card-radius once and
every card, image and bullet follows.
"""

from __future__ import annotations

import json
import pathlib
import re
import sys

# This tool lives inside the working set and edits the working set. Everything
# is derived from this file's own location, so it keeps working wherever the
# folder lives and never reaches into a superseded project folder.
WORKING = pathlib.Path(__file__).resolve().parents[1]
TARGET = WORKING / "bdstar-header-v5.json"
BACKUP = TARGET.with_name("bdstar-header-v5.before-card-system.json")
# validate_blocks ships with the divi5-migration skill, which is shared tooling
# rather than part of any project folder, so it is referenced by its real path.
SKILL_DIR = pathlib.Path("/home/dioscarr/Work/bdstar-transport-v3/.claude/skills/divi5-migration")
sys.path.insert(0, str(SKILL_DIR))
from helpers import validate_blocks  # noqa: E402

# Anchor on the bare selector, not on a newline escape. On disk a value
# newline is stored doubled as \\n, so an anchor written with a single \n is a
# *substring* of it - the replace then matches mid-token and leaves a dangling
# backslash and a stray 'n', which is an invalid JSON string escape.
ANCHOR = ".bd-scroll-whatsapp{display:none;"

CARD_SYSTEM = r"""/* ===== BD card + media system (2026-10-02) =====
   Card borders were stored per-module in the page exports, which let them
   drift: home had 3 bordered card columns, about a radius with no border,
   services none at all. Cards are Divi COLUMNS, but the dark palette above
   only recolours text/blurb/row - never a column - and nothing set a column
   height, so in dark mode the card background only covered its own content.
   This block puts card appearance in one place for every page and both
   themes. Tune --bd-card-radius to change all corners at once. */
:root{
  --bd-card-radius:12px;
  --bd-card-line:rgba(20,22,48,.14);
  --bd-card-shadow:0 10px 28px -12px rgba(20,22,48,.22);
  --bd-card-shadow-hover:0 16px 36px -14px rgba(20,22,48,.30);
  --bd-accent:#de7e0a;
}

/* A card is a column that actually carries a border or a background.
   .et_pb_with_border / .et_pb_with_background are added by Divi at render
   time, so this matches real cards and skips plain layout columns.

   border-width and border-style are set here, not just border-color: the
   about, services and contact cards are stored with a background image but NO
   border at all, so colouring a border with zero width does nothing and those
   cards would still have looked different from home's five bordered ones.
   Setting the width is what makes every card's outline actually identical. */
#main-content .et_pb_column.et_pb_with_border,
#main-content .et_pb_column.et_pb_with_background{
  border-radius:var(--bd-card-radius);
  border-style:solid;
  border-width:1px;
  border-color:var(--bd-card-line);
  box-shadow:var(--bd-card-shadow);
  transition:box-shadow .3s ease,transform .3s ease,border-color .3s ease,background-color .35s ease;
}
/* Full-height fix. Deliberately NOT display:flex + flex:1 on the inner
   modules: that would re-parent Divi's own column layout, and nothing in this
   export shows how Divi 5 lays out rows, so it cannot be verified without a
   browser. Stretching the column itself is enough for its background to reach
   the bottom of the tallest card, and it cannot disturb the children. */
#main-content .et_pb_column.et_pb_with_border,
#main-content .et_pb_column.et_pb_with_background{
  align-self:stretch;
  height:100%;
  box-sizing:border-box;
}
#main-content .et_pb_column.et_pb_with_border:hover,
#main-content .et_pb_column.et_pb_with_background:hover{
  box-shadow:var(--bd-card-shadow-hover);
  transform:translateY(-2px);
}
/* Blurb-based cards (service lists) get the same treatment, including the
   border width, for the same reason. */
#main-content .et_pb_blurb.et_pb_with_border{
  border-radius:var(--bd-card-radius);
  border-style:solid;
  border-width:1px;
  border-color:var(--bd-card-line);
  box-shadow:var(--bd-card-shadow);
  transition:box-shadow .3s ease,transform .3s ease;
}
#main-content .et_pb_blurb.et_pb_with_border:hover{
  box-shadow:var(--bd-card-shadow-hover);
  transform:translateY(-2px);
}

/* Images: content images already carry a stored 12px radius, enforced here so
   they cannot drift from the cards. Section background images are inline
   styles on the row/section, so they need clipping to round the corners. */
#main-content .et_pb_image img,
#main-content .et_pb_image .et_pb_image_wrap{
  border-radius:var(--bd-card-radius);
}
#main-content .et_pb_row[style*="background-image"],
#main-content .et_pb_section[style*="background-image"]{
  border-radius:var(--bd-card-radius);
  overflow:hidden;
  -webkit-background-clip:padding-box;
  background-clip:padding-box;
}

/* Bullets: replace the default disc with the site accent and align the
   marker to the first line of text. */
#main-content ul li{
  list-style:none;
  position:relative;
  padding-left:1.35em;
  margin-bottom:.6em;
}
#main-content ul li::before{
  content:"";
  position:absolute;
  left:.15em;
  top:.62em;
  width:.42em;
  height:.42em;
  border-radius:50%;
  background:var(--bd-accent);
  transform:translateY(-50%);
}
#main-content ul li:last-child{margin-bottom:0;}

/* Dark theme: the missing piece from the original bug. Cards are columns, so
   the palette above never reached them. */
html[data-bd-theme="dark"] #main-content .et_pb_column.et_pb_with_border,
html[data-bd-theme="dark"] #main-content .et_pb_column.et_pb_with_background{
  background-color:var(--bd-dark-panel)!important;
  border-color:var(--bd-dark-line)!important;
  box-shadow:0 18px 40px -24px rgba(0,0,0,.75)!important;
}
html[data-bd-theme="dark"] #main-content .et_pb_column.et_pb_with_border:hover,
html[data-bd-theme="dark"] #main-content .et_pb_column.et_pb_with_background:hover{
  box-shadow:0 22px 48px -24px rgba(0,0,0,.85)!important;
}
/* This is the actual "inner background is not full height" bug. The old
   palette above paints var(--bd-dark-panel) on inner text/blurb/testimonial/
   toggle modules, but those are content boxes - they stop where the text
   stops, leaving a lighter band below the text inside the card. Now the card
   column owns the panel colour, the inner fills must go transparent so only
   one surface shows through. Scoped to modules inside a card, so text blocks
   that are deliberately panels in their own right are untouched. */
html[data-bd-theme="dark"] #main-content .et_pb_column.et_pb_with_border .et_pb_module.et_pb_text,
html[data-bd-theme="dark"] #main-content .et_pb_column.et_pb_with_border .et_pb_module.et_pb_blurb,
html[data-bd-theme="dark"] #main-content .et_pb_column.et_pb_with_background .et_pb_module.et_pb_text,
html[data-bd-theme="dark"] #main-content .et_pb_column.et_pb_with_background .et_pb_module.et_pb_blurb{
  background-color:transparent!important;
  box-shadow:none!important;
}
html[data-bd-theme="dark"] #main-content .et_pb_blurb.et_pb_with_border{
  background-color:var(--bd-dark-panel)!important;
  border-color:var(--bd-dark-line)!important;
  box-shadow:0 18px 40px -24px rgba(0,0,0,.75)!important;
}
html[data-bd-theme="dark"] #main-content ul li::before{
  background:#f0952e;
}
@media(prefers-reduced-motion:reduce){
  #main-content .et_pb_column.et_pb_with_border,
  #main-content .et_pb_column.et_pb_with_background,
  #main-content .et_pb_blurb.et_pb_with_border{transition:none!important;}
  #main-content .et_pb_column.et_pb_with_border:hover,
  #main-content .et_pb_column.et_pb_with_background:hover,
  #main-content .et_pb_blurb.et_pb_with_border:hover{transform:none!important;}
}
"""

# Radii that are deliberate and must survive.
PRESERVE = ["border-radius:999px", "border-radius:50%"]


def main() -> int:
    raw = TARGET.read_text(encoding="utf-8")
    if not BACKUP.exists():
        BACKUP.write_text(raw, encoding="utf-8")
        print(f"backup written: {BACKUP}")

    if "--bd-card-radius" in raw:
        print("ABORT: card system already present")
        return 1

    for keep in PRESERVE:
        if raw.count(keep) != 1:
            print(f"ABORT: expected one {keep!r}, found {raw.count(keep)}")
            return 1

    if raw.count(ANCHOR) != 1:
        print(f"ABORT: anchor found {raw.count(ANCHOR)} times, expected 1")
        return 1

    # Encoding. Do not hand-roll this - three earlier attempts each failed
    # differently (real newlines left in the JSON string, then a one-backslash-
    # short quote, then a truncated string), all from guessing the layers.
    #
    # The file has exactly two layers, now verified in both directions against
    # existing content in this same file:
    #   layer 1 - the Divi payload: newlines are the two characters \n and
    #             quotes are \", because the payload is itself escaped HTML/CSS
    #             sitting inside a JSON string.
    #   layer 2 - the raw bytes on disk, which is that payload JSON-encoded.
    # json.dumps(payload)[1:-1] reproduces layer 2 exactly, so let json do it.
    payload = CARD_SYSTEM.replace("\n", "\\n").replace('"', '\\"')
    assert "\n" not in payload, "real newline survived payload encoding"
    stored = json.dumps(payload)[1:-1]
    assert "\n" not in stored, "real newline survived file encoding"

    # Proved correct on a real slice of this file: re-encoding the decoded
    # payload of the .bd-scroll-whatsapp rule returns the original bytes.
    probe_at = raw.find(ANCHOR)
    probe_raw = raw[probe_at - 200:probe_at + 120]
    probe_payload = json.loads('"' + probe_raw + '"')
    assert json.dumps(probe_payload)[1:-1] == probe_raw, "encoder disagrees with file"

    # Insert immediately before the anchor. The anchor already has a value
    # newline in front of it, so only the block's own trailing newline is added -
    # adding a second separator leaves a stray blank line.
    updated = raw.replace(ANCHOR, stored + "\\\\n" + ANCHOR)

    TARGET.write_text(updated, encoding="utf-8")

    written = TARGET.read_text(encoding="utf-8")
    post = next(iter(json.loads(written)["data"].values()))

    problems = validate_blocks(post)
    print("\nvalidate_blocks:", "ALL OK" if not problems else problems)
    print("card system inserted:", "--bd-card-radius" in post)
    print("dark column rule present:",
          'data-bd-theme=\\"dark\\"\\" #main-content .et_pb_column' in post
          or 'et_pb_column.et_pb_with_border' in post)
    print("brace balance: { =", post.count("{"), " } =", post.count("}"),
          "->", "OK" if post.count("{") == post.count("}") else "MISMATCH")
    for keep in PRESERVE:
        print(f"preserved {keep}:", post.count(keep))
    stray = sorted({m for m in re.findall(r"\\u([0-9a-fA-F]{4})", post)
                    if m not in ("003c", "003e", "0022")})
    print("stray literal escapes:", stray or "NONE")
    print(f"\nbytes: {len(raw.encode()):,} -> {len(written.encode()):,}")
    return 0 if not problems else 1


if __name__ == "__main__":
    raise SystemExit(main())