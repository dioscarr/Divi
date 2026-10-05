#!/usr/bin/env python3
"""Refresh the homepage's Five-Star and Why Families feature sections."""

import json
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path


WORKING_SET = Path(__file__).resolve().parents[1]
TARGET = WORKING_SET / "bdstar-home-v5.json"
BACKUPS = WORKING_SET / ".backup"
SKILL_DIR = Path(
    "/home/dioscarr/Work/bdstar-transport-v3/.claude/skills/divi5-migration"
)
sys.path.insert(0, str(SKILL_DIR))
from helpers import split_sections, validate_blocks, validate_sections_balanced  # noqa: E402

from polish_home_card_grids import preserve_export_format, replacement_for  # noqa: E402


COMMENT_RE = re.compile(
    r"<!--\s*(?:wp:divi/(?P<kind>[\w-]+)\s+(?P<payload>\{.*?\})\s*(?P<self>/)?"
    r"|/(?P<close>wp:divi/[\w-]+))\s*-->",
    re.S,
)

CARD_SHADOW = {
    "desktop": {
        "value": {
            "style": "preset1",
            "horizontal": "0px",
            "vertical": "12px",
            "blur": "28px",
            "spread": "-10px",
            "position": "outer",
            "color": "rgba(20,22,48,0.18)",
        }
    }
}

PREVIOUS_CARD_SHADOW = {
    "desktop": {
        "value": {
            "style": "custom",
            "horizontal": "0px",
            "vertical": "8px",
            "blur": "24px",
            "spread": "-8px",
            "color": "rgba(20,22,48,0.22)",
        }
    }
}

IMAGE_SHADOW = {
    "desktop": {
        "value": {
            "style": "preset1",
            "horizontal": "0px",
            "vertical": "18px",
            "blur": "36px",
            "spread": "-14px",
            "position": "outer",
            "color": "rgba(20,22,48,0.18)",
        }
    }
}


def parse_blocks(content):
    nodes = []
    stack = []
    for match in COMMENT_RE.finditer(content):
        closing = match.group("close")
        if closing:
            expected = closing.removeprefix("wp:divi/")
            if not stack and expected == "placeholder":
                continue
            if not stack or stack[-1]["kind"] != expected:
                raise ValueError(f"Mismatched Divi block close for {expected!r}")
            stack.pop()
            continue

        node = {
            "kind": match.group("kind"),
            "block": json.loads(match.group("payload")),
            "start": match.start(),
            "end": match.end(),
            "parent": stack[-1] if stack else None,
        }
        nodes.append(node)
        if not match.group("self"):
            stack.append(node)

    if stack:
        raise ValueError(f"Unclosed Divi block: {stack[-1]['kind']}")
    return nodes


def section_for(nodes, content, needle):
    index = content.lower().find(needle.lower())
    if index < 0:
        raise ValueError(f"Could not find section anchor {needle!r}")
    sections = [
        node
        for node in nodes
        if node["kind"] == "section" and node["parent"] is None
    ]
    preceding = [node for node in sections if node["start"] <= index]
    if not preceding:
        raise ValueError(f"No section contains anchor {needle!r}")
    section = preceding[-1]
    following = [node for node in sections if node["start"] > section["start"]]
    end = following[0]["start"] if following else len(content)
    if index >= end:
        raise ValueError(f"Anchor {needle!r} is not inside its containing section")
    return section, end


def blocks_in_range(nodes, start, end, kind):
    return [
        node
        for node in nodes
        if node["kind"] == kind and start <= node["start"] < end
    ]


def module_of(node):
    return node["block"].setdefault("module", {})


def set_radius(border, radius):
    value = border.setdefault("desktop", {}).setdefault("value", {})
    value.setdefault("styles", {}).setdefault("all", {}).update(
        {"width": "1px", "color": "#d8dce4", "style": "solid"}
    )
    value["radius"] = {
        "sync": "on",
        "topLeft": radius,
        "topRight": radius,
        "bottomRight": radius,
        "bottomLeft": radius,
    }


