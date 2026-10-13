#!/usr/bin/env python3
"""drive_guard_test.py — every way an upload could reach a shared drive is
refused (2026-10-13; the user: "I want nothing more going to a public shared
folder. Very serious."). A GATE: run by run_all_audits.sh and
run_changed_audits.sh; nonzero exit fails.

A fake `rclone` (written to a temp dir, first on PATH) answers `config dump`
and `lsjson` from a scenario and LOGS every other command. Each attack below
must raise DriveRefused with NOTHING written; the honest setup must write
exactly once, with --drive-skip-shortcuts. Then meshy_pipeline.drive_push
(Hero Studio's SAVE) is run end to end on both.
"""
import json
import os
import stat
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOLS = HERE.parent
sys.path.insert(0, str(TOOLS))

FAKE = r'''#!/usr/bin/env python3
import json, os, sys
sc = json.load(open(os.environ["FAKE_RCLONE_SCENARIO"]))
a = sys.argv[1:]
if a[:2] == ["config", "dump"]:
    print(json.dumps(sc["config"])); sys.exit(0)
if a[:1] == ["lsjson"]:
    print(json.dumps(sc.get("lsjson", []))); sys.exit(sc.get("lsjson_rc", 0))
if a[:1] == ["version"]:
    print("rclone v1.68.2"); sys.exit(0)
with open(os.environ["FAKE_RCLONE_LOG"], "a") as f:
    f.write(json.dumps(a) + "\n")
sys.exit(0)
'''

MY_DRIVE = {"gdrive": {"type": "drive", "scope": "drive", "token": "{}"}}
OWNED = [{"Name": "ModernMythology", "IsDir": True, "ID": "1Ofi", "Metadata": {"owner": "me@example.com"}}]
SHARED_LS = [{"Name": "ModernMythology", "IsDir": True, "ID": "1wBM", "Metadata": {}}]


def scenario(tmp, config=None, lsjson=None, env=None, owner_file=None):
    sc = {"config": config if config is not None else MY_DRIVE, "lsjson": lsjson if lsjson is not None else OWNED}
    p = Path(tmp) / "scenario.json"
    p.write_text(json.dumps(sc))
    log = Path(tmp) / "log.txt"
    log.write_text("")
    os.environ["FAKE_RCLONE_SCENARIO"] = str(p)
    os.environ["FAKE_RCLONE_LOG"] = str(log)
    for k in [k for k in os.environ if k.startswith("RCLONE_DRIVE_") or k.startswith("RCLONE_CONFIG_")]:
        del os.environ[k]
    for k, v in (env or {}).items():
        os.environ[k] = v
    import drive_guard
    drive_guard.OWNER_FILE = Path(tmp) / "owner.txt"
    if owner_file is not None:
        drive_guard.OWNER_FILE.write_text(owner_file)
    elif drive_guard.OWNER_FILE.exists():
        drive_guard.OWNER_FILE.unlink()
    drive_guard._VERIFIED.update(at=0.0, owner="")
    return log


def writes(log):
    return [json.loads(l) for l in log.read_text().splitlines() if l.strip()]


