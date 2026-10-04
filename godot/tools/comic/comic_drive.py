#!/usr/bin/env python3
"""Google Drive for the comic tool's images — the same scheme Hero Studio uses.

Renders, sheets and reference pictures go to the Drive folder Hero Studio
already uses (gdrive:ModernMythology), under the same relative path they
have in the repo. Git keeps only a small manifest of what the Drive holds
(godot/tools/comic/drive_manifest.json: size + md5 per file), so any
checkout can pull back the pictures it lacks. rclone does the transfer;
`copy`, never `sync`: nothing on the Drive is ever deleted.

Set-up is shared with Hero Studio: rclone and its "gdrive" connection live
in your home folder, so signing in once from the game branch
(godot/tools/drive_setup.sh) covers both tools.

SAVE (the inspector's button, or `save` here) does what the old Deck paste
did, minus the images: commit the comic's text files, pull the branch
(keeping the Deck's references.json on a conflict), sync the references,
push; then upload the images to the Drive and commit + push the manifest.
Images already in git stay there; new ones are not added to git.

  python3 godot/tools/comic/comic_drive.py status   # set up? what is not on the Drive yet
  python3 godot/tools/comic/comic_drive.py save     # text to git, images to the Drive
  python3 godot/tools/comic/comic_drive.py push     # images to the Drive only
  python3 godot/tools/comic/comic_drive.py pull     # fetch the images this checkout lacks
"""

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent.parent

DRIVE_REMOTE = os.environ.get("MM_DRIVE_REMOTE", "gdrive:ModernMythology")
MANIFEST = HERE / "drive_manifest.json"
DRIVE_DIRS = [
    "godot/assets/comic",       # renders, sheets, refs, concept pulls
    "lore/drift_wood/refs",     # reference pictures kept with the lore
]
DRIVE_EXTS = {".png", ".jpg", ".jpeg", ".webp"}
# What SAVE commits to git: the comic's text (strips, references.json,
# manifests). Images are excluded — they go to the Drive.
GIT_PATHS = ["godot/tools/comic", "godot/assets/comic"]
IMAGE_EXCLUDES = [f":(exclude,glob)**/*{e}" for e in sorted(DRIVE_EXTS)]

LIVE = False            # the CLI sets it: rclone shows progress in the terminal
_md5_cache = {}
_lock = threading.Lock()


def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# ── rclone + set-up ──────────────────────────────────────────────────────

def rclone():
    found = shutil.which("rclone")
    if found:
        return found
    local = Path.home() / ".local" / "bin" / "rclone"
    return str(local) if local.exists() else None


def _remote_name():
    r = DRIVE_REMOTE
    return r.split(":", 1)[0] + ":" if ":" in r and not r.startswith("/") else None


def configured():
    rc = rclone()
    if not rc:
        return False
    name = _remote_name()
    if name is None:                 # a local folder (tests): always usable
        return True
    try:
        out = subprocess.run([rc, "listremotes"], capture_output=True, text=True, timeout=20).stdout
    except Exception:  # noqa: BLE001
        return False
    return name in out.split()


def setup_command():
    """Where drive_setup.sh lives: this checkout, or the main folder next to
    it (the comic folder is a worktree of the game folder)."""
    own = REPO / "godot" / "tools" / "drive_setup.sh"
    if own.exists():
        return f"bash {own}"
    try:
        common = subprocess.run(["git", "-C", str(REPO), "rev-parse", "--git-common-dir"],
                                capture_output=True, text=True, timeout=10).stdout.strip()
        main = (REPO / common).resolve().parent if common else None
        if main and (main / "godot" / "tools" / "drive_setup.sh").exists():
            return f"bash {main / 'godot' / 'tools' / 'drive_setup.sh'}"
    except Exception:  # noqa: BLE001
        pass
    return "bash godot/tools/drive_setup.sh  (in the game-branch folder)"


# ── manifest ─────────────────────────────────────────────────────────────

