#!/usr/bin/env python3
"""drive_rescue.py — the project's files belong on YOUR My Drive (2026-10-13).

The user: "my google drive should be on my google drive, not the one model
nation drive … flag one model nation drive not to use, as that is a shared
project, that I have no permission over … make sure all the files from One
Model Nation drive that are the most current are backed up on My Drive."

What happened: on 2026-10-01 the `gdrive` connection was re-signed (own
client id) and rclone's "Configure this as a Shared Drive?" was answered
yes, so `gdrive:` became the One Model Nation shared drive. Every SAVE since
went into a `ModernMythology` folder there; the one on My Drive (made the
same morning) stopped getting files.

This, in one run:
  1. keeps a READ-ONLY-BY-USE connection to the shared drive's folder,
     `gdrive_modelnation` (the tool never writes through it);
  2. points `gdrive` back at My Drive (no team_drive, no root_folder_id);
  3. copies every file from the shared folder to My Drive's ModernMythology
     with --update: a file My Drive already has NEWER stays; everything
     else (missing, or older on My Drive) comes across. Server-side when
     Google allows (same account on both: nothing streams through the Deck);
  4. checks: every file in the shared folder is now on My Drive.
Nothing is deleted anywhere. Safe to run again (it only copies what's left).

    python3 godot/tools/drive_rescue.py            # do it
    python3 godot/tools/drive_rescue.py --dry-run  # show what would copy
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

# Shared drives the project must never write to (meshy_pipeline refuses them).
DENY_SHARED = {"0AEnZu3oDWBFuUk9PVA": "One Model Nation"}
MAIN = "gdrive"
SHARED = "gdrive_modelnation"
FOLDER = "ModernMythology"
HERE = Path(__file__).resolve().parent


def rclone():
    rc = shutil.which("rclone")
    if rc:
        return rc
    local = Path.home() / ".local" / "bin" / "rclone"
    if local.exists():
        return str(local)
    sys.exit("rclone is not installed — run: bash godot/tools/drive_setup.sh")


RC = rclone()


def run(args, live=False, check=False):
    if live:
        return subprocess.run([RC] + args).returncode
    r = subprocess.run([RC] + args, capture_output=True, text=True)
    if check and r.returncode != 0:
        sys.exit(f"rclone {' '.join(args[:3])} failed:\n{(r.stderr or r.stdout)[-800:]}")
    return r


def dump():
    r = run(["config", "dump"], check=True)
    return json.loads(r.stdout or "{}")


def size(remote):
    r = run(["size", remote, "--json"])
    try:
        d = json.loads(r.stdout)
        return int(d.get("count", 0)), int(d.get("bytes", 0))
    except (ValueError, TypeError):
        return None


def gb(n):
    return f"{n / 1e9:.2f} GB"


def main():
    dry = "--dry-run" in sys.argv
    conf = dump()
    if MAIN not in conf:
        sys.exit("No `gdrive` connection yet — run: bash godot/tools/drive_setup.sh")
    g = conf[MAIN]
    td = g.get("team_drive", "")
    print(f"`{MAIN}` points at: " + (f"SHARED DRIVE {DENY_SHARED.get(td, td)} ({td})" if td else "My Drive"))
    # names in quotes may hold spaces and slashes ("ModernMythology - Delete/Accident"):
    # rclone takes them as paths, so a "/" in a Drive folder NAME is written as its
    # full-width twin by rclone's encoder — lsjson returns it already encoded
    if dry:
        # change nothing: name both places inline (rclone connection strings)
        shared_id = td or next(iter(DENY_SHARED))
        src_root = f"{MAIN},team_drive={shared_id}:"
        for name in shared_folders(src_root) or [FOLDER]:
            print(f"\n── from the shared drive's  {name!r}")
            copy_and_check(src_root + name, f"{MAIN},team_drive='',root_folder_id='':{FOLDER}", dry=True)
        return 0

    # 1. the shared folder, kept as its own connection (read from, never written)
    if SHARED not in conf:
        shared_id = td or next(iter(DENY_SHARED))
        params = {k: v for k, v in g.items() if k not in ("type", "team_drive", "root_folder_id")}
        params["team_drive"] = shared_id
        args = ["config", "create", SHARED, "drive"] + [f"{k}={v}" for k, v in params.items()] + ["--non-interactive"]
        run(args, check=True)
        print(f"kept the shared drive as `{SHARED}:` (the tool only ever reads it)")
    # 2. `gdrive` back to My Drive
    if td or g.get("root_folder_id"):
        run(["config", "update", MAIN, "team_drive=", "root_folder_id=", "--non-interactive"], check=True)
        if dump()[MAIN].get("team_drive"):
            # some rclone builds will not blank a key through `update`: edit the file
            path = run(["config", "file"]).stdout.strip().splitlines()[-1]
            lines, sec = [], None
            for ln in Path(path).read_text().splitlines():
                s = ln.strip()
                if s.startswith("[") and s.endswith("]"):
                    sec = s[1:-1]
                if sec == MAIN and (s.startswith("team_drive") or s.startswith("root_folder_id")):
                    continue
                lines.append(ln)
            Path(path).write_text("\n".join(lines) + "\n")
        print(f"`{MAIN}` now points at My Drive")
    if dump()[MAIN].get("team_drive"):
        sys.exit("could not move `gdrive` off the shared drive — nothing copied")
    run(["mkdir", f"{MAIN}:{FOLDER}"])

    # (2026-10-13) the shared drive's folders may have been RENAMED
    # ("ModernMythology - Delete/Accident"): copy out of every folder whose
    # name begins with ModernMythology, oldest first, newest version winning
    srcs = shared_folders(f"{SHARED}:")
    if not srcs:
        sys.exit(f"no ModernMythology… folder on the shared drive — nothing to copy")
    worst = 0
    for name in srcs:
        print(f"\n── from the shared drive's  {name!r}")
        worst = max(worst, copy_and_check(f"{SHARED}:{name}", f"{MAIN}:{FOLDER}", dry=False) or 0)
    return worst


def shared_folders(remote):
    """Top-level folders on the shared drive named ModernMythology…, the
    oldest first (so a newer copy of a file overwrites an older one)."""
    r = run(["lsjson", remote, "--dirs-only"])
    try:
        rows = json.loads(r.stdout or "[]")
    except ValueError:
        return []
    rows = [x for x in rows if str(x.get("Name", "")).startswith(FOLDER)]
    rows.sort(key=lambda x: x.get("ModTime", ""))
    return [x["Name"] for x in rows]


def copy_and_check(src, dst, dry):
    a, b = size(src), size(dst)
    if a is None:
        sys.exit(f"cannot read {src} — is your account still a member of that shared drive?")
    print(f"shared drive folder: {a[0]} files, {gb(a[1])}")
    if b is not None:
        print(f"My Drive folder:     {b[0]} files, {gb(b[1])}")

    # 3. copy across, newest wins
    base = ["copy", src, dst, "--update", "--transfers", "8", "--checkers", "16", "--progress",
            "--stats-one-line", "--retries", "5"]
    if dry:
        base.append("--dry-run")
    print("\ncopying (server-side where Google allows; files newer on My Drive are kept) …", flush=True)
    rc = run(base + ["--drive-server-side-across-configs"], live=True)
    if rc != 0 and not dry:
        print("some files could not be copied server-side — sending those through this machine …", flush=True)
        rc = run(base, live=True)
    if dry:
        print("\n(dry run: nothing was copied)")
        return 0

    # 4. check: every file of the shared folder is on My Drive
    miss = HERE / ".drive_rescue_missing.txt"
    run(["check", src, dst, "--one-way", "--size-only", "--missing-on-dst", str(miss)])
    missing = [l for l in miss.read_text().splitlines() if l.strip()] if miss.exists() else []
    b = size(dst)
    print()
    if b is not None:
        print(f"My Drive folder now: {b[0]} files, {gb(b[1])}")
    if missing:
        print(f"!! {len(missing)} file(s) are still only on the shared drive (listed in {miss}).")
        print("   Run this again; if they stay, paste that list to Claude.")
        return 1
    print("OK  every file from the shared drive's folder is on your My Drive (the newest version of each).")
    print(f"    Hero Studio's SAVE now goes to My Drive; `{SHARED}:` is never written to.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
