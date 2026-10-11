/* daw_fx.js — insert effects, a noise gate and sidechain ducking for the DAW's mixer strips.
 *
 * Most inserts ARE FORGE's snap-ins (forge_synth.js → ForgeSynth.createEffect): the same EQ,
 * compressor, distortion, filter, delay, reverb, chorus, tape … that live in FORGE's lanes.
 * This file adds what a mixer needs on top: low / high cut on the EQ, a bitcrusher as its own
 * insert, a NOISE gate (FORGE's gate is a trance gate, kept here as "trance"), and the
 * envelope follower that drives sidechain ducking. Plain classic script, works from file://
 * (worklets load from a data: URL via AK.addWorklet), in a live AudioContext and in an
 * OfflineAudioContext alike.
 *
 *   await DawFX.prepare(ctx)                     worklets (FORGE crush + gate + duck), once per context
 *   const u = DawFX.create(ctx, {type, params}, {bpm})
 *       u.input / u.output (GainNodes) · u.set(param, value, when) · u.bpm = 96 · u.sync(when) · u.dispose()
 *   DawFX.TYPES                                  [{id, label}] in menu order
 *   DawFX.spec(type) → {param: {min,max,def,label,unit,curve?,opts?,bool?}}   DawFX.defaults(type)
 *   DawFX.auto(type) → automatable params        DawFX.presets(type) → [{name, params}]
 *   DawFX.toValue(spec, v01) / DawFX.toNorm(spec, value)   automation lanes are 0..1
 *   DawFX.createDuck(ctx) → AudioWorkletNode (in: sidechain source, out: gain 1 − depth) | null
 *   DawFX.setDuck(node, {amount, attack, release, thresh}, when)
 *
 * Project data (plain JSON, on a strip's mix object):
 *   mix.fx   = [{ id, type, on, params: {…} }]          inserts, in order, between strip in and pan
 *   mix.duck = { source: stripId, amount 0..1, attack s, release s, thresh dB }   (absent = no ducking)
 *              the follower reads the source's post-insert, pre-fader signal: full dip (gain 1 − amount)
 *              at or above thresh, none 12 dB below it, a dB-linear knee between
 */
