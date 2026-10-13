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
 *
 * Review staging: assets/audio/review/<track id>/<take id>/ mix.wav · stems/<role>.wav · stems.json · credits.txt · meta.json
 */
(function (root) {
  'use strict';
  // audio_kit.js declares AK with a top-level const (not a window property): reach it lexically
  const SG = () => root.SeqGen, AKg = () => (typeof AK !== 'undefined' ? AK : root.AK);
  const BAR = () => root.DAW.BAR;

  const ROLE_ORDER = ['drums', 'bass', 'chords', 'lead', 'pad'];
  const ROLE_LEVEL = { drums: 0.62, bass: 0.6, chords: 0.42, lead: 0.42, pad: 0.36 };
  const ROLE_VEL = { drums: 1, bass: 0.95, chords: 0.75, lead: 0.85, pad: 0.7 };
  const COLORS = { drums: '#e08a7a', bass: '#c87633', chords: '#d8a060', lead: '#a8e89c', pad: '#8ab4f0', audio: '#c8a4f0', midi: '#f0b94a' };
  // the game's intensity layers per stem (AudioMgr: pad / chords always, bass from 0.25, drums 0.5, lead 0.75)
  const STEM_LAYER = { pad: 0, chords: 0, bass: 0.25, drums: 0.5, lead: 0.75 };
  const EXTRA_PADS = ['pad2', 'pad3'];                       // texture layers: the pad an octave up · a sub drone
  const TEMP_MIN_SEC = 90;
  const REVIEW_DIR = 'assets/audio/review';
  const APPROVALS = 'resources/music/temp_approvals.json';
  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
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
  };

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
    await E.load(proj);
    let emuDev = null, hwDev = null;
    if (rt.emu) emuDev = await E.addDevice('emu', { name: rt.emu === 'x0x' ? 'X0X' : 'FELUCCA', emuId: rt.emu });
    if (rt.hw) hwDev = await E.addDevice('hw', { name: 'FM-1 HW' });
    for (const role of ROLE_ORDER) {
      const part = song.parts[role]; if (!part.clips.length) continue;
      let dev, ch = 1;
      if (rt.map[role] && (emuDev || hwDev)) { dev = emuDev || hwDev; ch = rt.map[role]; }
      else if (rt.patch && root.PatchBank) {
        const pool = (PATCH_POOLS[song.style] || {})[role], base = (PATCH_PICKS[song.style] || PATCH_PICKS.lofi)[role];
        const pick = pool && pool.length ? [base, ...pool][SG().hash(song.seed + ':' + role) % (pool.length + 1)] : base;
        const it = pick && await root.PatchBank.item(pick);
        dev = await E.addDevice('patch', { name: it ? it.name : pick, patch: pick });
      }
      else if (role === 'drums') dev = await E.addDevice('kit', { name: 'KIT', kit: song.style });
      else dev = await E.addDevice(typeof root.ForgeSynth === 'function' ? 'forge' : 'basic', { name: role.toUpperCase() + ' · ' + part.preset, preset: part.preset });
      const t = E.addTrack('midi', { name: role, role, deviceId: dev.id, channel: ch, color: COLORS[role] });
      t.patterns = part.patterns; t.clips = part.clips;
      if (dev !== emuDev && dev !== hwDev) dev.mix.vol = ROLE_LEVEL[role];   // a starting balance with headroom
      else t.vel = ROLE_VEL[role];
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
    if (o.key !== undefined && o.key !== null && o.key !== '' && Number.isFinite(+o.key)) r.key = ((Math.round(+o.key) % 12) + 12) % 12;
    if (+o.energy) r.energy = clamp(+o.energy, -0.5, 0.5);
    if (o.density !== undefined && o.density !== null && o.density !== '' && Number.isFinite(+o.density)) r.density = clamp(+o.density, 0, 1);
    const L = o.length || {};
    if (+L.sec > 0) r.length = { sec: clamp(+L.sec, 2, 900) }; else if (+L.bars > 0) r.length = { bars: clamp(Math.round(+L.bars), 1, 512) };
    if (o.loop) r.loop = true;
    if (Array.isArray(o.roles) && o.roles.length) { const rs = ROLE_ORDER.filter(x => o.roles.includes(x)); if (rs.length && rs.length < ROLE_ORDER.length) r.roles = rs; }
    if (+o.extraPads) r.extraPads = clamp(Math.round(+o.extraPads), 0, EXTRA_PADS.length);
    if (o.instruments && typeof o.instruments === 'object') {
      const ins = {};
      for (const [k, v] of Object.entries(o.instruments)) if ((ROLE_ORDER.includes(k) || EXTRA_PADS.includes(k)) && v && v !== 'auto' && /^(kit|forge:.+|patch:.+)$/.test(String(v))) ins[k] = String(v);
      if (Object.keys(ins).length) r.instruments = ins;
    }
    if (o.seed !== undefined && o.seed !== null && o.seed !== '' && Number.isFinite(+o.seed)) r.seed = Math.round(+o.seed);
    return r;
  }
  // the mood a take is composed with: brief (+ energy nudge) → typed direction → explicit overrides
  function takeMood(t, b, o) {
    const S = SG();
    let bb = b;
    if (b && o.energy) bb = Object.assign({}, b, { energy: clamp((b.energy ?? 0.5) + o.energy, 0, 1) });
    const m = S.moodFromBrief(t, bb, o.description);
    if (!b && o.energy) { const [lo, hi] = S.STYLES[m.style].bpm; m.bpm = Math.round(clamp(m.bpm + o.energy * (hi - lo), lo, hi)); m.density = +clamp(m.density + o.energy * 0.4, 0.15, 0.95).toFixed(2); }
    if (o.style && o.style !== m.style) { const a = S.STYLES[m.style].bpm, z = S.STYLES[o.style].bpm, pos = clamp((m.bpm - a[0]) / Math.max(1, a[1] - a[0]), 0, 1); m.style = o.style; m.bpm = Math.round(z[0] + pos * (z[1] - z[0])); }
    if (o.form) m.form = o.form;
    if (o.mode) m.mode = o.mode;
    if (o.bpm) m.bpm = o.bpm;
    if (o.density !== undefined) m.density = o.density;
    m.key = o.key;
    return m;
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
    if (kind === 'kit') return E.addDevice('kit', { name: 'KIT' });
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
    dev.mix.vol = ROLE_LEVEL[t.role] ?? ROLE_LEVEL.pad * 0.8;
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
    if (o.roles) for (const t of P.tracks.slice()) if (!o.roles.includes(t.role)) { const d = t.deviceId; E.removeTrack(t.id); if (d && !P.tracks.some(x => x.deviceId === d)) E.removeDevice(d); }
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
      if (spec && !EXTRA_PADS.includes(t.role)) await setInstrument(E, t, spec);
    }
    E.applyMix();
    return instrumentsOf(E);
  }
  // { role (or track name): instrument } of the project as it stands — a take's meta.instruments
  function instrumentsOf(E) {
    const instr = {};
    for (const t of E.project.tracks) {
      const d = E.dev(t.deviceId), k = t.role || t.name;
      instr[k] = !d ? (t.kind === 'audio' ? 'audio' : 'none') : d.type === 'forge' ? 'forge:' + (d.preset || '') : d.type === 'patch' ? 'patch:' + d.patch : d.type === 'emu' ? 'emu:' + (d.emuId || '') + ' ch' + t.channel : d.type;
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
  async function render(E, { loop = false, stems = true, master = true, lufs = -14, onProgress } = {}) {
    const P = E.project; if (!P || !P.tracks.length) throw new Error('nothing to render');
    const from = loop ? P.loop.a : 0, to = loop ? P.loop.b : E.songBars();
    const AK = AKg();
    if (stems && !E.canRenderOffline()) throw new Error('stems need every track on FORGE / KIT / PATCH BANK (emulator and hardware tracks render in real time only)');
    if (stems) {
      const parts = await E.renderStems({ groups: stemGroups(P), fromBar: from, toBar: to, loop, onProgress });
      const sum = sumChannels(parts), sr = parts[0].sampleRate;
      let mixCh = sum, stats = null, stemCh = parts.map(p => p.channels);
      if (master) { stats = await AK.dsp.master(sum, sr, { lufs, truePeak: -1.5, stems: stemCh }); mixCh = stats.channels; stemCh = stats.stems; }
      return Object.assign({}, parts[0], { channels: mixCh, mastered: stats, stems: parts.map((p, i) => Object.assign(p, { channels: stemCh[i] })) });
    }
    const r = await E.bounce({ fromBar: from, toBar: to, loop });
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
    const done = [], total = list.length * nTakes; let k = 0, song = null;
    for (const t of list) {
      const b = req.useBriefs === false ? null : (briefs && briefs[t.id]) || null;
      let seeds = { used: new Set(), rejected: new Set() };
      if (review) seeds = await seedsUsed(t.id);
      for (let n = 0; n < nTakes; n++) {
        k++;
        const m = takeMood(t, b, o);
        m.seed = o.seed != null && n === 0 ? o.seed : nextSeed(t.id, m.seed, seeds.used);
        seeds.used.add(m.seed);
        const tag = k + '/' + total + ' · ' + t.title + ' · ' + S.STYLES[m.style].name + ' ' + m.mode + ' · seed ' + m.seed;
        const say = (stage, text) => on({ type: 'progress', id: t.id, n: k, total, stage, text: tag + ' — ' + text });
        say('compose', 'composing…');
        try {
          // LENGTH: whole bars; a length in seconds nudges the tempo so whole bars land exactly on it
          let bars = o.length && o.length.bars;
          if (o.length && o.length.sec) { bars = Math.max(1, Math.round(o.length.sec * m.bpm / 240)); m.bpm = bars * 240 / o.length.sec; }
          if (E.project) E.project.name = t.id;
          song = await compose(E, { seed: m.seed, style: m.style, form: m.form, mode: m.mode, bpm: m.bpm, density: m.density, key: m.key }, ctx.inst || 'forge');
          const P = E.project; P.name = t.id;
          const instruments = await shapeArrangement(E, song, o);
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
          const r = await render(E, { loop: !!o.length, stems, master: ctx.master !== false, lufs: ctx.lufs ?? -14,
            onProgress: p => p && p.phase === 'stem' && say('render', 'rendering stems: ' + p.done + ' of ' + p.total + ' done…') });
          const credits = await E.credits();
          const sec = r.channels[0].length / r.sampleRate;
          const mood = { style: song.style, form: song.form, mode: song.mode, key: song.key, bpm: +(+song.bpm).toFixed(4), density: song.density, seed: song.seed };
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
    const song = await compose(E, { seed: mo.seed, style: mo.style, form: mo.form, mode: mo.mode, bpm: mo.bpm, density: mo.density, key: mo.key }, 'forge');
    E.project.name = meta.id;
    await shapeArrangement(E, song, normOpts(meta.request));
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
      r = await render(E, { loop: folded, stems: E.canRenderOffline(), master: ctx.master !== false, lufs: ctx.lufs ?? -14,
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
    ROLE_ORDER, ROLE_LEVEL, ROLE_VEL, COLORS, STEM_LAYER, EXTRA_PADS, TEMP_MIN_SEC, REVIEW_DIR, APPROVALS, PATCH_POOLS, PATCH_PICKS,
    routing, compose, loadBriefs, normOpts, takeMood, readApprovals, seedsUsed, nextSeed, arrangeTo, deviceFor, setInstrument,
    padLayer, texturePreset, shapeArrangement, instrumentsOf, loadTake, stageEdit, stemGroups, sumChannels, render, takeStamp, writeTake, writeTempToGame, makeTakes,
  };
})(typeof window !== 'undefined' ? window : globalThis);
