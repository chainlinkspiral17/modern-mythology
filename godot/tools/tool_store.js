// tool_store.js — the tools' work kept in FILES, not only in a browser
// (2026-10-19; CLAUDE.md, "The user's work is saved to FILES").
//
// The user: "when I ask to save relevant data, I mean this." Each tool below
// kept the user's work (patches, banks, presets, queues, results, a studio's
// state) only in localStorage, which a browser files under the page's address
// and can lose. Include this FIRST in a tool's <head>, naming its keys:
//
//   <script src="tool_store.js" data-keys="mm_meshy_queue"></script>
//
// It runs before the tool's own scripts, so the tool's code stays as it was:
//   * the repo's copy (godot/tools/tool_state/<key>.json) is put into
//     localStorage before the tool reads it, when it is newer than the
//     browser's own (or the browser has none);
//   * every localStorage.setItem on those keys is timestamped and — when the
//     page is served or opened as a file — written to the repo's copy at once
//     (POST /api/tool_state; Hero Studio's SAVE commits it);
//   * opened as a bare file (file://) the repo's copy still loads (through
//     tool_state/<key>.js, a script a file page may load) and saves go to
//     Hero Studio at 127.0.0.1:8877; when it is not running a red notice
//     says so and the store keeps trying.
// The browser's copy that a newer repo copy replaced is kept under
// "<key>__replaced" so nothing is silently lost.
(function () {
  const me = document.currentScript;
  const keys = ((me && me.dataset.keys) || '').split(/[\s,]+/).filter(Boolean);
  const SERVED = location.protocol === 'http:' || location.protocol === 'https:';
  const META = 'mm_toolstore_meta';
  window.MM_TOOL_STATE = window.MM_TOOL_STATE || {};

  function meta() { try { return JSON.parse(localStorage.getItem(META) || '{}'); } catch (e) { return {}; } }
  function setMeta(m) { try { realSet.call(localStorage, META, JSON.stringify(m)); } catch (e) {} }
  const realSet = Storage.prototype.setItem;

  // 1. the repo's copies, synchronously, before the tool's scripts run
  if (SERVED) {
    for (const k of keys) {
      try {
        const x = new XMLHttpRequest();
        x.open('GET', '/api/tool_state?key=' + encodeURIComponent(k), false);   // sync on purpose: the tool reads next
        x.send();
        if (x.status === 200) {
          const j = JSON.parse(x.responseText);
          if (j && j.saved_at) window.MM_TOOL_STATE[k] = j;
        }
      } catch (e) {}
    }
  } else {
    // a file page may load a script; document.write keeps it before the tool's own
    for (const k of keys) document.write('<script src="tool_state/' + k + '.js"><\/script>');
  }
  // file page: apply after the state scripts above have run (served: below, now)
  if (!SERVED) document.write('<script>window.ToolStore && window.ToolStore._apply()<\/script>');

  // (2026-10-19, the user: "There really needs to be a better way of doing
  // this.") A page opened as a FILE saves too: it sends to Hero Studio at
  // 127.0.0.1:8877, which accepts the tools' state from file pages. Hero
  // Studio not running → a red notice, and it keeps trying until it is up.
  const SAVE_URL = SERVED ? '/api/tool_state' : 'http://127.0.0.1:8877/api/tool_state';
  const pending = {};
  let timer = null;
  function push() {
    timer = null;
    const batch = Object.assign({}, pending);
    for (const k in batch) {
      fetch(SAVE_URL, { method: 'POST', headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ key: k, value: batch[k].value, saved_at: batch[k].saved_at }) })
        .then(r => r.json()).then(j => {
          if (j && j.error) { notice('NOT saved to the repo: ' + j.error, true); return; }
          if (pending[k] && pending[k].saved_at === batch[k].saved_at) delete pending[k];
          if (!Object.keys(pending).length) notice('Saved to the repo (godot/tools/tool_state/). Press SAVE in Hero Studio to push.', false, true);
        })
        .catch(() => {
          notice('NOT SAVED to the repo: Hero Studio is not running (start it: bash godot/tools/hero_studio.sh). ' +
                 'Your work is kept in this browser and saved the moment it is up — retrying.', true);
          clearTimeout(timer); timer = setTimeout(push, 8000);
        });
    }
  }

  // 2. timestamp every write of our keys and write the repo's copy too
  Storage.prototype.setItem = function (k, v) {
    realSet.call(this, k, v);
    if (this !== localStorage || !keys.includes(k)) return;
    const m = meta(); m[k] = Date.now(); setMeta(m);
    pending[k] = { value: String(v), saved_at: m[k] };
    clearTimeout(timer); timer = setTimeout(push, 500);
  };

  function notice(text, bad, fade) {
    const show = () => {
      let el = document.getElementById('toolStoreNotice');
      if (!el) {
        el = document.createElement('div');
        el.id = 'toolStoreNotice';
        el.style.cssText = 'position:fixed;right:12px;bottom:12px;z-index:99999;max-width:460px;padding:8px 30px 8px 12px;' +
          'font:12px/1.4 system-ui,sans-serif;border-radius:6px;box-shadow:0 2px 10px rgba(0,0,0,.4)';
        const x = document.createElement('span');
        x.textContent = '×';
        x.style.cssText = 'position:absolute;right:9px;top:5px;cursor:pointer;font-size:15px';
        x.onclick = () => { el.remove(); try { sessionStorage.setItem('toolStoreNoticeShut', '1'); } catch (e) {} };
        el.appendChild(document.createElement('span'));
        el.appendChild(x);
        document.body.appendChild(el);
      }
      el.style.background = bad ? '#5a1d1d' : '#2b2a22';
      el.style.color = bad ? '#ffd9d9' : '#e8e0c8';
      el.firstChild.textContent = text;
      clearTimeout(el._fade);
      if (fade) el._fade = setTimeout(() => el.remove(), 4000);
    };
    if (document.body) show(); else document.addEventListener('DOMContentLoaded', show);
  }

  window.ToolStore = {
    keys, served: SERVED,
    // 3. the newer copy wins; a replaced browser copy is kept beside it
    _apply() {
      const m = meta();
      const unsaved = [];
      for (const k of keys) {
        const repo = window.MM_TOOL_STATE[k];
        const local = localStorage.getItem(k);
        const localAt = m[k] || 0;
        // a browser copy from before tool_store (no timestamp) is the user's own
        // work: it is never replaced, only pushed (served) or flagged (file)
        if (repo && repo.saved_at && (local === null || (localAt > 0 && repo.saved_at > localAt))) {
          if (local !== null && local !== repo.value) realSet.call(localStorage, k + '__replaced', local);
          realSet.call(localStorage, k, repo.value);
          m[k] = repo.saved_at;
        } else if (local !== null && (!repo || localAt === 0 || localAt > (repo.saved_at || 0))) {
          if (localAt === 0) { m[k] = Date.now(); }
          pending[k] = { value: local, saved_at: localAt || Date.now() };
          clearTimeout(timer); timer = setTimeout(push, 500);
          unsaved.push(k);
        }
      }
      setMeta(m);
      let shut = false;
      try { shut = sessionStorage.getItem('toolStoreNoticeShut') === '1'; } catch (e) {}
      if (unsaved.length && !shut) notice('Saving to the repo: ' + unsaved.join(', ') + ' …', false);
    },
  };
  if (SERVED) window.ToolStore._apply();
})();
