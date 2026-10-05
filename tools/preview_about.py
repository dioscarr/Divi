#!/usr/bin/env python3
"""Quick preview of compiled About export via headless Chromium."""

import base64, json, os, subprocess, sys, tempfile, time
from pathlib import Path

BASE = Path('/home/dioscarr/Work/divi-working-set')
EXPORT = BASE / 'Modules/_compiled/bdstar-about-v5.json'
OUTDIR = BASE / 'evidence/modern-ui/preview'
OUTDIR.mkdir(parents=True, exist_ok=True)

def main():
    # Load compiled JSON
    data = json.load(open(EXPORT, newline=''))
    layout_id, payload = next(iter(data['data'].items()))
    print(f'Previewing {EXPORT.name} layout {layout_id}')

    # Minimal HTML shell that loads Divi builder context
    html_template = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>BD Star About Preview</title>
</head>
<body>
<div id="et-boc">{payload}</div>
</body>
</html>'''

    with tempfile.NamedTemporaryFile('w', suffix='.html', delete=False) as f:
        f.write(html_template)
        html_path = f.name

    try:
        # Chromium headless screenshots at common widths
        for label, width in [('desktop', 1440), ('tablet', 768), ('phone', 375)]:
            out_png = OUTDIR / f'about-preview-{label}.png'
            cmd = [
                'chromium',
                '--headless=new',
                '--disable-gpu',
                '--no-sandbox',
                f'--window-size={width},2000',
                f'--screenshot={out_png}',
                f'file://{html_path}'
            ]
            print(f'Running: {" ".join(cmd)}')
            subprocess.run(cmd, check=True, timeout=30)
            print(f'Saved {out_png}')
            # also capture console/log if any
            log = subprocess.run([
                'chromium',
                '--headless=new',
                '--disable-gpu',
                '--no-sandbox',
                '--dump-dom',
                f'file://{html_path}'
            ], capture_output=True, text=True, timeout=20)
            if log.returncode != 0:
                print(f'Chromium stderr: {log.stderr[:200]}')
    finally:
        os.unlink(html_path)

if __name__ == '__main__':
    main()