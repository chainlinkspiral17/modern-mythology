/* daw_perf.js — PERFORMANCE TOOLS for the DAW (daw.html / daw_engine.js). Classic script, global DawPerf.
 *
 * Per-track live chain, in this order:   input → SCALE LOCK → CHORD → ARPEGGIATOR → device
 *   (and, with track.perf.onClips, the same chain over the track's clip notes on playback).
 * Plus GROOVE (project.groove: templates, per-role push / lay-back, accent maps, seeded humanize)
 * and STEP PROBABILITY (a pattern note's optional `p`), applied identically by live scheduling
 * and renderOffline. Music theory comes from seqgen.js (SeqGen.SCALES / deg2midi / rng / hash):
 * nothing here duplicates the scale tables.
 *
 * Data (all optional — a project without these plays exactly as before):
 *   track.perf = {
 *     scale:  { on, mode: 'nearest'|'up'|'down'|'filter' }     snap to project key + mode (ties go down);
 *                                                               filter drops out-of-scale notes
 *     chord:  { on, type: 'triad'|'seventh'|'sus2'|'sus4'|'power'|'custom', inv: 0..3,
 *               spread: 'close'|'open'|'wide', shape: [semitones] }   diatonic types follow key + mode;
 *               power = root·5th·octave; custom = the stored semitone shape (LEARN captures one)
 *     arp:    { on, mode: 'up'|'down'|'updown'|'random'|'played'|'chord', rate: '1/4'…'1/32T',
 *               oct: 1..4, gate: 0.05..2 (of a step), latch }
 *     onClips: bool      the chain also rewrites the track's clip notes on playback (deterministic)
 *     seed:   int        random arp + step probability (same seed → same notes, live and offline)
 *     groove: 0..1       this track's share of the project groove (timing, accents, humanize)
 *     nudge:  ms         this track early (−) / late (+), on top of its role's offset
 *   }
 *   project.groove = { on, type: 'mpc16'|'shuffle8'|'triplet'|'flat', swing: 0.5..0.75,
 *                      roles: { drums|bass|chords|lead|pad: ms (−30..30) },
 *                      accent: 'none'|'downbeat'|'backbeat'|'offbeat'|'hats'|[16 multipliers], accentDepth: 0..1,
 *                      human: { ms, vel, seed } }
 *     While a groove is on it replaces project.swing (the transport SWING slider); with no groove
 *     (or on:false) the engine runs the old swingDelay path untouched — bit-identical renders.
 *   pattern note { t, d, n, v, p? }   p = probability 0..1 (absent = always). Decided per occurrence,
 *     seeded by (track.perf.seed, track id, absolute tick, note) → the same in live play and offline.
 *   pattern.steps? = 8|12|16|24|32    the STEP view's resolution for that pattern (display only).
 *
 * API
 *   DawPerf.norm(perf) → perf with every default filled in    DawPerf.active(perf) / clipsActive(perf)
 *   DawPerf.snap(n, key, scale, mode) → note | null            DawPerf.chordOf(n, chord, key, scale) → notes
 *   DawPerf.processNotes(notes, perf, {key, scale, len}) → notes   the chain over a pattern (pure)
 *   DawPerf.clipNotes(pattern, perf, project) → notes          the same, cached per pattern + settings
 *   DawPerf.plays(seed, trackId, tick, n, p) → bool            step probability
 *   DawPerf.groove(project, track, spt) → null | { delay(tick) s, note(at, offTick, n, vel) → {on, off, v} }
 *   new DawPerf.Live(engine)   the live chain: input(tr, n, v, on, now) · range(t0, t1) (transport grid) ·
 *                              onPlay() · onStop(now) · reset(id) · resetAll() · learnChord(id, cb)
 *   Every note the live chain plays goes through engine.perfRecord(tr, n, v, on, when, {generated}) —
 *   the recording hook (see daw_engine.js).
 *
 * Arp clock: steps sit on the transport grid while it plays (scheduled from the engine's look-ahead
 * windows, so loops / tempo / groove follow), and free-run at the project tempo from the first key
 * when it is stopped. A 15 ms chord window lets a chord land before the first step.
 */
