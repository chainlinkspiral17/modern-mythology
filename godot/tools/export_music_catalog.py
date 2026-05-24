#!/usr/bin/env python3
"""
export_music_catalog.py — Extract MM_MUSIC catalog from vn-music.jsx to JSON.

Writes resources/music_catalog.json (consumed by SceneDataDB.gd).

Requirements: Node.js in PATH.

Usage:
    cd /path/to/godot
    python3 tools/export_music_catalog.py
    python3 tools/export_music_catalog.py --src ../project/vn-music.jsx --out resources/music_catalog.json
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

_NODE_EXTRACTOR = r"""
const vm  = require('vm');
const fs  = require('fs');

const srcPath = process.argv[2];
let code = fs.readFileSync(srcPath, 'utf8');

// Strip Object.assign(window, ...) and everything after (multi-line block)
code = code.replace(/\nObject\.assign\s*\(\s*window\s*,[\s\S]*$/, '');
// Strip export keywords
code = code.replace(/^export\s+/gm, '');
// Promote const/let/var MM_MUSIC to bare global assignment → lands on sandbox
code = code.replace(/(?:const|let|var)\s+(MM_MUSIC)\s*=/g, '$1 =');

const sandbox = {
    MM_MUSIC: [],
    window: { addEventListener: () => {}, dispatchEvent: () => {} },
    localStorage: { getItem: () => null, setItem: () => {}, removeItem: () => {} },
    CustomEvent: function() {},
    Set: Set, JSON: JSON, parseInt: parseInt,
    console: { log: () => {}, warn: () => {}, error: () => {} },
};

vm.createContext(sandbox);
try {
    vm.runInContext(code, sandbox);
} catch (err) {
    if (sandbox.MM_MUSIC.length === 0) {
        process.stderr.write('VM error: ' + err.message + '\n');
        process.exit(1);
    }
    process.stderr.write('VM warning (non-fatal): ' + err.message + '\n');
}

// Apply default unlock (mirrors vn-music.jsx forEach)
sandbox.MM_MUSIC.forEach(t => { if (!t.unlock) t.unlock = { type: 'heard' }; });

process.stdout.write(JSON.stringify(sandbox.MM_MUSIC, null, 2));
"""


def main() -> None:
    parser = argparse.ArgumentParser(description='Export MM_MUSIC catalog to JSON')
    parser.add_argument('--src', default='../project/vn-music.jsx')
    parser.add_argument('--out', default='resources/music_catalog.json')
    args = parser.parse_args()

    src = Path(args.src).resolve()
    out = Path(args.out).resolve()

    if not src.exists():
        print(f"ERROR: not found: {src}", file=sys.stderr)
        sys.exit(1)

    with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False, encoding='utf-8') as f:
        f.write(_NODE_EXTRACTOR)
        tmp = f.name

    try:
        result = subprocess.run(['node', tmp, str(src)],
                                capture_output=True, text=True, timeout=30)
    finally:
        os.unlink(tmp)

    if result.returncode != 0:
        print("ERROR:", result.stderr, file=sys.stderr)
        sys.exit(1)

    catalog = json.loads(result.stdout)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)

    print(f"Wrote {len(catalog)} tracks → {out}")


if __name__ == '__main__':
    main()
