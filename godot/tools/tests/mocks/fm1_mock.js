/* fm1_mock.js — a fake M-VAVE FM-1 for headless tests (Web MIDI + USB audio).
 * Injected as an init script with window.__FM1_PROFILE set. It answers the vendor
 * version query and the Felucca-family INFO request, echoes notes (MIDI thru),
 * records every send in window.__fm1sent, and fakes a USB audio input whose tone
 * starts P.latencyMs after each note-on's MIDI timestamp. Exposes __fm1mock.key/knob. */
module.exports.PROFILES = {
  fm1va:   { port: 'FM-1 MIDI 1', identity: 'FM-1_093', info: null, keyCh: 1, audioLabel: 'FM-1 Analog Stereo', latencyMs: 23 },
  stock:   { port: 'FM-1 MIDI 1', identity: 'FM-1_015', info: null, keyCh: 1, audioLabel: 'FM-1 Analog Stereo', latencyMs: 23 },
  felucca: { port: 'Felucca MIDI 1', identity: 'FM-1_915', info: 'FELUCCA v1.5.1', keyCh: 3, audioLabel: 'Felucca Analog Stereo', latencyMs: 23 },
  sloop:   { port: 'Felucca MIDI 1', identity: 'FM-1_925', info: 'FELUCCA SLOOP 2.5', keyCh: 1, audioLabel: 'Felucca Analog Stereo', latencyMs: 23 },
  x0x:     { port: 'X0X FM-1 MIDI 1', identity: 'FM-1_9010005', info: 'X0X 1.0.5 BETA', keyCh: 10, audioLabel: 'X0X FM-1 Analog Stereo', latencyMs: 23 },
  unknown: { port: 'USB MIDI Interface MIDI 1', identity: null, info: null, keyCh: 1, audioLabel: 'USB Audio Device Analog Stereo', latencyMs: 23 },
};

module.exports.MOCK = () => {
  const P = window.__FM1_PROFILE;
  const sent = []; window.__fm1sent = sent;
  const listeners = new Set();
  const emit = bytes => { const ev = { data: Uint8Array.from(bytes), timeStamp: performance.now() }; for (const l of listeners) l(ev); };
  const pack = s => { const blk = [0x00, 0x59, 0x11, 0, 0, 0, ...[...s].map(c => c.charCodeAt(0))]; while (blk.length < 34) blk.push(0);
    let acc = 0, bits = 0; const o = [0xF0];
    for (const x of blk) { acc |= x << bits; bits += 8; while (bits >= 7) { o.push(acc & 0x7F); acc >>>= 7; bits -= 7; } }
    if (bits) o.push(acc & 0x7F); o.push(0xF7); return o; };
  const audio = { gates: [] };
  const input = { id: 'in-1', name: P.port, manufacturer: 'mock', type: 'input', state: 'connected', connection: 'open',
    addEventListener(t, f) { if (t === 'midimessage') listeners.add(f); }, removeEventListener(t, f) { listeners.delete(f); } };
  const output = { id: 'out-1', name: P.port, manufacturer: 'mock', type: 'output', state: 'connected', connection: 'open',
    send(data, ts) {
      const d = [...data], now = performance.now();
      if (d.some(b => b > 255 || b < 0)) throw new TypeError('bad byte');
      sent.push({ d, ts: ts == null ? null : ts, now });
      const at = ts == null ? now : ts;
      if (d[0] === 0xF0 && d[1] === 0x00 && d[2] === 0x32 && d[3] === 0x45 && P.identity) setTimeout(() => emit(pack(P.identity)), 40);
      if (d[0] === 0xF0 && d[1] === 0x7D && d[2] === 0x46 && d[3] === 0x4C && d[4] === 0x01 && P.info)
        setTimeout(() => emit([0xF0, 0x7D, 0x46, 0x4C, 0x01, ...[...P.info].map(c => c.charCodeAt(0)), 0, 0xF7]), 20);
      const st = d[0] & 0xF0;
      if ((st === 0x90 || st === 0x80) && d.length === 3) {
        setTimeout(() => emit(d), Math.max(0, at - now) + 3);                 // MIDI thru echo
        const on = st === 0x90 && d[2] > 0;
        for (const g of audio.gates) g(on, at);
      }
    } };
  const access = { inputs: new Map([[input.id, input]]), outputs: new Map([[output.id, output]]), sysexEnabled: true,
    addEventListener() {}, removeEventListener() {} };
  navigator.requestMIDIAccess = async opts => { access.sysexEnabled = !!(opts && opts.sysex); return access; };
  window.__fm1mock = {
    key(n, v, ch = P.keyCh) { emit([0x90 | (ch - 1), n, v]); setTimeout(() => emit([0x80 | (ch - 1), n, 0]), 150); },
    knob(cc, vals, ch = P.keyCh) { vals.forEach((v, i) => setTimeout(() => emit([0xB0 | (ch - 1), cc, v]), i * 30)); },
  };
  // ── audio: an oscillator that "plays" P.latencyMs after each note-on's MIDI timestamp ──
  const fake = new WeakSet();
  const realCMSS = AudioContext.prototype.createMediaStreamSource;
  const ctxOf = (ctx, perf) => { const ts = ctx.getOutputTimestamp ? ctx.getOutputTimestamp() : null;
    if (ts && ts.performanceTime) return ts.contextTime + (perf - ts.performanceTime) / 1000;
    return ctx.currentTime + (perf - performance.now()) / 1000; };
  function voice(ctx, dest) {
    const osc = ctx.createOscillator(); osc.frequency.value = 330;
    const gate = ctx.createGain(); gate.gain.value = 0; osc.connect(gate); gate.connect(dest); osc.start();
    audio.gates.push((on, perf) => { const t = Math.max(ctx.currentTime, ctxOf(ctx, perf) + P.latencyMs / 1000); gate.gain.setValueAtTime(on ? 0.5 : 0, t); });
  }
  let bridgeCtx = null;
  navigator.mediaDevices.getUserMedia = async c => {
    if (P.audioMode === 'bridge') {   // a real MediaStream from another AudioContext (adds Chrome's stream buffering)
      if (!bridgeCtx) { bridgeCtx = new AudioContext(); const dst = bridgeCtx.createMediaStreamDestination(); voice(bridgeCtx, dst); bridgeCtx._dst = dst; }
      await bridgeCtx.resume();
      return bridgeCtx._dst.stream.clone();
    }
    const s = new MediaStream(); fake.add(s); return s;
  };
  navigator.mediaDevices.enumerateDevices = async () => [
    { deviceId: 'default', kind: 'audioinput', label: 'Default', groupId: 'a' },
    { deviceId: 'deck', kind: 'audioinput', label: 'Steam Deck Internal Microphone', groupId: 'b' },
    { deviceId: 'fm1', kind: 'audioinput', label: P.audioLabel, groupId: 'c' },
    { deviceId: 'spk', kind: 'audiooutput', label: 'Speakers', groupId: 'd' },
  ];
  AudioContext.prototype.createMediaStreamSource = function (stream) {
    if (!fake.has(stream)) return realCMSS.call(this, stream);
    const outN = this.createGain(); voice(this, outN); return outN;
  };
  window.__fm1audio = audio;
};
