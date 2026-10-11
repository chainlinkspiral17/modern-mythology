// The VN MusicDirector (scripts/vn/MusicDirector.gd) in a throwaway Godot project: inference,
// cue sheets, leitmotifs, locales, silence, smoothing, replay. Needs a Godot binary (GODOT=…).
const { suite, TOOLS } = require('./harness');
const fs = require('fs'), os = require('os'), path = require('path'), cp = require('child_process');
const GAME = path.join(TOOLS, '..');

function wav(file, sec = 3) {
  const sr = 22050, n = sr * sec, b = Buffer.alloc(44 + n * 2);
  b.write('RIFF', 0); b.writeUInt32LE(36 + n * 2, 4); b.write('WAVEfmt ', 8); b.writeUInt32LE(16, 16); b.writeUInt16LE(1, 20); b.writeUInt16LE(1, 22);
  b.writeUInt32LE(sr, 24); b.writeUInt32LE(sr * 2, 28); b.writeUInt16LE(2, 32); b.writeUInt16LE(16, 34); b.write('data', 36); b.writeUInt32LE(n * 2, 40);
  for (let i = 0; i < n; i++) b.writeInt16LE(Math.round(8000 * Math.sin(2 * Math.PI * 220 * i / sr)), 44 + i * 2);
  fs.mkdirSync(path.dirname(file), { recursive: true }); fs.writeFileSync(file, b);
}

suite('godot · VN MusicDirector', async t => {
  const godot = [process.env.GODOT, '/tmp/claude-0/-home-user/d52ab41f-1be2-52a2-8aea-26508dc0c250/scratchpad/godot/Godot_v4.6-stable_linux.x86_64'].find(p => p && fs.existsSync(p));
  if (!godot) return t.skip('MusicDirector in Godot', 'no Godot binary — set GODOT=/path/to/Godot_v4.6');
  const proj = fs.mkdtempSync(path.join(os.tmpdir(), 'mmdirector-'));
  fs.cpSync(path.join(__dirname, 'godot'), proj, { recursive: true });
  fs.copyFileSync(path.join(GAME, 'autoload', 'AudioMgr.gd'), path.join(proj, 'autoload', 'AudioMgr.gd'));
  fs.copyFileSync(path.join(GAME, 'scripts', 'vn', 'MusicDirector.gd'), path.join(proj, 'scripts', 'vn', 'MusicDirector.gd'));
  fs.writeFileSync(path.join(proj, 'project.godot'), fs.readFileSync(path.join(proj, 'project.godot'), 'utf8').replace('res://autoload/Tester.gd', 'res://DirectorTester.gd'));
  // fixture catalog + direction: Sharp's theme on disk, a club locale track, the real lexicon / defaults
  const real = JSON.parse(fs.readFileSync(path.join(GAME, 'resources', 'music', 'direction.json'), 'utf8'));
  fs.mkdirSync(path.join(proj, 'resources', 'music'), { recursive: true });
  fs.writeFileSync(path.join(proj, 'resources', 'music_catalog.json'), JSON.stringify([
    { id: 'vol1_sharp_theme', vol: 1, src: 'assets/audio/bgm/vol1_sharp_theme.ogg', chars: ['sharp'] },
    { id: 'vol1_club_thump', vol: 1, src: 'assets/audio/bgm/vol1_club_thump.mp3' },
    { id: 'vol1_cue', vol: 1, src: 'assets/audio/bgm/vol1_cue.ogg' }]));
  fs.writeFileSync(path.join(proj, 'resources', 'music', 'direction.json'), JSON.stringify({
    defaults: real.defaults, lexicon: real.lexicon,
    scenes: { t_cued: { track: 'vol1_cue', intensity: 0.3, beats: [{ at: 1, intensity: 0.95 }, { at: 2, auto: true }] } },
    locales: {}, characters: {},
    locales_auto: { 'assets/backgrounds/vol1_club_dance.jpg': { 1: 'vol1_club_thump' } },
    characters_auto: { sharp: { theme: 'vol1_sharp_theme', leitmotif: true } } }));
  for (const f of ['vol1_sharp_theme', 'vol1_club_thump', 'vol1_cue']) wav(path.join(proj, 'assets/audio/bgm', f + '.wav'));
  let r = null;
  await t.test('runs headless', async () => {
    cp.spawnSync(godot, ['--headless', '--path', proj, '--import'], { timeout: 180000 });
    const o = cp.spawnSync(godot, ['--headless', '--path', proj], { timeout: 180000, encoding: 'utf8' });
    const line = (o.stdout + o.stderr).split('\n').find(l => l.startsWith('RESULT '));
    t.ok(line, 'no RESULT:\n' + (o.stdout + o.stderr).split('\n').filter(l => /ERROR/.test(l)).slice(0, 6).join('\n'));
    r = JSON.parse(line.slice(7));
  });
  if (!r) return;
  await t.test('inference: tense writing plays harder than calm writing', async () => {
    t.ok(r.tense.target > r.calm.target + 0.25, `tense ${r.tense.target} vs calm ${r.calm.target}`);
    t.ok(r.tense.baseline > r.calm.baseline, 'scene baselines');
  });
  await t.test('choice builds, interlude breathes, cg lifts', async () => {
    t.ok(r.choice >= 0.85, 'choice ' + r.choice); t.near(r.interlude, 0.2, 0.01, 'interlude'); t.ok(r.cg >= 0.9, 'cg ' + r.cg);
  });
  await t.test('cue sheet: track + pinned intensity, beat moves it, auto hands back', async () => {
    t.eq(r.cued_start.track, 'assets/audio/bgm/vol1_cue.ogg'); t.eq(r.cued_start.track_reason, 'cue sheet');
    t.near(r.cued_pinned, 0.3, 0.001, 'tense line ignored while pinned'); t.near(r.cued_beat, 0.95, 0.001, 'beat');
    t.ok(!r.cued_auto.pinned && r.cued_auto.target < 0.95, 'auto → inference ' + JSON.stringify(r.cued_auto));
  });
  await t.test('leitmotif: the focal character\'s theme', async () => {
    t.eq(r.sharp.focal, 'sharp'); t.eq(r.sharp.track, 'assets/audio/bgm/vol1_sharp_theme.ogg'); t.ok(r.sharp.track_reason.startsWith('leitmotif'));
  });
  await t.test('locale: the background picks the track (and it plays when nothing else is)', async () => {
    t.eq(r.club.track, 'assets/audio/bgm/vol1_club_thump.mp3'); t.ok(r.club.track_reason.startsWith('locale'));
    t.eq(r.club_playing, 'assets/audio/bgm/vol1_club_thump.mp3');
  });
  await t.test('music node: silence', async () => t.ok(r.silence.startsWith('silence'), r.silence));
  await t.test('smoothed intensity reaches AudioMgr', async () => t.near(r.sent, r.target_now, 0.15, 'sent vs target'));
  await t.test('replay to node 2 lands on the authored beat', async () => t.near(r.replay, 0.95, 0.001));
  fs.rmSync(proj, { recursive: true, force: true });
});
