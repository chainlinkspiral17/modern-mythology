/*
 * tape_model.js — TAPE MACHINE: a physical model of a reel-to-reel / cassette tape path, after Jatin Chowdhury's
 * "Real-time Physical Modelling for Analog Tape Machines" (DAFx 2019) — the model behind ChowDSP's CHOW Tape.
 * Our own implementation of the published model (CHOW Tape's code is GPL-3 and is not used here). Sections in the
 * order a tape path has them, the same sections CHOW Tape exposes:
 *
 *   INPUT (dB) → TONE (pre-emphasis tilt, undone after the tape: the drive becomes frequency-dependent)
 *   → COMPRESSION (a soft feed-forward squeeze before the tape)
 *   → HYSTERESIS: the Jiles–Atherton model of the tape's magnetisation, M(H), solved per sample with RK4 (or RK2,
 *     lighter) at 2× oversampling. DRIVE = how hard the head writes (H), SATURATION = how early the oxide runs out
 *     (the anhysteretic shape a), BIAS = how well the bias signal linearises it (under-biased → a wide, gritty loop)
 *   → LOSS: the playback head's losses for a tape SPEED (ips) — spacing e^(−kd), thickness (1 − e^(−kδ)) / kδ,
 *     gap sin(kg/2) / (kg/2), k = 2πf / v — as a linear-phase FIR, plus the low-frequency HEAD BUMP
 *   → WOW & FLUTTER: the transport — slow wow (rate, depth) and capstan flutter (three partials), with VARIANCE
 *     (the rates and depths wander) and DRIFT (slow speed creep); a modulated fractional delay (cubic)
 *   → DEGRADE: hiss + an ageing low-pass + level wander, with VARIANCE
 *   → CHEW: crinkled tape — every so often (FREQUENCY) a stretch goes dull, dips and grinds (DEPTH, VARIANCE)
 *   → OUTPUT (dB) · MIX (the dry path is delayed to line up with the tape's latency).
 *
 * Every random thing comes from a seeded generator: the same SEED → the same wow, hiss and chews (offline renders and
 * ⟳ AGAIN repeat exactly). One DSP core (TAPE_DSP, a source string) runs in two places:
 *   TapeModel.process(channels, sampleRate, params) → new channels      plain JS: offline, REMIX, node tests
 *   await TapeModel.prepare(ctx); TapeModel.createNode(ctx, params)     AudioWorkletNode 'mm-tape-model' (live +
 *        node.setParams({...}) · node.parameters (drive, sat, bias, tone, wow, flutter, degrade, chew, mix)
 *   TapeModel.SPEC (param specs) · TapeModel.MACHINES (presets) · TapeModel.lossResponse(params, sr, freqs) → dB
 */
