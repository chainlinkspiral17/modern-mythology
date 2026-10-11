// The game side: AudioMgr.gd in a throwaway Godot 4.6 project (stub autoloads + fixture audio).
// Needs a Godot binary: env GODOT, or the cloud sandbox's copy. Skips otherwise.
// Ogg fixtures come from the vendored encoder the tools use (harness.oggEncode).
const { suite, TOOLS, oggEncode } = require('./harness');
const fs = require('fs'), os = require('os'), path = require('path'), cp = require('child_process');

function wav(file, freq, sec = 4, amp = 0.3) {          // 16-bit stereo sine
  const sr = 44100, n = sr * sec, b = Buffer.alloc(44 + n * 4);
  b.write('RIFF', 0); b.writeUInt32LE(36 + n * 4, 4); b.write('WAVEfmt ', 8); b.writeUInt32LE(16, 16); b.writeUInt16LE(1, 20); b.writeUInt16LE(2, 22);
  b.writeUInt32LE(sr, 24); b.writeUInt32LE(sr * 4, 28); b.writeUInt16LE(4, 32); b.writeUInt16LE(16, 34); b.write('data', 36); b.writeUInt32LE(n * 4, 40);
  for (let i = 0; i < n; i++) { const v = Math.round(amp * 32767 * Math.sin(2 * Math.PI * freq * i / sr)); b.writeInt16LE(v, 44 + i * 4); b.writeInt16LE(v, 46 + i * 4); }
  fs.mkdirSync(path.dirname(file), { recursive: true }); fs.writeFileSync(file, b);
}

const sine = (freq, sec, amp = 0.3, sr = 44100) => { const c = new Float32Array(Math.round(sr * sec)); for (let i = 0; i < c.length; i++) c[i] = amp * Math.sin(2 * Math.PI * freq * i / sr); return [c, c.slice()]; };
async function ogg(file, freq, sec, amp) { fs.mkdirSync(path.dirname(file), { recursive: true }); fs.writeFileSync(file, await oggEncode(sine(freq, sec, amp), 44100)); }
const manifest = (file, o) => fs.writeFileSync(file, JSON.stringify(Object.assign({ v: 1, temp: true, format: 'ogg', loop: false, loop_offset: 0, stems: [] }, o)));