def polish_card(node):
    decoration = module_of(node).setdefault("decoration", {})
    set_radius(decoration.setdefault("border", {}), "16px")
    legacy_shadow = decoration.pop("shadow", None)
    current_shadow = decoration.get("boxShadow")
    if current_shadow not in (None, CARD_SHADOW, PREVIOUS_CARD_SHADOW):
        raise ValueError("Five-Star card has an unexpected existing box shadow")
    decoration["boxShadow"] = CARD_SHADOW
    if not legacy_shadow and current_shadow is None:
        raise ValueError("Five-Star card has no existing shadow to migrate")


def polish_image(node, width, max_width, phone_width):
    module = module_of(node)
    advanced_sizing = (
        module.setdefault("advanced", {})
        .setdefault("sizing", {})
        .setdefault("desktop", {})
        .setdefault("value", {})
    )
    if advanced_sizing.get("forceFullwidth") not in (None, "on", "off"):
        raise ValueError("Image has an unexpected forceFullwidth value")
    advanced_sizing["forceFullwidth"] = "off"
    advanced_sizing["borderRadius"] = "18px"

    decoration = module.setdefault("decoration", {})
    sizing = decoration.setdefault("sizing", {})
    sizing.setdefault("desktop", {}).setdefault("value", {}).update(
        {"width": width, "maxWidth": max_width}
    )
    sizing.setdefault("tablet", {}).setdefault("value", {}).update(
        {"width": "84%", "maxWidth": max_width}
    )
    sizing.setdefault("phone", {}).setdefault("value", {}).update(
        {"width": phone_width, "maxWidth": "440px"}
    )
    set_radius(decoration.setdefault("border", {}), "18px")
    decoration["boxShadow"] = IMAGE_SHADOW

    image = node["block"].setdefault("image", {})
    image_decoration = image.setdefault("decoration", {})
    image_border = image_decoration.setdefault("border", {})
    image_border_value = (
        image_border.setdefault("desktop", {}).setdefault("value", {})
    )
    image_border_value["styles"] = {
        "all": {"width": "0px", "color": "rgba(0,0,0,0)"}
    }
    image_border_value["radius"] = {
        "sync": "on",
        "topLeft": "17px",
        "topRight": "17px",
        "bottomRight": "17px",
        "bottomLeft": "17px",
    }


def center_parent_column(node):
    parent = node["parent"]
    if not parent or parent["kind"] != "column":
        raise ValueError("Feature image is not a direct child of its expected column")
    layout = module_of(parent).setdefault("decoration", {}).setdefault("layout", {})
    for breakpoint in ("desktop", "tablet", "phone"):
        value = layout.setdefault(breakpoint, {}).setdefault("value", {})
        value.update(
            {
                "display": "flex",
                "flexDirection": "column",
                "alignItems": "center",
            }
        )


def refresh_five_star(nodes, content, edits):
    section, end = section_for(nodes, content, "5-star rated, licensed")
    section_nodes = [
        node for node in nodes if section["start"] <= node["start"] < end
    ]
    cards = []
    for node in blocks_in_range(section_nodes, section["start"], end, "blurb"):
        title = (
            node["block"]
            .get("title", {})
            .get("innerContent", {})
            .get("desktop", {})
            .get("value", {})
            .get("text")
        )
        if title in ("5★ TripAdvisor", "Licensed & Insured"):
            cards.append(node)
    if len(cards) != 2:
        raise ValueError(f"Expected the two Five-Star cards; found {len(cards)}")
    for card in cards:
        polish_card(card)
        edits.append(card)

    feature_rows = []
    for node in blocks_in_range(section_nodes, section["start"], end, "row-inner"):
        label = (
            module_of(node)
            .get("meta", {})
            .get("adminLabel", {})
            .get("desktop", {})
            .get("value")
        )
        if label == "Features":
            feature_rows.append(node)
    if len(feature_rows) != 1:
        raise ValueError(f"Expected one Five-Star Features row; found {len(feature_rows)}")
    gutter = (
        module_of(feature_rows[0])
        .setdefault("advanced", {})
        .setdefault("gutter", {})
    )
    for breakpoint, width in (("desktop", "3"), ("tablet", "2"), ("phone", "2")):
        gutter.setdefault(breakpoint, {}).setdefault("value", {})["width"] = width
    edits.append(feature_rows[0])

    images = []
    for node in blocks_in_range(section_nodes, section["start"], end, "image"):
        src = (
            node["block"]
            .get("image", {})
            .get("innerContent", {})
            .get("desktop", {})
            .get("value", {})
            .get("src", "")
        )
        if src.endswith("/transport2.png"):
            images.append(node)
    if len(images) != 1:
        raise ValueError(f"Expected the Five-Star side image; found {len(images)}")
    image = images[0]
    polish_image(image, "72%", "460px", "100%")
    center_parent_column(image)
    edits.extend((image, image["parent"]))


