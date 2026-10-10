/* forge_synth.js — FORGE · a Phase Plant-style semi-modular synthesizer
 *
 * Engine + reusable editor for the Modern Mythology browser tools. Plain
 * classic script (no modules, no build step, no fetch) so it works opened
 * from file:// in Chrome / Edge, inside a live AudioContext OR an
 * OfflineAudioContext (nothing that makes sound depends on setTimeout;
 * timers only tidy up nodes afterwards).
 *
 *   const synth = new ForgeSynth(ctx, { output: ctx.destination, maxVoices: 12 });
 *   await synth.init();                  // registers the crush worklet
 *   synth.loadPreset('keys_tape_ep');
 *   synth.noteOn(60, 0.8, t);  synth.noteOff(60, t + 1);
 *   const ed = synth.mountEditor(el);   …   ed.destroy();
 *
 * PUBLIC API
 *   new ForgeSynth(ctx, {output, maxVoices = 12, bpm = 120})
 *   init() → Promise            loaded() → Promise (library samples ready)
 *   noteOn(note, vel01, when)   noteOff(note, when)   allOff(when)   panic()
 *   cc(num, value01, when)      1 = mod wheel, 64 = sustain, 120/123 = all off,
 *                               state.ccMap {74: 'm1'} = CC → macro (default)
 *   pitchBend(-1..1, when)      setMacro(0-7, value01, when)
 *   bpm (get/set)               syncAt(when) — restart synced LFOs + gates on a bar
 *   getState() → {v:1,…}        setState(obj | JSON string)
 *   loadPreset(id) → bool       presetList → [{id, name, category}]   presetId
 *   getParam(path)  setParam(path, value, when)   (paths: see _resolve(), e.g.
 *     'gen.g1.level', 'filter.cutoff', 'env.2.d', 'lfo.1.rate', 'macro.3.value',
 *     'lane.A.gain', 'fx.s2.mix', 'mod.r4.depth', 'voice.glide', 'master.gain')
 *   addGenerator(type) / removeGenerator(id) / moveGenerator(id, ±1)
 *   addSnapin(lane, type, params) / removeSnapin(id) / moveSnapin(id, ±1)
 *   addMod(src, dst, depth) → id / removeMod(id) / setModDepth(id, depth, when)
 *   modTargets() → [{id, label}]   modSources() → [{id, label, color}]
 *   on(type, fn) → off()   types: state | change | macro | mods | note | cc
 *   loadLibrarySample(id)       (needs audio_kit.js's AK.lib on the page)
 *   mountEditor(el, {presets: true}) → {destroy(), element}
 *   activeVoices · output (GainNode → opts.output) · dispose()
 *   statics: ForgeSynth.defaultState() / normalizeState(s) / userPresets() /
 *            saveUserPreset(name, state) / deleteUserPreset(name)
 *   window.ForgeSynth, window.FORGE_PRESETS
 *
 * SIGNAL FLOW
 *   per voice   GENERATORS (≤ 6: analog / wavetable / noise / sample / FM op)
 *               → lane bus A|B|C → voice FILTER (lanes it covers) → velocity
 *               → AMP ENV → lane input
 *   global      LANE  input → SNAPINS (fx chain) → lane gain → master | a later lane
 *               MASTER gain → soft limiter (waveshaper, ceiling 0.98) → synth.output
 *
 * MODULATION (Phase Plant style). A routing is {id, src, dst, depth, on}.
 *   sources   env1 env2 env3 (per voice ADSR, 0..1) · lfo1 lfo2 lfo3 (-1..1,
 *             or 0..1 when "uni"; per voice when retrig, else global) ·
 *             vel (0..1) · note ((note-60)/60) · rand (per-note 0..1) ·
 *             mw (mod wheel 0..1) · pb (bend -1..1) · m1..m8 (macros 0..1)
 *   targets   voice.pitch                       4800 cents per unit depth
 *             gen.<gid>.level|pitch|pan|morph|fm|cutoff
 *                                               (pitch 4800 ct, cutoff 12000 ct,
 *                                                the rest = the knob's full span)
 *             filter.cutoff (12000 ct) · filter.res · amp.level
 *             lfo.<n>.amount · lfo.<n>.rate (20 Hz)
 *             lane.<A|B|C>.gain · master.gain
 *             fx.<sid>.<param>                  (each snapin lists its own)
 *   depth is -1..1 in "knob space": 1.0 sweeps the whole knob (pitch: 4 oct,
 *   so 1 semitone = 0.0208). Signals are summed into AudioParams through
 *   GainNodes (src → gain(depth × scale) → param); pitch goes through detune
 *   and cutoffs through filter.detune, so depth is musical. Implicit routes:
 *   filter ENV2 knob = env2 → filter.cutoff, BEND range = pb → voice.pitch.
 *   A per-voice source that targets a global parameter follows the most
 *   recent voice. An LFO may only modulate a higher-numbered LFO.
 *
 * VOICES  poly with oldest-first stealing (released voices go first), or
 *   mono / legato with glide. Mono events are kept in a time-sorted log and
 *   replayed when an earlier one arrives, so a DAW that schedules noteOn +
 *   noteOff pairs ahead (out of time order) still gets last-note priority
 *   and legato slides.
 *
 * STATE JSON ({v:1, …}) — see DEFAULT_STATE below. gens[] carry stable ids
 * (g1…), snapins carry stable ids (s1…), routings (r1…). getState() /
 * setState() round-trip it exactly; setState() normalises anything else.
 *
 * WORKLET  Chrome refuses Blob-URL worklet modules on file:// pages, so the
 *   bitcrush / downsample processor is added from a data: URL (Blob URL as
 *   the fallback). Without it, BITCRUSH falls back to a stepped waveshaper
 *   and DOWNSAMPLE passes through.
 */