suite('godot · AudioMgr stems, intensity, fallbacks, Ogg temps + loops', async t => {
  const godot = [process.env.GODOT, '/tmp/claude-0/-home-user/d52ab41f-1be2-52a2-8aea-26508dc0c250/scratchpad/godot/Godot_v4.6-stable_linux.x86_64'].find(p => p && fs.existsSync(p));
  if (!godot) return t.skip('AudioMgr in Godot', 'no Godot binary — set GODOT=/path/to/Godot_v4.6');
  const proj = fs.mkdtempSync(path.join(os.tmpdir(), 'mmgodot-'));
  fs.cpSync(path.join(__dirname, 'godot'), proj, { recursive: true });
  fs.copyFileSync(path.join(TOOLS, '..', 'autoload', 'AudioMgr.gd'), path.join(proj, 'autoload', 'AudioMgr.gd'));
  const bgm = path.join(proj, 'assets/audio/bgm');
  wav(path.join(bgm, 'plain.wav'), 220);
  wav(path.join(bgm, 'layered.wav'), 330);                                   // the mix (not played: stems win)
  const stems = [['pad', 0, 110], ['bass', 0.25, 55], ['drums', 0.5, 880], ['lead', 0.75, 440]];
  for (const [n, , f] of stems) wav(path.join(bgm, 'layered.stems', n + '.wav'), f);
  fs.writeFileSync(path.join(bgm, 'layered.stems.json'), JSON.stringify({ v: 1, stems: stems.map(([n, l]) => ({ name: n, role: n, layer: l, file: `assets/audio/bgm/layered.stems/${n}.wav` })) }));
  wav(path.join(bgm, 'broken.wav'), 330);
  fs.writeFileSync(path.join(bgm, 'broken.stems.json'), JSON.stringify({ v: 1, stems: [{ name: 'pad', layer: 0, file: 'assets/audio/bgm/missing/pad.wav' }] }));
  // Ogg temps (what the DAW / AUDIO DIRECTOR write): a looping temp with a loop offset (882 Hz: whole cycles in
  // 0.5 s and 1.5 s, so the loop is seamless), layered Ogg stems, a real .ogg beside a temp, a .wav beside a temp
  const B = 'assets/audio/bgm/';
  await ogg(path.join(bgm, 'tmp_loop.temp.ogg'), 882, 1.5);
  manifest(path.join(bgm, 'tmp_loop.stems.json'), { mix: B + 'tmp_loop.temp.ogg', loop: true, loop_offset: (22050 + 0.25) / 44100 });
  await ogg(path.join(bgm, 'oggstems.temp.ogg'), 330, 2);
  const ostems = [['pad', 0, 110], ['bass', 0.25, 55], ['lead', 0.75, 440]];
  for (const [n, , f] of ostems) await ogg(path.join(bgm, 'oggstems.stems', n + '.ogg'), f, 2);
  manifest(path.join(bgm, 'oggstems.stems.json'), { mix: B + 'oggstems.temp.ogg', loop: true, stems: ostems.map(([n, l]) => ({ name: n, role: n, layer: l, file: B + 'oggstems.stems/' + n + '.ogg' })) });
  await ogg(path.join(bgm, 'realwin.ogg'), 220, 2);                          // real audio: wins over the temp + its stems
  await ogg(path.join(bgm, 'realwin.temp.ogg'), 330, 1);
  await ogg(path.join(bgm, 'realwin.stems', 'pad.ogg'), 110, 1);
  manifest(path.join(bgm, 'realwin.stems.json'), { mix: B + 'realwin.temp.ogg', loop: true, stems: [{ name: 'pad', role: 'pad', layer: 0, file: B + 'realwin.stems/pad.ogg' }] });
  wav(path.join(bgm, 'both.wav'), 220, 1);                                    // a recorded .wav beats a temp
  await ogg(path.join(bgm, 'both.temp.ogg'), 330, 1);
  // never imported (.gdignore): the raw load_from_buffer path
  const raw = path.join(proj, 'assets/audio/raw'); fs.mkdirSync(raw, { recursive: true }); fs.writeFileSync(path.join(raw, '.gdignore'), '');
  await ogg(path.join(raw, 'rawtmp.temp.ogg'), 441, 1);
  manifest(path.join(raw, 'rawtmp.stems.json'), { mix: 'assets/audio/raw/rawtmp.temp.ogg', loop: true });
  let res = null;
  await t.test('runs headless', async () => {
    cp.spawnSync(godot, ['--headless', '--path', proj, '--import'], { timeout: 180000 });
    const o = cp.spawnSync(godot, ['--headless', '--path', proj], { timeout: 180000, encoding: 'utf8' });
    const line = (o.stdout + o.stderr).split('\n').find(l => l.startsWith('RESULT '));
    t.ok(line, 'no RESULT line:\n' + (o.stdout + o.stderr).split('\n').filter(l => /ERROR|error/.test(l)).slice(0, 5).join('\n'));
    res = JSON.parse(line.slice(7));
  });
  if (!res) return;
  await t.test('.ogg catalog path falls back to the .wav beside it', async () => t.eq(res.wav_fallback, 'AudioStreamWAV'));
  await t.test('a .stems.json track plays as synchronized stems', async () => { t.eq(res.stream, 'AudioStreamSynchronized'); t.eq(res.layers, 4); t.near(res.length, 4, 0.1); });
  await t.test('intensity 0 drops bass / drums / lead, 1 brings them back', async () => {
    t.eq(res.gains_low, [1, 0, 0, 0]);
    t.ok(res.rms_low < res.rms_full * 0.7, `rms ${res.rms_low} vs ${res.rms_full}`);
    t.near(res.rms_back, res.rms_full, res.rms_full * 0.15, 'back to full');
  });
  await t.test('a missing stem plays the mix instead — and the old track ending mid-fade does not swallow the switch', async () => t.eq(res.broken_stream, 'AudioStreamWAV'));
  await t.test('a temp-only track: can_play, .temp.ogg found, exact length, loop + loop_offset from the manifest (imported and raw)', async () => {
    t.eq([res.tmp_can_play, res.tmp_class, res.tmp_loop, res.tmp_offset_frame, res.tmp_frames], [true, 'AudioStreamOggVorbis', true, 22050, 66150]);
    t.eq([res.raw_class, res.raw_loop, res.raw_frames], ['AudioStreamOggVorbis', true, 44100]);
  });
  await t.test('the temp loops seamlessly in game: no restart, no gap, no click at the loop points', async () => {
    t.eq(res.seam_finished, 0, 'finished signals while looping'); t.eq(res.seam_quiet, 0, 'silent stretches');
    t.ok(res.seam_frames > 44100 * 2, 'captured ' + res.seam_frames);
    t.ok(res.seam_worst < 0.02, `worst sine-predictor residual ${res.seam_worst} (a restart / gap is > 0.05; typical ${res.seam_typical})`);
    console.log(`    loop seam: worst residual ${res.seam_worst}, typical ${res.seam_typical}, over ${res.seam_frames} frames`);
  });
  await t.test('Ogg stems layer as AudioStreamSynchronized, every stem looping, intensity drops layers', async () => {
    t.eq([res.ostems_class, res.ostems_layers, res.ostems_sub, res.ostems_sub_loop], ['AudioStreamSynchronized', 3, 'AudioStreamOggVorbis', [true, true, true]]);
    t.eq(res.ostems_gains_low, [1, 0, 0]);
  });
  await t.test('real audio wins: a real .ogg over a temp (and its stems), a .wav over a .temp.ogg', async () => {
    t.eq([res.real_class, res.real_len, res.real_loop], ['AudioStreamOggVorbis', 2, false]);
    t.eq(res.both_class, 'AudioStreamWAV');
  });
  fs.rmSync(proj, { recursive: true, force: true });
});