(function (root) {
  "use strict";
  const PPQ = 96, BAR = PPQ * 4, S16 = PPQ / 4;
  const LOOKAHEAD = 0.12, TICK_MS = 25, CHORD_MS = 15;
  const SG = () => (typeof SeqGen !== 'undefined' ? SeqGen : root.SeqGen);
  const mod = (a, m) => ((a % m) + m) % m;
  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));

  // ── settings ──────────────────────────────────────────────────────
  const RATES = { '1/4': 96, '1/4T': 64, '1/8': 48, '1/8T': 32, '1/16': 24, '1/16T': 16, '1/32': 12, '1/32T': 8 };
  const SCALE_MODES = ['nearest', 'up', 'down', 'filter'];
  const CHORD_DEG = { triad: [0, 2, 4], seventh: [0, 2, 4, 6], sus2: [0, 1, 4], sus4: [0, 3, 4] };   // scale degrees above the root
  const CHORD_TYPES = ['triad', 'seventh', 'sus2', 'sus4', 'power', 'custom'];
  const SPREADS = ['close', 'open', 'wide'];
  const ARP_MODES = ['up', 'down', 'updown', 'random', 'played', 'chord'];
  const DEF = {
    scale: { on: false, mode: 'nearest' },
    chord: { on: false, type: 'triad', inv: 0, spread: 'close', shape: [0, 4, 7] },
    arp: { on: false, mode: 'up', rate: '1/16', oct: 1, gate: 0.5, latch: false },
  };
  function norm(perf) {
    const p = perf || {};
    const sc = Object.assign({}, DEF.scale, p.scale), ch = Object.assign({}, DEF.chord, p.chord), ar = Object.assign({}, DEF.arp, p.arp);
    sc.on = !!sc.on; if (!SCALE_MODES.includes(sc.mode)) sc.mode = 'nearest';
    ch.on = !!ch.on; if (!CHORD_TYPES.includes(ch.type)) ch.type = 'triad';
    ch.inv = clamp(Math.round(+ch.inv) || 0, 0, 3); if (!SPREADS.includes(ch.spread)) ch.spread = 'close';
    ch.shape = (Array.isArray(ch.shape) ? ch.shape : []).map(x => Math.round(+x)).filter(x => Number.isFinite(x) && x >= -24 && x <= 36);
    if (!ch.shape.length) ch.shape = [0, 4, 7];
    ar.on = !!ar.on; if (!ARP_MODES.includes(ar.mode)) ar.mode = 'up';
    if (!RATES[ar.rate]) ar.rate = '1/16';
    ar.oct = clamp(Math.round(+ar.oct) || 1, 1, 4); ar.gate = clamp(+ar.gate || 0.5, 0.05, 2); ar.latch = !!ar.latch;
    return { scale: sc, chord: ch, arp: ar, onClips: !!p.onClips, seed: (Math.round(+p.seed) || 1) >>> 0,
             groove: p.groove == null || !Number.isFinite(+p.groove) ? 1 : clamp(+p.groove, 0, 1), nudge: clamp(+p.nudge || 0, -40, 40) };
  }
  const active = perf => !!perf && !!((perf.scale && perf.scale.on) || (perf.chord && perf.chord.on) || (perf.arp && perf.arp.on));
  const clipsActive = perf => active(perf) && !!perf.onClips;

  // ── theory (SeqGen's tables) ──────────────────────────────────────
  function scaleOf(P) { const S = SG().SCALES; return S[P && P.mode] || S.minor; }
  const inScale = (n, key, sc) => sc.includes(mod(n - key, 12));
  // the nearest scale note (ties go down) / the next one up / down; filter → null
  function snap(n, key, sc, mode) {
    if (inScale(n, key, sc)) return n;
    if (mode === 'filter') return null;
    for (let d = 1; d < 12; d++) {
      if (mode !== 'up' && n - d >= 0 && inScale(n - d, key, sc)) return n - d;
      if (mode !== 'down' && n + d <= 127 && inScale(n + d, key, sc)) return n + d;
    }
    return n;
  }
  // a chord on note n. Diatonic types stack scale degrees on n's degree (an out-of-scale n is the chord of
  // the scale note below it, shifted up the difference). Voicing: inversion (lowest notes up an octave),
  // spread open = drop-2, wide = every other note up an octave.
  function chordOf(n, ch, key, sc) {
    let tones;
    if (ch.type === 'power') tones = [n, n + 7, n + 12];
    else if (ch.type === 'custom') tones = [...new Set(ch.shape)].map(x => n + x);
    else {
      let r = n; while (!inScale(r, key, sc) && r > n - 12) r--;
      const i = sc.indexOf(mod(r - key, 12)), oct = Math.floor((r - key) / 12) - 1, off = n - r;
      tones = (CHORD_DEG[ch.type] || CHORD_DEG.triad).map(k => SG().deg2midi(key, sc, i + k, oct) + off);
    }
    const up = a => a.sort((x, y) => x - y);
    up(tones);
    for (let j = 0; j < Math.min(ch.inv, tones.length - 1); j++) { tones.push(tones.shift() + 12); up(tones); }
    if (ch.spread === 'open' && tones.length >= 3) { tones[tones.length - 2] -= 12; up(tones); }
    else if (ch.spread === 'wide') { tones = tones.map((x, j) => (j % 2 ? x + 12 : x)); up(tones); }
    return [...new Set(tones)].filter(x => x >= 0 && x <= 127);
  }

  // ── arpeggiator core (shared by the live arp and the clip chain) ──
  const rand = (seed, key) => SG().rng(SG().hash(seed + ':' + key));
  // groups: [{ tones, v, order, … }] (a held key after scale lock + chord) → the cycle [{ n, g }]
  function arpSeq(groups, ar) {
    const owner = new Map(); let base;
    for (const g of groups.slice().sort((a, b) => a.order - b.order)) for (const t of g.tones) if (!owner.has(t)) owner.set(t, g);
    if (ar.mode === 'played') base = [...owner.keys()];
    else base = [...owner.keys()].sort((a, b) => a - b);
    let seq = [];
    for (let o = 0; o < ar.oct; o++) for (const t of base) if (t + 12 * o <= 127) seq.push({ n: t + 12 * o, g: owner.get(t) });
    if (ar.mode === 'down') seq.reverse();
    else if (ar.mode === 'updown') seq = seq.concat(seq.slice(1, -1).reverse());   // no repeated top / bottom
    return seq;
  }
  function arpPick(seq, ar, k, rnd) {
    if (!seq.length) return [];
    if (ar.mode === 'chord') return seq;
    if (ar.mode === 'random') return [seq[Math.floor(rnd() * seq.length)]];
    return [seq[k % seq.length]];
  }

  // ── the chain over a pattern's notes (pure; same input → same output) ──
  // ctx: { key, scale, len (ticks) }. Arp steps sit on the pattern's own grid; a note joins at the
  // first step at/after its start (6-tick tolerance) and stays while it is held. The step counter
  // restarts when the held set was empty. Notes derived from a note with a probability carry
  // p + its source (pt, pn), so a chord / an arp run from one step is kept or dropped as a whole.
  function processNotes(notes, perf, ctx) {
    const pf = norm(perf), out = [], groups = [];
    notes.forEach((n, i) => {
      let m = n.n;
      if (pf.scale.on) { m = snap(m, ctx.key, ctx.scale, pf.scale.mode); if (m == null) return; }
      const tones = pf.chord.on ? chordOf(m, pf.chord, ctx.key, ctx.scale) : [m];
      if (tones.length) groups.push({ t: n.t, d: n.d, v: n.v, p: n.p, src: n, order: i, tones });
    });
    const tag = (o, g) => { if (g.p !== undefined && g.p !== null && g.p < 1) { o.p = g.p; o.pt = g.src.t; o.pn = g.src.n; } return o; };
    if (!pf.arp.on) { for (const g of groups) for (const t of g.tones) out.push(tag({ t: g.t, d: g.d, n: t, v: g.v }, g)); }
    else {
      const ar = pf.arp, rate = RATES[ar.rate], gate = Math.max(1, Math.round(rate * ar.gate)), tol = Math.min(6, rate / 4);
      for (const g of groups) g.first = Math.max(0, Math.ceil((g.t - tol) / rate) * rate);
      let k = 0, idle = true;
      for (let s = 0; s < ctx.len; s += rate) {
        const held = groups.filter(g => s >= g.first && (s < g.t + g.d || s === g.first));
        if (!held.length) { idle = true; continue; }
        if (idle) { k = 0; idle = false; }
        for (const x of arpPick(arpSeq(held, ar), ar, k, rand(pf.seed, 'clip:' + s))) out.push(tag({ t: s, d: gate, n: x.n, v: x.g.v }, x.g));
        k++;
      }
    }
    out.sort((a, b) => a.t - b.t || a.n - b.n);
    return out;
  }
  function sigNotes(notes) {
    let h = 2166136261 >>> 0;
    for (const n of notes) for (const x of [n.t, n.d, n.n, n.v, n.p === undefined || n.p === null ? -1 : n.p]) { h ^= Math.round(x * 1000) | 0; h = Math.imul(h, 16777619); }
    return notes.length + ':' + (h >>> 0);
  }
  const cache = new WeakMap();
  function clipNotes(p, perf, P) {
    const sig = JSON.stringify(norm(perf)) + '|' + P.key + '|' + P.mode + '|' + p.lenBars + '|' + sigNotes(p.notes);
    const c = cache.get(p); if (c && c.sig === sig) return c.out;
    const out = processNotes(p.notes, perf, { key: P.key, scale: scaleOf(P), len: p.lenBars * BAR });
    cache.set(p, { sig, out });
    return out;
  }

  // ── step probability ──────────────────────────────────────────────
  function plays(seed, trackId, tick, n, prob) {
    if (prob === undefined || prob === null || prob >= 1) return true;
    if (!(prob > 0)) return false;
    return rand(seed, trackId + ':' + tick + ':' + n)() < prob;
  }

  // ── groove ────────────────────────────────────────────────────────
  // templates warp a note's position inside a period (piecewise linear, so on < off stays true):
  //   mpc16    the off 16th lands at `swing` of an 8th (50 % straight, 66.7 % triplet, 75 % dotted)
  //   shuffle8 the off 8th lands at `swing` of a quarter
  //   triplet  16ths pulled onto a 12/8 feel (¼ → ⅓, ½ → ⅔, ¾ → ⅚ of the beat)
  //   flat     no timing — accents, role offsets and humanize only
  const GROOVES = {
    mpc16: { name: 'MPC 16', period: S16 * 2 },
    shuffle8: { name: '8 SHUFFLE', period: PPQ },
    triplet: { name: 'TRIPLET', period: PPQ, map: [[0, 0], [24, 32], [48, 64], [72, 80], [96, 96]] },
    flat: { name: 'FLAT', period: 0 },
  };
  const ACCENTS = {   // velocity multipliers per 16th of the bar
    none: null,
    downbeat: [1.2, 0.8, 0.9, 0.8, 1.05, 0.8, 0.9, 0.8, 1.1, 0.8, 0.9, 0.8, 1.05, 0.8, 0.9, 0.8],
    backbeat: [1.0, 0.8, 0.9, 0.8, 1.2, 0.8, 0.9, 0.8, 1.0, 0.8, 0.9, 0.8, 1.2, 0.8, 0.9, 0.8],
    offbeat: [0.85, 0.8, 1.15, 0.8, 0.85, 0.8, 1.15, 0.8, 0.85, 0.8, 1.15, 0.8, 0.85, 0.8, 1.15, 0.8],
    hats: [1.0, 0.65, 0.85, 0.65, 1.0, 0.65, 0.85, 0.65, 1.0, 0.65, 0.85, 0.65, 1.0, 0.65, 0.85, 0.7],
  };
  const ROLES = ['drums', 'bass', 'chords', 'lead', 'pad'];
  const GDEF = { on: true, type: 'mpc16', swing: 0.58, roles: {}, accent: 'none', accentDepth: 0.5, human: { ms: 0, vel: 0, seed: 1 } };
  function grooveNorm(g) {
    const o = Object.assign({}, GDEF, g || {});
    o.on = o.on !== false; if (!GROOVES[o.type]) o.type = 'mpc16';
    o.swing = clamp(+o.swing || 0.5, 0.5, 0.75);
    const roles = {}; for (const r of ROLES) roles[r] = clamp(+((o.roles || {})[r]) || 0, -30, 30); o.roles = roles;
    if (!(Array.isArray(o.accent) && o.accent.length === 16) && !(o.accent in ACCENTS)) o.accent = 'none';
    o.accentDepth = clamp(o.accentDepth == null ? 0.5 : +o.accentDepth || 0, 0, 1);
    const h = Object.assign({}, GDEF.human, o.human || {});
    o.human = { ms: clamp(+h.ms || 0, 0, 30), vel: clamp(+h.vel || 0, 0, 0.5), seed: (Math.round(+h.seed) || 1) >>> 0 };
    return o;
  }
  function warp(type, swing, tick) {        // template offset in ticks
    const T = GROOVES[type]; if (!T || !T.period) return 0;
    const per = T.period, x = mod(tick, per), pts = T.map || [[0, 0], [per / 2, per * swing], [per, per]];
    for (let i = 1; i < pts.length; i++) if (x <= pts[i][0]) { const a = pts[i - 1], b = pts[i]; return a[1] + (b[1] - a[1]) * (x - a[0]) / (b[0] - a[0]) - x; }
    return 0;
  }
  // null when the project has no groove (the engine then keeps its old swing path)
  function groove(P, tr, spt) {
    const g0 = P && P.groove; if (!g0 || g0.on === false) return null;
    const G = grooveNorm(g0), pf = norm(tr && tr.perf), amt = pf.groove, tid = tr ? tr.id : '';
    const shift = (((tr && tr.role && G.roles[tr.role]) || 0) + pf.nudge) / 1000;
    const acc = Array.isArray(G.accent) ? G.accent : ACCENTS[G.accent];
    const delay = tick => warp(G.type, G.swing, tick) * amt * spt + shift;
    const note = (at, offTick, n, v) => {
      let h = 0, dv = 0;
      if (G.human.ms > 0 || G.human.vel > 0) { const r = rand(G.human.seed, tid + ':' + at + ':' + n); h = (r() * 2 - 1) * G.human.ms / 1000 * amt; dv = (r() * 2 - 1) * G.human.vel * amt; }
      let m = 1;
      if (acc) { const i = mod(Math.round(mod(at, BAR) / S16), 16); m = 1 + G.accentDepth * amt * ((+acc[i] || 1) - 1); }
      return { on: delay(at) + h, off: delay(offTick) + h, v: clamp(v * m + dv, 0.02, 1) };
    };
    return { delay, note, settings: G };
  }

  // ═══════════════════════════════════════════════════════════════════
  // live chain, per track: input → scale lock → chord → arp → device (+ engine.perfRecord)
  // ═══════════════════════════════════════════════════════════════════
  class Live {
    constructor(engine) { this.E = engine; this.st = new Map(); this.timer = null; this.learn = null; }
    _s(id) { let s = this.st.get(id); if (!s) { s = { ins: new Map(), sound: new Map(), arp: null }; this.st.set(id, s); } return s; }
    _key() { const P = this.E.project; return { key: P.key, scale: scaleOf(P) }; }
    learning(id) { return !!(this.learn && this.learn.id === id); }
    // hold a chord on the keys; on release its shape (semitones above the lowest note) goes to cb
    learnChord(id, cb) { this.learn = cb ? { id, held: new Set(), all: new Set(), cb } : null; }

    input(tr, n, v, on, now) {
      const s = this._s(tr.id);
      if (this.learning(tr.id)) {                       // learning a custom chord: play it raw
        const L = this.learn;
        if (on) { L.held.add(n); L.all.add(n); s.ins.set(n, { tones: [n], arp: false }); this._on(tr, s, n, v, now); }
        else {
          L.held.delete(n); const r = s.ins.get(n); s.ins.delete(n); if (r) this._off(tr, s, n, now);
          if (!L.held.size && L.all.size) { const a = [...L.all].sort((x, y) => x - y); this.learn = null; L.cb(a.map(x => x - a[0])); }
        }
        return;
      }
      const pf = norm(tr.perf), k = this._key();
      if (on) {
        if (s.ins.has(n)) this.input(tr, n, 0, false, now);        // a second note-on without an off
        const m = pf.scale.on ? snap(n, k.key, k.scale, pf.scale.mode) : n;
        if (m == null) { s.ins.set(n, null); return; }               // filtered out
        const tones = pf.chord.on ? chordOf(m, pf.chord, k.key, k.scale) : [m];
        s.ins.set(n, { tones, arp: pf.arp.on });
        if (pf.arp.on) this._arpAdd(tr, s, n, tones, v, now, pf);
        else for (const t of tones) this._on(tr, s, t, v, now);
      } else {
        const r = s.ins.get(n); s.ins.delete(n);
        if (r && r.arp && s.arp) this._arpRelease(s, n, pf);
        if (r && !r.arp) for (const t of r.tones) this._off(tr, s, t, now);
      }
    }
    // direct (non-arp) notes are ref-counted: two chords sharing a note keep it until both let go
    _on(tr, s, n, v, when) {
      const c = s.sound.get(n) || 0; s.sound.set(n, c + 1); if (c) return;
      const inst = this.E.devices.get(tr.deviceId);
      if (inst) { try { inst.noteOn(n, v, when, tr.channel); } catch (e) { /* device mid-reload */ } }
      this.E.perfRecord(tr, n, v, true, when, { generated: false });
    }
    _off(tr, s, n, when) {
      const c = s.sound.get(n) || 0; if (!c) return;
      if (c > 1) { s.sound.set(n, c - 1); return; }
      s.sound.delete(n);
      const inst = this.E.devices.get(tr.deviceId);
      if (inst) { try { inst.noteOff(n, when, tr.channel); } catch (e) {} }
      this.E.perfRecord(tr, n, 0, false, when, { generated: false });
    }

    // ── arp ─────────────────────────────────────────────────────────
    _arpAdd(tr, s, n, tones, v, now, pf) {
      const A = s.arp || (s.arp = { groups: [], phys: new Set(), k: 0, order: 0, running: false, free: null, lastAt: -1, released: false });
      if (pf.arp.latch && !A.phys.size && A.released) { A.groups = []; A.k = 0; }    // a fresh chord replaces the latched one
      A.released = false;
      A.phys.add(n);
      A.groups = A.groups.filter(g => g.id !== n);
      A.groups.push({ id: n, tones, v, order: A.order++ });
      if (!A.running) this._arpStart(tr, A, now);
    }
    _arpRelease(s, n, pf) {
      const A = s.arp; A.phys.delete(n);
      if (pf.arp.latch) { if (!A.phys.size) A.released = true; return; }
      A.groups = A.groups.filter(g => g.id !== n);
    }
    _arpStart(tr, A, now) {
      const E = this.E;
      A.running = true; A.k = 0;
      if (E.playing) { A.free = null; const id = tr.id; setTimeout(() => this._catchUp(id), CHORD_MS); }
      else { A.free = { ctx: now + (CHORD_MS + 10) / 1000, spt: E.spt(), g: 0 }; this._timer(); setTimeout(() => this._tick(), CHORD_MS); }
    }
    // transport running: the steps between now and the engine's scheduled horizon (later ones come from range())
    _catchUp(id) {
      const E = this.E, s = this.st.get(id), A = s && s.arp, tr = E.track(id);
      if (!A || !A.running || A.free || !E.playing || !tr || !E.anchor) return;
      const now = E.ctx.currentTime; if (E.anchor.ctx > now) return;   // lead-in / just wrapped: range() covers it
      const t0 = E.tickNow(), t1 = E.schedTick; if (!(t1 > t0)) return;
      this._steps(tr, s, A, norm(tr.perf), t0, t1, tk => E.timeOf(tk), now);
    }
    // the engine's look-ahead window [t0, t1) ticks, while the transport plays
    range(t0, t1) {
      const E = this.E;
      for (const [id, s] of this.st) {
        const A = s.arp; if (!A || !A.running || A.free) continue;
        const tr = E.track(id); if (!tr) { A.running = false; continue; }
        this._steps(tr, s, A, norm(tr.perf), t0, t1, tk => E.timeOf(tk), -Infinity);
      }
    }
    _steps(tr, s, A, pf, t0, t1, timeOf, minTime) {
      if (!pf.arp.on) { A.running = false; return; }
      const E = this.E, rate = RATES[pf.arp.rate], spt = E.spt(), gr = groove(E.project, tr, spt);
      for (let g = Math.ceil(t0 / rate - 1e-6) * rate; g < t1; g += rate) {
        const at = timeOf(g) + (gr ? gr.delay(g) : E.swingDelay(g));
        if (at < minTime) continue;
        if (A.lastAt >= 0 && at < A.lastAt + rate * spt * 0.5) continue;    // free → transport hand-over
        if (!this._step(tr, A, pf, g, timeOf, gr)) return;
        A.lastAt = at;
      }
    }
    _step(tr, A, pf, g, timeOf, gr) {
      if (!A.groups.length) { A.running = false; return false; }
      const E = this.E, ar = pf.arp, rate = RATES[ar.rate], spt = E.spt(), gateT = rate * ar.gate;
      const inst = E.devices.get(tr.deviceId);
      const pick = arpPick(arpSeq(A.groups, ar), ar, A.k, rand(pf.seed, 'live:' + A.k));
      for (const x of pick) {
        let on, off, v = x.g.v;
        if (gr) { const q = gr.note(g, g + gateT, x.n, v); on = timeOf(g) + q.on; off = timeOf(g) + gateT * spt + q.off; v = q.v; }
        else { on = timeOf(g) + E.swingDelay(g); off = on + gateT * spt; }
        off = Math.max(on + 0.005, off - 0.002);
        if (inst) { try { inst.noteOn(x.n, v, on, tr.channel); inst.noteOff(x.n, off, tr.channel); } catch (e) {} }
        E.perfRecord(tr, x.n, v, true, on, { generated: true });
        E.perfRecord(tr, x.n, 0, false, off, { generated: true });
      }
      A.k++;
      return true;
    }
    _timer() { if (!this.timer) this.timer = setInterval(() => this._tick(), TICK_MS); }
    // stopped transport: free-running arps at the project tempo
    _tick() {
      const E = this.E; let any = false;
      if (E.ctx && E.project && !E.playing) {
        const now = E.ctx.currentTime, horizon = now + LOOKAHEAD;
        for (const [id, s] of this.st) {
          const A = s.arp; if (!A || !A.running || !A.free) continue;
          const tr = E.track(id); if (!tr) { A.running = false; continue; }
          const pf = norm(tr.perf), F = A.free, spt = E.spt(), rate = RATES[pf.arp.rate];
          if (spt !== F.spt) { F.ctx += F.g * (F.spt - spt); F.spt = spt; }     // tempo change: the next step keeps its time
          const tEnd = (horizon - F.ctx) / spt;
          if (tEnd > F.g) { this._steps(tr, s, A, pf, F.g, tEnd, tk => F.ctx + tk * spt, -Infinity); F.g = Math.ceil(tEnd / rate - 1e-6) * rate; }
          if (A.running) any = true;
        }
      }
      if (!any && this.timer) { clearInterval(this.timer); this.timer = null; }
    }
    onPlay() { for (const s of this.st.values()) if (s.arp && s.arp.running && s.arp.free) s.arp.free = null; }
    onStop(now) {
      let any = false;
      for (const s of this.st.values()) { const A = s.arp; if (A && A.running && !A.free) { A.free = { ctx: now + 0.03, spt: this.E.spt(), g: 0 }; A.lastAt = -1; any = true; } }
      if (any) this._timer();
    }
    // settings changed / track gone: let go of everything this track's chain is holding
    reset(id) {
      const s = this.st.get(id); if (!s) return;
      const tr = this.E.track(id), now = this.E.ctx ? this.E.ctx.currentTime : 0;
      if (tr) for (const n of [...s.sound.keys()]) { s.sound.set(n, 1); this._off(tr, s, n, now); }
      this.st.delete(id);
      if (this.learn && this.learn.id === id) this.learn = null;
    }
    resetAll() { for (const id of [...this.st.keys()]) this.reset(id); this.st.clear(); }
  }

  const API = { PPQ, BAR, RATES, SCALE_MODES, CHORD_TYPES, SPREADS, ARP_MODES, GROOVES, ACCENTS, ROLES, DEF, GDEF,
                norm, active, clipsActive, scaleOf, inScale, snap, chordOf, arpSeq, arpPick, processNotes, clipNotes,
                plays, grooveNorm, warp, groove, Live };
  root.DawPerf = API;
})(typeof window !== 'undefined' ? window : globalThis);
