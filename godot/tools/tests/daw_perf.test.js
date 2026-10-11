// DAW performance tools: scale lock, chords, arpeggiator, groove, step sequencer + probability (daw_perf.js)
const { suite } = require('./harness');
const path = require('path'), { execFileSync } = require('child_process');

// the engine as it was before daw_perf.js (the parent of the commit that added it; HEAD before that commit)
function oldEngineSource() {
  const repo = path.resolve(__dirname, '../../..'), git = a => execFileSync('git', ['-C', repo, ...a], { encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] });
  try {
    const added = git(['log', '--diff-filter=A', '--format=%H', '--', 'godot/tools/daw_perf.js']).trim().split('\n').filter(Boolean).pop();
    return git(['show', (added ? added + '^' : 'HEAD') + ':godot/tools/daw_engine.js']);
  } catch (e) { return null; }
}

suite('daw perf · scale lock, chords, arp, groove, step sequencer', async t => {
  const { p, errors, cdp } = await t.page('daw.html', { start: true, touch: true });
  const f = t.touch(cdp);
  const sl = ms => new Promise(r => setTimeout(r, ms));
  await p.evaluate(() => {
    window.confirm = () => true;
    const sleep = ms => new Promise(r => setTimeout(r, ms));
    // a project of BASIC synths (fast, renders offline): tracks [{ name, role, notes, lenBars, bars, perf }]
    async function basic({ bpm = 240, key = 9, mode = 'minor', tracks = [] } = {}) {
      const P0 = DAW.Engine.newProject(); Object.assign(P0, { bpm, key, mode, loop: { on: false, a: 0, b: 4 } });
      await E.load(P0); P = E.project; sel = { trackId: null, clip: -1 };
      for (const s of tracks) {
        const d = await E.addDevice('basic', { name: s.name });
        const tr = E.addTrack('midi', { name: s.name, deviceId: d.id, role: s.role || '' });
        if (s.notes) { tr.patterns.a = { name: 'a', lenBars: s.lenBars || 1, notes: s.notes }; tr.clips = [{ bar: 0, pid: 'a', bars: s.bars }]; }
        if (s.perf) tr.perf = s.perf;
      }
      E.emit('project');
      return P.tracks;
    }
    // every noteOn / noteOff a live device gets
    const LOG = [];
    function spy(tr) {
      const inst = E.devices.get(tr.deviceId);
      if (!inst.__spied) {
        const on = inst.noteOn.bind(inst), off = inst.noteOff.bind(inst);
        inst.noteOn = (n, v, w, ch) => { LOG.push({ tr: tr.name, on: 1, n, v, w }); return on(n, v, w, ch); };
        inst.noteOff = (n, w, ch, now) => { if (w !== undefined) LOG.push({ tr: tr.name, on: 0, n, w }); return off(n, w, ch, now); };   // (BasicSynth's own retrigger cut has no time)
        inst.__spied = true;
      }
      return LOG;
    }
    // the same for the instruments renderOffline builds
    const OFF = [], origOff = E._offlineDevice.bind(E);
    E._offlineDevice = async (off, d, out) => {
      const inst = await origOff(off, d, out); if (!inst) return inst;
      const on = inst.noteOn.bind(inst), name = (P.tracks.find(x => x.deviceId === d.id) || {}).name;
      inst.noteOn = (n, v, w, ch) => { OFF.push({ tr: name, on: 1, n, v, w }); return on(n, v, w, ch); };
      return inst;
    };
    const ons = (log, name) => log.filter(e => e.on && (!name || e.tr === name));
    const press = (tr, ns, on = true) => ns.forEach(n => E.liveNote(tr.id, n, 0.8, on));
    window.PT = { sleep, basic, spy, LOG, OFF, ons, press };
  });

  // ── 1. old projects play exactly as before ─────────────────────────
  // Offline renders are not sample-reproducible run to run in Chromium, not even with the old engine: ~1 float ULP
  // on a bare oscillator (6e-8), ~1e-5 with FORGE (its voices are also reaped by wall-clock timers). So the exact
  // check is on what the engine feeds the devices — every noteOn / noteOff: note, velocity, time, channel — and the
  // audio is held to the render's own noise floor.
  const oldSrc = oldEngineSource();
  if (!oldSrc) t.skip('swing-only project = old engine', 'no git history here');
  else await t.test('swing-only projects play exactly as before PERF: identical device events (FORGE + BASIC), audio at the noise floor, groove off = no groove', async () => {
    const r = await p.evaluate(async src => {
      document.getElementById('g-inst').value = 'forge'; document.getElementById('g-style').value = 'boom_bap'; document.getElementById('g-form').value = 'loop';
      await generate({ force: true, seed: 11 }); await E.whenReady();
      P.swing = 0.55; P.loop.on = false;
      const oldEngine = s => { const ours = window.DAW; (0, eval)(s); const O = window.DAW; window.DAW = ours; const OE = new O.Engine(); Object.assign(OE, { ctx: E.ctx, verb: E.verb, devices: E.devices, project: E.project, start: async () => {} }); return OE; };
      const real = Math.random, rst = window.setTimeout;
      const render = async eng => {          // seeded noise; FORGE's voice-reaping timers wait until the render is done
        let a = 12345; Math.random = () => { a = (a + 0x6D2B79F5) | 0; let x = Math.imul(a ^ (a >>> 15), 1 | a); x = (x + Math.imul(x ^ (x >>> 7), 61 | x)) ^ x; return ((x ^ (x >>> 14)) >>> 0) / 4294967296; };
        const q = []; window.setTimeout = f => { q.push(f); return 0; };
        try { return await eng.renderOffline({ fromBar: 0, toBar: 1, tailSec: 0.3 }); }
        finally { Math.random = real; window.setTimeout = rst; q.forEach(f => { try { f(); } catch (e) {} }); }
      };
      const events = async eng => {          // every call renderOffline makes on its devices
        const L = [], own = Object.prototype.hasOwnProperty.call(eng, '_offlineDevice'), prev = eng._offlineDevice, base = prev.bind(eng);
        eng._offlineDevice = async (o, d, out) => { const i = await base(o, d, out); const on = i.noteOn.bind(i), off = i.noteOff.bind(i); i.noteOn = (n, v, w, c) => { L.push([d.id, 1, n, v, w, c]); return on(n, v, w, c); }; i.noteOff = (n, w, c) => { L.push([d.id, 0, n, w, c]); return off(n, w, c); }; return i; };
        try { const res = await render(eng); return { res, L: JSON.stringify(L), n: L.length }; } finally { if (own) eng._offlineDevice = prev; else delete eng._offlineDevice; }
      };
      const diff = (a, b) => { let m = 0; for (let c = 0; c < 2; c++) { if (a.channels[c].length !== b.channels[c].length) return Infinity; for (let i = 0; i < a.channels[c].length; i++) m = Math.max(m, Math.abs(a.channels[c][i] - b.channels[c][i])); } return m; };
      const OE = oldEngine(src), out = {};
      await render(E);                                        // warm-up: FORGE builds shared tables on its first offline render
      const o = await events(OE), n = await events(E);
      out.forge = { same: o.L === n.L, events: o.n, audio: diff(o.res, n.res), peak: AK.util.peakOf(o.res.channels) };
      // the same arrangement on BASIC synths: sample-exact (the old engine gets the same BasicSynth note-off fix)
      const j = JSON.parse(JSON.stringify(P)); j.devices.forEach(d => { d.type = 'basic'; d.state = null; delete d.preset; });
      await E.load(j); P = E.project; sel = { trackId: null, clip: -1 };
      const OB = oldEngine(src.replace('this.noteOff(n, undefined, true);', 'this.noteOff(n, undefined, undefined, true);').replace('noteOff(n, when = this.ctx.currentTime, immediate) {', 'noteOff(n, when = this.ctx.currentTime, ch, immediate) {'));
      const b0 = await events(OB), b1 = await events(E), b1b = await render(E);
      P.groove = { on: false, type: 'triplet', swing: 0.7, human: { ms: 10, vel: 0.2 } }; const b2 = await events(E);   // a groove that is off changes nothing
      P.groove = { on: true, type: 'mpc16', swing: 0.7, human: { ms: 5 } }; out.grooveOn = (await events(E)).L === b0.L;   // …one that is on does
      delete P.groove;
      out.basic = { same: b0.L === b1.L, off: b0.L === b2.L, events: b0.n, audio: diff(b0.res, b1.res), offAudio: diff(b0.res, b2.res), floor: diff(b1.res, b1b), peak: AK.util.peakOf(b0.res.channels) };
      return out;
    }, oldSrc);
    t.ok(r.forge.events > 50 && r.forge.peak > 0.05, 'FORGE render: ' + r.forge.events + ' device events, peak ' + r.forge.peak.toFixed(2));
    t.ok(r.forge.same, 'FORGE: device events differ from the old engine');
    t.ok(r.forge.audio < 1e-4, 'FORGE audio vs old ' + r.forge.audio.toExponential(1) + ' (≈ its own run-to-run noise, 1e-5)');
    t.ok(r.basic.peak > 0.05 && r.basic.events > 50, 'BASIC render audible ' + r.basic.peak);
    t.ok(r.basic.same, 'BASIC: device events differ from the old engine');
    t.ok(r.basic.off, 'a groove that is off changed the events'); t.ok(!r.grooveOn, 'a groove that is on left the events alone');
    t.ok(r.basic.audio < 1e-6 && r.basic.offAudio < 1e-6, 'BASIC audio vs old ' + r.basic.audio.toExponential(1) + ' / groove off ' + r.basic.offAudio.toExponential(1) + ' (run-to-run floor ' + r.basic.floor.toExponential(1) + ')');
  });

  // ── 2. STEP view on the generated project: touch edits = pattern notes, undo / redo ─────────
  await t.test('STEP view: tap toggles a step, drag sets velocity, long-press sets probability; undo / redo', async () => {
    await p.evaluate(async () => {
      if (!P.tracks.length) { document.getElementById('g-inst').value = 'forge'; document.getElementById('g-form').value = 'loop'; await generate({ force: true, seed: 11 }); }
      const dr = P.tracks.find(x => x.role === 'drums');
      dr.patterns.st = { name: 'steps', lenBars: 1, notes: [] }; dr.clips = [{ bar: 0, pid: 'st' }];
      sel = { trackId: dr.id, clip: 0 }; STEP.on = true; openPerf(null); renderHeads(); drawArr(); drawRoll(); saveSoon();
      await PT.sleep(400);
    });
    // a cell's centre on screen, scrolled into view
    const cell = (i, n) => p.evaluate(({ i, n }) => {
      const ri = STEP.rows.findIndex(r => r.n === n), wrap = document.getElementById('rollwrap');
      wrap.scrollTop = Math.max(0, STEP.TOP + ri * STEP.H - 40); wrap.scrollLeft = 0;
      const r = document.getElementById('stepcv').getBoundingClientRect();
      return { x: r.left + STEP.LBL + (i + 0.5) * STEP.W, y: r.top + STEP.TOP + (ri + 0.5) * STEP.H };
    }, { i, n });
    const notes = () => p.evaluate(() => curClip().p.notes.map(n => ({ t: n.t, d: n.d, n: n.n, v: n.v, p: n.p })));
    let c = await cell(4, 38); await f.tap(c.x, c.y);
    c = await cell(0, 36); await f.tap(c.x, c.y);
    c = await cell(12, 38); await f.tap(c.x, c.y);
    t.eq(await notes(), [{ t: 0, d: 24, n: 36, v: 0.8 }, { t: 96, d: 24, n: 38, v: 0.8 }, { t: 288, d: 24, n: 38, v: 0.8 }], 'three taps → three steps');
    c = await cell(12, 38); await f.tap(c.x, c.y);
    t.eq((await notes()).length, 2, 'tapping a step again removes it');
    c = await cell(4, 38); await f.drag(c.x, c.y, 0, -12, 6);
    const v = (await notes()).find(n => n.t === 96).v;
    t.ok(v > 0.82 && v <= 1, 'dragged up → louder: ' + v);
    c = await cell(0, 36); await f.hold(c.x, c.y);
    const ed = await p.evaluate(() => { const b = [...document.querySelectorAll('#stepedit button')].find(x => x.textContent === '50%'), r = b.getBoundingClientRect(); return { show: document.getElementById('stepedit').classList.contains('show'), x: r.left + r.width / 2, y: r.top + r.height / 2, h: r.height, w: r.width }; });
    t.ok(ed.show, 'long-press opens the step editor'); t.ok(ed.h >= 36 && ed.w >= 36, 'editor buttons ≥ 36 px');
    await f.tap(ed.x, ed.y);
    const lenB = await p.evaluate(() => { const b = [...document.querySelectorAll('#stepedit [data-se=len]')].find(x => x.dataset.v === '1').getBoundingClientRect(); return { x: b.left + b.width / 2, y: b.top + b.height / 2 }; });
    await f.tap(lenB.x, lenB.y);
    t.eq((await notes()).find(n => n.t === 0), { t: 0, d: 48, n: 36, v: 0.8, p: 0.5 }, 'PROB 50 % + LEN 2 written onto the note');
    // resolution: 12 / bar → steps are 32 ticks
    await p.evaluate(async () => { closeStepEdit(); document.getElementById('s-res').click(); document.getElementById('s-res').click(); document.getElementById('s-res').click(); await PT.sleep(50); });
    t.eq(await p.evaluate(() => curClip().p.steps), 8, 'cycled 16 → 24 → 32 → 8');
    await p.evaluate(() => { document.getElementById('s-res').click(); });
    c = await cell(3, 42); await f.tap(c.x, c.y);
    t.ok((await notes()).some(n => n.n === 42 && n.t === 96 && n.d === 32), '12 / bar: step 4 = tick 96, 32 long');
    // undo / redo walk the same pattern notes
    const r = await p.evaluate(async () => {
      await PT.sleep(400);
      const snap = () => JSON.stringify(curClip().p.notes), a = snap();
      await undo(); const b = snap(); await undo(); const c2 = snap(); await redo(); await redo(); const d = snap();
      return { a, b, c2, d };
    });
    t.ok(r.b !== r.a && r.c2 !== r.b, 'undo steps back'); t.eq(r.d, r.a, 'redo returns');
  });

  await t.test('STEP view: melodic rows are the scale degrees of the project key', async () => {
    const r = await p.evaluate(async () => {
      P.key = 2; P.mode = 'dorian';
      const tr = P.tracks.find(x => x.role === 'lead'); tr.patterns.st = { name: 's', lenBars: 1, notes: [] }; tr.clips = [{ bar: 0, pid: 'st' }];
      sel = { trackId: tr.id, clip: 0 }; STEP.oct[tr.id] = 4; drawRoll();
      return STEP.rows.map(r => r.n).reverse().slice(0, 8);
    });
    t.eq(r, [62, 64, 65, 67, 69, 71, 72, 74], 'D dorian from D4');
    const c = await p.evaluate(() => { const wrap = document.getElementById('rollwrap'); wrap.scrollTop = 0; const ri = STEP.rows.findIndex(x => x.n === 69), rc = document.getElementById('stepcv').getBoundingClientRect(); wrap.scrollTop = Math.max(0, STEP.TOP + ri * STEP.H - 40); const rc2 = document.getElementById('stepcv').getBoundingClientRect(); return { x: rc2.left + STEP.LBL + 2.5 * STEP.W, y: rc2.top + STEP.TOP + (ri + 0.5) * STEP.H }; });
    await f.tap(c.x, c.y);
    t.eq(await p.evaluate(() => curClip().p.notes.map(n => [n.t, n.n])), [[48, 69]], 'tap on degree 5 at step 3');
  });

  // ── 3. PERF panel by touch ─────────────────────────────────────────
  await t.test('PERF panel: opened from the track header by touch, buttons ≥ 36 px, edits undo', async () => {
    await p.evaluate(async () => { STEP.on = false; drawRoll(); await PT.sleep(350); });
    const tr = await p.evaluate(() => { const i = P.tracks.findIndex(x => x.role === 'chords'); const b = document.querySelectorAll('#thlist .th')[i].querySelector('[data-a=perf]').getBoundingClientRect(); return { x: b.left + b.width / 2, y: b.top + b.height / 2, w: b.width, h: b.height, id: P.tracks[i].id }; });
    await f.tap(tr.x, tr.y);
    const btn = sel => p.evaluate(s => { const b = document.querySelector('#perfpanel ' + s); b.scrollIntoView({ block: 'center' }); const r = b.getBoundingClientRect(); return { x: r.left + r.width / 2, y: r.top + r.height / 2, w: r.width, h: r.height }; }, sel);
    const open = await p.evaluate(() => ({ show: document.getElementById('perfpanel').classList.contains('show'), id: PERF.trackId, small: [...document.querySelectorAll('#perfpanel button')].filter(b => { const r = b.getBoundingClientRect(); return r.height < 36 || r.width < 36; }).length }));
    t.ok(open.show && open.id === tr.id, 'panel open for the tapped track'); t.eq(open.small, 0, 'buttons under 36 px');
    t.ok(tr.h >= 36 && tr.w >= 36, 'header P button ' + tr.w + '×' + tr.h);
    let b = await btn('[data-p="arp.on"]'); await f.tap(b.x, b.y);
    b = await btn('[data-p="arp.rate"][data-v="1/8T"]'); await f.tap(b.x, b.y);
    b = await btn('[data-p="arp.oct"][data-v="3"]'); await f.tap(b.x, b.y);
    b = await btn('[data-p="chord.type"][data-v="seventh"]'); await f.tap(b.x, b.y);
    b = await btn('[data-g="type"][data-v="shuffle8"]'); await f.tap(b.x, b.y);
    const st = await p.evaluate(() => ({ perf: E.track(PERF.trackId).perf, groove: P.groove && { on: P.groove.on, type: P.groove.type }, hdr: document.querySelector('#thlist .th.sel [data-a=perf]').classList.contains('on') }));
    t.eq(st.perf.arp, { on: true, rate: '1/8T', oct: 3 }, 'arp settings'); t.eq(st.perf.chord, { type: 'seventh' }, 'chord type');
    t.eq(st.groove, { on: true, type: 'shuffle8' }, 'project groove'); t.ok(st.hdr, 'header P lights up');
    const r = await p.evaluate(async () => { await PT.sleep(400); const id = PERF.trackId; await undo(); const pf = E.track(id).perf, a = !!(pf && pf.arp && pf.arp.on); await redo(); return { a, b: E.track(id).perf.arp.on, panel: document.getElementById('perfpanel').classList.contains('show') }; });
    t.ok(!r.a, 'undo turned the arp back off'); t.ok(r.b, 'redo'); t.ok(r.panel, 'panel follows undo');
    await p.evaluate(() => { openPerf(null); delete P.groove; });
  });

  // ── 4. scale lock + chords through the live chain ──────────────────
  await t.test('scale lock: every mode (A minor), through the live chain to the device', async () => {
    const r = await p.evaluate(async () => {
      const [tr] = await PT.basic({ tracks: [{ name: 'k' }] }); PT.spy(tr);
      const out = {};
      for (const mode of ['nearest', 'up', 'down', 'filter']) {
        tr.perf = { scale: { on: true, mode } }; E.perfReset(tr.id); PT.LOG.length = 0;
        const got = [];
        for (let n = 60; n < 72; n++) { const k = PT.LOG.length; PT.press(tr, [n]); PT.press(tr, [n], false); got.push(PT.LOG.length > k ? PT.LOG[k].n : null); }
        out[mode] = got;
      }
      tr.perf = { scale: { on: true, mode: 'nearest' } }; PT.LOG.length = 0; PT.press(tr, [61, 63]); PT.press(tr, [61, 63], false);
      out.shared = PT.LOG.map(e => (e.on ? '+' : '-') + e.n).join(' ');      // C# and D# both → … C and D: no stuck notes
      return out;
    });
    t.eq(r.nearest, [60, 60, 62, 62, 64, 65, 65, 67, 67, 69, 69, 71], 'nearest (ties down)');
    t.eq(r.up, [60, 62, 62, 64, 64, 65, 67, 67, 69, 69, 71, 71], 'up');
    t.eq(r.down, [60, 60, 62, 62, 64, 65, 65, 67, 67, 69, 69, 71], 'down');
    t.eq(r.filter, [60, null, 62, null, 64, 65, null, 67, null, 69, null, 71], 'filter');
    t.eq(r.shared, '+60 +62 -60 -62');
  });

  await t.test('chords: diatonic triads / 7ths per degree, voicings, power, custom, follows key + mode', async () => {
    const r = await p.evaluate(async () => {
      const tr = P.tracks[0], chord = c => { tr.perf = { chord: Object.assign({ on: true }, c) }; E.perfReset(tr.id); };
      const play = n => { PT.LOG.length = 0; PT.press(tr, [n]); const o = PT.ons(PT.LOG).map(e => e.n); PT.press(tr, [n], false); return o; };
      const roots = [69, 71, 72, 74, 76, 77, 79], out = {};
      chord({ type: 'triad' }); out.triads = roots.map(play); out.chromatic = play(70);
      chord({ type: 'seventh' }); out.sevenths = roots.map(play);
      chord({ type: 'sus2' }); out.sus2 = play(69); chord({ type: 'sus4' }); out.sus4 = play(69);
      chord({ type: 'triad', inv: 1 }); out.inv1 = play(69); chord({ type: 'triad', inv: 2 }); out.inv2 = play(69);
      chord({ type: 'triad', spread: 'open' }); out.open = play(69); chord({ type: 'seventh', spread: 'wide' }); out.wide = play(69);
      chord({ type: 'power' }); out.power = play(69); chord({ type: 'custom', shape: [0, 3, 7, 10] }); out.custom = play(64);
      P.key = 0; P.mode = 'major'; chord({ type: 'triad' }); out.cmaj = [60, 62, 64, 65, 67, 69, 71].map(play);
      tr.perf = { scale: { on: true, mode: 'nearest' }, chord: { on: true, type: 'triad' } }; E.perfReset(tr.id); out.chain = play(61);    // scale lock first, then the chord
      P.key = 9; P.mode = 'minor';
      return out;
    });
    t.eq(r.triads, [[69, 72, 76], [71, 74, 77], [72, 76, 79], [74, 77, 81], [76, 79, 83], [77, 81, 84], [79, 83, 86]], 'A minor triads i … VII');
    t.eq(r.sevenths, [[69, 72, 76, 79], [71, 74, 77, 81], [72, 76, 79, 83], [74, 77, 81, 84], [76, 79, 83, 86], [77, 81, 84, 88], [79, 83, 86, 89]], 'A minor 7ths');
    t.eq(r.chromatic, [70, 73, 77], 'A# = A minor chord shifted up');
    t.eq([r.sus2, r.sus4], [[69, 71, 76], [69, 74, 76]], 'sus2 / sus4');
    t.eq([r.inv1, r.inv2], [[72, 76, 81], [76, 81, 84]], 'inversions');
    t.eq([r.open, r.wide], [[60, 69, 76], [69, 76, 84, 91]], 'open (drop 2) / wide');
    t.eq([r.power, r.custom], [[69, 76, 81], [64, 67, 71, 74]], 'power / custom');
    t.eq(r.cmaj, [[60, 64, 67], [62, 65, 69], [64, 67, 71], [65, 69, 72], [67, 71, 74], [69, 72, 76], [71, 74, 77]], 'C major follows the project key + mode');
    t.eq(r.chain, [60, 64, 67], 'C# → scale lock C → C major triad');
  });

  // ── 5. arpeggiator against the transport grid ──────────────────────
  const grid = (r, rate) => {     // every note-on on the grid ±1 ms; returns { ticks, notes, offs }
    const ons = r.log.filter(e => e.on), offs = r.log.filter(e => !e.on), ticks = ons.map(e => r.anchor.tick + (e.w - r.anchor.ctx) / r.spt);
    for (const tk of ticks) { const err = Math.abs(tk - Math.round(tk / rate) * rate) * r.spt; if (err > 0.001) throw new Error('off the grid by ' + (err * 1000).toFixed(2) + ' ms at tick ' + tk.toFixed(2)); }
    return { ticks: ticks.map(x => Math.round(x)), notes: ons.map(e => e.n), ons, offs };
  };
  const arpRun = (perf, keys, ms, opts = {}) => p.evaluate(async ({ perf, keys, ms, opts }) => {
    const tr = P.tracks[0]; tr.perf = perf; E.perfReset(tr.id);
    if (opts.play && !E.playing) { P.loop = { on: true, a: 0, b: 64 }; await E.play(0); await PT.sleep(200); }
    if (!opts.play && E.playing) E.stop();
    await PT.sleep(60); PT.LOG.length = 0;
    const t0 = E.ctx.currentTime;
    for (const n of keys) E.liveNote(tr.id, n, 0.8, true);
    await PT.sleep(ms);
    const anchor = E.playing ? Object.assign({}, E.anchor) : null, log = PT.LOG.slice();
    if (!opts.hold) for (const n of keys) E.liveNote(tr.id, n, 0, false);
    return { log, anchor, spt: E.spt(), t0 };
  }, { perf, keys, ms, opts });

  await t.test('arp up · 1/16 · 2 octaves · gate 50 %: on the transport grid, in order', async () => {
    await p.evaluate(async () => { await PT.basic({ bpm: 240, tracks: [{ name: 'k' }] }); PT.spy(P.tracks[0]); });
    const r = await arpRun({ arp: { on: true, mode: 'up', rate: '1/16', oct: 2, gate: 0.5 } }, [64, 60, 67], 800, { play: true });
    const g = grid(r, 24);
    t.ok(g.notes.length >= 10, 'steps ' + g.notes.length);
    t.eq(g.notes.slice(0, 8), [60, 64, 67, 72, 76, 79, 60, 64], 'order');
    g.ticks.slice(1).forEach((tk, i) => { if (tk - g.ticks[i] !== 24) throw new Error('step ' + (tk - g.ticks[i]) + ' ticks'); });
    g.ons.forEach((e, i) => t.near(g.offs[i].w - e.w, 0.5 * 24 * r.spt - 0.002, 0.001, 'gate'));
  });
  await t.test('arp down · 1/8T · 1 octave, played order, chord mode', async () => {
    let r = await arpRun({ arp: { on: true, mode: 'down', rate: '1/8T', oct: 1, gate: 0.25 } }, [60, 64, 67], 650, { play: true });
    let g = grid(r, 32);
    t.eq(g.notes.slice(0, 6), [67, 64, 60, 67, 64, 60], 'down');
    g.ticks.slice(1).forEach((tk, i) => { if (tk - g.ticks[i] !== 32) throw new Error('1/8T step ' + (tk - g.ticks[i])); });
    t.near(g.offs[0].w - g.ons[0].w, 0.25 * 32 * r.spt - 0.002, 0.001, 'gate 25 %');
    r = await arpRun({ arp: { on: true, mode: 'played', rate: '1/16' } }, [67, 60, 64], 450, { play: true });
    t.eq(grid(r, 24).notes.slice(0, 6), [67, 60, 64, 67, 60, 64], 'as played');
    r = await arpRun({ arp: { on: true, mode: 'chord', rate: '1/8' } }, [60, 64, 67], 450, { play: true });
    g = grid(r, 48);
    t.eq(g.notes.slice(0, 6), [60, 64, 67, 60, 64, 67], 'chord stabs'); t.eq(g.ticks[3] - g.ticks[0], 48);
    r = await arpRun({ seed: 7, arp: { on: true, mode: 'random', rate: '1/16' } }, [60, 64, 67, 71], 420, { play: true });
    const r2 = await arpRun({ seed: 7, arp: { on: true, mode: 'random', rate: '1/16' } }, [60, 64, 67, 71], 420, { play: true });
    const a = grid(r, 24).notes.slice(0, 6), b = grid(r2, 24).notes.slice(0, 6);
    t.eq(a, b, 'random arp: same seed → same run'); t.ok(new Set(a).size > 1, 'random picks vary');
  });
  await t.test('arp latch: keeps going after release, a fresh chord replaces it, latch off stops it', async () => {
    const r = await p.evaluate(async () => {
      const tr = P.tracks[0]; tr.perf = { arp: { on: true, mode: 'up', rate: '1/16', latch: true } }; E.perfReset(tr.id);
      if (!E.playing) { await E.play(0); await PT.sleep(200); }
      PT.LOG.length = 0;
      PT.press(tr, [60, 64]); await PT.sleep(150); PT.press(tr, [60, 64], false);
      const tRel = E.ctx.currentTime; await PT.sleep(400);
      const after = PT.ons(PT.LOG).filter(e => e.w > tRel + 0.13).map(e => e.n);
      PT.press(tr, [67]); const tNew = E.ctx.currentTime; await PT.sleep(80); PT.press(tr, [67], false); await PT.sleep(400);
      const replaced = PT.ons(PT.LOG).filter(e => e.w > tNew + 0.13).map(e => e.n);
      tr.perf.arp.latch = false; E.perfReset(tr.id); const tOff = E.ctx.currentTime; await PT.sleep(400);
      const stopped = PT.ons(PT.LOG).filter(e => e.w > tOff + 0.15).length;
      return { after, replaced, stopped };
    });
    t.ok(r.after.length >= 4 && r.after.every(n => n === 60 || n === 64), 'latched 60/64 after release: ' + r.after.join(' '));
    t.ok(r.replaced.length >= 4 && r.replaced.every(n => n === 67), 'replaced by 67: ' + r.replaced.join(' '));
    t.eq(r.stopped, 0, 'notes after latch off');
  });
  await t.test('arp free-runs at the project tempo while stopped; swing moves its off-16ths', async () => {
    let r = await arpRun({ arp: { on: true, mode: 'up', rate: '1/16' } }, [60, 64], 700);
    let ons = r.log.filter(e => e.on);
    t.ok(ons.length >= 8, 'steps ' + ons.length);
    t.ok(ons[0].w - r.t0 < 0.06, 'first step ' + Math.round((ons[0].w - r.t0) * 1000) + ' ms after the key');
    ons.slice(1).forEach((e, i) => t.near(e.w - ons[i].w, 24 * r.spt, 0.001, 'free step'));
    await p.evaluate(() => { P.swing = 0.5; });
    r = await arpRun({ arp: { on: true, mode: 'up', rate: '1/16' } }, [60, 64], 700, { play: true });
    const g = r.log.filter(e => e.on).map(e => ({ tk: r.anchor.tick + (e.w - r.anchor.ctx) / r.spt }));
    const sw = 0.5 * 24 * 0.5;      // the old swingDelay, in ticks: off 16ths 6 ticks late
    for (const x of g) { const base = Math.round(x.tk / 24) * 24, want = base + (base % 48 === 24 ? sw : 0); if (Math.abs(x.tk - want) * r.spt > 0.001) throw new Error('swung step at ' + x.tk.toFixed(2) + ', want ' + want); }
    t.ok(g.some(x => Math.abs(x.tk % 48 - 24 - sw) < 0.2), 'some steps swung');
    await p.evaluate(() => { P.swing = 0; E.stop(); });
  });

  await t.test('recording hook: the processed notes (what you hear) reach recordMidi', async () => {
    const r = await p.evaluate(async () => {
      const tr = P.tracks[0], rec = []; tr.arm = true;
      tr.perf = { scale: { on: true }, chord: { on: true } }; E.perfReset(tr.id);
      await E.play(0); await PT.sleep(150);
      E.recordMidi = (t, n, v, on, when) => rec.push({ n, on, when }); E.recording = true;
      const want = E.recNow(); PT.press(tr, [61]); PT.press(tr, [61], false);   // played notes: the raw-MIDI timing (event stamp, recNow), not the audio round trip
      const chord = rec.map(e => (e.on ? '+' : '-') + e.n).join(' '), lat = want - rec[0].when;
      rec.length = 0; tr.perf = { arp: { on: true, rate: '1/8' } }; E.perfReset(tr.id);
      PT.press(tr, [64]); await PT.sleep(400); PT.press(tr, [64], false);
      const arp = rec.filter(e => e.on).map(e => E.anchor.tick + (e.when - E.anchor.ctx) / E.spt());
      E.recording = false; delete E.recordMidi; tr.arm = false; E.stop();
      return { chord, lat, arp };
    });
    t.eq(r.chord, '+60 +64 +67 -60 -64 -67', 'C# → scale lock → C major chord recorded'); t.near(r.lat, 0, 0.002, 'played notes recorded with raw-MIDI timing (recNow)');
    t.ok(r.arp.length >= 2, 'arp steps recorded: ' + r.arp.length);
    for (const tk of r.arp) t.near(tk, Math.round(tk / 48) * 48, 0.2, 'recorded arp steps on the grid');
  });

  // ── 6. groove: live scheduling = renderOffline ─────────────────────
  await t.test('groove (MPC swing, roles, accents, humanize) + clip arp + probability: live notes = offline notes', async () => {
    const r = await p.evaluate(async () => {
      const hats = [], kick = [], bass = [];
      for (let i = 0; i < 16; i++) hats.push({ t: i * 24, d: 12, n: 42, v: 0.7 });
      for (let i = 0; i < 4; i++) kick.push({ t: i * 96, d: 24, n: 36, v: 0.9, p: i % 2 ? 0.5 : undefined });
      for (let i = 1; i < 8; i++) bass.push({ t: i * 48 + (i === 3 ? 5 : 0), d: 40, n: 45 + (i % 3) * 2, v: 0.8 });
      kick.forEach(k => { if (k.p === undefined) delete k.p; });
      await PT.basic({ bpm: 200, tracks: [
        { name: 'hats', role: 'drums', notes: hats, bars: 2 }, { name: 'kick', role: 'drums', notes: kick, bars: 2, perf: { seed: 4 } },
        { name: 'bass', role: 'bass', notes: bass, bars: 2, perf: { nudge: 4, groove: 0.7 } },
        { name: 'lead', role: 'lead', notes: [{ t: 0, d: 384, n: 69, v: 0.7 }, { t: 192, d: 96, n: 72, v: 0.5, p: 0.6 }], bars: 2,
          perf: { seed: 9, chord: { on: true, type: 'seventh' }, arp: { on: true, mode: 'random', rate: '1/16T', oct: 2, gate: 0.8 }, onClips: true } },
      ] });
      P.groove = { on: true, type: 'mpc16', swing: 0.66, roles: { drums: 10, bass: -10, lead: 8 }, accent: 'backbeat', accentDepth: 0.8, human: { ms: 7, vel: 0.08, seed: 3 } };
      for (const tr of P.tracks) PT.spy(tr);
      PT.LOG.length = 0; await E.play(0); const anchor = Object.assign({}, E.anchor);
      await PT.sleep(2700); E.stop();
      const live = PT.ons(PT.LOG).map(e => ({ tr: e.tr, n: e.n, v: e.v, w: e.w - anchor.ctx }));
      PT.OFF.length = 0; await E.renderOffline({ fromBar: 0, toBar: 2, tailSec: 0.2 });
      const off = PT.OFF.map(e => ({ tr: e.tr, n: e.n, v: e.v, w: e.w }));
      PT.OFF.length = 0; await E.renderOffline({ fromBar: 0, toBar: 2, tailSec: 0.2 });
      const off2 = PT.OFF.map(e => ({ tr: e.tr, n: e.n, v: e.v, w: e.w }));
      const key = e => e.tr + ':' + e.n + ':' + e.w.toFixed(6);
      const sort = a => a.slice().sort((x, y) => x.w - y.w || key(x).localeCompare(key(y)));
      const straight = 60 / (200 * 96);
      const hatOffs = sort(off).filter(e => e.tr === 'hats').map(e => e.w / straight);
      return { live: sort(live), off: sort(off), same2: JSON.stringify(sort(off)) === JSON.stringify(sort(off2)), hatOffs, leadN: off.filter(e => e.tr === 'lead').length, kicks: off.filter(e => e.tr === 'kick').length };
    });
    t.ok(r.same2, 'two offline renders give the same notes');
    t.eq(r.live.length, r.off.length, 'note count live vs offline');
    let dw = 0, dv = 0, mism = 0;
    r.live.forEach((a, i) => { const b = r.off[i]; if (a.tr !== b.tr || a.n !== b.n) mism++; dw = Math.max(dw, Math.abs(a.w - b.w)); dv = Math.max(dv, Math.abs(a.v - b.v)); });
    t.eq(mism, 0, 'notes that differ'); t.ok(dw < 1e-6, 'max time difference ' + dw); t.ok(dv < 1e-9, 'max velocity difference ' + dv);
    t.ok(r.leadN > 20, 'clip arp notes ' + r.leadN); t.ok(r.kicks >= 4 && r.kicks <= 8, 'kicks with 50 % on half of them: ' + r.kicks);
    // the swung hats: off 16ths ~ 0.66 · 48 − 24 ≈ 7.7 ticks late, + 10 ms role (3.2 ticks) ± humanize 7 ms (2.2 ticks)
    const late = r.hatOffs.filter((x, i) => i % 2 === 1).map((x, i) => x - (i * 2 + 1) * 24);
    t.ok(late.every(x => x > 4 && x < 14), 'off-16th hats late by ' + late.map(x => x.toFixed(1)).join(' '));
  });

  await t.test('step probability: seeded, deterministic offline, re-seed changes it', async () => {
    const r = await p.evaluate(async () => {
      const notes = []; for (let i = 0; i < 16; i++) notes.push({ t: i * 24, d: 12, n: 42, v: 0.7, p: 0.5 });
      await PT.basic({ bpm: 200, tracks: [{ name: 'hats', notes, bars: 8, perf: { seed: 21 } }] });
      const run = async () => { PT.OFF.length = 0; await E.renderOffline({ fromBar: 0, toBar: 8, tailSec: 0.1 }); return PT.OFF.map(e => e.w.toFixed(6)).join(','); };
      const a = await run(), b = await run(); P.tracks[0].perf.seed = 22; const c = await run();
      return { same: a === b, diff: a !== c, n: a.split(',').length };
    });
    t.ok(r.same, 'same seed → same steps'); t.ok(r.diff, 'new seed → different steps'); t.ok(r.n > 128 * 0.3 && r.n < 128 * 0.7, 'about half of 128 play: ' + r.n);
  });

  await t.test('clip chain: processNotes is pure; scale-lock filter + arp updown on a pattern', async () => {
    const r = await p.evaluate(() => {
      const notes = [{ t: 0, d: 192, n: 60, v: 0.8 }, { t: 0, d: 192, n: 61, v: 0.8 }, { t: 0, d: 192, n: 64, v: 0.6 }, { t: 192, d: 96, n: 67, v: 0.5 }];
      const ctx = { key: 0, scale: SeqGen.SCALES.major, len: 384 };
      const perf = { scale: { on: true, mode: 'filter' }, arp: { on: true, mode: 'updown', rate: '1/8', oct: 2, gate: 0.5 } };
      const a = DawPerf.processNotes(notes, perf, ctx), b = DawPerf.processNotes(notes, perf, ctx);
      return { same: JSON.stringify(a) === JSON.stringify(b), seq: a.map(n => n.t + ':' + n.n).join(' ') };
    });
    t.ok(r.same, 'pure');
    t.eq(r.seq, '0:60 48:64 96:72 144:76 192:67 240:79', 'C# filtered; up-down over 2 octaves; G alone from beat 3');
  });

  // ── 7. save / reload ───────────────────────────────────────────────
  await t.test('save / reload keeps track.perf, project.groove, pattern.steps and step probability', async () => {
    const want = await p.evaluate(async () => {
      const tr = P.tracks[0];
      tr.perf = { scale: { on: true, mode: 'up' }, chord: { on: true, type: 'custom', shape: [0, 5, 7] }, arp: { on: true, rate: '1/32', latch: true }, onClips: false, seed: 5, groove: 0.4, nudge: -6 };
      P.groove = { on: true, type: 'triplet', swing: 0.6, roles: { drums: 4 }, accent: 'hats', accentDepth: 0.3, human: { ms: 3, vel: 0.05, seed: 8 } };
      tr.patterns.a.steps = 24;
      await E.save();
      return JSON.stringify({ perf: tr.perf, groove: P.groove, steps: tr.patterns.a.steps, p: tr.patterns.a.notes.map(n => n.p) });
    });
    await p.reload(); await sl(400);
    await p.evaluate(() => document.getElementById('gatebtn').click()); await sl(1200);
    const got = await p.evaluate(() => { const tr = P.tracks[0]; openPerf(tr.id); sel = { trackId: tr.id, clip: 0 }; STEP.on = true; drawRoll(); return JSON.stringify({ perf: tr.perf, groove: P.groove, steps: tr.patterns.a.steps, p: tr.patterns.a.notes.map(n => n.p) }); });
    t.eq(got, want);
  });
  await t.test('no page / console errors', async () => t.noErrors(errors));
});
