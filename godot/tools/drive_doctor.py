#!/usr/bin/env python3
"""drive_doctor — where would a SAVE go right now, and why (2026-10-18).

The user: "hero studio is still trying to save to shared drive." This
answers it on the Deck in one run, writing nothing anywhere:

  * every Hero Studio process running, and whether its code is OLDER than
    the code on disk (a Studio started before the 2026-10-13 guard has no
    guard at all: it is the one that can still write to a shared drive);
  * the `gdrive` connection's settings (a team_drive or root_folder_id
    points it at a shared drive), and any rclone environment override;
  * every OTHER rclone connection that points at a shared drive;
  * drive_guard's own verdict: Google is asked who owns ModernMythology.

    python3 godot/tools/drive_doctor.py          # look only
    python3 godot/tools/drive_doctor.py --fix    # also: stop every Studio,
                                                 # point gdrive at My Drive

--fix stops every running Hero Studio by PID and, when `gdrive` points at a
shared drive, runs drive_rescue.py (which repoints it and copies anything
stranded there back to My Drive; it deletes nothing). Start the Studio
again afterwards with: bash godot/tools/hero_studio.sh
"""
import argparse
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
import drive_guard  # noqa: E402

CODE = [TOOLS / "meshy_pipeline.py", TOOLS / "drive_guard.py"]


def studios():
    """[(pid, started_unix, cmdline)] for every `meshy_pipeline.py serve`."""
    out = []
    try:
        tick = os.sysconf("SC_CLK_TCK")
        boot = next(float(l.split()[1]) for l in Path("/proc/stat").read_text().splitlines() if l.startswith("btime"))
    except (OSError, ValueError, StopIteration):
        tick, boot = 100, 0.0
    for d in Path("/proc").glob("[0-9]*"):
        try:
            args = [a.decode("utf-8", "replace") for a in (d / "cmdline").read_bytes().split(b"\0") if a]
            if not (any(a.endswith("meshy_pipeline.py") for a in args) and "serve" in args):
                continue
            fields = (d / "stat").read_text().rsplit(")", 1)[1].split()
            started = boot + int(fields[19]) / tick
            out.append((int(d.name), started, " ".join(args)))
        except (OSError, ValueError, IndexError):
            continue
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--fix", action="store_true", help="stop every Studio; repoint gdrive at My Drive if needed")
    args = ap.parse_args()
    bad = []

    newest = max(p.stat().st_mtime for p in CODE if p.exists())
    print("== Hero Studio processes")
    procs = studios()
    if not procs:
        print("   none running")
    for pid, started, cmd in procs:
        stale = started < newest
        print(f"   PID {pid} started {time.strftime('%Y-%m-%d %H:%M', time.localtime(started))}"
              + ("  ← OLDER than the code on disk: restart it" if stale else "  (current code)"))
        if stale:
            bad.append(f"Hero Studio PID {pid} runs code older than the guard on disk")

    print("== rclone")
    rc = drive_guard.rclone_bin()
    if not rc:
        print("   rclone not installed: nothing can reach the Drive")
        conf = {}
    else:
        try:
            conf = json.loads(subprocess.run([rc, "config", "dump"], capture_output=True, text=True,
                                             timeout=30).stdout or "{}")
        except (ValueError, subprocess.SubprocessError) as ex:
            conf = {}
            bad.append(f"cannot read the rclone config ({ex})")
    env = drive_guard._env_overrides()
    if env:
        bad.append(f"rclone environment overrides set: {', '.join(sorted(env))} (unset them)")
        print(f"   ENV OVERRIDES: {', '.join(sorted(env))}")
    g = conf.get(drive_guard.REMOTE_NAME) or {}
    td = (g.get("team_drive") or "").strip()
    rf = (g.get("root_folder_id") or "").strip()
    if rc:
        print(f"   gdrive: type={g.get('type', '—')} scope={g.get('scope', '—')} "
              f"team_drive={td or '(none)'} root_folder_id={rf or '(none)'}")
    if td:
        bad.append(f"gdrive points at the shared drive {drive_guard.DENY_SHARED.get(td, td)} ({td})")
    if rf:
        bad.append("gdrive has a root_folder_id (it may sit inside a shared drive)")
    for name, c in sorted(conf.items()):
        if name != drive_guard.REMOTE_NAME and (c.get("team_drive") or "").strip():
            t = c["team_drive"].strip()
            print(f"   {name}: shared drive {drive_guard.DENY_SHARED.get(t, t)} — the tools never write through it")

    print("== the guard (Google is asked who owns ModernMythology)")
    if rc and not td and not rf and not env:
        try:
            owner = drive_guard.verify(f"{drive_guard.REMOTE_NAME}:{drive_guard.ROOT_FOLDER}")
            print(f"   PASS: ModernMythology is in {owner}'s My Drive — SAVE writes there and nowhere else")
        except drive_guard.DriveRefused as ex:
            print(f"   REFUSED (nothing will be written): {ex}")
            bad.append(f"the guard refuses: {ex}")
    else:
        print("   not asked: fix the connection first (the guard refuses every write until then)")

    print()
    if not bad:
        print("All clear: a SAVE from a freshly started Hero Studio goes only to your My Drive.")
        return
    print("Found:")
    for b in bad:
        print(f"  - {b}")
    if not args.fix:
        print("\nFix it: python3 godot/tools/drive_doctor.py --fix")
        return
    for pid, _, _ in procs:
        try:
            os.kill(pid, signal.SIGTERM)
            print(f"stopped Hero Studio PID {pid}")
        except OSError as ex:
            print(f"could not stop PID {pid}: {ex}")
    time.sleep(1.0)
    for pid, _, _ in procs:
        if Path(f"/proc/{pid}").exists():
            try:
                os.kill(pid, signal.SIGKILL)
            except OSError:
                pass
    if td or rf:
        print("repointing gdrive at My Drive (drive_rescue.py) …")
        subprocess.run([sys.executable, str(TOOLS / "drive_rescue.py")])
    print("\nNow run this again to confirm, then start the Studio: bash godot/tools/hero_studio.sh")


if __name__ == "__main__":
    main()
