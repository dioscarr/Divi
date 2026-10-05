#!/usr/bin/env python3
"""Prepare and validate the editable Code-module backdrop settings for the home video modal."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


SOURCE = Path("/home/dioscarr/Work/divi-working-set/Modules/home/sections/01-hero.divi")
CODE_BLOCK_RE = re.compile(r"(<!-- wp:divi/code\s+)(\{.*?\})(\s+/-->)", re.S)
OLD_BACKDROP_RULE = (
    "#bdstar-video::backdrop{background:rgba(12,16,31,.80);"
    "backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);}"
)
BACKDROP_RULE = (
    "/* BACKDROP SETTINGS: edit only these two values in this Code module. */\n"
    "#bdstar-video{--bd-video-backdrop-color:rgba(12,16,31,.80);"
    "--bd-video-backdrop-blur:12px;}"
    "#bdstar-video::backdrop{background:var(--bd-video-backdrop-color);"
    "backdrop-filter:blur(var(--bd-video-backdrop-blur));"
    "-webkit-backdrop-filter:blur(var(--bd-video-backdrop-blur));}"
)
LEGACY_CONFIG_RE = re.compile(
    r'<script id="bd-video-backdrop-settings" type="application/json">.*?</script>\n?',
    re.S,
)
LEGACY_CONFIG_LOGIC_RE = re.compile(
    r"  var backdropSettings=document\.getElementById\('bd-video-backdrop-settings'\);"
    r".*?"
    r"  applyBackdropSettings\(\);\n",
    re.S,
)
UNCOMMENTED_BACKDROP_RULE = (
    "#bdstar-video{--bd-video-backdrop-color:rgba(12,16,31,.80);"
    "--bd-video-backdrop-blur:12px;}"
    "#bdstar-video::backdrop{background:var(--bd-video-backdrop-color);"
    "backdrop-filter:blur(var(--bd-video-backdrop-blur));"
    "-webkit-backdrop-filter:blur(var(--bd-video-backdrop-blur));}"
)
ADMIN_LABEL = "BD Video Modal — Backdrop (Code)"


def find_modal_block(text: str) -> tuple[re.Match[str], dict, str]:
    for match in CODE_BLOCK_RE.finditer(text):
        attrs = json.loads(match.group(2))
        label = (
            attrs.get("module", {})
            .get("meta", {})
            .get("adminLabel", {})
            .get("desktop", {})
            .get("value")
        )
        if label in {"BD Video Modal", ADMIN_LABEL}:
            content = attrs["content"]["innerContent"]["desktop"]["value"]
            return match, attrs, content
    raise SystemExit("BD Video Modal code module was not found")


def apply() -> None:
    with SOURCE.open("r", encoding="utf-8", newline="") as source:
        text = source.read()
    match, attrs, content = find_modal_block(text)
    content = LEGACY_CONFIG_RE.sub("", content)
    content = LEGACY_CONFIG_LOGIC_RE.sub("", content)
    if OLD_BACKDROP_RULE in content:
        content = content.replace(OLD_BACKDROP_RULE, BACKDROP_RULE, 1)
    elif UNCOMMENTED_BACKDROP_RULE in content:
        content = content.replace(UNCOMMENTED_BACKDROP_RULE, BACKDROP_RULE, 1)
    elif BACKDROP_RULE not in content:
        raise SystemExit("Expected default backdrop rule was not found")
    attrs["content"]["innerContent"]["desktop"]["value"] = content
    attrs["module"]["meta"]["adminLabel"]["desktop"]["value"] = ADMIN_LABEL
    replacement = match.group(1) + json.dumps(attrs, separators=(",", ":")) + match.group(3)
    with SOURCE.open("w", encoding="utf-8", newline="") as source:
        source.write(text[:match.start()] + replacement + text[match.end():])
    print(f"updated {SOURCE}")


def validate() -> None:
    with SOURCE.open("r", encoding="utf-8", newline="") as source:
        text = source.read()
    _, attrs, content = find_modal_block(text)
    label = attrs["module"]["meta"]["adminLabel"]["desktop"]["value"]
    if label != ADMIN_LABEL:
        raise SystemExit("Video modal Code module label is incorrect")
    if BACKDROP_RULE not in content:
        raise SystemExit("Backdrop CSS variables are missing")
    if "bd-video-backdrop-settings" in content or "applyBackdropSettings" in content:
        raise SystemExit("Unsupported faux Builder settings schema is still present")
    print("video modal Code-module backdrop workflow is valid")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("apply", "validate"))
    args = parser.parse_args()
    if args.command == "apply":
        apply()
    else:
        validate()


if __name__ == "__main__":
    main()
