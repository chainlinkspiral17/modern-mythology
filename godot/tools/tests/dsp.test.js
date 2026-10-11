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
