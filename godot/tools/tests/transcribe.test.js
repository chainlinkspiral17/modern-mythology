// transcribe_notes.js + vendor/basicpitch/ (Spotify Basic Pitch on TensorFlow.js): loads from file:// with no
// network, finds a synthesized melody's notes and a chord sequence's chord tones, agrees across backends, long
// audio decodes in segments without losing notes, and prints seconds of processing per second of audio.
const { suite } = require('./harness');

// the page side: a small additive synth (a few harmonics, 5 ms attack, exponential decay, 15 ms release)
const SYNTH = () => {
  window.synth = (sr, sec, notes, harm = [1, 0.5, 0.25, 0.12]) => {
    const x = new Float32Array(Math.round(sr * sec));
    for (const { m, t, d, a = 0.25, k = 1.5 } of notes) {
      const f = 440 * 2 ** ((m - 69) / 12), s = Math.round(t * sr), L = Math.round(d * sr), R = Math.round(0.015 * sr);
      for (let i = 0; i < L + R && s + i < x.length; i++) {
        const env = Math.min(1, i / (0.005 * sr)) * Math.exp(-i / sr * k) * (i < L ? 1 : 1 - (i - L) / R);
        let v = 0; for (let h = 0; h < harm.length; h++) v += harm[h] * Math.sin(2 * Math.PI * f * (h + 1) * i / sr);
        x[s + i] += a * env * v;
      }
    }
    return x;
  };
  // each wanted note matched by a found note of the same MIDI pitch starting within tol seconds
  window.match = (want, got, tol) => {
    const used = new Set(); let hit = 0; const miss = [];
    for (const w of want) {
      const i = got.findIndex((g, k) => !used.has(k) && g.n === w.m && Math.abs(g.t - w.t) <= tol);
      if (i >= 0) { used.add(i); hit++; } else miss.push(w);
    }
    return { hit, miss, extra: got.filter((g, k) => !used.has(k)) };
  };
  // an extra note that is an overtone of a wanted note sounding then (octave, octave + fifth, two octaves …):
  // Basic Pitch's usual mistake on bright, harmonic-rich tones
  window.overtone = (e, want) => want.some(w => [12, 19, 24, 28, 31].includes(e.n - w.m) && e.t >= w.t - 0.06 && e.t <= w.t + w.d);
};

const MELODY = [[57, 0.30], [64, 0.85], [59, 1.45], [67, 1.95], [62, 2.60], [71, 3.10], [60, 3.70], [69, 4.25]]
  .map(([m, t]) => ({ m, t, d: 0.4 }));

