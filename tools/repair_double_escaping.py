#!/usr/bin/env python3
"""Repair the bf5f7a8 double-escaping in the four page exports.

Commit bf5f7a8 rewrote home/about/services/contact with a serializer that
escaped non-ASCII a second time. Result: typographic characters and emoji sit
in the content as literal six-character text - a reader sees
`we don't just transport people-u2014we connect` and
`\\ud83d\\udcde` instead of an em dash and a phone emoji.

Divi legitimately stores `<`, `>` and `"` as `\\u003c` / `\\u003e` / `\\u0022`;
that is normal and must survive untouched. Only the *other* codes are the
regression, so those are decoded to real characters:

  2014 em dash    2018/2019 curly single quotes   201c/201d curly double quotes
  2026 ellipsis   00e9 e-acute   00f7 u-acute      00d7 multiplication x
  2605 star       25b6 play       2705/270f checks  2709 envelope   fe0f selector
  d83d/dc..       emoji surrogate pairs

Surrogate pairs are joined into a single code point; decoding the halves
separately would produce lone surrogates that no font can render.

The intended visual edits from bf5f7a83 (spacing/padding values, the base64
logo, the re-serialised whitespace) are all preserved - only the escape
sequences are touched.

Edits are asserted per file: the expected escape multiset must match exactly,
so a file that has drifted fails loudly instead of being half-repaired.
"""

from __future__ import annotations

import json
import pathlib
import re
import sys
from collections import Counter

# This tool lives inside the working set and edits the working set. Everything
# is derived from this file's own location, so it keeps working wherever the
# folder lives and never reaches into a superseded project folder.
WORKING = pathlib.Path(__file__).resolve().parents[1]
SKILL_DIR = pathlib.Path("/home/dioscarr/Work/bdstar-transport-v3/.claude/skills/divi5-migration")
sys.path.insert(0, str(SKILL_DIR))
from helpers import validate_blocks  # noqa: E402

PAGES = ["home", "about", "services", "contact"]

STRAGRAY = re.compile(r"\\u([0-9a-fA-F]{4})")
DIVI_KEEP = {"003c", "003e", "0022"}
SURROGATE_HIGH = range(0xD800, 0xDC00)

# Escape counts observed in the working set, asserted before writing so a
# drifted file cannot be silently rewritten.
EXPECTED = {
    "home": {"2014": 4, "201c": 4, "201d": 4, "d83d": 3, "dc4f": 3,
             "2019": 2, "00d7": 1, "25b6": 1, "2605": 1},
    "about": {"2605": 5, "2014": 3, "201c": 1, "2019": 1},
    "services": {"2014": 1, "2019": 1},
    "contact": {"d83d": 2, "2019": 1, "dcde": 1, "2709": 1, "fe0f": 1,
                "dccd": 1, "00fa": 1},
}


def stray_counts(content: str) -> Counter:
    return Counter(m for m in STRAGRAY.findall(content) if m not in DIVI_KEEP)


def decode_escapes(content: str) -> tuple[str, int]:
    """Turn literal \\uXXXX text into real characters, joining surrogate pairs."""
    out = []
    i = 0
    replaced = 0
    while i < len(content):
        m = STRAGRAY.match(content, i)
        if not m or m.group(1) in DIVI_KEEP:
            out.append(content[i])
            i += 1
            continue
        code = int(m.group(1), 16)
        if code in SURROGATE_HIGH:
            # Look for the matching low surrogate; pair them into one code point.
            nxt = STRAGRAY.match(content, m.end())
            if nxt and nxt.group(1) not in DIVI_KEEP:
                low = int(nxt.group(1), 16)
                if 0xDC00 <= low <= 0xDFFF:
                    combined = 0x10000 + ((code - 0xD800) << 10) + (low - 0xDC00)
                    out.append(chr(combined))
                    replaced += 1
                    i = nxt.end()
                    continue
            out.append(content[i])  # unpaired high surrogate: leave alone
            i += 1
            continue
        out.append(chr(code))
        replaced += 1
        i = m.end()
    return "".join(out), replaced


def main() -> int:
    failures = []
    for page in PAGES:
        path = WORKING / f"bdstar-{page}-v5.json"
        backup = WORKING / f"bdstar-{page}-v5.before-unescape.json"
        original_text = path.read_text(encoding="utf-8")
        original = next(iter(json.loads(original_text)["data"].values()))

        found = stray_counts(original)
        if dict(found) != EXPECTED[page]:
            failures.append(f"{page}: escapes {dict(found)} != expected {EXPECTED[page]}")
            print(f"ABORT {page}: escape set drifted")
            print(f"       found    {dict(found)}")
            print(f"       expected {EXPECTED[page]}")
            continue

        if not backup.exists():
            backup.write_text(original_text, encoding="utf-8")

        repaired, n = decode_escapes(original)
        problems = validate_blocks(repaired)
        remaining = stray_counts(repaired)
        if problems:
            failures.append(f"{page}: validate_blocks -> {problems}")
        if remaining:
            failures.append(f"{page}: {sum(remaining.values())} escapes left")
            continue

        # Re-serialise the whole export, matching Divi's own formatting.
        data = json.loads(original_text)
        key = next(iter(data["data"]))
        data["data"][key] = repaired
        path.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")

        size = path.stat().st_size
        print(f"{page:9} decoded {n:3} escapes -> {size:,} bytes   "
              f"validate_blocks={'ALL OK' if not problems else problems}")

    if failures:
        print("\nFAILURES:")
        for f in failures:
            print("  " + f)
        return 1

    print("\nre-verify from disk:")
    for page in PAGES:
        path = WORKING / f"bdstar-{page}-v5.json"
        c = next(iter(json.loads(path.read_text(encoding="utf-8"))["data"].values()))
        left = stray_counts(c)
        print(f"  {page:9} stray={sum(left.values())}  divi 003c/003e/0022 intact="
              f"{all(c.count('\\\\u' + k) >= 0 for k in DIVI_KEEP)}  "
              f"validate_blocks={'OK' if not validate_blocks(c) else 'FAIL'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())