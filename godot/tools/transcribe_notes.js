/* transcribe_notes.js — audio → notes for the file:// tool pages, with Spotify's Basic Pitch.
 *
 *   <script src="transcribe_notes.js"></script>          (classic script, no modules, no network)
 *   await BasicPitchLite.ready()        → true / false     loads engine + model; false if no backend runs it
 *   await BasicPitchLite.transcribe(mono, sampleRate, opts)
 *     mono        Float32Array, any sample rate (resampled to Basic Pitch's 22 050 Hz with an OfflineAudioContext)
 *     opts        onProgress(fraction 0…1), onsetThreshold (0.5), frameThreshold (0.3), minNoteMs (58),
 *                 minFreq / maxFreq (Hz, null = no limit), melodiaTrick (true), signal (AbortSignal, optional)
 *     → { notes: [{ t: start s, d: duration s, n: MIDI note, v: 0…1 }] sorted by t then n,
 *         seconds (audio length), backend ('webgl' | 'wasm' | 'cpu'), ms (processing time) }
 *   BasicPitchLite.backend / .renderer / .error           diagnostics once ready() has run
 *
 * The engine is vendored in vendor/basicpitch/ (see its README): basicpitch_tf.js is TensorFlow.js 4.22
 * (core + converter + WebGL / WASM / CPU backends) with Basic Pitch 1.0.1's inference and note-creation code,
 * basicpitch_model.js the model with its weights as base64, basicpitch_wasm.js the WASM backend's SIMD binary
 * as base64. They load with a <script> on first use; the model goes in through tf.io.fromMemory and the
 * .wasm as a data: URL — Chrome blocks fetch() on file://, and nothing here touches the network.
 *
 * Backends, in order: WebGL on a real GPU (the Deck), WASM (SIMD, one thread), plain-JS CPU. A software
 * WebGL (SwiftShader, llvmpipe) goes last — it is ~10× slower than WASM. Each backend must pass a warm-up
 * (a 440 Hz window must come out as A4) or the next one is tried. Measured in headless Chromium on the
 * sandbox (2026-10-16): WASM 0.10–0.16 s per second of audio, SwiftShader WebGL ~1.0, CPU ~1.6–1.9.
 *
 * Notes come from Basic Pitch's own outputToNotesPoly + noteFramesToTime with its defaults. The audio runs
 * through the model one 2 s window at a time (Basic Pitch's evaluateModel, every tensor disposed), yielding
 * between windows so the page keeps painting; long pieces decode in 30 s segments (see _decode).
 * Basic Pitch is polyphonic and instrument-agnostic but NOT a stem separator: on bright tones and full mixes
 * it adds overtone notes (+12, +19 semitones) and octaves under the bass. The notes are a sketch.
 */
