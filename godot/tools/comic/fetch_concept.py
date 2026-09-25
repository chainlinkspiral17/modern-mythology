#!/usr/bin/env python3
"""fetch_concept.py — download concept-run renders listed in
godot/assets/comic/vol10/concept/manifest.json.

Runway's signed image URLs expire and the cloud session can't reach
Runway's CDN, so this runs on your machine. Give it the task → URL
pairs (from the Runway app, or from `get_task` in a session) and it
saves each PNG under the manifest's `file` path.

Usage:
  python3 godot/tools/comic/fetch_concept.py <taskId> <url> [<taskId> <url> ...]
  python3 godot/tools/comic/fetch_concept.py --urls urls.json   # {"<taskId>": "<url>", ...}
"""
import json, sys, urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
MAN = REPO / "godot" / "assets" / "comic" / "vol10" / "concept" / "manifest.json"


def main(argv):
    if len(argv) >= 2 and argv[0] == "--urls":
        pairs = json.loads(Path(argv[1]).read_text())
    else:
        if len(argv) % 2:
            sys.exit(__doc__)
        pairs = dict(zip(argv[0::2], argv[1::2]))
    m = json.loads(MAN.read_text())
    by_task = {r["taskId"]: r for r in m["renders"]}
    for task, url in pairs.items():
        r = by_task.get(task)
        if not r:
            print(f"✗ unknown task {task}"); continue
        out = REPO / r["file"]
        out.parent.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(url, timeout=120) as resp:
            out.write_bytes(resp.read())
        r["status"] = "SUCCEEDED"; r["downloaded"] = True
        print(f"✓ {out.relative_to(REPO)}")
    MAN.write_text(json.dumps(m, indent=2))


if __name__ == "__main__":
    main(sys.argv[1:])
