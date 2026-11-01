/*
 * surface.js — hardware control surfaces (first: the Arturia MiniLab 3) for every tool page.
 *
 * A control surface is a controller you PLAY THE TOOLS with — keys, pads, knobs, faders, an encoder — as opposed
 * to the FM-1, which is a synth (midi_input.js). Both can be plugged in at once: Surface opens its own port (by
 * name) and midi_input.js leaves a surface's port alone (Surface.claims), so the FM-1 keeps its slot.
 *
 * The MiniLab 3's factory MIDI map isn't published as a table and its controls are re-assignable (Arturia MIDI
 * Control Center), so the profile below is a starting point and every control can be LEARNED on
 * surface_checkout.html: the learned map (localStorage 'mm_surface_<id>') wins over the default, on every page.
 *
 *   Surface.start()                       → Promise<bool>  (Web MIDI; Chrome / Edge)
 *   Surface.on(fn) / Surface.off(fn)      fn(ev) for every control event (also window 'surface' CustomEvents)
 *   Surface.connected · Surface.portName · Surface.profile (the device) · Surface.map (control → binding)
 *   Surface.learn(controlId) → Promise<binding>   the next unassigned message from the surface becomes it
 *   Surface.setBinding(id, binding|null) · Surface.resetMap() · Surface.claims(portName) → bool
 *   Surface.send(bytes)                   to the surface's output (if it has one)
 *
 * Events (ev.kind):
 *   key     {note, vel 0..1, on}                 the keybed (pitch-bend / mod strips: 'bend' / 'mod')
 *   pad     {i 0..15 (8–15 = bank B), vel, on}   pressure: 'padpress' {i, value}
 *   knob    {i 0..7, value 0..1, delta (−1..1 step), raw}
 *   fader   {i 0..3, value 0..1, raw}
 *   encoder {delta (±n clicks)} · click {on}     the big encoder (scroll) and its push
 *   button  {id, on}                             any extra learned button (shift, hold, oct−/+ …)
 *   mod {value 0..1} · bend {value −1..1} · pressure {value 0..1} (channel aftertouch) · sustain {on}
 *   raw     {data}                               everything (monitors)
 * Every event carries {surface: 'minilab3', control: '<id>', t (performance.now())}.
 */
