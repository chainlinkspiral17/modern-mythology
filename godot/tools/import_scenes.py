#!/usr/bin/env python3
"""
import_scenes.py — Convert vn-scenes.jsx to per-scene JSON files for Godot.

Reads DEMO_SCENES from the JSX source by evaluating it in a Node.js sandbox,
then writes one JSON file per scene under resources/scenes/vol{N}/.
Also regenerates resources/scenes/index.json.

Requirements: Node.js (node) must be in PATH.

Usage:
    cd /path/to/godot
    python3 tools/import_scenes.py
    python3 tools/import_scenes.py --src ../project/vn-scenes.jsx --out resources/scenes
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

# Node.js script injected at runtime — evaluates the JSX in a fresh VM context
# and dumps DEMO_SCENES as JSON to stdout.
#
# Key subtlety: in Node vm.runInContext, `const` declarations are script-scoped
# and NOT promoted to the context object. We rename DEMO_SCENES from const to a
# bare assignment so it lands on the sandbox (the context's global object).
_NODE_EXTRACTOR = r"""
const vm  = require('vm');
const fs  = require('fs');

const srcPath = process.argv[2];
let code = fs.readFileSync(srcPath, 'utf8');

// Remove Object.assign(window, ...) line and everything after it
code = code.replace(/\nObject\.assign\s*\(\s*window\s*,[\s\S]*$/, '');
// Strip export keywords
code = code.replace(/^export\s+/gm, '');
// Promote `const/let/var DEMO_SCENES` to a bare global assignment
// so it ends up as a property on the sandbox context object
code = code.replace(/(?:const|let|var)\s+(DEMO_SCENES)\s*=/g, '$1 =');

// Sandbox: stub every browser API the file touches
const sandbox = {
    DEMO_SCENES: {},
    localStorage: {
        getItem:    () => null,
        setItem:    () => {},
        removeItem: () => {},
    },
    window:  {},
    VNData:  undefined,
    JSON:    JSON,
    console: { log: () => {}, warn: () => {}, error: () => {} },
};

vm.createContext(sandbox);
try {
    vm.runInContext(code, sandbox);
} catch (err) {
    // Most errors come from the localStorage IIFE which has its own try/catch;
    // hard-fail only if DEMO_SCENES ended up empty.
    if (Object.keys(sandbox.DEMO_SCENES).length === 0) {
        process.stderr.write('VM error (and no scenes extracted): ' + err.message + '\n');
        process.stderr.write(err.stack + '\n');
        process.exit(1);
    }
    process.stderr.write('VM warning (non-fatal): ' + err.message + '\n');
}

process.stdout.write(JSON.stringify(sandbox.DEMO_SCENES));
"""


def _run_node(src_path: Path) -> dict:
    """Execute the extractor via Node.js and return the parsed DEMO_SCENES dict."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False, encoding='utf-8') as f:
        f.write(_NODE_EXTRACTOR)
        tmp = f.name
    try:
        result = subprocess.run(
            ['node', tmp, str(src_path)],
            capture_output=True, text=True, timeout=30
        )
    finally:
        os.unlink(tmp)

    if result.returncode != 0:
        print("ERROR from node:", result.stderr, file=sys.stderr)
        sys.exit(1)

    if result.stderr:
        print("node warning:", result.stderr, file=sys.stderr)

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}", file=sys.stderr)
        print("First 500 chars of output:", result.stdout[:500], file=sys.stderr)
        sys.exit(1)


def _infer_vol(scene_id: str, scene: dict) -> int:
    """Return vol number from scene dict or from scene_id pattern."""
    if scene.get('vol'):
        return int(scene['vol'])
    import re
    m = re.match(r'^vol(\d+)', scene_id)
    if m:
        return int(m.group(1))
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description='Convert vn-scenes.jsx → Godot JSON scene files')
    parser.add_argument('--src', default='../project/vn-scenes.jsx',
                        help='Path to vn-scenes.jsx (default: ../project/vn-scenes.jsx)')
    parser.add_argument('--out', default='resources/scenes',
                        help='Output directory (default: resources/scenes)')
    parser.add_argument('--force', action='store_true',
                        help='Overwrite existing files')
    args = parser.parse_args()

    src = Path(args.src).resolve()
    out_base = Path(args.out).resolve()

    if not src.exists():
        print(f"ERROR: source not found: {src}", file=sys.stderr)
        sys.exit(1)

    print(f"Reading {src} ...")
    scenes = _run_node(src)
    print(f"  Loaded {len(scenes)} scenes.")

    # Group by volume
    by_vol: dict[int, list[tuple[str, dict]]] = {}
    for scene_id, scene in scenes.items():
        if not isinstance(scene, dict):
            continue
        vol = _infer_vol(scene_id, scene)
        if vol == 0:
            print(f"  WARNING: cannot determine vol for '{scene_id}', skipping")
            continue
        by_vol.setdefault(vol, []).append((scene_id, scene))

    # Write scene files
    written = 0
    skipped = 0
    index: dict[str, list[str]] = {}

    for vol in sorted(by_vol.keys()):
        vol_dir = out_base / f'vol{vol}'
        vol_dir.mkdir(parents=True, exist_ok=True)
        vol_ids: list[str] = []

        for scene_id, scene in by_vol[vol]:
            out_path = vol_dir / f'{scene_id}.json'
            if out_path.exists() and not args.force:
                skipped += 1
            else:
                # Ensure vol is in the scene data
                scene_out = dict(scene)
                scene_out.setdefault('vol', vol)
                with open(out_path, 'w', encoding='utf-8') as f:
                    json.dump(scene_out, f, indent=2, ensure_ascii=False)
                written += 1
            vol_ids.append(scene_id)

        index[str(vol)] = vol_ids

    # Write index.json
    index_path = out_base / 'index.json'
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2)

    vol_count = len(by_vol)
    print(f"Done. {written} written, {skipped} skipped (use --force to overwrite).")
    print(f"  Volumes: {vol_count}  |  index → {index_path}")
    if skipped > 0:
        print("  Tip: existing files are not overwritten by default so local edits are preserved.")


if __name__ == '__main__':
    main()