def main():
    tmp = tempfile.mkdtemp(prefix="drive_guard_test_")
    fake = Path(tmp) / "rclone"
    fake.write_text(FAKE)
    fake.chmod(fake.stat().st_mode | stat.S_IEXEC)
    os.environ["PATH"] = tmp + os.pathsep + os.environ.get("PATH", "")
    import drive_guard
    assert drive_guard.rclone_bin() == str(fake), drive_guard.rclone_bin()

    copy = ["copy", "/tmp/x", "gdrive:ModernMythology/godot/assets/3d/props", "--transfers", "8"]
    attacks = {
        "connection on the One Model Nation shared drive":
            dict(config={"gdrive": {"type": "drive", "team_drive": "0AEnZu3oDWBFuUk9PVA"}}),
        "connection on any other shared drive":
            dict(config={"gdrive": {"type": "drive", "team_drive": "0AXXXXXXXXXXXXXXXXX"}}),
        "root_folder_id (could sit in a shared drive)":
            dict(config={"gdrive": {"type": "drive", "root_folder_id": "1abc"}}),
        "env RCLONE_DRIVE_TEAM_DRIVE":
            dict(env={"RCLONE_DRIVE_TEAM_DRIVE": "0AEnZu3oDWBFuUk9PVA"}),
        "env RCLONE_CONFIG_GDRIVE_TEAM_DRIVE":
            dict(env={"RCLONE_CONFIG_GDRIVE_TEAM_DRIVE": "0AEnZu3oDWBFuUk9PVA"}),
        "folder Google reports with no owner (a shared drive)":
            dict(lsjson=SHARED_LS),
        "owner differs from the recorded owner":
            dict(owner_file="someone.else@example.com\n"),
        "Google does not answer":
            dict(lsjson=[]),
        "not a Google Drive connection":
            dict(config={"gdrive": {"type": "alias", "remote": "gdrive_modelnation:"}}),
    }
    fails = 0
    for name, kw in attacks.items():
        log = scenario(tmp, **kw)
        try:
            drive_guard.rclone_write(copy)
            ok = False
        except drive_guard.DriveRefused:
            ok = True
        if not ok or writes(log):
            fails += 1
            print(f"FAIL  {name}: {'not refused' if not ok else 'refused but wrote'} {writes(log)}")
        else:
            print(f"ok    refused: {name}")
    for name, args in {
        "another remote as destination": ["copy", "/tmp/x", "gdrive_modelnation:ModernMythology"],
        "a path outside ModernMythology": ["copy", "/tmp/x", "gdrive:Elsewhere"],
        "the bare root": ["copy", "/tmp/x", "gdrive:"],
        "an inline override in the remote name": ["copy", "/tmp/x", "gdrive,team_drive=0AEnZu3oDWBFuUk9PVA:ModernMythology"],
    }.items():
        log = scenario(tmp)
        try:
            drive_guard.rclone_write(args)
            ok = False
        except drive_guard.DriveRefused:
            ok = True
        if not ok or writes(log):
            fails += 1
            print(f"FAIL  {name}")
        else:
            print(f"ok    refused: {name}")

    # the honest setup writes once, never following shortcuts
    log = scenario(tmp)
    r = drive_guard.rclone_write(copy)
    w = writes(log)
    if r.returncode != 0 or len(w) != 1 or "--drive-skip-shortcuts" not in w[0]:
        fails += 1
        print(f"FAIL  honest write: {w}")
    else:
        print("ok    honest write to My Drive goes through (with --drive-skip-shortcuts)")

    # Hero Studio's SAVE end to end
    import meshy_pipeline as M
    M.drive_pending = lambda: ["godot/assets/3d/props/x.glb"]
    M._record_on_drive = lambda rels: None
    log = scenario(tmp, config={"gdrive": {"type": "drive", "team_drive": "0AEnZu3oDWBFuUk9PVA"}})
    res = M.drive_push()
    if res["ok"] or writes(log):
        fails += 1
        print(f"FAIL  SAVE on the shared drive: {res} {writes(log)}")
    else:
        print("ok    refused: Hero Studio SAVE with the connection on the shared drive")
    log = scenario(tmp, lsjson=SHARED_LS)
    res = M.drive_push()
    if res["ok"] or writes(log):
        fails += 1
        print(f"FAIL  SAVE into an ownerless folder: {res}")
    else:
        print("ok    refused: Hero Studio SAVE into a folder Google says has no owner")
    log = scenario(tmp)
    res = M.drive_push()
    if not res["ok"] or len(writes(log)) != 1:
        fails += 1
        print(f"FAIL  honest SAVE: {res} {writes(log)}")
    else:
        print("ok    honest SAVE to My Drive goes through")
    print("drive_guard_test · %d failure(s)" % fails)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
