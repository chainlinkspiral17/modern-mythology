// DAW recording: count-in, punch in/out (replace / overdub), loop takes (MIDI + audio), latency
// (FM-1 CHECK-OUT pickup, loopback calibration, compensation), takes UI + undo, save / reload, old projects,
// finger controls. MIDI comes from the mock FM-1 (tests/mocks/fm1_mock.js) with exact event time stamps;
// audio from its fake USB input (gated 23 ms after each note-on) or a delay line off the click bus.
// Real-time transport at 300 BPM (a bar = 0.8 s), so the suite stays fast.
const { suite } = require('./harness');
const { PROFILES, MOCK } = require('./mocks/fm1_mock');

const init = `localStorage.setItem('mm_fm1_latency_ms', '23');
window.__FM1_PROFILE = ${JSON.stringify(Object.assign({ audioMode: 'gate' }, PROFILES.felucca))};(${MOCK})();`;

suite('daw rec · count-in, punch, loop takes, latency', async t => {
  const o = await t.page('daw.html', { init, touch: true, start: true, settle: 400 });
  const { p, errors, cdp } = o;
  const f = t.touch(cdp);
  await p.waitForFunction(() => typeof P !== 'undefined' && P && E.midi && E.midi.output, null, { timeout: 10000 });

  // page-side helpers (again after a reload)
  const helpers = () => p.evaluate(() => {
    const sleep = ms => new Promise(r => setTimeout(r, ms));
    const RT = window.RT = {
      sleep,
      async fresh(rec = {}) {
        if (E.recording) await E.stopRecord();
        E.stop();
        const j = DAW.Engine.newProject(); j.bpm = 300; j.loop = { on: false, a: 0, b: 1 }; j.rec = Object.assign({ countIn: 0, mode: 'replace', quant: 0 }, rec);
        await E.load(j); P = E.project; sel = { trackId: null, clip: -1 }; E._stopTick = 0; E.emit('project');
        E.setLatency('midi', 0);
      },
      async midiTrack(name = 'keys') {
        const d = await E.addDevice('basic', { name: 'basic' });
        const tr = E.addTrack('midi', { name, deviceId: d.id }); tr.arm = true; sel.trackId = tr.id; return tr;
      },
      spt: () => E.spt(),
      // a key struck when tick-time T is HEARD (scheduled time + the master look-ahead), released dur seconds later,
      // sent as MIDI with that exact time stamp. The stamp is worked out just before the strike: an audio glitch moves
      // the context clock against performance time, and a performer follows what they hear after it.
      key(T, n, dur = 0.03, extraMs = 0) {
        const at = (Tx, bytes) => {
          const lead = (Tx - E.ctxAtPerf(performance.now())) * 1000;
          setTimeout(() => { const ts = E.perfTime(Tx + E.outDelay) + extraMs; setTimeout(() => __fm1mock.raw(bytes, ts), Math.max(0, ts - performance.now() + 1)); }, Math.max(0, lead - 40));
        };
        at(T, [0x92, n, 100]); at(T + dur, [0x82, n, 0]);
      },
      async untilCtx(T) { while (E.ctx.currentTime < T) await sleep(10); },
      notes: trackId => SMF.read(E.exportMidi([trackId])).tracks[0].notes.map(n => [n.n, n.t]).sort((a, b) => a[1] - b[1] || a[0] - b[0]),
      onset(c, thr = 0.01, from = 0) { for (let i = from; i < c.length; i++) if (Math.abs(c[i]) > thr) return i; return -1; },
      onsets(c, thr, gap) { const o = []; for (let i = 0; i < c.length; i++) if (Math.abs(c[i]) > thr) { o.push(i); i += gap; } return o; },
    };
  });
  await helpers();

  await t.test('latency: FM-1 CHECK-OUT value picked up at start and live from another tab; FM-1 input selects it', async () => {
    const r1 = await p.evaluate(() => ({ fm1: E.lat.fm1, kind: E.audioLatencyKind(), btn: document.getElementById('latbtn').textContent }));
    t.eq(r1.fm1, { ms: 23, src: 'checkout' }, 'fm1 latency');
    t.eq(r1.kind, 'input', 'no input → play-along number');
    const r2 = await p.evaluate(async () => { await E.setInput('fm1'); return { kind: E.audioLatencyKind(), label: E.inputLabel, ms: E.latencyMs, btn: document.getElementById('latbtn').textContent, now: document.getElementById('lat-now').textContent }; });
    t.eq([r2.kind, r2.ms], ['fm1', 23], 'FM-1 input → FM-1 number (' + r2.label + ')');
    t.ok(/REC ⚙ 23 ms/.test(r2.btn), 'REC button: ' + r2.btn);
    t.ok(/FM-1 RETURN \+ [\d.]+ ms master look-ahead/.test(r2.now), 'panel says which number applies: ' + r2.now);
    const other = await o.ctx.newPage();                    // CHECK-OUT re-measures in another tab
    await other.goto('file://' + require('path').join(require('./harness').TOOLS, 'index.html'));
    await other.evaluate(() => localStorage.setItem('mm_fm1_latency_ms', '27.5'));
    await p.waitForTimeout(300);
    t.eq(await p.evaluate(() => E.lat.fm1), { ms: 27.5, src: 'checkout' }, 'storage event');
    await other.evaluate(() => localStorage.setItem('mm_fm1_latency_ms', '23')); await other.close(); await p.waitForTimeout(200);
    const r3 = await p.evaluate(() => { E.setLatency('fm1', 40); const m = E.lat.fm1; E.checkoutLatency(); const kept = E.lat.fm1.ms; E.checkoutLatency(true); return { m, kept, back: E.lat.fm1 }; });
    t.eq([r3.m.src, r3.kept, r3.back.ms, r3.back.src], ['manual', 40, 23, 'checkout'], 'manual wins until CHECK-OUT is asked for');
  });

  await t.test('count-in: 1 bar of click first, notes in its last 1/16 land on the record start, earlier ones dropped', async () => {
    const r = await p.evaluate(async () => {
      await RT.fresh({ countIn: 1 }); const tr = await RT.midiTrack();
      const clicks = [], orig = E.clickAt.bind(E); E.clickAt = (w, hi) => { clicks.push([w, hi]); orig(w, hi); };
      E.setLatency('midi', 5);
      await E.startRecord();
      const R = E.rec, live = R.liveCtx, a0 = E._anchors[0], spt = RT.spt();
      RT.key(live - 0.03, 60);              // inside the last 1/16 (50 ms) of the count-in
      RT.key(live - 0.15, 61);              // too early: count-in
      RT.key(live + 192 * spt, 62, 0.03, 5);   // beat 3 — struck 5 ms late, the MIDI nudge (5 ms) takes it back
      await RT.untilCtx(live + 192 * spt + 0.12);
      const raw = (E.rec.tracks.get(tr.id).last || {}).raw;
      await RT.untilCtx(live + 0.6); await E.stopRecord(); E.stop();
      E.clickAt = orig;
      const pat = Object.values(tr.patterns)[0];
      return { lead: live - a0.ctx, bar: BAR * spt, clicks: clicks.map(([w, hi]) => [+((w - a0.ctx) / (PPQ * spt)).toFixed(3), hi]), notes: pat.notes.map(n => [n.n, n.t]), rawErrMs: (raw - 192) * spt * 1000 };
    });
    t.near(r.lead, r.bar, 1e-6, 'record start one bar after the transport start');
    t.eq(r.clicks, [[0, true], [1, false], [2, false], [3, false]], 'four count-in clicks (in beats), accent on the bar, none after');
    t.eq(r.notes, [[60, 0], [62, 192]], 'notes');
    t.near(r.rawErrMs, 0, 2, 'beat-3 note placement before rounding (ms)');
  });

  for (const mode of ['replace', 'overdub']) {
    await t.test('punch (MIDI ' + mode + '): pre-roll from bar 1, only bar 2 is recorded' + (mode === 'replace' ? ', and replaced' : ', merged'), async () => {
      const r = await p.evaluate(async mode => {
        await RT.fresh({ mode }); const tr = await RT.midiTrack();
        const pid = E.uid('pat'); tr.patterns[pid] = { name: 'orig', lenBars: 4, notes: [...Array(16).keys()].map(k => ({ t: k * 96, d: 24, n: 48, v: 0.8 })) }; tr.clips.push({ bar: 0, pid });
        P.punch = { on: true, a: 1, b: 2 };
        await E.startRecord();
        const a0 = E._anchors[0], spt = RT.spt();
        for (let k = 0; k < 10; k++) RT.key(a0.ctx + (48 + k * 96) * spt, 72);    // an 8th after every beat of bars 1–3
        await RT.untilCtx(a0.ctx + 2.5 * BAR * spt); await E.stopRecord(); E.stop();
        return { start: a0.tick, notes: RT.notes(tr.id), takes: (tr.takes || []).map(k => [k.region.a, k.region.b, k.active]) };
      }, mode);
      t.eq(r.start, 0, 'transport pre-rolled from bar 1');
      const orig = r.notes.filter(n => n[0] === 48).map(n => n[1]), rec = r.notes.filter(n => n[0] === 72).map(n => n[1]);
      // membership is the point here (exact timing: count-in / audio checks); a headless audio glitch can shift one by a few ticks
      t.eq(rec.length, 4, 'recorded notes: bar 2 only — ' + rec);
      [432, 528, 624, 720].forEach((w, i) => t.near(rec[i], w, 5, 'note ' + (i + 1)));
      t.ok(rec.every(x => x >= 384 && x < 768), 'inside the punch');
      const want = mode === 'replace' ? [0, 96, 192, 288, 768, 864, 960, 1056, 1152, 1248, 1344, 1440] : [...Array(16).keys()].map(k => k * 96);
      t.eq(orig, want, 'existing notes');
      t.eq(r.takes, [[1, 2, true]], 'one take for the punch region');
    });
  }

  await t.test('loop takes (MIDI): 3 passes → 3 takes, the last plays; pick / undo / redo / delete / keep only', async () => {
    const r = await p.evaluate(async () => {
      await RT.fresh(); const id = (await RT.midiTrack()).id; P.loop = { on: true, a: 0, b: 1 };
      await E.startRecord();
      const a0 = E._anchors[0], spt = RT.spt();
      for (let k = 0; k < 3; k++) RT.key(a0.ctx + k * BAR * spt + 96 * spt, 60 + k);
      await RT.untilCtx(a0.ctx + 3 * BAR * spt + 0.1); await E.stopRecord(); E.stop();
      const tr = { get id() { return id; }, get patterns() { return E.track(id).patterns; }, get clips() { return E.track(id).clips; } };   // undo swaps the track objects
      const g = () => E.takeGroups(E.track(id))[0], out = { n: g().takes.length, names: g().takes.map(k => k.name), active: g().active.name, plays: RT.notes(tr.id) };
      await RT.sleep(400);                                          // the recording's undo step lands
      E.pickTake(tr.id, g().takes[0].id); out.picked = RT.notes(tr.id);
      await RT.sleep(400); await undo(); out.undone = RT.notes(tr.id); await redo(); out.redone = RT.notes(tr.id);
      E.deleteTake(tr.id, g().active.id); out.afterDel = [g().takes.length, g().active.name, RT.notes(tr.id)];
      E.keepOnlyActive(tr.id, g().key); out.afterKeep = [g().takes.length, Object.keys(tr.patterns).length, tr.clips.length];
      return out;
    });
    t.eq([r.n, r.names, r.active], [3, ['take 1', 'take 2', 'take 3'], 'take 3']);
    t.eq(r.plays, [[62, 96]], 'take 3 plays');
    t.eq(r.picked, [[60, 96]], 'picking take 1 changes what plays');
    t.eq([r.undone, r.redone], [[[62, 96]], [[60, 96]]], 'undo / redo the pick');
    t.eq(r.afterDel, [2, 'take 3', [[62, 96]]], 'deleting the playing take hands over to the newest other');
    t.eq(r.afterKeep, [1, 1, 1], 'keep only active: one take, one pattern, one clip');
  });

  await t.test('loop takes (MIDI overdub loop): every pass into one take', async () => {
    const r = await p.evaluate(async () => {
      await RT.fresh({ mode: 'loop', quant: 24 }); const tr = await RT.midiTrack(); P.loop = { on: true, a: 0, b: 1 };
      await E.startRecord();
      const a0 = E._anchors[0], spt = RT.spt();
      for (let k = 0; k < 3; k++) RT.key(a0.ctx + k * BAR * spt + (96 * (k + 1) + 5) * spt, 60 + k);   // a little late: quantize pulls them in
      RT.key(a0.ctx + 3 * BAR * spt - 4 * spt, 70);     // just before the wrap → quantized onto the downbeat (folded in: the pass after never ends)
      await RT.untilCtx(a0.ctx + 3 * BAR * spt + 0.1); await E.stopRecord(); E.stop();
      return { takes: tr.takes.length, notes: RT.notes(tr.id) };
    });
    t.eq(r.takes, 1);
    t.eq(r.notes, [[70, 0], [60, 96], [61, 192], [62, 288]]);
  });

  await t.test('loop takes (audio, FM-1 over MIDI): one capture → 3 sample-exact slices, aligned to ±2 ms with CHECK-OUT\'s 23 ms', async () => {
    const r = await p.evaluate(async () => {
      await RT.fresh(); P.loop = { on: true, a: 0, b: 1 };
      const hw = await E.addDevice('hw', { name: 'FM-1' });
      const mt = E.addTrack('midi', { name: 'fm1 part', deviceId: hw.id }); const pid = E.uid('pat');
      mt.patterns[pid] = { name: 'p', lenBars: 1, notes: [{ t: 96, d: 24, n: 60, v: 0.9 }] }; mt.clips.push({ bar: 0, pid });
      const at = E.addTrack('audio', { name: 'fm1 audio' }); at.arm = true; sel.trackId = at.id;
      await E.setInput('fm1');
      let pass = 0; const vary = () => { if (RT.vary) mt.patterns[pid].notes[0].t = 96 + 48 * ++pass; };   // each pass plays its note later
      RT.vary = true; E.on('loop', vary);
      await E.startRecord();
      const a0 = E._anchors[0], spt = RT.spt();
      await RT.untilCtx(a0.ctx + 3 * BAR * spt + 0.1); await E.stopRecord(); E.stop(); RT.vary = false;
      const R = E.lastRec, sr = E.ctx.sampleRate, out = { lat: R.lat, made: R.made.map(m => [m.p, m.n]), f0d: R.made.map(m => m.f0 - R.made[0].f0), takes: [], render: [] };
      for (const k of at.takes) { const c = (await AK.lib.pcm(k.audioRef.libId))[0]; out.takes.push({ len: c.length, on: RT.onset(c), first: Math.abs(c[0]) }); }
      out.want = [0, 1, 2].map(k => Math.round((96 + 48 * k) * spt * sr));
      out.loopLen = Math.round(BAR * spt * sr);
      for (const k of [at.takes[0], at.takes[2]]) { E.pickTake(at.id, k.id); const o = await E.renderOffline({ fromBar: 0, toBar: 1, trackIds: [at.id], tailSec: 0, limiter: false }); out.render.push(RT.onset(o.channels[0], 0.005)); }
      return out;
    });
    t.eq([r.lat.kind, r.lat.ms], ['fm1', 23], 'audio takes used the FM-1 number');
    t.ok(r.lat.extra > 4 && r.lat.extra < 8, '+ the master look-ahead ' + r.lat.extra + ' ms');
    t.eq(r.made, [[0, r.loopLen], [1, r.loopLen], [2, r.loopLen]], 'three passes, each exactly the loop length');
    for (let k = 0; k < 3; k++) {
      t.near(r.f0d[k], k * r.loopLen, 1, 'slice ' + k + ' starts one loop after the last');
      t.eq(r.takes[k].len, r.loopLen, 'take ' + k + ' length');
      t.near(r.takes[k].on, r.want[k], 88, 'take ' + (k + 1) + ' onset vs its note (samples, ±2 ms)');
    }
    t.near(r.render[0], r.want[0], 88, 'take 1 renders its own onset');
    t.near(r.render[1], r.want[2], 88, 'take 3 renders its own onset');
  });

  await t.test('loopback calibrate (17 ms line) → play-along punch take: trimmed to the bar, 5 ms fades, clicks aligned ±2 ms; outside audio kept', async () => {
    const r = await p.evaluate(async () => {
      await RT.fresh();
      // the "input" hears the click bus 17 ms late — a cable from the output into a line input
      const c = E.ctx, d = c.createDelay(1), g = c.createGain(); d.delayTime.value = 0.017; E.clickDelay.connect(d); d.connect(g);
      E.inputSrc = g; E.inputLabel = 'USB Audio Line In';
      const cal = await E.calibrateLoopback({ gap: 0.2 });
      // an older clip under bars 1–3 (silence) on the track that records
      const spt = RT.spt(), sil = await AK.lib.put({ kind: 'daw-rec', name: 'old', sampleRate: 44100, meta: {} }, [new Float32Array(Math.round(3 * BAR * spt * 44100))]);
      const at = E.addTrack('audio', { name: 'vox' }); at.arm = true; sel.trackId = at.id;
      at.audio.push({ t: 0, libId: sil.id, name: 'old', offset: 0, len: 3 * BAR * spt, gain: 1 });
      P.metro = true; P.punch = { on: true, a: 1, b: 2 };                // the performer = the click, played along
      await E.startRecord();
      const a0 = E._anchors[0];
      await RT.untilCtx(a0.ctx + 2.15 * BAR * spt); await E.stopRecord(); E.stop(); P.metro = false;
      E.clickDelay.disconnect(d);
      const k = at.takes[0], ch = (await AK.lib.pcm(k.audioRef.libId))[0];
      return { cal, la: E.outDelay * 1000, barN: Math.round(BAR * spt * 44100), beatN: Math.round(PPQ * spt * 44100), use: E.lastRec.lat, len: ch.length, t: k.audioRef.t, edge: [Math.abs(ch[0]), Math.abs(ch[ch.length - 1])], fade: Math.max(...[...ch.slice(0, 40)].map(Math.abs)),
               on: RT.onsets(ch, 0.02, 2000), clips: at.audio.map(x => [x.t / BAR, +(x.len).toFixed(3), +(x.offset || 0).toFixed(3), x.libId === sil.id]) };
    });
    t.near(r.cal.ms, 17 + r.la, 2, 'loopback median = 17 ms line + the ' + r.la.toFixed(2) + ' ms master look-ahead the click shares'); t.ok(r.cal.found >= 7, 'clicks found ' + r.cal.found);
    t.eq([r.use.kind, r.use.total], ['input', r.cal.ms], 'the take used the play-along number as measured');
    t.eq([r.len, r.t], [r.barN, 384], 'take = exactly bar 2');
    t.ok(r.edge[0] === 0 && r.edge[1] === 0 && r.fade < 0.05, 'faded edges ' + r.edge + ' / ' + r.fade);
    const beats = r.on.filter(i => i > 400);           // the bar-2 downbeat click sits under the fade-in
    t.eq(beats.length, 3, 'three beat clicks inside the bar: ' + r.on);
    beats.forEach((s, i) => t.near(s, r.beatN * (i + 1), 88, 'click ' + (i + 2)));
    const bs = r.barN / 44100;
    t.eq(r.clips, [[0, +bs.toFixed(3), 0, true], [2, +bs.toFixed(3), +(2 * bs).toFixed(3), true], [1, +bs.toFixed(3), 0, false]], 'old clip cut around the punch (replace), take in between');
  });

  await t.test('save → reload: takes, punch and settings come back; the takes rows draw', async () => {
    await p.evaluate(async () => {
      await RT.fresh({ countIn: 1, mode: 'overdub', quant: 16 }); const tr = await RT.midiTrack('kept'); P.loop = { on: true, a: 0, b: 1 };
      await E.startRecord(); const a0 = E._anchors[0], spt = RT.spt();
      for (let k = 0; k < 2; k++) RT.key(a0.ctx + (1 + k) * BAR * spt + 192 * spt, 64 + k);
      await RT.untilCtx(a0.ctx + 3 * BAR * spt + 0.1); await E.stopRecord(); E.stop();
      P.punch = { on: false, a: 3, b: 5 }; await E.save();
    });
    await p.reload(); await p.waitForTimeout(400);
    await p.evaluate(() => document.getElementById('gatebtn').click());
    await p.waitForFunction(() => typeof P !== 'undefined' && P && P.tracks.length, null, { timeout: 10000 });
    await p.waitForTimeout(300); await helpers();
    const r = await p.evaluate(() => { const tr = P.tracks[0]; return { takes: tr.takes.map(k => [k.name, k.active]), punch: P.punch, rec: P.rec, q: E.quantize, ui: [document.getElementById('countin').value, document.getElementById('recmode').value, document.getElementById('quant').value], rows: document.querySelectorAll('.tkh').length }; });
    t.eq(r.takes, [['take 1', false], ['take 2', true]], 'takes');
    t.eq(r.punch, { on: false, a: 3, b: 5 }); t.eq(r.rec, { countIn: 1, mode: 'overdub', quant: 16 }); t.eq(r.q, 16);
    t.eq(r.ui, ['1', 'overdub', '16'], 'transport controls');
    t.eq(r.rows, 1, 'one takes row');
  });

  await t.test('old project (no rec / punch / takes fields) loads and stays byte-identical', async () => {
    const r = await p.evaluate(async () => {
      const j = DAW.Engine.newProject(); j.bpm = 110;
      j.devices.push({ id: 'dev_old', type: 'basic', name: 'b', state: null, mix: { vol: 0.8, pan: 0, mute: false, solo: false, sendA: 0.1, sendB: 0 } });
      j.tracks.push({ id: 'trk_old', name: 'old', color: '#d8a060', kind: 'midi', deviceId: 'dev_old', channel: 1, mute: false, solo: false, arm: false, vel: 1, patterns: { p1: { name: 'p', lenBars: 2, notes: [{ t: 0, d: 48, n: 60, v: 0.8 }, { t: 400, d: 48, n: 64, v: 0.7 }] } }, clips: [{ bar: 0, pid: 'p1' }, { bar: 4, pid: 'p1', bars: 4 }], audio: [], role: '' });
      const before = JSON.stringify(j.tracks) + JSON.stringify(j.loop) + Object.keys(j).join();
      await E.load(JSON.parse(JSON.stringify(j))); P = E.project; E.emit('project'); await RT.sleep(200);
      drawArr(); renderHeads();
      const after = JSON.stringify(P.tracks) + JSON.stringify(P.loop) + Object.keys(P).filter(k => k in j).join();
      const o = await E.renderOffline({ fromBar: 0, toBar: 2, tailSec: 0 });
      return { same: before === after, extra: Object.keys(P).filter(k => !(k in j)), q: E.quantize, pk: AK.util.peakOf(o.channels) };
    });
    t.ok(r.same, 'project JSON unchanged'); t.eq(r.extra, [], 'no new keys'); t.eq(r.q, 24, 'quantize default'); t.ok(r.pk > 0.01, 'renders');
  });

  await t.test('fingers: PUNCH button, punch edges / middle dragged on the ruler, takes row tap + header buttons (≥ 36 px)', async () => {
    await p.evaluate(async () => {
      await RT.fresh(); const tr = await RT.midiTrack();          // two takes of bar 1, as a loop recording leaves them
      tr.takes = [1, 2].map(k => { const pid = 'pt' + k; tr.patterns[pid] = { name: 'take ' + k, lenBars: 1, notes: [{ t: 96, d: 24, n: 59 + k, v: 0.8 }] };
        return { id: 'tk' + k, region: { a: 0, b: 1 }, kind: 'midi', pid, name: 'take ' + k, at: new Date().toISOString(), pass: k - 1, rec: 'r', active: false }; });
      E._activate(tr, tr.takes[1]);
      E.emit('project'); document.getElementById('lanes').scrollLeft = 0;
    });
    const box = sel => p.evaluate(s => { const r = document.querySelector(s).getBoundingClientRect(); return { x: r.left + r.width / 2, y: r.top + r.height / 2, w: r.width, h: r.height }; }, sel);
    const pb = await box('#punchbtn');
    t.ok(pb.h >= 36, 'PUNCH button ' + pb.h + ' px');
    await f.tap(pb.x, pb.y);
    let u = await p.evaluate(() => P.punch);
    t.ok(u && u.on, 'PUNCH on by touch');
    const g = await p.evaluate(() => { const r = document.getElementById('arrcv').getBoundingClientRect(); return { x: r.left, y: r.top, bar: view.barPx, ruler: view.rulerH }; });
    const ry = g.y + g.ruler / 2;
    await p.evaluate(() => { P.punch = { on: true, a: 2, b: 4 }; drawArr(); });
    await f.drag(g.x + 4 * g.bar + 6, ry, 2 * g.bar, 0);             // right edge → bar 6
    u = await p.evaluate(() => P.punch); t.eq([u.a, u.b], [2, 6], 'right edge dragged');
    await f.drag(g.x + 2 * g.bar - 5, ry, -g.bar, 0);                // left edge → bar 1
    u = await p.evaluate(() => P.punch); t.eq([u.a, u.b], [1, 6], 'left edge dragged');
    await f.drag(g.x + 3.5 * g.bar, ry, 2 * g.bar, 0);              // middle → moved 2 bars
    u = await p.evaluate(() => P.punch); t.eq([u.a, u.b], [3, 8], 'moved');
    // takes row: tap cycles; header ▶ / ✕ / KEEP are finger-sized
    const lay = await p.evaluate(() => { const L = arrLayout(), k = L.rows[0].takes[0]; return { y: k.y, a: k.g.region.a, active: k.g.active.name }; });
    await f.tap(g.x + (lay.a + 0.5) * g.bar, g.y + lay.y + 20);
    const after = await p.evaluate(() => E.takeGroups(P.tracks[0])[0].active.name);
    t.ok(after !== lay.active, 'tap cycled ' + lay.active + ' → ' + after);
    const rb = await box('#latbtn'); t.ok(rb.h >= 36, 'REC button ' + rb.h + ' px');
    await f.tap(rb.x, rb.y);                                            // the recording panel opens
    t.ok(await p.evaluate(() => document.getElementById('latpanel').classList.contains('show')), 'panel open');
    const sizes = await p.evaluate(() => [...document.querySelectorAll('.tkh button, .tkh select, #latpanel select, #latpanel input, #latpanel button')].map(e => Math.round(e.getBoundingClientRect().height)));
    t.ok(sizes.length >= 14 && sizes.every(h => h >= 36), 'sizes ' + sizes);
    const tbar = await p.evaluate(() => Math.round(document.querySelector('.transport').getBoundingClientRect().height));
    t.ok(tbar <= 52, 'transport bar stays one line (' + tbar + ' px)');
    const cb = await box('#lat-close'); await f.tap(cb.x, cb.y);
    const nb = await box('.tkh button[data-x="next"]'); await f.tap(nb.x, nb.y);
    t.eq(await p.evaluate(() => E.takeGroups(P.tracks[0])[0].active.name), lay.active, '▶ cycled back');
    const kb = await box('.tkh button[data-x="keep"]'); await f.tap(kb.x, kb.y);
    t.eq(await p.evaluate(() => (P.tracks[0].takes || []).length), 1, 'KEEP left one take');
  });

  await t.test('no page / console errors', async () => t.noErrors(errors));
});
