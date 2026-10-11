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
  });

  const SMF = require(path.join(TOOLS, 'smf.js'));
  await t.test('MIDI file write → read round trip (incl. same-pitch overlaps)', async () => {
    const notes = [{ t: 0, d: 96, n: 60, v: 0.8 }, { t: 48, d: 96, n: 60, v: 0.5 }, { t: 96, d: 48, n: 64, v: 1 }];
    const back = SMF.read(SMF.write([{ name: 'x', channel: 10, notes }], { ppq: 96, bpm: 123 }));
    t.eq(back.bpm, 123); t.eq(back.tracks[0].channel, 10);
    t.eq(back.tracks[0].notes.map(n => [n.t, n.d, n.n]), [[0, 48, 60], [48, 96, 60], [96, 48, 64]], 'overlap trimmed');
  });
});
