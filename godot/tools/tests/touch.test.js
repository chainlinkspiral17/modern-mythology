// finger controls: relative sliders, clip drag / long-press delete, piano-roll tap / hold
const { suite } = require('./harness');

suite('touch · sliders, arrangement, piano roll', async t => {
  const { p, errors, cdp } = await t.page('daw.html', { touch: true, start: true });
  const f = t.touch(cdp);
  await p.evaluate(async () => { window.confirm = () => true; document.getElementById('g-inst').value = 'forge'; document.getElementById('g-form').value = 'loop'; await generate({ force: true, seed: 3 }); });
  const rect = sel => p.evaluate(s => { const r = document.querySelector(s).getBoundingClientRect(); return { x: r.left, y: r.top, w: r.width, h: r.height }; }, sel);

  await t.test('slider: slide up raises (relative), double-tap resets', async () => {
    const r = await rect('#swing');
    await f.drag(r.x + 5, r.y + r.h / 2, 0, -110);
    const up = +(await p.evaluate(() => document.getElementById('swing').value));
    await f.tap(r.x + 5, r.y + r.h / 2); await f.tap(r.x + 5, r.y + r.h / 2);
    const reset = +(await p.evaluate(() => document.getElementById('swing').value));
    t.ok(up > 0.25, 'after slide ' + up); t.eq(reset, 0);
  });
  const geo = await p.evaluate(() => { const r = document.getElementById('arrcv').getBoundingClientRect(); return { x: r.left, y: r.top, bar: view.barPx, lane: view.laneH }; });
  const laneY = i => geo.y + 34 + i * geo.lane + geo.lane / 2;
  await t.test('arrangement: drag a clip two bars, long-press deletes', async () => {
    await f.drag(geo.x + geo.bar * 2, laneY(0), geo.bar * 2, 0);
    const bar = await p.evaluate(() => P.tracks[0].clips[0].bar);
    await f.hold(geo.x + geo.bar * 2, laneY(1));
    const left = await p.evaluate(() => P.tracks[1].clips.length);
    t.eq(bar, 2); t.eq(left, 0);
  });
  await t.test('piano roll: tap adds a note, long-press removes it', async () => {
    await p.evaluate(() => { sel = { trackId: P.tracks[3].id, clip: 0 }; roll.zoom = 3; drawRoll(); });
    const g = await p.evaluate(() => { const r = document.getElementById('rollcv').getBoundingClientRect(), w = document.getElementById('rollwrap').getBoundingClientRect(); return { x: r.left, y: r.top, keyw: roll.KEYW, tp: roll.tickPx, rh: roll.rowH, wy: w.top, wh: w.height, n: curClip().p.notes.length, sl: document.getElementById('rollwrap').scrollLeft }; });
    // an empty cell: first bar, a sixteenth in, in the middle of the visible rows
    const ri = Math.floor((g.wy + g.wh / 2 - g.y) / g.rh), x = g.x + g.keyw + 12 * g.tp + 3, y = g.y + ri * g.rh + g.rh / 2;
    const occupied = await p.evaluate(({ ri }) => { const n = roll.rows[ri]; return curClip().p.notes.some(m => m.n === n && m.t <= 12 && m.t + m.d > 12); }, { ri });
    if (occupied) return t.skip('roll tap', 'cell already has a note for this seed');
    await f.tap(x, y); await new Promise(r => setTimeout(r, 300));
    const added = await p.evaluate(() => curClip().p.notes.length);
    await f.hold(x, y);
    const removed = await p.evaluate(() => curClip().p.notes.length);
    t.eq([added, removed], [g.n + 1, g.n]);
  });
  await t.test('no page / console errors', async () => t.noErrors(errors));
});
