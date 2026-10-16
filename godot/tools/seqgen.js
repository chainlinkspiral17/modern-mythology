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
 *     part.preset is a FORGE preset id: the style's own pick or one of its FORGE_POOLS alternates, chosen by
 *     hash(seed, role) — the notes never see that choice, so a seed keeps its notes whatever the pools hold.
 *   SeqGen.presetFor(style, role, seed)        that pick on its own
 *   SeqGen.part(role, songResult, { seed })    re-roll one part in place
 *   SeqGen.moodFromText(title, desc, id)       catalog brief → song options
 *   SeqGen.moodFromBrief(track, brief, text)  + the MusicDirector's per-track brief (temp_briefs.json)
 *                                             + optional creative direction typed in the AUDIO DIRECTOR
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

  // progressions as scale degrees (0 = tonic), one chord per harmonic-rhythm step. Families by mode; a song picks one
  // for its A section and a contrasting one for B (and C) — see harmonyPlan()
  const PROGS = {
    minor: [[0, 5, 2, 6], [0, 3, 4, 0], [0, 6, 5, 6], [0, 0, 5, 4], [0, 5, 3, 4], [0, 3, 0, 6], [0, 2, 5, 6], [0, 0, 3, 3],
      [0, 3, 6, 2], [0, 4, 5, 3], [0, 6, 3, 4], [5, 6, 0, 0], [0, 5, 0, 4], [3, 4, 0, 5], [0, 2, 3, 4], [5, 3, 0, 4], [0, 6, 5, 4]],
    major: [[0, 5, 3, 4], [0, 4, 5, 3], [1, 4, 0, 0], [0, 3, 0, 4], [0, 3, 5, 4], [0, 2, 3, 4], [3, 4, 0, 0], [0, 6, 3, 0],
      [0, 3, 1, 4], [5, 3, 0, 4], [0, 2, 5, 3], [3, 0, 4, 5], [0, 4, 3, 3], [1, 2, 3, 4], [0, 5, 1, 4], [3, 5, 4, 0]],
    modal: [[0, 6, 0, 6], [0, 1, 0, 1], [0, 3, 0, 3], [0, 0, 6, 6], [0, 6, 5, 6], [0, 3, 6, 0], [0, 0, 1, 6], [0, 4, 3, 0]],
    drone: [[0, 0, 0, 0], [0, 0, 5, 5], [0, 0, 3, 3], [0, 5, 0, 5], [0, 0, 6, 6], [0, 3, 0, 5]],
    // genre families (a style names one in `prog`; any mode) — the cadences each genre leans on
    folk: [[0, 3, 0, 4], [0, 4, 5, 3], [0, 3, 5, 4], [5, 3, 0, 4], [0, 0, 3, 0], [0, 3, 4, 0], [3, 0, 4, 0], [0, 5, 3, 4], [0, 4, 3, 0]],
    hymn: [[0, 3, 4, 0], [0, 3, 0, 4], [0, 5, 3, 4], [0, 4, 5, 3], [0, 1, 4, 0], [3, 0, 4, 0], [0, 5, 1, 4], [0, 3, 1, 4], [0, 2, 3, 4]],
    jazz: [[1, 4, 0, 0], [1, 4, 0, 5], [0, 5, 1, 4], [2, 5, 1, 4], [1, 4, 2, 5], [0, 3, 1, 4], [3, 2, 1, 4], [0, 1, 2, 4]],
    jazz_minor: [[1, 4, 0, 0], [0, 5, 1, 4], [0, 3, 1, 4], [0, 0, 1, 4], [5, 1, 4, 0], [0, 3, 4, 0], [3, 4, 0, 0]],   // <family>_minor: used in minor modes
    blues: [[0, 0, 3, 0], [3, 3, 0, 0], [4, 3, 0, 4], [0, 3, 0, 4], [0, 3, 4, 3], [0, 3, 0, 0], [3, 0, 4, 0]],
    horror: [[0, 5, 0, 5], [0, 1, 0, 1], [0, 0, 5, 6], [0, 6, 5, 6], [0, 5, 6, 0], [0, 0, 1, 0], [0, 3, 5, 4], [5, 5, 0, 0]],
    surf: [[0, 3, 4, 3], [0, 0, 3, 4], [0, 5, 6, 0], [0, 6, 5, 6], [0, 3, 0, 4], [0, 5, 3, 4], [0, 6, 5, 4]],
  };

  // ── styles ──────────────────────────────────────────────────────
  // drum grids: 16 steps per bar, values = probability (0..1). `grooves`: the style's beat vocabulary — a song picks one
  // for A, another for B, a thinned one for breaks. bass / chords / lead / pad: the figure vocabularies picked per song
  // (and per section). `drums` stays the first groove (older callers read it).
  const G = (kick, back, hat, extra) => Object.assign({ kick }, back, hat, extra || {});
  const STYLES = {
    four_floor: { name: 'four on the floor', bpm: [118, 126], swing: 0.0, prog: 'minor', modes: ['minor', 'dorian'], hr: [1, 1, 2],
      grooves: [
        G('1000100010001000', { clap: '0000100000001000' }, { hat_c: '0010001000100010', shaker: '1111111111111111/0.35' }),
        G('1000100010001000', { clap: '0000100000001000' }, { hat_c: '1111111111111111/0.55', hat_o: '0010001000100010' }),
        G('1000100010001010/0.9', { clap: '0000100000001001/0.9' }, { hat_c: '0010001000100010', rim: '0001000100010001/0.5' }),
        G('1000100010001000', { snare: '0000100000001000', clap: '0000000000001000/0.5' }, { hat_o: '0010001000100010', shaker: '1010101010101010/0.4' }),
        G('1000100010001000', { clap: '0000100000001000' }, { ride: '1010101010101010/0.6', hat_c: '0010001000100010' }),
      ],
      bass: ['offbeat8', 'octave16', 'pump8', 'kicklock', 'tresillo'], chords: ['stabs', 'offbeat', 'pulse8', 'push', 'pad'], lead: ['sparse', 'motif', 'hook'], pad: ['swell', 'shimmer'],
      presets: { bass: 'bass_sub', chords: 'keys_organ', lead: 'pluck_bell', pad: 'pad_glass' } },
    boom_bap: { name: 'boom bap', bpm: [84, 94], swing: 0.55, prog: 'minor', modes: ['minor', 'dorian'], hr: [1, 1, 0.5], ghost: true,
      grooves: [
        G('1000000010100000', { snare: '0000100000001000' }, { hat_c: '1010101010101010', rim: '0000000100000010/0.4' }),
        G('1000000110100000', { snare: '0000100000001000' }, { hat_c: '1010101010101010', hat_o: '0000000000000010/0.5' }),
        G('1001000000100100', { snare: '0000100000001000' }, { hat_c: '1010101010101010/0.85' }),
        G('1000001000100000', { snare: '0000100000001001/0.9' }, { hat_c: '1011101010111010/0.75' }),
        G('1010000000100010', { snare: '0000100000001000' }, { ride: '1010101010101010/0.7', rim: '0000000100000000/0.5' }),
        G('1000000100000100', { snare: '0000100000001000', clap: '0000100000000000/0.4' }, { hat_c: '1010101010101010', shaker: '0010001000100010/0.4' }),
      ],
      bass: ['syncop', 'kicklock', 'rootfifth', 'tresillo', 'walking'], chords: ['comp', 'charleston', 'strum', 'push'], lead: ['motif', 'answer', 'sparse'], pad: ['swell', 'moving'],
      presets: { bass: 'bass_sub', chords: 'keys_ep', lead: 'pluck_marimba', pad: 'pad_warm' } },
    lofi: { name: 'lo-fi', bpm: [70, 86], swing: 0.45, prog: 'major', modes: ['major', 'dorian'], hr: [1, 1, 0.5, 2], ghost: true,
      grooves: [
        G('1000000010010000', { snare: '0000100000001000' }, { hat_c: '1010101010101010/0.8', shaker: '0010001000100010/0.5' }),
        G('1000001000100000', { snare: '0000100000001000' }, { hat_c: '1010101010101010/0.75' }),
        G('1000000100100100/0.9', { snare: '0000100000001000' }, { hat_c: '0010101000101010/0.8', rim: '0000000000000100/0.5' }),
        G('1001000000000100', { snare: '0000100000001000' }, { shaker: '1111111111111111/0.4', hat_c: '1000100010001000/0.6' }),
        G('1000000010000000', { rim: '0000100000001000' }, { hat_c: '1010101010101010/0.7' }),
      ],
      bass: ['syncop', 'rootfifth', 'root_half', 'walking', 'arp'], chords: ['pad', 'strum', 'charleston', 'arp_broken'], lead: ['motif', 'answer', 'sparse'], pad: ['swell', 'moving', 'sus'],
      presets: { bass: 'bass_sub', chords: 'keys_ep', lead: 'pluck_bell', pad: 'pad_warm' } },
    trap: { name: 'trap', bpm: [130, 145], swing: 0.0, prog: 'minor', modes: ['minor', 'phrygian', 'harmonic'], hr: [2, 1, 2], rolls: true,
      grooves: [
        G('1000000100100000', { clap: '0000000010000000' }, { hat_c: '1111111111111111/0.9' }),
        G('1000001000000100', { clap: '0000000010000000' }, { hat_c: '1010101010101010', hat_o: '0000000000000010/0.5' }),
        G('1000000000100010', { clap: '0000000010000000', snare: '0000000010000001/0.4' }, { hat_c: '1111111111111111/0.75' }),
        G('1010000000010000', { clap: '0000000010000000' }, { hat_c: '1011101110111011/0.8' }),
      ],
      bass: ['drone808', 'kicklock', 'tresillo'], chords: ['pad', 'arp_broken', 'swell'], lead: ['motif', 'hook', 'sparse'], pad: ['swell', 'drone'],
      presets: { bass: 'bass_sub', chords: 'pad_glass', lead: 'lead_square', pad: 'choir_vox' } },
    dnb: { name: 'drum & bass', bpm: [168, 176], swing: 0.0, prog: 'minor', modes: ['minor', 'dorian'], hr: [2, 1],
      grooves: [
        G('1000000000100000', { snare: '0000100000001000' }, { hat_c: '1010101010101010/0.7', ride: '0010001000100010/0.3' }),
        G('1000000000000100', { snare: '0000100000001000' }, { hat_c: '1010101010101010/0.75' }),
        G('1000000001100000', { snare: '0000100100001000' }, { hat_c: '1111111111111111/0.5' }),
        G('1010000000110000', { snare: '0000100101001001/0.85' }, { hat_c: '1010101010101010/0.7', ride: '1000100010001000/0.4' }),
      ],
      bass: ['rolling', 'root_whole', 'syncop'], chords: ['pad', 'swell', 'stabs'], lead: ['sparse', 'motif'], pad: ['swell', 'shimmer'],
      presets: { bass: 'bass_reese', chords: 'pad_warm', lead: 'lead_saw', pad: 'pad_glass' } },
    shuffle: { name: 'gulf-coast shuffle', bpm: [92, 112], swing: 0.62, prog: 'major', modes: ['mixolydian', 'major'], hr: [1, 0.5, 1],
      grooves: [
        G('1000000010000000', { snare: '0000100000001000' }, { ride: '1010101010101010', hat_c: '0000100000001000/0.6' }),
        G('1000001010000000', { snare: '0000100000001000' }, { ride: '1011101110111011/0.8' }),
        G('1000000010100000', { snare: '0010100000101000/0.7' }, { hat_c: '1010101010101010' }),
        G('1000000000000000', { snare: '0000000010000000' }, { ride: '1010101010101010', rim: '0000100000001000/0.6' }),
      ],
      bass: ['walking', 'rootfifth', 'pump8', 'arp'], chords: ['comp', 'charleston', 'offbeat', 'strum'], lead: ['motif', 'answer', 'hook'], pad: ['swell', 'moving'],
      presets: { bass: 'bass_sub', chords: 'keys_organ', lead: 'keys_ep', pad: 'strings_ensemble' } },
    motorik: { name: 'motorik', bpm: [112, 124], swing: 0.0, prog: 'modal', modes: ['dorian', 'mixolydian'], hr: [2, 1, 2],
      grooves: [
        G('1000100010001000', { snare: '0000100000001000' }, { hat_c: '1010101010101010' }),
        G('1000100010101000', { snare: '0000100000001000' }, { hat_c: '1111111111111111/0.6' }),
        G('1010100010001000', { snare: '0000100000001000' }, { hat_c: '1010101010101010', shaker: '0101010101010101/0.4' }),
        G('1000100010001000', { snare: '0000100000001010/0.8' }, { ride: '1010101010101010/0.7' }),
      ],
      bass: ['pump8', 'pedal', 'octave16'], chords: ['arp_up', 'arp_ud', 'pulse8'], lead: ['sparse', 'motif', 'hook'], pad: ['swell', 'drone'],
      presets: { bass: 'bass_acid', chords: 'arp_chip', lead: 'lead_saw', pad: 'pad_glass' } },
    synthwave: { name: 'synthwave', bpm: [96, 108], swing: 0.0, prog: 'minor', modes: ['minor', 'dorian'], hr: [1, 2, 1],
      grooves: [
        G('1000100010001000', { snare: '0000100000001000', clap: '0000100000001000/0.5' }, { hat_c: '0010001000100010' }),
        G('1000000010100000', { snare: '0000100000001000' }, { hat_c: '1010101010101010' }),
        G('1000100010001000', { snare: '0000100000001000' }, { hat_c: '1111111111111111/0.5', hat_o: '0010001000100010/0.6' }),
        G('1000001010000000', { snare: '0000100000001000' }, { hat_c: '1010101010101010', tom: '0000000000000111/0.3' }),
      ],
      bass: ['pump8', 'octave16', 'offbeat8', 'arp'], chords: ['pad', 'arp_up', 'pulse8', 'stabs'], lead: ['motif', 'hook', 'sparse'], pad: ['swell', 'shimmer'],
      presets: { bass: 'bass_acid', chords: 'pad_warm', lead: 'lead_saw', pad: 'strings_ensemble' } },
    noir: { name: 'slow noir', bpm: [64, 80], swing: 0.58, prog: 'minor', modes: ['minor', 'harmonic', 'phrygian'], hr: [1, 2, 2],
      grooves: [
        G('1000000000000000/0.8', { rim: '0000100000001000/0.7' }, { ride: '1010101010101010/0.75' }),
        G('1000000010000000/0.8', { rim: '0000100000001000/0.6' }, { ride: '1011101110111011/0.6' }),
        G('0000000000000000', { rim: '0000000000001000/0.7' }, { ride: '1010101010101010/0.6', shaker: '0010001000100010/0.3' }),
        G('1000000000100000/0.7', { snare: '0000100000001000/0.35' }, { ride: '1010101010101010/0.7' }),
      ],
      bass: ['walking', 'root_half', 'root_whole', 'pedal'], chords: ['pad', 'strum', 'charleston', 'arp_broken'], lead: ['motif', 'answer', 'sparse'], pad: ['swell', 'drone', 'sus', 'moving'],
      presets: { bass: 'bass_sub', chords: 'keys_ep', lead: 'keys_ep', pad: 'drone_dark' } },
    ambient: { name: 'ambient bed', bpm: [60, 76], swing: 0.0, prog: 'drone', modes: ['lydian', 'dorian', 'minor', 'major'], hr: [2, 2, 1], bed: true,
      grooves: [
        G('0000000000000000', {}, { shaker: '0010000000100000/0.25', rim: '0000000000000100/0.15' }),
        G('0000000000000000', {}, { rim: '0000001000000000/0.2', ride: '1000000010000000/0.15' }),
        G('1000000000000000/0.25', {}, { shaker: '0000100000001000/0.2' }),
        G('0000000000000000', {}, {}),
      ],
      bass: ['drone', 'root_whole', 'pedal'], chords: ['swell', 'pad', 'arp_broken'], lead: ['sparse', 'motif'], pad: ['drone', 'shimmer', 'sus'],
      presets: { bass: 'drone_dark', chords: 'pad_glass', lead: 'pluck_bell', pad: 'pad_warm' } },
  };
  // The score bible's genres. Extra style fields: `fills` (the fill pool; ['none'] = no fills), `nocrash` (no crash on a
  // lift), `bed` (a bed is the default form), `trip8` (offbeat eighths land on the triplet: swung eighths — the engine's
  // `swing` only moves off-sixteenths), `lilt` (triplet-flavoured figures: 12/8 inside the 4/4 bar), `link` {role: role}
  // (the same instrument as that role: solo piano's two hands). A 12-character grid is a bar of triplet eighths; a grid
  // may carry a velocity after its probability ('1000/0.5/0.4'). Extra drum voices: hat_p (pedal hat), tamb, cowbell,
  // conga, conga_lo, clave, tom_lo, tom_hi.
  Object.assign(STYLES, {
    folk: { name: 'folk / americana', bpm: [84, 112], swing: 0.2, prog: 'folk', modes: ['major', 'mixolydian', 'major', 'dorian'], hr: [1, 2, 1, 0.5], nocrash: true,
      fills: ['flam', 'drop', 'snare16'],
      grooves: [
        G('1000000010000000/0.9', { snare: '0000100000001000/0.8/0.7' }, { shaker: '1010101010101010/0.6' }),                    // brushes two-step
        G('1000000010000000', { snare: '0000100000001000/1/0.8', rim: '1011101110111011/0.55/0.45' }, {}),                       // train beat
        G('1000000010100000/0.9', { clap: '0000100000001000/0.9/0.75' }, { tamb: '0000100000001000/0.7' }),                      // porch stomp-clap
        G('1000000000100000/0.8', { snare: '0000000010000000/0.8/0.7' }, { tamb: '1010101010101010/0.5' }),                      // half-time
      ],
      bass: ['two_beat', 'two_beat', 'rootfifth', 'root_half', 'stepwise'], chords: ['fingerpick', 'fingerpick', 'boomchick', 'strum'], lead: ['whistle', 'motif', 'answer'], pad: ['swell', 'moving', 'sus'],
      presets: { bass: 'bass_upright', chords: 'pluck_nylon', lead: 'winds_harmonica', pad: 'strings_silver' } },
    chamber: { name: 'chamber strings', bpm: [56, 76], swing: 0.0, prog: 'minor', modes: ['minor', 'harmonic', 'dorian', 'major'], hr: [1, 2, 1, 0.5], fills: ['none'], nocrash: true,
      grooves: [
        G('0000000000000000', {}, {}),
        G('1000000000000000/0.25/0.6', {}, {}),                                                                                   // a timpani stroke now and then
        G('0000000000000000', {}, { tom_lo: '0000000000001111/0.15/0.45' }),                                                     // a soft timpani roll into the bar
      ],
      bass: ['stepwise', 'root_half', 'pedal', 'arp', 'stepwise'], chords: ['pad', 'tremolo', 'pulse8', 'chorale', 'arp_broken'], lead: ['answer', 'whistle', 'motif', 'sparse'], pad: ['swell', 'moving', 'sus'],
      presets: { bass: 'bass_fretless', chords: 'strings_ensemble', lead: 'strings_noir', pad: 'strings_silver' } },
    piano: { name: 'solo piano', bpm: [58, 84], swing: 0.0, prog: 'minor', modes: ['minor', 'major', 'dorian', 'lydian'], hr: [1, 2, 1, 0.5], fills: ['none'], nocrash: true,
      link: { bass: 'chords', lead: 'chords' },
      grooves: [G('0000000000000000', {}, {})],
      bass: ['root_whole', 'lh_octave', 'stepwise', 'root_half'], chords: ['alberti', 'block', 'arp_broken', 'block', 'alberti'], lead: ['answer', 'sparse', 'motif', 'whistle'], pad: ['swell', 'sus'],
      presets: { bass: 'keys_felt', chords: 'keys_felt', lead: 'keys_felt', pad: 'pad_dusk' } },
    hymn: { name: 'hymn / chorale', bpm: [60, 80], swing: 0.0, prog: 'hymn', modes: ['major', 'harmonic', 'major', 'dorian'], hr: [1, 0.5, 1], fills: ['none'], nocrash: true,
      grooves: [G('0000000000000000', {}, {})],
      bass: ['chorale_bass', 'chorale_bass', 'root_half', 'stepwise'], chords: ['chorale', 'chorale', 'pad'], lead: ['hymn', 'hymn', 'whistle'], pad: ['open', 'swell', 'sus'],
      presets: { bass: 'bass_sub', chords: 'keys_organ', lead: 'choir_angel', pad: 'pad_organ_swell' } },
    dark_drone: { name: 'dark drone', bpm: [50, 66], swing: 0.0, prog: 'drone', modes: ['phrygian', 'minor', 'harmonic'], hr: [2, 4, 1], fills: ['none'], nocrash: true, bed: true,
      grooves: [
        G('0000000000000000', {}, {}),
        G('1000000000000000/0.2/0.6', {}, {}),                                                                                    // a far-off thud
        G('0000000000000000', {}, { ride: '1000000000000000/0.15/0.4' }),                                                        // a bell-ish cymbal in the dark
      ],
      bass: ['drone', 'drone', 'root_whole', 'pedal'], chords: ['swell', 'pad', 'tremolo'], lead: ['sparse', 'whistle'], pad: ['cluster', 'drone', 'cluster', 'sus'],
      presets: { bass: 'bass_sub', chords: 'pad_bowed_metal', lead: 'lead_theremin', pad: 'drone_dark' } },
    synth_horror: { name: 'synth horror', bpm: [100, 126], swing: 0.0, prog: 'horror', modes: ['minor', 'phrygian', 'harmonic'], hr: [1, 2, 2, 1],
      fills: ['tom_run', 'drop', 'snare16', 'kick_push'],
      grooves: [
        G('1000100010001000', { snare: '0000100000001000' }, { hat_c: '1010101010101010/0.7' }),
        G('1000000010000000', { snare: '0000100000001000' }, { hat_c: '1111111111111111/0.5' }),
        G('0000000000000000', {}, { hat_c: '1010101010101010/0.65' }),                                                           // only the ticking hat: dread
        G('1000000000000000', { tom_lo: '0000000000001010/0.5' }, { hat_c: '0010001000100010' }),
        G('1001001000100000', { snare: '0000100000001000' }, { hat_c: '1010101010101010' }),
      ],
      bass: ['pedal_pulse', 'pedal_pulse', 'pump8', 'octave16', 'pedal'], chords: ['pad', 'arp_up', 'ostinato', 'swell', 'pulse8'], lead: ['sparse', 'whistle', 'motif'], pad: ['cluster', 'drone', 'swell'],
      presets: { bass: 'bass_ladder', chords: 'pad_glass', lead: 'lead_square', pad: 'pad_sub_drone' } },
    jazz: { name: 'jazz trio', bpm: [88, 132], swing: 0.4, prog: 'jazz', modes: ['major', 'harmonic', 'major', 'dorian'], hr: [1, 0.5, 1, 2], trip8: true, nocrash: true,
      fills: ['flam', 'snare16', 'drop'],
      grooves: [
        G('100000100000/0.3/0.6', { snare: '000000000001/0.35/0.4' }, { ride: '100101100101/1.3', hat_p: '000100000100/1.3' }),      // spang-a-lang ride, hat on 2 & 4
        G('100000000000/0.35/0.6', { snare: '101101101101/0.8/0.35' }, { hat_p: '000100000100/1.3', ride: '100000100000/0.4/0.7' }),  // brushes
        G('1000000000000000/0.35/0.6', { snare: '0000100000001000/0.5/0.5' }, { ride: '1000100010001000/0.8', hat_p: '0000100000001000' }),  // ballad
        G('100000100000/0.5/0.7', { rim: '000100000100/0.6' }, { ride: '100101100101/0.9' }),                                // two-feel
      ],
      bass: ['stand_up', 'stand_up', 'walking', 'two_beat'], chords: ['shell', 'comp', 'charleston', 'four', 'shell'], lead: ['blue', 'lilt', 'answer', 'motif'], pad: ['swell', 'moving', 'sus'],
      presets: { bass: 'bass_upright', chords: 'keys_felt', lead: 'winds_sax', pad: 'strings_noir' } },
    dub: { name: 'dub', bpm: [66, 80], swing: 0.15, prog: 'modal', modes: ['minor', 'dorian'], hr: [2, 1, 2], fills: ['drop', 'flam', 'stutter', 'tom_run'],
      grooves: [
        G('0000000010000000', { rim: '0000000010000000' }, { hat_c: '1010101010101010/0.8', hat_o: '0000000000000010/0.4' }),  // one drop
        G('1000100010001000', { rim: '0000000010000000' }, { hat_c: '0010001000100010' }),                                      // steppers
        G('1000000010000000', { snare: '0000000010000000/0.9' }, { hat_c: '1011101110111011/0.7' }),                            // rockers
        G('0000000010000000', { rim: '0000000010000000', snare: '0000000000000001/0.3/0.4' }, { hat_c: '1111111111111111/0.5' }),
      ],
      bass: ['dub', 'dub', 'syncop', 'tresillo'], chords: ['skank', 'skank', 'bubble', 'swell'], lead: ['sparse', 'answer', 'whistle'], pad: ['swell', 'drone', 'shimmer'],
      presets: { bass: 'bass_sub', chords: 'keys_clav', lead: 'winds_harmonica', pad: 'pad_tape_wobble' } },
    post_rock: { name: 'post-rock', bpm: [96, 126], swing: 0.0, prog: 'major', modes: ['major', 'lydian', 'minor', 'dorian'], hr: [2, 1, 2], fills: ['tom_run', 'snare16', 'flam', 'drop'],
      grooves: [
        G('1000000010000000/0.8', { tom_lo: '0010001000100010/0.6' }, { ride: '1010101010101010/0.5' }),                      // floor-tom pulse
        G('1000000010100000', { snare: '0000100000001000' }, { ride: '1010101010101010/0.8' }),
        G('1000000000100000', { snare: '0000000010000000' }, { hat_c: '1010101010101010/0.7' }),                                 // half-time
        G('0000000000000000', {}, { ride: '1000100010001000/0.4/0.6' }),                                                         // the quiet part
        G('1010101010101010/0.75', { snare: '0000100000001000' }, { ride: '1010101010101010' }),                                 // the climax
      ],
      bass: ['root_whole', 'pump8', 'root_half', 'pedal'], chords: ['tremolo', 'dotted', 'arp_ud', 'swell', 'tremolo'], lead: ['sparse', 'whistle', 'motif'], pad: ['rise', 'swell', 'shimmer'],
      presets: { bass: 'bass_fender', chords: 'pluck_neon', lead: 'bell_glock', pad: 'strings_silver' } },
    lullaby: { name: 'lullaby / music box', bpm: [60, 76], swing: 0.0, prog: 'hymn', modes: ['major', 'major', 'minor', 'mixolydian'], hr: [1, 2, 1], trip8: true, lilt: true,
      fills: ['none'], nocrash: true,
      grooves: [
        G('000000000000', {}, {}),
        G('000000000000', {}, { shaker: '100000100000/0.3/0.6' }),                                                              // rocking on the dotted quarters
        G('100000000000/0.15/0.5', {}, { clave: '100100100100/0.25/0.45' }),                                                    // a clock in the nursery
      ],
      bass: ['root_whole', 'two_beat', 'root_half', 'stepwise'], chords: ['alberti', 'alberti', 'block', 'arp_broken'], lead: ['lilt', 'lilt', 'whistle', 'sparse'], pad: ['swell', 'sus', 'shimmer'],
      presets: { bass: 'bass_upright', chords: 'pluck_harp', lead: 'bell_music_box', pad: 'pad_dusk' } },
    industrial: { name: 'industrial', bpm: [96, 124], swing: 0.0, prog: 'modal', modes: ['phrygian', 'minor', 'harmonic'], hr: [2, 1, 2], fills: ['stutter', 'snare16', 'kick_push', 'tom_run'],
      grooves: [
        G('1000001010000000', { snare: '0000100000001000', clap: '0000100000001000/0.5' }, { hat_c: '1111111111111111/0.6', cowbell: '0010000000100000/0.5' }),
        G('1000100010001000', { snare: '0000100000001000' }, { clave: '0001000100010001/0.5', hat_c: '1010101010101010' }),     // machine march
        G('1010001000100010/0.9', { snare: '0000100000001001/0.8' }, { hat_c: '1011101110111011/0.7' }),
        G('1000000000000000', { tom_lo: '0000001000000100/0.6', snare: '0000000010000000' }, { shaker: '1111111111111111/0.5', cowbell: '1000000000000000/0.6' }),  // stomp
        G('1001001001001000', { clap: '0000100000001000' }, { hat_o: '0010001000100010/0.6' }),                                 // 3-3-3-3-4
      ],
      bass: ['machine', 'pedal_pulse', 'octave16', 'kicklock', 'machine'], chords: ['chug', 'stabs', 'pad', 'chug', 'pulse8'], lead: ['sparse', 'hook', 'motif'], pad: ['cluster', 'drone', 'swell'],
      presets: { bass: 'bass_ladder', chords: 'pad_gate', lead: 'lead_fuzz', pad: 'pad_bowed_metal' } },
    surf: { name: 'surf', bpm: [128, 168], swing: 0.0, prog: 'surf', modes: ['minor', 'harmonic', 'major', 'mixolydian'], hr: [1, 1, 2, 0.5], fills: ['tom_run', 'snare16', 'flam', 'tom_run'],
      grooves: [
        G('1000000010000000', { snare: '0000100000001000' }, { tom: '1010101010101010/0.5' }),                                   // tom-tom surf beat
        G('1000000010100000', { snare: '0000100000001000' }, { hat_c: '1010101010101010' }),
        G('1000000010010000', { snare: '0000100000001000' }, { ride: '1010101010101010', tamb: '0000100000001000/0.6' }),          // ride drive, the kick pushing
        G('1000000010000000', { snare: '0000100000001000/0.8' }, { tom_lo: '1011101110111011/0.5/0.6' }),                       // floor-tom rumble
      ],
      bass: ['two_beat', 'pump8', 'walking', 'rootfifth'], chords: ['tremolo', 'offbeat', 'strum', 'stabs'], lead: ['trem', 'hook', 'motif', 'trem'], pad: ['swell', 'sus'],
      presets: { bass: 'bass_fender', chords: 'pluck_dobro', lead: 'pluck_neon', pad: 'keys_combo_organ' } },
    bayou: { name: 'bayou / swamp', bpm: [92, 124], swing: 0.3, prog: 'blues', modes: ['mixolydian', 'major', 'dorian'], hr: [1, 1, 0.5, 2], trip8: true,
      fills: ['flam', 'snare16', 'drop'],
      grooves: [
        G('100000100000', { snare: '000100000100' }, { hat_c: '101101101101/0.9', shaker: '111111111111/0.4' }),               // triplet shuffle + washboard
        G('100100100100/0.8', { snare: '000100000100' }, { tamb: '111111111111/0.55' }),                                       // zydeco two-step
        G('1000000010100000', { snare: '0000100000001000' }, { hat_c: '1010101010101010' }),                                    // swamp groove (swung)
        G('100000000100/0.8', { snare: '000000100000' }, { ride: '101101101101/0.7' }),                                       // half-time swamp
      ],
      bass: ['swamp', 'swamp', 'walking', 'two_beat', 'rootfifth'], chords: ['offbeat', 'four', 'comp', 'strum'], lead: ['blue', 'hook', 'answer', 'blue'], pad: ['swell', 'moving'],
      presets: { bass: 'bass_upright', chords: 'keys_combo_organ', lead: 'winds_harmonica', pad: 'pad_organ_swell' } },
    minimal: { name: 'minimalist pulse', bpm: [100, 132], swing: 0.0, prog: 'modal', modes: ['dorian', 'major', 'lydian', 'minor'], hr: [2, 2, 1, 4], fills: ['none', 'drop'], nocrash: true,
      grooves: [
        G('000000000000', {}, { clave: '111011010110/1.25/0.9' }),                                                              // clapping-music cell on claves
        G('1000000010000000/0.5/0.7', {}, { shaker: '1111111111111111/0.5' }),
        G('0000000000000000', {}, { clave: '1010101010101010/1.1/0.8' }),
        G('0000000000000000', {}, {}),
        G('100000000000/0.4/0.7', { clap: '111011010110/1/0.55' }, {}),
      ],
      bass: ['root_whole', 'pedal', 'pump8'], chords: ['ostinato', 'ostinato', 'arp_up', 'pulse8', 'arp_ud'], lead: ['sparse', 'whistle', 'motif'], pad: ['swell', 'sus', 'shimmer'],
      presets: { bass: 'bass_fretless', chords: 'pluck_marimba', lead: 'winds_flute', pad: 'strings_ensemble' } },
    chiptune: { name: 'chiptune', bpm: [120, 160], swing: 0.0, prog: 'minor', modes: ['minor', 'major', 'dorian'], hr: [1, 1, 2, 0.5], fills: ['snare16', 'stutter', 'tom_run', 'kick_push'],
      grooves: [
        G('1000000010000000', { snare: '0000100000001000' }, { hat_c: '1010101010101010' }),
        G('1000001000100000', { snare: '0000100000001000' }, { hat_c: '1111111111111111/0.6' }),
        G('1010000010100000', { snare: '0000100000001010/0.8' }, { hat_c: '0010001000100010' }),
        G('1000100010001000', { snare: '0000100000001000' }, { hat_o: '0010001000100010/0.7' }),
      ],
      bass: ['octave16', 'pump8', 'arp', 'rolling'], chords: ['chip_arp', 'chip_arp', 'pulse8', 'stabs', 'offbeat'], lead: ['chip', 'chip', 'hook', 'motif'], pad: ['swell', 'shimmer'],
      presets: { bass: 'bass_pluck', chords: 'arp_chip', lead: 'lead_square', pad: 'keys_combo_organ' } },
    trip_hop: { name: 'trip-hop', bpm: [70, 90], swing: 0.35, prog: 'minor', modes: ['minor', 'harmonic', 'dorian', 'phrygian'], hr: [1, 2, 2], ghost: true, fills: ['drop', 'flam', 'stutter'],
      grooves: [
        G('1000000100100000', { snare: '0000100000001000' }, { hat_c: '1010101010101010/0.8' }),
        G('1000000000100100', { snare: '0000100000001000' }, { hat_c: '0010001000100010', shaker: '1111111111111111/0.3' }),
        G('1000001000000000', { snare: '0000000010000000' }, { ride: '1010101010101010/0.6' }),                                  // half-time
        G('1001000000100000', { snare: '0000100000001001/0.8' }, { hat_c: '1011101010111010/0.7', rim: '0000001000000000/0.4' }),
        G('1000000010010000', { snare: '0000100000001000', clap: '0000000000001000/0.4' }, { hat_o: '0010000000100000/0.5', hat_c: '1000100010001000' }),
      ],
      bass: ['dub', 'syncop', 'root_whole', 'drone808'], chords: ['dotted', 'pad', 'arp_broken', 'swell', 'block'], lead: ['sparse', 'answer', 'whistle', 'motif'], pad: ['swell', 'drone', 'moving'],
      presets: { bass: 'bass_sub', chords: 'keys_tape_ep', lead: 'lead_theremin', pad: 'strings_noir' } },
  });
  // ids the score bible names before their style is built: { id: [nearest built style, name] } clones that style (marked
  // `placeholder`; the composer-variety test skips them) until its own grooves / figures / presets land
  const PLACEHOLDER = {};
  for (const [id, [from, name]] of Object.entries(PLACEHOLDER)) if (!STYLES[id]) STYLES[id] = Object.assign({}, STYLES[from], { name, placeholder: from });
  for (const st of Object.values(STYLES)) st.drums = st.grooves[0];

  // FORGE alternates per style and role, next to each style's own `presets` pick. Role rules: bass = mono
  // patches (ambient's drone bass may be a pad), chords + pad = polyphonic, lead = anything melodic.
  const FORGE_POOLS = {
    four_floor: { bass: ['bass_pluck', 'bass_fm', 'bass_808'], chords: ['keys_combo_organ', 'pluck_neon', 'winds_brass', 'keys_mk1'],
      lead: ['pluck_steel_pan', 'lead_siren', 'bell_glock', 'pluck_neon'], pad: ['pad_gate', 'pad_shimmer', 'pad_neon_rain', 'strings_silver'] },
    boom_bap: { bass: ['bass_upright', 'bass_ladder', 'bass_fender', 'bass_808'], chords: ['keys_mk1', 'keys_wurli', 'keys_felt', 'keys_tape_ep', 'keys_clav'],
      lead: ['keys_vibes', 'winds_sax', 'winds_flute', 'pluck_kalimba', 'pluck_nylon'], pad: ['pad_tape_wobble', 'pad_velvet', 'pad_dusk'] },
    lofi: { bass: ['bass_upright', 'bass_fender', 'bass_fretless'], chords: ['keys_tape_ep', 'keys_felt', 'keys_wurli', 'keys_mk1', 'pluck_nylon'],
      lead: ['pluck_kalimba', 'keys_vibes', 'bell_music_box', 'keys_celesta', 'winds_flute', 'pluck_nylon'], pad: ['pad_tape_wobble', 'pad_dusk', 'pad_velvet'] },
    trap: { bass: ['bass_808'], chords: ['pad_frost', 'choir_crypt', 'bell_music_box', 'keys_celesta'],
      lead: ['bell_glock', 'pluck_neon', 'lead_siren', 'keys_celesta', 'bell_music_box'], pad: ['choir_crypt', 'strings_tremolo', 'pad_seance', 'pad_sub_drone'] },
    dnb: { bass: ['bass_ladder', 'bass_fm'], chords: ['pad_velvet', 'pad_shimmer', 'keys_mk1', 'pad_neon_rain'],
      lead: ['lead_fm', 'lead_siren', 'pluck_neon', 'lead_brass'], pad: ['pad_neon_rain', 'pad_seance', 'pad_shimmer', 'pad_frost'] },
    shuffle: { bass: ['bass_upright', 'bass_fender'], chords: ['keys_combo_organ', 'keys_wurli', 'winds_brass', 'keys_clav', 'keys_mk1'],
      lead: ['winds_harmonica', 'winds_sax', 'winds_harmon', 'winds_clarinet', 'pluck_steel_pan', 'keys_vibes'], pad: ['strings_silver', 'winds_horns', 'pad_organ_swell', 'pad_dusk'] },
    motorik: { bass: ['bass_pluck', 'bass_ladder'], chords: ['pluck_neon', 'keys_combo_organ', 'keys_harpsichord'],
      lead: ['lead_brass', 'lead_ring', 'lead_fm'], pad: ['pad_neon_rain', 'pad_gate', 'pad_hollow'] },
    synthwave: { bass: ['bass_pluck', 'bass_ladder', 'bass_fm'], chords: ['pad_gate', 'pad_velvet', 'pad_neon_rain', 'keys_mk1'],
      lead: ['lead_brass', 'lead_fuzz', 'lead_square', 'lead_fm'], pad: ['strings_silver', 'pad_neon_rain', 'pad_shimmer', 'pad_velvet'] },
    noir: { bass: ['bass_upright', 'bass_fretless'], chords: ['keys_felt', 'keys_vibes', 'keys_mk1', 'winds_brass', 'strings_noir'],
      lead: ['winds_harmon', 'winds_clarinet', 'winds_sax', 'lead_theremin', 'keys_vibes', 'pluck_nylon'],
      pad: ['strings_noir', 'choir_crypt', 'strings_tremolo', 'pad_tape_wobble', 'pad_sub_drone', 'pad_bowed_metal', 'winds_horns'] },
    ambient: { bass: ['pad_sub_drone', 'drone_cathedral', 'drone_horizon'], chords: ['pad_shimmer', 'pad_bowed_glass', 'pad_cathedral_air', 'pad_frost', 'pad_organ_swell', 'choir_angel'],
      lead: ['bell_tubular', 'bell_bowl', 'pluck_kalimba', 'keys_celesta', 'winds_flute', 'pluck_harp', 'lead_theremin'],
      pad: ['pad_seance', 'pad_bowed_metal', 'drone_horizon', 'pad_dusk', 'pad_hollow', 'choir_angel', 'pad_cathedral_air'] },
    folk: { bass: ['bass_fender', 'bass_fretless'], chords: ['pluck_harp', 'pluck_dobro', 'keys_felt', 'pluck_kalimba'],
      lead: ['pluck_dobro', 'winds_flute', 'lead_whistle', 'winds_clarinet', 'pluck_nylon'], pad: ['pad_organ_swell', 'pad_dusk', 'winds_horns', 'strings_ensemble'] },
    chamber: { bass: ['bass_upright', 'winds_clarinet', 'bass_sub'], chords: ['strings_noir', 'strings_silver', 'strings_tremolo', 'keys_felt', 'winds_horns'],
      lead: ['winds_clarinet', 'winds_flute', 'strings_silver', 'keys_felt', 'winds_harmon'], pad: ['strings_noir', 'strings_tremolo', 'choir_crypt', 'pad_velvet', 'winds_horns'] },
    // solo piano: bass + lead are linked to the chords' piano (STYLES.piano.link), so only chords + pad have pools
    piano: { chords: ['keys_tape_ep', 'keys_mk1', 'keys_ep', 'keys_wurli'], pad: ['pad_velvet', 'strings_silver', 'pad_bowed_glass', 'pad_warm'] },
    hymn: { bass: ['bass_fretless', 'bass_upright'], chords: ['pad_organ_swell', 'keys_felt', 'winds_horns', 'strings_ensemble', 'choir_vox'],
      lead: ['keys_felt', 'winds_flute', 'winds_horns', 'winds_clarinet', 'strings_noir'], pad: ['choir_vox', 'pad_cathedral_air', 'choir_angel', 'strings_silver'] },
    dark_drone: { bass: ['bass_reese', 'bass_fretless', 'bass_fm'], chords: ['pad_sub_drone', 'choir_crypt', 'strings_tremolo', 'pad_seance', 'pad_hollow'],
      lead: ['bell_bowl', 'bell_tubular', 'lead_ring', 'strings_noir'], pad: ['pad_sub_drone', 'drone_cathedral', 'drone_horizon', 'pad_seance', 'choir_crypt'] },
    synth_horror: { bass: ['bass_pluck', 'bass_fm', 'bass_acid', 'bass_sub'], chords: ['pad_gate', 'pad_frost', 'keys_felt', 'pad_seance', 'keys_celesta'],
      lead: ['lead_theremin', 'lead_saw', 'lead_fm', 'bell_tubular', 'lead_ring'], pad: ['pad_seance', 'choir_crypt', 'pad_frost', 'strings_tremolo', 'pad_bowed_metal'] },
    jazz: { bass: ['bass_fretless', 'bass_fender'], chords: ['keys_mk1', 'keys_vibes', 'keys_ep', 'keys_wurli'],
      lead: ['winds_harmon', 'keys_vibes', 'winds_clarinet', 'winds_flute', 'keys_felt'], pad: ['winds_horns', 'pad_velvet', 'pad_dusk', 'strings_silver'] },
    dub: { bass: ['bass_808', 'bass_fretless', 'bass_fender'], chords: ['keys_organ', 'pluck_nylon', 'keys_combo_organ', 'keys_mk1'],
      lead: ['winds_flute', 'winds_harmon', 'lead_whistle', 'pluck_steel_pan', 'winds_brass'], pad: ['pad_dusk', 'pad_hollow', 'pad_organ_swell', 'pad_seance'] },
    post_rock: { bass: ['bass_pluck', 'bass_fretless', 'bass_sub'], chords: ['pluck_nylon', 'keys_mk1', 'pluck_harp', 'pad_shimmer', 'strings_tremolo'],
      lead: ['lead_ring', 'lead_fuzz', 'strings_noir', 'keys_celesta', 'bell_tubular'], pad: ['pad_shimmer', 'pad_cathedral_air', 'pad_frost', 'strings_ensemble', 'pad_bowed_glass'] },
    lullaby: { bass: ['bass_fretless', 'bass_sub'], chords: ['keys_celesta', 'keys_felt', 'bell_music_box', 'pluck_kalimba', 'keys_toy_piano'],
      lead: ['keys_celesta', 'bell_glock', 'winds_flute', 'keys_toy_piano', 'pluck_kalimba'], pad: ['choir_angel', 'pad_velvet', 'strings_silver', 'pad_warm', 'pad_bowed_glass'] },
    industrial: { bass: ['bass_reese', 'bass_fm', 'bass_808', 'bass_acid'], chords: ['pad_bowed_metal', 'keys_clav', 'pad_fluorescent', 'pad_frost'],
      lead: ['lead_ring', 'lead_saw', 'lead_siren', 'lead_fm'], pad: ['pad_sub_drone', 'choir_crypt', 'pad_seance', 'pad_fluorescent'] },
    surf: { bass: ['bass_pluck', 'bass_upright'], chords: ['keys_combo_organ', 'pluck_neon', 'pluck_nylon', 'keys_clav'],
      lead: ['pluck_dobro', 'lead_square', 'pluck_steel_pan', 'winds_brass', 'lead_ring'], pad: ['pad_organ_swell', 'winds_horns', 'pad_neon_rain', 'strings_silver'] },
    bayou: { bass: ['bass_fender', 'bass_fretless'], chords: ['keys_wurli', 'pluck_dobro', 'keys_clav', 'pluck_nylon', 'winds_brass'],
      lead: ['pluck_dobro', 'winds_sax', 'winds_clarinet', 'winds_harmon', 'lead_whistle'], pad: ['winds_horns', 'pad_dusk', 'strings_silver', 'drone_bayou'] },
    minimal: { bass: ['bass_sub', 'bass_upright', 'bass_pluck'], chords: ['keys_vibes', 'keys_celesta', 'keys_felt', 'pluck_kalimba', 'keys_harpsichord', 'keys_organ'],
      lead: ['winds_clarinet', 'keys_vibes', 'bell_glock', 'choir_vox', 'pluck_marimba'], pad: ['choir_vox', 'pad_organ_swell', 'strings_silver', 'pad_glass'] },
    chiptune: { bass: ['bass_sub', 'bass_fm', 'bass_acid'], chords: ['pluck_neon', 'keys_combo_organ', 'keys_toy_piano', 'bell_glock'],
      lead: ['arp_chip', 'lead_fm', 'pluck_neon', 'bell_glock', 'lead_siren'], pad: ['pad_gate', 'keys_organ', 'pad_glass', 'pad_neon_rain'] },
    trip_hop: { bass: ['bass_808', 'bass_fretless', 'bass_upright', 'bass_ladder'], chords: ['keys_felt', 'strings_noir', 'keys_wurli', 'pad_tape_wobble', 'keys_vibes'],
      lead: ['strings_noir', 'winds_harmon', 'keys_vibes', 'bell_glock', 'winds_clarinet'], pad: ['pad_tape_wobble', 'choir_crypt', 'pad_seance', 'pad_dusk', 'strings_tremolo'] },
  };
  // The arrangement parts per style: p = how likely a song has each one; counter / arp / perc / double = the idiomatic
  // figures (see genCounter, genArp, PERC_KITS, genDouble); reg = arp registers; presets + pools are merged into
  // STYLES[id].presets and FORGE_POOLS[id] below (counter and arp play mono, so any melodic FORGE preset will do).
  const ARRANGE = {
    four_floor: { p: [0.35, 0.6, 0.6, 0.3], counter: ['answer', 'ring'], arp: ['seq16', 'up', 'updown', 'pedal'], reg: ['mid', 'high'], perc: ['bongo', 'conga', 'shaker', 'cabasa'], double: ['bass_up', 'lead_low'],
      presets: ['strings_silver', 'pluck_neon', 'lead_fm'], pools: [['winds_horns', 'lead_fm', 'keys_vibes'], ['arp_chip', 'pluck_bell', 'bell_glock', 'keys_harpsichord'], ['pluck_neon', 'winds_brass']] },
    boom_bap: { p: [0.5, 0.25, 0.55, 0.2], counter: ['answer', 'horn'], arp: ['thirds', 'walk', 'alberti'], reg: ['high', 'mid'], perc: ['bongo', 'shaker', 'tamb', 'conga'], double: ['lead_low'],
      presets: ['winds_horns', 'pluck_kalimba', 'keys_vibes'], pools: [['winds_sax', 'keys_vibes', 'strings_noir'], ['keys_vibes', 'pluck_marimba', 'keys_celesta'], ['winds_flute', 'keys_ep']] },
    lofi: { p: [0.45, 0.4, 0.45, 0.2], counter: ['answer', 'horn'], arp: ['thirds', 'walk', 'updown', 'alberti'], reg: ['high', 'mid'], perc: ['shaker', 'bongo', 'cabasa', 'tamb'], double: ['lead_low', 'lead_high'],
      presets: ['winds_flute', 'pluck_kalimba', 'keys_vibes'], pools: [['keys_vibes', 'winds_clarinet', 'strings_silver'], ['keys_celesta', 'bell_music_box', 'pluck_nylon'], ['winds_flute', 'pluck_nylon']] },
    trap: { p: [0.3, 0.55, 0.2, 0.25], counter: ['ring', 'answer'], arp: ['triplet', 'pedal', 'down', 'up'], reg: ['high'], perc: ['shaker', 'woodblock'], double: ['lead_high', 'lead_low'],
      presets: ['strings_noir', 'bell_music_box', 'bell_glock'], pools: [['choir_crypt', 'lead_theremin', 'pad_frost'], ['keys_celesta', 'bell_glock', 'pluck_bell'], ['lead_square', 'keys_celesta']] },
    dnb: { p: [0.35, 0.5, 0.45, 0.3], counter: ['ring', 'answer'], arp: ['seq16', 'up', 'pedal'], reg: ['high', 'mid'], perc: ['shaker', 'bongo', 'tamb'], double: ['bass_up', 'lead_low'],
      presets: ['strings_silver', 'pluck_neon', 'lead_brass'], pools: [['lead_fm', 'pad_shimmer', 'winds_horns'], ['arp_chip', 'bell_glock', 'pluck_bell'], ['lead_saw']] },
    shuffle: { p: [0.55, 0.15, 0.5, 0.35], counter: ['horn', 'answer'], arp: ['walk', 'alberti'], reg: ['mid'], perc: ['tamb', 'conga', 'cowbell', 'shaker'], double: ['lead_low'],
      presets: ['winds_horns', 'keys_vibes', 'winds_brass'], pools: [['winds_brass', 'winds_sax', 'keys_organ'], ['pluck_nylon', 'keys_ep'], ['winds_sax', 'winds_horns']] },
    motorik: { p: [0.3, 0.75, 0.4, 0.35], counter: ['ring', 'interlock'], arp: ['seq16', 'up', 'pedal', 'updown'], reg: ['mid', 'low', 'high'], perc: ['shaker', 'tamb', 'cabasa'], double: ['bass_up', 'lead_low'],
      presets: ['lead_ring', 'arp_chip', 'lead_saw'], pools: [['strings_silver', 'lead_brass'], ['pluck_neon', 'keys_harpsichord', 'pluck_bell'], ['lead_brass']] },
    synthwave: { p: [0.45, 0.8, 0.35, 0.35], counter: ['answer', 'ring'], arp: ['up', 'updown', 'seq16', 'pedal', 'thirds'], reg: ['mid', 'high'], perc: ['tamb', 'shaker'], double: ['bass_up', 'lead_low'],
      presets: ['lead_brass', 'arp_chip', 'lead_square'], pools: [['strings_silver', 'lead_fm', 'winds_horns'], ['pluck_neon', 'pluck_bell', 'keys_harpsichord'], ['strings_silver', 'lead_saw']] },
    noir: { p: [0.6, 0.2, 0.35, 0.25], counter: ['horn', 'answer', 'horn'], arp: ['walk', 'thirds'], reg: ['mid', 'high'], perc: ['bongo', 'conga', 'shaker'], double: ['lead_low'],
      presets: ['winds_harmon', 'keys_vibes', 'winds_clarinet'], pools: [['winds_horns', 'winds_clarinet', 'strings_noir'], ['pluck_harp', 'keys_celesta'], ['strings_noir', 'winds_sax']] },
    ambient: { p: [0.3, 0.4, 0.1, 0], counter: ['second', 'ring'], arp: ['walk', 'updown', 'up'], reg: ['high', 'mid'], perc: ['shaker', 'woodblock'], double: ['lead_low'],
      presets: ['strings_silver', 'pluck_harp', 'winds_flute'], pools: [['winds_flute', 'choir_angel', 'pad_bowed_glass'], ['keys_celesta', 'pluck_kalimba', 'bell_bowl'], []] },
    folk: { p: [0.65, 0.3, 0.45, 0.25], counter: ['harmony', 'answer', 'harmony'], arp: ['alberti', 'thirds', 'up'], reg: ['mid'], perc: ['tamb', 'shaker', 'frame'], double: ['lead_low'],
      presets: ['strings_silver', 'pluck_nylon', 'winds_flute'], pools: [['winds_flute', 'winds_harmonica', 'pluck_dobro'], ['pluck_harp', 'pluck_dobro', 'pluck_kalimba'], ['winds_harmonica', 'lead_whistle']] },
    chamber: { p: [0.8, 0.35, 0.1, 0.3], counter: ['second', 'second', 'answer'], arp: ['alberti', 'updown', 'thirds'], reg: ['mid'], perc: ['frame'], double: ['lead_low'],
      presets: ['strings_noir', 'pluck_harp', 'strings_noir'], pools: [['winds_clarinet', 'winds_horns', 'strings_silver'], ['keys_harpsichord', 'keys_celesta'], ['winds_clarinet', 'strings_silver']] },
    // solo piano: the counter is an inner voice, the arp a right-hand figure, the double melody in octaves — all on the
    // chords' piano (STYLES.piano.link)
    piano: { p: [0.5, 0.25, 0, 0.15], counter: ['second', 'answer'], arp: ['updown', 'alberti', 'up'], reg: ['high'], perc: [], double: ['lead_low'], presets: [], pools: [] },
    hymn: { p: [0.75, 0.1, 0, 0.35], counter: ['second', 'second'], arp: ['updown'], reg: ['mid'], perc: [], double: ['lead_low'],
      presets: ['choir_vox', 'pluck_harp', 'winds_horns'], pools: [['winds_horns', 'strings_ensemble', 'keys_organ'], ['keys_celesta'], ['choir_vox', 'keys_organ']] },
    dark_drone: { p: [0.3, 0.2, 0.1, 0], counter: ['second', 'ring'], arp: ['walk', 'pedal'], reg: ['high', 'low'], perc: ['frame'], double: ['lead_low'],
      presets: ['strings_noir', 'bell_tubular', 'strings_noir'], pools: [['bell_bowl', 'choir_crypt', 'pad_bowed_metal'], ['bell_bowl', 'pluck_harp'], []] },
    synth_horror: { p: [0.35, 0.65, 0.2, 0.25], counter: ['ring', 'answer'], arp: ['up', 'down', 'pedal', 'triplet', 'seq16'], reg: ['high', 'mid'], perc: ['woodblock', 'shaker'], double: ['lead_low', 'bass_up'],
      presets: ['strings_noir', 'keys_celesta', 'lead_saw'], pools: [['lead_theremin', 'choir_crypt', 'pad_seance'], ['pluck_bell', 'arp_chip', 'keys_harpsichord'], ['lead_ring']] },
    jazz: { p: [0.6, 0.1, 0.2, 0.3], counter: ['guide', 'guide', 'answer'], arp: ['walk'], reg: ['mid'], perc: ['bongo', 'conga', 'shaker'], double: ['lead_low', 'lead_high'],
      presets: ['winds_clarinet', 'keys_vibes', 'keys_vibes'], pools: [['winds_horns', 'keys_vibes', 'winds_harmon'], ['pluck_harp'], ['winds_flute', 'winds_clarinet']] },
    dub: { p: [0.5, 0.2, 0.55, 0.3], counter: ['horn', 'answer'], arp: ['pedal', 'walk'], reg: ['mid'], perc: ['nyabinghi', 'shaker', 'conga'], double: ['lead_low'],
      presets: ['winds_brass', 'pluck_nylon', 'winds_brass'], pools: [['winds_horns', 'winds_flute', 'keys_organ'], ['keys_clav', 'pluck_steel_pan'], ['winds_flute']] },
    post_rock: { p: [0.55, 0.6, 0.3, 0.4], counter: ['ring', 'ring', 'second'], arp: ['updown', 'up', 'pedal', 'thirds'], reg: ['high', 'mid'], perc: ['tamb', 'shaker'], double: ['lead_low', 'bass_up'],
      presets: ['lead_ring', 'pluck_nylon', 'strings_silver'], pools: [['keys_celesta', 'strings_silver', 'bell_tubular'], ['pluck_harp', 'pluck_neon', 'keys_celesta'], ['lead_fuzz']] },
    lullaby: { p: [0.5, 0.5, 0.2, 0.3], counter: ['second', 'answer'], arp: ['triplet', 'alberti', 'updown'], reg: ['high', 'mid'], perc: ['woodblock', 'shaker'], double: ['lead_high', 'lead_low'],
      presets: ['winds_flute', 'pluck_harp', 'keys_celesta'], pools: [['keys_celesta', 'strings_silver', 'choir_angel'], ['keys_celesta', 'bell_music_box', 'keys_toy_piano'], ['bell_glock']] },
    industrial: { p: [0.3, 0.5, 0.55, 0.3], counter: ['ring', 'interlock'], arp: ['seq16', 'pedal', 'down'], reg: ['low', 'mid'], perc: ['woodblock', 'cowbell', 'shaker'], double: ['bass_up', 'lead_low'],
      presets: ['lead_ring', 'arp_chip', 'lead_fuzz'], pools: [['pad_bowed_metal', 'lead_siren'], ['pluck_bell', 'keys_clav'], ['lead_saw']] },
    surf: { p: [0.45, 0.3, 0.55, 0.35], counter: ['answer', 'horn'], arp: ['updown', 'up'], reg: ['mid'], perc: ['tamb', 'bongo'], double: ['lead_low'],
      presets: ['keys_combo_organ', 'pluck_nylon', 'pluck_neon'], pools: [['winds_brass', 'lead_ring'], ['pluck_neon', 'pluck_steel_pan'], ['winds_brass']] },
    bayou: { p: [0.55, 0.15, 0.6, 0.3], counter: ['answer', 'horn', 'harmony'], arp: ['walk'], reg: ['mid'], perc: ['washboard', 'tamb', 'cowbell'], double: ['lead_low'],
      presets: ['winds_clarinet', 'pluck_dobro', 'winds_harmonica'], pools: [['winds_harmon', 'keys_combo_organ', 'pluck_dobro'], ['pluck_nylon'], ['winds_sax']] },
    minimal: { p: [0.6, 0.75, 0.4, 0.2], counter: ['interlock', 'interlock', 'second'], arp: ['pedal', 'seq16', 'updown', 'walk'], reg: ['mid', 'high'], perc: ['woodblock', 'shaker', 'clave'], double: ['lead_high'],
      presets: ['pluck_marimba', 'keys_celesta', 'winds_clarinet'], pools: [['keys_vibes', 'keys_celesta', 'winds_clarinet'], ['pluck_marimba', 'keys_harpsichord', 'pluck_kalimba'], ['choir_vox']] },
    chiptune: { p: [0.45, 0.55, 0.15, 0.35], counter: ['answer', 'interlock'], arp: ['up', 'updown', 'seq16'], reg: ['high', 'mid'], perc: ['shaker'], double: ['lead_low', 'lead_high'],
      presets: ['lead_square', 'arp_chip', 'lead_square'], pools: [['arp_chip', 'bell_glock'], ['pluck_neon', 'bell_glock'], ['arp_chip']] },
    trip_hop: { p: [0.45, 0.35, 0.45, 0.25], counter: ['answer', 'horn', 'ring'], arp: ['walk', 'thirds', 'pedal'], reg: ['high', 'mid'], perc: ['shaker', 'bongo', 'tamb'], double: ['lead_low'],
      presets: ['strings_noir', 'keys_vibes', 'strings_noir'], pools: [['winds_harmon', 'keys_vibes', 'lead_theremin'], ['keys_celesta', 'pluck_harp', 'bell_glock'], ['winds_clarinet']] },
  };
  const ARRANGE_DEFAULT = { p: [0.35, 0.35, 0.3, 0.2], counter: ['answer'], arp: ['up', 'updown'], reg: ['mid'], perc: ['shaker', 'tamb'], double: ['lead_low'], presets: ['strings_silver', 'pluck_bell', 'strings_silver'], pools: [] };
  const COUNTER_RANGE = { ring: [72, 91], interlock: [60, 79] };      // else [55, 74]: under the lead
  // presets + pools → the style tables; the piano's new hands are the chords' piano too
  for (const [id, A] of Object.entries(ARRANGE)) {
    const st = STYLES[id]; if (!st) continue;
    ['counter', 'arp', 'double'].forEach((r, i) => {
      if (A.presets[i]) st.presets[r] = A.presets[i];
      if ((A.pools[i] || []).length) FORGE_POOLS[id] = Object.assign(FORGE_POOLS[id] || {}, { [r]: A.pools[i].slice() });
    });
  }
  STYLES.piano.link = Object.assign({}, STYLES.piano.link, { counter: 'chords', arp: 'chords', double: 'chords' });
  function presetFor(styleId, role, seed) {
    const st = STYLES[styleId]; if (!st) return null;
    if (role === 'drums' || role === 'perc') return 'kit';
    if (st.link && st.link[role]) return presetFor(styleId, st.link[role], seed);   // one instrument for several roles
    const base = st.presets[role], pool = ((FORGE_POOLS[styleId] || {})[role] || []).filter(x => x !== base);
    const all = base ? [base, ...pool] : pool;
    return all.length ? all[hash(String(seed) + ':forge:' + role) % all.length] : null;
  }

  // ── forms: sections + which roles play ──────────────────────────
  // FORMS stays the menu (song / short / loop / bed); a 'song' picks one of SONG_SHAPES per seed. A section's `base`
  // (A for A / A2) shares material — A2 is A again with variation; B, C (a bridge) and brk (a break) contrast.
  const FORMS = {
    song: [['intro', 4, ['pad', 'chords']], ['A', 8, ['drums', 'bass', 'chords']], ['B', 8, ['drums', 'bass', 'chords', 'lead', 'pad']],
           ['A2', 8, ['drums', 'bass', 'chords', 'lead']], ['outro', 4, ['pad', 'bass']]],
    short: [['A', 8, ['drums', 'bass', 'chords']], ['B', 8, ['drums', 'bass', 'chords', 'lead', 'pad']]],
    loop: [['loop', 8, ['drums', 'bass', 'chords', 'lead', 'pad']]],
    // game beds: one continuous section, no intro/outro, no crash on bar 1 → loops seamlessly
    bed: [['bed', 16, ['drums', 'bass', 'chords', 'lead', 'pad']]],
  };
  const SONG_SHAPES = [
    [['intro', 4], ['A', 8], ['B', 8], ['A2', 8], ['outro', 4]],
    [['intro', 4], ['A', 8], ['A2', 8], ['B', 8], ['brk', 4], ['B2', 8], ['outro', 4]],
    [['intro', 8], ['A', 8], ['B', 8], ['C', 8], ['B2', 8], ['outro', 4]],
    [['intro', 2], ['A', 16], ['B', 8], ['A2', 8], ['outro', 4]],
    [['intro', 4], ['A', 8], ['B', 8], ['brk', 8], ['A2', 8], ['outro', 8]],
    [['intro', 4], ['A', 8], ['C', 8], ['A2', 8], ['B', 8], ['outro', 4]],
  ];
  const baseOf = name => name.replace(/\d+$/, '');
  // which roles play in a section: the kind's options, picked per song (texture / fx / hit are added by song())
  function rolesFor(R, base, name, st, sparse) {
    const lead = R.chance(sparse ? 0.35 : 0.55);
    switch (base) {
      case 'intro': return R.pick([['pad', 'chords'], ['pad', 'lead'], ['chords'], ['pad', 'drums'], ['pad', 'chords', 'bass']]);
      case 'A': return name === 'A2' ? ['drums', 'bass', 'chords', 'lead'].concat(R.chance(0.5) ? ['pad'] : []) : ['drums', 'bass', 'chords'].concat(lead ? ['lead'] : []);
      case 'B': return ['drums', 'bass', 'chords', 'lead', 'pad'];
      case 'C': return R.pick([['chords', 'pad', 'lead', 'bass'], ['pad', 'lead'], ['drums', 'bass', 'pad', 'lead'], ['chords', 'lead', 'bass']]);
      case 'brk': return R.pick([['pad', 'lead'], ['drums', 'bass'], ['pad', 'chords'], ['bass', 'pad']]);
      case 'outro': return R.pick([['pad', 'bass'], ['pad', 'chords'], ['chords', 'lead'], ['pad', 'lead', 'chords']]);
      default: return ['drums', 'bass', 'chords', 'lead', 'pad'];
    }
  }

  function parseGrid(s) {
    const [pat, p] = String(s).split('/');
    const prob = p === undefined ? 1 : parseFloat(p);
    return pat.split('').map(c => c === '1' ? prob : 0);
  }
  const gridVel = s => { const v = String(s).split('/')[2]; return v === undefined ? 1 : parseFloat(v); };
  // the steps a grid plays, as sixteenths (a 12-step triplet grid rounds to the nearest)
  const STEPS = s => { const g = parseGrid(s); return g.map((p, i) => p ? Math.round(i * 16 / g.length) : -1).filter(i => i >= 0); };

  // ── harmony ─────────────────────────────────────────────────────
  // chord tones (scale-degree offsets) per extension
  const EXT = { triad: [0, 2, 4], seventh: [0, 2, 4, 6], sus2: [0, 1, 4], sus4: [0, 3, 4], add9: [0, 2, 4, 8], ninth: [0, 2, 4, 6, 8], power: [0, 4], sixth: [0, 2, 4, 5] };
  const EXT_W = {
    four_floor: [['seventh', 3], ['triad', 2], ['add9', 2], ['sus2', 1]], boom_bap: [['seventh', 4], ['ninth', 2], ['add9', 1]], lofi: [['seventh', 3], ['ninth', 3], ['add9', 2]],
    trap: [['triad', 3], ['sus2', 1], ['power', 1]], dnb: [['seventh', 2], ['add9', 2], ['sus2', 1]], shuffle: [['seventh', 3], ['triad', 2]],
    motorik: [['sus2', 2], ['triad', 2], ['power', 1], ['sus4', 1]], synthwave: [['triad', 2], ['add9', 2], ['seventh', 1]],
    noir: [['seventh', 3], ['ninth', 2], ['triad', 1]], ambient: [['add9', 3], ['sus2', 2], ['sus4', 1], ['triad', 1]],
    folk: [['triad', 5], ['sus2', 1], ['sus4', 1], ['add9', 1]], chamber: [['triad', 3], ['seventh', 2], ['sus4', 1], ['add9', 1]],
    piano: [['add9', 2], ['seventh', 2], ['triad', 2], ['sus2', 1]], hymn: [['triad', 6], ['sus4', 1], ['seventh', 1]],
    dark_drone: [['triad', 2], ['sus2', 1], ['sus4', 1], ['power', 1]], synth_horror: [['triad', 4], ['sus2', 1], ['power', 1]],
    jazz: [['seventh', 4], ['ninth', 3], ['sixth', 1]], dub: [['triad', 2], ['seventh', 2], ['sus2', 1]],
    post_rock: [['add9', 3], ['sus2', 2], ['triad', 2], ['power', 1]], lullaby: [['triad', 3], ['add9', 2], ['sus2', 1], ['sixth', 1]],
    industrial: [['power', 3], ['triad', 1], ['sus2', 1]], surf: [['triad', 3], ['sixth', 2], ['seventh', 1]],
    bayou: [['seventh', 4], ['triad', 1], ['sixth', 1]], minimal: [['triad', 2], ['sus2', 2], ['add9', 2]],
    chiptune: [['triad', 4], ['seventh', 1], ['sus4', 1]], trip_hop: [['seventh', 3], ['ninth', 2], ['triad', 1]],
  };
  // a section's harmony: progression, harmonic rhythm (bars per chord), extension; B / C contrast with A
  // colour hook (the AUDIO DIRECTOR's HARMONY / PROGRESSION controls, all optional): o.progFamily — a PROGS family to
  // draw from instead of the style's; o.ext — an EXT name or [[ext, weight], …] instead of the style's EXT_W. Each
  // pick still takes one draw from R, so a seed keeps its other choices; absent → exactly the style's own.
  function harmonyPlan(R, st, fam, prog0, o) {
    const xe = o && (typeof o.ext === 'string' ? (EXT[o.ext] ? [[o.ext, 1]] : null) : Array.isArray(o.ext) ? o.ext.filter(x => Array.isArray(x) && EXT[x[0]] && +x[1] > 0) : null);
    const pool = PROGS[(o && PROGS[o.progFamily]) ? o.progFamily : fam], W = xe && xe.length ? xe : EXT_W[st.id] || [['triad', 1]];
    const A = { prog: prog0 || R.pick(pool), hr: R.pick(st.hr || [1]), ext: R.weighted(W) };
    const other = avoid => { const c = pool.filter(p => p.join() !== avoid.join() && p[0] !== avoid[0]); return R.pick(c.length ? c : pool.filter(p => p.join() !== avoid.join()).concat([avoid])); };
    const B = { prog: other(A.prog), hr: R.chance(0.3) ? R.pick(st.hr || [1]) : A.hr, ext: R.chance(0.4) ? R.weighted(W) : A.ext };
    const C = { prog: other(B.prog), hr: R.pick([1, 2]), ext: R.weighted(W) };
    const brk = R.chance(0.5) ? { prog: [A.prog[0]], hr: 4, ext: 'sus2' } : A;
    return { A, B, C, brk, intro: R.chance(0.6) ? A : { prog: [A.prog[0], A.prog[A.prog.length - 1]], hr: 2, ext: A.ext }, outro: A, loop: A, bed: A };
  }
  // the chord under bar b (+ beat) of a section — { deg, ext }; a dominant-ish V gets its seventh
  function chordAt(H, b, beat = 0) {
    const pos = Math.floor((b + beat / 4) / H.hr), deg = H.prog[((pos % H.prog.length) + H.prog.length) % H.prog.length];
    return { deg, ext: deg % 7 === 4 && H.ext === 'triad' ? 'seventh' : H.ext };
  }
  // a 'sixth' adds the major sixth over the root whatever the scale (the minor-six of jazz / surf, a dim7 on a diminished triad)
  const chordNotes = (key, scale, c, oct) => c.ext === 'sixth' ? [0, 2, 4].map(x => deg2midi(key, scale, c.deg + x, oct)).concat(deg2midi(key, scale, c.deg, oct) + 9)
    : EXT[c.ext].map(x => deg2midi(key, scale, c.deg + x, oct));
  const chordPcsOf = (key, scale, c) => [...new Set(chordNotes(key, scale, c, 4).map(n => ((n % 12) + 12) % 12))];

  // ── drums ───────────────────────────────────────────────────────
  // ctx.groove: the section's grid set; variations every 4 bars, a fill (from a pool) on the phrase end
  const FILLS = ['snare16', 'tom_run', 'stutter', 'drop', 'open_hat', 'flam', 'kick_push'];
  // percussion colour a song may add on top of its grooves (GM: tamb 54, cowbell 56, congas 62 / 64, clave 75)
  const PERC = {
    tamb24: { n: 54, g: '0000100000001000/0.7' }, tamb8: { n: 54, g: '1010101010101010/0.45' }, conga: { n: 62, g: '0010010000100100/0.6', n2: 64, g2: '1000000010010000/0.5' },
    clave: { n: 75, g: '1001001000101000/0.6' }, cowbell: { n: 56, g: '1000100010001000/0.4' }, shaker16: { n: 70, g: '1111111111111111/0.3' },
  };
  const PERC_FOR = { four_floor: ['tamb8', 'cowbell', 'conga'], boom_bap: ['clave', 'tamb24', 'shaker16'], lofi: ['shaker16', 'conga', 'tamb24'], shuffle: ['tamb24', 'conga', 'cowbell'],
    synthwave: ['tamb24', 'shaker16'], motorik: ['tamb8', 'shaker16'], dnb: ['shaker16', 'tamb8'], trap: [], noir: ['conga', 'shaker16'], ambient: [],
    folk: ['tamb24', 'shaker16'], chamber: [], piano: [], hymn: [], dark_drone: [], synth_horror: ['shaker16'], jazz: [], dub: ['shaker16', 'clave', 'conga'],
    post_rock: ['tamb8', 'shaker16'], lullaby: [], industrial: ['cowbell', 'shaker16'], surf: ['tamb8', 'tamb24'], bayou: ['tamb8', 'shaker16'], minimal: ['shaker16', 'clave'],
    chiptune: [], trip_hop: ['shaker16', 'conga'] };
  const GM_OF = { kick: 36, rim: 37, snare: 38, clap: 39, hat_c: 42, tom: 45, hat_o: 46, crash: 49, ride: 51, shaker: 70,
    hat_p: 44, tamb: 54, cowbell: 56, conga: 62, conga_lo: 64, clave: 75, tom_lo: 41, tom_hi: 48 };
  const SOFT_VOICE = { hat_c: 0.55, shaker: 0.55, ride: 0.55, rim: 0.7, hat_p: 0.5, tamb: 0.5, clave: 0.6, cowbell: 0.6, conga: 0.65, conga_lo: 0.65 };
  function genDrums(R, st, sec, ctx, opts) {
    const notes = [], bars = sec.bars, dens = opts.density, groove = ctx.groove, thin = ctx.thin;
    const grids = {}, gvel = {}; for (const k in groove) { grids[k] = parseGrid(groove[k]); gvel[k] = gridVel(groove[k]); }
    if (thin) { for (const k of ['kick', 'snare', 'clap']) if (grids[k] && thin === 'perc') delete grids[k]; if (thin === 'half') { if (grids.snare) grids.snare = parseGrid('0000000010000000'); if (grids.clap) grids.clap = parseGrid('0000000010000000'); if (grids.kick) grids.kick = parseGrid('1000000000000000'); } }
    const perc = ctx.perc && PERC[ctx.perc];
    const fillKind = ctx.fill;
    for (let b = 0; b < bars; b++) {
      const phraseEnd = !opts.bed && (b === bars - 1 || (bars > 4 && b % 8 === 7) || (b % 4 === 3 && R.chance(0.25)));
      const turn = b % 4 === 3 && !phraseEnd;                 // a small variation every fourth bar
      const T = b * BAR;
      for (const voice in grids) {
        const g = grids[voice], len = g.length, stepT = BAR / len;          // 16 sixteenths, or 12 triplet eighths
        for (let s = 0; s < len; s++) {
          let p = g[s];
          const at = s * stepT, pos = at % BEAT;
          if (phraseEnd && at >= 3 * BEAT && fillKind !== 'open_hat' && (voice === 'kick' || voice === 'hat_o' || voice === 'hat_c')) p *= fillKind === 'drop' ? 0 : 0.5;
          if (turn && voice === 'kick' && (s === len - 2 || s === len - 1) && !p && R.chance(0.4)) p = 0.8;
          if (!p) continue;
          const keep = voice === 'kick' || voice === 'snare' || voice === 'clap' ? p : p * (0.55 + 0.45 * dens);
          if (!R.chance(keep)) continue;
          const accent = pos === 0 ? 1 : pos === BEAT / 2 ? 0.8 : len === 12 && pos > BEAT / 2 ? 0.72 : 0.62;
          const base = SOFT_VOICE[voice] || 0.9;
          notes.push({ t: T + Math.round(at), d: S16, n: GM_OF[voice], v: clampV(base * accent * gvel[voice] + (R() - 0.5) * 0.12) });
        }
      }
      if (perc && !thin) for (const [n, g] of [[perc.n, perc.g], [perc.n2, perc.g2]]) { if (!n) continue; const pg = parseGrid(g); for (let s = 0; s < 16; s++) if (pg[s] && R.chance(pg[s] * (0.6 + 0.4 * dens))) notes.push({ t: T + s * S16, d: S16, n, v: clampV(0.5 + (s % 4 === 0 ? 0.15 : 0) + (R() - 0.5) * 0.15) }); }
      if (st.ghost && !thin) for (let s = 0; s < 16; s++) if ((s === 7 || s === 9 || s === 15 || s === 3) && R.chance(0.3 * dens)) notes.push({ t: T + s * S16, d: S16, n: GM.snare, v: 0.18 + R() * 0.1 });
      if (st.rolls && !thin && R.chance(0.45)) { const at = R.pick([2, 6, 10, 14]), k3 = R.pick([3, 4, 6]); for (let k = 0; k < k3; k++) notes.push({ t: T + at * S16 + Math.round(k * S16 * 2 / k3), d: Math.max(4, Math.round(S16 * 2 / k3)), n: GM.hat_c, v: 0.35 + k * 0.07 }); }
      if (phraseEnd && !thin) {
        const sn = groove.snare ? GM.snare : groove.clap ? GM.clap : GM.rim;
        if (fillKind === 'snare16') for (let s = 12; s < 16; s++) notes.push({ t: T + s * S16, d: S16, n: sn, v: 0.45 + (s - 12) * 0.13 });
        else if (fillKind === 'tom_run') [[12, 48], [13, 48], [14, 45], [15, 41]].forEach(([s, n]) => notes.push({ t: T + s * S16, d: S16, n, v: 0.7 }));
        else if (fillKind === 'stutter') for (let k = 0; k < 6; k++) notes.push({ t: T + 12 * S16 + Math.round(k * S16 * 4 / 6), d: 8, n: R.chance(0.5) ? sn : GM.kick, v: 0.5 + k * 0.07 });
        else if (fillKind === 'open_hat') notes.push({ t: T + 14 * S16, d: S16 * 2, n: GM.hat_o, v: 0.75 });
        else if (fillKind === 'flam') { notes.push({ t: T + 12 * S16 - 6, d: 6, n: sn, v: 0.35 }, { t: T + 12 * S16, d: S16, n: sn, v: 0.85 }, { t: T + 14 * S16, d: S16, n: sn, v: 0.7 }); }
        else if (fillKind === 'kick_push') notes.push({ t: T + 14 * S16, d: S16, n: GM.kick, v: 0.8 }, { t: T + 15 * S16, d: S16, n: GM.kick, v: 0.7 });
      }
      if (b === 0 && ctx.crash && !opts.bed && !st.nocrash) notes.push({ t: 0, d: BEAT, n: GM.crash, v: 0.7 });
    }
    return notes;
  }

  // ── bass ────────────────────────────────────────────────────────
  // one figure per section (from the style's vocabulary); approach notes lead into the next chord
  // dub riffs: [sixteenth, scale steps above the chord root, length in sixteenths] — beat 1 mostly left empty
  const DUB_RIFFS = [[[2, 0, 3], [6, 0, 2], [8, 4, 2], [10, 2, 2], [12, 0, 4]], [[4, 0, 4], [8, 0, 2], [10, 4, 2], [12, 6, 2], [14, 4, 2]],
    [[3, 0, 3], [6, 4, 2], [8, 0, 6], [14, -1, 2]], [[2, 0, 2], [4, 2, 2], [6, 4, 4], [10, 4, 2], [12, 2, 2], [14, 0, 2]], [[0, 0, 3], [3, 0, 1], [6, 7, 2], [10, 4, 2], [12, 2, 4]]];
  // swamp boogie: per bar, four (on-beat, triplet-let) pairs in semitones over the chord root (null = rest)
  const SWAMP = [[[0, 4, 7, 9, 10, 9, 7, 4]], [[0, 12, 0, 12, 0, 12, 10, 7]], [[0, null, 10, 12, 0, null, 7, 5]], [[0, 4, 7, 9, 10, 9, 7, 4], [0, 12, 10, 7, 5, 4, 3, 2]]];
  // pedal pulse: a rhythm gate (16ths) + the semitones over the tonic per step
  const PULSES = [['1010101010101010', [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], ['1010101010101010', [0, 0, 0, 0, 12, 0, 0, 0, 0, 0, 0, 0, 12, 0, 0, 0]],
    ['1111111111111111', [0, 0, 12, 0, 0, 0, 12, 0, 0, 0, 12, 0, 0, 0, 12, 0]], ['1001001010010010', [0, 0, 0, 12, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], ['1010101010101011', [0, 0, 7, 0, 0, 0, 7, 0, 0, 0, 7, 0, 0, 0, 7, 12]]];
  const MACHINE = ['1011101110111011', '1001001010010010', '1110111011101110', '1000101010001010', '1101101101101101'];
  function genBass(R, st, sec, ctx, harm, opts) {
    const notes = [], { key, scale } = harm, H = ctx.H, kind = ctx.fig, kick = ctx.kickSteps || [0, 8];
    const low = n => { while (n > 52) n -= 12; while (n < 31) n += 12; return n; };
    const push = (t, d, n, v) => notes.push({ t, d, n, v });
    // degree `deg` in the octave of `ref` (a note of degree refDeg); the shortest way round from degree a to z (−3..3)
    const at = (deg, ref, refDeg) => deg2midi(key, scale, deg, 1) + (ref - deg2midi(key, scale, refDeg, 1));
    const toward = (a, z) => { let d = ((z - a) % 7 + 7) % 7; if (d > 3) d -= 7; return d; };
    const reg = (n, lo = 28, hi = 55) => { while (n > hi) n -= 12; while (n < lo) n += 12; return n; };
    let figure = null;                                           // a section-long pick (riff, gate, boogie)
    for (let b = 0; b < sec.bars; b++) {
      const T = b * BAR, c = chordAt(H, b), nx = chordAt(H, b + 1), c2 = chordAt(H, b, 2);
      const root = low(deg2midi(key, scale, c.deg, 1)), fifth = low(deg2midi(key, scale, c.deg + 4, 1)), third = low(deg2midi(key, scale, c.deg + 2, 1));
      const oct = root + 12 <= 60 ? root + 12 : root, root2 = low(deg2midi(key, scale, c2.deg, 1));
      const nextRoot = low(deg2midi(key, scale, nx.deg, 1));
      const approach = nx.deg !== c.deg && R.chance(0.45 + 0.3 * opts.density) ? (R.chance(0.5) ? nextRoot + (nextRoot > root ? -1 : 1) : low(deg2midi(key, scale, nx.deg - 1, 1))) : null;
      const end = approach !== null ? 14 : 16;                 // the last eighth goes to the approach note
      const v1 = 0.88, v2 = 0.7;
      switch (kind) {
        case 'drone': if (b % 2 === 0) push(T, BAR * Math.min(2, sec.bars - b) - S16, root, 0.7); break;
        case 'root_whole': push(T, BAR - S16, root, 0.8); break;
        case 'root_half': push(T, BEAT * 2 - 8, root, v1); push(T + BEAT * 2, BEAT * 2 - 8, R.chance(0.4) ? fifth : root2, v2); break;
        case 'pedal': push(T, BEAT * 2 - 8, low(deg2midi(key, scale, 0, 1)), v1); push(T + BEAT * 2, BEAT * 2 - 8, R.chance(0.5) ? root : low(deg2midi(key, scale, 0, 1)), v2); break;
        case 'drone808': push(T, BEAT * 3, root, 0.9); if (R.chance(0.55)) push(T + BEAT * 3 + S16 * 2, S16 * 2, R.chance(0.5) ? oct : fifth, 0.8); break;
        case 'offbeat8': for (let k = 0; k < 4; k++) push(T + k * BEAT + S16 * 2, S16 * 2, k === 3 && R.chance(0.3) ? fifth : root, 0.85); break;
        case 'pump8': for (let k = 0; k < 8; k++) if (k * 2 < end) push(T + k * S16 * 2, S16 * 2 - 6, k === 7 && R.chance(0.4) ? oct : (k >= 4 ? root2 : root), k % 2 ? 0.66 : 0.86); break;
        case 'octave16': for (let k = 0; k < 8; k++) if (k * 2 < end) push(T + k * S16 * 2, S16 - 4, k % 2 ? oct : root, k % 2 ? 0.7 : 0.88); break;
        case 'rolling': for (let k = 0; k < 16; k++) if (k < end && R.chance(k % 4 === 0 ? 1 : 0.45 * opts.density + 0.15)) push(T + k * S16, S16, R.chance(0.25) ? fifth : root, 0.8); break;
        case 'tresillo': [[0, 3], [3, 3], [6, 2]].forEach(([s, l]) => push(T + s * S16, l * S16 - 6, s === 6 && R.chance(0.4) ? fifth : root, s ? v2 : v1)); [[8, 3], [11, 3]].forEach(([s, l]) => { if (s < end && R.chance(0.7)) push(T + s * S16, l * S16 - 6, root2, v2); }); break;
        case 'kicklock': for (const s of kick) if (s < end) push(T + s * S16, Math.max(S16, ((kick.find(x => x > s) ?? 16) - s) * S16 - 8), s >= 8 ? root2 : root, s % 4 === 0 ? v1 : v2); break;
        case 'rootfifth': push(T, BEAT + S16 * 2, root, v1); push(T + BEAT * 2, BEAT, fifth, v2); if (R.chance(0.6)) push(T + BEAT * 3, S16 * 2, R.chance(0.5) ? oct : root2, v2); break;
        case 'arp': [root, third, fifth, oct].forEach((n, k) => { if (k * 4 < end) push(T + k * BEAT, BEAT - 10, k >= 2 && c2.deg !== c.deg ? low(deg2midi(key, scale, c2.deg + [0, 2, 4, 7][k], 1)) : n, k ? v2 : v1); }); break;
        case 'two_beat': {            // root on 1, the fifth (often the one below) on 3; a walk-up into some changes
          if (approach !== null && R.chance(0.5)) {
            push(T, BEAT - 8, root, v1);
            let w = [3, 2, 1].map(k => at(nx.deg - k, nextRoot, nx.deg)); if (w[0] < 28) w = w.map(n => n + 12);
            w.forEach((n, k) => push(T + (k + 1) * BEAT, BEAT - 8, n, v2));
            continue;
          }
          const alt = c2.deg !== c.deg ? root2 : R.chance(0.6) && fifth - 12 >= 28 ? fifth - 12 : fifth;
          push(T, BEAT * 2 - 10, root, v1); push(T + BEAT * 2, (end < 16 ? BEAT + S16 * 2 : BEAT * 2) - 10, alt, v2);
          break;
        }
        case 'stepwise': {            // beat 1 the root, beat 3 a passing step toward the next root (a lament / cello line)
          let pass;
          const dd = toward(c.deg, nx.deg);
          if (c2.deg !== c.deg) pass = root2;
          else if (Math.abs(dd) >= 2) pass = reg(at(c.deg + Math.sign(dd), root, c.deg));
          else pass = R.chance(0.5) ? third : fifth;
          push(T, BEAT * 2 - 8, root, v1); push(T + BEAT * 2, BEAT * 2 - 8, pass, v2);
          continue;
        }
        case 'chorale_bass': {        // hymn: half notes — the root, then an inversion or quarters stepping to the next root
          if (c2.deg !== c.deg) { push(T, BEAT * 2 - 6, root, v1); push(T + BEAT * 2, BEAT * 2 - 6, root2, v2); continue; }
          if (b % 4 === 3) { push(T, BAR - 8, root, v1); continue; }          // the cadence holds
          const r = R(), dd = toward(c.deg, nx.deg);
          push(T, BEAT * 2 - 6, root, v1);
          if (r < 0.45) push(T + BEAT * 2, BEAT * 2 - 6, R.chance(0.5) ? third : fifth, v2);
          else if (r < 0.8 && dd) { push(T + BEAT * 2, BEAT - 6, R.chance(0.5) ? root : third, v2); push(T + BEAT * 3, BEAT - 6, reg(at(nx.deg - Math.sign(dd), nextRoot, nx.deg)), v2); }
          else push(T + BEAT * 2, BEAT * 2 - 6, root, v2 * 0.9);
          continue;
        }
        case 'lh_octave': {           // piano left hand: root + octave (sometimes broken), the fifth / next root on 3
          push(T, BEAT * 2 - 6, root, 0.72);
          if (root + 12 <= 62) push(T + (R.chance(0.4) ? S16 * 2 : 0), BEAT * 2 - 6 - S16 * 2, root + 12, 0.56);
          push(T + BEAT * 2, BEAT * 2 - 8, c2.deg !== c.deg ? root2 : fifth, 0.62);
          continue;
        }
        case 'dub': {                 // heavy, round, melodic: the riff leaves beat 1 open; every fourth bar it turns around
          if (!figure) figure = R.pick(DUB_RIFFS);
          const turnBar = b % 4 === 3;
          for (const [s, off, l] of figure) {
            if (turnBar && s >= 12) continue;
            const ch = s >= 8 ? c2 : c, ref = s >= 8 ? root2 : root;
            push(T + s * S16, l * S16 - 6, reg(at(ch.deg + off, ref, ch.deg), 28, 52), s % 4 === 0 ? 0.88 : 0.76);
          }
          if (turnBar) { push(T + 12 * S16, S16 * 2 - 6, reg(root2 + 12, 28, 55), 0.72); push(T + 14 * S16, S16 * 2 - 6, approach ?? root2, 0.7); }
          continue;
        }
        case 'pedal_pulse': {         // synth horror: a pulse on the tonic pedal under the moving chords
          if (!figure) figure = R.pick(PULSES);
          const [gate, oct] = figure, ped = low(deg2midi(key, scale, 0, 1));
          for (let s = 0; s < 16; s++) if (gate[s] === '1') { const nx16 = gate.indexOf('1', s + 1); push(T + s * S16, Math.min(S16 * 2, ((nx16 < 0 ? 16 : nx16) - s) * S16) - 6, ped + oct[s], s % 4 === 0 ? 0.86 : 0.68); }
          continue;
        }
        case 'machine': {             // industrial: a sequencer's sixteenth gate on the root, accents jumping an octave
          if (!figure) figure = R.pick(MACHINE);
          for (let s = 0; s < 16; s++) if (figure[s] === '1') { const acc = s % 4 === 0; push(T + s * S16, S16 - 4, (s >= 8 ? root2 : root) + (acc && R.chance(0.25) ? 12 : 0), acc ? 0.9 : 0.7); }
          continue;
        }
        case 'swamp': {               // bayou: shuffled boogie — long on the beat, short on the triplet let; the blue third slid into
          if (!figure) figure = R.pick(SWAMP);
          const seq = figure[b % figure.length];
          for (let k = 0; k < 4; k++) {
            const ref = k >= 2 ? root2 : root, on = seq[2 * k], lt = seq[2 * k + 1];
            const tail = k === 3 && approach !== null;
            if (on !== null) { if (on === 4 && R.chance(0.35)) push(T + k * BEAT - 10, 10, ref + 3, 0.5); push(T + k * BEAT, lt === null && !tail ? BEAT - 8 : 60, ref + on, k ? 0.78 : 0.88); }
            if (tail) push(T + k * BEAT + 64, 26, approach, 0.66);
            else if (lt !== null) push(T + k * BEAT + 64, 26, ref + lt, 0.62);
          }
          continue;
        }
        case 'stand_up': {            // jazz walking: chord tones, scale steps, a chromatic enclosure into the next root, a ghosted skip
          const step2 = R.chance(0.5) ? third : reg(at(c.deg + 1, root, c.deg));
          let b3 = c2.deg !== c.deg ? root2 : R.chance(0.6) ? fifth : third, b4 = R.pick([nextRoot - 1, nextRoot + 1, reg(at(nx.deg + 1, nextRoot, nx.deg))]);
          if (c2.deg === c.deg && R.chance(0.25)) { b3 = reg(at(nx.deg + 1, nextRoot, nx.deg)); b4 = nextRoot - 1; }    // enclosure: above, then below
          const line = [root, step2, b3, b4];
          const skip = R.chance(0.2) ? R.int(1, 3) : -1;
          line.forEach((n, k) => {
            push(T + k * BEAT, (k === skip ? 60 : BEAT - 8), reg(n), k === 0 ? 0.86 : 0.7);
            if (k === skip) push(T + k * BEAT + 64, 24, reg(n), 0.4);
          });
          continue;
        }
        case 'walking': {
          const pcs = chordPcsOf(key, scale, c);
          const line = [root, nearestPC(root + 4, pcs, root + 1, root + 9), nearestPC(root + 7, pcs, root + 3, root + 12)];
          const ap = nextRoot + (R.chance(0.5) ? -1 : 1);
          line.push(inScale(ap, key, scale) || R.chance(0.5) ? ap : nextRoot - 2);
          line.forEach((n, k) => push(T + k * BEAT, BEAT - 8, n, k === 0 ? 0.85 : 0.68));
          continue;
        }
        default: { // syncop
          const cells = [[0, 1], [3, 0.6], [6, 0.7], [10, 0.8], [12, 0.5], [14, 0.4]];
          for (const [s, p] of cells) if (s < end && (s === 0 || R.chance(p * (0.5 + 0.5 * opts.density)))) push(T + s * S16, S16 * 2, s === 6 && R.chance(0.4) ? fifth : s >= 8 ? root2 : root, s === 0 ? 0.9 : 0.72);
        }
      }
      if (approach !== null && kind !== 'drone' && kind !== 'root_whole') push(T + 14 * S16, S16 * 2 - 6, approach, 0.66);
    }
    return notes;
  }

  // ── chords ──────────────────────────────────────────────────────
  function voiceChord(pcs, prev, lo, hi, spread) {
    // pick one note per pitch class near the previous voicing's centre
    const centre = prev && prev.length ? prev.reduce((a, b) => a + b, 0) / prev.length : (lo + hi) / 2;
    const out = pcs.map(pc => nearestPC(centre, [pc], lo, hi)).sort((a, b) => a - b);
    // spread collisions
    for (let i = 1; i < out.length; i++) if (out[i] - out[i - 1] < 2 && out[i] + 12 <= hi) out[i] += 12;
    out.sort((a, b) => a - b);
    if (spread && out.length >= 4 && out[out.length - 2] - 12 >= lo - 5) out[out.length - 2] -= 12;   // drop-2: an open voicing
    return out.sort((a, b) => a - b);
  }
  // fingerpicking: eight eighth-note slots — R thumb root, 5 thumb fifth, T top voice, M the one under it, P a pinch (R + T)
  const FINGER = [['P', 'M', '5', 'T', 'R', 'M', '5', 'T'], ['R', 'T', '5', 'M', 'R', 'T', '5', 'M'], ['P', null, '5', 'M', 'R', 'T', null, 'M'], ['R', 'M', 'T', 'R', 'M', 'T', 'R', 'T']];
  const CHUG = ['1011101110111011', '1001001010010010', '1110111011101110', '1000101010001010', '1111101011111010'];
  function genChords(R, st, sec, ctx, harm, opts) {
    const notes = [], { key, scale } = harm, H = ctx.H, kind = ctx.fig, [lo, hi] = ctx.range;
    let prev = harm.prevVoicing || null;
    const memo = {}, once = (k, f) => (k in memo ? memo[k] : (memo[k] = f()));     // a section-long pick
    for (let b = 0; b < sec.bars; b++) {
      const T = b * BAR;
      for (const half of H.hr < 1 ? [0, 2] : [0]) {
        const c = chordAt(H, b, half), span = H.hr < 1 ? BEAT * 2 : BAR, t0 = half * BEAT;
        const pcs = chordPcsOf(key, scale, c);
        const v = voiceChord(pcs, prev, lo, hi, ctx.spread); prev = v;
        const push = (t, d, vel, only) => (only || v).forEach(n => { if (t < t0 + span) notes.push({ t: T + t, d: Math.min(d, t0 + span - t), n, v: vel }); });
        const top = v.slice(-1), bottom = v.slice(0, -1);
        switch (kind) {
          case 'pad': push(t0, span - 4, 0.62); break;
          case 'swell': push(t0, span - 4, 0.48); break;
          case 'stabs': for (let k = 0; k < 4; k++) if (k * BEAT >= t0 && (k !== 3 || R.chance(0.6))) push(k * BEAT + S16 * 2, S16 + 6, 0.7); break;
          case 'offbeat': for (let k = 0; k < 4; k++) if (k * BEAT >= t0) push(k * BEAT + S16 * 2, S16 * 2 - 6, k % 2 ? 0.6 : 0.68); break;
          case 'pulse8': for (let k = 0; k < 8; k++) if (k * S16 * 2 >= t0) push(k * S16 * 2, S16 * 2 - 8, k % 2 ? 0.48 : 0.6); break;
          case 'push': push(t0, BEAT + S16 * 2, 0.66); push(t0 + BEAT * 2 + S16 * 2, BEAT, 0.56); if (!half) push(BEAT * 3 + S16 * 2, S16 * 2, 0.6); break;
          case 'charleston': push(t0, S16 * 3, 0.68); push(t0 + S16 * 6, S16 * 2, 0.56); if (span === BAR && R.chance(0.6)) push(BEAT * 3, S16 * 3, 0.55); break;
          case 'comp': push(t0, S16 * 3, 0.68); push(t0 + BEAT + S16 * 2, S16 * 2, 0.55); if (span === BAR) { if (R.chance(0.6)) push(BEAT * 2 + S16 * 2, S16 * 2, 0.5); push(BEAT * 3, S16 * 3, 0.6); } break;
          case 'strum': v.forEach((n, i) => notes.push({ t: T + t0 + i * 14, d: span - 8 - i * 14, n, v: 0.58 - i * 0.03 })); if (span === BAR && R.chance(0.5)) v.forEach((n, i) => notes.push({ t: T + BEAT * 2 + S16 * 2 + i * 10, d: BEAT, n, v: 0.42 })); break;
          case 'arp_up': case 'arp_ud': case 'arp_broken': {
            const up = [...v, top[0] + 12].filter(n => n <= hi + 12);
            const seq = kind === 'arp_up' ? up : kind === 'arp_ud' ? up.concat(up.slice(1, -1).reverse()) : [v[0], v[2] ?? v[1], v[1], top[0], v[2] ?? v[1], v[1]];
            const step = kind === 'arp_broken' ? S16 * 2 : S16, n = span / step;
            for (let k = 0; k < n; k++) notes.push({ t: T + t0 + k * step, d: step * (kind === 'arp_broken' ? 2 : 1) - 4, n: seq[k % seq.length], v: k % 4 === 0 ? 0.7 : 0.52 });
            break;
          }
          case 'fingerpick': case 'boomchick': {      // folk guitar: an alternating thumb under the chord (Travis), or boom-chick
            const fifthPc = ((deg2midi(key, scale, c.deg + 4, 4) % 12) + 12) % 12;
            const tr = nearestPC(v[0] - 8, [pcs[0]], v[0] - 15, v[0] - 1), t5 = nearestPC(tr + 7, [fifthPc], tr + 3, tr + 9);
            if (kind === 'boomchick') {
              const late = once('chick', () => R.chance(0.4));
              for (let k = 0; k < 4; k++) {
                const x = k * BEAT; if (x < t0 || x >= t0 + span) continue;
                if (k % 2 === 0) push(x, BEAT - 8, 0.62, [k === 2 ? t5 : tr]); else push(x, S16 * 2, 0.5, v.slice(-3));
              }
              if (late && t0 + span === BAR) push(BEAT * 3 + S16 * 2, S16 * 2, 0.42, v.slice(-3));
              break;
            }
            const fp = once('finger', () => R.pick(FINGER)), M = v[v.length - 2] ?? v[0];
            for (let e = t0 / (S16 * 2); e < (t0 + span) / (S16 * 2); e++) {
              const tok = fp[e], x = e * S16 * 2; if (!tok) continue;
              if (tok === 'R' || tok === '5' || tok === 'P') push(x, BEAT - 6, e === 0 ? 0.62 : 0.55, [tok === '5' ? t5 : tr]);
              if (tok === 'T' || tok === 'P') push(x, S16 * 3, tok === 'P' ? 0.52 : 0.46, top);
              if (tok === 'M') push(x, S16 * 3, 0.43, [M]);
            }
            break;
          }
          case 'chorale': {                           // hymn: block chords in half notes, the top voice moving on repeats; cadences hold
            const rh = b % 4 === 3 && span === BAR ? [0] : once('chorale', () => R.pick([[0, 2], [0, 2], [0, 1, 2], [0, 3], [0, 2, 3], [0, 1, 2, 3]]));
            const on = rh.map(x => x * BEAT).filter(x => x > t0 && x < t0 + span); on.unshift(t0);
            let vo = v;
            on.forEach((x, i) => {
              if (i) {                                // re-voice: the top voice steps to another chord tone nearby
                const tp = vo[vo.length - 1], floor = vo.length > 1 ? vo[vo.length - 2] + 2 : lo, cands = [];
                for (let n = tp - 5; n <= tp + 5; n++) if (n !== tp && n >= floor && n <= hi + 2 && pcs.includes(((n % 12) + 12) % 12)) cands.push(n);
                if (cands.length) vo = vo.slice(0, -1).concat(R.pick(cands));
              }
              const end = on[i + 1] ?? t0 + span;
              vo.forEach((n, j) => notes.push({ t: T + x, d: end - x - 6, n, v: 0.5 + (x === t0 ? 0.06 : 0) + (j === vo.length - 1 ? 0.04 : 0) }));
            });
            prev = vo.slice().sort((a, z) => a - z);
            break;
          }
          case 'tremolo': {                           // post-rock / surf / strings: the chord re-struck in 16ths (32nds on the top two), swelling
            const rate = once('trem', () => R.pick([S16, S16, S16 / 2]));
            const vs = rate < S16 ? v.slice(-2) : v;
            for (let x = t0; x < t0 + span; x += rate) { const vel = 0.34 + 0.28 * ((b + x / BAR) / sec.bars) + (x % BEAT === 0 ? 0.05 : 0); vs.forEach(n => notes.push({ t: T + x, d: rate - 3, n, v: vel })); }
            break;
          }
          case 'skank': {                             // dub / reggae: short chops on 2 and 4 (or every offbeat), sometimes echoing
            const sk = once('skank', () => ({ at: R.pick([[1, 3], [1, 3], [1, 3, 3.25], [0.5, 1.5, 2.5, 3.5]]), echo: R.chance(0.5) }));
            const vs = v.slice(-3);
            for (const x of sk.at) {
              const tt = x * BEAT; if (tt < t0 || tt >= t0 + span) continue;
              push(tt, 18, 0.66, vs);
              if (sk.echo && x === sk.at[sk.at.length - 1]) for (let e = 1; e <= 2; e++) push(tt + e * S16 * 3, 14, 0.66 * Math.pow(0.45, e), vs);
            }
            break;
          }
          case 'bubble':                              // reggae organ bubble: chord on the &, the low note on the e and a
            for (let k = 0; k < 4; k++) { const tt = k * BEAT; if (tt < t0 || tt >= t0 + span) continue; push(tt + S16 * 2, S16 + 4, 0.52, v.slice(1)); push(tt + S16, 14, 0.34, [v[0]]); push(tt + S16 * 3, 14, 0.38, [v[0]]); }
            break;
          case 'four':                                // four to the bar: short quarter chords, 2 and 4 leaning (Freddie Green, zydeco)
            for (let k = 0; k < 4; k++) { const tt = k * BEAT; if (tt >= t0 && tt < t0 + span) push(tt, S16 * 2 + 4, k % 2 ? 0.6 : 0.5); }
            break;
          case 'shell': {                             // jazz piano: rootless shells, comped off the beat, never the same bar twice
            let sh = v.filter(n => n % 12 !== pcs[0]); if (sh.length < 2) sh = v.slice(-2);
            const rh = R.pick(span === BAR ? [[0, 1.5], [0, 2.5], [1.5, 3], [0, 3.5], [0.5, 2], [0, 1.5, 3]] : [[0], [0.5], [0, 1.5]]);
            rh.forEach((x, i) => { const tt = t0 + x * BEAT, last = i === rh.length - 1; push(tt, last ? Math.min(BEAT * 1.5, t0 + span - tt) - 6 : S16 * 3, 0.56 + (R() - 0.5) * 0.08, sh); });
            break;
          }
          case 'alberti': {                           // piano / lullaby: low–high–middle–high in eighths, or low–middle–high triplets
            const trip = once('alberti', () => (st.lilt ? R.chance(0.8) : R.chance(0.3)));
            const m = v[1] ?? v[0], seq = trip ? [v[0], m, top[0]] : [v[0], top[0], m, top[0]], step = trip ? BEAT / 3 : S16 * 2;
            for (let k = 0; k * step < span; k++) { const x = t0 + k * step; notes.push({ t: T + x, d: Math.min(step * 2, t0 + span - x) - 4, n: seq[k % seq.length], v: k % seq.length === 0 ? 0.52 : 0.4 }); }
            break;
          }
          case 'block': {                             // piano: a held voicing, a hair late, sometimes rolled from the bottom; a soft re-strike
            const late = R.int(0, 8), roll = R.chance(0.5) ? R.int(5, 10) : 0;
            v.forEach((n, i) => notes.push({ t: T + t0 + late + i * roll, d: span - late - i * roll - 6, n, v: (i === v.length - 1 ? 0.56 : 0.48) + (R() - 0.5) * 0.06 }));
            if (span === BAR && R.chance(0.45)) { const a2 = R.pick([BEAT * 2, BEAT * 2, BEAT + S16 * 2, BEAT * 3]) + R.int(0, 6); v.slice(-2).forEach(n => notes.push({ t: T + a2, d: BAR - a2 - 6, n, v: 0.4 })); }
            break;
          }
          case 'ostinato': {                          // minimalism: a 5–7 note cell over the chord, phasing against the bar, one note longer every four bars
            const os = once('ost', () => { const L = R.int(5, 7), cell = []; for (let i = 0; i < L; i++) cell.push(R.int(0, 4)); return { cell, k: 0, rate: R.pick([S16 * 2, S16 * 2, S16]) }; });
            if (half === 0 && b > 0 && b % 4 === 0 && os.cell.length < 9) os.cell.push(R.int(0, 4));
            const tones = v.concat(v.map(n => n + 12));
            for (let x = t0; x < t0 + span; x += os.rate) { const i = os.k++ % os.cell.length; notes.push({ t: T + x, d: os.rate - 4, n: tones[Math.min(os.cell[i], tones.length - 1)], v: i === 0 ? 0.6 : 0.47 }); }
            break;
          }
          case 'chip_arp': {                          // chiptune: the chord as a 32nd (or 16th) arpeggio — one voice faking a chord
            const ca = once('chip', () => ({ rate: R.pick([S16 / 2, S16 / 2, S16]), shape: R.pick(['up', 'updown', 'oct']) }));
            const up = v.concat(top[0] + 12), seq = ca.shape === 'up' ? v : ca.shape === 'updown' ? up.concat(up.slice(1, -1).reverse()) : up;
            let k = 0; for (let x = t0; x < t0 + span; x += ca.rate, k++) notes.push({ t: T + x, d: ca.rate - 2, n: seq[k % seq.length], v: x % BEAT === 0 ? 0.58 : 0.46 });
            break;
          }
          case 'dotted': {                            // post-rock / trip-hop: dotted-eighth arpeggio from the top (a delay's echo pattern)
            const seq = [top[0], v[v.length - 2] ?? v[0], v[0], v[v.length - 2] ?? v[0]];
            for (let k = 0; k * S16 * 3 < span; k++) { const x = t0 + k * S16 * 3; notes.push({ t: T + x, d: Math.min(S16 * 5, t0 + span - x) - 4, n: seq[k % seq.length], v: k % 3 === 0 ? 0.56 : 0.44 }); }
            break;
          }
          case 'chug': {                              // industrial: palm-muted power chord on a sixteenth gate; every 4th bar may ring
            const mask = once('chug', () => R.pick(CHUG)), r0 = nearestPC(lo - 2, [pcs[0]], lo - 9, lo + 4), pw = [r0, r0 + 7, r0 + 12];
            if (b % 4 === 3 && half === 0 && R.chance(0.4)) { push(t0, span - 6, 0.7, pw); break; }
            for (let k = 0; k < 16; k++) { const x = k * S16; if (x >= t0 && x < t0 + span && mask[k] === '1') push(x, S16 - 6, x % BEAT === 0 ? 0.68 : 0.54, pw); }
            break;
          }
          default: push(t0, span - 4, 0.6);
        }
        if (kind === 'pad' && bottom.length && R.chance(0.15)) { /* the pad sometimes leaves the top voice out for air */ }
      }
    }
    harm.prevVoicing = prev;
    return notes;
  }

  // ── lead ────────────────────────────────────────────────────────
  // A motif (rhythm cells + a contour in scale steps) developed over the section: statement, sequence (moved with the
  // harmony), answer (same rhythm, new ending), cadence. A character's leitmotif keeps its rhythm + contour in every
  // track (seeded by the character); key, mode, register and instrument come from the track.
  const CELL_SETS = {
    sparse: [[1, 0, 0, 0], [0, 0, 0, 0], [1, 0, 0, 0], [0, 0, 1, 0]],
    motif: [[1, 0, 0, 0], [1, 0, 1, 0], [1, 1, 1, 0], [0, 0, 1, 0], [1, 0, 0, 1], [0, 1, 1, 0], [1, 0, 1, 1]],
    answer: [[0, 0, 0, 0], [1, 0, 1, 0], [0, 0, 1, 0], [1, 0, 0, 0], [0, 1, 0, 1]],
    hook: [[1, 0, 1, 0], [1, 1, 0, 1], [1, 0, 1, 1], [0, 1, 1, 1], [1, 0, 0, 0]],
    // genre kinds: whistle (long held tones), hymn (stepwise quarters and halves), chip (busy sixteenths, played staccato
    // with arpeggio bursts), lilt (positions 1 / 2 of a cell sit on the triplet: 12/8 in a 4/4 bar), trem (a hook,
    // tremolo-picked), blue (a motif with blue-note slides)
    whistle: [[1, 0, 0, 0], [0, 0, 0, 0], [0, 0, 1, 0], [1, 0, 0, 0], [0, 0, 0, 0]],
    hymn: [[1, 0, 0, 0], [1, 0, 0, 0], [1, 0, 1, 0], [0, 0, 0, 0]],
    chip: [[1, 1, 1, 1], [1, 0, 1, 1], [1, 1, 1, 0], [1, 0, 1, 0], [0, 1, 1, 1]],
    lilt: [[1, 0, 0, 0], [1, 0, 1, 0], [1, 1, 1, 0], [0, 0, 1, 0], [1, 0, 0, 0]],
    trem: [[1, 0, 0, 0], [1, 0, 1, 0], [1, 0, 0, 1], [0, 0, 1, 0]],
    blue: [[1, 0, 0, 0], [1, 0, 1, 0], [0, 0, 1, 0], [1, 0, 0, 1], [0, 1, 1, 0], [1, 1, 1, 0]],
  };
  const LONG_LEAD = { sparse: 1, whistle: 1 }, STEPWISE_LEAD = { hymn: 1, whistle: 1 };
  const LILT = [0, BEAT / 3, (BEAT * 2) / 3, (BEAT * 3) / 4];           // a cell's four positions in a lilting beat
  const CONTOURS = { arch: [1, 1, 1, -1, -1, -1], fall: [-1, -1, 1, -1, -1, 0], rise: [1, 1, -1, 1, 1, 0], wave: [1, -1, 1, -1, 1, -1], still: [0, 1, -1, 0, 1, -1] };
  function makeMotif(MR, kind, density) {
    const cells = CELL_SETS[kind] || CELL_SETS.motif, contour = CONTOURS[MR.pick(Object.keys(CONTOURS))];
    const ev = []; let step = 0, i = 0;
    for (let beat = 0; beat < 8; beat++) {
      const cell = beat > 0 && MR.chance(0.12 + 0.3 * (1 - density)) ? [0, 0, 0, 0] : MR.pick(cells);
      cell.forEach((on, k) => {
        if (!on) return;
        const dir = contour[i++ % contour.length], size = MR.weighted(STEPWISE_LEAD[kind] ? [[1, 6], [0, 1.5], [2, 1]] : [[1, 5], [2, 2], [0, 1.5], [3, 0.6], [4, 0.3]]);
        step += dir * size; step = Math.max(-5, Math.min(7, step));
        ev.push({ s: beat * 4 + k, step });
      });
    }
    if (!ev.length) ev.push({ s: 0, step: 0 });
    return ev;
  }
  function genLead(R, st, sec, ctx, harm, opts) {
    const notes = [], { key, scale } = harm, H = ctx.H, motif = ctx.motif, lo = ctx.range[0], hi = ctx.range[1];
    const plan = ctx.phrase;                                  // e.g. ['M', 'S', 'M', 'C'] per 2-bar slot
    const base = ctx.lift || 0, kind = ctx.kind;
    const tOf = kind === 'lilt' ? s => Math.floor(s / 4) * BEAT + LILT[s % 4] : s => s * S16;
    let lastN = deg2midi(key, scale, base, 5);
    for (let b = 0; b < sec.bars; b += 2) {
      const slot = plan[(b / 2) % plan.length];
      if (slot === '-') continue;                             // breathe
      const c0 = chordAt(H, b);
      const shift = slot === 'S' ? c0.deg - H.prog[0] : slot === 'U' ? 2 : 0;    // sequence with the harmony · up a third
      const ev = slot === 'A' ? motif.filter((m, i) => i < Math.ceil(motif.length / 2) || m.s >= 16) : motif;
      ev.forEach((m, i) => {
        if (b * 16 + m.s >= sec.bars * 16) return;
        const bar = b + Math.floor(m.s / 16), cd = chordAt(H, bar, (m.s % 16) / 4);
        let n = deg2midi(key, scale, base + m.step + shift + (slot === 'A' && m.s >= 16 ? -1 : 0), 5);
        while (n > hi) n -= 12; while (n < lo) n += 12;
        const strong = m.s % 4 === 0;
        if (strong) n = nearestPC(n, chordPcsOf(key, scale, cd), lo, hi);
        if (Math.abs(n - lastN) > 9) n += n > lastN ? -12 : 12;
        n = Math.min(hi, Math.max(lo, n));
        const nextS = i + 1 < ev.length ? ev[i + 1].s : 32;
        const isEnd = (slot === 'C' || slot === 'A') && i === ev.length - 1;
        const dur = Math.max(S16, Math.min(tOf(nextS) - tOf(m.s), LONG_LEAD[kind] ? BAR : kind === 'chip' ? S16 * 2 : BEAT * 2));
        if (isEnd) n = nearestPC(n, chordPcsOf(key, scale, { deg: 0, ext: 'triad' }), lo, hi);
        const t = b * BAR + tOf(m.s), d = isEnd ? Math.min(BAR, (sec.bars - b) * BAR - tOf(m.s)) : dur - 4, vel = clampV((strong ? 0.78 : 0.62) + (R() - 0.5) * 0.12);
        if (kind === 'chip' && strong && !isEnd && R.chance(0.3)) {          // an arpeggio burst in 32nds through the chord
          const up = chordPcsOf(key, scale, cd), burst = [n, nearestPC(n + 4, up, n + 2, n + 5), nearestPC(n + 7, up, n + 6, n + 9), n + 12];
          burst.forEach((x, k) => { if (k * 12 < dur) notes.push({ t: t + k * 12, d: 10, n: x, v: clampV(vel - k * 0.05) }); });
        } else if (kind === 'trem' && d >= BEAT) {                            // tremolo-picked: the note re-struck in 32nds
          for (let x = 0; x < d; x += 12) notes.push({ t: t + x, d: 10, n, v: clampV(vel * (x % 24 ? 0.82 : 1)) });
        } else notes.push({ t, d, n, v: vel });
        // a grace note into some strong notes
        const graced = strong && ctx.kind !== 'sparse' && R.chance(0.08) && m.s > 0;
        if (graced) notes.push({ t: b * BAR + m.s * S16 - 12, d: 10, n: n + (inScale(n + 2, key, scale) ? 2 : 1), v: 0.45 });
        // blue: a slide from a semitone under into some strong notes (the third, the fifth)
        if (kind === 'blue' && strong && m.s > 0 && !graced && R.chance(0.3)) notes.push({ t: t - 10, d: 10, n: n - 1, v: 0.48 });
        lastN = n;
      });
    }
    return notes;
  }

  // ── pad ─────────────────────────────────────────────────────────
  function genPad(R, st, sec, ctx, harm, opts) {
    const notes = [], { key, scale } = harm, H = ctx.H, kind = ctx.fig;
    for (let b = 0; b < sec.bars; b += 2) {
      const c = chordAt(H, b), len = Math.min(2, sec.bars - b) * BAR - 8, T = b * BAR;
      const r = deg2midi(key, scale, c.deg, 3), f = deg2midi(key, scale, c.deg + 4, 3), th = deg2midi(key, scale, c.deg + 2, 4);
      if (kind === 'drone') notes.push({ t: T, d: len, n: r - 12, v: 0.55 }, { t: T, d: len, n: f - 12, v: 0.45 });
      else if (kind === 'sus') {           // the fourth, resolving to the third halfway
        const s4 = deg2midi(key, scale, c.deg + 3, 4);
        notes.push({ t: T, d: len, n: r, v: 0.45 }, { t: T, d: len, n: f, v: 0.4 }, { t: T, d: Math.round(len / 2), n: s4, v: 0.36 }, { t: T + Math.round(len / 2), d: len - Math.round(len / 2), n: th, v: 0.36 });
      } else if (kind === 'moving') {       // a slow top line: chord tones stepping each bar
        notes.push({ t: T, d: len, n: r, v: 0.42 }, { t: T, d: len, n: f, v: 0.38 });
        const tops = chordNotes(key, scale, c, 4).slice(1);
        const a = R.pick(tops), z = R.pick(tops);
        notes.push({ t: T, d: Math.min(BAR - 8, len), n: a, v: 0.36 });
        if (len > BAR) notes.push({ t: T + BAR, d: len - BAR, n: z, v: 0.34 });
      } else if (kind === 'shimmer') {      // high fifth + ninth over the root
        notes.push({ t: T, d: len, n: r, v: 0.4 }, { t: T, d: len, n: deg2midi(key, scale, c.deg + 4, 5), v: 0.3 }, { t: T, d: len, n: deg2midi(key, scale, c.deg + 8, 5), v: 0.26 });
      } else if (kind === 'cluster') {      // dark drone / horror: root + fifth, a minor ninth creeping in, sometimes the tritone
        const half = Math.round(len / 2);
        notes.push({ t: T, d: len, n: r - 12, v: 0.44 }, { t: T, d: len, n: f, v: 0.34 }, { t: T + half, d: len - half, n: r + 13, v: 0.24 });
        if (R.chance(0.5)) notes.push({ t: T + Math.round(len * 3 / 4), d: len - Math.round(len * 3 / 4), n: r + 18, v: 0.2 });
      } else if (kind === 'rise') {         // post-rock: the triad swelling toward the end of the section
        const v = 0.22 + 0.48 * Math.min(1, (b + 2) / sec.bars);
        notes.push({ t: T, d: len, n: r, v }, { t: T, d: len, n: f, v: v * 0.9 }, { t: T, d: len, n: th, v: v * 0.8 }, { t: T, d: len, n: r + 24, v: v * 0.6 });
      } else if (kind === 'open') {         // hymn / organ: open voicing — root, fifth, octave, tenth
        notes.push({ t: T, d: len, n: r - 12, v: 0.4 }, { t: T, d: len, n: f, v: 0.36 }, { t: T, d: len, n: r + 12, v: 0.32 }, { t: T, d: len, n: th + 12, v: 0.28 });
      } else notes.push({ t: T, d: len, n: r, v: 0.45 }, { t: T, d: len, n: f, v: 0.4 }, { t: T, d: len, n: th, v: 0.35 });
    }
    return notes;
  }

  // ── arrangement parts: counter, arp, perc, double ───────────────
  // Parts an arranger adds over the five-piece band. Each style says how likely each one is and which figures are
  // idiomatic (ARRANGE); plan() decides per song from its own 'arr:<role>' streams, so these parts never move a note
  // of drums / bass / chords / lead / pad (tests/fixtures/seqgen_roles_v2.json pins those).
  const ARR_ROLES = ['counter', 'arp', 'perc', 'double'];
  const ARR_AUTO_MAX = 2;
  const pcOf = n => ((n % 12) + 12) % 12;
  // one voice at a time: each note ends before the next one starts (counter, arp and double are monophonic)
  function monoLine(ns) {
    const s = ns.slice().sort((a, b) => a.t - b.t || b.v - a.v), out = [];
    for (const x of s) {
      const prev = out[out.length - 1];
      if (prev && prev.t === x.t) continue;
      if (prev && prev.t + prev.d > x.t - 2) prev.d = Math.max(4, x.t - prev.t - 2);
      out.push(Object.assign({}, x));
    }
    return out;
  }
  // counter — a second melodic voice built on the same chords, aware of the lead's actual notes in the section:
  //   answer    call / response: short phrases in the lead's rests, moving against the lead's last direction
  //   horn      a muted horn: one or two long notes swelling in the rests (noir, dub)
  //   second    a second voice in halves / wholes, contrary to the lead, passing tones on weak beats (chamber, hymn)
  //   guide     jazz guide tones: the 3rd / 7th of each chord, voice-led, anticipated past the lead's onsets
  //   harmony   a harmony a third or a sixth below the lead, phrase by phrase (folk fiddle / second whistle)
  //   ring      a high ringing line: a slow pendulum between the top chord tones (post-rock)
  //   interlock an eighth-note cell in the gaps of the lead (minimalism)
  // Never a unison / octave against the lead where a note starts; never a new note on a lead onset (but harmony,
  // which moves with the lead by design).
  const ANSWER_CELLS = [[0, 2, 4], [0, 4], [0, 2, 6], [2, 4], [0, 3, 6], [0, 2]];
  function genCounter(R, st, sec, ctx, harm, opts) {
    const { key, scale } = harm, H = ctx.H, [lo, hi] = ctx.range, bars = sec.bars, N = bars * 16, kind = ctx.kind;
    // the lead on a 16th grid (grace notes and slides left out; swung offbeats read on the straight grid)
    const lead = (ctx.lead || []).filter(x => x.d > 10 || x.v >= 0.5).map(x => {
      const pos = ((x.t % BEAT) + BEAT) % BEAT;
      return ctx.unswing && pos === BEAT / 2 + BEAT / 6 ? Object.assign({}, x, { t: x.t - BEAT / 6 }) : x;
    });
    const on = new Uint8Array(N + 1), snd = new Array(N + 1).fill(null), age = new Array(N + 1).fill(0);
    for (const x of ctx.unswing ? ctx.lead || [] : []) {         // swung: an eighth the counter would swing onto a lead onset is taken
      if (!(x.d > 10 || x.v >= 0.5)) continue;
      const b0 = Math.floor(x.t / BEAT), pos = x.t - b0 * BEAT, s = pos < 16 ? b0 * 4 : pos > 84 ? b0 * 4 + 4 : pos >= 44 ? b0 * 4 + 2 : -1;
      if (s >= 0 && s < N) on[s] = 1;
    }
    for (const x of lead) {
      const s = Math.round(x.t / S16); if (s >= 0 && s < N) on[s] = 1;
      for (let k = Math.max(0, Math.floor(x.t / S16)); k < Math.min(N, Math.ceil((x.t + x.d) / S16)); k++) { snd[k] = x.n; age[k] = k - Math.floor(x.t / S16); }
    }
    // where the lead leaves room: a rest, or the tail of a note it has held for a beat (a fill under a held note)
    const room = s => s < N && !on[s] && (snd[s] === null || age[s] >= 4);
    const pcsAt = s => chordPcsOf(key, scale, chordAt(H, Math.floor(s / 16), (s % 16) / 4));
    const okLead = (n, s) => { const l = snd[Math.min(N - 1, Math.max(0, s))]; return l === null || pcOf(n - l) !== 0; };
    const free = s => s >= 0 && s < N && !on[s];
    const pool = (s, chordTone) => { const pcs = pcsAt(s), out = []; for (let n = lo; n <= hi; n++) if ((chordTone ? pcs.includes(pcOf(n)) : inScale(n, key, scale)) && okLead(n, s)) out.push(n); return out; };
    const nearest = (c, target) => c.reduce((a, n) => (a === null || Math.abs(n - target) < Math.abs(a - target) ? n : a), null);
    // the next note: a chord tone on a strong beat (else a scale step), in direction dir from prev when there is one
    const next = (s, prev, dir, chordTone) => {
      let c = pool(s, chordTone); if (!c.length) c = pool(s, false); if (!c.length) return null;
      if (dir) { const d = c.filter(n => (n - prev) * dir > 0 && Math.abs(n - prev) <= 7); if (d.length) return nearest(d, prev); }
      return nearest(c.filter(n => n !== prev).length ? c.filter(n => n !== prev) : c, prev);
    };
    // the lead's last move before s: up (1) or down (−1) — the counter goes the other way
    const leadDir = s => { let a = null, b = null; for (let k = s - 1; k >= 0 && b === null; k--) { const n = snd[k]; if (n === null) continue; if (a === null) a = n; else if (n !== a) b = n; } return a !== null && b !== null ? Math.sign(a - b) : 0; };
    const shift = (s, tries) => { for (const d of tries) if (free(s + d)) return s + d; return null; };
    const out = [], push = (s, len, n, v) => { if (n !== null && len > 0) out.push({ t: s * S16, d: Math.max(6, len * S16 - 6), n, v: clampV(v + (R() - 0.5) * 0.06) }); };
    let prev = nearest(pool(0, true), Math.round((lo + hi) / 2)) ?? Math.round((lo + hi) / 2);
    const hasLead = lead.length > 0;
    const play = k0 => {
      if (k0 === 'answer' || k0 === 'horn') {
        const cells = ANSWER_CELLS.filter(c => !st.trip8 || c.every(x => x % 2 === 0));
        for (let a = 0; a < N;) {
          if (!room(a)) { a++; continue; }
          let z = a; while (z < N && room(z)) z++;
          let s0 = a + (a % 2);
          for (let chunk = 0; s0 < z; chunk++) {
            const end = Math.min(z, s0 + (k0 === 'horn' ? 16 : 8)), len = end - s0;
            if (len >= 4 && (chunk === 0 || R.chance(0.5))) {
              const rh = k0 === 'horn' ? (len >= 8 ? R.pick([[0], [0, 4], [0]]) : [0]) : len >= 8 ? R.pick(cells) : R.pick([[0], [0, 2]]).filter(x => x < len);
              let dir = -leadDir(s0) || R.pick([-1, 1]);
              rh.forEach((off, i) => {
                const s = s0 + off; if (s >= z || !free(s)) return;
                const last = i === rh.length - 1, strong = s % 8 === 0 || last;
                const n = next(s, prev, i ? dir : 0, strong || k0 === 'horn');
                if (n === null) return;
                if (i && R.chance(0.2)) dir = -dir;                       // a turn inside the answer
                const until = last ? Math.min(N, end + (R.chance(0.5) ? 4 : 0)) : s0 + rh[i + 1];
                push(s, until - s, n, k0 === 'horn' ? 0.44 : 0.5 + (strong ? 0.05 : 0));
                prev = n;
              });
            }
            s0 = end;
          }
          a = z;
        }
      } else if (k0 === 'second' || k0 === 'ring') {
        const whole = k0 === 'ring' || R.chance(0.45), step = whole ? 16 : 8;
        for (let s = 0; s < N; s += step) {
          const at = shift(s, st.trip8 ? [0, 2, 4] : [0, 2, 4, 1]); if (at === null) continue;   // a voice entering just after the lead (a suspension)
          let dir = 0;
          if (k0 === 'second' && snd[s] !== null && s >= step && snd[s - step] !== null) dir = -Math.sign(snd[s] - snd[s - step]);
          const n = k0 === 'ring' ? nearest(pool(at, true).filter(x => x !== prev).slice(-3), prev) ?? next(at, prev, 0, true) : next(at, prev, dir, true);
          const nx = Math.min(N, s + step);
          // a passing tone on the weak half toward the next chord (second voice in wholes)
          if (k0 === 'second' && whole && R.chance(0.35) && free(s + 8)) {
            const tgt = nearest(pool(Math.min(N - 1, s + 16), true), n ?? prev) ?? prev, d = Math.sign(tgt - (n ?? prev));
            const p = d ? next(s + 8, n ?? prev, d, false) : null;
            push(at, s + 8 - at, n, 0.5); if (p !== null && Math.abs(p - tgt) <= 4) { push(s + 8, nx - s - 8, p, 0.44); prev = p; } else prev = n ?? prev;
            continue;
          }
          push(at, nx - at, n, k0 === 'ring' ? 0.42 : 0.5);
          if (n !== null) prev = n;
        }
      } else if (k0 === 'guide') {
        let lastKey = null;
        for (let s = 0; s < N; s += 8) {
          const c = chordAt(H, Math.floor(s / 16), (s % 16) / 4), ck = c.deg + ':' + c.ext;
          if (ck === lastKey && s % 16) continue;
          lastKey = ck;
          const tones = chordNotes(key, scale, c, 4), g = [tones[1], tones[3] ?? tones[2]].map(pcOf);
          const at = shift(s, [0, -2, 2, 4]); if (at === null || (out.length && at * S16 <= out[out.length - 1].t)) continue;
          const cands = []; for (let n = lo; n <= hi; n++) if (g.includes(pcOf(n)) && okLead(n, at)) cands.push(n);
          const n = nearest(cands, prev); if (n === null) continue;
          let nx = s + 8; while (nx < N && chordAt(H, Math.floor(nx / 16), (nx % 16) / 4).deg === c.deg) nx += 8;
          push(at, Math.min(N, nx) - at, n, 0.5); prev = n;
        }
      } else if (k0 === 'harmony') {
        const below = R.pick([2, 2, 5]);                                  // a third (or a sixth) under the tune
        const down = (n, k) => { let m = n; for (let i = 0; i < k; i++) { m--; while (!inScale(m, key, scale)) m--; } return m; };
        for (let b = 0; b < bars; b += 2) {
          if (!R.chance(0.65)) continue;
          for (const x of lead) {
            if (x.t < b * BAR || x.t >= (b + 2) * BAR || x.d < S16 || !inScale(x.n, key, scale)) continue;
            let n = down(x.n, below); while (n < lo) n += 12; while (n > hi) n -= 12;
            if (pcOf(n - x.n) === 0) continue;
            out.push({ t: x.t, d: x.d, n, v: clampV(x.v * 0.72) });
          }
        }
      } else if (k0 === 'interlock') {
        const L = R.int(3, 5), cell = [], pit = [];
        for (let i = 0; i < L; i++) { cell.push(i === 0 || R.chance(0.6)); pit.push(R.int(0, 2)); }
        for (let s = 0; s < N; s += 2) {
          const i = (s / 2) % L; if (!cell[i] || !free(s)) continue;
          const pcs = pcsAt(s), tones = []; for (let n = lo; n <= hi && tones.length < 4; n++) if (pcs.includes(pcOf(n))) tones.push(n);
          let n = tones[pit[i] % (tones.length || 1)]; if (n === undefined) continue;
          if (!okLead(n, s)) n = tones.find(m => okLead(m, s)); if (n === undefined) continue;
          push(s, 2, n, i === 0 ? 0.52 : 0.44);
        }
      }
    };
    // no lead to answer (or a lead that never leaves room): a second voice in long notes instead
    const k0 = !hasLead && (kind === 'answer' || kind === 'horn' || kind === 'harmony' || kind === 'guide') ? 'second' : kind;
    play(k0);
    if ((k0 === 'answer' || k0 === 'horn') && out.length < 2) { out.length = 0; play('second'); }
    // a held note the lead moves onto (unison / octave on beat 1 or 3) ends just before that beat
    const res = [];
    for (const x of monoLine(out)) {
      for (let t = Math.ceil((x.t + 1) / (2 * BEAT)) * 2 * BEAT; t < x.t + x.d; t += 2 * BEAT) {
        const l = snd[Math.min(N - 1, t / S16)];
        if (l !== null && pcOf(x.n - l) === 0) { x.d = t - x.t - 6; break; }
      }
      if (x.d >= S16) res.push(x);
    }
    return res;
  }

  // arp — an ostinato over the current chord, one note at a time:
  //   up · down · updown · thirds (broken thirds: 1 3 2 4 3 5) · alberti (low high mid high) · pedal (a pedal tone
  //   between the moving chord tones) · seq16 (a sixteenth sequencer cell, an octave jump, a gate) · triplet · walk
  //   (a random walk inside the chord). Rate from density; registers: low / mid / high (above the lead for bells).
  const ARP_GATES = ['1011101110111011', '1101101101101101', '1110111011101110', '1011011010110110', '1111111011111110'];
  const SEQ_CELLS = [[0, 1, 2, 1], [0, 2, 1, 3], [0, 2, 3, 1], [0, 1, 3, 2], [0, 3, 1, 2], [0, 0, 2, 1]];
  const ARP_RANGE = { low: [45, 66], mid: [55, 77], high: [72, 93] };
  function genArp(R, st, sec, ctx, harm, opts) {
    const notes = [], { key, scale } = harm, H = ctx.H, kind = ctx.kind, [lo, hi] = ARP_RANGE[ctx.reg] || ARP_RANGE.mid, bars = sec.bars, dens = opts.density;
    let rate = kind === 'triplet' ? BEAT / 3 : kind === 'seq16' || kind === 'pedal' ? S16 : kind === 'alberti' || kind === 'walk' ? (dens > 0.7 ? S16 : S16 * 2) : (dens >= 0.6 ? S16 : S16 * 2);
    if (st.trip8 && rate === S16) rate = BEAT / 3;                    // swung styles: triplets, never straight sixteenths
    const cell = R.pick(SEQ_CELLS), octJump = R.chance(0.5), span = ctx.span || 4, len = ctx.legato ? 0.85 : 0.5;
    let k = 0, wi = 1, lastKey = '';
    for (let x = 0; x < bars * BAR; x += rate) {
      const b = Math.floor(x / BAR), beat = (x % BAR) / BEAT, c = chordAt(H, b, beat), pcs = chordPcsOf(key, scale, c);
      const tones = []; for (let n = lo; n <= hi && tones.length < 7; n++) if (pcs.includes(pcOf(n))) tones.push(n);
      if (!tones.length) continue;
      const ck = c.deg + ':' + c.ext; if (ck !== lastKey) { lastKey = ck; if (kind !== 'walk') k = 0; }
      const L = Math.min(tones.length, span);
      let n;
      switch (kind) {
        case 'down': n = tones[L - 1 - (k % L)]; break;
        case 'updown': { const per = Math.max(1, 2 * L - 2), i = k % per; n = tones[i < L ? i : per - i]; break; }
        case 'thirds': { const kk = k % (2 * Math.max(1, tones.length - 2)); n = tones[Math.min(tones.length - 1, (kk >> 1) + (kk & 1) * 2)]; break; }
        case 'alberti': n = tones[[0, L - 1, Math.min(1, L - 1), L - 1][k % 4]]; break;
        case 'pedal': n = k % 2 === 0 ? tones[0] : tones[1 + ((k >> 1) % Math.max(1, L - 1))] ?? tones[0]; break;
        case 'seq16': { n = tones[cell[k % 4] % L]; if (octJump && k % 8 === 7 && n + 12 <= hi + 12) n += 12; break; }
        case 'walk': wi = Math.max(0, Math.min(tones.length - 1, wi + R.pick([-1, 1, 1, -1, 2, -2]))); n = tones[wi]; break;
        default: n = tones[k % L];                                      // up, triplet
      }
      const step16 = Math.round((x % BAR) / S16);
      k++;
      if (ctx.gate && rate === S16 && ctx.gate[step16 % 16] === '0') continue;
      if (x % BEAT !== 0 && dens < 0.35 && R.chance(0.3)) continue;   // sparse: the arp thins between the beats
      const acc = (x % BEAT === 0 ? 0.1 : 0) + (ctx.accent && (k - 1) % ctx.accent === 0 ? 0.07 : 0);
      notes.push({ t: Math.round(x), d: Math.max(8, Math.round(rate * len)), n, v: clampV((0.44 + acc) * (ctx.lvl || 1) + (R() - 0.5) * 0.06) });
    }
    return notes;
  }

  // perc — a hand percussionist next to the kit (on a KIT device: congas 60–64, tambourine 54, cowbell 56, cabasa 69,
  // shaker 70, claves 75, wood blocks 76 / 77). Each kit is a few [GM note, grid, velocity]; a 32-step grid spans two
  // bars, a 12-step one is a bar of triplet eighths. The drums' own percussion colour (PERC / pl.perc) stays in the
  // drums part untouched; a song's perc avoids the voices its drums already play.
  const PERC_KITS = {
    conga: [[61, '0000100000001000', 0.6], [62, '0000001000001010/0.85', 0.7], [64, '1000000010000000/0.6', 0.5]],      // tumbao: slap on 2 & 4, open tones on 4-and
    bongo: [[60, '1010100010101000', 0.5], [61, '0000001000000010', 0.58]],                                               // martillo
    shaker: [[70, '1111111111111111/0.85', 0.3]],
    trip_shaker: [[70, '101101101101/0.9', 0.32]],
    cabasa: [[69, '1010101010101010', 0.34]],
    tamb: [[54, '0000100000001000', 0.6], [54, '0010001000100010/0.55', 0.3]],
    cowbell: [[56, '1000100010001000', 0.48], [56, '0010000000100000/0.5', 0.34]],
    clave: [[75, '10010010000000000000100010000000', 0.55]],                                                                // son clave 3-2
    woodblock: [[76, '1000000010000000', 0.42], [77, '0000100000001000', 0.38]],                                         // tick-tock
    frame: [[64, '1000000010000000', 0.55], [63, '0000100000001000/0.6', 0.34]],                                         // a frame drum
    nyabinghi: [[64, '1000000010000000', 0.66], [62, '0000100000001000/0.8', 0.42], [60, '0010001000100010/0.6', 0.32]],
    washboard: [[70, '111111111111/0.9', 0.32], [54, '000100000100', 0.48]],
  };
  const KIT_NOTES = k => (PERC_KITS[k] || []).map(x => x[0]);
  function genPerc(R, st, sec, ctx, opts) {
    const notes = [], bars = sec.bars, dens = opts.density, kits = ctx.kits || [];
    const drumish = kits.some(k => /conga|bongo|frame|nyabinghi/.test(k));
    for (let b = 0; b < bars; b++) {
      const T = b * BAR, fill = drumish && !opts.bed && (b === bars - 1 || b % 4 === 3) && R.chance(0.45);
      for (const kit of kits) for (const [n, g, vel] of PERC_KITS[kit] || []) {
        const grid = parseGrid(g), steps = grid.length === 32 ? 16 : grid.length, off = grid.length === 32 ? (b % 2) * 16 : 0, stepT = BAR / steps;
        for (let s = 0; s < steps; s++) {
          const p = grid[off + s]; if (!p) continue;
          const at = s * stepT, pos = at % BEAT;
          if (fill && at >= 3 * BEAT && n >= 60 && n <= 64) continue;           // the fill takes beat 4
          const accent = kit === 'shaker' || kit === 'cabasa' ? (pos === BEAT / 2 ? 1.35 : pos === 0 ? 1 : 0.8) : pos === 0 ? 1.12 : pos === BEAT / 2 ? 0.95 : 0.82;
          if (!R.chance(accent >= 1 ? p : p * (0.55 + 0.45 * dens))) continue;
          notes.push({ t: T + Math.round(at), d: S16, n, v: clampV(vel * accent * (ctx.lvl || 1) + (R() - 0.5) * 0.08) });
        }
      }
      if (fill) {
        const run = R.pick([[62, 62, 63, 64], [60, 60, 61, 61], [61, 62, 63, 64], [60, 61, 62, 64]]), at = st.trip8 ? [0, 32, 64] : [0, 24, 48, 72];
        at.forEach((x, i) => notes.push({ t: T + 3 * BEAT + x, d: S16, n: run[i], v: clampV(0.45 + i * 0.08) }));
      }
    }
    return notes;
  }

  // double — the lead an octave down (or up), or the bass an octave up, for lift in B / C: the same notes on another
  // instrument, softer. Sometimes it arrives halfway through a long section.
  function genDouble(R, sec, ctx) {
    const src = (ctx.src || []).filter(x => x.d > 10 || x.v >= 0.5), kind = ctx.kind;
    const sh = kind === 'lead_low' ? -12 : 12, g = kind === 'bass_up' ? 0.62 : kind === 'lead_high' ? 0.55 : 0.7;
    const from = sec.bars >= 8 && R.chance(0.35) ? Math.floor(sec.bars / 2) * BAR : 0;
    return monoLine(src.filter(x => x.t >= from).map(x => ({ t: x.t, d: x.d, n: x.n + sh, v: clampV(x.v * g) })).filter(x => x.n >= 36 && x.n <= 100));
  }

  // ── sound design: texture beds, transitions, hits ──────────────
  // texture: one held note per section (the bed's own preset breathes; the level follows the section)
  function genTexture(R, sec, ctx) {
    const lvl = { intro: 0.75, brk: 0.8, outro: 0.75, C: 0.65, B: 0.5, A: 0.55, loop: 0.6, bed: 0.7 }[baseOf(sec.name)] ?? 0.6;
    return [{ t: 0, d: sec.bars * BAR - 2, n: ctx.pitch || 48, v: clampV(lvl * (ctx.gain || 1)) }];
  }
  // transitions: a riser / swell over the bars before a lift (B, C, a loop's restart); a downer before a break / outro
  function genFx(R, sec, ctx) {
    const notes = [], into = ctx.into, bars = sec.bars;
    // a whoosh / tape stop is a ~1 s event from its note-on: it goes a beat before the downbeat, not over bars
    if (ctx.short) { if (into) notes.push({ t: bars * BAR - BEAT, d: BEAT - 4, n: 60, v: into === 'up' ? 0.7 : 0.6 }); return notes; }
    if (into === 'up' && bars >= 2) { const len = Math.min(bars, R.pick([1, 2, 2, 4])); notes.push({ t: (bars - len) * BAR, d: len * BAR - 4, n: 60, v: 0.7 }); }
    else if (into === 'down' && bars >= 2) notes.push({ t: (bars - 1) * BAR, d: BAR - 4, n: 60, v: 0.6 });
    return notes;
  }
  // hits: on the downbeat of a lift, sometimes mid-section on a phrase start
  function genHit(R, sec, ctx) {
    const notes = [];
    if (ctx.on0) notes.push({ t: 0, d: BEAT * 2, n: 48, v: 0.8 });
    if (sec.bars >= 8 && R.chance(0.35)) notes.push({ t: 8 * BAR > (sec.bars - 1) * BAR ? 4 * BAR : 8 * BAR, d: BEAT * 2, n: 48, v: 0.55 });
    return notes.filter(x => x.t < sec.bars * BAR);
  }
  // default beds / transitions / hits per style — the catalog's own sound words (soundsFromText) come first
  const TEXTURE_FOR = { four_floor: ['amb_city'], boom_bap: ['amb_vinyl', 'amb_city'], lofi: ['amb_vinyl', 'amb_tape_hiss', 'amb_rain'], trap: ['amb_city', 'amb_room_tone'],
    dnb: ['amb_city'], shuffle: ['amb_room_tone', 'amb_vinyl'], motorik: ['drone_engine', 'amb_tape_hiss'], synthwave: ['amb_tape_hiss', 'amb_city'],
    noir: ['amb_rain', 'amb_room_tone', 'amb_radio', 'amb_vinyl'], ambient: ['amb_wind', 'amb_room_tone', 'drone_horizon', 'amb_forest_night'],
    folk: ['amb_crickets', 'amb_fire', 'amb_wind', 'amb_forest_night'], chamber: ['amb_room_tone', 'amb_rain', 'amb_clock'], piano: ['amb_room_tone', 'amb_rain', 'amb_clock', 'amb_vinyl'],
    hymn: ['amb_room_tone', 'amb_fire', 'amb_wind', 'drone_cathedral'], dark_drone: ['amb_wind', 'amb_room_tone', 'amb_fluor_hum', 'drone_engine', 'amb_life_support'],
    synth_horror: ['amb_tape_hiss', 'amb_fluor_hum', 'amb_wind', 'amb_crickets'], jazz: ['amb_rain', 'amb_room_tone', 'amb_vinyl', 'amb_city'],
    dub: ['amb_vinyl', 'amb_tape_hiss', 'amb_city', 'amb_rain'], post_rock: ['amb_wind', 'amb_tape_hiss', 'amb_forest_night', 'amb_surf'],
    lullaby: ['amb_crickets', 'amb_clock', 'amb_room_tone', 'amb_rain'], industrial: ['drone_engine', 'amb_fluor_hum', 'amb_life_support', 'amb_city'],
    surf: ['amb_surf', 'amb_vinyl', 'amb_wind', 'amb_city'], bayou: ['amb_crickets', 'amb_cicadas', 'amb_forest_night', 'drone_bayou'],
    minimal: ['amb_room_tone', 'amb_clock', 'amb_tape_hiss', 'drone_horizon'], chiptune: ['amb_fluor_hum', 'amb_modem', 'amb_room_tone', 'amb_city'],
    trip_hop: ['amb_vinyl', 'amb_rain', 'amb_city', 'amb_tape_hiss'] };
  const FX_FOR = { four_floor: ['fx_riser', 'fx_noise_sweep'], trap: ['fx_riser', 'fx_reverse_swell'], dnb: ['fx_riser', 'fx_noise_sweep'], synthwave: ['fx_riser', 'fx_reverse_swell'],
    motorik: ['fx_noise_sweep', 'fx_riser'], boom_bap: ['fx_reverse_swell', 'fx_whoosh'], lofi: ['fx_reverse_swell', 'fx_tape_stop'], shuffle: ['fx_reverse_swell', 'fx_whoosh'],
    noir: ['fx_reverse_swell', 'fx_noise_sweep'], ambient: ['fx_reverse_swell'],
    folk: ['fx_reverse_swell', 'fx_whoosh'], chamber: ['fx_reverse_swell'], piano: ['fx_reverse_swell'], hymn: ['fx_reverse_swell'], dark_drone: ['fx_reverse_swell', 'fx_downer', 'fx_noise_sweep'],
    synth_horror: ['fx_riser', 'fx_reverse_swell', 'fx_noise_sweep'], jazz: ['fx_reverse_swell', 'fx_whoosh'], dub: ['fx_reverse_swell', 'fx_tape_stop', 'fx_whoosh'],
    post_rock: ['fx_reverse_swell', 'fx_riser', 'fx_noise_sweep'], lullaby: ['fx_reverse_swell'], industrial: ['fx_noise_sweep', 'fx_riser', 'fx_tape_stop'],
    surf: ['fx_reverse_swell', 'fx_whoosh', 'fx_riser'], bayou: ['fx_reverse_swell', 'fx_whoosh'], minimal: ['fx_reverse_swell', 'fx_noise_sweep'],
    chiptune: ['fx_riser', 'fx_noise_sweep'], trip_hop: ['fx_reverse_swell', 'fx_tape_stop'] };
  const HIT_FOR = { four_floor: ['fx_impact'], trap: ['fx_sub_drop', 'fx_impact'], dnb: ['fx_sub_drop', 'fx_impact'], synthwave: ['fx_impact', 'fx_glass_ping'], motorik: ['fx_impact'],
    boom_bap: ['fx_wood_knock', 'fx_impact'], lofi: ['fx_glass_ping', 'fx_wood_knock'], shuffle: ['fx_wood_knock', 'fx_bell_hit'], noir: ['fx_bell_hit', 'fx_glass_ping'], ambient: ['fx_bell_hit', 'fx_glass_ping'],
    folk: ['fx_wood_knock', 'fx_bell_hit'], chamber: ['fx_bell_hit', 'fx_glass_ping'], piano: ['fx_glass_ping', 'fx_bell_hit'], hymn: ['fx_bell_hit'], dark_drone: ['fx_sub_drop', 'fx_bell_hit'],
    synth_horror: ['fx_impact', 'fx_sub_drop', 'fx_bell_hit'], jazz: ['fx_glass_ping', 'fx_bell_hit'], dub: ['fx_sub_drop', 'fx_glass_ping'], post_rock: ['fx_impact', 'fx_bell_hit'],
    lullaby: ['fx_glass_ping', 'fx_bell_hit'], industrial: ['fx_impact', 'fx_sub_drop', 'fx_wood_knock'], surf: ['fx_impact', 'fx_glass_ping'], bayou: ['fx_wood_knock', 'fx_bell_hit'],
    minimal: ['fx_glass_ping', 'fx_bell_hit'], chiptune: ['fx_impact', 'fx_glass_ping', 'fx_flicker'], trip_hop: ['fx_sub_drop', 'fx_glass_ping'] };
  // where a preset a newer FORGE adds isn't there yet, the page swaps in its nearest older sound (temp_maker.js)
  const SOUND_FALLBACK = { amb_vinyl: 'amb_radio', amb_tape_hiss: 'amb_radio', amb_room_tone: 'amb_wind', amb_fluor_hum: 'pad_fluorescent', amb_life_support: 'drone_engine',
    amb_crickets: 'amb_wind', amb_cicadas: 'amb_wind', amb_surf: 'amb_wind', amb_fire: 'amb_rain', amb_thunder: 'amb_rain', amb_city: 'drone_engine', amb_clock: 'amb_wind',
    amb_forest_night: 'amb_wind', amb_modem: 'amb_radio', fx_reverse_swell: 'fx_riser', fx_whoosh: 'fx_noise_sweep', fx_tape_stop: 'fx_downer', fx_sub_drop: 'fx_impact',
    fx_bell_hit: 'bell_tubular', fx_wood_knock: 'fx_impact', fx_glass_ping: 'bell_glock' };

  // ── song ────────────────────────────────────────────────────────
  // o: { seed, style, key, mode, bpm, form, density, progression, motif (a leitmotif's seed: a character's name),
  //      textures [preset ids] | 'none', fx (preset | 'none'), hit (preset | 'none'), voices { role: FORGE preset } }
  const ROLES = ['drums', 'bass', 'chords', 'lead', 'pad'];
  const SD_ROLES = ['texture', 'texture2', 'fx', 'hit'];
  // The arrangement parts of one song: whether it has each (the style's odds, or o.arrange), its figures, and the
  // sections each one plays in. Every draw comes from a stream of its own (P('arr:<role>'), P('arr:place:<role>')),
  // so these never reshuffle the five original roles, nor each other. o.arrange: undefined = the style's odds ·
  // 'none' = no arrangement parts · [roles] = those always (the rest by the odds). A cue's own section roles stand.
  function arrangePlan(P, o, st, styleId, sections, { formId, sparse, density, gi, gB, perc }) {
    const AR = ARRANGE[styleId] || ARRANGE_DEFAULT, forced = Array.isArray(o.arrange) ? o.arrange : [], off = o.arrange === 'none';
    const arr = {};
    ARR_ROLES.forEach((role, i) => {
      const A = P('arr:' + role), roll = A.chance((AR.p[i] || 0) * (sparse ? 0.65 : 1));
      const on = !off && (roll || forced.includes(role));
      if (role === 'counter') { const kind = A.pick(AR.counter); arr.counter = { on, kind, range: COUNTER_RANGE[kind] || [55, 74] }; }
      else if (role === 'arp') {
        const kindA = A.pick(AR.arp), kindB = A.chance(0.5) ? A.pick(AR.arp) : kindA;
        arr.arp = { on, kindA, kindB, reg: A.pick(AR.reg), span: A.pick([3, 4, 4, 5]), legato: A.chance(0.5), accent: A.pick([0, 0, 3, 4, 5]),
          gate: A.chance(kindA === 'seq16' ? 0.7 : 0.2) ? A.pick(ARP_GATES) : null, intro: A.chance(/synthwave|motorik|minimal|chiptune|post_rock/.test(styleId) ? 0.55 : 0.2), early: A.chance(0.4) };
      } else if (role === 'perc') {
        // the voices the kit already plays (both grooves + the drums' colour) are left to the drums
        const busy = new Set();
        for (const g of [st.grooves[gi], st.grooves[gB]]) for (const v of Object.keys(g || {})) busy.add(GM_OF[v]);
        if (perc && PERC[perc]) { busy.add(PERC[perc].n); if (PERC[perc].n2) busy.add(PERC[perc].n2); }
        const cands = AR.perc.map(k => (st.trip8 && k === 'shaker' ? 'trip_shaker' : k)).filter(k => !KIT_NOTES(k).some(n => busy.has(n) || (n >= 60 && n <= 64 && [60, 61, 62, 63, 64].some(m => busy.has(m)))));
        const main = cands.length ? A.pick(cands) : null, rest = cands.filter(k => k !== main), second = rest.length && A.chance(0.5) ? A.pick(rest) : null;
        // every idiomatic kit doubles the drums: the odds leave perc out; asked for by name (PARTS, a cue) it plays anyway
        const first = main || (AR.perc[0] ? (st.trip8 && AR.perc[0] === 'shaker' ? 'trip_shaker' : AR.perc[0]) : null);
        arr.perc = { on: !off && ((roll && !!main) || (forced.includes(role) && !!first)), kitsA: first ? [first] : [], kitsB: first ? [first].concat(second ? [second] : []) : [], early: A.chance(0.35) };
      } else {
        const kind = AR.double.length ? A.pick(AR.double) : null;
        arr.double = { on: on && !!kind, kind };
      }
    });
    // at most ARR_AUTO_MAX parts by the odds (each costs a lead's render time — the Deck's PLAY: RENDER start): the
    // style's most likely ones stay. Asked-for parts (o.arrange, PARTS, a cue) always play and don't count.
    const maxAuto = Number.isFinite(+o.arrangeMax) ? Math.max(0, Math.round(+o.arrangeMax)) : ARR_AUTO_MAX;
    const auto = ARR_ROLES.map((r, i) => ({ r, p: AR.p[i] || 0, i })).filter(x => arr[x.r].on && !forced.includes(x.r)).sort((a, b) => b.p - a.p || a.i - b.i);
    for (const x of auto.slice(maxAuto)) arr[x.r].on = false;
    // where each part plays: with intent — an arp entering in A2, the counter answering in B / A2, perc lifting B, the
    // doubling for the lift. Loops and beds have one section: a part the song has plays there.
    for (const role of ARR_ROLES) {
      const a = arr[role], X = P('arr:place:' + role);
      if (!a.on) continue;
      for (const sec of sections) {
        if (sec.given || sec.roles.includes(role)) continue;
        const b = sec.base, v = /\d$/.test(sec.name), has = r => sec.roles.includes(r), one = b === 'loop' || b === 'bed';
        let yes = false;
        if (role === 'arp') yes = one || b === 'B' || (b === 'A' ? v || a.early : b === 'intro' ? a.intro : b === 'C' ? X.chance(0.6) : b === 'brk' ? X.chance(0.5) : b === 'outro' ? X.chance(0.45) : false);
        else if (role === 'counter') {
          const alone = a.kind === 'second' || a.kind === 'ring' || a.kind === 'interlock';   // these stand without the lead
          if (!has('lead') && !(alone && (has('chords') || has('pad')))) continue;
          yes = one ? b === 'loop' || X.chance(0.5) : b === 'B' || (b === 'A' ? v : b === 'C' ? X.chance(0.7) : b === 'outro' ? X.chance(0.35) : b === 'intro' ? alone && X.chance(0.3) : false);
        } else if (role === 'perc') yes = one ? b === 'loop' || X.chance(0.4) : b === 'B' || (b === 'A' ? (v ? X.chance(0.7) : a.early) : b === 'C' ? X.chance(0.5) : b === 'brk' ? X.chance(0.55) : b === 'intro' ? X.chance(0.2) : b === 'outro' ? X.chance(0.3) : false);
        else if (role === 'double') {
          if (!has(a.kind === 'bass_up' ? 'bass' : 'lead')) continue;
          yes = b === 'loop' ? X.chance(0.5) : b === 'B' || (b === 'C' ? X.chance(0.5) : b === 'A' && v ? X.chance(0.35) : false);
        }
        if (yes) sec.roles.push(role);
      }
    }
    return arr;
  }
  function plan(o) {
    const seed = o.seed ?? Math.floor(Math.random() * 1e9);
    const R = rng(seed);
    const styleId = STYLES[o.style] ? o.style : R.pick(Object.keys(STYLES));
    const st = Object.assign({ id: styleId }, STYLES[styleId]);
    const mode = SCALES[o.mode] ? o.mode : R.pick(st.modes);
    const scale = SCALES[mode];
    const kq = keyOf(o.key), key = kq !== undefined ? kq : R.int(0, 11);
    const bpm = o.bpm || R.int(st.bpm[0], st.bpm[1]);
    const custom = Array.isArray(o.shape) && o.shape.length ? o.shape.filter(x => Array.isArray(x) && x[0] && +x[1] > 0) : null;
    const formId = FORMS[o.form] ? o.form : custom ? 'song' : (st.bed ? 'bed' : 'song');
    const density = Math.max(0, Math.min(1, o.density ?? 0.6));
    // a style's own family (drone, modal, folk, hymn, jazz, blues, horror, surf); 'minor' / 'major' follow the mode
    const own = PROGS[st.prog] && st.prog !== 'minor' && st.prog !== 'major' ? st.prog : null;
    const fam = own ? (MINORISH[mode] && PROGS[own + '_minor'] ? own + '_minor' : own) : (MINORISH[mode] ? 'minor' : 'major');
    // every structural choice comes from its own stream, so adding a choice never reshuffles the others
    const P = k => rng(seed * 7 + hash('plan:' + k));
    const HP = harmonyPlan(P('harm'), st, fam, o.progression, o);
    // a score cue's own layout ([name, bars, roles?]) wins; else a song picks one of the shapes
    const shape = custom ? custom.map(([n, b, r]) => [String(n), Math.round(+b), Array.isArray(r) ? r : null]) : formId === 'song' ? P('shape').pick(SONG_SHAPES) : FORMS[formId].map(([n, b]) => [n, b]);
    const sparse = density < 0.45;
    const sections = []; let bar = 0;
    const SR = P('roles');
    shape.forEach(([name, bars, given], i) => {
      const base = baseOf(name), fixed = given || (formId !== 'song' || custom ? (FORMS[formId].find(f => f[0] === name) || [])[2] : null);
      sections.push({ name, base, bar, bars, roles: fixed ? fixed.slice() : rolesFor(SR, base, name, st, sparse), given: !!given });
      bar += bars;
    });
    // per-song vocabulary picks (A / B contrast), from the style's lists
    const V = P('vocab');
    const gi = V.int(0, st.grooves.length - 1), gB = st.grooves.length > 1 && V.chance(0.6) ? (gi + V.int(1, st.grooves.length - 1)) % st.grooves.length : gi;
    const pick2 = list => { const a = V.pick(list), b = V.chance(0.55) ? V.pick(list) : a; return [a, b]; };
    const [bassA, bassB] = pick2(st.bass), [compA, compB] = pick2(st.chords), [padA, padB] = pick2(st.pad);
    const leadKind = V.pick(st.lead);
    const perc = V.chance(0.45) && (PERC_FOR[styleId] || []).length ? V.pick(PERC_FOR[styleId]) : null;
    const range = V.pick([[50, 72], [53, 76], [55, 79], [48, 70]]), spread = V.chance(0.35);
    const fills = [V.pick(st.fills || FILLS), V.pick(st.fills || FILLS)];
    // the lead's motif: a leitmotif (same in every track of that character) or the song's own
    const MR = o.motif ? rng(hash('motif:' + String(o.motif).toLowerCase())) : rng(seed * 13 + 5);
    const spec = o.motifSpec && Array.isArray(o.motifSpec.rhythm) && Array.isArray(o.motifSpec.degrees) && o.motifSpec.rhythm.length ? o.motifSpec : null;
    const motifA = spec ? spec.rhythm.map((s, i) => ({ s: Math.max(0, Math.min(31, Math.round(+s))), step: +spec.degrees[i % spec.degrees.length] || 0 })).sort((a, b) => a.s - b.s)
      : makeMotif(MR, o.motif ? 'motif' : leadKind, o.motif ? 0.6 : density), motifB = makeMotif(rng(seed * 13 + 9), leadKind, density);
    const phrases = [['M', 'S', 'M', 'C'], ['M', 'A', 'M', 'C'], ['M', '-', 'S', 'C'], ['M', 'M', 'U', 'C'], ['-', 'M', '-', 'A']];
    const phraseA = V.pick(phrases), phraseB = V.pick(phrases);
    // sound design
    const SD = P('sound');
    const want = x => x !== 'none' && x !== false;
    let textures = Array.isArray(o.textures) ? o.textures.slice(0, 2) : o.textures === 'none' ? [] : null;
    if (!textures) textures = SD.chance(0.7) ? [SD.pick(TEXTURE_FOR[styleId] || ['amb_room_tone'])] : [];
    const fxPreset = want(o.fx) ? (o.fx || SD.pick(FX_FOR[styleId] || ['fx_noise_sweep'])) : null;
    const hitPreset = want(o.hit) ? (o.hit || (SD.chance(0.6) ? SD.pick(HIT_FOR[styleId] || ['fx_impact']) : null)) : null;
    const arr = arrangePlan(P, o, st, styleId, sections, { formId, sparse, density, gi, gB, perc });
    const out = { seed, R, styleId, st, mode, scale, key, bpm, formId, density, fam, HP, sections, gi, gB, bassA, bassB, compA, compB, padA, padB, leadKind, perc, range, spread, fills,
      motifA, motifB, phraseA, phraseB, textures, fxPreset, hitPreset, motif: o.motif || null, voices: o.voices || {}, arr, arrange: o.arrange ?? null,
      soundBy: shape.some(x => x[2] && x[2].some(r => r === 'texture' || r === 'fx')) };
    // a remix (remix.js) grafts another song's material onto this plan: its harmony, sections, motif (fields of `out`)
    return typeof o.graft === 'function' ? Object.assign(out, o.graft(out) || {}) : out;
  }
  // swung eighths (st.trip8): an offbeat eighth moves to the triplet's last third; the note before it stretches to meet it
  function swing8(ns) {
    const off = BEAT / 2, push = BEAT / 6;
    return ns.map(x => {
      const pos = ((x.t % BEAT) + BEAT) % BEAT;
      if (pos === off) return Object.assign({}, x, { t: x.t + push, d: Math.max(6, x.d - push) });
      if (pos === 0 && x.d >= S16 && x.d <= off) return Object.assign({}, x, { d: Math.round(x.d * 4 / 3) });
      return x;
    });
  }
  // one role's notes for one section
  // src: the section's notes of the parts already written ({ lead, bass }) — the counter answers the lead, the
  // double copies it (both already swung, so the double is not swung again)
  function renderRole(pl, role, sec, i, harm, src) {
    if (ARR_ROLES.includes(role)) {
      const ns = renderArr(pl, role, sec, harm, src || {});
      if (!pl.st.trip8 || role === 'double') return ns;
      return role === 'perc' ? swing8(ns) : monoLine(swing8(ns));
    }
    const ns = renderRole0(pl, role, sec, i, harm);
    return pl.st.trip8 && (role === 'drums' || role === 'bass' || role === 'chords' || role === 'lead') ? swing8(ns) : ns;
  }
  function renderArr(pl, role, sec, harm, src) {
    const { st, density, formId, HP } = pl, opts = { density, bed: formId === 'bed' }, a = pl.arr[role];
    const base = sec.base, isB = base === 'B' || base === 'C', variant = /\d$/.test(sec.name), H = HP[base] || HP.A;
    const RR = rng(pl.seed * 31 + hash(role + base + (variant ? '~' : '')));
    const lvl = { intro: 0.85, outro: 0.85, brk: 0.95, B: 1.05, C: 1 }[base] || 1;
    if (role === 'counter') return genCounter(RR, st, sec, { H, kind: a.kind, range: base === 'B' && a.kind !== 'ring' ? [a.range[0] + 2, a.range[1] + 2] : a.range, lead: src.lead, unswing: !!st.trip8 }, harm, opts);
    if (role === 'arp') return genArp(RR, st, sec, { H, kind: isB ? a.kindB : a.kindA, reg: a.reg, span: a.span, legato: a.legato, accent: a.accent, gate: a.gate, lvl }, harm, opts);
    if (role === 'perc') return genPerc(RR, st, sec, { kits: isB || variant || base === 'brk' || base === 'loop' ? a.kitsB : a.kitsA, lvl: base === 'brk' ? 1.1 : lvl }, opts);
    if (role === 'double') return genDouble(RR, sec, { kind: a.kind, src: a.kind === 'bass_up' ? src.bass : src.lead });
    return [];
  }
  function renderRole0(pl, role, sec, i, harm) {
    const { st, density, formId, HP } = pl, opts = { density, bed: formId === 'bed' };
    const base = sec.base, isB = base === 'B' || base === 'C', variant = /\d$/.test(sec.name);
    const H = HP[base] || HP.A;
    const RR = rng(pl.seed * 31 + hash(role + base + (variant ? '~' : '')));
    const next = pl.sections[i + 1], nextBase = next ? next.base : (formId === 'loop' || formId === 'bed' ? 'loop' : null);
    if (role === 'drums') {
      const thin = base === 'brk' ? RR.pick(['perc', 'half']) : base === 'intro' ? 'perc' : base === 'outro' ? 'half' : base === 'C' && RR.chance(0.5) ? 'half' : null;
      const groove = st.grooves[isB ? pl.gB : pl.gi];
      return genDrums(RR, st, sec, { groove, thin, perc: isB || variant ? pl.perc : (RR.chance(0.5) ? pl.perc : null), fill: pl.fills[isB ? 1 : 0], crash: (isB || variant) && formId === 'song' }, opts);
    }
    if (role === 'bass') {
      const kickSteps = STEPS((st.grooves[isB ? pl.gB : pl.gi].kick) || '1000000010000000');
      const fig = base === 'intro' || base === 'outro' || base === 'brk' ? (RR.chance(0.5) ? 'root_whole' : 'root_half') : isB ? pl.bassB : pl.bassA;
      return genBass(RR, st, sec, { H, fig, kickSteps }, harm, opts);
    }
    if (role === 'chords') return genChords(RR, st, sec, { H, fig: base === 'intro' || base === 'outro' ? 'pad' : isB ? pl.compB : pl.compA, range: pl.range, spread: pl.spread }, harm, opts);
    if (role === 'lead') {
      const motif = base === 'B' || (base === 'C' && !pl.motif) ? pl.motifB : pl.motifA;
      const phrase = base === 'intro' || base === 'outro' ? ['M', '-', '-', '-'] : isB ? pl.phraseB : pl.phraseA;
      return genLead(RR, st, sec, { H, motif, phrase, kind: pl.leadKind, range: [62, 84], lift: base === 'B' ? RR.pick([2, 3, 4]) : base === 'C' ? -2 : 0 }, harm, opts);
    }
    if (role === 'pad') return genPad(RR, st, sec, { H, fig: isB ? pl.padB : pl.padA }, harm, opts);
    if (role === 'texture' || role === 'texture2') return genTexture(RR, sec, { gain: role === 'texture2' ? 0.75 : 1 });
    if (role === 'fx') {
      const into = nextBase === 'B' || nextBase === 'C' || ((formId === 'loop' || formId === 'bed') && !next) ? 'up' : nextBase === 'brk' || nextBase === 'outro' ? 'down' : null;
      return genFx(RR, sec, { into, short: /whoosh|tape_stop/.test(pl.fxPreset || '') });
    }
    if (role === 'hit') return genHit(RR, sec, { on0: (base === 'B' || base === 'C') && formId === 'song' });
    return [];
  }
  function song(o = {}) {
    const pl = plan(o), { seed, st, styleId, mode, key, scale, bpm, formId, density, sections } = pl;
    const harm = { key, scale, prevVoicing: null };
    const parts = {};
    const linked = r => st.link && st.link[r] && pl.voices[st.link[r]];      // solo piano: the hands follow the chords' instrument
    for (const role of ROLES) parts[role] = { role, patterns: {}, clips: [], preset: pl.voices[role] || linked(role) || presetFor(styleId, role, seed) };
    // arrangement parts: only the ones some section plays (perc plays on a KIT, like the drums)
    for (const role of ARR_ROLES) if (sections.some(sec => sec.roles.includes(role))) parts[role] = { role, patterns: {}, clips: [], preset: pl.voices[role] || linked(role) || presetFor(styleId, role, seed) };
    // sound design parts (texture / texture2 → one 'texture' stem; fx + hit → one 'fx' stem)
    if (pl.textures[0]) parts.texture = { role: 'texture', patterns: {}, clips: [], preset: pl.textures[0], sound: true };
    if (pl.textures[1]) parts.texture2 = { role: 'texture', patterns: {}, clips: [], preset: pl.textures[1], sound: true };
    if (pl.fxPreset) parts.fx = { role: 'fx', patterns: {}, clips: [], preset: pl.fxPreset, sound: true };
    if (pl.hitPreset) parts.hit = { role: 'fx', patterns: {}, clips: [], preset: pl.hitPreset, sound: true };
    sections.forEach((sec, i) => {
      // the sound layer plays everywhere — unless a cue's layout places it ('texture' / 'fx' in a section's roles)
      const snd = Object.keys(parts).filter(k => parts[k].sound && (!pl.soundBy || sec.roles.includes(parts[k].role)));
      const roles = sec.roles.concat(snd);
      for (const role of Object.keys(parts)) {
        if (!roles.includes(role)) continue;
        const notes = renderRole(pl, role, sec, i, harm, srcOf(parts, sec));
        if (!notes.length) continue;
        const pid = role + '_' + sec.name;
        parts[role].patterns[pid] = { name: role + ' ' + sec.name, lenBars: sec.bars, notes: sortNotes(clampLen(notes, sec.bars)) };
        parts[role].clips.push({ bar: sec.bar, pid });
      }
    });
    const A = pl.HP.A;
    return {
      v: 2, seed, style: styleId, styleName: st.name, key, keyName: NOTE_NAMES[key], mode, bpm, swing: st.swing, form: formId, density,
      progression: A.prog, progressionText: A.prog.map(d => romanFor(d, mode)).join(' – ') + (A.hr !== 1 ? ' (' + (A.hr < 1 ? 'two per bar' : A.hr + ' bars each') + ')' : ''),
      sections: sections.map(({ name, bar, bars }) => ({ name, bar, bars })), bars: sections.reduce((n, s) => n + s.bars, 0), parts,
      motif: pl.motif, textures: pl.textures, fx: pl.fxPreset, hit: pl.hitPreset,
      vocab: { groove: [pl.gi, pl.gB], bass: [pl.bassA, pl.bassB], chords: [pl.compA, pl.compB], pad: [pl.padA, pl.padB], lead: pl.leadKind, perc: pl.perc, fills: pl.fills, ext: [A.ext, pl.HP.B.ext], hr: [A.hr, pl.HP.B.hr],
        arrange: arrVocab(pl, parts) },
      arrange: pl.arrange,
      harmony: Object.fromEntries(Object.entries(pl.HP).map(([k, h]) => [k, { prog: h.prog, hr: h.hr, ext: h.ext }])),
    };
  }
  // the chord tones (pitch classes) under tick `t` of a section of a song() result
  function chordTonesAt(s, secName, t) {
    const H = (s.harmony || {})[baseOf(secName)] || (s.harmony || {}).A; if (!H) return [];
    return chordPcsOf(s.key, SCALES[s.mode], chordAt(H, Math.floor(t / BAR), (t % BAR) / BEAT));
  }
  // the lead / bass notes of one section, for the parts that follow them (counter, double)
  const srcOf = (parts, sec) => ({ lead: ((parts.lead && parts.lead.patterns['lead_' + sec.name]) || {}).notes || [], bass: ((parts.bass && parts.bass.patterns['bass_' + sec.name]) || {}).notes || [] });
  // what the arrangement parts play (null = not in this song): the song's vocab, saved with every take
  function arrVocab(pl, parts) {
    const a = pl.arr, has = r => !!(parts[r] && parts[r].clips.length);
    return { counter: has('counter') ? a.counter.kind : null, arp: has('arp') ? [a.arp.kindA, a.arp.kindB, a.arp.reg] : null, perc: has('perc') ? a.perc.kitsB : null, double: has('double') ? a.double.kind : null };
  }
  // re-roll one role in place: the same plan (structure, harmony, picks), that role's note dice re-seeded
  function part(role, s, o = {}) {
    const seed = o.seed ?? Math.floor(Math.random() * 1e9);
    const pl = plan({ seed: s.seed, style: s.style, key: s.key, mode: s.mode, bpm: s.bpm, form: s.form, density: o.density ?? s.density, progression: s.progression, motif: s.motif,
      textures: s.textures && s.textures.length ? s.textures : 'none', fx: s.fx || 'none', hit: s.hit || 'none', arrange: s.arrange ?? undefined });
    const pl2 = Object.assign({}, pl, { seed });                // new note dice, same structure
    if (role === 'lead') { pl2.motifA = s.motif ? pl.motifA : makeMotif(rng(seed * 13 + 5), pl.leadKind, pl.density); pl2.motifB = makeMotif(rng(seed * 13 + 9), pl.leadKind, pl.density); }
    const harm = { key: pl.key, scale: pl.scale, prevVoicing: null };
    const prev = s.parts[role] || {};
    const p = { role: prev.role || role, patterns: {}, clips: [], preset: prev.preset || presetFor(pl.styleId, role, s.seed) };
    if (prev.sound) p.sound = true;
    pl.sections.forEach((sec, i) => {
      if (!sec.roles.includes(role) && !p.sound) return;
      const notes = renderRole(pl2, role, sec, i, harm, srcOf(s.parts, sec));
      if (!notes.length) return;
      const pid = role + '_' + sec.name;
      p.patterns[pid] = { name: role + ' ' + sec.name, lenBars: sec.bars, notes: sortNotes(clampLen(notes, sec.bars)) };
      p.clips.push({ bar: sec.bar, pid });
    });
    return p;
  }

  // nothing rings past its own pattern (clips butt up against each other)
  function clampLen(ns, bars) { const end = bars * BAR; return ns.filter(x => x.t >= 0 && x.t < end && x.n >= 0 && x.n <= 127).map(x => (x.t + x.d > end ? Object.assign({}, x, { d: end - x.t }) : x)); }
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
  function romanFor(deg, mode) {
    const R = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII'];
    const sc = SCALES[mode];
    const third = (sc[(deg + 2) % 7] - sc[deg % 7] + 12) % 12;
    const r = R[deg % 7];
    return third === 3 ? r.toLowerCase() : r;
  }

  // ── mood from a catalog brief ───────────────────────────────────
  // ties go to the first entry. Genre words name the music outright, so they come first (a "hymn" by a kitchen stove is a
  // hymn); among the scene words ambient beds lead, as they are what most game cues need. Words match as substrings:
  // keep them specific ('dub ' not 'dub' — "dubious").
  const MOODS = [
    { words: ['hymn', 'chorale', 'church organ', 'pipe organ', 'congregation', 'chapel', 'sunday service'], style: 'hymn', form: 'loop' },
    { words: ['lullaby', 'music box', 'nursery', 'cradle', 'bedtime'], style: 'lullaby', form: 'loop' },
    { words: ['banjo', 'fiddle', 'folk song', 'folk tune', 'americana', 'acoustic guitar', 'fingerpick', 'bluegrass', 'hayride'], style: 'folk', form: 'loop' },
    { words: ['jazz', 'brushes', 'upright bass', 'walking bass', 'bebop', 'piano trio', 'supper club'], style: 'jazz', form: 'loop' },
    { words: ['swamp', 'zydeco', 'bayou', 'accordion', 'cajun', 'lake charles', 'washboard'], style: 'bayou', form: 'loop' },
    { words: ['chiptune', '8-bit', 'arcade', 'game boy', 'pixel'], style: 'chiptune', form: 'loop' },
    { words: ['synth horror', 'carpenter', 'slasher', '80s horror'], style: 'synth_horror', form: 'loop' },
    { words: ['reggae', 'dub ', 'dub.', 'dub,', 'dubwise', 'melodica', 'riddim'], style: 'dub', form: 'loop' },
    { words: ['surf rock', 'surf guitar', 'twang', 'spring reverb'], style: 'surf', form: 'loop' },
    { words: ['industrial', 'factory', 'machine shop', 'foundry', 'sawmill', 'steel mill', 'assembly line', 'clanking'], style: 'industrial', form: 'loop' },
    { words: ['string quartet', 'chamber music', 'chamber strings', 'quartet', 'cello', 'violin'], style: 'chamber', form: 'loop' },
    { words: ['solo piano', 'lone piano', 'piano alone', 'after-hours piano', 'nocturne', 'parlor piano'], style: 'piano', form: 'loop' },
    { words: ['dark drone', 'rumble', 'abyss', 'subterranean', 'mine shaft', 'catacomb'], style: 'dark_drone', form: 'bed' },
    { words: ['minimalist', 'phasing', 'ostinato', 'clockwork', 'interlocking'], style: 'minimal', form: 'loop' },
    { words: ['post-rock', 'post rock', 'tremolo-picked', 'slow build', 'crescendo'], style: 'post_rock', form: 'loop' },
    { words: ['trip-hop', 'trip hop', 'downtempo', 'breakbeat'], style: 'trip_hop', form: 'loop' },
    { words: ['drone', 'ambient', 'hum', 'substation', 'cathedral', 'hospital', 'waiting', 'liminal', 'dust', 'wind', 'tide', 'marina', 'bluff', 'field', 'cicada', 'stove', 'interior', 'long sleep'], style: 'ambient', form: 'bed' },
    { words: ['club', 'thump', 'dance', 'rave', 'warehouse party'], style: 'four_floor', form: 'loop' },
    { words: ['chillwave', 'vhs', 'neon', 'synth', 'arcade', 'render'], style: 'synthwave', form: 'loop' },
    { words: ['diner', 'jukebox', 'saturday', 'bar', 'roadhouse', 'band', 'porch', 'iced tea', 'garage'], style: 'shuffle', form: 'loop' },
    { words: ['noir', 'night shift', 'office', 'closing', 'detective', 'smoke', 'standoff', 'five am', '3:02'], style: 'noir', form: 'loop' },
    { words: ['notebook', 'tuesday', 'grind', 'study', 'kitchen', 'morning', 'apartment', 'rain'], style: 'lofi', form: 'loop' },
    { words: ['chase', 'tense', 'drive', 'service road', 'storm', 'highway'], style: 'motorik', form: 'loop' },
    { words: ['demon', 'weighing', 'judgement', 'tower', 'sinkhole'], style: 'trap', form: 'loop' },
  ];
  // Mode by TONE words (weighted), style by SCENE words, tempo by pace words. The brief decides;
  // the track id seeds the dice so the same catalog entry always writes the same piece.
  const TONES = [
    { mode: 'phrygian', w: ['stranger', 'uncanny', "doesn't quite", 'wrong', 'mirror', 'menace', 'threat', 'demon', 'sinkhole', 'weighing', 'judgement', 'underworld'] },
    { mode: 'minor', w: ['dark', 'basement', 'night', 'rain', 'alone', 'grave', 'cemetery', 'empty', 'loss', 'leaving', 'no clock', 'cold', 'hospital', 'storm', 'low '] },
    { mode: 'dorian', w: ['warm', 'echo', 'groove', 'smoke', 'cool', 'amp', 'bass', 'drive', 'headlights', 'club', 'loud'] },
    { mode: 'lydian', w: ['dream', 'painting', 'wonder', 'float', 'room behind', 'sky', 'shimmer', 'glow', 'oil-tone'] },
    { mode: 'mixolydian', w: ['road', 'juke', 'porch', 'saturday', 'band', 'diner'] },
    { mode: 'major', w: ['resolved', 'released', 'breath', 'morning', 'family', 'sun', 'home', 'iced tea', 'credits', 'warm pad'] },
  ];
  // ── sound words: what a catalog description asks to hear → ambience beds, hits, transitions, instruments ──────────
  // ("Kitchen fire crackle, distant German hymn fragment" → a fire bed + organ; "Bowed cello single note" → strings).
  // Several beds may match: the two most specific play (a generic room tone gives way).
  const SOUNDS = [
    { w: ['rain', 'drizzle', 'downpour'], tex: 'amb_rain' },
    { w: ['storm', 'thunder', 'lightning'], tex: 'amb_thunder' },
    { w: ['owl', 'pine', 'forest', 'woods', 'trees'], tex: 'amb_forest_night' },
    { w: ['wind', 'gust', 'breeze', 'rest stop'], tex: 'amb_wind' },
    { w: ['cicada'], tex: 'amb_cicadas' },
    { w: ['cricket', 'night field'], tex: 'amb_crickets' },
    { w: ['surf', 'tide', 'shore', 'waves', 'marina', 'ocean', 'beach', 'bluff', 'harbor', 'harbour'], tex: 'amb_surf' },
    { w: ['fire', 'crackle', 'hearth', 'stove', 'campfire'], tex: 'amb_fire' },
    { w: ['static', 'radio', 'transmission'], tex: 'amb_radio' },
    { w: ['hiss', 'cassette', 'tape', 'reel', 'recording'], tex: 'amb_tape_hiss' },
    { w: ['vinyl', 'record player', 'jukebox', 'needle'], tex: 'amb_vinyl' },
    { w: ['fluorescent', 'ballast', 'crt', '60 hz', 'buzz', 'neon'], tex: 'amb_fluor_hum' },
    { w: ['life support', 'station omega', 'deep space', 'airlock', 'vacuum', 'decompression', 'hull', 'robot'], tex: 'amb_life_support' },
    { w: ['engine', 'idling', 'motor', 'bus', 'canopy fans', 'generator', 'pump'], tex: 'drone_engine' },
    { w: ['city', 'traffic', 'street', 'five am', 'downtown', 'depot'], tex: 'amb_city' },
    { w: ['clock', 'ticking', 'waiting room'], tex: 'amb_clock' },
    { w: ['modem', 'dial-up', 'bbs', 'handshake', 'sysop'], tex: 'amb_modem' },
    { w: ['room', 'interior', 'apartment', 'house', 'kitchen', 'bedroom', 'office', 'diner', 'store'], tex: 'amb_room_tone' },
    { w: ['bell', 'chime', 'ding'], hit: 'fx_bell_hit' },
    { w: ['knock', 'wood-block', 'woodblock', 'wood block', 'door', 'clasp'], hit: 'fx_wood_knock' },
    { w: ['glass', 'bottle', 'clink', 'thermos', 'ping'], hit: 'fx_glass_ping' },
    { w: ['sinkhole', 'collapse', 'impact', 'demon'], hit: 'fx_sub_drop' },
    { w: ['headlights', 'rush', 'chase', 'build'], fx: 'fx_riser' },
    { w: ['tape stop', 'winding down', 'call drops', 'hollow', 'going hollow'], fx: 'fx_tape_stop' },
    { w: ['echo', 'reverse', 'dream', 'memory', 'flashback', 'from another room'], fx: 'fx_reverse_swell' },
    { w: ['cello', 'double-bass', 'double bass', 'bowed', 'violin', 'strings'], voice: { lead: 'strings_noir', pad: 'strings_tremolo' } },
    { w: ['piano', 'upright'], voice: { chords: 'keys_felt', lead: 'keys_felt' } },
    { w: ['guitar', 'strummed', 'acoustic'], voice: { chords: 'pluck_nylon', lead: 'pluck_nylon' } },
    { w: ['dobro', 'slide guitar'], voice: { lead: 'pluck_dobro' } },
    { w: ['brass', 'horn', 'trumpet'], voice: { lead: 'winds_brass' } },
    { w: ['sax'], voice: { lead: 'winds_sax' } },
    { w: ['harmonica'], voice: { lead: 'winds_harmonica' } },
    { w: ['flute', 'whistle'], voice: { lead: 'winds_flute' } },
    { w: ['clarinet'], voice: { lead: 'winds_clarinet' } },
    { w: ['organ', 'hymn'], voice: { chords: 'keys_organ', pad: 'pad_organ_swell' } },
    { w: ['humming', 'choir', 'vocal', 'voice-tone', 'singing', 'voice'], voice: { pad: 'choir_vox', lead: 'choir_angel' } },
    { w: ['music box', 'lullaby'], voice: { lead: 'bell_music_box' } },
    { w: ['glockenspiel'], voice: { lead: 'bell_glock' } },
    { w: ['vibraphone', 'vibes'], voice: { lead: 'keys_vibes' } },
    { w: ['harp'], voice: { lead: 'pluck_harp' } },
    { w: ['theremin'], voice: { lead: 'lead_theremin' } },
    { w: ['resonator', 'metallic'], voice: { lead: 'lead_ring', pad: 'pad_bowed_metal' } },
    { w: ['low sine', 'sine'], voice: { bass: 'bass_sub' } },
    { w: ['electric piano', 'rhodes', 'wurlitzer'], voice: { chords: 'keys_ep' } },
    { w: ['808'], voice: { bass: 'bass_808' } },
  ];
  const hasWord = (s, w) => new RegExp('(^|[^a-z])' + w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).test(s);
  function soundsFromText(text) {
    const s = String(text || '').toLowerCase(), out = { textures: [], voices: {}, hit: null, fx: null, words: [] };
    if (/no field-recording|no field recording|no texture/.test(s)) { out.textures = 'none'; return out; }
    for (const e of SOUNDS) {
      const w = e.w.find(x => hasWord(s, x)); if (!w) continue;
      out.words.push(w);
      if (e.tex && !out.textures.includes(e.tex)) out.textures.push(e.tex);
      if (e.hit && !out.hit) out.hit = e.hit;
      if (e.fx && !out.fx) out.fx = e.fx;
      if (e.voice) for (const [r, p] of Object.entries(e.voice)) if (!out.voices[r]) out.voices[r] = p;
    }
    if (out.textures.length > 1) out.textures = out.textures.filter(t => t !== 'amb_room_tone');
    out.textures = out.textures.slice(0, 2);
    return out;
  }
  // the character a track belongs to (its leitmotif): vol5_alberto_theme → alberto; the title / credits pair share 'title'
  function motifOf(id) {
    const m = /^vol\d+_([a-z_]+?)_theme/.exec(id || '');
    if (m) return m[1];
    return /^(title|credits)_theme$/.test(id || '') ? 'title' : null;
  }
  // a volume's tonal home: its tracks sit on that tonic or a close neighbour (fifth, fourth, relative) — one soundtrack
  function volumeKey(vol, id) {
    if (vol === undefined || vol === null) return undefined;
    const home = hash('volume-key:' + vol) % 12, step = [0, 0, 0, 7, 5, 9][hash('key:' + id) % 6];
    return (home + step) % 12;
  }

  // a key as a pitch class: 0–11, or a name ('D', 'Eb', 'F#', 'Bbm' → the tonic only)
  const FLATS = { Db: 1, Eb: 3, Gb: 6, Ab: 8, Bb: 10, Cb: 11, Fb: 4 };
  function keyOf(k) {
    if (k === undefined || k === null || k === '') return undefined;
    if (Number.isFinite(+k)) return ((Math.round(+k) % 12) + 12) % 12;
    const m = /^\s*([A-Ga-g])([#b]?)/.exec(String(k)); if (!m) return undefined;
    const name = m[1].toUpperCase() + m[2];
    if (FLATS[name] !== undefined) return FLATS[name];
    const i = NOTE_NAMES.indexOf(name); if (i >= 0) return i;
    return ((NOTE_NAMES.indexOf(m[1].toUpperCase()) + (m[2] === '#' ? 1 : 0)) % 12 + 12) % 12;
  }

  // ── the score bible (resources/music/score/*.json) ──────────────────────────────────────────────────────────────
  // Written musical direction, layered: soundtrack → volume → chapter → character (motif, signature instrument) →
  // track cue. Each layer may set: style, form, mode, key, bpm, density (a value or a list / [lo, hi] — picked per
  // seed), voices {role: preset | [presets]}, textures [..] | 'none', fx, hit, motif, motifSpec {rhythm, degrees},
  // shape [[name, bars, roles]], stems, feel (prose). Later layers win field by field; typed direction wins over all
  // of them (applyDirection after this).
  const chapterOf = sceneId => (/^(vol\d+_ch\d+)/.exec(sceneId || '') || [])[1] || null;
  function applyScore(m, score, t) {
    if (!score || !t) return m;
    const R = rng(hash('score:' + t.id + ':' + (m.seed || 0)));
    const pickOne = v => Array.isArray(v) ? (v.length === 2 && v.every(x => typeof x === 'number') ? v[0] + R() * (v[1] - v[0]) : R.pick(v)) : v;
    const chapters = [...new Set((t.chapters || []).map(chapterOf).filter(Boolean))];
    // a track the scenes play in several chapters: each take leans toward one of them (the ones the score describes),
    // so takes differ the way those chapters do
    const described = chapters.filter(c => (score.chapters || {})[c]), chap = described.length ? described[R.int(0, described.length - 1)] : null;
    if (chap) m.chapter = chap;
    const layers = [score.soundtrack, (score.volumes || {})[String(t.vol)], chap && (score.chapters || {})[chap], (score.tracks || {})[t.id]].filter(Boolean);
    const feel = [];
    const take = L => {
      if (L.style && STYLES[pickOne(L.style)] !== undefined) m.style = pickOne(L.style);
      for (const k of ['form', 'mode']) if (L[k]) { const v = pickOne(L[k]); if ((k === 'form' ? FORMS : SCALES)[v]) m[k] = v; }
      if (L.key !== undefined) { const k = keyOf(pickOne(L.key)); if (k !== undefined) m.key = k; }
      if (L.bpm !== undefined) m.bpm = Math.round(pickOne(L.bpm));
      if (L.density !== undefined) m.density = +Math.max(0.05, Math.min(1, pickOne(L.density))).toFixed(2);
      if (L.voices) { m.voices = Object.assign({}, m.voices || {}); for (const [r, v] of Object.entries(L.voices)) m.voices[r] = pickOne(v); }
      if (L.textures !== undefined) m.textures = L.textures === 'none' ? 'none' : (Array.isArray(L.textures) ? (L.textures.length > 2 ? [R.pick(L.textures), R.pick(L.textures)].filter((x, i, a) => a.indexOf(x) === i) : L.textures.slice()) : [L.textures]);
      for (const k of ['fx', 'hit']) if (L[k] !== undefined) m[k] = pickOne(L[k]);
      if (L.motif !== undefined) m.motif = L.motif || null;
      if (L.shape) m.shape = L.shape;
      if (L.stems !== undefined) m.stems = !!L.stems;
      if (L.feel) feel.push(String(L.feel));
    };
    for (const L of layers) take(L);
    // the character whose motif this is: the motif's own shape, their signature instrument (unless the cue names one)
    const ch = m.motif && (score.characters || {})[String(m.motif).toLowerCase()];
    if (ch) {
      if (ch.motifSpec) m.motifSpec = ch.motifSpec;
      const cue = (score.tracks || {})[t.id] || {};
      if (ch.instrument && !(cue.voices && cue.voices.lead)) m.voices = Object.assign({}, m.voices || {}, { lead: pickOne(ch.instrument) });
      if (ch.mode && !cue.mode && SCALES[ch.mode] && /_theme$/.test(t.id)) m.mode = ch.mode;
      if (ch.feel) feel.push(String(ch.feel));
    }
    if (layers.length || ch) { m.scored = true; m.why = (m.why ? m.why + ' · ' : '') + 'score' + (feel.length ? ': ' + feel[feel.length - 1].slice(0, 70) : ''); }
    return m;
  }
  // the roles a cue's shape may place (texture / fx: the sound layer) and the roles `voices` may name
  const SHAPE_ROLES = ROLES.concat(ARR_ROLES, ['texture', 'fx']), PART_ROLES = SHAPE_ROLES.concat(['texture2', 'hit']);
  // the score's referential integrity — styles, modes, keys, presets (FORGE or a known fallback), catalog ids, roles
  function checkScore(score, { catalog = [], presets = [] } = {}) {
    const bad = [], ids = new Set(catalog.map(t => t.id)), P = new Set(presets), okPreset = v => v === 'none' || v === 'kit' || P.has(v) || (/^patch:/.test(v)) || SOUND_FALLBACK[v] !== undefined;
    const arr = v => (Array.isArray(v) ? v : [v]);
    const layer = (where, L) => {
      if (!L || typeof L !== 'object') return;
      if (L.style) for (const s of arr(L.style)) if (!STYLES[s]) bad.push(where + ': style ' + s);
      if (L.mode) for (const s of arr(L.mode)) if (!SCALES[s]) bad.push(where + ': mode ' + s);
      if (L.form) for (const s of arr(L.form)) if (!FORMS[s]) bad.push(where + ': form ' + s);
      if (L.key !== undefined) for (const k of arr(L.key)) if (keyOf(k) === undefined) bad.push(where + ': key ' + k);
      for (const [r, v] of Object.entries(L.voices || {})) { if (!PART_ROLES.includes(r)) bad.push(where + ': voices role ' + r); for (const x of arr(v)) if (!okPreset(x)) bad.push(where + ': voice ' + r + ' ' + x); }
      if (L.textures && L.textures !== 'none') for (const x of arr(L.textures)) if (!okPreset(x)) bad.push(where + ': texture ' + x);
      for (const k of ['fx', 'hit']) if (L[k]) for (const x of arr(L[k])) if (!okPreset(x)) bad.push(where + ': ' + k + ' ' + x);
      if (L.instrument) for (const x of arr(L.instrument)) if (!okPreset(x)) bad.push(where + ': instrument ' + x);
      if (L.shape) for (const sec of L.shape) {
        if (!Array.isArray(sec) || !sec[0] || !(+sec[1] > 0)) bad.push(where + ': shape ' + JSON.stringify(sec));
        else if (sec[2] !== undefined && sec[2] !== null) for (const r of arr(sec[2])) if (!SHAPE_ROLES.includes(r)) bad.push(where + ': shape ' + sec[0] + ' role ' + r);
      }
      if (L.motifSpec && !(Array.isArray(L.motifSpec.rhythm) && Array.isArray(L.motifSpec.degrees))) bad.push(where + ': motifSpec');
    };
    layer('soundtrack', score.soundtrack);
    for (const [k, L] of Object.entries(score.volumes || {})) layer('volume ' + k, L);
    for (const [k, L] of Object.entries(score.chapters || {})) layer('chapter ' + k, L);
    for (const [k, L] of Object.entries(score.characters || {})) layer('character ' + k, L);
    for (const [k, L] of Object.entries(score.tracks || {})) { if (ids.size && !ids.has(k)) bad.push('track ' + k + ': not in the catalog'); layer('track ' + k, L); }
    return bad;
  }

  const PACE = { slow: ['slow', 'slower', 'held', 'sustained', 'single', 'drone', 'still'], fast: ['loud', 'dancing', 'chase', 'thump', 'rush', 'headlights, then more'] };
  function moodFromText(title, desc, id) {
    const s = ((title || '') + ' ' + (desc || '') + ' ' + (id || '')).toLowerCase();
    let best = null, bestScore = 0;
    for (const m of MOODS) { const sc = m.words.reduce((n, w) => n + (s.includes(w) ? 1 : 0), 0); if (sc > bestScore) { best = m; bestScore = sc; } }
    // a character / title theme is a piece with a shape (intro → A → B → A → outro), not a bed
    const theme = /(theme|title|credits|signature|choice)/.test(s);
    let m = best || { style: theme ? 'noir' : 'ambient', form: theme ? 'song' : 'bed' };
    if (!best && /(bass swell|amp buzz|basement)/.test(s)) m = { style: 'noir', form: 'song' };
    const st = STYLES[m.style];
    const score = {};
    for (const t of TONES) score[t.mode] = t.w.reduce((n, w) => n + (s.includes(w) ? 1 : 0), 0);
    let mode = Object.keys(score).sort((a, b) => score[b] - score[a])[0];
    if (!score[mode]) mode = st.modes[0];
    else if (!SCALES[mode]) mode = st.modes[0];
    const slow = PACE.slow.some(w => s.includes(w)), fast = PACE.fast.some(w => s.includes(w));
    const [lo, hi] = st.bpm, bpm = Math.round(slow ? lo : fast ? hi : (lo + hi) / 2);
    const dark = ['phrygian', 'minor', 'harmonic'].includes(mode), bright = ['major', 'lydian', 'mixolydian'].includes(mode);
    const snd = soundsFromText(s), quiet = /(single (low )?(note|pad|figure)|quietest|held silence|no one around)/.test(s);
    const out = { style: m.style, form: theme && m.form !== 'loop' ? 'song' : m.form, mode, bpm, seed: hash(id || s), density: quiet ? 0.32 : dark ? 0.45 : bright ? 0.62 : 0.55, matched: bestScore, toneScore: score[mode] || 0 };
    if (snd.textures === 'none' || snd.textures.length) out.textures = snd.textures;
    if (snd.hit) out.hit = snd.hit;
    if (snd.fx) out.fx = snd.fx;
    if (Object.keys(snd.voices).length) out.voices = snd.voices;
    if (snd.words.length) out.sounds = snd.words;
    const motif = motifOf(id); if (motif) out.motif = motif;
    return out;
  }
  // The MusicDirector's brief for a track (resources/music/temp_briefs.json, from music_direction.py brief):
  // start from the catalog text (+ the scenes' lexicon words, locales, characters), then move tempo, density and
  // mode toward the intensity the director will actually drive in those scenes. No brief → moodFromText as is.
  function moodFromBrief(t, b, direction) {
    const m = moodFromBrief0(t, b);
    return direction && String(direction).trim() ? applyDirection(m, String(direction)) : m;
  }
  // Creative direction typed for one request ("slower, more dread, a lonely piano over rain"). It is the
  // newest word on the piece, so where it names a style, a mode, a pace or a density it overrides the
  // catalog text and the brief; where it says nothing, they stand.
  const DIRECTION = {
    modes: [
      { mode: 'phrygian', w: ['dread', 'ominous', 'sinister', 'creepy', 'eerie', 'menacing', 'horror', 'unsettling', 'wrong'] },
      { mode: 'minor', w: ['sad', 'sadder', 'lonely', 'melancholy', 'melancholic', 'grief', 'mournful', 'somber', 'sombre', 'dark', 'darker', 'bleak', 'loss'] },
      { mode: 'dorian', w: ['cool', 'groovy', 'smoky', 'bittersweet', 'wistful'] },
      { mode: 'lydian', w: ['dreamy', 'ethereal', 'magical', 'floating', 'wonder', 'shimmering'] },
      { mode: 'mixolydian', w: ['bluesy', 'rootsy', 'twangy', 'swagger'] },
      { mode: 'major', w: ['happy', 'hopeful', 'bright', 'brighter', 'uplifting', 'joyful', 'warm', 'warmer', 'triumphant', 'sunny'] },
    ],
    slow: ['slow', 'slower', 'slowly', 'calm', 'calmer', 'gentle', 'lazy', 'languid', 'still', 'stiller', 'unhurried', 'drifting'],
    fast: ['fast', 'faster', 'urgent', 'frantic', 'driving', 'upbeat', 'energetic', 'racing', 'tense', 'tenser', 'quicker'],
    sparse: ['sparse', 'sparser', 'minimal', 'bare', 'thin', 'empty', 'simple', 'simpler', 'quiet', 'quieter', 'lonely'],
    busy: ['busy', 'busier', 'dense', 'denser', 'full', 'fuller', 'lush', 'layered', 'complex', 'intricate', 'bigger'],
  };
  function applyDirection(m, text) {
    const s = text.toLowerCase(), has = w => new RegExp('(^|[^a-z])' + w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '([^a-z]|$)').test(s);
    const d = moodFromText('', text, '');
    const st0 = STYLES[m.style], pos = (m.bpm - st0.bpm[0]) / Math.max(1, st0.bpm[1] - st0.bpm[0]);
    if (d.matched && d.style !== m.style) {
      m.style = d.style;
      if (m.form !== 'song') m.form = d.form;
      const st = STYLES[m.style]; m.bpm = Math.round(st.bpm[0] + Math.max(0, Math.min(1, pos)) * (st.bpm[1] - st.bpm[0]));
    }
    let best = null, bestN = 0;
    for (const x of DIRECTION.modes) { const n = x.w.filter(has).length; if (n > bestN) { best = x.mode; bestN = n; } }
    if (best) m.mode = best;
    else if (d.toneScore && SCALES[d.mode]) m.mode = d.mode;
    const [lo, hi] = STYLES[m.style].bpm;
    const slow = DIRECTION.slow.some(has), fast = DIRECTION.fast.some(has);
    if (slow && !fast) m.bpm = lo; else if (fast && !slow) m.bpm = hi;
    const sparse = DIRECTION.sparse.some(has), busy = DIRECTION.busy.some(has);
    if (sparse && !busy) m.density = +Math.max(0.15, m.density - 0.2).toFixed(2);
    else if (busy && !sparse) m.density = +Math.min(0.95, m.density + 0.2).toFixed(2);
    // sounds named in the direction ("a lonely piano over rain") win over the catalog's
    const snd = soundsFromText(text);
    if (snd.textures === 'none' || snd.textures.length) m.textures = snd.textures;
    if (snd.hit) m.hit = snd.hit;
    if (snd.fx) m.fx = snd.fx;
    if (Object.keys(snd.voices).length) m.voices = Object.assign({}, m.voices || {}, snd.voices);
    m.direction = text.trim();
    m.why = (m.why ? m.why + ' · ' : '') + 'direction: "' + m.direction.slice(0, 60) + '"';
    return m;
  }
  function moodFromBrief0(t, b) {
    const m = moodFromText(t.title, t.desc, t.id);
    const k = volumeKey(t.vol, t.id); if (k !== undefined) m.key = k;
    const sounds = m.sounds ? ' · hears: ' + m.sounds.slice(0, 5).join(', ') : '';
    if (!b || !b.intensity) return Object.assign(m, { why: 'catalog text' + sounds + (m.motif ? ' · motif: ' + m.motif : '') });
    // the catalog text was written for this track: it decides style / mode; the scenes' words only fill a blank
    if (!m.matched || !m.toneScore) {
      const extra = [(b.words || []).join(' '), (b.locales || []).join(' ')].join(' ');
      const w = moodFromText(t.title, (t.desc || '') + ' ' + extra, t.id);
      if (!m.matched && w.matched) { m.style = w.style; m.form = w.form; m.bpm = w.bpm; }
      if (!m.toneScore && w.toneScore && SCALES[w.mode]) m.mode = w.mode;
    }
    // energy / darkness: this track's scenes ranked against the game's other music (0..1, 0.5 = typical)
    const st = STYLES[m.style], e = b.energy ?? 0.5, dk = b.darkness ?? 0.5;
    const [lo, hi] = st.bpm, span = hi - lo;
    m.bpm = Math.round(Math.max(lo, Math.min(hi, m.bpm + (e - 0.5) * span)));
    m.density = +Math.max(0.25, Math.min(0.85, m.density + (e - 0.5) * 0.4)).toFixed(2);
    if (dk >= 0.8 && !MINORISH[m.mode]) m.mode = dk >= 0.95 ? 'phrygian' : 'minor';
    else if (dk <= 0.2 && (m.mode === 'phrygian' || m.mode === 'harmonic')) m.mode = 'dorian';
    const roles = b.roles || {}, lead = Object.keys(roles).sort((x, y) => roles[y] - roles[x])[0];
    if (lead === 'leitmotif') m.form = 'song';                                // a character's theme has a shape
    m.stems = !!b.stems;
    // a track the scenes play under one character carries that character's motif (cohesion across the soundtrack)
    if (!m.motif && lead === 'leitmotif' && (b.chars || []).length) m.motif = String(b.chars[0]).toLowerCase();
    m.why = b.scene_count + ' scene' + (b.scene_count === 1 ? '' : 's') + ' · ' + Object.entries(roles).map(([k, v]) => k + ' ' + v).join(', ') +
      ' · energy ' + Math.round(e * 100) + '% · dark ' + Math.round(dk * 100) + '%' + (m.stems ? ' · stems' : '') + sounds + (m.motif ? ' · motif: ' + m.motif : '');
    return m;
  }

  const API = { PPQ, BAR, S16, GM, SCALES, STYLES, FORMS, PROGS, NOTE_NAMES, FORGE_POOLS, SONG_SHAPES, SOUNDS, SOUND_FALLBACK, TEXTURE_FOR, FX_FOR, HIT_FOR, PERC_FOR, rng, hash, deg2midi, chordPCs, song, part, presetFor,
    ROLES, ARR_ROLES, SHAPE_ROLES, ARRANGE, PERC_KITS, chordTonesAt,
    moodFromText, moodFromBrief, applyDirection, romanFor, soundsFromText, motifOf, volumeKey, keyOf, applyScore, checkScore, chapterOf };
  API.plan = plan;                                           // remix.js: a song's plan without its notes
  if (typeof module !== 'undefined' && module.exports) module.exports = API;
  root.SeqGen = API;
})(typeof window !== 'undefined' ? window : globalThis);
