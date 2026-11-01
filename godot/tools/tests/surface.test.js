// surface.js — the Arturia MiniLab 3 as a controller: the checkout page (live view, LEARN EVERY CONTROL, the map
// kept for every page), and what its controls do in the DAW, the AUDIO DIRECTOR, FORGE and TAPE STUDIO. A mock
// Web MIDI with a MiniLab 3 port (and an FM-1 next to it: midi_input.js must leave the MiniLab alone).
const { suite } = require('./harness');

const MOCK = `(() => {
  const mkIn = (id, name) => { const p = { id, name, type: 'input', state: 'connected', onmidimessage: null, _l: [],
    addEventListener(t, f) { if (t === 'midimessage') this._l.push(f); }, removeEventListener(t, f) { this._l = this._l.filter(x => x !== f); } }; return p; };
  const mini = mkIn('in-mini', window.__MINI_NAME || 'Minilab3 MIDI'), fm1 = mkIn('in-fm1', 'FM-1');
  const thru = mkIn('in-thru', 'Midi Through Port-0');
  const outs = new Map([['out-mini', { id: 'out-mini', name: 'Minilab3 MIDI', type: 'output', state: 'connected', send() {} }]]);
  const withFm1 = !window.__NO_FM1;
  const access = { inputs: new Map(withFm1 ? [['in-thru', thru], ['in-fm1', fm1], ['in-mini', mini]] : [['in-thru', thru], ['in-mini', mini]]), outputs: outs, sysexEnabled: false, addEventListener() {}, removeEventListener() {} };
  navigator.requestMIDIAccess = async () => access;
  const fire = (port, bytes) => { const ev = { data: new Uint8Array(bytes), timeStamp: performance.now() }; if (port.onmidimessage) port.onmidimessage(ev); for (const f of port._l) f(ev); };
  window.__mini = bytes => fire(mini, bytes);
  window.__fm1 = bytes => fire(fm1, bytes);
  try { if (!sessionStorage.getItem('__surf_clean')) { localStorage.removeItem('mm_surface_minilab3'); sessionStorage.setItem('__surf_clean', '1'); } } catch (e) {}      // once per tab: a reload keeps the learned map
})();`;

