#!/usr/bin/env python3
"""meshy_recover — the account remembers what the folder forgot.

2026-09-26: a day's worth of image-to-3D runs were not on the Deck's
disk (a checkout reset, a different clone, a page in download mode —
it does not matter which). Meshy keeps every task on the account, with
its thumbnail and its model URLs, and listing them costs nothing. This
lists the account's recent image-to-3d and multi-image-to-3d tasks and
pulls a chosen task's GLB into the canonical place for a roster slug,
with its thumbnail filed as a concept candidate so Hero Studio shows it.

    python3 godot/tools/meshy_recover.py list [--days 7] [--all]
    python3 godot/tools/meshy_recover.py fetch <task_id> <slug>
    python3 godot/tools/meshy_recover.py fetch-all --days 7     # every finished task → recovered/<id>.glb + thumbnail
    python3 godot/tools/meshy_recover.py contact                # one page of the recovered thumbnails with their ids
    python3 godot/tools/meshy_recover.py assign mapping.txt     # lines of `<id> <slug>` → GLBs to the heroes folder, thumbnails as candidates
    python3 godot/tools/meshy_recover.py adopt <manifest.json>  # a runner manifest from wherever it ran: every mesh job names its slug — no naming by hand

Keys come from the same files the pipeline uses (godot/tools/.meshy_key).
"""
import argparse
import datetime as dt
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import meshy_pipeline as M   # noqa: E402  (key files, http helpers, roster, paths)

RESOURCES = ("image-to-3d", "multi-image-to-3d", "text-to-3d")


def list_tasks(api_key, days, want_all):
    headers = {"Authorization": f"Bearer {api_key}"}
    since = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=days)
    out = []
    for res in RESOURCES:
        page = 1
        while True:
            try:
                tasks = M.http_json("GET", f"{M.MESHY_BASE}/{res}?page_num={page}&page_size=50&sort_by=-created_at", headers=headers, timeout=60)
            except Exception as exc:  # a resource the plan lacks, or a 404 on an empty list
                sys.stderr.write(f"  {res}: {exc}\n")
                break
            if isinstance(tasks, dict):
                tasks = tasks.get("result") or tasks.get("data") or tasks.get("tasks") or []
            if not tasks:
                break
            stop = False
            for t in tasks:
                created = t.get("created_at")
                when = dt.datetime.fromtimestamp(created / 1000.0, dt.timezone.utc) if isinstance(created, (int, float)) else None
                if when and when < since and not want_all:
                    stop = True
                    continue
                out.append({"resource": res, "id": t.get("id"), "status": t.get("status"), "when": when.isoformat(timespec="minutes") if when else "?",
                            "glb": (t.get("model_urls") or {}).get("glb", ""), "thumb": t.get("thumbnail_url", ""),
                            "art_style": t.get("art_style", ""), "textured": bool(t.get("texture_urls")), "progress": t.get("progress")})
            if stop or len(tasks) < 50:
                break
            page += 1
    out.sort(key=lambda r: r["when"], reverse=True)
    return out


def cmd_list(args):
    key = M.get_api_key("meshy")
    rows = list_tasks(key, args.days, args.all)
    if not rows:
        print("no tasks on the account in that window")
        return 0
    print(f"{'when (UTC)':17} {'resource':18} {'status':10} {'tex':3} {'id':26} thumbnail")
    for r in rows:
        print(f"{r['when']:17} {r['resource']:18} {str(r['status']):10} {'y' if r['textured'] else ' ':3} {str(r['id']):26} {r['thumb'][:70]}")
    print(f"\n{len(rows)} task(s). Recover one:  python3 godot/tools/meshy_recover.py fetch <id> <slug>")
    return 0