(function (root) {
  'use strict';
  const LS = 'mm_surface_';

  // ── profiles ──────────────────────────────────────────────────────
  // binding: { t: 'cc' | 'note', n: number, ch: 1..16 | null (any) } · rel: relative encoder
  const cc = (n, ch = null, extra) => Object.assign({ t: 'cc', n, ch }, extra || {});
  const note = (n, ch = null) => ({ t: 'note', n, ch });
  const PROFILES = {
    minilab3: {
      id: 'minilab3', name: 'Arturia MiniLab 3', match: /mini ?lab ?(3|iii|mk ?3)|minilab3/i,
      // the defaults (factory "Arturia" mode as far as published / reported — learn your own on surface_checkout.html)
      keys: { ch: 1 }, padCh: 10,
      controls: Object.assign({},
        ...[74, 71, 76, 77, 93, 18, 19, 16].map((n, i) => ({ ['knob' + (i + 1)]: cc(n) })),
        ...[82, 83, 85, 17].map((n, i) => ({ ['fader' + (i + 1)]: cc(n) })),
        ...Array.from({ length: 16 }, (_, i) => ({ ['pad' + (i + 1)]: note(36 + i, 10) })),
        { encoder: cc(28, null, { rel: true }), click: cc(118) }),
      layout: { keys: 25, pads: 8, banks: 2, knobs: 8, faders: 4 },
      labels: { encoder: 'MAIN ENCODER (turn)', click: 'MAIN ENCODER (push)' },
    },
  };
  const CONTROL_ORDER = p => [...Array.from({ length: p.layout.knobs }, (_, i) => 'knob' + (i + 1)), ...Array.from({ length: p.layout.faders }, (_, i) => 'fader' + (i + 1)),
    ...Array.from({ length: p.layout.pads * p.layout.banks }, (_, i) => 'pad' + (i + 1)), 'encoder', 'click'];
  const labelOf = (p, id) => (p.labels && p.labels[id]) || id.replace(/^([a-z]+)(\d+)$/, (_, a, n) => a.toUpperCase() + ' ' + n).replace(/^PAD (\d+)$/, (m, n) => +n > p.layout.pads ? 'PAD ' + (n - p.layout.pads) + ' (bank B)' : 'PAD ' + n + ' (bank A)');

  // relative encoders: two's complement (1..63 up, 65..127 down) or offset-64 (65.. up, ..63 down) — told apart by
  // where the values cluster
  function relDelta(v) {
    if (v === 0 || v === 64) return 0;
    if (v >= 1 && v <= 24) return v;               // two's complement +
    if (v >= 104) return v - 128;                  // two's complement −
    return v - 64;                                 // offset-64
  }

  const S = {
    supported: typeof navigator !== 'undefined' && !!navigator.requestMIDIAccess,
    access: null, input: null, output: null, connected: false, portName: '', profile: PROFILES.minilab3, map: null,
    listeners: new Set(), learning: null, last: {}, _started: null,
    PROFILES, CONTROL_ORDER, labelOf,
    claims(name) { return Object.values(PROFILES).some(p => p.match.test(name || '')); },
    loadMap() {
      let saved = null; try { saved = JSON.parse(localStorage.getItem(LS + this.profile.id) || 'null'); } catch (e) {}
      this.map = Object.assign({}, this.profile.controls, (saved && saved.controls) || {});
      this.keysCh = saved && saved.keysCh !== undefined ? saved.keysCh : this.profile.keys.ch;
      this.learned = (saved && saved.learned) || {};
      return this.map;
    },
    saveMap() {
      const own = {}; for (const [k, b] of Object.entries(this.map)) if (JSON.stringify(b) !== JSON.stringify(this.profile.controls[k])) own[k] = b;
      try { localStorage.setItem(LS + this.profile.id, JSON.stringify({ controls: own, keysCh: this.keysCh, learned: this.learned, saved: new Date().toISOString() })); } catch (e) {}
      this._emit({ kind: 'map' });
    },
    setBinding(id, b) { if (!this.map) this.loadMap(); if (b) { this.map[id] = b; this.learned[id] = true; } else { this.map[id] = this.profile.controls[id]; delete this.learned[id]; } this.saveMap(); },
    resetMap() { try { localStorage.removeItem(LS + this.profile.id); } catch (e) {} this.loadMap(); this._emit({ kind: 'map' }); },
    on(fn) { this.listeners.add(fn); return () => this.listeners.delete(fn); },
    off(fn) { this.listeners.delete(fn); },
    _emit(ev) {
      ev.surface = this.profile.id; ev.t = performance.now();
      for (const f of [...this.listeners]) { try { f(ev); } catch (e) { console.warn('surface listener:', e); } }
      if (typeof window !== 'undefined' && window.dispatchEvent) window.dispatchEvent(new CustomEvent('surface', { detail: ev }));
    },
    start() {
      if (this._started) return this._started;
      if (!this.map) this.loadMap();
      if (!this.supported) return (this._started = Promise.resolve(false));
      this._started = navigator.requestMIDIAccess({ sysex: false }).then(acc => {
        this.access = acc; acc.addEventListener('statechange', () => this._pick()); this._pick(); return true;
      }).catch(e => { console.warn('surface MIDI:', e && e.message); return false; });
      return this._started;
    },
    _pick() {
      if (!this.access) return;
      const ins = [...this.access.inputs.values()], outs = [...this.access.outputs.values()];
      let prof = null, inp = null;
      for (const p of Object.values(PROFILES)) { inp = ins.find(x => p.match.test(x.name || '') && !/\bdin\b|\bthru\b/i.test(x.name || '')) || ins.find(x => p.match.test(x.name || '')); if (inp) { prof = p; break; } }
      if (inp !== this.input) {
        if (this.input) this.input.onmidimessage = null;
        this.input = inp || null;
        if (this.input) this.input.onmidimessage = e => this._msg(e.data);
      }
      if (prof && prof !== this.profile) { this.profile = prof; this.loadMap(); }
      this.output = prof ? outs.find(x => prof.match.test(x.name || '')) || null : null;
      const was = this.connected;
      this.connected = !!this.input; this.portName = this.input ? this.input.name : '';
      if (was !== this.connected) this._emit({ kind: this.connected ? 'connected' : 'disconnected', port: this.portName });
    },
    send(bytes) { if (this.output) try { this.output.send(bytes); } catch (e) {} },
    // ⟶ the next message becomes `id` (notes, CCs; off-messages and CC 0 → ignored). Rejects on cancel.
    learn(id) {
      if (this.learning) this.learning.reject(new Error('cancelled'));
      return new Promise((resolve, reject) => { this.learning = { id, resolve, reject }; this._emit({ kind: 'learning', control: id }); });
    },
    cancelLearn() { if (this.learning) { this.learning.reject(new Error('cancelled')); this.learning = null; } },
    // the binding a message hits: exact (with channel) first, then any-channel
    _find(t, n, ch) {
      let any = null;
      for (const [id, b] of Object.entries(this.map)) {
        if (!b || b.t !== t || b.n !== n) continue;
        if (b.ch === ch) return id;
        if (b.ch === null || b.ch === undefined) any = any || id;
      }
      return any;
    },
    _msg(data) {
      if (!data || !data.length) return;
      const st = data[0] & 0xf0, ch = (data[0] & 0x0f) + 1, a = data[1], b = data[2];
      this._emit({ kind: 'raw', data: Array.from(data) });
      if (data[0] >= 0xf0) return;
      // learning: the first note-on / moving CC is the control
      if (this.learning && ((st === 0x90 && b > 0) || st === 0xb0)) {
        const L = this.learning, bind = st === 0x90 ? note(a, ch) : cc(a, ch, L.id === 'encoder' ? { rel: true } : undefined);
        // one control per message: another control that had this message loses it
        for (const [k, x] of Object.entries(this.map)) if (k !== L.id && x && x.t === bind.t && x.n === bind.n && (x.ch == null || x.ch === ch)) this.map[k] = null;
        this.map[L.id] = bind; this.learned[L.id] = true; this.saveMap(); this.learning = null;
        this._emit({ kind: 'learned', control: L.id, binding: bind }); L.resolve(bind);
        return;
      }
      if (st === 0x90 || st === 0x80) {
        const on = st === 0x90 && b > 0, id = this._find('note', a, ch);
        if (id && /^pad/.test(id)) { this._emit({ kind: 'pad', control: id, i: +id.slice(3) - 1, vel: b / 127, on, note: a }); return; }
        if (id) { this._emit({ kind: 'button', control: id, id, on }); return; }
        if (ch === this.profile.padCh && !this.learned.keys) { this._emit({ kind: 'pad', control: 'pad?', i: -1, note: a, vel: b / 127, on }); return; }
        this._emit({ kind: 'key', control: 'keys', note: a, vel: b / 127, on, ch });
        return;
      }
      if (st === 0xb0) {
        const id = this._find('cc', a, ch);
        if (id) {
          const B = this.map[id];
          if (/^knob/.test(id)) {
            const i = +id.slice(4) - 1, prev = this.last[id];
            if (B.rel) { const v = Math.max(0, Math.min(1, (prev ?? 0.5) + relDelta(b) / 127)); this.last[id] = v; this._emit({ kind: 'knob', control: id, i, value: v, delta: relDelta(b) / 127, raw: b }); }
            else { const v = b / 127; this.last[id] = v; this._emit({ kind: 'knob', control: id, i, value: v, delta: prev == null ? 0 : v - prev, raw: b }); }
          } else if (/^fader/.test(id)) this._emit({ kind: 'fader', control: id, i: +id.slice(5) - 1, value: b / 127, raw: b });
          else if (id === 'encoder') { const d = B.rel === false ? (b - (this.last.encoder ?? b)) : relDelta(b); this.last.encoder = b; if (d) this._emit({ kind: 'encoder', control: id, delta: d }); }
          else if (id === 'click') this._emit({ kind: 'click', control: id, on: b >= 64 });
          else if (/^pad/.test(id)) this._emit({ kind: 'pad', control: id, i: +id.slice(3) - 1, vel: b / 127, on: b > 0 });
          else this._emit({ kind: 'button', control: id, id, on: b >= 64, value: b / 127 });
          return;
        }
        if (a === 1) { this._emit({ kind: 'mod', control: 'mod', value: b / 127 }); return; }
        if (a === 64) { this._emit({ kind: 'sustain', control: 'sustain', on: b >= 64 }); return; }
        this._emit({ kind: 'cc', control: 'cc' + a, cc: a, value: b / 127, ch });
        return;
      }
      if (st === 0xe0) { this._emit({ kind: 'bend', control: 'bend', value: Math.max(-1, Math.min(1, (((b << 7) | a) - 8192) / 8191)) }); return; }
      if (st === 0xd0) { this._emit({ kind: 'pressure', control: 'pressure', value: a / 127 }); return; }
      if (st === 0xa0) { const id = this._find('note', a, ch); if (id && /^pad/.test(id)) this._emit({ kind: 'padpress', control: id, i: +id.slice(3) - 1, value: b / 127 }); return; }
    },
  };
  S.loadMap();
  root.Surface = S;
  if (typeof module !== 'undefined' && module.exports) module.exports = S;
})(typeof window !== 'undefined' ? window : globalThis);