suite('surface · MiniLab 3: checkout, learn, DAW / director / FORGE / TAPE STUDIO', async t => {
  const tick = p => p.waitForTimeout(40);

  await t.test('checkout: found by name, controls light up, LEARN EVERY CONTROL maps a re-assigned unit, kept after a reload', async () => {
    const { p, errors } = await t.page('surface_checkout.html', { init: MOCK, settle: 500 });
    t.ok(/Minilab3/.test(await p.textContent('#b-conn')), 'connected: ' + await p.textContent('#b-conn'));
    await p.evaluate(() => __mini([0xB0, 74, 100])); await tick(p);
    t.ok(await p.evaluate(() => document.querySelector('[data-c="knob1"]').classList.contains('hit')), 'knob 1 (factory CC 74) lights up');
    // a unit re-assigned in MIDI Control Center: knobs CC 20–27, faders 30–33, pads notes 60–75 on ch 1, encoder CC 40, push CC 41
    await p.click('#learnall');
    const msgs = [...[20, 21, 22, 23, 24, 25, 26, 27].map(n => [0xB0, n, 70]), ...[30, 31, 32, 33].map(n => [0xB0, n, 90]),
      ...Array.from({ length: 16 }, (_, i) => [0x90, 60 + i, 100]), [0xB0, 40, 65], [0xB0, 41, 127]];
    for (const m of msgs) { await p.evaluate(m => __mini(m), m); await tick(p); }
    const r = await p.evaluate(() => ({ wiz: document.getElementById('wiz').textContent, k8: Surface.map.knob8, f1: Surface.map.fader1, p16: Surface.map.pad16, enc: Surface.map.encoder, n: Object.keys(Surface.learned).length, saved: localStorage.getItem('mm_surface_minilab3') }));
    t.ok(/done/.test(r.wiz) && r.n === 30, r.wiz + ' · learned ' + r.n);
    t.eq([r.k8.n, r.f1.n, r.p16.t, r.p16.n, r.enc.n, r.enc.rel], [27, 30, 'note', 75, 40, true]);
    t.ok(JSON.parse(r.saved).controls.knob1.n === 20, 'saved for every page');
    await p.waitForTimeout(300); await p.reload(); await p.waitForFunction(() => window.Surface && Surface.connected, null, { timeout: 10000 });
    await p.evaluate(() => __mini([0xB0, 20, 50])); await tick(p);
    t.ok(await p.evaluate(() => document.querySelector('[data-c="knob1"]').classList.contains('hit') && Surface.map.knob1.n === 20), 'the learned map after a reload');
    t.noErrors(errors);
  });

  await t.test('checkout: a MiniLab under an odd port name is listed, USE THIS picks it, every page keeps the pick, AUTO undoes it', async () => {
    const init = 'window.__MINI_NAME = "USB MIDI Interface 20:0";' + MOCK.replace("'__surf_clean'", "'__surf_clean2'").replace("'__surf_clean', '1'", "'__surf_clean2', '1'") + ';try{if(!sessionStorage.getItem("__port_clean")){localStorage.removeItem("mm_surface_port");sessionStorage.setItem("__port_clean","1")}}catch(e){}';
    const { p, errors } = await t.page('surface_checkout.html', { init, settle: 500 });
    const before = await p.evaluate(() => ({ conn: Surface.connected, rows: [...document.querySelectorAll('#ports tr')].map(r => r.textContent) }));
    t.ok(!before.conn && before.rows.some(r => /USB MIDI Interface/.test(r)) && before.rows.some(r => /FM-1/.test(r)), 'not matched by name, but listed: ' + before.rows.join(' | '));
    t.ok(await p.evaluate(() => { const r = [...document.querySelectorAll('#ports tr')].find(r => /Midi Through/.test(r.textContent)); return r && /loopback/.test(r.textContent) && !r.querySelector('[data-pick]'); }), 'Midi Through is marked as the loopback, no USE THIS');
    const i = before.rows.findIndex(r => /USB MIDI Interface/.test(r));
    await p.click(`#ports tr:nth-child(${i + 1}) [data-pick]`); await tick(p);
    await p.evaluate(() => __mini([0xB0, 74, 100])); await tick(p);
    const r = await p.evaluate(() => ({ conn: Surface.connected, port: Surface.portName, hit: document.querySelector('[data-c="knob1"]').classList.contains('hit'), badge: document.getElementById('b-conn').textContent, claims: Surface.claims('USB MIDI Interface 20:0') }));
    t.ok(r.conn && r.hit && /USB MIDI Interface/.test(r.badge) && r.claims, JSON.stringify(r));
    await p.waitForTimeout(300); await p.reload(); await p.waitForFunction(() => window.Surface && Surface.connected, null, { timeout: 10000 });
    t.ok(await p.evaluate(() => Surface.connected && Surface.portName === 'USB MIDI Interface 20:0'), 'kept after a reload');
    await p.click('[data-unpick]'); await tick(p);
    t.ok(await p.evaluate(() => !Surface.connected && !Surface.chosenPort()), 'AUTO: back to the name match');
    t.noErrors(errors);
  });

  await t.test('DAW: keys play the selected track, knobs = its FORGE macros, faders = volumes, encoder selects, pads = drums + transport; the FM-1 keeps its port', async () => {
    const { p, errors } = await t.page('daw.html', { init: MOCK, start: true });
    await p.evaluate(async () => { window.confirm = () => true; document.getElementById('g-inst').value = 'forge'; document.getElementById('g-style').value = 'boom_bap'; document.getElementById('g-form').value = 'loop'; await generate({ force: true, seed: 42 }); await E.whenReady(); await Surface.start(); });
    const r = await p.evaluate(async () => {
      const wait = () => new Promise(res => setTimeout(res, 30));
      const calls = []; const orig = E.liveNote.bind(E); E.liveNote = (id, n, v, on) => { calls.push([E.track(id).role, n, on]); return orig(id, n, v, on); };
      const lead = P.tracks.find(x => x.role === 'lead'); sel.trackId = lead.id;
      __mini([0x90, 60, 100]); __mini([0x80, 60, 0]); await wait();
      __mini([0xB0, 74, 127]); await wait();                       // knob 1 → macro 1 of the lead's FORGE
      const m1 = E.devices.get(lead.deviceId).getState().macros[0].value;
      __mini([0xB0, 82, 64]); await wait();                        // fader 1 → the first track of the lead's group of four
      const i0 = P.tracks.findIndex(x => x.id === lead.id), ft = P.tracks[i0 - (i0 % 4)], fvol = E.stripOwner(E.stripOf(ft)).mix.vol;
      __mini([0x99, 36, 110]); __mini([0x89, 36, 0]); await wait();   // pad 1 → kick on the drum track
      const loop0 = P.loop.on; __mini([0x99, 46, 100]); await wait(); // pad 3 of bank B → loop
      const loop1 = P.loop.on;
      __mini([0xB0, 114, 65]); await wait(); const after = sel.trackId; // encoder (CC 114, Arturia mode) → next track
      return { calls, m1, fvol, loop0, loop1, moved: after !== lead.id, fm1In: E.midi && E.midi.input ? E.midi.input.name : null, badge: document.getElementById('b-surf').textContent };
    });
    t.ok(r.calls.some(c => c[0] === 'lead' && c[1] === 60 && c[2]) && r.calls.some(c => c[0] === 'lead' && c[1] === 60 && !c[2]), 'keys → the lead: ' + JSON.stringify(r.calls));
    t.ok(r.calls.some(c => c[0] === 'drums' && c[1] === 36 && c[2]), 'pad 1 → kick on the drums');
    t.ok(r.m1 === 1 && Math.abs(r.fvol - 64 / 127 * 1.4) < 0.01, 'macro 1 = ' + r.m1 + ', fader vol = ' + r.fvol);
    t.eq([r.loop1, r.moved], [!r.loop0, true]);
    t.eq(r.fm1In, 'FM-1', 'midi_input.js keeps the FM-1, never the MiniLab');
    t.noErrors(errors);
  });

  await t.test('FORGE: keys play, knobs move the macros, the encoder browses presets and the push loads one', async () => {
    const { p, errors } = await t.page('forge_synth.html', { init: MOCK, settle: 600 });
    const r = await p.evaluate(async () => {
      await Surface.start(); const wait = () => new Promise(res => setTimeout(res, 30));
      const notes = []; const on = synth.noteOn.bind(synth); synth.noteOn = (n, v) => { notes.push(n); return on(n, v); };
      __mini([0x90, 64, 90]); __mini([0x80, 64, 0]); await wait();
      __mini([0xB0, 71, 127]); await wait();                       // knob 2 (CC 71) → macro 2
      const m2 = synth.state.macros[1].value;
      const before = synth.presetId; __mini([0xB0, 28, 65]); __mini([0xB0, 28, 65]); await wait(); __mini([0xB0, 118, 127]); await wait();
      return { notes, m2, el: +document.getElementById('mac2').value, before, after: synth.presetId };
    });
    t.ok(r.notes.includes(64) && r.m2 === 1 && r.el === 1, JSON.stringify(r));
    t.ok(r.after && r.after !== r.before, 'preset ' + r.before + ' → ' + r.after);
    t.noErrors(errors);
  });

  await t.test('TAPE STUDIO: knobs move the master tape controls, pads arm tapes', async () => {
    const { p, errors } = await t.page('tape_studio.html', { init: MOCK, settle: 600 });
    const r = await p.evaluate(async () => {
      await Surface.start(); const wait = () => new Promise(res => setTimeout(res, 30));
      __mini([0xB0, 76, 0]); await wait();                         // knob 3 → VERB mix to 0
      __mini([0x99, 37, 100]); await wait();                       // pad 2 → arm tape 2
      return { verb: +document.getElementById('verbmix').value, armed: tracks[1].armed };
    });
    t.eq([r.verb, r.armed], [0, true]);
    t.noErrors(errors);
  });

  await t.test('AUDIO DIRECTOR: the MiniLab badge follows the controls (a pad with no take says so)', async () => {
    const { p, errors } = await t.page('audio_director.html', { init: MOCK, settle: 600 });
    const r = await p.evaluate(async () => { await Surface.start(); __mini([0x99, 36, 100]); await new Promise(res => setTimeout(res, 50)); return document.getElementById('b-surf').textContent; });
    t.ok(/no take 1/.test(r), r);
    t.noErrors(errors);
  });
});