def refresh_why_families(nodes, content, edits):
    section, end = section_for(nodes, content, "Why Families Choose B.D Star Transport")
    section_nodes = [
        node for node in nodes if section["start"] <= node["start"] < end
    ]
    decoration = module_of(section).setdefault("decoration", {})
    background = decoration.setdefault("background", {})
    background.setdefault("desktop", {}).setdefault("value", {})["color"] = "#f7f7f7"

    feature_rows = []
    for node in blocks_in_range(section_nodes, section["start"], end, "row"):
        label = (
            module_of(node)
            .get("meta", {})
            .get("adminLabel", {})
            .get("desktop", {})
            .get("value")
        )
        if label == "Feature":
            feature_rows.append(node)
    if len(feature_rows) != 1:
        raise ValueError(f"Expected one Why Families feature row; found {len(feature_rows)}")
    row_sizing = (
        module_of(feature_rows[0])
        .setdefault("decoration", {})
        .setdefault("sizing", {})
    )
    row_sizing.setdefault("desktop", {}).setdefault("value", {}).update(
        {"width": "90%", "maxWidth": "1200px"}
    )
    row_sizing.setdefault("tablet", {}).setdefault("value", {}).update(
        {"width": "90%", "maxWidth": "1100px"}
    )
    row_sizing.setdefault("phone", {}).setdefault("value", {}).update(
        {"width": "92%", "maxWidth": "100%"}
    )
    edits.append(feature_rows[0])

    images = []
    for node in blocks_in_range(section_nodes, section["start"], end, "image"):
        src = (
            node["block"]
            .get("image", {})
            .get("innerContent", {})
            .get("desktop", {})
            .get("value", {})
            .get("src", "")
        )
        if src.endswith("/delvis.png"):
            images.append(node)
    if len(images) != 1:
        raise ValueError(f"Expected the Why Families feature image; found {len(images)}")
    image = images[0]
    polish_image(image, "92%", "560px", "100%")
    center_parent_column(image)
    edits.extend((image, image["parent"]))

    spacing = decoration.setdefault("spacing", {})
    for breakpoint, vertical in (("desktop", "56px"), ("phone", "32px")):
        padding = (
            spacing.setdefault(breakpoint, {})
            .setdefault("value", {})
            .setdefault("padding", {})
        )
        padding["top"] = vertical
        padding["bottom"] = vertical
    edits.append(section)


def main():
    original_text = TARGET.read_text(encoding="utf-8")
    data = json.loads(original_text)
    content = data["data"]["2"]
    nodes = parse_blocks(content)
    edits = []
    refresh_five_star(nodes, content, edits)
    refresh_why_families(nodes, content, edits)

    replacements = {}
    for node in edits:
        replacements[(node["start"], node["end"])] = replacement_for(
            content, node["start"], node["end"], node["block"]
        )
    updated_content = content
    for (start, end), replacement in sorted(replacements.items(), reverse=True):
        updated_content = updated_content[:start] + replacement + updated_content[end:]

    if updated_content == content:
        print(f"{TARGET} already has the requested image-element clipping.")
        return

    if updated_content == content:
        print(f"{TARGET} already has the requested feature-section refresh.")
        return

    errors = validate_blocks(updated_content)
    if errors:
        raise ValueError(f"Divi block validation failed: {errors}")
    sections = split_sections(updated_content)
    problems = validate_sections_balanced(sections, range(1, len(sections)))
    if problems:
        raise ValueError(f"Divi section validation failed: {problems}")

    BACKUPS.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    backup = BACKUPS / f"bdstar-home-v5.before-feature-refresh-{stamp}.json"
    shutil.copy2(TARGET, backup)
    TARGET.write_text(
        preserve_export_format(original_text, updated_content),
        encoding="utf-8",
    )
    print(f"Updated {TARGET}")
    print(f"Backup: {backup}")
    print("Refreshed two Five-Star cards, contained both feature images, and updated Why Families.")
    print("Divi block JSON and section-balance validation passed.")


if __name__ == "__main__":
    main()