def _md5(p):
    st = p.stat()
    key = (str(p), st.st_size, st.st_mtime_ns)
    if key not in _md5_cache:
        h = hashlib.md5()
        with open(p, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
        _md5_cache[key] = h.hexdigest()
    return _md5_cache[key]


def load_manifest():
    try:
        return json.loads(MANIFEST.read_text())
    except (OSError, ValueError):
        return {"remote": DRIVE_REMOTE, "files": {}}


def local_files():
    out = []
    for d in DRIVE_DIRS:
        root = REPO / d
        if root.exists():
            out += [p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in DRIVE_EXTS]
    return out


def pending():
    """Local images the manifest does not record as on the Drive, as they are now."""
    files = load_manifest().get("files", {})
    out = []
    for p in local_files():
        r = str(p.relative_to(REPO))
        m = files.get(r)
        if not m or m.get("size") != p.stat().st_size or m.get("md5") != _md5(p):
            out.append(r)
    return out


def _record(paths):
    man = load_manifest()
    files = man.setdefault("files", {})
    now = now_iso()
    for r in paths:
        p = REPO / r
        if p.is_file():
            files[r] = {"size": p.stat().st_size, "md5": _md5(p), "at": now}
    man["remote"] = DRIVE_REMOTE
    MANIFEST.write_text(json.dumps(man, indent=1, sort_keys=True) + "\n")


def status():
    try:
        pend = pending()
    except Exception:  # noqa: BLE001
        pend = []
    return {"configured": configured(), "rclone": bool(rclone()), "remote": DRIVE_REMOTE,
            "pending": len(pend), "pending_files": pend[:12],
            "on_drive": len(load_manifest().get("files", {})), "setup": setup_command()}


# ── transfer ─────────────────────────────────────────────────────────────

def push():
    """Upload every image the Drive lacks, one chunk per folder, recording
    each chunk in the manifest as it lands — an interrupted upload resumes
    on the next run instead of starting over."""
    rc = rclone()
    if not rc:
        return {"ok": False, "steps": ["rclone is not installed — run: " + setup_command()]}
    if not configured():
        return {"ok": False, "steps": ["Google Drive is not set up — run: " + setup_command()]}
    steps = []
    with _lock:
        pend = pending()
        if not pend:
            return {"ok": True, "steps": ["Google Drive: already holds every comic image"]}
        chunks = {}
        for r in pend:
            d = next((d for d in DRIVE_DIRS if r.startswith(d + "/")), None)
            if d is None:
                continue
            rest = r[len(d) + 1:]
            key = d + "/" + rest.rsplit("/", 1)[0] if "/" in rest else d
            chunks.setdefault((d, key), []).append(r)
        done, total = 0, len(pend)
        for (d, key), rels in sorted(chunks.items()):
            with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as tf:
                tf.write("".join(r[len(d) + 1:] + "\n" for r in rels))
                lst = tf.name
            args = [rc, "copy", str(REPO / d), f"{DRIVE_REMOTE}/{d}", "--files-from", lst,
                    "--no-traverse", "--transfers", "8", "--checkers", "16"]
            try:
                if LIVE:
                    print(f"uploading {key} ({len(rels)} file(s); {done}/{total} done) …", flush=True)
                    r = subprocess.run(args + ["--progress", "--stats-one-line"])
                    err = "see the lines above"
                else:
                    r = subprocess.run(args, capture_output=True, text=True)
                    err = (r.stderr or r.stdout or "")[-300:]
            finally:
                os.unlink(lst)
            if r.returncode:
                steps.append(f"Google Drive upload failed for {key}: {err} ({done} of {total} up)")
                return {"ok": False, "steps": steps}
            _record(rels)
            done += len(rels)
        steps.append(f"Google Drive: uploaded {done} image(s) to {DRIVE_REMOTE}")
    return {"ok": True, "steps": steps}


def pull():
    """Fetch every image this checkout lacks from the Drive (never overwrites)."""
    rc = rclone()
    if not rc:
        return {"ok": False, "steps": ["rclone is not installed — run: " + setup_command()]}
    for d in DRIVE_DIRS:
        dst = REPO / d
        dst.mkdir(parents=True, exist_ok=True)
        if LIVE:
            print(f"pulling {d} …", flush=True)
        r = subprocess.run([rc, "copy", f"{DRIVE_REMOTE}/{d}", str(dst), "--ignore-existing", "--transfers", "4"],
                           capture_output=True, text=True, timeout=3600)
        # rclone exits 3 when the folder is not on the Drive yet: nothing to pull
        if r.returncode and r.returncode != 3 and "directory not found" not in (r.stderr or ""):
            return {"ok": False, "steps": [f"pull failed for {d}: {((r.stderr or r.stdout) or '')[-300:]}"]}
    return {"ok": True, "steps": [f"pulled from {DRIVE_REMOTE}: every comic image this checkout lacked"]}


# ── git (the old Deck paste, as code, without the images) ────────────────

def _git(*args, timeout=120):
    r = subprocess.run(["git", "-C", str(REPO), *args], capture_output=True, text=True, timeout=timeout)
    return r.returncode, (r.stdout or "").strip(), (r.stderr or "").strip()


def _branch():
    code, out, err = _git("rev-parse", "--abbrev-ref", "HEAD", timeout=10)
    return (None, err or "not a git checkout") if code else (out, None)


def _commit(message, steps):
    paths = [p for p in GIT_PATHS if (REPO / p).exists()]
    code, _, err = _git("add", "-A", "--", *paths, *IMAGE_EXCLUDES)
    if code:
        steps.append(f"git add failed: {err}")
        return False
    code, _, _ = _git("diff", "--cached", "--quiet", timeout=30)
    if code == 0:
        steps.append("git: nothing new to commit")
        return True
    code, out, err = _git("commit", "-q", "-m", message)
    if code:
        steps.append(f"git commit failed: {err or out}")
        return False
    steps.append("git: committed " + message)
    return True


def _pull_merge(branch, steps):
    """git pull --no-rebase; on a conflict keep the Deck's references.json and
    the branch's version of everything else (the README's Deck paste)."""
    code, _, _ = _git("ls-remote", "--exit-code", "--heads", "origin", branch, timeout=120)
    if code == 2:
        steps.append(f"git: origin/{branch} does not exist yet — this push creates it")
        return True
    code, out, err = _git("pull", "--no-rebase", "--no-edit", "origin", branch, timeout=600)
    if code == 0:
        return True
    code2, conflicted, _ = _git("diff", "--name-only", "--diff-filter=U", timeout=30)
    files = [f for f in conflicted.splitlines() if f.strip()]
    if not files:
        steps.append(f"git pull failed: {(err or out)[-300:]}")
        return False
    for f in files:
        side = "--ours" if f.endswith("godot/tools/comic/references.json") else "--theirs"
        _git("checkout", side, "--", f, timeout=30)
        _git("add", "--", f, timeout=30)
    code, out, err = _git("commit", "-q", "--no-edit", "-m", "merge · the Deck's references kept", timeout=60)
    if code:
        _git("merge", "--abort", timeout=30)
        steps.append(f"merge failed and was undone: {(err or out)[-300:]}")
        return False
    steps.append(f"merged the branch; kept the Deck's references.json ({len(files)} conflict(s) settled)")
    return True


def _refs_sync(steps):
    r = subprocess.run([sys.executable or "python3", "comic_tool.py", "refs", "sync"], cwd=str(HERE),
                       capture_output=True, text=True, timeout=300)
    if r.returncode:
        steps.append(f"refs sync failed: {(r.stderr or r.stdout)[-200:]}")
        return
    _commit("comic · refs sync after merge", steps)


def _push(branch, steps):
    code, out, err = _git("push", "-u", "origin", f"HEAD:{branch}", timeout=600)
    if code:
        steps.append(f"git push failed: {(err or out)[-300:]}")
        return False
    steps.append(f"git: pushed to origin/{branch}")
    return True


def save(message=None):
    """SAVE: text to git first (never waits on the Drive), then the images to
    the Drive, then the manifest to git."""
    steps = []
    branch, err = _branch()
    if err:
        return {"ok": False, "steps": [err]}
    if branch == "HEAD":
        return {"ok": False, "steps": ["the comic folder is not on a branch — check out the comic branch first"]}
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    if not _commit(message or f"comic · saved from the Deck ({stamp})", steps):
        return {"ok": False, "steps": steps}
    if not _pull_merge(branch, steps):
        return {"ok": False, "steps": steps}
    _refs_sync(steps)
    if not _push(branch, steps):
        return {"ok": False, "steps": steps}
    drive_ok = True
    if configured():
        try:
            res = push()
        except Exception as ex:  # noqa: BLE001
            res = {"ok": False, "steps": [f"Google Drive upload stopped: {ex}"]}
        steps += res["steps"]
        drive_ok = res["ok"]
        if not drive_ok:
            steps.append("the images uploaded so far are recorded; SAVE again to carry on from there")
    else:
        n = len(pending())
        if n:
            drive_ok = False
            steps.append(f"Google Drive is not set up — {n} image(s) are NOT backed up. Run: {setup_command()}")
    if _commit(f"comic · Drive manifest ({stamp})", steps):
        _push(branch, steps)
    return {"ok": drive_ok and "git push failed" not in " ".join(steps), "steps": steps}


def main(argv=None):
    global LIVE
    argv = sys.argv[1:] if argv is None else argv
    cmd = argv[0] if argv else "status"
    LIVE = True
    if cmd == "status":
        st = status()
        print(f"rclone:     {'installed' if st['rclone'] else 'MISSING'}")
        print(f"Drive:      {'connected (' + st['remote'] + ')' if st['configured'] else 'NOT set up'}")
        print(f"on Drive:   {st['on_drive']} image(s) recorded in {MANIFEST.relative_to(REPO)}")
        print(f"not yet:    {st['pending']} image(s)")
        for r in st["pending_files"]:
            print(f"            {r}")
        if not st["configured"]:
            print(f"\nset up once (shared with Hero Studio):  {st['setup']}")
        return 0 if st["configured"] else 1
    fn = {"save": save, "push": push, "pull": pull}.get(cmd)
    if fn is None:
        print(__doc__)
        return 2
    res = fn()
    for s in res["steps"]:
        print(("✓ " if res["ok"] else "· ") + s)
    return 0 if res["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