(function (root) {
  "use strict";
  const FS = () => (typeof ForgeSynth !== 'undefined' ? ForgeSynth : root.ForgeSynth);
  const AKg = () => (typeof AK !== 'undefined' ? AK : root.AK);
  const clamp = (v, a, b) => (v < a ? a : v > b ? b : v);
  const isNum = v => typeof v === 'number' && isFinite(v);

  // ── worklets: a noise gate and the sidechain envelope follower ──────
  const WORKLET = `
const dbl = d => Math.pow(10, d / 20);
class DawGate extends AudioWorkletProcessor {
  static get parameterDescriptors() { return [
    { name: 'thresh', defaultValue: -40, minValue: -100, maxValue: 0, automationRate: 'k-rate' },
    { name: 'range', defaultValue: -60, minValue: -100, maxValue: 0, automationRate: 'k-rate' },
    { name: 'attack', defaultValue: 0.002, minValue: 0.0001, maxValue: 1, automationRate: 'k-rate' },
    { name: 'release', defaultValue: 0.12, minValue: 0.001, maxValue: 4, automationRate: 'k-rate' }]; }
  constructor() { super(); this.env = 0; this.g = 0; this.hold = 0; this.open = false; this.alive = true;
    this.port.onmessage = e => { if (e.data === 'stop') this.alive = false; }; }
  process(ins, outs, P) {
    const i = ins[0], o = outs[0], n = o[0].length, sr = sampleRate;
    if (!i || !i.length) { for (const c of o) c.fill(0); return this.alive; }
    const thr = dbl(P.thresh[0]), close = thr * 0.7, floor = dbl(P.range[0]);
    const er = Math.exp(-1 / (0.01 * sr)), ga = Math.exp(-1 / (Math.max(0.0001, P.attack[0]) * sr)), gr = Math.exp(-1 / (Math.max(0.001, P.release[0]) * sr));
    const holdN = Math.round(0.02 * sr);
    let env = this.env, g = this.g, hold = this.hold, open = this.open;
    for (let s = 0; s < n; s++) {
      let x = 0; for (let c = 0; c < i.length; c++) { const a = Math.abs(i[c][s]); if (a > x) x = a; }
      env = x > env ? x : env * er;
      if (env > thr) { open = true; hold = holdN; } else if (env < close) { if (hold > 0) hold--; else open = false; }
      const target = open ? 1 : floor;
      g = target + (g - target) * (target > g ? ga : gr);
      for (let c = 0; c < o.length; c++) o[c][s] = i[Math.min(c, i.length - 1)][s] * g;
    }
    this.env = env; this.g = g; this.hold = hold; this.open = open;
    return this.alive;
  }
}
registerProcessor('daw-gate', DawGate);
class DawDuck extends AudioWorkletProcessor {
  static get parameterDescriptors() { return [
    { name: 'amount', defaultValue: 0.5, minValue: 0, maxValue: 1, automationRate: 'k-rate' },
    { name: 'attack', defaultValue: 0.005, minValue: 0.0001, maxValue: 1, automationRate: 'k-rate' },
    { name: 'release', defaultValue: 0.15, minValue: 0.001, maxValue: 4, automationRate: 'k-rate' },
    { name: 'thresh', defaultValue: -10, minValue: -100, maxValue: 0, automationRate: 'k-rate' }]; }
  constructor() { super(); this.env = 0; this.alive = true; this.port.onmessage = e => { if (e.data === 'stop') this.alive = false; }; }
  process(ins, outs, P) {
    const i = ins[0], o = outs[0][0], n = o.length, sr = sampleRate;
    const amt = Math.min(1, Math.max(0, P.amount[0])), thrDb = P.thresh[0];
    const a = Math.exp(-1 / (Math.max(0.0001, P.attack[0]) * sr)), r = Math.exp(-1 / (Math.max(0.001, P.release[0]) * sr));
    let env = this.env;
    for (let s = 0; s < n; s++) {
      let x = 0;
      if (i) for (let c = 0; c < i.length; c++) { const v = Math.abs(i[c][s]); if (v > x) x = v; }
      env = x + (env - x) * (x > env ? a : r);
      // soft knee: no ducking 12 dB under the threshold, the full amount at it
      const k = env > 1e-6 ? Math.min(1, Math.max(0, 1 + (20 * Math.log10(env) - thrDb) / 12)) : 0;
      o[s] = 1 - amt * k;
    }
    this.env = env;
    return this.alive;
  }
}
registerProcessor('daw-duck', DawDuck);
`;
  const READY = new WeakMap();      // ctx → { p: Promise, ok: bool }
  function prepare(ctx) {
    let r = READY.get(ctx);
    if (r) return r.p;
    r = { ok: false, p: null };
    READY.set(ctx, r);
    const F = FS();
    const mine = (async () => {
      if (!ctx.audioWorklet) throw new Error('no AudioWorklet');
      const ak = AKg();
      if (ak && ak.addWorklet) await ak.addWorklet(ctx, WORKLET);
      else await ctx.audioWorklet.addModule('data:text/javascript;base64,' + btoa(WORKLET));
      r.ok = true;
    })().catch(e => { console.warn('daw_fx worklet:', e && e.message); });
    r.p = Promise.all([mine, F && F.prepareEffects ? F.prepareEffects(ctx) : null]).then(() => r.ok);
    return r.p;
  }
  const workletOk = ctx => !!(READY.get(ctx) || {}).ok;

  // ── types ───────────────────────────────────────────────────────────
  // forge: the snap-in it wraps · only: restrict / relabel FORGE params · extra: DAW-side params
  const DEF = {
    eq:      { label: 'EQ', forge: 'eq', extra: {
                 lowcut: { min: 20, max: 1000, curve: 'log', def: 20, label: 'LO CUT', unit: 'Hz' },
                 highcut: { min: 1000, max: 20000, curve: 'log', def: 20000, label: 'HI CUT', unit: 'Hz' } },
               order: ['lowcut', 'low', 'lowf', 'mid', 'midf', 'midq', 'high', 'highf', 'highcut'],
               auto: ['lowcut', 'low', 'mid', 'midf', 'high', 'highcut'] },
    comp:    { label: 'COMPRESSOR', forge: 'comp', auto: ['thresh', 'ratio', 'makeup', 'mix'] },
    drive:   { label: 'DRIVE', forge: 'dist', only: { mode: { opts: ['soft', 'hard', 'fold'], def: 'soft' } }, auto: ['drive', 'tone', 'level', 'mix'] },
    filter:  { label: 'FILTER', forge: 'filter', only: { type: { opts: ['lowpass', 'highpass', 'bandpass', 'notch', 'peaking'], def: 'lowpass' } }, auto: ['cutoff', 'res', 'gain', 'mix'] },
    delay:   { label: 'DELAY', forge: 'delay', auto: ['fb', 'tone', 'mix'] },
    reverb:  { label: 'REVERB', forge: 'reverb', auto: ['pre', 'mix'] },
    chorus:  { label: 'CHORUS', forge: 'chorus', auto: ['rate', 'depth', 'mix'] },
    crush:   { label: 'BITCRUSH', forge: 'dist', only: { mode: { opts: ['bitcrush', 'downsample'], def: 'bitcrush' }, drive: { min: 0, max: 1, def: 0.5, label: 'CRUSH', unit: '%' } }, auto: ['drive', 'tone', 'mix'] },
    tape:    { label: 'TAPE', forge: 'tape', auto: ['sat', 'wow', 'flutter', 'age', 'hiss', 'mix'] },
    gate:    { label: 'NOISE GATE', own: {
                 thresh: { min: -80, max: 0, def: -40, label: 'THRESH', unit: 'dB' },
                 range: { min: -80, max: 0, def: -60, label: 'FLOOR', unit: 'dB' },
                 attack: { min: 0.0005, max: 0.05, curve: 'log', def: 0.002, label: 'ATK', unit: 's' },
                 release: { min: 0.01, max: 1, curve: 'log', def: 0.12, label: 'REL', unit: 's' } },
               auto: ['thresh', 'range'] },
    phaser:  { label: 'PHASER', forge: 'phaser', auto: ['freq', 'depth', 'fb', 'mix'] },
    flanger: { label: 'FLANGER', forge: 'flanger', auto: ['depth', 'fb', 'mix'] },
    width:   { label: 'WIDTH', forge: 'width', auto: ['width'] },
    trance:  { label: 'TRANCE GATE', forge: 'gate', auto: ['depth', 'mix'] },
  };
  const PRESETS = {
    eq: [['flat', {}], ['low cut', { lowcut: 120 }], ['air', { high: 4, highf: 8000 }], ['warm', { low: 3, high: -3 }], ['scoop', { mid: -5, midf: 800 }], ['telephone', { lowcut: 400, highcut: 3200, mid: 6, midf: 1500 }]],
    comp: [['glue', { thresh: -18, ratio: 2, attack: 0.03, release: 0.2, makeup: 2 }], ['punch', { thresh: -20, ratio: 4, attack: 0.02, release: 0.1, makeup: 4 }], ['squash', { thresh: -35, ratio: 12, attack: 0.002, release: 0.08, makeup: 10 }]],
    drive: [['warm', { mode: 'soft', drive: 0.2 }], ['crunch', { mode: 'hard', drive: 0.5, tone: 6000 }], ['fold', { mode: 'fold', drive: 0.6, mix: 0.6 }]],
    filter: [['dark', { type: 'lowpass', cutoff: 900, res: 0.2 }], ['thin', { type: 'highpass', cutoff: 600, res: 0.1 }], ['radio', { type: 'bandpass', cutoff: 1500, res: 0.4 }], ['wah', { type: 'bandpass', cutoff: 700, res: 0.8 }]],
    delay: [['1/8 dotted', { sync: true, div: '1/8d', fb: 0.35, mix: 0.25 }], ['1/4 ping-pong', { sync: true, div: '1/4', pp: true, fb: 0.4, mix: 0.3 }], ['slap', { sync: false, ms: 110, fb: 0.1, mix: 0.3 }], ['dub', { sync: true, div: '1/4d', fb: 0.6, tone: 2000, mix: 0.35 }]],
    reverb: [['room', { size: 0.8, damp: 0.5, mix: 0.2 }], ['plate', { size: 1.6, damp: 0.1, pre: 0.02, mix: 0.25 }], ['hall', { size: 2.5, damp: 0.5, mix: 0.25 }], ['cathedral', { size: 6, damp: 0.3, mix: 0.35 }]],
    chorus: [['subtle', { rate: 0.4, depth: 0.3, mix: 0.3 }], ['wide', { rate: 0.8, depth: 0.6, mix: 0.5 }], ['warble', { rate: 3, depth: 0.8, mix: 0.5 }]],
    crush: [['8-bit', { mode: 'bitcrush', drive: 0.55 }], ['lofi', { mode: 'downsample', drive: 0.35, tone: 6000 }], ['wreck', { mode: 'bitcrush', drive: 0.85, mix: 0.7 }]],
    tape: [['cassette', { sat: 0.35, wow: 0.3, flutter: 0.25, age: 0.4, hiss: 0.15 }], ['warped', { wow: 0.9, flutter: 0.4, age: 0.5 }], ['clean deck', { sat: 0.2, wow: 0.08, flutter: 0.05, age: 0.1, hiss: 0 }]],
    gate: [['tight', { thresh: -30, release: 0.05 }], ['gentle', { thresh: -45, range: -20, release: 0.25 }]],
  };
  let SPECS = null;
  function specs() {
    if (SPECS) return SPECS;
    const F = FS(), fx = F && F.effectSpecs ? F.effectSpecs() : {};
    const out = {};
    for (const [id, d] of Object.entries(DEF)) {
      let sp = null;
      if (d.own) sp = Object.assign({}, d.own);
      else if (fx[d.forge]) {
        sp = Object.assign({}, fx[d.forge].params, d.only || {}, d.extra || {});
        if (d.order) { const o = {}; for (const k of d.order) if (sp[k]) o[k] = sp[k]; for (const k in sp) if (!o[k]) o[k] = sp[k]; sp = o; }
      }
      if (sp) out[id] = sp;
    }
    if (F) SPECS = out;            // FORGE not loaded (yet): only the gate, and don't cache that
    return out;
  }
  const spec = type => specs()[type] || null;
  function normField(v, sp) {
    if (sp.opts) return sp.opts.includes(v) ? v : sp.def;
    if (sp.bool) return v === undefined || v === null ? sp.def : !!v;
    if (sp.pattern || sp.str) return typeof v === 'string' ? v : sp.def;
    let x = isNum(v) ? v : (typeof v === 'string' && v !== '' && isFinite(+v) ? +v : sp.def);
    x = clamp(x, sp.min, sp.max);
    if (sp.step) x = Math.round(x / sp.step) * sp.step;
    return x;
  }
  function defaults(type) { const sp = spec(type), o = {}; if (!sp) return o; for (const k in sp) o[k] = sp[k].def; return o; }
  function normParams(type, p) { const sp = spec(type), o = {}; if (!sp) return o; p = p || {}; for (const k in sp) o[k] = normField(p[k], sp[k]); return o; }
  // automation lanes carry 0..1; a param's own curve maps it (log for Hz / seconds)
  function toValue(sp, v) {
    v = clamp(+v || 0, 0, 1);
    if (sp.opts) return sp.opts[Math.round(v * (sp.opts.length - 1))];
    if (sp.bool) return v >= 0.5;
    if (sp.curve === 'log' && sp.min > 0) return sp.min * Math.pow(sp.max / sp.min, v);
    if (sp.curve === 'sq') return sp.min + (sp.max - sp.min) * v * v;
    return sp.min + (sp.max - sp.min) * v;
  }
  function toNorm(sp, x) {
    if (sp.opts) return Math.max(0, sp.opts.indexOf(x)) / Math.max(1, sp.opts.length - 1);
    if (sp.bool) return x ? 1 : 0;
    if (!isNum(x)) x = sp.def;
    if (sp.curve === 'log' && sp.min > 0) return clamp(Math.log(x / sp.min) / Math.log(sp.max / sp.min), 0, 1);
    if (sp.curve === 'sq') return Math.sqrt(clamp((x - sp.min) / (sp.max - sp.min), 0, 1));
    return clamp((x - sp.min) / (sp.max - sp.min), 0, 1);
  }
  const smooth = (param, v, t) => { if (t == null) param.value = v; else param.setTargetAtTime(v, t, 0.008); };

  // ── one insert ──────────────────────────────────────────────────────
  // entry: {type, params}. Returns a unit with the same face as ForgeSynth.createEffect.
  function create(ctx, entry, opts = {}) {
    const type = entry.type, d = DEF[type], sp = spec(type);
    if (!d || !sp) throw new Error('unknown effect ' + type);
    const p = normParams(type, entry.params);
    const input = ctx.createGain(), output = ctx.createGain();
    const unit = { type, input, output, params: p, dispose() {}, sync() {}, set() { return false; } };
    let bpm = isNum(opts.bpm) ? opts.bpm : 120;
    Object.defineProperty(unit, 'bpm', { get: () => bpm, set: v => { if (isNum(v)) { bpm = v; if (unit._fx) unit._fx.bpm = v; } } });
    const at = when => (when === null ? null : Math.max(ctx.currentTime, isNum(when) ? when : ctx.currentTime));

    if (type === 'gate') {
      let node = null;
      if (workletOk(ctx)) {
        try {
          node = new AudioWorkletNode(ctx, 'daw-gate', { numberOfInputs: 1, numberOfOutputs: 1, outputChannelCount: [2], channelCount: 2, channelCountMode: 'explicit', channelInterpretation: 'speakers' });
          for (const k of ['thresh', 'range', 'attack', 'release']) node.parameters.get(k).value = p[k];
        } catch (e) { node = null; }
      }
      if (node) { input.connect(node); node.connect(output); } else input.connect(output);    // no worklet → pass through
      unit.set = (k, v, when) => {
        if (!(k in sp)) return false;
        p[k] = normField(v, sp[k]);
        if (node) smooth(node.parameters.get(k), p[k], at(when));
        return true;
      };
      unit.dispose = () => { try { if (node) { node.port.postMessage('stop'); node.disconnect(); } input.disconnect(); output.disconnect(); } catch (e) {} };
      return unit;
    }

    const F = FS();
    if (!F || !F.createEffect) { input.connect(output); return unit; }        // FORGE missing → wire through
    const fp = {}; for (const k in p) if (!(d.extra && k in d.extra)) fp[k] = p[k];
    const fx = F.createEffect(ctx, d.forge, fp, { bpm });
    unit._fx = fx;
    let hp = null, lp = null;
    if (type === 'eq') {
      hp = ctx.createBiquadFilter(); lp = ctx.createBiquadFilter();
      hp.type = 'highpass'; lp.type = 'lowpass'; hp.Q.value = lp.Q.value = -3.01;   // Q is in dB for LP/HP: −3 dB = Butterworth
      hp.frequency.value = p.lowcut; lp.frequency.value = Math.min(p.highcut, ctx.sampleRate * 0.49);
      input.connect(hp); hp.connect(lp); lp.connect(fx.input);
    } else input.connect(fx.input);
    fx.output.connect(output);
    unit.set = (k, v, when) => {
      if (!(k in sp)) return false;
      p[k] = normField(v, sp[k]);
      if (k === 'lowcut' && hp) { smooth(hp.frequency, p.lowcut, at(when)); return true; }
      if (k === 'highcut' && lp) { smooth(lp.frequency, Math.min(p.highcut, ctx.sampleRate * 0.49), at(when)); return true; }
      return fx.set(k, p[k], when === null ? null : at(when));
    };
    unit.sync = when => fx.sync(when);
    unit.dispose = () => { fx.dispose(); try { input.disconnect(); output.disconnect(); if (hp) { hp.disconnect(); lp.disconnect(); } } catch (e) {} };
    return unit;
  }

  // ── sidechain ducking ───────────────────────────────────────────────
  const DUCK_DEF = { amount: 0.5, attack: 0.005, release: 0.15, thresh: -10 };   // thresh: the full dip from here, none 12 dB under it
  function createDuck(ctx) {
    if (!workletOk(ctx)) return null;
    try {
      return new AudioWorkletNode(ctx, 'daw-duck', { numberOfInputs: 1, numberOfOutputs: 1, outputChannelCount: [1], channelCount: 2, channelCountMode: 'explicit', channelInterpretation: 'speakers' });
    } catch (e) { return null; }
  }
  function setDuck(node, duck, when) {
    if (!node || !duck) return;
    const t = when == null ? null : when;
    for (const k of ['amount', 'attack', 'release', 'thresh']) {
      const v = isNum(duck[k]) ? duck[k] : DUCK_DEF[k];
      const prm = node.parameters.get(k);
      if (t == null) prm.value = v; else prm.setTargetAtTime(v, t, 0.01);
    }
  }

  const DawFX = {
    prepare, workletOk, create, createDuck, setDuck, DUCK_DEF,
    TYPES: Object.keys(DEF).map(id => ({ id, label: DEF[id].label })),
    label: type => (DEF[type] || {}).label || type,
    spec, defaults, normParams, normField, toValue, toNorm,
    auto: type => ((DEF[type] || {}).auto || []).slice(),
    presets: type => (PRESETS[type] || []).map(([name, params]) => ({ name, params })),
  };
  root.DawFX = DawFX;
})(typeof window !== 'undefined' ? window : globalThis);
