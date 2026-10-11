// FORGE instrument library: every preset loads, renders, sounds like itself; macros route somewhere real;
// the composer's per-style pools; the DAW's KIT styles + finger preset browser; old presets / projects unchanged.
const { suite, TOOLS } = require('./harness');
const path = require('path');

// FNV-1a of {name, category, state} for the 29 presets that predate the library (2026-10-11) — their sound is
// what saved projects and generated songs already use, so their data must never change.
const LEGACY = { kick: 'b15110ae', snare: '9eedef94', clap: '5fae2047', hat_closed: '6dd56d3', hat_open: 'dfc1a69', perc_rim: 'c3a93bb', tom: 'e0919f3e',
  bass_sub: '1aa101fd', bass_acid: 'a2ca9e7b', bass_reese: '550901f0', keys_ep: '179ede9', keys_organ: 'cb16864a', keys_tape_ep: '2327c2e4',
  pad_warm: '163c4a6c', pad_glass: 'eac8f6c3', strings_ensemble: '28dfdee0', choir_vox: '61125dfa', pad_fluorescent: '453b0bb3',
  pluck_bell: '6415b903', pluck_marimba: '6ac21703', arp_chip: 'ed44750e', pluck_dobro: 'f8c4dc5', lead_saw: 'f08dd6e5', lead_square: 'd4541ccf',
  lead_whistle: 'da15c302', drone_dark: '10cea232', drone_bayou: '3db6fab2', fx_riser: 'ec584b31', fx_noise_sweep: 'ab600e80' };