(function () {
  'use strict';
  if (typeof window === 'undefined') return;
  if (window.BasicPitchLite) return;

  const BASE = (document.currentScript && document.currentScript.src) || location.href;
  const SR = 22050, FFT_HOP = 256, FPS = SR / FFT_HOP;           // Basic Pitch's constants (constants.py)
  const DEFAULTS = { onsetThreshold: 0.5, frameThreshold: 0.3, minNoteMs: 58, minFreq: null, maxFreq: null, melodiaTrick: true };

  const yieldNow = () => new Promise(r => { const c = new MessageChannel(); c.port1.onmessage = () => { c.port1.close(); r(); }; c.port2.postMessage(0); });
  const loadScript = rel => new Promise((res, rej) => {
    const s = document.createElement('script');
    s.src = new URL(rel, BASE).href;
    s.onload = res; s.onerror = () => rej(new Error('could not load ' + rel));
    document.head.appendChild(s);
  });
  // the WebGL renderer's name, and whether it is a software rasterizer (SwiftShader in headless Chromium,
  // llvmpipe on a GPU-less Linux): those run the model ~10× slower than the WASM backend
  function webglRenderer() {
    try {
      const c = document.createElement('canvas'), gl = c.getContext('webgl2') || c.getContext('webgl');
      if (!gl) return { name: '', software: true };
      const ext = gl.getExtension('WEBGL_debug_renderer_info');
      const name = String(ext ? gl.getParameter(ext.UNMASKED_RENDERER_WEBGL) : gl.getParameter(gl.RENDERER));
      const lose = gl.getExtension('WEBGL_lose_context'); if (lose) lose.loseContext();
      return { name, software: /swiftshader|llvmpipe|softpipe|software|basic render/i.test(name) };
    } catch (e) { return { name: '', software: true }; }
  }
  function b64ToBuffer(b64) {
    const b = atob(b64), u = new Uint8Array(b.length);
    for (let i = 0; i < b.length; i++) u[i] = b.charCodeAt(i);
    return u.buffer;
  }

  const L = {
    backend: null,      // 'webgl' | 'wasm' | 'cpu' once ready() resolved true
    error: null,        // why the last backend failed (diagnostics)
    renderer: null,     // the WebGL renderer name, when WebGL was looked at
    _ready: null,
    _bp: null,
    _queue: Promise.resolve(),
    DEFAULTS,

    // Order: WebGL on a real GPU, then WASM (SIMD, single thread), then plain-JS CPU. opts.backend
    // ('webgl' | 'wasm' | 'cpu') forces one — for tests; don't switch while a transcription runs.
    ready(opts = {}) {
      if (this._ready && !opts.backend) return this._ready;
      if (this._ready && opts.backend === this.backend) return this._ready;
      return this._ready = this._load(opts.backend).catch(e => { this.error = String(e && e.message || e); this.backend = null; return false; });
    },

    async _load(force) {
      if (typeof BasicPitchVendor === 'undefined') await loadScript('vendor/basicpitch/basicpitch_tf.js');
      if (typeof BASIC_PITCH_MODEL === 'undefined') await loadScript('vendor/basicpitch/basicpitch_model.js');
      const V = BasicPitchVendor, tf = V.tf;
      if (this._bp) { (await this._bp.model).dispose(); this._bp = null; }
      let order = ['webgl', 'wasm', 'cpu'];
      if (force) order = [force];
      else {
        const r = webglRenderer();
        this.renderer = r.name;
        if (r.software) order = ['wasm', 'cpu', 'webgl'];
      }
      for (const name of order) {
        let model = null;
        try {
          if (name === 'wasm') {
            // only the SIMD binary is vendored: without SIMD the backend would ask for another file and hang
            if (!(await tf.env().getAsync('WASM_HAS_SIMD_SUPPORT'))) throw new Error('no WebAssembly SIMD');
            tf.env().set('WASM_HAS_MULTITHREAD_SUPPORT', false);
            if (typeof BASIC_PITCH_WASM_SIMD === 'undefined') await loadScript('vendor/basicpitch/basicpitch_wasm.js');
            // a data: URL is read from memory — no .wasm file, no network (fetch() of file:// is what Chrome blocks)
            const url = 'data:application/wasm;base64,' + BASIC_PITCH_WASM_SIMD;
            V.setWasmPaths({ 'tfjs-backend-wasm.wasm': url, 'tfjs-backend-wasm-simd.wasm': url, 'tfjs-backend-wasm-threaded-simd.wasm': url });
          }
          if (!(await tf.setBackend(name))) throw new Error('could not initialise');
          await tf.ready();
          const M = BASIC_PITCH_MODEL;
          model = await V.loadGraphModel(tf.io.fromMemory({
            modelTopology: M.modelTopology, weightSpecs: M.weightSpecs, weightData: b64ToBuffer(M.weightData),
            format: M.format, generatedBy: M.generatedBy, convertedBy: M.convertedBy, signature: M.signature,
          }));
          // warm-up: one window of a 440 Hz tone. Compiles the shaders, and catches a backend that runs but
          // computes garbage (NaN, or the wrong key on a low-precision GPU): the loudest frame bin must be A4.
          const n = model.inputs[0].shape[1], x = new Float32Array(n);
          for (let i = 0; i < n; i++) x[i] = 0.3 * Math.sin(2 * Math.PI * 440 * i / SR);
          const chk = tf.tidy(() => {
            const fr = model.execute(tf.tensor3d(x, [1, n, 1]), 'Identity_1');
            return [tf.max(fr), tf.argMax(tf.mean(fr, [0, 1]))];
          });
          const [mx, key] = await Promise.all(chk.map(t => t.data()));
          chk.forEach(t => t.dispose());
          if (!(Number.isFinite(mx[0]) && mx[0] > 0.3 && mx[0] <= 1.0001 && key[0] + 21 === 69)) throw new Error('warm-up gave max ' + mx[0] + ', key ' + (key[0] + 21));
          this._bp = new V.BasicPitch(Promise.resolve(model));
          this.backend = tf.getBackend();
          this.error = null;
          return true;
        } catch (e) {
          if (model) try { model.dispose(); } catch (e2) {}
          this.error = name + ': ' + (e && e.message || e);
          if (typeof console !== 'undefined') console.warn('BasicPitchLite: backend ' + name + ' failed — ' + this.error);
        }
      }
      this.backend = null;
      return false;
    },

    // one transcription at a time (tensor scopes are engine-global)
    transcribe(mono, sampleRate, opts = {}) {
      const run = this._queue.then(() => this._transcribe(mono, sampleRate, opts));
      this._queue = run.catch(() => {});
      return run;
    },

    async resample(mono, sampleRate) {
      if (sampleRate === SR) return mono;
      const len = Math.max(1, Math.ceil(mono.length * SR / sampleRate));
      const ctx = new OfflineAudioContext(1, len, SR);
      const buf = ctx.createBuffer(1, mono.length, sampleRate);
      buf.copyToChannel(mono, 0);
      const src = ctx.createBufferSource();
      src.buffer = buf; src.connect(ctx.destination); src.start();
      return (await ctx.startRendering()).getChannelData(0);
    },

    async _transcribe(mono, sampleRate, opts) {
      const t0 = performance.now();
      if (!(mono instanceof Float32Array)) throw new Error('BasicPitchLite.transcribe: mono must be a Float32Array');
      if (!(sampleRate > 0)) throw new Error('BasicPitchLite.transcribe: bad sample rate ' + sampleRate);
      if (!(await this.ready())) throw new Error('BasicPitchLite: no backend could run the model (' + this.error + ')');
      const o = Object.assign({}, DEFAULTS, opts);
      const prog = f => { if (o.onProgress) try { o.onProgress(Math.min(1, Math.max(0, f))); } catch (e) {} };
      const abort = () => { if (o.signal && o.signal.aborted) throw new DOMException('transcription aborted', 'AbortError'); };
      const seconds = mono.length / sampleRate;
      prog(0);
      if (mono.length < sampleRate * 0.05) { prog(1); return { notes: [], seconds, backend: this.backend, ms: performance.now() - t0 }; }

      const x = await this.resample(mono, sampleRate);
      abort(); prog(0.02);

      // ── the model, window by window (Basic Pitch's evaluateModel, with every tensor disposed) ──
      const V = BasicPitchVendor, tf = V.tf, bp = this._bp;
      const frames = [], onsets = [];
      tf.engine().startScope();
      try {
        const [framed, origLen] = await bp.prepareData(x);
        const nOut = Math.floor(origLen * (Math.floor(FPS) / SR)), nWin = framed.shape[0];
        let done = 0;
        for (let i = 0; i < nWin && done < nOut; i++) {
          abort();
          tf.engine().startScope();
          try {
            const [fr, on] = await bp.evaluateSingleFrame(framed, i);
            let F = bp.unwrapOutput(fr), O = bp.unwrapOutput(on);
            const rows = F.shape[0];
            if (done + rows >= nOut) { F = F.slice([0, 0], [nOut - done, -1]); O = O.slice([0, 0], [nOut - done, -1]); }
            const [fa, oa] = await Promise.all([F.array(), O.array()]);
            for (const r of fa) frames.push(r);
            for (const r of oa) onsets.push(r);
            done += rows;
          } finally { tf.engine().endScope(); }
          prog(0.02 + 0.9 * (i + 1) / nWin);
          await yieldNow();
        }
      } finally { tf.engine().endScope(); }
      abort(); prog(0.92);

      // ── notes: Basic Pitch's own decoder ──
      let notes = [];
      if (frames.length > 1) {
        const ev = await this._decode(frames, onsets, o, f => prog(0.92 + 0.08 * f), abort);
        notes = V.noteFramesToTime(ev).map(e => ({
          t: Math.max(0, e.startTimeSeconds), d: e.durationSeconds, n: e.pitchMidi | 0, v: Math.min(1, Math.max(0, e.amplitude)),
        })).filter(e => e.t < seconds && e.d > 0);
        notes.sort((a, b) => a.t - b.t || a.n - b.n);
      }
      prog(1);
      return { notes, seconds, backend: this.backend, ms: performance.now() - t0 };
    },

    // Basic Pitch's outputToNotesPoly over the whole piece is quadratic (its melodia pass rescans every frame
    // per note found): 30 s → 0.4 s, 180 s → 12 s of frozen page. So past SEG_S + 2 × PAD_S it runs on
    // SEG_S-second segments with PAD_S of context on each side, keeping the notes that START in each segment's
    // core. A note the window cut short (it reaches the window's end) is carried over and stretched by the
    // same pitch found in the next segment's left context. Same decoder, same thresholds; only the per-piece
    // onset normalisation becomes per-segment. o.noteSegmentSec = Infinity turns this off (tests compare).
    SEG_S: 30, PAD_S: 4,
    async _decode(frames, onsets, o, prog, abort) {
      const V = BasicPitchVendor, nF = frames.length, ENERGY_TOL = 11;
      const minLen = Math.round(o.minNoteMs / 1000 * FPS);
      const run = (fr, on) => V.outputToNotesPoly(fr, on, o.onsetThreshold, o.frameThreshold, minLen, true,
        o.maxFreq || null, o.minFreq || null, !!o.melodiaTrick);
      const SEG = Math.round((o.noteSegmentSec || this.SEG_S) * FPS), PAD = Math.round(this.PAD_S * FPS);
      if (!(nF > SEG + 2 * PAD)) { const ev = run(frames, onsets); prog(1); return ev; }
      // (outputToNotesPoly only mutates its inputs by zeroing bins outside min/maxFreq: idempotent, so the
      // overlapping segments can share rows)
      const out = [];
      let open = [];
      for (let c0 = 0; c0 < nF; c0 += SEG) {
        abort();
        const c1 = Math.min(nF, c0 + SEG), w0 = Math.max(0, c0 - PAD), w1 = Math.min(nF, c1 + PAD);
        const cut = end => w1 < nF && end >= w1 - 1 - ENERGY_TOL;
        const next = [];
        for (const e of run(frames.slice(w0, w1), onsets.slice(w0, w1))) {
          const s = e.startFrame + w0, end = s + e.durationFrames;
          if (s < c0) {                     // in the left context: only continues a note the last window cut
            const prev = open.find(p => p.pitchMidi === e.pitchMidi && s <= p.end && end > p.end);
            if (prev) { prev.end = end; prev.durationFrames = end - prev.startFrame; if (cut(end)) next.push(prev); }
            continue;
          }
          if (s >= c1) continue;            // the next segment's
          const n = { startFrame: s, durationFrames: e.durationFrames, pitchMidi: e.pitchMidi, amplitude: e.amplitude, end };
          out.push(n);
          if (cut(end)) next.push(n);
        }
        open = next;
        prog(c1 / nF);
        await yieldNow();
      }
      return out;
    },
  };

  window.BasicPitchLite = L;
})();
