/* fm1_emu.js — the M-VAVE FM-1 custom firmwares that ship browser emulators, as instruments.
 *
 * Felucca (Leo Kuroshita / Hügelton Instruments) and X0X (Charles Vestal) each publish their whole
 * firmware compiled to WebAssembly plus an AudioWorklet that runs it against a simulated FM-1. This
 * file hosts those builds inside the Modern Mythology tools: a note / CC / raw-MIDI instrument API for
 * the DAW, flash persistence (the projects and presets you save on the emulated device), and the
 * FM-1 face (live screen, LEDs, buttons, knobs, 27 keys) mapped exactly as the authors' own pages.
 *
 * Works from file:// offline: load the vendored builds as classic scripts first —
 *   <script src="vendor/fm1emu/felucca/felucca_wasm.js"></script>
 *   <script src="vendor/fm1emu/felucca/felucca_worklet.js"></script>
 *   <script src="fm1_emu.js"></script>
 * (vendor/fm1emu/pack.py makes those wrappers; the builds are GPL-3.0-only, see vendor/fm1emu/<id>/SOURCE.md.)
 * The worklet is added from a data: URL — on file:// a Blob URL is blob:null/… and Chrome refuses it as a
 * worklet module; data: works offline. If AudioContext.sampleRate differs from emu.rate it warns, not throws.
 *
 *   const emu = new FM1Emu(ctx, { id: 'felucca', output: ctx.destination });
 *   await emu.init();                       // ctx should run at emu.rate (44100) or pitch is off
 *   emu.noteOn(60, 0.8, ctx.currentTime + 0.1, 1);
 *   emu.mountPanel(document.getElementById('face'), { scale: 0.8, keyboard: true });
 *
 * Timing: messages with a future `when` are queued inside the worklet (a small adapter prepended to the
 * upstream worklet source, which itself stays verbatim) and applied at the render quantum that contains
 * `when` — sample-clock accurate, immune to main-thread jank. The device then reads MIDI once per
 * audio block (X0X: 256 samples, as the FM-1's I2S half buffer), exactly like the hardware.
 *
 * MIDI per firmware (confirmed in source, see vendor/fm1emu/<id>/SOURCE.md):
 *   Felucca  ch1-4 = tracks 1-4 (MENU > MIDI > MIDI IN "CH1-4", the default); 5-16 ignored. CCs: the
 *            standard map (7 level, 10 pan, 71/74 engine, 72/73/75 env, 91/93/94 sends, 64 pedal, 123).
 *            Realtime (clock / start / stop) is followed when MENU > MIDI > CLOCK is USB. The upstream
 *            web build drops realtime bytes; the adapter slips them into the firmware's own USB-MIDI ring.
 *   X0X      909 ch10, 808 ch11 (GM drum notes), 303 A ch2, 303 B ch3 (overlapping notes slide),
 *            break ch4 (notes 36-43 = slices); the sequencer follows clock / start / stop at once.
 *            Upstream's web build has no MIDI input at all; the vendored x0x_midi.wasm is that build
 *            plus a web_midi export (vendor/fm1emu/x0x/x0x_web_midi.patch) and is otherwise identical.
 */
"use strict";