// in-page offline renderer + fingerprint (spectral bands, envelope, modulation, spectral motion)
const RENDER = `(async function () {
  const SR = 16000;
  const PAT = { drums: [[[60, 0, 0.3]], 2], bass: [[[36, 0, 1.2], [43, 1.3, 0.5]], 2.6], pads: [[[48, 0, 2.6], [55, 0, 2.6], [60, 0, 2.6], [64, 0, 2.6]], 3.4],
    ambient: [[[48, 0, 2.6], [55, 0, 2.6]], 3.4], fx: [[[60, 0, 2.2]], 3], keys: [[[60, 0, 1.4], [64, 0, 1.4], [67, 0, 1.4]], 2.6],
    plucks: [[[60, 0, 0.5], [67, 0.6, 0.5]], 2.6], leads: [[[67, 0, 1.2], [72, 1.25, 1]], 2.6], winds: [[[67, 0, 1.2], [72, 1.25, 1]], 2.6] };
  function fft(re, im) { const n = re.length; for (let i = 1, j = 0; i < n; i++) { let bit = n >> 1; for (; j & bit; bit >>= 1) j ^= bit; j ^= bit; if (i < j) { [re[i], re[j]] = [re[j], re[i]]; [im[i], im[j]] = [im[j], im[i]]; } }
    for (let len = 2; len <= n; len <<= 1) { const a = -2 * Math.PI / len, wr = Math.cos(a), wi = Math.sin(a); for (let i = 0; i < n; i += len) { let cr = 1, ci = 0; for (let k = 0; k < len / 2; k++) { const h = len / 2, ur = re[i + k], ui = im[i + k], vr = re[i + k + h] * cr - im[i + k + h] * ci, vi = re[i + k + h] * ci + im[i + k + h] * cr; re[i + k] = ur + vr; im[i + k] = ui + vi; re[i + k + h] = ur - vr; im[i + k + h] = ui - vi; const t = cr * wr - ci * wi; ci = cr * wi + ci * wr; cr = t; } } } }
  const edges = Array.from({ length: 25 }, (_, i) => 40 * Math.pow((SR / 2) / 40, i / 24));
  async function render(id, macros) {
    const P = FORGE_PRESETS.find(x => x.id === id), [notes, len] = PAT[P.category] || [[[60, 0, 1.4]], 2.6];
    const off = new OfflineAudioContext(2, Math.round(SR * len), SR);
    const s = new ForgeSynth(off, { output: off.destination, maxVoices: 12, bpm: 100 });
    await s.init(); s.loadPreset(id); await s.loaded();
    if (macros) for (let i = 0; i < 8; i++) s.setMacro(i, 1, 0);
    for (const [n, t, d] of notes) { s.noteOn(n, 0.8, t); s.noteOff(n, t + d); }
    const buf = await off.startRendering(); s.dispose();
    const L = buf.getChannelData(0), R = buf.getChannelData(1), m = new Float32Array(L.length);
    let pk = 0, finite = true;
    for (let i = 0; i < L.length; i++) { if (!isFinite(L[i]) || !isFinite(R[i])) { finite = false; break; } m[i] = (L[i] + R[i]) / 2; pk = Math.max(pk, Math.abs(L[i]), Math.abs(R[i])); }
    const env = (w) => { const f = Math.round(SR * w), o = []; for (let i = 0; i + f <= m.length; i += f) { let e = 0; for (let k = i; k < i + f; k++) e += m[k] * m[k]; o.push(Math.sqrt(e / f)); } return o; };
    const e50 = env(0.05), mx = Math.max(...e50) || 1e-9, holdEnd = Math.max(...notes.map(n => n[1] + n[2]));
    const sus = Math.max(...e50.slice(Math.floor((holdEnd - 0.45) / 0.05), Math.floor((holdEnd - 0.05) / 0.05))) / mx;   // gated pads: the loudest frame of the last 0.4 s
    const act = e50.filter(v => v > mx * 0.01), rms = Math.sqrt(act.reduce((a, v) => a + v * v, 0) / (act.length || 1));
    const N = 2048, bands = new Float64Array(24), cents = [];
    for (let st = 0; st + N <= m.length; st += N) {
      const re = new Float64Array(N), im = new Float64Array(N);
      for (let i = 0; i < N; i++) re[i] = m[st + i] * (0.5 - 0.5 * Math.cos(2 * Math.PI * i / N));
      fft(re, im); let cn = 0, cd = 0;
      for (let k = 1; k < N / 2; k++) { const f = k * SR / N, pw = re[k] * re[k] + im[k] * im[k]; cn += k * pw; cd += pw; if (st < SR * 2.5) { const b = edges.findIndex((e, j) => f >= e && f < edges[j + 1]); if (b >= 0 && b < 24) bands[b] += pw; } }
      if (st >= 0.3 * SR && st + N <= holdEnd * SR && cd > 1e-9) cents.push(cn / cd);
    }
    const bt = bands.reduce((a, v) => a + v, 0) || 1, fp = Array.from(bands, v => Math.log10(1e-6 + v / bt));
    const ef = Array.from({ length: 16 }, (_, i) => e50[Math.floor(i * e50.length / 16)] / mx);
    const e10 = env(0.01), a0 = 30, a1 = Math.max(a0 + 20, Math.floor(holdEnd * 100)); let md = 0, mm = 0;
    for (let i = a0; i < Math.min(a1, e10.length - 8); i++) { let sm = 0; for (let k = -7; k <= 7; k++) sm += e10[Math.max(0, i + k)]; sm /= 15; md += Math.abs(e10[i] - sm); mm += sm; }
    const cmu = cents.reduce((a, v) => a + v, 0) / (cents.length || 1);
    const motion = cents.length > 2 ? Math.sqrt(cents.reduce((a, v) => a + (v - cmu) ** 2, 0) / cents.length) / (cmu || 1) : 0;
    return { id, cat: P.category, pk, finite, rmsDb: 20 * Math.log10(rms || 1e-9), sus, fp, ef, mod: mm ? md / mm : 0, motion };
  }
  const dist = (a, b) => { let d = 0, e = 0; for (let i = 0; i < 24; i++) d += (a.fp[i] - b.fp[i]) ** 2; for (let i = 0; i < 16; i++) e += (a.ef[i] - b.ef[i]) ** 2;
    return Math.sqrt(d / 24) + Math.sqrt(e / 16) + 2 * Math.abs(a.mod - b.mod) + 2 * Math.abs(a.motion - b.motion); };
  window.LIB = { render, dist, async all(ids, macros) { const out = []; for (let i = 0; i < ids.length; i += 8) out.push(...await Promise.all(ids.slice(i, i + 8).map(id => render(id, macros)))); return out; } };
})()`;

