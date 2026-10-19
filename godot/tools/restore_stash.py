#!/usr/bin/env python3
"""restore_stash — put the user's work back from a git stash, safely
(2026-10-19).

The user: "Once again, audio director is missing all my work. Again." On
2026-10-19 Claude had the user run `git stash push -m "local edits before
voice studio update"` so a pull could land — and that set aside every
tracked file the tools had changed on the Deck (the audio director's
temp_approvals.json, temp_briefs.json, the music catalog, the score …).
Nothing was deleted; this brings it back.

For every file in the stash:
  * unchanged in the repo since the stash  → the stashed version is put back;
  * the repo has the same content already  → nothing to do;
  * changed in the repo since              → a clean three-way merge is
    written when git can merge it; otherwise the repo's version stays and
    the stashed one is written beside it as <file>.from_stash, and listed.
The stash itself is never dropped.

    python3 godot/tools/restore_stash.py            # the voice-studio stash
    python3 godot/tools/restore_stash.py --dry-run  # say what it would do
    python3 godot/tools/restore_stash.py --stash 'stash@{1}'
"""
import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MESSAGE = "local edits before voice studio update"


def git(*args, check=True, text=True):
    r = subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=text)
    if check and r.returncode != 0:
        sys.exit(f"git {' '.join(args)} failed: {(r.stderr or '').strip()}")
    return r


def blob(ref, path):
    r = subprocess.run(["git", "show", f"{ref}:{path}"], cwd=REPO, capture_output=True)
    return r.stdout if r.returncode == 0 else None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stash", help="which stash (default: the newest one named '%s')" % MESSAGE)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    stashes = git("stash", "list").stdout.splitlines()
    if not stashes:
        sys.exit("No stashes on this machine: nothing was set aside here.")
    ref = args.stash
    if not ref:
        hit = [s for s in stashes if MESSAGE in s]
        ref = (hit or stashes)[0].split(":")[0]
    print(f"Restoring from {ref}: {next((s for s in stashes if s.startswith(ref + ':')), ref)}")
    base = f"{ref}^1"
    files = [f for f in git("stash", "show", "--name-only", ref).stdout.splitlines() if f.strip()]
    restored, same, merged, beside = [], [], [], []
    for f in files:
        stashed = blob(ref, f)
        at_base = blob(base, f)
        p = REPO / f
        now = p.read_bytes() if p.exists() else None
        if stashed is None:                       # the stash deleted it; leave the repo's
            continue
        if now == stashed:
            same.append(f)
            continue
        if now == at_base or now is None:
            restored.append(f)
            if not args.dry_run:
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes(stashed)
            continue
        # changed on both sides: try a clean three-way merge
        with tempfile.TemporaryDirectory() as td:
            cur, bas, sta = Path(td, "cur"), Path(td, "base"), Path(td, "stash")
            cur.write_bytes(now)
            bas.write_bytes(at_base or b"")
            sta.write_bytes(stashed)
            r = subprocess.run(["git", "merge-file", "-p", str(cur), str(bas), str(sta)], capture_output=True)
            if r.returncode == 0:
                merged.append(f)
                if not args.dry_run:
                    p.write_bytes(r.stdout)
                continue
        beside.append(f)
        if not args.dry_run:
            Path(str(p) + ".from_stash").write_bytes(stashed)
    print(f"  put back: {len(restored)}")
    for f in restored:
        print(f"    {f}")
    if merged:
        print(f"  merged with today's version: {len(merged)}")
        for f in merged:
            print(f"    {f}")
    if beside:
        print(f"  changed both ways — today's kept, yours written beside it as .from_stash: {len(beside)}")
        for f in beside:
            print(f"    {f}.from_stash")
    if same:
        print(f"  already the same: {len(same)}")
    print("The stash is kept (git stash list)." + ("  (dry run: nothing written)" if args.dry_run else ""))


if __name__ == "__main__":
    main()
