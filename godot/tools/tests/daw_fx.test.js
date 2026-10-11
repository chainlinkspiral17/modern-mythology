// DAW mixer: insert FX chains, sidechain ducking, automation lanes — offline renders only
// (the live-vs-offline match was measured once at build time; see the audio playbook).
const { suite } = require('./harness');

suite('daw fx · inserts, ducking, automation', async t => {
  const { p, errors } = await t.page('daw.html', { start: true });
  await p.evaluate(async () => {
    window.confirm = () => true;
    document.getElementById('g-inst').value = 'forge';
    await generate({ force: true, seed: 7 }); await E.whenReady();
    P.loop.on = false; P.swing = 0;
    const sr = 44100;
    const mono = chs => { const o = new Float32Array(chs[0].length); for (const c of chs) for (let i = 0; i < o.length; i++) o[i] += c[i] / chs.length; return o; };
    const rms = (c, a, b) => { let s = 0; a = Math.max(0, a | 0); b = Math.min(c.length, b | 0); for (let i = a; i < b; i++) s += c[i] * c[i]; return Math.sqrt(s / Math.max(1, b - a)); };
    // spectral centroid: zero-crossing rate is a cheap, monotone stand-in for brightness on these sources
    const zcr = c => { let z = 0; for (let i = 1; i < c.length; i++) if ((c[i] >= 0) !== (c[i - 1] >= 0)) z++; return z / c.length; };
    const trk = role => P.tracks.find(x => x.role === role), dev = role => E.dev(trk(role).deviceId);
    const reset = () => { for (const d of P.devices) { d.mix.solo = false; d.mix.mute = false; d.mix.fx = []; delete d.mix.duck; d.mix.sendA = d.mix.sendB = 0; } for (const x of P.tracks) x.auto = []; E.applyMix(); };
    const solo = role => { for (const d of P.devices) d.mix.solo = d === dev(role); E.applyMix(); };
    window.FXT = { sr, mono, rms, zcr, trk, dev, reset, solo };
  });

  await t.test('every insert type builds and renders offline: finite, audible, no errors', async () => {
    const r = await p.evaluate(async () => {
      const { reset, solo, dev } = FXT, bad = [];
      for (const { id } of DawFX.TYPES) {
        reset(); solo('chords');
        E.addFx(dev('chords').id, id, {});
        const o = await E.renderOffline({ fromBar: 4, toBar: 5, tailSec: 0.5 });
        const pk = AK.util.peakOf(o.channels), finite = o.channels.every(c => c.every(Number.isFinite));
        if (!finite || !(pk > 1e-3)) bad.push(id + ' peak ' + pk + (finite ? '' : ' NaN'));
      }
      return { n: DawFX.TYPES.length, bad };
    });
    t.ok(r.n >= 14, 'insert types ' + r.n);
    t.eq(r.bad, [], 'inserts that failed');
    t.noErrors(errors);
  });

  await t.test('inserts move the sound the right way (filter LP/HP, EQ low cut, drive)', async () => {
    const r = await p.evaluate(async () => {
      const { reset, solo, dev, mono, zcr } = FXT;
      const bright = async fx => { reset(); solo('chords'); if (fx) E.addFx(dev('chords').id, fx[0], fx[1]); const o = await E.renderOffline({ fromBar: 4, toBar: 6, tailSec: 0.2 }); return zcr(mono(o.channels)); };
      const base = await bright(null);
      return {
        lp: await bright(['filter', { type: 'lowpass', cutoff: 300, res: 0.1 }]) / base,
        hp: await bright(['filter', { type: 'highpass', cutoff: 3000, res: 0.1 }]) / base,
        lowcut: await bright(['eq', { lowcut: 900 }]) / base,
        drive: await bright(['drive', { mode: 'hard', drive: 0.8 }]) / base,
      };
    });
    t.ok(r.lp < 0.8, 'lowpass darkens: ' + r.lp.toFixed(2));
    t.ok(r.hp > 1.3, 'highpass brightens: ' + r.hp.toFixed(2));
    t.ok(r.lowcut > 1.1, 'EQ low cut brightens: ' + r.lowcut.toFixed(2));
    t.ok(r.drive > 1.1, 'drive adds harmonics: ' + r.drive.toFixed(2));
  });

  await t.test('sidechain: the pad ducks on the kicks, even with the drums muted by solo', async () => {
    const r = await p.evaluate(async () => {
      const { reset, solo, dev, trk, mono, rms, sr } = FXT, spt = E.spt(), FB = 12;
      const kicks = []; { const x = trk('drums'); for (const c of x.clips) { const pt = x.patterns[c.pid]; for (let b = c.bar * BAR; b < (c.bar + (c.bars || pt.lenBars)) * BAR; b += pt.lenBars * BAR) for (const n of pt.notes) { const at = b + n.t; if (n.n === 36 && at >= FB * BAR && at < (FB + 2) * BAR) kicks.push((at - FB * BAR) * spt); } } }
      reset(); solo('pad');
      const dry = await E.renderOffline({ fromBar: FB, toBar: FB + 2, tailSec: 0.5, limiter: false });
      E.setDuck(dev('pad').id, { source: dev('drums').id, amount: 0.6, attack: 0.003, release: 0.12 });
      const wet = await E.renderOffline({ fromBar: FB, toBar: FB + 2, tailSec: 0.5, limiter: false });
      const a = mono(wet.channels), b = mono(dry.channels);
      const g = kicks.map(k => rms(a, (k + 0.01) * sr, (k + 0.06) * sr) / (rms(b, (k + 0.01) * sr, (k + 0.06) * sr) + 1e-9));
      return { kicks: kicks.length, gain: g.reduce((x, y) => x + y, 0) / g.length };
    });
    t.ok(r.kicks >= 4, 'kicks in range ' + r.kicks);
    t.near(r.gain, 0.4, 0.15, 'pad gain at the kicks (amount 0.6)');
  });

  await t.test('automation: a 0→1 volume lane ramps the pad up, and the knob value returns after', async () => {
    const r = await p.evaluate(async () => {
      const { reset, solo, dev, trk, mono, rms, sr } = FXT, FB = 12;
      reset(); solo('pad');
      const vol0 = dev('pad').mix.vol;
      trk('pad').auto = [{ target: 'strip.vol', on: true, points: [{ t: FB * BAR, v: 0 }, { t: (FB + 4) * BAR, v: 1 }] }];
      const o = await E.renderOffline({ fromBar: FB, toBar: FB + 4, tailSec: 0.2, limiter: false });
      const m = mono(o.channels), n = Math.round(4 * BAR * E.spt() * sr), seg = Math.floor(n / 4);
      const q = [0, 1, 2, 3].map(k => rms(m, k * seg, (k + 1) * seg));
      return { q, vol0, volAfter: dev('pad').mix.vol, json: JSON.stringify(trk('pad').auto).length };
    });
    t.ok(r.q[0] < r.q[1] && r.q[1] < r.q[2] && r.q[2] < r.q[3], 'rising quarters ' + r.q.map(v => v.toFixed(3)).join(' '));
    t.ok(r.q[0] < r.q[3] * 0.5, 'first quarter well under the last');
    t.eq(r.volAfter, r.vol0, 'project knob untouched by automation');
  });

  await t.test('undo / redo of an insert + duck edit reaches the audio graph', async () => {
    const r = await p.evaluate(async () => {
      const sl = ms => new Promise(res => setTimeout(res, ms)), { reset, dev } = FXT;
      reset(); saveSoon(); await sl(500);
      const id = dev('chords').id;
      E.addFx(id, 'filter', { type: 'lowpass', cutoff: 400 }); E.setDuck(id, { source: dev('drums').id, amount: 0.5 }); saveSoon(); await sl(500);
      const after = { fx: dev('chords').mix.fx.length, duck: !!dev('chords').mix.duck };
      await undo();
      const undone = { fx: (dev('chords').mix.fx || []).length, duck: !!dev('chords').mix.duck, stripFx: E.strips.get(id).fxUnits.size, duckNode: !!E.strips.get(id).duckNode };
      await redo();
      const redone = { fx: dev('chords').mix.fx.length, duck: !!dev('chords').mix.duck, stripFx: E.strips.get(id).fxUnits.size, duckNode: !!E.strips.get(id).duckNode };
      return { after, undone, redone };
    });
    t.eq(r.after, { fx: 1, duck: true }, 'edit applied');
    t.eq(r.undone, { fx: 0, duck: false, stripFx: 0, duckNode: false }, 'after undo');
    t.eq(r.redone, { fx: 1, duck: true, stripFx: 1, duckNode: true }, 'after redo');
    t.noErrors(errors);
  });
});
