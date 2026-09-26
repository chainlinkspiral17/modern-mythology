#!/usr/bin/env python3
"""comic_inspector.py — browse and generate the Drift Wood / ROFLCOPTER run
on your own machine.

A local web page (stdlib only, no install) over the strip JSONs, the
reference sheets, the reference registry and every render on disk, with a
Generate button that runs the existing tools (comic_tool.py strip-prompts →
comic_render.py) for one strip or one sheet at a time and shows the result
when it lands.

  python3 godot/tools/comic/comic_inspector.py            # http://127.0.0.1:8765
  python3 godot/tools/comic/comic_inspector.py --open     # …and open the browser
  python3 godot/tools/comic/comic_inspector.py --port 9000

What it shows per strip: the script sheet (the same markdown as
lore/drift_wood/scripts/), the panels, the whole-strip prompt (lettered and
unlettered), the references that would be attached, and every render of it
from godot/assets/comic/vol10/{runway,google,concept}/. What it writes: a
`review` block into the strip JSON when you mark a strip (ok / revise / note)
— the validator ignores it, `md` shows it — and approve/reject on references.
Renders go where comic_render.py puts them, with the same manifests.

Keys: the runners read godot/tools/.runway_key / .google_key or the env, as
before. Nothing here talks to the network itself; the subprocess does.
"""
import argparse
import json
import re
import mimetypes
import os
import subprocess
import sys
import threading
import time
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import comic_tool as ct  # noqa: E402

REPO = ct.REPO
ASSETS = REPO / "godot" / "assets" / "comic" / "vol10"
PROVIDER_DIRS = ["runway", "google", "concept", "sheets"]
JOBS = {}
JOBS_LOCK = threading.Lock()
PY = sys.executable or "python3"


# ── data ─────────────────────────────────────────────────────────────────

def _renders_index():
    """slug → [render records] from every provider manifest + files on disk."""
    idx = {}
    for prov in PROVIDER_DIRS:
        d = ASSETS / prov
        if not d.exists():
            continue
        seen = set()
        mp = d / "manifest.json"
        if mp.exists():
            try:
                for r in json.loads(mp.read_text(encoding="utf-8")).get("renders", []):
                    f = REPO / r["file"] if r.get("file") else None
                    rec = dict(r)
                    rec["provider_dir"] = prov
                    rec["exists"] = bool(f and f.exists())
                    rec["url"] = "/asset/" + str(Path(r["file"]).relative_to("godot/assets/comic/vol10")).replace(os.sep, "/") if r.get("file") else None
                    rec["prompt"] = (r.get("prompt") or "")[:400]
                    idx.setdefault(r.get("slug") or r.get("strip_id"), []).append(rec)
                    if f:
                        seen.add(f.name)
            except (json.JSONDecodeError, KeyError, ValueError):
                pass
        for png in sorted(d.glob("*.png")):
            if png.name in seen:
                continue
            slug = re.sub(r"(_v\d+)?(_t\d+)?$", "", png.stem)
            idx.setdefault(slug, []).append({"slug": slug, "file": str(png.relative_to(REPO)), "provider": prov, "provider_dir": prov,
                                             "exists": True, "url": f"/asset/{prov}/{png.name}", "rendered_at": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(png.stat().st_mtime)), "prompt": ""})
    return idx


def _strip_summary(s, renders):
    r = renders.get(s["id"], [])
    return {"id": s["id"], "date": s["date"], "title": s.get("title", ""), "strip": s["strip"], "run": s.get("run"), "era": s["era"],
            "format": s["format"], "tier": s.get("tier"), "selection": s.get("selection"), "arc": s.get("arc", ""), "cast": s.get("cast", []),
            "location": s.get("location", ""), "mark": (s.get("margin") or {}).get("mark", ""), "logline": s.get("logline", ""),
            "renders": len([x for x in r if x.get("exists")]), "review": (s.get("review") or {}).get("status", ""), "file": s.get("_file")}


def api_strips():
    eras = ct.load_eras()
    renders = _renders_index()
    strips = ct.load_strips()
    return {"strips": [_strip_summary(s, renders) for s in strips],
            "eras": {k: v.get("name", k) for k, v in eras["eras"].items()},
            "counts": {"strips": len(strips), "rendered": sum(1 for s in strips if renders.get(s["id"]))}}


def api_strip(sid):
    eras = ct.load_eras()
    strips = [s for s in ct.load_strips() if s["id"] == sid]
    if not strips:
        return None
    s = strips[0]
    refs = ct.load_refs()
    prompt_l, neg_l = ct.compose_strip_prompt(s, eras, letter=True)
    prompt_c, _ = ct.compose_strip_prompt(s, eras, letter=True, compact=True)
    prompt_u, neg_u = ct.compose_strip_prompt(s, eras, letter=False)
    picks = {}
    for prov in ("runway", "google"):
        picks[prov] = [{"id": r["id"], "kind": r["kind"], "status": r.get("status"), "score": sc, "why": why, "tag": ct.ref_tag_name(r),
                        "file": r.get("file"), "url": _ref_url(r), "tags": r.get("tags", [])}
                       for r, sc, why in ct.select_refs(s, refs, provider=prov, include_draft=True)]
    renders = _renders_index().get(sid, [])
    rw, gg = ct.RATIOS.get(s["format"], ("1024:1024", "1:1"))
    md = ct.strip_to_md(s, eras)
    if s.get("review"):
        md += f"\n\n---\n\n**Review** · {s['review'].get('status','')} · {s['review'].get('note','')}\n"
    clean = {k: v for k, v in s.items() if not k.startswith("_")}
    return {"strip": clean, "md": md, "prompt": {"lettered": prompt_l, "compact": prompt_c, "negative_lettered": neg_l, "unlettered": prompt_u, "negative_unlettered": neg_u,
                                                  "runway_ratio": rw, "google_aspect": gg},
            "refs": picks, "renders": renders, "errors": ct.validate_strip(s, eras, ct.load_heroes())}


def _ref_url(r):
    f = r.get("file")
    if f and (REPO / f).exists():
        try:
            return "/asset/" + str(Path(f).relative_to("godot/assets/comic/vol10")).replace(os.sep, "/")
        except ValueError:
            return "/file/" + f
    return r.get("url")


def api_sheets():
    data = ct.load_json(ct.SHEETS_PATH)
    renders = _renders_index()
    refs = {r["id"]: r for r in ct.load_refs().get("references", [])}
    out = []
    for sh in data["sheets"]:
        r = refs.get(sh["id"], {})
        out.append({"id": sh["id"], "kind": sh["kind"], "era": sh["era"], "ratio": sh.get("ratio", "16:9"), "tags": sh.get("tags", []),
                    "prompt": sh["prompt"], "status": r.get("status", "missing"), "notes": r.get("notes", ""),
                    "renders": [x for x in renders.get(sh["id"], []) if x.get("exists")], "url": _ref_url(r) if r else None})
    return {"sheets": out}


def api_refs():
    refs = ct.load_refs()
    out = []
    for r in refs.get("references", []):
        d = dict(r)
        d["url"] = _ref_url(r)
        out.append(d)
    return {"policy": refs.get("policy", {}), "references": out}


def api_models():
    import comic_render as cr
    return {"models": cr.known_models()}


def discover(provider):
    import comic_render as cr
    key, src = _read_key(provider)
    if not key:
        return {"ok": False, "why": "no key saved for " + provider}
    try:
        return cr.discover_models(provider, key)
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "why": f"could not reach the provider: {e}"}


KEY_FILES = {"runway": (".runway_key", ["RUNWAYML_API_KEY"]), "google": (".google_key", ["GOOGLE_API_KEY", "GEMINI_API_KEY"])}


