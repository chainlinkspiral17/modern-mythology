// DAW: compose, offline render, seamless loops, stems, undo, MIDI export, TEMP TRACKS → game folder
const { suite, TOOLS } = require('./harness');
const fs = require('fs'), os = require('os'), path = require('path');

suite('daw · compose, render, stems, undo, temp tracks', async t => {
  const { p, errors } = await t.page('daw.html', { start: true });
  await p.evaluate(async () => { window.confirm = () => true; document.getElementById('g-inst').value = 'forge'; document.getElementById('g-style').value = 'boom_bap'; document.getElementById('g-form').value = 'loop'; await generate({ force: true, seed: 42 }); await E.whenReady(); });

  await t.test('generated project: 5 parts on FORGE / KIT', async () => {
    const r = await p.evaluate(() => P.tracks.map(t => t.role + ':' + E.dev(t.deviceId).type));
    t.eq(r.filter(x => !/^(texture|fx):/.test(x)), ['drums:kit', 'bass:forge', 'chords:forge', 'lead:forge', 'pad:forge']);
    t.ok(r.filter(x => /^(texture|fx):/.test(x)).every(x => x.endsWith(':forge')), 'the sound-design layer (beds, risers, hits) is FORGE: ' + r);
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
    t.eq(r.names.filter(n => n !== 'texture' && n !== 'fx'), ['drums', 'bass', 'chords', 'lead', 'pad']); t.ok(r.corr > 0.99, 'envelope corr ' + r.corr.toFixed(4));
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
    t.eq(r.filter(x => !/^(texture2?|fx|hit):/.test(x)), ['drums:10', 'bass:1', 'chords:1', 'lead:1', 'pad:1']);
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
  await t.test('TEMP TRACKS "straight into game (skip review)" writes a mastered ≥ 90 s track as small Ogg Vorbis' + (SLOW ? ' + Ogg stems' : '') + ' + manifest into the game folder, replacing an older .wav temp', async () => {
    const game = fs.mkdtempSync(path.join(os.tmpdir(), 'mmgame-'));
    fs.mkdirSync(path.join(game, 'resources'), { recursive: true });
    fs.writeFileSync(path.join(game, 'resources', 'music_catalog.json'), JSON.stringify([
      { id: 'test_club', vol: 1, title: 'Test Club', src: 'assets/audio/bgm/test_club.ogg', desc: 'Intercut. Dancing. Loud music club thump.' }]));
    await p.exposeFunction('__exists', rel => fs.existsSync(path.join(game, rel)));
    await p.exposeFunction('__read', rel => fs.readFileSync(path.join(game, rel), 'utf8'));
    await p.exposeFunction('__write', (rel, b64) => { const f = path.join(game, rel); fs.mkdirSync(path.dirname(f), { recursive: true }); fs.writeFileSync(f, Buffer.from(b64, 'base64')); return true; });
    await p.exposeFunction('__rb', rel => fs.readFileSync(path.join(game, rel)).toString('base64'));
    await p.exposeFunction('__ls', rel => { try { return fs.readdirSync(path.join(game, rel), { withFileTypes: true }).map(d => ({ name: d.name, kind: d.isDirectory() ? 'directory' : 'file' })); } catch (e) { return []; } });
    await p.exposeFunction('__rm', rel => { const f = path.join(game, rel); if (!fs.existsSync(f)) return false; fs.rmSync(f, { recursive: true, force: true }); return true; });
    const r = await p.evaluate(async (SLOW) => {
      AK.game.root = { name: 'test' }; AK.game.exists = rel => window.__exists(rel); AK.game.readText = rel => window.__read(rel);
      AK.game.write = async (rel, blob) => { const u = new Uint8Array(await blob.arrayBuffer()); let s = ''; for (let i = 0; i < u.length; i += 0x8000) s += String.fromCharCode.apply(null, u.subarray(i, i + 0x8000)); return window.__write(rel, btoa(s)); };
      AK.game.readFile = async rel => { const b = atob(await window.__rb(rel)), u = new Uint8Array(b.length); for (let i = 0; i < b.length; i++) u[i] = b.charCodeAt(i); return new Blob([u]); };
      AK.game.list = rel => window.__ls(rel); AK.game.remove = rel => window.__rm(rel);
      document.getElementById('g-inst').value = 'forge'; document.getElementById('g-tempstems').checked = SLOW;
      document.getElementById('g-skipreview').checked = true;      // the direct write (review staging: audio_director suite)
      await refreshWanted(); tempPick = wanted[0];
      // an older temp, from before Ogg: it would shadow the new .temp.ogg, so it has to go
      const c = new Float32Array(4410); await AK.game.write('assets/audio/bgm/test_club.wav', AK.wav.encode([c, c], 44100, { meta: { title: 'Test Club (temp)', temp: true } }));
      await tempTracks();
      return window.lastTempTracks[0];
    }, SLOW);
    t.ok(!r.error, r.error); t.ok(r.sec >= 90, 'length ' + r.sec); t.near(r.lufs, -14, 0.6, 'LUFS');
    const B = path.join(game, 'assets/audio/bgm/test_club'), mbMin = f => fs.statSync(f).size / r.sec * 60 / 1048576;
    const man = JSON.parse(fs.readFileSync(B + '.stems.json', 'utf8'));
    t.eq([man.temp, man.format, man.mix, man.loop], [true, 'ogg', 'assets/audio/bgm/test_club.temp.ogg', false]); t.near(man.frames, r.sec * 44100, 50, 'frames');
    if (SLOW) {
      t.eq(man.stems.map(s => s.name + '@' + s.layer).filter(x => !/^(texture|fx)@/.test(x)), ['drums@0.5', 'bass@0.25', 'chords@0', 'lead@0.75', 'pad@0']);
      t.ok(man.stems.every(s => s.name !== 'texture' || s.layer === 0) && man.stems.every(s => s.name !== 'fx' || s.layer === 0.5), 'bed always on, fx with the drums');
      for (const s of man.stems) { const m = mbMin(path.join(game, s.file)); t.ok(s.file.endsWith('.ogg') && m > 0.02 && m < 0.8, s.file + ' ' + m.toFixed(2) + ' MB/min'); }
      console.log('    stems (MB/min): ' + man.stems.map(s => s.name + ' ' + mbMin(path.join(game, s.file)).toFixed(2)).join(', '));
    }
    t.eq(fs.readFileSync(B + '.temp.ogg').toString('ascii', 0, 4), 'OggS');
    const mix = mbMin(B + '.temp.ogg');
    console.log(`    temp mix: ${(fs.statSync(B + '.temp.ogg').size / 1048576).toFixed(2)} MB for ${r.sec.toFixed(1)} s = ${mix.toFixed(2)} MB/min (16-bit WAV: 10.1)`);
    t.ok(mix > 0.1 && mix < 1.3, 'mix ' + mix.toFixed(2) + ' MB/min');
    t.ok(!fs.existsSync(B + '.wav'), 'the older .wav temp is gone');
    fs.rmSync(game, { recursive: true, force: true });
  });
  await t.test('PLAY: RENDER (the default ▶): streams the render — starts in about a second, sounds exactly like the bounce, loops, cached replay', async () => {
    const r = await p.evaluate(async () => {
      const sl = ms => new Promise(res => setTimeout(res, ms)), sr = E.ctx.sampleRate;
      E._rcache = null; E.diag = [];
      P.loop = { on: false, a: 0, b: 4 };
      const songEnd = E.songBars();
      const cap = new AK.Capture(E.ctx, E.out, { preRollSec: 0, maxChannels: 2 }); await cap.start(); cap.begin(0);
      const t0 = performance.now(); let startMs = null;
      E.on('transport', x => { if (x.playing && startMs === null) startMs = performance.now() - t0; });
      document.getElementById('play').click();                       // the button: PLAY mode defaults to RENDER
      while (startMs === null && performance.now() - t0 < 20000) await sl(20);
      const rendered = !!E._rendered;
      await sl(5000);
      const tick = E.tickNow(); E.stop();
      const res = cap.end(); cap.stop();
      while (!E._rcache) await sl(100);                             // the render finishes on its own after ■
      // streamed output == the finished render, sample for sample (the live master's gain is undone)
      const R = E._rcache.buf.getChannelData(0), C = res.channels[0];
      // align on the loudest moment of the render's first 3 s, then compare everything the capture overlaps
      let k = Math.round(sr * 0.3); for (let i = k; i < Math.min(R.length, sr * 3); i++) if (Math.abs(R[i]) > Math.abs(R[k])) k = i;
      const w0 = Math.max(0, k - 1024); let best = -1, bestErr = Infinity;
      for (let o = 0; o + 2048 < C.length; o++) { let e = 0; for (let i = 0; i < 2048; i += 4) { const d = C[o + i] - R[w0 + i]; e += d * d; if (e > bestErr) break; } if (e < bestErr) { bestErr = e; best = o; } }
      const at = best - w0, i0 = Math.max(0, -at), i1 = Math.min(R.length, C.length - at); let maxd = 0;
      for (let i = i0; i < i1; i++) maxd = Math.max(maxd, Math.abs(C[at + i] - R[i]));
      const first = i1 - i0;
      // loop: the playhead wraps on the loop; ▶ again with no edits plays from the cache at once
      P.loop = { on: true, a: 0, b: 1 };
      await E.playRendered(); while (!E.playing) await sl(20);
      const lenMs = BAR * E.spt() * 1000, ticks = [];
      for (let i = 0; i < 8; i++) { await sl(lenMs / 3); ticks.push(E.tickNow()); }
      E.stop(); while (E._rjob) await sl(100);
      const t1 = performance.now(); await E.playRendered(); const cachedMs = performance.now() - t1, cachedOn = E.playing; E.stop();
      P.loop = { on: true, a: 0, b: 2 };
      return { dbg: [k, best, at, first], bar: BAR, startMs, rendered, tick, maxd, ticks, cachedMs, cachedOn, songEnd, notes: E.diag.filter(x => x.kind === 'audio').map(x => x.msg) };
    });
    t.ok(r.rendered, 'the ▶ button played rendered');
    t.ok(r.startMs < 8000, 'first sound after ' + Math.round(r.startMs) + ' ms (8 parts incl. the sound layer, a 90 s song)');
    t.ok(r.tick > r.bar, 'playhead moved: ' + r.tick);
    t.ok(r.dbg[3] > 44100 * 3 && r.maxd < 1e-5, 'streamed output vs the finished render over ' + (r.dbg[3] / 44100).toFixed(1) + ' s, max diff ' + r.maxd);
    t.ok(r.ticks.every(x => x >= 0 && x < r.bar), 'loop playhead stays in bar 1: ' + r.ticks.map(Math.round).join(' '));
    t.ok(r.ticks.some((x, i) => i && x < r.ticks[i - 1]), 'and wraps');
    t.ok(r.cachedOn && r.cachedMs < 200, 'cached replay ' + Math.round(r.cachedMs) + ' ms');
    t.ok(!r.notes.some(m => /fell behind/.test(m)), 'never fell behind: ' + JSON.stringify(r.notes));
  });
  await t.test('PLAY mode toggle (RENDER / LIVE) + LIVE SOUND light / full', async () => {
    const r = await p.evaluate(async () => {
      const sl = ms => new Promise(res => setTimeout(res, ms));
      document.getElementById('playmode').click();
      const mode = [E.playMode, document.getElementById('playmode').textContent];
      document.getElementById('play').click(); await sl(600);
      const live = [E.playing, !!E._rendered]; E.stop();
      document.getElementById('playmode').click();
      await E.setLiveQuality('full');
      const full = [...E.devices.values()].filter(i => 'light' in i).map(i => i.light);
      await E.setLiveQuality('light');
      const light = [...E.devices.values()].filter(i => 'light' in i).map(i => i.light);
      await E.play(0); await sl(1500); const lv = E._level(E._tap('out', E.out)); E.stop();
      return { mode, live, back: E.playMode, full, light, lv, stored: localStorage.getItem('mm_daw_live') };
    });
    t.eq(r.mode, ['live', 'LIVE'], 'toggle → LIVE');
    t.eq(r.live, [true, false], '▶ in LIVE plays live');
    t.eq(r.back, 'render', 'toggle back');
    t.ok(r.full.length >= 4 && r.full.every(x => x === false), 'FULL: no light devices');
    t.ok(r.light.length >= 4 && r.light.every(x => x === true), 'LIGHT: every FORGE / KIT device light');
    t.ok(r.lv > 0.01, 'light live playback sounds: ' + r.lv);
    t.eq(r.stored, 'light');
  });
  await t.test('no page / console errors', async () => t.noErrors(errors));
});
