/* seqgen_snapshot.js — the reproducibility fingerprint of the composer's five original musical roles.
 *
 *   node godot/tools/tests/fixtures/seqgen_snapshot.js > godot/tools/tests/fixtures/seqgen_roles_v2.json
 *
 * One hash per (style × form × seed × option variant) over the drums / bass / chords / lead / pad notes + clips and the
 * section layout (presets are left out: FORGE pools grow, notes must not move). The checked-in JSON was generated from
 * seqgen.js BEFORE the arrangement parts (counter / arp / perc / double) existed; data.test.js recomputes and compares,
 * so a new part that steals a random draw from an old one fails CI. Never regenerate it to make a failure go away:
 * a mismatch means takes in review / approved takes would re-compose differently.
 */
const path = require('path'), crypto = require('crypto');
const ROLES = ['drums', 'bass', 'chords', 'lead', 'pad'];
const VARIANTS = {
  plain: {},
  sparse: { density: 0.3 },
  busy: { density: 0.9 },
  motif: { motif: 'alma', key: 'D' },
  shape: { shape: [['intro', 2, ['pad']], ['A', 4], ['B', 4, ['drums', 'bass', 'chords', 'lead']], ['outro', 2, ['pad', 'bass']]] },
};
function fingerprint(SG, style, form, seed, vo) {
  const s = SG.song(Object.assign({ seed, style, form }, vo));
  const roles = {};
  for (const r of ROLES) { const p = s.parts[r]; roles[r] = p ? { patterns: p.patterns, clips: p.clips } : null; }
  const o = { sections: s.sections, progression: s.progression, roles };
  return crypto.createHash('sha1').update(JSON.stringify(o)).digest('hex').slice(0, 16);
}
function snapshot(SG) {
  const out = {};
  for (const style of Object.keys(SG.STYLES).sort()) for (const form of ['song', 'short', 'loop', 'bed']) for (const seed of [1, 7, 4242, 987654321])
    for (const [vk, vo] of Object.entries(VARIANTS)) {
      if (vk !== 'plain' && seed !== 7 && seed !== 4242) continue;
      if (vk === 'shape' && form !== 'song') continue;
      out[[style, form, seed, vk].join('/')] = fingerprint(SG, style, form, seed, vo);
    }
  return out;
}
module.exports = { snapshot, fingerprint, VARIANTS, ROLES };
if (require.main === module) {
  const SG = require(path.join(__dirname, '..', '..', 'seqgen.js'));
  process.stdout.write(JSON.stringify(snapshot(SG)).replace(/","/g, '",\n"') + '\n');
}
