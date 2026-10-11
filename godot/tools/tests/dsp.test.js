// audio_kit.js DSP + worklets on file:// (regressions: blob-URL worklets, LUFS K-weighting)
const { suite } = require('./harness');

suite('dsp · loudness, true peak, mastering, worklets on file://', async t => {
  const { p, errors } = await t.page('field_recorder.html', { fakeMedia: true });
  await t.test('LUFS matches ffmpeg ebur128 on sines (K-weighting incl. the 38 Hz RLB stage)', async () => {
    const r = await p.evaluate(async () => {
      const sr = 44100, n = sr * 5, o = {};
      for (const f of [1000, 100, 40, 5000]) { const c = new Float32Array(n); for (let i = 0; i < n; i++) c[i] = 0.1 * Math.sin(2 * Math.PI * f * i / sr); o[f] = await AK.dsp.lufs([c, c.slice()], sr); }
      return o;
    });
    // ffmpeg ebur128 for the same stereo sines: 1k −20.0, 100 Hz −21.9, 40 Hz −26.3, 5 kHz −16.7
    t.near(r[1000], -20.0, 0.15, '1 kHz'); t.near(r[100], -21.85, 0.15, '100 Hz'); t.near(r[40], -26.3, 0.2, '40 Hz'); t.near(r[5000], -16.7, 0.15, '5 kHz');
  });
  await t.test('true peak catches inter-sample overs', async () => {
    const tp = await p.evaluate(async () => {
      const sr = 44100, n = sr, c = new Float32Array(n);
      for (let i = 0; i < n; i++) c[i] = 0.5 * Math.sin(2 * Math.PI * (sr / 4) * i / sr + Math.PI / 4);   // samples ±0.354, real peak 0.5
      return { tp: await AK.dsp.truePeak([c, c.slice()], sr), sp: AK.util.db(AK.util.peakOf([c])) };
    });
    t.near(tp.sp, -9.0, 0.1, 'sample peak'); t.near(tp.tp, -6.0, 0.4, 'true peak');
  });
  await t.test('master() lands on the LUFS target under the true-peak ceiling', async () => {
    const r = await p.evaluate(async () => {
      const sr = 44100, n = sr * 8, L = new Float32Array(n), R = new Float32Array(n);
      for (let i = 0; i < n; i++) { const kick = (i % 22050) < 2000 ? Math.sin(2 * Math.PI * 55 * i / sr) * Math.exp(-(i % 22050) / 600) : 0; L[i] = 0.2 * Math.sin(2 * Math.PI * 220 * i / sr) + 0.9 * kick; R[i] = L[i]; }
      const m = await AK.dsp.master([L, R], sr, { lufs: -14, truePeak: -1.5 });
      return { lufs: await AK.dsp.lufs(m.channels, sr), tp: m.truePeak };
    });
    t.near(r.lufs, -14, 0.25, 'LUFS'); t.ok(r.tp <= -1.4, 'true peak ' + r.tp);
  });
  await t.test('stems share the mix\'s limiter curve and still sum to the mastered mix', async () => {
    const r = await p.evaluate(async () => {
      const sr = 44100, n = sr * 4, mk = f => { const c = new Float32Array(n); for (let i = 0; i < n; i++) c[i] = 0.6 * Math.sin(2 * Math.PI * f * i / sr) * (i % 11025 < 3000 ? 1 : 0.3); return [c, c.slice()]; };
      const a = mk(110), b = mk(330), sum = [0, 1].map(ch => a[ch].map((v, i) => v + b[ch][i]));
      const m = await AK.dsp.master(sum, sr, { lufs: -10, truePeak: -1.5, stems: [a, b] });
      let d = 0, e = 0; for (let i = 0; i < n; i++) { const s = m.stems[0][0][i] + m.stems[1][0][i]; d += (s - m.channels[0][i]) ** 2; e += m.channels[0][i] ** 2; }
      return 10 * Math.log10(d / e);
    });
    t.ok(r < -80, 'stems sum residual ' + r.toFixed(1) + ' dB');
  });
  await t.test('Ogg Vorbis: the vendored encoder runs from file:// with no network; Chrome decodes it back aligned and as loud', async () => {
    const r = await p.evaluate(async () => {
      const sr = 44100, n = sr * 10, L = new Float32Array(n), R = new Float32Array(n);
      let seed = 7; const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647) - 0.5;
      for (let i = 0; i < n; i++) {          // chords + a bass line + noisy hats: busy enough to cost real bits
        const t = i / sr, beat = (i % 11025) / sr, f = [110, 146.8, 98, 130.8][Math.floor(t / 2) % 4];
        const v = 0.18 * Math.sin(2 * Math.PI * f * t) + 0.1 * (Math.sin(2 * Math.PI * f * 2.5 * t) + Math.sin(2 * Math.PI * f * 3 * t)) + rnd() * 0.25 * Math.exp(-beat * 40);
        L[i] = v; R[i] = 0.8 * v + 0.05 * Math.sin(2 * Math.PI * 660 * t);
      }
      const t0 = performance.now();
      const blob = await AK.ogg.encode([L, R], sr, { quality: AK.ogg.Q.mix });
      const encMs = performance.now() - t0;
      const head = new TextDecoder().decode(new Uint8Array(await blob.slice(0, 4).arrayBuffer()));
      const dec = await new OfflineAudioContext(2, 1, sr).decodeAudioData(await blob.arrayBuffer());
      const D = [dec.getChannelData(0), dec.getChannelData(1)];
      let e = 0, s = 0; for (let i = 0; i < n; i++) { e += (D[0][i] - L[i]) ** 2; s += L[i] ** 2; }
      // a loop {start, end}: the file ends at end + 1 (the loop end IS the stream end); the start is the manifest's
      const cut = await AK.ogg.encode([L, R], sr, { quality: 1, loop: { start: 4410, end: sr * 5 - 1 } });
      const dcut = await new OfflineAudioContext(2, 1, sr).decodeAudioData(await cut.arrayBuffer());
      const lo = AK.ogg.loopOf({ start: 4410, end: sr * 5 - 1 }, n, sr);
      return { head, len: dec.length, n, lufsIn: await AK.dsp.lufs([L, R], sr), lufsOut: await AK.dsp.lufs(D, sr), snr: 10 * Math.log10(s / e), bytes: blob.size, encMs,
        cutLen: dcut.length, lo, net: performance.getEntriesByType('resource').map(x => x.name).filter(u => !u.startsWith('file:')) };
    });
    t.eq(r.head, 'OggS'); t.eq(r.net, [], 'no network requests');
    // Chrome's decoder does not trim the last page to its granule position (Godot does: the godot_audiomgr suite
    // checks the exact length there): up to one Vorbis block of padding at the END, none at the start
    t.ok(r.len >= r.n && r.len - r.n <= 2048, 'decoded length ' + r.len + ' vs ' + r.n);
    t.near(r.lufsOut, r.lufsIn, 0.3, 'loudness'); t.ok(r.snr > 12, 'SNR ' + r.snr.toFixed(1) + ' dB');
    const mbMin = r.bytes / 10 * 60 / 1048576;
    t.ok(mbMin < 1.3, 'mix ' + mbMin.toFixed(2) + ' MB/min (a 16-bit WAV is 10.1)');
    t.ok(r.cutLen >= 44100 * 5 && r.cutLen - 44100 * 5 <= 2048, 'loop cut at the end: ' + r.cutLen);
    t.eq([r.lo.loop, r.lo.start, r.lo.frames], [true, 4410, 44100 * 5], 'loop cut');
    t.ok(Math.floor(r.lo.offset * 44100) === 4410 && Math.round(r.lo.offset * 44100) === 4410, 'loop_offset lands on the start frame');
    console.log(`    mix q${4}: ${mbMin.toFixed(2)} MB/min, encoded 10 s in ${r.encMs.toFixed(0)} ms`);
  });
  await t.test('AK.wav.decode reads 16 / 24-bit PCM sample-exact, with the smpl loop', async () => {
    const r = await p.evaluate(async () => {
      const sr = 22050, n = 3001, c = new Float32Array(n); for (let i = 0; i < n; i++) c[i] = 0.5 * Math.sin(i / 7);
      const out = {};
      for (const bits of [16, 24]) {
        const d = AK.wav.decode(await AK.wav.encode([c, c], sr, { bitDepth: bits, loop: { start: 10, end: 2999 } }).arrayBuffer());
        let m = 0; for (let i = 0; i < n; i++) m = Math.max(m, Math.abs(d.channels[1][i] - c[i]));
        out[bits] = { len: d.channels[0].length, nch: d.channels.length, sr: d.sampleRate, loop: d.loop, err: m };
      }
      return out;
    });
    for (const b of [16, 24]) { t.eq([r[b].len, r[b].nch, r[b].sr, r[b].loop], [3001, 2, 22050, { start: 10, end: 2999 }]); t.ok(r[b].err < (b === 16 ? 1.5e-4 : 1e-6), b + '-bit error ' + r[b].err); }
  });
  await t.test('AudioWorklets load from file:// (data: URL path)', async () => {
    const mode = await p.evaluate(async () => { const c = new AudioContext(); const cap = new AK.Capture(c, c.createGain(), {}); await cap.start(); const m = cap.mode; cap.stop(); return m; });
    t.eq(mode, 'worklet');
  });
  await t.test('TAPE STUDIO starts its tape worklet from file://', async () => {
    const { p: tp, errors: te } = await t.page('tape_studio.html');
    const ok = await tp.evaluate(async () => { await startAudio(); return !!tape && ctx.state; });
    t.eq(ok, 'running'); t.noErrors(te);
  });
  await t.test('no page / console errors', async () => t.noErrors(errors));
});
