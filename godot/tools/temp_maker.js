/* temp_maker.js — compose, render and stage TEMP TRACK takes without the DAW's UI.
 *
 * One pipeline for both pages: the AUDIO DIRECTOR makes takes itself (MAKE TAKES → listen → APPROVE, no DAW tab), and
 * the DAW's TEMP TRACKS panel calls the same functions. Needs the DAW engine scripts on the page (seqgen.js,
 * forge_synth.js, sampler.js, dx7_synth.js, patch_bank.js, daw_fx.js, daw_perf.js, daw_engine.js, audio_kit.js) and a
 * started engine: E = new DAW.Engine(); await E.start() — from a tap (the AudioContext needs a user gesture).
 *
 *   TempMaker.makeTakes(E, list, req, ctx) → [{ id, take, seed, files, … } | { id, seed, error }]
 *     list: catalog entries [{id, title, src, vol, desc, …}]; req: { takes, review, stems, opts, useBriefs }
 *     ctx: { briefs, inst ('forge'), master (true), lufs (−14), onEvent({type: 'progress' | 'take' | 'done', …}) }
 *   TempMaker.compose(E, opts, inst) → song (loads a fresh generated project into E)
 *   TempMaker.render(E, { loop, stems, master, lufs, onProgress }) → { channels, sampleRate, loop, bars, mastered, stems }
 *   writeTake / writeTempToGame / seedsUsed / normOpts / takeMood / arrangeTo / shapeArrangement / stemGroups …
 *   req.opts (normOpts): description, style, mode, form, bpm, key (0–11 | 'home'), energy, density, length, loop, roles,
 *     extraPads, instruments {role: kit[:style] | forge:… | patch:…}, seed, ensemble (ENSEMBLES), variety (close | wide |
 *     wild; mixed = absent), feel (FEELS), harmony (HARMONY), prog (a SeqGen.PROGS family), textures ([≤2] | 'none'),
 *     fx / hit (preset | 'none'). varyTake applies the per-take ones; meta.mood records what each take got.
 *
 * Review staging: assets/audio/review/<track id>/<take id>/ mix.wav · stems/<role>.wav · stems.json · credits.txt · meta.json
 */