suite('library · FORGE presets, composer pools, KIT styles, preset browser', async t => {
  // ── 1. the presets themselves (forge_synth.html) ─────────────────────────
  const B = await t.browser();
  const F = await t.page('forge_synth.html', { browser: B, touch: true });
  await F.p.evaluate(RENDER);

  await t.test('library size, categories, ids, names, tags', async () => {
    const r = await F.p.evaluate(() => {
      const cats = ForgeSynth.categories.map(c => c.id), n = {}, bad = [];
      const ids = new Set();
      for (const p of FORGE_PRESETS) {
        if (ids.has(p.id)) bad.push('dup ' + p.id); ids.add(p.id);
        if (!cats.includes(p.category)) bad.push('category ' + p.id + ':' + p.category);
        if (!/^\S.* · \S/.test(p.name)) bad.push('name ' + p.id);
        if (!ForgeSynth.presetTags(p.id).length) bad.push('no tags ' + p.id);
        n[p.category] = (n[p.category] || 0) + 1;
      }
      return { total: FORGE_PRESETS.length, n, bad, listTags: new ForgeSynth(new OfflineAudioContext(1, 128, 22050)).presetList.every(p => Array.isArray(p.tags)) };
    });
    t.eq(r.bad, [], 'preset problems');
    t.ok(r.total >= 90, 'presets ' + r.total);
    t.ok(r.n.pads >= 20, 'pads ' + r.n.pads); t.ok(r.n.keys >= 10 && r.n.bass >= 8 && r.n.leads >= 8 && r.n.plucks >= 10 && r.n.winds >= 5 && r.n.ambient >= 6 && r.n.drums >= 14, JSON.stringify(r.n));
    t.ok(r.listTags, 'presetList carries tags');
  });

  await t.test('the 29 original presets are unchanged (data fingerprint)', async () => {
    const got = await F.p.evaluate(() => { const h = s => { let x = 2166136261; for (let i = 0; i < s.length; i++) { x ^= s.charCodeAt(i); x = Math.imul(x, 16777619); } return (x >>> 0).toString(16); };
      return Object.fromEntries(FORGE_PRESETS.map(p => [p.id, h(JSON.stringify({ name: p.name, category: p.category, state: p.state }))])); });
    for (const [id, f] of Object.entries(LEGACY)) t.eq(got[id], f, id);
  });

  await t.test('every mod route resolves and every named macro drives something', async () => {
    const bad = await F.p.evaluate(() => {
      const out = [], specs = ForgeSynth.effectSpecs();
      for (const P of FORGE_PRESETS) {
        const S = ForgeSynth.normalizeState(P.state), raw = P.state.mods || [];
        if (raw.length !== S.mods.length) out.push(P.id + ': ' + (raw.length - S.mods.length) + ' route(s) dropped by the normaliser');
        const gens = new Set(S.gens.map(g => g.id)), fx = {}; for (const L of ['A', 'B', 'C']) S.lanes[L].fx.forEach(f => { fx[f.id] = f.type; });
        for (const m of S.mods) {
          const p = m.dst.split('.');
          if (p[0] === 'gen' && !gens.has(p[1])) out.push(P.id + ': no generator ' + m.dst);
          if (p[0] === 'fx' && (!fx[p[1]] || !specs[fx[p[1]]].mods.includes(p[2]))) out.push(P.id + ': no fx target ' + m.dst);
          if (p[0] === 'gen' && p[2] === 'fm' && S.gens.find(g => g.id === p[1]).type !== 'fm') out.push(P.id + ': fm on a non-FM gen ' + m.dst);
          if (p[0] === 'gen' && p[2] === 'cutoff' && S.gens.find(g => g.id === p[1]).type !== 'noise') out.push(P.id + ': cutoff on a non-noise gen ' + m.dst);
          if (p[0] === 'gen' && p[2] === 'morph' && S.gens.find(g => g.id === p[1]).type !== 'wavetable') out.push(P.id + ': morph on a non-wavetable gen ' + m.dst);
        }
        if (P.tags) {   // the library presets: 8 macros on melodic patches, every named one routed
          const named = (P.state.macros || []).length;
          if (!['drums', 'fx', 'bass'].includes(P.category) && named !== 8) out.push(P.id + ': ' + named + ' macros');
          for (let i = 1; i <= named; i++) if (!S.mods.some(m => m.src === 'm' + i)) out.push(P.id + ': macro ' + i + ' (' + S.macros[i - 1].name + ') routes nowhere');
          if (S.mods.some(m => /^m\d$/.test(m.src) && +m.src.slice(1) > named)) out.push(P.id + ': route from an unnamed macro');
        }
      }
      return out;
    });
    t.eq(bad, [], 'routing problems');
  });

  let R = [];
  await t.test('every preset renders offline: finite, audible, under the limiter, pads/ambient sustain', async () => {
    R = await F.p.evaluate(async () => LIB.all(FORGE_PRESETS.map(p => p.id)));
    const bad = [];
    for (const r of R) {
      if (!r.finite) bad.push(r.id + ' NaN');
      if (!(r.pk > 0.01)) bad.push(r.id + ' silent ' + r.pk.toFixed(4));
      if (r.pk > 0.99) bad.push(r.id + ' peak ' + r.pk.toFixed(3));
      if ((r.cat === 'pads' || r.cat === 'ambient') && r.sus < 0.3) bad.push(r.id + ' does not sustain (' + r.sus.toFixed(2) + ')');
    }
    t.eq(bad, [], 'render problems');
  });

  await t.test('loudness: library presets sit within ±8 dB of their category\'s originals', async () => {
    const isNew = await F.p.evaluate(() => Object.fromEntries(FORGE_PRESETS.map(p => [p.id, !!p.tags])));
    const ref = {}; for (const r of R) if (!isNew[r.id]) (ref[r.cat] = ref[r.cat] || []).push(r.rmsDb);
    const mean = a => a.reduce((x, y) => x + y, 0) / a.length;
    const out = R.filter(r => isNew[r.id] && ref[r.cat] && !['drums', 'fx', 'ambient'].includes(r.cat) && Math.abs(r.rmsDb - mean(ref[r.cat])) > 8).map(r => r.id + ' ' + (r.rmsDb - mean(ref[r.cat])).toFixed(1) + ' dB');
    t.eq(out, [], 'too loud / too quiet');
  });

  await t.test('every preset is distinct from its nearest neighbour (spectrum + envelope + motion)', async () => {
    const r = await F.p.evaluate(R => { const near = []; for (const a of R) { let bd = 1e9, bn = ''; for (const b of R) if (a !== b) { const d = LIB.dist(a, b); if (d < bd) { bd = d; bn = b.id; } } near.push([a.id, bn, bd]); } return near; }, R);
    const close = r.filter(x => x[2] < 0.22).map(x => x[0] + '≈' + x[1] + ' ' + x[2].toFixed(2));
    t.eq(close, [], 'near-duplicates');
  });

  await t.test('macros move the sound: all eight up ≠ the patch as voiced (library presets)', async () => {
    const ids = await F.p.evaluate(() => FORGE_PRESETS.filter(p => p.tags).map(p => p.id));
    const up = await F.p.evaluate(ids => LIB.all(ids, true), ids);
    const base = Object.fromEntries(R.map(r => [r.id, r]));
    const dead = await F.p.evaluate(([up, base]) => up.filter(u => LIB.dist(u, base[u.id]) < 0.05 && Math.abs(u.rmsDb - base[u.id].rmsDb) < 0.5).map(u => u.id), [up, base]);
    t.eq(dead, [], 'macros with no audible effect');
    // all eight up may lean on FORGE's soft limiter (0.98 ceiling; its oversampling overshoots to ~0.995) but never past full scale
    t.eq(up.filter(u => !(u.finite && u.pk <= 1)).map(u => u.id + ' ' + u.pk.toFixed(3) + (u.finite ? '' : ' NaN')), [], 'macros up: finite, never past full scale');
  });

  await t.test('FORGE editor: BROWSE overlay by touch — category chip, tile loads the preset, ≥ 36 px targets', async () => {
    const T = t.touch(F.cdp);
    await F.p.evaluate(() => document.getElementById('gatebtn') && document.getElementById('gatebtn').click());
    await F.p.waitForTimeout(600);
    const bb = await F.p.evaluate(() => { const b = [...document.querySelectorAll('.fg-bar button')].find(x => /BROWSE/.test(x.textContent)); const r = b.getBoundingClientRect(); return [r.x + r.width / 2, r.y + r.height / 2]; });
    await T.tap(bb[0], bb[1]);
    const chip = await F.p.evaluate(() => { const c = document.querySelector('.fgb-chip[data-v="cat:pads"]'); const r = c.getBoundingClientRect(); return [r.x + r.width / 2, r.y + r.height / 2]; });
    await T.tap(chip[0], chip[1]);
    const st = await F.p.evaluate(() => {
      const tiles = [...document.querySelectorAll('.fgb-tile')], small = [...document.querySelectorAll('.fgb-chip, .fgb-tile, .fgb-x, .fgb-q')].filter(e => { const r = e.getBoundingClientRect(); return r.height < 36 || r.width < 36; }).length;
      const pick = tiles.find(x => x.dataset.id === 'strings_noir'); const r = pick.getBoundingClientRect();
      return { n: tiles.length, pads: FORGE_PRESETS.filter(p => p.category === 'pads').length, allPads: tiles.every(x => FORGE_PRESETS.find(p => p.id === x.dataset.id).category === 'pads'), small, xy: [r.x + r.width / 2, r.y + r.height / 2] };
    });
    t.eq(st.n, st.pads, 'pad tiles'); t.ok(st.allPads, 'chip filters'); t.eq(st.small, 0, 'targets under 36 px');
    await T.tap(st.xy[0], st.xy[1]);
    t.eq(await F.p.evaluate(() => [...document.querySelectorAll('.fg-name')].map(e => e.value)[0]), 'Strings · After Hours', 'loaded');
    t.noErrors(F.errors);
  });

  // ── 2. composer pools (pure JS) ───────────────────────────────────────────
  const SG = require(path.join(TOOLS, 'seqgen.js'));
  await t.test('composer: pools name real, role-fit presets; picks are per-seed deterministic and varied; notes untouched', async () => {
    const info = await F.p.evaluate(() => Object.fromEntries(FORGE_PRESETS.map(p => [p.id, { cat: p.category, mode: ForgeSynth.normalizeState(p.state).voice.mode }])));
    const bad = [];
    for (const [style, roles] of Object.entries(SG.FORGE_POOLS)) {
      if (!SG.STYLES[style]) bad.push('no style ' + style);
      for (const [role, ids] of Object.entries(roles)) for (const id of ids) {
        const p = info[id]; if (!p) { bad.push(style + '/' + role + ': no preset ' + id); continue; }
        if ((role === 'chords' || role === 'pad') && p.mode !== 'poly') bad.push(style + '/' + role + ': mono ' + id);
        if (role === 'bass' && style !== 'ambient' && p.mode === 'poly') bad.push(style + '/bass: poly ' + id);
        if (p.cat === 'drums' || p.cat === 'fx') bad.push(style + '/' + role + ': ' + p.cat + ' ' + id);
      }
    }
    t.eq(bad, [], 'pool problems');
    const a = SG.song({ seed: 77, style: 'noir', form: 'song' }), b = SG.song({ seed: 77, style: 'noir', form: 'song' });
    t.eq(Object.values(a.parts).map(p => p.preset), Object.values(b.parts).map(p => p.preset), 'same seed, same instruments');
    for (const style of Object.keys(SG.STYLES)) for (const role of ['bass', 'chords', 'lead', 'pad']) {
      const seen = new Set(); for (let seed = 1; seed <= 40; seed++) seen.add(SG.song({ seed, style, form: 'loop' }).parts[role].preset);
      const avail = 1 + ((SG.FORGE_POOLS[style] || {})[role] || []).filter(x => x !== SG.STYLES[style].presets[role]).length;
      if (seen.size < Math.min(3, avail)) bad.push(style + '/' + role + ' only ' + [...seen].join(','));
    }
    t.eq(bad, [], 'variety across seeds');
    // the pick never touches the note RNG: the same song with the pools emptied has identical notes
    const saved = JSON.parse(JSON.stringify(SG.FORGE_POOLS)); for (const k in SG.FORGE_POOLS) SG.FORGE_POOLS[k] = {};
    const c = SG.song({ seed: 77, style: 'noir', form: 'song' });
    Object.assign(SG.FORGE_POOLS, saved);
    t.eq(JSON.stringify(Object.values(c.parts).map(p => p.patterns)), JSON.stringify(Object.values(a.parts).map(p => p.patterns)), 'notes');
    t.eq(c.parts.pad.preset, SG.STYLES.noir.presets.pad, 'empty pool → the style\'s own pick');
  });

  // ── 3. the DAW ─────────────────────────────────────────────────────────────
  const D = await t.page('daw.html', { browser: B, start: true, touch: true });
  await t.test('DAW: generated songs play the seed\'s FORGE picks; KIT gets the style\'s pieces', async () => {
    const r = await D.p.evaluate(async () => {
      window.confirm = () => true; document.getElementById('g-inst').value = 'forge'; document.getElementById('g-form').value = 'loop';
      const out = [];
      for (const [style, seed] of [['trap', 5], ['noir', 12], ['lofi', 3]]) {
        document.getElementById('g-style').value = style;
        await generate({ force: true, seed });
        const want = SeqGen.song({ seed, style, form: 'loop', key: song.key, mode: song.mode, bpm: song.bpm });
        const dev = role => { const t = P.tracks.find(x => x.role === role); return t && E.dev(t.deviceId); };
        const kit = dev('drums'), ki = kit && E.devices.get(kit.id);
        const built0 = ki ? Object.keys(ki.voices).length : -1;               // pieces build on first hit
        if (ki) ki.prepare(Object.keys(ki.map).map(Number));
        out.push({ style, picks: ['bass', 'chords', 'lead', 'pad'].map(r => dev(r) ? dev(r).preset === want.parts[r].preset : true).every(Boolean),
          kick: ki && ki.map[36][0], snare: ki && ki.map[38][0], ride: ki && ki.map[51][0], voices: ki && Object.keys(ki.voices).sort().join(','), built0 });
      }
      return out;
    });
    for (const x of r) t.ok(x.picks, x.style + ' FORGE presets follow SeqGen.presetFor');
    const by = Object.fromEntries(r.map(x => [x.style, x]));
    t.eq([by.trap.kick, by.lofi.kick, by.noir.snare, by.noir.ride], ['kick_808', 'kick_felt', 'snare_brush', 'cym_ride']);
    t.eq(await D.p.evaluate(() => DAW.kitMapFor('ambient')[36][0] + ' ' + DAW.kitMapFor('nope')[70][0]), 'kick perc_shaker', 'unstyled kits use KIT_MAP');
    for (const x of r) t.eq(x.built0, 0, x.style + ': no kit piece is built before it is hit');
    t.ok(!/hat_closed.*kick_808|kick_808/.test(by.lofi.voices) && by.trap.voices.includes('kick_808') && !by.trap.voices.split(',').includes('kick'), 'kit builds only the voices its map plays: ' + by.trap.voices);
  });

  await t.test('DAW: an old project (old KIT map, FORGE state) loads unchanged', async () => {
    const r = await D.p.evaluate(async () => {
      const OLD = { 35: ['kick', 36, 1], 36: ['kick', 36, 1], 37: ['perc_rim', 60, 0.9], 38: ['snare', 60, 1], 42: ['hat_closed', 60, 0.8], 46: ['hat_open', 60, 0.8], 49: ['hat_open', 54, 0.9], 51: ['hat_closed', 66, 0.55], 70: ['hat_closed', 72, 0.4] };
      const fs = new ForgeSynth(new OfflineAudioContext(1, 128, 44100)); fs.loadPreset('keys_ep'); const st = fs.getState();
      const proj = DAW.Engine.newProject();
      proj.devices = [{ id: 'dev1', type: 'kit', name: 'KIT', state: { map: OLD, voices: {} }, mix: { vol: 0.8, pan: 0, mute: false, solo: false, sendA: 0, sendB: 0 } },
        { id: 'dev2', type: 'forge', name: 'EP', preset: 'keys_ep', state: st, mix: { vol: 0.8, pan: 0, mute: false, solo: false, sendA: 0, sendB: 0 } }];
      proj.tracks = [];
      await E.load(proj);
      const kit = E.devices.get('dev1'), ep = E.devices.get('dev2');
      kit.prepare(Object.keys(OLD).map(Number));
      E.snapshotStates();
      return { map: JSON.stringify(kit.map) === JSON.stringify(OLD), voices: Object.keys(kit.voices).sort().join(','), ep: JSON.stringify(ep.getState()) === JSON.stringify(st), saved: JSON.stringify(E.project.devices[0].state.map) === JSON.stringify(OLD) };
    });
    t.ok(r.map && r.saved, 'kit map kept'); t.eq(r.voices, 'hat_closed,hat_open,kick,perc_rim,snare', 'kit voices'); t.ok(r.ep, 'FORGE state kept');
  });

  await t.test('DAW: FORGE picker by touch — search, chips, tap loads + renames, ≥ 36 px; PATCH picker chips ≥ 36 px', async () => {
    const T = t.touch(D.cdp);
    await D.p.evaluate(async () => { document.getElementById('g-style').value = 'noir'; await generate({ force: true, seed: 12 }); const tr = P.tracks.find(x => x.role === 'pad'); sel = { trackId: tr.id, clip: 0 }; document.querySelector('.tabs button[data-tab="dev"]').click(); renderDevDetail(); });
    await D.p.waitForTimeout(200);
    const b = await D.p.evaluate(() => { const r = document.getElementById('dd-preset').getBoundingClientRect(); return [r.x + r.width / 2, r.y + r.height / 2, r.height]; });
    t.ok(b[2] >= 36, 'PRESET button ' + b[2] + ' px');
    await T.tap(b[0], b[1]);
    await D.p.fill('.fgb-q', 'choir');
    const st = await D.p.evaluate(() => {
      const tiles = [...document.querySelectorAll('#modalbody .fgb-tile')], small = [...document.querySelectorAll('#modalbody .fgb-chip, #modalbody .fgb-tile, #modalbody .fgb-x')].filter(e => { const r = e.getBoundingClientRect(); return r.height < 36 || r.width < 36; }).length;
      const c = tiles.find(x => x.dataset.id === 'choir_angel'); const r = c.getBoundingClientRect();
      return { ids: tiles.map(x => x.dataset.id), small, xy: [r.x + r.width / 2, r.y + r.height / 2] };
    });
    t.ok(st.ids.length >= 3 && st.ids.every(id => /choir|crypt|seance|angel|vox|cathedral/.test(id)), 'search: ' + st.ids.join(','));
    t.eq(st.small, 0, 'targets under 36 px');
    await T.tap(st.xy[0], st.xy[1]);
    const after = await D.p.evaluate(() => { const tr = P.tracks.find(x => x.role === 'pad'), d = E.dev(tr.deviceId); return { preset: d.preset, name: d.name, live: E.devices.get(d.id).presetId }; });
    t.eq([after.preset, after.live], ['choir_angel', 'choir_angel']); t.ok(/choir_angel$/.test(after.name), 'device name ' + after.name);
    await D.p.evaluate(() => closeModal());
    await D.p.evaluate(() => openPatchPicker(() => {}));
    await D.p.waitForTimeout(300);
    const pp = await D.p.evaluate(() => { const ch = [...document.querySelectorAll('#pp-cats .chip')]; const rows = [...document.querySelectorAll('#pp-list .item')].slice(0, 20);
      return { chips: ch.length, small: ch.concat(rows).filter(e => e.getBoundingClientRect().height < 36).length, strings: ch.some(c => c.dataset.cat === 'strings') }; });
    t.ok(pp.chips >= 8 && pp.strings, 'patch category chips ' + pp.chips); t.eq(pp.small, 0, 'patch targets under 36 px');
    await D.p.evaluate(() => closeModal());
  });
  await t.test('no page / console errors', async () => { t.noErrors(F.errors); t.noErrors(D.errors); });
});