(function () {
  const W = window;
  const REG = (W.FM1EMU = W.FM1EMU || {});

  // ── what both firmwares share (Felucca panel.c / X0X web/emu/index.html) ──────────────────────
  const BTN = { FX: 0, SCL: 1, SEL: 1, ENV: 2, LFO: 3, EDIT: 4, GLO: 5, HOME: 6, SAVE: 7, ARP: 8, SEQ: 9, PLAY: 10, REC: 11, 'OCT-': 12, 'OCT+': 13 };
  const ENC = { SELECT: 0, ALGORITHM: 1, PRESETS: 2, 'KNOB 1': 3, 'KNOB 2': 4, 'KNOB 3': 5, 'KNOB 4': 6 };
  const PLAY_GREEN = 14;                                            // Felucca: PLAY lit green
  const WHITE = [0, 2, 4, 6, 7, 9, 11, 12, 14, 16, 18, 19, 21, 23, 24, 26];   // the 27 keys F3..G5
  const BLACK = [1, 3, 5, 8, 10, 13, 15, 17, 20, 22, 25];
  const BLACK_AFTER = [0, 1, 2, 4, 5, 7, 8, 9, 11, 12, 14];
  const ROW2 = ['HOME', 'SAVE', 'ARP', 'SEQ', 'PLAY', 'REC'];
  const KNOBS = ['MASTER', 'SELECT', 'PRESETS', 'ALGORITHM', 'KNOB 1', 'KNOB 2', 'KNOB 3', 'KNOB 4'];

  const PROFILES = {
    felucca: {
      id: 'felucca', name: 'Felucca', version: '1.5.1', author: 'Leo Kuroshita (Hügelton Instruments)',
      license: 'GPL-3.0-only', rate: 44100, processor: 'felucca',
      source: 'https://github.com/hugelton/Felucca', sourceCommit: 'a4d7ca2e5d52a4c35e2468401f00d883cadbda03',
      pagesCommit: '92d0634be3def39b7ae2a099a326d2cf8270453f',
      hosted: { page: 'https://hugelton.github.io/Felucca/webapp/try/', wasm: 'https://hugelton.github.io/Felucca/webapp/try/felucca.wasm',
                worklet: 'https://hugelton.github.io/Felucca/webapp/try/worklet.js' },
      master: { max: 1023, def: 700, step: 16 }, flashKey: 'sectors', rt: 'piggyback',
      // the firmware's USB-MIDI ring (usb.c midi_in_q / mi_w, MQ 64) in this build; re-found by a memory scan if stale
      rtHint: { '4e13d98f8af0e53656515011e6bf6f0b5b0ea3e462e9e4a05d83616e8a840223': { q: 1525232, w: 1525488, mq: 64 } },
      row1: ['FX', 'SCL', 'ENV', 'LFO', 'EDIT', 'GLO'], look: 'felucca',
      channels: { 1: 'track 1', 2: 'track 2', 3: 'track 3', 4: 'track 4 (DRUM: GM 35-81 by default)' },
      notes: 'Four tracks, each its own engine (ANALOG, FM6, PHASE, LOFI, SAMPLE, VOICE, TRIO, WHEEL, GRAIN, PHYS, NOISE, SLICE, DRUM). MIDI ch1-4 = tracks 1-4; standard CC map; follows MIDI clock when MENU > MIDI > CLOCK = USB.',
    },
    x0x: {
      id: 'x0x', name: 'X0X', version: '1.0.5', author: 'Charles Vestal',
      license: 'GPL-3.0-only', rate: 44100, processor: 'x0x',
      source: 'https://github.com/charlesvestal/fm1-x0x', sourceCommit: '6cffa408b5b95de2e41ff8b06be6c48084a95d2d',
      pagesCommit: '225e01d0ec330abbde0409e51d14062d523d6598',
      hosted: { page: 'https://charlesvestal.github.io/fm1-x0x/emu/', wasm: 'https://charlesvestal.github.io/fm1-x0x/emu/x0x.wasm',
                worklet: 'https://charlesvestal.github.io/fm1-x0x/emu/worklet.js' },
      master: { max: 4096, def: 2800, step: 64 }, flashKey: 'store', rt: 'direct', rtHint: {},
      row1: ['FX', 'SEL', 'ENV', 'LFO', 'EDIT', 'GLO'], look: 'x0x',
      channels: { 2: '303 A', 3: '303 B', 4: 'break (notes 36-43 = slices)', 10: '909 (GM drum notes)', 11: '808 (GM drum notes)' },
      notes: 'ReBirth-style groovebox: 909 (ch10), 808 (ch11), two 303s (ch2, ch3; overlapping notes slide), a break slicer (ch4). Follows MIDI clock / start / stop. Notes only (no CCs).',
    },
  };

  // ── the adapter, prepended to the upstream worklet source (which runs verbatim after it) ─────────
  // It wraps the processor class as it registers: scheduled messages ({type:'fm1', op:'at', t, m}),
  // MIDI through web_midi incl. realtime, capability report, stats, dispose.
  const ADAPTER = String.raw`/* fm1_emu.js adapter: prepended to the unmodified upstream worklet below */
const __fm1Orig = globalThis.__fm1RegOrig || (globalThis.__fm1RegOrig = globalThis.registerProcessor);
globalThis.registerProcessor = function (name, C) { __fm1Patch(C); return __fm1Orig.call(globalThis, name, C); };
const __fm1P1 = (0x0A | 0xAF << 8 | 0x55 << 16 | 0x2A << 24) >>> 0, __fm1P2 = (0x0A | 0xAE << 8 | 0x33 << 16 | 0x11 << 24) >>> 0;
function __fm1Check(ex, a) {                 // a hint {q, w, mq}: two probe messages land where it says (then undone)
  const u = new Uint32Array(ex.memory.buffer), wi = a.w >> 2, qi = a.q >> 2;
  if (!(wi > 0 && wi < u.length && qi > 0 && qi + a.mq < u.length)) return false;
  const w0 = u[wi], s1 = qi + w0 % a.mq, s2 = qi + (w0 + 1) % a.mq, k1 = u[s1], k2 = u[s2];
  let ok = !!ex.web_midi(0xAF, 0x55, 0x2A) && u[wi] === ((w0 + 1) >>> 0) && u[s1] === __fm1P1;
  ok = ok && !!ex.web_midi(0xAE, 0x33, 0x11) && u[wi] === ((w0 + 2) >>> 0) && u[s2] === __fm1P2;
  u[wi] = w0; u[s1] = k1; u[s2] = k2;
  return ok;
}
function __fm1Scan(ex, mq) {                 // find the ring by diffing memory around two probes; everything restored
  const s0 = new Uint32Array(ex.memory.buffer).slice();
  let res = null;
  try {
    if (!ex.web_midi(0xAF, 0x55, 0x2A)) return null;
    let u = new Uint32Array(ex.memory.buffer);
    const ch = [];
    for (let i = 0; i < s0.length; i++) if (u[i] !== s0[i]) ch.push(i);
    if (!ex.web_midi(0xAE, 0x33, 0x11)) return null;
    u = new Uint32Array(ex.memory.buffer);
    for (const qi of ch.filter((i) => u[i] === __fm1P1)) {
      for (const wi of ch.filter((i) => ((s0[i] + 2) >>> 0) === u[i])) {
        const base = qi - (s0[wi] % mq);
        if (base > 0 && u[base + ((s0[wi] + 1) % mq)] === __fm1P2) { res = { q: base * 4, w: wi * 4, mq }; break; }
      }
      if (res) break;
    }
  } finally {
    const v = new Uint32Array(ex.memory.buffer);
    for (let i = 0; i < s0.length; i++) if (v[i] !== s0[i]) v[i] = s0[i];
  }
  return res;
}
function __fm1Ready(self, m) {
  const ex = self.ex;
  if (!ex) { self.port.postMessage({ type: 'fm1', op: 'error', message: 'the emulator did not start' }); return; }
  const cfg = m.fm1 || {}, info = { type: 'fm1', op: 'info', midi: typeof ex.web_midi === 'function', realtime: false,
    rate: typeof ex.web_sample_rate === 'function' ? ex.web_sample_rate() : 0 };
  self.__fm1rtMode = '';
  if (info.midi && cfg.rt === 'direct') { self.__fm1rtMode = 'direct'; info.realtime = true; }
  else if (info.midi && cfg.rt === 'piggyback') {
    let a = cfg.hint && __fm1Check(ex, cfg.hint) ? cfg.hint : null;
    if (!a) { a = __fm1Scan(ex, cfg.mq || 64); info.scanned = !!a; }
    if (a) { self.__fm1rt = a; self.__fm1rtMode = 'piggyback'; info.realtime = true; info.ring = a; }
  }
  self.port.postMessage(info);
}
function __fm1Midi(self, d) {
  const ex = self.ex;
  if (!ex || typeof ex.web_midi !== 'function' || !d) return;
  const s = d[0] & 255;
  if (s >= 0xF8) {
    if (self.__fm1rtMode === 'direct') ex.web_midi(s, 0, 0);
    else if (self.__fm1rtMode === 'piggyback' && (s === 0xF8 || s === 0xFA || s === 0xFB || s === 0xFC)) {
      // usb.c's path for realtime: a packet with CIN 0xF in the same ring. web_midi queues a carrier
      // (poly aftertouch, ch16) with the ring's own bookkeeping; its slot then takes the realtime packet
      // before the firmware can read it (this thread runs both).
      const a = self.__fm1rt, u = new Uint32Array(ex.memory.buffer), w = u[a.w >> 2];
      if (ex.web_midi(0xAF, 0, 0)) u[(a.q >> 2) + (w % a.mq)] = (0x0F | s << 8) >>> 0;
    }
    return;
  }
  if (s >= 0x80 && s < 0xF0) ex.web_midi(s, (d[1] | 0) & 127, (d[2] | 0) & 127);
}
function __fm1Patch(C) {
  if (!C || !C.prototype || C.prototype.__fm1) return;
  const P = C.prototype, onMessage = P.onMessage, process = P.process;
  P.__fm1 = true;
  P.onMessage = function (m) {
    if (m && m.type === 'fm1') {
      const q = this.__fm1q || (this.__fm1q = []);
      if (m.op === 'at') {
        let i = q.length;
        while (i > 0 && q[i - 1].t > m.t) i--;
        q.splice(i, 0, { t: m.t, m: m.m });
      } else if (m.op === 'clear') q.length = 0;
      else if (m.op === 'stats') {
        const s = this.__fm1st || { n: 0, sum: 0, abs: 0, max: 0, min: 0, late: 0 };
        this.port.postMessage({ type: 'fm1', op: 'stats', id: m.id, n: s.n, meanMs: s.n ? 1000 * s.sum / s.n : 0, meanAbsMs: s.n ? 1000 * s.abs / s.n : 0,
          maxMs: 1000 * s.max, minMs: 1000 * s.min, late: s.late, queued: q.length, quantumMs: 1000 * 128 / sampleRate });
        if (m.reset) this.__fm1st = null;
      } else if (m.op === 'dispose') { this.__fm1dead = true; this.ex = null; q.length = 0; }
      return;
    }
    if (m && m.type === 'midi') return __fm1Midi(this, m.data);
    if (m && m.type === 'load') {
      const r = onMessage.call(this, m);
      Promise.resolve(r).then(() => __fm1Ready(this, m), (e) => this.port.postMessage({ type: 'fm1', op: 'error', message: String(e && e.message || e) }));
      return r;
    }
    return onMessage.call(this, m);
  };
  P.process = function (inputs, outputs) {
    if (this.__fm1dead) return false;
    const q = this.__fm1q;
    if (q && q.length && this.ex) {
      const lim = currentTime + 64 / sampleRate;           // events up to the middle of this quantum: error within +-64 samples
      while (q.length && q[0].t < lim) {
        const e = q.shift(), err = currentTime - e.t;
        const s = this.__fm1st || (this.__fm1st = { n: 0, sum: 0, abs: 0, max: -1e9, min: 1e9, late: 0 });
        s.n++; s.sum += err; s.abs += Math.abs(err);
        if (err > s.max) s.max = err;
        if (err < s.min) s.min = err;
        if (err > 64 / sampleRate) s.late++;
        P.onMessage.call(this, e.m);
      }
    }
    return process.call(this, inputs, outputs);
  };
}
`;

  // ── small helpers ─────────────────────────────────────────────────────────────────────────────
  const b64e = (u8) => { let s = ''; for (let i = 0; i < u8.length; i += 0x8000) s += String.fromCharCode.apply(null, u8.subarray(i, i + 0x8000)); return btoa(s); };
  const b64d = (s) => { const b = atob(s), u = new Uint8Array(b.length); for (let i = 0; i < b.length; i++) u[i] = b.charCodeAt(i); return u; };
  const clampCh = (c) => Math.max(1, Math.min(16, (c | 0) || 1)) - 1;
  const lsGet = (k) => { try { return localStorage.getItem(k); } catch (e) { return null; } };
  const lsSet = (k, v) => { try { localStorage.setItem(k, v); } catch (e) { /* storage blocked */ } };

  // flash storage: AK.lib's IndexedDB kv when audio_kit.js is loaded (AK is a global const, not window.AK),
  // else a tiny IndexedDB of our own, else memory
  const FALLBACK_KV = {
    _db: null, _mem: new Map(),
    _open() {
      if (this._db) return this._db;
      this._db = new Promise((res, rej) => {
        let r;
        try { r = indexedDB.open('fm1emu', 1); } catch (e) { rej(e); return; }
        r.onupgradeneeded = () => r.result.createObjectStore('kv', { keyPath: 'k' });
        r.onsuccess = () => res(r.result);
        r.onerror = () => rej(r.error);
      });
      return this._db;
    },
    async kvGet(k) {
      try {
        const db = await this._open();
        return await new Promise((res, rej) => { const q = db.transaction('kv').objectStore('kv').get(k); q.onsuccess = () => res(q.result ? q.result.v : undefined); q.onerror = () => rej(q.error); });
      } catch (e) { return this._mem.get(k); }
    },
    async kvSet(k, v) {
      try {
        const db = await this._open();
        await new Promise((res, rej) => { const tx = db.transaction('kv', 'readwrite'); tx.objectStore('kv').put({ k, v }); tx.oncomplete = res; tx.onerror = () => rej(tx.error); });
      } catch (e) { this._mem.set(k, v); }
    },
  };
  function kvStore() {
    const ak = (typeof AK !== 'undefined' && AK) || W.AK;            // eslint-disable-line no-undef
    return ak && ak.lib && typeof ak.lib.kvGet === 'function' ? ak.lib : FALLBACK_KV;
  }

  const BYTES = {};                                                 // decoded wasm per id (shared by instances)
  function vendored(id) {
    const v = REG[id];
    if (!v || !v.wasmB64 || !v.workletSrc) {
      throw new Error(`FM1Emu: the ${id} build is not loaded — include vendor/fm1emu/${id}/${id}_wasm.js and ${id}_worklet.js before fm1_emu.js`);
    }
    if (!BYTES[id]) BYTES[id] = b64d(v.wasmB64);
    return { bytes: BYTES[id], src: v.workletSrc, sha: v.wasmSha256 || '' };
  }
  async function hostedBuild(p) {
    const [w, s] = await Promise.all([fetch(p.hosted.wasm, { cache: 'no-cache' }), fetch(p.hosted.worklet, { cache: 'no-cache' })]);
    if (!w.ok || !s.ok) throw new Error(`FM1Emu: ${p.hosted.page} answered ${w.status} / ${s.status}`);
    return { bytes: new Uint8Array(await w.arrayBuffer()), src: await s.text(), sha: 'hosted' };
  }
  // A data: URL, not a Blob: on a file:// page the Blob URL is blob:null/… and Chrome refuses it as a
  // worklet module ("Unable to load a worklet's module"); data: modules load. Blob stays as the fallback.
  function addModule(ctx, p, build) {
    const mods = ctx.__fm1emuMods || (ctx.__fm1emuMods = {});
    if (!mods[p.processor]) {
      const src = ADAPTER + '\n' + build.src;
      const dataUrl = 'data:text/javascript;base64,' + b64e(new TextEncoder().encode(src));
      mods[p.processor] = ctx.audioWorklet.addModule(dataUrl).catch(() => {
        const url = URL.createObjectURL(new Blob([src], { type: 'text/javascript' }));
        return ctx.audioWorklet.addModule(url).finally(() => URL.revokeObjectURL(url));
      });
    }
    return mods[p.processor];
  }

  // ── the instrument ────────────────────────────────────────────────────────────────────────────
  class FM1Emu extends EventTarget {
    constructor(ctx, opts = {}) {
      super();
      const p = PROFILES[opts.id || 'felucca'];
      if (!p) throw new Error('FM1Emu: unknown firmware ' + opts.id + ' (have ' + Object.keys(PROFILES).join(', ') + ')');
      this.ctx = ctx;
      this.id = p.id;
      this.profile = p;
      this.opts = opts;
      this.output = ctx.createGain();
      if (opts.output) this.output.connect(opts.output);
      else if (opts.output === undefined) this.output.connect(ctx.destination);
      this.node = null;
      this.ready = false;
      this.caps = { midi: false, realtime: false };
      this.cpu = null;                                 // % of real time the device takes (the worklet's 'load')
      this.flashKey = opts.flashKey || 'fm1emu_flash_' + p.id;
      this._flash = null;                              // { key: Uint8Array } — Felucca: NOR sector offsets, X0X: store objects
      this._master = p.master.def;
      this._rate = 0;
      this._btnBy = new Map(); this._keyBy = new Map(); this._latched = 0; this._btnMask = 0; this._keyMask = 0;
      this._leds = { litB: 0, litK: 0, dimB: 0, dimK: 0, dimLo: 0, brB: 0, brK: 0, midK: 0, anim: null };
      this._ledKey = '';
      this._fb = null;
      this._panels = new Set();
      this._active = new Map();                        // ch*128+note -> true (for allOff)
      this._chUsed = new Set();
      this._saveT = 0; this._savePending = null;
      this._statsWait = new Map(); this._statsN = 0;
      this._onVis = () => this._sendVisible();
      document.addEventListener('visibilitychange', this._onVis);
    }

    get rate() { return this._rate || this.profile.rate; }
    get master() { return this._master; }

    async init() {
      if (this._initP) return this._initP;
      this._initP = (async () => {
        const p = this.profile;
        const build = this.opts.source === 'hosted' ? await hostedBuild(p) : vendored(p.id);
        this._build = build;
        await addModule(this.ctx, p, build);
        if (this._flash === null) this._flash = await this._loadFlash();
        await this._boot();
        if (Math.abs(this.ctx.sampleRate - this.rate) > 0.5) {
          console.warn(`FM1Emu ${p.name}: the AudioContext runs at ${this.ctx.sampleRate} Hz, the device at ${this.rate} Hz — pitch is off by ${(1200 * Math.log2(this.ctx.sampleRate / this.rate)).toFixed(0)} cents. Create the context with { sampleRate: ${this.rate} }.`);
        }
        return this;
      })();
      return this._initP;
    }

    _boot() {
      const p = this.profile, build = this._build;
      const node = new AudioWorkletNode(this.ctx, p.processor, { numberOfInputs: 0, numberOfOutputs: 1, outputChannelCount: [2] });
      node.connect(this.output);
      this.node = node;
      this.ready = false;
      return new Promise((resolve, reject) => {
        const to = setTimeout(() => reject(new Error(`FM1Emu ${p.name}: no answer from the worklet in 20 s`)), 20000);
        this._bootDone = (err) => { clearTimeout(to); this._bootDone = null; if (err) reject(err); else resolve(); };
        node.port.onmessage = (e) => this._onMsg(e.data);
        node.onprocessorerror = () => { const e = new Error(`FM1Emu ${p.name}: the worklet crashed`); this.dispatchEvent(new CustomEvent('error', { detail: e })); if (this._bootDone) this._bootDone(e); };
        const wasm = build.bytes.slice().buffer;
        const hint = p.rtHint[build.sha] || this._cachedRing(build.sha);
        const load = { type: 'load', wasm, master: this._master, fm1: { rt: p.rt, hint, mq: 64 } };
        load[p.flashKey] = this._flash || {};
        node.port.postMessage(load, [wasm]);
      }).then(() => {
        this.ready = true;
        this._btnMask = -1; this._keyMask = -1;        // resend the held controls
        this._syncButtons(true); this._syncKeys(true);
        this._sendVisible();
        this.dispatchEvent(new CustomEvent('ready', { detail: { caps: this.caps, rate: this.rate } }));
      });
    }

    _cachedRing(sha) { try { const v = lsGet('fm1emu_ring_' + sha); return v ? JSON.parse(v) : null; } catch (e) { return null; } }

    _onMsg(m) {
      if (!m) return;
      if (m.type === 'frame') return this._frame(m);
      if (m.type === 'ready') { if (m.rate) this._rate = m.rate; return; }
      if (m.type === 'error') { const e = new Error(m.message); this.dispatchEvent(new CustomEvent('error', { detail: e })); if (this._bootDone) this._bootDone(e); return; }
      if (m.type !== 'fm1') return;
      if (m.op === 'info') {
        if (m.rate) this._rate = m.rate;
        this.caps = { midi: !!m.midi, realtime: !!m.realtime };
        if (m.scanned && m.ring && this._build && this._build.sha) lsSet('fm1emu_ring_' + this._build.sha, JSON.stringify(m.ring));
        if (!m.midi) console.warn(`FM1Emu ${this.profile.name}: this build has no MIDI input; only the panel plays it.`);
        if (this._bootDone) this._bootDone();
      } else if (m.op === 'stats') {
        const r = this._statsWait.get(m.id);
        if (r) { this._statsWait.delete(m.id); r(m); }
      } else if (m.op === 'error') {
        const e = new Error(m.message);
        this.dispatchEvent(new CustomEvent('error', { detail: e }));
        if (this._bootDone) this._bootDone(e);
      }
    }

    _frame(m) {
      const p = this.profile;
      if (m.fb) { this._fb = m.fb; for (const pn of this._panels) pn.paint(m.fb); }
      let L = null;
      if (p.id === 'felucca') {
        if (m.leds) { const l = m.leds; L = { litB: l[0], litK: l[1], dimB: l[2], dimK: l[3], dimLo: l[4] || 0, brB: l[5] || 0, brK: l[6] || 0, midK: l[7] || 0, anim: m.anim || null }; }
      } else if (m.buttons !== undefined) {
        L = { litB: m.buttons >>> 0, litK: m.keys >>> 0, dimB: 0, dimK: m.dim >>> 0, dimLo: 0, brB: 0, brK: 0, midK: 0, anim: null };
      }
      if (L) {
        const key = [L.litB, L.litK, L.dimB, L.dimK, L.dimLo, L.brB, L.brK, L.midK, L.anim ? L.anim.join(',') : ''].join(';');
        if (key !== this._ledKey) { this._ledKey = key; this._leds = L; for (const pn of this._panels) pn.lights(L); }
      }
      if (m.load !== undefined) {
        this.cpu = p.id === 'felucca' ? m.load * 100 : +m.load;
        this.dispatchEvent(new CustomEvent('load', { detail: { cpu: this.cpu } }));
      }
      const fl = m[p.flashKey];
      if (fl) {
        const f = {};
        for (const [k, v] of Object.entries(fl)) f[k] = v instanceof Uint8Array ? v : new Uint8Array(v);
        this._flash = f;
        this._scheduleSave();
        this.dispatchEvent(new CustomEvent('flash', { detail: { keys: Object.keys(f).length } }));
      }
      if (m.fb || L) this.dispatchEvent(new CustomEvent('frame', { detail: { fb: !!m.fb, leds: !!L } }));
    }

    // ── flash persistence ─────────────────────────────────────────────────────────────────────
    _flashJSON(f = this._flash) {
      const data = {};
      for (const [k, v] of Object.entries(f || {})) data[k] = b64e(v);
      return { kind: this.profile.flashKey, data };
    }
    _flashFrom(j) {
      if (!j || !j.data) return {};
      if (j.kind && j.kind !== this.profile.flashKey) throw new Error(`FM1Emu: flash of kind ${j.kind}, ${this.profile.name} keeps ${this.profile.flashKey}`);
      const f = {};
      for (const [k, v] of Object.entries(j.data)) f[k] = b64d(v);
      return f;
    }
    async _loadFlash() {
      try { return this._flashFrom(await kvStore().kvGet(this.flashKey)); } catch (e) { console.warn('FM1Emu: could not read the saved flash', e); return {}; }
    }
    _scheduleSave() {
      if (this.opts.persist === false) return;
      clearTimeout(this._saveT);
      this._saveT = setTimeout(() => this.flushFlash(), 400);
    }
    /** Write the device's flash to storage now; resolves when stored. */
    flushFlash() {
      clearTimeout(this._saveT);
      if (this.opts.persist === false || this._flash === null) return Promise.resolve(false);
      const j = this._flashJSON();
      this._savePending = kvStore().kvSet(this.flashKey, j).then(() => { this.dispatchEvent(new CustomEvent('flashsaved')); return true; },
        (e) => { console.warn('FM1Emu: could not save the flash', e); return false; });
      return this._savePending;
    }

    getState() {
      return { v: 1, id: this.id, version: this.profile.version, master: this._master, flash: this._flashJSON() };
    }
    /** Restore a getState() snapshot: the device reboots with that flash (its saved projects / presets). */
    async setState(json, { persist = true } = {}) {
      const s = typeof json === 'string' ? JSON.parse(json) : json;
      if (!s || (s.id && s.id !== this.id)) { console.warn(`FM1Emu: state for ${s && s.id}, this is ${this.id}`); return false; }
      if (s.master !== undefined) this._master = Math.max(0, Math.min(this.profile.master.max, s.master | 0));
      this._flash = this._flashFrom(s.flash);
      if (persist && this.opts.persist !== false) await this.flushFlash();
      if (this.node) await this.reboot();
      return true;
    }
    /** Power-cycle the emulated device (keeps its flash). */
    async reboot() {
      if (!this._build) return this.init();
      this._killNode();
      this._active.clear();
      await this._boot();
    }
    _killNode() {
      if (!this.node) return;
      try { this.node.port.postMessage({ type: 'fm1', op: 'dispose' }); } catch (e) { /* closed */ }
      try { this.node.disconnect(); } catch (e) { /* already */ }
      this.node.port.onmessage = null;
      this.node = null;
      this.ready = false;
    }

    // ── playing it ────────────────────────────────────────────────────────────────────────────
    _post(m, when) {
      if (!this.node) return;
      if (when != null && when > this.ctx.currentTime + 0.0005) this.node.port.postMessage({ type: 'fm1', op: 'at', t: when, m });
      else this.node.port.postMessage(m);
    }
    noteOn(note, vel01 = 1, when, channel = 1) {
      const ch = clampCh(channel), v = vel01 > 0 ? Math.max(1, Math.min(127, Math.round(vel01 * 127))) : 0;
      if (!v) return this.noteOff(note, when, channel);
      this._active.set(ch * 128 + (note & 127), true);
      this._chUsed.add(ch);
      this._post({ type: 'midi', data: [0x90 | ch, note & 127, v] }, when);
    }
    noteOff(note, when, channel = 1) {
      const ch = clampCh(channel);
      this._active.delete(ch * 128 + (note & 127));
      this._post({ type: 'midi', data: [0x80 | ch, note & 127, 0] }, when);
    }
    /** Every note off. Without `when` (or when it is now) the not-yet-applied scheduled messages are dropped too. */
    allOff(when) {
      const now = when == null || when <= this.ctx.currentTime + 0.0005;
      if (now && this.node) this.node.port.postMessage({ type: 'fm1', op: 'clear' });
      for (const k of this._active.keys()) this._post({ type: 'midi', data: [0x80 | (k >> 7), k & 127, 0] }, when);
      this._active.clear();
      if (this.profile.id === 'felucca') {                              // pedal up, then CC123 (midi_control.c)
        for (const ch of this._chUsed) {
          this._post({ type: 'midi', data: [0xB0 | ch, 64, 0] }, when);
          this._post({ type: 'midi', data: [0xB0 | ch, 123, 0] }, when);
        }
      }
    }
    cc(num, value01, when, channel = 1) {
      const ch = clampCh(channel);
      this._chUsed.add(ch);
      this._post({ type: 'midi', data: [0xB0 | ch, num & 127, Math.max(0, Math.min(127, Math.round(value01 * 127)))] }, when);
    }
    /** Raw MIDI bytes (one or more messages, running status ok), realtime included: 0xF8 clock, 0xFA start, 0xFB continue, 0xFC stop. SysEx / system common are skipped. */
    midi(bytes, when) {
      const d = bytes instanceof Uint8Array || Array.isArray(bytes) ? bytes : Array.from(bytes || []);
      let run = 0, i = 0;
      while (i < d.length) {
        const b = d[i] & 255;
        if (b >= 0xF8) { this._post({ type: 'midi', data: [b, 0, 0] }, when); i++; continue; }
        if (b === 0xF0) { while (i < d.length && (d[i] & 255) !== 0xF7) i++; i++; run = 0; continue; }
        if (b >= 0xF1 && b <= 0xF7) { i += b === 0xF2 ? 3 : b === 0xF1 || b === 0xF3 ? 2 : 1; run = 0; continue; }
        let s = run;
        if (b >= 0x80) { s = run = b; i++; }
        if (!s) { i++; continue; }
        const n = (s & 0xF0) === 0xC0 || (s & 0xF0) === 0xD0 ? 1 : 2;
        const d1 = d[i] & 127, d2 = n === 2 ? (d[i + 1] & 127) : 0;
        i += n;
        const t = s & 0xF0, ch = s & 15;
        if (t === 0x90 && d2) { this._active.set(ch * 128 + d1, true); this._chUsed.add(ch); }
        else if (t === 0x80 || t === 0x90) this._active.delete(ch * 128 + d1);
        else this._chUsed.add(ch);
        this._post({ type: 'midi', data: [s, d1, d2] }, when);
      }
    }
    /** Jitter of the scheduled messages so far: {n, meanMs, meanAbsMs, maxMs, minMs, late, quantumMs}. */
    stats(reset = false) {
      if (!this.node) return Promise.resolve(null);
      const id = ++this._statsN;
      return new Promise((res) => { this._statsWait.set(id, res); this.node.port.postMessage({ type: 'fm1', op: 'stats', id, reset }); });
    }

    // ── the panel's controls, also callable directly ──────────────────────────────────────────
    setMaster(v) {
      this._master = Math.max(0, Math.min(this.profile.master.max, Math.round(v)));
      if (this.node) this.node.port.postMessage({ type: 'master', value: this._master });
      for (const pn of this._panels) pn.knob('MASTER');
    }
    /** Turn an encoder: role 0 SELECT, 1 ALGORITHM, 2 PRESETS, 3..6 KNOB 1..4 (or its name). */
    enc(role, n) {
      const r = typeof role === 'string' ? ENC[role] : role;
      if (r === undefined || !n) return;
      if (this.node) this.node.port.postMessage({ type: 'enc', role: r, n: n | 0 });
    }
    /** Hold (down=true) or let go a button by its label ('PLAY', 'OCT-', …) or bit; `src` names who holds it. */
    button(label, down, src = 'api') {
      const bit = typeof label === 'string' ? BTN[label] : label;
      if (bit === undefined) return;
      const id = src + ':' + bit;
      if (down) this._btnBy.set(id, bit); else this._btnBy.delete(id);
      this._syncButtons();
    }
    /** Hold or let go one of the 27 keys (0 = F3 … 26 = G5). */
    key(k, down, src = 'api') {
      if (!(k >= 0 && k < 27)) return;
      const id = src + ':' + k;
      if (down) this._keyBy.set(id, k); else this._keyBy.delete(id);
      this._syncKeys();
    }
    latch(bit) { this._latched ^= 1 << bit; this._syncButtons(true); }
    _syncButtons(redraw) {
      let m = this._latched;
      for (const b of this._btnBy.values()) m |= 1 << b;
      if (m !== this._btnMask) { this._btnMask = m; if (this.node) this.node.port.postMessage({ type: 'buttons', mask: m >>> 0 }); }
      else if (!redraw) return;
      for (const pn of this._panels) pn.held(m, this._latched, -1);
    }
    _syncKeys(redraw) {
      let m = 0;
      for (const k of this._keyBy.values()) m |= 1 << k;
      if (m !== this._keyMask) { this._keyMask = m; if (this.node) this.node.port.postMessage({ type: 'keys', mask: m >>> 0 }); }
      else if (!redraw) return;
      for (const pn of this._panels) pn.held(-1, -1, m);
    }
    _sendVisible() {
      if (this.node && this.profile.id === 'felucca') this.node.port.postMessage({ type: 'visible', on: !document.hidden && this._panels.size > 0 });
    }

    /** The FM-1 face: { el, relayout(), destroy() }. opts.scale: 1 = 1000 px wide (default: fill the container's width); opts.keyboard: the computer keyboard plays it, mapped as the author's page. */
    mountPanel(container, opts = {}) {
      const pn = new Panel(this, container, opts);
      this._panels.add(pn);
      if (this._fb) pn.paint(this._fb);
      pn.lights(this._leds);
      pn.held(this._btnMask < 0 ? 0 : this._btnMask, this._latched, this._keyMask < 0 ? 0 : this._keyMask);
      this._sendVisible();
      // relayout(): re-measure the hit areas (call it if the panel was mounted while hidden, e.g. display:none)
      return { el: pn.root, relayout: () => pn._hits(), destroy: () => { pn.destroy(); this._panels.delete(pn); this._sendVisible(); } };
    }

    dispose() {
      if (this._disposed) return;
      this._disposed = true;
      if (this._saveT) this.flushFlash();
      for (const pn of this._panels) pn.destroy();
      this._panels.clear();
      this._killNode();
      try { this.output.disconnect(); } catch (e) { /* already */ }
      document.removeEventListener('visibilitychange', this._onVis);
    }
  }

  // ── the panel (after Felucca's web/emu/index.html and X0X's, which it follows control for control) ─────
  const NS = 'http://www.w3.org/2000/svg';
  const CSS = `
.fm1e { position: relative; user-select: none; -webkit-user-select: none; -webkit-touch-callout: none; touch-action: manipulation; max-width: 100%; }
.fm1e svg { position: absolute; inset: 0; width: 100%; height: 100%; pointer-events: none; }
.fm1e canvas { position: absolute; image-rendering: pixelated; background: #000; }
.fm1e .hit { position: absolute; touch-action: none; cursor: pointer; -webkit-tap-highlight-color: transparent; border-radius: 10px; }
.fm1e .hit.knob { cursor: ns-resize; border-radius: 50%; }
.fm1e .hit:focus-visible { outline: 2px solid #fff4d6; outline-offset: 2px; }
.fm1e-felucca .face { transition: fill .05s; }
.fm1e-felucca .dim .face.btn { fill: #3a3934; }
.fm1e-felucca .lit .face.btn { fill: #fff4d6; }
.fm1e-felucca .lit text { fill: #1d1d1f; }
.fm1e-felucca .green .face.btn { fill: #5fe08a; }
.fm1e-felucca .green text { fill: #0d2414; }
.fm1e-felucca .face.key { fill: #0c0c0d; stroke: #3a3a3e; stroke-width: 1.5; }
.fm1e-felucca .slit { fill: #3a3a3c; transition: fill .05s; }
.fm1e-felucca .dim .slit { fill: #77777b; }
.fm1e-felucca .lit .slit { fill: #ececee; filter: drop-shadow(0 0 3px rgba(255, 255, 255, .6)); }
@keyframes fm1e-breath-btn { 0%, 100% { fill: #3a3934; } 50% { fill: #d8cfb6; } }
@keyframes fm1e-breath-slit { 0%, 100% { fill: #3a3a3c; } 50% { fill: #c8c8ca; } }
@keyframes fm1e-breath-btn-lo { 0%, 100% { fill: #3a3934; } 50% { fill: #aca592; } }
@keyframes fm1e-breath-slit-lo { 0%, 100% { fill: #3a3a3c; } 50% { fill: #a1a1a3; } }
.fm1e-felucca .breath .face.btn { animation: fm1e-breath-btn 1.13s ease-in-out infinite; }
.fm1e-felucca .breath .slit { animation: fm1e-breath-slit 1.13s ease-in-out infinite; }
.fm1e-felucca.dimlo .breath .face.btn { animation-name: fm1e-breath-btn-lo; }
.fm1e-felucca.dimlo .breath .slit { animation-name: fm1e-breath-slit-lo; }
.fm1e-felucca .mid .slit { fill: #9a9a9e; }
.fm1e-felucca.dimlo .mid .slit { fill: #8a8a8e; }
.fm1e-felucca .held .face { stroke: #fff4d6; stroke-width: 3; }
.fm1e-felucca .latched .face { stroke: #79b8ff; stroke-width: 3; }
.fm1e-x0x .btnface, .fm1e-x0x .keyface { transition: fill .06s; }
.fm1e-x0x .lit .btnface { fill: #f0a043; }
.fm1e-x0x .lit text { fill: #1b1205; }
.fm1e-x0x .held .btnface, .fm1e-x0x .held .keyface { stroke: #f0a043; stroke-width: 3; }
.fm1e-x0x .latched .btnface { stroke: #6fc3ff; stroke-width: 3; }
.fm1e-x0x .lit .keyface.white { fill: #f3b25c; }
.fm1e-x0x .lit .keyface.black { fill: #e0902c; }
.fm1e-x0x .dim .keyface.white { fill: #f6dcb6; }
.fm1e-x0x .dim .keyface.black { fill: #7a5326; }
@media (prefers-reduced-motion: reduce) { .fm1e-felucca .breath .face.btn, .fm1e-felucca .breath .slit { animation: none; } }
`;
  function injectCss() {
    if (document.getElementById('fm1emu-css')) return;
    const s = document.createElement('style');
    s.id = 'fm1emu-css';
    s.textContent = CSS;
    document.head.appendChild(s);
  }
  const LOOK = {
    felucca: {
      w: 1000, h: 624, body: '#1d1d1f', tray: '#141415', part: '#2a2a2d', edge: '#3a3a3e', label: '#d6d6d8',
      screen: [292, 44, 256], screenRx: 18, inset: 8,
      knobs: [[105, 100, 24], [215, 100, 24], [105, 205, 24], [215, 205, 24], [610, 100, 22], [714, 100, 22], [818, 100, 22], [922, 100, 22]],
      trays: [[50, 250, 220, 50], [568, 160, 400, 140]], oct: [[60, 258, 90, 34], [170, 258, 90, 34]],
      grid: [582, 174, 54, 48, 63, 62], keybed: [36, 332, 928, 256], font: "'DotGothic16', -apple-system, 'Helvetica Neue', Arial, sans-serif",
    },
    x0x: {
      w: 1000, h: 640, body: '#3a3d42', tray: '#26282c', part: '#2e3135', edge: '#4a4d52', label: '#e8e8ea', knob: '#1f2124',
      screen: [300, 44, 236], screenRx: 26, inset: 18,
      knobs: [[105, 100, 24], [215, 100, 24], [105, 205, 24], [215, 205, 24], [610, 100, 22], [714, 100, 22], [818, 100, 22], [922, 100, 22]],
      trays: [[58, 258, 210, 58], [568, 160, 400, 140]], oct: [[72, 268, 82, 38], [170, 268, 82, 38]],
      grid: [582, 174, 54, 48, 63, 62], keybed: [36, 340, 928, 270], font: "'Barlow Semi Condensed', 'Arial Narrow', Arial, sans-serif",
    },
  };
  // the computer keyboard, as each author's page maps it
  function keymap(p) {
    const K = {};
    if (p.look === 'felucca') {
      ['KeyZ', 'KeyX', 'KeyC', 'KeyV', 'KeyB', 'KeyN', 'KeyM', 'Comma', 'Period', 'Slash'].forEach((c, i) => { K[c] = { key: WHITE[i] }; });
      [['KeyS', 1], ['KeyD', 3], ['KeyF', 5], ['KeyH', 8], ['KeyJ', 10], ['KeyL', 13], ['Semicolon', 15], ['Quote', 17]].forEach(([c, k]) => { K[c] = { key: k }; });
      ['KeyQ', 'KeyW', 'KeyE', 'KeyR', 'KeyT', 'KeyY', 'KeyU', 'KeyI', 'KeyO'].forEach((c, i) => { K[c] = { key: 18 + i }; });
      ['Digit1', 'Digit2', 'Digit3', 'Digit4', 'Digit5', 'Digit6', 'Digit7', 'Digit8', 'Digit9', 'Digit0', 'Minus', 'Equal']
        .forEach((c, i) => { K[c] = { btn: BTN[[...p.row1, ...ROW2][i]] }; });
      K.BracketLeft = { btn: BTN['OCT-'] }; K.BracketRight = { btn: BTN['OCT+'] };
      K.ArrowUp = { enc: [ENC.SELECT, 1] }; K.ArrowDown = { enc: [ENC.SELECT, -1] };
      K.ArrowRight = { enc: [ENC.ALGORITHM, 1] }; K.ArrowLeft = { enc: [ENC.ALGORITHM, -1] };
    } else {
      'qwertyui'.split('').forEach((c, i) => { K['Key' + c.toUpperCase()] = { key: WHITE[i] }; });
      'asdfghjk'.split('').forEach((c, i) => { K['Key' + c.toUpperCase()] = { key: WHITE[8 + i] }; });
      '1234567890'.split('').forEach((c, i) => { K['Digit' + c] = { key: BLACK[i] }; });
      K.Minus = { key: BLACK[10] };
      Object.assign(K, { Space: { btn: BTN.PLAY }, Enter: { btn: BTN.REC }, ShiftLeft: { btn: BTN.SEL }, ShiftRight: { btn: BTN.SEL },
        Escape: { btn: BTN.HOME }, KeyZ: { btn: BTN['OCT-'] }, KeyX: { btn: BTN['OCT+'] },
        ArrowUp: { enc: [ENC.SELECT, 1] }, ArrowDown: { enc: [ENC.SELECT, -1] } });
    }
    return K;
  }
  const KEYNAMES = ['F', 'F♯', 'G', 'G♯', 'A', 'A♯', 'B', 'C', 'C♯', 'D', 'D♯', 'E'];
  const keyName = (k) => KEYNAMES[k % 12] + (3 + Math.floor((k + 5) / 12));

  class Panel {
    constructor(emu, container, opts) {
      injectCss();
      this.emu = emu;
      const p = emu.profile, L = (this.L = LOOK[p.look]);
      this.p = p;
      this.uid = 'pn' + Math.random().toString(36).slice(2, 8);
      const root = (this.root = document.createElement('div'));
      root.className = 'fm1e fm1e-' + p.look;
      root.style.aspectRatio = `${L.w} / ${L.h}`;
      root.style.width = opts.scale ? Math.round(L.w * opts.scale) + 'px' : '100%';
      const svg = (this.svg = document.createElementNS(NS, 'svg'));
      svg.setAttribute('viewBox', `0 0 ${L.w} ${L.h}`);
      svg.setAttribute('aria-hidden', 'true');
      root.appendChild(svg);
      const cv = (this.canvas = document.createElement('canvas'));
      cv.width = cv.height = 240;
      cv.setAttribute('role', 'img');
      cv.setAttribute('aria-label', p.name + ' screen');
      root.appendChild(cv);
      this.g2 = cv.getContext('2d');
      this.img = this.g2.createImageData(240, 240);
      this.angle = Object.fromEntries(KNOBS.map((n) => [n, 0]));
      this.knobs = []; this.buttons = []; this.keys = [];
      this._build();
      container.appendChild(root);
      requestAnimationFrame(() => this._hits());                       // the hit areas need the laid-out SVG
      this._off = [];
      const release = (e) => { const id = 'p' + this.uid + e.pointerId; if (emu._btnBy.delete(id)) emu._syncButtons(); if (emu._keyBy.delete(id)) emu._syncKeys(); };
      for (const t of ['pointerup', 'pointercancel', 'lostpointercapture']) { root.addEventListener(t, release); }
      if (opts.keyboard) this._keyboard();
    }

    el(tag, attrs, parent = this.svg) {
      const e = document.createElementNS(NS, tag);
      for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, v);
      parent.appendChild(e);
      return e;
    }
    text(parent, x, y, s, size, ink) {
      const t = this.el('text', { x, y, 'text-anchor': 'middle', 'font-family': this.L.font, 'font-size': size, 'font-weight': 600,
        fill: ink || this.L.label, 'letter-spacing': '.04em' }, parent);
      t.textContent = s;
      return t;
    }

    _build() {
      const L = this.L, p = this.p, x0x = p.look === 'x0x';
      this.el('rect', { x: 4, y: 4, width: L.w - 8, height: L.h - 8, rx: x0x ? 44 : 40, fill: L.body });
      for (const [x, y, w, h] of L.trays) this.el('rect', { x, y, width: w, height: h, rx: 14, fill: L.tray });
      const [sx, sy, ss] = L.screen;
      this.el('rect', { x: sx, y: sy, width: ss, height: ss, rx: L.screenRx, fill: x0x ? '#111214' : '#0b0b0c' });
      Object.assign(this.canvas.style, { left: `${(sx + L.inset) / L.w * 100}%`, top: `${(sy + L.inset) / L.h * 100}%`,
        width: `${(ss - 2 * L.inset) / L.w * 100}%`, height: `${(ss - 2 * L.inset) / L.h * 100}%` });
      KNOBS.forEach((n, i) => {
        const [x, y, r] = L.knobs[i], g = this.el('g', {});
        this.el('circle', { cx: x, cy: y, r: r + 5, fill: L.tray }, g);
        this.el('circle', { cx: x, cy: y, r, fill: x0x ? L.knob : L.part, stroke: x0x ? '#44474c' : L.edge, 'stroke-width': 2 }, g);
        const ind = n === 'MASTER' || x0x ? this.el('line', { x1: x, y1: y - r + 5, x2: x, y2: y - r + (x0x ? 15 : 14), stroke: L.label, 'stroke-width': 3, 'stroke-linecap': 'round' }, g) : null;
        this.text(g, x, y - r - 12, x0x ? n.replace(' ', '') : n, x0x ? 17 : 16);
        this.el('circle', { cx: x, cy: y, r: r + (x0x ? 14 : 12), fill: 'transparent' }, g);
        this.knobs.push({ g, ind, x, y, name: n, role: n === 'MASTER' ? 'master' : ENC[n] });
      });
      const button = ([x, y, w, h], n, sub) => {
        const g = this.el('g', {});
        this.el('rect', { x, y, width: w, height: h, rx: x0x ? 9 : 8, fill: L.part, stroke: L.edge, 'stroke-width': 1.5, class: x0x ? 'btnface' : 'face btn' }, g);
        const ink = n === 'REC' && !x0x ? '#ff453a' : undefined;
        if (sub) { this.text(g, x + w / 2, y + h / 2 - (x0x ? 1 : 2), n, x0x ? 12 : 10.8, ink); this.text(g, x + w / 2, y + h / 2 + (x0x ? 12 : 11), sub, x0x ? 12 : 9.9); }
        else this.text(g, x + w / 2, y + h / 2 + (x0x ? 5 : 4.5), n, x0x ? 15 : 12.6, ink);
        this.buttons.push({ g, bit: BTN[n], name: sub ? `${n} / ${sub}` : n });
      };
      button(L.oct[0], 'OCT-');
      button(L.oct[1], 'OCT+');
      const [gx, gy, gw, gh, dx, dy] = L.grid;
      for (let i = 0; i < 6; i++) {
        button([gx + i * dx, gy, gw, gh], p.row1[i]);
        button([gx + i * dx, gy + dy, gw, gh], ROW2[i], ROW2[i] === 'PLAY' ? 'STOP' : '');
      }
      const [x0, y0, w, h] = L.keybed;
      this.el('rect', { x: x0, y: y0, width: w, height: h, rx: 18, fill: L.tray });
      const pitch = (w - 24) / 16, kw = pitch * 0.78;
      if (x0x) {
        WHITE.forEach((k, i) => {
          const g = this.el('g', {});
          this.el('rect', { x: x0 + 12 + i * pitch + (pitch - kw) / 2, y: y0 + h * 0.43, width: kw, height: h * 0.52, rx: kw / 2, fill: '#d9dadc', class: 'keyface white' }, g);
          this.keys[k] = { g, name: keyName(k) };
        });
        BLACK_AFTER.forEach((a, j) => {
          const g = this.el('g', {});
          this.el('rect', { x: x0 + 12 + (a + 1) * pitch - kw / 2, y: y0 + h * 0.06, width: kw, height: h * 0.33, rx: kw / 2, fill: '#c9cacd', class: 'keyface black' }, g);
          this.keys[BLACK[j]] = { g, name: keyName(BLACK[j]) };
        });
      } else {
        const kh = h * 0.425, sw = Math.max(3, kw * 0.14);
        const key = (cx, cy, k) => {
          const g = this.el('g', {}), y = cy - kh / 2;
          this.el('rect', { x: cx - kw / 2, y, width: kw, height: kh, rx: kw / 2, class: 'face key' }, g);
          this.el('rect', { x: cx - sw / 2, y: y + kw * 0.4, width: sw, height: kh - kw * 0.8, rx: sw / 2, class: 'slit' }, g);
          this.el('rect', { x: cx - pitch / 2, y: cy - h * 0.24, width: pitch, height: h * 0.48, fill: 'transparent' }, g);
          this.keys[k] = { g, name: keyName(k) };
        };
        WHITE.forEach((k, i) => key(x0 + 12 + (i + 0.5) * pitch, y0 + h * 0.75, k));
        BLACK_AFTER.forEach((a, j) => key(x0 + 12 + (a + 1) * pitch, y0 + h * 0.25, BLACK[j]));
      }
    }

    // HTML targets over the drawing (the SVG takes no pointer events): touch-action and capture work everywhere
    _hits() {
      if (this.dead) return;
      const L = this.L, emu = this.emu;
      for (const d of this.root.querySelectorAll('.hit')) d.remove();
      const hit = (c, cls, role) => {
        const b = c.g.getBBox(), d = document.createElement('div');
        d.className = 'hit' + (cls ? ' ' + cls : '');
        Object.assign(d.style, { left: `${b.x / L.w * 100}%`, top: `${b.y / L.h * 100}%`, width: `${b.width / L.w * 100}%`, height: `${b.height / L.h * 100}%` });
        d.setAttribute('role', role);
        d.setAttribute('aria-label', c.name);
        d.title = c.name;
        d.tabIndex = 0;
        d.addEventListener('touchstart', (e) => e.preventDefault(), { passive: false });
        d.addEventListener('contextmenu', (e) => e.preventDefault());
        this.root.appendChild(d);
        c.hit = d;
      };
      for (const k of this.knobs) {
        hit(k, 'knob', 'slider');
        k.hit.dataset.knob = k.name;
        this._bindKnob(k);
        this.knob(k.name);
      }
      for (const b of this.buttons) {
        hit(b, '', 'button');
        b.hit.dataset.btn = b.name.split(' ')[0];
        b.hit.addEventListener('pointerdown', (e) => {
          e.preventDefault();
          if (e.shiftKey || e.button === 2) { emu.latch(b.bit); return; }          // Shift-click / right-click holds it
          if (emu._latched & (1 << b.bit)) { emu.latch(b.bit); return; }
          b.hit.setPointerCapture(e.pointerId);
          emu._btnBy.set('p' + this.uid + e.pointerId, b.bit);
          emu._syncButtons();
        });
        b.hit.addEventListener('keydown', (e) => {
          if ((e.key === 'Enter' || e.key === ' ') && !e.repeat) { emu._btnBy.set('f' + this.uid + b.bit, b.bit); emu._syncButtons(); e.preventDefault(); e.stopPropagation(); }
        });
        b.hit.addEventListener('keyup', () => { if (emu._btnBy.delete('f' + this.uid + b.bit)) emu._syncButtons(); });
      }
      this.keys.forEach((k, i) => {
        hit(k, '', 'button');
        k.hit.dataset.key = i;
        k.hit.addEventListener('pointerdown', (e) => {
          e.preventDefault();
          k.hit.setPointerCapture(e.pointerId);
          emu._keyBy.set('p' + this.uid + e.pointerId, i);
          emu._syncKeys();
        });
      });
      this.held(emu._btnMask < 0 ? 0 : emu._btnMask, emu._latched, emu._keyMask < 0 ? 0 : emu._keyMask);
      this.lights(emu._leds);
    }

    knob(name) {
      const k = this.knobs.find((x) => x.name === name);
      if (!k || !k.ind) return;
      const a = name === 'MASTER' ? -135 + 270 * this.emu._master / this.p.master.max : this.angle[name];
      k.ind.setAttribute('transform', `rotate(${a} ${k.x} ${k.y})`);
    }
    turn(k, n) {
      if (!n) return;
      const emu = this.emu;
      if (k.role === 'master') emu.setMaster(emu._master + n * this.p.master.step);
      else { this.angle[k.name] = (this.angle[k.name] + n * 18) % 360; emu.enc(k.role, n); this.knob(k.name); }   // 20 detents a turn
    }
    _bindKnob(k) {
      let drag = null, wheel = 0;
      const x0x = this.p.look === 'x0x';
      k.hit.addEventListener('pointerdown', (e) => { e.preventDefault(); k.hit.setPointerCapture(e.pointerId); drag = { x: e.clientX, y: e.clientY, acc: 0 }; });
      k.hit.addEventListener('pointermove', (e) => {
        if (!drag) return;
        // up or right turns clockwise (a finger on the Deck can slide either way)
        drag.acc += (drag.y - e.clientY) + (e.clientX - drag.x);
        drag.x = e.clientX; drag.y = e.clientY;
        const step = k.role === 'master' ? 3 : (x0x ? 7 : 8), n = Math.trunc(drag.acc / step);
        if (n) { drag.acc -= n * step; this.turn(k, n); }
      });
      const end = () => { drag = null; };
      k.hit.addEventListener('pointerup', end);
      k.hit.addEventListener('pointercancel', end);
      k.hit.addEventListener('wheel', (e) => {
        e.preventDefault();
        const dy = e.deltaMode === 1 ? e.deltaY * 33 : e.deltaY;
        if (Math.abs(dy) >= 50) { this.turn(k, dy < 0 ? 1 : -1); wheel = 0; return; }   // a wheel notch: one detent
        wheel -= dy;                                                                       // a trackpad: by distance
        const n = Math.trunc(wheel / 25);
        if (n) { wheel -= n * 25; this.turn(k, n); }
      }, { passive: false });
      k.hit.addEventListener('keydown', (e) => {
        const d = { ArrowUp: 1, ArrowRight: 1, ArrowDown: -1, ArrowLeft: -1 }[e.key];
        if (d) { this.turn(k, d); e.preventDefault(); e.stopPropagation(); }
      });
    }

    _keyboard() {
      const emu = this.emu, K = keymap(this.p), src = 'k' + this.uid;
      const skip = (e) => e.metaKey || e.ctrlKey || e.altKey || (e.target && e.target.closest && (e.target.closest('input, textarea, select, [contenteditable]') || e.target.closest('.hit.knob')));
      const down = (e) => {
        if (skip(e) || !emu.node) return;
        const m = K[e.code];
        if (!m) return;
        e.preventDefault();
        if (m.enc) { const k = this.knobs.find((x) => x.role === m.enc[0]); if (k) this.turn(k, m.enc[1]); return; }
        if (e.repeat) return;
        if (m.key !== undefined) emu.key(m.key, true, src + e.code); else emu.button(m.btn, true, src + e.code);
      };
      const up = (e) => {
        const m = K[e.code];
        if (!m) return;
        if (m.key !== undefined) emu.key(m.key, false, src + e.code); else if (m.btn !== undefined) emu.button(m.btn, false, src + e.code);
      };
      const blur = () => {
        for (const id of [...emu._btnBy.keys()]) if (id.startsWith(src)) emu._btnBy.delete(id);
        for (const id of [...emu._keyBy.keys()]) if (id.startsWith(src)) emu._keyBy.delete(id);
        emu._syncButtons(); emu._syncKeys();
      };
      W.addEventListener('keydown', down);
      W.addEventListener('keyup', up);
      W.addEventListener('blur', blur);
      this._off.push(() => { W.removeEventListener('keydown', down); W.removeEventListener('keyup', up); W.removeEventListener('blur', blur); blur(); });
    }

    paint(fb) {
      const d = this.img.data;
      for (let i = 0; i < 57600; i++) {
        const v = fb[i], p = ((v >> 8) | (v << 8)) & 0xFFFF;       // the panel's byte order -> RGB565
        d[i * 4] = ((p >> 11) & 31) * 255 / 31;
        d[i * 4 + 1] = ((p >> 5) & 63) * 255 / 63;
        d[i * 4 + 2] = (p & 31) * 255 / 31;
        d[i * 4 + 3] = 255;
      }
      this.g2.putImageData(this.img, 0, 0);
    }

    lights(L) {
      const fel = this.p.look === 'felucca';
      if (fel) this._anim(L.anim);
      this.root.classList.toggle('dimlo', !!L.dimLo);
      for (const b of this.buttons) {
        const bit = 1 << b.bit, green = fel && b.bit === BTN.PLAY && (L.litB & (1 << PLAY_GREEN));
        b.g.classList.toggle('lit', !!(L.litB & bit) && !green);
        b.g.classList.toggle('green', !!green);
        b.g.classList.toggle('dim', !!(L.dimB & bit));
        b.g.classList.toggle('breath', !!(L.brB & bit));
      }
      this.keys.forEach((k, i) => {
        const lit = !!(L.litK & (1 << i));
        k.g.classList.toggle('lit', lit);
        k.g.classList.toggle('dim', !lit && !!(L.dimK & (1 << i)));
        k.g.classList.toggle('breath', !!(L.brK & (1 << i)));
        k.g.classList.toggle('mid', !!(L.midK & (1 << i)));
      });
    }
    // Felucca's power-on sweep (hal/fm1_led_anim.h): a level per LED, mixed in linear light as its page does
    _anim(anim) {
      const lin = (hx) => [1, 3, 5].map((i) => (parseInt(hx.slice(i, i + 2), 16) / 255) ** 2.2);
      const A = this._A || (this._A = { btn: [lin('#3a3934'), lin('#3a3934'), lin('#fff4d6')], slit: [lin('#3a3a3c'), lin('#77777b'), lin('#ececee')] });
      const fill = (kind, q) => {
        const [dark, glow, lit] = A[kind], s = Math.min(q & 127, 64) / 64, base = q & 128 ? glow : dark;
        return `rgb(${base.map((v, i) => Math.round(255 * (v + (lit[i] - v) * s) ** (1 / 2.2))).join(',')})`;
      };
      for (const b of this.buttons) b.g.querySelector('.face').style.fill = anim ? fill('btn', anim[b.bit]) : '';
      this.keys.forEach((k, i) => { const s = k.g.querySelector('.slit'); if (s) s.style.fill = anim ? fill('slit', anim[14 + i]) : ''; });
    }

    held(btnMask, latched, keyMask) {
      if (btnMask >= 0) {
        for (const b of this.buttons) {
          const on = !!(btnMask & (1 << b.bit));
          b.g.classList.toggle('held', on);
          b.g.classList.toggle('latched', !!(latched & (1 << b.bit)));
          if (b.hit) b.hit.setAttribute('aria-pressed', on);
        }
      }
      if (keyMask >= 0) this.keys.forEach((k, i) => k.g.classList.toggle('held', !!(keyMask & (1 << i))));
    }

    destroy() {
      this.dead = true;
      for (const f of this._off) f();
      this.root.remove();
    }
  }

  const LIST = Object.values(PROFILES).map((p) => ({
    id: p.id, name: p.name, version: p.version, author: p.author, license: p.license, rate: p.rate, notes: p.notes,
    channels: p.channels, source: p.source, sourceCommit: p.sourceCommit, pagesCommit: p.pagesCommit, hosted: p.hosted.page,
    get vendored() { return !!(REG[p.id] && REG[p.id].wasmB64 && REG[p.id].workletSrc); },   // its wrappers are loaded
  }));

  FM1Emu.PROFILES = PROFILES;
  FM1Emu.BUTTONS = BTN;
  FM1Emu.ENCODERS = ENC;
  W.FM1Emu = FM1Emu;
  W.FM1EMU_LIST = LIST;
})();
