#!/usr/bin/env python3
"""Polish the homepage's Divi 5 service-card modules using native settings."""

import argparse
import json
import re
import shutil
import sys
from copy import deepcopy
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


BLOCK_RE = re.compile(r"<!-- wp:divi/([\w-]+)\s+(\{.*?\})\s*/?-->", re.S)


def blocks_of_type(content, block_type):
    for match in BLOCK_RE.finditer(content):
        if match.group(1) == block_type:
            yield match.start(), match.end(), match.group(2), json.loads(match.group(2))


def set_full_height(block):
    sizing = (
        block.setdefault("module", {})
        .setdefault("decoration", {})
        .setdefault("sizing", {})
    )
    desktop = sizing.setdefault("desktop", {}).setdefault("value", {})
    if desktop.get("height") not in (None, "100%"):
        raise ValueError(f"Unexpected existing card height: {desktop['height']!r}")
    if desktop.get("minHeight") not in (None, "100%"):
        raise ValueError(f"Unexpected existing card minHeight: {desktop['minHeight']!r}")
    desktop.pop("minHeight", None)
    desktop["width"] = "100%"
    desktop["height"] = "100%"


def remove_stale_grid_class(block):
    module = block.get("module", {})
    for attributes in (
        module.get("attributes", {})
        .get("desktop", {})
        .get("value", {})
        .get("attributes", []),
        module.get("decoration", {})
        .get("attributes", {})
        .get("desktop", {})
        .get("value", {})
        .get("attributes", []),
    ):
        for item in list(attributes):
            if item.get("name") != "class":
                continue
            classes = item.get("value", "").split()
            if "bd-premium-services-grid" not in classes:
                continue
            classes.remove("bd-premium-services-grid")
            if classes:
                item["value"] = " ".join(classes)
            else:
                attributes.remove(item)


def style_blurb(block, column_border, column_shadow):
    module = block.setdefault("module", {})
    decoration = module.setdefault("decoration", {})

    background = decoration.setdefault("background", {})
    desktop_background = background.setdefault("desktop", {}).setdefault("value", {})
    existing_color = desktop_background.get("color")
    if existing_color not in (None, "#ffffff"):
        raise ValueError(f"Unexpected card background: {existing_color!r}")
    desktop_background["color"] = "#ffffff"

    border = decoration.setdefault("border", {})
    existing_border = border.get("desktop", {}).get("value", {})
    existing_width = existing_border.get("styles", {}).get("all", {}).get("width")
    if column_border is not None:
        if "desktop" not in column_border:
            raise ValueError("Card column border has no desktop values")
        if existing_width not in (None, "0px"):
            raise ValueError("Blurb already has a visible border; refusing to overwrite it")
        border["desktop"] = deepcopy(column_border["desktop"])
        border["desktop"]["value"]["styles"]["all"]["color"] = "#e0e0e0"
    else:
        radius = existing_border.get("radius", {})
        if existing_width != "1px" or any(
            radius.get(corner) != "12px"
            for corner in ("topLeft", "topRight", "bottomRight", "bottomLeft")
        ):
            raise ValueError("Existing blurb border is not the expected 1px/12px card border")

    if (
        "boxShadow" in decoration
        and column_shadow is not None
        and decoration["boxShadow"] != column_shadow
    ):
        raise ValueError("Blurb already has a different shadow; refusing to overwrite it")
    if "boxShadow" not in decoration:
        if not column_shadow:
            raise ValueError("Card has no shadow on either module or column")
        decoration["boxShadow"] = column_shadow
    set_full_height(block)


def replacement_for(original_html, start, end, block):
    comment = original_html[start:end]
    brace = comment.find("{")
    if brace < 0:
        raise ValueError("Divi block comment is missing its JSON payload")
    prefix = comment[:brace]
    suffix = " /-->" if comment.rstrip().endswith("/-->") else " -->"
    return prefix + json.dumps(block, ensure_ascii=False, separators=(",", ":")) + suffix


