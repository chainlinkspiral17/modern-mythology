// registries, catalogs and the pure-JS composer / MIDI file code — no browser needed
const { suite, TOOLS } = require('./harness');
const fs = require('fs'), path = require('path');
const between = (s, a, b) => s.split(a)[1].split(b)[0];

suite('data · registries, composer, MIDI files', async t => {
  await t.test('FM-1 firmware registry is strict JSON with the fields the tools read', async () => {
    const src = fs.readFileSync(path.join(TOOLS, 'fm1_firmwares.js'), 'utf8');
    const reg = JSON.parse(between(src, '/*FM1-JSON-BEGIN*/', '/*FM1-JSON-END*/'));
    t.ok(reg.firmwares.length >= 10, 'firmware count');
    const ids = new Set();
    for (const f of reg.firmwares) {
      t.ok(f.id && f.name && !ids.has(f.id), 'unique id ' + f.id); ids.add(f.id);
      if (f.roles) for (const ch of Object.values(f.roles)) t.ok(ch === null || (ch >= 1 && ch <= 16), f.id + ' role channel (null = no such track)');
    }
    const fel = reg.firmwares.find(f => f.id === 'felucca');
    t.eq([fel.roles.bass, fel.roles.chords, fel.roles.lead], [1, 2, 3], 'Felucca role map (bass 1, chords 2, lead 3)');
  });

  await t.test('PATCH BANK catalog: pinned commits, known licences, unique item ids', async () => {
    const src = fs.readFileSync(path.join(TOOLS, 'patch_sources.js'), 'utf8');
    const reg = JSON.parse(between(src, '/*PATCH-JSON-BEGIN*/', '/*PATCH-JSON-END*/'));
    t.ok(reg.sources.length >= 20, 'source count');
    for (const s of reg.sources) {
      t.ok(reg.licences[s.licence], s.id + ' licence ' + s.licence);
      t.ok(/^https:\/\/raw\.githubusercontent\.com\/[^/]+\/[^/]+\/[0-9a-f]{40}\/$/.test(s.base), s.id + ' base is a pinned raw.githubusercontent URL');
      const ids = s.items.map(i => i.id); t.eq(ids.length, new Set(ids).size, s.id + ' duplicate item ids');
    }
    for (const [k, l] of Object.entries(reg.licences)) t.ok(['free', 'credit', 'share-alike'].includes(l.game), k + ' game verdict');
  });

  const SG = require(path.join(TOOLS, 'seqgen.js'));
  await t.test('composer is deterministic per seed and keeps notes inside their patterns', async () => {
    const a = SG.song({ seed: 1234, style: 'noir', form: 'song' }), b = SG.song({ seed: 1234, style: 'noir', form: 'song' });
    t.eq(JSON.stringify(a.parts), JSON.stringify(b.parts), 'same seed, same song');
    for (const style of Object.keys(SG.STYLES)) for (const form of Object.keys(SG.FORMS)) {
      const s = SG.song({ seed: 7, style, form });
      for (const p of Object.values(s.parts)) for (const pat of Object.values(p.patterns)) for (const n of pat.notes) {
        if (n.t < 0 || n.t + n.d > pat.lenBars * SG.BAR + 1 || n.n < 0 || n.n > 127) throw new Error(`${style}/${form}: note out of range ${JSON.stringify(n)}`);
      }
    }
  });

  await t.test('mood from a catalog brief: modes and styles that fit the words', async () => {
    const m = (title, desc) => SG.moodFromText(title, desc, title);
    t.eq(m('Sharp', 'Low bass swell, basement amp buzz. Sharp\'s signature.').mode, 'minor');
    t.eq(m('The Pharmacy Mirror', "Pharmacy fluorescent buzz. The mirror that doesn't quite reflect right.").mode, 'phrygian');
    t.eq(m('The Underworld', 'Intercut. Dancing. Loud music club thump.').style, 'four_floor');
    t.eq(m('The Painting', 'A slow oil-tone pad. The painting that knows you saw it.').mode, 'lydian');
    // genre words name the style outright, and win a tie with a scene word ("kitchen" → lo-fi)
    t.eq(['Kitchen fire crackle, distant German hymn fragment.', 'Lake Charles accordion on the jukebox.', 'A jazz trio with brushes.', 'A music box lullaby.',
      'Low rumble under the floor. A demon.', 'Banjo and fiddle on the porch.', 'Chiptune from the arcade.', 'Dub with melodica, deep reggae bass.', 'Factory floor, machine shop.',
      'Surf guitar twang.', 'Bowed cello single note.', 'Solo piano, late.', 'Synth horror, a Carpenter pulse.', 'A minimalist ostinato.', 'Post-rock slow build.', 'Trip-hop, downtempo.']
      .map(d => m('Cue', d).style),
    ['hymn', 'bayou', 'jazz', 'lullaby', 'dark_drone', 'folk', 'chiptune', 'dub', 'industrial', 'surf', 'chamber', 'piano', 'synth_horror', 'minimal', 'post_rock', 'trip_hop']);
    t.eq(m('Doubts', 'A dubious stranger.').style !== 'dub', true, '"dubious" is not dub');
  });
  await t.test('genre idioms: swung eighths, drumless styles, a dub bass that leaves the one, the horror pedal, a lilting lullaby, one piano', async () => {
    const S = (style, seed) => SG.song({ seed, style, form: 'loop' }), all = (s, r) => Object.values(s.parts[r].patterns).flatMap(p => p.notes);
    const offEighth = [];
    for (let seed = 1; seed <= 8; seed++) for (const style of ['jazz', 'bayou']) for (const r of ['bass', 'chords', 'lead']) if (all(S(style, seed), r).some(n => n.t % SG.PPQ === SG.PPQ / 2)) offEighth.push(style + '/' + r + ' seed ' + seed);
    t.eq(offEighth, [], 'jazz / bayou offbeat eighths sit on the triplet');
    const kit = [];
    for (const style of ['chamber', 'piano', 'hymn', 'lullaby', 'dark_drone']) for (let seed = 1; seed <= 8; seed++) for (const form of ['loop', 'song']) {
      const d = Object.values(SG.song({ seed, style, form }).parts.drums.patterns).flatMap(p => p.notes);
      if (d.some(n => [38, 39, 42, 46, 49].includes(n.n))) kit.push(style + ' seed ' + seed + ' ' + form);
    }
    t.eq(kit, [], 'no snare / clap / hats / crash in the drumless styles');
    let one = 0, bars = 0, ped = 0, pedBad = 0, lilt = 0, liltAll = 0;
    for (let seed = 1; seed <= 40; seed++) {
      const d = S('dub', seed); if (d.vocab.bass[0] === 'dub') { const b = all(d, 'bass'); for (let k = 0; k < 8; k++) { bars++; if (b.some(n => n.t === k * SG.BAR)) one++; } }
      const h = S('synth_horror', seed); if (h.vocab.bass[0] === 'pedal_pulse') { for (const n of all(h, 'bass')) { ped++; if (![0, 7].includes(((n.n - h.key) % 12 + 12) % 12)) pedBad++; } }
      const l = S('lullaby', seed); if (l.vocab.lead === 'lilt') for (const n of all(l, 'lead')) { liltAll++; if ([32, 64].includes(n.t % SG.PPQ)) lilt++; }
    }
    t.ok(bars && one / bars < 0.35, 'dub bass on the one in ' + one + ' / ' + bars + ' bars');
    t.ok(ped && pedBad === 0, 'horror pedal stays on the tonic (+ fifth): ' + pedBad + ' / ' + ped + ' off');
    t.ok(liltAll && lilt / liltAll > 0.25, 'lullaby lead on the triplet: ' + lilt + ' / ' + liltAll);
    for (let seed = 1; seed <= 6; seed++) { const p = S('piano', seed).parts; t.eq([p.bass.preset, p.lead.preset], [p.chords.preset, p.chords.preset], 'solo piano: one instrument, seed ' + seed); }
    const v = SG.song({ seed: 3, style: 'piano', form: 'loop', voices: { chords: 'keys_ep' } }).parts;
    t.eq([v.bass.preset, v.lead.preset], ['keys_ep', 'keys_ep'], 'a voiced piano carries both hands');
    t.eq(Object.values(SG.STYLES).filter(s => s.placeholder).length, 0, 'no placeholder styles left');
  });

  await t.test('composer variety: 12 takes of one style differ in groove, bass figure, progression, comping and song shape', async () => {
    const low = { motorik: { bass: 2, comp: 2 }, ambient: { kick: 1, bass: 3, comp: 2 }, four_floor: { kick: 3 }, synthwave: { kick: 3 }, trap: { comp: 2 }, dnb: { comp: 3 },
      // drumless by design — strings, a piano, an organ chorale, a nursery, a drone keep the kit out (a timpani stroke at most)
      chamber: { kick: 1 }, piano: { kick: 1 }, hymn: { kick: 1 }, lullaby: { kick: 1 }, dark_drone: { kick: 1 } }, bad = [];
    for (const style of Object.keys(SG.STYLES).filter(x => !SG.STYLES[x].placeholder)) {      // placeholders borrow another style's vocabulary
      const k = new Set(), b = new Set(), p = new Set(), c = new Set(), sh = new Set();
      for (let seed = 1; seed <= 12; seed++) {
        const s = SG.song({ seed, style, form: 'loop' }), first = r => Object.values(s.parts[r].patterns)[0];
        const d = first('drums'); k.add(d ? d.notes.filter(n => n.n === 36 && n.t < SG.BAR * 2).map(n => n.t).join() : '');
        const bs = first('bass'); b.add(bs ? bs.notes.filter(n => n.t < SG.BAR * 2).map(n => n.t % SG.BAR).join() : '');
        p.add(s.progression.join()); const ch = first('chords'); c.add(ch ? ch.notes.filter(n => n.t < SG.BAR).map(n => n.t).join() : '');
        sh.add(SG.song({ seed, style, form: 'song' }).sections.map(x => x.name + x.bars).join(' '));
      }
      const need = Object.assign({ kick: 3, bass: 4, prog: 5, comp: 3, shape: 4 }, low[style] || {});
      const got = { kick: k.size, bass: b.size, prog: p.size, comp: c.size, shape: sh.size };
      for (const x in need) if (got[x] < need[x]) bad.push(style + ' ' + x + ' ' + got[x] + ' < ' + need[x]);
    }
    t.eq(bad, [], 'too samey');
  });
  await t.test('sound words → ambience beds, hits, instruments; "no field-recording" means no bed', async () => {
    const a = SG.soundsFromText('Kitchen fire crackle, distant German hymn fragment, table set for nine.');
    t.ok(a.textures.includes('amb_fire') && a.voices.chords === 'keys_organ', JSON.stringify(a));
    const b = SG.soundsFromText('Modem handshake + low fluorescent buzz.');
    t.eq(b.textures, ['amb_fluor_hum', 'amb_modem']);
    t.eq(SG.soundsFromText('A single low pad, no field-recording layer. The quietest track in Vol 2.').textures, 'none');
    t.eq(SG.soundsFromText('Bowed cello single note, dampened.').voices.lead, 'solo_cello');            // the 2026-10-14 solo cello, ahead of the strings patch
    t.eq(SG.soundsFromText('a door chime, then a heartbeat').hit, 'fx_door_chime');
    t.eq(SG.soundsFromText('a door chime, then a heartbeat').textures, ['amb_heartbeat']);
    t.eq(SG.soundsFromText('Pump-bell ding + a fluorescent ballast click').hit, 'fx_bell_hit');
    const s = SG.song({ seed: 3, style: 'noir', form: 'song', textures: ['amb_rain'], hit: 'fx_bell_hit', fx: 'fx_reverse_swell' });
    t.ok(s.parts.texture.preset === 'amb_rain' && s.parts.texture.role === 'texture' && s.parts.texture.clips.length === s.sections.length, 'the bed runs under every section');
    t.ok(s.parts.fx && s.parts.fx.role === 'fx' && s.parts.hit.role === 'fx', 'risers + hits share the fx stem');
    t.ok(!SG.song({ seed: 3, style: 'noir', form: 'song', textures: 'none', fx: 'none', hit: 'none' }).parts.texture, 'none → no bed');
  });
  await t.test('leitmotif: a character\'s motif keeps its rhythm across tracks (any seed / style); volume keys cohere', async () => {
    const on = s => { const ps = Object.values(s.parts.lead.patterns); const all = []; for (const p of ps) for (const n of p.notes) all.push(Math.round(n.t / SG.S16) % 32); return new Set(all); };
    const j = (a, b) => { const i = [...a].filter(x => b.has(x)).length; return i / (new Set([...a, ...b]).size || 1); };
    const x = on(SG.song({ seed: 11, style: 'noir', form: 'loop', motif: 'alma' })), y = on(SG.song({ seed: 99, style: 'lofi', form: 'loop', motif: 'alma' }));
    const z = on(SG.song({ seed: 99, style: 'lofi', form: 'loop', motif: 'sam' }));
    t.ok(j(x, y) > j(x, z) && j(x, y) >= 0.5, 'same motif ' + j(x, y).toFixed(2) + ' vs other ' + j(x, z).toFixed(2));
    t.eq([SG.motifOf('vol5_drunk_uncle_theme'), SG.motifOf('credits_theme'), SG.motifOf('vol7_ambient')], ['drunk_uncle', 'title', null]);
    const keys = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'].map(id => SG.volumeKey(6, 'vol6_' + id)), home = SG.volumeKey(6, 'vol6_a');
    t.ok(new Set(keys).size <= 4, 'one volume, a few related keys: ' + keys);
  });
  await t.test('score bible: every file valid (styles, modes, keys, presets, catalog ids); layers apply in order, typed direction wins', async () => {
    const fs = require('fs'), dir = path.join(TOOLS, '..', 'resources', 'music', 'score');
    global.window = global.window || globalThis; require(path.join(TOOLS, 'forge_synth.js'));
    const presets = (globalThis.FORGE_PRESETS || []).map(p => p.id);
    const cat = JSON.parse(fs.readFileSync(path.join(TOOLS, '..', 'resources', 'music_catalog.json'), 'utf8')), catalog = Array.isArray(cat) ? cat : cat.tracks;
    const merged = { soundtrack: null, volumes: {}, chapters: {}, characters: {}, tracks: {} }, bad = [];
    for (const f of fs.readdirSync(dir).filter(f => f.endsWith('.json'))) {
      let j; try { j = JSON.parse(fs.readFileSync(path.join(dir, f), 'utf8')); } catch (e) { bad.push(f + ': ' + e.message); continue; }
      for (const b of SG.checkScore(j, { catalog, presets })) bad.push(f + ': ' + b);
      if (j.soundtrack) merged.soundtrack = j.soundtrack; for (const k of ['volumes', 'chapters', 'characters', 'tracks']) Object.assign(merged[k], j[k] || {});
    }
    t.eq(bad, [], 'score problems');
    // layering on a made-up score
    const sc = { soundtrack: { bpm: 70 }, volumes: { 9: { style: 'noir', key: 'D', voices: { lead: 'strings_noir' }, feel: 'v' } }, chapters: { vol9_ch2: { mode: 'phrygian', feel: 'c' } },
      characters: { zed: { instrument: 'winds_clarinet', motifSpec: { rhythm: [0, 4, 8], degrees: [0, 2, 4] } } }, tracks: { vol9_zed_theme: { bpm: 60, textures: ['amb_fire'], feel: 't' } } };
    const tr = { id: 'vol9_zed_theme', vol: 9, title: 'Zed', desc: 'A theme.', chapters: ['vol9_ch2_door'] };
    const m = SG.applyScore(SG.moodFromText(tr.title, tr.desc, tr.id), sc, tr);
    t.eq([m.style, m.key, m.mode, m.bpm, m.voices.lead, m.textures, m.motif, m.motifSpec.degrees], ['noir', 2, 'phrygian', 60, 'winds_clarinet', ['amb_fire'], 'zed', [0, 2, 4]]);
    const d = SG.applyDirection(Object.assign({}, m), 'faster, a lonely piano over rain');
    t.ok(d.bpm > 60 && d.voices.lead === 'keys_felt' && d.textures.includes('amb_rain'), 'typed direction wins: ' + JSON.stringify([d.bpm, d.voices, d.textures]));
  });
  // ── the AUDIO DIRECTOR's MAKE TAKES choices (temp_maker.js, pure parts: no engine) ──
  global.window = global.window || globalThis; require(path.join(TOOLS, 'forge_synth.js')); require(path.join(TOOLS, 'temp_maker.js'));
  const TM = globalThis.TempMaker, FORGE = new Set((globalThis.FORGE_PRESETS || []).map(p => p.id));
  await t.test('normOpts: ensemble / variety / key / bpm / feel / harmony / progression / sound design validated strictly (unknown → dropped)', async () => {
    t.eq(TM.normOpts({ ensemble: 'jazz', variety: 'wide', key: 'home', bpm: 300, feel: 'shuffle', harmony: 'lush', prog: 'blues', textures: ['amb_rain', 'amb_fire', 'amb_wind'], fx: 'fx_riser', hit: 'none' }),
      { bpm: 240, key: 'home', ensemble: 'jazz', variety: 'wide', feel: 'shuffle', harmony: 'lush', prog: 'blues', textures: ['amb_rain', 'amb_fire'], fx: 'fx_riser', hit: 'none' });
    t.eq(TM.normOpts({ ensemble: 'kazoo', variety: 'mixed', key: 'H', feel: 'polka', harmony: 'atonal', prog: 'jazz_minor', textures: ['nope', 'fx_riser'], fx: 'amb_rain', hit: 'kick', bogus: 1, ensembleX: 'jazz' }), {},
      'unknown / default values are dropped (mixed is the default; a _minor family is picked by the mode, not asked for)');
    t.eq([TM.normOpts({ key: 'Eb' }).key, TM.normOpts({ key: 7 }).key, TM.normOpts({ key: '' }).key, TM.normOpts({ textures: 'none' }).textures, TM.normOpts({ ensemble: 'toString' }).ensemble], [3, 7, undefined, 'none', undefined]);
    t.eq(TM.normOpts({ instruments: { drums: 'kit:jazz', bass: 'kit', lead: 'forge:lead_saw', pad: 'kitchen', chords: 'patch:gugs:0.4', nope: 'forge:x' } }).instruments,
      { drums: 'kit:jazz', bass: 'kit', lead: 'forge:lead_saw', chords: 'patch:gugs:0.4' });
  });
  await t.test('ENSEMBLES name only presets FORGE has (by role kind), real kit styles, well-formed PATCH ids; every style has PATCH picks and compatible neighbours', async () => {
    const bad = [], cat = Object.fromEntries((globalThis.FORGE_PRESETS || []).map(p => [p.id, p.category])), PATCH = /^(gugs:(0|128)\.\d{1,3}|jrhodes:st|vsco:[a-z0-9_]+)$/;
    t.ok(Object.keys(TM.ENSEMBLES).length >= 17, 'ensembles (+ auto): ' + Object.keys(TM.ENSEMBLES).length);
    for (const [id, e] of Object.entries(TM.ENSEMBLES)) {
      if (!e.name || !e.short) bad.push(id + ': name');
      for (const [role, list] of Object.entries(e.roles)) for (const x of list) {
        if (role === 'drums') { if (!/^kit(:[a-z_]+)?$/.test(x) || (x.includes(':') && !SG.STYLES[x.split(':')[1]])) bad.push(id + ' drums ' + x); continue; }
        if (!FORGE.has(x)) { bad.push(id + ' ' + role + ' ' + x + ' (no such FORGE preset)'); continue; }
        if (role === 'texture' ? cat[x] !== 'ambient' : ['drums', 'fx'].includes(cat[x]) || (cat[x] === 'ambient' && !/^drone_/.test(x))) bad.push(id + ' ' + role + ' ' + x + ' is ' + cat[x]);
      }
      for (const list of Object.values(e.patch || {})) for (const x of list) if (!PATCH.test(x)) bad.push(id + ' patch ' + x);
      for (const [r, from] of Object.entries(e.link || {})) if (!e.roles[from]) bad.push(id + ' link ' + r + '→' + from);
      for (const s of e.fits || []) if (!SG.STYLES[s]) bad.push(id + ' fits ' + s);
    }
    for (const s of Object.keys(SG.STYLES)) {
      if (!TM.PATCH_PICKS[s] || !TM.PATCH_POOLS[s]) bad.push('PATCH tables miss ' + s);
      for (const x of Object.values(TM.PATCH_PICKS[s] || {}).concat(...Object.values(TM.PATCH_POOLS[s] || {}))) if (!PATCH.test(x)) bad.push(s + ' patch ' + x);
      const c = TM.STYLE_COMPAT[s] || [];
      if (c.length < 3 || c.includes(s) || c.some(x => !SG.STYLES[x])) bad.push('STYLE_COMPAT ' + s + ': ' + c);
      for (const x of c) if (!(TM.STYLE_COMPAT[x] || []).includes(s)) bad.push('STYLE_COMPAT not symmetric: ' + s + ' → ' + x);
    }
    t.eq(bad, []);
  });
  const TR = [{ id: 'vol5_alberto_theme', vol: 5, title: 'Alberto', desc: 'A character theme. Warm, a little tired. Piano over rain.' }, { id: 'vol2_diner', vol: 2, title: 'Diner', desc: 'Jukebox at the diner, saturday.' },
    { id: 'vol7_sinkhole', vol: 7, title: 'Sinkhole', desc: 'Low rumble, a demon under the floor.' }, { id: 'vol3_hymn', vol: 3, title: 'Hymn', desc: 'Kitchen fire crackle, distant German hymn fragment.' }];
  const BRIEF = { scene_count: 4, roles: { leitmotif: 4 }, energy: 0.7, darkness: 0.3, intensity: { p10: 0.2, mean: 0.5, p90: 0.8 }, stems: true, chars: ['alberto'], words: [], locales: [] };
  await t.test('default requests compose exactly as before: no new option → varyTake changes nothing, songOpts = the old option list, same song per seed', async () => {
    const legacy = m => ({ seed: m.seed, style: m.style, form: m.form, mode: m.mode, bpm: m.bpm, density: m.density, key: m.key, motif: m.motif, motifSpec: m.motifSpec, shape: m.shape, textures: m.textures, fx: m.fx, hit: m.hit, voices: m.voices });
    for (const tr of TR) for (const seed of [1, 4242, 987654321]) for (const b of [null, BRIEF]) for (const req of [{}, { description: 'slower, a lonely piano', energy: 0.2 }, { style: 'jazz', key: 4 }]) {
      const o = TM.normOpts(req), m0 = TM.takeMood(tr, b, o, null); m0.seed = seed;
      const before = JSON.stringify(m0), m = TM.varyTake(JSON.parse(before), o, { n: 1, seed, used: new Set(['noir']) });
      t.eq(JSON.stringify(m), before, 'varyTake is a no-op: ' + tr.id + ' ' + JSON.stringify(req));
      t.eq(TM.songOpts(m), legacy(m), 'songOpts');
      t.eq(SG.hash(JSON.stringify(SG.song(TM.songOpts(m)))), SG.hash(JSON.stringify(SG.song(legacy(m)))), 'same song: ' + tr.id + ' seed ' + seed);
    }
    // the harmony hook changes only the harmony: the other streams (groove, bass figure, shape …) keep their picks
    const a = SG.song({ seed: 9, style: 'noir', form: 'song' }), c = SG.song({ seed: 9, style: 'noir', form: 'song', ext: [['ninth', 1]], progFamily: 'blues' });
    t.eq([c.vocab.groove, c.vocab.bass, c.vocab.lead, c.sections], [a.vocab.groove, a.vocab.bass, a.vocab.lead, a.sections]);
    t.ok(c.vocab.ext.every(x => x === 'ninth') && SG.PROGS.blues.some(p => p.join() === c.progression.join()), JSON.stringify([c.vocab.ext, c.progression]));
    t.eq(SG.song({ seed: 9, style: 'noir', form: 'song', ext: 'bogus' }).vocab, a.vocab, 'an unknown ext is the style\'s own');
  });
  await t.test('varyTake: ensembles give each seed its own line-up from the family; wide → different compatible styles; wild → anything; feel / harmony / key', async () => {
    const tr = TR[0], run = (req, n = 4) => { const o = TM.normOpts(req), used = new Set(), out = []; for (let k = 0; k < n; k++) { const m = TM.takeMood(tr, null, o, null); m.seed = 1000 + k * 7919; TM.varyTake(m, o, { n: k, seed: m.seed, used }); used.add(m.style); out.push(m); } return out; };
    const J = TM.ENSEMBLES.jazz.roles, jz = run({ ensemble: 'jazz' }, 6);
    for (const m of jz) for (const r of ['bass', 'chords', 'lead', 'pad']) t.ok(J[r].includes(m.voices[r]), r + ' ' + m.voices[r]);
    t.ok(jz.every(m => ['jazz', 'noir'].includes(m.kit) && m.ensemble === 'jazz'), 'kits from the family');
    t.ok(new Set(jz.map(m => JSON.stringify(m.voices))).size >= 5, 'line-ups differ per seed');
    t.ok(new Set(jz.map(m => m.kit)).size === 2, 'both kits turn up across six seeds (the pick is well mixed)');
    const pn = run({ ensemble: 'piano' })[0];
    t.ok(pn.voices.bass === pn.voices.chords && pn.voices.lead === pn.voices.chords && pn.drop.join() === 'drums,pad', 'solo piano: one instrument, no kit / pad: ' + JSON.stringify(pn));
    const hand = run({ ensemble: 'jazz', instruments: { lead: 'forge:lead_saw' }, description: 'a harmonica' })[0];
    t.ok(!('lead' in hand.voices) || hand.voices.lead === TM.takeMood(tr, null, TM.normOpts({ description: 'a harmonica' }), null).voices.lead, 'a hand-picked / named instrument is not overridden: ' + JSON.stringify(hand.voices));
    const wide = run({ variety: 'wide' }).map(m => m.style), base = TM.takeMood(tr, null, {}, null).style;
    t.ok(wide[0] === base && new Set(wide).size === 4 && wide.slice(1).every(s => TM.STYLE_COMPAT[base].includes(s)), 'wide: ' + wide);
    const wideX = run({ variety: 'wide', style: 'hymn' }).map(m => m.style);
    t.ok(wideX[0] === 'hymn' && wideX.slice(1).every(s => TM.STYLE_COMPAT.hymn.includes(s)), 'wide around an asked-for style: ' + wideX);
    const wild = run({ variety: 'wild' }, 6);
    t.ok(new Set(wild.map(m => m.style)).size === 6 && new Set(wild.map(m => m.ensemble || 'auto')).size >= 3, 'wild: ' + wild.map(m => m.style + '/' + (m.ensemble || 'auto')));
    const close = run({ variety: 'close', ensemble: 'rock' });
    t.ok(new Set(close.map(m => m.style)).size === 1, 'close keeps the style');
    // feel: half / double time scale the auto tempo and the density, never a typed BPM / density
    const m0 = TM.takeMood(tr, null, {}, null), half = run({ feel: 'half' })[0], dbl = run({ feel: 'double' })[0], typed = run({ feel: 'half', bpm: 90, density: 0.5 })[0];
    t.eq([half.bpm, dbl.bpm, half.feel], [Math.max(40, Math.round(m0.bpm / 2)), Math.min(220, m0.bpm * 2), 'half']);
    t.ok(half.density > m0.density && dbl.density < m0.density, 'density follows: ' + [half.density, m0.density, dbl.density]);
    t.eq([typed.bpm, typed.density], [90, 0.5]);
    const h = run({ harmony: 'modal', mode: 'minor' })[0], j = run({ prog: 'jazz', mode: 'minor' })[0], jM = run({ prog: 'jazz', mode: 'major' })[0];
    t.eq([h.harmony, h.progFamily, JSON.stringify(h.ext), j.progFamily, jM.progFamily], ['modal', 'modal', JSON.stringify(TM.HARMONY.modal.ext), 'jazz_minor', 'jazz']);
    t.eq([TM.takeMood(tr, null, TM.normOpts({ key: 'home' }), null).key, TM.homeKey(5)], [SG.hash('volume-key:5') % 12, SG.hash('volume-key:5') % 12], 'volume home key');
    const snd = TM.takeMood(TR[3], null, TM.normOpts({ textures: ['amb_rain'], hit: 'none' }), null);
    t.eq([snd.textures, snd.hit], [['amb_rain'], 'none'], 'the SOUND controls win over the catalog\'s words (fire crackle)');
    const amb = TM.takeMood(TR[1], null, TM.normOpts({}), null); TM.varyTake(amb, TM.normOpts({ ensemble: 'lofi' }), { seed: 3 });
    t.ok(amb.textures === undefined || TM.ENSEMBLES.lofi.roles.texture.includes(amb.textures[0]), 'an ensemble bed only where nothing named one: ' + JSON.stringify(amb.textures));
  });
  // ── arrangement parts: counter, arp, perc, double ─────────────────────────
  await t.test('reproducibility: drums / bass / chords / lead / pad notes are byte-identical to the composer before the arrangement parts', async () => {
    const { snapshot } = require('./fixtures/seqgen_snapshot.js');
    const want = JSON.parse(fs.readFileSync(path.join(__dirname, 'fixtures', 'seqgen_roles_v2.json'), 'utf8')), got = snapshot(SG);
    const bad = Object.keys(want).filter(k => want[k] !== got[k]);
    t.ok(Object.keys(want).length > 1000, 'snapshot size ' + Object.keys(want).length);
    t.eq(bad, [], 'style/form/seed/variant whose five original parts changed (takes would re-compose differently)');
    // and o.arrange never moves them either: no arrangement parts, all of them forced, the style's odds — same five parts
    const five = s => JSON.stringify(['drums', 'bass', 'chords', 'lead', 'pad'].map(r => s.parts[r].patterns));
    for (const style of ['noir', 'synthwave', 'folk', 'jazz', 'chamber']) {
      const a = SG.song({ seed: 31, style, form: 'song' }), b = SG.song({ seed: 31, style, form: 'song', arrange: 'none' }), c = SG.song({ seed: 31, style, form: 'song', arrange: SG.ARR_ROLES });
      t.eq([five(b), five(c)], [five(a), five(a)], style + ': arrange option moved an original part');
      t.ok(SG.ARR_ROLES.every(r => !b.parts[r]), style + ': arrange none');
    }
  });
  await t.test('arrangement parts: each style gets the parts it wants (and none it doesn\'t), with sections bringing them in and out', async () => {
    const bad = [], seen = {};
    for (const style of Object.keys(SG.STYLES)) {
      const A = SG.ARRANGE[style], got = { counter: 0, arp: 0, perc: 0, double: 0 }, kinds = new Set();
      for (let seed = 1; seed <= 24; seed++) for (const form of ['loop', 'song']) {
        const s = SG.song({ seed, style, form });
        for (const r of SG.ARR_ROLES) if (s.parts[r] && s.parts[r].clips.length) got[r]++;
        if (s.vocab.arrange.counter) kinds.add(s.vocab.arrange.counter);
      }
      seen[style] = got;
      SG.ARR_ROLES.forEach((r, i) => {
        if (A.p[i] >= 0.3 && !got[r]) bad.push(style + ': no ' + r + ' in 48 songs');
        if (A.p[i] === 0 && got[r]) bad.push(style + ': ' + r + ' though the style never wants it');
      });
      if (A.p[0] >= 0.5 && kinds.size < Math.min(2, new Set(A.counter).size)) bad.push(style + ': counter kinds ' + [...kinds]);
    }
    t.eq(bad, [], 'arrangement odds');
    t.ok(seen.synthwave.arp > seen.jazz.arp && seen.chamber.counter > seen.trap.counter && seen.bayou.perc > seen.chamber.perc, 'idioms: synthwave arps, chamber counter lines, bayou percussion');
    // in a song the parts come and go with the sections: an arp / counter never in every section of every song
    let everywhere = 0, songs = 0;
    for (let seed = 1; seed <= 30; seed++) {
      const s = SG.song({ seed, style: 'synthwave', form: 'song', arrange: ['arp', 'counter'] }); songs++;
      if (['arp', 'counter'].every(r => s.parts[r].clips.length === s.sections.length)) everywhere++;
      const lead = new Set(s.parts.lead.clips.map(c => c.bar));
      for (const c of s.parts.counter.clips) if (!lead.has(c.bar) && !['second', 'ring', 'interlock'].includes(s.vocab.arrange.counter)) throw new Error('an answering counter without a lead, seed ' + seed);
    }
    t.ok(everywhere < songs / 3, 'arp + counter in every section of ' + everywhere + ' / ' + songs + ' songs');
  });
  await t.test('counter: answers around the lead — off its onsets, no unison / octave on strong beats, no parallel octaves, one voice', async () => {
    const pc = n => ((n % 12) + 12) % 12, S16 = SG.S16, BEAT = SG.PPQ;
    let on = 0, hit = 0, strong = 0, oct = 0, par = 0, overlap = 0, inRange = 0, notes = 0;
    for (const style of Object.keys(SG.STYLES)) for (let seed = 1; seed <= 10; seed++) for (const form of ['song', 'loop']) {
      const s = SG.song({ seed, style, form, arrange: ['counter'] }), c = s.parts.counter; if (!c) continue;
      for (const [pid, p] of Object.entries(c.patterns)) {
        const lp = s.parts.lead.patterns['lead_' + pid.slice('counter_'.length)], ln = lp ? lp.notes.filter(x => x.d > 10 || x.v >= 0.5) : [];
        const onsets = new Set(ln.map(x => Math.round(x.t / S16))), sound = t => { let n = null; for (const x of ln) if (x.t <= t && x.t + x.d > t) n = x.n; return n; };
        for (const x of p.notes) { notes++; if (x.n >= 52 && x.n <= 93) inRange++; if (s.vocab.arrange.counter !== 'harmony') { on++; if (onsets.has(Math.round(x.t / S16))) hit++; } }
        for (let i = 1; i < p.notes.length; i++) if (p.notes[i - 1].t + p.notes[i - 1].d > p.notes[i].t) overlap++;
        let prev = null;
        for (let t0 = 0; t0 < p.lenBars * SG.BAR; t0 += 2 * BEAT) {
          const cn = (p.notes.find(x => x.t <= t0 && x.t + x.d > t0) || {}).n, l = sound(t0);
          if (cn === undefined || l === null) { prev = null; continue; }
          strong++; const o = pc(cn - l) === 0; if (o) oct++;
          if (o && prev && prev.o && prev.c !== cn && prev.l !== l) par++;
          prev = { c: cn, l, o };
        }
      }
    }
    t.ok(notes > 2000, notes + ' counter notes');
    t.ok(hit / on < 0.05, 'counter notes on a lead onset: ' + hit + ' / ' + on);
    t.eq([oct, par, overlap], [0, 0, 0], 'strong-beat unisons / octaves (of ' + strong + '), parallel octaves, overlapping notes');
    t.eq(inRange, notes, 'counter register');
  });
  await t.test('arp: chord tones only, one note at a time, rate from density; perc on its own voices; doubles in octaves; swung where the style swings', async () => {
    const pc = n => ((n % 12) + 12) % 12;
    let n = 0, off = 0, overlap = 0;
    for (const style of Object.keys(SG.STYLES)) for (let seed = 1; seed <= 6; seed++) for (const form of ['song', 'loop', 'bed']) {
      const s = SG.song({ seed, style, form, arrange: ['arp'] }), a = s.parts.arp; if (!a) continue;
      for (const [pid, p] of Object.entries(a.patterns)) {
        for (const x of p.notes) { n++; if (!SG.chordTonesAt(s, pid.slice(4), x.t).includes(pc(x.n))) off++; }
        for (let i = 1; i < p.notes.length; i++) if (p.notes[i - 1].t + p.notes[i - 1].d > p.notes[i].t) overlap++;
      }
    }
    t.ok(n > 10000, n + ' arp notes'); t.eq([off, overlap], [0, 0], 'arp notes off the chord / overlapping');
    const count = d => Object.values(SG.song({ seed: 4, style: 'synthwave', form: 'loop', density: d, arrange: ['arp'] }).parts.arp.patterns).reduce((k, p) => k + p.notes.length, 0);
    t.ok(count(0.9) > count(0.3) * 1.4, 'denser → faster arp: ' + count(0.3) + ' → ' + count(0.9));
    // perc (by the style's odds) never doubles a voice the drums play; plays a KIT
    const clash = [];
    for (const style of Object.keys(SG.STYLES)) for (let seed = 1; seed <= 24; seed++) {
      const s = SG.song({ seed, style, form: 'song' }); if (!s.parts.perc) continue;
      const dn = new Set(Object.values(s.parts.drums.patterns).flatMap(p => p.notes.map(x => x.n)));
      const both = [...new Set(Object.values(s.parts.perc.patterns).flatMap(p => p.notes.map(x => x.n)))].filter(x => dn.has(x));
      if (both.length) clash.push(style + '/' + seed + ': ' + both); if (s.parts.perc.preset !== 'kit') clash.push(style + ' perc preset ' + s.parts.perc.preset);
    }
    t.eq(clash, [], 'perc voices the drums already play');
    // double: the lead an octave away, the same rhythm
    const d = SG.song({ seed: 9, style: 'noir', form: 'song', arrange: ['double'] });
    for (const [pid, p] of Object.entries(d.parts.double.patterns)) {
      const src = d.vocab.arrange.double === 'bass_up' ? d.parts.bass.patterns['bass_' + pid.slice(7)] : d.parts.lead.patterns['lead_' + pid.slice(7)];
      const st = new Map(src.notes.map(x => [x.t, x.n]));
      t.ok(p.notes.every(x => st.has(x.t) && Math.abs(x.n - st.get(x.t)) === 12), 'double ' + pid + ' is its source in octaves');
    }
    // trip8 styles (jazz, bayou, lullaby): no straight offbeat eighth in the new parts either
    const straight = [];
    for (const style of ['jazz', 'bayou', 'lullaby']) for (let seed = 1; seed <= 8; seed++) {
      const s = SG.song({ seed, style, form: 'loop', arrange: SG.ARR_ROLES });
      for (const r of SG.ARR_ROLES) if (s.parts[r] && Object.values(s.parts[r].patterns).some(p => p.notes.some(x => x.t % SG.PPQ === SG.PPQ / 2))) straight.push(style + '/' + r + ' seed ' + seed);
    }
    t.eq(straight, [], 'straight offbeat eighths in a swung style');
    // re-roll one arrangement part: same structure, new notes
    const s0 = SG.song({ seed: 12, style: 'synthwave', form: 'song', arrange: SG.ARR_ROLES });
    for (const r of SG.ARR_ROLES) {
      const p = SG.part(r, s0, { seed: 777 });
      t.eq(p.clips.map(c => c.bar), s0.parts[r].clips.map(c => c.bar), r + ' re-roll keeps its sections');
      t.ok(r === 'double' || JSON.stringify(p.patterns) !== JSON.stringify(s0.parts[r].patterns), r + ' re-roll changes the notes');
    }
  });
  await t.test('score shapes may place the arrangement parts; checkScore knows the roles', async () => {
    const s = SG.song({ seed: 5, style: 'noir', shape: [['intro', 2, ['pad', 'arp']], ['A', 4, ['drums', 'bass', 'chords', 'lead', 'counter']], ['B', 4, ['drums', 'bass', 'lead', 'perc', 'double']]] });
    const where = r => (s.parts[r] ? s.parts[r].clips.map(c => c.bar) : []);
    t.eq([where('arp'), where('counter'), where('perc'), where('double')], [[0], [2], [6], [6]], 'parts exactly where the cue puts them');
    const bad = SG.checkScore({ tracks: {}, volumes: { 1: { shape: [['A', 4, ['drums', 'arp', 'counter', 'bogus']]], voices: { counter: 'winds_horns', fiddle: 'strings_silver' } } } }, { presets: ['winds_horns', 'strings_silver'] });
    t.eq(bad, ['volume 1: voices role fiddle', 'volume 1: shape A role bogus']);
    t.eq(SG.song({ seed: 5, style: 'noir', form: 'loop', voices: { counter: 'winds_flute' }, arrange: ['counter'] }).parts.counter.preset, 'winds_flute', 'voices name the counter\'s instrument');
  });
  const SMF = require(path.join(TOOLS, 'smf.js'));
  await t.test('remix: NOTES recipes graft the source\'s harmony, sections and theme; plain songs unchanged; seeded', async () => {
    const SG = require(path.join(TOOLS, 'seqgen.js')), RX = require(path.join(TOOLS, 'remix.js'));
    const src = { seed: 4242, style: 'hymn', form: 'song', mode: 'major', key: 5, bpm: 70, density: 0.5 };
    const before = JSON.stringify(SG.song(src).parts);
    const sp = SG.plan(src);
    for (const recipe of ['restyle', 'cover', 'variations', 'underscore', 'intense', 'dream', 'blend']) {
      const no = RX.notesOptions(recipe, src, { seed: 7, n: 0, target: { style: 'noir', key: 9, density: 0.6 }, with: recipe === 'blend' ? { seed: 99, style: 'folk', mode: 'major', key: 2, motif: 'sam' } : null });
      const pl = SG.plan(no.o), song = SG.song(no.o);
      t.eq(pl.sections.map(x => x.name + ':' + x.bars), sp.sections.map(x => x.name + ':' + x.bars), recipe + ' sections');
      t.eq(pl.HP.A.prog, sp.HP.A.prog, recipe + ' progression A');
      if (recipe !== 'variations') t.eq(pl.HP.B.prog, sp.HP.B.prog, recipe + ' progression B');
      t.eq([pl.mode, pl.key], [sp.mode, 9], recipe + ': the source mode, the target key');
      t.ok(song.bars === sp.sections.reduce((n, x) => n + x.bars, 0) && song.parts.lead.clips.length + song.parts.pad.clips.length > 0, recipe + ' composes');
      if (recipe === 'underscore' || recipe === 'dream') t.ok(!song.parts.drums.clips.length, recipe + ': no drums');
      if (recipe === 'intense') t.ok(song.bpm >= SG.STYLES[song.style].bpm[0] && song.parts.drums.clips.length >= sp.sections.filter(x => x.base !== 'intro').length, 'intense: drums everywhere, up to tempo');
      if (recipe === 'restyle' || recipe === 'cover') t.ok(song.style !== 'hymn', recipe + ' changes style: ' + song.style);
      t.eq(JSON.stringify(SG.song(RX.notesOptions(recipe, src, { seed: 7, n: 0, target: { style: 'noir', key: 9, density: 0.6 }, with: recipe === 'blend' ? { seed: 99, style: 'folk', mode: 'major', key: 2, motif: 'sam' } : null }).o).parts), JSON.stringify(song.parts), recipe + ' seeded');
    }
    const bl = SG.plan(RX.notesOptions('blend', src, { seed: 7, n: 0, target: {}, with: { seed: 99, style: 'folk', mode: 'major', key: 2 } }).o);
    t.eq(JSON.stringify(bl.motifA), JSON.stringify(SG.plan({ seed: 99, style: 'folk', mode: 'major', key: 2 }).motifA), 'blend: the WITH source\'s theme');
    t.eq(JSON.stringify(SG.song(src).parts), before, 'a plain song is untouched by the graft hook');
    const m = [{ s: 0, step: 0 }, { s: 4, step: 2 }, { s: 16, step: 4 }];
    t.eq(RX.motifOp(m, 'invert').map(x => x.step), [0, -2, -4]);
    t.eq(RX.motifOp(m, 'augment').map(x => x.s), [0, 8]);
    t.eq(RX.motifOp(m, 'displace').map(x => x.s), [2, 6, 18]);
    t.ok(RX.MOTIF_OPS.every(op => RX.motifOp(m, op).every(x => x.s >= 0 && x.s < 32)), 'every op stays in two bars');
  });
  await t.test('remix: tempo, downbeat, key and bar roots heard from audio; the stretch and chop are finite and the right length', async () => {
    const SG = require(path.join(TOOLS, 'seqgen.js')), RX = require(path.join(TOOLS, 'remix.js')), sr = 48000;
    const synth = (bpm, key, minor, sec, off) => {
      const x = new Float32Array(sec * sr), beat = 60 / bpm, sc = minor ? [0, 2, 3, 5, 7, 8, 10] : [0, 2, 4, 5, 7, 9, 11], prog = [0, 5, 3, 4], R = SG.rng(1);
      for (let i = 0; i < x.length; i++) {
        const tt = i / sr - off; if (tt < 0) continue;
        const deg = prog[Math.floor(tt / (4 * beat)) % 4]; let v = 0;
        for (const d of [deg, deg + 2, deg + 4]) v += 0.08 * Math.sin(2 * Math.PI * 440 * Math.pow(2, (key + sc[d % 7] + 12 * Math.floor(d / 7) - 21) / 12) * tt);
        const bt = tt % beat; if (bt < 0.03) v += Math.sin(2 * Math.PI * 60 * bt) * Math.exp(-bt * 80) * 0.8 + (bt < 0.01 ? (R() - 0.5) * 0.3 : 0);
        x[i] = v;
      }
      return x;
    };
    for (const [bpm, key, minor, off] of [[100, 9, true, 0.3], [84, 2, false, 0], [126, 4, true, 1.1]]) {
      const x = synth(bpm, key, minor, 30, off), tp = RX.estimateTempo(x, sr), k = RX.estimateKey(x, sr);
      const beat = 60 / bpm, ph = RX.downbeat(x, sr, tp.bpm, tp.phase), barSec = 4 * beat;
      const err = Math.abs(((ph - off) % barSec + barSec + barSec / 2) % barSec - barSec / 2);
      t.ok(Math.abs(tp.bpm - bpm) < 0.5, 'tempo ' + tp.bpm + ' vs ' + bpm);
      t.ok(err < 0.04, 'downbeat ' + ph.toFixed(3) + ' vs ' + off + ' (off by ' + (err * 1000).toFixed(0) + ' ms)');
      // a key or its relative (D major / B minor: the same notes, which is what the remix's bass needs)
      const tonicMaj = k.mode === 'major' ? k.key : (k.key + 3) % 12, want = minor ? (key + 3) % 12 : key;
      t.eq(tonicMaj, want, 'key ' + SG.NOTE_NAMES[k.key] + ' ' + k.mode + ' (or its relative) for ' + SG.NOTE_NAMES[key] + (minor ? ' minor' : ' major'));
      const sc = SG.SCALES[k.mode], pcs = RX.barRoots(x, sr, { bpm: tp.bpm, phase: ph, key: k.key, mode: k.mode }).slice(0, 4).map(d => SG.deg2midi(k.key, sc, d, 4) % 12);
      const tsc = SG.SCALES[minor ? 'minor' : 'major'];
      const first = Math.round((ph - off) / barSec), exp = [0, 1, 2, 3].map(i => [0, 5, 3, 4][(((first + i) % 4) + 4) % 4]);   // the downbeat found may be a later bar's
      t.eq(pcs, exp.map(d => SG.deg2midi(key, tsc, d, 4) % 12), 'bar roots (pitch classes) of i VI iv v / I vi IV V');
    }
    const x = synth(90, 9, true, 12, 0), R = SG.rng(3);
    const st = RX.stretchLayer([x, x], sr, 40, R);
    t.ok(st.channels[0].length === 40 * sr && st.channels.every(c => c.every(Number.isFinite)) && st.factor > 3, 'stretch ×' + st.factor.toFixed(1));
    let diff = 0; for (let i = sr * 10; i < sr * 11; i++) diff += Math.abs(st.channels[0][i] - st.channels[1][i]);
    t.ok(diff > 1, 'L and R decorrelated (wide)');
    const ch = RX.chopLayer([x, x], sr, { bpm: 90, phase: 0 }, 8, SG.rng(5), 0.6);
    t.ok(ch.channels[0].length === 8 * Math.round(240 / 90 * sr) && ch.srcBars.length === 8 && ch.channels[0].some(v => v !== 0), 'chop: 8 bars');
  });
  await t.test('tape machine: hysteresis harmonics grow with drive, unity small-signal gain, losses follow tape speed, wow moves pitch', async () => {
    const TM = require(path.join(TOOLS, 'tape_model.js')), sr = 48000;
    const sine = (f, amp, sec) => { const x = new Float32Array(Math.round(sec * sr)); for (let i = 0; i < x.length; i++) x[i] = amp * Math.sin(2 * Math.PI * f * i / sr); return x; };
    const harm = (y, f, h) => { const N = sr / 2, st = y.length - N; let re = 0, im = 0; for (let i = 0; i < N; i++) { re += y[st + i] * Math.cos(2 * Math.PI * f * h * i / sr); im += y[st + i] * Math.sin(2 * Math.PI * f * h * i / sr); } return 2 * Math.hypot(re, im) / N; };
    const flat = { wow: 0, flutter: 0, drift: 0, degrade: 0, chew: 0, loss: 0, bump: 0 };
    const thd = (amp, drive) => { const [y] = TM.process([sine(200, amp, 1)], sr, Object.assign({ drive }, flat)); return { g: harm(y, 200, 1) / amp, h3: 20 * Math.log10(harm(y, 200, 3) / harm(y, 200, 1)), h2: 20 * Math.log10(harm(y, 200, 2) / harm(y, 200, 1) + 1e-12) }; };
    const q = thd(0.01, 0.5), lo = thd(0.3, 0.2), mid = thd(0.3, 0.5), hi = thd(0.3, 0.9);
    t.ok(Math.abs(q.g - 1) < 0.05, 'small-signal gain ' + q.g.toFixed(3));
    t.ok(lo.h3 < mid.h3 && mid.h3 < hi.h3 && mid.h3 > -40 && mid.h3 < -20 && hi.h3 > -22, 'H3 rises with drive: ' + [lo.h3, mid.h3, hi.h3].map(x => x.toFixed(0)).join(' / ') + ' dB');
    t.ok(mid.h2 < -60, 'symmetric loop: no even harmonics (' + mid.h2.toFixed(0) + ' dB)');
    const at10k = id => TM.lossResponse(TM.machine(id), sr, [10000])[0];
    t.ok(at10k('master_30') > at10k('reel_7') && at10k('reel_7') > at10k('cassette') && at10k('cassette') > at10k('dictaphone'), 'slower / worse tape is darker at 10 kHz: ' + ['master_30', 'reel_7', 'cassette', 'dictaphone'].map(at10k).map(x => x.toFixed(1)).join(' > '));
    t.ok(Math.abs(TM.lossResponse(TM.machine('cassette'), sr, [100])[0]) < 0.5, 'lows untouched by the head losses');
    const dev = wow => { const [y] = TM.process([sine(1000, 0.1, 4)], sr, Object.assign({}, flat, { loss: 0, wow, drive: 0.3 })); const zc = []; for (let i = 1; i < y.length; i++) if (y[i - 1] < 0 && y[i] >= 0) zc.push(i - y[i] / (y[i] - y[i - 1])); const fs = []; for (let i = 501; i < zc.length; i++) fs.push(sr / (zc[i] - zc[i - 1])); return Math.max(...fs) - Math.min(...fs); };
    const d1 = dev(0.25), d2 = dev(0.75);
    t.ok(d1 > 0.3 && d2 > 4 * d1, 'wow pitch swing ' + d1.toFixed(2) + ' Hz → ' + d2.toFixed(2) + ' Hz');
  });
  await t.test('tape machine: seeded, safe under abuse, seamless loops, stems through one transport', async () => {
    const TM = require(path.join(TOOLS, 'tape_model.js')), sr = 48000, R = require(path.join(TOOLS, 'seqgen.js')).rng(9);
    const x = new Float32Array(sr * 2).map((_, i) => 0.5 * Math.sin(i * 0.03) + 0.2 * (R() - 0.5));
    const m = Object.assign(TM.machine('chewed'), { seed: 7 });
    const a = TM.process([x, x], sr, m), b = TM.process([x, x], sr, m), c = TM.process([x, x], sr, Object.assign({}, m, { seed: 8 }));
    t.ok(a[0].every((v, i) => v === b[0][i]) && a[0].some((v, i) => v !== c[0][i]), 'same seed → same tape; another seed → another');
    const wild = new Float32Array(sr).map(() => (R() - 0.5) * 20);
    const w = TM.process([wild, wild], sr, { drive: 1, sat: 1, bias: 0, in: 24, chew: 1, chewFreq: 1, degrade: 1, wow: 1, flutter: 1 });
    t.ok(w.every(ch => ch.every(Number.isFinite)) && Math.max(...w[0].map(Math.abs)) < 20, 'finite and bounded when slammed');
    // a loop: the wrap continues as smoothly as the rest of the signal
    const L = sr, loop = new Float32Array(L).map((_, i) => 0.4 * Math.sin(2 * Math.PI * 110 * i / L * Math.round(L / sr * 1)));
    const lp = TM.processLoop([loop, loop], sr, TM.machine('cassette'));
    const d = lp[0], jumps = []; for (let i = 1; i < d.length; i++) jumps.push(Math.abs(d[i] - d[i - 1]));
    const wrap = Math.abs(d[0] - d[d.length - 1]), typical = jumps.sort((p, q) => p - q)[Math.floor(jumps.length * 0.99)];
    t.ok(lp[0].length === L && wrap <= typical * 1.5, 'loop wrap step ' + wrap.toFixed(4) + ' vs 99th-percentile step ' + typical.toFixed(4));
    // stems: identical stems come out identical (one transport); hiss is shared out
    const st = TM.processStems([[x, x], [x, x]], sr, Object.assign(TM.machine('worn_cassette'), { seed: 3 }));
    t.ok(st[0][0].every((v, i) => v === st[1][0][i]), 'two stems, one machine: sample-identical');
  });
  await t.test('remix: transcription cleanup drops overtones and phantom sub-octaves, keeps a melody doubling a held chord tone', async () => {
    const RX = require(path.join(TOOLS, 'remix.js'));
    const notes = [
      { t: 0, d: 1, n: 57, v: 0.8 }, { t: 0.01, d: 0.9, n: 69, v: 0.4 }, { t: 0.0, d: 0.9, n: 76, v: 0.3 },   // A3 + its octave and 12th overtones
      { t: 0, d: 1, n: 45, v: 0.4 },                                                                        // a phantom octave under it
      { t: 0.5, d: 0.3, n: 81, v: 0.6 },                                                                    // a melody note over the held chord (own onset)
      { t: 2, d: 0.2, n: 64, v: 0.1 }];                                                                     // too faint
    t.eq(RX.cleanNotes(notes).map(x => x.n), [57, 81]);
  });
  await t.test('MIDI file write → read round trip (incl. same-pitch overlaps)', async () => {
    const notes = [{ t: 0, d: 96, n: 60, v: 0.8 }, { t: 48, d: 96, n: 60, v: 0.5 }, { t: 96, d: 48, n: 64, v: 1 }];
    const back = SMF.read(SMF.write([{ name: 'x', channel: 10, notes }], { ppq: 96, bpm: 123 }));
    t.eq(back.bpm, 123); t.eq(back.tracks[0].channel, 10);
    t.eq(back.tracks[0].notes.map(n => [n.t, n.d, n.n]), [[0, 48, 60], [48, 96, 60], [96, 48, 64]], 'overlap trimmed');
  });
});