(function (root) {
  'use strict';

  const TAPE_DSP = String.raw`
const TAPE_SPEC = {
  in:       { min: -24, max: 24, def: 0, label: 'INPUT', unit: 'dB' },
  tone:     { min: -1, max: 1, def: 0, label: 'TONE', unit: '' },
  comp:     { min: 0, max: 1, def: 0, label: 'COMP', unit: '%' },
  drive:    { min: 0, max: 1, def: 0.5, label: 'DRIVE', unit: '%' },
  sat:      { min: 0, max: 1, def: 0.5, label: 'SATURATION', unit: '%' },
  bias:     { min: 0, max: 1, def: 0.5, label: 'BIAS', unit: '%' },
  mode:     { opts: ['rk4', 'rk2'], def: 'rk4', label: 'SOLVER' },
  speed:    { opts: [1.875, 3.75, 7.5, 15, 30], def: 7.5, label: 'SPEED', unit: 'ips' },
  spacing:  { min: 0, max: 20, def: 0.2, label: 'SPACING', unit: 'µm' },
  thickness:{ min: 0, max: 50, def: 1.5, label: 'THICKNESS', unit: 'µm' },
  gap:      { min: 0.5, max: 50, def: 1.5, label: 'GAP', unit: 'µm' },
  loss:     { min: 0, max: 1, def: 1, label: 'LOSS', unit: '%' },
  bump:     { min: 0, max: 1, def: 0.5, label: 'HEAD BUMP', unit: '%' },
  wow:      { min: 0, max: 1, def: 0.15, label: 'WOW', unit: '%' },
  wowRate:  { min: 0.1, max: 4, def: 0.6, label: 'WOW RATE', unit: 'Hz' },
  flutter:  { min: 0, max: 1, def: 0.1, label: 'FLUTTER', unit: '%' },
  flutRate: { min: 2, max: 20, def: 7, label: 'FLUT RATE', unit: 'Hz' },
  wfVar:    { min: 0, max: 1, def: 0.3, label: 'VARIANCE', unit: '%' },
  drift:    { min: 0, max: 1, def: 0.1, label: 'DRIFT', unit: '%' },
  degrade:  { min: 0, max: 1, def: 0, label: 'DEGRADE', unit: '%' },
  degVar:   { min: 0, max: 1, def: 0.3, label: 'DEG VAR', unit: '%' },
  chew:     { min: 0, max: 1, def: 0, label: 'CHEW', unit: '%' },
  chewFreq: { min: 0, max: 1, def: 0.4, label: 'CHEW FREQ', unit: '%' },
  chewVar:  { min: 0, max: 1, def: 0.5, label: 'CHEW VAR', unit: '%' },
  out:      { min: -24, max: 24, def: 0, label: 'OUTPUT', unit: 'dB' },
  mix:      { min: 0, max: 1, def: 1, label: 'MIX', unit: '%' },
  seed:     { min: 0, max: 4294967295, def: 1, label: 'SEED', unit: '', step: 1 },
};
function tapeNorm(p) {
  const o = {};
  for (const k in TAPE_SPEC) {
    const s = TAPE_SPEC[k], v = p ? p[k] : undefined;
    if (s.opts) o[k] = s.opts.indexOf(v) >= 0 ? v : (s.opts.indexOf(+v) >= 0 ? +v : s.def);
    else { let x = typeof v === 'number' && isFinite(v) ? v : (typeof v === 'string' && v !== '' && isFinite(+v) ? +v : s.def); x = Math.max(s.min, Math.min(s.max, x)); o[k] = s.step ? Math.round(x) : x; }
  }
  return o;
}
// a small seeded generator (mulberry32) — the worklet has no seeded Math.random
function tapeRng(seed) { let a = (seed >>> 0) || 1; return () => { a = (a + 0x6D2B79F5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
// RBJ biquad, direct form I state per instance
function bq(type, f, q, gainDb, sr) {
  const w = 2 * Math.PI * Math.min(f, sr * 0.49) / sr, cw = Math.cos(w), sw = Math.sin(w), al = sw / (2 * q), A = Math.pow(10, (gainDb || 0) / 40);
  let b0, b1, b2, a0, a1, a2;
  if (type === 'lp') { b0 = (1 - cw) / 2; b1 = 1 - cw; b2 = b0; a0 = 1 + al; a1 = -2 * cw; a2 = 1 - al; }
  else if (type === 'hp') { b0 = (1 + cw) / 2; b1 = -(1 + cw); b2 = b0; a0 = 1 + al; a1 = -2 * cw; a2 = 1 - al; }
  else if (type === 'peak') { b0 = 1 + al * A; b1 = -2 * cw; b2 = 1 - al * A; a0 = 1 + al / A; a1 = -2 * cw; a2 = 1 - al / A; }
  else if (type === 'hs') { const s = 2 * Math.sqrt(A) * al; b0 = A * ((A + 1) + (A - 1) * cw + s); b1 = -2 * A * ((A - 1) + (A + 1) * cw); b2 = A * ((A + 1) + (A - 1) * cw - s); a0 = (A + 1) - (A - 1) * cw + s; a1 = 2 * ((A - 1) - (A + 1) * cw); a2 = (A + 1) - (A - 1) * cw - s; }
  return { b0: b0 / a0, b1: b1 / a0, b2: b2 / a0, a1: a1 / a0, a2: a2 / a0, x1: 0, x2: 0, y1: 0, y2: 0 };
}
function bqSet(f, n) { f.b0 = n.b0; f.b1 = n.b1; f.b2 = n.b2; f.a1 = n.a1; f.a2 = n.a2; }
function bqRun(f, x) { const y = f.b0 * x + f.b1 * f.x1 + f.b2 * f.x2 - f.a1 * f.y1 - f.a2 * f.y2; f.x2 = f.x1; f.x1 = x; f.y2 = f.y1; f.y1 = y; return y; }
// the playback head's losses (magnitude) at f for a speed (ips) and spacing / thickness / gap (µm)
function tapeLossAt(f, p) {
  const v = p.speed * 0.0254, k = 2 * Math.PI * f / v;
  const d = p.spacing * 1e-6, th = p.thickness * 1e-6, g = p.gap * 1e-6;
  const sp = Math.exp(-k * d);
  const kt = k * th, tl = kt > 1e-9 ? (1 - Math.exp(-kt)) / kt : 1;
  const kg = k * g / 2, gl = kg > 1e-9 ? Math.abs(Math.sin(kg) / kg) : 1;
  return sp * tl * gl;
}
// a 63-tap linear-phase FIR of the loss (blended with flat by LOSS)
const TAPE_FIR_N = 63;
function tapeLossFir(p, sr) {
  const N = TAPE_FIR_N, M = (N - 1) / 2, K = 256, mag = new Float64Array(K + 1), h = new Float64Array(N);
  for (let i = 0; i <= K; i++) { const f = i * sr / 2 / K; mag[i] = 1 + p.loss * (tapeLossAt(Math.max(1, f), p) - 1); }
  for (let n = 0; n < N; n++) {
    let s = mag[0] + mag[K] * Math.cos(Math.PI * (n - M));
    for (let i = 1; i < K; i++) s += 2 * mag[i] * Math.cos(Math.PI * i * (n - M) / K);
    const w = 0.42 - 0.5 * Math.cos(2 * Math.PI * n / (N - 1)) + 0.08 * Math.cos(4 * Math.PI * n / (N - 1));   // Blackman
    h[n] = s / (2 * K) * w;
  }
  let dc = 0; for (let n = 0; n < N; n++) dc += h[n];
  const want = mag[0]; if (Math.abs(dc) > 1e-9) for (let n = 0; n < N; n++) h[n] *= want / dc;
  return h;
}
// Jiles–Atherton (Ms, a, α, k, c): dM/dt for the field H and its rate Hd
const JA_MS = 1, JA_ALPHA = 1.6e-3 * 15.9;            // normalised: M in units of Ms, H in units of the physical a
function jaRate(H, Hd, M, a, k, c) {
  const Q = (H + JA_ALPHA * M) / a;
  let L, Lp;
  if (Math.abs(Q) < 1e-3) { L = Q / 3; Lp = 1 / 3 - Q * Q / 15; }
  else { const e = Math.exp(-2 * Math.abs(Q)), coth = (1 + e) / (1 - e) * (Q < 0 ? -1 : 1); L = coth - 1 / Q; const sh = Math.sinh(Q); Lp = 1 / (Q * Q) - (Math.abs(Q) > 350 ? 0 : 1 / (sh * sh)); }
  const Man = JA_MS * L, dM = Man - M, delta = Hd >= 0 ? 1 : -1;
  const dMflag = (delta > 0) === (dM > 0) ? 1 : 0;
  let den1 = (1 - c) * delta * k - JA_ALPHA * dM; if (Math.abs(den1) < 1e-6) den1 = den1 < 0 ? -1e-6 : 1e-6;
  const t1 = (1 - c) * dMflag * dM / den1 * Hd, t2 = c * (JA_MS / a) * Hd * Lp;
  let den = 1 - c * JA_ALPHA * (JA_MS / a) * Lp; if (den < 1e-3) den = 1e-3;
  return (t1 + t2) / den;
}
class TapeDSP {
  constructor(sr, channels, params, opts) {
    this.sr = sr; this.nch = Math.max(1, channels || 2); this.hissScale = opts && opts.hissScale !== undefined ? opts.hissScale : 1;
    this.p = tapeNorm(params); this.rng = tapeRng(this.p.seed);
    // per channel: oversampling filters, JA state, FIR history, delay line, degrade / chew filters
    this.ch = [];
    const D = Math.ceil(0.06 * sr);
    for (let c = 0; c < this.nch; c++) this.ch.push({ up1: null, up2: null, dn1: null, dn2: null, H: 0, Hd: 0, M: 0,
      fir: new Float64Array(TAPE_FIR_N * 2), fi: 0, line: new Float32Array(D), dry: new Float32Array(D), w: 0,
      pre: null, post: null, bump: null, age: null, chewLp: null, env: 0, hiss: null, comp: 0 });
    this.D = D; this.t = 0;
    this.wowPh = this.rng() * 6.283; this.flPh = [this.rng() * 6.283, this.rng() * 6.283, this.rng() * 6.283];
    this.wowVar = 0; this.flVar = 0; this.driftV = 0; this.degWalk = 0; this.chewLeft = 0; this.chewNext = 0; this.chewDepth = 0;
    this.setParams(this.p, true);
  }
  setParams(params, init) {
    const p = this.p = tapeNorm(Object.assign({}, this.p, params || {})), sr = this.sr, sr2 = sr * 2;
    // hysteresis: drive → field gain, saturation → the anhysteretic shape a, bias → coercivity k + reversibility c
    this.hGain = Math.pow(10, (-22 + 38 * p.drive) / 20);
    this.a = 0.35 * Math.pow(0.25, p.sat) + 0.05;
    this.k = (0.35 + 1.6 * (1 - p.bias)) * this.a * 4;
    this.c = 0.05 + 0.4 * p.bias;
    this.rk4 = p.mode !== 'rk2';
    this.norm = this._smallGain();
    this.inG = Math.pow(10, p.in / 20); this.outG = Math.pow(10, p.out / 20);
    const tilt = p.tone * 9;
    for (const ch of this.ch) {
      if (!ch.up1 || init) { ch.up1 = bq('lp', sr * 0.45, 0.541, 0, sr2); ch.up2 = bq('lp', sr * 0.45, 1.307, 0, sr2); ch.dn1 = bq('lp', sr * 0.45, 0.541, 0, sr2); ch.dn2 = bq('lp', sr * 0.45, 1.307, 0, sr2); }
      const pre = bq('hs', 1200, 0.6, tilt, sr), post = bq('hs', 1200, 0.6, -tilt, sr);
      if (!ch.pre) { ch.pre = pre; ch.post = post; } else { bqSet(ch.pre, pre); bqSet(ch.post, post); }
      // head bump: a low resonance that rises with tape speed (≈ 30 Hz at 3¾ ips … 120 Hz at 30)
      const bf = 30 * Math.sqrt(p.speed / 3.75), bump = bq('peak', bf, 1.4, 4.5 * p.bump, sr);
      if (!ch.bump) ch.bump = bump; else bqSet(ch.bump, bump);
      if (!ch.age) ch.age = bq('lp', 18000, 0.707, 0, sr);
      if (!ch.chewLp) ch.chewLp = bq('lp', 18000, 0.6, 0, sr);
      if (!ch.hiss) ch.hiss = { a: bq('hp', 900, 0.707, 0, sr), b: bq('lp', 9000, 0.707, 0, sr) };
    }
    this.fir = tapeLossFir(p, sr);
    // latency of the wet path (FIR centre + the wow line's resting delay): the dry path waits as long
    this.base = Math.round(0.006 * sr);
    this.latency = (TAPE_FIR_N - 1) / 2 + this.base;
  }
  // the small-signal gain of the tape at these settings (a quiet 1 kHz tone through a fresh state) → 1 / gain
  _smallGain() {
    const sr2 = this.sr * 2, n = Math.round(sr2 * 0.02), amp = 0.01;
    let H0 = 0, Hd0 = 0, M = 0, pk = 0;
    for (let i = 0; i < n; i++) {
      const H = amp * this.hGain * Math.sin(2 * Math.PI * 1000 * i / sr2), Hd = (H - H0) * sr2;
      M = this._step(H0, Hd0, H, Hd, M, 1 / sr2);
      if (i > n / 2) pk = Math.max(pk, Math.abs(M));
      H0 = H; Hd0 = Hd;
    }
    return pk > 1e-9 ? amp / pk : 1;
  }
  _step(H0, Hd0, H1, Hd1, M, T) {
    const a = this.a, k = this.k, c = this.c;
    if (this.rk4) {
      const Hm = (H0 + H1) / 2, Hdm = (Hd0 + Hd1) / 2;
      const k1 = T * jaRate(H0, Hd0, M, a, k, c), k2 = T * jaRate(Hm, Hdm, M + k1 / 2, a, k, c);
      const k3 = T * jaRate(Hm, Hdm, M + k2 / 2, a, k, c), k4 = T * jaRate(H1, Hd1, M + k3, a, k, c);
      M += (k1 + 2 * k2 + 2 * k3 + k4) / 6;
    } else {
      const k1 = T * jaRate(H0, Hd0, M, a, k, c), k2 = T * jaRate(H1, Hd1, M + k1, a, k, c);
      M += (k1 + k2) / 2;
    }
    if (!(M === M)) M = 0;                                        // NaN guard: restart from demagnetised
    return Math.max(-1.2, Math.min(1.2, M));
  }
  // one block: ins / outs are Float32Array per channel (outs may be ins). Params are read once per block.
  process(ins, outs, n) {
    const p = this.p, sr = this.sr, sr2 = sr * 2, T2 = 1 / sr2, R = this.rng, nch = this.nch;
    const D = this.D, fir = this.fir, FN = TAPE_FIR_N;
    // transport: wow + flutter (+ variance, drift) → delay in samples, shared by the channels (one capstan)
    const wowAmp = p.wow * p.wow * 0.0035 * sr, flAmp = p.flutter * p.flutter * 0.0004 * sr;
    const dly = new Float32Array(n);
    for (let i = 0; i < n; i++) {
      if ((this.t + i) % 64 === 0) {
        this.wowVar += (R() - 0.5) * 0.05 * p.wfVar - this.wowVar * 0.002; this.flVar += (R() - 0.5) * 0.08 * p.wfVar - this.flVar * 0.004;
        this.driftV += (R() - 0.5) * 0.02 * p.drift - this.driftV * 0.0005;
      }
      this.wowPh += 2 * Math.PI * p.wowRate * (1 + 0.6 * this.wowVar) / sr;
      const fr = 2 * Math.PI * p.flutRate * (1 + 0.4 * this.flVar) / sr;
      this.flPh[0] += fr; this.flPh[1] += fr * 2.03; this.flPh[2] += fr * 3.11;
      const wow = wowAmp * (1 + 0.5 * this.wowVar) * (0.5 + 0.5 * Math.sin(this.wowPh)) + Math.abs(this.driftV) * 0.004 * sr;
      const fl = flAmp * (0.55 * Math.sin(this.flPh[0]) + 0.3 * Math.sin(this.flPh[1]) + 0.15 * Math.sin(this.flPh[2]));
      dly[i] = Math.min(D - 4, this.base + wow + fl);
    }
    if (this.wowPh > 1e4) this.wowPh -= 2 * Math.PI * 1000;
    for (let j = 0; j < 3; j++) if (this.flPh[j] > 1e4) this.flPh[j] -= 2 * Math.PI * 1000;
    // degrade: a slowly wandering ageing low-pass and level; chew: occasional dull, dipping stretches
    this.degWalk += (R() - 0.5) * 0.2 * p.degVar - this.degWalk * 0.05;
    const ageHz = Math.max(900, 19000 * Math.pow(0.12, p.degrade * (1 + 0.5 * this.degWalk)));
    const hissG = p.degrade * p.degrade * 0.02 * this.hissScale, wander = 1 - p.degrade * 0.15 * Math.abs(this.degWalk);
    if (p.chew > 0) {
      if (this.chewLeft <= 0) {
        if (this.chewNext <= 0) this.chewNext = Math.round(sr * (0.3 + (1 - p.chewFreq) * 6) * (0.5 + R() * p.chewVar + (1 - p.chewVar) * 0.5));
        this.chewNext -= n;
        if (this.chewNext <= 0) { this.chewLeft = Math.round(sr * (0.05 + R() * 0.4 * (0.4 + p.chewVar))); this.chewDepth = p.chew * (1 - p.chewVar * 0.6 * R()); }
      } else this.chewLeft -= n;
    } else this.chewLeft = 0;
    const chewing = this.chewLeft > 0, cd = chewing ? this.chewDepth : 0;
    const chewHz = chewing ? Math.max(500, 16000 * Math.pow(0.08, cd)) : 18000;
    for (let c = 0; c < nch; c++) {
      const ch = this.ch[c], x = ins[Math.min(c, ins.length - 1)], y = outs[c];
      bqSet(ch.age, bq('lp', ageHz, 0.707, 0, sr)); bqSet(ch.chewLp, bq('lp', chewHz, 0.6, 0, sr));
      const ca = Math.exp(-1 / (0.01 * sr)), cr = Math.exp(-1 / (0.15 * sr));
      for (let i = 0; i < n; i++) {
        let v = x[i] * this.inG;
        ch.dry[ch.w] = x[i];
        v = bqRun(ch.pre, v);
        if (p.comp > 0) {                                         // feed-forward squeeze above −18 dBFS
          const a = Math.abs(v); ch.comp = a > ch.comp ? a + (ch.comp - a) * ca : a + (ch.comp - a) * cr;
          const over = ch.comp > 0.125 ? Math.pow(ch.comp / 0.125, -p.comp * 0.66) : 1; v *= over;
        }
        // hysteresis at 2×: zero-stuffed up, solved per sub-sample, band-limited down
        let out = 0;
        for (let s = 0; s < 2; s++) {
          const u = bqRun(ch.up2, bqRun(ch.up1, s === 0 ? v * 2 : 0));
          const H = u * this.hGain, Hd = (H - ch.H) * sr2;
          ch.M = this._step(ch.H, ch.Hd, H, Hd, ch.M, T2);
          ch.H = H; ch.Hd = Hd;
          const d = bqRun(ch.dn2, bqRun(ch.dn1, ch.M * this.norm));
          if (s === 0) out = d;
        }
        v = bqRun(ch.post, out);
        // the head's losses (FIR, circular history) + head bump
        ch.fir[ch.fi] = v; ch.fir[ch.fi + FN] = v;
        let acc = 0; for (let t = 0; t < FN; t++) acc += fir[t] * ch.fir[ch.fi + t];
        ch.fi = ch.fi === 0 ? FN - 1 : ch.fi - 1;
        v = bqRun(ch.bump, acc);
        // the transport: write, read back through the modulated delay (cubic)
        ch.line[ch.w] = v;
        const rp = ch.w - dly[i], i1 = Math.floor(rp), f = rp - i1;
        const g = k => ch.line[((i1 + k) % D + D) % D];
        const y0 = g(-1), y1 = g(0), y2 = g(1), y3 = g(2);
        v = y1 + 0.5 * f * (y2 - y0 + f * (2 * y0 - 5 * y1 + 4 * y2 - y3 + f * (3 * (y1 - y2) + y3 - y0)));
        // degrade + chew
        v = bqRun(ch.age, v) * wander;
        if (hissG > 0) v += bqRun(ch.hiss.b, bqRun(ch.hiss.a, R() * 2 - 1)) * hissG;
        if (chewing) { v = bqRun(ch.chewLp, v) * (1 - 0.5 * cd); v = Math.tanh(v * (1 + 3 * cd)) / (1 + 2 * cd); } else bqRun(ch.chewLp, v);
        const dr = ch.dry[((ch.w - this.latency) % D + D) % D];
        y[i] = (v * this.outG) * p.mix + dr * (1 - p.mix);
        ch.w = (ch.w + 1) % D;
      }
    }
    this.t += n;
  }
}
`;
  const core = new Function(TAPE_DSP + '\nreturn { TAPE_SPEC, tapeNorm, tapeLossAt, tapeLossFir, TapeDSP, TAPE_FIR_N };')();

  const WORKLET = TAPE_DSP + String.raw`
const TAPE_AUTO = ['drive', 'sat', 'bias', 'tone', 'wow', 'flutter', 'degrade', 'chew', 'mix'];
class MMTapeModel extends AudioWorkletProcessor {
  static get parameterDescriptors() { return TAPE_AUTO.map(k => ({ name: k, defaultValue: TAPE_SPEC[k].def, minValue: TAPE_SPEC[k].min, maxValue: TAPE_SPEC[k].max, automationRate: 'k-rate' })); }
  constructor(o) {
    super(); const po = (o && o.processorOptions) || {};
    this.dsp = new TapeDSP(sampleRate, 2, po.params || {}); this.alive = true; this.last = {};
    this.port.onmessage = e => { const d = e.data; if (d === 'stop') this.alive = false; else if (d && d.params) this.dsp.setParams(d.params); };
  }
  process(ins, outs, P) {
    const o = outs[0], i = ins[0], n = o[0].length;
    const ch = {}; let changed = false;
    for (const k of TAPE_AUTO) { const v = P[k][0]; if (this.last[k] !== v) { ch[k] = v; this.last[k] = v; changed = true; } }
    if (changed) this.dsp.setParams(ch);
    const src = i && i.length ? [i[0], i[1] || i[0]] : [new Float32Array(n), new Float32Array(n)];
    this.dsp.process(src, o.length > 1 ? o : [o[0], new Float32Array(n)], n);
    return this.alive;
  }
}
registerProcessor('mm-tape-model', MMTapeModel);
`;

  const READY = new WeakMap();
  function prepare(ctx) {
    let r = READY.get(ctx); if (r) return r;
    const AKx = typeof AK !== 'undefined' ? AK : root.AK;
    r = (async () => {
      if (!ctx.audioWorklet) return false;
      if (AKx && AKx.addWorklet) await AKx.addWorklet(ctx, WORKLET);
      else await ctx.audioWorklet.addModule('data:text/javascript;base64,' + btoa(unescape(encodeURIComponent(WORKLET))));
      return true;
    })().catch(e => { console.warn('tape_model worklet:', e && e.message); return false; });
    READY.set(ctx, r);
    return r;
  }
  function createNode(ctx, params) {
    const p = core.tapeNorm(params);
    const node = new AudioWorkletNode(ctx, 'mm-tape-model', { numberOfInputs: 1, numberOfOutputs: 1, outputChannelCount: [2], channelCount: 2, channelCountMode: 'explicit', channelInterpretation: 'speakers', processorOptions: { params: p } });
    for (const k of ['drive', 'sat', 'bias', 'tone', 'wow', 'flutter', 'degrade', 'chew', 'mix']) node.parameters.get(k).value = p[k];
    node.setParams = q => { for (const [k, v] of Object.entries(q || {})) { const prm = node.parameters.get(k); if (prm) prm.value = v; } node.port.postMessage({ params: q }); };
    node.stop = () => { try { node.port.postMessage('stop'); node.disconnect(); } catch (e) {} };
    return node;
  }
  // plain JS: the whole buffer through a fresh machine → new channels (same length; the latency is compensated)
  function processBuffer(channels, sampleRate, params, opts) {
    const nch = Math.max(1, channels.length), dsp = new core.TapeDSP(sampleRate, Math.max(2, nch), params, opts), L = channels[0].length, lat = dsp.latency;
    const outs = Array.from({ length: Math.max(2, nch) }, () => new Float32Array(L + lat)), B = 128;      // the worklet's render quantum: the same numbers either way
    const ins = Array.from({ length: Math.max(2, nch) }, (_, c) => channels[Math.min(c, nch - 1)]);
    for (let o = 0; o < L + lat; o += B) {
      const n = Math.min(B, L + lat - o);
      const bi = ins.map(x => { const b = new Float32Array(n); if (o < L) b.set(x.subarray(o, Math.min(L, o + n))); return b; }), bo = bi.map(() => new Float32Array(n));
      dsp.process(bi, bo, n);
      bo.forEach((b, c) => outs[c].set(b, o));
    }
    return outs.slice(0, Math.max(nch, 2)).map(x => x.slice(lat, lat + L)).slice(0, nch === 1 ? 1 : nch);
  }
  // a seamless loop through the machine: three passes, the middle one kept, its head crossfaded from the third pass's
  // head (which is what follows the middle's tail) — the loop point then continues the tape exactly
  function processLoop(channels, sampleRate, params, opts) {
    const L = channels[0].length, x3 = channels.map(c => { const o = new Float32Array(3 * L); o.set(c, 0); o.set(c, L); o.set(c, 2 * L); return o; });
    const y = processBuffer(x3, sampleRate, params, opts), F = Math.min(Math.round(0.06 * sampleRate), Math.floor(L / 4));
    return y.map(c => {
      const o = c.slice(L, 2 * L);
      for (let i = 0; i < F; i++) { const g = i / F; o[i] = c[2 * L + i] * (1 - g) + c[L + i] * g; }
      return o;
    });
  }
  // every stem through the same machine + seed (one transport: the stems still line up, and still sum to the mix);
  // hiss shared out so n stems carry one tape's hiss between them. stems: [[L, R], …] → the same shape
  function processStems(stems, sampleRate, params, { loop = false } = {}) {
    const opts = { hissScale: 1 / Math.max(1, stems.length) };
    return stems.map(chs => (loop ? processLoop : processBuffer)(chs, sampleRate, params, opts));
  }
  const lossResponse = (params, sr, freqs) => { const p = core.tapeNorm(params); return freqs.map(f => 20 * Math.log10(Math.max(1e-6, 1 + p.loss * (core.tapeLossAt(f, p) - 1)))); };

  // machines: starting points (CHOW Tape-style section settings), from pristine to wrecked
  const MACHINES = {
    master_30:   { name: '30 ips mastering deck', params: { speed: 30, drive: 0.35, sat: 0.4, bias: 0.7, spacing: 0.1, thickness: 1, gap: 1, bump: 0.6, wow: 0.03, flutter: 0.03, wfVar: 0.1, drift: 0 } },
    studio_15:   { name: '15 ips studio 2-track', params: { speed: 15, drive: 0.5, sat: 0.5, bias: 0.6, spacing: 0.15, thickness: 1.5, gap: 1.5, bump: 0.7, wow: 0.06, flutter: 0.06, wfVar: 0.2 } },
    reel_7:      { name: '7½ ips home reel', params: { speed: 7.5, drive: 0.55, sat: 0.55, bias: 0.5, spacing: 0.3, thickness: 2, gap: 2.5, bump: 0.6, wow: 0.15, flutter: 0.12, wfVar: 0.3, drift: 0.1 } },
    cassette:    { name: 'cassette deck', params: { speed: 1.875, drive: 0.55, sat: 0.6, bias: 0.45, spacing: 0.25, thickness: 0.8, gap: 1, bump: 0.5, wow: 0.25, flutter: 0.2, wfVar: 0.35, drift: 0.15, degrade: 0.2, tone: 0.2 } },
    worn_cassette: { name: 'worn cassette', params: { speed: 1.875, drive: 0.6, sat: 0.65, bias: 0.3, spacing: 0.7, thickness: 1.5, gap: 1.5, bump: 0.4, wow: 0.45, flutter: 0.35, wfVar: 0.6, drift: 0.35, degrade: 0.45, degVar: 0.5, chew: 0.25, chewFreq: 0.3 } },
    dictaphone:  { name: 'dictaphone / answering machine', params: { speed: 1.875, drive: 0.75, sat: 0.7, bias: 0.25, spacing: 1.2, thickness: 2, gap: 4, bump: 0.1, wow: 0.3, flutter: 0.5, flutRate: 11, wfVar: 0.5, degrade: 0.5, comp: 0.6, tone: 0.4 } },
    vhs:         { name: 'VHS hi-fi, warped', params: { speed: 1.875, drive: 0.5, sat: 0.5, bias: 0.4, spacing: 0.45, thickness: 1, gap: 1.2, wow: 0.7, wowRate: 0.35, flutter: 0.15, wfVar: 0.7, drift: 0.5, degrade: 0.35 } },
    chewed:      { name: 'chewed tape', params: { speed: 3.75, drive: 0.6, sat: 0.6, bias: 0.35, spacing: 0.5, thickness: 1.5, gap: 2, wow: 0.35, flutter: 0.3, wfVar: 0.6, degrade: 0.4, chew: 0.7, chewFreq: 0.7, chewVar: 0.7 } },
    hot_drive:   { name: 'slammed reel (drive)', params: { speed: 15, drive: 0.9, sat: 0.75, bias: 0.25, spacing: 0.2, thickness: 1.5, gap: 1.5, bump: 0.8, wow: 0.05, flutter: 0.05, out: 3 } },
  };
  const machine = id => MACHINES[id] ? Object.assign(core.tapeNorm({}), MACHINES[id].params) : null;

  root.TapeModel = { SPEC: core.TAPE_SPEC, norm: core.tapeNorm, DSP: core.TapeDSP, WORKLET, prepare, createNode, process: processBuffer, processLoop, processStems, lossResponse, lossAt: core.tapeLossAt,
    lossFir: core.tapeLossFir, MACHINES, machine, AUTO: ['drive', 'sat', 'bias', 'tone', 'wow', 'flutter', 'degrade', 'chew', 'mix'] };
  if (typeof module !== 'undefined' && module.exports) module.exports = root.TapeModel;
})(typeof window !== 'undefined' ? window : globalThis);
