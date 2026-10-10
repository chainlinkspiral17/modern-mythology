/* seqgen.js — generative composer for the MM tools.
 *
 * Pure functions, no audio: give it a seed, a style, a key and a form
 * and it writes drums, bass, chords, lead and pad parts as note lists
 * plus an arrangement. Same seed → same song. Works in a page and in
 * Node (module.exports) so it can be tested headless.
 *
 *   SeqGen.song({ seed, style, key, mode, bpm, form, density })
 *     → { bpm, swing, key, mode, style, form, progression, sections[],
 *         parts: { drums|bass|chords|lead|pad: { role, patterns{pid:{name,lenBars,notes[]}}, clips[{bar,pid}], preset } } }
 *   SeqGen.part(role, songResult, { seed })    re-roll one part in place
 *   SeqGen.moodFromText(title, desc, id)       catalog brief → song options
 *
 * Notes are { t, d, n, v } — start tick, duration ticks, MIDI note,
 * velocity 0..1 — at SeqGen.PPQ ticks per quarter note.
 * Drums use General MIDI notes (36 kick, 38 snare, 39 clap, 42/46 hats,
 * 37 rim, 45 tom, 51 ride, 49 crash, 70 shaker) — the Felucca family,
 * X0X and the DAW's FORGE kit all take GM.
 */
