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
    python3 godot/tools/meshy_recover.py fetch-all --days 7     # every finished task → recovered/<id>.glb + thumbnail, to sort by eye

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


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("list"); p.add_argument("--days", type=int, default=7); p.add_argument("--all", action="store_true"); p.set_defaults(fn=cmd_list)
    p = sub.add_parser("fetch"); p.add_argument("task_id"); p.add_argument("slug"); p.set_defaults(fn=cmd_fetch)
    p = sub.add_parser("fetch-all"); p.add_argument("--days", type=int, default=7); p.set_defaults(fn=cmd_fetch_all)
    args = ap.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main() or 0)