(function () {
"use strict";

const TAU = Math.PI * 2;
const clamp = (v, a, b) => (v < a ? a : v > b ? b : v);
const mtof = n => 440 * Math.pow(2, (n - 69) / 12);
const clone = o => JSON.parse(JSON.stringify(o));
const isNum = v => typeof v === 'number' && isFinite(v);
const LANES = ['A', 'B', 'C'];
const MAX_GENS = 6;
const MAX_FX_PER_LANE = 8;
const MAX_OSC_PER_VOICE = 16;      // unison is trimmed to stay under this per voice
const FM_MAX_INDEX = 10;           // fm amount 1.0 = modulation index 10
const PITCH_RANGE = 4800;          // cents per unit depth
const CUTOFF_RANGE = 12000;        // cents per unit depth (≈ the 20 Hz–20 kHz knob)

const DIVS = { '4/1': 16, '2/1': 8, '1/1': 4, '1/2': 2, '1/2d': 3, '1/2t': 4 / 3, '1/4': 1, '1/4d': 1.5, '1/4t': 2 / 3,
  '1/8': 0.5, '1/8d': 0.75, '1/8t': 1 / 3, '1/16': 0.25, '1/16d': 0.375, '1/16t': 1 / 6, '1/32': 0.125 };
const DIV_LIST = Object.keys(DIVS);

// Knob-tweak smoothing. t == null → immediate (graph build time).
function smooth(param, v, t) {
  if (t == null) { param.value = v; return; }
  param.setTargetAtTime(v, t, 0.008);
}
function hold(p, t) {
  if (p.cancelAndHoldAtTime) p.cancelAndHoldAtTime(t);
  else p.cancelScheduledValues(t);
}
// ADSR on an AudioParam (0 → 1 → s). Decay / release are exponential:
// the time knob is roughly the time to fall ~35 dB.
function envOn(p, e, t) {
  const a = Math.max(0.0008, e.a);
  p.setValueAtTime(0, t);
  p.linearRampToValueAtTime(1, t + a);
  p.setTargetAtTime(e.s, t + a, Math.max(0.0006, e.d) / 4);
}
function envRetrig(p, e, t) {
  const a = Math.max(0.0008, e.a);
  hold(p, t);
  p.linearRampToValueAtTime(1, t + a);
  p.setTargetAtTime(e.s, t + a, Math.max(0.0006, e.d) / 4);
}
function envOff(p, r, t) {
  hold(p, t);
  p.setTargetAtTime(0, t, Math.max(0.003, r) / 5);
}
// Re-issue an envelope's course from T (after a cancel), given when it was
// last (re)triggered and, if so, released.
function envCont(p, e, trig, rel, T) {
  hold(p, T);
  if (rel != null) { p.setTargetAtTime(0, T, Math.max(0.003, e.r) / 5); return; }
  const a = Math.max(0.0008, e.a);
  if (T < trig + a) { p.linearRampToValueAtTime(1, trig + a); p.setTargetAtTime(e.s, trig + a, Math.max(0.0006, e.d) / 4); }
  else p.setTargetAtTime(e.s, T, Math.max(0.0006, e.d) / 4);
}
// Resonance knob 0..1 → BiquadFilter Q. LP/HP Q is in dB in Web Audio.
const isLPHP = type => type === 'lowpass' || type === 'highpass';
const resQ = (type, res) => isLPHP(type) ? -3 + res * 27 : 0.3 * Math.pow(2, res * 6);
const resScale = type => isLPHP(type) ? 27 : 19;
const dbToLin = db => Math.pow(10, db / 20);

// ── Per-context caches (PeriodicWaves belong to a context) ──────────
const CTX_CACHE = new WeakMap();
function cacheOf(ctx) {
  let c = CTX_CACHE.get(ctx);
  if (!c) { c = { waves: new Map(), workletP: null }; CTX_CACHE.set(ctx, c); }
  return c;
}

// ── Wavetables: two harmonic frames per table, morphed by POSITION ─
const NH = 48;
function harm(fn) { const a = new Float32Array(NH + 1); for (let h = 1; h <= NH; h++) a[h] = fn(h) || 0; return a; }
function formant(h, f0, fs) { let s = 0; for (const [F, bw, g] of fs) s += g * Math.exp(-Math.pow((h * f0 - F) / bw, 2)); return s; }
const VOWELS = {
  ah: [[730, 170, 1], [1090, 190, 0.55], [2440, 260, 0.22]],
  oo: [[300, 130, 1], [870, 170, 0.32], [2240, 260, 0.08]],
};
const TABLES = {
  classic: { label: 'classic · sine → saw', a: harm(h => h === 1 ? 1 : 0), b: harm(h => 1 / h) },
  hollow:  { label: 'hollow · tri → square', a: harm(h => h % 2 ? ((((h - 1) / 2) % 2) ? -1 : 1) / (h * h) : 0), b: harm(h => h % 2 ? 1 / h : 0) },
  vocal:   { label: 'vocal · ah → oo', a: harm(h => (formant(h, 130, VOWELS.ah) + 0.015) / Math.pow(h, 0.35)), b: harm(h => (formant(h, 130, VOWELS.oo) + 0.01) / Math.pow(h, 0.35)) },
  glass:   { label: 'glass · odd → sparse', a: harm(h => ({ 1: 1, 2: 0.2, 3: 0.5, 5: 0.32, 7: 0.2, 9: 0.12 })[h]), b: harm(h => ({ 1: 1, 4: 0.5, 7: 0.42, 11: 0.35, 17: 0.25, 23: 0.18 })[h]) },
  organ:   { label: 'organ · 3 bars → 7 bars', a: harm(h => ({ 1: 1, 2: 0.9, 3: 0.8 })[h]), b: harm(h => ({ 1: 1, 2: 0.9, 3: 0.8, 4: 0.7, 6: 0.55, 8: 0.6, 10: 0.3 })[h]) },
  reed:    { label: 'reed · clarinet → nasal', a: harm(h => h % 2 ? 1 / h : 0.06 / h), b: harm(h => (1 / h) * (1 + 2.6 * Math.exp(-Math.pow((h - 7) / 3, 2)))) },
  digital: { label: 'digital · square → buzz', a: harm(h => h % 2 ? 1 / h : 0), b: harm(h => h % 3 === 0 ? 0 : 1 / Math.sqrt(h)) },
};
function tableWave(ctx, name, side) {
  const C = cacheOf(ctx), key = 'wt:' + name + ':' + side;
  let w = C.waves.get(key);
  if (!w) { const im = (TABLES[name] || TABLES.classic)[side]; w = ctx.createPeriodicWave(new Float32Array(im.length), im); C.waves.set(key, w); }
  return w;
}
function pulseWave(ctx, pw) {
  pw = Math.round(clamp(pw, 0.02, 0.98) * 50) / 50;
  const C = cacheOf(ctx), key = 'pw:' + pw;
  let w = C.waves.get(key);
  if (!w) {
    const re = new Float32Array(64), im = new Float32Array(64);
    for (let h = 1; h < 64; h++) re[h] = (2 / (h * Math.PI)) * Math.sin(h * Math.PI * pw);
    w = ctx.createPeriodicWave(re, im); C.waves.set(key, w);
  }
  return w;
}
// One cycle for thumbnails (editor) — same maths as the engine.
function tableSample(name, morph, x) {
  const T = TABLES[name] || TABLES.classic; let a = 0, b = 0, na = 0, nb = 0;
  for (let h = 1; h <= NH; h++) { const s = Math.sin(TAU * h * x); a += T.a[h] * s; b += T.b[h] * s; na += Math.abs(T.a[h]); nb += Math.abs(T.b[h]); }
  return (1 - morph) * a / (na || 1) * 1.6 + morph * b / (nb || 1) * 1.6;
}

// ── Generated buffers (noise, S&H, built-in one-shots) per sample rate ─
function mkBuf(sr, chans) {
  const b = new AudioBuffer({ length: chans[0].length, numberOfChannels: chans.length, sampleRate: sr });
  chans.forEach((d, i) => b.copyToChannel(d, i));
  return b;
}
function normPeak(d, peak) { let p = 0; for (let i = 0; i < d.length; i++) p = Math.max(p, Math.abs(d[i])); if (p > 0) { const k = peak / p; for (let i = 0; i < d.length; i++) d[i] *= k; } return d; }
function jsBandpass(x, sr, f, q) {
  const w = TAU * f / sr, al = Math.sin(w) / (2 * q), a0 = 1 + al;
  const b0 = al / a0, b2 = -al / a0, a1 = -2 * Math.cos(w) / a0, a2 = (1 - al) / a0;
  const y = new Float32Array(x.length); let x1 = 0, x2 = 0, y1 = 0, y2 = 0;
  for (let i = 0; i < x.length; i++) { const v = b0 * x[i] + b2 * x2 - a1 * y1 - a2 * y2; x2 = x1; x1 = x[i]; y2 = y1; y1 = v; y[i] = v; }
  return y;
}
function karplus(sr, f, dur, o) {
  const n = Math.floor(sr * dur), out = new Float32Array(n);
  const N = Math.max(2, Math.round(sr / f - 0.5)), buf = new Float32Array(N);
  let lp = 0;
  for (let i = 0; i < N; i++) { const w = Math.random() * 2 - 1; lp += (w - lp) * o.bright; buf[i] = lp; }
  let idx = 0;
  for (let i = 0; i < n; i++) {
    const cur = buf[idx], nxt = buf[(idx + 1) % N];
    out[i] = cur; buf[idx] = o.decay * (o.blend * cur + (1 - o.blend) * nxt);
    idx = (idx + 1) % N;
  }
  return out;
}
const SAMPLE_DEFS = {
  pluck: { label: 'nylon pluck', root: 60, gen(sr) {
    const d = karplus(sr, mtof(60), 2.6, { bright: 0.55, decay: 0.997, blend: 0.5 });
    return [normPeak(d, 0.9)];
  } },
  dobro: { label: 'resonator pluck', root: 60, gen(sr) {
    const a = karplus(sr, mtof(60), 3.2, { bright: 0.92, decay: 0.9988, blend: 0.52 });
    const b = karplus(sr, mtof(72) * 1.0017, 3.2, { bright: 0.8, decay: 0.998, blend: 0.5 });
    const r1 = jsBandpass(a, sr, 470, 4), r2 = jsBandpass(a, sr, 1250, 5), r3 = jsBandpass(a, sr, 2900, 6);
    const out = new Float32Array(a.length);
    for (let i = 0; i < a.length; i++) out[i] = a[i] + 0.22 * b[i] + 0.9 * r1[i] + 0.7 * r2[i] + 0.4 * r3[i];
    return [normPeak(out, 0.9)];
  } },
  kalimba: { label: 'kalimba tine', root: 60, gen(sr) {
    const f = mtof(60), n = Math.floor(sr * 2.6), d = new Float32Array(n);
    const P = [[1, 1, 1.5], [5.4, 0.32, 0.35], [10.9, 0.12, 0.12], [2.01, 0.06, 0.6]];
    for (let i = 0; i < n; i++) {
      const t = i / sr; let v = 0;
      for (const [r, g, dec] of P) v += g * Math.sin(TAU * f * r * t) * Math.exp(-t / dec * 2.3);
      d[i] = v * Math.min(1, t * sr / 24);
    }
    return [normPeak(d, 0.9)];
  } },
  vox: { label: 'choir ah (loops)', root: 60, loop: [0.45, 2.3], gen(sr) {
    const f = mtof(60), n = Math.floor(sr * 2.6);
    const voice = (det, vibPh) => {
      const x = new Float32Array(n); let ph = 0;
      for (let i = 0; i < n; i++) {
        const t = i / sr;
        const ff = f * det * (1 + 0.006 * Math.sin(TAU * 5.1 * t + vibPh) + 0.002 * Math.sin(TAU * 0.7 * t));
        ph += ff / sr; ph -= Math.floor(ph);
        x[i] = (2 * ph - 1) * 0.5 + (ph < 0.08 ? 0.4 : 0);
      }
      const y = new Float32Array(n);
      for (const [F, bw, g] of VOWELS.ah) { const r = jsBandpass(x, sr, F, F / bw); for (let i = 0; i < n; i++) y[i] += r[i] * g; }
      return y;
    };
    const a = voice(1, 0), b = voice(1.0042, 1.7), c = voice(0.9965, 3.1);
    const L = new Float32Array(n), R = new Float32Array(n);
    for (let i = 0; i < n; i++) { const fi = Math.min(1, i / (sr * 0.12)); L[i] = (a[i] + 0.8 * b[i] + 0.4 * c[i]) * fi; R[i] = (a[i] + 0.4 * b[i] + 0.8 * c[i]) * fi; }
    const k = 0.9 / Math.max(normPk(L), normPk(R));
    for (let i = 0; i < n; i++) { L[i] *= k; R[i] *= k; }
    return [L, R];
  } },
  bowl: { label: 'singing bowl', root: 60, gen(sr) {
    const f = mtof(60), n = Math.floor(sr * 5), L = new Float32Array(n), R = new Float32Array(n);
    const P = [[1, 1, 6], [2.76, 0.5, 3.5], [5.4, 0.3, 2], [8.93, 0.15, 1.2]];
    for (let i = 0; i < n; i++) {
      const t = i / sr; let l = 0, r = 0;
      for (const [k, g, dec] of P) {
        const e = g * Math.exp(-t / dec * 2.3);
        l += e * (Math.sin(TAU * f * k * t) + Math.sin(TAU * (f * k + 0.7 * k) * t));
        r += e * (Math.sin(TAU * f * k * t + 0.6) + Math.sin(TAU * (f * k + 0.55 * k) * t + 1.1));
      }
      const fi = Math.min(1, t / 0.03); L[i] = l * fi; R[i] = r * fi;
    }
    const k = 0.9 / Math.max(normPk(L), normPk(R));
    for (let i = 0; i < n; i++) { L[i] *= k; R[i] *= k; }
    return [L, R];
  } },
  vinyl: { label: 'vinyl crackle (loops)', root: 60, loop: [0, 3], gen(sr) {
    const n = Math.floor(sr * 3), L = new Float32Array(n), R = new Float32Array(n);
    let lpl = 0, lpr = 0;
    for (let i = 0; i < n; i++) {
      lpl += ((Math.random() * 2 - 1) - lpl) * 0.08; lpr += ((Math.random() * 2 - 1) - lpr) * 0.08;
      L[i] = lpl * 0.12; R[i] = lpr * 0.12;
    }
    for (let i = 0; i < n - 40; i++) {
      if (Math.random() < 0.00035) {
        const a = (0.25 + Math.random() * 0.7) * (Math.random() < 0.5 ? -1 : 1), ch = Math.random();
        for (let j = 0; j < 30; j++) { const v = a * Math.exp(-j / 4) * (j % 2 ? -0.6 : 1); if (ch < 0.7) L[i + j] += v; if (ch > 0.3) R[i + j] += v; }
      }
    }
    return [L, R];
  } },
};
function normPk(d) { let p = 0; for (let i = 0; i < d.length; i++) p = Math.max(p, Math.abs(d[i])); return p || 1; }

const BUFS = new Map();
function bufsFor(sr) {
  let B = BUFS.get(sr);
  if (B) return B;
  B = { sr, noise: {}, samples: {}, sh: null, white: null };
  B.getNoise = color => {
    if (B.noise[color]) return B.noise[color];
    const n = sr * 2, chans = [];
    for (let c = 0; c < 2; c++) {
      const d = new Float32Array(n);
      if (color === 'pink') {
        let b0 = 0, b1 = 0, b2 = 0, b3 = 0, b4 = 0, b5 = 0, b6 = 0;
        for (let i = 0; i < n; i++) {
          const w = Math.random() * 2 - 1;
          b0 = 0.99886 * b0 + w * 0.0555179; b1 = 0.99332 * b1 + w * 0.0750759; b2 = 0.969 * b2 + w * 0.153852;
          b3 = 0.8665 * b3 + w * 0.3104856; b4 = 0.55 * b4 + w * 0.5329522; b5 = -0.7616 * b5 - w * 0.016898;
          d[i] = b0 + b1 + b2 + b3 + b4 + b5 + b6 + w * 0.5362; b6 = w * 0.115926;
        }
        normPeak(d, 0.95);
      } else if (color === 'brown') {
        let last = 0;
        for (let i = 0; i < n; i++) { last = (last + 0.02 * (Math.random() * 2 - 1)) / 1.02; d[i] = last; }
        const drift = d[n - 1] - d[0];
        for (let i = 0; i < n; i++) d[i] -= drift * i / (n - 1);
        let m = 0; for (let i = 0; i < n; i++) m += d[i]; m /= n;
        for (let i = 0; i < n; i++) d[i] -= m;
        normPeak(d, 0.95);
      } else {
        for (let i = 0; i < n; i++) d[i] = Math.random() * 2 - 1;
      }
      chans.push(d);
    }
    return (B.noise[color] = mkBuf(sr, chans));
  };
  B.getSample = name => {
    if (B.samples[name]) return B.samples[name];
    const def = SAMPLE_DEFS[name]; if (!def) return null;
    const buf = mkBuf(sr, def.gen(sr));
    return (B.samples[name] = { buffer: buf, root: def.root, loop: def.loop || null, label: def.label });
  };
  // S&H LFO source: 64 random steps, each sr/64 frames → 1 s at rate 1.
  const step = Math.floor(sr / 64), sh = new Float32Array(step * 64);
  for (let s = 0; s < 64; s++) { const v = Math.random() * 2 - 1; sh.fill(v, s * step, (s + 1) * step); }
  B.sh = mkBuf(sr, [sh]);
  BUFS.set(sr, B);
  return B;
}

// Library samples (AK.lib from audio_kit.js, when the page loaded it).
// audio_kit.js declares `const AK` — a global lexical binding, not a
// window property — so look it up by name.
function akLib() { try { return (typeof AK !== 'undefined' && AK && AK.lib) ? AK : null; } catch (e) { return null; } }
const LIB_CACHE = new Map();      // 'lib:<id>' → Promise<{buffer, root, loop, label}|null>
function loadLibSample(src) {
  if (LIB_CACHE.has(src)) return LIB_CACHE.get(src);
  const id = src.slice(4);
  const AKr = akLib();
  const p = (AKr && AKr.lib) ? Promise.all([AKr.lib.meta(id), AKr.lib.pcm(id)]).then(([meta, pcm]) => {
    if (!meta || !pcm || !pcm.length) return null;
    const chans = pcm.slice(0, 2).map(c => c instanceof Float32Array ? c : new Float32Array(c));
    const root = (meta.meta && isNum(meta.meta.root)) ? meta.meta.root : 60;
    return { buffer: mkBuf(meta.sampleRate || 48000, chans), root, loop: null, label: meta.name || id };
  }).catch(() => null) : Promise.resolve(null);
  p.then(r => { p.value = r; });
  LIB_CACHE.set(src, p);
  return p;
}

// ── Reverb impulse responses (generated, cached) ───────────────────
const IR_CACHE = new Map();
function irFor(sr, size, damp) {
  const key = sr + '|' + size.toFixed(2) + '|' + damp.toFixed(2);
  if (IR_CACHE.has(key)) return IR_CACHE.get(key);
  const len = Math.floor(sr * Math.min(12, size * 1.15 + 0.05));
  const f0 = 15000, f1 = 250 + (1 - damp) * 11000, chans = [];
  for (let c = 0; c < 2; c++) {
    const d = new Float32Array(len); let lp = 0, a = 0;
    for (let i = 0; i < len; i++) {
      if ((i & 63) === 0) { const t = i / sr, f = f0 * Math.pow(f1 / f0, Math.min(1, t / size)); a = Math.exp(-TAU * f / sr); }
      const t = i / sr;
      lp = (Math.random() * 2 - 1) * (1 - a) + lp * a;
      d[i] = lp * Math.exp(-6.9 * t / size) * Math.min(1, i / (sr * 0.004));
    }
    // a few early reflections
    for (let k = 0; k < 6; k++) { const at = Math.floor(sr * (0.007 + Math.random() * 0.045 * Math.min(1, size))); if (at < len) d[at] += (Math.random() < 0.5 ? -1 : 1) * 0.5 * Math.exp(-k * 0.3); }
    chans.push(d);
  }
  const buf = mkBuf(sr, chans);
  IR_CACHE.set(key, buf);
  if (IR_CACHE.size > 16) IR_CACHE.delete(IR_CACHE.keys().next().value);
  return buf;
}

// ── Waveshaper curves ─────────────────────────────────────────────
const SHAPE_K = 8;     // curves cover ±8 so drive never hits the hard edge
const CURVES = {};
function shaperCurve(mode) {
  if (CURVES[mode]) return CURVES[mode];
  const n = 4096, c = new Float32Array(n);
  for (let i = 0; i < n; i++) {
    const u = ((i / (n - 1)) * 2 - 1) * SHAPE_K;
    let y;
    if (mode === 'soft') y = Math.tanh(u);
    else if (mode === 'hard') y = clamp(u, -1, 1) * 0.92;
    else if (mode === 'fold') y = Math.sin(u * Math.PI / 2) * 0.95;
    else if (mode === 'crushfb') y = Math.round(clamp(u, -1, 1) * 6) / 6;     // no-worklet bitcrush fallback
    else y = clamp(u, -1, 1);
    c[i] = y;
  }
  return (CURVES[mode] = c);
}
// Master soft limiter: linear to 0.7, smooth knee to a 0.98 ceiling. The
// pre-gain of 0.25 means the curve covers inputs up to ±4.
const LIMIT_CURVE = (() => {
  const n = 8192, c = new Float32Array(n);
  for (let i = 0; i < n; i++) {
    const u = ((i / (n - 1)) * 2 - 1) * 4, a = Math.abs(u);
    c[i] = Math.sign(u) * (a < 0.7 ? a : 0.7 + 0.28 * Math.tanh((a - 0.7) / 0.28));
  }
  return c;
})();

// ── AudioWorklet: bitcrush / downsample (registered from a Blob URL) ─
const FORGE_WORKLET = `
class ForgeCrush extends AudioWorkletProcessor {
  static get parameterDescriptors() { return [
    { name: 'amount', defaultValue: 0, minValue: 0, maxValue: 1, automationRate: 'k-rate' },
    { name: 'mode', defaultValue: 0, minValue: 0, maxValue: 2, automationRate: 'k-rate' }]; }
  constructor() { super(); this.alive = true; this.h = [0, 0]; this.c = [0, 0];
    this.port.onmessage = e => { if (e.data === 'stop') this.alive = false; }; }
  process(ins, outs, P) {
    const inp = ins[0], out = outs[0];
    const amt = Math.min(1, Math.max(0, P.amount[0])), mode = Math.round(P.mode[0]);
    const q = Math.pow(2, 15 - amt * 13.6), step = 1 + Math.floor(amt * amt * 48);
    for (let ch = 0; ch < out.length; ch++) {
      const o = out[ch], i = inp && inp.length ? inp[Math.min(ch, inp.length - 1)] : null;
      if (!i) { o.fill(0); continue; }
      if (mode === 1) { for (let n = 0; n < o.length; n++) o[n] = Math.round(i[n] * q) / q; }
      else if (mode === 2) {
        let h = this.h[ch] || 0, c = this.c[ch] || 0;
        for (let n = 0; n < o.length; n++) { if (c <= 0) { h = i[n]; c = step; } c--; o[n] = h; }
        this.h[ch] = h; this.c[ch] = c;
      } else o.set(i);
    }
    return this.alive;
  }
}
registerProcessor('forge-crush', ForgeCrush);
`;
// Chrome refuses Blob-URL worklet modules on file:// pages (AbortError,
// unless launched with --allow-file-access-from-files); data: URLs load
// everywhere, so try that first and keep the Blob URL as the fallback.
let WORKLET_BLOB = null;
function loadWorklet(ctx) {
  const C = cacheOf(ctx);
  if (C.workletP) return C.workletP;
  if (!ctx.audioWorklet || typeof ctx.audioWorklet.addModule !== 'function') return (C.workletP = Promise.reject(new Error('no AudioWorklet')));
  const dataUrl = 'data:text/javascript;base64,' + btoa(FORGE_WORKLET);
  C.workletP = ctx.audioWorklet.addModule(dataUrl).catch(() => {
    if (!WORKLET_BLOB) WORKLET_BLOB = URL.createObjectURL(new Blob([FORGE_WORKLET], { type: 'application/javascript' }));
    return ctx.audioWorklet.addModule(WORKLET_BLOB);
  });
  return C.workletP;
}

// ═══════════════════════════════════════════════════════════════════
// Parameter specs (shared by the engine's normaliser and the editor)
// ═══════════════════════════════════════════════════════════════════
const GEN_TYPES = { analog: 'ANALOG', wavetable: 'WAVETABLE', noise: 'NOISE', sample: 'SAMPLE', fm: 'FM OP' };
const ANALOG_SHAPES = ['sine', 'triangle', 'saw', 'square', 'pulse'];
const NOISE_COLORS = ['white', 'pink', 'brown'];
const NOISE_FILTERS = ['none', 'lowpass', 'highpass', 'bandpass', 'notch'];
const FILTER_TYPES = ['lowpass', 'highpass', 'bandpass', 'notch', 'peaking'];
const LFO_SHAPES = ['sine', 'triangle', 'saw', 'ramp', 'square', 'sh'];

const GEN_SPEC = {
  type: { opts: Object.keys(GEN_TYPES), def: 'analog' },
  on: { bool: true, def: true },
  level: { min: 0, max: 1, def: 0.6, label: 'LEVEL', unit: '%' },
  coarse: { min: -48, max: 48, step: 1, def: 0, label: 'TUNE', unit: 'st', bip: true },
  fine: { min: -100, max: 100, step: 1, def: 0, label: 'FINE', unit: 'ct', bip: true },
  mode: { opts: ['ratio', 'fixed'], def: 'ratio' },
  ratio: { min: 0.125, max: 16, curve: 'log', def: 1, label: 'RATIO', unit: 'x' },
  hz: { min: 8, max: 16000, curve: 'log', def: 440, label: 'FREQ', unit: 'Hz' },
  unison: { min: 1, max: 7, step: 1, def: 1, label: 'UNI', unit: 'v' },
  detune: { min: 0, max: 100, def: 15, label: 'DETUNE', unit: 'ct' },
  spread: { min: 0, max: 1, def: 0.5, label: 'SPREAD', unit: '%' },
  lane: { opts: LANES, def: 'A' },
  pan: { min: -1, max: 1, def: 0, label: 'PAN', unit: 'pan', bip: true },
  shape: { opts: ANALOG_SHAPES, def: 'saw' },
  pw: { min: 0.05, max: 0.95, def: 0.5, label: 'WIDTH', unit: '%' },
  table: { opts: Object.keys(TABLES), def: 'classic' },
  morph: { min: 0, max: 1, def: 0, label: 'POS', unit: '%' },
  color: { opts: NOISE_COLORS, def: 'white' },
  nfilt: { opts: NOISE_FILTERS, def: 'none' },
  nfreq: { min: 20, max: 20000, curve: 'log', def: 4000, label: 'CUT', unit: 'Hz' },
  nres: { min: 0, max: 1, def: 0.1, label: 'RES', unit: '%' },
  src: { str: true, def: 'pluck' },
  root: { min: 12, max: 108, step: 1, def: 60, label: 'ROOT', unit: 'note' },
  start: { min: 0, max: 0.95, def: 0, label: 'START', unit: '%' },
  loop: { bool: true, def: false },
  fmTarget: { str: true, def: '' },
  fmAmt: { min: 0, max: 1, def: 0.3, label: 'FM AMT', unit: '%' },
};
const ENV_SPEC = {
  a: { min: 0.0005, max: 10, curve: 'log', def: 0.005, label: 'ATK', unit: 's' },
  d: { min: 0.001, max: 10, curve: 'log', def: 0.4, label: 'DEC', unit: 's' },
  s: { min: 0, max: 1, def: 0.7, label: 'SUS', unit: '%' },
  r: { min: 0.001, max: 12, curve: 'log', def: 0.3, label: 'REL', unit: 's' },
};
const LFO_SPEC = {
  shape: { opts: LFO_SHAPES, def: 'sine' },
  rate: { min: 0.01, max: 100, curve: 'log', def: 2, label: 'RATE', unit: 'Hz' },
  sync: { bool: true, def: false },
  div: { opts: DIV_LIST, def: '1/4' },
  retrig: { bool: true, def: true },
  uni: { bool: true, def: false },
  fade: { min: 0, max: 5, curve: 'sq', def: 0, label: 'FADE IN', unit: 's' },
  amount: { min: 0, max: 1, def: 1, label: 'AMOUNT', unit: '%' },
};
const FILTER_SPEC = {
  on: { bool: true, def: true },
  type: { opts: FILTER_TYPES, def: 'lowpass' },
  cutoff: { min: 20, max: 20000, curve: 'log', def: 8000, label: 'CUTOFF', unit: 'Hz' },
  res: { min: 0, max: 1, def: 0.15, label: 'RES', unit: '%' },
  key: { min: 0, max: 1, def: 0, label: 'KEY', unit: '%' },
  env: { min: -1, max: 1, def: 0, label: 'ENV2', unit: '%', bip: true },
  gain: { min: -24, max: 24, def: 6, label: 'GAIN', unit: 'dB', bip: true },
  lanes: { lanes: true, def: 'ABC' },
};
const VOICE_SPEC = {
  mode: { opts: ['poly', 'mono', 'legato'], def: 'poly' },
  glide: { min: 0, max: 2, curve: 'sq', def: 0, label: 'GLIDE', unit: 's' },
  bend: { min: 0, max: 24, step: 1, def: 2, label: 'BEND', unit: 'st' },
  velSens: { min: 0, max: 1, def: 0.6, label: 'VEL', unit: '%' },
};
const MASTER_SPEC = {
  gain: { min: 0, max: 1.5, def: 0.8, label: 'MASTER', unit: '%' },
  limit: { bool: true, def: true },
};
const LANE_SPEC = {
  gain: { min: 0, max: 1.5, def: 1, label: 'LANE', unit: '%' },
};
const MACRO_SPEC = { min: 0, max: 1, def: 0, label: 'MACRO', unit: '%' };

// ── Snapin (lane effect) definitions. `mods` lists modulatable params.
const SNAP_SPECS = {
  filter: { label: 'FILTER', params: {
    type: { opts: ['lowpass', 'highpass', 'bandpass', 'notch', 'peaking', 'lowshelf', 'highshelf'], def: 'lowpass' },
    cutoff: { min: 20, max: 20000, curve: 'log', def: 2000, label: 'CUTOFF', unit: 'Hz' },
    res: { min: 0, max: 1, def: 0.2, label: 'RES', unit: '%' },
    gain: { min: -24, max: 24, def: 6, label: 'GAIN', unit: 'dB', bip: true },
    mix: { min: 0, max: 1, def: 1, label: 'MIX', unit: '%' } }, mods: ['cutoff', 'res', 'gain', 'mix'] },
  dist: { label: 'DISTORTION', params: {
    mode: { opts: ['soft', 'hard', 'fold', 'bitcrush', 'downsample'], def: 'soft' },
    drive: { min: 0, max: 1, def: 0.3, label: 'DRIVE', unit: '%' },
    tone: { min: 200, max: 20000, curve: 'log', def: 12000, label: 'TONE', unit: 'Hz' },
    level: { min: 0, max: 1.5, def: 1, label: 'LEVEL', unit: '%' },
    mix: { min: 0, max: 1, def: 1, label: 'MIX', unit: '%' } }, mods: ['drive', 'tone', 'mix'] },
  delay: { label: 'DELAY', params: {
    sync: { bool: true, def: true },
    div: { opts: DIV_LIST, def: '1/8d' },
    ms: { min: 1, max: 2000, curve: 'log', def: 300, label: 'TIME', unit: 'ms' },
    fb: { min: 0, max: 0.95, def: 0.35, label: 'FDBK', unit: '%' },
    tone: { min: 300, max: 16000, curve: 'log', def: 4500, label: 'TONE', unit: 'Hz' },
    pp: { bool: true, def: false },
    mix: { min: 0, max: 1, def: 0.25, label: 'MIX', unit: '%' } }, mods: ['fb', 'tone', 'mix'], structural: ['pp'] },
  reverb: { label: 'REVERB', params: {
    size: { min: 0.2, max: 10, curve: 'log', def: 2.5, label: 'SIZE', unit: 's' },
    damp: { min: 0, max: 1, def: 0.5, label: 'DAMP', unit: '%' },
    pre: { min: 0, max: 0.2, def: 0.01, label: 'PRE', unit: 's' },
    mix: { min: 0, max: 1, def: 0.25, label: 'MIX', unit: '%' } }, mods: ['mix'] },
  chorus: { label: 'CHORUS', params: {
    rate: { min: 0.05, max: 8, curve: 'log', def: 0.6, label: 'RATE', unit: 'Hz' },
    depth: { min: 0, max: 1, def: 0.4, label: 'DEPTH', unit: '%' },
    mix: { min: 0, max: 1, def: 0.4, label: 'MIX', unit: '%' } }, mods: ['rate', 'depth', 'mix'] },
  flanger: { label: 'FLANGER', params: {
    rate: { min: 0.02, max: 5, curve: 'log', def: 0.2, label: 'RATE', unit: 'Hz' },
    depth: { min: 0, max: 1, def: 0.6, label: 'DEPTH', unit: '%' },
    fb: { min: -0.95, max: 0.95, def: 0.5, label: 'FDBK', unit: '%', bip: true },
    mix: { min: 0, max: 1, def: 0.5, label: 'MIX', unit: '%' } }, mods: ['depth', 'fb', 'mix'] },
  phaser: { label: 'PHASER', params: {
    rate: { min: 0.02, max: 8, curve: 'log', def: 0.3, label: 'RATE', unit: 'Hz' },
    depth: { min: 0, max: 1, def: 0.6, label: 'DEPTH', unit: '%' },
    freq: { min: 100, max: 4000, curve: 'log', def: 700, label: 'FREQ', unit: 'Hz' },
    fb: { min: 0, max: 0.9, def: 0.4, label: 'FDBK', unit: '%' },
    mix: { min: 0, max: 1, def: 0.5, label: 'MIX', unit: '%' } }, mods: ['freq', 'depth', 'mix'] },
  comb: { label: 'COMB', params: {
    freq: { min: 20, max: 340, curve: 'log', def: 110, label: 'FREQ', unit: 'Hz' },
    fb: { min: -0.97, max: 0.97, def: 0.7, label: 'FDBK', unit: '%', bip: true },
    damp: { min: 0, max: 1, def: 0.3, label: 'DAMP', unit: '%' },
    mix: { min: 0, max: 1, def: 0.4, label: 'MIX', unit: '%' } }, mods: ['fb', 'mix'] },
  gate: { label: 'TRANCE GATE', params: {
    div: { opts: ['1/8', '1/8t', '1/16', '1/16t', '1/32'], def: '1/16' },
    pattern: { pattern: true, def: 'x.x.xx.x x.xxx.x.'.replace(/ /g, '') },
    depth: { min: 0, max: 1, def: 1, label: 'DEPTH', unit: '%' },
    len: { min: 0.1, max: 1, def: 0.6, label: 'LEN', unit: '%' },
    smooth: { min: 0, max: 1, def: 0.25, label: 'SMOOTH', unit: '%' },
    mix: { min: 0, max: 1, def: 1, label: 'MIX', unit: '%' } }, mods: ['depth', 'mix'] },
  comp: { label: 'COMPRESSOR', params: {
    thresh: { min: -60, max: 0, def: -18, label: 'THRESH', unit: 'dB' },
    ratio: { min: 1, max: 20, curve: 'log', def: 4, label: 'RATIO', unit: ':1' },
    attack: { min: 0.001, max: 0.3, curve: 'log', def: 0.01, label: 'ATK', unit: 's' },
    release: { min: 0.02, max: 1, curve: 'log', def: 0.15, label: 'REL', unit: 's' },
    makeup: { min: 0, max: 24, def: 4, label: 'MAKEUP', unit: 'dB' },
    mix: { min: 0, max: 1, def: 1, label: 'MIX', unit: '%' } }, mods: ['thresh', 'mix'] },
  eq: { label: '3-BAND EQ', params: {
    low: { min: -18, max: 18, def: 0, label: 'LOW', unit: 'dB', bip: true },
    lowf: { min: 30, max: 600, curve: 'log', def: 120, label: 'LO F', unit: 'Hz' },
    mid: { min: -18, max: 18, def: 0, label: 'MID', unit: 'dB', bip: true },
    midf: { min: 150, max: 8000, curve: 'log', def: 1000, label: 'MID F', unit: 'Hz' },
    midq: { min: 0, max: 1, def: 0.35, label: 'MID Q', unit: '%' },
    high: { min: -18, max: 18, def: 0, label: 'HIGH', unit: 'dB', bip: true },
    highf: { min: 1500, max: 16000, curve: 'log', def: 6000, label: 'HI F', unit: 'Hz' } }, mods: ['low', 'mid', 'midf', 'high'] },
  width: { label: 'STEREO WIDTH', params: {
    width: { min: 0, max: 2, def: 1.4, label: 'WIDTH', unit: '%' } }, mods: ['width'] },
  ring: { label: 'RING MOD', params: {
    freq: { min: 1, max: 4000, curve: 'log', def: 220, label: 'FREQ', unit: 'Hz' },
    mix: { min: 0, max: 1, def: 0.5, label: 'MIX', unit: '%' } }, mods: ['freq', 'mix'] },
  tape: { label: 'TAPE', params: {
    sat: { min: 0, max: 1, def: 0.3, label: 'SAT', unit: '%' },
    wow: { min: 0, max: 1, def: 0.3, label: 'WOW', unit: '%' },
    flutter: { min: 0, max: 1, def: 0.2, label: 'FLUTTER', unit: '%' },
    age: { min: 0, max: 1, def: 0.3, label: 'AGE', unit: '%' },
    hiss: { min: 0, max: 1, def: 0.1, label: 'HISS', unit: '%' },
    mix: { min: 0, max: 1, def: 1, label: 'MIX', unit: '%' } }, mods: ['wow', 'age', 'mix'] },
};

const SOURCES = [
  { id: 'env1', label: 'ENV 1', color: '#f0b94a', hint: 'ADSR envelope 1 (per voice, 0..1)' },
  { id: 'env2', label: 'ENV 2', color: '#e8875a', hint: 'ADSR envelope 2 (per voice) — also the filter ENV2 amount' },
  { id: 'env3', label: 'ENV 3', color: '#e06a8a', hint: 'ADSR envelope 3 (per voice)' },
  { id: 'lfo1', label: 'LFO 1', color: '#6ac0e8', hint: 'LFO 1' },
  { id: 'lfo2', label: 'LFO 2', color: '#6ae0b8', hint: 'LFO 2' },
  { id: 'lfo3', label: 'LFO 3', color: '#9a8af0', hint: 'LFO 3' },
  { id: 'vel', label: 'VEL', color: '#e0d0a8', hint: 'note velocity (0..1)' },
  { id: 'note', label: 'NOTE', color: '#a8e89c', hint: 'keytrack: (note − 60) / 60' },
  { id: 'rand', label: 'RAND', color: '#f0e070', hint: 'a new random value (0..1) per note' },
  { id: 'mw', label: 'MOD WHL', color: '#ffd896', hint: 'mod wheel (CC 1)' },
  { id: 'pb', label: 'BEND', color: '#ffb0a0', hint: 'pitch bend (−1..1); also drives pitch by the BEND range' },
];
for (let i = 1; i <= 8; i++) SOURCES.push({ id: 'm' + i, label: 'M' + i, color: ['#c8a4f0', '#b8b0f8', '#e0a4e0', '#f0a4c8', '#a4c8f0', '#a4e0e0', '#d0c0a0', '#f0c0a0'][i - 1], hint: 'macro ' + i });
const SOURCE_IDS = SOURCES.map(s => s.id);
const srcColor = id => (SOURCES.find(s => s.id === id) || { color: '#d8a060' }).color;
const DST_RX = /^(voice\.pitch|gen\.[\w-]+\.(level|pitch|pan|morph|fm|cutoff)|filter\.(cutoff|res)|amp\.level|lfo\.[123]\.(amount|rate)|lane\.[ABC]\.gain|master\.gain|fx\.[\w-]+\.\w+)$/;

// ═══════════════════════════════════════════════════════════════════
// Default patch + normaliser
// ═══════════════════════════════════════════════════════════════════
const DEFAULT_STATE = {
  v: 1, name: 'INIT', category: 'user',
  gens: [{ id: 'g1', type: 'analog', shape: 'saw', level: 0.6 }],
  filter: { on: true, type: 'lowpass', cutoff: 5000, res: 0.15, key: 0.3, env: 0.15, gain: 6, lanes: 'ABC' },
  amp: { a: 0.005, d: 0.4, s: 0.75, r: 0.3 },
  envs: [{ a: 0.005, d: 0.4, s: 0.3, r: 0.3 }, { a: 0.005, d: 0.5, s: 0.2, r: 0.4 }, { a: 0.3, d: 0.6, s: 0.5, r: 0.5 }],
  lfos: [{}, { rate: 0.5 }, { rate: 5, shape: 'triangle' }],
  macros: [],
  mods: [],
  lanes: { A: { gain: 1, to: 'master', fx: [{ type: 'reverb', p: { mix: 0.15, size: 1.8 } }] }, B: {}, C: {} },
  master: { gain: 0.8, limit: true },
  voice: { mode: 'poly', glide: 0, bend: 2, velSens: 0.6 },
  ccMap: { 74: 'm1' },
};

function normNum(v, sp) {
  let x = isNum(v) ? v : (typeof v === 'string' && v.trim() !== '' && isFinite(+v) ? +v : sp.def);
  x = clamp(x, sp.min, sp.max);
  if (sp.step) x = Math.round(x / sp.step) * sp.step;
  return x;
}
function normPattern(v, def) {
  const s = (typeof v === 'string' ? v : def).replace(/[^x.]/gi, '').toLowerCase().slice(0, 16);
  return (s + '................').slice(0, 16);
}
function normField(v, sp) {
  if (sp.opts) return sp.opts.includes(v) ? v : sp.def;
  if (sp.bool) return v === undefined || v === null ? sp.def : !!v;
  if (sp.pattern) return normPattern(v, sp.def);
  if (sp.lanes) return typeof v === 'string' ? LANES.filter(L => v.toUpperCase().includes(L)).join('') : sp.def;
  if (sp.str) return typeof v === 'string' ? v.slice(0, 80) : sp.def;
  return normNum(v, sp);
}
function normObj(src, specs) {
  const o = {}; src = (src && typeof src === 'object') ? src : {};
  for (const k in specs) o[k] = normField(src[k], specs[k]);
  return o;
}
function validTo(L, to) {
  const i = LANES.indexOf(L);
  return (typeof to === 'string' && LANES.indexOf(to) > i) ? to : 'master';
}
function nextId(prefix, used) { let n = 1; while (used.has(prefix + n)) n++; const id = prefix + n; used.add(id); return id; }
function normSnap(f, used) {
  const spec = SNAP_SPECS[f.type];
  const o = { id: '', type: f.type, on: f.on !== false, p: normObj(f.p || {}, spec.params) };
  if (typeof f.id === 'string' && /^[\w-]{1,24}$/.test(f.id) && !used.has(f.id)) { o.id = f.id; used.add(f.id); }
  return o;
}
function normalizeState(src) {
  const s = (src && typeof src === 'object') ? src : {};
  const out = { v: 1, name: typeof s.name === 'string' ? s.name.slice(0, 60) : 'INIT', category: typeof s.category === 'string' ? s.category.slice(0, 24) : 'user' };
  // generators
  const gUsed = new Set();
  const gens = (Array.isArray(s.gens) ? s.gens : []).filter(g => g && GEN_TYPES[g.type]).slice(0, MAX_GENS)
    .map(g => { const o = normObj(g, GEN_SPEC); o.id = (typeof g.id === 'string' && /^[\w-]{1,24}$/.test(g.id) && !gUsed.has(g.id)) ? g.id : ''; if (o.id) gUsed.add(o.id); return o; });
  gens.forEach(g => { if (!g.id) g.id = nextId('g', gUsed); });
  gens.forEach(g => { if (g.src && !SAMPLE_DEFS[g.src] && !/^lib:/.test(g.src)) g.src = 'pluck'; if (g.fmTarget && (g.fmTarget === g.id || !gens.some(x => x.id === g.fmTarget))) g.fmTarget = ''; });
  // ids written first so the property order stays readable in the JSON
  out.gens = gens.map(g => Object.assign({ id: g.id }, g));
  out.filter = normObj(s.filter, FILTER_SPEC);
  out.amp = normObj(s.amp, ENV_SPEC);
  out.envs = [0, 1, 2].map(i => normObj((Array.isArray(s.envs) && s.envs[i]) || DEFAULT_ENV(i), ENV_SPEC));
  out.lfos = [0, 1, 2].map(i => normObj(Array.isArray(s.lfos) ? s.lfos[i] : null, LFO_SPEC));
  out.macros = Array.from({ length: 8 }, (_, i) => {
    const m = (Array.isArray(s.macros) && s.macros[i]) || {};
    return { name: typeof m.name === 'string' && m.name.trim() ? m.name.slice(0, 16) : 'MACRO ' + (i + 1), value: normNum(m.value, MACRO_SPEC) };
  });
  // lanes + snapins
  const sUsed = new Set(), pending = [];
  out.lanes = {};
  for (const L of LANES) {
    const l = (s.lanes && s.lanes[L]) || {};
    const fx = (Array.isArray(l.fx) ? l.fx : []).filter(f => f && SNAP_SPECS[f.type]).slice(0, MAX_FX_PER_LANE).map(f => normSnap(f, sUsed));
    fx.forEach(f => { if (!f.id) pending.push(f); });
    out.lanes[L] = { gain: normNum(l.gain, LANE_SPEC.gain), to: validTo(L, l.to), fx };
  }
  pending.forEach(f => { f.id = nextId('s', sUsed); });
  out.master = normObj(s.master, MASTER_SPEC);
  out.voice = normObj(s.voice, VOICE_SPEC);
  // routings
  const rUsed = new Set();
  out.mods = [];
  for (const m of (Array.isArray(s.mods) ? s.mods : [])) {
    if (!m || !SOURCE_IDS.includes(m.src) || typeof m.dst !== 'string' || !DST_RX.test(m.dst)) continue;
    const id = (typeof m.id === 'string' && /^[\w-]{1,24}$/.test(m.id) && !rUsed.has(m.id)) ? (rUsed.add(m.id), m.id) : '';
    out.mods.push({ id, src: m.src, dst: m.dst, depth: normNum(m.depth, { min: -1, max: 1, def: 0 }), on: m.on !== false });
    if (out.mods.length >= 64) break;
  }
  out.mods.forEach(m => { if (!m.id) m.id = nextId('r', rUsed); });
  out.ccMap = {};
  const cm = (s.ccMap && typeof s.ccMap === 'object') ? s.ccMap : { 74: 'm1' };
  for (const k in cm) { const n = parseInt(k, 10); if (n >= 0 && n < 128 && n !== 1 && n !== 64 && /^(m[1-8]|mw)$/.test(cm[k])) out.ccMap[n] = cm[k]; }
  return out;
}
function DEFAULT_ENV(i) { return DEFAULT_STATE.envs[i]; }

// ═══════════════════════════════════════════════════════════════════
// Snapins — each builder wires o.input → … → o.output and defines
//   o.set(key, t)   apply p[key] (already written into the state)
//   o.mod(key)      → [{param, scale}] for modulation (scale = units per depth 1)
//   o.tempo(t)      bpm changed      o.sync(t)  restart at a bar line
// Returning 'rebuild' from set() asks the synth to rebuild the snapin.
// ═══════════════════════════════════════════════════════════════════
SNAP_SPECS.filter.structural = ['type'];
SNAP_SPECS.dist.structural = ['mode'];
const logScale = sp => 1200 * Math.log2(sp.max / sp.min);

function mkMix(c, o, mix) {
  const dry = o.N(c.createGain()), wet = o.N(c.createGain());
  dry.gain.value = 1 - mix; wet.gain.value = mix;
  o.input.connect(dry); dry.connect(o.output); wet.connect(o.output);
  return {
    wet, dry,
    set(m, t) { smooth(dry.gain, 1 - m, t); smooth(wet.gain, m, t); },
    mod: () => [{ param: wet.gain, scale: 1 }, { param: dry.gain, scale: -1 }],
  };
}

function buildSnap(synth, f) {
  const c = synth.ctx, nodes = [], srcs = [], worklets = [];
  const o = {
    id: f.id, type: f.type, nodes, srcs, worklets,
    N: n => (nodes.push(n), n),
    S: n => (nodes.push(n), srcs.push(n), n),
    set: () => {}, mod: () => [], tempo: () => {}, sync: () => {},
    dispose() {
      for (const s of srcs) { try { s.stop(); } catch (e) { /* not started */ } }
      for (const w of worklets) { try { w.port.postMessage('stop'); } catch (e) { /* gone */ } }
      for (const n of nodes) { try { n.disconnect(); } catch (e) { /* already */ } }
    },
  };
  o.input = o.N(c.createGain());
  o.output = o.N(c.createGain());
  SNAP_BUILD[f.type](o, c, f.p, synth);
  return o;
}

const SNAP_BUILD = {
  filter(o, c, p) {
    const bq = o.N(c.createBiquadFilter()), mx = mkMix(c, o, p.mix);
    bq.type = p.type; bq.frequency.value = p.cutoff; bq.Q.value = resQ(p.type, p.res); bq.gain.value = p.gain;
    o.input.connect(bq); bq.connect(mx.wet);
    o.set = (k, t) => {
      if (k === 'cutoff') smooth(bq.frequency, p.cutoff, t);
      else if (k === 'res') smooth(bq.Q, resQ(p.type, p.res), t);
      else if (k === 'gain') smooth(bq.gain, p.gain, t);
      else if (k === 'mix') mx.set(p.mix, t);
    };
    o.mod = k => k === 'cutoff' ? [{ param: bq.detune, scale: CUTOFF_RANGE }]
      : k === 'res' ? [{ param: bq.Q, scale: resScale(p.type) }]
      : k === 'gain' ? [{ param: bq.gain, scale: 48 }]
      : k === 'mix' ? mx.mod() : [];
  },

  dist(o, c, p, synth) {
    const mx = mkMix(c, o, p.mix);
    const pre = o.N(c.createGain()), sh = o.N(c.createWaveShaper()), tone = o.N(c.createBiquadFilter()), post = o.N(c.createGain());
    tone.type = 'lowpass'; tone.frequency.value = p.tone; tone.Q.value = -3;
    const crushMode = p.mode === 'bitcrush' ? 1 : p.mode === 'downsample' ? 2 : 0;
    let crush = null;
    if (crushMode && synth._worklet) {
      try {
        crush = new AudioWorkletNode(c, 'forge-crush', { numberOfInputs: 1, numberOfOutputs: 1, outputChannelCount: [2],
          channelCount: 2, channelCountMode: 'explicit', channelInterpretation: 'speakers' });
        o.N(crush); o.worklets.push(crush);
        crush.parameters.get('mode').value = crushMode;
        crush.parameters.get('amount').value = p.drive;
      } catch (e) { crush = null; }
    }
    sh.curve = shaperCurve(crushMode ? (!crush && crushMode === 1 ? 'crushfb' : 'clean') : p.mode);
    if (!crushMode) sh.oversample = '4x';
    const apply = t => {
      if (crushMode) {
        smooth(pre.gain, 1 / SHAPE_K, t); smooth(post.gain, p.level, t);
        if (crush) smooth(crush.parameters.get('amount'), p.drive, t);
      } else {
        const g = 1 + p.drive * 30;
        smooth(pre.gain, g / SHAPE_K, t);
        smooth(post.gain, p.level / (1 + 0.22 * Math.sqrt(g - 1)), t);
      }
    };
    apply();
    o.input.connect(pre); pre.connect(sh);
    if (crush) { sh.connect(crush); crush.connect(tone); } else sh.connect(tone);
    tone.connect(post); post.connect(mx.wet);
    o.set = (k, t) => {
      if (k === 'drive' || k === 'level') apply(t);
      else if (k === 'tone') smooth(tone.frequency, p.tone, t);
      else if (k === 'mix') mx.set(p.mix, t);
    };
    o.mod = k => k === 'drive' ? (crushMode ? (crush ? [{ param: crush.parameters.get('amount'), scale: 1 }] : []) : [{ param: pre.gain, scale: 30 / SHAPE_K }])
      : k === 'tone' ? [{ param: tone.detune, scale: logScale(SNAP_SPECS.dist.params.tone) }]
      : k === 'mix' ? mx.mod() : [];
  },

  delay(o, c, p, synth) {
    const mx = mkMix(c, o, p.mix);
    const T = () => clamp(p.sync ? DIVS[p.div] * 60 / synth.bpm : p.ms / 1000, 0.003, 3.9);
    const dls = [], fbs = [], tones = [];
    const mkTone = () => { const b = o.N(c.createBiquadFilter()); b.type = 'lowpass'; b.frequency.value = p.tone; b.Q.value = -3; tones.push(b); return b; };
    if (!p.pp) {
      const d = o.N(c.createDelay(4)), tn = mkTone(), fb = o.N(c.createGain());
      fb.gain.value = p.fb;
      o.input.connect(d); d.connect(tn); tn.connect(fb); fb.connect(d); tn.connect(mx.wet);
      dls.push(d); fbs.push(fb);
    } else {
      const sum = o.N(c.createGain()); sum.channelCount = 1; sum.channelCountMode = 'explicit';
      const dL = o.N(c.createDelay(4)), dR = o.N(c.createDelay(4)), tL = mkTone(), tR = mkTone();
      const fA = o.N(c.createGain()), fB = o.N(c.createGain()), mg = o.N(c.createChannelMerger(2));
      fA.gain.value = Math.max(0.5, p.fb); fB.gain.value = p.fb;
      o.input.connect(sum); sum.connect(dL); dL.connect(tL); tL.connect(fA); fA.connect(dR); dR.connect(tR); tR.connect(fB); fB.connect(dL);
      tL.connect(mg, 0, 0); tR.connect(mg, 0, 1); mg.connect(mx.wet);
      dls.push(dL, dR); fbs.push(fB);
      o._fA = fA;
    }
    dls.forEach(d => { d.delayTime.value = T(); });
    o.tempo = t => dls.forEach(d => smooth(d.delayTime, T(), t));
    o.set = (k, t) => {
      if (k === 'ms' || k === 'div' || k === 'sync') o.tempo(t);
      else if (k === 'fb') { fbs.forEach(f => smooth(f.gain, p.fb, t)); if (o._fA) smooth(o._fA.gain, Math.max(0.5, p.fb), t); }
      else if (k === 'tone') tones.forEach(b => smooth(b.frequency, p.tone, t));
      else if (k === 'mix') mx.set(p.mix, t);
    };
    o.mod = k => k === 'fb' ? fbs.map(f => ({ param: f.gain, scale: 0.95 }))
      : k === 'tone' ? tones.map(b => ({ param: b.detune, scale: logScale(SNAP_SPECS.delay.params.tone) }))
      : k === 'mix' ? mx.mod() : [];
  },

  reverb(o, c, p) {
    const mx = mkMix(c, o, p.mix), pre = o.N(c.createDelay(1)), cv = o.N(c.createConvolver());
    pre.delayTime.value = p.pre;
    cv.buffer = irFor(c.sampleRate, p.size, p.damp);
    o.input.connect(pre); pre.connect(cv); cv.connect(mx.wet);
    o.set = (k, t) => {
      if (k === 'size' || k === 'damp') { try { cv.buffer = irFor(c.sampleRate, p.size, p.damp); } catch (e) { return 'rebuild'; } }
      else if (k === 'pre') smooth(pre.delayTime, p.pre, t);
      else if (k === 'mix') mx.set(p.mix, t);
    };
    o.mod = k => k === 'mix' ? mx.mod() : [];
  },

  chorus(o, c, p) {
    const mx = mkMix(c, o, p.mix), ws = o.N(c.createGain());
    ws.gain.value = 0.62; ws.connect(mx.wet);
    const B = [0.011, 0.0165, 0.0225], P = [-0.85, 0.05, 0.85], R = [1, 1.21, 0.83], oscs = [], lg = [];
    const t0 = c.currentTime;
    for (let k = 0; k < 3; k++) {
      const d = o.N(c.createDelay(0.1)); d.delayTime.value = B[k];
      const os = o.S(c.createOscillator()); os.frequency.value = p.rate * R[k];
      const g = o.N(c.createGain()); g.gain.value = p.depth * 0.0045;
      const pn = o.N(c.createStereoPanner()); pn.pan.value = P[k];
      os.connect(g); g.connect(d.delayTime);
      o.input.connect(d); d.connect(pn); pn.connect(ws);
      os.start(t0 + k * 0.11);
      oscs.push(os); lg.push(g);
    }
    o.set = (k, t) => {
      if (k === 'rate') oscs.forEach((os, i) => smooth(os.frequency, p.rate * R[i], t));
      else if (k === 'depth') lg.forEach(g => smooth(g.gain, p.depth * 0.0045, t));
      else if (k === 'mix') mx.set(p.mix, t);
    };
    o.mod = k => k === 'rate' ? oscs.map((os, i) => ({ param: os.frequency, scale: 8 * R[i] }))
      : k === 'depth' ? lg.map(g => ({ param: g.gain, scale: 0.0045 }))
      : k === 'mix' ? mx.mod() : [];
  },

  flanger(o, c, p) {
    const mx = mkMix(c, o, p.mix), d = o.N(c.createDelay(0.05)), fb = o.N(c.createGain());
    const os = o.S(c.createOscillator()), g = o.N(c.createGain());
    d.delayTime.value = 0.006; fb.gain.value = p.fb; os.type = 'triangle'; os.frequency.value = p.rate; g.gain.value = p.depth * 0.003;
    os.connect(g); g.connect(d.delayTime);
    o.input.connect(d); d.connect(fb); fb.connect(d); d.connect(mx.wet);
    os.start();
    o.set = (k, t) => {
      if (k === 'rate') smooth(os.frequency, p.rate, t);
      else if (k === 'depth') smooth(g.gain, p.depth * 0.003, t);
      else if (k === 'fb') smooth(fb.gain, p.fb, t);
      else if (k === 'mix') mx.set(p.mix, t);
    };
    o.mod = k => k === 'depth' ? [{ param: g.gain, scale: 0.003 }] : k === 'fb' ? [{ param: fb.gain, scale: 1.9 }] : k === 'mix' ? mx.mod() : [];
  },

  phaser(o, c, p) {
    const mx = mkMix(c, o, p.mix), inS = o.N(c.createGain()), aps = [];
    o.input.connect(inS);
    let n = inS;
    for (let k = 0; k < 6; k++) {
      const a = o.N(c.createBiquadFilter()); a.type = 'allpass'; a.frequency.value = p.freq * (1 + k * 0.18); a.Q.value = 0.6;
      n.connect(a); n = a; aps.push(a);
    }
    const os = o.S(c.createOscillator()), g = o.N(c.createGain());
    os.frequency.value = p.rate; g.gain.value = p.depth * 2400;
    os.connect(g); aps.forEach(a => g.connect(a.detune));
    const fb = o.N(c.createGain()), fd = o.N(c.createDelay(0.01));
    fb.gain.value = p.fb; fd.delayTime.value = 128 / c.sampleRate;
    n.connect(fb); fb.connect(fd); fd.connect(inS);
    n.connect(mx.wet);
    os.start();
    o.set = (k, t) => {
      if (k === 'rate') smooth(os.frequency, p.rate, t);
      else if (k === 'depth') smooth(g.gain, p.depth * 2400, t);
      else if (k === 'freq') aps.forEach((a, i) => smooth(a.frequency, p.freq * (1 + i * 0.18), t));
      else if (k === 'fb') smooth(fb.gain, p.fb, t);
      else if (k === 'mix') mx.set(p.mix, t);
    };
    o.mod = k => k === 'freq' ? aps.map(a => ({ param: a.detune, scale: logScale(SNAP_SPECS.phaser.params.freq) }))
      : k === 'depth' ? [{ param: g.gain, scale: 2400 }] : k === 'mix' ? mx.mod() : [];
  },

  comb(o, c, p) {
    const mx = mkMix(c, o, p.mix), d = o.N(c.createDelay(1)), dp = o.N(c.createBiquadFilter()), fb = o.N(c.createGain()), cg = o.N(c.createGain());
    dp.type = 'lowpass'; dp.Q.value = -3;
    const ap = t => {
      smooth(d.delayTime, 1 / p.freq, t); smooth(dp.frequency, 200 + (1 - p.damp) * 17800, t);
      smooth(fb.gain, p.fb, t); smooth(cg.gain, Math.pow(1 - Math.abs(p.fb), 0.6), t);
    };
    ap();
    o.input.connect(d); d.connect(dp); dp.connect(fb); fb.connect(d); d.connect(cg); cg.connect(mx.wet);
    o.set = (k, t) => k === 'mix' ? mx.set(p.mix, t) : ap(t);
    o.mod = k => k === 'fb' ? [{ param: fb.gain, scale: 1.94 }] : k === 'mix' ? mx.mod() : [];
  },

  gate(o, c, p, synth) {
    const mx = mkMix(c, o, p.mix), vca = o.N(c.createGain()), dg = o.N(c.createGain());
    vca.gain.value = 1 - p.depth; dg.gain.value = p.depth;
    o.input.connect(vca); vca.connect(mx.wet); dg.connect(vca.gain);
    const REF = 120;
    let buf = null, src = null, t0 = c.currentTime;
    const build = () => {
      const sr = c.sampleRate, step = DIVS[p.div] * 60 / REF, n = Math.max(32, Math.round(step * 16 * sr));
      const d = new Float32Array(n), per = n / 16, on = Math.max(2, Math.floor(per * p.len));
      const ramp = Math.max(1, Math.floor(on * 0.5 * p.smooth));
      for (let s = 0; s < 16; s++) {
        if (p.pattern[s] !== 'x') continue;
        const a = Math.floor(s * per);
        for (let i = 0; i < on && a + i < n; i++) d[a + i] = Math.min(1, (i + 1) / ramp, (on - i) / ramp);
      }
      return mkBuf(sr, [d]);
    };
    const start = (t, off) => {
      const s = c.createBufferSource(); s.buffer = buf; s.loop = true; s.playbackRate.value = synth.bpm / REF;
      s.connect(dg); s.start(t, off || 0);
      o.srcs.push(s); o.nodes.push(s);
      return s;
    };
    const swap = (t, keepPhase) => {
      const old = src;
      const off = keepPhase ? (((t - t0) * synth.bpm / REF) % buf.duration + buf.duration) % buf.duration : 0;
      src = start(t, off);
      if (old) {
        try { old.stop(t); } catch (e) { /* fine */ }
        const drop = a => { const i = a.indexOf(old); if (i >= 0) a.splice(i, 1); };
        drop(o.srcs); drop(o.nodes);
        setTimeout(() => { try { old.disconnect(); } catch (e) { /* ok */ } }, 2000);
      }
    };
    buf = build();
    src = start(t0, 0);
    o.set = (k, t) => {
      if (k === 'depth') { smooth(vca.gain, 1 - p.depth, t); smooth(dg.gain, p.depth, t); }
      else if (k === 'mix') mx.set(p.mix, t);
      else { buf = build(); swap(t == null ? c.currentTime : t, true); }
    };
    o.tempo = t => smooth(src.playbackRate, synth.bpm / REF, t);
    o.sync = t => { t0 = t; swap(t, false); };
    o.mod = k => k === 'depth' ? [{ param: dg.gain, scale: 1 }, { param: vca.gain, scale: -1 }] : k === 'mix' ? mx.mod() : [];
  },

  comp(o, c, p) {
    const mx = mkMix(c, o, p.mix), cp = o.N(c.createDynamicsCompressor()), mk = o.N(c.createGain());
    cp.knee.value = 6;
    const ap = t => {
      smooth(cp.threshold, p.thresh, t); smooth(cp.ratio, p.ratio, t); smooth(cp.attack, p.attack, t);
      smooth(cp.release, p.release, t); smooth(mk.gain, dbToLin(p.makeup), t);
    };
    ap();
    o.input.connect(cp); cp.connect(mk); mk.connect(mx.wet);
    o.set = (k, t) => k === 'mix' ? mx.set(p.mix, t) : ap(t);
    o.mod = k => k === 'thresh' ? [{ param: cp.threshold, scale: 60 }] : k === 'mix' ? mx.mod() : [];
  },

  eq(o, c, p) {
    const lo = o.N(c.createBiquadFilter()), md = o.N(c.createBiquadFilter()), hi = o.N(c.createBiquadFilter());
    lo.type = 'lowshelf'; md.type = 'peaking'; hi.type = 'highshelf';
    const ap = t => {
      smooth(lo.frequency, p.lowf, t); smooth(lo.gain, p.low, t);
      smooth(md.frequency, p.midf, t); smooth(md.gain, p.mid, t); smooth(md.Q, 0.3 * Math.pow(2, p.midq * 5), t);
      smooth(hi.frequency, p.highf, t); smooth(hi.gain, p.high, t);
    };
    ap();
    o.input.connect(lo); lo.connect(md); md.connect(hi); hi.connect(o.output);
    o.set = (k, t) => ap(t);
    o.mod = k => k === 'low' ? [{ param: lo.gain, scale: 36 }] : k === 'mid' ? [{ param: md.gain, scale: 36 }]
      : k === 'high' ? [{ param: hi.gain, scale: 36 }]
      : k === 'midf' ? [{ param: md.detune, scale: logScale(SNAP_SPECS.eq.params.midf) }] : [];
  },

  width(o, c, p) {
    o.input.channelCount = 2; o.input.channelCountMode = 'explicit'; o.input.channelInterpretation = 'speakers';
    const sp = o.N(c.createChannelSplitter(2)), mg = o.N(c.createChannelMerger(2));
    const g = v => { const n = o.N(c.createGain()); n.gain.value = v; return n; };
    const lM = g(0.5), rM = g(0.5), lS = g(0.5), rS = g(-0.5), W = g(p.width), inv = g(-1);
    o.input.connect(sp);
    sp.connect(lM, 0); sp.connect(rM, 1); sp.connect(lS, 0); sp.connect(rS, 1);
    lS.connect(W); rS.connect(W);
    lM.connect(mg, 0, 0); rM.connect(mg, 0, 0); lM.connect(mg, 0, 1); rM.connect(mg, 0, 1);
    W.connect(mg, 0, 0); W.connect(inv); inv.connect(mg, 0, 1);
    mg.connect(o.output);
    o.set = (k, t) => smooth(W.gain, p.width, t);
    o.mod = k => k === 'width' ? [{ param: W.gain, scale: 2 }] : [];
  },

  ring(o, c, p) {
    const mx = mkMix(c, o, p.mix), vca = o.N(c.createGain()), os = o.S(c.createOscillator());
    vca.gain.value = 0; os.frequency.value = p.freq;
    os.connect(vca.gain); o.input.connect(vca); vca.connect(mx.wet);
    os.start();
    o.set = (k, t) => k === 'freq' ? smooth(os.frequency, p.freq, t) : mx.set(p.mix, t);
    o.mod = k => k === 'freq' ? [{ param: os.detune, scale: logScale(SNAP_SPECS.ring.params.freq) }] : k === 'mix' ? mx.mod() : [];
  },

  tape(o, c, p) {
    const mx = mkMix(c, o, p.mix);
    const pre = o.N(c.createGain()), sh = o.N(c.createWaveShaper()), post = o.N(c.createGain());
    const d = o.N(c.createDelay(0.1)), age = o.N(c.createBiquadFilter()), bump = o.N(c.createBiquadFilter());
    sh.curve = shaperCurve('soft'); sh.oversample = '2x';
    d.delayTime.value = 0.012;
    age.type = 'lowpass'; age.Q.value = -3;
    bump.type = 'peaking'; bump.frequency.value = 95; bump.Q.value = 0.8;
    const wo = o.S(c.createOscillator()), fo = o.S(c.createOscillator()), wg = o.N(c.createGain()), fg = o.N(c.createGain());
    wo.frequency.value = 0.55; fo.frequency.value = 7.3;
    wo.connect(wg); fo.connect(fg); wg.connect(d.delayTime); fg.connect(d.delayTime);
    const hs = o.S(c.createBufferSource()), hp = o.N(c.createBiquadFilter()), hg = o.N(c.createGain());
    hs.buffer = bufsFor(c.sampleRate).getNoise('pink'); hs.loop = true;
    hp.type = 'highpass'; hp.frequency.value = 1800;
    hs.connect(hp); hp.connect(hg); hg.connect(mx.wet);
    o.input.connect(pre); pre.connect(sh); sh.connect(post); post.connect(bump); bump.connect(d); d.connect(age); age.connect(mx.wet);
    const ap = t => {
      const g = 1 + p.sat * 5;
      smooth(pre.gain, g / SHAPE_K, t); smooth(post.gain, 1 / (1 + p.sat * 1.6), t); smooth(bump.gain, p.sat * 3, t);
      smooth(wg.gain, p.wow * 0.0032, t); smooth(fg.gain, p.flutter * 0.00035, t);
      smooth(age.frequency, 18000 * Math.pow(0.12, p.age), t); smooth(hg.gain, p.hiss * p.hiss * 0.05, t);
    };
    ap();
    const t0 = c.currentTime;
    wo.start(t0); fo.start(t0); hs.start(t0, Math.random());
    o.set = (k, t) => k === 'mix' ? mx.set(p.mix, t) : ap(t);
    o.mod = k => k === 'wow' ? [{ param: wg.gain, scale: 0.0032 }]
      : k === 'age' ? [{ param: age.detune, scale: -1200 * Math.log2(1 / 0.12) }]
      : k === 'mix' ? mx.mod() : [];
  },
};

// ═══════════════════════════════════════════════════════════════════
// ForgeSynth — the engine
// ═══════════════════════════════════════════════════════════════════
class ForgeSynth {
  constructor(ctx, opts = {}) {
    if (!ctx) throw new Error('ForgeSynth needs an AudioContext');
    this.ctx = ctx;
    this.maxVoices = clamp(Math.round(opts.maxVoices || 12), 1, 64);
    this._bpm = isNum(opts.bpm) ? clamp(opts.bpm, 20, 400) : 120;
    this.voices = [];
    this._ls = {};
    this._uid = 0;
    this._sus = false; this._susNotes = new Set();
    this._monoStack = []; this._mono = null; this._lead = null; this._lastNote = null;
    this._monoEv = []; this._monoBase = { stack: [], last: null }; this._monoVoices = [];
    this._worklet = false; this._disposed = false; this._inited = false;
    this._editors = new Set();
    this._pend = new Set();
    this._gRoutes = {}; this._gLinks = [];
    this._presetId = null;
    this.output = ctx.createGain();
    this._dest = opts.output || ctx.destination;
    this.output.connect(this._dest);
    this._buildStatic();
    this.state = normalizeState(DEFAULT_STATE);
    this._applyStateGraph();
  }

  // ── lifecycle ────────────────────────────────────────────────────
  async init() {
    if (this._inited) return this;
    try { await loadWorklet(this.ctx); this._worklet = true; } catch (e) { this._worklet = false; }
    this._inited = true;
    if (this._worklet && this._usesCrush()) { this._rebuildLanes(); this._rebuildGlobalRoutes(); }
    await this.loaded();
    return this;
  }
  loaded() { return Promise.all([...this._pend]).then(() => this); }
  dispose() {
    if (this._disposed) return;
    this.panic();
    [...this._editors].forEach(e => e.destroy());
    this._disposed = true;
    for (const L of LANES) for (const id in this._lanes[L].objs) this._lanes[L].objs[id].dispose();
    this._stopGlobalLfos();
    this._clearGlobalRoutes();
    for (const k in this._gsrc) { const n = this._gsrc[k]; if (n.stop) { try { n.stop(); } catch (e) { /* ok */ } } try { n.disconnect(); } catch (e) { /* ok */ } }
    const later = () => this.voices.slice().forEach(v => this._cleanup(v));
    if (typeof setTimeout === 'function') setTimeout(later, 60); else later();
    for (const k in this._master) { try { this._master[k].disconnect(); } catch (e) { /* ok */ } }
    for (const L of LANES) { try { this._lanes[L].input.disconnect(); this._lanes[L].gain.disconnect(); } catch (e) { /* ok */ } }
    try { this.output.disconnect(); } catch (e) { /* ok */ }
    this._ls = {};
  }

  // ── events: 'state' | 'change' | 'macro' | 'mods' | 'note' | 'cc' ──
  on(type, fn) { (this._ls[type] = this._ls[type] || new Set()).add(fn); return () => this.off(type, fn); }
  off(type, fn) { if (this._ls[type]) this._ls[type].delete(fn); }
  _emit(type, detail) { const s = this._ls[type]; if (s) for (const fn of [...s]) { try { fn(detail); } catch (e) { console.error(e); } } }

  // ── tempo ────────────────────────────────────────────────────────
  get bpm() { return this._bpm; }
  set bpm(v) {
    if (!isNum(v)) return;
    this._bpm = clamp(v, 20, 400);
    const t = this.ctx.currentTime;
    for (const k in this._glfo) { const L = this._glfo[k]; if (L.cfg.sync) smooth(L.rateParam, this._lfoRate(L.cfg), t); }
    for (const v2 of this.voices) for (const k in v2.lfos) { const L = v2.lfos[k]; if (L.cfg.sync) smooth(L.rateParam, this._lfoRate(L.cfg), t); }
    for (const L of LANES) for (const id in this._lanes[L].objs) this._lanes[L].objs[id].tempo(t);
  }
  // Restart tempo-synced global things (global LFOs, trance gates) on a bar line.
  syncAt(when) {
    const t = this._t(when);
    this._buildGlobalLfos(t, true);
    for (const L of LANES) for (const id in this._lanes[L].objs) this._lanes[L].objs[id].sync(t);
    this._rebuildGlobalRoutes();
  }
  get activeVoices() { const t = this.ctx.currentTime; return this.voices.filter(v => v.end > t && v.t0 <= t + 0.2).length; }

  // ── presets / state ─────────────────────────────────────────────
  get presetList() { return FORGE_PRESETS.map(p => ({ id: p.id, name: p.name, category: p.category })); }
  get presetId() { return this._presetId; }
  loadPreset(id) {
    const p = FORGE_PRESETS.find(x => x.id === id);
    if (!p) return false;
    this.setState(Object.assign({}, p.state, { name: p.name, category: p.category }));
    this._presetId = id;
    return true;
  }
  getState() { const s = clone(this.state); s.v = 1; return s; }
  setState(json) {
    let src = json;
    if (typeof src === 'string') { try { src = JSON.parse(src); } catch (e) { return false; } }
    this.allOff();
    this._presetId = null;
    this.state = normalizeState(src);
    this._monoReset();
    this._applyStateGraph();
    this._emit('state', this.state);
    this._emit('change', { path: '*' });
    return true;
  }

  // ── playing ─────────────────────────────────────────────────────
  _t(when) { const now = this.ctx.currentTime; return (when == null || !isFinite(when)) ? now : Math.max(now, when); }
  noteOn(note, vel = 0.8, when) {
    if (this._disposed) return;
    note = clamp(Math.round(note), 0, 127);
    vel = clamp(isNum(vel) ? vel : 0.8, 0, 1);
    const t = this._t(when);
    if (vel <= 0) { this.noteOff(note, when); return; }
    this._susNotes.delete(note);
    if (this.state.voice.mode !== 'poly') { this._monoOn(note, vel, t); this._emit('note', { note, vel, on: true, t }); return; }
    for (const v of this.voices) if (v.note === note && !v.rel) this._releaseVoice(v, t);
    this._prune(t);
    while (this.voices.length >= this.maxVoices) {
      const rel = this.voices.filter(v => v.rel);
      const pool = rel.length ? rel : this.voices;
      let old = pool[0];
      for (const v of pool) if (v.t0 < old.t0) old = v;
      this._killVoice(old, t);
      this.voices.splice(this.voices.indexOf(old), 1);
    }
    const v = this._startVoice(note, vel, t);
    this.voices.push(v);
    this._setLead(v, t);
    this._lastNote = note;
    this._emit('note', { note, vel, on: true, t });
  }
  noteOff(note, when) {
    if (this._disposed) return;
    note = clamp(Math.round(note), 0, 127);
    const t = this._t(when);
    if (this._sus) { this._susNotes.add(note); return; }
    this._noteOff(note, t);
  }
  _noteOff(note, t) {
    if (this.state.voice.mode !== 'poly') this._monoOff(note, t);
    else for (const v of this.voices) if (v.note === note && !v.rel) this._releaseVoice(v, t);
    this._emit('note', { note, on: false, t });
  }
  allOff(when) {
    const t = this._t(when);
    this._susNotes.clear(); this._sus = false;
    for (const v of this.voices) this._releaseVoice(v, t);
    this._monoReset();
    this._emit('note', { all: true, on: false, t });
  }
  panic() {
    const t = this.ctx.currentTime;
    this._susNotes.clear(); this._sus = false;
    for (const v of this.voices) this._killVoice(v, t);
    this.voices = [];
    this._monoReset();
  }
  cc(num, value01, when) {
    const t = this._t(when), v = clamp(isNum(value01) ? value01 : 0, 0, 1);
    num = num | 0;
    if (num === 1) this._gsrc.mw.offset.setTargetAtTime(v, t, 0.004);
    else if (num === 64) this._sustain(v >= 0.5, t);
    else if (num === 120 || num === 123) this.allOff(when);
    const map = this.state.ccMap[num];
    if (map === 'mw') this._gsrc.mw.offset.setTargetAtTime(v, t, 0.004);
    else if (map) { const m = /^m([1-8])$/.exec(map); if (m) this.setMacro(+m[1] - 1, v, when); }
    this._emit('cc', { num, value: v, t });
  }
  pitchBend(norm, when) {
    const t = this._t(when);
    this._gsrc.pb.offset.setTargetAtTime(clamp(isNum(norm) ? norm : 0, -1, 1), t, 0.003);
  }
  setMacro(i, value01, when) {
    i = i | 0; if (i < 0 || i > 7) return;
    const v = clamp(isNum(value01) ? value01 : 0, 0, 1), t = this._t(when);
    this.state.macros[i].value = v;
    this._gsrc['m' + (i + 1)].offset.setTargetAtTime(v, t, 0.004);
    this._emit('macro', { i, value: v });
  }
  _sustain(down, t) {
    if (down) { this._sus = true; return; }
    this._sus = false;
    const notes = [...this._susNotes]; this._susNotes.clear();
    notes.forEach(n => this._noteOff(n, t));
  }

  // ── editing API (the editor and the DAW use these) ───────────────
  getParam(path) {
    const r = this._resolve(path);
    return r ? r.obj[r.key] : undefined;
  }
  setParam(path, value, when) {
    const r = this._resolve(path);
    if (!r) return false;
    const spec = r.spec;
    const v = spec ? normField(value, spec) : value;
    r.obj[r.key] = v;
    const t = when === undefined ? this.ctx.currentTime : this._t(when);
    this._live(r, v, t);
    this._emit('change', { path, value: v });
    return true;
  }
  _resolve(path) {
    if (typeof path !== 'string') return null;
    const p = path.split('.'), S = this.state;
    switch (p[0]) {
      case 'gen': { const g = S.gens.find(x => x.id === p[1]); if (!g || !(p[2] in GEN_SPEC)) return null; return { kind: 'gen', g, obj: g, key: p[2], spec: GEN_SPEC[p[2]] }; }
      case 'filter': return (p[1] in FILTER_SPEC) ? { kind: 'filter', obj: S.filter, key: p[1], spec: FILTER_SPEC[p[1]] } : null;
      case 'amp': return (p[1] in ENV_SPEC) ? { kind: 'amp', obj: S.amp, key: p[1], spec: ENV_SPEC[p[1]] } : null;
      case 'voice': return (p[1] in VOICE_SPEC) ? { kind: 'voice', obj: S.voice, key: p[1], spec: VOICE_SPEC[p[1]] } : null;
      case 'master': return (p[1] in MASTER_SPEC) ? { kind: 'master', obj: S.master, key: p[1], spec: MASTER_SPEC[p[1]] } : null;
      case 'env': { const e = S.envs[(+p[1]) - 1]; return (e && p[2] in ENV_SPEC) ? { kind: 'env', obj: e, key: p[2], spec: ENV_SPEC[p[2]] } : null; }
      case 'lfo': { const n = +p[1], l = S.lfos[n - 1]; return (l && p[2] in LFO_SPEC) ? { kind: 'lfo', n, obj: l, key: p[2], spec: LFO_SPEC[p[2]] } : null; }
      case 'macro': { const m = S.macros[(+p[1]) - 1]; if (!m) return null; return p[2] === 'name' ? { kind: 'macroname', obj: m, key: 'name', spec: { str: true, def: 'MACRO' } } : p[2] === 'value' ? { kind: 'macro', i: (+p[1]) - 1, obj: m, key: 'value', spec: MACRO_SPEC } : null; }
      case 'lane': { const l = S.lanes[p[1]]; if (!l) return null; return p[2] === 'gain' ? { kind: 'lane', L: p[1], obj: l, key: 'gain', spec: LANE_SPEC.gain } : p[2] === 'to' ? { kind: 'laneto', L: p[1], obj: l, key: 'to', spec: { opts: ['master', ...LANES.slice(LANES.indexOf(p[1]) + 1)], def: 'master' } } : null; }
      case 'fx': { const f = this._fx(p[1]); if (!f) return null; if (p[2] === 'on') return { kind: 'fxon', f, obj: f.f, key: 'on', spec: { bool: true, def: true } }; const sp = SNAP_SPECS[f.f.type].params[p[2]]; return sp ? { kind: 'fx', f, obj: f.f.p, key: p[2], spec: sp } : null; }
      case 'mod': { const m = S.mods.find(x => x.id === p[1]); if (!m) return null; if (p[2] === 'depth') return { kind: 'moddepth', m, obj: m, key: 'depth', spec: { min: -1, max: 1, def: 0 } }; if (p[2] === 'on') return { kind: 'modon', m, obj: m, key: 'on', spec: { bool: true, def: true } }; if (p[2] === 'src') return { kind: 'modsrc', m, obj: m, key: 'src', spec: { opts: SOURCE_IDS, def: m.src } }; return null; }
      case 'cc': { const n = parseInt(p[1], 10); if (!(n >= 0 && n < 128)) return null; return { kind: 'cc', obj: S.ccMap, key: n, spec: { opts: ['', 'mw', 'm1', 'm2', 'm3', 'm4', 'm5', 'm6', 'm7', 'm8'], def: '' } }; }
      case 'name': return { kind: 'name', obj: S, key: 'name', spec: { str: true, def: 'INIT' } };
    }
    return null;
  }
  _fx(id) {
    for (const L of LANES) { const f = this.state.lanes[L].fx.find(x => x.id === id); if (f) return { L, f, obj: this._lanes[L].objs[id] }; }
    return null;
  }
  // Apply a changed value to the running graph where it makes sense; the
  // rest takes effect on the next note.
  _live(r, v, t) {
    const S = this.state;
    switch (r.kind) {
      case 'gen': {
        const g = r.g, k = r.key;
        for (const vc of this.voices) {
          const vg = vc.gens[g.id]; if (!vg) continue;
          if (k === 'level') smooth(vg.gain.gain, g.level, t);
          else if (k === 'coarse' || k === 'fine' || k === 'detune') vg.det.forEach((p, i) => smooth(p, g.coarse * 100 + g.fine + vg.detPos[i] * g.detune, t));
          else if (k === 'pan' || k === 'spread') vg.pan.forEach((p, i) => smooth(p, clamp(g.pan + vg.panPos[i] * g.spread, -1, 1), t));
          else if (k === 'morph') { vg.wa.forEach(p => smooth(p, 1 - g.morph, t)); vg.wb.forEach(p => smooth(p, g.morph, t)); }
          else if (k === 'fmAmt' && vg.fmGain) smooth(vg.fmGain.gain, g.fmAmt * FM_MAX_INDEX * vg.hz, t);
          else if (k === 'nfreq' && vg.nf) smooth(vg.nf.frequency, g.nfreq, t);
          else if (k === 'nres' && vg.nf) smooth(vg.nf.Q, resQ(g.nfilt, g.nres), t);
          else if ((k === 'ratio' || k === 'hz') && vg.freq.length) { const hz = g.mode === 'fixed' ? g.hz : mtof(vc.baseNote) * g.ratio; vg.freq.forEach(p => smooth(p, hz, t)); }
        }
        if (k === 'type' || k === 'lane') this._emit('mods', {});
        break;
      }
      case 'filter': {
        const k = r.key;
        for (const vc of this.voices) for (const f of vc.filters) {
          if (k === 'cutoff') smooth(f.frequency, S.filter.cutoff, t);
          else if (k === 'res') smooth(f.Q, resQ(f.type, S.filter.res), t);
          else if (k === 'gain') smooth(f.gain, S.filter.gain, t);
          else if (k === 'key') smooth(f.detune, S.filter.key * (vc.note - 60) * 100, t);
        }
        break;
      }
      case 'voice': if (r.key === 'mode') this.allOff(t); break;
      case 'master': if (r.key === 'gain') smooth(this._master.gain.gain, v, t); else this._applyMaster(); break;
      case 'lfo': {
        const k = r.key, cfg = r.obj;
        const G = this._glfo[r.n];
        if (k === 'rate' || k === 'sync' || k === 'div') {
          if (G) smooth(G.rateParam, this._lfoRate(cfg), t);
          for (const vc of this.voices) { const L = vc.lfos[r.n]; if (L) smooth(L.rateParam, this._lfoRate(cfg), t); }
        } else if (k === 'amount') {
          if (G) smooth(G.out.gain, cfg.amount, t);
          for (const vc of this.voices) { const L = vc.lfos[r.n]; if (L) smooth(L.out.gain, cfg.amount, t); }
        } else if (k === 'shape' || k === 'uni' || k === 'retrig') { this._buildGlobalLfos(); this._rebuildGlobalRoutes(); }
        break;
      }
      case 'macro': this._gsrc['m' + (r.i + 1)].offset.setTargetAtTime(v, t, 0.004); this._emit('macro', { i: r.i, value: v }); break;
      case 'lane': smooth(this._lanes[r.L].gain.gain, v, t); break;
      case 'laneto': r.obj.to = validTo(r.L, v); this._relink(); break;
      case 'fxon': this._relink(); break;
      case 'fx': {
        const spec = SNAP_SPECS[r.f.f.type];
        const res = (spec.structural && spec.structural.includes(r.key)) ? 'rebuild' : (r.f.obj ? r.f.obj.set(r.key, t) : 'rebuild');
        if (res === 'rebuild') this._rebuildSnap(r.f.f.id);
        break;
      }
      case 'moddepth': this._liveDepth(r.m, t); break;
      case 'modon': case 'modsrc': this._rebuildGlobalRoutes(); this._emit('mods', {}); break;
      case 'cc': if (!v) delete this.state.ccMap[r.key]; break;
    }
  }

  addGenerator(type = 'analog', init) {
    const S = this.state;
    if (S.gens.length >= MAX_GENS || !GEN_TYPES[type]) return null;
    const used = new Set(S.gens.map(g => g.id));
    const g = normObj(Object.assign({ type, level: type === 'fm' ? 0 : 0.6 }, init || {}), GEN_SPEC);
    if (type === 'fm' && !g.fmTarget) { const t = S.gens.find(x => x.type !== 'fm' && x.type !== 'noise' && x.type !== 'sample'); g.fmTarget = t ? t.id : ''; }
    const id = nextId('g', used);
    S.gens.push(Object.assign({ id }, g));
    this._changed();
    return id;
  }
  removeGenerator(id) {
    const S = this.state, i = S.gens.findIndex(g => g.id === id);
    if (i < 0) return false;
    S.gens.splice(i, 1);
    S.gens.forEach(g => { if (g.fmTarget === id) g.fmTarget = ''; });
    S.mods = S.mods.filter(m => !m.dst.startsWith('gen.' + id + '.'));
    this._rebuildGlobalRoutes();
    this._changed();
    return true;
  }
  moveGenerator(id, delta) {
    const a = this.state.gens, i = a.findIndex(g => g.id === id), j = i + delta;
    if (i < 0 || j < 0 || j >= a.length) return false;
    [a[i], a[j]] = [a[j], a[i]];
    this._changed();
    return true;
  }
  addSnapin(lane, type, params) {
    const S = this.state, l = S.lanes[lane];
    if (!l || !SNAP_SPECS[type] || l.fx.length >= MAX_FX_PER_LANE) return null;
    const used = new Set(); LANES.forEach(L => S.lanes[L].fx.forEach(f => used.add(f.id)));
    const f = normSnap({ type, p: params || {} }, used);
    f.id = nextId('s', used);
    l.fx.push(f);
    this._lanes[lane].objs[f.id] = buildSnap(this, f);
    this._relink();
    this._rebuildGlobalRoutes();
    this._changed();
    return f.id;
  }
  removeSnapin(id) {
    const r = this._fx(id); if (!r) return false;
    const l = this.state.lanes[r.L];
    l.fx.splice(l.fx.indexOf(r.f), 1);
    if (r.obj) { r.obj.dispose(); delete this._lanes[r.L].objs[id]; }
    this.state.mods = this.state.mods.filter(m => !m.dst.startsWith('fx.' + id + '.'));
    this._relink();
    this._rebuildGlobalRoutes();
    this._changed();
    return true;
  }
  moveSnapin(id, delta) {
    const r = this._fx(id); if (!r) return false;
    const a = this.state.lanes[r.L].fx, i = a.indexOf(r.f), j = i + delta;
    if (j < 0 || j >= a.length) return false;
    [a[i], a[j]] = [a[j], a[i]];
    this._relink();
    this._changed();
    return true;
  }
  addMod(src, dst, depth = 0.25) {
    if (!SOURCE_IDS.includes(src) || typeof dst !== 'string' || !DST_RX.test(dst)) return null;
    const S = this.state;
    const ex = S.mods.find(m => m.src === src && m.dst === dst);
    if (ex) return ex.id;
    if (S.mods.length >= 64) return null;
    const id = nextId('r', new Set(S.mods.map(m => m.id)));
    S.mods.push({ id, src, dst, depth: clamp(isNum(depth) ? depth : 0.25, -1, 1), on: true });
    this._rebuildGlobalRoutes();
    this._emit('mods', {});
    this._emit('change', { path: 'mods' });
    return id;
  }
  removeMod(id) {
    const S = this.state, i = S.mods.findIndex(m => m.id === id);
    if (i < 0) return false;
    const m = S.mods[i];
    S.mods.splice(i, 1);
    m.depth = 0; this._liveDepth(m, this.ctx.currentTime);
    this._rebuildGlobalRoutes();
    this._emit('mods', {});
    this._emit('change', { path: 'mods' });
    return true;
  }
  setModDepth(id, depth, when) { return this.setParam('mod.' + id + '.depth', depth, when); }
  _changed() { this._emit('change', { path: '*', structure: true }); }

  // Labels for every modulation target that exists in the current patch.
  modTargets() {
    const S = this.state, out = [{ id: 'voice.pitch', label: 'VOICE · PITCH' }];
    S.gens.forEach((g, i) => {
      const n = 'GEN ' + (i + 1) + ' ' + GEN_TYPES[g.type] + ' · ';
      out.push({ id: `gen.${g.id}.level`, label: n + 'LEVEL' }, { id: `gen.${g.id}.pan`, label: n + 'PAN' });
      if (g.type !== 'noise') out.push({ id: `gen.${g.id}.pitch`, label: n + 'PITCH' });
      if (g.type === 'wavetable') out.push({ id: `gen.${g.id}.morph`, label: n + 'POSITION' });
      if (g.type === 'fm') out.push({ id: `gen.${g.id}.fm`, label: n + 'FM AMOUNT' });
      if (g.type === 'noise') out.push({ id: `gen.${g.id}.cutoff`, label: n + 'CUTOFF' });
    });
    out.push({ id: 'filter.cutoff', label: 'FILTER · CUTOFF' }, { id: 'filter.res', label: 'FILTER · RES' }, { id: 'amp.level', label: 'AMP · LEVEL' });
    for (let n = 1; n <= 3; n++) out.push({ id: `lfo.${n}.amount`, label: `LFO ${n} · AMOUNT` }, { id: `lfo.${n}.rate`, label: `LFO ${n} · RATE` });
    for (const L of LANES) {
      out.push({ id: `lane.${L}.gain`, label: `LANE ${L} · GAIN` });
      S.lanes[L].fx.forEach(f => { const sp = SNAP_SPECS[f.type]; sp.mods.forEach(k => out.push({ id: `fx.${f.id}.${k}`, label: `LANE ${L} · ${sp.label} · ${sp.params[k].label}` })); });
    }
    out.push({ id: 'master.gain', label: 'MASTER · GAIN' });
    return out;
  }
  modSources() { return SOURCES.map(s => Object.assign({}, s, s.id[0] === 'm' && s.id !== 'mw' ? { label: this.state.macros[+s.id.slice(1) - 1].name } : {})); }
  // Fraction of a knob's sweep that depth 1.0 covers (for drawing rings).
  _disp(dst) {
    if (/pitch$/.test(dst)) return 0.5;
    if (/^(lane\.\w\.gain|master\.gain)$/.test(dst)) return 1 / 1.5;
    if (/^lfo\.\d\.rate$/.test(dst)) return 0.4;
    return 1;
  }

  // ── static graph ────────────────────────────────────────────────
  _buildStatic() {
    const c = this.ctx;
    const m = this._master = { in: c.createGain(), gain: c.createGain(), pre: c.createGain(), clip: c.createWaveShaper() };
    m.pre.gain.value = 0.25;
    m.clip.curve = LIMIT_CURVE; m.clip.oversample = '2x';
    m.in.connect(m.gain); m.pre.connect(m.clip); m.clip.connect(this.output);
    this._lanes = {};
    for (const L of LANES) this._lanes[L] = { input: c.createGain(), gain: c.createGain(), objs: {} };
    this._gsrc = {};
    const cs = v => { const n = c.createConstantSource(); n.offset.value = v; n.start(); return n; };
    this._gsrc.mw = cs(0); this._gsrc.pb = cs(0);
    for (let i = 1; i <= 8; i++) this._gsrc['m' + i] = cs(0);
    this._glfo = {};
  }
  _applyStateGraph() {
    const S = this.state;
    for (let i = 0; i < 8; i++) this._gsrc['m' + (i + 1)].offset.value = S.macros[i].value;
    this._buildGlobalLfos();
    this._rebuildLanes();
    this._applyMaster();
    this._rebuildGlobalRoutes();
    this._preloadSamples();
  }
  _applyMaster() {
    const m = this._master;
    m.gain.gain.value = this.state.master.gain;
    try { m.gain.disconnect(); } catch (e) { /* ok */ }
    m.gain.connect(this.state.master.limit ? m.pre : this.output);
  }
  _usesCrush() { return LANES.some(L => this.state.lanes[L].fx.some(f => f.type === 'dist' && (f.p.mode === 'bitcrush' || f.p.mode === 'downsample'))); }
  _rebuildLanes() {
    for (const L of LANES) { const ln = this._lanes[L]; for (const id in ln.objs) ln.objs[id].dispose(); ln.objs = {}; }
    for (const L of LANES) {
      const ln = this._lanes[L];
      for (const f of this.state.lanes[L].fx) ln.objs[f.id] = buildSnap(this, f);
      ln.gain.gain.value = this.state.lanes[L].gain;
    }
    this._relink();
  }
  _rebuildSnap(id) {
    const r = this._fx(id); if (!r) return;
    if (r.obj) r.obj.dispose();
    this._lanes[r.L].objs[id] = buildSnap(this, r.f);
    this._relink();
    this._rebuildGlobalRoutes();
  }
  _relink() {
    for (const L of LANES) {
      const ln = this._lanes[L];
      try { ln.input.disconnect(); } catch (e) { /* ok */ }
      for (const id in ln.objs) { try { ln.objs[id].output.disconnect(); } catch (e) { /* ok */ } }
      try { ln.gain.disconnect(); } catch (e) { /* ok */ }
    }
    for (const L of LANES) {
      const ln = this._lanes[L], st = this.state.lanes[L];
      let n = ln.input;
      for (const f of st.fx) { const o = ln.objs[f.id]; if (!o || !f.on) continue; n.connect(o.input); n = o.output; }
      n.connect(ln.gain);
      st.to = validTo(L, st.to);
      ln.gain.connect(st.to === 'master' ? this._master.in : this._lanes[st.to].input);
    }
  }

  // ── LFOs ────────────────────────────────────────────────────────
  _lfoRate(cfg) { return cfg.sync ? (this._bpm / 60) / (DIVS[cfg.div] || 1) : cfg.rate; }
  _mkLfo(cfg, t, perVoice) {
    const c = this.ctx, nodes = [], srcs = [];
    const hz = this._lfoRate(cfg);
    let node, rateParam, rateScale, off = 0;
    if (cfg.shape === 'sh') {
      node = c.createBufferSource(); node.buffer = bufsFor(c.sampleRate).sh; node.loop = true;
      node.playbackRate.value = hz / 64; rateParam = node.playbackRate; rateScale = 20 / 64; off = Math.random();
    } else {
      node = c.createOscillator();
      node.type = { sine: 'sine', triangle: 'triangle', saw: 'sawtooth', ramp: 'sawtooth', square: 'square' }[cfg.shape] || 'sine';
      node.frequency.value = hz; rateParam = node.frequency; rateScale = 20;
    }
    nodes.push(node); srcs.push([node, t, off]);
    const pol = c.createGain(); pol.gain.value = (cfg.shape === 'ramp' ? -1 : 1) * (cfg.uni ? 0.5 : 1);
    node.connect(pol); nodes.push(pol);
    const out = c.createGain(); nodes.push(out); pol.connect(out);
    if (cfg.uni) { const o = c.createConstantSource(); o.offset.value = 0.5; o.connect(out); nodes.push(o); srcs.push([o, t, 0]); }
    if (perVoice && cfg.fade > 0.001) { out.gain.setValueAtTime(0, t); out.gain.linearRampToValueAtTime(cfg.amount, t + cfg.fade); }
    else out.gain.value = cfg.amount;
    return { node, out, rateParam, rateScale, nodes, srcs, cfg };
  }
  _stopGlobalLfos(t) {
    for (const k in this._glfo) {
      const L = this._glfo[k];
      L.srcs.forEach(([s]) => { try { s.stop(t); } catch (e) { /* ok */ } });
      const kill = () => L.nodes.forEach(n => { try { n.disconnect(); } catch (e) { /* ok */ } });
      if (t && t > this.ctx.currentTime && typeof setTimeout === 'function') setTimeout(kill, (t - this.ctx.currentTime) * 1000 + 100); else kill();
    }
    this._glfo = {};
    for (let i = 1; i <= 3; i++) delete this._gsrc['lfo' + i];
  }
  _buildGlobalLfos(t, atTime) {
    const start = atTime ? t : this.ctx.currentTime;
    this._stopGlobalLfos(atTime ? t : undefined);
    this.state.lfos.forEach((cfg, i) => {
      if (cfg.retrig) return;
      const L = this._mkLfo(cfg, start, false);
      L.srcs.forEach(([s, st, off]) => s.start(st, off));
      this._glfo[i + 1] = L;
      this._gsrc['lfo' + (i + 1)] = L.out;
    });
  }

  // ── routing ─────────────────────────────────────────────────────
  _routes() {
    const S = this.state, rs = [];
    for (const m of S.mods) if (m.on !== false && m.depth) rs.push(m);
    if (S.filter.on && S.filter.env) rs.push({ id: '_fenv', src: 'env2', dst: 'filter.cutoff', depth: S.filter.env });
    if (S.voice.bend) rs.push({ id: '_bend', src: 'pb', dst: 'voice.pitch', depth: S.voice.bend * 100 / PITCH_RANGE });
    return rs;
  }
  _srcScope(src) {
    if (/^env[123]$/.test(src) || src === 'vel' || src === 'note' || src === 'rand') return 'voice';
    const m = /^lfo([123])$/.exec(src);
    if (m) return this.state.lfos[+m[1] - 1].retrig ? 'voice' : 'global';
    return 'global';
  }
  _dstScope(dst) {
    const p = dst.split('.');
    if (p[0] === 'voice' || p[0] === 'gen' || p[0] === 'filter' || p[0] === 'amp') return 'voice';
    if (p[0] === 'lfo') { const l = this.state.lfos[+p[1] - 1]; return l && l.retrig ? 'voice' : 'global'; }
    return 'global';
  }
  _lfoOk(r) {
    const s = /^lfo([123])$/.exec(r.src), d = /^lfo\.([123])\./.exec(r.dst);
    return !(s && d && +d[1] <= +s[1]);
  }
  _voiceParams(v, dst) {
    const p = dst.split('.');
    if (p[0] === 'voice') return p[1] === 'pitch' ? [{ node: v.pitchBus, scale: PITCH_RANGE }] : [];
    if (p[0] === 'gen') {
      const vg = v.gens[p[1]]; if (!vg) return [];
      switch (p[2]) {
        case 'level': return [{ param: vg.gain.gain, scale: 1 }];
        case 'pitch': return vg.det.map(x => ({ param: x, scale: PITCH_RANGE }));
        case 'pan': return vg.pan.map(x => ({ param: x, scale: 2 }));
        case 'morph': return vg.wb.map(x => ({ param: x, scale: 1 })).concat(vg.wa.map(x => ({ param: x, scale: -1 })));
        case 'fm': return vg.fmGain ? [{ param: vg.fmGain.gain, scale: FM_MAX_INDEX * vg.hz }] : [];
        case 'cutoff': return vg.nf ? [{ param: vg.nf.detune, scale: CUTOFF_RANGE }] : [];
      }
      return [];
    }
    if (p[0] === 'filter') {
      if (p[1] === 'cutoff') return v.filters.map(f => ({ param: f.detune, scale: CUTOFF_RANGE }));
      if (p[1] === 'res') return v.filters.map(f => ({ param: f.Q, scale: resScale(f.type) }));
      return [];
    }
    if (p[0] === 'amp' && p[1] === 'level') return v.velGains.map(g => ({ param: g.gain, scale: 1 }));
    if (p[0] === 'lfo') {
      const L = v.lfos[p[1]]; if (!L) return [];
      return p[2] === 'amount' ? [{ param: L.out.gain, scale: 1 }] : p[2] === 'rate' ? [{ param: L.rateParam, scale: L.rateScale }] : [];
    }
    return [];
  }
  _globalParams(dst) {
    const p = dst.split('.');
    if (p[0] === 'lane') { const ln = this._lanes[p[1]]; return ln && p[2] === 'gain' ? [{ param: ln.gain.gain, scale: 1 }] : []; }
    if (p[0] === 'master') return p[1] === 'gain' ? [{ param: this._master.gain.gain, scale: 1 }] : [];
    if (p[0] === 'fx') { const r = this._fx(p[1]); return r && r.obj ? r.obj.mod(p[2]) : []; }
    if (p[0] === 'lfo') {
      const L = this._glfo[p[1]]; if (!L) return [];
      return p[2] === 'amount' ? [{ param: L.out.gain, scale: 1 }] : p[2] === 'rate' ? [{ param: L.rateParam, scale: L.rateScale }] : [];
    }
    return [];
  }
  // src → gain(depth × scale) → param(s); one gain per distinct scale.
  _link(srcNode, targets, depth, sink, init) {
    const groups = new Map();
    for (const tg of targets) { if (!groups.has(tg.scale)) groups.set(tg.scale, []); groups.get(tg.scale).push(tg); }
    const made = [];
    for (const [scale, list] of groups) {
      const g = this.ctx.createGain();
      g.gain.value = init === undefined ? depth * scale : init;
      srcNode.connect(g);
      for (const x of list) g.connect(x.node || x.param);
      sink.push([srcNode, g]);
      made.push({ g, scale });
    }
    return made;
  }
  _clearGlobalRoutes() {
    for (const [s, g] of this._gLinks) { try { s.disconnect(g); } catch (e) { /* ok */ } try { g.disconnect(); } catch (e) { /* ok */ } }
    this._gLinks = []; this._gRoutes = {};
  }
  _rebuildGlobalRoutes() {
    this._clearGlobalRoutes();
    for (const r of this._routes()) {
      if (this._srcScope(r.src) !== 'global' || this._dstScope(r.dst) !== 'global' || !this._lfoOk(r)) continue;
      const sn = this._gsrc[r.src]; if (!sn) continue;
      const tg = this._globalParams(r.dst); if (!tg.length) continue;
      this._gRoutes[r.id] = this._link(sn, tg, r.depth, this._gLinks);
    }
  }
  _liveDepth(m, t) {
    const set = list => list && list.forEach(x => smooth(x.g.gain, (m.on === false ? 0 : m.depth) * x.scale, t));
    set(this._gRoutes[m.id]);
    for (const v of this.voices) { if (v.glIds.has(m.id) && this._lead !== v) continue; set(v.routes[m.id]); }
  }
  _setLead(v, t) {
    const old = this._lead;
    if (old && old !== v) old.gl.forEach(x => x.g.gain.setValueAtTime(0, t));
    this._lead = v;
  }

  // ── samples ─────────────────────────────────────────────────────
  _sample(src) {
    if (typeof src === 'string' && src.startsWith('lib:')) { const p = loadLibSample(src); return p.value || null; }
    return bufsFor(this.ctx.sampleRate).getSample(src);
  }
  _preloadSamples() {
    for (const g of this.state.gens) {
      if (g.type !== 'sample') continue;
      if (g.src.startsWith('lib:')) { const p = loadLibSample(g.src); if (p.value === undefined) { this._pend.add(p); p.then(() => this._pend.delete(p)); } }
      else bufsFor(this.ctx.sampleRate).getSample(g.src);
    }
  }
  // Pre-load a library take for a Sample generator (AK.lib must be on the page).
  loadLibrarySample(id) { const p = loadLibSample('lib:' + id); this._pend.add(p); p.then(() => this._pend.delete(p)); return p; }

  // ── voices ──────────────────────────────────────────────────────
  _prune(t) { this.voices = this.voices.filter(v => v.end > t); }
  _startVoice(note, vel, t) {
    const c = this.ctx, S = this.state;
    const v = {
      id: ++this._uid, note, baseNote: note, vel, t0: t, end: Infinity, rel: false, relT: 0,
      amp: Object.assign({}, S.amp), envCfg: S.envs.map(e => Object.assign({}, e)), key: S.filter.key,
      nodes: [], srcs: [], gens: {}, filters: [], velGains: [], outs: [], lfos: {}, msrc: {}, envs: {},
      routes: {}, gl: [], glIds: new Set(), links: [], rand: Math.random(), cleaned: false,
    };
    const N = n => (v.nodes.push(n), n);
    const SRC = (n, st = t, off = 0) => { v.nodes.push(n); v.srcs.push([n, st, off]); return n; };
    v.pitchCS = SRC(c.createConstantSource()); v.pitchCS.offset.value = 0;
    v.pitchBus = N(c.createGain()); v.pitchCS.connect(v.pitchBus);
    v.ampEnv = SRC(c.createConstantSource()); v.ampEnv.offset.value = 0;

    const velScale = 1 - S.voice.velSens + S.voice.velSens * Math.pow(vel, 1.4);
    const fl = S.filter.on ? S.filter.lanes : '';
    const paths = {};
    const pathFor = L => {
      if (paths[L]) return paths[L];
      const bus = N(c.createGain());
      let n = bus;
      if (fl.includes(L)) {
        const f = N(c.createBiquadFilter());
        f.type = S.filter.type; f.frequency.value = S.filter.cutoff; f.Q.value = resQ(S.filter.type, S.filter.res);
        f.gain.value = S.filter.gain; f.detune.value = S.filter.key * (note - 60) * 100;
        n.connect(f); n = f; v.filters.push(f);
      }
      const vg = N(c.createGain()); vg.gain.value = velScale; n.connect(vg); v.velGains.push(vg);
      const ag = N(c.createGain()); ag.gain.value = 0; vg.connect(ag); v.ampEnv.connect(ag.gain);
      const out = N(c.createGain()); ag.connect(out); out.connect(this._lanes[L].input); v.outs.push(out);
      return (paths[L] = bus);
    };

    // generators
    let budget = MAX_OSC_PER_VOICE;
    const gens = S.gens.filter(g => g.on);
    const B = bufsFor(c.sampleRate);
    for (const g of gens) {
      const vg = { g, gain: N(c.createGain()), det: [], detPos: [], pan: [], panPos: [], freq: [], wa: [], wb: [], hz: 0, fmGain: null, nf: null, osc: null };
      vg.gain.gain.value = g.level;
      vg.gain.connect(pathFor(g.lane));
      const fixed = g.mode === 'fixed', det0 = g.coarse * 100 + g.fine;
      const baseHz = fixed ? g.hz : mtof(note) * g.ratio;
      vg.hz = baseHz * Math.pow(2, det0 / 1200);
      const mkPan = pos => { const p = N(c.createStereoPanner()); p.pan.value = clamp(g.pan + pos * g.spread, -1, 1); vg.pan.push(p.pan); vg.panPos.push(pos); return p; };
      if (g.type === 'noise') {
        const s = SRC(c.createBufferSource(), t, Math.random() * 1.9);
        s.buffer = B.getNoise(g.color); s.loop = true;
        let n = s;
        if (g.nfilt !== 'none') {
          const f = N(c.createBiquadFilter()); f.type = g.nfilt; f.frequency.value = g.nfreq; f.Q.value = resQ(g.nfilt, g.nres);
          n.connect(f); n = f; vg.nf = f;
        }
        const p = mkPan(0); n.connect(p); p.connect(vg.gain);
      } else if (g.type === 'fm') {
        const o = SRC(c.createOscillator());
        o.frequency.value = baseHz; o.detune.value = det0;
        if (!fixed) v.pitchBus.connect(o.detune);
        vg.det.push(o.detune); vg.detPos.push(0); vg.freq.push(o.frequency); vg.osc = o;
        const p = mkPan(0); o.connect(p); p.connect(vg.gain);
        budget--;
      } else {
        const per = g.type === 'wavetable' ? 2 : 1;
        const n = Math.max(1, Math.min(g.unison, Math.floor(budget / per)));
        budget -= n * per;
        const uni = N(c.createGain()); uni.gain.value = 1 / Math.sqrt(n); uni.connect(vg.gain);
        let sb = null, rate = 1;
        if (g.type === 'sample') { sb = this._sample(g.src); if (sb) rate = fixed ? g.ratio : Math.pow(2, (note - g.root) / 12) * g.ratio; }
        for (let i = 0; i < n; i++) {
          const pos = n === 1 ? 0 : (i / (n - 1)) * 2 - 1;
          const d = det0 + pos * g.detune;
          const pn = mkPan(pos); pn.connect(uni);
          const st = (n > 1 && i > 0) ? t + Math.random() / Math.max(30, baseHz) : t;
          if (g.type === 'analog') {
            const o = SRC(c.createOscillator(), st);
            if (g.shape === 'pulse') o.setPeriodicWave(pulseWave(c, g.pw));
            else o.type = g.shape === 'saw' ? 'sawtooth' : g.shape;
            o.frequency.value = baseHz; o.detune.value = d; o.connect(pn);
            if (!fixed) v.pitchBus.connect(o.detune);
            vg.det.push(o.detune); vg.detPos.push(pos); vg.freq.push(o.frequency);
          } else if (g.type === 'wavetable') {
            const ga = N(c.createGain()), gb = N(c.createGain());
            ga.gain.value = 1 - g.morph; gb.gain.value = g.morph; ga.connect(pn); gb.connect(pn);
            vg.wa.push(ga.gain); vg.wb.push(gb.gain);
            for (const [side, gg] of [['a', ga], ['b', gb]]) {
              const o = SRC(c.createOscillator(), st);
              o.setPeriodicWave(tableWave(c, g.table, side));
              o.frequency.value = baseHz; o.detune.value = d; o.connect(gg);
              if (!fixed) v.pitchBus.connect(o.detune);
              vg.det.push(o.detune); vg.detPos.push(pos); vg.freq.push(o.frequency);
            }
          } else if (sb) {
            const buf = sb.buffer, dur = buf.duration;
            const s = SRC(c.createBufferSource(), st, clamp(g.start, 0, 0.95) * dur);
            s.buffer = buf; s.playbackRate.value = rate; s.detune.value = d;
            if (g.loop) {
              s.loop = true;
              const lp = sb.loop || [0, dur];
              s.loopStart = Math.max(lp[0], g.start * dur); s.loopEnd = Math.min(dur, lp[1]);
              if (s.loopEnd - s.loopStart < 0.01) { s.loopStart = 0; s.loopEnd = dur; }
            }
            if (!fixed) v.pitchBus.connect(s.detune);
            s.connect(pn);
            vg.det.push(s.detune); vg.detPos.push(pos);
          }
        }
      }
      v.gens[g.id] = vg;
    }
    // FM operators → target generators' oscillator frequencies (no loops)
    const edges = {};
    const reaches = (a, b) => { const seen = new Set(), st = [a]; while (st.length) { const x = st.pop(); if (x === b) return true; if (seen.has(x)) continue; seen.add(x); (edges[x] || []).forEach(y => st.push(y)); } return false; };
    for (const g of gens) {
      if (g.type !== 'fm' || !g.fmTarget || g.fmTarget === g.id) continue;
      const vg = v.gens[g.id], tg = v.gens[g.fmTarget];
      if (!vg || !tg || !tg.freq.length || reaches(g.fmTarget, g.id)) continue;
      (edges[g.id] = edges[g.id] || []).push(g.fmTarget);
      const fg = N(c.createGain()); fg.gain.value = g.fmAmt * FM_MAX_INDEX * vg.hz;
      vg.osc.connect(fg); tg.freq.forEach(p => fg.connect(p));
      vg.fmGain = fg;
    }

    // per-voice modulation sources (only the ones some routing uses)
    const routes = this._routes();
    const need = new Set();
    for (const r of routes) if (this._srcScope(r.src) === 'voice') need.add(r.src);
    for (const k of [...need].sort()) {
      let m;
      if ((m = /^env([123])$/.exec(k))) {
        const cs = SRC(c.createConstantSource()); cs.offset.value = 0;
        envOn(cs.offset, v.envCfg[+m[1] - 1], t);
        v.envs[k] = cs; v.msrc[k] = cs;
      } else if ((m = /^lfo([123])$/.exec(k))) {
        const L = this._mkLfo(S.lfos[+m[1] - 1], t, true);
        L.nodes.forEach(n => v.nodes.push(n)); L.srcs.forEach(x => v.srcs.push(x));
        v.lfos[m[1]] = L; v.msrc[k] = L.out;
      } else {
        const cs = SRC(c.createConstantSource());
        cs.offset.value = k === 'vel' ? vel : k === 'note' ? (note - 60) / 60 : v.rand;
        v.msrc[k] = cs;
      }
    }
    for (const r of routes) {
      if (!this._lfoOk(r)) continue;
      const ss = this._srcScope(r.src), ds = this._dstScope(r.dst);
      const sn = ss === 'voice' ? v.msrc[r.src] : this._gsrc[r.src];
      if (!sn) continue;
      if (ds === 'voice') {
        const tg = this._voiceParams(v, r.dst); if (!tg.length) continue;
        v.routes[r.id] = this._link(sn, tg, r.depth, v.links);
      } else if (ss === 'voice') {
        const tg = this._globalParams(r.dst); if (!tg.length) continue;
        const made = this._link(sn, tg, r.depth, v.links, 0);
        made.forEach(x => x.g.gain.setValueAtTime(r.depth * x.scale, t));
        v.gl.push(...made); v.glIds.add(r.id); v.routes[r.id] = made;
      }
    }

    // envelopes + start
    envOn(v.ampEnv.offset, v.amp, t);
    for (const [n, st, off] of v.srcs) n.start(st, off);
    if (v.amp.s <= 0.0001) this._stopAt(v, t + Math.max(0.0008, v.amp.a) + v.amp.d * 1.7 + 0.03);
    v.ampEnv.onended = () => this._cleanup(v);
    return v;
  }
  _stopAt(v, end) {
    v.end = end;
    for (const [n] of v.srcs) { try { n.stop(end); } catch (e) { /* ok */ } }
  }
  _releaseVoice(v, t) {
    if (v.rel || v.end <= t) return;
    v.rel = true;
    t = Math.max(t, v.t0 + 0.002);
    v.relT = t;
    if (v.ops) v.ops.push({ k: 'rel', t });
    envOff(v.ampEnv.offset, v.amp.r, t);
    v.envCfg.forEach((e, i) => { const cs = v.envs['env' + (i + 1)]; if (cs) envOff(cs.offset, e.r, t); });
    const end = t + Math.max(0.003, v.amp.r) * 1.3 + 0.03;
    if (end < v.end) this._stopAt(v, end);
  }
  _killVoice(v, t) {
    v.rel = true;
    if (v.ops) v.ops.push({ k: 'kill', t });
    for (const o of v.outs) { o.gain.cancelScheduledValues(t); o.gain.setValueAtTime(1, t); o.gain.linearRampToValueAtTime(0, t + 0.008); }
    const e = t + 0.012;
    if (e < v.end) this._stopAt(v, e);
  }
  _cleanup(v) {
    if (v.cleaned) return;
    v.cleaned = true;
    for (const [s, g] of v.links) { try { s.disconnect(g); } catch (e) { /* ok */ } }
    for (const n of v.nodes) { try { n.disconnect(); } catch (e) { /* ok */ } }
    for (const [s, g] of v.links) { try { g.disconnect(); } catch (e) { /* ok */ } }
    const i = this.voices.indexOf(v); if (i >= 0) this.voices.splice(i, 1);
    if (this._lead === v) this._lead = null;
    if (this._mono === v) this._mono = null;
    const j = this._monoVoices.indexOf(v); if (j >= 0) this._monoVoices.splice(j, 1);
  }
  _glide(v, note, t, glide) {
    const cents = (note - v.baseNote) * 100, p = v.pitchCS.offset;
    if (v.ops) v.ops.push({ k: 'glide', t, note, tau: glide > 0.0005 ? glide / 3 : 0 });
    hold(p, t);
    if (glide > 0.0005) p.setTargetAtTime(cents, t, glide / 3); else p.setValueAtTime(cents, t);
    if (v.key) v.filters.forEach(f => { hold(f.detune, t); f.detune.setTargetAtTime(v.key * (note - 60) * 100, t, Math.max(0.002, glide / 3)); });
    const ns = v.msrc.note; if (ns && ns.offset) ns.offset.setValueAtTime((note - 60) / 60, t);
  }
  _retrig(v, t) {
    if (v.ops) v.ops.push({ k: 'retrig', t });
    envRetrig(v.ampEnv.offset, v.amp, t);
    v.envCfg.forEach((e, i) => { const cs = v.envs['env' + (i + 1)]; if (cs) envRetrig(cs.offset, e, t); });
    if (v.amp.s <= 0.0001) this._stopAt(v, t + Math.max(0.0008, v.amp.a) + v.amp.d * 1.7 + 0.03);
  }
  // ── mono / legato ───────────────────────────────────────────────
  // Events go into a time-sorted log. A DAW that schedules ahead sends
  // noteOn + noteOff per note, i.e. out of time order; when an earlier
  // event arrives the mono voice is rewound to that time and the log is
  // replayed, so last-note priority, legato glides and releases come out
  // as if the events had arrived in order.
  _monoOn(note, vel, t) { this._monoEvent({ t, on: true, note, vel }); }
  _monoOff(note, t) { this._monoEvent({ t, on: false, note }); }
  _monoReset() {
    this._monoEv = []; this._monoBase = { stack: [], last: this._lastNote }; this._monoStack = []; this._mono = null;
  }
  _monoEvent(ev) {
    const E = this._monoEv;
    let i = E.length;
    while (i > 0 && E[i - 1].t > ev.t) i--;
    E.splice(i, 0, ev);
    if (i === E.length - 1) this._monoApply(ev);
    else {
      const T = ev.t, st = this._monoBase.stack.slice();
      let last = this._monoBase.last;
      for (const e of E) {
        if (e.t >= T) break;
        const k = st.indexOf(e.note); if (k >= 0) st.splice(k, 1);
        if (e.on) { st.push(e.note); last = e.note; }
      }
      this._monoStack = st; this._lastNote = last;
      this._monoRewind(T);
      for (const e of E) if (e.t >= T) this._monoApply(e);
    }
    const old = this.ctx.currentTime - 2, B = this._monoBase;
    while (E.length > 1 && E[0].t < old) {
      const e = E.shift(), k = B.stack.indexOf(e.note);
      if (k >= 0) B.stack.splice(k, 1);
      if (e.on) { B.stack.push(e.note); B.last = e.note; }
    }
  }
  _monoApply(ev) {
    const S = this.state, st = this._monoStack, t = ev.t;
    if (!ev.on) {
      const i = st.indexOf(ev.note); if (i < 0) return;
      st.splice(i, 1);
      const v = this._mono;
      if (!v || v.rel || v.end <= t || ev.note !== v.note) return;
      if (st.length) { const top = st[st.length - 1]; this._glide(v, top, t, S.voice.glide); v.note = top; }
      else this._releaseVoice(v, t);
      return;
    }
    const note = ev.note, from = this._lastNote;
    const i = st.indexOf(note); if (i >= 0) st.splice(i, 1);
    st.push(note);
    this._lastNote = note;
    const v = this._mono;
    if (v && !v.rel && v.end > t) {
      this._glide(v, note, t, S.voice.glide);
      if (S.voice.mode === 'mono') this._retrig(v, t);
      v.note = note;
      return;
    }
    if (v && v.end > t) { this._killVoice(v, t); const k = this.voices.indexOf(v); if (k >= 0) this.voices.splice(k, 1); }
    this._prune(t);
    while (this.voices.length >= this.maxVoices) { const o = this.voices.shift(); this._killVoice(o, t); }
    const nv = this._startVoice(note, ev.vel, t);
    nv.ops = [{ k: 'start', t, note, tau: 0 }];
    if (S.voice.mode === 'mono' && S.voice.glide > 0.0005 && from != null && from !== note) {
      const p = nv.pitchCS.offset;
      p.setValueAtTime((from - note) * 100, t);
      p.setTargetAtTime(0, t, S.voice.glide / 3);
      nv.ops[0].tau = S.voice.glide / 3;
    }
    this._mono = nv;
    this.voices.push(nv);
    this._monoVoices.push(nv);
    this._setLead(nv, t);
  }
  // Undo everything the mono voices were told to do at or after T.
  _monoRewind(T) {
    let active = null;
    for (const v of this._monoVoices.slice()) {
      if (v.cleaned) continue;
      if (v.t0 >= T) {                                   // born at/after T: never sounds
        v.ops = []; v.rel = true;
        for (const o of v.outs) { o.gain.cancelScheduledValues(v.t0); o.gain.setValueAtTime(0, v.t0); }
        this._stopAt(v, v.t0);
        const k = this.voices.indexOf(v); if (k >= 0) this.voices.splice(k, 1);
        if (this._lead === v) this._lead = null;
        continue;
      }
      const ops = v.ops.filter(o => o.t < T);
      if (ops.length === v.ops.length && v.end <= T) continue;
      v.ops = ops;
      let note = v.baseNote, tau = 0, trig = v.t0, rel = null, kill = null;
      for (const o of ops) {
        if (o.k === 'start' || o.k === 'glide') { note = o.note; tau = o.tau; }
        else if (o.k === 'retrig') trig = o.t;
        else if (o.k === 'rel') rel = o.t;
        else if (o.k === 'kill') kill = o.t;
      }
      if (kill != null) continue;
      v.note = note; v.rel = rel != null; v.relT = rel || 0;
      for (const o of v.outs) o.gain.cancelScheduledValues(T);
      for (const x of v.gl) x.g.gain.cancelScheduledValues(T);
      const pc = (note - v.baseNote) * 100, pp = v.pitchCS.offset;
      hold(pp, T);
      if (tau) pp.setTargetAtTime(pc, T, tau); else pp.setValueAtTime(pc, T);
      if (v.key) v.filters.forEach(f => { hold(f.detune, T); f.detune.setTargetAtTime(v.key * (note - 60) * 100, T, Math.max(0.002, tau)); });
      const ns = v.msrc.note; if (ns && ns.offset) { hold(ns.offset, T); ns.offset.setValueAtTime((note - 60) / 60, T); }
      envCont(v.ampEnv.offset, v.amp, trig, rel, T);
      v.envCfg.forEach((e, i) => { const cs = v.envs['env' + (i + 1)]; if (cs) envCont(cs.offset, e, trig, rel, T); });
      let end = 1e7;
      if (rel != null) end = rel + Math.max(0.003, v.amp.r) * 1.3 + 0.03;
      else if (v.amp.s <= 0.0001) end = trig + Math.max(0.0008, v.amp.a) + v.amp.d * 1.7 + 0.03;
      this._stopAt(v, end);
      if (end > T) {
        if (!this.voices.includes(v)) this.voices.push(v);
        if (!active || v.t0 > active.t0) active = v;
      }
    }
    this._mono = active;
  }

  mountEditor(containerEl, opts) {
    const ed = new ForgeEditor(this, containerEl, opts || {});
    this._editors.add(ed);
    return { destroy: () => ed.destroy(), element: ed.root, editor: ed };
  }
}

// ═══════════════════════════════════════════════════════════════════
// Factory presets. Partial states — normalizeState() fills the rest.
// Generator ids are g1… in order; snapins referenced by routings carry ids.
// ═══════════════════════════════════════════════════════════════════
const E = (a, d, s, r) => ({ a, d, s, r });
const FX = (type, p, id) => (id ? { id, type, p } : { type, p });
const R = (src, dst, depth) => ({ src, dst, depth });
const MAC = (...names) => names.map(n => ({ name: n, value: 0 }));
const LN = (A, B, C) => ({ A: A || {}, B: B || {}, C: C || {} });

const FORGE_PRESETS = [
  // ── DRUMS ─────────────────────────────────────────────────────────
  { id: 'kick', name: 'Kick · Levee', category: 'drums', state: {
    gens: [
      { type: 'analog', shape: 'sine', mode: 'fixed', hz: 47, level: 0.95 },
      { type: 'noise', color: 'white', nfilt: 'highpass', nfreq: 2600, nres: 0.1, level: 0 },
      { type: 'analog', shape: 'triangle', mode: 'fixed', hz: 94, level: 0 },
    ],
    filter: { on: false },
    amp: E(0.0008, 0.5, 0, 0.08),
    envs: [E(0.0005, 0.075, 0, 0.05), E(0.0005, 0.12, 0, 0.05), E(0.0005, 0.012, 0, 0.01)],
    mods: [R('env1', 'gen.g1.pitch', 0.6), R('env1', 'gen.g3.pitch', 0.5), R('env3', 'gen.g2.level', 0.55), R('env2', 'gen.g3.level', 0.3),
      R('m1', 'gen.g1.pitch', 0.06), R('m2', 'fx.kd.drive', 0.6)],
    macros: MAC('TUNE', 'DRIVE', 'BODY'),
    lanes: LN({ fx: [FX('dist', { mode: 'soft', drive: 0.22, tone: 9000 }, 'kd'), FX('eq', { low: 3, lowf: 70, mid: -3, midf: 400, high: 1 }), FX('comp', { thresh: -16, ratio: 4, attack: 0.006, release: 0.12, makeup: 3 })] }),
    voice: { velSens: 0.5 }, master: { gain: 0.8 },
  } },
  { id: 'snare', name: 'Snare · Backroom', category: 'drums', state: {
    gens: [
      { type: 'analog', shape: 'triangle', mode: 'fixed', hz: 186, level: 0 },
      { type: 'noise', color: 'white', nfilt: 'highpass', nfreq: 1500, nres: 0.15, level: 0.5 },
      { type: 'analog', shape: 'sine', mode: 'fixed', hz: 332, level: 0 },
    ],
    filter: { on: false },
    amp: E(0.0008, 0.24, 0, 0.1),
    envs: [E(0.0005, 0.045, 0, 0.03), E(0.0005, 0.1, 0, 0.05), E(0.0005, 0.02, 0, 0.02)],
    mods: [R('env1', 'gen.g1.pitch', 0.08), R('env1', 'gen.g3.pitch', 0.05), R('env2', 'gen.g1.level', 0.8), R('env2', 'gen.g3.level', 0.35),
      R('m1', 'gen.g2.level', 0.35), R('m2', 'fx.sv.mix', 0.4)],
    macros: MAC('SNAP', 'ROOM'),
    lanes: LN({ fx: [FX('eq', { low: -2, lowf: 120, mid: 3, midf: 2400, high: 3, highf: 8000 }), FX('comp', { thresh: -18, ratio: 4, attack: 0.004, release: 0.1, makeup: 3 }), FX('reverb', { size: 0.9, damp: 0.6, mix: 0.14 }, 'sv')] }),
    voice: { velSens: 0.6 }, master: { gain: 0.8 },
  } },
  { id: 'clap', name: 'Clap · Juke Joint', category: 'drums', state: {
    gens: [{ type: 'noise', color: 'white', nfilt: 'bandpass', nfreq: 1150, nres: 0.25, level: 0.5 }],
    filter: { on: false },
    amp: E(0.0008, 0.3, 0, 0.15),
    envs: [E(0.0005, 0.045, 0, 0.02), E(0.0005, 0.3, 0, 0.1), E(0.0005, 0.3, 0, 0.1)],
    lfos: [{ shape: 'square', rate: 85, retrig: true, amount: 0 }],
    mods: [R('env1', 'lfo.1.amount', 1), R('lfo1', 'gen.g1.level', 0.5), R('m1', 'fx.cv.mix', 0.4), R('rand', 'gen.g1.cutoff', 0.03)],
    macros: MAC('ROOM'),
    lanes: LN({ fx: [FX('eq', { low: -6, lowf: 200, mid: 2, midf: 1400, high: 2 }), FX('reverb', { size: 1.1, damp: 0.5, mix: 0.2 }, 'cv'), FX('comp', { thresh: -16, ratio: 3, makeup: 3 })] }),
    master: { gain: 1.4 },
  } },
  { id: 'hat_closed', name: 'Hat · Closed Tin', category: 'drums', state: {
    gens: [
      { type: 'analog', shape: 'square', mode: 'fixed', hz: 540, level: 0.35 },
      { type: 'fm', mode: 'fixed', hz: 1467, fmTarget: 'g1', fmAmt: 0.6, level: 0 },
      { type: 'analog', shape: 'square', mode: 'fixed', hz: 811, level: 0.25 },
      { type: 'noise', color: 'white', level: 0.35 },
    ],
    filter: { on: true, type: 'highpass', cutoff: 7200, res: 0.25, key: 0 },
    amp: E(0.0005, 0.06, 0, 0.04),
    mods: [R('m1', 'filter.cutoff', 0.12), R('vel', 'filter.cutoff', -0.05)],
    macros: MAC('TONE'),
    lanes: LN({ fx: [FX('eq', { high: 3, highf: 10000, low: -12, lowf: 300 })] }),
    master: { gain: 0.8 },
  } },
  { id: 'hat_open', name: 'Hat · Open Screen Door', category: 'drums', state: {
    gens: [
      { type: 'analog', shape: 'square', mode: 'fixed', hz: 540, level: 0.35 },
      { type: 'fm', mode: 'fixed', hz: 1467, fmTarget: 'g1', fmAmt: 0.6, level: 0 },
      { type: 'analog', shape: 'square', mode: 'fixed', hz: 811, level: 0.25 },
      { type: 'noise', color: 'white', level: 0.3 },
    ],
    filter: { on: true, type: 'highpass', cutoff: 6800, res: 0.2, key: 0 },
    amp: E(0.0008, 0.5, 0, 0.3),
    envs: [E(0.0005, 0.4, 0, 0.3)],
    mods: [R('env1', 'filter.cutoff', 0.06), R('m1', 'filter.cutoff', 0.12)],
    macros: MAC('TONE'),
    lanes: LN({ fx: [FX('eq', { high: 2, highf: 9000, low: -12, lowf: 300 }), FX('reverb', { size: 0.8, damp: 0.3, mix: 0.1 })] }),
    master: { gain: 0.95 },
  } },
  { id: 'perc_rim', name: 'Rim · Bottle Neck', category: 'drums', state: {
    gens: [
      { type: 'analog', shape: 'triangle', mode: 'fixed', hz: 1720, level: 0.5 },
      { type: 'analog', shape: 'sine', mode: 'fixed', hz: 470, level: 0.65 },
      { type: 'noise', color: 'white', nfilt: 'bandpass', nfreq: 3200, nres: 0.3, level: 0.35 },
    ],
    filter: { on: false },
    amp: E(0.0005, 0.06, 0, 0.03),
    envs: [E(0.0005, 0.012, 0, 0.01), E(0.0005, 0.008, 0, 0.01)],
    mods: [R('env1', 'gen.g1.pitch', 0.04), R('env2', 'gen.g3.level', 0.4), R('m1', 'fx.rv.mix', 0.4)],
    macros: MAC('ROOM'),
    lanes: LN({ fx: [FX('eq', { low: -8, lowf: 250, mid: 4, midf: 1800 }), FX('reverb', { size: 0.6, damp: 0.4, mix: 0.12 }, 'rv')] }),
    master: { gain: 0.8 },
  } },
  { id: 'tom', name: 'Tom · Floor', category: 'drums', state: {
    gens: [
      { type: 'analog', shape: 'sine', level: 0.9 },
      { type: 'analog', shape: 'triangle', ratio: 1.5, level: 0.12 },
      { type: 'noise', color: 'white', nfilt: 'lowpass', nfreq: 3500, level: 0 },
    ],
    filter: { on: false },
    amp: E(0.0008, 0.6, 0, 0.2),
    envs: [E(0.0005, 0.14, 0, 0.1), E(0.0005, 0.03, 0, 0.02)],
    mods: [R('env1', 'gen.g1.pitch', 0.12), R('env1', 'gen.g2.pitch', 0.12), R('env2', 'gen.g3.level', 0.4), R('m1', 'gen.g1.pitch', 0.1)],
    macros: MAC('TUNE'),
    lanes: LN({ fx: [FX('dist', { mode: 'soft', drive: 0.12, tone: 7000 }), FX('comp', { thresh: -16, ratio: 3, makeup: 2 }), FX('reverb', { size: 1.4, damp: 0.55, mix: 0.14 })] }),
    master: { gain: 0.8 },
  } },

  // ── BASS ──────────────────────────────────────────────────────────
  { id: 'bass_sub', name: 'Sub · Under the Bridge', category: 'bass', state: {
    gens: [{ type: 'analog', shape: 'sine', level: 0.85 }, { type: 'analog', shape: 'triangle', coarse: 12, level: 0.16 }],
    filter: { on: true, type: 'lowpass', cutoff: 900, res: 0.05, key: 0.3, env: 0 },
    amp: E(0.004, 0.4, 0.85, 0.12),
    mods: [R('m1', 'fx.sd.drive', 0.6), R('m1', 'gen.g2.level', 0.3)],
    macros: MAC('GROWL'),
    lanes: LN({ fx: [FX('dist', { mode: 'soft', drive: 0.1, tone: 2500, mix: 0.6 }, 'sd'), FX('eq', { low: 2, lowf: 60, high: -6, highf: 3000 })] }),
    voice: { mode: 'legato', glide: 0.035, velSens: 0.35 }, master: { gain: 0.85 },
  } },
  { id: 'bass_acid', name: 'Acid · Swamp 303', category: 'bass', state: {
    gens: [{ type: 'analog', shape: 'saw', level: 0.7 }],
    filter: { on: true, type: 'lowpass', cutoff: 240, res: 0.62, key: 0.25, env: 0.42 },
    amp: E(0.002, 0.3, 0.75, 0.06),
    envs: [E(0.005, 0.4, 0.3, 0.3), E(0.0008, 0.22, 0.04, 0.1), E(0.3, 0.6, 0.5, 0.5)],
    mods: [R('vel', 'filter.cutoff', 0.12), R('m1', 'filter.cutoff', 0.35), R('m2', 'filter.res', 0.3)],
    macros: MAC('CUTOFF', 'RES'),
    lanes: LN({ fx: [FX('dist', { mode: 'soft', drive: 0.35, tone: 6000, mix: 0.7 }), FX('delay', { sync: true, div: '1/8d', fb: 0.3, tone: 2500, mix: 0.14 })] }),
    voice: { mode: 'legato', glide: 0.06, velSens: 0.4 }, master: { gain: 0.8 },
  } },
  { id: 'bass_reese', name: 'Reese · Night Freight', category: 'bass', state: {
    gens: [
      { type: 'analog', shape: 'saw', unison: 3, detune: 22, spread: 0.4, level: 0.55 },
      { type: 'analog', shape: 'saw', fine: -9, unison: 2, detune: 12, spread: 0.3, level: 0.45 },
      { type: 'analog', shape: 'sine', coarse: -12, level: 0.4 },
    ],
    filter: { on: true, type: 'lowpass', cutoff: 700, res: 0.15, key: 0.2, env: 0.08 },
    amp: E(0.008, 0.5, 0.9, 0.2),
    lfos: [{ shape: 'sine', rate: 0.18, retrig: false }],
    mods: [R('lfo1', 'filter.cutoff', 0.08), R('m1', 'filter.cutoff', 0.3), R('mw', 'filter.cutoff', 0.25)],
    macros: MAC('OPEN'),
    lanes: LN({ fx: [FX('dist', { mode: 'soft', drive: 0.18, tone: 5000, mix: 0.6 }), FX('eq', { low: 1, lowf: 80, mid: -2, midf: 500 })] }),
    voice: { mode: 'legato', glide: 0.05, velSens: 0.3 }, master: { gain: 0.8 },
  } },

  // ── KEYS ──────────────────────────────────────────────────────────
  { id: 'keys_ep', name: 'EP · Suitcase', category: 'keys', state: {
    gens: [
      { type: 'analog', shape: 'sine', level: 0.75 },
      { type: 'fm', ratio: 1, fmTarget: 'g1', fmAmt: 0.03, level: 0 },
      { type: 'fm', ratio: 14, fmTarget: 'g1', fmAmt: 0.0, level: 0 },
      { type: 'analog', shape: 'sine', ratio: 2, level: 0.08 },
    ],
    filter: { on: false },
    amp: E(0.002, 2.2, 0.3, 0.4),
    envs: [E(0.001, 1.3, 0.12, 0.3), E(0.001, 0.08, 0, 0.05), E(0.3, 0.6, 0.5, 0.5)],
    lfos: [{ shape: 'sine', rate: 4.6, retrig: false, amount: 0 }],
    mods: [R('env1', 'gen.g2.fm', 0.2), R('vel', 'gen.g2.fm', 0.12), R('env2', 'gen.g3.fm', 0.012), R('lfo1', 'gen.g1.pan', 0.3), R('m1', 'lfo.1.amount', 1)],
    macros: MAC('TREMOLO'),
    lanes: LN({ fx: [FX('comp', { thresh: -20, ratio: 2.5, makeup: 2 }), FX('chorus', { rate: 0.5, depth: 0.25, mix: 0.25 }), FX('reverb', { size: 1.6, damp: 0.5, mix: 0.18 })] }),
    voice: { velSens: 0.65 }, master: { gain: 0.85 },
  } },
  { id: 'keys_organ', name: 'Organ · Revival Tent', category: 'keys', state: {
    gens: [
      { type: 'analog', shape: 'sine', ratio: 0.5, level: 0.42 },
      { type: 'analog', shape: 'sine', ratio: 1, level: 0.5 },
      { type: 'analog', shape: 'sine', ratio: 1.5, level: 0.32 },
      { type: 'analog', shape: 'sine', ratio: 2, level: 0.28 },
      { type: 'noise', color: 'white', nfilt: 'bandpass', nfreq: 2500, nres: 0.2, level: 0 },
    ],
    filter: { on: false },
    amp: E(0.004, 0.1, 1, 0.06),
    envs: [E(0.0005, 0.012, 0, 0.01)],
    mods: [R('env1', 'gen.g5.level', 0.25), R('m1', 'fx.ol.rate', 0.7), R('mw', 'fx.ol.rate', 0.7), R('m2', 'fx.od.drive', 0.5)],
    macros: MAC('LESLIE', 'GRIT'),
    lanes: LN({ fx: [FX('dist', { mode: 'soft', drive: 0.15, tone: 7000, mix: 0.55 }, 'od'), FX('chorus', { rate: 0.8, depth: 0.35, mix: 0.45 }, 'ol'), FX('reverb', { size: 1.3, damp: 0.5, mix: 0.15 })] }),
    voice: { velSens: 0.1 }, master: { gain: 0.75 },
  } },
  { id: 'keys_tape_ep', name: 'EP · Dusty Tape', category: 'keys', state: {
    gens: [
      { type: 'analog', shape: 'sine', level: 0.75 },
      { type: 'fm', ratio: 1, fmTarget: 'g1', fmAmt: 0.02, level: 0 },
      { type: 'fm', ratio: 7, fmTarget: 'g1', fmAmt: 0.0, level: 0 },
      { type: 'analog', shape: 'triangle', ratio: 1, fine: 4, level: 0.12 },
    ],
    filter: { on: true, type: 'lowpass', cutoff: 3600, res: 0.05, key: 0.4 },
    amp: E(0.003, 2.6, 0.25, 0.5),
    envs: [E(0.001, 1.6, 0.1, 0.4), E(0.001, 0.06, 0, 0.05)],
    mods: [R('env1', 'gen.g2.fm', 0.15), R('vel', 'gen.g2.fm', 0.08), R('env2', 'gen.g3.fm', 0.01), R('rand', 'voice.pitch', 0.002), R('m1', 'fx.tp.wow', 0.6), R('m2', 'fx.tp.age', 0.5)],
    macros: MAC('WARBLE', 'DUST'),
    lanes: LN({ fx: [FX('tape', { sat: 0.35, wow: 0.45, flutter: 0.3, age: 0.5, hiss: 0.3 }, 'tp'), FX('eq', { low: 2, lowf: 140, high: -4, highf: 5000 }), FX('reverb', { size: 1.2, damp: 0.7, mix: 0.16 })] }),
    voice: { velSens: 0.6 }, master: { gain: 1.1 },
  } },

  // ── PADS ──────────────────────────────────────────────────────────
  { id: 'pad_warm', name: 'Pad · Porch Light', category: 'pads', state: {
    gens: [{ type: 'analog', shape: 'saw', unison: 5, detune: 14, spread: 0.8, level: 0.45 }, { type: 'analog', shape: 'triangle', coarse: -12, level: 0.28 }],
    filter: { on: true, type: 'lowpass', cutoff: 1100, res: 0.12, key: 0.3, env: 0.12 },
    amp: E(0.9, 1.5, 0.85, 1.8),
    envs: [E(0.5, 1, 0.5, 1), E(1.2, 2, 0.4, 1.5)],
    lfos: [{ shape: 'sine', rate: 0.12, retrig: false }],
    mods: [R('lfo1', 'filter.cutoff', 0.05), R('m1', 'filter.cutoff', 0.3), R('m2', 'fx.pv.mix', 0.4), R('mw', 'filter.cutoff', 0.2)],
    macros: MAC('BRIGHT', 'SPACE'),
    lanes: LN({ fx: [FX('chorus', { rate: 0.35, depth: 0.5, mix: 0.35 }), FX('reverb', { size: 4, damp: 0.55, mix: 0.32 }, 'pv')] }),
    voice: { velSens: 0.3 }, master: { gain: 1.3 },
  } },
  { id: 'pad_glass', name: 'Pad · Glass Harmonica', category: 'pads', state: {
    gens: [
      { type: 'wavetable', table: 'glass', morph: 0.2, unison: 3, detune: 8, spread: 0.7, level: 0.8 },
      { type: 'fm', ratio: 3.5, fmTarget: 'g1', fmAmt: 0.04, level: 0 },
      { type: 'analog', shape: 'sine', coarse: 12, level: 0.1 },
    ],
    filter: { on: true, type: 'lowpass', cutoff: 6000, res: 0.1, key: 0.2 },
    amp: E(0.6, 2, 0.7, 2.2),
    lfos: [{ shape: 'triangle', rate: 0.08, retrig: false, uni: true }],
    mods: [R('lfo1', 'gen.g1.morph', 0.6), R('m1', 'gen.g2.fm', 0.15), R('mw', 'gen.g1.morph', 0.4)],
    macros: MAC('SHIMMER'),
    lanes: LN({ fx: [FX('delay', { sync: true, div: '1/4d', fb: 0.45, tone: 5000, pp: true, mix: 0.24 }), FX('reverb', { size: 6, damp: 0.3, mix: 0.4 })] }),
    voice: { velSens: 0.4 }, master: { gain: 1.4 },
  } },
  { id: 'strings_ensemble', name: 'Strings · Grange Hall', category: 'pads', state: {
    gens: [{ type: 'analog', shape: 'saw', unison: 7, detune: 9, spread: 0.9, level: 0.75 }, { type: 'analog', shape: 'saw', coarse: -12, unison: 2, detune: 6, spread: 0.5, level: 0.22 }],
    filter: { on: true, type: 'lowpass', cutoff: 3600, res: 0.08, key: 0.4, env: 0.05 },
    amp: E(0.32, 0.6, 0.85, 0.7),
    envs: [E(0.005, 0.4, 0.3, 0.3), E(0.3, 1, 0.6, 0.6)],
    lfos: [{ shape: 'sine', rate: 5.2, retrig: true, fade: 0.7 }],
    mods: [R('lfo1', 'voice.pitch', 0.0035), R('mw', 'lfo.1.amount', 0.5), R('m1', 'filter.cutoff', 0.25)],
    macros: MAC('BOW'),
    lanes: LN({ fx: [FX('eq', { low: -4, lowf: 180, mid: -2, midf: 900, high: 2, highf: 7000 }), FX('chorus', { rate: 0.6, depth: 0.4, mix: 0.35 }), FX('reverb', { size: 3, damp: 0.5, mix: 0.28 })] }),
    voice: { velSens: 0.5 }, master: { gain: 1.3 },
  } },
  { id: 'choir_vox', name: 'Choir · Clapboard Church', category: 'pads', state: {
    gens: [
      { type: 'wavetable', table: 'vocal', morph: 0.15, unison: 3, detune: 10, spread: 0.8, level: 0.7 },
      { type: 'sample', src: 'vox', loop: true, level: 0.6 },
    ],
    filter: { on: true, type: 'lowpass', cutoff: 3200, res: 0.1, key: 0.3 },
    amp: E(0.6, 1, 0.9, 1.4),
    lfos: [{ shape: 'sine', rate: 0.2, retrig: false }, { shape: 'sine', rate: 5, retrig: true, fade: 0.8 }],
    mods: [R('lfo1', 'gen.g1.morph', 0.25), R('lfo2', 'voice.pitch', 0.003), R('m1', 'gen.g1.morph', 0.6)],
    macros: MAC('VOWEL'),
    lanes: LN({ fx: [FX('chorus', { rate: 0.4, depth: 0.35, mix: 0.3 }), FX('eq', { low: -3, lowf: 160, mid: 2, midf: 1100 }), FX('reverb', { size: 4.5, damp: 0.45, mix: 0.38 })] }),
    voice: { velSens: 0.4 }, master: { gain: 1.3 },
  } },
  { id: 'pad_fluorescent', name: 'Pad · Fluorescent Hall', category: 'pads', state: {
    gens: [
      { type: 'analog', shape: 'pulse', pw: 0.3, unison: 2, detune: 5, spread: 0.6, level: 0.3 },
      { type: 'analog', shape: 'sine', level: 0.42 },
      { type: 'analog', shape: 'sine', mode: 'fixed', hz: 120, level: 0.05 },
    ],
    filter: { on: true, type: 'lowpass', cutoff: 1800, res: 0.25, key: 0.3 },
    amp: E(1.2, 1, 0.9, 2),
    lfos: [{ shape: 'sh', rate: 7, retrig: false }],
    mods: [R('lfo1', 'gen.g1.level', 0.06), R('m1', 'fx.fr.mix', 0.5), R('m2', 'filter.cutoff', 0.3)],
    macros: MAC('BUZZ', 'GLARE'),
    lanes: LN({ fx: [FX('ring', { freq: 60, mix: 0.1 }, 'fr'), FX('phaser', { rate: 0.07, depth: 0.7, freq: 600, fb: 0.4, mix: 0.45 }), FX('reverb', { size: 7, damp: 0.7, mix: 0.42 })] }),
    voice: { velSens: 0.2 }, master: { gain: 1.25 },
  } },

  // ── PLUCKS ────────────────────────────────────────────────────────
  { id: 'pluck_bell', name: 'Bell · Mission Tower', category: 'plucks', state: {
    gens: [
      { type: 'analog', shape: 'sine', level: 0.7 },
      { type: 'fm', ratio: 3.5, fmTarget: 'g1', fmAmt: 0.06, level: 0 },
      { type: 'analog', shape: 'sine', ratio: 2.76, level: 0.1 },
    ],
    filter: { on: false },
    amp: E(0.001, 2.4, 0, 1.2),
    envs: [E(0.0008, 0.9, 0, 0.6), E(0.0008, 0.4, 0, 0.3)],
    mods: [R('env1', 'gen.g2.fm', 0.22), R('vel', 'gen.g2.fm', 0.1), R('env2', 'gen.g3.level', 0.15), R('m1', 'gen.g2.fm', 0.2)],
    macros: MAC('CLANG'),
    lanes: LN({ fx: [FX('delay', { sync: true, div: '1/8d', fb: 0.35, tone: 4000, pp: true, mix: 0.22 }), FX('reverb', { size: 3.5, damp: 0.4, mix: 0.3 })] }),
    voice: { velSens: 0.6 }, master: { gain: 1.45 },
  } },
  { id: 'pluck_marimba', name: 'Marimba · Gulf Pier', category: 'plucks', state: {
    gens: [
      { type: 'analog', shape: 'sine', level: 0.8 },
      { type: 'fm', ratio: 4, fmTarget: 'g1', fmAmt: 0.02, level: 0 },
      { type: 'analog', shape: 'sine', ratio: 3.93, level: 0 },
      { type: 'noise', color: 'white', nfilt: 'bandpass', nfreq: 2600, nres: 0.2, level: 0 },
    ],
    filter: { on: false },
    amp: E(0.0008, 0.65, 0, 0.25),
    envs: [E(0.0005, 0.12, 0, 0.1), E(0.0005, 0.08, 0, 0.05), E(0.0005, 0.01, 0, 0.01)],
    mods: [R('env1', 'gen.g2.fm', 0.12), R('env2', 'gen.g3.level', 0.25), R('env3', 'gen.g4.level', 0.25), R('vel', 'gen.g2.fm', 0.06)],
    lanes: LN({ fx: [FX('eq', { low: 1, lowf: 200, mid: 1, midf: 1200 }), FX('reverb', { size: 1.5, damp: 0.5, mix: 0.18 })] }),
    voice: { velSens: 0.7 }, master: { gain: 0.85 },
  } },
  { id: 'arp_chip', name: 'Chip · Arcade Motel', category: 'plucks', state: {
    gens: [{ type: 'analog', shape: 'pulse', pw: 0.25, level: 0.7 }, { type: 'analog', shape: 'square', coarse: -12, level: 0.14 }],
    filter: { on: false },
    amp: E(0.001, 0.18, 0.35, 0.05),
    envs: [E(0.0005, 0.03, 0, 0.02)],
    mods: [R('env1', 'voice.pitch', 0.02), R('m1', 'fx.cc.drive', 0.4)],
    macros: MAC('CRUSH'),
    lanes: LN({ fx: [FX('dist', { mode: 'bitcrush', drive: 0.5, tone: 9000, mix: 0.7 }, 'cc'), FX('delay', { sync: true, div: '1/8d', fb: 0.35, tone: 3500, mix: 0.22 })] }),
    voice: { velSens: 0.2 }, master: { gain: 1.2 },
  } },
  { id: 'pluck_dobro', name: 'Dobro · Resonator Slide', category: 'plucks', state: {
    gens: [{ type: 'sample', src: 'dobro', level: 0.8 }, { type: 'analog', shape: 'saw', level: 0.1 }],
    filter: { on: true, type: 'lowpass', cutoff: 2600, res: 0.15, key: 0.4, env: 0.25 },
    amp: E(0.001, 3, 0, 0.5),
    envs: [E(0.005, 0.4, 0.3, 0.3), E(0.0008, 0.4, 0, 0.3)],
    mods: [R('m1', 'voice.pitch', 2 * 100 / PITCH_RANGE), R('mw', 'voice.pitch', 100 / PITCH_RANGE)],
    macros: MAC('SLIDE +2'),
    lanes: LN({ fx: [FX('tape', { sat: 0.2, wow: 0.15, flutter: 0.1, age: 0.25, hiss: 0.05 }), FX('delay', { sync: false, ms: 110, fb: 0.15, tone: 3000, mix: 0.18 }), FX('reverb', { size: 2.2, damp: 0.5, mix: 0.2 })] }),
    voice: { mode: 'poly', velSens: 0.6 }, master: { gain: 1.3 },
  } },

  // ── LEADS ─────────────────────────────────────────────────────────
  { id: 'lead_saw', name: 'Lead · Highway Saw', category: 'leads', state: {
    gens: [{ type: 'analog', shape: 'saw', unison: 3, detune: 12, spread: 0.5, level: 0.5 }, { type: 'analog', shape: 'square', coarse: -12, level: 0.2 }],
    filter: { on: true, type: 'lowpass', cutoff: 3000, res: 0.25, key: 0.4, env: 0.2 },
    amp: E(0.005, 0.3, 0.85, 0.2),
    envs: [E(0.005, 0.4, 0.3, 0.3), E(0.002, 0.4, 0.3, 0.3)],
    lfos: [{ shape: 'sine', rate: 5.5, retrig: true, fade: 0.3, amount: 0.25 }],
    mods: [R('lfo1', 'voice.pitch', 0.006), R('mw', 'lfo.1.amount', 0.75), R('m1', 'filter.cutoff', 0.3)],
    macros: MAC('BRIGHT'),
    lanes: LN({ fx: [FX('dist', { mode: 'soft', drive: 0.2, tone: 8000, mix: 0.5 }), FX('delay', { sync: true, div: '1/8d', fb: 0.35, tone: 4000, pp: true, mix: 0.2 }), FX('reverb', { size: 2, damp: 0.5, mix: 0.16 })] }),
    voice: { mode: 'legato', glide: 0.06, velSens: 0.4 }, master: { gain: 1.25 },
  } },
  { id: 'lead_square', name: 'Lead · Neon Square', category: 'leads', state: {
    gens: [
      { type: 'analog', shape: 'square', level: 0.4 },
      { type: 'analog', shape: 'pulse', pw: 0.15, fine: 7, level: 0.22 },
      { type: 'analog', shape: 'sine', coarse: -12, level: 0.3 },
    ],
    filter: { on: true, type: 'lowpass', cutoff: 2500, res: 0.2, key: 0.3, env: 0.12 },
    amp: E(0.003, 0.2, 0.8, 0.18),
    lfos: [{ shape: 'sine', rate: 5.2, retrig: true, fade: 0.5, amount: 0.3 }],
    mods: [R('lfo1', 'voice.pitch', 0.005), R('mw', 'lfo.1.amount', 0.7), R('m1', 'filter.cutoff', 0.3)],
    macros: MAC('BRIGHT'),
    lanes: LN({ fx: [FX('chorus', { rate: 0.4, depth: 0.2, mix: 0.2 }), FX('delay', { sync: true, div: '1/4', fb: 0.3, tone: 3500, mix: 0.18 }), FX('reverb', { size: 2.4, damp: 0.5, mix: 0.18 })] }),
    voice: { mode: 'legato', glide: 0.05, velSens: 0.4 }, master: { gain: 1.3 },
  } },
  { id: 'lead_whistle', name: 'Lead · Lonesome Whistle', category: 'leads', state: {
    gens: [
      { type: 'analog', shape: 'sine', level: 0.7 },
      { type: 'noise', color: 'pink', nfilt: 'bandpass', nfreq: 2200, nres: 0.35, level: 0.07 },
      { type: 'analog', shape: 'triangle', coarse: 12, level: 0.05 },
    ],
    filter: { on: false },
    amp: E(0.09, 0.3, 0.85, 0.35),
    envs: [E(0.0008, 0.16, 0, 0.1)],
    lfos: [{ shape: 'sine', rate: 5.2, retrig: true, fade: 0.45 }],
    mods: [R('lfo1', 'voice.pitch', 0.005), R('env1', 'voice.pitch', -0.012), R('mw', 'gen.g2.level', 0.15), R('m1', 'fx.wv.mix', 0.4)],
    macros: MAC('DISTANCE'),
    lanes: LN({ fx: [FX('delay', { sync: true, div: '1/4d', fb: 0.3, tone: 3000, pp: true, mix: 0.2 }), FX('reverb', { size: 5, damp: 0.4, mix: 0.38 }, 'wv')] }),
    voice: { mode: 'legato', glide: 0.08, velSens: 0.4 }, master: { gain: 1.05 },
  } },

  // ── AMBIENT ───────────────────────────────────────────────────────
  { id: 'drone_dark', name: 'Drone · Below Sea Level', category: 'ambient', state: {
    gens: [
      { type: 'analog', shape: 'saw', coarse: -12, unison: 3, detune: 8, spread: 0.7, level: 0.4 },
      { type: 'analog', shape: 'sine', coarse: -24, level: 0.42 },
      { type: 'noise', color: 'brown', nfilt: 'lowpass', nfreq: 300, level: 0.18 },
    ],
    filter: { on: true, type: 'lowpass', cutoff: 380, res: 0.3, key: 0.2 },
    amp: E(2.5, 2, 0.9, 4),
    lfos: [{ shape: 'sine', rate: 0.05, retrig: false }, { shape: 'triangle', rate: 0.11, retrig: false }],
    mods: [R('lfo1', 'filter.cutoff', 0.1), R('lfo2', 'gen.g1.pan', 0.3), R('m1', 'filter.cutoff', 0.3), R('mw', 'filter.cutoff', 0.25)],
    macros: MAC('OPEN'),
    lanes: LN({ fx: [FX('comb', { freq: 55, fb: 0.6, damp: 0.5, mix: 0.25 }), FX('reverb', { size: 8, damp: 0.6, mix: 0.45 })] }),
    voice: { velSens: 0.2 }, master: { gain: 1.4 },
  } },
  { id: 'drone_bayou', name: 'Drone · Bayou Night', category: 'ambient', state: {
    gens: [
      { type: 'wavetable', table: 'reed', morph: 0.3, coarse: -12, unison: 2, detune: 6, spread: 0.6, level: 0.4 },
      { type: 'analog', shape: 'sine', coarse: -12, fine: 3, level: 0.3 },
      { type: 'noise', color: 'brown', nfilt: 'lowpass', nfreq: 500, level: 0.2 },
      { type: 'noise', color: 'white', nfilt: 'bandpass', nfreq: 4800, nres: 0.7, level: 0.05, lane: 'B' },
    ],
    filter: { on: true, type: 'lowpass', cutoff: 1400, res: 0.1, key: 0.2, lanes: 'A' },
    amp: E(3, 2, 0.9, 4),
    lfos: [{ shape: 'sine', rate: 0.09, retrig: false }, { shape: 'square', rate: 26, retrig: false }, { shape: 'sine', rate: 0.07, retrig: false, uni: true }],
    mods: [R('lfo1', 'gen.g1.morph', 0.3), R('lfo2', 'gen.g4.level', 0.05), R('lfo3', 'lane.B.gain', -0.6), R('m1', 'lane.B.gain', 0.6), R('m2', 'fx.bt.wow', 0.5)],
    macros: MAC('CICADAS', 'WARP'),
    lanes: LN({ fx: [FX('tape', { sat: 0.25, wow: 0.5, flutter: 0.2, age: 0.4, hiss: 0.15 }, 'bt'), FX('phaser', { rate: 0.05, depth: 0.6, freq: 500, fb: 0.3, mix: 0.35 }), FX('reverb', { size: 6, damp: 0.6, mix: 0.4 })] },
      { gain: 0.9, fx: [FX('width', { width: 1.7 }), FX('reverb', { size: 3, damp: 0.3, mix: 0.5 })] }),
    voice: { velSens: 0.2 }, master: { gain: 1.45 },
  } },

  // ── FX ────────────────────────────────────────────────────────────
  { id: 'fx_riser', name: 'Riser · Headlights', category: 'fx', state: {
    gens: [{ type: 'noise', color: 'white', level: 0.4 }, { type: 'analog', shape: 'saw', unison: 5, detune: 25, spread: 0.9, level: 0.3 }],
    filter: { on: true, type: 'lowpass', cutoff: 500, res: 0.45, key: 0 },
    amp: E(2.5, 0.1, 1, 1.2),
    envs: [E(4, 0.1, 1, 1)],
    mods: [R('env1', 'filter.cutoff', 0.55), R('env1', 'voice.pitch', 0.25), R('m1', 'filter.res', 0.3)],
    macros: MAC('SCREAM'),
    lanes: LN({ fx: [FX('flanger', { rate: 0.25, depth: 0.6, fb: 0.5, mix: 0.35 }), FX('delay', { sync: true, div: '1/8', fb: 0.4, tone: 5000, pp: true, mix: 0.2 }), FX('width', { width: 1.5 }), FX('reverb', { size: 5, damp: 0.4, mix: 0.35 })] }),
    voice: { velSens: 0.2 }, master: { gain: 1.0 },
  } },
  { id: 'fx_noise_sweep', name: 'Sweep · Static Tide', category: 'fx', state: {
    gens: [{ type: 'noise', color: 'pink', level: 1 }],
    filter: { on: true, type: 'lowpass', cutoff: 500, res: 0.6, key: 0 },
    amp: E(0.4, 1, 0.9, 1.5),
    lfos: [{ shape: 'triangle', rate: 0.3, retrig: true, uni: true }],
    mods: [R('lfo1', 'filter.cutoff', 0.45), R('m1', 'lfo.1.rate', 0.2), R('note', 'filter.cutoff', 0.5)],
    macros: MAC('SPEED'),
    lanes: LN({ fx: [FX('phaser', { rate: 0.2, depth: 0.6, freq: 900, fb: 0.5, mix: 0.4 }), FX('delay', { sync: true, div: '1/4', fb: 0.4, tone: 4000, pp: true, mix: 0.25 }), FX('width', { width: 1.6 }), FX('reverb', { size: 4, damp: 0.5, mix: 0.35 })] }),
    voice: { velSens: 0.3 }, master: { gain: 1.3 },
  } },
];

// ═══════════════════════════════════════════════════════════════════
// Editor — mountEditor(el) builds the whole patch editor inside any
// element (standalone page, or the DAW's side panel). Scoped .fg-* CSS.
// ═══════════════════════════════════════════════════════════════════
const EDITOR_CSS = `
.fg-root { --fg-bg0:#050304; --fg-bg1:#0e0908; --fg-ink:#1a1410; --fg-rule:#553318; --fg-gold:#d8a060; --fg-hi:#ffd896;
  --fg-text:#c8a878; --fg-dim:#7a5828; --fg-rust:#c87633; --fg-red:#c64a3a; --fg-em:#a8e89c;
  font-family:"Courier New",monospace; color:var(--fg-text); background:var(--fg-bg0); font-size:11px;
  height:100%; min-height:0; display:flex; flex-direction:column; box-sizing:border-box; }
.fg-root * { box-sizing:border-box; }
.fg-bar { display:flex; gap:5px; align-items:center; flex-wrap:wrap; padding:5px 8px; border-bottom:1px solid var(--fg-rule); }
.fg-bar .fg-name { width:150px; }
.fg-main { flex:1; min-height:0; display:grid; grid-template-columns:minmax(0,1.12fr) minmax(0,1fr) minmax(0,1.12fr); }
.fg-col { overflow-y:auto; min-height:0; padding:4px 8px 10px; border-right:1px solid var(--fg-rule); }
.fg-col:last-child { border-right:none; }
.fg-root.fg-narrow .fg-main { display:block; overflow-y:auto; }
.fg-root.fg-narrow .fg-col { overflow:visible; border-right:none; border-bottom:1px solid var(--fg-rule); }
.fg-h { color:var(--fg-gold); font-size:11px; letter-spacing:.16em; border-bottom:1px solid var(--fg-rule); margin:8px 0 5px; padding-bottom:3px; display:flex; align-items:center; gap:5px; flex-wrap:wrap; }
.fg-sp { flex:1; }
.fg-card { background:var(--fg-bg1); border:1px solid var(--fg-rule); padding:4px 6px; margin-bottom:6px; }
.fg-card.off { opacity:.5; }
.fg-ch { display:flex; gap:4px; align-items:center; margin-bottom:3px; }
.fg-ch b { color:var(--fg-hi); font-weight:normal; letter-spacing:.06em; }
.fg-row { display:flex; gap:4px; align-items:center; flex-wrap:wrap; margin:2px 0; }
.fg-gbody { display:flex; gap:6px; align-items:flex-start; }
.fg-thumb { width:96px; height:36px; border:1px solid var(--fg-rule); background:#0a0605; flex:none; }
.fg-knobs { display:flex; flex-wrap:wrap; gap:1px 2px; align-items:flex-start; }
.fg-knob { width:46px; display:flex; flex-direction:column; align-items:center; user-select:none; -webkit-user-select:none; touch-action:none; cursor:ns-resize; position:relative; }
.fg-knob svg { width:38px; height:38px; display:block; overflow:visible; }
.fg-knob.fg-over svg { filter:drop-shadow(0 0 4px var(--fg-hi)); }
.fg-kl { font-size:9px; letter-spacing:.04em; color:var(--fg-dim); white-space:nowrap; overflow:hidden; max-width:48px; text-overflow:ellipsis; }
.fg-kv { font-size:9px; color:var(--fg-hi); white-space:nowrap; }
.fg-ktr { fill:none; stroke:#2c1d10; stroke-width:3.2; }
.fg-kva { fill:none; stroke:var(--fg-gold); stroke-width:3.2; }
.fg-kma { fill:none; stroke-width:2.2; stroke-linecap:round; }
.fg-kma.off { opacity:.3; }
.fg-kptr { stroke:var(--fg-hi); stroke-width:2; stroke-linecap:round; }
.fg-karm { fill:none; stroke:var(--fg-hi); stroke-width:1; stroke-dasharray:2 2; opacity:.7; }
.fg-root button { background:var(--fg-ink); color:var(--fg-hi); border:1px solid var(--fg-gold); padding:2px 7px; font-family:inherit; font-size:10px; letter-spacing:.06em; cursor:pointer; }
.fg-root button:hover { background:var(--fg-gold); color:var(--fg-ink); }
.fg-root button.dim { color:var(--fg-dim); border-color:var(--fg-rule); }
.fg-root button.dim:hover { color:var(--fg-ink); }
.fg-root button.on { background:var(--fg-rust); color:var(--fg-ink); border-color:var(--fg-hi); }
.fg-root button.fg-ib { padding:1px 5px; border-color:var(--fg-rule); color:var(--fg-dim); }
.fg-root button.fg-tog { padding:1px 5px; min-width:20px; }
.fg-root select, .fg-root input[type=text], .fg-root input[type=number] { background:var(--fg-ink); color:var(--fg-hi); border:1px solid var(--fg-rule); font-family:inherit; font-size:10px; padding:1px 3px; max-width:100%; }
.fg-root input[type=number] { width:58px; }
.fg-root input[type=range] { accent-color:var(--fg-rust); }
.fg-root label { cursor:pointer; color:var(--fg-dim); font-size:10px; display:inline-flex; gap:3px; align-items:center; }
.fg-chips { display:flex; flex-wrap:wrap; gap:3px; margin:3px 0; }
.fg-chip { padding:2px 6px; border:1px solid var(--c); color:var(--c); font-size:10px; cursor:grab; user-select:none; -webkit-user-select:none; letter-spacing:.05em; position:relative; touch-action:none; }
.fg-chip.sel { box-shadow:inset 0 -3px 0 var(--c); }
.fg-chip.armed { background:var(--c); color:#1a1410; animation:fgpulse 1s infinite; }
.fg-chip sup { font-size:8px; margin-left:2px; opacity:.8; }
@keyframes fgpulse { 50% { box-shadow:0 0 10px var(--c); } }
.fg-hint { color:var(--fg-dim); font-size:10px; font-style:italic; min-height:13px; margin:2px 0; }
.fg-hint.armed { color:var(--fg-hi); }
.fg-detail { border:1px solid var(--fg-rule); background:var(--fg-bg1); padding:4px 6px; }
.fg-prev { width:120px; height:46px; border:1px solid var(--fg-rule); background:#0a0605; flex:none; }
.fg-mrow { display:grid; grid-template-columns:10px minmax(54px,auto) minmax(0,1fr) 72px 50px 18px 22px; gap:4px; align-items:center; padding:2px 0; border-bottom:1px dotted #2c1d10; font-size:10px; }
.fg-mrow .dot { width:8px; height:8px; border-radius:50%; }
.fg-mrow .dst { overflow:hidden; text-overflow:ellipsis; white-space:nowrap; color:var(--fg-text); }
.fg-mrow input[type=range] { width:100%; margin:0; }
.fg-mrow input[type=number] { width:50px; }
.fg-tabs { display:flex; gap:3px; }
.fg-scope { width:100%; height:112px; display:block; border:1px solid var(--fg-rule); background:#0a0605; }
.fg-note { color:var(--fg-dim); font-size:10px; font-style:italic; line-height:1.4; }
.fg-pat { display:grid; grid-template-columns:repeat(16,1fr); gap:2px; margin:3px 0; }
.fg-pat i { height:14px; border:1px solid var(--fg-rule); cursor:pointer; }
.fg-pat i.x { background:var(--fg-rust); border-color:var(--fg-gold); }
.fg-pat i:nth-child(4n+1) { border-left-color:var(--fg-gold); }
.fg-status { color:var(--fg-dim); font-size:10px; margin-left:auto; white-space:nowrap; }
.fg-macros { display:grid; grid-template-columns:repeat(4, 1fr); gap:2px; }
.fg-macros .fg-knob { width:100%; }
.fg-macros .fg-kl { max-width:100%; }
.fg-root.fg-arming .fg-knob.fg-mt svg { filter:drop-shadow(0 0 2px rgba(255,216,150,.55)); }
`;

function h(tag, attrs, ...kids) {
  const e = document.createElement(tag);
  if (attrs) for (const k in attrs) {
    const v = attrs[k];
    if (v == null || v === false) continue;
    if (k === 'class') e.className = v;
    else if (k === 'style') e.style.cssText = v;
    else if (k === 'text') e.textContent = v;
    else if (k.startsWith('on') && typeof v === 'function') e.addEventListener(k.slice(2), v);
    else e.setAttribute(k, v === true ? '' : v);
  }
  for (const c of kids.flat()) if (c != null && c !== false) e.appendChild(typeof c === 'string' ? document.createTextNode(c) : c);
  return e;
}
function selEl(opts, value, onchange, title) {
  const s = h('select', { title });
  for (const o of opts) { const [v, l] = Array.isArray(o) ? o : [o, o]; s.appendChild(h('option', { value: v, text: l })); }
  s.value = value;
  s.addEventListener('change', () => onchange(s.value));
  return s;
}
function chk(label, on, onchange, title) {
  const i = h('input', { type: 'checkbox' }); i.checked = !!on;
  i.addEventListener('change', () => onchange(i.checked));
  return h('label', { title }, i, label);
}
const NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
const noteName = n => NOTE_NAMES[((Math.round(n) % 12) + 12) % 12] + (Math.floor(Math.round(n) / 12) - 1);
function fmtVal(v, sp) {
  if (!isNum(v)) return '—';
  switch (sp.unit) {
    case 'Hz': return v >= 1000 ? (v / 1000).toFixed(v >= 10000 ? 1 : 2) + 'k' : v >= 100 ? v.toFixed(0) : v.toFixed(v >= 10 ? 1 : 2);
    case 's': return v < 1 ? (v < 0.01 ? (v * 1000).toFixed(1) : Math.round(v * 1000)) + 'ms' : v.toFixed(2) + 's';
    case 'ms': return v >= 1000 ? (v / 1000).toFixed(2) + 's' : Math.round(v) + 'ms';
    case '%': return Math.round(v * 100) + '%';
    case 'st': return (v > 0 ? '+' : '') + Math.round(v) + 'st';
    case 'ct': return (v > 0 ? '+' : '') + Math.round(v) + 'ct';
    case 'dB': return (v > 0 ? '+' : '') + v.toFixed(1);
    case 'pan': return Math.abs(v) < 0.02 ? 'C' : (v < 0 ? 'L' : 'R') + Math.round(Math.abs(v) * 100);
    case 'x': return (v < 10 ? v.toFixed(3) : v.toFixed(2)).replace(/0+$/, '').replace(/\.$/, '') + 'x';
    case 'note': return noteName(v);
    case 'v': return String(Math.round(v));
    case ':1': return v.toFixed(1) + ':1';
  }
  return v.toFixed(2);
}
function toNorm(sp, v) {
  if (sp.curve === 'log') return clamp(Math.log(v / sp.min) / Math.log(sp.max / sp.min), 0, 1);
  if (sp.curve === 'sq') return clamp(Math.sqrt((v - sp.min) / (sp.max - sp.min)), 0, 1);
  return clamp((v - sp.min) / (sp.max - sp.min), 0, 1);
}
function fromNorm(sp, n) {
  n = clamp(n, 0, 1);
  let v = sp.curve === 'log' ? sp.min * Math.pow(sp.max / sp.min, n) : sp.curve === 'sq' ? sp.min + n * n * (sp.max - sp.min) : sp.min + n * (sp.max - sp.min);
  if (sp.step) v = Math.round(v / sp.step) * sp.step;
  return clamp(v, sp.min, sp.max);
}
const KA0 = -0.75 * Math.PI, KA1 = 0.75 * Math.PI;
function arcPath(r, a0, a1) {
  const x0 = 20 + r * Math.sin(a0), y0 = 20 - r * Math.cos(a0), x1 = 20 + r * Math.sin(a1), y1 = 20 - r * Math.cos(a1);
  return `M${x0.toFixed(2)} ${y0.toFixed(2)} A${r} ${r} 0 ${a1 - a0 > Math.PI ? 1 : 0} 1 ${x1.toFixed(2)} ${y1.toFixed(2)}`;
}
const defaultDepth = dst => /pitch$/.test(dst) ? 0.05 : 0.25;
const slugify = s => String(s || 'patch').toLowerCase().replace(/[^a-z0-9]+/g, '_').replace(/^_|_$/g, '').slice(0, 40) || 'patch';

// ── User presets (localStorage, shared by the standalone page + DAW) ─
const USER_KEY = 'mm_forge_user_presets';
function userPresets() {
  try { const a = JSON.parse(localStorage.getItem(USER_KEY) || '[]'); return Array.isArray(a) ? a.filter(p => p && p.name && p.state) : []; }
  catch (e) { return []; }
}
function saveUserPresets(list) {
  try { localStorage.setItem(USER_KEY, JSON.stringify(list)); return true; } catch (e) { return false; }
}

class Knob {
  // o: {label, spec, get(), set(v), target?, after?, title?}
  constructor(ed, o) {
    this.ed = ed; this.o = o; this.sp = o.spec;
    this.el = h('div', { class: 'fg-knob' + (o.target ? ' fg-mt' : ''),
      title: (o.title || o.label) + ' · drag ↕ (shift = fine) · dbl-click resets' + (o.target ? ' · drop a modulator chip here, or drag the outer ring to set depth' : '') });
    this.sv = h('div');
    this.vl = h('div', { class: 'fg-kv' });
    this.el.append(this.sv, h('div', { class: 'fg-kl', text: o.label }), this.vl);
    this.el.addEventListener('pointerdown', e => this._down(e));
    this.el.addEventListener('pointermove', e => this._move(e));
    this.el.addEventListener('pointerup', e => this._up(e));
    this.el.addEventListener('pointercancel', e => this._up(e));
    this.el.addEventListener('dblclick', () => { if (this.ed.armed) return; this.o.set(this.sp.def); this.draw(); if (this.o.after) this.o.after(); });
    this.el.addEventListener('wheel', e => this._wheel(e), { passive: false });
    if (o.target) {
      this.el.addEventListener('dragover', e => { if (e.dataTransfer && [...e.dataTransfer.types].includes('text/forge-mod')) { e.preventDefault(); this.el.classList.add('fg-over'); } });
      this.el.addEventListener('dragleave', () => this.el.classList.remove('fg-over'));
      this.el.addEventListener('drop', e => {
        this.el.classList.remove('fg-over');
        const src = e.dataTransfer.getData('text/forge-mod'); if (!src) return;
        e.preventDefault();
        this.ed.s.addMod(src, o.target, defaultDepth(o.target));
        this.ed.sel = src;
        this.ed._modsChanged();
      });
    }
    this.draw();
  }
  draw() {
    const sp = this.sp, v = this.o.get(), n = toNorm(sp, isNum(v) ? v : sp.def), a = KA0 + n * (KA1 - KA0);
    const ac = sp.bip ? KA0 + toNorm(sp, 0) * (KA1 - KA0) : KA0;
    let s = `<svg viewBox="0 0 40 40"><path d="${arcPath(13, KA0, KA1)}" class="fg-ktr"/>`;
    if (Math.abs(a - ac) > 0.01) s += `<path d="${arcPath(13, Math.min(a, ac), Math.max(a, ac))}" class="fg-kva"/>`;
    const t = this.o.target;
    if (t) {
      const rs = this.ed.s.state.mods.filter(m => m.dst === t), disp = this.ed.s._disp(t);
      rs.forEach((m, i) => {
        const r = 17.4 + (i % 3) * 1.9, b = clamp(a + m.depth * disp * (KA1 - KA0), KA0, KA1), col = srcColor(m.src);
        if (Math.abs(b - a) > 0.02) s += `<path d="${arcPath(r, Math.min(a, b), Math.max(a, b))}" stroke="${col}" class="fg-kma${m.on === false ? ' off' : ''}"/>`;
        else s += `<circle cx="${(20 + r * Math.sin(a)).toFixed(2)}" cy="${(20 - r * Math.cos(a)).toFixed(2)}" r="1.4" fill="${col}"/>`;
      });
      if (this.ed.armed) s += `<circle cx="20" cy="20" r="19.5" class="fg-karm"/>`;
    }
    s += `<line x1="${(20 + 5 * Math.sin(a)).toFixed(2)}" y1="${(20 - 5 * Math.cos(a)).toFixed(2)}" x2="${(20 + 11.5 * Math.sin(a)).toFixed(2)}" y2="${(20 - 11.5 * Math.cos(a)).toFixed(2)}" class="fg-kptr"/></svg>`;
    this.sv.innerHTML = s;
    this.vl.textContent = fmtVal(v, sp);
  }
  _down(e) {
    if (e.button !== 0) return;
    e.preventDefault();
    const svg = this.sv.firstChild, rc = svg.getBoundingClientRect();
    const dist = Math.hypot(e.clientX - (rc.left + rc.width / 2), e.clientY - (rc.top + rc.height / 2)) * 40 / Math.max(1, rc.width);
    const t = this.o.target, s = this.ed.s;
    let route = null;
    if (t && this.ed.armed) {
      route = s.state.mods.find(m => m.src === this.ed.armed && m.dst === t);
      if (!route) { const id = s.addMod(this.ed.armed, t, defaultDepth(t)); route = s.state.mods.find(m => m.id === id) || null; this.ed._modsChanged(); }
    } else if (t && dist > 15.2) {
      const rs = s.state.mods.filter(m => m.dst === t);
      route = rs.find(m => m.src === this.ed.sel) || rs[rs.length - 1] || null;
    }
    this.drag = { y: e.clientY, route, start: route ? route.depth : toNorm(this.sp, this.o.get()), sv: this.o.get() };
    try { this.el.setPointerCapture(e.pointerId); } catch (err) { /* ok */ }
  }
  _move(e) {
    const d = this.drag; if (!d) return;
    const dy = d.y - e.clientY, k = e.shiftKey ? 1 / 700 : 1 / 160;
    if (d.route) {
      const disp = this.ed.s._disp(this.o.target);
      this.ed.s.setModDepth(d.route.id, clamp(d.start + dy * k / disp, -1, 1));
      this.draw(); this.ed._matrixSync(d.route.id);
    } else {
      let v = fromNorm(this.sp, d.start + dy * k);
      if (this.sp.step && Math.abs(dy) > 2 && v === d.sv) v = clamp(d.sv + Math.sign(dy) * this.sp.step * Math.floor(Math.abs(dy) / 12), this.sp.min, this.sp.max);
      if (v !== this.o.get()) { this.o.set(v); this.draw(); if (this.o.after) this.o.after(); }
    }
  }
  _up(e) {
    const d = this.drag; if (!d) return;
    this.drag = null;
    try { this.el.releasePointerCapture(e.pointerId); } catch (err) { /* ok */ }
    if (d.route) this.ed._modsChanged();
  }
  _wheel(e) {
    e.preventDefault();
    const dir = e.deltaY < 0 ? 1 : -1, sp = this.sp, cur = this.o.get();
    const v = sp.step ? clamp(cur + dir * sp.step, sp.min, sp.max) : fromNorm(sp, toNorm(sp, cur) + dir * (e.shiftKey ? 0.004 : 0.025));
    this.o.set(v); this.draw(); if (this.o.after) this.o.after();
  }
}

class ForgeEditor {
  constructor(synth, el, opts) {
    this.s = synth; this.host = el; this.opts = opts || {};
    this.armed = null; this.sel = 'env1'; this.lane = 'A'; this.knobs = []; this.offs = []; this.dead = false;
    this.libList = [];
    if (!document.getElementById('forge-editor-style')) {
      const st = document.createElement('style'); st.id = 'forge-editor-style'; st.textContent = EDITOR_CSS; document.head.appendChild(st);
    }
    this.root = h('div', { class: 'fg-root' });
    el.appendChild(this.root);
    this._lastRender = 0; this._lastMods = 0;
    this.offs.push(synth.on('state', () => this.render()));
    this.offs.push(synth.on('macro', e => { const k = this.macroKnobs && this.macroKnobs[e.i]; if (k && !k.drag) k.draw(); }));
    // Follow edits made by someone else (the DAW, MIDI): structural changes
    // re-render on the next frame unless this editor already did; plain
    // value changes redraw the matching knobs.
    this.offs.push(synth.on('change', e => {
      if (e.structure || e.path === '*') { const at = performance.now(); requestAnimationFrame(() => { if (!this.dead && this._lastRender < at) this.render(); }); return; }
      if (e.path) this.knobs.forEach(k => { if (k.o.path === e.path && !k.drag) k.draw(); });
    }));
    this.offs.push(synth.on('mods', () => { const at = performance.now(); requestAnimationFrame(() => { if (!this.dead && this._lastMods < at && this._lastRender < at) this._modsChanged(); }); }));
    this._onKey = e => { if (e.key === 'Escape' && this.armed) this.arm(null); };
    window.addEventListener('keydown', this._onKey);
    try { this.an = synth.ctx.createAnalyser(); this.an.fftSize = 2048; this.an.smoothingTimeConstant = 0.7; synth.output.connect(this.an); } catch (e) { this.an = null; }
    if (typeof ResizeObserver !== 'undefined') { this.ro = new ResizeObserver(() => this._resize()); this.ro.observe(this.root); }
    this.render();
    this._loop = this._loop.bind(this);
    this._last = 0;
    this.raf = requestAnimationFrame(this._loop);
    this._loadLib();
  }
  destroy() {
    if (this.dead) return;
    this.dead = true;
    cancelAnimationFrame(this.raf);
    this.offs.forEach(f => f()); this.offs = [];
    window.removeEventListener('keydown', this._onKey);
    if (this.ro) this.ro.disconnect();
    if (this.an) { try { this.s.output.disconnect(this.an); } catch (e) { /* ok */ } }
    this.root.remove();
    this.knobs = [];
    this.s._editors.delete(this);
  }
  _resize() { const w = this.root.clientWidth; this.root.classList.toggle('fg-narrow', w > 0 && w < 860); }
  async _loadLib() {
    const AKr = akLib();
    if (!AKr) return;
    try {
      const all = await AKr.lib.list();
      this.libList = all.filter(r => r.frames && r.sampleRate).slice(0, 80).map(r => ({ id: r.id, name: r.name || (r.meta && r.meta.title) || r.id, kind: r.kind }));
      if (!this.dead && this.s.state.gens.some(g => g.type === 'sample')) this.render();
    } catch (e) { /* library unavailable */ }
  }
  arm(src) {
    this.armed = src;
    this.root.classList.toggle('fg-arming', !!src);
    this.knobs.forEach(k => k.o.target && k.draw());
    this._renderChips();
  }
  _k(label, spec, path, target, after, extra) {
    const s = this.s;
    const k = new Knob(this, Object.assign({ label, spec, target, after, path, get: () => s.getParam(path), set: v => s.setParam(path, v) }, extra || {}));
    this.knobs.push(k);
    return k.el;
  }
  _modsChanged() {
    this._lastMods = performance.now();
    this.knobs.forEach(k => k.o.target && !k.drag && k.draw());
    this._renderMatrix();
    this._renderChips();
    this._renderModDetail();
  }

  // ── whole editor ────────────────────────────────────────────────
  render() {
    if (this.dead) return;
    this._lastRender = performance.now();
    const scroll = [...this.root.querySelectorAll('.fg-col')].map(c => c.scrollTop);
    this.root.textContent = '';
    this.knobs = [];
    if (this.opts.presets !== false) this.root.appendChild(this._presetBar());
    const main = h('div', { class: 'fg-main' }, this._colGen(), this._colMid(), this._colFx());
    this.root.appendChild(main);
    [...this.root.querySelectorAll('.fg-col')].forEach((c, i) => { c.scrollTop = scroll[i] || 0; });
    this._resize();
  }

  _presetBar() {
    const s = this.s, bar = h('div', { class: 'fg-bar' });
    const sel = h('select', { title: 'factory + user presets' });
    sel.appendChild(h('option', { value: '', text: '— preset —' }));
    const order = ['drums', 'bass', 'keys', 'pads', 'plucks', 'leads', 'ambient', 'fx'];
    const cats = {};
    s.presetList.forEach(p => (cats[p.category] = cats[p.category] || []).push(p));
    [...order, ...Object.keys(cats).filter(c => !order.includes(c))].forEach(cat => {
      if (!cats[cat]) return;
      const og = h('optgroup', { label: cat.toUpperCase() });
      cats[cat].forEach(p => og.appendChild(h('option', { value: 'f:' + p.id, text: p.name })));
      sel.appendChild(og);
    });
    const ups = userPresets();
    if (ups.length) { const og = h('optgroup', { label: 'USER' }); ups.forEach(p => og.appendChild(h('option', { value: 'u:' + p.name, text: p.name }))); sel.appendChild(og); }
    sel.value = s.presetId ? 'f:' + s.presetId : (ups.some(p => p.name === s.state.name) ? 'u:' + s.state.name : '');
    const load = val => {
      if (!val) return;
      if (val.startsWith('f:')) s.loadPreset(val.slice(2));
      else { const p = userPresets().find(x => x.name === val.slice(2)); if (p) s.setState(Object.assign({}, p.state, { name: p.name })); }
    };
    sel.addEventListener('change', () => load(sel.value));
    const step = d => { const opts = [...sel.options].filter(o => o.value); let i = opts.findIndex(o => o.value === sel.value); i = (i + d + opts.length) % opts.length; sel.value = opts[i].value; load(sel.value); };
    const name = h('input', { type: 'text', class: 'fg-name', title: 'patch name', value: s.state.name });
    name.addEventListener('change', () => s.setParam('name', name.value.trim() || 'INIT'));
    const msg = h('span', { class: 'fg-note' });
    const flash = t => { msg.textContent = t; setTimeout(() => { if (msg.textContent === t) msg.textContent = ''; }, 2500); };
    const file = h('input', { type: 'file', accept: '.json,application/json', style: 'display:none' });
    file.addEventListener('change', () => {
      const f = file.files && file.files[0]; if (!f) return;
      const rd = new FileReader();
      rd.onload = () => { try { const j = JSON.parse(rd.result); s.setState(j.state && j.state.gens ? j.state : j); flash('imported ' + f.name); } catch (e) { flash('not a FORGE preset'); } };
      rd.readAsText(f); file.value = '';
    });
    this.status = h('span', { class: 'fg-status' });
    bar.append(
      h('button', { class: 'dim', title: 'previous preset', text: '◀', onclick: () => step(-1) }), sel,
      h('button', { class: 'dim', title: 'next preset', text: '▶', onclick: () => step(1) }), name,
      h('button', { title: 'save as a user preset (this browser)', text: 'SAVE', onclick: () => {
        const nm = (name.value || '').trim() || 'my patch';
        s.setParam('name', nm);
        const list = userPresets().filter(p => p.name !== nm);
        list.push({ name: nm, category: 'user', state: s.getState() });
        flash(saveUserPresets(list) ? 'saved "' + nm + '"' : 'could not save (storage blocked)');
        this.render();
      } }),
      h('button', { class: 'dim', title: 'delete this user preset', text: 'DEL', onclick: () => {
        const nm = s.state.name, list = userPresets(); if (!list.some(p => p.name === nm)) { flash('not a user preset'); return; }
        saveUserPresets(list.filter(p => p.name !== nm)); flash('deleted "' + nm + '"'); this.render();
      } }),
      h('button', { class: 'dim', title: 'download the patch as JSON', text: '⇩ JSON', onclick: () => {
        const blob = new Blob([JSON.stringify({ forge: 1, name: s.state.name, state: s.getState() }, null, 1)], { type: 'application/json' });
        const a = h('a', { href: URL.createObjectURL(blob), download: slugify(s.state.name) + '.forge.json' });
        document.body.appendChild(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(a.href), 4000);
      } }),
      h('button', { class: 'dim', title: 'load a patch JSON file', text: '⇪ JSON', onclick: () => file.click() }), file,
      h('button', { class: 'dim', title: 'start from the init patch', text: 'INIT', onclick: () => s.setState(DEFAULT_STATE) }),
      msg, this.status);
    return bar;
  }

  // ── generators ─────────────────────────────────────────────────
  _colGen() {
    const s = this.s, S = s.state;
    const add = selEl([['', '+ GENERATOR'], ...Object.keys(GEN_TYPES).map(k => [k, GEN_TYPES[k]])], '', v => { if (v && s.addGenerator(v)) this.render(); }, 'add a generator (max 6)');
    const col = h('div', { class: 'fg-col' }, h('div', { class: 'fg-h' }, 'GENERATORS', h('span', { class: 'fg-sp' }), S.gens.length < MAX_GENS ? add : h('span', { class: 'fg-note', text: 'max 6' })));
    S.gens.forEach((g, i) => col.appendChild(this._genCard(g, i)));
    if (!S.gens.length) col.appendChild(h('div', { class: 'fg-note', text: 'no generators — add one above.' }));
    col.appendChild(h('div', { class: 'fg-note', text: 'analog · wavetable (POS morphs the table) · noise · sample (built-ins or your library) · FM op (modulates another generator\'s frequency; its LEVEL is what you hear of it).' }));
    return col;
  }
  _genCard(g, i) {
    const s = this.s, id = g.id, P = k => `gen.${id}.${k}`, S = s.state;
    const thumb = h('canvas', { class: 'fg-thumb', width: 192, height: 72 });
    const redraw = () => this._drawThumb(thumb, g);
    const set = (k, v, re) => { s.setParam(P(k), v); if (re) this.render(); else redraw(); };
    const head = h('div', { class: 'fg-ch' },
      h('button', { class: 'fg-tog' + (g.on ? ' on' : ''), title: 'generator on / off', text: g.on ? '●' : '○', onclick: () => set('on', !g.on, true) }),
      h('b', { text: String(i + 1) }),
      selEl(Object.keys(GEN_TYPES).map(k => [k, GEN_TYPES[k]]), g.type, v => set('type', v, true), 'generator type'),
      selEl(LANES.map(L => [L, '→ ' + L]), g.lane, v => set('lane', v, true), 'output lane'),
      h('span', { class: 'fg-sp' }),
      h('button', { class: 'fg-ib', text: '▲', title: 'move up', onclick: () => { s.moveGenerator(id, -1); this.render(); } }),
      h('button', { class: 'fg-ib', text: '▼', title: 'move down', onclick: () => { s.moveGenerator(id, 1); this.render(); } }),
      h('button', { class: 'fg-ib', text: '✕', title: 'remove', onclick: () => { s.removeGenerator(id); this.render(); } }));
    const opts = h('div', { class: 'fg-row' });
    const ks = h('div', { class: 'fg-knobs' });
    ks.append(this._k('LEVEL', GEN_SPEC.level, P('level'), `gen.${id}.level`));
    if (g.type !== 'noise') ks.append(this._k('TUNE', GEN_SPEC.coarse, P('coarse'), `gen.${id}.pitch`), this._k('FINE', GEN_SPEC.fine, P('fine')));
    ks.append(this._k('PAN', GEN_SPEC.pan, P('pan'), `gen.${id}.pan`));
    if (g.type === 'analog') {
      opts.append(selEl(ANALOG_SHAPES, g.shape, v => set('shape', v, true), 'waveform'));
      if (g.shape === 'pulse') ks.append(this._k('WIDTH', GEN_SPEC.pw, P('pw'), null, redraw));
    } else if (g.type === 'wavetable') {
      opts.append(selEl(Object.keys(TABLES).map(k => [k, TABLES[k].label]), g.table, v => set('table', v, false), 'wavetable'));
      ks.append(this._k('POS', GEN_SPEC.morph, P('morph'), `gen.${id}.morph`, redraw));
    } else if (g.type === 'noise') {
      opts.append(selEl(NOISE_COLORS, g.color, v => set('color', v, false), 'noise colour'),
        selEl(NOISE_FILTERS.map(f => [f, f === 'none' ? 'no filter' : f]), g.nfilt, v => set('nfilt', v, true), 'noise filter'));
      if (g.nfilt !== 'none') ks.append(this._k('CUT', GEN_SPEC.nfreq, P('nfreq'), `gen.${id}.cutoff`), this._k('RES', GEN_SPEC.nres, P('nres')));
    } else if (g.type === 'sample') {
      const list = [...Object.keys(SAMPLE_DEFS).map(k => [k, SAMPLE_DEFS[k].label])];
      this.libList.forEach(r => list.push(['lib:' + r.id, '♪ ' + r.name.slice(0, 28)]));
      if (g.src.startsWith('lib:') && !list.some(x => x[0] === g.src)) list.push([g.src, '♪ ' + g.src.slice(4, 20)]);
      opts.append(selEl(list, g.src, v => { set('src', v, false); if (v.startsWith('lib:')) s.loadLibrarySample(v.slice(4)).then(redraw); }, 'sample (built-in, or from the shared take library)'),
        chk('loop', g.loop, v => set('loop', v, false), 'loop the sample while the note is held'));
      ks.append(this._k('ROOT', GEN_SPEC.root, P('root')), this._k('START', GEN_SPEC.start, P('start'), null, redraw));
    } else if (g.type === 'fm') {
      const others = S.gens.filter(x => x.id !== id && x.type !== 'noise' && x.type !== 'sample').map(x => [x.id, '→ GEN ' + (S.gens.indexOf(x) + 1) + ' ' + GEN_TYPES[x.type]]);
      opts.append(selEl([['', '→ (audible only)'], ...others], g.fmTarget, v => set('fmTarget', v, false), 'which generator this operator frequency-modulates'));
      ks.append(this._k('FM AMT', GEN_SPEC.fmAmt, P('fmAmt'), `gen.${id}.fm`));
    }
    if (g.type !== 'noise') {
      opts.append(selEl([['ratio', 'ratio × note'], ['fixed', 'fixed Hz']], g.mode, v => set('mode', v, true), 'pitch: follows the note, or a fixed frequency'));
      ks.append(g.mode === 'fixed' ? this._k('FREQ', GEN_SPEC.hz, P('hz')) : this._k('RATIO', GEN_SPEC.ratio, P('ratio')));
    }
    if (g.type === 'analog' || g.type === 'wavetable' || g.type === 'sample') {
      ks.append(this._k('UNISON', GEN_SPEC.unison, P('unison')), this._k('DETUNE', GEN_SPEC.detune, P('detune')), this._k('SPREAD', GEN_SPEC.spread, P('spread')));
    }
    const card = h('div', { class: 'fg-card' + (g.on ? '' : ' off') }, head, h('div', { class: 'fg-gbody' }, thumb, opts), ks);
    redraw();
    return card;
  }
  _drawThumb(cv, g) {
    const x = cv.getContext('2d'), W = cv.width, H = cv.height;
    x.fillStyle = '#0a0605'; x.fillRect(0, 0, W, H);
    x.strokeStyle = '#2c1d10'; x.beginPath(); x.moveTo(0, H / 2); x.lineTo(W, H / 2); x.stroke();
    x.strokeStyle = g.on ? '#d8a060' : '#7a5828'; x.lineWidth = 2; x.beginPath();
    if (g.type === 'sample') {
      const sb = this.s._sample(g.src);
      if (sb) {
        const d = sb.buffer.getChannelData(0), per = d.length / W;
        for (let i = 0; i < W; i++) { let pk = 0; const a = Math.floor(i * per), b = Math.min(d.length, Math.floor((i + 1) * per)); for (let j = a; j < b; j += 4) pk = Math.max(pk, Math.abs(d[j])); x.moveTo(i, H / 2 - pk * H * 0.45); x.lineTo(i, H / 2 + pk * H * 0.45); }
        x.stroke();
        x.fillStyle = 'rgba(255,216,150,.5)'; x.fillRect(g.start * W, 0, 2, H);
      } else { x.fillStyle = '#7a5828'; x.font = '18px Courier New'; x.fillText('loading…', 8, H / 2 + 6); }
      return;
    }
    let seed = 7;
    const rnd = () => { seed = (seed * 16807) % 2147483647; return seed / 2147483647 * 2 - 1; };
    for (let i = 0; i <= W; i++) {
      const ph = (i / W) * 2 % 1;
      let y = 0;
      if (g.type === 'noise') y = rnd() * (g.color === 'white' ? 0.9 : g.color === 'pink' ? 0.6 : 0.35);
      else if (g.type === 'wavetable') y = tableSample(g.table, g.morph, ph);
      else if (g.type === 'fm') y = Math.sin(TAU * ph + (g.fmTarget ? 0 : 0));
      else switch (g.shape) {
        case 'sine': y = Math.sin(TAU * ph); break;
        case 'triangle': y = 1 - 4 * Math.abs(ph - 0.5); y = -y; break;
        case 'saw': y = 2 * ph - 1; break;
        case 'square': y = ph < 0.5 ? 1 : -1; break;
        case 'pulse': y = ph < g.pw ? 1 : -1; break;
      }
      const py = H / 2 - clamp(y, -1.2, 1.2) * H * 0.4;
      if (i === 0) x.moveTo(i, py); else x.lineTo(i, py);
    }
    x.stroke();
    if (g.type === 'fm' && g.fmTarget) { x.fillStyle = '#c8a4f0'; x.font = '16px Courier New'; x.fillText('FM →', 6, 18); }
  }

  // ── middle: modulators, macros, voice ───────────────────────────
  _colMid() {
    const s = this.s, S = s.state, col = h('div', { class: 'fg-col' });
    this.chips = h('div', { class: 'fg-chips' });
    this.hint = h('div', { class: 'fg-hint' });
    this.md = h('div', { class: 'fg-detail' });
    col.append(h('div', { class: 'fg-h' }, 'MODULATORS'), this.chips, this.hint, this.md);
    this._renderChips(); this._renderModDetail();
    // macros
    this.macroKnobs = [];
    const mg = h('div', { class: 'fg-macros' });
    S.macros.forEach((m, i) => {
      const k = new Knob(this, { label: m.name, spec: MACRO_SPEC, get: () => s.state.macros[i].value, set: v => s.setMacro(i, v), title: m.name + ' (source M' + (i + 1) + ')' });
      this.knobs.push(k); this.macroKnobs.push(k); mg.appendChild(k.el);
    });
    col.append(h('div', { class: 'fg-h' }, 'MACROS', h('span', { class: 'fg-sp' }), h('span', { class: 'fg-note', text: 'select M1–M8 to rename' })), mg);
    // voice filter
    const F = S.filter;
    const laneT = h('span', {}, ...LANES.map(L => h('button', { class: 'fg-ib' + (F.lanes.includes(L) ? ' on' : ''), text: L, title: 'filter lane ' + L, onclick: () => { s.setParam('filter.lanes', F.lanes.includes(L) ? F.lanes.replace(L, '') : F.lanes + L); this.render(); } })));
    const fk = h('div', { class: 'fg-knobs' },
      this._k('CUTOFF', FILTER_SPEC.cutoff, 'filter.cutoff', 'filter.cutoff'),
      this._k('RES', FILTER_SPEC.res, 'filter.res', 'filter.res'),
      this._k('KEY', FILTER_SPEC.key, 'filter.key'),
      this._k('ENV2', FILTER_SPEC.env, 'filter.env', null, null, { title: 'how far ENV 2 opens the cutoff' }));
    if (F.type === 'peaking') fk.append(this._k('GAIN', FILTER_SPEC.gain, 'filter.gain'));
    col.append(h('div', { class: 'fg-h' }, 'VOICE FILTER', h('span', { class: 'fg-sp' }),
      h('button', { class: 'fg-tog' + (F.on ? ' on' : ''), text: F.on ? 'ON' : 'OFF', onclick: () => { s.setParam('filter.on', !F.on); this.render(); } }),
      selEl(FILTER_TYPES, F.type, v => { s.setParam('filter.type', v); this.render(); }, 'filter type'), laneT), fk);
    // amp
    const ampPrev = h('canvas', { class: 'fg-prev', width: 240, height: 92 });
    const drawAmp = () => this._drawEnv(ampPrev, S.amp, '#d8a060');
    col.append(h('div', { class: 'fg-h' }, 'AMP ENVELOPE'),
      h('div', { class: 'fg-gbody' }, ampPrev, h('div', { class: 'fg-knobs' },
        this._k('ATK', ENV_SPEC.a, 'amp.a', null, drawAmp), this._k('DEC', ENV_SPEC.d, 'amp.d', null, drawAmp),
        this._k('SUS', ENV_SPEC.s, 'amp.s', null, drawAmp), this._k('REL', ENV_SPEC.r, 'amp.r', null, drawAmp))));
    drawAmp();
    col.append(h('div', { class: 'fg-h' }, 'VOICE', h('span', { class: 'fg-sp' }),
      selEl([['poly', 'poly · ' + s.maxVoices], ['mono', 'mono'], ['legato', 'legato']], S.voice.mode, v => s.setParam('voice.mode', v), 'poly, mono (retrigger) or legato (no retrigger while held)')),
      h('div', { class: 'fg-knobs' }, this._k('GLIDE', VOICE_SPEC.glide, 'voice.glide'), this._k('BEND', VOICE_SPEC.bend, 'voice.bend'),
        this._k('VEL', VOICE_SPEC.velSens, 'voice.velSens', null, null, { title: 'velocity sensitivity' })));
    return col;
  }
  _renderChips() {
    if (!this.chips) return;
    const s = this.s, counts = {};
    s.state.mods.forEach(m => { counts[m.src] = (counts[m.src] || 0) + 1; });
    this.chips.textContent = '';
    for (const src of s.modSources()) {
      const c = h('span', { class: 'fg-chip' + (this.sel === src.id ? ' sel' : '') + (this.armed === src.id ? ' armed' : ''), draggable: 'true',
        style: '--c:' + src.color, title: src.hint + ' · click to select + arm, then click a knob · or drag onto a knob' }, src.id[0] === 'm' && src.id !== 'mw' ? src.label.slice(0, 9) : src.label);
      if (counts[src.id]) c.appendChild(h('sup', { text: String(counts[src.id]) }));
      c.addEventListener('dragstart', e => { e.dataTransfer.setData('text/forge-mod', src.id); e.dataTransfer.setData('text/plain', src.id); e.dataTransfer.effectAllowed = 'link'; });
      c.addEventListener('click', () => {
        if (this.sel === src.id) this.arm(this.armed === src.id ? null : src.id);
        else { this.sel = src.id; this.arm(src.id); }
        this._renderModDetail();
      });
      this.chips.appendChild(c);
    }
    if (this.hint) {
      const lbl = (s.modSources().find(x => x.id === this.armed) || {}).label;
      this.hint.className = 'fg-hint' + (this.armed ? ' armed' : '');
      this.hint.textContent = this.armed ? `armed: ${lbl} — click any ringed knob to route it, drag that knob for depth · Esc / click the chip to stop`
        : 'drag a chip onto a knob (or click chip, then knob) · drag a knob\'s outer ring to set depth';
    }
  }
  _renderModDetail() {
    const el = this.md; if (!el) return;
    const s = this.s, S = s.state, id = this.sel;
    el.textContent = '';
    let m;
    if ((m = /^env([123])$/.exec(id))) {
      const n = m[1], cv = h('canvas', { class: 'fg-prev', width: 240, height: 92 }), e = S.envs[n - 1];
      const dr = () => this._drawEnv(cv, e, srcColor(id));
      el.append(h('div', { class: 'fg-gbody' }, cv, h('div', { class: 'fg-knobs' },
        this._k('ATK', ENV_SPEC.a, `env.${n}.a`, null, dr), this._k('DEC', ENV_SPEC.d, `env.${n}.d`, null, dr),
        this._k('SUS', ENV_SPEC.s, `env.${n}.s`, null, dr), this._k('REL', ENV_SPEC.r, `env.${n}.r`, null, dr))));
      dr();
    } else if ((m = /^lfo([123])$/.exec(id))) {
      const n = m[1], L = S.lfos[n - 1], cv = h('canvas', { class: 'fg-prev', width: 240, height: 92 });
      const dr = () => this._drawLfo(cv, L, srcColor(id));
      const re = () => { this._renderModDetail(); };
      el.append(h('div', { class: 'fg-row' },
        selEl(LFO_SHAPES.map(x => [x, x === 'sh' ? 'S&H random' : x]), L.shape, v => { s.setParam(`lfo.${n}.shape`, v); dr(); }, 'shape'),
        selEl([['1', 'per voice · retrig'], ['0', 'global · free']], L.retrig ? '1' : '0', v => { s.setParam(`lfo.${n}.retrig`, v === '1'); re(); this._modsChanged(); }, 'retrigger per note, or one free-running LFO'),
        chk('sync', L.sync, v => { s.setParam(`lfo.${n}.sync`, v); re(); }, 'tempo sync'),
        L.sync ? selEl(DIV_LIST, L.div, v => s.setParam(`lfo.${n}.div`, v), 'note division') : null,
        chk('0..1', L.uni, v => { s.setParam(`lfo.${n}.uni`, v); dr(); }, 'unipolar (0..1) instead of −1..1')));
      const ks = h('div', { class: 'fg-knobs' });
      if (!L.sync) ks.append(this._k('RATE', LFO_SPEC.rate, `lfo.${n}.rate`, `lfo.${n}.rate`));
      ks.append(this._k('AMOUNT', LFO_SPEC.amount, `lfo.${n}.amount`, `lfo.${n}.amount`, dr));
      if (L.retrig) ks.append(this._k('FADE IN', LFO_SPEC.fade, `lfo.${n}.fade`));
      el.append(h('div', { class: 'fg-gbody' }, cv, ks));
      dr();
    } else if ((m = /^m([1-8])$/.exec(id))) {
      const i = +m[1] - 1, nm = h('input', { type: 'text', value: S.macros[i].name, title: 'macro name', style: 'width:110px' });
      nm.addEventListener('change', () => { s.setParam(`macro.${i + 1}.name`, nm.value.trim() || 'MACRO ' + (i + 1)); this.render(); });
      el.append(h('div', { class: 'fg-row' }, h('b', { text: 'MACRO ' + (i + 1) + ' ', style: 'color:var(--fg-hi);font-weight:normal' }), nm,
        h('span', { class: 'fg-note', text: 'CC 74 drives M1 by default · the page can MIDI-learn all eight' })));
    } else {
      el.append(h('div', { class: 'fg-note', text: (SOURCES.find(x => x.id === id) || {}).hint || '' }));
    }
    const tl = new Map(s.modTargets().map(t => [t.id, t.label]));
    const rs = S.mods.filter(r => r.src === id);
    el.append(h('div', { class: 'fg-note', style: 'margin-top:3px' }, rs.length ? 'routes: ' + rs.map(r => (tl.get(r.dst) || r.dst) + ' ' + Math.round(r.depth * 100) + '%').join(' · ') : 'no routes yet.'));
  }
  _drawEnv(cv, e, col) {
    const x = cv.getContext('2d'), W = cv.width, H = cv.height;
    x.fillStyle = '#0a0605'; x.fillRect(0, 0, W, H);
    const hold = Math.max(0.15, (e.a + e.d) * 0.4), tot = e.a + e.d * 1.2 + hold + e.r * 1.2;
    const X = t => 4 + (t / tot) * (W - 8), Y = v => H - 4 - v * (H - 8);
    x.strokeStyle = col; x.lineWidth = 2; x.beginPath(); x.moveTo(X(0), Y(0)); x.lineTo(X(e.a), Y(1));
    const N = 40;
    for (let i = 1; i <= N; i++) { const t = e.d * 1.2 * i / N; x.lineTo(X(e.a + t), Y(e.s + (1 - e.s) * Math.exp(-t / (e.d / 4)))); }
    const t1 = e.a + e.d * 1.2 + hold, v1 = e.s + (1 - e.s) * Math.exp(-1.2 * 4);
    x.lineTo(X(t1), Y(v1));
    for (let i = 1; i <= N; i++) { const t = e.r * 1.2 * i / N; x.lineTo(X(t1 + t), Y(v1 * Math.exp(-t / (e.r / 5)))); }
    x.stroke();
    x.fillStyle = '#7a5828'; x.font = '15px Courier New'; x.fillText(tot < 1 ? Math.round(tot * 1000) + 'ms' : tot.toFixed(1) + 's', W - 66, 16);
  }
  _drawLfo(cv, L, col) {
    const x = cv.getContext('2d'), W = cv.width, H = cv.height;
    x.fillStyle = '#0a0605'; x.fillRect(0, 0, W, H);
    x.strokeStyle = '#2c1d10'; x.beginPath(); x.moveTo(0, L.uni ? H - 6 : H / 2); x.lineTo(W, L.uni ? H - 6 : H / 2); x.stroke();
    x.strokeStyle = col; x.lineWidth = 2; x.beginPath();
    let seed = 3, last = 0;
    for (let i = 0; i <= W; i++) {
      const ph = (i / W) * 2, f = ph % 1;
      let y;
      switch (L.shape) {
        case 'sine': y = Math.sin(TAU * f); break;
        case 'triangle': y = 1 - 4 * Math.abs(f - 0.25 - Math.floor(f + 0.25)); y = f < 0.25 ? 4 * f : f < 0.75 ? 2 - 4 * f : 4 * f - 4; break;
        case 'saw': y = 2 * f - 1; break;
        case 'ramp': y = 1 - 2 * f; break;
        case 'square': y = f < 0.5 ? 1 : -1; break;
        default: { const st = Math.floor(ph * 4); if (st !== last || i === 0) { seed = (seed * 16807 + st) % 2147483647; last = st; } y = (seed / 2147483647) * 2 - 1; }
      }
      y *= L.amount;
      const v = L.uni ? (y * 0.5 + 0.5) : y;
      const py = L.uni ? H - 6 - v * (H - 12) : H / 2 - v * (H / 2 - 6);
      if (i === 0) x.moveTo(i, py); else x.lineTo(i, py);
    }
    x.stroke();
    x.fillStyle = '#7a5828'; x.font = '15px Courier New';
    x.fillText(L.sync ? L.div : (L.rate < 10 ? L.rate.toFixed(2) : L.rate.toFixed(1)) + ' Hz', W - 80, 16);
  }

  // ── right: output, lanes, master, matrix ────────────────────────
  _colFx() {
    const s = this.s, S = s.state, col = h('div', { class: 'fg-col' });
    this.scope = h('canvas', { class: 'fg-scope' });
    col.append(h('div', { class: 'fg-h' }, 'OUTPUT', h('span', { class: 'fg-sp' }), h('span', { class: 'fg-note', text: 'scope · spectrum' })), this.scope);
    const tabs = h('div', { class: 'fg-tabs' }, ...LANES.map(L => h('button', { class: this.lane === L ? 'on' : 'dim', text: `${L} · ${S.lanes[L].fx.length}`, title: 'lane ' + L, onclick: () => { this.lane = L; this.render(); } })));
    col.append(h('div', { class: 'fg-h' }, 'LANES', h('span', { class: 'fg-sp' }), tabs));
    col.append(this._lanePanel(this.lane));
    col.append(h('div', { class: 'fg-h' }, 'MASTER', h('span', { class: 'fg-sp' }),
      chk('soft limiter', S.master.limit, v => s.setParam('master.limit', v), 'soft-clip the output at 0.98')),
    h('div', { class: 'fg-knobs' }, this._k('MASTER', MASTER_SPEC.gain, 'master.gain', 'master.gain')));
    this.mx = h('div');
    col.append(h('div', { class: 'fg-h' }, 'MOD MATRIX', h('span', { class: 'fg-sp' }), h('span', { class: 'fg-note', text: 'depth −100..100% of the knob' })), this.mx);
    this._renderMatrix();
    return col;
  }
  _lanePanel(L) {
    const s = this.s, S = s.state, st = S.lanes[L], wrap = h('div');
    const toOpts = [['master', '→ master'], ...LANES.slice(LANES.indexOf(L) + 1).map(x => [x, '→ lane ' + x])];
    const add = selEl([['', '+ SNAPIN'], ...Object.keys(SNAP_SPECS).map(k => [k, SNAP_SPECS[k].label])], '', v => { if (v && s.addSnapin(L, v)) this.render(); }, 'add an effect to this lane');
    const users = S.gens.filter(g => g.lane === L).map(g => S.gens.indexOf(g) + 1);
    wrap.append(h('div', { class: 'fg-row' },
      h('div', { class: 'fg-knobs' }, this._k('GAIN', LANE_SPEC.gain, `lane.${L}.gain`, `lane.${L}.gain`)),
      h('div', {}, selEl(toOpts, st.to, v => { s.setParam(`lane.${L}.to`, v); }, 'where this lane goes'), h('br'),
        st.fx.length < MAX_FX_PER_LANE ? add : null, h('br'),
        h('span', { class: 'fg-note', text: users.length ? 'fed by gen ' + users.join(', ') : 'no generator feeds this lane' }))));
    st.fx.forEach(f => wrap.appendChild(this._snapCard(L, f)));
    if (!st.fx.length) wrap.appendChild(h('div', { class: 'fg-note', text: 'empty lane — signal passes straight through.' }));
    return wrap;
  }
  _snapCard(L, f) {
    const s = this.s, spec = SNAP_SPECS[f.type], P = k => `fx.${f.id}.${k}`;
    const head = h('div', { class: 'fg-ch' },
      h('button', { class: 'fg-tog' + (f.on ? ' on' : ''), text: f.on ? '●' : '○', title: 'bypass', onclick: () => { s.setParam(P('on'), !f.on); this.render(); } }),
      h('b', { text: spec.label }), h('span', { class: 'fg-sp' }),
      h('button', { class: 'fg-ib', text: '▲', onclick: () => { s.moveSnapin(f.id, -1); this.render(); } }),
      h('button', { class: 'fg-ib', text: '▼', onclick: () => { s.moveSnapin(f.id, 1); this.render(); } }),
      h('button', { class: 'fg-ib', text: '✕', onclick: () => { s.removeSnapin(f.id); this.render(); } }));
    const opts = h('div', { class: 'fg-row' }), ks = h('div', { class: 'fg-knobs' });
    for (const k in spec.params) {
      const sp = spec.params[k];
      if (f.type === 'delay' && ((k === 'ms' && f.p.sync) || (k === 'div' && !f.p.sync))) continue;
      if (f.type === 'filter' && k === 'gain' && !/peaking|shelf/.test(f.p.type)) continue;
      if (sp.opts) opts.append(selEl(sp.opts, f.p[k], v => { s.setParam(P(k), v); if (spec.structural && spec.structural.includes(k)) this.render(); }, k));
      else if (sp.bool) opts.append(chk(k === 'pp' ? 'ping-pong' : k, f.p[k], v => { s.setParam(P(k), v); this.render(); }));
      else if (sp.pattern) {
        const pat = h('div', { class: 'fg-pat', title: 'gate pattern — click steps' });
        for (let i = 0; i < 16; i++) {
          const cell = h('i', { class: f.p.pattern[i] === 'x' ? 'x' : '' });
          cell.addEventListener('click', () => { const a = f.p.pattern.split(''); a[i] = a[i] === 'x' ? '.' : 'x'; s.setParam(P('pattern'), a.join('')); cell.className = a[i] === 'x' ? 'x' : ''; });
          pat.appendChild(cell);
        }
        opts.append(pat);
        pat.style.width = '100%';
      } else ks.append(this._k(sp.label, sp, P(k), spec.mods.includes(k) ? `fx.${f.id}.${k}` : null));
    }
    return h('div', { class: 'fg-card' + (f.on ? '' : ' off') }, head, opts, ks);
  }
  _renderMatrix() {
    const el = this.mx; if (!el) return;
    const s = this.s, S = s.state;
    el.textContent = ''; this.mxRows = {};
    const targets = s.modTargets(), tl = new Map(targets.map(t => [t.id, t.label]));
    const srcOpts = s.modSources().map(x => [x.id, x.label]);
    for (const m of S.mods) {
      const rng = h('input', { type: 'range', min: -1, max: 1, step: 0.001, title: 'depth' }); rng.value = m.depth;
      const num = h('input', { type: 'number', min: -100, max: 100, step: 0.1, title: 'depth %' }); num.value = (m.depth * 100).toFixed(1);
      const setD = v => { s.setModDepth(m.id, v); rng.value = m.depth; num.value = (m.depth * 100).toFixed(1); this.knobs.forEach(k => k.o.target === m.dst && k.draw()); };
      rng.addEventListener('input', () => setD(+rng.value));
      num.addEventListener('change', () => setD((+num.value || 0) / 100));
      const on = h('input', { type: 'checkbox', title: 'route on / off' }); on.checked = m.on !== false;
      on.addEventListener('change', () => { s.setParam(`mod.${m.id}.on`, on.checked); this._modsChanged(); });
      el.appendChild(h('div', { class: 'fg-mrow' },
        h('span', { class: 'dot', style: 'background:' + srcColor(m.src) }),
        selEl(srcOpts, m.src, v => { s.setParam(`mod.${m.id}.src`, v); this._modsChanged(); }, 'source'),
        h('span', { class: 'dst', title: m.dst, text: '→ ' + (tl.get(m.dst) || m.dst + ' (gone)') }),
        rng, num, on,
        h('button', { class: 'fg-ib', text: '✕', title: 'delete route', onclick: () => { s.removeMod(m.id); this._modsChanged(); } })));
      this.mxRows[m.id] = { rng, num };
    }
    if (!S.mods.length) el.appendChild(h('div', { class: 'fg-note', text: 'no routes. drag a modulator chip onto a knob.' }));
    const ss = selEl(srcOpts, this.sel, () => {}, 'source'), ds = selEl(targets.map(t => [t.id, t.label]), 'filter.cutoff', () => {}, 'target');
    ds.style.maxWidth = '170px';
    el.appendChild(h('div', { class: 'fg-row', style: 'margin-top:4px' }, ss, ds,
      h('button', { text: '+ ROUTE', onclick: () => { s.addMod(ss.value, ds.value, defaultDepth(ds.value)); this._modsChanged(); } })));
  }
  _matrixSync(id) {
    const r = this.mxRows && this.mxRows[id], m = this.s.state.mods.find(x => x.id === id);
    if (r && m) { r.rng.value = m.depth; r.num.value = (m.depth * 100).toFixed(1); }
  }

  // ── scope / spectrum loop ───────────────────────────────────────
  _loop(ts) {
    if (this.dead) return;
    this.raf = requestAnimationFrame(this._loop);
    if (ts - this._last < 33) return;
    this._last = ts;
    if (this.status) this.status.textContent = `voices ${this.s.activeVoices}/${this.s.maxVoices} · ${Math.round(this.s.bpm)} bpm${this.s._worklet ? '' : ' · no worklet'}`;
    const cv = this.scope;
    if (!cv || !cv.isConnected || !this.an) return;
    const r = window.devicePixelRatio || 1, W = Math.max(1, Math.round(cv.clientWidth * r)), H = Math.max(1, Math.round(cv.clientHeight * r));
    if (cv.width !== W || cv.height !== H) { cv.width = W; cv.height = H; }
    const x = cv.getContext('2d');
    x.fillStyle = '#0a0605'; x.fillRect(0, 0, W, H);
    const n = this.an.fftSize;
    if (!this.td || this.td.length !== n) { this.td = new Float32Array(n); this.fd = new Float32Array(this.an.frequencyBinCount); }
    this.an.getFloatTimeDomainData(this.td);
    this.an.getFloatFrequencyData(this.fd);
    const sh = H * 0.5;
    let trig = 0;
    for (let i = 1; i < n / 2; i++) if (this.td[i - 1] < 0 && this.td[i] >= 0) { trig = i; break; }
    let pk = 0;
    for (let i = 0; i < n; i++) pk = Math.max(pk, Math.abs(this.td[i]));
    x.strokeStyle = '#2c1d10'; x.lineWidth = 1; x.beginPath(); x.moveTo(0, sh / 2); x.lineTo(W, sh / 2); x.stroke();
    x.strokeStyle = pk > 0.97 ? '#c64a3a' : '#d8a060'; x.lineWidth = 1.5 * r; x.beginPath();
    const span = n / 2;
    for (let i = 0; i < W; i++) { const v = this.td[trig + Math.floor(i / W * span)] || 0, y = sh / 2 - v * sh * 0.46; if (i === 0) x.moveTo(i, y); else x.lineTo(i, y); }
    x.stroke();
    const fb = this.fd, nb = fb.length, ny = this.s.ctx.sampleRate / 2;
    x.fillStyle = 'rgba(200,118,51,0.75)';
    for (let i = 0; i < W; i += 2 * r) {
      const f = 20 * Math.pow(1000, i / W), b = Math.min(nb - 1, Math.round(f / ny * nb));
      const db = clamp((fb[b] + 100) / 90, 0, 1);
      x.fillRect(i, H - db * (H - sh - 2), Math.max(1, 2 * r - 1), db * (H - sh - 2));
    }
    x.fillStyle = '#7a5828'; x.font = (10 * r) + 'px Courier New';
    x.fillText('peak ' + (pk > 0 ? (20 * Math.log10(pk)).toFixed(1) : '-∞') + ' dB', 4 * r, 11 * r);
  }
}

// ═══════════════════════════════════════════════════════════════════
// Exports
// ═══════════════════════════════════════════════════════════════════
ForgeSynth.VERSION = 1;
ForgeSynth.defaultState = () => clone(normalizeState(DEFAULT_STATE));
ForgeSynth.normalizeState = s => normalizeState(s);
ForgeSynth.sources = SOURCES.map(s => Object.assign({}, s));
ForgeSynth.snapinTypes = Object.keys(SNAP_SPECS).map(k => ({ id: k, label: SNAP_SPECS[k].label, mods: SNAP_SPECS[k].mods.slice() }));
ForgeSynth.generatorTypes = Object.keys(GEN_TYPES).map(k => ({ id: k, label: GEN_TYPES[k] }));
ForgeSynth.builtinSamples = Object.keys(SAMPLE_DEFS).map(k => ({ id: k, label: SAMPLE_DEFS[k].label }));
ForgeSynth.userPresets = () => userPresets();
ForgeSynth.saveUserPreset = (name, state) => {
  const nm = String(name || '').trim(); if (!nm) return false;
  const list = userPresets().filter(p => p.name !== nm);
  list.push({ name: nm, category: 'user', state: normalizeState(state) });
  return saveUserPresets(list);
};
ForgeSynth.deleteUserPreset = name => saveUserPresets(userPresets().filter(p => p.name !== name));
ForgeSynth.USER_PRESETS_KEY = USER_KEY;

window.ForgeSynth = ForgeSynth;
window.FORGE_PRESETS = FORGE_PRESETS;
})();
