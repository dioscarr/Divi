#!/usr/bin/env python3
"""Split/compile BD Star Divi 5 exports into editable module files.

This tool is intentionally conservative for Divi 5:
- It does not reinterpret module settings.
- It preserves each block as original Gutenberg/Divi comment markup.
- It preserves the original JSON export wrapper as a raw template and only
  replaces the exact data payload string at compile time.
- It validates basic Divi block balance before writing compiled exports.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

BASE = Path('/home/dioscarr/Work/divi-working-set')
MODULES = BASE / 'Modules'
EXPORTS = {
    'home': BASE / 'bdstar-home-v5.json',
    'about': BASE / 'bdstar-about-v5.json',
    'services': BASE / 'bdstar-services-v5.json',
    'contact': BASE / 'bdstar-contact-v5.json',
    'header': BASE / 'bdstar-header-v5.json',
    'footer': BASE / 'bdstar-footer-v5.json',
}
OPEN_RE = re.compile(r'<!--\s*wp:divi/([A-Za-z0-9-]+)')
CLOSE_RE = re.compile(r'<!--\s*/wp:divi/([A-Za-z0-9-]+)\s*-->')
BLOCK_HEADER_RE = re.compile(r'<!--\s*wp:divi/([A-Za-z0-9-]+)(.*?)-->', re.S)
LABEL_RE = re.compile(r'"adminLabel"\s*:\s*\{\s*"desktop"\s*:\s*\{\s*"value"\s*:\s*"([^"]+)"')
PLACEHOLDER = '__DIVI_MODULES_PAYLOAD__'


@dataclass
class Part:
    kind: str
    file: str | None = None
    text: str | None = None
    label: str | None = None


def slugify(text: str, fallback: str) -> str:
    text = re.sub(r'\\u[0-9a-fA-F]{4}', '', text)
    text = re.sub(r'[^A-Za-z0-9]+', '-', text).strip('-').lower()
    return text[:70] or fallback


def read_text_exact(path: Path) -> str:
    with path.open('r', encoding='utf-8', newline='') as f:
        return f.read()


def write_text_exact(path: Path, text: str) -> None:
    with path.open('w', encoding='utf-8', newline='') as f:
        f.write(text)


def load_export(path: Path) -> tuple[str, str, str, str]:
    raw = read_text_exact(path)
    data = json.loads(raw)
    if not isinstance(data.get('data'), dict) or len(data['data']) != 1:
        raise SystemExit(f'{path.name}: expected exactly one data payload key')
    layout_id, payload = next(iter(data['data'].items()))
    if not isinstance(payload, str):
        raise SystemExit(f'{path.name}: data payload is not a string')
    encoded_candidates = [
        json.dumps(payload, ensure_ascii=True),
        json.dumps(payload, ensure_ascii=False),
        json.dumps(payload, ensure_ascii=True, separators=(',', ':')),
        json.dumps(payload, ensure_ascii=False, separators=(',', ':')),
    ]
    encoded_candidates += [candidate.replace('/', '\\/') for candidate in list(encoded_candidates)]
    template = None
    for encoded in encoded_candidates:
        if raw.count(encoded) == 1:
            template = raw.replace(encoded, json.dumps(PLACEHOLDER), 1)
            break
    if template is None:
        raise SystemExit(f'{path.name}: could not locate exact encoded payload in raw JSON')
    return raw, layout_id, payload, template


def read_payload_from_template(template_path: Path, payload: str) -> str:
    template = read_text_exact(template_path)
    encoded = json.dumps(payload, ensure_ascii=True)
    out = template.replace(json.dumps(PLACEHOLDER), encoded, 1)
    if PLACEHOLDER in out:
        raise SystemExit(f'{template_path}: placeholder replacement failed')
    return out


def scan_divi_balance(payload: str) -> tuple[bool, list[str]]:
    stack: list[str] = []
    errors: list[str] = []
    decoder = json.JSONDecoder()
    i = 0
    while True:
        mo = OPEN_RE.search(payload, i)
        mc = CLOSE_RE.search(payload, i)
        if not mo and not mc:
            break
        if mo and (not mc or mo.start() < mc.start()):
            name = mo.group(1)
            pos = mo.end()
            window = payload[pos:pos + 256]
            stripped = window.lstrip()
            ws = len(window) - len(stripped)
            if stripped.startswith('{'):
                try:
                    _, end = decoder.raw_decode(payload, pos + ws)
                except json.JSONDecodeError as exc:
                    errors.append(f'JSON attrs decode failed for {name} at {pos}: {exc}')
                    i = mo.end()
                    continue
                suffix = payload[end:end + 6]
                selfclose = suffix.startswith(' /-->')
                if not (suffix.startswith(' -->') or selfclose):
                    errors.append(f'Unexpected block suffix for {name}: {suffix!r}')
            else:
                m = re.match(r'\s*(/)?-->', payload[pos:pos + 64])
                if not m:
                    errors.append(f'Cannot parse block header for {name} at {pos}')
                    i = mo.end()
                    continue
                selfclose = bool(m.group(1))
            if not selfclose:
                stack.append(name)
            i = mo.end()
        else:
            name = mc.group(1)
            if not stack or stack[-1] != name:
                errors.append(f'Mismatched close {name}, stack top {stack[-1] if stack else None}')
            else:
                stack.pop()
            i = mc.end()
    if stack:
        errors.append(f'Unclosed blocks: {stack}')
    return not errors, errors


def top_level_sections(payload: str) -> list[tuple[int, int, str]]:
    sections: list[tuple[int, int, str]] = []
    stack: list[tuple[str, int]] = []
    decoder = json.JSONDecoder()
    i = 0
    while True:
        mo = OPEN_RE.search(payload, i)
        mc = CLOSE_RE.search(payload, i)
        if not mo and not mc:
            break
        if mo and (not mc or mo.start() < mc.start()):
            name = mo.group(1)
            start = mo.start()
            pos = mo.end()
            window = payload[pos:pos + 256]
            stripped = window.lstrip()
            ws = len(window) - len(stripped)
            if stripped.startswith('{'):
                _, end = decoder.raw_decode(payload, pos + ws)
                suffix = payload[end:end + 6]
                selfclose = suffix.startswith(' /-->')
                next_i = end + (5 if selfclose else 4)
            else:
                m = re.match(r'\s*(/)?-->', payload[pos:pos + 64])
                if not m:
                    raise SystemExit(f'Cannot parse block at {pos}')
                selfclose = bool(m.group(1))
                next_i = pos + m.end()
            if name == 'section' and len(stack) <= 1 and (not stack or stack[-1][0] == 'placeholder') and not selfclose:
                stack.append((name, start))
            elif not selfclose:
                stack.append((name, start))
            i = next_i
        else:
            name = mc.group(1)
            close_end = mc.end()
            if not stack:
                raise SystemExit(f'Mismatched close {name} at {mc.start()}')
            top_name, start = stack.pop()
            if top_name != name:
                raise SystemExit(f'Mismatched close {name}; expected {top_name}')
            if name == 'section' and (not stack or (len(stack) == 1 and stack[-1][0] == 'placeholder')):
                section_text = payload[start:close_end]
                label = extract_label(section_text)
                sections.append((start, close_end, label))
            i = close_end
    return sections


def extract_label(block_text: str) -> str:
    head = BLOCK_HEADER_RE.search(block_text)
    if head:
        m = LABEL_RE.search(head.group(0))
        if m:
            return m.group(1)
    return 'section'


def split_one(name: str, export_path: Path) -> None:
    raw, layout_id, payload, template = load_export(export_path)
    ok, errors = scan_divi_balance(payload)
    if not ok:
        raise SystemExit(f'{export_path.name}: invalid Divi block balance before split:\n' + '\n'.join(errors[:20]))
    page_dir = MODULES / name
    sections_dir = page_dir / 'sections'
    if page_dir.exists():
        shutil.rmtree(page_dir)
    sections_dir.mkdir(parents=True)
    write_text_exact(page_dir / 'template.json', template)
    sections = top_level_sections(payload)
    parts: list[Part] = []
    cursor = 0
    for idx, (start, end, label) in enumerate(sections, 1):
        if start > cursor:
            parts.append(Part(kind='raw', text=payload[cursor:start]))
        filename = f'{idx:02d}-{slugify(label, f"section-{idx}")}.divi'
        write_text_exact(sections_dir / filename, payload[start:end])
        parts.append(Part(kind='section', file=f'sections/{filename}', label=label))
        cursor = end
    if cursor < len(payload):
        parts.append(Part(kind='raw', text=payload[cursor:]))
    manifest = {
        'schema': 'bdstar-divi5-modules-v1',
        'source_export': export_path.name,
        'layout_id': layout_id,
        'notes': [
            'Edit .divi files as raw Divi 5 Gutenberg block markup.',
            'Do not JSON-round-trip module attrs; preserve Divi 5 nested module/advanced/decoration structure.',
            'Run tools/divi_modules.py compile --page <name> after edits and validate before import.',
        ],
        'parts': [p.__dict__ for p in parts],
    }
    write_text_exact(page_dir / 'manifest.json', json.dumps(manifest, indent=2, ensure_ascii=False))
    print(f'split {name}: {len(sections)} top-level sections -> {page_dir}')


def compile_one(name: str, out_dir: Path | None = None) -> Path:
    page_dir = MODULES / name
    manifest = json.loads(read_text_exact(page_dir / 'manifest.json'))
    payload_parts = []
    for part in manifest['parts']:
        if part['kind'] == 'raw':
            payload_parts.append(part.get('text') or '')
        elif part['kind'] == 'section':
            payload_parts.append(read_text_exact(page_dir / part['file']))
        else:
            raise SystemExit(f'Unknown manifest part kind: {part["kind"]}')
    payload = ''.join(payload_parts)
    ok, errors = scan_divi_balance(payload)
    if not ok:
        raise SystemExit(f'{name}: invalid Divi block balance after compile:\n' + '\n'.join(errors[:30]))
    out_dir = out_dir or (BASE / 'Modules' / '_compiled')
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / manifest['source_export']
    write_text_exact(out_path, read_payload_from_template(page_dir / 'template.json', payload))
    # semantic sanity check
    compiled = json.loads(read_text_exact(out_path))
    layout_id = manifest['layout_id']
    if compiled['data'][layout_id] != payload:
        raise SystemExit(f'{name}: compiled payload did not round-trip through JSON')
    print(f'compiled {name}: {out_path}')
    return out_path


def validate_one(name: str) -> None:
    path = compile_one(name, MODULES / '_validate')
    data = json.loads(path.read_text(encoding='utf-8'))
    layout_id, payload = next(iter(data['data'].items()))
    ok, errors = scan_divi_balance(payload)
    if not ok:
        raise SystemExit('\n'.join(errors))
    print(f'validated {name}: layout {layout_id}, payload length {len(payload)}')


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('split')
    p.add_argument('--page', choices=[*EXPORTS.keys(), 'all'], default='all')
    p = sub.add_parser('compile')
    p.add_argument('--page', choices=[*EXPORTS.keys(), 'all'], default='all')
    p.add_argument('--out-dir', default=str(MODULES / '_compiled'))
    p = sub.add_parser('validate')
    p.add_argument('--page', choices=[*EXPORTS.keys(), 'all'], default='all')
    args = ap.parse_args()

    pages = list(EXPORTS) if args.page == 'all' else [args.page]
    if args.cmd == 'split':
        MODULES.mkdir(exist_ok=True)
        for page in pages:
            split_one(page, EXPORTS[page])
    elif args.cmd == 'compile':
        for page in pages:
            compile_one(page, Path(args.out_dir))
    elif args.cmd == 'validate':
        for page in pages:
            validate_one(page)


if __name__ == '__main__':
    main()