def _read_key(provider):
    fname, envs = KEY_FILES[provider]
    for e in envs:
        if os.environ.get(e, "").strip():
            return os.environ[e].strip(), f"env {e}"
    p = ct.HERE.parent / fname
    if p.exists():
        lines = [l.strip() for l in p.read_text().splitlines() if l.strip()]
        if lines:
            return lines[0], f"godot/tools/{fname}"
    return "", ""


def api_keys():
    out = {}
    for prov in KEY_FILES:
        key, src = _read_key(prov)
        hint = ""
        if key and prov == "runway" and not key.startswith("key_"):
            hint = "Runway developer-API keys start with key_ — this one doesn't; it may be a key for a different Runway product (the app or the MCP), which the API refuses."
        if key and prov == "google" and not key.startswith("AIza"):
            hint = "Google AI Studio keys start with AIza — this one doesn't."
        out[prov] = {"present": bool(key), "source": src, "masked": (key[:6] + "…" + key[-3:]) if len(key) > 12 else ("set" if key else ""), "hint": hint,
                     "file": f"godot/tools/{KEY_FILES[prov][0]}"}
    out["runway_ok"] = out["runway"]["present"]; out["google_ok"] = out["google"]["present"]
    return out


def set_key(provider, key):
    if provider not in KEY_FILES:
        return {"error": "provider must be runway or google"}
    key = (key or "").strip().strip('"').strip("'")
    p = ct.HERE.parent / KEY_FILES[provider][0]
    if not key:
        if p.exists():
            p.unlink()
        return {"ok": True, "removed": True}
    p.write_text(key + "\n", encoding="utf-8")
    try:
        os.chmod(p, 0o600)
    except OSError:
        pass
    return {"ok": True, "file": f"godot/tools/{KEY_FILES[provider][0]}"}


def test_key(provider):
    """One cheap authenticated call per provider: Runway GET /organization
    (credits), Google GET /models (also yields the live image-model list)."""
    import comic_render as cr
    key, src = _read_key(provider)
    if not key:
        return {"ok": False, "why": "no key saved"}
    try:
        if provider == "runway":
            st, raw = cr._http(f"{cr.RUNWAY_BASE}/organization", "GET", {"Authorization": f"Bearer {key}", "X-Runway-Version": cr.RUNWAY_API_VERSION}, None, timeout=30)
            body = raw.decode("utf-8", "replace")[:600]
            if st == 200:
                try:
                    d = json.loads(body); credits = d.get("creditBalance", d.get("credits"))
                except json.JSONDecodeError:
                    credits = None
                return {"ok": True, "status": st, "why": f"key accepted{f' · {credits} credits' if credits is not None else ''}", "body": body}
            why = {401: "key refused (401): wrong key, or a key for a different Runway product. The developer API wants a key made at dev.runwayml.com (starts with key_).",
                   403: "key refused (403): the key is valid but not allowed to do this; check the organization/plan at dev.runwayml.com.",
                   404: "the /organization probe isn't available on this API version; the key may still work for generation."}.get(st, f"HTTP {st}")
            return {"ok": False, "status": st, "why": why, "body": body}
        st, raw = cr._http(f"{cr.GOOGLE_BASE}/models?pageSize=200", "GET", {"x-goog-api-key": key}, None, timeout=30)
        body = raw.decode("utf-8", "replace")
        if st == 200:
            names = [m.get("name", "").split("/")[-1] for m in json.loads(body).get("models", [])]
            imgs = [n for n in names if "image" in n or "imagen" in n]
            return {"ok": True, "status": st, "why": f"key accepted · {len(names)} models visible · image models: {', '.join(imgs) or 'none listed'}", "models": imgs, "body": body[:300]}
        why = {400: "key refused (400): malformed or not an AI Studio key.", 403: "key refused (403): the key is valid but the Generative Language API isn't enabled for it, or it's restricted."}.get(st, f"HTTP {st}")
        return {"ok": False, "status": st, "why": why, "body": body[:600]}
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "why": f"could not reach the provider: {e}"}


def set_review(sid, status, note):
    p = ct.STRIPS / f"{sid}.json"
    if not p.exists():
        return {"error": "no such strip"}
    s = ct.load_json(p)
    if status:
        s["review"] = {"status": status, "note": note or "", "at": time.strftime("%Y-%m-%d")}
    else:
        s.pop("review", None)
    p.write_text(json.dumps(s, indent=2, ensure_ascii=False), encoding="utf-8")  # same shape as the batch writers: no trailing newline
    return {"ok": True, "review": s.get("review")}


def set_ref_status(rid, status, note=None):
    refs = ct.load_refs()
    hit = False
    for r in refs.get("references", []):
        if r["id"] == rid:
            r["status"] = status
            if note is not None:
                r["notes"] = note
            hit = True
    if not hit:
        return {"error": "no such reference"}
    ct.save_refs(refs)
    return {"ok": True}


# ── jobs (generation) ────────────────────────────────────────────────────

