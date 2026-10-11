// PATCH BANK against the real sources on GitHub (opt-in: TEST_NETWORK=1 — downloads a few MB)
const { suite, network } = require('./harness');

suite('patch bank · real downloads (network)', async t => {
  if (!network) return t.skip('downloads', 'set TEST_NETWORK=1');
  const { p, errors } = await t.page('patch_bank.html', { network: true, start: true });
  const check = async (id, note) => p.evaluate(async ({ id, note }) => {
    const it = await PatchBank.item(id), L = await PatchBank.load(it, ctx);
    const off = new OfflineAudioContext(2, 44100 * 2, 44100);
    let s;
    if (L.kind === 'dx7') { s = new DX7Synth(off, { output: off.destination }); await s.init(); s.loadVoice(L.voice); }
    else { s = new SampleInstrument(off, { output: off.destination }); await s.init(); await s.load(L.inst); }
    s.noteOn(note, 0.8, 0.01); s.noteOff(note, 1.2); if (s.flush) await s.flush();
    const hz = SampleFormats.detectPitch(await off.startRendering(), 0.3);
    return { cents: 1200 * Math.log2(hz / (440 * Math.pow(2, (note - 69) / 12))), cached: await PatchBank.isCached(id), credit: PatchBank.creditSync(it).game };
  }, { id, note });
  await t.test('FluidR3 piano (midi-js) in tune, cached, needs a credit', async () => { const r = await check('fluid:acoustic_grand_piano', 69); t.near(r.cents, 0, 15); t.ok(r.cached); t.eq(r.credit, 'credit'); });
  await t.test('Yamaha ROM 1A voice (DX7 bank) in tune', async () => { const r = await check('rom1a:10', 69); t.near(r.cents, 0, 10); });
  await t.test('Tone.js cello (note-named folder) in tune', async () => { const r = await check('tonejs:cello', 69); t.near(r.cents, 0, 15); });
  await t.test('no page errors', async () => t.noErrors(errors));
});
