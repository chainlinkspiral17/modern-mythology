#!/usr/bin/env python3
"""voice_rescue — get the voice studio's voice IDs back out of the browser
(2026-10-18).

The voice studio used to keep its voice IDs only in the browser's
localStorage, and a browser files localStorage under the page's ADDRESS
(scheme + host + port). Hero Studio moved from port 8765 to 8877 on
2026-10-13, so the studio opened at a new address and looked empty; the
IDs saved at the old address are most likely still in the browser.

This serves one small page on the OLD address. Open it in the SAME browser
you used the studio in; it reads what that address stored (only the studio's two keys,
`mm_voice_map` and `mm_voice_meta`)
and sends it back here. The IDs are merged into godot/tools/voice_map.json
and godot/tools/voice_ids_backup.json (gaps only: an ID already saved is
kept), and the raw copy is kept in godot/tools/browser_rescue/. The same
page also brings back the other tools' work kept at that address (FORGE's
user patches, the DX7 bank, Runway presets and queue, Resolve actions, the
FM-1 checkout, the planned-community studio, the DAW inbox, the Meshy
queue), one file each in godot/tools/browser_rescue/ — never an API key.

    python3 godot/tools/voice_rescue.py              # port 8765, the old one
    python3 godot/tools/voice_rescue.py --port 8877  # any other address

Then open the URL it prints (try both http://127.0.0.1:PORT and
http://localhost:PORT — they are different addresses to the browser).
Port 8765 belongs to another program on the Deck now; close that program
for a minute if this says the port is busy. Stdlib only.
"""
import argparse
import json
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
RESCUE_DIR = TOOLS / "browser_rescue"
# the keys this reads: the voice studio's two, and the other tools' WORK
# (user patches, banks, presets, results, authored state) — never a key,
# a token, a latency or a UI preference
VOICE_KEYS = ["mm_voice_map", "mm_voice_meta"]
WORK_KEYS = ["mm_forge_user_presets", "mm_dx7_bank", "mm_runway_presets_v1", "mm_runway_queue_v1",
             "mm_resolve_actions_v1", "mm_fm1_checkout", "community_planned_w1_state", "mm_daw_inbox",
             "mm_meshy_queue"]
sys.path.insert(0, str(TOOLS))
import voice_ids  # noqa: E402

PAGE = """<!doctype html><meta charset="utf-8"><title>Voice rescue</title>
<style>body{font:15px system-ui;margin:2em;max-width:46em;background:#111;color:#eee}
.good{color:#7d7}.bad{color:#f77}pre{background:#222;padding:1em;overflow:auto}</style>
<h1>Voice rescue</h1><p id="s">Reading this browser's storage for <b id="o"></b> …</p><pre id="d"></pre>
<script>
const WORK_KEYS = __WORK_KEYS__;
document.getElementById('o').textContent = location.origin;
const found = {};
for (let i = 0; i < localStorage.length; i++) {
  const k = localStorage.key(i);
  if (WORK_KEYS.includes(k)) found[k] = localStorage.getItem(k);
}
let ids = {};
try { ids = JSON.parse(found['mm_voice_map'] || '{}'); } catch (e) {}
const n = Object.values(ids).filter(v => v && String(v).trim()).length;
document.getElementById('d').textContent = JSON.stringify(ids, null, 2);
fetch('/rescue', {method: 'POST', headers: {'Content-Type': 'application/json'},
                  body: JSON.stringify({origin: location.origin, storage: found})})
  .then(r => r.json()).then(j => {
    const s = document.getElementById('s');
    if (!n) { s.className = 'bad'; s.textContent = 'No voice IDs stored at ' + location.origin +
      '. Other tools\' work found: ' + ((j.work || []).join(', ') || 'none') +
      '. Try the other address (127.0.0.1 vs localhost) or another port.'; return; }
    s.className = 'good';
    s.textContent = `Found ${n} voice IDs at ${location.origin}: ${j.set + j.added} written to voice_map.json, ` +
      `${j.kept} already saved (kept). Other tools' work found: ${(j.work || []).join(', ') || 'none'} ` +
      `(saved under godot/tools/browser_rescue/).`;
  }).catch(e => { document.getElementById('s').textContent = 'Send failed: ' + e; });
</script>"""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--port", type=int, default=8765, help="the address's port (default 8765, the old one)")
    ap.add_argument("--host", default="127.0.0.1")
    args = ap.parse_args()

    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def _send(self, code, body, ctype):
            data = body.encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            self._send(200, PAGE.replace("__WORK_KEYS__", json.dumps(VOICE_KEYS + WORK_KEYS)), "text/html; charset=utf-8")

        def do_POST(self):
            n = int(self.headers.get("Content-Length") or 0)
            req = json.loads(self.rfile.read(n).decode("utf-8") or "{}")
            storage = req.get("storage") or {}
            raw = RESCUE_DIR / f"voice_rescued_{args.port}.json"
            RESCUE_DIR.mkdir(exist_ok=True)
            work = []
            for k in WORK_KEYS:
                v = storage.get(k)
                if v:
                    dst = RESCUE_DIR / f"{k}__{args.port}.json"
                    try:
                        body = json.dumps(json.loads(v), indent=2, ensure_ascii=False)
                    except ValueError:
                        body = json.dumps(v)
                    if not dst.exists() or dst.read_text(encoding="utf-8").strip() != body.strip():
                        dst.write_text(body + "\n", encoding="utf-8")
                    work.append(k)
            prev = {}
            if raw.exists():
                try:
                    prev = json.loads(raw.read_text(encoding="utf-8"))
                except ValueError:
                    prev = {}
            prev[req.get("origin") or "?"] = {"read": time.strftime("%Y-%m-%d %H:%M:%S"), "storage": storage}
            raw.write_text(json.dumps(prev, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            try:
                ids = json.loads(storage.get("mm_voice_map") or "{}")
            except ValueError:
                ids = {}
            res = voice_ids.save_ids(ids, f"voice_rescue {req.get('origin')}", overwrite=False)
            res["raw"] = str(raw.relative_to(TOOLS.parent.parent))
            res["work"] = work
            got = sum(1 for v in ids.values() if v)
            print(f"  {req.get('origin')}: {got} voice IDs found · written {res['set'] + res['added']} · "
                  f"kept {res['kept']} · other tools' work: {', '.join(work) or 'none'} · "
                  f"saved under godot/tools/browser_rescue/", flush=True)
            self._send(200, json.dumps(res), "application/json")

    try:
        srv = ThreadingHTTPServer((args.host, args.port), H)
    except OSError:
        sys.exit(f"Port {args.port} is busy: another program holds it. Close that program for a minute and run "
                 f"this again (the browser only shows what it saved at exactly this port).")
    print(f"Voice rescue on port {args.port}. In the browser you used the voice studio in, open:\n"
          f"  http://127.0.0.1:{args.port}/\n  http://localhost:{args.port}/\n"
          f"Ctrl-C when done.", flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
