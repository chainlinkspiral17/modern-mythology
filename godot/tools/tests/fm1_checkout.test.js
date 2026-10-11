// fm1_checkout — the guided FM-1 hardware check-out page, against a mock FM-1
// (tests/mocks/fm1_mock.js: Web MIDI replies, MIDI thru, a fake USB audio input).
const { suite } = require('./harness');
const { PROFILES, MOCK } = require('./mocks/fm1_mock');

const init = (name, extra = {}) =>
  `window.__FM1_PROFILE = ${JSON.stringify(Object.assign({ audioMode: 'gate' }, PROFILES[name], extra))};(${MOCK})();`;

suite('fm1 checkout · mock hardware', async t => {
  async function open(name) {
    const o = await t.page('fm1_checkout.html', { init: init(name), settle: 400 });
    const { p } = o;
    o.press = async sel => {
      const r = await p.evaluate(s => { const el = document.querySelector(s); if (!el) return null; el.scrollIntoView({ block: 'center' });
        const q = el.getBoundingClientRect(); return { x: q.left + q.width / 2, y: q.top + q.height / 2 }; }, sel);
      if (!r) throw new Error('no element ' + sel);
      await p.mouse.click(r.x, r.y); await p.waitForTimeout(80);
    };
    o.answer = (cid, a = 'yes') => o.press(`.chk[data-cid="${cid}"] button.${a}`);
    o.waitFor = async (fn, ms = 8000) => { const end = Date.now() + ms; while (Date.now() < end) { if (await p.evaluate(fn)) return true; await p.waitForTimeout(100); } return false; };
    o.sentLen = () => p.evaluate(() => window.__fm1sent.length);
    o.sentSince = i => p.evaluate(i => window.__fm1sent.slice(i), i);
    o.connect = async () => {
      await o.press('[data-act="connect"]');
      t.ok(await o.waitFor(() => !connecting && R.steps.connect && R.steps.connect.checks.fw && R.steps.connect.checks.fw.status !== 'pending', 9000), 'connect step finished');
      if (await p.$('.chk[data-cid="port"] button.yes')) await o.answer('port');
      if (await p.$('.chk[data-cid="fw_ok"] button.yes')) await o.answer('fw_ok');
    };
    o.goto = async id => { await o.press(`.nav-step[data-go="${id}"]`); t.eq(await p.evaluate(() => R.cur), id, 'on step'); };
    return o;
  }
  const isInfo = s => s.d[0] === 0xF0 && s.d[1] === 0x7D;
  const noteOnChans = sent => [...new Set(sent.filter(x => (x.d[0] & 0xF0) === 0x90).map(x => (x.d[0] & 15) + 1))];

  await t.test('Felucca: identified, INFO asked, parts on registry channels, DX7 not applicable', async () => {
    const o = await open('felucca'), { p } = o;
    await o.connect();
    const dev = await p.evaluate(() => R.device);
    t.ok(/felucca/i.test(dev.firmware), 'firmware ' + dev.firmware);
    t.ok((await o.sentSince(0)).some(isInfo), 'INFO request sent to a Felucca port');
    await o.goto('notes_out');
    const parts = await p.evaluate(() => [...document.querySelectorAll('[data-act="play-part"]')].map(b => [b.dataset.role, +b.dataset.ch]));
    t.eq(Object.fromEntries(parts), { bass: 1, chords: 2, lead: 3, drums: 4 }, 'Felucca part channels');
    const a = await o.sentLen();
    await o.press('[data-act="play-part"][data-role="lead"]'); await p.waitForTimeout(2600);
    const s = await o.sentSince(a);
    t.eq(noteOnChans(s), [3], 'lead phrase channel');
    t.eq(s.filter(x => (x.d[0] & 0xF0) === 0x90).length, s.filter(x => (x.d[0] & 0xF0) === 0x80).length, 'every note-on released');
    await o.goto('dx7');
    t.ok(await p.evaluate(() => !!document.querySelector('#card .na')), 'DX7 step marked not applicable');
    t.noErrors(o.errors);
  });

  await t.test('stock firmware: no INFO request (Felucca-only SysEx never reaches it)', async () => {
    const o = await open('stock');
    await o.connect();
    const sent = await o.sentSince(0);
    t.ok(sent.some(s => s.d[0] === 0xF0 && s.d[1] === 0x00 && s.d[2] === 0x32), 'version query sent');
    t.ok(!sent.some(isInfo), 'INFO not sent to stock');
    t.noErrors(o.errors);
  });

  await t.test('FM-1+VA: DX7 push refused until the overwrite box is ticked, then valid 163-byte dumps', async () => {
    const o = await open('fm1va'), { p } = o;
    await o.connect();
    await o.goto('dx7');
    t.ok(await p.$('#dx7-ack'), 'overwrite acknowledgement shown');
    let a = await o.sentLen();
    await o.press('[data-act="dx7-send"][data-v="sine"]'); await p.waitForTimeout(300);
    t.eq((await o.sentSince(a)).length, 0, 'nothing sent before the tick');
    await o.press('label.ack');
    a = await o.sentLen();
    await o.press('[data-act="dx7-send"][data-v="brass"]'); await p.waitForTimeout(400);
    const dumps = (await o.sentSince(a)).filter(x => x.d[0] === 0xF0 && x.d[1] === 0x43 && x.d.length > 10);
    t.eq(dumps.length, 1, 'one voice dump');
    const d = dumps[0].d, data = d.slice(6, 161), sum = data.reduce((x, y) => x + y, 0);
    t.eq(d.length, 163, 'dump length');
    t.eq(d.slice(0, 6), [0xF0, 0x43, 0x00, 0x00, 0x01, 0x1B], 'header');
    t.ok(data.every(b => b < 128), 'data is 7-bit');
    t.eq(d[161], (128 - (sum & 127)) & 127, 'checksum');
    t.eq(d[162], 0xF7, 'EOX');
    t.eq(String.fromCharCode(...d.slice(151, 161)).trim(), 'MM BRASS', 'voice name');
    t.noErrors(o.errors);
  });

  await t.test('clock: START, 24 timestamped ticks per beat at 90 BPM, STOP after the last tick', async () => {
    const o = await open('felucca'), { p } = o;
    await o.connect();
    await o.goto('clock');
    const a = await o.sentLen();
    await o.press('[data-act="clk-bpm"][data-bpm="90"]');
    await o.press('[data-act="clk-start"]');
    await p.waitForTimeout(1500);
    await o.press('[data-act="clk-stop"]'); await p.waitForTimeout(300);
    const s = await o.sentSince(a);
    const ticks = s.filter(x => x.d[0] === 0xF8), fa = s.find(x => x.d[0] === 0xFA), fc = s.find(x => x.d[0] === 0xFC);
    t.ok(fa && fc, 'START and STOP sent');
    t.ok(ticks.length > 30 && ticks.every(x => x.ts != null), 'ticks timestamped');
    const per = 60000 / (90 * 24);
    for (let i = 1; i < ticks.length; i++) t.near(ticks[i].ts - ticks[i - 1].ts, per, 0.5, 'tick ' + i);
    t.ok(fc.ts >= ticks[ticks.length - 1].ts, 'STOP after last tick');
    t.noErrors(o.errors);
  });

  await t.test('USB audio: input auto-picked, latency measured ≈ 23 ms and saved for the DAW', async () => {
    const o = await open('felucca'), { p } = o;
    await o.connect();
    await o.goto('audio');
    await o.press('[data-act="aud-find"]');
    t.ok(await o.waitFor(() => !!AUD.cap, 5000), 'FM-1 audio input opened automatically');
    await p.waitForTimeout(400);
    await o.press('[data-act="lat-run"]');
    t.ok(await o.waitFor(() => !audBusy && R.steps.audio.checks.latency.status !== 'pending', 30000), 'latency run finished');
    const r = await p.evaluate(() => ({ lat: R.latency, ls: localStorage.getItem('mm_fm1_latency_ms') }));
    t.near(r.lat.ms, 23, 2, 'median latency');
    t.near(+r.ls, 23, 2, 'mm_fm1_latency_ms');
    t.noErrors(o.errors);
  });

  await t.test('answers persist across a reload', async () => {
    const o = await open('felucca'), { p } = o;
    await o.connect();
    await p.reload(); await p.waitForTimeout(600);
    const r = await p.evaluate(() => ({ cur: R.cur, fw: R.device.firmware, banner: /are loaded/.test(document.getElementById('card').textContent) }));
    t.eq(r.cur, 'connect', 'back on step 1');
    t.ok(/felucca/i.test(r.fw) && r.banner, 'results restored');
    t.noErrors(o.errors);
  });
});
