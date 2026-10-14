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
    t.eq(SG.soundsFromText('Bowed cello single note, dampened.').voices.lead, 'strings_noir');
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
  const SMF = require(path.join(TOOLS, 'smf.js'));
  await t.test('MIDI file write → read round trip (incl. same-pitch overlaps)', async () => {
    const notes = [{ t: 0, d: 96, n: 60, v: 0.8 }, { t: 48, d: 96, n: 60, v: 0.5 }, { t: 96, d: 48, n: 64, v: 1 }];
    const back = SMF.read(SMF.write([{ name: 'x', channel: 10, notes }], { ppq: 96, bpm: 123 }));
    t.eq(back.bpm, 123); t.eq(back.tracks[0].channel, 10);
    t.eq(back.tracks[0].notes.map(n => [n.t, n.d, n.n]), [[0, 48, 60], [48, 96, 60], [96, 48, 64]], 'overlap trimmed');
  });
});