def _fetch(task, slug_or_none, api_key):
    headers = {"Authorization": f"Bearer {api_key}"}
    t = M.http_json("GET", f"{M.MESHY_BASE}/{task['resource']}/{task['id']}", headers=headers, timeout=60)
    glb = (t.get("model_urls") or {}).get("glb", "")
    if not glb:
        print(f"  {task['id']}: no GLB (status {t.get('status')})")
        return False
    if slug_or_none:
        roster = M.load_roster()
        entry = next((e for e in roster["entries"] if e["slug"] == slug_or_none), None)
        if entry is None:
            sys.exit(f"no roster slug {slug_or_none!r}")
        out = M.entry_out_path(entry)
        thumb_dir = M.entry_dir(entry)
        thumb = thumb_dir / f"{entry['slug']}_front_meshy_recovered.png"
    else:
        out = M.CONCEPT_ROOT / "recovered" / f"{task['id']}.glb"
        thumb = M.CONCEPT_ROOT / "recovered" / f"{task['id']}.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    thumb.parent.mkdir(parents=True, exist_ok=True)
    M.http_download(glb, out)
    print(f"  GLB  → {M.rel(out)}")
    th = t.get("thumbnail_url", "")
    if th:
        try:
            M.http_download(th, thumb)
            print(f"  thumb → {M.rel(thumb)}")
        except Exception as exc:
            print(f"  thumbnail failed: {exc}")
    M.append_manifest({"kind": "recovered", "task": task["id"], "resource": task["resource"], "slug": slug_or_none, "glb": M.rel(out), "when": M.now_iso()})
    return True


def cmd_fetch(args):
    key = M.get_api_key("meshy")
    rows = [r for r in list_tasks(key, 3650, True) if r["id"] == args.task_id]
    if not rows:
        sys.exit(f"task {args.task_id} not found on the account")
    return 0 if _fetch(rows[0], args.slug, key) else 1


def cmd_fetch_all(args):
    key = M.get_api_key("meshy")
    rows = [r for r in list_tasks(key, args.days, False) if r["glb"]]
    print(f"{len(rows)} finished task(s) → {M.rel(M.CONCEPT_ROOT / 'recovered')}")
    n = 0
    for r in rows:
        print(f"{r['when']} {r['id']}")
        n += 1 if _fetch(r, None, key) else 0
    print(f"recovered {n}; sort them by eye (the thumbnails), then move each GLB to godot/assets/3d/characters/heroes/<slug>.glb")
    return 0


RECOVERED = M.CONCEPT_ROOT / "recovered"


def cmd_contact(args):
    """One page of every recovered thumbnail with its task id, served by
    the runner at /assets/concept/meshy/recovered/index.html."""
    ids = sorted(p.stem for p in RECOVERED.glob("*.glb"))
    cards = []
    for i in ids:
        png = RECOVERED / f"{i}.png"
        img = f'<img src="{i}.png">' if png.exists() else '<div class="none">no thumbnail</div>'
        cards.append(f'<figure>{img}<figcaption><code>{i}</code></figcaption></figure>')
    html = ("<!doctype html><meta charset=utf-8><title>recovered models</title>"
            "<style>body{background:#111;color:#ddd;font:13px monospace;margin:16px}"
            ".grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px}"
            "figure{margin:0;background:#1a1a1a;padding:8px;border:1px solid #333}img{width:100%;display:block}"
            ".none{height:200px;display:grid;place-items:center;color:#666}figcaption{margin-top:6px;word-break:break-all}</style>"
            f"<h2>{len(ids)} recovered model(s)</h2><p>Write one line per model — <code>&lt;id&gt; &lt;roster slug&gt;</code> — into a text file, then "
            "<code>python3 godot/tools/meshy_recover.py assign that_file.txt</code>. Skip the ones you do not want.</p>"
            f'<div class="grid">{"".join(cards)}</div>')
    RECOVERED.mkdir(parents=True, exist_ok=True)
    (RECOVERED / "index.html").write_text(html)
    print(f"{len(ids)} model(s) → {M.rel(RECOVERED / 'index.html')}")
    print("with the runner up:  http://127.0.0.1:8765/assets/concept/meshy/recovered/index.html")
    return 0


