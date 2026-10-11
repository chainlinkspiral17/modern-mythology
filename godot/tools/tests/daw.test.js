// DAW: compose, offline render, seamless loops, stems, undo, MIDI export, TEMP TRACKS → game folder
const { suite, TOOLS } = require('./harness');
const fs = require('fs'), os = require('os'), path = require('path');

suite('daw · compose, render, stems, undo, temp tracks', async t => {
  const { p, errors } = await t.page('daw.html', { start: true });
  await p.evaluate(async () => { window.confirm = () => true; document.getElementById('g-inst').value = 'forge'; document.getElementById('g-style').value = 'boom_bap'; document.getElementById('g-form').value = 'loop'; await generate({ force: true, seed: 42 }); await E.whenReady(); });

  await t.test('generated project: 5 parts on FORGE / KIT', async () => {
    const r = await p.evaluate(() => P.tracks.map(t => t.role + ':' + E.dev(t.deviceId).type));
    t.eq(r, ['drums:kit', 'bass:forge', 'chords:forge', 'lead:forge', 'pad:forge']);
  });
  await t.test('offline render: exact length, audible, faster than real time', async () => {
    const r = await p.evaluate(async () => { const t0 = performance.now(); const o = await E.renderOffline({ fromBar: 0, toBar: 2, loop: true }); return { len: o.channels[0].length, want: Math.round(2 * BAR * E.spt() * 44100), pk: AK.util.peakOf(o.channels), ms: performance.now() - t0, sec: o.lenSec }; });
    t.eq(r.len, r.want, 'samples'); t.ok(r.pk > 0.05, 'peak ' + r.pk); t.ok(r.ms / 1000 < r.sec * 2.5, 'render took ' + Math.round(r.ms) + ' ms');
  });
  await t.test('seamless loop: the wrap is no bigger than an ordinary step', async () => {
    const r = await p.evaluate(async () => { const o = await E.renderOffline({ fromBar: 0, toBar: 2, loop: true }); const c = o.channels[0]; let s = 0; for (let i = 1; i < c.length; i++) s += Math.abs(c[i] - c[i - 1]); return { wrap: Math.abs(c[0] - c[c.length - 1]), mean: s / c.length }; });
    t.ok(r.wrap < Math.max(0.02, r.mean * 20), `wrap ${r.wrap.toFixed(4)} vs mean step ${r.mean.toFixed(4)}`);
  });
  await t.test('stems: one per part, envelopes sum to the un-limited mix', async () => {
    const r = await p.evaluate(async () => {
      const stems = await E.renderStems({ groups: stemGroups(), fromBar: 0, toBar: 2, loop: true });
      const mix = await E.renderOffline({ fromBar: 0, toBar: 2, loop: true, limiter: false }), sum = sumChannels(stems);
      const env = c => { const w = 2205, o = []; for (let i = 0; i + w <= c.length; i += w) { let s = 0; for (let k = i; k < i + w; k++) s += c[k] * c[k]; o.push(Math.sqrt(s / w)); } return o; };
      const a = env(sum[0]), b = env(mix.channels[0]); let ma = 0, mb = 0; a.forEach((v, i) => { ma += v; mb += b[i]; }); ma /= a.length; mb /= b.length;
      let x = 0, ya = 0, yb = 0; a.forEach((v, i) => { x += (v - ma) * (b[i] - mb); ya += (v - ma) ** 2; yb += (b[i] - mb) ** 2; });
      return { names: stems.map(s => s.name), corr: x / Math.sqrt(ya * yb) };
    });
    t.eq(r.names, ['drums', 'bass', 'chords', 'lead', 'pad']); t.ok(r.corr > 0.99, 'envelope corr ' + r.corr.toFixed(4));
  });
  await t.test('undo / redo an arrangement edit (no instrument reload)', async () => {
    const r = await p.evaluate(async () => {
      const sl = ms => new Promise(r => setTimeout(r, ms)); await sl(400);
      const inst0 = E.devices.get(P.devices[1].id), c = P.tracks[0].clips[0], b0 = c.bar;
      P.tracks[0].clips[0].bar = b0 + 3; saveSoon(); await sl(400);
      await undo(); const afterUndo = P.tracks[0].clips[0].bar; await redo(); const afterRedo = P.tracks[0].clips[0].bar;
      return { b0, afterUndo, afterRedo, same: E.devices.get(P.devices[1].id) === inst0 };
    });
    t.eq([r.afterUndo, r.afterRedo], [r.b0, r.b0 + 3]); t.ok(r.same, 'devices were reloaded');
  });
  await t.test('MIDI export: drums on channel 10, all five parts', async () => {
    const r = await p.evaluate(() => SMF.read(E.exportMidi()).tracks.map(t => t.name + ':' + t.channel));
    t.eq(r, ['drums:10', 'bass:1', 'chords:1', 'lead:1', 'pad:1']);
  });

  const SLOW = !!process.env.TEST_SLOW;   // stems = one full render per part (~5× the time)
  await t.test('TEMP TRACKS follow the MusicDirector briefs: most-played first, composed for their scenes', async () => {
    const game = fs.mkdtempSync(path.join(os.tmpdir(), 'mmbrief-'));
    fs.mkdirSync(path.join(game, 'resources', 'music'), { recursive: true });
    fs.writeFileSync(path.join(game, 'resources', 'music_catalog.json'), JSON.stringify([
      { id: 'a_bed', vol: 1, title: 'A Bed', src: 'assets/audio/bgm/a_bed.ogg', desc: 'Quiet room tone.' },
      { id: 'b_theme', vol: 1, title: 'B Theme', src: 'assets/audio/bgm/b_theme.ogg', desc: 'A character theme.' },
      { id: 'c_free', vol: 1, title: 'C Unused', src: 'assets/audio/bgm/c_free.ogg', desc: 'Nobody plays this one.' }]));
    const brief = (id, n, roles, e, dk, stems) => ({ id, scene_count: n, scenes: [], roles, baseline: 0.5, intensity: { p10: 0.4, mean: 0.5, p90: stems ? 0.7 : 0.5 }, stems, words: [], chars: [], locales: [], moments: {}, energy: e, darkness: dk });
    fs.writeFileSync(path.join(game, 'resources', 'music', 'temp_briefs.json'), JSON.stringify({ tracks: [
      brief('b_theme', 12, { leitmotif: 12 }, 0.9, 0.95, true), brief('a_bed', 3, { locale: 3 }, 0.1, 0.1, false)] }));
    await p.exposeFunction('__bexists', rel => fs.existsSync(path.join(game, rel)));
    await p.exposeFunction('__bread', rel => fs.readFileSync(path.join(game, rel), 'utf8'));
    const r = await p.evaluate(async () => {
      const keep = { root: AK.game.root, exists: AK.game.exists, readText: AK.game.readText };
      AK.game.root = { name: 'brief' }; AK.game.exists = rel => window.__bexists(rel); AK.game.readText = rel => window.__bread(rel);
      document.getElementById('g-musiconly').checked = false; document.getElementById('g-vnfirst').checked = true;
      await refreshWanted();
      const on = orderWanted().map(x => x.id), mb = moodOf(wanted.find(x => x.id === 'b_theme')), ma = moodOf(wanted.find(x => x.id === 'a_bed'));
      const plain = SeqGen.moodFromText('B Theme', 'A character theme.', 'b_theme');
      const shown = document.getElementById('g-wanted').textContent;
      document.getElementById('g-vnfirst').checked = false; await refreshWanted();
      const off = orderWanted().map(x => x.id), plainOrder = wanted.map(x => x.id);
      document.getElementById('g-vnfirst').checked = true; document.getElementById('g-musiconly').checked = true;
      Object.assign(AK.game, keep);
      return { on, off, plainOrder, mb, ma, plain, shown };
    });
    t.eq(r.on, ['b_theme', 'a_bed', 'c_free'], 'most-played first, unplayed last');
    t.eq(r.off, r.plainOrder, 'VN-first off: the usual order');
    t.ok(r.on.join() !== r.off.join(), 'briefs change the order');
    t.eq([r.mb.form, r.mb.stems], ['song', true], 'leitmotif → a song form; a moving intensity → stems');
    t.ok(r.mb.bpm > r.ma.bpm || r.mb.style !== r.ma.style, `energy: ${r.mb.bpm} vs ${r.ma.bpm}`);
    t.ok(['minor', 'phrygian', 'dorian', 'harmonic'].includes(r.mb.mode), 'dark scenes → a dark mode: ' + r.mb.mode);
    t.ok(r.mb.density > r.plain.density, `busier than the text-only mood: ${r.mb.density} vs ${r.plain.density}`);
    t.ok(/12 scenes/.test(r.shown) && /leitmotif 12/.test(r.shown), 'the list says why');
  });
  await t.test('TEMP TRACKS writes a mastered ≥ 90 s track' + (SLOW ? ' + stems + manifest' : '') + ' into the game folder', async () => {
    const game = fs.mkdtempSync(path.join(os.tmpdir(), 'mmgame-'));
    fs.mkdirSync(path.join(game, 'resources'), { recursive: true });
    fs.writeFileSync(path.join(game, 'resources', 'music_catalog.json'), JSON.stringify([
      { id: 'test_club', vol: 1, title: 'Test Club', src: 'assets/audio/bgm/test_club.ogg', desc: 'Intercut. Dancing. Loud music club thump.' }]));
    await p.exposeFunction('__exists', rel => fs.existsSync(path.join(game, rel)));
    await p.exposeFunction('__read', rel => fs.readFileSync(path.join(game, rel), 'utf8'));
    await p.exposeFunction('__write', (rel, b64) => { const f = path.join(game, rel); fs.mkdirSync(path.dirname(f), { recursive: true }); fs.writeFileSync(f, Buffer.from(b64, 'base64')); return true; });
    const r = await p.evaluate(async (SLOW) => {
      AK.game.root = { name: 'test' }; AK.game.exists = rel => window.__exists(rel); AK.game.readText = rel => window.__read(rel);
      AK.game.write = async (rel, blob) => { const u = new Uint8Array(await blob.arrayBuffer()); let s = ''; for (let i = 0; i < u.length; i += 0x8000) s += String.fromCharCode.apply(null, u.subarray(i, i + 0x8000)); return window.__write(rel, btoa(s)); };
      document.getElementById('g-inst').value = 'forge'; document.getElementById('g-tempstems').checked = SLOW;
      await refreshWanted(); tempPick = wanted[0]; await tempTracks();
      return window.lastTempTracks[0];
    }, SLOW);
    t.ok(!r.error, r.error); t.ok(r.sec >= 90, 'length ' + r.sec); t.near(r.lufs, -14, 0.6, 'LUFS');
    if (SLOW) {
      const man = JSON.parse(fs.readFileSync(path.join(game, 'assets/audio/bgm/test_club.stems.json'), 'utf8'));
      t.eq(man.stems.map(s => s.name + '@' + s.layer), ['drums@0.5', 'bass@0.25', 'chords@0', 'lead@0.75', 'pad@0']);
      for (const s of man.stems) t.ok(fs.statSync(path.join(game, s.file)).size > 100000, s.file);
    }
    t.ok(fs.statSync(path.join(game, 'assets/audio/bgm/test_club.wav')).size > 1e6, 'mix wav');
    fs.rmSync(game, { recursive: true, force: true });
  });
  await t.test('no page / console errors', async () => t.noErrors(errors));
});
