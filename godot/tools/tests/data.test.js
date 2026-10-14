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
  const SMF = require(path.join(TOOLS, 'smf.js'));
  await t.test('MIDI file write → read round trip (incl. same-pitch overlaps)', async () => {
    const notes = [{ t: 0, d: 96, n: 60, v: 0.8 }, { t: 48, d: 96, n: 60, v: 0.5 }, { t: 96, d: 48, n: 64, v: 1 }];
    const back = SMF.read(SMF.write([{ name: 'x', channel: 10, notes }], { ppq: 96, bpm: 123 }));
    t.eq(back.bpm, 123); t.eq(back.tracks[0].channel, 10);
    t.eq(back.tracks[0].notes.map(n => [n.t, n.d, n.n]), [[0, 48, 60], [48, 96, 60], [96, 48, 64]], 'overlap trimmed');
  });
});