(function (root) {
  'use strict';
  // audio_kit.js declares AK with a top-level const (not a window property): reach it lexically
  const SG = () => root.SeqGen, AKg = () => (typeof AK !== 'undefined' ? AK : root.AK);
  const BAR = () => root.DAW.BAR;

  // the five-piece band, then the arrangement parts (seqgen ARR_ROLES): perc (hand percussion, on a KIT), arp (an
  // ostinato), counter (a countermelody) and double (the lead / bass in octaves for lift) — appended, so older takes'
  // tracks keep their order
  const ARR_ROLES = ['perc', 'arp', 'counter', 'double'];
  const ROLE_ORDER = ['drums', 'bass', 'chords', 'lead', 'pad'].concat(ARR_ROLES);
  // the sound-design layer seqgen.js writes: ambience beds (texture, texture2 → one 'texture' stem) · transitions + hits (→ 'fx')
  const SOUND_PARTS = ['texture', 'texture2', 'fx', 'hit'], SOUND_ROLES = ['texture', 'fx'], ALL_ROLES = ROLE_ORDER.concat(SOUND_ROLES);
  // starting balance: the arrangement parts sit under the lead (arp / counter / double well under it — they must not mask it)
  const ROLE_LEVEL = { drums: 0.62, bass: 0.6, chords: 0.42, lead: 0.42, pad: 0.36, perc: 0.38, arp: 0.24, counter: 0.28, double: 0.24, texture: 0.3, texture2: 0.24, fx: 0.4, hit: 0.42 };
  const ROLE_VEL = { drums: 1, bass: 0.95, chords: 0.75, lead: 0.85, pad: 0.7, perc: 0.85, arp: 0.6, counter: 0.65, double: 0.6 };
  const COLORS = { drums: '#e08a7a', bass: '#c87633', chords: '#d8a060', lead: '#a8e89c', pad: '#8ab4f0', perc: '#e0b07a', arp: '#7ad8c8', counter: '#d4e87a', double: '#b4c8f0',
    audio: '#c8a4f0', midi: '#f0b94a' };
  // the game's intensity layers per stem (AudioMgr: pad / chords always, bass from 0.25, hand percussion 0.4, drums + the
  // arp 0.5, lead + its counter 0.75, the doubling only at the top (0.9: choices, reveals))
  const STEM_LAYER = { pad: 0, chords: 0, bass: 0.25, perc: 0.4, drums: 0.5, arp: 0.5, lead: 0.75, counter: 0.75, double: 0.9, texture: 0, fx: 0.5 };
  const MONO_ROLES = ['arp', 'counter', 'double'];             // one FORGE voice each (the Deck plays these live)
  const EXTRA_PADS = ['pad2', 'pad3'];                       // texture layers: the pad an octave up · a sub drone
  const TEMP_MIN_SEC = 90;
  const REVIEW_DIR = 'assets/audio/review';
  const APPROVALS = 'resources/music/temp_approvals.json';
  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
  // SeqGen.hash (FNV-1a) + a murmur finalizer: FNV's low bits barely move between near seeds (its lowest bit is the parity
  // of the input's characters), so `hash % 2` picks the same entry for most seeds. The panel's per-take picks use this.
  const mixHash = s => { let h = SG().hash(String(s)); h = Math.imul(h ^ (h >>> 16), 0x85ebca6b); h = Math.imul(h ^ (h >>> 13), 0xc2b2ae35); return (h ^ (h >>> 16)) >>> 0; };
  // PATCH BANK picks per style — free-to-use and light: one GeneralUser GS download (32 MB) + jRhodes3d. GeneralUser ids are
  // 'gugs:<bank>.<program>' (GM program numbers from 0; bank 128 = drum kits: 0 standard, 8 room, 16 power, 24 electronic,
  // 25 TR-808, 32 jazz, 40 brush, 48 orchestra). Alternates per style and role — the track seed picks one, so two noir
  // themes don't share all five instruments. The two VSCO picks are real string / harp sections: big WAVs (~60 MB per
  // articulation) on their first download. FORGE alternates live in SeqGen.FORGE_POOLS.
  const PATCH_POOLS = {
    noir:      { drums: ['gugs:128.32', 'gugs:128.40'], bass: ['gugs:0.35', 'gugs:0.33'], chords: ['gugs:0.4', 'gugs:0.0', 'gugs:0.26', 'gugs:0.11', 'gugs:0.5'],
                 lead: ['gugs:0.66', 'gugs:0.59', 'gugs:0.71', 'gugs:0.11', 'gugs:0.65', 'gugs:0.60', 'gugs:0.68', 'vsco:celloenssusvib'],
                 pad: ['gugs:0.49', 'gugs:0.92', 'gugs:0.52', 'gugs:0.44', 'gugs:0.48', 'gugs:0.94', 'gugs:0.53', 'gugs:0.89'] },
    ambient:   { drums: ['gugs:128.40'], bass: ['gugs:0.35', 'gugs:0.42'], chords: ['gugs:0.92', 'gugs:0.4', 'gugs:0.46', 'gugs:0.88', 'gugs:0.94', 'gugs:0.19'],
                 lead: ['gugs:0.12', 'gugs:0.14', 'gugs:0.98', 'gugs:0.75', 'gugs:0.8', 'gugs:0.10', 'gugs:0.108', 'gugs:0.79', 'vsco:harp'],
                 pad: ['gugs:0.89', 'gugs:0.95', 'gugs:0.99', 'gugs:0.52', 'gugs:0.91', 'gugs:0.92', 'gugs:0.97', 'gugs:0.101', 'gugs:0.53'] },
    lofi:      { bass: ['gugs:0.33', 'gugs:0.32', 'gugs:0.35'], chords: ['gugs:0.4', 'gugs:0.0', 'gugs:0.5', 'gugs:0.11', 'gugs:0.24'],
                 lead: ['gugs:0.11', 'gugs:0.24', 'gugs:0.12', 'gugs:0.10', 'gugs:0.108', 'gugs:0.73'], pad: ['gugs:0.49', 'gugs:0.52', 'gugs:0.89', 'gugs:0.88'] },
    boom_bap:  { drums: ['gugs:128.8', 'gugs:128.0'], bass: ['gugs:0.33', 'gugs:0.32', 'gugs:0.38'], chords: ['jrhodes:st', 'gugs:0.4', 'gugs:0.5', 'gugs:0.11', 'gugs:0.7'],
                 lead: ['gugs:0.11', 'gugs:0.12', 'gugs:0.66', 'gugs:0.73', 'gugs:0.108'], pad: ['gugs:0.48', 'gugs:0.49', 'gugs:0.89'] },
    four_floor: { drums: ['gugs:128.25'], bass: ['gugs:0.39', 'gugs:0.87', 'gugs:0.38'], chords: ['gugs:0.81', 'gugs:0.95', 'gugs:0.16', 'gugs:0.61', 'gugs:0.90'],
                 lead: ['gugs:0.84', 'gugs:0.98', 'gugs:0.114', 'gugs:0.9', 'gugs:0.81'], pad: ['gugs:0.90', 'gugs:0.95', 'gugs:0.89', 'gugs:0.50'] },
    motorik:   { drums: ['gugs:128.24'], bass: ['gugs:0.38', 'gugs:0.34'], chords: ['gugs:0.90', 'gugs:0.27', 'gugs:0.16', 'gugs:0.6'],
                 lead: ['gugs:0.81', 'gugs:0.84', 'gugs:0.62', 'gugs:0.80'], pad: ['gugs:0.89', 'gugs:0.95', 'gugs:0.51', 'gugs:0.94'] },
    synthwave: { bass: ['gugs:0.39', 'gugs:0.38'], chords: ['gugs:0.81', 'gugs:0.5', 'gugs:0.88'], lead: ['gugs:0.84', 'gugs:0.86', 'gugs:0.62', 'gugs:0.81'],
                 pad: ['gugs:0.95', 'gugs:0.90', 'gugs:0.50', 'gugs:0.51', 'gugs:0.89'] },
    shuffle:   { drums: ['gugs:128.0', 'gugs:128.40'], bass: ['gugs:0.33', 'gugs:0.32'], chords: ['gugs:0.25', 'gugs:0.4', 'gugs:0.16', 'gugs:0.7', 'gugs:0.61'],
                 lead: ['gugs:0.66', 'gugs:0.22', 'gugs:0.27', 'gugs:0.65', 'gugs:0.56', 'gugs:0.114', 'gugs:0.11'], pad: ['gugs:0.17', 'gugs:0.48', 'gugs:0.61', 'gugs:0.21'] },
    trap:      { drums: ['gugs:128.25'], bass: ['gugs:0.38', 'gugs:0.39'], chords: ['gugs:0.0', 'gugs:0.10', 'gugs:0.8', 'gugs:0.88'],
                 lead: ['gugs:0.10', 'gugs:0.9', 'gugs:0.8', 'gugs:0.81', 'gugs:0.45'], pad: ['gugs:0.94', 'gugs:0.52', 'gugs:0.91', 'gugs:0.44', 'gugs:0.48'] },
    dnb:       { drums: ['gugs:128.24'], bass: ['gugs:0.39', 'gugs:0.38'], chords: ['gugs:0.89', 'gugs:0.4', 'gugs:0.95'], lead: ['gugs:0.81', 'gugs:0.84', 'gugs:0.98'],
                 pad: ['gugs:0.91', 'gugs:0.89', 'gugs:0.95', 'gugs:0.94'] },
    // the score bible's 16 genres (GM programs: 0 piano · 4 EP · 8 celesta · 10 music box · 11 vibes · 12 marimba · 14 tubular ·
    // 16–20 organs · 21 accordion · 22 harmonica · 24–30 guitars · 32–39 basses · 40–45 strings · 46 harp · 48–55 ensembles /
    // choirs · 56–63 brass · 64–79 reeds / pipes · 80–87 synth leads · 88–95 pads · 96–103 synth fx · 104–111 ethnic)
    folk:      { drums: ['gugs:128.40', 'gugs:128.32'], bass: ['gugs:0.32', 'gugs:0.33'], chords: ['gugs:0.24', 'gugs:0.25', 'gugs:0.105', 'gugs:0.46'],
                 lead: ['gugs:0.22', 'gugs:0.110', 'gugs:0.105', 'gugs:0.73', 'gugs:0.78', 'gugs:0.25'], pad: ['gugs:0.48', 'gugs:0.21', 'gugs:0.60', 'gugs:0.89'] },
    chamber:   { drums: ['gugs:128.48'], bass: ['gugs:0.43', 'gugs:0.42'], chords: ['gugs:0.48', 'gugs:0.44', 'gugs:0.45', 'gugs:0.49'],
                 lead: ['gugs:0.40', 'gugs:0.41', 'gugs:0.42', 'gugs:0.71', 'gugs:0.73', 'gugs:0.68', 'vsco:celloenssusvib'], pad: ['gugs:0.48', 'gugs:0.49', 'gugs:0.44', 'gugs:0.52'] },
    piano:     { drums: ['gugs:128.40'], bass: ['gugs:0.0', 'gugs:0.1'], chords: ['gugs:0.0', 'gugs:0.1', 'gugs:0.4', 'jrhodes:st', 'gugs:0.3'],
                 lead: ['gugs:0.0', 'gugs:0.1', 'gugs:0.8'], pad: ['gugs:0.48', 'gugs:0.89', 'gugs:0.49'] },
    hymn:      { drums: ['gugs:128.48'], bass: ['gugs:0.19', 'gugs:0.32', 'gugs:0.43'], chords: ['gugs:0.19', 'gugs:0.20', 'gugs:0.52', 'gugs:0.48', 'gugs:0.60'],
                 lead: ['gugs:0.19', 'gugs:0.52', 'gugs:0.73', 'gugs:0.60', 'gugs:0.71', 'gugs:0.53'], pad: ['gugs:0.52', 'gugs:0.53', 'gugs:0.19', 'gugs:0.91', 'gugs:0.48'] },
    dark_drone: { drums: ['gugs:128.48'], bass: ['gugs:0.38', 'gugs:0.43', 'gugs:0.35'], chords: ['gugs:0.92', 'gugs:0.93', 'gugs:0.94', 'gugs:0.44', 'gugs:0.97'],
                 lead: ['gugs:0.14', 'gugs:0.93', 'gugs:0.42', 'gugs:0.101', 'gugs:0.103'], pad: ['gugs:0.92', 'gugs:0.93', 'gugs:0.91', 'gugs:0.94', 'gugs:0.95', 'gugs:0.97'] },
    synth_horror: { drums: ['gugs:128.24', 'gugs:128.25'], bass: ['gugs:0.38', 'gugs:0.39', 'gugs:0.87'], chords: ['gugs:0.90', 'gugs:0.50', 'gugs:0.95', 'gugs:0.88'],
                 lead: ['gugs:0.81', 'gugs:0.80', 'gugs:0.84', 'gugs:0.14', 'gugs:0.103'], pad: ['gugs:0.50', 'gugs:0.95', 'gugs:0.94', 'gugs:0.91'] },
    jazz:      { drums: ['gugs:128.40', 'gugs:128.32'], bass: ['gugs:0.32', 'gugs:0.35'], chords: ['jrhodes:st', 'gugs:0.0', 'gugs:0.4', 'gugs:0.26', 'gugs:0.11'],
                 lead: ['gugs:0.66', 'gugs:0.65', 'gugs:0.59', 'gugs:0.56', 'gugs:0.11', 'gugs:0.71', 'gugs:0.73'], pad: ['gugs:0.61', 'gugs:0.48', 'gugs:0.49', 'gugs:0.89'] },
    dub:       { drums: ['gugs:128.8', 'gugs:128.0'], bass: ['gugs:0.33', 'gugs:0.38', 'gugs:0.39'], chords: ['gugs:0.16', 'gugs:0.17', 'gugs:0.27', 'gugs:0.4', 'gugs:0.28'],
                 lead: ['gugs:0.22', 'gugs:0.73', 'gugs:0.114', 'gugs:0.21', 'gugs:0.56'], pad: ['gugs:0.16', 'gugs:0.89', 'gugs:0.48', 'gugs:0.94'] },
    post_rock: { drums: ['gugs:128.16', 'gugs:128.8'], bass: ['gugs:0.33', 'gugs:0.34', 'gugs:0.35'], chords: ['gugs:0.27', 'gugs:0.29', 'gugs:0.26', 'gugs:0.44', 'gugs:0.48'],
                 lead: ['gugs:0.27', 'gugs:0.29', 'gugs:0.30', 'gugs:0.42', 'gugs:0.14'], pad: ['gugs:0.48', 'gugs:0.49', 'gugs:0.89', 'gugs:0.95', 'gugs:0.94'] },
    lullaby:   { drums: ['gugs:128.40'], bass: ['gugs:0.32', 'gugs:0.35', 'gugs:0.12'], chords: ['gugs:0.8', 'gugs:0.10', 'gugs:0.46', 'gugs:0.108', 'gugs:0.0'],
                 lead: ['gugs:0.10', 'gugs:0.9', 'gugs:0.8', 'gugs:0.108', 'gugs:0.112', 'gugs:0.79', 'vsco:harp'], pad: ['gugs:0.52', 'gugs:0.53', 'gugs:0.49', 'gugs:0.88'] },
    industrial: { drums: ['gugs:128.24', 'gugs:128.16'], bass: ['gugs:0.38', 'gugs:0.39', 'gugs:0.87', 'gugs:0.30'], chords: ['gugs:0.30', 'gugs:0.29', 'gugs:0.93', 'gugs:0.90'],
                 lead: ['gugs:0.30', 'gugs:0.81', 'gugs:0.84', 'gugs:0.103', 'gugs:0.55'], pad: ['gugs:0.93', 'gugs:0.94', 'gugs:0.95', 'gugs:0.97'] },
    surf:      { drums: ['gugs:128.0', 'gugs:128.8'], bass: ['gugs:0.34', 'gugs:0.33', 'gugs:0.32'], chords: ['gugs:0.27', 'gugs:0.16', 'gugs:0.17', 'gugs:0.26'],
                 lead: ['gugs:0.27', 'gugs:0.28', 'gugs:0.26', 'gugs:0.56', 'gugs:0.114'], pad: ['gugs:0.16', 'gugs:0.18', 'gugs:0.61', 'gugs:0.48'] },
    bayou:     { drums: ['gugs:128.40', 'gugs:128.0'], bass: ['gugs:0.33', 'gugs:0.32'], chords: ['gugs:0.21', 'gugs:0.23', 'gugs:0.25', 'gugs:0.4', 'gugs:0.105'],
                 lead: ['gugs:0.21', 'gugs:0.22', 'gugs:0.110', 'gugs:0.65', 'gugs:0.71', 'gugs:0.105'], pad: ['gugs:0.21', 'gugs:0.61', 'gugs:0.48', 'gugs:0.89'] },
    minimal:   { drums: ['gugs:128.0', 'gugs:128.24'], bass: ['gugs:0.32', 'gugs:0.38', 'gugs:0.12'], chords: ['gugs:0.12', 'gugs:0.11', 'gugs:0.13', 'gugs:0.8', 'gugs:0.6', 'gugs:0.16'],
                 lead: ['gugs:0.71', 'gugs:0.11', 'gugs:0.9', 'gugs:0.53', 'gugs:0.12', 'gugs:0.73'], pad: ['gugs:0.52', 'gugs:0.53', 'gugs:0.16', 'gugs:0.49'] },
    chiptune:  { drums: ['gugs:128.24', 'gugs:128.25'], bass: ['gugs:0.38', 'gugs:0.39', 'gugs:0.80'], chords: ['gugs:0.80', 'gugs:0.81', 'gugs:0.16', 'gugs:0.9'],
                 lead: ['gugs:0.80', 'gugs:0.81', 'gugs:0.82', 'gugs:0.83', 'gugs:0.9'], pad: ['gugs:0.16', 'gugs:0.80', 'gugs:0.90', 'gugs:0.50'] },
    trip_hop:  { drums: ['gugs:128.8', 'gugs:128.40', 'gugs:128.25'], bass: ['gugs:0.33', 'gugs:0.35', 'gugs:0.38', 'gugs:0.32'], chords: ['jrhodes:st', 'gugs:0.4', 'gugs:0.48', 'gugs:0.11', 'gugs:0.89'],
                 lead: ['gugs:0.40', 'gugs:0.42', 'gugs:0.11', 'gugs:0.59', 'gugs:0.71', 'gugs:0.9'], pad: ['gugs:0.48', 'gugs:0.49', 'gugs:0.94', 'gugs:0.89', 'gugs:0.44'] },
  };
  const PATCH_PICKS = {
    four_floor: { drums: 'gugs:128.24', bass: 'gugs:0.38', chords: 'gugs:0.90', lead: 'gugs:0.80', pad: 'gugs:0.89' },
    boom_bap:   { drums: 'gugs:128.8',  bass: 'gugs:0.33', chords: 'jrhodes:st', lead: 'gugs:0.11', pad: 'gugs:0.48' },
    lofi:       { drums: 'gugs:128.40', bass: 'gugs:0.32', chords: 'jrhodes:st', lead: 'gugs:0.73', pad: 'gugs:0.89' },
    trap:       { drums: 'gugs:128.25', bass: 'gugs:0.38', chords: 'gugs:0.0', lead: 'gugs:0.10', pad: 'gugs:0.94' },
    dnb:        { drums: 'gugs:128.24', bass: 'gugs:0.39', chords: 'gugs:0.89', lead: 'gugs:0.81', pad: 'gugs:0.91' },
    shuffle:    { drums: 'gugs:128.32', bass: 'gugs:0.32', chords: 'gugs:0.17', lead: 'gugs:0.65', pad: 'gugs:0.16' },
    motorik:    { drums: 'gugs:128.16', bass: 'gugs:0.33', chords: 'gugs:0.29', lead: 'gugs:0.62', pad: 'gugs:0.50' },
    synthwave:  { drums: 'gugs:128.25', bass: 'gugs:0.38', chords: 'gugs:0.90', lead: 'gugs:0.81', pad: 'gugs:0.89' },
    noir:       { drums: 'gugs:128.40', bass: 'gugs:0.32', chords: 'jrhodes:st', lead: 'gugs:0.65', pad: 'gugs:0.48' },
    ambient:    { drums: 'gugs:128.48', bass: 'gugs:0.32', chords: 'gugs:0.88', lead: 'gugs:0.11', pad: 'gugs:0.91' },
    folk:       { drums: 'gugs:128.40', bass: 'gugs:0.32', chords: 'gugs:0.25', lead: 'gugs:0.22', pad: 'gugs:0.48' },
    chamber:    { drums: 'gugs:128.48', bass: 'gugs:0.43', chords: 'gugs:0.48', lead: 'gugs:0.40', pad: 'gugs:0.49' },
    piano:      { drums: 'gugs:128.40', bass: 'gugs:0.0',  chords: 'gugs:0.0',  lead: 'gugs:0.0',  pad: 'gugs:0.48' },
    hymn:       { drums: 'gugs:128.48', bass: 'gugs:0.19', chords: 'gugs:0.19', lead: 'gugs:0.52', pad: 'gugs:0.53' },
    dark_drone: { drums: 'gugs:128.48', bass: 'gugs:0.38', chords: 'gugs:0.92', lead: 'gugs:0.14', pad: 'gugs:0.95' },
    synth_horror: { drums: 'gugs:128.24', bass: 'gugs:0.38', chords: 'gugs:0.90', lead: 'gugs:0.81', pad: 'gugs:0.50' },
    jazz:       { drums: 'gugs:128.40', bass: 'gugs:0.32', chords: 'jrhodes:st', lead: 'gugs:0.66', pad: 'gugs:0.61' },
    dub:        { drums: 'gugs:128.8',  bass: 'gugs:0.38', chords: 'gugs:0.16', lead: 'gugs:0.22', pad: 'gugs:0.89' },
    post_rock:  { drums: 'gugs:128.16', bass: 'gugs:0.34', chords: 'gugs:0.27', lead: 'gugs:0.29', pad: 'gugs:0.49' },
    lullaby:    { drums: 'gugs:128.40', bass: 'gugs:0.32', chords: 'gugs:0.46', lead: 'gugs:0.10', pad: 'gugs:0.53' },
    industrial: { drums: 'gugs:128.24', bass: 'gugs:0.38', chords: 'gugs:0.30', lead: 'gugs:0.81', pad: 'gugs:0.93' },
    surf:       { drums: 'gugs:128.0',  bass: 'gugs:0.34', chords: 'gugs:0.16', lead: 'gugs:0.27', pad: 'gugs:0.18' },
    bayou:      { drums: 'gugs:128.40', bass: 'gugs:0.33', chords: 'gugs:0.21', lead: 'gugs:0.110', pad: 'gugs:0.61' },
    minimal:    { drums: 'gugs:128.0',  bass: 'gugs:0.32', chords: 'gugs:0.12', lead: 'gugs:0.71', pad: 'gugs:0.52' },
    chiptune:   { drums: 'gugs:128.24', bass: 'gugs:0.38', chords: 'gugs:0.80', lead: 'gugs:0.80', pad: 'gugs:0.16' },
    trip_hop:   { drums: 'gugs:128.8',  bass: 'gugs:0.33', chords: 'jrhodes:st', lead: 'gugs:0.40', pad: 'gugs:0.48' },
  };

  // ── ENSEMBLES: named instrument families a request can ask for instead of hand-picking five instruments ──────────────
  // roles: { role: [FORGE preset ids] } — each take draws its own pick per role by its seed (4 takes → 4 line-ups from one
  // family). drums: 'kit' (the standard FORGE kit) or 'kit:<style>' (that style's KIT_STYLES pieces). texture: ambience
  // beds, used only when nothing else (score, catalog, the SOUND controls) named one. Roles an ensemble doesn't list keep
  // the style's own pick (so roles another composer adds later just fall back to auto). link: { role: from } plays `from`'s
  // pick on `role` too (one piano, both hands). drop: parts left out unless PARTS were picked by hand. patch: GeneralUser GS
  // / jRhodes / VSCO ids per role for the PATCH BANK route. fits: the styles it suits (SURPRISE ME pairs from these).
  // A preset this FORGE build lacks is skipped at pick time; explicit per-role picks (INSTRUMENTS) always win.
  const ENSEMBLES = {
    orchestral: { name: 'orchestral', short: 'orchestra', fits: ['chamber', 'hymn', 'post_rock', 'ambient', 'dark_drone', 'noir', 'minimal'],
      roles: { drums: ['kit:chamber', 'kit:hymn'], bass: ['bass_upright', 'bass_fretless', 'strings_noir'], chords: ['strings_ensemble', 'strings_silver', 'strings_tremolo', 'winds_horns', 'strings_noir'],
        lead: ['winds_flute', 'winds_clarinet', 'winds_horns', 'strings_noir', 'winds_brass', 'bell_glock'], pad: ['strings_ensemble', 'choir_vox', 'winds_horns', 'pad_cathedral_air', 'strings_silver'] },
      patch: { drums: ['gugs:128.48'], bass: ['gugs:0.43', 'gugs:0.42'], chords: ['gugs:0.48', 'gugs:0.49', 'gugs:0.44', 'gugs:0.60'], lead: ['gugs:0.73', 'gugs:0.71', 'gugs:0.68', 'gugs:0.60', 'gugs:0.40', 'vsco:celloenssusvib'], pad: ['gugs:0.48', 'gugs:0.52', 'gugs:0.61'] } },
    strings: { name: 'chamber strings', short: 'strings', drop: ['drums'], fits: ['chamber', 'noir', 'piano', 'hymn', 'minimal', 'post_rock'],
      roles: { bass: ['bass_upright', 'bass_fretless'], chords: ['strings_silver', 'strings_noir', 'strings_tremolo', 'strings_ensemble'], lead: ['strings_noir', 'strings_silver'], pad: ['strings_ensemble', 'strings_tremolo', 'strings_silver'] },
      patch: { bass: ['gugs:0.43', 'gugs:0.42'], chords: ['gugs:0.48', 'gugs:0.49', 'gugs:0.44', 'gugs:0.45'], lead: ['gugs:0.40', 'gugs:0.41', 'gugs:0.42', 'vsco:celloenssusvib'], pad: ['gugs:0.48', 'gugs:0.49', 'gugs:0.44'] } },
    brass: { name: 'brass band', short: 'brass', fits: ['shuffle', 'bayou', 'surf', 'jazz', 'folk', 'four_floor', 'hymn'],
      roles: { drums: ['kit:shuffle', 'kit:folk'], bass: ['bass_upright', 'bass_fender', 'winds_brass'], chords: ['winds_brass', 'winds_horns', 'keys_combo_organ'],
        lead: ['lead_brass', 'winds_brass', 'winds_harmon', 'winds_sax'], pad: ['winds_horns', 'winds_brass', 'pad_organ_swell'] },
      patch: { drums: ['gugs:128.0', 'gugs:128.40'], bass: ['gugs:0.58', 'gugs:0.32'], chords: ['gugs:0.61', 'gugs:0.57', 'gugs:0.60'], lead: ['gugs:0.56', 'gugs:0.59', 'gugs:0.57', 'gugs:0.65'], pad: ['gugs:0.61', 'gugs:0.60', 'gugs:0.62'] } },
    winds: { name: 'woodwinds', short: 'winds', fits: ['folk', 'chamber', 'lullaby', 'jazz', 'minimal', 'hymn', 'bayou'],
      roles: { drums: ['kit:folk', 'kit:lullaby'], bass: ['bass_upright', 'winds_clarinet', 'bass_fretless'], chords: ['winds_horns', 'winds_clarinet', 'keys_felt', 'pluck_harp'],
        lead: ['winds_flute', 'winds_clarinet', 'winds_sax', 'lead_whistle', 'winds_harmonica'], pad: ['winds_horns', 'pad_velvet', 'strings_silver'] },
      patch: { drums: ['gugs:128.40'], bass: ['gugs:0.70', 'gugs:0.32'], chords: ['gugs:0.71', 'gugs:0.68', 'gugs:0.69', 'gugs:0.46'], lead: ['gugs:0.73', 'gugs:0.71', 'gugs:0.68', 'gugs:0.72', 'gugs:0.74', 'gugs:0.75'], pad: ['gugs:0.60', 'gugs:0.48', 'gugs:0.69'] } },
    piano: { name: 'solo piano', short: 'piano', drop: ['drums', 'pad'], link: { bass: 'chords', lead: 'chords' }, fits: ['piano', 'noir', 'lofi', 'chamber', 'jazz', 'lullaby', 'hymn', 'ambient'],
      roles: { chords: ['keys_felt', 'keys_ep', 'keys_tape_ep', 'keys_mk1', 'keys_wurli'], pad: ['pad_velvet', 'strings_silver', 'pad_warm', 'pad_bowed_glass'] },
      patch: { bass: ['gugs:0.0'], chords: ['gugs:0.0', 'gugs:0.1', 'gugs:0.4', 'jrhodes:st', 'gugs:0.3'], lead: ['gugs:0.0'], pad: ['gugs:0.48', 'gugs:0.89'] } },
    rock: { name: 'rock band', short: 'rock', fits: ['post_rock', 'surf', 'motorik', 'shuffle', 'industrial', 'dnb', 'four_floor'],
      roles: { drums: ['kit:post_rock', 'kit:four_floor'], bass: ['bass_fender', 'bass_pluck', 'bass_upright'], chords: ['pluck_nylon', 'keys_combo_organ', 'keys_clav', 'lead_fuzz', 'keys_organ'],
        lead: ['lead_fuzz', 'lead_ring', 'lead_saw', 'lead_brass'], pad: ['keys_organ', 'pad_organ_swell', 'strings_ensemble'] },
      patch: { drums: ['gugs:128.16', 'gugs:128.0', 'gugs:128.8'], bass: ['gugs:0.34', 'gugs:0.33'], chords: ['gugs:0.29', 'gugs:0.27', 'gugs:0.30', 'gugs:0.18'], lead: ['gugs:0.30', 'gugs:0.29', 'gugs:0.27'], pad: ['gugs:0.18', 'gugs:0.16', 'gugs:0.48'] } },
    jazz: { name: 'jazz combo', short: 'jazz', fits: ['jazz', 'noir', 'lofi', 'trip_hop', 'boom_bap', 'bayou', 'shuffle'],
      roles: { drums: ['kit:jazz', 'kit:noir'], bass: ['bass_upright', 'bass_fretless'], chords: ['keys_mk1', 'keys_ep', 'keys_vibes', 'keys_wurli', 'keys_felt'],
        lead: ['winds_sax', 'winds_harmon', 'winds_clarinet', 'keys_vibes', 'winds_flute'], pad: ['winds_horns', 'pad_velvet', 'strings_silver', 'pad_dusk'] },
      patch: { drums: ['gugs:128.40', 'gugs:128.32'], bass: ['gugs:0.32', 'gugs:0.35'], chords: ['jrhodes:st', 'gugs:0.0', 'gugs:0.26', 'gugs:0.11'], lead: ['gugs:0.66', 'gugs:0.65', 'gugs:0.59', 'gugs:0.56', 'gugs:0.11'], pad: ['gugs:0.61', 'gugs:0.48'] } },
    folk: { name: 'folk / acoustic', short: 'folk', fits: ['folk', 'bayou', 'shuffle', 'hymn', 'lullaby', 'post_rock'],
      roles: { drums: ['kit:folk', 'kit:bayou'], bass: ['bass_upright', 'bass_fretless', 'bass_fender'], chords: ['pluck_nylon', 'pluck_dobro', 'pluck_harp', 'keys_felt'],
        lead: ['winds_harmonica', 'pluck_dobro', 'lead_whistle', 'winds_flute', 'pluck_nylon'], pad: ['winds_horns', 'strings_ensemble', 'pad_organ_swell', 'pad_dusk'] },
      patch: { drums: ['gugs:128.40', 'gugs:128.32'], bass: ['gugs:0.32'], chords: ['gugs:0.24', 'gugs:0.25', 'gugs:0.105', 'gugs:0.46'], lead: ['gugs:0.22', 'gugs:0.110', 'gugs:0.105', 'gugs:0.73', 'gugs:0.21'], pad: ['gugs:0.48', 'gugs:0.21', 'gugs:0.60'] } },
    electronic: { name: 'electronic', short: 'electronic', fits: ['four_floor', 'dnb', 'trap', 'motorik', 'minimal', 'synthwave', 'industrial'],
      roles: { drums: ['kit:four_floor', 'kit:trap', 'kit:industrial'], bass: ['bass_sub', 'bass_acid', 'bass_reese', 'bass_fm', 'bass_808', 'bass_pluck', 'bass_ladder'],
        chords: ['pad_gate', 'pluck_neon', 'keys_mk1', 'pad_glass', 'arp_chip'], lead: ['lead_saw', 'lead_fm', 'lead_siren', 'lead_square', 'pluck_neon'], pad: ['pad_shimmer', 'pad_neon_rain', 'pad_glass', 'pad_frost', 'pad_velvet'] },
      patch: { drums: ['gugs:128.24', 'gugs:128.25'], bass: ['gugs:0.38', 'gugs:0.39', 'gugs:0.87'], chords: ['gugs:0.90', 'gugs:0.81', 'gugs:0.95'], lead: ['gugs:0.81', 'gugs:0.80', 'gugs:0.84', 'gugs:0.98'], pad: ['gugs:0.89', 'gugs:0.95', 'gugs:0.91', 'gugs:0.94'] } },
    synthwave: { name: 'synthwave / 80s', short: 'synthwave', fits: ['synthwave', 'four_floor', 'synth_horror', 'motorik', 'dnb', 'chiptune'],
      roles: { drums: ['kit:synthwave', 'kit:trap'], bass: ['bass_pluck', 'bass_ladder', 'bass_fm', 'bass_acid'], chords: ['pad_gate', 'pad_velvet', 'keys_mk1', 'pad_neon_rain'],
        lead: ['lead_brass', 'lead_saw', 'lead_square', 'lead_fm', 'lead_fuzz'], pad: ['strings_silver', 'pad_neon_rain', 'pad_shimmer', 'pad_velvet', 'pad_glass'] },
      patch: { drums: ['gugs:128.25', 'gugs:128.24'], bass: ['gugs:0.38', 'gugs:0.39'], chords: ['gugs:0.90', 'gugs:0.81', 'gugs:0.5', 'gugs:0.88'], lead: ['gugs:0.81', 'gugs:0.62', 'gugs:0.84', 'gugs:0.86'], pad: ['gugs:0.95', 'gugs:0.50', 'gugs:0.90', 'gugs:0.89'] } },
    chiptune: { name: 'chiptune', short: 'chiptune', fits: ['chiptune', 'synthwave', 'four_floor', 'surf', 'minimal', 'lullaby'],
      roles: { drums: ['kit:chiptune'], bass: ['bass_pluck', 'bass_sub', 'bass_fm'], chords: ['arp_chip', 'pluck_neon', 'keys_toy_piano', 'bell_glock'], lead: ['lead_square', 'arp_chip', 'lead_fm', 'pluck_neon'], pad: ['pad_gate', 'keys_organ', 'pad_glass'] },
      patch: { drums: ['gugs:128.24', 'gugs:128.25'], bass: ['gugs:0.38', 'gugs:0.80'], chords: ['gugs:0.80', 'gugs:0.81', 'gugs:0.9'], lead: ['gugs:0.80', 'gugs:0.81', 'gugs:0.82', 'gugs:0.83'], pad: ['gugs:0.16', 'gugs:0.80'] } },
    ambient: { name: 'ambient / drone', short: 'ambient', drop: ['drums'], fits: ['ambient', 'dark_drone', 'minimal', 'post_rock', 'hymn', 'chamber', 'piano'],
      roles: { bass: ['pad_sub_drone', 'drone_horizon', 'drone_cathedral', 'bass_sub'], chords: ['pad_shimmer', 'pad_bowed_glass', 'pad_cathedral_air', 'pad_frost', 'choir_angel'],
        lead: ['bell_bowl', 'bell_tubular', 'keys_celesta', 'pluck_kalimba', 'lead_theremin'], pad: ['pad_seance', 'drone_horizon', 'pad_hollow', 'pad_dusk', 'pad_cathedral_air'], texture: ['amb_wind', 'amb_room_tone', 'amb_forest_night'] },
      patch: { bass: ['gugs:0.89', 'gugs:0.95'], chords: ['gugs:0.88', 'gugs:0.92', 'gugs:0.94', 'gugs:0.99'], lead: ['gugs:0.14', 'gugs:0.98', 'gugs:0.8', 'gugs:0.108', 'vsco:harp'], pad: ['gugs:0.89', 'gugs:0.91', 'gugs:0.95', 'gugs:0.97', 'gugs:0.101'] } },
    world: { name: 'world (strings / plucked)', short: 'world', fits: ['folk', 'dub', 'bayou', 'minimal', 'ambient', 'lofi', 'surf'],
      roles: { drums: ['kit:bayou', 'kit:dub'], bass: ['bass_fretless', 'bass_upright'], chords: ['pluck_harp', 'pluck_kalimba', 'pluck_steel_pan', 'pluck_marimba', 'pluck_dobro', 'pluck_nylon'],
        lead: ['pluck_steel_pan', 'pluck_kalimba', 'winds_flute', 'pluck_dobro', 'keys_vibes', 'pluck_marimba'], pad: ['pad_dusk', 'strings_silver', 'drone_bayou', 'pad_warm'] },
      patch: { drums: ['gugs:128.40', 'gugs:128.0'], bass: ['gugs:0.32', 'gugs:0.35'], chords: ['gugs:0.104', 'gugs:0.107', 'gugs:0.106', 'gugs:0.46', 'gugs:0.12', 'gugs:0.15'], lead: ['gugs:0.104', 'gugs:0.107', 'gugs:0.77', 'gugs:0.75', 'gugs:0.114', 'gugs:0.110', 'gugs:0.111'], pad: ['gugs:0.48', 'gugs:0.89', 'gugs:0.109'] } },
    choir: { name: 'choir / sacred', short: 'choir', drop: ['drums'], fits: ['hymn', 'ambient', 'chamber', 'dark_drone', 'minimal', 'lullaby'],
      roles: { bass: ['bass_fretless', 'keys_organ', 'bass_sub'], chords: ['choir_vox', 'keys_organ', 'pad_organ_swell', 'choir_angel'], lead: ['choir_angel', 'choir_vox', 'winds_flute', 'bell_tubular'],
        pad: ['choir_vox', 'choir_crypt', 'pad_cathedral_air', 'choir_angel', 'pad_organ_swell'], texture: ['drone_cathedral', 'amb_room_tone'] },
      patch: { bass: ['gugs:0.19', 'gugs:0.43'], chords: ['gugs:0.52', 'gugs:0.19', 'gugs:0.53', 'gugs:0.20'], lead: ['gugs:0.53', 'gugs:0.52', 'gugs:0.73', 'gugs:0.14'], pad: ['gugs:0.52', 'gugs:0.53', 'gugs:0.91', 'gugs:0.54'] } },
    horror: { name: 'horror / industrial', short: 'horror', fits: ['synth_horror', 'industrial', 'dark_drone', 'trap', 'noir', 'minimal'],
      roles: { drums: ['kit:industrial', 'kit:dark_drone'], bass: ['bass_reese', 'bass_fm', 'bass_808', 'bass_acid'], chords: ['pad_bowed_metal', 'pad_seance', 'pad_frost', 'strings_tremolo', 'keys_celesta'],
        lead: ['lead_theremin', 'lead_ring', 'lead_siren', 'bell_tubular', 'keys_toy_piano'], pad: ['choir_crypt', 'pad_sub_drone', 'pad_seance', 'pad_fluorescent', 'strings_tremolo'], texture: ['amb_fluor_hum', 'drone_engine', 'amb_life_support'] },
      patch: { drums: ['gugs:128.24', 'gugs:128.48'], bass: ['gugs:0.38', 'gugs:0.39', 'gugs:0.87'], chords: ['gugs:0.93', 'gugs:0.44', 'gugs:0.97', 'gugs:0.101'], lead: ['gugs:0.103', 'gugs:0.14', 'gugs:0.81', 'gugs:0.8'], pad: ['gugs:0.93', 'gugs:0.94', 'gugs:0.95', 'gugs:0.52'] } },
    toybox: { name: 'toy box / lullaby', short: 'toy box', fits: ['lullaby', 'chiptune', 'minimal', 'piano', 'folk'],
      roles: { drums: ['kit:lullaby'], bass: ['bass_fretless', 'bass_sub', 'pluck_marimba'], chords: ['keys_celesta', 'bell_music_box', 'keys_toy_piano', 'pluck_kalimba', 'pluck_harp'],
        lead: ['bell_music_box', 'bell_glock', 'keys_toy_piano', 'keys_celesta', 'pluck_kalimba'], pad: ['choir_angel', 'pad_velvet', 'pad_warm', 'strings_silver'], texture: ['amb_clock', 'amb_crickets'] },
      patch: { drums: ['gugs:128.40'], bass: ['gugs:0.32', 'gugs:0.12'], chords: ['gugs:0.8', 'gugs:0.10', 'gugs:0.108', 'gugs:0.46'], lead: ['gugs:0.10', 'gugs:0.9', 'gugs:0.8', 'gugs:0.112', 'gugs:0.13'], pad: ['gugs:0.52', 'gugs:0.53', 'gugs:0.88'] } },
    lofi: { name: 'lo-fi / tape', short: 'lo-fi', fits: ['lofi', 'boom_bap', 'trip_hop', 'jazz', 'dub', 'piano', 'noir'],
      roles: { drums: ['kit:lofi', 'kit:boom_bap'], bass: ['bass_upright', 'bass_fender', 'bass_sub', 'bass_fretless'], chords: ['keys_tape_ep', 'keys_felt', 'keys_wurli', 'keys_mk1', 'pluck_nylon'],
        lead: ['pluck_kalimba', 'keys_vibes', 'bell_music_box', 'winds_flute', 'keys_celesta'], pad: ['pad_tape_wobble', 'pad_dusk', 'pad_velvet'], texture: ['amb_vinyl', 'amb_tape_hiss', 'amb_rain'] },
      patch: { drums: ['gugs:128.40', 'gugs:128.8'], bass: ['gugs:0.33', 'gugs:0.32', 'gugs:0.35'], chords: ['jrhodes:st', 'gugs:0.4', 'gugs:0.5', 'gugs:0.0'], lead: ['gugs:0.11', 'gugs:0.12', 'gugs:0.10', 'gugs:0.108', 'gugs:0.73'], pad: ['gugs:0.49', 'gugs:0.89', 'gugs:0.52'] } },
  };
  // ── TODO(new FORGE presets) — the ONE place to append them after the FORGE preset merge (guitars, orchestral solos /
  // sections, world instruments, pianos / organs, choirs, synths): { ensemble id: { role: [preset ids …] } } is added onto
  // ENSEMBLES[id].roles below, after the ids already there. Safe to add before a preset ships: ids FORGE doesn't have are
  // skipped when a take picks (the data test checks every id once they exist). A new ensemble goes straight into ENSEMBLES.
  const ENSEMBLE_MORE = {
    // rock: { chords: ['guitar_…'], lead: ['guitar_…'] },  orchestral: { lead: ['…'] },  world: { chords: ['…'], lead: ['…'] },
  };
  for (const [id, more] of Object.entries(ENSEMBLE_MORE)) {
    const e = ENSEMBLES[id]; if (!e) continue;
    for (const [role, list] of Object.entries(more || {})) e.roles[role] = [...new Set((e.roles[role] || []).concat(list || []))];
  }

  // ── VARIETY across a request's takes: close (same style + instruments, new notes) · mixed (default: same style, the
  // instruments vary by seed) · wide (each take a different but compatible style; take 1 keeps the brief's) · wild (any
  // style, any ensemble). Compatibility is symmetric (closed below): a style's neighbours share tempo range, harmony or
  // instrumentation, so a wide request stays one cue in different clothes.
  const STYLE_COMPAT = {
    four_floor: ['synthwave', 'motorik', 'dnb', 'minimal', 'chiptune'], boom_bap: ['lofi', 'trip_hop', 'jazz', 'dub', 'trap'],
    lofi: ['boom_bap', 'trip_hop', 'jazz', 'piano', 'noir'], trap: ['boom_bap', 'trip_hop', 'synth_horror', 'industrial'],
    dnb: ['four_floor', 'synthwave', 'industrial', 'post_rock'], shuffle: ['bayou', 'folk', 'surf', 'jazz'],
    motorik: ['four_floor', 'synthwave', 'minimal', 'post_rock', 'surf'], synthwave: ['four_floor', 'motorik', 'synth_horror', 'chiptune'],
    noir: ['jazz', 'trip_hop', 'lofi', 'piano', 'chamber'], ambient: ['dark_drone', 'minimal', 'hymn', 'post_rock', 'chamber'],
    folk: ['bayou', 'shuffle', 'hymn', 'lullaby'], chamber: ['hymn', 'piano', 'ambient', 'minimal', 'noir'],
    piano: ['chamber', 'lofi', 'noir', 'lullaby'], hymn: ['chamber', 'ambient', 'minimal', 'folk'],
    dark_drone: ['ambient', 'synth_horror', 'industrial'], synth_horror: ['dark_drone', 'industrial', 'synthwave'],
    jazz: ['noir', 'lofi', 'trip_hop', 'boom_bap', 'bayou'], dub: ['trip_hop', 'boom_bap', 'lofi', 'minimal'],
    post_rock: ['ambient', 'minimal', 'motorik', 'chamber'], lullaby: ['piano', 'chamber', 'hymn', 'folk', 'chiptune'],
    industrial: ['synth_horror', 'dark_drone', 'trap', 'dnb'], surf: ['shuffle', 'bayou', 'motorik', 'chiptune'],
    bayou: ['shuffle', 'folk', 'jazz', 'surf'], minimal: ['ambient', 'motorik', 'chamber', 'post_rock', 'hymn'],
    chiptune: ['synthwave', 'four_floor', 'surf', 'lullaby'], trip_hop: ['noir', 'dub', 'lofi', 'boom_bap', 'jazz'],
  };
  for (const [a, list] of Object.entries(STYLE_COMPAT)) for (const b of list) if (STYLE_COMPAT[b] && !STYLE_COMPAT[b].includes(a)) STYLE_COMPAT[b].push(a);
  const VARIETY = ['close', 'mixed', 'wide', 'wild'];
  // FEEL: straight / swung (a 16th MPC swing) / shuffle (8ths on the triplet) go into the project's swing / groove (the
  // engine's PERF groove: daw_perf.js); half / double time scale the auto tempo and adjust the density. An explicit BPM
  // or DENSITY stays as typed.
  const FEELS = {
    straight: { name: 'straight', swing: 0 },
    swung: { name: 'swung', groove: { on: true, type: 'mpc16', swing: 0.62, roles: {}, accent: 'backbeat', accentDepth: 0.35, human: { ms: 6, vel: 0.06 } } },
    shuffle: { name: 'shuffle', groove: { on: true, type: 'shuffle8', swing: 0.67, roles: { drums: 0, bass: 4, chords: 6, lead: 8, pad: 0 }, accent: 'backbeat', accentDepth: 0.4, human: { ms: 5, vel: 0.05 } } },
    half: { name: 'half-time', bpm: 0.5, density: 0.15 },
    double: { name: 'double-time', bpm: 2, density: -0.15 },
  };
  // HARMONY colour → seqgen's chord extensions (o.ext, weighted) and, for modal, its progression family
  const HARMONY = {
    plain: { name: 'plain triads', ext: [['triad', 1]] },
    sevenths: { name: 'sevenths', ext: [['seventh', 3], ['sixth', 1]] },
    lush: { name: 'lush 9ths', ext: [['ninth', 3], ['add9', 2], ['seventh', 1]] },
    open: { name: 'open 5ths / sus', ext: [['sus2', 2], ['sus4', 2], ['power', 1]] },
    modal: { name: 'modal', ext: [['sus2', 2], ['triad', 2], ['sus4', 1], ['add9', 1]], prog: 'modal' },
  };
  const MINORISH = { minor: 1, dorian: 1, phrygian: 1, harmonic: 1 };
  // PROGRESSION families a request may name (SeqGen.PROGS; a '<family>_minor' variant is used in minor modes)
  const progFamilies = () => Object.keys(SG().PROGS).filter(k => !/_minor$/.test(k));
  // a volume's tonic itself (SeqGen.volumeKey's home, before its per-track step to a neighbour)
  const homeKey = vol => (vol === undefined || vol === null ? undefined : SG().hash('volume-key:' + vol) % 12);
  // the sound-design presets a request may name: FORGE's own (by category) plus the ones seqgen knows (with fallbacks)
  function soundChoices(kind) {
    const S = SG(), out = new Set();
    for (const p of root.FORGE_PRESETS || []) if (p.category === kind) out.add(p.id);
    const tables = kind === 'ambient' ? [S.TEXTURE_FOR] : [S.FX_FOR, S.HIT_FOR];
    for (const T of tables) for (const list of Object.values(T || {})) for (const id of list) out.add(id);
    for (const id of Object.keys(S.SOUND_FALLBACK || {})) if (kind === 'ambient' ? /^(amb|drone)_/.test(id) : /^fx_/.test(id)) out.add(id);
    return out;
  }

  const havePreset = id => !!id && (root.FORGE_PRESETS || []).some(p => p.id === id);
  // an instrument spec a request may carry per role: the FORGE kit (standard or a style's pieces), a FORGE preset, a patch
  const INSTR_SPEC = /^(kit(:[a-z_]+)?|forge:.+|patch:.+)$/;
  // counter / arp / double: a FORGE device plays them as one mono voice (any preset; the line is monophonic anyway)
  function monoVoice(E, dev, role) {
    const inst = dev && MONO_ROLES.includes(role) && dev.type === 'forge' && E.devices.get(dev.id);
    if (inst && inst.setParam) { try { inst.setParam('voice.mode', 'mono'); } catch (e) {} }
  }
  // where each role plays for each "PLAY ON" choice (emulator / hardware channels from the firmware registry)
  function routing(E, inst) {
    const reg = id => (typeof root.fm1Firmware === 'function' && root.fm1Firmware(id)) || {};
    if (inst === 'felucca') { const r = reg('felucca').roles || { lead: 3, bass: 1, chords: 2, drums: 4 }; return { emu: 'felucca', map: { drums: r.drums, bass: r.bass, chords: r.chords, lead: r.lead } }; }
    if (inst === 'x0x') { const r = reg('x0x').roles || { lead: 3, bass: 2, drums: 10 }; return { emu: 'x0x', map: { drums: r.drums, bass: r.bass, lead: r.lead } }; }
    if (inst === 'patch') return { patch: true, map: {} };
    if (inst === 'hw') { const p = E.midi && E.midi.profile && E.midi.profile(); const r = (p && p.roles) || { lead: 1 }; const map = {}; for (const k of ROLE_ORDER) if (r[k]) map[k] = r[k]; return { hw: true, map }; }
    return { map: {} };
  }
  // a generated song loaded into E as a fresh project (keeps the project's name + master). o: SeqGen.song options.
  async function compose(E, o, inst = 'forge') {
    E.stop();
    o = Object.assign({}, o); delete o.force;
    const song = SG().song(o), rt = routing(E, inst);
    const prev = E.project || {}, proj = root.DAW.Engine.newProject();
    if (prev.name) proj.name = prev.name;
    if (prev.master) proj.master = prev.master;
    Object.assign(proj, { bpm: song.bpm, swing: song.swing, key: song.key, mode: song.mode, sections: song.sections, loop: { on: song.form === 'loop' || song.form === 'bed', a: 0, b: song.bars }, gen: { o, inst } });
    // FEEL: straight → no swing; swung / shuffle → a PERF groove (replaces the swing while on), humanized by the seed
    const fz = FEELS[o.feel];
    if (fz && fz.swing !== undefined) proj.swing = fz.swing;
    if (fz && fz.groove) proj.groove = Object.assign({}, fz.groove, { roles: Object.assign({}, fz.groove.roles), human: Object.assign({}, fz.groove.human, { seed: (song.seed >>> 0) || 1 }) });
    const ens = ENSEMBLES[o.ensemble];
    await E.load(proj);
    let emuDev = null, hwDev = null;
    if (rt.emu) emuDev = await E.addDevice('emu', { name: rt.emu === 'x0x' ? 'X0X' : 'FELUCCA', emuId: rt.emu });
    if (rt.hw) hwDev = await E.addDevice('hw', { name: 'FM-1 HW' });
    for (const role of ROLE_ORDER) {
      const part = song.parts[role]; if (!part || !part.clips.length) continue;
      let dev, ch = 1;
      if (rt.map[role] && (emuDev || hwDev)) { dev = emuDev || hwDev; ch = rt.map[role]; }
      else if (rt.patch && root.PatchBank && ((PATCH_POOLS[song.style] || {})[role] || (PATCH_PICKS[song.style] || PATCH_PICKS.lofi)[role])) {   // arrangement parts: no picks → FORGE / KIT
        const pool = (PATCH_POOLS[song.style] || {})[role], base = (PATCH_PICKS[song.style] || PATCH_PICKS.lofi)[role];
        const ep = ens && ens.patch && ens.patch[role];        // an ensemble's own PATCH BANK family for this role
        const pick = ep && ep.length ? ep[mixHash(song.seed + ':ens:' + role) % ep.length]
          : pool && pool.length ? [base, ...pool][SG().hash(song.seed + ':' + role) % (pool.length + 1)] : base;
        const it = pick && await root.PatchBank.item(pick);
        dev = await E.addDevice('patch', { name: it ? it.name : pick, patch: pick });
      }
      else if (role === 'drums' || role === 'perc') dev = await E.addDevice('kit', { name: role === 'perc' ? 'PERC KIT' : 'KIT', kit: role === 'drums' ? o.kit || song.style : song.style });   // o.kit: an ensemble's kit
      else { const pr = havePreset(part.preset) ? part.preset : SG().presetFor(song.style, role, song.seed); dev = await E.addDevice(typeof root.ForgeSynth === 'function' ? 'forge' : 'basic', { name: role.toUpperCase() + ' · ' + pr, preset: pr }); monoVoice(E, dev, role); }
      const t = E.addTrack('midi', { name: role, role, deviceId: dev.id, channel: ch, color: COLORS[role] });
      t.patterns = part.patterns; t.clips = part.clips;
      if (dev !== emuDev && dev !== hwDev) dev.mix.vol = ROLE_LEVEL[role];   // a starting balance with headroom
      else t.vel = ROLE_VEL[role];
    }
    // the sound-design layer: always FORGE (beds / risers / hits); a preset this FORGE lacks → its nearest older sound
    if (typeof root.ForgeSynth === 'function') for (const key of SOUND_PARTS) {
      const part = song.parts[key]; if (!part || !part.clips.length) continue;
      const fb = (SG().SOUND_FALLBACK || {})[part.preset], pr = havePreset(part.preset) ? part.preset : fb && havePreset(fb) ? fb : null;
      if (!pr) continue;
      const dev = await E.addDevice('forge', { name: key.toUpperCase() + ' · ' + pr, preset: pr });
      const t = E.addTrack('midi', { name: key, role: part.role || key, deviceId: dev.id, color: COLORS.pad });
      t.patterns = part.patterns; t.clips = part.clips;
      dev.mix.vol = ROLE_LEVEL[key] ?? 0.3;
    }
    E.applyMix();
    if (emuDev) emuDev.clock = true;
    E.applyMaster(); E.emit('project');
    return song;
  }

  // The MusicDirector's briefs (python3 godot/tools/music_direction.py brief → resources/music/temp_briefs.json):
  // which catalog tracks the VN scenes actually play, how often, and how intense / dark those scenes read.
  async function loadBriefs() {
    try { const j = JSON.parse(await AKg().game.readText('resources/music/temp_briefs.json')); return Object.fromEntries((j.tracks || []).map(b => [b.id, b])); }
    catch (e) { return null; }
  }
  // one request's creative direction → a clean options object (everything optional; absent = the auto pick)
  function normOpts(o) {
    o = o || {}; const r = {}, S = SG();
    if (o.description && String(o.description).trim()) r.description = String(o.description).trim().slice(0, 400);
    if (o.style && S.STYLES[o.style]) r.style = o.style;
    if (o.mode && S.SCALES[o.mode]) r.mode = o.mode;
    if (o.form && S.FORMS[o.form]) r.form = o.form;
    if (+o.bpm > 0) r.bpm = clamp(+o.bpm, 30, 240);
    if (o.key === 'home') r.key = 'home';                    // the volume's own tonic
    else if (o.key !== undefined && o.key !== null && o.key !== '' && Number.isFinite(+o.key)) r.key = ((Math.round(+o.key) % 12) + 12) % 12;
    else if (typeof o.key === 'string' && /^\s*[A-Ga-g][#b]?\s*$/.test(o.key) && S.keyOf(o.key) !== undefined) r.key = S.keyOf(o.key);
    if (+o.energy) r.energy = clamp(+o.energy, -0.5, 0.5);
    if (o.density !== undefined && o.density !== null && o.density !== '' && Number.isFinite(+o.density)) r.density = clamp(+o.density, 0, 1);
    const L = o.length || {};
    if (+L.sec > 0) r.length = { sec: clamp(+L.sec, 2, 900) }; else if (+L.bars > 0) r.length = { bars: clamp(Math.round(+L.bars), 1, 512) };
    if (o.loop) r.loop = true;
    // PARTS: exactly the roles asked for — the sound layer (texture, fx) counts as parts too
    if (Array.isArray(o.roles) && o.roles.length) { const rs = ALL_ROLES.filter(x => o.roles.includes(x)); if (rs.length && rs.length < ALL_ROLES.length) r.roles = rs; }
    if (+o.extraPads) r.extraPads = clamp(Math.round(+o.extraPads), 0, EXTRA_PADS.length);
    if (o.instruments && typeof o.instruments === 'object') {
      const ins = {};
      for (const [k, v] of Object.entries(o.instruments)) if ((ALL_ROLES.includes(k) || EXTRA_PADS.includes(k)) && v && v !== 'auto' && INSTR_SPEC.test(String(v))) ins[k] = String(v);
      if (Object.keys(ins).length) r.instruments = ins;
    }
    // ENSEMBLE / VARIETY / FEEL / HARMONY / PROGRESSION / SOUND DESIGN — unknown values are dropped, 'auto' is absent
    if (o.ensemble && Object.prototype.hasOwnProperty.call(ENSEMBLES, o.ensemble)) r.ensemble = String(o.ensemble);
    if (o.variety && o.variety !== 'mixed' && VARIETY.includes(o.variety)) r.variety = o.variety;
    if (o.feel && Object.prototype.hasOwnProperty.call(FEELS, o.feel)) r.feel = o.feel;
    if (o.harmony && Object.prototype.hasOwnProperty.call(HARMONY, o.harmony)) r.harmony = o.harmony;
    if (o.prog && progFamilies().includes(o.prog)) r.prog = o.prog;
    if (o.textures === 'none') r.textures = 'none';
    else if (Array.isArray(o.textures)) { const amb = soundChoices('ambient'), x = [...new Set(o.textures.map(String))].filter(id => amb.has(id)).slice(0, 2); if (x.length) r.textures = x; }
    for (const k of ['fx', 'hit']) { if (o[k] === 'none') r[k] = 'none'; else if (o[k] && soundChoices('fx').has(String(o[k]))) r[k] = String(o[k]); }
    if (o.seed !== undefined && o.seed !== null && o.seed !== '' && Number.isFinite(+o.seed)) r.seed = Math.round(+o.seed);
    // TAPE: the whole take through a tape machine (tape_model.js) after rendering
    if (o.tape && TMg() && TMg().MACHINES[o.tape]) r.tape = o.tape;
    return r;
  }
  // the arrangement parts a request names in PARTS (a subset): those are always written; no PARTS → the style's odds
  const arrangeOf = o => (o && o.roles ? ARR_ROLES.filter(r => o.roles.includes(r)) : undefined);
  // the mood a take is composed with: brief (+ energy nudge) → typed direction → explicit overrides
  function takeMood(t, b, o, score) {
    const S = SG();
    let bb = b;
    if (b && o.energy) bb = Object.assign({}, b, { energy: clamp((b.energy ?? 0.5) + o.energy, 0, 1) });
    // brief → the score's written direction (volume → chapter → character → track cue) → typed direction
    let m = S.moodFromBrief(t, bb);
    // the chapters a track plays in: the catalog's own list plus every scene the MusicDirector's brief plays it under
    if (score && S.applyScore) m = S.applyScore(m, score, Object.assign({}, t, { chapters: [...(t.chapters || []), ...((b && b.scenes) || [])] }));
    if (o.description) m = S.applyDirection(m, o.description);
    if (!b && o.energy) { const [lo, hi] = S.STYLES[m.style].bpm; m.bpm = Math.round(clamp(m.bpm + o.energy * (hi - lo), lo, hi)); m.density = +clamp(m.density + o.energy * 0.4, 0.15, 0.95).toFixed(2); }
    if (o.style && o.style !== m.style) { const a = S.STYLES[m.style].bpm, z = S.STYLES[o.style].bpm, pos = clamp((m.bpm - a[0]) / Math.max(1, a[1] - a[0]), 0, 1); m.style = o.style; m.bpm = Math.round(z[0] + pos * (z[1] - z[0])); }
    if (o.form) m.form = o.form;
    if (o.mode) m.mode = o.mode;
    if (o.bpm) m.bpm = o.bpm;
    if (o.density !== undefined) m.density = o.density;
    if (o.key === 'home') { const h = homeKey(t.vol); if (h !== undefined) m.key = h; }   // the volume's tonic itself
    else if (o.key !== undefined) m.key = o.key;            // else the mood's own (its volume's tonal home)
    // SOUND DESIGN typed in the panel: wins over the catalog's / score's / direction's sound words
    if (o.textures !== undefined) m.textures = o.textures === 'none' ? 'none' : o.textures.slice();
    if (o.fx !== undefined) m.fx = o.fx;
    if (o.hit !== undefined) m.hit = o.hit;
    return m;
  }
  // a take's own choices on top of its mood (needs the take's seed): VARIETY (its style), ENSEMBLE (its line-up), FEEL
  // (tempo / density), HARMONY + PROGRESSION. c: { n (take index), seed, used (styles earlier takes of this track got),
  // lock (VARIETY close: take 1's choices) }. Nothing asked → m unchanged, so a seed composes exactly as before.
  function varyTake(m, o, c = {}) {
    const S = SG(), seed = c.seed ?? m.seed, n = c.n || 0, used = c.used || new Set(), H = s => mixHash(String(seed) + ':' + s);
    if (o.variety === 'close' && c.lock) Object.assign(m, JSON.parse(JSON.stringify(c.lock)));
    const wild = o.variety === 'wild' && !(n === 0 && o.style);
    if ((o.variety === 'wide' && n > 0) || wild) {
      const all = Object.keys(S.STYLES).filter(s => !S.STYLES[s].placeholder);
      let cands = (wild ? all : (STYLE_COMPAT[m.style] || all)).filter(s => S.STYLES[s] && s !== m.style && !used.has(s));
      if (!cands.length) cands = (wild ? all : (STYLE_COMPAT[m.style] || all)).filter(s => S.STYLES[s] && s !== m.style);
      if (cands.length) restyle(m, cands[H('variety') % cands.length]);
    }
    // ENSEMBLE: the one asked for, or (wild, none asked) any of them — or none at all, the style's own line-up
    let ensId = o.ensemble || null;
    if (!ensId && o.variety === 'wild') { const ids = [null].concat(Object.keys(ENSEMBLES)); ensId = ids[H('wild-ensemble') % ids.length]; }
    if (ensId && ENSEMBLES[ensId] && !(o.variety === 'close' && c.lock)) applyEnsemble(m, ENSEMBLES[ensId], o, seed);
    if (ensId) m.ensemble = ensId;
    // FEEL: half / double time scale the auto tempo (never a typed BPM) and thin / fill the density (never a typed one)
    const F = FEELS[o.feel];
    if (F) {
      m.feel = o.feel;
      if (F.bpm && !o.bpm && !(o.variety === 'close' && c.lock)) m.bpm = Math.round(clamp(m.bpm * F.bpm, 40, 220));
      if (F.density && o.density === undefined && !(o.variety === 'close' && c.lock)) m.density = +clamp(m.density + F.density, 0.1, 0.95).toFixed(2);
    }
    const Hc = HARMONY[o.harmony];
    if (Hc) { m.harmony = o.harmony; m.ext = Hc.ext; }
    const fam = o.prog || (Hc && Hc.prog);
    if (fam && S.PROGS[fam]) m.progFamily = MINORISH[m.mode] && S.PROGS[fam + '_minor'] ? fam + '_minor' : fam;
    return m;
  }
  // a different style for a take: tempo at the same place in the new style's range (as an explicit STYLE does)
  function restyle(m, style) {
    const S = SG(), a = S.STYLES[m.style].bpm, z = S.STYLES[style].bpm, pos = clamp((m.bpm - a[0]) / Math.max(1, a[1] - a[0]), 0, 1);
    m.style = style; m.bpm = Math.round(z[0] + pos * (z[1] - z[0]));
    // a style seqgen links (solo piano: the hands follow the chords) keeps that; an earlier style's voices may not fit
    return m;
  }
  // an ensemble's picks for this take (by its seed) → the mood's voices / kit / texture / parts. A role picked by hand
  // (INSTRUMENTS) or named in the typed direction ("a sax lead") keeps that; a preset FORGE lacks is skipped.
  function ensemblePicks(ens, seed, skip = {}) {
    const out = {}, forge = root.FORGE_PRESETS ? havePreset : () => true;
    for (const [role, list] of Object.entries(ens.roles || {})) {
      if (skip[role] || !Array.isArray(list)) continue;
      const ok = role === 'drums' ? list.filter(x => /^kit(:[a-z_]+)?$/.test(x)) : list.filter(forge);
      if (ok.length) out[role] = ok[mixHash(String(seed) + ':ens:' + role) % ok.length];
    }
    for (const [role, from] of Object.entries(ens.link || {})) if (!skip[role] && out[from]) out[role] = out[from];
    return out;
  }
  function applyEnsemble(m, ens, o, seed) {
    const skip = Object.assign({}, o.instruments || {}, o.description ? SG().soundsFromText(o.description).voices : {});
    const p = ensemblePicks(ens, seed, skip);
    m.voices = Object.assign({}, m.voices || {});
    for (const [role, v] of Object.entries(p)) {
      if (role === 'drums') m.kit = v.split(':')[1] || 'standard';
      else if (role === 'texture') { if (m.textures === undefined) m.textures = [v]; }
      else m.voices[role] = v;
    }
    if (ens.drop && ens.drop.length && !o.roles) m.drop = ens.drop.slice();
    return m;
  }
  // a mood (+ the take's choices) → the options compose / SeqGen.song take
  function songOpts(m) {
    const s = { seed: m.seed, style: m.style, form: m.form, mode: m.mode, bpm: m.bpm, density: m.density, key: m.key,
      motif: m.motif, motifSpec: m.motifSpec, shape: m.shape, textures: m.textures, fx: m.fx, hit: m.hit, voices: m.voices };
    if (m.ext) s.ext = m.ext;
    if (m.progFamily) s.progFamily = m.progFamily;
    if (m.feel) s.feel = m.feel;
    if (m.kit) s.kit = m.kit;
    if (m.ensemble) s.ensemble = m.ensemble;
    return s;
  }
  // the score bible: every resources/music/score/*.json merged (soundtrack / volumes / chapters / characters / tracks)
  async function loadScore() {
    const G = AKg().game, out = { soundtrack: null, volumes: {}, chapters: {}, characters: {}, tracks: {} };
    let n = 0;
    for (const e of await G.list('resources/music/score')) {
      if (e.kind !== 'file' || !/\.json$/.test(e.name)) continue;
      try {
        const j = JSON.parse(await G.readText('resources/music/score/' + e.name)); n++;
        if (j.soundtrack) out.soundtrack = Object.assign(out.soundtrack || {}, j.soundtrack);
        // field by field: a character the soundtrack file describes keeps that when a volume file adds its motif
        for (const k of ['volumes', 'chapters', 'characters', 'tracks']) for (const [id, v] of Object.entries(j[k] || {})) out[k][id] = Object.assign({}, out[k][id] || {}, v);
      } catch (err) { console.warn('score ' + e.name + ':', err && err.message); }
    }
    return n ? out : null;
  }
  async function readApprovals() { try { const j = JSON.parse(await AKg().game.readText(APPROVALS)); j.tracks = j.tracks || {}; return j; } catch (e) { return { tracks: {} }; } }
  // seeds a new take must not reuse: every take still in review, the approved one, and every seed rejected before
  async function seedsUsed(id) {
    const used = new Set(), rejected = new Set(), G = AKg().game;
    const a = (await readApprovals()).tracks[id] || {};
    for (const r of a.rejected || []) { used.add(+r.seed); rejected.add(+r.seed); }
    if (a.approved && a.approved.seed != null) used.add(+a.approved.seed);
    for (const e of await G.list(REVIEW_DIR + '/' + id)) {
      if (e.kind !== 'directory') continue;
      try { const m = JSON.parse(await G.readText(REVIEW_DIR + '/' + id + '/' + e.name + '/meta.json')); if (m.mood && m.mood.seed != null) used.add(+m.mood.seed); } catch (err) {}
    }
    return { used, rejected };
  }
  function nextSeed(id, base, used) {
    if (!used.has(base)) return base;
    for (let n = 1; n < 100000; n++) { const s = SG().hash(id + '#take' + n) % 1000000000; if (!used.has(s)) return s; }
    return Math.floor(Math.random() * 1e9);
  }
  // arrange the generated sections to exactly L bars: intro · middle sections cycled (the last one cut on a bar
  // line) · outro. Too short for intro + outro → the middle alone. Loops / beds simply repeat, bar-aligned.
  function arrangeTo(E, song, L) {
    const P = E.project, secs = song.sections, intro = secs.find(s => s.name === 'intro'), outro = secs.find(s => s.name === 'outro');
    const mid = secs.filter(s => s !== intro && s !== outro);
    let head = intro ? [intro] : [], tail = outro ? [outro] : [];
    const edge = head.concat(tail).reduce((n, s) => n + s.bars, 0);
    if (L - edge < Math.min(...mid.map(s => s.bars))) { head = []; tail = []; }
    const plan = []; let at = 0;
    for (const s of head) { plan.push({ s, at, len: s.bars }); at += s.bars; }
    let room = L - at - tail.reduce((n, s) => n + s.bars, 0), i = 0;
    while (room > 0) { const s = mid[i++ % mid.length], len = Math.min(s.bars, room); plan.push({ s, at, len }); at += len; room -= len; }
    for (const s of tail) { plan.push({ s, at, len: s.bars }); at += s.bars; }
    for (const tr of P.tracks) {
      const old = tr.clips; tr.clips = [];
      for (const { s, at: a, len } of plan) for (const c of old.filter(c => c.bar === s.bar)) {
        let pid = c.pid; const p = tr.patterns[pid]; if (!p) continue;
        if (len < p.lenBars) {
          pid = c.pid + '_' + len + 'b';
          if (!tr.patterns[pid]) tr.patterns[pid] = { name: p.name + ' (' + len + ' bars)', lenBars: len, notes: p.notes.filter(n => n.t < len * BAR()).map(n => Object.assign({}, n, { d: Math.min(n.d, len * BAR() - n.t) })) };
        }
        tr.clips.push({ bar: a, pid });
      }
    }
    return plan.map(x => x.s.name + (x.len < x.s.bars ? '(' + x.len + ')' : '')).join(' ');
  }
  const forgePresets = () => (root.FORGE_PRESETS || []).map(p => ({ id: p.id, name: p.name, category: p.category }));
  async function deviceFor(E, role, spec) {
    const [kind, ...rest] = spec.split(':'), id = rest.join(':');
    if (kind === 'kit') return E.addDevice('kit', Object.assign({ name: role === 'perc' ? 'PERC KIT' : 'KIT' }, id ? { kit: id } : {}));    // kit:<style> → that style's pieces
    if (kind === 'forge') {
      if (typeof root.ForgeSynth !== 'function') throw new Error('FORGE is not loaded');
      if (!forgePresets().some(p => p.id === id)) throw new Error('no FORGE preset "' + id + '"');
      return E.addDevice('forge', { name: role.toUpperCase() + ' · ' + id, preset: id });
    }
    if (kind === 'patch') {
      if (!root.PatchBank) throw new Error('patch_bank.js is not loaded');
      const it = await root.PatchBank.item(id).catch(() => null);
      return E.addDevice('patch', { name: it ? it.name : id, patch: id });
    }
    throw new Error('unknown instrument ' + spec);
  }
  async function setInstrument(E, t, spec) {
    const P = E.project, old = E.dev(t.deviceId), dev = await deviceFor(E, t.role, spec);
    dev.mix.vol = ROLE_LEVEL[t.role] ?? ROLE_LEVEL.pad * 0.8; monoVoice(E, dev, t.role);
    t.deviceId = dev.id; t.channel = 1; t.vel = 1;
    if (old && !P.tracks.some(x => x.deviceId === old.id)) E.removeDevice(old.id);
  }
  // texture pads from the generated pad part: pad2 = the pad an octave up, softer · pad3 = its root an octave down
  function padLayer(song, kind) {
    const src = song.parts.pad, patterns = {};
    for (const [pid, p] of Object.entries(src.patterns)) {
      let notes;
      if (kind === 'pad2') notes = p.notes.map(n => Object.assign({}, n, { n: n.n + 12, v: +(n.v * 0.75).toFixed(3) }));
      else { const lo = new Map(); for (const n of p.notes) if (!lo.has(n.t) || lo.get(n.t).n > n.n) lo.set(n.t, n); notes = [...lo.values()].map(n => Object.assign({}, n, { n: Math.max(24, n.n - 12), v: 0.5 })); }
      patterns[pid] = { name: kind + ' ' + p.name.replace(/^pad /, ''), lenBars: p.lenBars, notes };
    }
    return { patterns, clips: src.clips.map(c => Object.assign({}, c)) };
  }
  function texturePreset(song, k, mainPreset) {
    const pads = forgePresets().filter(p => /pad|ambient|drone|string|choir/i.test(p.category + ' ' + p.id) && p.id !== mainPreset);
    return pads.length ? pads[SG().hash(song.seed + ':' + k) % pads.length].id : mainPreset;
  }
  // a request's PARTS / EXTRA PADS / INSTRUMENTS applied to the generated project → { role: instrument } for the take's meta
  async function shapeArrangement(E, song, o) {
    const P = E.project, instr = {};
    if (o.roles) for (const t of P.tracks.slice()) if (ALL_ROLES.includes(t.role) && !o.roles.includes(t.role)) { const d = t.deviceId; E.removeTrack(t.id); if (d && !P.tracks.some(x => x.deviceId === d)) E.removeDevice(d); }
    for (let k = 0; k < (o.extraPads || 0); k++) {
      const role = EXTRA_PADS[k], lay = padLayer(song, role);
      if (!Object.keys(lay.patterns).length) continue;
      const spec = (o.instruments && o.instruments[role]) || 'forge:' + texturePreset(song, role, song.parts.pad.preset);
      const dev = await deviceFor(E, role, spec); dev.mix.vol = ROLE_LEVEL.pad * 0.8;
      const t = E.addTrack('midi', { name: role, role, deviceId: dev.id, color: COLORS.pad });
      t.patterns = lay.patterns; t.clips = lay.clips;
    }
    for (const t of P.tracks) {
      const spec = o.instruments && o.instruments[t.role];
      // texture2 / hit share their stem's role but are their own sound: a pick for 'texture' / 'fx' is the first one's
      if (SOUND_PARTS.includes(t.name) && t.name !== t.role) continue;
      // already that instrument (⟳ AGAIN re-applies every recorded one): keep the device; a bare 'kit' keeps the style's kit
      if (spec && (spec === specOf(E, t) || (spec === 'kit' && /^kit/.test(specOf(E, t))))) continue;
      if (spec && !EXTRA_PADS.includes(t.role)) await setInstrument(E, t, spec);
    }
    E.applyMix();
    return instrumentsOf(E);
  }
  // a track's instrument as a request spec: kit · kit:<style> · forge:<preset> · patch:<id> · emu:… · audio · none
  function specOf(E, t) {
    const d = E.dev(t.deviceId);
    return !d ? (t.kind === 'audio' ? 'audio' : 'none') : d.type === 'forge' ? 'forge:' + (d.preset || '') : d.type === 'patch' ? 'patch:' + d.patch
      : d.type === 'kit' ? (d.kit ? 'kit:' + d.kit : 'kit') : d.type === 'emu' ? 'emu:' + (d.emuId || '') + ' ch' + t.channel : d.type;
  }
  // { role (or track name): instrument } of the project as it stands — a take's meta.instruments
  function instrumentsOf(E) {
    const instr = {};
    for (const t of E.project.tracks) {
      const k = t.role && !(t.role in instr) ? t.role : t.name;   // texture2 / hit share their stem's role
      instr[k] = specOf(E, t);
    }
    return instr;
  }

  // stems: one per generated role (drums / bass / chords / lead / pad), anything else one per track
  function stemGroups(P) {
    const g = new Map(), slug = AKg().util.slug;
    for (const t of P.tracks) {
      const hasContent = t.kind === 'midi' ? t.clips.length : t.audio.length; if (!hasContent) continue;
      const key = t.role || ('t_' + slug(t.name));
      if (!g.has(key)) g.set(key, { name: t.role || slug(t.name), role: t.role || '', trackIds: [] });
      g.get(key).trackIds.push(t.id);
    }
    return [...g.values()];
  }
  const sumChannels = list => { const n = Math.max(...list.map(r => r.channels[0].length)); const o = [new Float32Array(n), new Float32Array(n)]; for (const r of list) for (let c = 0; c < 2; c++) { const d = r.channels[c]; for (let i = 0; i < d.length; i++) o[c][i] += d[i]; } return o; };
  // render the project's song (or its loop, folded seamless): with stems, the mastered mix is their sum and every stem
  // gets the same gain and limiter curve → they still add up to the mix exactly, so the game's layered version is as
  // loud as the stereo one. Throws on failure (never hands back an older render).
  // tape: { id (a TapeModel.MACHINES id), seed } — every stem through that machine (same transport) before the master
  const TMg = () => root.TapeModel || null;
  const tapeParams = tape => { const T = TMg(); const p = tape && T && T.machine(tape.id); return p ? Object.assign(p, { seed: (+tape.seed >>> 0) || 1 }) : null; };
  async function render(E, { loop = false, stems = true, master = true, lufs = -14, onProgress, tape = null } = {}) {
    const P = E.project; if (!P || !P.tracks.length) throw new Error('nothing to render');
    const from = loop ? P.loop.a : 0, to = loop ? P.loop.b : E.songBars();
    const AK = AKg();
    if (stems && !E.canRenderOffline()) throw new Error('stems need every track on FORGE / KIT / PATCH BANK (emulator and hardware tracks render in real time only)');
    if (stems) {
      const parts = await E.renderStems({ groups: stemGroups(P), fromBar: from, toBar: to, loop, onProgress });
      const tp = tapeParams(tape);
      if (tp) { if (onProgress) onProgress({ phase: 'tape', id: tape.id }); TMg().processStems(parts.map(p => p.channels), parts[0].sampleRate, tp, { loop }).forEach((c, i) => { parts[i].channels = c; }); }
      const sum = sumChannels(parts), sr = parts[0].sampleRate;
      let mixCh = sum, stats = null, stemCh = parts.map(p => p.channels);
      if (master) { stats = await AK.dsp.master(sum, sr, { lufs, truePeak: -1.5, stems: stemCh }); mixCh = stats.channels; stemCh = stats.stems; }
      return Object.assign({}, parts[0], { channels: mixCh, mastered: stats, stems: parts.map((p, i) => Object.assign(p, { channels: stemCh[i] })) });
    }
    const r = await E.bounce({ fromBar: from, toBar: to, loop });
    const tp = tapeParams(tape);
    if (tp) r.channels = (loop ? TMg().processLoop : TMg().process)(r.channels, r.sampleRate, tp);
    if (!master) return Object.assign(r, { stems: null });
    const m = await AK.dsp.master(r.channels, r.sampleRate, { lufs, truePeak: -1.5 });
    return Object.assign({}, r, { channels: m.channels, mastered: m, stems: null });
  }

  const takeStamp = () => { const d = new Date(), p = n => String(n).padStart(2, '0'); return d.getFullYear() + p(d.getMonth() + 1) + p(d.getDate()) + '-' + p(d.getHours()) + p(d.getMinutes()) + p(d.getSeconds()); };
  const blobJson = o => new Blob([JSON.stringify(o, null, 1)], { type: 'application/json' });
  // a take into review staging: mix.wav · stems/<role>.wav · stems.json · credits.txt · meta.json
  async function writeTake(E, dir, r, stems, credits, meta) {
    const AK = AKg(), G = AK.game, bpm = E.project.bpm, loop = meta.request.loop ? r.loop : null;
    const enc = (chs, extra) => AK.wav.encode(chs, r.sampleRate, { bitDepth: 16, loop, meta: Object.assign({ title: meta.title + ' (temp)', description: meta.title + ' (temp)', originator: 'MM DAW', tags: ['daw', 'temp'], bpm, date: meta.created, temp: true, forTrack: meta.id, take: meta.take, comment: credits.text ? 'Instruments: ' + credits.text.replace(/\n/g, '; ') : undefined }, extra || {}) });
    const files = ['mix.wav'];
    // Godot must neither import nor export the staging folder: a .gdignore keeps it out of the project
    if (!(await G.exists(REVIEW_DIR + '/.gdignore'))) await G.write(REVIEW_DIR + '/.gdignore', new Blob([''], { type: 'text/plain' }));
    await G.write(dir + 'mix.wav', enc(r.channels));
    if (stems && stems.length) {
      const man = { v: 1, title: meta.title + ' (temp)', bpm, bars: r.bars, length_sec: +(r.channels[0].length / r.sampleRate).toFixed(3), loop: !!loop,
        lufs: r.mastered ? +r.mastered.after.toFixed(1) : null, credits: credits.text || '', mix: dir + 'mix.wav', stems: [] };
      for (const st of stems) {
        const f = 'stems/' + AK.util.slug(st.name) + '.wav';
        await G.write(dir + f, enc(st.channels, { title: meta.title + ' (temp) · ' + st.name }));
        // pad2 / pad3 (texture layers) sit on the pad / chords layer (0)
        man.stems.push({ name: st.name, role: st.role || '', file: dir + f, layer: STEM_LAYER[st.name] ?? 0 });
        files.push(f);
      }
      await G.write(dir + 'stems.json', blobJson(man));
      files.push('stems.json');
      meta.stems = man.stems.map(s => ({ name: s.name, role: s.role, layer: s.layer }));
    }
    if (credits.worst !== 'free') { await G.write(dir + 'credits.txt', new Blob([credits.text + '\n'], { type: 'text/plain' })); files.push('credits.txt'); }
    // the exact project, so ✎ EDIT IN DAW opens this take as it was made (older takes are rebuilt from meta)
    await G.write(dir + 'project.json', blobJson(E.project)); files.push('project.json');
    // and as standard MIDI (every track) — Drive keeps the notes alongside the audio
    try { await G.write(dir + 'song.mid', new Blob([E.exportMidi()], { type: 'audio/midi' })); files.push('song.mid'); } catch (e) { /* no SMF writer on the page */ }
    meta.files = files.slice();
    await G.write(dir + 'meta.json', blobJson(meta));
    return files.concat('meta.json').map(f => dir + f);
  }
  // "straight into game (skip review)": the temp as Ogg Vorbis — the files APPROVE writes (AK.game.writeMusic). An older
  // .wav temp at the same base would shadow it (a .wav comes before the .temp.ogg), so it goes; a real .wav stays.
  async function writeTempToGame(E, base, r, stems, credits, title, loop, onProgress) {
    const G = AKg().game;
    const out = await G.writeMusic(base, { mix: r, loop, title: title + ' (temp)', credits: credits.worst !== 'free' ? credits.text : '',
      stems: (stems || []).map(st => ({ name: st.name, role: st.role || '', layer: STEM_LAYER[st.name] ?? 0, pcm: { channels: st.channels, sampleRate: st.sampleRate || r.sampleRate } })),
      extra: { bpm: E.project.bpm, bars: r.bars, lufs: r.mastered ? +r.mastered.after.toFixed(1) : null, credits: credits.text || '' }, onProgress });
    if ((await G.wavKind(base + '.wav')) === 'temp') { await G.remove(base + '.wav'); await G.remove(base + '.wav.credits.txt'); }
    return out.files;
  }

  // make req.takes takes for each catalog track in `list` — compose from its brief + the request, render, master, then
  // stage it for review (or, review: false, write it straight into the game). Events: progress {id, text, stage},
  // take {id, take, seed} | take {id, error}, done {made, failed}.
  async function makeTakes(E, list, req, ctx = {}) {
    const o = normOpts(req.opts), review = req.review !== false, nTakes = clamp(Math.round(+req.takes || 1), 1, 12);
    const on = ctx.onEvent || (() => {}), S = SG(), AK = AKg();
    const briefs = ctx.briefs !== undefined ? ctx.briefs : await loadBriefs();
    const score = ctx.score !== undefined ? ctx.score : await loadScore();
    const done = [], total = list.length * nTakes; let k = 0, song = null;
    for (const t of list) {
      const b = req.useBriefs === false ? null : (briefs && briefs[t.id]) || null;
      let seeds = { used: new Set(), rejected: new Set() };
      if (review) seeds = await seedsUsed(t.id);
      const styles = new Set(); let lock = null, lockIns = null;      // VARIETY: styles taken so far · close: take 1's choices
      for (let n = 0; n < nTakes; n++) {
        k++;
        const m = takeMood(t, b, o, score);
        m.seed = o.seed != null && n === 0 ? o.seed : nextSeed(t.id, m.seed, seeds.used);
        seeds.used.add(m.seed);
        varyTake(m, o, { n, seed: m.seed, used: styles, lock });
        styles.add(m.style);
        // this take's PARTS (an ensemble may leave some out) and INSTRUMENTS (close: take 1's line-up, hand picks win)
        const ot = Object.assign({}, o);
        if (m.drop && !o.roles) { const rs = ALL_ROLES.filter(x => !m.drop.includes(x)); if (rs.length) ot.roles = rs; }
        if (lockIns) ot.instruments = Object.assign({}, lockIns, o.instruments || {});
        const tag = k + '/' + total + ' · ' + t.title + ' · ' + S.STYLES[m.style].name + ' ' + m.mode + ' · seed ' + m.seed;
        const say = (stage, text) => on({ type: 'progress', id: t.id, n: k, total, stage, text: tag + ' — ' + text });
        say('compose', 'composing…');
        try {
          // LENGTH: whole bars; a length in seconds nudges the tempo so whole bars land exactly on it
          let bars = o.length && o.length.bars;
          if (o.length && o.length.sec) { bars = Math.max(1, Math.round(o.length.sec * m.bpm / 240)); m.bpm = bars * 240 / o.length.sec; }
          if (E.project) E.project.name = t.id;
          song = await compose(E, Object.assign(songOpts(m), { shape: o.length ? undefined : m.shape, arrange: arrangeOf(o) }), ctx.inst || 'forge');
          const P = E.project; P.name = t.id;
          const instruments = await shapeArrangement(E, song, ot);
          if (o.variety === 'close' && !lock) {
            // close: every later take gets this one's style, key, tempo, sound and instruments — only the notes change
            const voices = {}; for (const r of ROLE_ORDER) if (song.parts[r] && song.parts[r].preset && r !== 'drums') voices[r] = song.parts[r].preset;
            lock = { style: song.style, mode: song.mode, key: song.key, bpm: m.bpm, density: song.density, form: song.form, textures: song.textures && song.textures.length ? song.textures : 'none',
              fx: song.fx || 'none', hit: song.hit || 'none', voices, kit: m.kit, ensemble: m.ensemble, drop: m.drop };
            lockIns = {}; for (const [r, v] of Object.entries(instruments)) if ((ROLE_ORDER.includes(r) || EXTRA_PADS.includes(r)) && INSTR_SPEC.test(v)) lockIns[r] = v;
          }
          // the game plays a track once, then the next: with no length asked, repeat to at least TEMP_MIN_SEC
          if (!bars) { const secs = song.bars * BAR() * E.spt(); bars = song.bars * Math.max(1, Math.ceil(TEMP_MIN_SEC / secs)); }
          const plan = arrangeTo(E, song, bars);
          P.loop = { on: false, a: 0, b: bars };
          E.emit('project');
          await E.whenReady();
          say('render', 'rendering…');
          // stems: as asked; else the page's default (ctx.stems), or when the brief's scenes swing in intensity (m.stems)
          const stems = (req.stems ?? (ctx.stems === undefined ? true : !!(ctx.stems || m.stems))) && E.canRenderOffline();
          // an asked-for length renders folded (the tail wraps onto the head): exactly `bars` long and seamless
          const r = await render(E, { loop: !!o.length, stems, master: ctx.master !== false, lufs: ctx.lufs ?? -14, tape: o.tape ? { id: o.tape, seed: song.seed } : null,
            onProgress: p => p && (p.phase === 'stem' ? say('render', 'rendering stems: ' + p.done + ' of ' + p.total + ' done…') : p.phase === 'tape' && say('render', 'through the tape machine…')) });
          const credits = await E.credits();
          const sec = r.channels[0].length / r.sampleRate;
          const mood = { style: song.style, form: song.form, mode: song.mode, key: song.key, bpm: +(+song.bpm).toFixed(4), density: song.density, seed: song.seed,
            composer: song.v || 1, motif: song.motif || undefined, textures: song.textures && song.textures.length ? song.textures : 'none', fx: song.fx || 'none', hit: song.hit || 'none',
            voices: m.voices || undefined, motifSpec: m.motifSpec || undefined, shape: m.shape || undefined, scored: m.scored || undefined, vocab: song.vocab,
            // what this take got from the panel's choices (absent when nothing was asked) — ⟳ AGAIN / loadTake rebuild from it
            ensemble: m.ensemble || undefined, kit: m.kit || undefined, drop: m.drop || undefined, feel: m.feel || undefined, harmony: m.harmony || undefined,
            ext: m.ext || undefined, prog: m.progFamily || undefined, variety: o.variety || undefined, tape: o.tape || undefined };
          const entry = { id: t.id, style: song.style, mode: song.mode, bpm: mood.bpm, sec: +sec.toFixed(3), bars, lufs: r.mastered ? +r.mastered.after.toFixed(1) : null, seed: song.seed };
          say('write', 'saving…');
          if (review) {
            const take = takeStamp() + '-s' + song.seed, dir = REVIEW_DIR + '/' + t.id + '/' + take + '/';
            const meta = { v: 1, id: t.id, take, created: new Date().toISOString(), status: 'candidate', title: t.title, vol: t.vol, src: t.src,
              mood, why: m.why || '', request: o, instruments, arrangement: plan, roles: P.tracks.map(x => x.role),
              lufs: entry.lufs, true_peak: r.mastered ? +r.mastered.truePeak.toFixed(2) : +AK.util.db(AK.util.peakOf(r.channels)).toFixed(2),
              seconds: entry.sec, bars, sample_rate: r.sampleRate, credits: credits.text || '', credits_worst: credits.worst || 'free',
              brief: b ? { scene_count: b.scene_count, roles: b.roles, energy: b.energy, darkness: b.darkness, intensity: b.intensity, stems: b.stems, chars: b.chars, words: (b.words || []).slice(0, 6), locales: b.locales, scenes: (b.scenes || []).slice(0, 6) } : null,
              stems: [] };
            entry.files = await writeTake(E, dir, r, r.stems, credits, meta);
            entry.take = take; entry.dir = dir;
            on({ type: 'take', id: t.id, take, seed: song.seed });
          } else {
            entry.files = await writeTempToGame(E, t.src.replace(/\.[^.\/]+$/, ''), r, r.stems, credits, t.title, o.loop ? r.loop : null,
              (f, what) => say('write', 'encoding Ogg Vorbis (' + what + ') ' + Math.round(f * 100) + '%'));
            on({ type: 'take', id: t.id, seed: song.seed, game: true });
          }
          entry.render = r; entry.credits = credits;
          done.push(entry);
        } catch (e) { done.push({ id: t.id, seed: m.seed, error: e.message || String(e) }); on({ type: 'take', id: t.id, error: e.message || String(e) }); }
      }
    }
    const ok = done.filter(d => !d.error);
    on({ type: 'done', made: ok.map(d => ({ id: d.id, take: d.take, seed: d.seed })), failed: done.filter(d => d.error) });
    done.song = song;
    return done;
  }

  // ✎ EDIT IN DAW: a staged take back into E as an editable project — its project.json when it has one, else rebuilt
  // from its meta (same seed / mood / request / length → the same notes and instruments). → { meta, song, exact }
  async function loadTake(E, dir) {
    const G = AKg().game;
    const meta = JSON.parse(await G.readText(dir + 'meta.json')); meta.dir = dir;
    let proj = null; try { proj = JSON.parse(await G.readText(dir + 'project.json')); } catch (e) {}
    if (proj && proj.v) { await E.load(proj); E.project.name = meta.id; E.emit('project'); return { meta, song: null, exact: true }; }
    const mo = meta.mood || {};
    if (E.project) E.project.name = meta.id;
    const song = await compose(E, Object.assign(songOpts(Object.assign({}, mo, { progFamily: mo.prog })), { arrange: arrangeOf(normOpts(meta.request)) }), 'forge');
    E.project.name = meta.id;
    const ro = normOpts(meta.request);
    if (mo.drop && !ro.roles) { const rs = ALL_ROLES.filter(x => !mo.drop.includes(x)); if (rs.length) ro.roles = rs; }
    await shapeArrangement(E, song, ro);
    if (meta.bars) arrangeTo(E, song, meta.bars);
    E.project.loop = { on: false, a: 0, b: meta.bars || E.songBars() };
    E.emit('project');
    return { meta, song, exact: false };
  }
  // ⇪ SEND TO DIRECTOR: the project in E as it is now → a NEW take of the same catalog track, next to the one it was
  // opened from (meta.edited_from). An asked-for length stays seamless (renders folded over the whole song).
  async function stageEdit(E, from, ctx = {}) {
    const P = E.project, AK = AKg(), say = ctx.onProgress || (() => {});
    if (!from || !from.id) throw new Error('no take to send back to');
    const folded = !!(from.request && from.request.length), keepLoop = Object.assign({}, P.loop), bars = E.songBars();
    if (folded) P.loop = { on: keepLoop.on, a: 0, b: bars };
    let r;
    try {
      const tp = from.request && from.request.tape ? { id: from.request.tape, seed: (from.mood || {}).seed } : null;      // the take's TAPE stays on the edit
      r = await render(E, { loop: folded, stems: E.canRenderOffline(), master: ctx.master !== false, lufs: ctx.lufs ?? -14, tape: tp,
        onProgress: p => p && p.phase === 'stem' && say('rendering stems: ' + p.done + ' of ' + p.total + ' done…') });
    } finally { P.loop = keepLoop; }
    say('saving…');
    const credits = await E.credits(), seed = (from.mood || {}).seed;
    const take = takeStamp() + '-s' + seed + '-edit', dir = REVIEW_DIR + '/' + from.id + '/' + take + '/';
    const meta = Object.assign({}, from, { take, created: new Date().toISOString(), status: 'candidate', edited_from: from.take,
      mood: Object.assign({}, from.mood, { bpm: P.bpm }), instruments: instrumentsOf(E), roles: P.tracks.map(x => x.role || x.name), bars,
      lufs: r.mastered ? +r.mastered.after.toFixed(1) : null, true_peak: r.mastered ? +r.mastered.truePeak.toFixed(2) : +AK.util.db(AK.util.peakOf(r.channels)).toFixed(2),
      seconds: +(r.channels[0].length / r.sampleRate).toFixed(3), sample_rate: r.sampleRate, credits: credits.text || '', credits_worst: credits.worst || 'free', stems: [] });
    delete meta.dir; delete meta.files; delete meta.arrangement;
    const files = await writeTake(E, dir, r, r.stems, credits, meta);
    return { take, dir, files, meta };
  }

  root.TempMaker = {
    ROLE_ORDER, ARR_ROLES, MONO_ROLES, SOUND_ROLES, ALL_ROLES, ROLE_LEVEL, ROLE_VEL, COLORS, STEM_LAYER, EXTRA_PADS, arrangeOf, TEMP_MIN_SEC, REVIEW_DIR, APPROVALS, PATCH_POOLS, PATCH_PICKS,
    routing, compose, loadBriefs, loadScore, normOpts, takeMood, readApprovals, seedsUsed, nextSeed, arrangeTo, deviceFor, setInstrument,
    padLayer, texturePreset, shapeArrangement, instrumentsOf, loadTake, stageEdit, stemGroups, sumChannels, render, takeStamp, writeTake, writeTempToGame, makeTakes,
    // the MAKE TAKES panel's choices: instrument families, take variety, feel, harmony colour, sound design
    ENSEMBLES, ENSEMBLE_MORE, STYLE_COMPAT, VARIETY, FEELS, HARMONY, INSTR_SPEC, progFamilies, homeKey, soundChoices, varyTake, restyle, ensemblePicks, applyEnsemble, songOpts, specOf,
  };
})(typeof window !== 'undefined' ? window : globalThis);