def _run(job):
    job["status"] = "running"
    job["started"] = time.time()
    try:
        for argv in job["commands"]:
            job["log"].append("$ " + " ".join(argv))
            proc = subprocess.Popen(argv, cwd=str(ct.HERE), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
            for line in proc.stdout:
                job["log"].append(line.rstrip("\n"))
            proc.wait()
            if proc.returncode != 0:
                job["status"] = "failed"
                job["log"].append(f"(exit {proc.returncode})")
                return
        job["status"] = "done"
    except Exception as e:  # noqa: BLE001
        job["status"] = "failed"
        job["log"].append(f"✗ {e}")
    finally:
        job["finished"] = time.time()


def start_job(body):
    kind = body.get("kind", "strip")  # strip | sheet
    target = body.get("id")
    provider = body.get("provider", "runway")
    if provider not in ("runway", "google"):
        return {"error": "provider must be runway or google"}
    if not target:
        return {"error": "id required"}
    variants = max(1, min(int(body.get("variants", 1) or 1), 6))
    queue = ct.OUT / f"inspector_{kind}_{target}.json"
    if kind == "sheet":
        compose = [PY, "comic_tool.py", "sheets", "--only", target, "--out", str(queue)]
    else:
        compose = [PY, "comic_tool.py", "strip-prompts", "--only", target, "--out", str(queue), "--provider", provider]
        if not body.get("letter", True):
            compose.append("--no-letter")
        if not body.get("refs", True):
            compose.append("--no-refs")
        if body.get("include_draft"):
            compose.append("--include-draft")
    render = [PY, "comic_render.py", "--provider", provider, "--queue", str(queue), "--variants", str(variants)]
    if body.get("model"):
        render += ["--model", body["model"]]
    if body.get("seed") not in (None, ""):
        render += ["--seed", str(int(body["seed"]))]
    if body.get("overwrite"):
        render.append("--overwrite")
    if body.get("dry_run"):
        render.append("--dry-run")
    jid = f"{int(time.time()*1000)}_{target}"
    job = {"id": jid, "kind": kind, "target": target, "provider": provider, "status": "queued", "log": [], "commands": [compose, render], "created": time.time()}
    with JOBS_LOCK:
        JOBS[jid] = job
    threading.Thread(target=_run, args=(job,), daemon=True).start()
    return {"ok": True, "job": _job_view(job)}


def _job_view(j):
    return {k: v for k, v in j.items() if k != "commands"} | {"commands": [" ".join(c) for c in j["commands"]], "log": j["log"][-80:]}


def api_jobs():
    with JOBS_LOCK:
        return {"jobs": [_job_view(j) for j in sorted(JOBS.values(), key=lambda j: -j["created"])][:40]}


# ── http ─────────────────────────────────────────────────────────────────

class H(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):  # quiet
        if "/api/jobs" not in (args[0] if args else ""):
            sys.stderr.write("· %s\n" % (fmt % args))

    def _send(self, code, body, ctype="application/json; charset=utf-8"):
        if isinstance(body, (dict, list)):
            body = json.dumps(body, ensure_ascii=False).encode("utf-8")
        elif isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _file(self, root, rel):
        p = (root / rel).resolve()
        if root.resolve() not in p.parents or not p.is_file():
            return self._send(404, {"error": "not found"})
        ctype = mimetypes.guess_type(str(p))[0] or "application/octet-stream"
        self._send(200, p.read_bytes(), ctype)

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        q = urllib.parse.parse_qs(u.query)
        path = u.path
        try:
            if path in ("/", "/index.html"):
                return self._send(200, PAGE, "text/html; charset=utf-8")
            if path == "/api/strips":
                return self._send(200, api_strips())
            if path == "/api/strip":
                d = api_strip(q.get("id", [""])[0])
                return self._send(200 if d else 404, d or {"error": "no such strip"})
            if path == "/api/sheets":
                return self._send(200, api_sheets())
            if path == "/api/refs":
                return self._send(200, api_refs())
            if path == "/api/keys":
                return self._send(200, api_keys())
            if path == "/api/models":
                return self._send(200, api_models())
            if path == "/api/jobs":
                return self._send(200, api_jobs())
            if path.startswith("/asset/"):
                return self._file(ASSETS, urllib.parse.unquote(path[len("/asset/"):]))
            if path.startswith("/file/"):
                return self._file(REPO, urllib.parse.unquote(path[len("/file/"):]))
            return self._send(404, {"error": "not found"})
        except Exception as e:  # noqa: BLE001
            return self._send(500, {"error": str(e)})

    def do_POST(self):
        u = urllib.parse.urlparse(self.path)
        n = int(self.headers.get("Content-Length") or 0)
        try:
            body = json.loads(self.rfile.read(n) or b"{}")
        except json.JSONDecodeError:
            return self._send(400, {"error": "bad json"})
        try:
            if u.path == "/api/generate":
                return self._send(200, start_job(body))
            if u.path == "/api/review":
                return self._send(200, set_review(body.get("id"), body.get("status"), body.get("note")))
            if u.path == "/api/ref_status":
                return self._send(200, set_ref_status(body.get("id"), body.get("status"), body.get("note")))
            if u.path == "/api/keys":
                return self._send(200, set_key(body.get("provider"), body.get("key")))
            if u.path == "/api/models/discover":
                return self._send(200, discover(body.get("provider")))
            if u.path == "/api/keys/test":
                return self._send(200, test_key(body.get("provider")))
            if u.path == "/api/md":
                subprocess.run([PY, "comic_tool.py", "md"], cwd=str(ct.HERE), check=False)
                return self._send(200, {"ok": True})
            return self._send(404, {"error": "not found"})
        except Exception as e:  # noqa: BLE001
            return self._send(500, {"error": str(e)})


# ── the page ─────────────────────────────────────────────────────────────

PAGE = r"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>COMIC INSPECTOR · Drift Wood / ROFLCOPTER</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
:root{--bg-0:#050304;--bg-1:#0e0908;--ink:#1a1410;--rule:#553318;--gold:#d8a060;--gold-hi:#ffd896;--text:#c8a878;--dim:#7a5828;--em:#4ea060;--em-hi:#a8e89c;--red:#b0342e;--paper:#f2ead8}
*{box-sizing:border-box}html,body{margin:0;background:var(--bg-0);color:var(--text);font:12px/1.5 "Courier New",monospace;height:100%}
header{display:flex;gap:18px;align-items:baseline;padding:12px 18px;border-bottom:1px solid var(--rule)}
header h1{margin:0;color:var(--gold-hi);font-size:15px;letter-spacing:.18em}header .sub{color:var(--dim);font-style:italic}
header .keys{margin-left:auto;font-size:11px}header .keys b{color:var(--em-hi)}header .keys s{color:var(--red)}
.mode{display:flex;gap:4px}.mode button{background:var(--bg-1);border:1px solid var(--rule);color:var(--text);padding:3px 10px;font:inherit;cursor:pointer;letter-spacing:.1em}
.mode button.on{color:var(--gold-hi);border-color:var(--gold)}
main{display:grid;grid-template-columns:380px 1fr;height:calc(100% - 50px)}
aside{border-right:1px solid var(--rule);display:flex;flex-direction:column;min-height:0}
.filters{padding:8px 10px;border-bottom:1px solid var(--rule);display:flex;flex-wrap:wrap;gap:5px}
.filters input,.filters select{background:var(--ink);border:1px solid var(--rule);color:var(--text);font:inherit;padding:3px 6px}
.filters input[type=text]{flex:1;min-width:120px}
.list{overflow:auto;flex:1}.row{padding:5px 10px;border-bottom:1px solid #1e1410;cursor:pointer;display:grid;grid-template-columns:78px 1fr auto;gap:8px;align-items:baseline}
.row:hover{background:var(--ink)}.row.sel{background:var(--ink);border-left:3px solid var(--gold)}
.row .d{color:var(--dim)}.row .t{color:var(--text)}.row .t small{color:var(--dim)}.row .b{display:flex;gap:4px}
.pill{border:1px solid var(--rule);padding:0 5px;font-size:9px;letter-spacing:.08em;color:var(--dim)}
.pill.r{color:var(--em-hi);border-color:var(--em)}.pill.A{color:var(--gold-hi)}.pill.ok{color:var(--em-hi)}.pill.revise{color:#ff9a8a;border-color:var(--red)}
.count{padding:5px 10px;color:var(--dim);border-top:1px solid var(--rule);font-size:11px}
section{overflow:auto;padding:14px 22px 60px;min-width:0}
h2{color:var(--gold);font-size:12px;letter-spacing:.16em;margin:22px 0 8px;padding-bottom:3px;border-bottom:1px solid var(--rule)}
h2:first-child{margin-top:0}
.head h1{margin:0;color:var(--gold-hi);font-size:18px}.head .meta{color:var(--dim);margin:4px 0 10px}.head .log{color:var(--text);font-style:italic;max-width:80ch}
.tabs{display:flex;gap:4px;margin:10px 0}.tabs button{background:var(--bg-1);border:1px solid var(--rule);color:var(--dim);padding:4px 12px;font:inherit;cursor:pointer;letter-spacing:.1em}
.tabs button.on{color:var(--gold-hi);border-color:var(--gold)}
.pane{display:none}.pane.on{display:block}
pre{white-space:pre-wrap;word-break:break-word;background:var(--bg-1);border:1px solid var(--rule);padding:10px 12px;color:var(--text);max-width:110ch}
.md h1{color:var(--gold-hi);font-size:16px}.md h2{border:0;margin-top:16px}.md h3{color:var(--gold);font-size:12px;margin:12px 0 4px}
.md table{border-collapse:collapse;margin:6px 0;max-width:110ch}.md td,.md th{border:1px solid var(--rule);padding:3px 8px;vertical-align:top;text-align:left}.md th{color:var(--gold)}
.md code{color:var(--em-hi)}.md blockquote{border-left:2px solid var(--rule);margin:6px 0;padding-left:10px;color:var(--text)}
.md p{max-width:90ch}
.gal{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:12px}
.card{background:var(--bg-1);border:1px solid var(--rule);padding:8px}.card img{width:100%;display:block;background:var(--paper);cursor:zoom-in}
.card .cap{color:var(--dim);font-size:10px;margin-top:5px;display:flex;justify-content:space-between;gap:8px}
.card .cap b{color:var(--text)}.card.missing{opacity:.55}
.gen{display:flex;flex-wrap:wrap;gap:10px 18px;align-items:center;background:var(--bg-1);border:1px solid var(--rule);padding:10px 12px;max-width:110ch}.gen>div{flex-basis:100%}
.gen label{color:var(--dim);display:flex;gap:6px;align-items:center}
.gen select,.gen input[type=number],.gen input[type=text]{background:var(--ink);border:1px solid var(--rule);color:var(--text);font:inherit;padding:3px 6px;width:130px}.gen select{width:auto;min-width:150px;max-width:320px}.gen label{white-space:nowrap}
button.go{background:var(--ink);border:1px solid var(--gold);color:var(--gold-hi);padding:6px 16px;font:inherit;cursor:pointer;letter-spacing:.14em}
button.go:disabled{opacity:.4;cursor:default}
button.sm{background:var(--ink);border:1px solid var(--rule);color:var(--text);padding:2px 8px;font:inherit;cursor:pointer;font-size:11px}
button.sm.ok{color:var(--em-hi);border-color:var(--em)}button.sm.bad{color:#ff9a8a;border-color:var(--red)}
.jobs .job{background:var(--bg-1);border:1px solid var(--rule);padding:8px 10px;margin-bottom:8px;max-width:110ch}
.job .st{letter-spacing:.12em;font-size:10px}.job .st.running{color:var(--gold-hi)}.job .st.done{color:var(--em-hi)}.job .st.failed{color:#ff9a8a}
.job pre{margin:6px 0 0;max-height:220px;overflow:auto;font-size:11px}
.refs .ref{display:grid;grid-template-columns:120px 1fr;gap:10px;background:var(--bg-1);border:1px solid var(--rule);padding:8px;margin-bottom:8px;max-width:110ch}
.refs img{width:120px;background:var(--paper)}.refs .why{color:var(--dim)}
.panels td:first-child{color:var(--gold);white-space:nowrap}
.review{display:flex;gap:8px;align-items:center;margin:8px 0}.review input{flex:1;max-width:60ch;background:var(--ink);border:1px solid var(--rule);color:var(--text);font:inherit;padding:3px 6px}
.empty{color:var(--dim);font-style:italic}
#lightbox{position:fixed;inset:0;background:rgba(0,0,0,.92);display:none;align-items:center;justify-content:center;z-index:9;cursor:zoom-out}
#lightbox img{max-width:96vw;max-height:96vh;background:var(--paper)}
kbd{border:1px solid var(--rule);padding:0 4px;color:var(--dim)}
@media (max-width:900px){main{grid-template-columns:1fr}aside{max-height:40vh}}
</style></head><body>
<header><h1>COMIC INSPECTOR</h1><span class="sub">Drift Wood / ROFLCOPTER · vol 10 · the run on disk</span>
<div class="mode"><button id="m-strips" class="on">STRIPS</button><button id="m-sheets">SHEETS</button><button id="m-refs">REFS</button><button id="m-jobs">JOBS</button><button id="m-keys">KEYS</button></div>
<div class="keys" id="keys"></div></header>
<main><aside>
<div class="filters">
<input type="text" id="q" placeholder="search id · title · arc · cast · location">
<select id="f-year"><option value="">year</option></select>
<select id="f-strip"><option value="">strip</option><option>drift_wood</option><option>rolfcoptr</option><option>roflcopter</option></select>
<select id="f-format"><option value="">format</option><option>biweekly</option><option>daily4</option><option>daily3</option><option>digest_cover</option><option>special</option><option>sunday</option><option>page</option><option>spread</option></select>
<select id="f-tier"><option value="">tier</option><option>A</option><option>B</option><option>C</option></select>
<select id="f-render"><option value="">renders</option><option value="yes">rendered</option><option value="no">not yet</option></select>
<select id="f-review"><option value="">review</option><option value="ok">ok</option><option value="revise">revise</option><option value="none">unmarked</option></select>
</div>
<div class="list" id="list"></div><div class="count" id="count"></div></aside>
<section id="detail"><p class="empty">Pick a strip. <kbd>j</kbd>/<kbd>k</kbd> move, <kbd>g</kbd> generate with the kept settings, <kbd>1</kbd>–<kbd>6</kbd> tabs.</p></section></main>
<div id="lightbox"><img id="lbimg"></div>
<script>
const $=s=>document.querySelector(s);const esc=s=>String(s??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
let MODE='strips',STRIPS=[],SHEETS=[],REFS=null,SEL=null,TAB='sheet',KEYS={},VIEW=[],MODELS={runway:[],google:[]};
const api=(p,o)=>fetch(p,o).then(r=>r.json());
function md(src){const L=src.split('\n'),out=[];let i=0,inT=false;while(i<L.length){let l=L[i];
 if(l.startsWith('|')){const rows=[];while(i<L.length&&L[i].startsWith('|')){rows.push(L[i]);i++;}const cells=r=>r.replace(/^\||\|$/g,'').split('|').map(c=>inl(c.trim()));
  let h='<table>';rows.forEach((r,k)=>{if(/^\|\s*-+/.test(r))return;const tag=k===0?'th':'td';h+='<tr>'+cells(r).map(c=>`<${tag}>${c}</${tag}>`).join('')+'</tr>';});out.push(h+'</table>');continue;}
 if(l.startsWith('```')){const b=[];i++;while(i<L.length&&!L[i].startsWith('```')){b.push(esc(L[i]));i++;}i++;out.push('<pre>'+b.join('\n')+'</pre>');continue;}
 const m=l.match(/^(#{1,4})\s+(.*)/);if(m){out.push(`<h${m[1].length}>${inl(m[2])}</h${m[1].length}>`);i++;continue;}
 if(l.startsWith('> ')){out.push('<blockquote>'+inl(l.slice(2))+'</blockquote>');i++;continue;}
 if(/^\s*[-*]\s+/.test(l)){let h='<ul>';while(i<L.length&&/^\s*[-*]\s+/.test(L[i])){h+='<li>'+inl(L[i].replace(/^\s*[-*]\s+/,''))+'</li>';i++;}out.push(h+'</ul>');continue;}
 if(l.trim()==='---'){out.push('<hr>');i++;continue;}
 if(/^<\/?(details|summary)/.test(l.trim())){out.push(l.trim().replace(/<summary>(.*)<\/summary>/,'<summary style="color:var(--dim);cursor:pointer">$1</summary>'));i++;continue;}
 if(l.trim()===''){i++;continue;}
 const p=[];while(i<L.length&&L[i].trim()!==''&&!/^(#|\||```|> |\s*[-*]\s|---)/.test(L[i])){p.push(L[i]);i++;}out.push('<p>'+inl(p.join(' '))+'</p>');}
 return out.join('\n');}
function inl(s){return esc(s).replace(/`([^`]+)`/g,'<code>$1</code>').replace(/\*\*([^*]+)\*\*/g,'<b>$1</b>').replace(/\*([^*]+)\*/g,'<i>$1</i>').replace(/\[([^\]]+)\]\(([^)]+)\)/g,'$1');}
async function loadKeys(){const k=await api('/api/keys');KEYS={runway:k.runway_ok,google:k.google_ok,info:k};try{MODELS=(await api('/api/models')).models;}catch(e){}$('#keys').innerHTML=`<a href="#" onclick="setMode('keys');return false" style="color:inherit">keys · runway ${KEYS.runway?'<b>found</b>':'<s>none</s>'} · google ${KEYS.google?'<b>found</b>':'<s>none</s>'}</a>`;}
async function loadStrips(){const d=await api('/api/strips');STRIPS=d.strips;const ys=[...new Set(STRIPS.map(s=>s.date.slice(0,4)))];$('#f-year').innerHTML='<option value="">year</option>'+ys.map(y=>`<option>${y}</option>`).join('');render();}
async function loadSheets(){SHEETS=(await api('/api/sheets')).sheets;render();}
async function loadRefs(){REFS=await api('/api/refs');render();}
function filt(){const q=$('#q').value.toLowerCase(),y=$('#f-year').value,st=$('#f-strip').value,f=$('#f-format').value,t=$('#f-tier').value,r=$('#f-render').value,rv=$('#f-review').value;
 return STRIPS.filter(s=>(!y||s.date.startsWith(y))&&(!st||s.strip===st)&&(!f||s.format===f)&&(!t||s.tier===t)&&(!r||(r==='yes'?s.renders>0:s.renders===0))&&(!rv||(rv==='none'?!s.review:s.review===rv))
  &&(!q||[s.id,s.title,s.arc,s.location,s.logline,...(s.cast||[])].join(' ').toLowerCase().includes(q)));}
function render(){const list=$('#list');if(MODE==='strips'){VIEW=filt();list.innerHTML=VIEW.map(s=>`<div class="row ${SEL===s.id?'sel':''}" data-id="${s.id}"><span class="d">${s.date}</span><span class="t">${esc(s.title)}<br><small>${s.format} · ${esc(s.arc)}</small></span><span class="b">${s.review?`<span class="pill ${s.review}">${s.review}</span>`:''}<span class="pill ${s.tier}">${s.tier}</span>${s.renders?`<span class="pill r">${s.renders}✓</span>`:''}</span></div>`).join('');
  $('#count').textContent=`${VIEW.length} of ${STRIPS.length} strips · ${STRIPS.filter(s=>s.renders).length} rendered`;}
 else if(MODE==='sheets'){const q=$('#q').value.toLowerCase();VIEW=SHEETS.filter(s=>!q||(s.id+' '+s.kind+' '+s.tags.join(' ')).toLowerCase().includes(q));
  list.innerHTML=VIEW.map(s=>`<div class="row ${SEL===s.id?'sel':''}" data-id="${s.id}"><span class="d">${s.era}</span><span class="t">${esc(s.id)}<br><small>${s.kind} · ${s.ratio}</small></span><span class="b"><span class="pill ${s.status==='approved'?'ok':s.status==='draft'?'A':''}">${s.status}</span>${s.renders.length?`<span class="pill r">${s.renders.length}✓</span>`:''}</span></div>`).join('');
  $('#count').textContent=`${VIEW.length} sheets · ${SHEETS.filter(s=>s.status==='approved').length} approved · ${SHEETS.filter(s=>s.renders.length).length} rendered`;}
 else if(MODE==='refs'){if(!REFS){list.innerHTML='';return;}const q=$('#q').value.toLowerCase();VIEW=REFS.references.filter(r=>!q||(r.id+' '+r.kind+' '+(r.tags||[]).join(' ')).toLowerCase().includes(q));
  list.innerHTML=VIEW.map(r=>`<div class="row ${SEL===r.id?'sel':''}" data-id="${r.id}"><span class="d">${r.kind}</span><span class="t">${esc(r.id)}<br><small>${esc((r.tags||[]).join(' '))}</small></span><span class="b"><span class="pill ${r.status==='approved'?'ok':r.status==='draft'?'A':''}">${r.status}</span></span></div>`).join('');
  $('#count').textContent=`${VIEW.length} references · policy: max ${JSON.stringify(REFS.policy.max_refs||{})}`;}
 else{list.innerHTML='';$('#count').textContent='';}
 list.querySelectorAll('.row').forEach(el=>el.onclick=()=>open(el.dataset.id));const sel=list.querySelector('.row.sel');if(sel)sel.scrollIntoView({block:'nearest'});}
async function open(id){SEL=id;render();const el=$('#detail');el.innerHTML='<p class="empty">loading…</p>';
 if(MODE==='strips'){const d=await api('/api/strip?id='+encodeURIComponent(id));if(d.error){el.innerHTML='<p class="empty">'+esc(d.error)+'</p>';return;}renderStrip(d);}
 else if(MODE==='sheets'){renderSheet(SHEETS.find(s=>s.id===id));}
 else if(MODE==='refs'){renderRef(REFS.references.find(r=>r.id===id));}}
let GEN={};try{GEN=JSON.parse(localStorage.getItem('comic.gen')||'{}');}catch(e){GEN={};}
function saveGen(){const f=$('#g-prov');if(!f)return;GEN={prov:$('#g-prov').value,model:$('#g-model').value,custom:$('#g-custom').value,variants:$('#g-var').value,seed:$('#g-seed').value,
 letter:$('#g-letter')?$('#g-letter').checked:GEN.letter,refs:$('#g-refs')?$('#g-refs').checked:GEN.refs,draft:$('#g-draft')?$('#g-draft').checked:GEN.draft,over:$('#g-over').checked,dry:$('#g-dry').checked};
 try{localStorage.setItem('comic.gen',JSON.stringify(GEN));}catch(e){}$('#g-remember').textContent='settings kept for every strip';}
function modelOptions(prov,sel){const ms=MODELS[prov]||[];const opts=['<option value="">default ('+(ms[0]?ms[0].id:'provider default')+')</option>'].concat(ms.map(m=>`<option value="${m.id}" title="${esc(m.note)}">${esc(m.label)}${m.verified?'':' · unverified id'}</option>`),['<option value="__custom">other id…</option>']).join('');
 return opts.replace(`value="${sel||''}"`,`value="${sel||''}" selected`);}
function onProv(){const p=$('#g-prov').value;$('#g-model').innerHTML=modelOptions(p,'');$('#g-custom').style.display='none';onModel();}
function onModel(){const v=$('#g-model').value;$('#g-custom').style.display=v==='__custom'?'inline-block':'none';const p=$('#g-prov').value;const m=(MODELS[p]||[]).find(x=>x.id===v);$('#g-note').textContent=m?m.note:(v==='__custom'?'type the exact id from the provider\'s docs; it is passed through unchanged':'');saveGen();}
function genForm(kind,id,fmt){const avail=p=>p==='runway'?KEYS.runway:KEYS.google;let prov=GEN.prov&&avail(GEN.prov)?GEN.prov:(KEYS.runway?'runway':'google');const nokey=!KEYS.runway&&!KEYS.google;
 const ck=(k,def)=>(GEN[k]===undefined?def:GEN[k])?'checked':'';
 return `${nokey?'<div class="job" style="border-color:var(--red)"><span class="st failed">NO KEYS</span> · nothing can generate until a key is saved. <a href="#" onclick="setMode(&quot;keys&quot;);return false" style="color:var(--gold-hi)">Open KEYS</a> to paste one and test it.</div>':''}<div class="gen"><label>provider <select id="g-prov" onchange="onProv()"><option value="runway" ${KEYS.runway?'':'disabled'} ${prov==='runway'?'selected':''}>runway${KEYS.runway?'':' (no key)'}</option><option value="google" ${KEYS.google?'':'disabled'} ${prov==='google'?'selected':''}>google${KEYS.google?'':' (no key)'}</option></select></label>
 <label>model <select id="g-model" onchange="onModel()">${modelOptions(prov,GEN.prov===prov?GEN.model:'')}</select><input type="text" id="g-custom" placeholder="exact model id" value="${esc(GEN.custom||'')}" oninput="saveGen()" style="display:${GEN.prov===prov&&GEN.model==='__custom'?'inline-block':'none'};width:200px"></label>
 <label>variants <input type="number" id="g-var" min="1" max="6" value="${GEN.variants||1}" onchange="saveGen()"></label><label>seed <input type="number" id="g-seed" placeholder="random" value="${esc(GEN.seed||'')}" onchange="saveGen()"></label>
 ${kind==='strip'?`<label><input type="checkbox" id="g-letter" ${ck('letter',true)} onchange="saveGen()"> letter balloons</label><label><input type="checkbox" id="g-refs" ${ck('refs',true)} onchange="saveGen()"> attach references</label><label><input type="checkbox" id="g-draft" ${ck('draft',false)} onchange="saveGen()"> allow draft refs</label>`:''}
 <label><input type="checkbox" id="g-over" ${ck('over',false)} onchange="saveGen()"> replace take 1 (else: new take)</label><label><input type="checkbox" id="g-dry" ${ck('dry',false)} onchange="saveGen()"> dry run</label>
 <button class="go" id="g-go" onclick="generate('${kind}','${id}')">GENERATE</button><span class="empty" id="g-msg"></span><div class="empty" id="g-note">${esc(((MODELS[prov]||[]).find(x=>x.id===GEN.model)||{}).note||'')}</div><div class="empty"><span id="g-remember">${GEN.prov?'settings kept for every strip':'settings are kept once you change them'}</span> · menu: ${(MODELS[prov]||[]).length} models · <a href="#" onclick="setMode('keys');return false" style="color:var(--gold)">fetch the provider's current list</a> (KEYS → fetch model list)</div></div>`;}
async function generate(kind,id){let model=$('#g-model').value;if(model==='__custom')model=$('#g-custom').value.trim();const b={kind,id,provider:$('#g-prov').value,model,variants:+$('#g-var').value,seed:$('#g-seed').value,overwrite:$('#g-over').checked,dry_run:$('#g-dry').checked};
 if(kind==='strip'){b.letter=$('#g-letter').checked;b.refs=$('#g-refs').checked;b.include_draft=$('#g-draft').checked;}
 $('#g-go').disabled=true;const r=await api('/api/generate',{method:'POST',body:JSON.stringify(b)});$('#g-go').disabled=false;
 $('#g-msg').textContent=r.error?('✗ '+r.error):'queued → JOBS · every run is a new take';if(!r.error){showLastRun(id);watch(r.job.id,()=>{if(SEL===id){TAB='renders';open(id);}if(MODE==='strips')loadStrips();else loadSheets();});}}
function watch(jid,done){const t=setInterval(async()=>{const j=(await api('/api/jobs')).jobs.find(x=>x.id===jid);if(!j)return clearInterval(t);const m=$('#g-msg');if(m)m.textContent=`${j.status}`;if(j.status==='done'||j.status==='failed'){clearInterval(t);done&&done();}},2000);}
function gallery(rs){if(!rs.length)return '<p class="empty">no renders on disk yet</p>';return '<div class="gal">'+rs.map(r=>`<div class="card ${r.exists?'':'missing'}">${r.exists?`<img src="${r.url}" onclick="lb('${r.url}')">`:'<div class="empty">file not on disk (see manifest / fetch_concept.py)</div>'}<div class="cap"><b>${esc(r.provider||r.provider_dir)}${r.model?' · '+esc(r.model):''}${r.seed!=null?' · seed '+r.seed:''}</b><span>${esc((r.rendered_at||'').slice(0,16))}</span></div><div class="cap"><span>${esc(r.file||'')}</span></div></div>`).join('')+'</div>';}
function lb(u){$('#lbimg').src=u;$('#lightbox').style.display='flex';}$('#lightbox').onclick=()=>$('#lightbox').style.display='none';
function renderStrip(d){const s=d.strip,p=d.prompt,rv=s.review||{};const el=$('#detail');setTimeout(()=>showLastRun(s.id),0);
 const tabs=[['sheet','SHEET'],['panels','PANELS'],['prompt','PROMPT'],['refs','REFS'],['renders',`RENDERS ${d.renders.filter(r=>r.exists).length}`],['json','JSON']];
 el.innerHTML=`<div class="head"><h1>${esc(s.title)}</h1><div class="meta">${s.id} · ${s.date} · ${s.strip} · run ${s.run} · ${s.era} · ${s.format} · tier ${s.tier} · ${s.selection} · ${esc(s.arc)} · ${esc(s.location)} · mark ${esc(s.margin?.mark)}</div><div class="log">${esc(s.logline)}</div>
 ${d.errors.length?`<pre style="border-color:var(--red)">${esc(d.errors.join('\n'))}</pre>`:''}
 <div class="review"><span class="pill ${rv.status||''}">${rv.status||'unreviewed'}</span><button class="sm ok" onclick="review('${s.id}','ok')">ok</button><button class="sm bad" onclick="review('${s.id}','revise')">revise</button><button class="sm" onclick="review('${s.id}','')">clear</button><input id="rv-note" placeholder="note for the writer (saved into the strip JSON)" value="${esc(rv.note||'')}"><button class="sm" onclick="review('${s.id}','${rv.status||'ok'}')">save note</button></div></div>
 <div class="tabs">${tabs.map(t=>`<button class="${TAB===t[0]?'on':''}" onclick="tab('${t[0]}')">${t[1]}</button>`).join('')}</div>
 <div class="pane ${TAB==='sheet'?'on':''}" id="p-sheet"><div class="md">${md(d.md)}</div></div>
 <div class="pane ${TAB==='panels'?'on':''}" id="p-panels"><table class="panels md"><tr><th>#</th><th>shot</th><th>composition</th><th>who</th><th>balloons</th><th>image prompt</th><th>notes</th></tr>${s.panels.map(x=>`<tr><td>${x.n}${x.name?'<br>'+esc(x.name):''}</td><td>${esc(x.shot)}</td><td>${esc(x.composition)}${x.caption?'<br><i>caption: '+esc(x.caption)+'</i>':''}${x.sfx?'<br><i>sfx: '+esc(x.sfx)+'</i>':''}</td><td>${(x.characters||[]).map(c=>esc(c.id)+(c.pose?' · <small>'+esc(c.pose)+'</small>':'')).join('<br>')}</td><td>${(x.balloons||[]).map(b=>'<b>'+esc(b.who)+'</b> '+esc(b.text)+(b.kind?' <small>('+esc(b.kind)+')</small>':'')).join('<br>')}</td><td>${esc(x.image?.prompt)}</td><td>${esc(x.image?.notes)}</td></tr>`).join('')}</table></div>
 <div class="pane ${TAB==='prompt'?'on':''}" id="p-prompt"><h2>whole-strip prompt · lettered · ${p.lettered.length} chars <button class="sm" onclick="copy('pl')">copy</button></h2><pre id="pl">${esc(p.lettered)}</pre><p class="empty">negative: ${esc(p.negative_lettered)} · runway ${p.runway_ratio} · google ${p.google_aspect}</p>
  <h2>compact · ${p.compact.length} chars${p.compact.length>1000?' · <span style="color:#ff9a8a">still over gen4_image\'s 1000; use another model or shorten the dialogue</span>':' · fits gen4_image\'s 1000'} <button class="sm" onclick="copy('pc')">copy</button></h2><pre id="pc">${esc(p.compact)}</pre><p class="empty">sent instead of the full prompt when a model's limit is 1000 characters (gen4) or when the provider rejects the length. Dialogue is never shortened; only the style line and the panel descriptions are.</p>
  <h2>unlettered (production) <button class="sm" onclick="copy('pu')">copy</button></h2><pre id="pu">${esc(p.unlettered)}</pre><p class="empty">negative: ${esc(p.negative_unlettered)}</p></div>
 <div class="pane ${TAB==='refs'?'on':''}" id="p-refs"><div class="refs">${['runway','google'].map(pr=>`<h2>${pr} would attach (${d.refs[pr].length})</h2>`+(d.refs[pr].length?d.refs[pr].map(r=>`<div class="ref">${r.url?`<img src="${r.url}" onclick="lb('${r.url}')">`:'<div class="empty">no image yet</div>'}<div><b>@${esc(r.tag)}</b> · ${esc(r.id)} · ${r.kind} · <span class="pill ${r.status==='approved'?'ok':'A'}">${r.status}</span> · score ${r.score}<br><span class="why">${esc(r.why.join(', '))}</span><br><small>${esc(r.tags.join(' '))}</small><br><button class="sm ok" onclick="refStatus('${r.id}','approved')">approve</button> <button class="sm bad" onclick="refStatus('${r.id}','rejected')">reject</button></div></div>`).join(''):'<p class="empty">none approved that match · render the sheets first (SHEETS mode) or tick "allow draft refs"</p>')).join('')}</div></div>
 <div class="pane ${TAB==='renders'?'on':''}" id="p-renders"><h2>generate</h2>${genForm('strip',s.id,s.format)}<div id="lastrun"></div><h2>on disk</h2>${gallery(d.renders)}</div>
 <div class="pane ${TAB==='json'?'on':''}" id="p-json"><pre>${esc(JSON.stringify(s,null,2))}</pre><p class="empty">file: strips/${s.id}.json · edit the JSON, then <button class="sm" onclick="regenMd()">regenerate the md sheets</button></p></div>`;}
function renderSheet(s){const el=$('#detail');showLastRun(s.id);el.innerHTML=`<div class="head"><h1>${esc(s.id)}</h1><div class="meta">${s.kind} · ${s.era} · ${s.ratio} · <span class="pill ${s.status==='approved'?'ok':'A'}">${s.status}</span> · ${esc(s.tags.join(' '))}</div><div class="log">${esc(s.prompt)}</div>
 <div class="review"><button class="sm ok" onclick="refStatus('${s.id}','approved')">approve</button><button class="sm bad" onclick="refStatus('${s.id}','rejected')">reject</button><button class="sm" onclick="refStatus('${s.id}','draft')">draft</button><span class="empty">${esc(s.notes||'')}</span></div></div>
 <h2>generate</h2>${genForm('sheet',s.id)}<div id="lastrun"></div><h2>on disk</h2>${gallery(s.renders)}<p class="empty">after a render, run <code>comic_tool.py refs sync</code> (or just approve here — sync also picks the file up).</p>`;}
function renderRef(r){const el=$('#detail');el.innerHTML=`<div class="head"><h1>${esc(r.id)}</h1><div class="meta">${r.kind} · <span class="pill ${r.status==='approved'?'ok':'A'}">${r.status}</span> · ${esc((r.tags||[]).join(' '))}</div><div class="log">${esc(r.notes||'')}</div>
 <div class="review"><button class="sm ok" onclick="refStatus('${r.id}','approved')">approve</button><button class="sm bad" onclick="refStatus('${r.id}','rejected')">reject</button><button class="sm" onclick="refStatus('${r.id}','draft')">draft</button></div></div>
 ${r.url?`<div class="gal"><div class="card"><img src="${r.url}" onclick="lb('${r.url}')"><div class="cap"><span>${esc(r.file||r.url)}</span></div></div></div>`:'<p class="empty">no image on disk'+(r.runway_task_id?' · runway task '+esc(r.runway_task_id):'')+'</p>'}
 <h2>registry entry</h2><pre>${esc(JSON.stringify(r,null,2))}</pre>`;}
function explain(j){const log=j.log.join('\n');
 if(/no API key/.test(log))return 'No API key for '+j.provider+'. Put it in godot/tools/.'+(j.provider==='runway'?'runway_key':'google_key')+' (one line) or export the env var, then generate again.';
 if(/doesn't take .* using its closest size/.test(log)&&j.status==='done')return 'Rendered. This model has its own size list; the closest size to the strip was used and remembered.';
 if(/submit 4(00|22)/.test(log))return 'The provider rejected the request (HTTP 400). If the body names the model, the id is wrong for this API — fix it in the "other id…" box. If it names another field, paste the body to me.';
 if(/submit 401|submit 403|PERMISSION_DENIED|API key not valid/.test(log))return 'The key was refused (401/403). Check the key file has the right key and nothing else in it.';
 if(/submit 429|RESOURCE_EXHAUSTED|insufficient/i.test(log))return 'Out of credits or rate-limited (429). Wait, or add credits on the provider.';
 if(/task FAILED|CANCELLED/.test(log))return 'The provider accepted the job and then failed it (often content moderation on a prompt with people, or an internal error). Try again with a different seed or model.';
 if(/dry run/.test(log))return 'That was a dry run: the prompt was printed and nothing was sent. Untick "dry run" to render.';
 if(/exists, skip/.test(log))return 'The file already existed and skip mode was on. Every run is a new take now; if you still see this, pull the latest.';
 if(/Traceback/.test(log))return 'The tool itself crashed. The traceback below is the bug; paste it to me.';
 if(/wrote 0 strip prompts|wrote 0 sheet prompts/.test(log))return 'No strip matched that id when composing the prompt; the id may have changed. Reload the page.';
 if(j.status==='done'&&/✓/.test(log))return 'Rendered. It is in the gallery below (reload the tab if not).';
 if(j.status==='done')return 'Finished with nothing rendered; read the log.';
 if(j.status==='running')return 'Running… the provider usually takes 20–90 seconds.';
 return '';}
let LASTRUN_HTML='';function showLastRun(id){api('/api/jobs').then(d=>{const box=$('#lastrun');if(!box)return;const wasOpen=!!(box.querySelector('details')&&box.querySelector('details').open);const js=d.jobs.filter(j=>j.target===id);if(!js.length){box.innerHTML='<p class="empty">no runs yet this session. Pick a provider and model above and press GENERATE. The result, or the reason it failed, appears here.</p>';return;}
 const j=js[0];const bad=j.log.filter(l=>/✗|error|Error|Traceback|FAILED|400|401|403|429|500/.test(l));const why=explain(j);
 const html=`<div class="job" style="border-color:${j.status==='failed'?'var(--red)':j.status==='done'?'var(--em)':'var(--gold)'}"><span class="st ${j.status}">${j.status.toUpperCase()}</span> · ${esc(j.target)} · ${j.provider}${j.commands[1].includes('--model')?' · '+esc(j.commands[1].split('--model ')[1].split(' ')[0]):''}<div style="margin:6px 0;color:var(--text)">${esc(why)}</div>${bad.length?'<pre style="border-color:var(--red)">'+esc(bad.join('\n'))+'</pre>':''}<details><summary style="cursor:pointer;color:var(--dim)">full log</summary><pre>${esc(j.commands.join('\n'))}\n\n${esc(j.log.join('\n'))}</pre></details>${js.length>1?'<div class="empty">'+(js.length-1)+' earlier run'+(js.length>2?'s':'')+' under JOBS</div>':''}</div>`;
 if(html!==LASTRUN_HTML){LASTRUN_HTML=html;box.innerHTML=html;const det=box.querySelector('details');if(det&&(wasOpen||LOGOPEN))det.open=true;if(det)det.ontoggle=()=>{LOGOPEN=det.open;};}
 if(j.status==='running'||j.status==='queued')setTimeout(()=>{if(SEL===id)showLastRun(id);},2000);});}
let LOGOPEN=false;
function renderKeys(){const k=KEYS.info||{};const row=p=>{const i=k[p]||{};return `<div class="job" style="border-color:${i.present?'var(--em)':'var(--rule)'}"><span class="st ${i.present?'done':''}">${p.toUpperCase()}</span> · ${i.present?'saved · '+esc(i.masked)+' · from '+esc(i.source):'no key'}${i.hint?'<div style="color:#ff9a8a;margin-top:4px">'+esc(i.hint)+'</div>':''}
 <div style="display:flex;gap:8px;margin-top:8px;flex-wrap:wrap"><input type="password" id="k-${p}" placeholder="${p==='runway'?'paste the developer-API key (starts with key_)':'paste the AI Studio key (starts with AIza)'}" style="flex:1;min-width:280px;background:var(--ink);border:1px solid var(--rule);color:var(--text);font:inherit;padding:4px 6px"><button class="sm ok" onclick="saveKey('${p}')">save</button><button class="sm" onclick="testKey('${p}')">test</button><button class="sm" onclick="discoverModels('${p}')">fetch model list</button><button class="sm bad" onclick="if(confirm('remove the saved ${p} key?'))saveKey('${p}',true)">remove</button></div>
 <div class="empty" style="margin-top:6px">saved to <code>${esc(i.file)}</code> on this machine only (git ignores it)</div><div id="kr-${p}" style="margin-top:6px"></div></div>`;};
 $('#detail').innerHTML='<h2>keys</h2><p class="empty">Two providers. Save a key, press test (Runway answers with your credit balance; Google with what the key can see), then press fetch model list: it asks the provider which model ids it accepts right now — no credits spent — and the menu uses that list from then on (saved in out/models_learned.json).</p>'+row('runway')+row('google')+'<h2>where keys come from</h2><ul class="md"><li><b>Runway</b>: dev.runwayml.com → API Keys → New. Developer-API keys start with <code>key_</code>. A key from the Runway app or the MCP is a different thing and the API refuses it with 401.</li><li><b>Google</b>: aistudio.google.com → Get API key. Starts with <code>AIza</code>. Imagen and Gemini image models bill to that key.</li></ul>';}
async function saveKey(p,remove){const v=remove?'':$('#k-'+p).value;const r=await api('/api/keys',{method:'POST',body:JSON.stringify({provider:p,key:v})});await loadKeys();renderKeys();$('#kr-'+p).innerHTML=r.error?'<span style="color:#ff9a8a">'+esc(r.error)+'</span>':(remove?'removed':'saved · now press test');if(!remove&&!r.error)testKey(p);}
async function discoverModels(p){const b=$('#kr-'+p);b.innerHTML='asking '+p+' which models it accepts…';const r=await api('/api/models/discover',{method:'POST',body:JSON.stringify({provider:p})});if(r.ok){try{MODELS=(await api('/api/models')).models;}catch(e){}}b.innerHTML=`<span style="color:${r.ok?'var(--em-hi)':'#ff9a8a'}">${esc(r.why||'')}</span>`+(r.models?'<pre style="margin-top:4px">'+esc(r.models.join('\n'))+'</pre>':'')+(r.body&&!r.ok?'<pre style="margin-top:4px">'+esc(r.body)+'</pre>':'');}
async function testKey(p){const b=$('#kr-'+p);b.innerHTML='testing…';const r=await api('/api/keys/test',{method:'POST',body:JSON.stringify({provider:p})});b.innerHTML=`<span style="color:${r.ok?'var(--em-hi)':'#ff9a8a'}">${esc(r.why||'')}</span>`+(r.body&&!r.ok?'<pre style="margin-top:4px">'+esc(r.body)+'</pre>':'');if(r.ok&&r.models&&r.models.length){MODELS.google=r.models.map(id=>({id,label:id,note:'listed by your key',verified:true}));}}
let JOBS_HTML='';function renderJobs(){api('/api/jobs').then(d=>{const el=$('#detail');const html='<h2>jobs (this session)</h2><div class="jobs">'+(d.jobs.length?d.jobs.map(j=>`<div class="job"><span class="st ${j.status}">${j.status.toUpperCase()}</span> · ${j.kind} · <b>${esc(j.target)}</b> · ${j.provider}<pre>${esc(j.commands.join('\n'))}\n\n${esc(j.log.join('\n'))}</pre></div>`).join(''):'<p class="empty">nothing run yet · pick a strip → RENDERS → GENERATE</p>')+'</div>';if(html!==JOBS_HTML){JOBS_HTML=html;el.innerHTML=html;}});}
function tab(t){TAB=t;document.querySelectorAll('.pane').forEach(p=>p.classList.toggle('on',p.id==='p-'+t));document.querySelectorAll('.tabs button').forEach((b,i)=>b.classList.toggle('on',['sheet','panels','prompt','refs','renders','json'][i]===t));}
function copy(id){navigator.clipboard.writeText($('#'+id).textContent);}
async function review(id,status){const note=$('#rv-note')?.value||'';await api('/api/review',{method:'POST',body:JSON.stringify({id,status,note})});await loadStrips();open(id);}
async function refStatus(id,status){await api('/api/ref_status',{method:'POST',body:JSON.stringify({id,status})});if(MODE==='sheets'){await loadSheets();open(id);}else if(MODE==='refs'){await loadRefs();open(id);}else open(SEL);}
async function regenMd(){await api('/api/md',{method:'POST',body:'{}'});$('#g-msg')&&($('#g-msg').textContent='md regenerated');}
function setMode(m){MODE=m;SEL=null;document.querySelectorAll('.mode button').forEach(b=>b.classList.toggle('on',b.id==='m-'+m));$('#detail').innerHTML='<p class="empty">pick one</p>';
 if(m==='strips')loadStrips();else if(m==='sheets')loadSheets();else if(m==='refs')loadRefs();else if(m==='keys'){render();renderKeys();}else{render();renderJobs();setTimeout(()=>{if(MODE==='jobs')renderJobs();},3000);}}
['m-strips','m-sheets','m-refs','m-jobs','m-keys'].forEach(id=>$('#'+id).onclick=()=>setMode(id.slice(2)));
['#q','#f-year','#f-strip','#f-format','#f-tier','#f-render','#f-review'].forEach(s=>$(s).addEventListener('input',render));
document.addEventListener('keydown',e=>{if(e.target.tagName==='INPUT'||e.target.tagName==='SELECT')return;const ids=VIEW.map(v=>v.id);const i=ids.indexOf(SEL);
 if(e.key==='j'&&ids.length){open(ids[Math.min(i+1,ids.length-1)]);}if(e.key==='k'&&ids.length){open(ids[Math.max(i-1,0)]);}
 if(e.key==='g'&&MODE==='strips'&&SEL){tab('renders');const b=$('#g-go');if(b&&!b.disabled&&GEN.prov)b.click();}if(/^[1-6]$/.test(e.key)&&MODE==='strips'&&SEL)tab(['sheet','panels','prompt','refs','renders','json'][+e.key-1]);
 if(e.key==='/'){e.preventDefault();$('#q').focus();}});
setInterval(()=>{if(MODE==='jobs')renderJobs();},4000);
const _open=open;open=function(id){history.replaceState(null,'','#'+MODE+'/'+encodeURIComponent(id)+'/'+TAB);return _open(id);};
loadKeys();(async()=>{const h=location.hash.slice(1).split('/');await loadStrips();if(h[0]==='keys'||h[0]==='jobs'){setMode(h[0]);}else if(h[0]&&h[1]){if(h[2])TAB=h[2];if(h[0]!=='strips'){setMode(h[0]);await (h[0]==='sheets'?loadSheets():loadRefs());}open(decodeURIComponent(h[1]));}})();
</script></body></html>
"""


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--open", action="store_true", help="open the page in a browser")
    args = ap.parse_args(argv)
    ct.OUT.mkdir(parents=True, exist_ok=True)
    srv = ThreadingHTTPServer((args.host, args.port), H)
    url = f"http://{args.host}:{args.port}/"
    n = len(list(ct.STRIPS.glob("*.json")))
    print(f"COMIC INSPECTOR · {n} strips · {url}   (Ctrl-C to stop)")
    if args.open:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nbye")
    return 0


if __name__ == "__main__":
    sys.exit(main())