(function (root) {
  "use strict";

  const PPQ = 96, BEAT = PPQ, BAR = PPQ * 4, S16 = PPQ / 4;
  const GM = { kick: 36, rim: 37, snare: 38, clap: 39, hat_c: 42, tom: 45, hat_o: 46, crash: 49, ride: 51, shaker: 70 };

  // ── seeded RNG ──────────────────────────────────────────────────
  function rng(seed) {
    let a = (typeof seed === 'number' ? seed : hash(String(seed))) >>> 0 || 1;
    const f = () => { a |= 0; a = (a + 0x6D2B79F5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
    f.int = (lo, hi) => lo + Math.floor(f() * (hi - lo + 1));
    f.pick = arr => arr[Math.floor(f() * arr.length)];
    f.chance = p => f() < p;
    f.weighted = pairs => { const tot = pairs.reduce((s, p) => s + p[1], 0); let x = f() * tot; for (const [v, w] of pairs) { if ((x -= w) <= 0) return v; } return pairs[pairs.length - 1][0]; };
    return f;
  }
  function hash(s) { let h = 2166136261; for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); } return h >>> 0; }

  // ── theory ──────────────────────────────────────────────────────
  const SCALES = {
    major: [0, 2, 4, 5, 7, 9, 11], minor: [0, 2, 3, 5, 7, 8, 10], dorian: [0, 2, 3, 5, 7, 9, 10],
    phrygian: [0, 1, 3, 5, 7, 8, 10], mixolydian: [0, 2, 4, 5, 7, 9, 10], lydian: [0, 2, 4, 6, 7, 9, 11],
    harmonic: [0, 2, 3, 5, 7, 8, 11],
  };
  const MINORISH = { minor: 1, dorian: 1, phrygian: 1, harmonic: 1 };
  const NOTE_NAMES = ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B'];
  // scale degree (0-based, may exceed 6 / go negative) → MIDI note around octave `oct`
  function deg2midi(key, scale, deg, oct) {
    const n = scale.length, o = Math.floor(deg / n), i = ((deg % n) + n) % n;
    return 12 * (oct + 1) + key + scale[i] + 12 * o;
  }
  // chord tones of a scale-degree chord: degrees deg, +2, +4 (+6)
  function chordDegrees(deg, seventh) { return seventh ? [deg, deg + 2, deg + 4, deg + 6] : [deg, deg + 2, deg + 4]; }
  function chordPCs(key, scale, deg, seventh) { return chordDegrees(deg, seventh).map(d => ((deg2midi(key, scale, d, 4)) % 12 + 12) % 12); }
  function nearestPC(target, pcs, lo, hi) {
    let best = null, bd = 1e9;
    for (let n = lo; n <= hi; n++) { if (!pcs.includes(((n % 12) + 12) % 12)) continue; const d = Math.abs(n - target); if (d < bd) { bd = d; best = n; } }
    return best ?? target;
  }
  function inScale(n, key, scale) { return scale.includes(((n - key) % 12 + 12) % 12); }

  // progressions as scale degrees (0 = tonic), 4 chords, one per bar
  const PROGS = {
    minor: [[0, 5, 2, 6], [0, 3, 4, 0], [0, 6, 5, 6], [0, 0, 5, 4], [0, 5, 3, 4], [0, 3, 0, 6], [0, 2, 5, 6], [0, 0, 3, 3]],
    major: [[0, 5, 3, 4], [0, 4, 5, 3], [1, 4, 0, 0], [0, 3, 0, 4], [0, 3, 5, 4], [0, 2, 3, 4], [3, 4, 0, 0], [0, 6, 3, 0]],
    modal: [[0, 6, 0, 6], [0, 1, 0, 1], [0, 3, 0, 3], [0, 0, 6, 6], [0, 6, 5, 6]],
    drone: [[0, 0, 0, 0], [0, 0, 5, 5], [0, 0, 3, 3]],
  };

  // ── styles ──────────────────────────────────────────────────────
  // drum grids: 16 steps per bar, values = probability (0..1); `acc` accents
  const STYLES = {
    four_floor: { name: 'four on the floor', bpm: [118, 126], swing: 0.0, prog: 'minor', modes: ['minor', 'dorian'],
      drums: { kick: '1000100010001000', clap: '0000100000001000', hat_c: '0010001000100010', hat_o: '0000000000000000', shaker: '1111111111111111/0.35' },
      bass: 'offbeat8', chords: 'stabs', lead: 'sparse', pad: 'swell', presets: { bass: 'bass_sub', chords: 'keys_organ', lead: 'pluck_bell', pad: 'pad_glass' } },
    boom_bap: { name: 'boom bap', bpm: [84, 94], swing: 0.55, prog: 'minor', modes: ['minor', 'dorian'],
      drums: { kick: '1000000010100000', snare: '0000100000001000', hat_c: '1010101010101010', rim: '0000000100000010/0.4' },
      bass: 'syncop', chords: 'comp', lead: 'motif', pad: 'none', ghost: true, presets: { bass: 'bass_sub', chords: 'keys_ep', lead: 'pluck_marimba', pad: 'pad_warm' } },
    lofi: { name: 'lo-fi', bpm: [70, 86], swing: 0.45, prog: 'major', modes: ['major', 'dorian'],
      drums: { kick: '1000000010010000', snare: '0000100000001000', hat_c: '1010101010101010/0.8', shaker: '0010001000100010/0.5' },
      bass: 'syncop', chords: 'pad', lead: 'motif', pad: 'none', ghost: true, presets: { bass: 'bass_sub', chords: 'keys_ep', lead: 'pluck_bell', pad: 'pad_warm' } },
    trap: { name: 'trap', bpm: [130, 145], swing: 0.0, prog: 'minor', modes: ['minor', 'phrygian', 'harmonic'],
      drums: { kick: '1000000100100000', clap: '0000000010000000', hat_c: '1111111111111111/0.9' },
      bass: 'drone808', chords: 'pad', lead: 'motif', pad: 'swell', rolls: true, presets: { bass: 'bass_sub', chords: 'pad_glass', lead: 'lead_square', pad: 'choir_vox' } },
    dnb: { name: 'drum & bass', bpm: [168, 176], swing: 0.0, prog: 'minor', modes: ['minor', 'dorian'],
      drums: { kick: '1000000000100000', snare: '0000100000001000', hat_c: '1010101010101010/0.7', ride: '0010001000100010/0.3' },
      bass: 'rolling', chords: 'pad', lead: 'sparse', pad: 'swell', presets: { bass: 'bass_reese', chords: 'pad_warm', lead: 'lead_saw', pad: 'pad_glass' } },
    shuffle: { name: 'gulf-coast shuffle', bpm: [92, 112], swing: 0.62, prog: 'major', modes: ['mixolydian', 'major'],
      drums: { kick: '1000000010000000', snare: '0000100000001000', ride: '1010101010101010', hat_c: '0000100000001000/0.6' },
      bass: 'walking', chords: 'comp', lead: 'motif', pad: 'none', presets: { bass: 'bass_sub', chords: 'keys_organ', lead: 'keys_ep', pad: 'strings_ensemble' } },
    motorik: { name: 'motorik', bpm: [112, 124], swing: 0.0, prog: 'modal', modes: ['dorian', 'mixolydian'],
      drums: { kick: '1000100010001000', snare: '0000100000001000', hat_c: '1010101010101010' },
      bass: 'pulse8', chords: 'arp', lead: 'sparse', pad: 'swell', presets: { bass: 'bass_acid', chords: 'arp_chip', lead: 'lead_saw', pad: 'pad_glass' } },
    synthwave: { name: 'synthwave', bpm: [96, 108], swing: 0.0, prog: 'minor', modes: ['minor', 'dorian'],
      drums: { kick: '1000100010001000', snare: '0000100000001000', hat_c: '0010001000100010', clap: '0000100000001000/0.5' },
      bass: 'pulse8', chords: 'pad', lead: 'motif', pad: 'swell', presets: { bass: 'bass_acid', chords: 'pad_warm', lead: 'lead_saw', pad: 'strings_ensemble' } },
    noir: { name: 'slow noir', bpm: [64, 80], swing: 0.58, prog: 'minor', modes: ['minor', 'harmonic', 'phrygian'],
      drums: { kick: '1000000000000000/0.8', rim: '0000100000001000/0.7', ride: '1010101010101010/0.75' },
      bass: 'walking', chords: 'pad', lead: 'motif', pad: 'swell', presets: { bass: 'bass_sub', chords: 'keys_ep', lead: 'keys_ep', pad: 'drone_dark' } },
    ambient: { name: 'ambient bed', bpm: [60, 76], swing: 0.0, prog: 'drone', modes: ['lydian', 'dorian', 'minor', 'major'],
      drums: { shaker: '0010000000100000/0.25', rim: '0000000000000100/0.15' },
      bass: 'drone', chords: 'swell', lead: 'sparse', pad: 'drone', presets: { bass: 'drone_dark', chords: 'pad_glass', lead: 'pluck_bell', pad: 'pad_warm' } },
  };

  // ── forms: sections + which roles play ──────────────────────────
  const FORMS = {
    song: [['intro', 4, ['pad', 'chords']], ['A', 8, ['drums', 'bass', 'chords']], ['B', 8, ['drums', 'bass', 'chords', 'lead', 'pad']],
           ['A2', 8, ['drums', 'bass', 'chords', 'lead']], ['outro', 4, ['pad', 'bass']]],
    short: [['A', 8, ['drums', 'bass', 'chords']], ['B', 8, ['drums', 'bass', 'chords', 'lead', 'pad']]],
    loop: [['loop', 8, ['drums', 'bass', 'chords', 'lead', 'pad']]],
    // game beds: one continuous section, no intro/outro, no crash on bar 1 → loops seamlessly
    bed: [['bed', 16, ['drums', 'bass', 'chords', 'lead', 'pad']]],
  };

  function parseGrid(s) {
    const [pat, p] = String(s).split('/');
    const prob = p === undefined ? 1 : parseFloat(p);
    return pat.split('').map(c => c === '1' ? prob : 0);
  }

  // ── parts ───────────────────────────────────────────────────────
  function genDrums(R, st, sec, opts) {
    const notes = [], bars = sec.bars, dens = opts.density;
    const grids = {}; for (const k in st.drums) grids[k] = parseGrid(st.drums[k]);
    for (let b = 0; b < bars; b++) {
      const fill = !opts.bed && (b === bars - 1 || (bars > 4 && b % 4 === 3 && R.chance(0.35)));
      for (const voice in grids) {
        const g = grids[voice];
        for (let s = 0; s < 16; s++) {
          let p = g[s];
          if (fill && s >= 12 && (voice === 'kick' || voice === 'hat_o')) p *= 0.5;
          if (!p) continue;
          const keep = voice === 'kick' || voice === 'snare' || voice === 'clap' ? p : p * (0.55 + 0.45 * dens);
          if (!R.chance(keep)) continue;
          const accent = s % 4 === 0 ? 1 : s % 2 === 0 ? 0.8 : 0.65;
          notes.push({ t: b * BAR + s * S16, d: S16, n: GM[voice], v: clampV((voice === 'hat_c' || voice === 'shaker' || voice === 'ride' ? 0.55 : 0.9) * accent + (R() - 0.5) * 0.1) });
        }
      }
      if (st.ghost) for (let s = 0; s < 16; s++) if ((s === 7 || s === 9 || s === 15) && R.chance(0.35 * dens)) notes.push({ t: b * BAR + s * S16, d: S16, n: GM.snare, v: 0.22 + R() * 0.1 });
      if (st.rolls && R.chance(0.5)) { const at = R.pick([2, 6, 10, 14]); for (let k = 0; k < 6; k++) notes.push({ t: b * BAR + at * S16 + Math.round(k * S16 * 2 / 6), d: S16 / 3, n: GM.hat_c, v: 0.35 + k * 0.06 }); }
      if (fill && (st.drums.snare || st.drums.clap)) {
        const sn = st.drums.snare ? GM.snare : GM.clap;
        for (let s = 12; s < 16; s++) if (R.chance(0.7)) notes.push({ t: b * BAR + s * S16, d: S16, n: R.chance(0.3) ? GM.tom : sn, v: 0.5 + (s - 12) * 0.12 });
      }
      if (b === 0 && !opts.bed && sec.name !== 'intro' && (st.drums.kick)) notes.push({ t: 0, d: BEAT, n: GM.crash, v: 0.7 });
    }
    return notes;
  }

  function genBass(R, st, sec, harm, opts) {
    const notes = [], { key, scale, chords } = harm, kind = st.bass;
    for (let b = 0; b < sec.bars; b++) {
      const deg = chords[(sec.bar + b) % chords.length];
      const root = deg2midi(key, scale, deg, 1) + (deg2midi(key, scale, deg, 1) < 33 ? 12 : 0);
      const fifth = deg2midi(key, scale, deg + 4, 1) + (deg2midi(key, scale, deg, 1) < 33 ? 12 : 0);
      const T = b * BAR;
      if (kind === 'drone') { if (b % 2 === 0) notes.push({ t: T, d: BAR * 2 - S16, n: root, v: 0.7 }); }
      else if (kind === 'drone808') { notes.push({ t: T, d: BEAT * 3, n: root, v: 0.9 }); if (R.chance(0.5)) notes.push({ t: T + BEAT * 3 + S16 * 2, d: S16 * 2, n: R.chance(0.5) ? root + 12 : fifth, v: 0.8 }); }
      else if (kind === 'offbeat8') { for (let k = 0; k < 4; k++) notes.push({ t: T + k * BEAT + S16 * 2, d: S16 * 2, n: k === 3 && R.chance(0.3) ? fifth : root, v: 0.85 }); }
      else if (kind === 'pulse8') { for (let k = 0; k < 8; k++) notes.push({ t: T + k * S16 * 2, d: S16 * 2 - 6, n: k % 4 === 3 && R.chance(0.4) ? root + 12 : root, v: k % 2 ? 0.65 : 0.85 }); }
      else if (kind === 'rolling') { for (let k = 0; k < 16; k++) if (R.chance(k % 4 === 0 ? 1 : 0.45 * opts.density + 0.15)) notes.push({ t: T + k * S16, d: S16, n: R.chance(0.25) ? fifth : root, v: 0.8 }); }
      else if (kind === 'walking') {
        const next = deg2midi(key, scale, chords[(sec.bar + b + 1) % chords.length], 1);
        const pcs = chordPCs(key, scale, deg, true);
        const line = [root, nearestPC(root + 4, pcs, root + 1, root + 9), nearestPC(root + 7, pcs, root + 3, root + 12)];
        const approach = next + (R.chance(0.5) ? -1 : 1);
        line.push(inScale(approach, key, scale) || R.chance(0.5) ? approach : next - 2);
        line.forEach((n, k) => notes.push({ t: T + k * BEAT, d: BEAT - 8, n, v: k === 0 ? 0.85 : 0.68 }));
      } else { // syncop
        const cells = [[0, 1], [3, 0.6], [6, 0.7], [10, 0.8], [12, 0.5], [14, 0.4]];
        for (const [s, p] of cells) if (s === 0 || R.chance(p * (0.5 + 0.5 * opts.density))) notes.push({ t: T + s * S16, d: S16 * 2, n: s === 6 && R.chance(0.4) ? fifth : s === 14 && R.chance(0.4) ? root + 12 : root, v: s === 0 ? 0.9 : 0.72 });
      }
    }
    return notes;
  }

  function voiceChord(pcs, prev, lo, hi) {
    // pick one note per pitch class near the previous voicing's centre
    const centre = prev && prev.length ? prev.reduce((a, b) => a + b, 0) / prev.length : (lo + hi) / 2;
    const out = pcs.map(pc => nearestPC(centre, [pc], lo, hi)).sort((a, b) => a - b);
    // spread collisions
    for (let i = 1; i < out.length; i++) if (out[i] - out[i - 1] < 2 && out[i] + 12 <= hi) out[i] += 12;
    return out.sort((a, b) => a - b);
  }

  function genChords(R, st, sec, harm, opts, kindOverride) {
    const notes = [], { key, scale, chords } = harm, kind = kindOverride || st.chords;
    const seventh = !(st.prog === 'drone') && R.chance(0.6);
    let prev = harm.prevVoicing || null;
    for (let b = 0; b < sec.bars; b++) {
      const deg = chords[(sec.bar + b) % chords.length], T = b * BAR;
      const v = voiceChord(chordPCs(key, scale, deg, seventh), prev, 52, 74); prev = v;
      const push = (t, d, vel) => v.forEach(n => notes.push({ t: T + t, d, n, v: vel }));
      if (kind === 'pad' || kind === 'swell') push(0, BAR - 4, kind === 'swell' ? 0.5 : 0.62);
      else if (kind === 'stabs') { for (let k = 0; k < 4; k++) if (k !== 3 || R.chance(0.6)) push(k * BEAT + S16 * 2, S16 + 6, 0.7); }
      else if (kind === 'comp') { push(0, S16 * 3, 0.68); push(BEAT + S16 * 2, S16 * 2, 0.55); if (R.chance(0.6)) push(BEAT * 2 + S16 * 2, S16 * 2, 0.5); push(BEAT * 3, S16 * 3, 0.6); }
      else if (kind === 'arp') {
        const seq = [...v, ...v.slice(1, -1).reverse()];
        for (let k = 0; k < 16; k++) notes.push({ t: T + k * S16, d: S16, n: seq[k % seq.length] + (k >= 8 && R.chance(0.2) ? 12 : 0), v: k % 4 === 0 ? 0.75 : 0.55 });
      }
    }
    harm.prevVoicing = prev;
    return notes;
  }

  function genLead(R, st, sec, harm, opts) {
    const notes = [], { key, scale, chords } = harm, kind = st.lead;
    const lo = 62, hi = 84;
    // motif: rhythm cells (16ths per beat) + scale-step contour
    const CELLS = kind === 'sparse'
      ? [[1, 0, 0, 0], [0, 0, 0, 0], [1, 0, 0, 0], [0, 0, 1, 0]]
      : [[1, 0, 0, 0], [1, 0, 1, 0], [1, 1, 1, 0], [0, 0, 1, 0], [1, 0, 0, 1], [0, 1, 1, 0], [1, 0, 1, 1]];
    const motif = [];
    let step = 0;
    for (let beat = 0; beat < 8; beat++) {
      const cell = R.chance(0.15 + 0.25 * (1 - opts.density)) ? [0, 0, 0, 0] : R.pick(CELLS);
      cell.forEach((on, k) => { if (on) { step += R.weighted([[0, 2], [1, 3], [-1, 3], [2, 1.2], [-2, 1.2], [4, 0.4], [-3, 0.4]]); motif.push({ s: beat * 4 + k, step }); } });
    }
    const base = deg2midi(key, scale, 0, 5) - 12 * (deg2midi(key, scale, 0, 5) > 76 ? 1 : 0);
    let lastN = base;
    for (let b = 0; b < sec.bars; b += 2) {
      const phraseVar = (b / 2) % 4;           // A A' A B
      const deg = chords[(sec.bar + b) % chords.length];
      const shift = phraseVar === 1 ? (deg - chords[0]) : phraseVar === 3 ? R.pick([2, -1, 4]) : 0;
      const ev = motif.filter(m => m.s < 32);
      ev.forEach((m, i) => {
        if (b * 16 + m.s >= sec.bars * 16) return;
        const bar = b + Math.floor(m.s / 16), cdeg = chords[(sec.bar + bar) % chords.length];
        let n = deg2midi(key, scale, m.step + shift, 5);
        while (n > hi) n -= 12; while (n < lo) n += 12;
        const strong = m.s % 4 === 0;
        if (strong) n = nearestPC(n, chordPCs(key, scale, cdeg, false), lo, hi);
        if (Math.abs(n - lastN) > 9) n += n > lastN ? -12 : 12;
        n = Math.min(hi, Math.max(lo, n));
        const nextS = i + 1 < ev.length ? ev[i + 1].s : 32;
        const isEnd = phraseVar === 3 && i === ev.length - 1;
        const dur = Math.max(S16, Math.min((nextS - m.s) * S16, kind === 'sparse' ? BAR : BEAT * 2));
        notes.push({ t: b * BAR + m.s * S16, d: isEnd ? BAR : dur - 4, n: isEnd ? nearestPC(n, chordPCs(key, scale, 0, false), lo, hi) : n, v: clampV((strong ? 0.78 : 0.62) + (R() - 0.5) * 0.12) });
        lastN = n;
      });
    }
    return notes;
  }

  function genPad(R, st, sec, harm, opts) {
    const notes = [], { key, scale, chords } = harm, kind = st.pad;
    if (kind === 'none') return notes;
    for (let b = 0; b < sec.bars; b += 2) {
      const deg = chords[(sec.bar + b) % chords.length];
      const r = deg2midi(key, scale, deg, 3), f = deg2midi(key, scale, deg + 4, 3);
      const len = Math.min(2, sec.bars - b) * BAR - 8;
      if (kind === 'drone') { notes.push({ t: b * BAR, d: len, n: r - 12, v: 0.55 }, { t: b * BAR, d: len, n: f - 12, v: 0.45 }); }
      else { notes.push({ t: b * BAR, d: len, n: r, v: 0.45 }, { t: b * BAR, d: len, n: f, v: 0.4 }, { t: b * BAR, d: len, n: deg2midi(key, scale, deg + 2, 4), v: 0.35 }); }
    }
    return notes;
  }

  // nothing rings past its own pattern (clips butt up against each other)
  function clampLen(ns, bars) { const end = bars * BAR; return ns.filter(x => x.t < end).map(x => (x.t + x.d > end ? Object.assign({}, x, { d: end - x.t }) : x)); }
  function clampV(v) { return Math.max(0.05, Math.min(1, v)); }
  // sort, merge duplicates (same tick + pitch: keep the louder) and trim
  // same-pitch overlaps — MIDI (and every synth's note-off) can't hold two
  // copies of one key at once.
  function sortNotes(ns) {
    ns.sort((a, b) => a.t - b.t || a.n - b.n || b.v - a.v);
    const out = [], last = new Map();
    for (const x of ns) {
      const prev = last.get(x.n);
      if (prev && prev.t === x.t) continue;
      if (prev && prev.t + prev.d > x.t) prev.d = Math.max(1, x.t - prev.t);
      const c = { t: Math.round(x.t), d: Math.max(1, Math.round(x.d)), n: x.n, v: Math.round(x.v * 1000) / 1000 };
      out.push(c); last.set(x.n, c);
    }
    return out;
  }

  // ── song ────────────────────────────────────────────────────────
  function song(o = {}) {
    const seed = o.seed ?? Math.floor(Math.random() * 1e9);
    const R = rng(seed);
    const styleId = STYLES[o.style] ? o.style : R.pick(Object.keys(STYLES));
    const st = STYLES[styleId];
    const mode = SCALES[o.mode] ? o.mode : R.pick(st.modes);
    const scale = SCALES[mode];
    const key = Number.isInteger(o.key) ? ((o.key % 12) + 12) % 12 : R.int(0, 11);
    const bpm = o.bpm || R.int(st.bpm[0], st.bpm[1]);
    const formId = FORMS[o.form] ? o.form : (styleId === 'ambient' ? 'bed' : 'song');
    const density = Math.max(0, Math.min(1, o.density ?? 0.6));
    const fam = st.prog === 'drone' ? 'drone' : st.prog === 'modal' ? 'modal' : (MINORISH[mode] ? 'minor' : 'major');
    const prog = o.progression || R.pick(PROGS[fam]);
    const harm = { key, scale, chords: prog, prevVoicing: null };
    const sections = [];
    let bar = 0;
    for (const [name, bars, roles] of FORMS[formId]) { sections.push({ name, bar, bars, roles }); bar += bars; }
    const roles = ['drums', 'bass', 'chords', 'lead', 'pad'];
    const parts = {};
    for (const role of roles) parts[role] = { role, patterns: {}, clips: [], preset: role === 'drums' ? 'kit' : st.presets[role] };
    const opts = { density, bed: formId === 'bed' };
    // lead motif is shared across sections (A/A2 sound related), re-seeded per role
    for (const sec of sections) {
      for (const role of roles) {
        if (!sec.roles.includes(role)) continue;
        const RR = rng(seed * 31 + hash(role + (sec.name.replace(/\d+$/, ''))));
        let notes;
        if (role === 'drums') notes = genDrums(RR, st, sec, opts);
        else if (role === 'bass') notes = genBass(RR, st, sec, harm, opts);
        else if (role === 'chords') notes = genChords(RR, st, sec, harm, opts, sec.name === 'intro' ? 'pad' : null);
        else if (role === 'lead') notes = genLead(RR, st, sec, harm, opts);
        else notes = genPad(RR, Object.assign({}, st, { pad: st.pad === 'none' ? 'swell' : st.pad }), sec, harm, opts);
        if (!notes.length) continue;
        const pid = role + '_' + sec.name;
        parts[role].patterns[pid] = { name: role + ' ' + sec.name, lenBars: sec.bars, notes: sortNotes(clampLen(notes, sec.bars)) };
        parts[role].clips.push({ bar: sec.bar, pid });
      }
    }
    return {
      seed, style: styleId, styleName: st.name, key, keyName: NOTE_NAMES[key], mode, bpm, swing: st.swing, form: formId, density,
      progression: prog, progressionText: prog.map(d => romanFor(d, mode)).join(' – '),
      sections: sections.map(({ name, bar, bars }) => ({ name, bar, bars })), bars: bar, parts,
    };
  }

  function part(role, s, o = {}) {
    const seed = o.seed ?? Math.floor(Math.random() * 1e9);
    const fresh = song({ seed: s.seed, style: s.style, key: s.key, mode: s.mode, bpm: s.bpm, form: s.form, density: o.density ?? s.density, progression: s.progression });
    // regenerate only `role` with a new seed by re-running with that seed for the role
    const R0 = seed;
    const st = STYLES[s.style], harm = { key: s.key, scale: SCALES[s.mode], chords: s.progression, prevVoicing: null };
    const p = { role, patterns: {}, clips: [], preset: fresh.parts[role].preset };
    for (const sec of fresh.sections) {
      const fsec = FORMS[s.form].find(f => f[0] === sec.name);
      if (!fsec || !fsec[2].includes(role)) continue;
      const RR = rng(R0 * 31 + hash(role + sec.name));
      const opts = { density: o.density ?? s.density, bed: s.form === 'bed' };
      const sec2 = Object.assign({}, sec, { roles: fsec[2] });
      let notes = role === 'drums' ? genDrums(RR, st, sec2, opts) : role === 'bass' ? genBass(RR, st, sec2, harm, opts)
        : role === 'chords' ? genChords(RR, st, sec2, harm, opts, sec.name === 'intro' ? 'pad' : null)
        : role === 'lead' ? genLead(RR, st, sec2, harm, opts) : genPad(RR, Object.assign({}, st, { pad: st.pad === 'none' ? 'swell' : st.pad }), sec2, harm, opts);
      if (!notes.length) continue;
      const pid = role + '_' + sec.name;
      p.patterns[pid] = { name: role + ' ' + sec.name, lenBars: sec.bars, notes: sortNotes(clampLen(notes, sec.bars)) };
      p.clips.push({ bar: sec.bar, pid });
    }
    return p;
  }

  function romanFor(deg, mode) {
    const R = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII'];
    const sc = SCALES[mode];
    const third = (sc[(deg + 2) % 7] - sc[deg % 7] + 12) % 12;
    const r = R[deg % 7];
    return third === 3 ? r.toLowerCase() : r;
  }

  // ── mood from a catalog brief ───────────────────────────────────
  // ties go to the first entry: ambient beds are what most game cues need
  const MOODS = [
    { words: ['drone', 'ambient', 'hum', 'substation', 'cathedral', 'hospital', 'waiting', 'liminal', 'dust', 'wind', 'tide', 'marina', 'bluff', 'field', 'cicada', 'stove', 'interior', 'long sleep'], style: 'ambient', form: 'bed' },
    { words: ['club', 'thump', 'dance', 'rave', 'warehouse party'], style: 'four_floor', form: 'loop' },
    { words: ['chillwave', 'vhs', 'neon', 'synth', 'arcade', 'render'], style: 'synthwave', form: 'loop' },
    { words: ['diner', 'jukebox', 'saturday', 'bar', 'roadhouse', 'band', 'porch', 'iced tea', 'garage'], style: 'shuffle', form: 'loop' },
    { words: ['noir', 'night shift', 'office', 'closing', 'detective', 'smoke', 'standoff', 'five am', '3:02'], style: 'noir', form: 'loop' },
    { words: ['notebook', 'tuesday', 'grind', 'study', 'kitchen', 'morning', 'apartment', 'rain'], style: 'lofi', form: 'loop' },
    { words: ['chase', 'tense', 'drive', 'service road', 'storm', 'highway'], style: 'motorik', form: 'loop' },
    { words: ['demon', 'weighing', 'judgement', 'tower', 'sinkhole'], style: 'trap', form: 'loop' },
  ];
  function moodFromText(title, desc, id) {
    const s = ((title || '') + ' ' + (desc || '') + ' ' + (id || '')).toLowerCase();
    let best = null, bestScore = 0;
    for (const m of MOODS) { const sc = m.words.reduce((n, w) => n + (s.includes(w) ? 1 : 0), 0); if (sc > bestScore) { best = m; bestScore = sc; } }
    const m = best || { style: 'ambient', form: 'bed' };
    const dark = /(night|dark|storm|noir|demon|death|hospital|weigh|grave|cemetery|blood|siren|static|empty|alone|leaving)/.test(s);
    const bright = /(morning|saturday|sunday|iced tea|porch|bread|family|bell|garden|sun)/.test(s);
    const st = STYLES[m.style];
    let mode = dark ? (st.modes.find(x => MINORISH[x]) || st.modes[0]) : bright ? (st.modes.find(x => !MINORISH[x]) || st.modes[0]) : st.modes[0];
    return { style: m.style, form: m.form, mode, seed: hash(id || s), density: dark ? 0.45 : bright ? 0.7 : 0.55, matched: bestScore };
  }

  const API = { PPQ, BAR, S16, GM, SCALES, STYLES, FORMS, PROGS, NOTE_NAMES, rng, hash, deg2midi, chordPCs, song, part, moodFromText, romanFor };
  if (typeof module !== 'undefined' && module.exports) module.exports = API;
  root.SeqGen = API;
})(typeof window !== 'undefined' ? window : globalThis);
