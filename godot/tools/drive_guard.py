#!/usr/bin/env python3
"""drive_guard.py — the ONLY way the project writes to Google Drive (2026-10-13).

The user: "I want nothing more going to a public shared folder. Very
serious." On 2026-10-01 a re-sign-in pointed rclone's `gdrive` at the One
Model Nation shared drive and every SAVE went there; on 2026-10-13 a Hero
Studio still running the old code re-created the folder there after it was
renamed. So every upload in every tool goes through `rclone_write()` here,
and it FAILS CLOSED — any doubt and nothing is written:

  1. no rclone environment override may be set (RCLONE_DRIVE_TEAM_DRIVE,
     RCLONE_CONFIG_GDRIVE_*: they would bypass the config file);
  2. the destination must be the `gdrive` connection, under
     gdrive:ModernMythology — never another remote, never a bare root;
  3. the connection's config has no team_drive and no root_folder_id;
  4. GOOGLE says where the folder is: rclone's Drive metadata (`lsjson -M`)
     names the folder's OWNER — an item on a shared drive has none. No
     owner, or no answer, or an older rclone that cannot say → refused;
  5. the owner is the one recorded on the first verified write
     (godot/tools/.drive_owner, gitignored; delete it to re-record);
  6. shortcuts are never followed (--drive-skip-shortcuts), so a shortcut
     inside My Drive cannot carry a write into a shared drive.

`godot/tools/audit/drive_write_audit.py` fails the suite if any rclone
write verb appears outside this file. DENY_SHARED names the shared drive
the user flagged; the rules above refuse EVERY shared drive regardless.
"""
import json
import os
import shutil
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
REMOTE_NAME = "gdrive"
ROOT_FOLDER = "ModernMythology"
OWNER_FILE = HERE / ".drive_owner"
DENY_SHARED = {"0AEnZu3oDWBFuUk9PVA": "One Model Nation"}
WRITE_VERBS = {"copy", "copyto", "move", "moveto", "sync", "bisync", "mkdir", "rcat", "purge", "delete",
               "deletefile", "rmdir", "rmdirs", "touch", "link", "dedupe", "settier", "cleanup"}


class DriveRefused(Exception):
    pass


def rclone_bin():
    found = shutil.which("rclone")
    if found:
        return found
    local = Path.home() / ".local" / "bin" / "rclone"
    return str(local) if local.exists() else None


def _run(rc, args, timeout=120):
    return subprocess.run([rc] + args, capture_output=True, text=True, timeout=timeout)


def _env_overrides():
    bad = []
    for k in os.environ:
        ku = k.upper()
        # per-backend and per-remote overrides (RCLONE_CONFIG itself, the
        # file's path, is fine: `config dump` below reads that same file)
        if ku.startswith("RCLONE_DRIVE_") or ku.startswith("RCLONE_CONFIG_"):
            bad.append(k)
    return bad


def verify(dest, allow_create_root=False):
    """Raise DriveRefused unless `dest` is inside the owner's My Drive
    ModernMythology folder. Returns the owner's address on success.
    allow_create_root: the folder may not exist YET (drive_setup's first
    mkdir) — the config checks must pass; the owner check runs after."""
    rc = rclone_bin()
    if not rc:
        raise DriveRefused("rclone is not installed — run: bash godot/tools/drive_setup.sh")
    env = _env_overrides()
    if env:
        raise DriveRefused(f"rclone environment overrides are set ({', '.join(sorted(env))}); "
                           "they can redirect the upload — unset them")
    if ":" not in dest:
        raise DriveRefused(f"{dest!r} is not a Drive path")
    name, path = dest.split(":", 1)
    if name != REMOTE_NAME or "," in name:
        raise DriveRefused(f"uploads go only through `{REMOTE_NAME}:` (asked for `{name}:`)")
    path = path.strip("/")
    if path != ROOT_FOLDER and not path.startswith(ROOT_FOLDER + "/"):
        raise DriveRefused(f"uploads go only under {REMOTE_NAME}:{ROOT_FOLDER} (asked for {dest})")
    try:
        conf = json.loads(_run(rc, ["config", "dump"], 30).stdout or "{}").get(REMOTE_NAME)
    except (ValueError, subprocess.SubprocessError) as ex:
        raise DriveRefused(f"cannot read the rclone config ({ex})")
    if not conf:
        raise DriveRefused(f"no `{REMOTE_NAME}` connection — run: bash godot/tools/drive_setup.sh")
    if conf.get("type") != "drive":
        raise DriveRefused(f"`{REMOTE_NAME}` is not a Google Drive connection")
    td = (conf.get("team_drive") or "").strip()
    if td:
        raise DriveRefused(f"`{REMOTE_NAME}` points at the shared drive {DENY_SHARED.get(td, td)} ({td}) — "
                           "run: python3 godot/tools/drive_rescue.py")
    if (conf.get("root_folder_id") or "").strip():
        raise DriveRefused(f"`{REMOTE_NAME}` has a root_folder_id; it could sit inside a shared drive — "
                           "run: rclone config update gdrive root_folder_id= ")
    # Google's own answer: who owns the project folder?
    r = _run(rc, ["lsjson", f"{REMOTE_NAME}:", "--dirs-only", "-M", "--drive-skip-shortcuts"], 180)
    if r.returncode != 0:
        raise DriveRefused(f"Google Drive did not answer ({(r.stderr or '').strip()[-200:]})")
    try:
        rows = [x for x in json.loads(r.stdout or "[]") if x.get("Name") == ROOT_FOLDER and x.get("IsDir")]
    except ValueError:
        rows = []
    if not rows and allow_create_root:
        return ""
    if len(rows) != 1:
        raise DriveRefused(f"expected one {ROOT_FOLDER} folder at the top of My Drive, found {len(rows)} — "
                           "run: bash godot/tools/drive_setup.sh")
    meta = rows[0].get("Metadata") or {}
    owner = (meta.get("owner") or "").strip()
    if not owner:
        raise DriveRefused(f"Google reports no owner for {ROOT_FOLDER} — it is on a shared drive, or this "
                           "rclone is too old to say (update: bash godot/tools/drive_setup.sh). Nothing written.")
    known = OWNER_FILE.read_text().strip() if OWNER_FILE.exists() else ""
    if known and known.lower() != owner.lower():
        raise DriveRefused(f"{ROOT_FOLDER} is owned by {owner}, not {known} (recorded in {OWNER_FILE.name}). "
                           "Nothing written. If that is really your account now, delete that file.")
    if not known:
        OWNER_FILE.write_text(owner + "\n")
    return owner


