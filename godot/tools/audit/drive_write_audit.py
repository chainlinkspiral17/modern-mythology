#!/usr/bin/env python3
"""drive_write_audit.py — nothing writes to Google Drive except drive_guard
(2026-10-13; the user: "I want nothing more going to a public shared folder.
Very serious."). A GATE: nonzero exit fails.

Scans every script under godot/tools and tools/ (Python, shell, HTML/JS)
for an rclone WRITE verb (copy, copyto, move, sync, mkdir, rcat, purge,
delete, touch, link, …) and for Google Drive API write endpoints. Each hit
must be in godot/tools/drive_guard.py (the one writer: it proves the
destination is the owner's My Drive), or carry the marker `drive-read` on
its line (or the line above) — a read whose DESTINATION is this machine
(Drive → local), with a word on why — or the marker `drive-guarded` on an
argument list the same file hands to drive_guard.rclone_write. Anything
else fails.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SCAN = [os.path.join(ROOT, "godot", "tools"), os.path.join(ROOT, "tools")]
ALLOWED_FILE = {os.path.join(ROOT, "godot", "tools", "drive_guard.py"),
                os.path.join(ROOT, "godot", "tools", "audit", "drive_guard_test.py"),
                os.path.abspath(__file__)}
VERBS = r"(copy|copyto|move|moveto|sync|bisync|mkdir|rcat|purge|delete|deletefile|rmdir|rmdirs|touch|link|dedupe|cleanup)"
# a verb as an rclone sub-command: in a Python arg list next to the binary,
# as a quoted list head ["copy", ...] in a file that runs rclone, or after
# rclone / "$RC" in a shell line
PY_PATTERNS = [re.compile(r"\[\s*rc\s*,\s*[\"']" + VERBS + r"[\"']"),
               re.compile(r"\[\s*RC\s*\]\s*\+\s*\[\s*[\"']" + VERBS + r"[\"']"),
               re.compile(r"(?:run|_run|rclone_write)\s*\(\s*(?:rc\s*,\s*)?\[\s*[\"']" + VERBS + r"[\"']"),
               re.compile(r"^\s*\w+\s*=\s*\[\s*[\"']" + VERBS + r"[\"']\s*,")]
SH_PATTERN = re.compile(r"(?:\brclone|\"\$RC\"|\$RC)\s+" + VERBS + r"\b")
API_PATTERN = re.compile(r"googleapis\.com/(upload/)?drive/v\d/files[^\"'\s]*", re.I)


def main():
    bad = []
    seen = 0
    for base in SCAN:
        for dp, dn, fn in os.walk(base):
            dn[:] = [d for d in dn if d not in ("__pycache__", "node_modules", ".git")]
            for f in fn:
                if not f.endswith((".py", ".sh", ".html", ".js")):
                    continue
                path = os.path.join(dp, f)
                if path in ALLOWED_FILE:
                    continue
                try:
                    lines = open(path, encoding="utf-8", errors="replace").read().splitlines()
                except OSError:
                    continue
                text = "\n".join(lines)
                runs_rclone = "rclone" in text
                for i, ln in enumerate(lines, 1):
                    prev = lines[i - 2] if i >= 2 else ""
                    if ln.lstrip().startswith("#"):
                        continue
                    # a read INTO this machine, said so on the line or the one above
                    if "drive-read" in ln or "drive-read" in prev:
                        continue
                    # an argument list handed to the gate — only where the file calls it
                    if ("drive-guarded" in ln or "drive-guarded" in prev) and "rclone_write(" in text:
                        continue
                    hit = False
                    if f.endswith(".sh"):
                        hit = bool(SH_PATTERN.search(ln))
                    elif f.endswith(".py") and runs_rclone:
                        hit = any(p.search(ln) for p in PY_PATTERNS)
                    if API_PATTERN.search(ln) and re.search(r"POST|PATCH|PUT|upload", ln, re.I):
                        hit = True
                    if hit:
                        seen += 1
                        bad.append((os.path.relpath(path, ROOT), i, ln.strip()[:140]))
    for p, i, ln in bad:
        print("UNGUARDED DRIVE WRITE  %s:%d  %s" % (p, i, ln))
    print("drive_write_audit · %d unguarded write(s) outside drive_guard.py" % len(bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
