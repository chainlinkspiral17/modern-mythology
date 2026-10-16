// AUDIO DIRECTOR: statuses, ordering, the AudioMgr-exact stem preview, A/B, PLAY AS SCENE, approve / reject /
// revoke into a shimmed game folder, real-audio protection, the DAW's review staging + request round trip with
// creative direction (description, instruments, length, parts, extra pads), finger controls. Takes are small
// synthesized WAVs; the DAW renders 2-bar / 7-second takes, so the suite stays fast.
const { suite } = require('./harness');
const fs = require('fs'), os = require('os'), path = require('path');

const GAME = fs.mkdtempSync(path.join(os.tmpdir(), 'mmdirector-'));
const G = rel => path.join(GAME, rel);
const put = (rel, data) => { fs.mkdirSync(path.dirname(G(rel)), { recursive: true }); fs.writeFileSync(G(rel), data); };
const json = rel => JSON.parse(fs.readFileSync(G(rel), 'utf8'));
// a plain 16-bit WAV with no temp marker — what FIELD RECORDER / a hand-made file looks like to the director
function plainWav(sec = 1, sr = 22050) {
  const n = sec * sr, b = Buffer.alloc(44 + n * 2);
  b.write('RIFF', 0); b.writeUInt32LE(36 + n * 2, 4); b.write('WAVE', 8); b.write('fmt ', 12); b.writeUInt32LE(16, 16);
  b.writeUInt16LE(1, 20); b.writeUInt16LE(1, 22); b.writeUInt32LE(sr, 24); b.writeUInt32LE(sr * 2, 28); b.writeUInt16LE(2, 32); b.writeUInt16LE(16, 34);
  b.write('data', 36); b.writeUInt32LE(n * 2, 40);
  for (let i = 0; i < n; i++) b.writeInt16LE(Math.round(8000 * Math.sin(2 * Math.PI * 330 * i / sr)), 44 + i * 2);
  return b;
}
// an Ogg file's length in frames: the granule position of its last page
const oggFrames = rel => { const b = fs.readFileSync(G(rel)); const i = b.lastIndexOf('OggS'); return Number(b.readBigInt64LE(i + 6)); };
const isOgg = rel => fs.readFileSync(G(rel)).toString('ascii', 0, 4) === 'OggS';
const MB_MIN = (rel, sec) => fs.statSync(G(rel)).size / sec * 60 / 1048576;
const wavFrames = rel => { const b = fs.readFileSync(G(rel)); let o = 12; while (o < b.length) { const id = b.toString('ascii', o, o + 4), sz = b.readUInt32LE(o + 4); if (id === 'data') return sz / 4; o += 8 + sz + (sz & 1); } return -1; };

// ── fixture game folder ─────────────────────────────────────────────
const CAT = [
  { id: 'tem_theme', vol: 7, title: 'Tem', src: 'assets/audio/bgm/tem_theme.ogg', desc: 'A character theme. Warm, a little tired.' },
  { id: 'sam_theme', vol: 6, title: 'Sam', src: 'assets/audio/bgm/sam_theme.ogg', desc: 'A character theme for Sam.' },
  { id: 'real_track', vol: 2, title: 'Real One', src: 'assets/audio/bgm/real_track.ogg', desc: 'Already composed.' },
  { id: 'old_temp', vol: 3, title: 'Old Temp', src: 'assets/audio/bgm/old_temp.ogg', desc: 'Ambient room tone.' },
  { id: 'field_rec', vol: 3, title: 'Field', src: 'assets/audio/bgm/field_rec.ogg', desc: 'Rain on the porch.' },
  { id: 'quiet_bed', vol: 1, title: 'Quiet Bed', src: 'assets/audio/bgm/quiet_bed.ogg', desc: 'Nobody plays this one.' },
];
const brief = (id, n, roles, extra) => Object.assign({ id, scene_count: n, scenes: [], roles, baseline: 0.5, intensity: { p10: 0.3, mean: 0.5, p90: 0.8 }, stems: true, words: ['rain'], chars: [], locales: ['cabin'], moments: { choice: 1 }, energy: 0.5, darkness: 0.5, curves: {} }, extra || {});
put('resources/music_catalog.json', JSON.stringify(CAT));
put('resources/music/temp_briefs.json', JSON.stringify({ tracks: [
  brief('tem_theme', 29, { leitmotif: 29 }, { chars: ['tem'], scenes: ['vol7_ch1_test', 'vol7_ch2_nofile'], curves: { vol7_ch1_test: { n: 6, at: [0, 2, 4], v: [0.2, 0.9, 0.4] }, vol7_ch2_nofile: { n: 4, at: [0], v: [0.5] } } }),
  brief('sam_theme', 22, { leitmotif: 22 }, { chars: ['sam'] }),
  brief('old_temp', 5, { locale: 5 }), brief('real_track', 3, { bgm: 3 }), brief('field_rec', 2, { locale: 2 })] }));
put('resources/music/direction.json', JSON.stringify({ defaults: { attack_sec: 2.5, release_sec: 8 } }));
put('resources/scenes/vol7/vol7_ch1_test.json', JSON.stringify({ id: 'vol7_ch1_test', vol: 7, nodes: [
  { t: 'narrate', text: 'The kitchen was quiet.' }, { t: 'say', char: 'tem', text: 'Coffee?' },
  { t: 'narrate', text: 'Then the siren started.' }, { t: 'choice', options: [{ text: 'Run' }, { text: 'Stay' }] },
  { t: 'narrate', text: 'It passed.' }, { t: 'think', char: 'tem', text: 'Still here.' }] }));
put('assets/audio/bgm/real_track.ogg', Buffer.from('OggS-not-really-but-real'));
put('assets/audio/bgm/field_rec.wav', plainWav());
put('project.godot', '; stub');

const shim = {
  __gx: rel => { try { return fs.statSync(G(rel)).isFile(); } catch (e) { return false; } },
  __gr: rel => fs.readFileSync(G(rel), 'utf8'),
  __gb: rel => fs.readFileSync(G(rel)).toString('base64'),
  __gw: (rel, b64) => { put(rel, Buffer.from(b64, 'base64')); return true; },
  __gl: rel => { try { return fs.readdirSync(G(rel), { withFileTypes: true }).map(d => ({ name: d.name, kind: d.isDirectory() ? 'directory' : 'file' })); } catch (e) { return []; } },
  __grm: rel => { if (!fs.existsSync(G(rel))) return false; fs.rmSync(G(rel), { recursive: true, force: true }); return true; },
};
// the linked godot/ folder → node fs, in every page of the context (pop-ups too), installed once the
// page's own scripts have run
const ctxInit = () => {
  window.addEventListener('DOMContentLoaded', () => {
    if (typeof AK === 'undefined') return;
    const g = AK.game;
    g.root = { name: 'test-game' };
    g.restore = async () => g.root;
    g.exists = rel => window.__gx(rel);
    g.readText = rel => window.__gr(rel);
    g.readFile = async rel => { const b = atob(await window.__gb(rel)), u = new Uint8Array(b.length); for (let i = 0; i < b.length; i++) u[i] = b.charCodeAt(i); return new Blob([u]); };
    g.list = async rel => (await window.__gl(rel)).sort((a, b) => a.name < b.name ? -1 : 1);
    g.remove = rel => window.__grm(rel);
    g.write = async (rel, blob) => { const u = new Uint8Array(await blob.arrayBuffer()); let s = ''; for (let i = 0; i < u.length; i += 0x8000) s += String.fromCharCode.apply(null, u.subarray(i, i + 0x8000)); await window.__gw(rel, btoa(s)); return rel; };
  });
};

// a synthesized take in review staging, written the way the DAW writes one (stems of distinct tones)
async function mkTake(p, id, take, seed, o = {}) {
  return p.evaluate(async ({ id, take, seed, o }) => {
    const sr = 22050, sec = o.sec || 6, n = sec * sr, dir = 'assets/audio/review/' + id + '/' + take + '/';
    const roles = [['drums', 0.5, 110], ['bass', 0.25, 55], ['chords', 0, 220], ['lead', 0.75, 440], ['pad', 0, 330]];
    const tone = f => { const c = new Float32Array(n), k = 1 + (seed % 7) / 50; for (let i = 0; i < n; i++) c[i] = 0.12 * Math.sin(2 * Math.PI * f * k * i / sr); return [c, c.slice()]; };
    const enc = (chs, title) => AK.wav.encode(chs, sr, { bitDepth: 16, meta: { title: title + ' (temp)', temp: true, forTrack: id, take } });
    const mix = [new Float32Array(n), new Float32Array(n)], man = { v: 1, title: id + ' (temp)', stems: [], mix: dir + 'mix.wav' }, files = ['mix.wav'];
    if (o.stems !== false) for (const [r, layer, f] of roles) { const t = tone(f); for (let c = 0; c < 2; c++) for (let i = 0; i < n; i++) mix[c][i] += t[c][i]; await AK.game.write(dir + 'stems/' + r + '.wav', enc(t, id + ' · ' + r)); man.stems.push({ name: r, role: r, file: dir + 'stems/' + r + '.wav', layer }); files.push('stems/' + r + '.wav'); }
    else { const t = tone(262); mix[0].set(t[0]); mix[1].set(t[1]); }
    await AK.game.write(dir + 'mix.wav', enc(mix, id));
    if (man.stems.length) { await AK.game.write(dir + 'stems.json', new Blob([JSON.stringify(man)])); files.push('stems.json'); }
    const meta = { v: 1, id, take, created: o.created || new Date().toISOString(), status: 'candidate', title: id, src: 'assets/audio/bgm/' + id + '.ogg',
      mood: { style: 'noir', form: 'song', mode: 'minor', key: 2, bpm: 72, density: 0.5, seed }, why: 'fixture', request: o.request || {}, instruments: { lead: 'forge:x' },
      lufs: -14, true_peak: -1.6, seconds: sec, bars: 2, stems: man.stems.map(s => ({ name: s.name, role: s.role, layer: s.layer })), files };
    await AK.game.write(dir + 'meta.json', new Blob([JSON.stringify(meta)]));
    return dir;
  }, { id, take, seed, o });
}