suite('transcribe · Basic Pitch (vendored) from file://', async t => {
  const requests = [];
  const { p, errors } = await t.page('tests/mocks/transcribe_page.html', { settle: 100 });
  p.on('request', r => requests.push(r.url()));
  await p.evaluate(SYNTH);
  const speed = [];

  await t.test('engine + model load from file:// — no network, no fetch of files, no console errors', async () => {
    const r = await p.evaluate(async () => {
      const t0 = performance.now(), ok = await BasicPitchLite.ready();
      return { ok, ms: performance.now() - t0, backend: BasicPitchLite.backend, renderer: BasicPitchLite.renderer, error: BasicPitchLite.error,
        v: BasicPitchVendor.versions, weights: BasicPitchVendor.tf.memory().numTensors, again: await BasicPitchLite.ready() };
    });
    console.log(`    backend ${r.backend} (WebGL renderer: ${r.renderer || 'none'}), ready in ${(r.ms / 1000).toFixed(2)} s, basic-pitch ${r.v.basicPitch}, tfjs ${r.v.tfjs}`);
    t.ok(r.ok && r.again, 'ready() → ' + r.ok + ' (' + r.error + ')');
    t.ok(['webgl', 'wasm', 'cpu'].includes(r.backend), 'backend ' + r.backend);
    t.eq(r.weights, 245, 'tensors held = the model\'s weights');
    const files = requests.filter(u => u.startsWith('file:')).map(u => u.replace(/^.*\/godot\/tools\//, ''));
    const other = requests.filter(u => !u.startsWith('file:') && !u.startsWith('data:'));
    t.eq(other, [], 'non-file requests');
    for (const f of files) t.ok(/^(tests\/mocks\/transcribe_page\.html|transcribe_notes\.js|vendor\/basicpitch\/basicpitch_(tf|model|wasm)\.js)$/.test(f), 'unexpected file request ' + f);
    t.noErrors(errors);
  });

  await t.test('melody: 8 enveloped notes (44.1 kHz in) → ≥ 7 at the right pitch within ±60 ms', async () => {
    const r = await p.evaluate(async want => {
      const sr = 44100, x = synth(sr, 5, want);
      const prog = []; const res = await BasicPitchLite.transcribe(x, sr, { onProgress: f => prog.push(f) });
      const m = match(want, res.notes, 0.06);
      return { res, m, wrong: m.extra.filter(e => !overtone(e, want)), prog, mono: prog.every((f, i) => !i || f >= prog[i - 1]) };
    }, MELODY);
    console.log(`    ${r.m.hit}/8 found; ${r.m.extra.length} extra, ${r.m.extra.length - r.wrong.length} of them overtones: ` + r.res.notes.map(n => n.n + '@' + n.t.toFixed(3)).join(' '));
    t.ok(r.m.hit >= 7, `${r.m.hit}/8 (missed ${JSON.stringify(r.m.miss)})`);
    t.ok(r.wrong.length <= 1, 'extra notes that are not overtones ' + JSON.stringify(r.wrong));
    t.near(r.res.seconds, 5, 1e-9, 'seconds = audio length');
    const mel = r.res.notes.filter(n => MELODY.some(w => w.m === n.n && Math.abs(w.t - n.t) <= 0.06));
    t.ok(mel.every(n => n.d > 0.25 && n.d < 0.6), 'melody note durations (0.4 s played) ' + mel.map(n => n.d.toFixed(2)));
    t.ok(r.res.notes.every(n => n.d > 0 && n.v > 0 && n.v <= 1 && Number.isInteger(n.n) && n.t >= 0), 'note fields');
    t.ok(r.mono && r.prog[0] === 0 && r.prog[r.prog.length - 1] === 1 && r.prog.length > 3, 'progress 0 → 1, monotonic');
  });

  await t.test('chords: C, Am, F, G7 (48 kHz in, a different timbre) → the chord tones', async () => {
    const r = await p.evaluate(async () => {
      const chords = [[60, 64, 67], [57, 60, 64], [53, 57, 60, 65], [55, 59, 62, 65]], sr = 48000, notes = [];
      chords.forEach((c, k) => c.forEach(m => notes.push({ m, t: 0.25 + k * 1.1, d: 0.95, a: 0.12 })));
      const res = await BasicPitchLite.transcribe(synth(sr, 5, notes, [1, 0.6, 0.3, 0.2, 0.1]), sr);
      return chords.map((c, k) => {
        const mid = 0.25 + k * 1.1 + 0.45, on = res.notes.filter(n => n.t <= mid && n.t + n.d >= mid), sounding = on.map(n => n.n).sort((a, b) => a - b);
        return { want: c, sounding, found: c.filter(m => sounding.includes(m)).length,
          wrong: on.filter(n => !c.includes(n.n) && !overtone(n, notes.filter(w => w.t === 0.25 + k * 1.1))).map(n => n.n),
          onsetOk: c.filter(m => res.notes.some(n => n.n === m && Math.abs(n.t - (0.25 + k * 1.1)) <= 0.06)).length };
      });
    });
    for (const c of r) console.log(`    want ${c.want.join(',')} → sounding ${c.sounding.join(',')} (onsets ±60 ms: ${c.onsetOk}/${c.want.length}${c.wrong.length ? '; not overtones: ' + c.wrong : ''})`);
    const total = r.reduce((s, c) => s + c.want.length, 0), found = r.reduce((s, c) => s + c.found, 0);
    t.ok(found === total, `chord tones found ${found}/${total}`);
    t.ok(r.every(c => c.onsetOk >= c.want.length - 1), 'chord onsets');
    t.ok(r.every(c => c.wrong.length === 0), 'extra pitches are overtones of chord tones: ' + JSON.stringify(r.map(c => c.wrong)));
  });

  await t.test('a synthetic full mix (drums, bass, chords, lead at 120 bpm): recall per part, and what the extras are', async () => {
    const r = await p.evaluate(async () => {
      const sr = 44100, sec = 16, n = sr * sec, x = new Float32Array(n), beat = 0.5;
      let seed = 5; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
      const add = (notes, harm) => { const y = synth(sr, sec, notes, harm); for (let i = 0; i < n; i++) x[i] += y[i]; };
      const parts = { lead: [], bass: [], chords: [] };
      const prog = [[48, [60, 64, 67]], [45, [57, 60, 64]], [41, [53, 57, 60]], [43, [55, 59, 62]]], scale = [72, 74, 76, 77, 79, 81, 83, 84];
      for (let bar = 0; bar < sec / (4 * beat); bar++) {
        const [b, ch] = prog[bar % 4], t0 = bar * 4 * beat;
        for (let q = 0; q < 4; q++) parts.bass.push({ m: b, t: t0 + q * beat, d: beat * 0.8, a: 0.35, k: 2 });
        for (const m of ch) parts.chords.push({ m, t: t0, d: 4 * beat * 0.95, a: 0.07, k: 0.5 });
        for (let e = 0; e < 8; e++) if (rnd() >= 0.25) parts.lead.push({ m: scale[Math.floor(rnd() * 8)], t: t0 + e * beat / 2, d: beat / 2 * 0.9, a: 0.18, k: 3 });
        for (let q = 0; q < 4; q++) {           // kick on the beat, snare on 2 and 4, hats on the eighths
          const s = Math.round((t0 + q * beat) * sr);
          for (let i = 0; i < 0.25 * sr && s + i < n; i++) { const tt = i / sr; x[s + i] += 0.7 * Math.sin(2 * Math.PI * (50 + 100 * Math.exp(-tt * 30)) * tt) * Math.exp(-tt * 12); }
          if (q % 2) for (let i = 0; i < 0.15 * sr && s + i < n; i++) x[s + i] += 0.35 * (rnd() * 2 - 1) * Math.exp(-i / sr * 25);
          for (let h = 0; h < 2; h++) { const s2 = s + Math.round(h * beat / 2 * sr); let pr = 0; for (let i = 0; i < 0.05 * sr && s2 + i < n; i++) { const w = rnd() * 2 - 1; x[s2 + i] += 0.12 * (w - pr) * Math.exp(-i / sr * 80); pr = w; } }
        }
      }
      add(parts.bass, [1, 0.3, 0.1]); add(parts.chords, [1, 0.5, 0.3, 0.2, 0.1]); add(parts.lead, [1, 0.6, 0.4, 0.2]);
      const res = await BasicPitchLite.transcribe(x, sr), all = Object.values(parts).flat(), used = new Set(), recall = {};
      for (const [k, want] of Object.entries(parts)) {
        let hit = 0;
        for (const w of want) { const i = res.notes.findIndex((g, j) => !used.has(j) && g.n === w.m && Math.abs(g.t - w.t) <= 0.07); if (i >= 0) { used.add(i); hit++; } }
        recall[k] = [hit, want.length];
      }
      const extra = res.notes.filter((g, j) => !used.has(j));
      const near = (e, d) => all.some(w => d.includes(e.n - w.m) && e.t >= w.t - 0.07 && e.t <= w.t + w.d);
      const over = extra.filter(e => near(e, [12, 19, 24, 28, 31])), under = extra.filter(e => !near(e, [12, 19, 24, 28, 31]) && near(e, [-12, -24]));
      return { recall, total: res.notes.length, extra: extra.length, over: over.length, under: under.length, other: extra.length - over.length - under.length };
    });
    console.log(`    recall: ${Object.entries(r.recall).map(([k, [h, n]]) => `${k} ${h}/${n}`).join(', ')}; ${r.total} notes found, ${r.extra} extra = ` +
      `${r.over} overtones + ${r.under} octaves below + ${r.other} other`);
    for (const [k, [h, n]] of Object.entries(r.recall)) t.ok(h >= 0.8 * n, `${k} recall ${h}/${n}`);
  });

  await t.test('options: thresholds, min note length, frequency limits, short / bad input', async () => {
    const r = await p.evaluate(async want => {
      const sr = 22050, x = synth(sr, 5, want);
      // Basic Pitch cuts at the key below the limit's (fractional) key: 300 Hz = key 62.4 → keys ≥ 62 go,
      // 330 Hz = key 64.0 → keys < 64 go
      const lo = await BasicPitchLite.transcribe(x, sr, { maxFreq: 300 });            // 57, 59, 60
      const hi = await BasicPitchLite.transcribe(x, sr, { minFreq: 330 });            // 64, 67, 71, 69 (+ overtones)
      const strict = await BasicPitchLite.transcribe(x, sr, { onsetThreshold: 0.95, frameThreshold: 0.9, melodiaTrick: false });
      const long = await BasicPitchLite.transcribe(x, sr, { minNoteMs: 600 });
      const empty = await BasicPitchLite.transcribe(new Float32Array(100), 44100);
      let bad = ''; try { await BasicPitchLite.transcribe([0, 0, 0], 44100); } catch (e) { bad = e.message; }
      const ac = new AbortController(); ac.abort(); let aborted = '';
      try { await BasicPitchLite.transcribe(x, sr, { signal: ac.signal }); } catch (e) { aborted = e.name; }
      const after = await BasicPitchLite.transcribe(x, sr);
      return { lo: lo.notes.map(n => n.n), hi: hi.notes.map(n => n.n), strict: strict.notes.length, long: long.notes.length, empty: empty.notes, bad, aborted,
        after: after.notes.length, tensors: BasicPitchVendor.tf.memory().numTensors };
    }, MELODY);
    t.ok(r.lo.length >= 3 && r.lo.every(n => n <= 61), 'maxFreq 300 → ' + r.lo);
    t.ok(r.hi.length >= 4 && r.hi.every(n => n >= 64), 'minFreq 330 → ' + r.hi);
    t.ok(r.strict < 8, 'strict thresholds find fewer notes: ' + r.strict);
    t.eq(r.long, 0, 'minNoteMs 600 drops 0.4 s notes');
    t.eq(r.empty, [], 'too-short input');
    t.ok(/Float32Array/.test(r.bad), 'non-Float32Array rejected: ' + r.bad);
    t.eq(r.aborted, 'AbortError', 'abort');
    t.ok(r.after >= 7, 'works after an abort: ' + r.after);
    t.eq(r.tensors, 245, 'no tensors leaked');
  });

  await t.test('long audio (75 s): segmented note decoding = whole-piece decoding; onsets stay put at 70 s', async () => {
    const r = await p.evaluate(async () => {
      const sr = 22050, notes = [];
      let seed = 11; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
      for (let t = 0.3; t < 74; t += 0.6) notes.push({ m: 55 + Math.floor(rnd() * 20), t, d: 0.4 });
      // sustained notes across the 30 s / 60 s segment edges (decay slowed: a held organ-ish tone)
      for (const t of [27, 57.5]) notes.push({ m: 43, t, d: 6, a: 0.2, k: 0.1 });
      const x = synth(sr, 75, notes);
      const t0 = performance.now();
      const seg = await BasicPitchLite.transcribe(x, sr);
      const segMs = performance.now() - t0;
      const whole = await BasicPitchLite.transcribe(x, sr, { noteSegmentSec: Infinity });
      const key = n => n.n + '@' + n.t.toFixed(3);
      // the same note = same key, onset within one model frame (11.6 ms; the onset peak can move a frame when
      // the onset normalisation is per segment)
      const same = (a, b) => a.n === b.n && Math.abs(a.t - b.t) < 0.013 && Math.abs(a.d - b.d) < 0.03;
      const late = notes.filter(n => n.t > 65 && n.d < 1);
      const held = r => [27, 57.5].map(t => r.notes.filter(n => n.n === 43 && Math.abs(n.t - t) < 0.06).map(n => +n.d.toFixed(2)));
      return { seg: seg.notes.length, whole: whole.notes.length, common: seg.notes.filter(n => whole.notes.some(w => same(n, w))).length,
        onlySeg: seg.notes.filter(n => !whole.notes.some(w => same(n, w))).map(key), onlyWhole: whole.notes.filter(n => !seg.notes.some(w => same(n, w))).map(key),
        held: held(seg), heldWhole: held(whole),
        lateHit: match(late, seg.notes, 0.06).hit, late: late.length, melodyHit: match(notes.filter(n => n.d < 1), seg.notes, 0.06).hit,
        melody: notes.length - 2, segMs, wholeMs: whole.ms };
    });
    console.log(`    segmented ${r.seg} notes vs whole ${r.whole} (${r.common} identical); held E2 notes ${JSON.stringify(r.held)} s (whole: ${JSON.stringify(r.heldWhole)}); melody ${r.melodyHit}/${r.melody}; ` +
      `decode+model ${(r.segMs / 1000).toFixed(1)} s segmented vs ${(r.wholeMs / 1000).toFixed(1)} s whole`);
    if (r.onlySeg.length || r.onlyWhole.length) console.log(`    only segmented: ${r.onlySeg.join(' ')} · only whole: ${r.onlyWhole.join(' ')}`);
    t.ok(r.common >= 0.97 * r.whole && Math.abs(r.seg - r.whole) <= 0.03 * r.whole, `segmented ≈ whole (${r.common} common of ${r.whole})`);
    t.eq(r.held, r.heldWhole, 'held notes across a segment edge: one note each, as long as whole-piece decoding makes them');
    t.ok(r.held.every(h => h.length === 1 && h[0] > 4.5), 'held notes ≥ 4.5 s');
    t.ok(r.lateHit >= r.late - 1, `onsets after 65 s within ±60 ms: ${r.lateHit}/${r.late}`);
    t.ok(r.melodyHit >= 0.9 * r.melody, `melody ${r.melodyHit}/${r.melody}`);
  });

  await t.test('speed: seconds of processing per second of audio, per backend; backends agree', async () => {
    const backends = await p.evaluate(() => BasicPitchLite.backend);
    const order = [backends, ...['wasm', 'cpu', 'webgl'].filter(b => b !== backends)];
    const results = {};
    for (const be of order) {
      const r = await p.evaluate(async ([be, want, sec]) => {
        const t0 = performance.now(), ok = await BasicPitchLite.ready({ backend: be }), loadMs = performance.now() - t0;
        if (!ok) return { be, ok, error: BasicPitchLite.error };
        const sr = 44100;
        const notes = []; for (let k = 0; k < sec / 5; k++) for (const n of want) notes.push({ ...n, t: n.t + 5 * k });
        const res = await BasicPitchLite.transcribe(synth(sr, sec, notes), sr);
        const first = res.notes.filter(n => n.t < 5).map(n => [n.n, +n.t.toFixed(3)]);
        return { be: res.backend, ok, loadMs, sec, ms: res.ms, first };
      }, [be, MELODY, be === order[0] ? 20 : 5]);   // the slow fallbacks get 5 s
      if (!r.ok) { console.log(`    ${be}: unavailable (${r.error})`); continue; }
      results[be] = r;
      const line = `${r.be}: ${(r.ms / 1000 / r.sec).toFixed(3)} s per audio second (${r.sec} s in ${(r.ms / 1000).toFixed(1)} s; load + warm-up ${(r.loadMs / 1000).toFixed(1)} s)`;
      speed.push(line); console.log('    ' + line);
    }
    const ref = results[order[0]].first;
    for (const [be, r] of Object.entries(results)) {
      t.eq(r.first.map(n => n[0]), ref.map(n => n[0]), be + ' pitches = ' + order[0] + '\'s');
      r.first.forEach((n, i) => t.near(n[1], ref[i][1], 0.012, be + ' onset ' + i));
    }
    await p.evaluate(b => BasicPitchLite.ready({ backend: b }), order[0]);
    t.noErrors(errors);
  });
});
