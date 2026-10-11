// DX7 engine + SysEx (regression: single-voice dump header 0n, not 1n), sampler mapping
const { suite } = require('./harness');

suite('engines · DX7 + sampler', async t => {
  const { p, errors } = await t.page('patch_bank.html');   // loads fm1_dx7.js, dx7_synth.js, sampler.js
  await t.test('DX7 single-voice dump uses sub-status 0 (bulk), both builders agree', async () => {
    const r = await p.evaluate(() => {
      const v = DX7.defaultVoice(), a = Array.from(dx7VoiceSysex(v, 3)), b = Array.from(DX7.voiceToSysex(v, 3));
      return { head: a.slice(0, 6), len: a.length, same: JSON.stringify(a) === JSON.stringify(b), param: Array.from(dx7ParamChangeSysex(134, 0, 3)).slice(0, 3) };
    });
    t.eq(r.head, [0xF0, 0x43, 0x02, 0x00, 0x01, 0x1B], 'header'); t.eq(r.len, 163); t.ok(r.same, 'fm1_dx7 and DX7 builders differ');
    t.eq(r.param, [0xF0, 0x43, 0x12], 'parameter change keeps 1n');
  });
  await t.test('32-voice bank: build → parse → pack is stable, checksums OK', async () => {
    const r = await p.evaluate(() => {
      const voices = Array.from({ length: 32 }, (_, i) => { const v = DX7.defaultVoice(); v.name = ('TEST ' + i).padEnd(10).slice(0, 10); v.algorithm = i; v.feedback = i % 8; return v; });
      const syx = DX7.bankToSysex(voices, 1), back = DX7.parseSysex(syx);
      const again = DX7.bankToSysex(back.voices, 1);
      return { n: back.voices.length, ok: back.checksums.every(c => c.ok), stable: JSON.stringify(Array.from(syx)) === JSON.stringify(Array.from(again)), alg: back.voices[17].algorithm };
    });
    t.eq(r.n, 32); t.ok(r.ok, 'checksums'); t.ok(r.stable, 'pack/parse not stable'); t.eq(r.alg, 17);
  });
  await t.test('DX7 engine in tune at 44.1 and 48 kHz (INIT voice, A4)', async () => {
    const r = await p.evaluate(async () => {
      const out = {};
      for (const sr of [44100, 48000]) {
        const off = new OfflineAudioContext(2, sr, sr), s = new DX7Synth(off, { output: off.destination });
        await s.init(); s.loadVoice(DX7.defaultVoice()); s.noteOn(69, 0.9, 0); s.noteOff(69, 0.9); await s.flush();
        out[sr] = SampleFormats.detectPitch(await off.startRendering(), 0.2);
      }
      return out;
    });
    for (const sr of [44100, 48000]) t.near(1200 * Math.log2(r[sr] / 440), 0, 3, sr + ' Hz cents');
  });

  // note-named WAVs synthesised in the page (sines at the named pitch)
  const build = `(names) => names.map(nm => {
      const sr = 44100, n = sr, f = 440 * Math.pow(2, (SampleFormats.noteNameToMidi(nm.match(/[A-G][#b]?\\d/)[0]) - 69) / 12);
      const c = new Float32Array(n); for (let i = 0; i < n; i++) c[i] = 0.5 * Math.sin(2 * Math.PI * f * i / sr);
      return { name: nm + '.wav', bytes: new Uint8Array(0), _ch: c };
    })`;
  await t.test('note-named folder: pitch between roots, sparse "v2" takes fold into round robin', async () => {
    const r = await p.evaluate(async (build) => {
      const mk = eval(build);
      const files = mk(['C3', 'E3', 'G3', 'C4', 'E4', 'G4', 'E3 v2', 'G3 v2']).map(f => ({ name: f.name, bytes: AK.wav.encode([f._ch], 44100, { bitDepth: 16 }) }));
      for (const f of files) f.bytes = await f.bytes.arrayBuffer();
      const inst = SampleFormats.instrumentFromFiles(files, { name: 't' });
      // every key maps to ONE root (alternate takes = round robin of that root), nothing layered on top
      let mixed = 0; for (let k = 0; k < 128; k++) { const roots = new Set(inst.zones.filter(z => k >= z.lokey && k <= z.hikey).map(z => z.root)); if (roots.size > 1) mixed++; }
      const rrE3 = inst.zones.filter(z => z.root === 52).map(z => z.seqLength);
      const off = new OfflineAudioContext(2, 44100, 44100), smp = new SampleInstrument(off, { output: off.destination });
      await smp.init(); await smp.load(inst); smp.noteOn(62, 0.8, 0); smp.noteOff(62, 0.9);   // D4 sits between C4 and E4
      const hz = SampleFormats.detectPitch(await off.startRendering(), 0.2);
      return { mixed, rrE3, layers: new Set(inst.zones.map(z => z.lovel + '-' + z.hivel)).size, hz };
    }, build);
    t.eq(r.mixed, 0, 'keys sounding two different roots'); t.eq(r.rrE3, [2, 2], 'E3 + "E3 v2" as round robin'); t.eq(r.layers, 1, 'velocity layers'); t.near(1200 * Math.log2(r.hz / 293.66), 0, 5, 'D4 cents');
  });
  await t.test('a failed sample leaves no hole: respread() covers the keys', async () => {
    const r = await p.evaluate(() => {
      const inst = SampleFormats.instrumentFromFiles(['C3', 'E3', 'G3', 'C4'].map(n => ({ name: n + '.wav', url: 'https://x/' + n + '.wav' })), {});
      inst.zones.forEach(z => { z.buffer = { duration: 1 }; }); inst.zones[2].error = 'HTTP 404'; inst.zones[2].buffer = null;   // G3 missing
      SampleFormats.respread(inst);
      const covered = k => inst.zones.some(z => k >= z.lokey && k <= z.hikey);
      return { n: inst.zones.length, holes: [55, 56, 57, 58, 59].filter(k => !covered(k)) };
    });
    t.eq(r.n, 3); t.eq(r.holes, []);
  });
  await t.test('no page / console errors', async () => t.noErrors(errors));
});