suite('audio_director · review, preview, approve, DAW takes', async t => {
  const { p, ctx, errors, cdp } = await t.page('audio_director.html', { touch: true, expose: shim, ctxInit, settle: 200 });
  const f = t.touch(cdp);
  await mkTake(p, 'tem_theme', 'take-a', 1111, { created: '2026-10-11T10:00:00Z' });
  await mkTake(p, 'tem_theme', 'take-b', 2222, { created: '2026-10-11T10:05:00Z' });
  await mkTake(p, 'real_track', 'take-r', 3333);
  await mkTake(p, 'field_rec', 'take-f', 4444, { stems: false });
  // a legacy approved temp: TEMP TRACKS wrote it straight into the game before review staging existed
  await p.evaluate(async () => {
    const sr = 22050, c = new Float32Array(sr); for (let i = 0; i < sr; i++) c[i] = 0.1 * Math.sin(i / 9);
    await AK.game.write('assets/audio/bgm/old_temp.wav', AK.wav.encode([c, c], sr, { meta: { title: 'Old Temp (temp)' } }));
    await AK.game.write('assets/audio/bgm/old_temp.stems/pad.wav', AK.wav.encode([c, c], sr, { meta: { title: 'Old Temp (temp) · pad' } }));
    await AK.game.write('assets/audio/bgm/old_temp.stems.json', new Blob([JSON.stringify({ stems: [{ name: 'pad', file: 'assets/audio/bgm/old_temp.stems/pad.wav', layer: 0 }] })]));
  });
  await p.evaluate(() => refresh());

  await t.test('statuses: missing / candidates / approved temp / real audio (.ogg and a non-temp .wav)', async () => {
    const r = await p.evaluate(() => Object.fromEntries(Object.keys(DIR.state).sort().map(k => [k, DIR.state[k].status + ':' + DIR.state[k].cand])));
    t.eq(r, { field_rec: 'real:1', old_temp: 'approved:0', quiet_bed: 'missing:0', real_track: 'real:1', sam_theme: 'missing:0', tem_theme: 'candidates:2' });
    const shown = await p.evaluate(() => document.getElementById('b-counts').textContent);
    t.ok(/6 tracks · 2 missing · 3 with candidates · 1 approved temp · 2 real/.test(shown), shown);
  });
  await t.test('ordering: most-played first, with the why; filters + search', async () => {
    const r = await p.evaluate(() => ({ order: DIR.order.map(x => x.id), rows: [...document.querySelectorAll('#list .tr')].map(e => e.dataset.id), first: document.querySelector('#list .tr i').textContent }));
    t.eq(r.order, ['tem_theme', 'sam_theme', 'old_temp', 'real_track', 'field_rec', 'quiet_bed']);
    t.eq(r.rows, r.order);
    t.ok(/29 scenes · leitmotif 29 · energy 50% · dark 50% · theme: tem/.test(r.first), r.first);
    const miss = await p.evaluate(() => { document.querySelector('[data-f="missing"]').click(); const a = [...document.querySelectorAll('#list .tr')].map(e => e.dataset.id); document.querySelector('[data-f="all"]').click();
      document.getElementById('q').value = 'sam'; document.getElementById('q').dispatchEvent(new Event('input')); const b = [...document.querySelectorAll('#list .tr')].map(e => e.dataset.id);
      document.getElementById('q').value = ''; document.getElementById('q').dispatchEvent(new Event('input')); return { a, b }; });
    t.eq(miss.a, ['sam_theme', 'quiet_bed']); t.eq(miss.b, ['sam_theme']);
  });

  await p.evaluate(() => selectTrack('tem_theme'));
  await t.test('preview graph: stem gains at intensity 0 / .25 / .5 / .75 / 1 follow AudioMgr\'s layers', async () => {
    const r = await p.evaluate(async () => {
      await pickTake(0, { autoplay: true });
      const out = {};
      for (const lv of [0, 0.25, 0.5, 0.75, 1]) { PV.setIntensity(lv, 0); await new Promise(r => setTimeout(r, 60)); out[lv] = PV.layerGains().map(l => l.name + '=' + Math.round(l.gain)).join(' '); }
      return out;
    });
    t.eq(r[0], 'drums=0 bass=0 chords=1 lead=0 pad=1');
    t.eq(r[0.25], 'drums=0 bass=1 chords=1 lead=0 pad=1');
    t.eq(r[0.5], 'drums=1 bass=1 chords=1 lead=0 pad=1');
    t.eq(r[0.75], 'drums=1 bass=1 chords=1 lead=1 pad=1');
    t.eq(r[1], 'drums=1 bass=1 chords=1 lead=1 pad=1');
  });
  await t.test('preview graph: fades are linear at 1 / fade per second (AudioMgr move_toward)', async () => {
    const g = await p.evaluate(async () => { PV.setIntensity(1, 0); await new Promise(r => setTimeout(r, 50)); PV.setIntensity(0, 1.5); await new Promise(r => setTimeout(r, 450)); return PV.layerGains().find(l => l.name === 'lead').gain; });
    t.ok(g > 0.55 && g < 0.85, 'lead after 0.45 s of a 1.5 s fade: ' + g.toFixed(3));
  });
  await t.test('A/B: switching takes keeps the position', async () => {
    const r = await p.evaluate(async () => {
      PV.setIntensity(1, 0); PV.seek(2.0); await new Promise(r => setTimeout(r, 400));
      // A keeps playing while B decodes; the switch lands B where A was at that moment
      const a = PV.position(), ta = PV.take.take; await pickTake(1); const b = PV.position(), sw1 = DIR.lastAB, tb = PV.take.take, playing = PV.playing;
      await new Promise(r => setTimeout(r, 300)); await pickTake(0); const c = PV.position(), sw2 = DIR.lastAB; return { a, b, c, sw1, sw2, ta, tb, playing };
    });
    t.eq([r.ta, r.tb, r.sw1.from, r.sw2.from], ['take-a', 'take-b', 'take-a', 'take-b']); t.ok(r.playing, 'still playing');
    t.ok(r.sw1.at >= r.a - 0.01, `switched at ${r.sw1.at.toFixed(3)} after ${r.a.toFixed(3)}`);
    t.ok(Math.abs(r.b - r.sw1.at) < 0.08, `A ${r.sw1.at.toFixed(3)} → B ${r.b.toFixed(3)}`);
    t.ok(Math.abs(r.c - r.sw2.at) < 0.08 && r.sw2.at > r.b + 0.2, `B ${r.sw2.at.toFixed(3)} → A ${r.c.toFixed(3)}`);
  });
  await t.test('PLAY AS SCENE: the curve drives intensity with the director\'s attack / release, lines follow', async () => {
    const r = await p.evaluate(async () => {
      const ok = await sceneStart('vol7_ch1_test', { manual: true });
      const s = []; const snap = () => s.push({ idx: SC.idx, target: +SC.target.toFixed(3), level: +SC.level.toFixed(3), pv: +PV.intensity.toFixed(3), on: PV.layerGains().filter(l => l.target).map(l => l.name).join('+'), line: document.getElementById('line').textContent });
      sceneTick(0.01); snap();                                                     // node 0: 0.2
      while (SC.idx < 2) sceneTick(0.05); snap();                                  // node 2: target 0.9, rising
      sceneTick(1.0); snap();                                                      // 1 s of a 2.5 s attack: +0.4
      for (let k = 0; k < 40; k++) sceneTick(0.05); snap();                        // settled at 0.9 (all layers)
      sceneTick(SC.timeline[4].t0 - SC.t + 0.001); for (let k = 0; k < 200; k++) sceneTick(0.1); snap();   // node 4: 0.4 after the 8 s release
      return { ok, s };
    });
    t.ok(r.ok, 'scene started');
    const [a, b, c, d, e] = r.s;
    t.eq([a.idx, a.target, a.pv, a.on], [0, 0.2, 0.2, 'chords+pad']); t.ok(/kitchen was quiet/.test(a.line), a.line);
    t.eq([b.idx, b.target], [2, 0.9]); t.ok(/siren/.test(b.line), b.line);
    t.near(c.level, b.level + 0.4, 0.03, 'attack 2.5 s');
    t.eq([d.level, d.pv, d.on], [0.9, 0.9, 'drums+bass+chords+lead+pad']);
    t.eq([e.idx, e.target, e.level, e.pv, e.on], [5, 0.4, 0.4, 0.4, 'bass+chords+pad']);
    await p.evaluate(() => { sceneStop(); PV.stop(); });
  });

  await t.test('APPROVE encodes the take to small Ogg Vorbis files — exactly what AudioMgr reads — + temp_approvals.json', async () => {
    const before = fs.readdirSync(G('assets/audio/bgm')).sort();
    const r = await p.evaluate(async () => { document.getElementById('who').value = 'tester'; document.getElementById('notes').value = 'first pass'; return approve(0); });
    t.ok(r.ok, JSON.stringify(r));
    const added = fs.readdirSync(G('assets/audio/bgm')).sort().filter(x => !before.includes(x));
    t.eq(added, ['tem_theme.stems', 'tem_theme.stems.json', 'tem_theme.temp.ogg']);
    t.eq(fs.readdirSync(G('assets/audio/bgm/tem_theme.stems')).sort(), ['bass.ogg', 'chords.ogg', 'drums.ogg', 'lead.ogg', 'pad.ogg']);
    const man = json('assets/audio/bgm/tem_theme.stems.json');
    t.eq([man.mix, man.temp, man.format, man.loop, man.loop_offset, man.frames], ['assets/audio/bgm/tem_theme.temp.ogg', true, 'ogg', false, 0, 6 * 22050]);
    t.eq(man.stems.map(s => s.name + '@' + s.layer), ['drums@0.5', 'bass@0.25', 'chords@0', 'lead@0.75', 'pad@0']);
    for (const s of man.stems) t.ok(fs.existsSync(G(s.file)) && s.file.startsWith('assets/audio/bgm/tem_theme.stems/') && isOgg(s.file), s.file);
    t.ok(isOgg('assets/audio/bgm/tem_theme.temp.ogg'), 'the mix is Ogg');
    t.eq(oggFrames('assets/audio/bgm/tem_theme.temp.ogg'), 6 * 22050, 'sample-exact length (last granule)');
    for (const s of man.stems) t.eq(oggFrames(s.file), 6 * 22050, s.name + ' length');
    const mix = MB_MIN('assets/audio/bgm/tem_theme.temp.ogg', 6), stem = Math.max(...man.stems.map(s => MB_MIN(s.file, 6)));
    t.ok(mix < 1.3 && stem < 0.8, `mix ${mix.toFixed(2)} MB/min, biggest stem ${stem.toFixed(2)} MB/min`);
    t.ok(r.bytes * 8 < r.wavBytes, `Ogg ${r.bytes} B vs the take's WAVs ${r.wavBytes} B`);
    t.ok(!fs.existsSync(G('assets/audio/bgm/tem_theme.ogg')) && !fs.existsSync(G('assets/audio/bgm/tem_theme.wav')), 'the real src path untouched, no .wav');
    const ap = json('resources/music/temp_approvals.json').tracks.tem_theme;
    t.eq([ap.approved.take, ap.approved.seed, ap.approved.by, ap.approved.notes, ap.approved.mood.style], ['take-a', 1111, 'tester', 'first pass', 'noir']);
    t.eq([ap.approved.format, ap.approved.bytes, ap.approved.quality], ['ogg', r.bytes, { mix: 4, stem: 1 }]);
    t.eq(ap.approved.files.length, 7); t.eq(ap.history.map(h => h.action), ['approve']);
    t.eq(json('assets/audio/review/tem_theme/take-a/meta.json').status, 'approved');
    t.eq(await p.evaluate(() => DIR.state.tem_theme.status), 'approved');
  });
  await t.test('real audio is never overwritten: a real .ogg refuses; a .wav that is not a temp is described, and a second tap moves it aside (kept) and approves', async () => {
    const ogg = fs.readFileSync(G('assets/audio/bgm/real_track.ogg')), wav = fs.readFileSync(G('assets/audio/bgm/field_rec.wav'));
    const r = await p.evaluate(async () => { await selectTrack('real_track'); const a = await approve(0); await approve(0); await selectTrack('field_rec'); const b = await approve(0); return { a, b, msg: document.getElementById('msg').textContent }; });
    t.eq([r.a.why, r.b.why], ['real', 'real-wav']);
    t.ok(/is not a temp \(/.test(r.msg) && /MB\)/.test(r.msg) && /Tap APPROVE again/.test(r.msg), r.msg);
    t.ok(!fs.existsSync(G('assets/audio/bgm/real_track.wav')) && !fs.existsSync(G('assets/audio/bgm/real_track.temp.ogg')), 'no temp next to the real .ogg');
    t.ok(!fs.existsSync(G('assets/audio/bgm/field_rec.temp.ogg')), 'one tap: no temp next to the real .wav');
    t.ok(fs.readFileSync(G('assets/audio/bgm/real_track.ogg')).equals(ogg) && fs.readFileSync(G('assets/audio/bgm/field_rec.wav')).equals(wav), 'real files unchanged');
    const c = await p.evaluate(async () => approve(0));
    t.ok(c.ok, JSON.stringify(c));
    const kept = fs.readdirSync(G('assets/audio/replaced')).filter(f => /^field_rec\..*\.wav$/.test(f));
    t.eq(kept.length, 1, 'moved aside: ' + kept);
    t.ok(fs.readFileSync(G('assets/audio/replaced/' + kept[0])).equals(wav), 'kept byte for byte');
    t.ok(fs.existsSync(G('assets/audio/replaced/.gdignore')), 'Godot ignores the folder');
    t.ok(!fs.existsSync(G('assets/audio/bgm/field_rec.wav')) && fs.existsSync(G('assets/audio/bgm/field_rec.temp.ogg')), 'the take is the game\'s temp now');
    const h = json('resources/music/temp_approvals.json').tracks.field_rec.history.slice(-1)[0];
    t.ok(h.moved_aside && h.moved_aside.some(x => /field_rec\.wav → assets\/audio\/replaced\//.test(x)), JSON.stringify(h));
    // put it back so the later tests see the fixture as it was
    fs.renameSync(G('assets/audio/replaced/' + kept[0]), G('assets/audio/bgm/field_rec.wav'));
    for (const f of fs.readdirSync(G('assets/audio/bgm')).filter(f => f.startsWith('field_rec') && f !== 'field_rec.wav')) fs.rmSync(G('assets/audio/bgm/' + f), { recursive: true, force: true });
    await p.evaluate(() => refresh());
  });
  await t.test('replacing an approved temp takes two taps', async () => {
    const was = fs.readFileSync(G('assets/audio/bgm/tem_theme.temp.ogg'));
    const r = await p.evaluate(async () => { await selectTrack('tem_theme'); const first = await approve(1); return first; });
    t.eq(r.why, 'confirm');
    t.ok(fs.readFileSync(G('assets/audio/bgm/tem_theme.temp.ogg')).equals(was), 'one tap changed nothing');
    const r2 = await p.evaluate(() => approve(1));
    t.ok(r2.ok, JSON.stringify(r2));
    t.ok(!fs.readFileSync(G('assets/audio/bgm/tem_theme.temp.ogg')).equals(was), 'second tap replaced it');
    t.eq(json('assets/audio/bgm/tem_theme.stems.json').approved.take, 'take-b');
    const ap = json('resources/music/temp_approvals.json').tracks.tem_theme;
    t.eq([ap.approved.take, ap.history.map(h => h.action).join()], ['take-b', 'approve,replace']);
    t.eq([json('assets/audio/review/tem_theme/take-a/meta.json').status, json('assets/audio/review/tem_theme/take-b/meta.json').status], ['candidate', 'approved']);
  });
  await t.test('REJECT (two taps) records the seed; with "deletes files" the take folder goes', async () => {
    const r = await p.evaluate(async () => { const i = DIR.takes.findIndex(m => m.take === 'take-a'); const a = await reject(i); const b = await reject(i); return { a, b, st: DIR.state.tem_theme.cand, shown: DIR.takes.map(m => m.take) }; });
    t.eq([r.a.why, r.b.ok], ['confirm', true]); t.eq(r.st, 1); t.eq(r.shown, ['take-b']);
    t.eq(json('assets/audio/review/tem_theme/take-a/meta.json').status, 'rejected');
    const ap = json('resources/music/temp_approvals.json').tracks.tem_theme;
    t.eq(ap.rejected.map(x => x.take + ':' + x.seed), ['take-a:1111']);
    const r2 = await p.evaluate(async () => { await selectTrack('real_track'); document.getElementById('rejdel').checked = true; await reject(0); const x = await reject(0); document.getElementById('rejdel').checked = false; return x; });
    t.ok(r2.ok); t.ok(!fs.existsSync(G('assets/audio/review/real_track/take-r')), 'take folder deleted');
    t.eq(json('resources/music/temp_approvals.json').tracks.real_track.rejected[0].seed, 3333);
  });
  await t.test('REVOKE removes only an approved temp (two taps) — an older .wav one or an Ogg one — never real audio', async () => {
    const r = await p.evaluate(async () => { await selectTrack('old_temp'); const a = await revoke(); const b = await revoke(); await selectTrack('field_rec'); const c = await revoke(); await revoke(); return { a, b, c, st: DIR.state.old_temp.status }; });
    t.eq([r.a.why, r.b.ok, r.c.why, r.st], ['confirm', true, 'real', 'missing']);
    for (const f of ['old_temp.wav', 'old_temp.stems.json', 'old_temp.stems']) t.ok(!fs.existsSync(G('assets/audio/bgm/' + f)), f + ' removed');
    t.ok(fs.existsSync(G('assets/audio/bgm/field_rec.wav')), 'the field recording stays');
    t.eq(json('resources/music/temp_approvals.json').tracks.old_temp.history.map(h => h.action), ['revoke']);
    const o = await p.evaluate(async () => { await selectTrack('tem_theme'); await revoke(); const x = await revoke(); return { x, st: DIR.state.tem_theme.status }; });
    t.ok(o.x.ok, JSON.stringify(o.x)); t.eq(o.st, 'candidates');
    t.eq(o.x.removed.sort(), ['assets/audio/bgm/tem_theme.stems', 'assets/audio/bgm/tem_theme.stems.json', 'assets/audio/bgm/tem_theme.temp.ogg']);
    t.eq(fs.readdirSync(G('assets/audio/bgm')).filter(f => f.startsWith('tem_theme')), [], 'nothing of the temp left');
  });
  await t.test('SHRINK: every older WAV temp → Ogg in place (stems, credits, approval record), real audio untouched', async () => {
    const field = fs.readFileSync(G('assets/audio/bgm/field_rec.wav'));
    await p.evaluate(async () => {   // a WAV temp approved before Ogg: mix + 2 stems + manifest + credits + an approval record
      const sr = 22050, n = sr * 3, mk = f => { const c = new Float32Array(n); for (let i = 0; i < n; i++) c[i] = 0.2 * Math.sin(2 * Math.PI * f * i / sr); return [c, c.slice()]; };
      const B = 'assets/audio/bgm/old_temp';
      await AK.game.write(B + '.wav', AK.wav.encode(mk(220), sr, { bitDepth: 16, loop: { start: 0, end: n - 1 }, meta: { title: 'Old Temp (temp)', temp: true } }));
      for (const [r, f] of [['pad', 110], ['lead', 440]]) await AK.game.write(B + '.stems/' + r + '.wav', AK.wav.encode(mk(f), sr, { bitDepth: 16, meta: { title: 'Old Temp (temp) · ' + r } }));
      await AK.game.write(B + '.stems.json', new Blob([JSON.stringify({ v: 1, title: 'Old Temp (temp)', bpm: 80, loop: true, mix: B + '.wav', stems: [{ name: 'pad', role: 'pad', file: B + '.stems/pad.wav', layer: 0 }, { name: 'lead', role: 'lead', file: B + '.stems/lead.wav', layer: 0.75 }] })]));
      await AK.game.write(B + '.wav.credits.txt', new Blob(['lead: some sampler, CC-BY\n']));
      const ap = await readApprovals(); ap.tracks.old_temp.approved = { take: 'legacy-take', seed: 5, files: [B + '.wav'] }; await writeApprovals(ap);
      await refresh();
    });
    const before = await p.evaluate(() => ({ st: DIR.state.old_temp.temp, label: document.getElementById('shrink').textContent, dis: document.getElementById('shrink').disabled }));
    t.eq(before, { st: 'wav', label: '⇣ SHRINK 1 WAV TEMP → OGG', dis: false });
    const r = await p.evaluate(() => shrinkAll());
    t.ok(r.ok && r.done.length === 1, JSON.stringify(r));
    const B = 'assets/audio/bgm/old_temp';
    t.eq(fs.readdirSync(G('assets/audio/bgm')).filter(f => f.startsWith('old_temp')).sort(), ['old_temp.stems', 'old_temp.stems.json', 'old_temp.temp.ogg', 'old_temp.temp.ogg.credits.txt']);
    t.eq(fs.readdirSync(G(B + '.stems')).sort(), ['lead.ogg', 'pad.ogg'], 'WAV stems replaced');
    const man = json(B + '.stems.json');
    t.eq([man.temp, man.format, man.mix, man.loop, man.loop_offset, man.frames, man.bpm, man.shrunk_from], [true, 'ogg', B + '.temp.ogg', true, 0, 3 * 22050, 80, 'wav']);
    t.eq(man.stems.map(s => s.file), [B + '.stems/pad.ogg', B + '.stems/lead.ogg']);
    t.eq(oggFrames(B + '.temp.ogg'), 3 * 22050, 'loop end = stream end');
    t.ok(/CC-BY/.test(fs.readFileSync(G(B + '.temp.ogg.credits.txt'), 'utf8')), 'credits moved');
    t.ok(r.done[0].after * 8 < r.done[0].before, `${r.done[0].before} B of WAV → ${r.done[0].after} B`);
    const ap = json('resources/music/temp_approvals.json').tracks.old_temp;
    t.eq([ap.approved.take, ap.approved.format, ap.approved.files.length, ap.history.map(h => h.action).join()], ['legacy-take', 'ogg', 4 + 1, 'revoke,shrink']);
    t.ok(fs.readFileSync(G('assets/audio/bgm/field_rec.wav')).equals(field), 'the field recording is untouched');
    const after = await p.evaluate(() => ({ st: DIR.state.old_temp.temp, status: DIR.state.old_temp.status, dis: document.getElementById('shrink').disabled }));
    t.eq(after, { st: 'ogg', status: 'approved', dis: true });
    // tidy for the next tests: revoke it again
    await p.evaluate(async () => { await selectTrack('old_temp'); await revoke(); await revoke(); });
  });

  // ── the DAW: review staging, the request round trip, creative direction ──
  let first = null, second = null;
  const leadPreset = await p.evaluate(() => FORGE_PRESETS.find(x => x.category === 'leads').id);
  const samSeed = await p.evaluate(() => SeqGen.moodFromBrief(DIR.cat.find(x => x.id === 'sam_theme'), DIR.briefs.sam_theme).seed);
  // a rejected seed — the very one the DAW would pick first for sam_theme
  const apj = json('resources/music/temp_approvals.json'); apj.tracks.sam_theme = { approved: null, rejected: [{ take: 'gone', seed: samSeed }], history: [] }; put('resources/music/temp_approvals.json', JSON.stringify(apj));
  await t.test('MAKE TAKES renders right here (no DAW tab): progress on the page, a take staged in review, listed under TAKES', async () => {
    const pages = ctx.pages().length;
    const r = await p.evaluate(async ({ leadPreset }) => {
      const req = requestTakes(['sam_theme'], 1, { description: 'slower, more dread, a lonely piano', form: 'loop', length: { bars: 2 }, roles: ['bass', 'chords', 'lead', 'pad'], extraPads: 1, instruments: { lead: 'forge:' + leadPreset } });
      const busy = [document.getElementById('make').textContent, document.getElementById('make').disabled, document.getElementById('b-daw').textContent];
      const seen = new Set(), el = document.getElementById('makemsg');
      const mo = new MutationObserver(() => seen.add(el.textContent.replace(/ · \d+ s$/, '').replace(/^.* — /, ''))); mo.observe(el, { childList: true, characterData: true, subtree: true });
      const R = await req.done; mo.disconnect();
      return { state: R.state, made: R.made, errors: R.errors, busy, seen: [...seen], after: [document.getElementById('make').textContent, document.getElementById('b-daw').textContent, document.getElementById('makemsg').textContent] };
    }, { leadPreset });
    t.eq([r.state, r.made, r.errors], ['done', 1, []], 'request');
    t.eq(r.busy, ['⚄ MAKING…', true, 'STUDIO: making'], 'busy while it works');
    t.ok(['composing…', 'saving…'].every(x => r.seen.includes(x)) && r.seen.some(x => /^rendering stems: (\d) of \1 done…$/.test(x)), 'progress: ' + JSON.stringify(r.seen));
    t.ok(/^⚄ MAKE \d+ TAKES?$/.test(r.after[0]) && r.after[1] === 'STUDIO: ready' && /1 take\(s\) made in \d+ s — ▶ PLAY them under TAKES/.test(r.after[2]), JSON.stringify(r.after));
    t.eq(ctx.pages().length, pages, 'no other tab opened');
    await p.waitForFunction(() => DIR.state.sam_theme && DIR.state.sam_theme.cand === 1, null, { timeout: 5000 });
    const takes = fs.readdirSync(G('assets/audio/review/sam_theme'));
    t.eq(takes.length, 1);
    const dir = 'assets/audio/review/sam_theme/' + takes[0] + '/';
    first = json(dir + 'meta.json'); first.dir = dir;
    t.eq(fs.readdirSync(G(dir)).sort(), ['meta.json', 'mix.wav', 'project.json', 'song.mid', 'stems', 'stems.json']);
    const mid = fs.readFileSync(G(dir + 'song.mid'));
    t.ok(mid.slice(0, 4).toString() === 'MThd' && mid.readUInt16BE(10) >= 5, 'song.mid: a MIDI file with every track (' + mid.readUInt16BE(10) + ' chunks)');
    t.ok(!fs.existsSync(G('assets/audio/bgm/sam_theme.wav')) && !fs.existsSync(G('assets/audio/bgm/sam_theme.temp.ogg')), 'nothing written into the game path');
  });
  await t.test('the take avoids the rejected seed and records the request', async () => {
    t.ok(first.mood.seed !== samSeed, `seed ${first.mood.seed} vs rejected ${samSeed}`);
    t.eq(first.request.description, 'slower, more dread, a lonely piano');
    t.eq([first.request.length.bars, first.request.extraPads, first.request.roles.join()], [2, 1, 'bass,chords,lead,pad']);
  });
  await t.test('description changes the mood (dread → phrygian, slower, sparser)', async () => {
    const base = await p.evaluate(() => { const m = SeqGen.moodFromBrief(DIR.cat.find(x => x.id === 'sam_theme'), DIR.briefs.sam_theme); m.lo = SeqGen.STYLES[m.style].bpm[0]; return m; });
    t.eq(first.mood.mode, 'phrygian');
    t.ok(first.mood.bpm < base.bpm || base.bpm === base.lo, `bpm ${first.mood.bpm} vs ${base.bpm}`);
    t.ok(first.mood.density < base.density, `density ${first.mood.density} vs ${base.density}`);
    t.ok(/direction: "slower, more dread/.test(first.why), first.why);
  });
  await t.test('instrument override is used; parts + extra pad give the expected tracks and stems', async () => {
    t.eq(first.instruments.lead, 'forge:' + leadPreset);
    const SOUND = r => r === 'texture' || r === 'fx' || r === 'texture2' || r === 'hit';
    t.eq(first.roles.filter(r => !SOUND(r)), ['bass', 'chords', 'lead', 'pad', 'pad2']);
    t.ok(!('drums' in first.instruments), 'drums left out');
    const man = json(first.dir + 'stems.json');
    t.eq(man.stems.map(s => s.name + '@' + s.layer).filter(x => !/^(texture|fx)@/.test(x)), ['bass@0.25', 'chords@0', 'lead@0.75', 'pad@0', 'pad2@0']);
    t.eq(fs.readdirSync(G(first.dir + 'stems')).filter(f => !/^(texture|fx)\.wav$/.test(f)).sort(), ['bass.wav', 'chords.wav', 'lead.wav', 'pad.wav', 'pad2.wav']);
    const dev = await p.evaluate(() => { const E = STUDIO.E, t = E.project.tracks.find(x => x.role === 'lead'); return E.dev(t.deviceId).preset; });
    t.eq(dev, leadPreset);
  });
  await t.test('length is exact: 2 bars, and 7 s on a bar line (tempo nudged), mix + stems the same length', async () => {
    const want = Math.round(2 * 240 / first.mood.bpm * 44100);
    t.near(wavFrames(first.dir + 'mix.wav'), want, 1, '2 bars');
    t.near(wavFrames(first.dir + 'stems/pad2.wav'), want, 1, 'stem');
    const st = await p.evaluate(async () => (await requestTakes(['sam_theme'], 1, { length: { sec: 7 }, form: 'loop', roles: ['pad'], loop: true }).done).state);
    t.eq(st, 'done', 'second request');
    const dirs = fs.readdirSync(G('assets/audio/review/sam_theme')).map(d => 'assets/audio/review/sam_theme/' + d + '/').filter(d => d !== first.dir);
    t.eq(dirs.length, 1);
    const m = json(dirs[0] + 'meta.json');
    t.eq(wavFrames(dirs[0] + 'mix.wav'), 7 * 44100);
    t.near(m.bars * 240 / m.mood.bpm, 7, 1e-3, 'whole bars at the nudged tempo');
    t.ok(m.mood.seed !== first.mood.seed && m.mood.seed !== samSeed, 'a fresh seed');
    t.eq(json(dirs[0] + 'stems.json').stems.map(s => s.name), ['pad']);
    second = dirs[0];
  });
  await t.test('APPROVE a seamless DAW take: Ogg mix + stem cut at the loop end, loop in the manifest, small; REVOKE restores', async () => {
    const r = await p.evaluate(async take => { await refresh(); await selectTrack('sam_theme'); const i = DIR.takes.findIndex(m => m.take === take); return approve(i); }, json(second + 'meta.json').take);
    t.ok(r.ok, JSON.stringify(r));
    const man = json('assets/audio/bgm/sam_theme.stems.json');
    t.eq([man.temp, man.loop, man.loop_offset, man.frames, man.stems.map(s => s.file)], [true, true, 0, 7 * 44100, ['assets/audio/bgm/sam_theme.stems/pad.ogg']]);
    t.eq([oggFrames('assets/audio/bgm/sam_theme.temp.ogg'), oggFrames('assets/audio/bgm/sam_theme.stems/pad.ogg')], [7 * 44100, 7 * 44100]);
    const mix = MB_MIN('assets/audio/bgm/sam_theme.temp.ogg', 7), stem = MB_MIN('assets/audio/bgm/sam_theme.stems/pad.ogg', 7);
    console.log(`    DAW take (FORGE pad, 7 s): mix ${mix.toFixed(2)} MB/min, stem ${stem.toFixed(2)} MB/min; WAV ${(r.wavBytes / 7 * 60 / 1048576 / 2).toFixed(1)} MB/min per file`);
    t.ok(mix < 1.3 && stem < 0.8, `mix ${mix.toFixed(2)} / stem ${stem.toFixed(2)} MB per minute`);
    const v = await p.evaluate(async () => { await revoke(); return revoke(); });
    t.ok(v.ok, JSON.stringify(v));
    t.eq(fs.readdirSync(G('assets/audio/bgm')).filter(f => f.startsWith('sam_theme')), []);
  });
  await t.test('✎ EDIT IN DAW opens the exact take in the DAW; an edit comes back by ⇪ SEND TO DIRECTOR as a new take', async () => {
    await p.evaluate(async () => { await refresh(); await selectTrack('sam_theme'); });
    const i = await p.evaluate(take => DIR.takes.findIndex(m => m.take === take), first.take);
    t.ok(i >= 0, 'take listed');
    const popup = ctx.waitForEvent('page');
    await p.evaluate(i => document.querySelector(`[data-edit="${i}"]`).click(), i);
    const daw = await popup; const dawErr = []; t.watch(daw, dawErr);
    await daw.waitForLoadState('domcontentloaded');
    t.ok(/[?&]take=/.test(daw.url()), daw.url());
    await daw.click('#gatebtn');
    await daw.waitForFunction(() => typeof editTake !== 'undefined' && editTake && P && P.name === 'sam_theme', null, { timeout: 30000 });
    const opened = await daw.evaluate(() => ({ roles: P.tracks.map(t => t.role), lead: E.dev(P.tracks.find(t => t.role === 'lead').deviceId).preset, bar: getComputedStyle(document.getElementById('takebar')).display, what: document.getElementById('take-what').textContent, note: document.getElementById('take-msg').textContent }));
    t.eq(opened.roles, first.roles, 'same tracks as the take');
    t.eq(opened.lead, leadPreset, 'same instrument');
    t.ok(opened.bar !== 'none' && opened.what.includes(first.take) && opened.note === '', JSON.stringify(opened));
    // an edit: drop the extra pad, then send it back
    await daw.evaluate(() => { const tr = P.tracks.find(x => x.role === 'pad2'); E.removeTrack(tr.id); E.emit('project'); });
    await daw.click('#takesend');
    await daw.waitForFunction(() => /^sent as take /.test(document.getElementById('take-msg').textContent) || /failed/.test(document.getElementById('take-msg').textContent), null, { timeout: 60000 });
    const sent = await daw.evaluate(() => document.getElementById('take-msg').textContent);
    // the DAW keeps its open project in the game folder too (saved 1.5 s after an edit): .daw.json + .mid
    await daw.waitForFunction(() => /in the game folder/.test(document.getElementById('b-save').textContent), null, { timeout: 10000 });
    const pj = json('assets/audio/projects/sam_theme.daw.json');
    t.ok(pj.v && pj.tracks.filter(x => !['texture', 'fx'].includes(x.role)).length === 4 && fs.readFileSync(G('assets/audio/projects/sam_theme.mid')).slice(0, 4).toString() === 'MThd' && fs.existsSync(G('assets/audio/projects/.gdignore')), 'project mirrored: ' + pj.tracks.map(x => x.role).join());
    t.ok(/^sent as take .*-edit/.test(sent), sent);
    t.noErrors(dawErr);
    await daw.close(); await p.bringToFront();
    const edit = fs.readdirSync(G('assets/audio/review/sam_theme')).find(d => /-edit$/.test(d)), dir = 'assets/audio/review/sam_theme/' + edit + '/';
    const m = json(dir + 'meta.json');
    const snd = r => r === 'texture' || r === 'fx' || r === 'texture2' || r === 'hit';
    t.eq([m.edited_from, m.status, m.id, m.roles.filter(r => !snd(r))], [first.take, 'candidate', 'sam_theme', ['bass', 'chords', 'lead', 'pad']]);
    t.eq(json(dir + 'stems.json').stems.map(s => s.name).filter(n => !snd(n)), ['bass', 'chords', 'lead', 'pad'], 'stems follow the edit');
    t.near(wavFrames(dir + 'mix.wav'), wavFrames(first.dir + 'mix.wav'), 1, 'same length (an asked-for length stays seamless)');
    await p.evaluate(() => rescanOne('sam_theme'));
    const card = await p.evaluate(take => { const i = DIR.takes.findIndex(m => m.take === take); return document.querySelector(`#takes [data-i="${i}"]`).textContent; }, edit);
    t.ok(/edited in the DAW from take/.test(card), card.slice(0, 200));
  });
  // ── REMIX: takes made from finished ones ──
  const remixDone = async (ids, n, rx) => p.evaluate(async ({ ids, n, rx }) => { const R = await requestRemix(ids, n, rx).done; return { state: R.state, made: R.made, errors: R.errors, msg: document.getElementById('rxmsg').textContent }; }, { ids, n, rx });
  const newest = (id, re) => { const d = fs.readdirSync(G('assets/audio/review/' + id)).filter(x => re.test(x)).sort().pop(); const dir = 'assets/audio/review/' + id + '/' + d + '/'; return Object.assign(json(dir + 'meta.json'), { dir }); };
  const firstRef = () => ({ kind: 'take', id: 'sam_theme', title: 'Sam', take: first.take, dir: first.dir });
  await t.test('REMIX box: sources listed (this track\'s take first), take-row ⤳ REMIX picks it, every recipe on for a recording', async () => {
    await p.evaluate(async () => { await refresh(); await selectTrack('sam_theme'); });
    const r = await p.evaluate(take => {
      const i = DIR.takes.findIndex(m => m.take === take);
      document.querySelector(`[data-remix="${i}"]`).click();
      const from = document.getElementById('rx-from').value, groups = [...document.querySelectorAll('#rx-from optgroup')].map(g => g.label.replace(/ \(\d+\)$/, ''));
      const field = RX.list.find(x => x.id === 'field_rec' && x.kind === 'file');
      RX.from = field ? 'file:' + field.path : ''; rxRender();
      const off = [...document.querySelectorAll('#rx-recipes [data-rx]')].filter(b => b.disabled).map(b => b.dataset.rx);
      return { from, groups, field: !!field, real: !!RX.list.find(x => x.id === 'real_track' && x.real), off, recipe: RX.recipe, go: document.getElementById('rx-go').textContent };
    }, first.take);
    t.ok(r.from.startsWith('take:') && r.from.includes(first.take), 'take-row REMIX selects it: ' + r.from);
    // ⤳ REMIX ↓ in the TAKES header brings the box into view (it sits under MAKE TAKES)
    const seen = await p.evaluate(async () => { document.getElementById('right').scrollTop = 0; document.getElementById('toremix').click(); await new Promise(r => setTimeout(r, 900));
      const b = document.getElementById('remix').getBoundingClientRect(), R = document.getElementById('right').getBoundingClientRect(); return b.top >= R.top - 1 && b.top < R.bottom - 40; });
    t.ok(seen, 'REMIX scrolled into view');
    t.ok(r.groups.includes('THIS TRACK') && r.field && r.real, JSON.stringify(r));
    t.eq(r.off, [], 'a recording takes every recipe (the NOTES ones transcribe it)');
    t.eq(r.go, '⤳ REMIX × 2');
  });
  let rs = null;
  await t.test('RESTYLE: the take\'s chords, sections and theme in another style, for another track, in that track\'s key', async () => {
    const r = await remixDone(['tem_theme'], 1, { recipe: 'restyle', from: firstRef(), bars: 4 });
    t.eq([r.state, r.made, r.errors], ['done', 1, []], r.msg);
    t.ok(/1 take\(s\) made/.test(r.msg), 'progress lands in the REMIX box: ' + r.msg);
    rs = newest('tem_theme', /-restyle$/);
    t.eq([rs.request.remix.recipe, rs.request.remix.from.take, rs.remix.recipe, rs.bars, rs.status], ['restyle', first.take, 'restyle', 4, 'candidate']);
    t.ok(rs.mood.style !== first.mood.style && /^REMIX · RESTYLE/.test(rs.why), rs.mood.style + ' · ' + rs.why);
    // the harmony is the source's: the same progression (degrees), in the target's key
    const src = await p.evaluate(o => SeqGen.plan(o).HP.A.prog.join(), JSON.parse(fs.readFileSync(G(first.dir + 'project.json'), 'utf8')).gen.o);
    const pj = json(rs.dir + 'project.json');
    t.ok(pj.tracks.some(x => x.role === 'lead') && json(rs.dir + 'stems.json').stems.length >= 3, 'tracks + stems: ' + pj.tracks.map(x => x.role).join());
    t.ok(src.length > 0, 'source progression ' + src);
  });
  await t.test('⟳ AGAIN on a remix makes the identical remix (same source, recipe, seed, style)', async () => {
    await p.evaluate(async () => { await refresh(); await selectTrack('tem_theme'); });
    const n0 = fs.readdirSync(G('assets/audio/review/tem_theme')).length;
    await p.evaluate(take => { const i = DIR.takes.findIndex(m => m.take === take); document.querySelector(`[data-again="${i}"]`).click(); }, rs.take);
    await p.waitForFunction(n0 => !STUDIO.busy && Object.values(DIR.requests).slice(-1)[0].state === 'done', n0, { timeout: 120000 });
    const dirs = fs.readdirSync(G('assets/audio/review/tem_theme')).filter(x => /-restyle$/.test(x)).sort();
    t.eq(dirs.length, 2, 'a second restyle take');
    const again = Object.assign(json('assets/audio/review/tem_theme/' + dirs[1] + '/meta.json'), { dir: 'assets/audio/review/tem_theme/' + dirs[1] + '/' });
    const notes = d => JSON.stringify(json(d + 'project.json').tracks.filter(x => x.kind === 'midi').map(x => [x.role, Object.values(x.patterns).map(q => q.notes.map(n => [n.t, n.n, n.d]))]));
    t.eq([again.mood.seed, again.mood.style, again.mood.key], [rs.mood.seed, rs.mood.style, rs.mood.key]);
    t.ok(notes(again.dir) === notes(rs.dir), 'the same notes');
  });
  await t.test('COVER for the same track keeps the source\'s lead notes exactly; the band around it is new', async () => {
    const r = await remixDone(['sam_theme'], 1, { recipe: 'cover', from: firstRef(), bars: 2 });
    t.eq([r.state, r.made, r.errors], ['done', 1, []], r.msg);
    const cv = newest('sam_theme', /-cover$/), a = json(first.dir + 'project.json'), b = json(cv.dir + 'project.json');
    const lead = pj => { const tr = pj.tracks.find(x => x.role === 'lead'); return Object.entries(tr.patterns).filter(([k]) => !/_\d+b$/.test(k)).map(([k, q]) => [k, q.notes.map(n => [n.t, n.n])]); };
    const la = Object.fromEntries(lead(a)), lb = lead(b);
    t.ok(lb.length && lb.some(([k]) => la[k]) && lb.every(([k, ns]) => !la[k] || JSON.stringify(ns) === JSON.stringify(la[k])), 'lead patterns: ' + JSON.stringify(lb).slice(0, 160));
    t.ok(cv.mood.style !== first.mood.style, cv.mood.style);
  });
  await t.test('CHOP from a take\'s audio: the source layer (layer 0) + new drums and a bass that follows it; tempo + key from the take, not guessed', async () => {
    const r = await remixDone(['tem_theme'], 1, { recipe: 'chop', from: firstRef(), bars: 4 });
    t.eq([r.state, r.made, r.errors], ['done', 1, []], r.msg);
    const ch = newest('tem_theme', /-chop$/), man = json(ch.dir + 'stems.json');
    t.ok(man.stems.some(s => s.name === 'source' && s.layer === 0) && man.stems.some(s => s.name === 'drums') && man.stems.some(s => s.name === 'bass'), man.stems.map(s => s.name + '@' + s.layer).join());
    t.eq([ch.remix.analysis.bpm, ch.remix.analysis.key, ch.remix.analysis.mode, ch.remix.analysis.guessed], [first.mood.bpm, first.mood.key, first.mood.mode, []]);
    t.ok(ch.remix.lib && fs.readdirSync(G('assets/audio/library/remix')).some(f => f.endsWith('.wav')), 'the chopped layer is a library item, mirrored');
    const pj = json(ch.dir + 'project.json'), src = pj.tracks.find(x => x.role === 'source');
    t.ok(src && src.kind === 'audio' && src.audio.length === 1 && src.audio[0].libId === ch.remix.lib, 'an audio track the DAW can open');
    t.near(wavFrames(ch.dir + 'stems/source.wav'), wavFrames(ch.dir + 'mix.wav'), 1, 'stems the mix\'s length');
  });
  await t.test('STRETCH from a recording (a plain .wav): tempo + key guessed, a stretched bed + a new theme', async () => {
    const r = await remixDone(['field_rec'], 1, { recipe: 'stretch', from: { kind: 'file', id: 'field_rec', title: 'Field', path: 'assets/audio/bgm/field_rec.wav' }, bars: 4 });
    t.eq([r.state, r.made, r.errors], ['done', 1, []], r.msg);
    const st = newest('field_rec', /-stretch$/);
    t.ok(st.remix.stretch.factor > 3 && st.remix.analysis.guessed.includes('key'), JSON.stringify(st.remix));
    t.ok(json(st.dir + 'stems.json').stems.some(s => s.name === 'source'), 'source stem');
    t.ok(st.lufs > -20 && st.true_peak <= -1, 'mastered: ' + st.lufs + ' LUFS ' + st.true_peak + ' dBTP');
  });
  await t.test('DUB and TAPE from a take: a source layer the new band\'s length; TAPE two semitones down and slower', async () => {
    for (const recipe of ['dub', 'tape']) {
      const r = await remixDone(['quiet_bed'], 1, { recipe, from: firstRef(), bars: 4 });
      t.eq([r.state, r.made, r.errors], ['done', 1, []], recipe + ': ' + r.msg);
      const m = newest('quiet_bed', new RegExp('-' + recipe + '$'));
      t.ok(json(m.dir + 'stems.json').stems.some(s => s.name === 'source') && m.bars === 4, recipe + ' stems');
      if (recipe === 'tape') t.ok(Math.abs(m.mood.bpm - first.mood.bpm * Math.pow(2, -2 / 12)) < 0.01 && m.mood.key === (first.mood.key + 10) % 12 && m.remix.machine === 'worn_cassette', 'tape: ' + m.mood.bpm + ' BPM in ' + m.mood.key + ' through ' + m.remix.machine);
    }
  });
  await t.test('TAPE MACHINE: the worklet and the plain-JS model give the same samples; the DAW insert renders (and keeps renders unchunked)', async () => {
    const r = await p.evaluate(async () => {
      const sr = 48000, n = sr, x = new Float32Array(n).map((_, i) => 0.5 * Math.sin(2 * Math.PI * 220 * i / sr));
      const prm = Object.assign(TapeModel.machine('reel_7'), { degrade: 0, chew: 0, seed: 5 });
      const off = new OfflineAudioContext(2, n + 2000, sr); await TapeModel.prepare(off);
      const src = off.createBufferSource(), b = off.createBuffer(2, n, sr); b.copyToChannel(x, 0); b.copyToChannel(x, 1); src.buffer = b;
      const node = TapeModel.createNode(off, prm); src.connect(node); node.connect(off.destination); src.start(0);
      const wl = (await off.startRendering()).getChannelData(0), js = TapeModel.process([x, x], sr, prm)[0], lat = new TapeModel.DSP(sr, 2, prm).latency;
      let err = 0, pk = 0; for (let i = 2000; i < n - 2000; i++) { err = Math.max(err, Math.abs(wl[i + lat] - js[i])); pk = Math.max(pk, Math.abs(js[i])); }
      // the DAW: a TAPE MACHINE insert on a FORGE strip
      const E = STUDIO.E || (STUDIO.E = new DAW.Engine()); await E.start();
      const proj = DAW.Engine.newProject(); proj.bpm = 100; await E.load(proj);
      const dev = await E.addDevice('forge', { name: 'K', preset: FORGE_PRESETS.find(q => q.category === 'keys').id });
      const tr = E.addTrack('midi', { name: 'keys', deviceId: dev.id }); tr.patterns = { p: { name: 'p', lenBars: 1, notes: [{ t: 0, d: 300, n: 60, v: 0.8 }, { t: 0, d: 300, n: 64, v: 0.8 }] } }; tr.clips = [{ bar: 0, pid: 'p' }];
      E.emit('project'); await E.whenReady();
      const plain = await E.renderOffline({ fromBar: 0, toBar: 1, tailSec: 0.5 });
      const chunkBefore = E.chunkable();
      dev.mix.fx = [{ id: 'm1', type: 'machine', on: true, params: Object.assign(TapeModel.machine('worn_cassette'), { seed: 2 }) }]; E.applyMix(); await E.whenReady();
      const taped = await E.renderOffline({ fromBar: 0, toBar: 1, tailSec: 0.5 });
      let diff = 0, fin = true; const a0 = plain.channels[0], b0 = taped.channels[0];
      for (let i = 0; i < Math.min(a0.length, b0.length); i++) { diff += Math.abs(a0[i] - b0[i]); if (!Number.isFinite(b0[i])) fin = false; }
      const listed = DawFX.TYPES.some(q => q.id === 'machine') && DawFX.presets('machine').length >= 5 && DawFX.normField('15', DawFX.spec('machine').speed) === 15;
      return { err, pk, diff, fin, chunkBefore, chunkAfter: E.chunkable(), listed };
    });
    t.ok(r.pk > 0.2 && r.err < 1e-4, 'worklet = JS: max difference ' + r.err.toExponential(2) + ' (peak ' + r.pk.toFixed(2) + ')');
    t.ok(r.diff > 1 && r.fin, 'the insert changes the render: ' + r.diff.toFixed(1));
    t.eq([r.chunkBefore, r.chunkAfter, r.listed], [true, false, true], 'chunkable before / after · listed with presets · numeric speed from a <select>');
  });
  await t.test('MAKE TAKES with TAPE: every stem through one machine, stems still sum to the mix, recorded for ⟳ AGAIN', async () => {
    const r = await p.evaluate(async () => { const R = await requestTakes(['quiet_bed'], 1, { length: { bars: 2 }, roles: ['bass', 'chords', 'pad'], tape: 'cassette' }).done; return { state: R.state, errors: R.errors, opts: regenForm.length }; });
    t.eq([r.state, r.errors], ['done', []]);
    const m = newest('quiet_bed', /^\d{8}-\d{6}-s\d+$/), man = json(m.dir + 'stems.json');
    t.eq([m.mood.tape, m.request.tape], ['cassette', 'cassette']);
    // the stems add up to the mix (the tape went on before the master, on every stem alike)
    const pcm = rel => { const b = fs.readFileSync(G(rel)); let o = 12; while (o < b.length) { const id = b.toString('ascii', o, o + 4), sz = b.readUInt32LE(o + 4); if (id === 'data') { const out = new Float32Array(sz / 2); for (let i = 0; i < out.length; i++) out[i] = b.readInt16LE(o + 8 + i * 2) / 32768; return out; } o += 8 + sz + (sz & 1); } return null; };
    const mix = pcm(m.dir + 'mix.wav'), sum = new Float32Array(mix.length);
    for (const st of man.stems) { const d = pcm(st.file); for (let i = 0; i < Math.min(d.length, sum.length); i++) sum[i] += d[i]; }
    let err = 0, pk = 0; for (let i = 0; i < mix.length; i++) { err = Math.max(err, Math.abs(mix[i] - sum[i])); pk = Math.max(pk, Math.abs(mix[i])); }
    t.ok(pk > 0.1 && err < 0.002 * man.stems.length + 1e-3, 'stems sum to the mix within 16-bit rounding: ' + err.toFixed(5));
    const card = await p.evaluate(async () => { await refresh(); await selectTrack('quiet_bed'); return document.getElementById('takes').textContent; });
    t.ok(/tape: cassette deck/.test(card), 'the take card says which tape');
  });
  // ── IMPORT AUDIO → covers, flagged TEMP ONLY ──
  await t.test('IMPORT AUDIO: an imported song (synthesized here) becomes a source; unlicensed → flagged, cleared → not', async () => {
    const r = await p.evaluate(async () => {
      // an original test piece: 16 bars at 100 BPM in A minor, i – VI – III – VII, a plucked line on top
      const sr = 44100, bpm = 100, beat = 60 / bpm, bars = 16, n = Math.round(bars * 4 * beat * sr), L = new Float32Array(n);
      const prog = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]], hz = m => 440 * Math.pow(2, (m - 69) / 12);
      for (let i = 0; i < n; i++) {
        const t = i / sr, bar = Math.floor(t / (4 * beat)), ch = prog[bar % 4], inBeat = t % beat;
        let v = 0; for (const m of ch) v += 0.06 * Math.sin(2 * Math.PI * hz(m - 12) * t);
        v += 0.1 * Math.sin(2 * Math.PI * hz(ch[0] - 24) * t) * (inBeat < beat * 0.9 ? 1 : 0.2);
        const mel = ch[(Math.floor(t / beat)) % 3] + 12; v += 0.12 * Math.sin(2 * Math.PI * hz(mel) * t) * Math.exp(-inBeat * 5);
        if (inBeat < 0.02) v += 0.3 * Math.sin(2 * Math.PI * 60 * inBeat) * Math.exp(-inBeat * 90);
        L[i] = v;
      }
      const f = new File([AK.wav.encode([L, L], sr, { bitDepth: 16 })], 'My Sketch Song.wav', { type: 'audio/wav' });
      await importAudio(f, 'unlicensed');
      const f2 = new File([AK.wav.encode([L, L], sr, { bitDepth: 16 })], 'Public Hymn.wav', { type: 'audio/wav' });
      await importAudio(f2, 'cleared');
      const imp = RX.list.filter(x => x.imported).map(x => ({ id: x.id, rights: x.rights, label: x.label })), sel = document.getElementById('rx-from');
      const groups = [...sel.querySelectorAll('optgroup')].map(g => g.label.replace(/ \(\d+\)$/, ''));
      const notesOff = [...document.querySelectorAll('#rx-recipes [data-rx]')].filter(b => b.disabled).map(b => b.dataset.rx);
      return { imp, groups, from: RX.from, notesOff, hint: document.getElementById('rx-hint').textContent };
    });
    t.ok(r.imp.length === 2 && r.imp.some(x => x.rights === 'unlicensed' && /temp only/.test(x.label)) && r.imp.some(x => x.rights === 'cleared'), JSON.stringify(r.imp));
    t.ok(r.groups[0] === 'IMPORTED' && /public_hymn/.test(r.from) && r.notesOff.length === 0, JSON.stringify(r));
    t.ok(fs.existsSync(G('assets/audio/imports/my_sketch_song.wav')) && fs.existsSync(G('assets/audio/imports/.gdignore')) && json('assets/audio/imports/my_sketch_song.json').rights === 'unlicensed', 'stored in imports/ with its rights');
  });
  let cover = null;
  await t.test('COVER of an unlicensed import: transcribed (tempo, key, chords, sections), flagged ⚠ cover · TEMP ONLY on the take', async () => {
    const from = { kind: 'file', id: 'import:my_sketch_song', title: 'My Sketch Song', path: 'assets/audio/imports/my_sketch_song.wav', imported: true, rights: 'unlicensed' };
    const r = await remixDone(['quiet_bed'], 1, { recipe: 'cover', from, bars: 4 });
    t.eq([r.state, r.made, r.errors], ['done', 1, []], r.msg);
    cover = newest('quiet_bed', /-cover$/);
    const tr = cover.remix.transcription;
    // A minor, or its relative C major (the same notes — the chords land on the same pitches either way)
    t.ok(Math.abs(tr.bpm - 100) < 1 && (tr.mode === 'major' ? tr.key : (tr.key + 3) % 12) === 0 && tr.bars >= 12 && tr.chords >= 12 && /^A/.test(tr.sections), 'heard: ' + JSON.stringify(tr));
    t.ok(/basic-pitch/.test(tr.engine || '') && tr.notes > 40 && tr.melody >= 20 && tr.bass >= 6, 'notes transcribed (melody + bass): ' + JSON.stringify(tr));
    // COVER keeps the transcribed line: the take's lead plays the test piece's melody (chord tones of A minor's i – VI – III – VII, an octave up)
    const pj = json(cover.dir + 'project.json'), lead = pj.tracks.find(x => x.role === 'lead'), ln = Object.values(lead.patterns).flatMap(q => q.notes);
    const pcs = new Set([9, 0, 4, 5, 7, 11, 2]);
    t.ok(ln.length >= 8 && ln.filter(x => pcs.has(((x.n % 12) + 12) % 12)).length / ln.length > 0.9, 'lead notes from the piece: ' + ln.slice(0, 8).map(x => x.n).join(' '));
    t.eq([cover.third_party.kind, cover.third_party.rights, cover.third_party.source], ['cover', 'temp-only', 'My Sketch Song']);
    const card = await p.evaluate(async () => { await refresh(); await selectTrack('quiet_bed'); return document.getElementById('takes').textContent; });
    t.ok(/⚠ COVER OF My Sketch Song · TEMP ONLY/.test(card), 'the card says so');
    // a cleared import → no flag; a CHOP of the unlicensed one → a flagged sample; a remix of the cover stays flagged
    const c2 = await remixDone(['quiet_bed'], 1, { recipe: 'restyle', from: { kind: 'file', id: 'import:public_hymn', title: 'Public Hymn', path: 'assets/audio/imports/public_hymn.wav', imported: true, rights: 'cleared' }, bars: 4 });
    t.eq(c2.errors, []);
    t.ok(!newest('quiet_bed', /-restyle$/).third_party, 'cleared import: not flagged');
    const c3 = await remixDone(['quiet_bed'], 1, { recipe: 'chop', from, bars: 4 });
    t.eq(c3.errors, []); t.eq(newest('quiet_bed', /-chop$/).third_party.kind, 'sample');
    const c4 = await remixDone(['quiet_bed'], 1, { recipe: 'dream', from: { kind: 'take', id: 'quiet_bed', title: 'Quiet Bed', take: cover.take, dir: cover.dir }, bars: 4 });
    t.eq(c4.errors, []); t.ok(newest('quiet_bed', /-dream$/).third_party.via === cover.take, 'a remix of the cover inherits the flag');
  });
  await t.test('APPROVE a flagged cover: approval + game manifest carry third_party; music_release_check.py lists it, --strip removes only the temp', async () => {
    const r = await p.evaluate(async take => { await refresh(); await selectTrack('quiet_bed'); const i = DIR.takes.findIndex(m => m.take === take); let a = await approve(i); if (!a.ok) a = await approve(i); return { a, list: document.getElementById('list').textContent, counts: document.getElementById('b-counts').textContent }; }, cover.take);
    t.ok(r.a.ok, JSON.stringify(r.a));
    const ap = json('resources/music/temp_approvals.json').tracks.quiet_bed.approved, man = json('assets/audio/bgm/quiet_bed.stems.json');
    t.eq([ap.third_party.kind, man.third_party.kind], ['cover', 'cover']);
    t.ok(/⚠ COVER · TEMP ONLY/.test(r.list) && /⚠ 1 third-party temp/.test(r.counts), 'track list + header flag it: ' + r.counts);
    const py = (...a) => require('child_process').spawnSync('python3', [path.join(__dirname, '..', 'music_release_check.py'), '--godot', GAME, ...a], { encoding: 'utf8' });
    const ls = py(); t.ok(ls.status === 1 && /quiet_bed/.test(ls.stdout) && /cover/.test(ls.stdout), ls.stdout + ls.stderr);
    const st = py('--strip'); t.eq(st.status, 0, st.stdout + st.stderr);
    t.ok(!fs.existsSync(G('assets/audio/bgm/quiet_bed.temp.ogg')) && !fs.existsSync(G('assets/audio/bgm/quiet_bed.stems.json')) && !fs.existsSync(G('assets/audio/bgm/quiet_bed.stems')), 'temp files gone');
    t.ok(fs.existsSync(G('assets/audio/bgm/real_track.ogg')), 'real audio untouched');
    t.eq(py().status, 0, 'clear to export after the strip');
  });
  await t.test('♫ COVER A SONG (top bar): one dialog — an imported song, a track, a style → flagged cover takes; ⚠ COVERS filter; build tag', async () => {
    const r = await p.evaluate(async () => {
      await refresh();
      document.getElementById('coverbtn').click();
      const open = document.getElementById('covdlg').classList.contains('show');
      const srcs = [...document.getElementById('cov-src').options].map(o => o.textContent);
      document.getElementById('cov-src').value = 'assets/audio/imports/my_sketch_song.wav';
      document.getElementById('cov-track').value = 'tem_theme'; document.getElementById('cov-n').value = '1'; document.getElementById('cov-style').value = 'folk';
      const req = await covMake(); const R = await req.done; await rescanOne('tem_theme');
      document.querySelector('#chips [data-f="covers"]').click();
      const listed = visible().map(t => t.id);
      document.querySelector('#chips [data-f="all"]').click();
      return { open, srcs, state: R.state, errors: R.errors, sel: DIR.sel, listed, ver: document.getElementById('b-ver').textContent };
    });
    t.ok(r.open && r.srcs.some(x => /My Sketch Song ⚠ temp only/.test(x)), JSON.stringify(r.srcs));
    t.eq([r.state, r.errors, r.sel], ['done', [], 'tem_theme']);
    const m = newest('tem_theme', /-cover$/);
    t.ok(m.third_party && m.third_party.kind === 'cover' && m.mood.style === 'folk', JSON.stringify({ tp: m.third_party, style: m.mood.style }));
    t.ok(r.listed.includes('tem_theme') && !r.listed.includes('sam_theme'), '⚠ COVERS lists the tracks with covers: ' + r.listed.join(','));
    t.ok(/^build 20\d\d-\d\d-\d\d/.test(r.ver), r.ver);
  });
  await t.test('the tools\' library is mirrored into the game folder (library/<kind>/…wav + .json), at once and on link for older items', async () => {
    const r = await p.evaluate(async () => {
      const tone = n => { const c = new Float32Array(n); for (let i = 0; i < n; i++) c[i] = 0.3 * Math.sin(i * 0.05); return c; };
      const a = await AK.lib.put({ kind: 'field', name: 'rain on tin', sampleRate: 44100, meta: { title: 'rain on tin' } }, [tone(4410), tone(4410)]);
      await new Promise(res => setTimeout(res, 400));
      // an item stored while no folder was linked: mirrored by the next link / restore
      const root = AK.game.root; AK.game.root = null;
      const b = await AK.lib.put({ kind: 'tape-mix', name: 'loop one', sampleRate: 44100, meta: { title: 'loop one' } }, [tone(2205)]);
      const before = (await AK.lib.meta(b.id)).archived || null;
      AK.game.root = root; const n = await AK.archive.all();
      return { a: (await AK.lib.meta(a.id)).archived, b: (await AK.lib.meta(b.id)).archived, before, n };
    });
    t.ok(/^assets\/audio\/library\/field\/rain_on_tin-.+\.wav$/.test(r.a) && fs.existsSync(G(r.a)) && fs.existsSync(G(r.a.replace(/\.wav$/, '.json'))), 'put → mirrored: ' + r.a);
    const info = json(r.a.replace(/\.wav$/, '.json')), bytes = fs.statSync(G(r.a)).size;
    t.ok(info.frames === 4410 && bytes >= 4410 * 2 * 3 && bytes < 4410 * 2 * 3 + 4096, 'the recording, whole, 24-bit: ' + bytes + ' bytes');
    t.ok(r.before === null && /^assets\/audio\/library\/tape[-_]mix\/loop_one-/.test(r.b) && fs.existsSync(G(r.b)) && r.n >= 1, 'caught up on link: ' + r.b);
    t.ok(fs.existsSync(G('assets/audio/library/.gdignore')), 'Godot ignores the library mirror');
  });
  await t.test('TEMP TRACKS stages into review by default (skip-review off)', async () => {
    const daw = await ctx.newPage(); await daw.goto(p.url().replace(/audio_director\.html.*$/, 'daw.html'));
    const r = await daw.evaluate(() => ({ skip: document.getElementById('g-skipreview').checked, linkToDirector: !!document.querySelector('a[href="audio_director.html"]') }));
    await daw.close();
    t.eq(r, { skip: false, linkToDirector: true });
  });

  await t.test('finger controls: track row, take, play, intensity, two-tap reject (CDP touch, ≥ 36 px)', async () => {
    // a background page gets no frames in headless Chromium, and touch input waits for one
    await p.bringToFront(); await p.evaluate(() => refresh());
    const box = s => p.evaluate(s => { const e = document.querySelector(s); e.scrollIntoView({ block: 'center' }); const r = e.getBoundingClientRect(); return { x: r.left + r.width / 2, y: r.top + r.height / 2, h: r.height, w: r.width }; }, s);
    let b = await box('#list .tr[data-id="sam_theme"] .nm'); await f.tap(b.x, b.y); await p.waitForTimeout(200);
    t.eq(await p.evaluate(() => DIR.sel), 'sam_theme');
    b = await box('#takes [data-pick="1"]'); t.ok(b.h >= 36 && b.w >= 36, 'take number ' + b.w + '×' + b.h); await f.tap(b.x, b.y); await p.waitForTimeout(400);
    t.eq(await p.evaluate(() => [DIR.cur, PV.playing]), [1, true], 'take 2 picked and playing');
    b = await box('#play'); t.ok(b.h >= 36, 'play ' + b.h); await f.tap(b.x, b.y); await p.waitForTimeout(200);
    t.ok(!(await p.evaluate(() => PV.playing)), 'stopped');
    await f.tap(b.x, b.y); await p.waitForTimeout(200);
    t.ok(await p.evaluate(() => PV.playing), 'playing again');
    b = await box('#list .tr[data-id="quiet_bed"] .cb'); t.ok(b.h >= 36 && b.w >= 28, 'tick cell ' + b.w + '×' + b.h); await f.tap(b.x, b.y); await p.waitForTimeout(100);
    t.eq(await p.evaluate(() => [[...DIR.checked], DIR.sel]), [['quiet_bed'], 'sam_theme'], 'ticked for batch, selection kept');
    await f.tap(b.x, b.y); await p.waitForTimeout(100);
    b = await box('[data-int="0.25"]'); t.ok(b.h >= 36 && b.w >= 36, 'intensity button'); await f.tap(b.x, b.y); await p.waitForTimeout(100);
    t.eq(await p.evaluate(() => PV.intensity), 0.25);
    const cand0 = await p.evaluate(() => DIR.state.sam_theme.cand);
    b = await box('#takes [data-rej="1"]'); t.ok(b.h >= 36, 'reject'); await f.tap(b.x, b.y); await p.waitForTimeout(100);
    t.ok(await p.evaluate(() => /TAP AGAIN/.test(document.querySelector('#takes [data-rej="1"]').textContent)), 'armed after one tap');
    const b2 = await box('#takes [data-rej="1"]'); t.near(b2.y, b.y, 1, 'the armed button stays put');
    await f.tap(b2.x, b2.y); await p.waitForTimeout(600);
    t.eq(await p.evaluate(() => DIR.state.sam_theme.cand), cand0 - 1, 'one candidate fewer');
    b = await box('#make'); t.ok(b.h >= 36, 'make takes');
    const small = await p.evaluate(() => [...document.querySelectorAll('#track button, header button, #chips button')].filter(e => e.offsetParent && (e.getBoundingClientRect().height < 36 || e.getBoundingClientRect().width < 36)).map(e => e.id || e.textContent));
    t.eq(small, [], 'buttons under 36 px');
    await p.evaluate(() => PV.stop());
  });
  await t.test('instrument picker lists FORGE presets (and PATCH BANK) by category at runtime', async () => {
    const r = await p.evaluate(async () => { await openPicker('lead'); const g = [...document.querySelectorAll('#pk-body .grp')].map(e => e.textContent); const btn = document.querySelector('#pk-body [data-pv^="forge:"]'); btn.click(); return { g, pick: RG.instruments.lead, want: btn.dataset.pv, shown: document.querySelector('[data-inst="lead"]').textContent }; });
    t.ok(r.g[0].startsWith('AUTO') && r.g.some(x => x.startsWith('FORGE · ')), r.g.join(' | '));
    t.eq(r.pick, r.want); t.ok(/FORGE/.test(r.shown), r.shown);
  });
  // ── MAKE TAKES: ensembles, variety, direct musical controls, quick moods, layout ──
  await t.test('MAKE TAKES panel fits 1280×800 (and the Deck at 125 %): every row reachable without horizontal scroll, ⚄ MAKE TAKES pinned in view', async () => {
    const check = () => p.evaluate(() => {
      document.getElementById('more').open = true; document.getElementById('moreinst').open = true;
      const right = document.getElementById('right'), R = right.getBoundingClientRect();
      const rows = [...document.querySelectorAll('#regen .row, #regen summary')].filter(e => e.offsetParent);
      const out = rows.filter(e => { const r = e.getBoundingClientRect(); return r.right > R.right - right.offsetWidth + right.clientWidth + 0.5 || r.left < R.left - 0.5; }).map(e => e.textContent.trim().slice(0, 30));
      const wide = [...document.querySelectorAll('#regen *')].filter(e => e.offsetParent && e.getBoundingClientRect().right > R.left + right.clientWidth + 0.5).map(e => e.id || e.tagName + ':' + e.textContent.trim().slice(0, 20));
      // scroll the box's top into view: the MAKE button (sticky at the bottom of the scroll area) must be on screen too
      document.getElementById('regen').scrollIntoView({ block: 'start' });
      const mk = document.getElementById('make').getBoundingClientRect();
      const small = [...document.querySelectorAll('#regen button, #regen summary')].filter(e => e.offsetParent && e.getBoundingClientRect().height < 36).map(e => e.id || e.textContent.trim());
      const res = { rows: rows.length, out, wide: wide.slice(0, 5), hscroll: [document.documentElement.scrollWidth - innerWidth, right.scrollWidth - right.clientWidth], make: [Math.round(mk.top), Math.round(mk.bottom), innerHeight], small };
      document.getElementById('more').open = false; document.getElementById('moreinst').open = false;
      return res;
    });
    await p.evaluate(() => selectTrack('sam_theme'));
    for (const [w, h] of [[1280, 800], [1024, 640]]) {
      await p.setViewportSize({ width: w, height: h }); await p.waitForTimeout(150);
      if (process.env.SHOT_DIR) { await p.evaluate(() => { document.getElementById('more').open = true; document.getElementById('regen').scrollIntoView({ block: 'start' }); }); await p.screenshot({ path: path.join(process.env.SHOT_DIR, `director_${w}.png`) }); }
      const r = await check();
      t.ok(r.rows >= 12, w + ': rows ' + r.rows);
      t.eq([r.out, r.wide, r.hscroll], [[], [], [0, 0]], w + '×' + h + ' horizontal overflow');
      t.ok(r.make[0] >= 0 && r.make[1] <= r.make[2], w + '×' + h + ': ⚄ MAKE TAKES on screen ' + r.make);
      t.eq(r.small, [], w + ': controls under 36 px');
    }
    // ⚙ SETTINGS ↓ lands the box's first rows below the sticky transport, not under it
    await p.evaluate(() => { document.getElementById('right').scrollTop = 0; document.getElementById('tosettings').click(); });
    await p.waitForTimeout(900);
    const s = await p.evaluate(() => ({ tr: document.querySelector('.transport').getBoundingClientRect().bottom, row: document.getElementById('forwho').getBoundingClientRect().top, mk: document.getElementById('make').getBoundingClientRect().bottom, h: innerHeight }));
    t.ok(s.row >= s.tr && s.row < s.tr + 80 && s.mk <= s.h, '⚙ SETTINGS ↓: FOR row at ' + s.row + ' under the transport (' + s.tr + '), MAKE at ' + s.mk);
    await p.setViewportSize({ width: 1280, height: 800 });
  });
  await t.test('QUICK moods fill the panel and say what they set; 🎲 SURPRISE ME fills style / ensemble / feel / harmony within the choices', async () => {
    const r = await p.evaluate(() => {
      document.getElementById('resetregen').click();
      document.querySelector('#quick [data-quick="dread"]').click();
      const q = { style: document.getElementById('r-style').value, ens: RG.ensemble, desc: document.getElementById('desc').value, hit: document.getElementById('r-hit').value, msg: document.getElementById('quickmsg').textContent,
        chip: document.querySelector('#ensembles [data-ens="horror"]').className, form: TempMaker.normOpts(regenForm()) };
      const s = []; for (let k = 0; k < 12; k++) { document.getElementById('surprise').click(); s.push({ o: TempMaker.normOpts(regenForm()), raw: regenForm(), msg: document.getElementById('quickmsg').textContent, feel: document.getElementById('r-feel').value }); }
      document.getElementById('resetregen').click();
      return { q, s, after: regenForm() };
    });
    t.eq([r.q.style, r.q.ens, r.q.hit, r.q.chip], ['dark_drone', 'horror', 'fx_sub_drop', 'on']);
    t.ok(/^dread → direction “dread, ominous/.test(r.q.msg) && /style dark drone/.test(r.q.msg) && /ensemble horror \/ industrial/.test(r.q.msg) && /hit fx_sub_drop/.test(r.q.msg), r.q.msg);
    t.eq([r.q.form.ensemble, r.q.form.harmony, r.q.form.energy], ['horror', 'open', -0.15]);
    for (const x of r.s) {
      t.ok(x.o.style && x.o.ensemble && x.o.feel && x.o.harmony, 'surprise sets them all: ' + JSON.stringify(x.o));
      t.eq(JSON.stringify(x.o.style) + x.o.ensemble + x.o.feel + x.o.harmony, JSON.stringify(x.raw.style) + x.raw.ensemble + x.raw.feel + x.raw.harmony, 'every pick survives normOpts');
      t.ok(/^🎲 → (direction “.*” · )?style .* · ensemble /.test(x.msg), x.msg);
    }
    t.ok(new Set(r.s.map(x => x.o.style + x.o.ensemble)).size >= 6, 'surprises differ');
    t.eq(r.after, {}, 'reset clears every choice');
  });
  let wideTakes = [];
  const TempMaker_rock = await p.evaluate(() => TempMaker.ENSEMBLES.rock.roles);
  await t.test('ENSEMBLE chip + VARIETY wide: each take draws its own line-up from the ensemble; take 1 keeps the brief\'s style, the others differ and are compatible', async () => {
    const before = new Set(fs.readdirSync(G('assets/audio/review/sam_theme')));
    const r = await p.evaluate(async () => {
      document.getElementById('resetregen').click();
      document.querySelector('#ensembles [data-ens="jazz"]').click(); document.querySelector('#variety [data-v="wide"]').click(); document.querySelector('#ntakes [data-n="3"]').click();
      RG.roles = ['bass', 'chords', 'lead', 'pad']; document.getElementById('r-lenmode').value = 'bars'; document.getElementById('r-len').value = 2; renderRegen();
      const shown = [document.getElementById('instrsum').textContent, document.querySelector('#ensembles [data-ens="jazz"]').className];
      const R = await makeNow().done;
      document.getElementById('resetregen').click();
      return { state: R.state, made: R.made, errors: R.errors, shown, base: SeqGen.moodFromBrief(DIR.cat.find(x => x.id === 'sam_theme'), DIR.briefs.sam_theme).style, ens: TempMaker.ENSEMBLES.jazz.roles, compat: TempMaker.STYLE_COMPAT };
    });
    t.eq([r.state, r.made, r.errors], ['done', 3, []]);
    t.ok(/jazz combo/.test(r.shown[0]) && r.shown[1] === 'on', JSON.stringify(r.shown));
    const dirs = fs.readdirSync(G('assets/audio/review/sam_theme')).filter(d => !before.has(d)).map(d => 'assets/audio/review/sam_theme/' + d + '/');
    wideTakes = dirs.map(d => Object.assign(json(d + 'meta.json'), { dir: d })).sort((a, b) => a.created.localeCompare(b.created));
    t.eq(wideTakes.length, 3);
    const lineups = wideTakes.map(m => ['bass', 'chords', 'lead', 'pad'].map(k => m.instruments[k]).join(' '));
    for (const m of wideTakes) {
      t.eq([m.request.ensemble, m.request.variety, m.mood.ensemble, m.mood.variety], ['jazz', 'wide', 'jazz', 'wide']);
      for (const k of ['bass', 'chords', 'lead', 'pad']) t.ok(r.ens[k].map(x => 'forge:' + x).includes(m.instruments[k]), k + ' ' + m.instruments[k] + ' from the jazz combo');
    }
    t.eq(new Set(lineups).size, 3, 'three line-ups: ' + lineups.join(' | '));
    const styles = wideTakes.map(m => m.mood.style);
    t.eq(styles[0], r.base, 'take 1 keeps the brief\'s style');
    t.ok(new Set(styles).size === 3 && styles.slice(1).every(s => r.compat[styles[0]].includes(s)), 'compatible, different styles: ' + styles.join(', '));
    await p.waitForFunction(n => DIR.takes.filter(m => m.request && m.request.variety === 'wide').length === n, 3, { timeout: 5000 });
    const card = await p.evaluate(take => { const i = DIR.takes.findIndex(m => m.take === take); return document.querySelector(`#takes [data-i="${i}"] .mood`).textContent + ' | ' + document.querySelector(`#takes [data-i="${i}"] .req`).textContent; }, wideTakes[1].take);
    t.ok(/jazz combo/.test(card) && /ensemble jazz · variety wide/.test(card), card);
  });
  await t.test('⟳ AGAIN on a wide / ensemble take makes the same take: same style, same instruments, same notes', async () => {
    const m = wideTakes[1]; t.ok(m, 'a wide take');
    const before = new Set(fs.readdirSync(G('assets/audio/review/sam_theme')));
    const r = await p.evaluate(async take => { const i = DIR.takes.findIndex(x => x.take === take); const o = regenOpts(DIR.takes[i]); const R = await requestTakes([DIR.sel], 1, o).done; return { state: R.state, o }; }, m.take);
    t.eq(r.state, 'done');
    t.ok(!('variety' in r.o) && r.o.ensemble === 'jazz' && r.o.style === m.mood.style, JSON.stringify(r.o));
    const d = fs.readdirSync(G('assets/audio/review/sam_theme')).find(x => !before.has(x)), again = json('assets/audio/review/sam_theme/' + d + '/meta.json');
    const pick = x => [x.mood.style, x.mood.key, x.mood.bpm, x.mood.seed, x.mood.ensemble, JSON.stringify(x.mood.vocab), JSON.stringify(x.instruments)];
    t.eq(pick(again), pick(m));
    t.ok(fs.readFileSync(G('assets/audio/review/sam_theme/' + d + '/song.mid')).equals(fs.readFileSync(G(m.dir + 'song.mid'))), 'the same notes (song.mid byte for byte)');
  });
  await t.test('VARIETY close: take 2 keeps take 1\'s style, key, tempo and instruments — only the notes change', async () => {
    const before = new Set(fs.readdirSync(G('assets/audio/review/sam_theme')));
    const r = await p.evaluate(async () => {
      document.getElementById('resetregen').click();
      document.querySelector('#ensembles [data-ens="rock"]').click(); document.querySelector('#variety [data-v="close"]').click(); document.querySelector('#ntakes [data-n="2"]').click();
      RG.roles = ['drums', 'bass', 'lead']; document.getElementById('r-lenmode').value = 'bars'; document.getElementById('r-len').value = 2; renderRegen();
      const R = await makeNow().done; document.getElementById('resetregen').click(); return { state: R.state, made: R.made };
    });
    t.eq([r.state, r.made], ['done', 2]);
    const ms = fs.readdirSync(G('assets/audio/review/sam_theme')).filter(d => !before.has(d)).map(d => json('assets/audio/review/sam_theme/' + d + '/meta.json')).sort((a, b) => a.created.localeCompare(b.created));
    const same = m => [m.mood.style, m.mood.mode, m.mood.key, m.mood.bpm, m.mood.ensemble, JSON.stringify(m.instruments)];
    t.eq(same(ms[1]), same(ms[0]));
    t.ok(ms[0].mood.seed !== ms[1].mood.seed && /^kit:(post_rock|four_floor)$/.test(ms[0].instruments.drums) && TempMaker_rock.lead.includes(ms[0].instruments.lead.replace(/^forge:/, '')), JSON.stringify(ms.map(m => [m.mood.seed, m.instruments])));
  });
  await t.test('KEY / BPM / FEEL / HARMONY / PROG / sound design reach the mood and the project', async () => {
    const before = new Set(fs.readdirSync(G('assets/audio/review/sam_theme')));
    const r = await p.evaluate(async () => {
      document.getElementById('resetregen').click();
      const set = (id, v) => { document.getElementById(id).value = v; document.getElementById(id).dispatchEvent(new Event('change')); };
      set('r-key', '5'); set('r-bpm', '100'); set('r-feel', 'shuffle'); set('r-harm', 'lush'); set('r-prog', 'blues'); set('r-mode', 'minor');
      set('r-tex', 'none'); set('r-fx', 'none'); set('r-hit', 'fx_glass_ping');
      document.querySelector('#ntakes [data-n="1"]').click(); RG.roles = ['drums', 'bass', 'chords']; set('r-lenmode', 'bars'); document.getElementById('r-len').value = 2; renderRegen();
      const form = regenForm(), sum = document.getElementById('moresum').textContent;
      const R = await makeNow().done;
      document.getElementById('resetregen').click();
      return { state: R.state, errors: R.errors, form, sum, blues: SeqGen.PROGS.blues.map(x => x.join()) };
    });
    t.eq([r.state, r.errors], ['done', []]);
    t.eq([r.form.key, r.form.bpm, r.form.feel, r.form.harmony, r.form.prog, r.form.textures, r.form.fx, r.form.hit], [5, 100, 'shuffle', 'lush', 'blues', 'none', 'none', 'fx_glass_ping']);
    t.ok(/texture none/.test(r.sum) && /hit glass ping/.test(r.sum), 'the folded MORE says what it holds: ' + r.sum);
    const d = fs.readdirSync(G('assets/audio/review/sam_theme')).find(x => !before.has(x)), dir = 'assets/audio/review/sam_theme/' + d + '/';
    const m = json(dir + 'meta.json'), proj = json(dir + 'project.json');
    t.eq([m.mood.key, Math.round(m.mood.bpm), m.mood.feel, m.mood.harmony, m.mood.prog, m.mood.textures, m.mood.fx, m.mood.hit], [5, 100, 'shuffle', 'lush', 'blues', 'none', 'none', 'fx_glass_ping']);
    t.ok(m.mood.vocab.ext.every(x => ['ninth', 'add9', 'seventh'].includes(x)), 'lush extensions: ' + m.mood.vocab.ext);
    t.ok(proj.groove && proj.groove.on && proj.groove.type === 'shuffle8' && proj.bpm === 100 && proj.key === 5, 'the project swings: ' + JSON.stringify(proj.groove));
    t.ok(r.blues.includes(proj.gen.o.progression ? proj.gen.o.progression.join() : '') || proj.gen.o.progFamily === 'blues', 'blues family asked: ' + JSON.stringify(proj.gen.o.progFamily));
    t.ok(proj.gen.o.hit === 'fx_glass_ping' && proj.gen.o.fx === 'none' && proj.gen.o.textures === 'none' && !proj.tracks.some(x => x.role === 'texture'), 'the composer got the sound design, no bed: ' + JSON.stringify([proj.gen.o.hit, proj.gen.o.fx, proj.gen.o.textures]));
  });
  await t.test('the picker offers the ensemble\'s own choices first, and kit flavours for drums', async () => {
    const r = await p.evaluate(async () => {
      RG.ensemble = 'jazz'; await openPicker('lead'); const lead = [...document.querySelectorAll('#pk-body .grp')].map(e => e.textContent);
      await openPicker('drums'); const kits = [...document.querySelectorAll('#pk-body [data-pv^="kit"]')].map(e => e.dataset.pv);
      document.querySelector('#pk-body [data-pv="kit:jazz"]').click(); const pick = RG.instruments.drums, form = TempMaker.normOpts(regenForm()).instruments;
      document.getElementById('resetregen').click(); return { lead, kits, pick, form };
    });
    t.ok(/^ENSEMBLE · jazz combo/.test(r.lead[1]), r.lead.slice(0, 3).join(' | '));
    t.ok(r.kits.includes('kit') && r.kits.includes('kit:jazz') && r.kits.includes('kit:standard') && r.kits.length >= 10, r.kits.join());
    t.eq([r.pick, r.form], ['kit:jazz', { drums: 'kit:jazz' }]);
  });
  await t.test('no page / console errors', async () => t.noErrors(errors));
  if (process.env.KEEP_GAME) console.log('  game folder kept: ' + GAME); else fs.rmSync(GAME, { recursive: true, force: true });
});
