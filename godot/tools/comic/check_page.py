#!/usr/bin/env python3
"""Syntax-check the inspector's embedded page script with node (if present).
Run before committing comic_inspector.py; the launcher runs it too."""
import subprocess, sys, shutil
from pathlib import Path
src = (Path(__file__).parent / "comic_inspector.py").read_text(encoding="utf-8")
page = src[src.index('PAGE = r"""') + len('PAGE = r"""'):src.index('"""\n\n\ndef main')]
js = page[page.index("<script>") + 8:page.index("</script>")]
if not shutil.which("node"):
    print("· node not found; skipping page syntax check"); sys.exit(0)
tmp = Path("/tmp/comic_inspector_page.js"); tmp.write_text(js, encoding="utf-8")
r = subprocess.run(["node", "--check", str(tmp)], capture_output=True, text=True)
if r.returncode:
    print("✗ the inspector's page script has a syntax error:\n" + r.stderr); sys.exit(1)
print("✓ page script ok")