def cmd_assign(args):
    """Each line `<task id> <roster slug>`: the GLB goes to the slug's
    canonical path, the thumbnail to its concept folder as a candidate
    and as front.png if it has none (so Hero Studio shows the model as
    installed and the image as chosen)."""
    import shutil
    roster = M.load_roster()
    by = {e["slug"]: e for e in roster["entries"]}
    n = 0
    for raw in Path(args.mapping).read_text().splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) != 2:
            print(f"  skip (need `<id> <slug>`): {raw}")
            continue
        tid, slug = parts
        entry = by.get(slug)
        if entry is None:
            print(f"  skip: no roster slug {slug!r} ({tid})")
            continue
        src = RECOVERED / f"{tid}.glb"
        if not src.exists():
            print(f"  skip: {M.rel(src)} not recovered yet ({slug})")
            continue
        out = M.entry_out_path(entry)
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(out))
        cdir = M.entry_dir(entry)
        cdir.mkdir(parents=True, exist_ok=True)
        thumb = RECOVERED / f"{tid}.png"
        if thumb.exists():
            cand = cdir / f"{slug}_front_meshy_recovered.png"
            shutil.copy2(str(thumb), str(cand))
            front = cdir / "front.png"
            if not front.exists():
                shutil.move(str(thumb), str(front))
            else:
                thumb.unlink()
        M.append_manifest({"kind": "assigned", "task": tid, "slug": slug, "glb": M.rel(out), "when": M.now_iso()})
        print(f"  {slug:28s} ← {tid}  → {M.rel(out)}")
        n += 1
    print(f"assigned {n}")
    return 0


def cmd_adopt(args):
    """Yesterday's runner wrote its manifest.json wherever it ran; every
    mesh job in it says `slug` and `task_id`. Given that file, pull each
    task's GLB straight to the slug's canonical path — no naming by hand."""
    data = json.loads(Path(args.manifest).read_text())
    if not isinstance(data, list):
        sys.exit("not a runner manifest (expected a list)")
    key = M.get_api_key("meshy")
    jobs = [(j.get("slug"), j.get("task_id"), j.get("resource", "image-to-3d")) for j in data if j.get("stage") == "mesh" and j.get("task_id") and j.get("slug")]
    print(f"{len(jobs)} mesh job(s) named in {args.manifest}")
    roster = M.load_roster()
    by = {e["slug"]: e for e in roster["entries"]}
    done = set()
    n = 0
    for slug, tid, res in reversed(jobs):          # newest first: the last run of a slug is the one that stands
        if slug in done:
            continue
        if slug not in by:
            print(f"  {slug}: not a roster slug any more — skipped ({tid})")
            continue
        out = M.entry_out_path(by[slug])
        if out.exists() and not args.overwrite:
            print(f"  {slug}: {M.rel(out)} already there (use --overwrite to replace)")
            done.add(slug)
            continue
        print(f"  {slug} ← {tid}")
        if _fetch({"id": tid, "resource": res}, slug, key):
            n += 1
            done.add(slug)
    print(f"adopted {n} model(s); the rest of the account's tasks stay recoverable by id")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("list"); p.add_argument("--days", type=int, default=7); p.add_argument("--all", action="store_true"); p.set_defaults(fn=cmd_list)
    p = sub.add_parser("fetch"); p.add_argument("task_id"); p.add_argument("slug"); p.set_defaults(fn=cmd_fetch)
    p = sub.add_parser("fetch-all"); p.add_argument("--days", type=int, default=7); p.set_defaults(fn=cmd_fetch_all)
    p = sub.add_parser("contact"); p.set_defaults(fn=cmd_contact)
    p = sub.add_parser("assign"); p.add_argument("mapping"); p.set_defaults(fn=cmd_assign)
    p = sub.add_parser("adopt"); p.add_argument("manifest"); p.add_argument("--overwrite", action="store_true"); p.set_defaults(fn=cmd_adopt)
    args = ap.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main() or 0)
