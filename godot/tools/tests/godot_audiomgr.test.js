// The game side: AudioMgr.gd in a throwaway Godot 4.6 project (stub autoloads + fixture audio).
// Needs a Godot binary: env GODOT, or the cloud sandbox's copy. Skips otherwise.
const { suite, TOOLS } = require('./harness');
const fs = require('fs'), os = require('os'), path = require('path'), cp = require('child_process');

function wav(file, freq, sec = 4, amp = 0.3) {          // 16-bit stereo sine
  const sr = 44100, n = sr * sec, b = Buffer.alloc(44 + n * 4);
  b.write('RIFF', 0); b.writeUInt32LE(36 + n * 4, 4); b.write('WAVEfmt ', 8); b.writeUInt32LE(16, 16); b.writeUInt16LE(1, 20); b.writeUInt16LE(2, 22);
  b.writeUInt32LE(sr, 24); b.writeUInt32LE(sr * 4, 28); b.writeUInt16LE(4, 32); b.writeUInt16LE(16, 34); b.write('data', 36); b.writeUInt32LE(n * 4, 40);
  for (let i = 0; i < n; i++) { const v = Math.round(amp * 32767 * Math.sin(2 * Math.PI * freq * i / sr)); b.writeInt16LE(v, 44 + i * 4); b.writeInt16LE(v, 46 + i * 4); }
  fs.mkdirSync(path.dirname(file), { recursive: true }); fs.writeFileSync(file, b);
}

suite('godot · AudioMgr stems, intensity, fallbacks', async t => {
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
  fs.rmSync(proj, { recursive: true, force: true });
});