def preserve_export_format(reference_text, payload):
    match = re.search(r'("data"\s*:\s*\{\s*"2"\s*:\s*)', reference_text)
    if not match:
        raise ValueError("Reference export does not contain data[2]")

    value_start = match.end()
    reference_payload, value_end = json.JSONDecoder().raw_decode(
        reference_text, value_start
    )
    if not isinstance(reference_payload, str):
        raise ValueError("Reference data[2] is not a string")
    encoded_reference = reference_text[value_start + 1 : value_end - 1]
    if encoded_reference != json.dumps(reference_payload, ensure_ascii=False)[1:-1]:
        raise ValueError("Reference payload is not in the canonical Divi JSON encoding")

    updated_text = (
        reference_text[:value_start]
        + json.dumps(payload, ensure_ascii=False)
        + reference_text[value_end:]
    )
    if json.loads(updated_text)["data"]["2"] != payload:
        raise ValueError("Format-preserving serialization changed the payload")
    return updated_text


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--preserve-from",
        type=Path,
        help="restore the original outer export format from a backup, keeping current data[2]",
    )
    args = parser.parse_args()

    if args.preserve_from:
        current = json.loads(TARGET.read_text(encoding="utf-8"))
        reference = args.preserve_from.read_text(encoding="utf-8")
        preserved = preserve_export_format(reference, current["data"]["2"])
        TARGET.write_text(preserved, encoding="utf-8")
        print(f"Restored outer export format in {TARGET}")
        return

    original_text = TARGET.read_text(encoding="utf-8")
    data = json.loads(original_text)
    content = data["data"]["2"]
    replacements = []
    rows_updated = 0
    cards_updated = 0
    shadows = []

    for row_start, row_end, _, row in blocks_of_type(content, "row"):
        module = row.get("module", {})
        structure = (
            module.get("advanced", {})
            .get("columnStructure", {})
            .get("desktop", {})
            .get("value")
        )
        if structure != "1_3,1_3,1_3":
            continue

        row_close = content.find("<!-- /wp:divi/row -->", row_end)
        if row_close < 0:
            raise ValueError(f"Unclosed 3-column row at {row_start}")
        row_body = content[row_end:row_close]
        columns = list(blocks_of_type(row_body, "column"))
        if len(columns) != 3:
            continue

        card_columns = []
        for col_start, col_end, _, column in columns:
            col_module = column.get("module", {})
            col_type = (
                col_module.get("advanced", {})
                .get("type", {})
                .get("desktop", {})
                .get("value")
            )
            col_decoration = col_module.get("decoration", {})
            col_end_tag = row_body.find("<!-- /wp:divi/column -->", col_end)
            if col_end_tag < 0:
                raise ValueError(f"Unclosed column at row offset {col_start}")
            column_body = row_body[col_end:col_end_tag]
            blurbs = list(blocks_of_type(column_body, "blurb"))
            if col_type != "1_3" or len(blurbs) != 1:
                card_columns = []
                break
            blurb_decoration = blurbs[0][3].get("module", {}).get("decoration", {})
            blurb_border = (
                blurb_decoration.get("border", {})
                .get("desktop", {})
                .get("value", {})
            )
            blurb_width = (
                blurb_border.get("styles", {})
                .get("all", {})
                .get("width")
            )
            if "border" not in col_decoration and blurb_width != "1px":
                card_columns = []
                break
            card_columns.append(
                (
                    col_start,
                    col_end,
                    column,
                    col_decoration,
                    blurbs[0],
                    col_end_tag,
                )
            )

        if len(card_columns) != 3:
            continue
        if (
            module.get("advanced", {})
            .get("gutter", {})
            .get("desktop", {})
            .get("value", {})
            .get("makeEqual")
            != "on"
        ):
            raise ValueError("Service-card row does not use equal-height columns")

        row_decoration = module.setdefault("decoration", {})
        remove_stale_grid_class(row)
        spacing = row_decoration.setdefault("spacing", {})
        for breakpoint, vertical in (("desktop", "20px"), ("phone", "12px")):
            value = spacing.setdefault(breakpoint, {}).setdefault("value", {})
            padding = value.setdefault("padding", {})
            padding["top"] = vertical
            padding["bottom"] = vertical

        for col_start, col_end, column, col_decoration, blurb_info, _ in card_columns:
            column_shadow = col_decoration.pop("boxShadow", None)
            column_border = col_decoration.pop("border", None)

            local_blurb_start, local_blurb_end, _, blurb = blurb_info
            style_blurb(blurb, column_border, column_shadow)
            shadows.append(blurb["module"]["decoration"]["boxShadow"])
            global_blurb_start = row_end + col_end + local_blurb_start
            global_blurb_end = row_end + col_end + local_blurb_end
            replacements.append(
                (
                    global_blurb_start,
                    global_blurb_end,
                    replacement_for(
                        content, global_blurb_start, global_blurb_end, blurb
                    ),
                )
            )

            global_col_start = row_end + col_start
            global_col_end = row_end + col_end
            replacements.append(
                (
                    global_col_start,
                    global_col_end,
                    replacement_for(content, global_col_start, global_col_end, column),
                )
            )
            cards_updated += 1

        replacements.append(
            (row_start, row_end, replacement_for(content, row_start, row_end, row))
        )
        rows_updated += 1

    if rows_updated != 3 or cards_updated != 9:
        raise ValueError(
            f"Expected 3 service-card rows/9 cards; found {rows_updated}/{cards_updated}"
        )
    if any(shadow != shadows[0] for shadow in shadows[1:]):
        raise ValueError("Card columns do not share one shadow style")

    updated_content = content
    for start, end, replacement in sorted(replacements, reverse=True):
        updated_content = updated_content[:start] + replacement + updated_content[end:]

    if updated_content == content:
        print(f"{TARGET} already has the corrected 9-card treatment.")
        return

    data["data"]["2"] = updated_content
    validation_content = data["data"]["2"]
    if validate_blocks(validation_content):
        raise ValueError(f"Divi block validation failed: {validate_blocks(validation_content)}")
    sections = split_sections(validation_content)
    section_indices = range(1, len(sections))
    section_problems = validate_sections_balanced(sections, section_indices)
    if section_problems:
        raise ValueError(f"Divi section validation failed: {section_problems}")

    BACKUPS.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = BACKUPS / f"bdstar-home-v5.before-card-polish-{stamp}.json"
    shutil.copy2(TARGET, backup)
    TARGET.write_text(
        preserve_export_format(original_text, updated_content),
        encoding="utf-8",
    )
    print(f"Updated {TARGET}")
    print(f"Backup: {backup}")
    print(f"Polished {cards_updated} service cards across {rows_updated} rows.")
    print("Divi block JSON and section-balance validation passed.")


if __name__ == "__main__":
    main()