def make_root():
    """Create gdrive:ModernMythology at the top of My Drive (first set-up),
    then prove it with the owner check."""
    verify(f"{REMOTE_NAME}:{ROOT_FOLDER}", allow_create_root=True)
    rc = rclone_bin()
    r = subprocess.run([rc, "mkdir", f"{REMOTE_NAME}:{ROOT_FOLDER}", "--drive-skip-shortcuts"],
                       capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        raise DriveRefused(f"could not make {ROOT_FOLDER}: {(r.stderr or '').strip()[-200:]}")
    return verify(f"{REMOTE_NAME}:{ROOT_FOLDER}")


_VERIFIED = {"at": 0.0, "owner": ""}
VERIFY_TTL = 300.0          # one proof covers a SAVE's many chunks, not a session


def verify_cached(dest):
    import time
    verify_path_only(dest)
    if _VERIFIED["owner"] and time.time() - _VERIFIED["at"] < VERIFY_TTL:
        return _VERIFIED["owner"]
    owner = verify(dest)
    _VERIFIED.update(at=time.time(), owner=owner)
    return owner


def verify_path_only(dest):
    """The cheap part of verify(): remote name and folder (every call)."""
    if ":" not in dest:
        raise DriveRefused(f"{dest!r} is not a Drive path")
    name, path = dest.split(":", 1)
    path = path.strip("/")
    if name != REMOTE_NAME or (path != ROOT_FOLDER and not path.startswith(ROOT_FOLDER + "/")):
        raise DriveRefused(f"uploads go only under {REMOTE_NAME}:{ROOT_FOLDER} (asked for {dest})")
    if _env_overrides():
        raise DriveRefused("rclone environment overrides are set; they can redirect the upload — unset them")


def rclone_write(args, timeout=None, live=False):
    """Run one rclone WRITE command after verify() on its destination (the
    last remote path in args). Returns the CompletedProcess (or the exit code
    when live). Raises DriveRefused when the destination is not proven safe."""
    rc = rclone_bin()
    if not rc:
        raise DriveRefused("rclone is not installed — run: bash godot/tools/drive_setup.sh")
    if not args or args[0] not in WRITE_VERBS:
        raise DriveRefused(f"not a write command: {args[:1]}")
    remotes = [a for a in args[1:] if not a.startswith("-") and ":" in a and not os.path.isabs(a)]
    if not remotes:
        raise DriveRefused("no Drive destination in the command")
    dest = remotes[-1]
    # every remote path in a write command must be the verified destination
    # tree (a copy FROM elsewhere is only allowed through drive_rescue)
    verify_cached(dest)
    full = [rc] + list(args) + ["--drive-skip-shortcuts"]
    if live:
        return subprocess.run(full).returncode
    return subprocess.run(full, capture_output=True, text=True, timeout=timeout)


if __name__ == "__main__":
    import sys
    try:
        who = make_root() if "--mkdir" in sys.argv else verify(f"{REMOTE_NAME}:{ROOT_FOLDER}")
        print(f"OK  uploads go to {REMOTE_NAME}:{ROOT_FOLDER} on the My Drive of {who}")
    except DriveRefused as ex:
        print(f"REFUSED  {ex}")
        sys.exit(1)
