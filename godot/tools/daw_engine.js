/* daw_engine.js — the playback / recording engine behind daw.html.
 *
 * Model (plain JSON, saved to IndexedDB through AK.lib.kv 'daw_project'):
 *   project = { v, name, bpm, swing, key, mode, loop:{on,a,b} (bars), metro,
 *               devices: [{ id, type, name, emuId?, preset?, state, mix }],
 *               tracks:  [{ id, name, color, kind:'midi'|'audio', deviceId, channel,
 *                           mute, solo, arm, vel, patterns:{pid:{name,lenBars,notes}},
 *                           clips:[{bar, pid, bars?}], audio:[{t, libId, name, offset, len, gain}], mix? }],
 *               sections: [{name, bar, bars}], master:{vol, verb, delay} }
 *   Notes { t, d, n, v } in ticks at PPQ (96 per quarter) — same as seqgen.js / smf.js.
 *   mix (a device's strip, or an audio track's) = { vol, pan, mute, solo, sendA, sendB,
 *               fx?:   [{ id, type, on, params }]      insert chain, in order (daw_fx.js types)
 *               duck?: { source: stripId, amount, attack, release, thresh } }   sidechain ducking
 *   track.auto? = [{ target, points: [{t (ticks), v (0..1)}], on }]   automation lanes; targets:
 *               'strip.vol' | 'strip.pan' | 'strip.sendA' | 'strip.sendB'   the track's strip
 *               'fx.<fxId>.<param>'   an insert on the track's strip
 *               'dev.<path>'          ForgeSynth.setParam path (macro.N.value, master.gain, lane.X.gain)
 *               'cc.<n>'              MIDI CC n through the device's cc() on the track's channel
 *   track.autoOpen? — automation lanes shown under the track. Every new field is optional: old
 *   projects load and render exactly as before.
 *   PERF (daw_perf.js — its header has the full field list):
 *     track.perf?    { scale, chord, arp, onClips, seed, groove, nudge }   the live chain per track:
 *                    keys → scale lock → chord → arp → device; with onClips also the track's clip notes
 *     project.groove? { on, type: mpc16|shuffle8|triplet|flat, swing, roles{role: ms}, accent, accentDepth,
 *                    human{ms, vel, seed} }   replaces project.swing while on; absent / on:false → the old
 *                    swingDelay path, untouched (same device events as before PERF)
 *     note.p?        step probability 0..1, decided per occurrence from (track.perf.seed, track id, tick, note)
 *     pattern.steps? the STEP view's resolution (8|12|16|24|32), display only
 *   Live scheduleRange and renderOffline share _playCtx(track): the notes a pattern plays (PERF chain on
 *   clips), the groove and the probability gate — the same notes, times and velocities in both.
 *
 * Recording (all optional too):
 *   project.rec?   = { countIn: 0|1|2 (bars of click first), mode: 'replace'|'overdub'|'loop', quant: ticks (0 = off) }
 *                    'loop' = overdub loop: every pass of a MIDI loop recording goes into one take
 *   project.punch? = { on, a, b }  bars [a, b): only this is recorded (separate from the loop region)
 *   track.takes?   = [{ id, region: {a, b} (bars), kind: 'midi'|'audio', pid | audioRef: {libId, t (ticks), offset, len (s)},
 *                       name, at (ISO), pass, rec (recording id), active, layer?, latMs?, latFrom? }]
 *                    one ACTIVE take per (region, kind, layer); the active one is what the region's clip plays (MIDI: the
 *                    clip's pid; audio: a track.audio clip). An audio OVERDUB over a region that already has a take opens
 *                    a new layer (both play). track.takesOpen? — takes rows shown under the track.
 *   What a take covers: punch ∩ loop › loop region (one take per pass) › punch › "open" (playhead bar → stop).
 *   REPLACE splits the clips at the region edges and drops what was inside (MIDI clips that resume mid-pattern
 *   get a rotated copy of the pattern; audio clips are trimmed by offset / len); OVERDUB copies what was inside into
 *   every MIDI take (audio: layers). Notes struck up to a 1/16 before the record start land on it (count-in grace);
 *   with QUANT on, a note quantized onto a looping region's end goes to the next pass's downbeat. Nothing recorded →
 *   the track is restored exactly. Audio: ONE frame-stamped capture (RecCapture, worklet posts currentFrame) cut per
 *   pass at the region's scheduled start + latency, every full pass exactly the loop length, 5 ms fades at the cuts;
 *   one library item per pass (AK.lib kind 'daw-rec'). A recording is one undo step (the page snapshots on 'record-arm').
 *   API: startRecord() / stopRecord() · takeGroups(track) → [{key, region, kind, layer, takes, active}] ·
 *   pickTake(trackId, takeId) · cycleTake(trackId, groupKey, ±1) · deleteTake(trackId, takeId) ·
 *   keepOnlyActive(trackId, groupKey?) · recNow() · stampInput(perfMs) · calibrateLoopback({n, gap}) ·
 *   setLatency(kind, ms, src) · setLatencyUse('auto'|'fm1'|'input') · checkoutLatency(force) · audioComp() ·
 *   events: 'record-arm', 'record' {on}, 'takes', 'latency'. DAW.GRIDS = the grid / record-quantize values
 *   (1/32 12 · 1/16 24 · 1/8 48 · 1/4 96 · 1/16T 16 · 1/8T 32 ticks) shared with the piano roll.
 *
 * Latency — which compensation applies where. Every recorded position is put back on SCHEDULED context time
 * (timeOf(tick): when the transport scheduled that tick). Facts it rests on:
 *   • perfTime(T) is when context time T reaches the speakers (getOutputTimestamp); ctxAtPerf() is its inverse.
 *   • The master limiter (DynamicsCompressorNode) looks ahead: everything on the master is HEARD outDelay after it
 *     is scheduled (measured at start(); 264 samples = 6.0 ms in Chrome). The click bus and hardware MIDI
 *     (HwDevice._send) are delayed by the same amount, so music, click and the FM-1 are heard together at T + outDelay.
 *   • A take's input sample is stamped with the context frame it was processed in (RecCapture), the same clock
 *     FM-1 CHECK-OUT's onset probe uses.
 *   Hence three separate numbers (machine settings, localStorage 'mm_daw_latency' = {fm1, input, midi: {ms, src}, use}):
 *   1. FM-1 RETURN (lat.fm1, from CHECK-OUT's 'mm_fm1_latency_ms', or manual): audio of the FM-1 on its own USB
 *      audio input. CHECK-OUT measured: note-on scheduled at ctx T (perfTime) → onset on the input frame clock = synth
 *      + USB + output/input buffering. The DAW sends the note at T + outDelay, so an audio take is shifted back by
 *      fm1 + outDelay. The same holds when the performer plays the FM-1's KEYS along to the playback (they strike at
 *      the heard time T + outDelay; only the ~1 ms USB-MIDI leg differs), so it follows the INPUT, not who played.
 *   2. PLAY-ALONG INPUT (lat.input, from LOOPBACK CALIBRATE or manual): any other input — a performer playing along.
 *      They hear T at T + outDelay (+ output buffering), the sound comes back with the input's latency. The loopback
 *      clicks run through the same delayed click bus, so the measured number (onset − scheduled T) already holds
 *      outDelay + output + input latency and is used as it stands.
 *   3. MIDI NOTES (lat.midi, manual, normally 0): FM-1 keys / MIDI keyboard / computer keys. Each event carries its
 *      own time stamp (MIDIMessageEvent / KeyboardEvent .timeStamp, handed over by the page via stampInput()), mapped
 *      with ctxAtPerf() − outDelay, so no round-trip number applies at all; this is only a nudge for a slow controller.
 *   'auto' (lat.use) picks 1 when the input's label looks like the FM-1's USB audio (felucca / fm-1 / m-vave / x0x), else 2.
 *   E.latencyMs is kept as an alias of the number audio takes use (1 or 2), without outDelay.
 *
 * Strip: in → [inserts] → post (sidechain tap, pre-fader) → duck → pan → vol → on (mute/solo)
 *        → master + sendA (reverb bus) + sendB (delay bus). Built by _buildStrip() for live
 *        playback AND renderOffline(), so both sound the same; automation runs through
 *        _autoRange() in both (live: per look-ahead window, offline: the whole timeline).
 *
 * Device types (each exposes noteOn/noteOff/allOff/cc(/midi) + getState/setState):
 *   forge  ForgeSynth (forge_synth.js) — one patch
 *   kit    a drum kit: one ForgeSynth per GM drum note
 *   emu    an FM-1 firmware running in the browser (fm1_emu.js); tracks pick its MIDI channel
 *   hw     the real FM-1 (or anything) over Web MIDI; its USB audio can come back in on a strip
 *   basic  tiny built-in synth (used if forge_synth.js isn't loaded)
 *
 * Mixer API (the UI edits through these, then saves): addFx(stripId, type, params) → entry ·
 *   removeFx(stripId, fxId) (its lanes go too) · moveFx(stripId, fxId, ±1) · setFxParam(stripId, fxId, k, v) ·
 *   setDuck(stripId, {source, amount, attack, release, thresh} | null) · applyMix() re-syncs everything
 *   from the project (undo / redo just swap the JSON and call it).
 * Automation API: autoTargets(track) → [{target, label}] · autoValueLabel(track, target, v01) ·
 *   autoLanes() → the lanes that drive something · recordAuto(stripId, key, value) / recordAutoEnd(…)
 *   (a mixer slider moved while recording an armed track writes a lane, touch mode).
 *
 * PERF API: liveNote(trackId, n, vel, on) runs the track's chain when track.perf is on (perfActive(tr)) ·
 *   perfLive (DawPerf.Live, lazy) · perfReset(trackId) after a settings change · swingDelay(tick, tr?)
 *   (with a track and a groove on: that track's groove offset) ·
 *   perfRecord(tr, n, vel, on, when, {generated}) — THE RECORDING HOOK: every note the chain plays (what you
 *   hear) passes through it; `when` is the AudioContext time it sounds, generated = arp step (already on the
 *   grid, no latency correction). The default records via recordMidi; recording code may replace it.
 *
 * Timing: a 25 ms timer schedules 120 ms ahead in AudioContext time; Web
 * Audio devices get exact times, the emulator dispatches messages on time,
 * hardware MIDI goes out with performance-time stamps (+ outDelay, to sound with the limited master).
 */
(function (root) {
  "use strict";
  const PPQ = 96, BAR = PPQ * 4;
  const RATE = 44100;     // the FM-1 emulators run at the device rate
  const LOOKAHEAD = 0.12, TICK_MS = 25;
  // the shared tool scripts declare top-level classes/consts (script scope, not window) — look in both
  const G = {
    get ForgeSynth() { return typeof ForgeSynth !== 'undefined' ? ForgeSynth : root.ForgeSynth; },
    get FM1Emu() { return typeof FM1Emu !== 'undefined' ? FM1Emu : root.FM1Emu; },
    get MidiInput() { return typeof MidiInput !== 'undefined' ? MidiInput : root.MidiInput; },
    get SMF() { return typeof SMF !== 'undefined' ? SMF : root.SMF; },
    get PatchBank() { return typeof PatchBank !== 'undefined' ? PatchBank : root.PatchBank; },
    get DawFX() { return typeof DawFX !== 'undefined' ? DawFX : root.DawFX; },
    get DawPerf() { return typeof DawPerf !== 'undefined' ? DawPerf : root.DawPerf; },
  };

  // ── automation helpers ────────────────────────────────────────────
  const AUTO_STEP = 6;                 // discrete targets (insert params, device params, CCs): every 1/64 note
  const STRIP_RANGE = { vol: [0, 1.4], pan: [-1, 1], sendA: [0, 1], sendB: [0, 1] };   // = the mixer sliders
  const DEV_RANGES = [[/^macro\.[1-8]\.value$/, 0, 1], [/^master\.gain$/, 0, 1.5], [/^lane\.[ABC]\.gain$/, 0, 1.5]];
  const devRange = path => { for (const [rx, a, b] of DEV_RANGES) if (rx.test(path)) return [a, b]; return null; };
  // piecewise linear through the points, flat before the first and after the last
  function autoValueAt(pts, tick) {
    const n = pts.length; if (!n) return 0;
    if (tick <= pts[0].t) return pts[0].v;
    if (tick >= pts[n - 1].t) return pts[n - 1].v;
    let lo = 0, hi = n - 1;
    while (hi - lo > 1) { const m = (lo + hi) >> 1; if (pts[m].t <= tick) lo = m; else hi = m; }
    const a = pts[lo], b = pts[hi];
    return b.t === a.t ? b.v : a.v + (b.v - a.v) * (tick - a.t) / (b.t - a.t);
  }
  const sortedPts = pts => { for (let i = 1; i < pts.length; i++) if (pts[i].t < pts[i - 1].t) return pts.slice().sort((a, b) => a.t - b.t); return pts; };

  const KIT_MAP = {   // GM note → [forge preset, note to play it at, gain]
    35: ['kick', 36, 1], 36: ['kick', 36, 1], 37: ['perc_rim', 60, 0.9], 38: ['snare', 60, 1], 39: ['clap', 60, 1], 40: ['snare', 62, 0.9],
    41: ['tom', 43, 1], 42: ['hat_closed', 60, 0.8], 43: ['tom', 45, 1], 44: ['hat_closed', 58, 0.6], 45: ['tom', 48, 1], 46: ['hat_open', 60, 0.8],
    47: ['tom', 50, 1], 48: ['tom', 52, 1], 49: ['hat_open', 54, 0.9], 50: ['tom', 55, 1], 51: ['hat_closed', 66, 0.55], 56: ['perc_rim', 72, 0.7],
    70: ['hat_closed', 72, 0.4],
  };

  // ── tiny fallback synth (no forge_synth.js) ───────────────────────
  class BasicSynth {
    constructor(ctx, { output, drums } = {}) { this.ctx = ctx; this.output = ctx.createGain(); this.output.connect(output || ctx.destination); this.voices = new Map(); this.drums = !!drums; this.state = { wave: 'sawtooth', cutoff: 2400, rel: 0.25 }; }
    async init() {}
    noteOn(n, v = 0.8, when = this.ctx.currentTime) {
      const c = this.ctx; const g = c.createGain(); g.gain.value = 0; g.connect(this.output);
      if (this.drums) {
        const isKick = n <= 36 || n === 41 || n === 43 || n === 45, isHat = n === 42 || n === 46 || n === 44 || n === 51 || n === 70 || n === 49;
        if (isKick) { const o = c.createOscillator(); o.frequency.setValueAtTime(140, when); o.frequency.exponentialRampToValueAtTime(42, when + 0.12); o.connect(g); g.gain.setValueAtTime(v, when); g.gain.exponentialRampToValueAtTime(0.001, when + 0.35); o.start(when); o.stop(when + 0.4); }
        else { const b = c.createBuffer(1, c.sampleRate * 0.4, c.sampleRate), d = b.getChannelData(0); for (let i = 0; i < d.length; i++) d[i] = Math.random() * 2 - 1; const s = c.createBufferSource(); s.buffer = b; const f = c.createBiquadFilter(); f.type = isHat ? 'highpass' : 'bandpass'; f.frequency.value = isHat ? 7000 : 1800; s.connect(f); f.connect(g); g.gain.setValueAtTime(v * (isHat ? 0.5 : 0.9), when); g.gain.exponentialRampToValueAtTime(0.001, when + (n === 46 || n === 49 ? 0.35 : isHat ? 0.06 : 0.18)); s.start(when); s.stop(when + 0.4); }
        return;
      }
      const o = c.createOscillator(); o.type = this.state.wave; o.frequency.value = 440 * Math.pow(2, (n - 69) / 12);
      const f = c.createBiquadFilter(); f.frequency.value = this.state.cutoff; o.connect(f); f.connect(g);
      g.gain.setValueAtTime(0, when); g.gain.linearRampToValueAtTime(v * 0.3, when + 0.01);
      o.start(when);
      this.noteOff(n, undefined, undefined, true);
      this.voices.set(n, { o, g });
    }
    noteOff(n, when = this.ctx.currentTime, ch, immediate) {     // (n, when, channel) like every device: the channel used to land in `immediate` and cut each note at once
      const v = this.voices.get(n); if (!v) return; this.voices.delete(n);
      const t = immediate ? this.ctx.currentTime : when;
      v.g.gain.cancelScheduledValues(t); v.g.gain.setTargetAtTime(0, t, this.state.rel / 4); v.o.stop(t + this.state.rel * 2);
    }
    allOff(when) { for (const n of [...this.voices.keys()]) this.noteOff(n, when); }
    cc() {} pitchBend() {}
    getState() { return Object.assign({}, this.state); } setState(s) { Object.assign(this.state, s || {}); }
    dispose() { this.allOff(); this.output.disconnect(); }
  }

  // ── drum kit of FORGE voices ──────────────────────────────────────
  class KitDevice {
    constructor(ctx, { output }) { this.ctx = ctx; this.output = ctx.createGain(); this.output.connect(output); this.voices = {}; this.map = Object.assign({}, KIT_MAP); this.basic = null; }
    async init() {
      if (typeof G.ForgeSynth !== 'function') { this.basic = new BasicSynth(this.ctx, { output: this.output, drums: true }); return; }
      const presets = [...new Set(Object.values(this.map).map(m => m[0]))];
      for (const id of presets) {
        const s = new G.ForgeSynth(this.ctx, { output: this.output, maxVoices: 6 });
        await s.init();
        try { s.loadPreset(id); } catch (e) { /* missing preset → stays init */ }
        this.voices[id] = s;
      }
      this.measureHolds();
    }
    // how long to hold each one-shot: a decaying preset (sustain 0) rings out its attack+decay,
    // a sustaining one gets a short gate. Releasing early would cut the kick's tail.
    measureHolds() {
      this.hold = {};
      for (const [id, s] of Object.entries(this.voices)) {
        let a = null; try { a = s.getState().amp; } catch (e) {}
        this.hold[id] = a && a.s <= 0.01 ? Math.min(4, (a.a || 0) + (a.d || 0.3)) : 0.12;
      }
    }
    noteOn(n, v, when) {
      if (this.basic) return this.basic.noteOn(n, v, when);
      const m = this.map[n] || this.map[36 + ((n - 36) % 12 + 12) % 12] || ['perc_rim', 60, 0.8];
      const s = this.voices[m[0]]; if (!s) return;
      s.noteOn(m[1], Math.min(1, v * m[2]), when);
      s.noteOff(m[1], when + ((this.hold && this.hold[m[0]]) || 0.12));
    }
    noteOff() {}
    allOff(when) { if (this.basic) this.basic.allOff(when); for (const s of Object.values(this.voices)) s.allOff(when); }
    cc() {} pitchBend() {}
    getState() { return { map: this.map, voices: Object.fromEntries(Object.entries(this.voices).map(([k, s]) => [k, s.getState()])) }; }
    setState(st) {
      if (!st) return;
      if (st.map) this.map = st.map;
      if (st.voices) for (const [k, s] of Object.entries(st.voices)) if (this.voices[k]) this.voices[k].setState(s);
      this.measureHolds();
    }
    dispose() { for (const s of Object.values(this.voices)) s.dispose(); this.output.disconnect(); }
  }

  // ── an instrument from the PATCH BANK (patch_bank.js): sampler or DX7 ──
  // Loads in the background (first use downloads + caches); notes before it's ready are dropped.
  class PatchDevice {
    constructor(ctx, { output, engine, patch, devId }) { this.ctx = ctx; this.engine = engine; this.patch = patch; this.devId = devId; this.output = output; this.inner = null; this.pendingState = null; this.error = ''; }
    init() { this.ready = this._load(); }          // don't block project load on downloads; bounce() awaits .ready
    async _load() {
      const PB = G.PatchBank; if (!PB) { this.error = 'patch_bank.js not loaded'; return; }
      try {
        this.inner = await PB.createDevice(this.ctx, this.patch, { output: this.output, onProgress: p => this.engine.emit('device-progress', { id: this.devId, p }) });
        if (this.pendingState) { try { this.inner.setState(this.pendingState); } catch (e) {} this.pendingState = null; }
        if (this.bpmV !== undefined && 'bpm' in this.inner) this.inner.bpm = this.bpmV;
        this.engine.emit('device-progress', { id: this.devId, p: { phase: 'ready' } });
      } catch (e) { this.error = e.message || String(e); this.engine.emit('error', 'patch ' + this.patch + ': ' + this.error); }
    }
    get bpm() { return this.bpmV; } set bpm(v) { this.bpmV = v; if (this.inner && 'bpm' in this.inner) this.inner.bpm = v; }
    noteOn(n, v, when, ch) { if (this.inner) this.inner.noteOn(n, v, when, ch); }
    noteOff(n, when, ch) { if (this.inner) this.inner.noteOff(n, when, ch); }
    allOff(when) { if (this.inner) this.inner.allOff(when); }
    cc(num, v, when) { if (this.inner && this.inner.cc) this.inner.cc(num, v, when); }
    pitchBend(v, when) { if (this.inner && this.inner.pitchBend) this.inner.pitchBend(v, when); }
    get keymap() { return this.inner && this.inner.keymap; }
    getState() { return this.inner && this.inner.getState ? this.inner.getState() : this.pendingState; }
    setState(st) { if (this.inner) { try { this.inner.setState(st); } catch (e) {} } else this.pendingState = st; }
    mountEditor(el) { return this.inner && this.inner.mountEditor ? this.inner.mountEditor(el) : null; }
    dispose() { if (this.inner) { try { this.inner.dispose(); } catch (e) {} } }
  }

  // ── the real FM-1 over Web MIDI ───────────────────────────────────
  class HwDevice {
    constructor(ctx, { output, engine }) { this.ctx = ctx; this.engine = engine; this.output = ctx.createGain(); this.output.connect(output); this.held = new Set(); this.returnSrc = null; this.returnStream = null; this.returnDevice = ''; }
    async init() {}
    get mi() { return this.engine.midi; }
    _send(bytes, when) {
      const mi = this.mi; if (!mi || !mi.output) return;
      // + outDelay: heard together with the DAW's own synths, which reach the speakers through the master limiter
      try { mi.output.send(bytes, this.engine.perfTime((when ?? this.ctx.currentTime) + (this.engine.outDelay || 0))); } catch (e) { /* port gone */ }
    }
    noteOn(n, v, when, ch = 1) { this.held.add(ch * 128 + n); this._send([0x90 | ((ch - 1) & 15), n & 127, Math.max(1, Math.round(v * 127))], when); }
    noteOff(n, when, ch = 1) { this.held.delete(ch * 128 + n); this._send([0x80 | ((ch - 1) & 15), n & 127, 0], when); }
    allOff(when) { for (const k of this.held) this._send([0x80 | ((Math.floor(k / 128) - 1) & 15), k % 128, 0], when); this.held.clear(); for (let c = 0; c < 16; c++) this._send([0xB0 | c, 123, 0], when); }
    cc(num, v01, when, ch = 1) { this._send([0xB0 | ((ch - 1) & 15), num & 127, Math.round(v01 * 127)], when); }
    midi(bytes, when) { this._send(bytes, when); }
    // USB audio coming back from the synth (Felucca / SLOOP "Felucca" input, or any interface)
    async setReturn(deviceId) {
      if (this.returnSrc) { try { this.returnSrc.disconnect(); } catch (e) {} this.returnSrc = null; }
      if (this.returnStream) { this.returnStream.getTracks().forEach(t => t.stop()); this.returnStream = null; }
      this.returnDevice = deviceId || '';
      if (!deviceId) return;
      this.returnStream = await AK.inputs.open(deviceId === 'default' ? undefined : deviceId, 2);
      this.returnSrc = this.ctx.createMediaStreamSource(this.returnStream);
      this.returnSrc.connect(this.output);
    }
    getState() { return { returnDevice: this.returnDevice }; }
    setState(s) { if (s && s.returnDevice) this.setReturn(s.returnDevice).catch(() => {}); }
    dispose() { this.allOff(); this.setReturn(''); this.output.disconnect(); }
  }

  // ── recording helpers ─────────────────────────────────────────────
  // grid / record-quantize values in ticks (PPQ 96): the piano roll's GRID and the transport's QUANT share these
  const GRIDS = [{ v: 12, label: '1/32' }, { v: 24, label: '1/16' }, { v: 48, label: '1/8' }, { v: 96, label: '1/4' }, { v: 16, label: '1/16T' }, { v: 32, label: '1/8T' }];
  const REC_MODES = ['replace', 'overdub', 'loop'];       // 'loop' = overdub loop: every pass into one pattern
  const GRACE = PPQ / 4;          // a note struck up to a 1/16 before the record start lands on it
  const FADE_MS = 5;              // audio takes: fade in / out at the cut
  const LS_FM1 = 'mm_fm1_latency_ms', LS_LAT = 'mm_daw_latency';
  const FM1_INPUT_RX = /felucca|fm-?1|m-?vave|x0x/i;      // an input named like the FM-1's own USB audio
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  // Frame-stamped input capture: every render quantum's input with the context frame it belongs to
  // (currentFrame), so a take is cut on the same AudioContext clock the transport schedules on —
  // the same stamping FM-1 CHECK-OUT's onset probe uses, so its latency number means the same thing here.
  const REC_WORKLET = `
class MMDawRec extends AudioWorkletProcessor {
  constructor() { super(); this.on = true; this.port.onmessage = e => { if (e.data === 'stop') this.on = false; }; }
  process(inputs) {
    const inp = inputs[0];
    if (inp && inp.length && inp[0].length) { const ch = inp.map(c => c.slice(0)); this.port.postMessage({ f: currentFrame, ch }, ch.map(c => c.buffer)); }
    return this.on;
  }
}
registerProcessor('mm-daw-rec', MMDawRec);
`;
  class RecCapture {
    constructor(ctx, src, maxCh = 2) { this.ctx = ctx; this.src = src; this.maxCh = maxCh; this.chunks = []; this.node = null; this.sink = null; this.first = null; this.last = null; }
    async start() {
      const c = this.ctx;
      this.sink = c.createGain(); this.sink.gain.value = 0; this.sink.connect(c.destination);
      try {
        if (!c.__mmDawRec) { await AK.addWorklet(c, REC_WORKLET); c.__mmDawRec = true; }
        // 'speakers': a mono mic fills both channels instead of only the left
        this.node = new AudioWorkletNode(c, 'mm-daw-rec', { numberOfInputs: 1, numberOfOutputs: 1, outputChannelCount: [1], channelCount: this.maxCh, channelCountMode: 'explicit', channelInterpretation: 'speakers' });
        this.node.port.onmessage = e => this._push(e.data.f, e.data.ch);
      } catch (e) {     // ScriptProcessor fallback: block frames estimated from playbackTime (not sample exact)
        const sp = c.createScriptProcessor(1024, this.maxCh, 1);
        sp.onaudioprocess = ev => { const ib = ev.inputBuffer, ch = []; for (let i = 0; i < ib.numberOfChannels; i++) ch.push(ib.getChannelData(i).slice(0)); this._push(Math.round(ev.playbackTime * c.sampleRate) - ib.length, ch); };
        this.node = sp;
      }
      this.src.connect(this.node); this.node.connect(this.sink);
    }
    _push(f, ch) { if (!ch || !ch.length || !ch[0].length) return; if (this.first === null) this.first = f; this.chunks.push({ f, ch }); this.last = f + ch[0].length; }
    stop() {
      try { this.src.disconnect(this.node); } catch (e) {}
      if (this.node && this.node.port) { try { this.node.port.postMessage('stop'); } catch (e) {} }
      try { this.node.disconnect(); this.sink.disconnect(); } catch (e) {}
    }
    async until(frame, maxMs = 1500) { const end = performance.now() + maxMs; while ((this.last === null || this.last < frame) && performance.now() < end) await sleep(15); }
    _from(f0) { const C = this.chunks; let lo = 0, hi = C.length; while (lo < hi) { const m = (lo + hi) >> 1; if (C[m].f + C[m].ch[0].length <= f0) lo = m + 1; else hi = m; } return lo; }
    // frames [f0, f0 + n) on the context frame clock; zeros where nothing was captured
    slice(f0, n) {
      const nch = this.chunks.length ? this.chunks[0].ch.length : 1, out = [];
      for (let c = 0; c < nch; c++) out.push(new Float32Array(n));
      for (let i = this._from(f0); i < this.chunks.length; i++) {
        const k = this.chunks[i], len = k.ch[0].length; if (k.f >= f0 + n) break;
        const a = Math.max(f0, k.f), b = Math.min(f0 + n, k.f + len);
        for (let c = 0; c < nch; c++) out[c].set((k.ch[c] || k.ch[0]).subarray(a - k.f, b - k.f), a - f0);
      }
      return out;
    }
    _scan(f0, f1, fn) {
      for (let i = this._from(f0); i < this.chunks.length; i++) {
        const k = this.chunks[i], len = k.ch[0].length; if (k.f >= f1) break;
        for (let j = Math.max(0, f0 - k.f); j < len && k.f + j < f1; j++) { let m = 0; for (const c of k.ch) { const v = c[j] < 0 ? -c[j] : c[j]; if (v > m) m = v; } if (fn(k.f + j, m)) return; }
      }
    }
    peak(f0, f1) { let p = 0; this._scan(f0, f1, (f, m) => { if (m > p) p = m; }); return p; }
    firstAbove(f0, f1, thr) { let at = null; this._scan(f0, f1, (f, m) => { if (m > thr) { at = f; return true; } }); return at; }
  }
  function fadeEdges(chs, sr, ms) {
    const len = chs[0].length, n = Math.min(Math.round(ms / 1000 * sr), len >> 1);
    for (const c of chs) for (let i = 0; i < n; i++) { const g = 0.5 - 0.5 * Math.cos(Math.PI * i / n); c[i] *= g; c[len - 1 - i] *= g; }
  }
  const clone = o => JSON.parse(JSON.stringify(o));

  // ═══════════════════════════════════════════════════════════════════
  class Engine {
    constructor() {
      this.ctx = null; this.project = null; this.devices = new Map(); this.strips = new Map();
      this.playing = false; this.recording = false; this.anchor = null; this.schedTick = 0; this.timer = null;
      this.sources = []; this.midi = null; this.listeners = {}; this.inputStream = null; this.inputLabel = '';
      this.quantize = 24; this.rec = null; this._anchors = []; this._countIn = null; this._evIn = null; this.outDelay = 0;
      this.loadLatency();
      this.on('loop', () => this._pushAnchor());      // every loop wrap: a new pass for loop recording
    }
    on(ev, fn) { (this.listeners[ev] = this.listeners[ev] || []).push(fn); }
    // the master limiter's look-ahead, measured: an impulse through an identical DynamicsCompressorNode
    async _measureOutDelay() {
      try {
        const sr = this.ctx.sampleRate, off = new OfflineAudioContext(1, 2048, sr), b = off.createBuffer(1, 2048, sr); b.getChannelData(0)[16] = 0.5;
        const s = off.createBufferSource(); s.buffer = b;
        const lim = off.createDynamicsCompressor(); lim.threshold.value = -2; lim.knee.value = 0; lim.ratio.value = 20; lim.attack.value = 0.002; lim.release.value = 0.1;
        s.connect(lim); lim.connect(off.destination); s.start();
        const o = (await off.startRendering()).getChannelData(0); let pk = 0, at = 16;
        for (let i = 0; i < o.length; i++) { const v = Math.abs(o[i]); if (v > pk) { pk = v; at = i; } }
        return Math.max(0, at - 16) / sr;
      } catch (e) { return 0.006; }
    }
    emit(ev, d) { (this.listeners[ev] || []).forEach(f => { try { f(d); } catch (e) { console.error(e); } }); }

    async start() {
      if (this.ctx) { if (this.ctx.state === 'suspended') await this.ctx.resume(); return; }
      this.ctx = new (root.AudioContext || root.webkitAudioContext)({ sampleRate: RATE, latencyHint: 'interactive' });
      const c = this.ctx;
      this.master = c.createGain();
      this.limiter = c.createDynamicsCompressor(); this.limiter.threshold.value = -2; this.limiter.knee.value = 0; this.limiter.ratio.value = 20; this.limiter.attack.value = 0.002; this.limiter.release.value = 0.1;
      this.out = c.createGain();
      this.master.connect(this.limiter); this.limiter.connect(this.out); this.out.connect(c.destination);
      this.split = c.createChannelSplitter(2); this.out.connect(this.split);
      this.anL = c.createAnalyser(); this.anR = c.createAnalyser(); this.anL.fftSize = this.anR.fftSize = 1024;
      this.split.connect(this.anL, 0); this.split.connect(this.anR, 1);
      // send buses
      this.verbIn = c.createGain(); this.verb = c.createConvolver(); this.verbOut = c.createGain();
      this.verbIn.connect(this.verb); this.verb.connect(this.verbOut); this.verbOut.connect(this.master);
      this.delayIn = c.createGain(); this.delay = c.createDelay(4); this.delayFb = c.createGain(); this.delayTone = c.createBiquadFilter(); this.delayOut = c.createGain();
      this.delayTone.type = 'lowpass'; this.delayTone.frequency.value = 4200;
      this.delayIn.connect(this.delay); this.delay.connect(this.delayTone); this.delayTone.connect(this.delayFb); this.delayFb.connect(this.delay);
      this.delayTone.connect(this.delayOut); this.delayOut.connect(this.master);
      // the master limiter looks ahead: everything on the master is heard outDelay (~6 ms) after it is scheduled.
      // The click (never in a bounce) and hardware MIDI are delayed to match, so all of it lands together.
      this.outDelay = await this._measureOutDelay();
      this.click = c.createGain(); this.click.gain.value = 0.5;
      this.clickDelay = c.createDelay(0.1); this.clickDelay.delayTime.value = this.outDelay;
      this.click.connect(this.clickDelay); this.clickDelay.connect(c.destination);
      if (G.DawFX) await G.DawFX.prepare(c);       // insert / gate / duck worklets before any strip exists
      if (G.MidiInput) { this.midi = new G.MidiInput({ role: 'chords', autoIdentify: true }); this.midi.start().catch(() => {}); }
    }

    // ── project ─────────────────────────────────────────────────────
    static newProject() {
      return { v: 1, name: 'untitled', bpm: 96, swing: 0, key: 9, mode: 'minor', loop: { on: true, a: 0, b: 8 }, metro: false,
               devices: [], tracks: [], sections: [], master: { vol: 0.9, verbSize: 2.4, verbMix: 0.8, delayBeats: 0.75, delayFb: 0.35, delayMix: 0.7 }, gen: null };
    }
    uid(p) { return p + '_' + Math.random().toString(36).slice(2, 8); }
    async load(project) {
      await this.start();
      this.stop();
      for (const id of [...this.devices.keys()]) this.removeDeviceRuntime(id);
      for (const id of [...this.strips.keys()]) this.removeStrip(id);
      this.project = project;
      if (this._perf) this._perf.resetAll();
      this.quantize = project.rec && project.rec.quant != null ? +project.rec.quant || 0 : 24;
      for (const d of project.devices) await this.createDeviceRuntime(d);
      for (const t of project.tracks) if (t.kind === 'audio') this.ensureStrip(t.id, t.mix || (t.mix = this.defaultMix()));
      this.applyMaster(); this.applyMix();
      this.emit('project');
    }
    defaultMix() { return { vol: 0.8, pan: 0, mute: false, solo: false, sendA: 0.1, sendB: 0 }; }

    // ── devices ─────────────────────────────────────────────────────
    async addDevice(type, opts = {}) {
      const d = { id: this.uid('dev'), type, name: opts.name || type, emuId: opts.emuId, preset: opts.preset, patch: opts.patch, state: null, mix: this.defaultMix() };
      this.project.devices.push(d);
      await this.createDeviceRuntime(d);
      if (opts.preset) this.setPreset(d.id, opts.preset);
      this.applyMix(); this.emit('project');
      return d;
    }
    async createDeviceRuntime(d) {
      const strip = this.ensureStrip(d.id, d.mix || (d.mix = this.defaultMix()));
      let inst;
      if (d.type === 'forge' && typeof G.ForgeSynth === 'function') inst = new G.ForgeSynth(this.ctx, { output: strip.in, maxVoices: 12 });
      else if (d.type === 'kit') inst = new KitDevice(this.ctx, { output: strip.in });
      else if (d.type === 'emu' && typeof G.FM1Emu === 'function') inst = new G.FM1Emu(this.ctx, { id: d.emuId || 'felucca', output: strip.in });
      else if (d.type === 'hw') inst = new HwDevice(this.ctx, { output: strip.in, engine: this });
      else if (d.type === 'patch') inst = new PatchDevice(this.ctx, { output: strip.in, engine: this, patch: d.patch, devId: d.id });
      else inst = new BasicSynth(this.ctx, { output: strip.in });
      inst.__type = d.type;
      this.devices.set(d.id, inst);
      try { await inst.init(); } catch (e) { this.emit('error', d.name + ': ' + (e.message || e)); }
      if (d.state) { try { inst.setState(d.state); } catch (e) { /* older state */ } }
      else if (d.preset && inst.loadPreset) { try { inst.loadPreset(d.preset); } catch (e) {} }
      if (inst.bpm !== undefined || 'bpm' in inst) { try { inst.bpm = this.project.bpm; } catch (e) {} }
      return inst;
    }
    setPreset(devId, preset) {
      const inst = this.devices.get(devId), d = this.dev(devId);
      if (inst && inst.loadPreset) { try { inst.loadPreset(preset); d.preset = preset; d.state = null; } catch (e) { this.emit('error', 'preset ' + preset + ': ' + e.message); } }
    }
    removeDeviceRuntime(id) {
      const inst = this.devices.get(id); if (inst) { try { inst.dispose(); } catch (e) {} } this.devices.delete(id); this.removeStrip(id);
    }
    removeDevice(id) {
      this.removeDeviceRuntime(id);
      this.project.devices = this.project.devices.filter(d => d.id !== id);
      for (const t of this.project.tracks) if (t.deviceId === id) t.deviceId = null;
      this.emit('project');
    }
    dev(id) { return this.project.devices.find(d => d.id === id); }
    track(id) { return this.project.tracks.find(t => t.id === id); }
    snapshotStates() { for (const d of this.project.devices) { const inst = this.devices.get(d.id); if (inst && inst.getState) { try { d.state = inst.getState(); } catch (e) {} } } }

    // ── tracks ──────────────────────────────────────────────────────
    addTrack(kind, opts = {}) {
      const t = { id: this.uid('trk'), name: opts.name || (kind === 'audio' ? 'audio' : 'midi'), color: opts.color || '#d8a060', kind,
                  deviceId: opts.deviceId || null, channel: opts.channel || 1, mute: false, solo: false, arm: false, vel: 1,
                  patterns: {}, clips: [], audio: [], role: opts.role || '' };
      if (kind === 'audio') { t.mix = this.defaultMix(); this.ensureStrip(t.id, t.mix); }
      this.project.tracks.push(t); this.applyMix(); this.emit('project');
      return t;
    }
    removeTrack(id) {
      this.perfReset(id);
      this.project.tracks = this.project.tracks.filter(t => t.id !== id);
      this.removeStrip(id); this.emit('project');
    }
    songBars() {
      let end = 0;
      for (const t of this.project.tracks) {
        for (const c of t.clips) { const p = t.patterns[c.pid]; end = Math.max(end, c.bar + (c.bars || (p ? p.lenBars : 1))); }
        for (const a of t.audio) end = Math.max(end, Math.ceil((a.t + a.len / this.spt()) / BAR));
      }
      return Math.max(end, 1);
    }

    // ── mixer ───────────────────────────────────────────────────────
    // one builder for live strips and renderOffline()'s: in → inserts → post → duck → pan → vol → on → buses
    _buildStrip(c, mix, bus) {
      const s = { in: c.createGain(), post: c.createGain(), duck: c.createGain(), pan: c.createStereoPanner(), vol: c.createGain(), on: c.createGain(),
                  sendA: c.createGain(), sendB: c.createGain(), mix, fxUnits: new Map(), fxSig: '', duckNode: null, duckSrc: null };
      s.in.connect(s.post); s.post.connect(s.duck); s.duck.connect(s.pan); s.pan.connect(s.vol); s.vol.connect(s.on);
      s.on.connect(bus.master); s.on.connect(s.sendA); s.on.connect(s.sendB); s.sendA.connect(bus.verbIn); s.sendB.connect(bus.delayIn);
      s.pan.pan.value = mix.pan; s.vol.gain.value = mix.vol; s.sendA.gain.value = mix.sendA; s.sendB.gain.value = mix.sendB;
      return s;
    }
    // bring a strip's inserts in line with mix.fx: create / dispose units, relink on order or bypass
    // changes, push edited params (automation moves a unit's own copy, never the project's)
    _syncFx(c, s, mix, bpm, when) {
      const FX = G.DawFX; if (!FX) return;
      const list = (Array.isArray(mix.fx) ? mix.fx : []).filter(f => f && f.id && FX.spec(f.type));
      const want = new Map(list.map(f => [f.id, f]));
      for (const [id, u] of s.fxUnits) if (!want.has(id) || want.get(id).type !== u.type) { u.dispose(); s.fxUnits.delete(id); s.fxSig = '?'; }
      for (const f of list) if (!s.fxUnits.has(f.id)) {
        let u; try { u = FX.create(c, f, { bpm }); } catch (e) { this.emit('error', 'fx ' + f.type + ': ' + (e.message || e)); continue; }
        u.applied = Object.assign({}, u.params); s.fxUnits.set(f.id, u); s.fxSig = '?';
      }
      const sig = list.map(f => f.id + (f.on === false ? '-' : '+')).join(',');
      if (sig !== s.fxSig) {
        try { s.in.disconnect(); } catch (e) {}
        for (const u of s.fxUnits.values()) { try { u.output.disconnect(); } catch (e) {} }
        let node = s.in;
        for (const f of list) { const u = s.fxUnits.get(f.id); if (!u || f.on === false) continue; node.connect(u.input); node = u.output; }
        node.connect(s.post);
        s.fxSig = sig;
      }
      for (const f of list) {
        const u = s.fxUnits.get(f.id); if (!u) continue;
        const np = FX.normParams(f.type, f.params);
        for (const k in np) if (np[k] !== u.applied[k]) { u.set(k, np[k], when); u.applied[k] = np[k]; }
      }
    }
    // sidechain: the source strip's post-insert, pre-fader signal drives an envelope follower whose
    // output (1 − depth) is the target's duck gain. Tapping before the fader means a muted source still ducks.
    _syncDuck(c, strips, id, s, when) {
      const FX = G.DawFX, d = s.mix && s.mix.duck;
      const src = d && d.source && d.source !== id ? strips.get(d.source) : null;
      if (!src || !FX) {
        if (s.duckNode) { try { s.duckNode.port.postMessage('stop'); s.duckNode.disconnect(); if (s.duckSrc) s.duckSrc.post.disconnect(s.duckNode); } catch (e) {} s.duckNode = null; s.duckSrc = null; s.duck.gain.value = 1; }
        return;
      }
      if (!s.duckNode) {
        s.duckNode = FX.createDuck(c); if (!s.duckNode) return;
        s.duck.gain.value = 0; s.duckNode.connect(s.duck.gain);
      }
      if (s.duckSrc !== src) {
        if (s.duckSrc) { try { s.duckSrc.post.disconnect(s.duckNode); } catch (e) {} }
        src.post.connect(s.duckNode); s.duckSrc = src;
      }
      FX.setDuck(s.duckNode, d, when);
    }
    ensureStrip(id, mix) {
      if (this.strips.has(id)) return this.strips.get(id);
      const s = this._buildStrip(this.ctx, mix, { master: this.master, verbIn: this.verbIn, delayIn: this.delayIn });
      s.an = this.ctx.createAnalyser(); s.an.fftSize = 512; s.on.connect(s.an);
      this.strips.set(id, s);
      return s;
    }
    removeStrip(id) {
      const s = this.strips.get(id); if (!s) return;
      try { s.on.disconnect(); s.in.disconnect(); s.post.disconnect(); } catch (e) {}
      for (const u of s.fxUnits.values()) u.dispose();
      if (s.duckNode) { try { s.duckNode.port.postMessage('stop'); s.duckNode.disconnect(); } catch (e) {} }
      this.strips.delete(id);
      for (const [oid, o] of this.strips) if (o.duckSrc === s) { o.duckSrc = null; try { if (o.duckNode) { o.duckNode.port.postMessage('stop'); o.duckNode.disconnect(); } } catch (e) {} o.duckNode = null; o.duck.gain.value = 1; }
    }
    stripOwner(id) { return this.project ? (this.dev(id) || this.project.tracks.find(t => t.id === id && t.kind === 'audio')) : null; }
    stripOf(tr) { return tr ? (tr.kind === 'audio' ? tr.id : tr.deviceId) : null; }
    applyMix() {
      if (!this.ctx) return;
      const now = this.ctx.currentTime;
      // undo / redo swap mix objects in the project: follow them
      for (const [id, s] of this.strips) { const o = this.stripOwner(id); if (o && o.mix) s.mix = o.mix; }
      const mixes = [...this.strips.values()].map(s => s.mix);
      const anySolo = mixes.some(m => m && m.solo);
      const auto = this.playing ? this.autoParams() : new Set();   // automation owns these while playing
      for (const [id, s] of this.strips) {
        const m = s.mix; if (!m) continue;
        const on = !m.mute && (!anySolo || m.solo);
        s.on.gain.setTargetAtTime(on ? 1 : 0, now, 0.02);
        if (!auto.has(id + ':vol')) s.vol.gain.setTargetAtTime(m.vol, now, 0.02);
        if (!auto.has(id + ':pan')) s.pan.pan.setTargetAtTime(m.pan, now, 0.02);
        if (!auto.has(id + ':sendA')) s.sendA.gain.setTargetAtTime(m.sendA, now, 0.02);
        if (!auto.has(id + ':sendB')) s.sendB.gain.setTargetAtTime(m.sendB, now, 0.02);
        this._syncFx(this.ctx, s, m, this.project ? this.project.bpm : 120, now);
      }
      for (const [id, s] of this.strips) this._syncDuck(this.ctx, this.strips, id, s, now);
    }
    // ── FX chain edits (the UI calls these, then saves) ─────────────
    addFx(stripId, type, params) {
      const o = this.stripOwner(stripId), FX = G.DawFX; if (!o || !FX || !FX.spec(type)) return null;
      const f = { id: this.uid('fx'), type, on: true, params: FX.normParams(type, params) };
      (o.mix.fx = Array.isArray(o.mix.fx) ? o.mix.fx : []).push(f);
      this.applyMix(); return f;
    }
    removeFx(stripId, fxId) {
      const o = this.stripOwner(stripId); if (!o || !Array.isArray(o.mix.fx)) return;
      o.mix.fx = o.mix.fx.filter(f => f.id !== fxId);
      // its automation lanes go with it
      for (const t of this.project.tracks) if (Array.isArray(t.auto)) t.auto = t.auto.filter(l => !l.target.startsWith('fx.' + fxId + '.'));
      this.applyMix();
    }
    moveFx(stripId, fxId, delta) {
      const o = this.stripOwner(stripId); if (!o || !Array.isArray(o.mix.fx)) return;
      const a = o.mix.fx, i = a.findIndex(f => f.id === fxId), j = i + delta; if (i < 0 || j < 0 || j >= a.length) return;
      [a[i], a[j]] = [a[j], a[i]]; this.applyMix();
    }
    setFxParam(stripId, fxId, k, v) {
      const o = this.stripOwner(stripId), f = o && (o.mix.fx || []).find(x => x.id === fxId); if (!f) return;
      const sp = G.DawFX.spec(f.type); if (!sp || !sp[k]) return;
      f.params = f.params || {}; f.params[k] = G.DawFX.normField(v, sp[k]); this.applyMix();
    }
    setDuck(stripId, duck) {
      const o = this.stripOwner(stripId); if (!o) return;
      if (!duck || !duck.source) delete o.mix.duck;
      else o.mix.duck = Object.assign({}, G.DawFX ? G.DawFX.DUCK_DEF : {}, o.mix.duck || {}, duck);
      this.applyMix();
    }
    applyMaster() {
      const M = this.project.master, now = this.ctx.currentTime;
      this.out.gain.setTargetAtTime(M.vol, now, 0.02);
      if (this._verbSize !== M.verbSize) {
        const n = Math.round(this.ctx.sampleRate * M.verbSize), b = this.ctx.createBuffer(2, n, this.ctx.sampleRate);
        for (let ch = 0; ch < 2; ch++) { const d = b.getChannelData(ch); for (let i = 0; i < n; i++) d[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / n, 2.8); }
        this.verb.buffer = b; this._verbSize = M.verbSize;
      }
      this.verbOut.gain.setTargetAtTime(M.verbMix, now, 0.02);
      this.delay.delayTime.setTargetAtTime(Math.min(3.9, M.delayBeats * 60 / this.project.bpm), now, 0.05);
      this.delayFb.gain.setTargetAtTime(M.delayFb, now, 0.02);
      this.delayOut.gain.setTargetAtTime(M.delayMix, now, 0.02);
      for (const inst of this.devices.values()) {
        for (const x of [inst, ...Object.values(inst.voices || {})]) if (x && 'bpm' in x) { try { x.bpm = this.project.bpm; } catch (e) {} }
      }
      for (const st of this.strips.values()) for (const u of st.fxUnits.values()) u.bpm = this.project.bpm;
    }
    levels(id) {
      const s = id ? this.strips.get(id) : null;
      const read = an => { const b = new Float32Array(an.fftSize); an.getFloatTimeDomainData(b); let p = 0; for (const v of b) { const a = Math.abs(v); if (a > p) p = a; } return p; };
      return s ? read(s.an) : [read(this.anL), read(this.anR)];
    }

    // ── time ────────────────────────────────────────────────────────
    spt() { return 60 / (this.project.bpm * PPQ); }          // seconds per tick
    timeOf(tick) { return this.anchor.ctx + (tick - this.anchor.tick) * this.spt(); }
    tickNow() {
      if (!this.playing || !this.anchor) return this._stopTick || 0;
      let t = this.anchor.tick + (this.ctx.currentTime - this.anchor.ctx) / this.spt();
      return Math.max(this.anchor.tick, t);
    }
    perfTime(ctxTime) {
      const ts = this.ctx.getOutputTimestamp ? this.ctx.getOutputTimestamp() : null;
      if (ts && ts.performanceTime) return ts.performanceTime + (ctxTime - ts.contextTime) * 1000;
      return performance.now() + (ctxTime - this.ctx.currentTime) * 1000;
    }
    swingDelay(tick, tr) {
      if (tr && this.project.groove) { const g = this._groove(tr); if (g) return g.delay(tick); }   // a groove replaces the swing slider
      const s = this.project.swing || 0; if (!s) return 0;
      const pos = ((tick % (PPQ / 2)) + PPQ / 2) % (PPQ / 2);
      return Math.abs(pos - PPQ / 4) <= 2 ? s * (PPQ / 4) * 0.5 * this.spt() : 0;
    }
    // ── PERF: groove, clip chain, step probability (daw_perf.js) ────
    // project.groove (on) → { delay(tick), note(at, offTick, n, vel) → {on, off, v} } for this track; null → the
    // old swing path, untouched (a project without a groove feeds its devices exactly the events it did before PERF)
    _groove(tr) { const PF = G.DawPerf; return PF && this.project.groove ? PF.groove(this.project, tr, this.spt()) : null; }
    // per track, for one scheduling pass: the notes a pattern plays (the PERF chain when track.perf.onClips),
    // the groove, and the step-probability gate. Live scheduleRange and renderOffline both use it.
    _playCtx(tr) {
      const PF = G.DawPerf, P = this.project, clips = !!(PF && PF.clipsActive(tr.perf)), seed = (tr.perf && tr.perf.seed) || 1;
      return {
        groove: this._groove(tr),
        notes: p => (clips ? PF.clipNotes(p, tr.perf, P) : p.notes),
        plays: (base, n) => (PF ? PF.plays(seed, tr.id, base + (n.pt ?? n.t), n.pn ?? n.n, n.p) : true),
      };
    }

    // ── transport ───────────────────────────────────────────────────
    async play(fromTick) {
      await this.start();
      if (this.playing) this.stop();
      const P = this.project;
      const startTick = fromTick ?? (P.loop.on ? P.loop.a * BAR : 0);
      this.anchor = { ctx: this.ctx.currentTime + 0.08, tick: startTick };
      this._anchors = [{ ctx: this.anchor.ctx, tick: startTick, n: 0 }];     // + one per loop wrap (recording passes)
      this.schedTick = startTick;
      this.playing = true;
      this._auto = { fresh: true, cancel: this.ctx.currentTime, cache: new Map(), seen: new Set() };
      this._recAuto = new Map();
      this.sendClock('start', this.anchor.ctx);
      if (this._perf) this._perf.onPlay();
      this.syncDevices(this.anchor.ctx);
      this.startCovering(startTick, this.anchor.ctx);
      this.timer = setInterval(() => this.schedule(), TICK_MS);
      this.schedule();
      this.emit('transport', { playing: true });
    }
    // FORGE: restart tempo-synced LFOs / trance gates on the bar line
    syncDevices(when) {
      for (const inst of this.devices.values()) {
        if (inst.syncAt) { try { inst.syncAt(when); } catch (e) {} }
        if (inst.voices) for (const v of Object.values(inst.voices)) if (v.syncAt) { try { v.syncAt(when); } catch (e) {} }
      }
      for (const st of this.strips.values()) for (const u of st.fxUnits.values()) { try { u.sync(when); } catch (e) {} }   // trance gates on the bar
    }
    stop() {
      if (!this.ctx) return;
      if (this.recording) this.stopRecord();
      if (this.timer) { clearInterval(this.timer); this.timer = null; }
      const now = this.ctx.currentTime, wasPlaying = this.playing;
      if (this.playing) { this._stopTick = this.tickNow(); this.sendClock('stop', now); }
      this.playing = false;
      for (const inst of this.devices.values()) { try { inst.allOff(now); } catch (e) {} }
      for (const s of this.sources) { try { s.stop(now + 0.02); } catch (e) {} }
      this.sources = [];
      if (this._perf && wasPlaying) this._perf.onStop(now);     // held / latched arps free-run from here
      this._autoRelease(now);
      this.emit('transport', { playing: false });
    }
    schedule() {
      if (!this.playing) return;
      const P = this.project, horizon = this.ctx.currentTime + LOOKAHEAD;
      for (let guard = 0; guard < 8; guard++) {
        const byTime = this.anchor.tick + (horizon - this.anchor.ctx) / this.spt();
        if (byTime <= this.schedTick) return;
        const loopEnd = P.loop.on ? P.loop.b * BAR : Infinity;
        const songEnd = this.recording ? Infinity : this.songBars() * BAR;     // recording runs on past the song
        const limit = P.loop.on ? loopEnd : songEnd;
        const end = Math.min(byTime, limit);
        if (end > this.schedTick) this.scheduleRange(this.schedTick, end);
        this.schedTick = end;
        if (end < limit) return;
        if (P.loop.on) {
          const tWrap = this.timeOf(loopEnd);
          this.anchor = { ctx: tWrap, tick: P.loop.a * BAR };
          this.schedTick = P.loop.a * BAR;
          this.startCovering(this.schedTick, tWrap, true);
          this.syncDevices(tWrap);
          if (this._auto) this._auto.fresh = true;          // automation jumps back with the loop
          this.emit('loop', { at: tWrap });
        } else {
          const tEnd = this.timeOf(songEnd);
          setTimeout(() => { if (this.playing && this.ctx.currentTime >= tEnd - 0.01) { this.stop(); this.emit('ended'); } }, Math.max(0, (tEnd - this.ctx.currentTime) * 1000 + 30));
          return;
        }
      }
    }
    activeTracks() {
      const ts = this.project.tracks, anySolo = ts.some(t => t.solo);
      return ts.filter(t => !t.mute && (!anySolo || t.solo));
    }
    scheduleRange(t0, t1) {
      const P = this.project;
      for (const tr of this.activeTracks()) {
        if (tr.kind !== 'midi') continue;
        const inst = this.devices.get(tr.deviceId); if (!inst) continue;
        const pc = this._playCtx(tr), gr = pc.groove;
        for (const c of tr.clips) {
          const p = tr.patterns[c.pid]; if (!p || !p.notes.length) continue;
          const plen = p.lenBars * BAR, cs = c.bar * BAR, ce = cs + (c.bars || p.lenBars) * BAR;
          if (ce <= t0 || cs >= t1) continue;
          // windows are fractional ticks: "- 1" here dropped the notes on a loop start when the window after
          // the wrap was under one tick long
          const rep0 = Math.max(0, Math.floor((t0 - cs) / plen)), rep1 = Math.floor((Math.min(t1, ce) - cs - 1e-6) / plen);
          const notes = pc.notes(p);
          for (let r = rep0; r <= rep1; r++) {
            const base = cs + r * plen;
            for (const n of notes) {
              const at = base + n.t;
              if (at < t0 || at >= t1 || at >= ce) continue;
              if (n.p !== undefined && !pc.plays(base, n)) continue;          // step probability (seeded)
              let when, off, vel;
              if (!gr) {
                when = this.timeOf(at) + this.swingDelay(at);
                off = this.timeOf(Math.min(at + n.d, ce)) + this.swingDelay(at + n.d) - 0.002;
                vel = Math.max(0.02, Math.min(1, n.v * (tr.vel ?? 1)));
              } else {
                const offT = Math.min(at + n.d, ce), q = gr.note(at, offT, n.n, n.v * (tr.vel ?? 1));
                when = this.timeOf(at) + q.on; off = this.timeOf(offT) + q.off - 0.002; vel = q.v;
              }
              try { inst.noteOn(n.n, vel, when, tr.channel); inst.noteOff(n.n, Math.max(when + 0.005, off), tr.channel); } catch (e) { /* device mid-reload */ }
            }
          }
        }
      }
      for (const tr of this.activeTracks()) {
        if (tr.kind !== 'audio') continue;
        for (const a of tr.audio) if (a.t >= t0 && a.t < t1) this.startAudioClip(tr, a, this.timeOf(a.t), 0);
      }
      const ci = this._countIn;       // the count-in clicks even with the metronome off (first pass only: by time)
      if (ci && ci.endCtx == null) { ci.fromCtx = this.timeOf(ci.from); ci.endCtx = this.timeOf(ci.to); }
      if (P.metro || ci) for (let b = Math.ceil(t0 / PPQ) * PPQ; b < t1; b += PPQ) { const w = this.timeOf(b); if (P.metro || (w > ci.fromCtx - 1e-4 && w < ci.endCtx - 1e-4)) this.clickAt(w, b % BAR === 0); }
      this.clockRange(t0, t1);
      if (this._perf) this._perf.range(t0, t1);              // live arps on the transport grid
      if (this._auto) {
        const A = this._auto;
        this._autoRange({ live: true, timeOf: tk => this.timeOf(tk), strip: id => this.strips.get(id), inst: id => this.devices.get(id), cache: A.cache, seen: A.seen, fresh: A.fresh, cancel: A.cancel }, t0, t1);
        A.fresh = false; A.cancel = null;
      }
    }

    // ── automation ──────────────────────────────────────────────────
    // the lanes that drive something, first lane wins when two tracks share a strip / device param
    autoLanes() {
      const out = [], seen = new Set();
      for (const tr of this.project.tracks) for (const ln of (Array.isArray(tr.auto) ? tr.auto : [])) {
        if (!ln || ln.on === false || !Array.isArray(ln.points) || !ln.points.length || typeof ln.target !== 'string') continue;
        const m = /^(strip|fx|dev|cc)\.(.+)$/.exec(ln.target); if (!m) continue;
        const sid = this.stripOf(tr); if (!sid) continue;
        const d = { tr, lane: ln, sid, kind: m[1] };
        if (d.kind === 'strip') { if (!STRIP_RANGE[m[2]]) continue; d.key = m[2]; }
        else if (d.kind === 'fx') { const i = m[2].indexOf('.'); if (i < 1) continue; d.fxId = m[2].slice(0, i); d.key = m[2].slice(i + 1); }
        else if (d.kind === 'dev') { if (tr.kind !== 'midi' || !devRange(m[2])) continue; d.key = m[2]; }
        else { d.cc = parseInt(m[2], 10); if (!(d.cc >= 0 && d.cc < 128) || tr.kind !== 'midi') continue; d.key = d.cc + '@' + tr.channel; }
        const key = d.kind + ':' + sid + ':' + (d.fxId || '') + ':' + d.key;
        if (seen.has(key)) continue; seen.add(key); d.id = key;
        out.push(d);
      }
      return out;
    }
    autoParams() { return new Set(this.autoLanes().filter(d => d.kind === 'strip').map(d => d.sid + ':' + d.key)); }
    // what a lane can point at, for the UI: [{target, label}]
    autoTargets(tr) {
      const out = [], sid = this.stripOf(tr), own = sid && this.stripOwner(sid);
      if (!own) return out;
      out.push({ target: 'strip.vol', label: 'volume' }, { target: 'strip.pan', label: 'pan' }, { target: 'strip.sendA', label: 'send A · reverb' }, { target: 'strip.sendB', label: 'send B · delay' });
      const FX = G.DawFX;
      if (FX) for (const f of own.mix.fx || []) for (const k of FX.auto(f.type)) { const sp = FX.spec(f.type)[k]; if (sp) out.push({ target: 'fx.' + f.id + '.' + k, label: FX.label(f.type) + ' · ' + (sp.label || k).toLowerCase() }); }
      if (tr.kind === 'midi') {
        const inst = this.devices.get(tr.deviceId);
        if (inst && inst.setParam && inst.__type === 'forge') {
          let st = null; try { st = inst.getState(); } catch (e) {}
          for (let i = 1; i <= 8; i++) out.push({ target: 'dev.macro.' + i + '.value', label: 'macro ' + i + (st && st.macros && st.macros[i - 1] ? ' · ' + st.macros[i - 1].name.toLowerCase() : '') });
          out.push({ target: 'dev.master.gain', label: 'synth master' });
          for (const L of ['A', 'B', 'C']) out.push({ target: 'dev.lane.' + L + '.gain', label: 'synth lane ' + L });
        }
        for (const [n, nm] of [[1, 'mod wheel'], [7, 'volume'], [10, 'pan'], [11, 'expression'], [71, 'resonance'], [74, 'cutoff'], [91, 'reverb'], [93, 'chorus']]) out.push({ target: 'cc.' + n, label: 'CC ' + n + ' · ' + nm });
      }
      return out;
    }
    // a lane's 0..1 as the value it sets, for labels
    autoValueLabel(tr, target, v) {
      let m = /^strip\.(\w+)$/.exec(target);
      if (m && STRIP_RANGE[m[1]]) { const R = STRIP_RANGE[m[1]], x = R[0] + (R[1] - R[0]) * v; return m[1] === 'pan' ? (Math.abs(x) < 0.01 ? 'C' : (x < 0 ? 'L' : 'R') + Math.round(Math.abs(x) * 100)) : x.toFixed(2); }
      if ((m = /^fx\.([^.]+)\.(\w+)$/.exec(target))) {
        const own = this.stripOwner(this.stripOf(tr)), f = own && (own.mix.fx || []).find(x => x.id === m[1]), sp = f && G.DawFX && G.DawFX.spec(f.type)[m[2]];
        if (sp) {
          const x = G.DawFX.toValue(sp, v);
          if (typeof x !== 'number') return String(x);
          if (sp.unit === '%') return Math.round(x * 100) + '%';
          if (sp.unit === 'Hz' && x >= 1000) return (x / 1000).toFixed(2) + ' kHz';
          return (Math.abs(x) >= 100 ? Math.round(x) : +x.toFixed(Math.abs(x) < 1 ? 3 : 2)) + (sp.unit ? ' ' + sp.unit : '');
        }
      }
      if ((m = /^dev\.(.+)$/.exec(target))) { const R = devRange(m[1]); if (R) return (R[0] + (R[1] - R[0]) * v).toFixed(2); }
      if (/^cc\./.test(target)) return String(Math.round(v * 127));
      return v.toFixed(2);
    }
    // schedule every lane over [t0, t1) ticks. env: { timeOf, strip(id), inst(id), cache, seen, fresh, cancel }
    // AudioParams (strip vol / pan / sends) get exact breakpoints + a ramp to the window end, so contiguous
    // windows draw one continuous line. Inserts, device params and CCs are discrete calls on a 1/64 grid.
    _autoRange(env, t0, t1) {
      const FX = G.DawFX;
      for (const d of this.autoLanes()) {
        const pts = sortedPts(d.lane.points), rec = env.live && this.recording && this._recAuto ? this._recAuto.get(d.tr.id + ':' + d.lane.target) : null;
        const val = rec ? (tk => tk >= rec.tick ? rec.v : autoValueAt(pts, tk)) : (tk => autoValueAt(pts, tk));   // a slider being written holds its value
        const fresh = env.fresh || !env.seen.has(d.id); env.seen.add(d.id);
        if (d.kind === 'strip') {
          const s = env.strip(d.sid); if (!s) continue;
          const prm = d.key === 'vol' ? s.vol.gain : d.key === 'pan' ? s.pan.pan : d.key === 'sendA' ? s.sendA.gain : s.sendB.gain;
          const R = STRIP_RANGE[d.key], map = v => R[0] + (R[1] - R[0]) * v;
          if (fresh) {
            if (env.cancel != null) { if (prm.cancelAndHoldAtTime) prm.cancelAndHoldAtTime(env.cancel); else prm.cancelScheduledValues(env.cancel); }
            prm.setValueAtTime(map(val(t0)), Math.max(0, env.timeOf(t0)));
          }
          for (const p of pts) if (p.t > t0 && p.t < t1) prm.linearRampToValueAtTime(map(p.v), env.timeOf(p.t));
          prm.linearRampToValueAtTime(map(val(t1)), env.timeOf(t1));
          continue;
        }
        let call = null;
        if (d.kind === 'fx') {
          const s = env.strip(d.sid), u = s && s.fxUnits.get(d.fxId), sp = u && FX && FX.spec(u.type)[d.key];
          if (!sp || !FX.auto(u.type).includes(d.key)) continue;
          call = (v, w) => u.set(d.key, FX.toValue(sp, v), w);
        } else if (d.kind === 'dev') {
          const inst = env.inst(d.sid); if (!inst || typeof inst.setParam !== 'function') continue;
          const R = devRange(d.key); call = (v, w) => inst.setParam(d.key, R[0] + (R[1] - R[0]) * v, w);
        } else {
          const inst = env.inst(d.sid); if (!inst || typeof inst.cc !== 'function') continue;
          call = (v, w) => inst.cc(d.cc, v, w, d.tr.channel);
        }
        let last = fresh ? undefined : env.cache.get(d.id);
        const emit = tk => {
          let v = val(tk); if (d.kind === 'cc') v = Math.round(v * 127) / 127;
          if (last !== undefined && Math.abs(v - last) < 1e-4) return;
          last = v;
          try { call(v, Math.max(0, env.timeOf(tk))); } catch (e) { /* device mid-reload */ }
        };
        if (fresh) emit(t0);
        for (let k = Math.ceil(t0 / AUTO_STEP) * AUTO_STEP; k < t1; k += AUTO_STEP) if (k > t0 || !fresh) emit(k);
        env.cache.set(d.id, last);
      }
    }
    // transport stopped: hand the strips back to the mixer and the inserts back to their knobs
    _autoRelease(now) {
      if (!this._auto) return;
      this._auto = null;
      for (const s of this.strips.values()) {
        for (const prm of [s.vol.gain, s.pan.pan, s.sendA.gain, s.sendB.gain]) { if (prm.cancelAndHoldAtTime) prm.cancelAndHoldAtTime(now); else prm.cancelScheduledValues(now); }
        for (const u of s.fxUnits.values()) for (const k in u.applied) if (u.params[k] !== u.applied[k]) u.set(k, u.applied[k], now);
      }
      this.applyMix();
    }
    // writing automation: a mixer slider moved while recording, on an armed track that plays through this strip
    recordAuto(stripId, key, value) {
      if (!this.recording || !this.playing || !STRIP_RANGE[key]) return false;
      const R = STRIP_RANGE[key], v = Math.max(0, Math.min(1, (value - R[0]) / (R[1] - R[0]))), tick = Math.round(this.tickNow());
      let wrote = false, created = false;
      for (const tr of this.project.tracks) {
        if (!tr.arm || this.stripOf(tr) !== stripId) continue;
        const target = 'strip.' + key;
        tr.auto = Array.isArray(tr.auto) ? tr.auto : [];
        let ln = tr.auto.find(l => l.target === target);
        if (!ln) { ln = { target, points: [], on: true }; tr.auto.push(ln); tr.autoOpen = true; created = true; }
        const rk = tr.id + ':' + target, prev = this._recAuto && this._recAuto.get(rk), from = prev && prev.tick <= tick ? prev.tick : tick - 1;   // (a loop wrap restarts the pass)
        // touch mode: what was under the pass we just made is replaced
        ln.points = ln.points.filter(p => !(p.t > Math.min(from, tick) && p.t <= Math.max(from, tick)));
        ln.points.push({ t: tick, v: +v.toFixed(4) }); ln.points.sort((a, b) => a.t - b.t);
        if (this._recAuto) this._recAuto.set(rk, { tick, v });      // held (latched) until the slider is let go
        wrote = true;
      }
      if (wrote) this.emit('auto', { stripId, key, created });
      return wrote;
    }
    // the slider was let go: playback follows the lane again from here (touch mode)
    recordAutoEnd(stripId, key) {
      if (!this._recAuto) return;
      for (const tr of this.project.tracks) if (this.stripOf(tr) === stripId) this._recAuto.delete(tr.id + ':strip.' + key);
    }
    // audio clips already sounding at a (re)start point
    startCovering(tick, when, loopWrap) {
      for (const tr of this.activeTracks()) {
        if (tr.kind !== 'audio') continue;
        for (const a of tr.audio) {
          const lenT = a.len / this.spt();
          if (a.t < tick && a.t + lenT > tick) this.startAudioClip(tr, a, when, (tick - a.t) * this.spt());
          else if (loopWrap && a.t === tick) { /* scheduleRange starts it */ }
        }
      }
    }
    async startAudioClip(tr, a, when, offsetSec) {
      const buf = await this.clipBuffer(a); if (!buf || !this.playing) return;
      const s = this.ctx.createBufferSource(); s.buffer = buf;
      const g = this.ctx.createGain(); g.gain.value = a.gain ?? 1;
      s.connect(g); g.connect(this.strips.get(tr.id).in);
      const off = (a.offset || 0) + offsetSec, dur = Math.max(0.01, a.len - offsetSec);
      try { s.start(Math.max(when, this.ctx.currentTime), off, dur); } catch (e) { return; }
      this.sources.push(s);
      s.onended = () => { this.sources = this.sources.filter(x => x !== s); };
      // a loop-region end cuts it
      if (this.project.loop.on) { const le = this.timeOf(this.project.loop.b * BAR); if (le > when) try { s.stop(le); } catch (e) {} }
    }
    async clipBuffer(a) {
      this._bufCache = this._bufCache || new Map();
      if (this._bufCache.has(a.libId)) return this._bufCache.get(a.libId);
      const meta = await AK.lib.meta(a.libId), chs = await AK.lib.pcm(a.libId);
      if (!chs || !meta) return null;
      const off = new OfflineAudioContext(chs.length, Math.ceil(chs[0].length * RATE / meta.sampleRate), RATE);
      const src = off.createBufferSource(); src.buffer = AK.util.toBuffer(off, chs, meta.sampleRate); src.connect(off.destination); src.start();
      const buf = meta.sampleRate === RATE ? AK.util.toBuffer(this.ctx, chs, RATE) : await off.startRendering();
      this._bufCache.set(a.libId, buf);
      return buf;
    }
    clickAt(when, hi) {
      const o = this.ctx.createOscillator(), g = this.ctx.createGain();
      o.frequency.value = hi ? 1760 : 1100; g.gain.setValueAtTime(0.4, when); g.gain.exponentialRampToValueAtTime(0.001, when + 0.05);
      o.connect(g); g.connect(this.click); o.start(when); o.stop(when + 0.06);
    }

    // ── MIDI clock to devices that follow (emu, hw) ──────────────────
    clockTargets() { return this.project.devices.filter(d => d.clock && (d.type === 'emu' || d.type === 'hw')).map(d => this.devices.get(d.id)).filter(Boolean); }
    sendClock(what, when) {
      const tg = this.clockTargets(); if (!tg.length) return;
      const b = what === 'start' ? [0xFA] : [0xFC];
      for (const inst of tg) { try { inst.midi(b, when); } catch (e) {} }
    }
    clockRange(t0, t1) {
      const tg = this.clockTargets(); if (!tg.length) return;
      const step = PPQ / 24;
      for (let k = Math.ceil(t0 / step) * step; k < t1; k += step) { const w = this.timeOf(k); for (const inst of tg) { try { inst.midi([0xF8], w); } catch (e) {} } }
    }

    // ── live play + MIDI recording ──────────────────────────────────
    liveNote(trackId, note, vel, on) {
      const tr = this.track(trackId); if (!tr || tr.kind !== 'midi') return;
      const inst = this.devices.get(tr.deviceId); if (!inst) return;
      const now = this.ctx.currentTime;
      if (this.perfActive(tr)) { this.perfLive.input(tr, note, vel, on, now); return; }   // scale lock → chord → arp → device
      if (on) inst.noteOn(note, vel, now, tr.channel); else inst.noteOff(note, now, tr.channel);
      if (this.recording && this.playing && tr.arm) this.recordMidi(tr, note, vel, on, this.recNow());
    }

    // ── recording latency ───────────────────────────────────────────
    // Three numbers, because three different paths are being lined up (see the header):
    //   fm1   audio from the FM-1's own USB audio input: MIDI out (or its keys) → synth → USB audio in
    //   input audio from any other input: a performer playing along to playback (output + input latency)
    //   midi  extra nudge for MIDI notes, which are already placed by their own event time stamps
    // Machine settings, not project ones: kept in localStorage 'mm_daw_latency'.
    loadLatency() {
      const L = this.lat = { fm1: { ms: 30, src: 'default' }, input: { ms: 30, src: 'default' }, midi: { ms: 0, src: 'default' }, use: 'auto' };
      let saved = null; try { saved = JSON.parse(root.localStorage.getItem(LS_LAT) || 'null'); } catch (e) { /* blocked / bad JSON */ }
      if (saved && typeof saved === 'object') {
        for (const k of ['fm1', 'input', 'midi']) if (saved[k] && Number.isFinite(+saved[k].ms)) L[k] = { ms: +saved[k].ms, src: String(saved[k].src || 'manual') };
        if (['auto', 'fm1', 'input'].includes(saved.use)) L.use = saved.use;
      }
      this.checkoutLatency();
      return L;
    }
    // FM-1 CHECK-OUT's measured median round trip (localStorage 'mm_fm1_latency_ms'); a manual value wins unless forced
    checkoutLatency(force) {
      let v = NaN; try { v = parseFloat(root.localStorage.getItem(LS_FM1)); } catch (e) {}
      if (!(v >= 0 && v < 1000)) return null;
      if (force || this.lat.fm1.src !== 'manual') this.lat.fm1 = { ms: Math.round(v * 10) / 10, src: 'checkout' };
      return v;
    }
    saveLatency() { try { root.localStorage.setItem(LS_LAT, JSON.stringify(this.lat)); } catch (e) {} }
    setLatency(kind, ms, src = 'manual') {
      if (!['fm1', 'input', 'midi'].includes(kind)) return;
      const v = Math.max(kind === 'midi' ? -100 : 0, Math.min(500, +ms || 0));
      this.lat[kind] = { ms: Math.round(v * 10) / 10, src };
      this.saveLatency(); this.emit('latency', this.lat);
    }
    setLatencyUse(use) { if (['auto', 'fm1', 'input'].includes(use)) { this.lat.use = use; this.saveLatency(); this.emit('latency', this.lat); } }
    // which audio number an audio take uses: the FM-1's when the input is the FM-1's USB audio
    audioLatencyKind() { const u = this.lat.use; return u === 'fm1' || u === 'input' ? u : FM1_INPUT_RX.test(this.inputLabel || '') ? 'fm1' : 'input'; }
    // what an audio take is shifted by: the FM-1 number + the master look-ahead (the DAW sends its MIDI that much
    // late, see HwDevice._send; CHECK-OUT has no limiter), or the play-along number as it stands (the loopback
    // clicks go through the same delayed click bus, so the look-ahead is already inside it)
    audioComp() {
      const kind = this.audioLatencyKind(), ms = this.lat[kind].ms, extra = kind === 'fm1' ? Math.round((this.outDelay || 0) * 1e5) / 100 : 0;
      return { kind, ms, extra, total: ms + extra };
    }
    get latencyMs() { return this.lat[this.audioLatencyKind()].ms; }
    set latencyMs(v) { this.setLatency(this.audioLatencyKind(), v); }

    // ── input time stamps ───────────────────────────────────────────
    // performance time → the context time that was AUDIBLE then (inverse of perfTime): what a performer
    // heard when they struck the note. MIDI / key events carry their own stamp, so handler delays drop out.
    ctxAtPerf(perf) {
      const ts = this.ctx.getOutputTimestamp ? this.ctx.getOutputTimestamp() : null;
      if (ts && ts.performanceTime) return ts.contextTime + (perf - ts.performanceTime) / 1000;
      return this.ctx.currentTime + (perf - performance.now()) / 1000;
    }
    // the page stamps each MIDI / key event before it reaches liveNote (window listeners, capture phase)
    stampInput(perf) { if (Number.isFinite(perf)) this._evIn = { perf, at: performance.now() }; }
    // when "now" is for a recorded note: the current input event's own stamp if one was just set
    // (same dispatch), else the present; minus the MIDI nudge
    recNow() {
      const now = performance.now(), ev = this._evIn;
      const perf = ev && now - ev.at < 20 && ev.perf <= now + 1 && now - ev.perf < 1000 ? ev.perf : now;
      return this.ctxAtPerf(perf) - (this.outDelay || 0) - this.lat.midi.ms / 1000;
    }

    // ── recording: settings, region, passes ─────────────────────────
    recCfg() {
      const R = (this.project && this.project.rec) || {};
      return { countIn: Math.max(0, Math.min(2, R.countIn | 0)), mode: REC_MODES.includes(R.mode) ? R.mode : 'replace' };
    }
    punchOn() { const u = this.project && this.project.punch; return !!(u && u.on && u.b > u.a); }
    // what a take covers: the punch region, else the loop region (passes), else open (from the playhead to stop)
    recRegion() {
      const P = this.project, L = P.loop, pu = this.punchOn() ? P.punch : null;
      if (L.on) {
        if (pu) { const a = Math.max(pu.a, L.a), b = Math.min(pu.b, L.b); if (b <= a) return { error: 'the punch region is outside the loop' }; return { a, b, loop: true, punch: true }; }
        return { a: L.a, b: L.b, loop: true };
      }
      if (pu) return { a: pu.a, b: pu.b, punch: true };
      return { a: null, b: null };
    }
    _pushAnchor() {
      const A = this._anchors, n = A.length ? A[A.length - 1].n + 1 : 0;
      A.push({ ctx: this.anchor.ctx, tick: this.anchor.tick, n });
      if (A.length > 256) A.splice(0, A.length - 256);
      const R = this.rec;
      if (R && R.loop && this.recording && n - R.n0 > 0) {     // a new pass: MIDI takes switch to a fresh pattern before it plays
        for (const rt of R.tracks.values()) if (rt.kind === 'midi' && !rt.accum) this._recPass(rt, n - R.n0);
        this.emit('takes', { recording: true });
      }
    }
    // the anchor (transport segment) in effect at a context time; anchors move ~120 ms before a wrap sounds
    _anchorAt(when) { const A = this._anchors; for (let i = A.length - 1; i >= 0; i--) if (A[i].ctx <= when + 1e-9) return A[i]; return A[0] || { ctx: this.anchor.ctx, tick: this.anchor.tick, n: 0 }; }
    // where a note struck at context time `when` goes: { p (pass), rel (ticks from the region start) } or null
    _recPos(when) {
      const R = this.rec, spt = this.spt();
      if (when < R.liveCtx - GRACE * spt - 1e-6) return null;
      const an = this._anchorAt(when), tick = an.tick + (when - an.ctx) / spt;
      let p = R.loop ? an.n - R.n0 : 0, rel = tick - R.a * BAR;
      if (rel < 0) { if (rel >= -GRACE - 1e-6) rel = 0; else return null; }        // count-in / pre-roll grace
      const q = this.quantize; rel = q ? Math.round(rel / q) * q : Math.round(rel);
      if (R.b != null) {
        const len = (R.b - R.a) * BAR;
        if (rel >= len) { if (R.wraps && rel - len < len) { p += 1; rel -= len; } else return null; }   // quantized onto the next pass's downbeat
      }
      if (p < 0) return null;
      return { p, rel, raw: tick };
    }
    // ── PERF live chain (daw_perf.js) ───────────────────────────────
    get perfLive() { if (!this._perf && G.DawPerf) this._perf = new G.DawPerf.Live(this); return this._perf || null; }
    perfActive(tr) { const PF = G.DawPerf; return !!(PF && tr && (PF.active(tr.perf) || (this._perf && this._perf.learning(tr.id)))); }
    perfReset(trackId) { if (this._perf) this._perf.reset(trackId); }
    // THE RECORDING HOOK. Every note the PERF chain plays — what you hear — comes through here:
    //   tr, n, vel (0 on note-off), on, when = the AudioContext time it sounds,
    //   info.generated = true for arp steps (already on the grid: recorded at `when` as scheduled),
    //                    false for notes that follow the player's key (scale lock / chord): recNow(), the same
    //                    event-stamp timing a raw MIDI note gets (latencyMs is the AUDIO round trip — never for MIDI).
    // The chain runs inside the input event's dispatch, so recNow() still sees that event's stamp.
    perfRecord(tr, n, vel, on, when, info) {
      if (this.recording && this.playing && tr.arm) this.recordMidi(tr, n, vel, on, info && info.generated ? when : this.recNow());
    }
    recordMidi(tr, note, vel, on, when) {
      const R = this.rec, rt = R && R.tracks.get(tr.id); if (!rt || rt.kind !== 'midi') return;
      if (on) { const pos = this._recPos(when); rt.last = pos; if (pos) rt.open.set(note, Object.assign(pos, { whenOn: when, vel })); return; }
      const o = rt.open.get(note); if (!o) return; rt.open.delete(note);
      this._recCommit(rt, note, o, when);
    }
    _recCommit(rt, note, o, whenOff) {
      const R = this.rec, ps = this._recPass(rt, o.p), pat = rt.tr.patterns[ps.pid];
      let d = Math.max(6, Math.round((whenOff - o.whenOn) / this.spt()));
      if (R.b != null) d = Math.max(1, Math.min(d, (R.b - R.a) * BAR - o.rel));
      else pat.lenBars = Math.max(pat.lenBars, Math.ceil((o.rel + d) / BAR));
      const n = { t: o.rel, d, n: note, v: Math.max(0.02, Math.min(1, o.vel)) };
      pat.notes.push(n); pat.notes.sort((x, y) => x.t - y.t);
      ps.notes.push(n);
      this.emit('notes', { trackId: rt.tr.id, pid: ps.pid });
    }
    // the take (pattern) a pass records into — created on demand and made the active take of its region
    _recPass(rt, p) {
      const R = this.rec, tr = rt.tr; if (rt.accum) p = 0;
      if (rt.passes.has(p)) return rt.passes.get(p);
      const closed = R.b != null, lenBars = closed ? R.b - R.a : 1, pid = this.uid('rec');
      tr.patterns[pid] = { name: '', lenBars, notes: rt.base.map(n => Object.assign({}, n)) };
      tr.takes = Array.isArray(tr.takes) ? tr.takes : [];
      const k = { id: this.uid('take'), region: { a: R.a, b: R.a + lenBars }, kind: 'midi', pid, name: '', at: R.at, pass: p, rec: R.id, active: false };
      k.name = tr.patterns[pid].name = 'take ' + (this._group(tr, k).length + 1) + (rt.accum ? ' · loop' : '');
      tr.takes.push(k);
      if (closed) this._activate(tr, k);
      else { tr.clips.push({ bar: R.a, pid }); k.active = true; }    // open: the clip grows with the pattern
      const ps = { pid, take: k, notes: [] }; rt.passes.set(p, ps);
      return ps;
    }

    // ── recording: start / stop ─────────────────────────────────────
    async startRecord() {
      await this.start();
      if (this.recording || this._recStopping) return false;
      const P = this.project, armed = P.tracks.filter(t => t.arm);
      if (!armed.length) { this.emit('error', 'arm a track first'); return false; }
      const reg = this.recRegion(); if (reg.error) { this.emit('error', reg.error); return false; }
      const midi = armed.filter(t => t.kind === 'midi'), audio = armed.filter(t => t.kind === 'audio');
      if (audio.length && !this.inputSrc) { this.emit('error', 'pick an audio input first'); if (!midi.length) return false; }
      const cfg = this.recCfg(), fly = this.playing;
      this.emit('record-arm');              // the page takes its undo snapshot before anything changes
      const a = reg.a != null ? reg.a : Math.floor(Math.max(0, fly ? this.tickNow() : (this._stopTick || 0)) / BAR);
      const R = this.rec = { id: this.uid('rec'), at: new Date().toISOString(), a, b: reg.b, loop: !!reg.loop, wraps: !!reg.loop && reg.b === P.loop.b,
                             punch: !!reg.punch, cfg, fly, tracks: new Map(), cap: null, n0: 0, liveCtx: Infinity, lat: null };
      const closed = R.b != null;
      for (const tr of midi) {
        const rt = { kind: 'midi', tr, open: new Map(), passes: new Map(), base: [], snap: this._snap(tr), accum: cfg.mode === 'loop' };
        if (closed) { const base = this._carveMidi(tr, a, R.b); if (cfg.mode !== 'replace') rt.base = base; }
        R.tracks.set(tr.id, rt);
        this._recPass(rt, 0);
      }
      if (audio.length && this.inputSrc) {
        R.cap = new RecCapture(this.ctx, this.inputSrc);
        await R.cap.start();
        R.lat = this.audioComp();
        for (const tr of audio) {
          const rt = { kind: 'audio', tr, snap: this._snap(tr), layer: 0 };
          if (closed && cfg.mode === 'replace') this._carveAudio(tr, a, R.b);
          else if (closed) rt.layer = this._overdubLayer(tr, { a, b: R.b });
          R.tracks.set(tr.id, rt);
        }
      }
      this.recording = true;
      if (!fly) {
        const pre = cfg.countIn * BAR, head = this._stopTick || 0;
        let start = a * BAR - pre;
        if (reg.punch && !reg.loop && head < start) start = Math.floor(head / BAR) * BAR;    // pre-roll from the playhead
        this._countIn = pre ? { from: a * BAR - pre, to: a * BAR } : null;
        await this.play(start);
        R.liveCtx = this.timeOf(a * BAR);
      } else R.liveCtx = this.ctxAtPerf(performance.now()) - (this.outDelay || 0);
      R.n0 = this._anchorAt(R.liveCtx).n;
      this.emit('record', { on: true }); this.emit('takes', { recording: true });
      return true;
    }
    async stopRecord() {
      if (!this.recording) return;
      const R = this.rec;
      this.recording = false; this._recStopping = true; this._countIn = null;
      try {
        const stopCtx = this.ctxAtPerf(performance.now()) - (this.outDelay || 0);    // the scheduled time that was audible at stop
        const lastN = this._anchorAt(stopCtx).n, lastP = R.loop ? Math.max(0, lastN - R.n0) : 0;
        for (const rt of R.tracks.values()) if (rt.kind === 'midi') {
          for (const [note, o] of rt.open) this._recCommit(rt, note, o, stopCtx);
          rt.open.clear();
          this._recFinishMidi(rt, lastP, stopCtx);
        }
        const aud = [...R.tracks.values()].filter(rt => rt.kind === 'audio');
        if (R.cap) {
          try { if (aud.length) await this._recFinishAudio(R, aud, stopCtx, lastP); }
          catch (e) { this.emit('error', 'recording: ' + (e.message || e)); for (const rt of aud) this._restore(rt.tr, rt.snap); }
          finally { R.cap.stop(); }
        }
      } finally {
        this.rec = null; this._recStopping = false;
        this.emit('record', { on: false }); this.emit('takes', {}); this.emit('project');
      }
    }
    _recFinishMidi(rt, lastP, stopCtx) {
      const R = this.rec, tr = rt.tr;
      // a note quantized onto a downbeat that never came (stopped first) lands on the last pass's downbeat
      if (!rt.accum) for (const [p, ps] of [...rt.passes]) if (p > lastP) {
        const into = this._recPass(rt, lastP), pat = tr.patterns[into.pid];
        for (const n of ps.notes) { pat.notes.push(n); into.notes.push(n); }
        pat.notes.sort((x, y) => x.t - y.t);
        ps.notes = []; this._dropTake(tr, ps.take); rt.passes.delete(p);
      }
      if (R.b == null) {          // open take: the region is wherever the recording went
        const ps = rt.passes.get(0);
        if (ps) {
          const pat = tr.patterns[ps.pid], an = this._anchorAt(stopCtx), stopRel = an.tick + (stopCtx - an.ctx) / this.spt() - R.a * BAR;
          pat.lenBars = Math.max(1, pat.lenBars, Math.ceil(stopRel / BAR - 1e-6));
          ps.take.region = { a: R.a, b: R.a + pat.lenBars };
          const c = tr.clips.find(x => x.pid === ps.pid); if (c) c.bars = pat.lenBars;
          if (ps.notes.length) {
            const base = this._carveMidi(tr, R.a, R.a + pat.lenBars, ps.pid);
            if (R.cfg.mode !== 'replace') { pat.notes.push(...base); pat.notes.sort((x, y) => x.t - y.t); }
          }
        }
      }
      for (const [p, ps] of [...rt.passes]) if (!ps.notes.length) { this._dropTake(tr, ps.take); rt.passes.delete(p); }
      if (!rt.passes.size) { this._restore(tr, rt.snap); return; }
      const last = [...rt.passes.keys()].sort((x, y) => x - y).pop();
      this._activate(tr, rt.passes.get(last).take);
    }
    // audio: one capture, cut per pass on the context frame clock. The region's start in pass p is
    // anchor(p).ctx + (a − anchor.tick)·spt — the time the transport scheduled it — and its sound
    // arrives `latency` later, at frame round((start + latency)·sr). Full passes all get the loop's exact length.
    async _recFinishAudio(R, rts, stopCtx, lastP) {
      const cap = R.cap, sr = this.ctx.sampleRate, spt = this.spt(), L = R.lat.total / 1000, A = R.a * BAR;
      const segs = [];
      for (let p = 0; p <= lastP; p++) {
        const an = this._anchors.find(x => x.n === R.n0 + p); if (!an) continue;
        const rs = an.ctx + (A - an.tick) * spt, re = R.b != null ? rs + (R.b - R.a) * BAR * spt : Infinity;
        const s = Math.max(rs, p === 0 ? R.liveCtx : -Infinity), e = Math.min(re, stopCtx);
        if (!(e > s)) continue;
        const full = s === rs && e === re;
        if (!full && e - s < PPQ * spt && (segs.length || p > 0)) continue;     // a sliver of a pass after the last wrap
        segs.push({ p, s, e, rs, full });
      }
      if (!segs.length) { for (const rt of rts) this._restore(rt.tr, rt.snap); return; }
      await cap.until(Math.round((segs[segs.length - 1].e + L) * sr) + 128, 400 + R.lat.total * 4);
      const Nfull = R.b != null ? Math.round((R.b - R.a) * BAR * spt * sr) : 0, made = [];
      for (const g of segs) {
        const f0 = Math.round((g.s + L) * sr), n = g.full ? Nfull : Math.max(1, Math.round((g.e - g.s) * sr));
        const chs = cap.slice(f0, n); fadeEdges(chs, sr, FADE_MS);
        const rec = await AK.lib.put({ kind: 'daw-rec', name: (rts[0].tr.name || 'audio') + ' take ' + AK.util.stamp() + (segs.length > 1 ? ' p' + (g.p + 1) : ''), sampleRate: sr, meta: { title: 'DAW take', tags: ['daw', 'take'] } }, chs);
        made.push({ g, rec, len: n / sr, t: A + (g.s - g.rs) / spt, f0, n });
      }
      R.made = made.map(m => ({ p: m.g.p, f0: m.f0, n: m.n, libId: m.rec.id }));     // for tests / diagnostics
      for (const rt of rts) {
        const tr = rt.tr; let b = R.b;
        if (b == null) { const m = made[0]; b = R.a + Math.max(1, Math.ceil((m.t - A + m.len / spt) / BAR - 1e-6)); if (R.cfg.mode === 'replace') this._carveAudio(tr, R.a, b); }
        tr.takes = Array.isArray(tr.takes) ? tr.takes : [];
        let last = null;
        for (const m of made) {
          const k = { id: this.uid('take'), region: { a: R.a, b }, kind: 'audio', audioRef: { libId: m.rec.id, t: m.t, offset: 0, len: m.len }, name: '', at: R.at, pass: m.g.p, rec: R.id, latMs: R.lat.total, latFrom: R.lat.kind, active: false };
          if (rt.layer) k.layer = rt.layer;
          k.name = 'take ' + (this._group(tr, k).length + 1);
          tr.takes.push(k); last = k;
        }
        this._activate(tr, last);
      }
      this.lastRec = R;
    }

    // ── takes ───────────────────────────────────────────────────────
    // track.takes = [{ id, region:{a,b} (bars), kind:'midi'|'audio', pid | audioRef:{libId,t,offset,len}, name, at,
    //                  pass, rec, active, layer?, latMs?, latFrom? }] — one active take per (region, kind, layer)
    _group(tr, k) { const L = k.layer || 0; return (tr.takes || []).filter(x => x.kind === k.kind && x.region.a === k.region.a && x.region.b === k.region.b && (x.layer || 0) === L); }
    _clipMatches(ref, x) { return !!ref && x.libId === ref.libId && (x.offset || 0) === (ref.offset || 0); }
    // make k the take that plays: its region's clip(s) switch to it (or it gets a clip)
    _activate(tr, k) {
      const g = this._group(tr, k);
      if (k.kind === 'midi') {
        const pids = new Set(g.map(x => x.pid)); let hit = false;
        for (const c of tr.clips) if (pids.has(c.pid)) { c.pid = k.pid; hit = true; }
        if (!hit) tr.clips.push({ bar: k.region.a, pid: k.pid, bars: k.region.b - k.region.a });
      } else {
        const ref = k.audioRef, name = tr.name + ' · ' + k.name;
        const idx = tr.audio.map((x, i) => g.some(y => this._clipMatches(y.audioRef, x)) ? i : -1).filter(i => i >= 0);
        const mk = old => ({ t: ref.t, libId: ref.libId, name, offset: ref.offset || 0, len: ref.len, gain: old && old.gain != null ? old.gain : 1 });
        if (idx.length) { tr.audio[idx[0]] = mk(tr.audio[idx[0]]); for (const i of idx.slice(1).reverse()) tr.audio.splice(i, 1); }
        else tr.audio.push(mk(null));
      }
      for (const x of g) x.active = x === k;
    }
    // remove a take record (+ its pattern when nothing uses it); if it was playing, the newest other take of
    // its region takes over, or its clip goes
    _dropTake(tr, k) {
      const others = this._group(tr, k).filter(x => x !== k);
      if (k.active) {
        if (others.length) this._activate(tr, others[others.length - 1]);
        else if (k.kind === 'midi') tr.clips = tr.clips.filter(c => c.pid !== k.pid);
        else tr.audio = tr.audio.filter(x => !this._clipMatches(k.audioRef, x));
      }
      tr.takes = (tr.takes || []).filter(x => x !== k);
      if (k.kind === 'midi' && !tr.clips.some(c => c.pid === k.pid) && !tr.takes.some(x => x.pid === k.pid)) delete tr.patterns[k.pid];
      if (!tr.takes.length) delete tr.takes;
    }
    // take groups for the UI: [{ key, region, kind, layer, takes, active }]
    takeGroups(tr) {
      const out = new Map();
      for (const k of (tr && tr.takes) || []) {
        const key = k.kind + ':' + k.region.a + ':' + k.region.b + ':' + (k.layer || 0);
        if (!out.has(key)) out.set(key, { key, region: k.region, kind: k.kind, layer: k.layer || 0, takes: [], active: null });
        const g = out.get(key); g.takes.push(k); if (k.active) g.active = k;
      }
      return [...out.values()].sort((x, y) => x.region.a - y.region.a || x.layer - y.layer);
    }
    _takeOf(trackId, takeId) { const tr = this.track(trackId), k = tr && (tr.takes || []).find(x => x.id === takeId); return k ? { tr, k } : null; }
    pickTake(trackId, takeId) { const o = this._takeOf(trackId, takeId); if (!o || this.rec) return false; this._activate(o.tr, o.k); this.emit('takes', { trackId }); return true; }
    cycleTake(trackId, groupKey, dir = 1) {
      const tr = this.track(trackId), g = this.takeGroups(tr).find(x => x.key === groupKey); if (!g || this.rec) return null;
      const i = g.takes.indexOf(g.active), k = g.takes[((i < 0 ? -1 : i) + dir + g.takes.length) % g.takes.length];
      this._activate(tr, k); this.emit('takes', { trackId }); return k;
    }
    deleteTake(trackId, takeId) { const o = this._takeOf(trackId, takeId); if (!o || this.rec) return false; this._dropTake(o.tr, o.k); this.emit('takes', { trackId }); return true; }
    keepOnlyActive(trackId, groupKey) {
      const tr = this.track(trackId); if (!tr || this.rec) return 0;
      let n = 0;
      for (const g of this.takeGroups(tr)) if ((!groupKey || g.key === groupKey) && g.active) for (const k of g.takes) if (!k.active) { this._dropTake(tr, k); n++; }
      this.emit('takes', { trackId }); return n;
    }

    // ── recording: editing what is already there ────────────────────
    _snap(tr) { return { clips: clone(tr.clips), audio: clone(tr.audio), takes: tr.takes ? clone(tr.takes) : null, pids: new Set(Object.keys(tr.patterns)) }; }
    _restore(tr, s) {
      tr.clips = s.clips; tr.audio = s.audio;
      if (s.takes) tr.takes = s.takes; else delete tr.takes;
      for (const k of Object.keys(tr.patterns)) if (!s.pids.has(k)) delete tr.patterns[k];
    }
    // cut bars [a, b) out of a MIDI track's clips (clips are split at a and b; a right-hand piece that starts
    // mid-pattern gets a rotated copy of the pattern). Returns the notes that were sounding there, relative to a.
    _carveMidi(tr, a, b, keepPid) {
      const A = a * BAR, B = b * BAR, base = [], out = [];
      for (const c of tr.clips) {
        const p = tr.patterns[c.pid];
        if (!p || c.pid === keepPid) { out.push(c); continue; }
        const plen = p.lenBars * BAR, cs = c.bar * BAR, ce = cs + (c.bars || p.lenBars) * BAR;
        if (ce <= A || cs >= B) { out.push(c); continue; }
        for (let r0 = cs; r0 < ce; r0 += plen) for (const n of p.notes) {
          const at = r0 + n.t; if (at < A || at >= B || at >= ce) continue;
          base.push({ t: at - A, d: Math.max(1, Math.min(n.d, ce - at, B - at)), n: n.n, v: n.v });
        }
        if (cs < A) out.push(Object.assign({}, c, { bars: a - c.bar }));
        if (ce > B) {
          const ph = ((B - cs) % plen + plen) % plen; let pid = c.pid;
          if (ph) { pid = this.uid('pat'); tr.patterns[pid] = { name: p.name + ' ›', lenBars: p.lenBars, notes: p.notes.map(n => Object.assign({}, n, { t: ((n.t - ph) % plen + plen) % plen })).sort((x, y) => x.t - y.t) }; }
          out.push(Object.assign({}, c, { bar: b, pid, bars: (ce - B) / BAR }));
        }
      }
      tr.clips = out;
      return base.sort((x, y) => x.t - y.t || x.n - y.n);
    }
    // cut bars [a, b) out of an audio track's clips (offset / len trims; the cut originals get no fades)
    _carveAudio(tr, a, b) {
      const A = a * BAR, B = b * BAR, spt = this.spt(), out = [];
      for (const x of tr.audio) {
        const s = x.t, e = x.t + x.len / spt;
        if (e <= A || s >= B) { out.push(x); continue; }
        if (s < A) out.push(Object.assign({}, x, { len: (A - s) * spt }));
        if (e > B) out.push(Object.assign({}, x, { t: B, offset: (x.offset || 0) + (B - s) * spt, len: (e - B) * spt }));
      }
      tr.audio = out;
    }
    // OVERDUB on audio layers a new take group over a region that already has an active audio take
    _overdubLayer(tr, region) {
      const used = (tr.takes || []).filter(k => k.kind === 'audio' && k.region.a === region.a && k.region.b === region.b && k.active).map(k => k.layer || 0);
      return used.length ? Math.max(...used) + 1 : 0;
    }

    // ── loopback calibration: the play-along input's round trip ─────
    // Short tone bursts on the click bus (never bounced) at scheduled context times T; the chosen input
    // hears them back; onset = first frame above max(0.01, 4 × floor) on the same frame clock a take is cut
    // on — the same quantity and detector as FM-1 CHECK-OUT's MIDI → audio measurement. Median of n.
    async calibrateLoopback({ n = 8, gap = 0.32 } = {}) {
      await this.start();
      if (!this.inputSrc) throw new Error('pick an audio input first (EXPORT → RECORDING)');
      if (this.playing) this.stop();
      const c = this.ctx, sr = c.sampleRate, cap = new RecCapture(c, this.inputSrc);
      await cap.start();
      try {
        await sleep(300);
        const t0 = c.currentTime, floor = cap.peak(Math.round((t0 - 0.25) * sr), Math.round(t0 * sr));
        const T0 = c.currentTime + 0.15, Ts = [];
        for (let i = 0; i < n; i++) { const T = T0 + i * gap; Ts.push(T); this._pulse(T); }
        await cap.until(Math.round((Ts[n - 1] + 0.3) * sr), (T0 - c.currentTime + n * gap) * 1000 + 2000);
        const thr = Math.max(0.01, floor * 4), samples = [];
        for (const T of Ts) { const f = cap.firstAbove(Math.round((T - 0.002) * sr), Math.round((T + 0.28) * sr), thr); samples.push(f == null ? null : Math.round((f / sr - T) * 100000) / 100); }
        const got = samples.filter(x => x != null).sort((x, y) => x - y);
        if (got.length < Math.ceil(n * 0.75)) throw new Error('only ' + got.length + ' of ' + n + ' clicks came back — cable the output into the input (or hold the mic to the speaker) and turn it up');
        const med = got.length % 2 ? got[(got.length - 1) / 2] : (got[got.length / 2 - 1] + got[got.length / 2]) / 2;
        const mean = got.reduce((x, y) => x + y, 0) / got.length, sd = Math.sqrt(got.reduce((x, y) => x + (y - mean) ** 2, 0) / got.length);
        this.setLatency('input', med, 'loopback');
        return { ms: Math.round(med * 10) / 10, jitterMs: Math.round(sd * 100) / 100, samples, found: got.length, of: n };
      } finally { cap.stop(); }
    }
    _pulse(T) {
      const c = this.ctx, o = c.createOscillator(), g = c.createGain();
      o.frequency.value = 2000; g.gain.setValueAtTime(0.9, T); g.gain.exponentialRampToValueAtTime(0.001, T + 0.02);
      o.connect(g); g.connect(this.click); o.start(T); o.stop(T + 0.03);
    }
    async setInput(deviceId) {
      if (this.inputSrc) { try { this.inputSrc.disconnect(); } catch (e) {} this.inputSrc = null; }
      if (this.inputStream) { this.inputStream.getTracks().forEach(t => t.stop()); this.inputStream = null; }
      this.inputLabel = '';
      if (deviceId === null) { this.emit('latency', this.lat); return; }
      await this.start();
      this.inputStream = await AK.inputs.open(deviceId || undefined, 2);
      this.inputSrc = this.ctx.createMediaStreamSource(this.inputStream);
      const at = this.inputStream.getAudioTracks()[0];
      let label = at && at.label;
      if (!label) { const list = await AK.inputs.list().catch(() => []); const d = list.find(x => x.deviceId === (deviceId || 'default')); label = d ? d.label : ''; }
      this.inputLabel = label || '';
      this.emit('latency', this.lat);
      return label;
    }

    // ── bounce (real time: emulators and hardware can't render offline) ──
    // ── offline render: faster than real time ───────────────────────
    // Everything that is plain Web Audio (FORGE, KIT, PATCH BANK sampler / DX7, basic) re-creates
    // itself inside an OfflineAudioContext from its current state. FM-1 emulators and hardware run in
    // real time only → canRenderOffline() is false and bounce() keeps the real-time path.
    canRenderOffline(trackIds) {
      const P = this.project;
      return P.tracks.filter(t => !trackIds || trackIds.includes(t.id)).every(t => {
        if (t.kind === 'audio') return true;
        const d = this.dev(t.deviceId); return !d || ['forge', 'kit', 'basic', 'patch'].includes(d.type) || !t.clips.length;
      });
    }
    async _offlineDevice(off, d, output) {
      const live = this.devices.get(d.id);
      let inst = null;
      if (d.type === 'forge' && typeof G.ForgeSynth === 'function') { inst = new G.ForgeSynth(off, { output, maxVoices: 16 }); await inst.init(); if (live && live.getState) inst.setState(live.getState()); }
      else if (d.type === 'kit') { inst = new KitDevice(off, { output }); await inst.init(); if (live && live.getState) inst.setState(live.getState()); }
      else if (d.type === 'patch') {
        const inner = live && live.inner; if (!inner) return null;
        if (inner.loadVoice) { inst = new inner.constructor(off, { output, maxVoices: 16 }); await inst.init(); inst.setState(inner.getState()); }
        else { inst = new inner.constructor(off, { output, maxVoices: 64 }); await inst.init(); await inst.load(inner.instrument); inst.setState(inner.getState()); }
        if ('bpm' in inst) inst.bpm = this.project.bpm;
      }
      else { inst = new BasicSynth(off, { output }); if (live && live.getState) inst.setState(live.getState()); }
      return inst;
    }
    // opts: fromBar, toBar, loop (fold the tail onto the head → seamless, exact length), tailSec,
    //       trackIds (only these — a stem), limiter (default true; stems render without it so they sum)
    async renderOffline({ fromBar = 0, toBar, loop = false, tailSec = 3, trackIds = null, limiter = true, sampleRate = RATE, onProgress } = {}) {
      await this.start(); await this.whenReady();
      const P = this.project, M = P.master, spt = this.spt();
      const t0 = fromBar * BAR, t1 = (toBar ?? this.songBars()) * BAR;
      const lenSec = (t1 - t0) * spt, total = Math.ceil((lenSec + tailSec) * sampleRate);
      const off = new OfflineAudioContext(2, total, sampleRate);
      // master chain, same as live
      const master = off.createGain(), out = off.createGain(); out.gain.value = M.vol;
      if (limiter) { const lim = off.createDynamicsCompressor(); lim.threshold.value = -2; lim.knee.value = 0; lim.ratio.value = 20; lim.attack.value = 0.002; lim.release.value = 0.1; master.connect(lim); lim.connect(out); }
      else master.connect(out);
      out.connect(off.destination);
      const verbIn = off.createGain(), verb = off.createConvolver(), verbOut = off.createGain();
      verb.buffer = this.verb.buffer; verbOut.gain.value = M.verbMix; verbIn.connect(verb); verb.connect(verbOut); verbOut.connect(master);
      const dIn = off.createGain(), dl = off.createDelay(4), dFb = off.createGain(), dTone = off.createBiquadFilter(), dOut = off.createGain();
      dl.delayTime.value = Math.min(3.9, M.delayBeats * 60 / P.bpm); dFb.gain.value = M.delayFb; dTone.type = 'lowpass'; dTone.frequency.value = 4200; dOut.gain.value = M.delayMix;
      dIn.connect(dl); dl.connect(dTone); dTone.connect(dFb); dFb.connect(dl); dTone.connect(dOut); dOut.connect(master);
      if (G.DawFX) await G.DawFX.prepare(off);
      const bus = { master, verbIn, delayIn: dIn };
      // which strips sound: the project's mute/solo, narrowed to trackIds for a stem
      const devMixes = [...P.devices.map(d => d.mix), ...P.tracks.filter(t => t.kind === 'audio').map(t => t.mix)].filter(Boolean);
      const anyDevSolo = devMixes.some(m => m.solo);
      const audible = mix => mix && !mix.mute && (!anyDevSolo || mix.solo);
      const active = this.activeTracks(), tracks = active.filter(t => !trackIds || trackIds.includes(t.id));
      const sidOf = t => this.stripOf(t), mixOf = sid => { const o = this.stripOwner(sid); return o && o.mix; };
      const sounding = new Set();
      for (const tr of tracks) { const sid = sidOf(tr); if (!sid || (tr.kind === 'midi' && !this.dev(sid))) continue; if (audible(mixOf(sid))) sounding.add(sid); }
      // a sidechain source that isn't sounding here (another stem, or a muted strip) still plays — silently —
      // so its envelope ducks the target exactly as in the full mix
      const needed = new Set(sounding);
      for (const sid of sounding) { const dk = (mixOf(sid) || {}).duck; if (dk && dk.source && dk.source !== sid && mixOf(dk.source)) needed.add(dk.source); }
      const insts = new Map(), strips = new Map();
      for (const sid of needed) {
        const mix = mixOf(sid), st = this._buildStrip(off, mix, bus);
        st.on.gain.value = sounding.has(sid) ? 1 : 0;
        this._syncFx(off, st, mix, P.bpm, null);
        for (const u of st.fxUnits.values()) u.sync(0);
        strips.set(sid, st);
        const d = this.dev(sid);
        if (d) {
          const inst = await this._offlineDevice(off, d, st.in);
          if (!inst) throw new Error(d.name + ' cannot render offline');
          insts.set(sid, inst);
          if (inst.syncAt) inst.syncAt(0);
        }
      }
      for (const [sid, st] of strips) this._syncDuck(off, strips, sid, st, null);
      // the tracks whose notes / clips play: this render's, plus whatever feeds a silent sidechain source
      const playing = active.filter(t => { const sid = sidOf(t); return strips.has(sid) && (sounding.has(sid) ? tracks.includes(t) : true); });
      // notes: same rules as live playback (patterns repeat inside clips, clipped at clip end, swing)
      const at = tick => (tick - t0) * spt + this.swingDelay(tick);
      let notes = 0;
      for (const tr of playing) {
        if (tr.kind === 'midi') {
          const inst = insts.get(tr.deviceId); if (!inst) continue;
          const pc = this._playCtx(tr), gr = pc.groove;      // the same PERF clip chain / groove / probability as live
          for (const c of tr.clips) {
            const p = tr.patterns[c.pid]; if (!p || !p.notes.length) continue;
            const plen = p.lenBars * BAR, cs = c.bar * BAR, ce = cs + (c.bars || p.lenBars) * BAR;
            if (ce <= t0 || cs >= t1) continue;
            const pnotes = pc.notes(p);
            for (let base = cs; base < ce; base += plen) for (const n of pnotes) {
              const on = base + n.t; if (on < t0 || on >= t1 || on >= ce) continue;
              if (n.p !== undefined && !pc.plays(base, n)) continue;
              const offT = Math.min(on + n.d, ce, loop ? t1 : Infinity);
              if (gr) {
                const q = gr.note(on, Math.min(on + n.d, ce), n.n, n.v * (tr.vel ?? 1)), w = Math.max(0, (on - t0) * spt + q.on);
                inst.noteOn(n.n, q.v, w, tr.channel); inst.noteOff(n.n, Math.max(w + 0.005, (offT - t0) * spt + q.off - 0.002), tr.channel);
                notes++; continue;
              }
              const vel = Math.max(0.02, Math.min(1, n.v * (tr.vel ?? 1)));
              inst.noteOn(n.n, vel, at(on), tr.channel); inst.noteOff(n.n, Math.max(at(on) + 0.005, at(offT) - 0.002), tr.channel);
              notes++;
            }
          }
        } else {
          const st = strips.get(tr.id); if (!st) continue;
          for (const a of tr.audio) {
            const s0 = a.t, s1 = a.t + a.len / spt; if (s1 <= t0 || s0 >= t1) continue;
            const buf = await this.clipBuffer(a); if (!buf) continue;
            const src = off.createBufferSource(); src.buffer = buf; const g = off.createGain(); g.gain.value = a.gain ?? 1; src.connect(g); g.connect(st.in);
            const skip = Math.max(0, (t0 - s0) * spt), when = Math.max(0, (s0 - t0) * spt), dur = Math.min(a.len - skip, lenSec - when + (loop ? 0 : tailSec));
            if (dur > 0) src.start(when, (a.offset || 0) + skip, dur);
          }
        }
      }
      // automation: the whole timeline up front
      this._autoRange({ timeOf: tk => (tk - t0) * spt, strip: id => strips.get(id), inst: id => insts.get(id), cache: new Map(), seen: new Set(), fresh: true, cancel: null }, t0, t1);
      for (const inst of insts.values()) if (inst.flush) await inst.flush();
      if (onProgress) onProgress({ phase: 'render', notes });
      const buf = await off.startRendering();
      let chs = [buf.getChannelData(0).slice(0), buf.getChannelData(1).slice(0)];
      const L = Math.round(lenSec * sampleRate);
      if (loop) {            // what rings past the end belongs at the start of the next pass
        chs = chs.map(c => { const o = c.slice(0, L); for (let i = L; i < c.length; i++) o[(i - L) % L] += c[i]; return o; });
      }
      for (const inst of insts.values()) { try { inst.dispose(); } catch (e) {} }
      for (const st of strips.values()) { for (const u of st.fxUnits.values()) u.dispose(); if (st.duckNode) { try { st.duckNode.port.postMessage('stop'); } catch (e) {} } }
      return { channels: chs, sampleRate, loop: loop ? { start: 0, end: L - 1 } : null, bars: (t1 - t0) / BAR, lenSec, notes, offline: true };
    }
    // stems: one render per group with no master limiter, so the stems sum back to the mix exactly.
    // groups: [{ name, trackIds }]. The mix is rendered the same way (sum of everything).
    async renderStems({ groups, fromBar = 0, toBar, loop = false, tailSec = 3, onProgress } = {}) {
      const stems = [];
      for (let i = 0; i < groups.length; i++) {
        if (onProgress) onProgress({ phase: 'stem', done: i, total: groups.length, name: groups[i].name });
        const r = await this.renderOffline({ fromBar, toBar, loop, tailSec, trackIds: groups[i].trackIds, limiter: false });
        stems.push(Object.assign({}, groups[i], r));
      }
      return stems;
    }

    // every device loaded (PATCH BANK instruments may still be downloading)
    async whenReady() { await Promise.all([...this.devices.values()].map(i => i.ready).filter(Boolean)); }
    async bounce({ fromBar = 0, toBar, loop = false, tailSec = 2, realtime = false } = {}) {
      await this.start();
      await this.whenReady();
      if (!realtime && this.canRenderOffline()) return this.renderOffline({ fromBar, toBar, loop, tailSec });
      const P = this.project, savedLoop = Object.assign({}, P.loop);
      const bars = (toBar ?? this.songBars()) - fromBar;
      const lenSec = bars * BAR * this.spt();
      const cap = new AK.Capture(this.ctx, this.out, { preRollSec: 0, maxChannels: 2 });
      await cap.start();
      if (loop) { P.loop = { on: true, a: fromBar, b: fromBar + bars }; }
      else { P.loop = { on: false, a: fromBar, b: fromBar + bars }; }
      cap.begin(0);
      const began = this.ctx.currentTime;
      await this.play(fromBar * BAR);
      const startAt = this.anchor.ctx;
      this.emit('bounce', { phase: 'running', seconds: loop ? lenSec * 2 : lenSec + tailSec });
      // loop: let it go round twice and keep the second pass (tails from pass one wrap into it → seamless)
      const total = loop ? lenSec * 2 + 0.3 : lenSec + tailSec;
      await new Promise(r => setTimeout(r, (startAt - this.ctx.currentTime + total) * 1000));
      if (!loop && this.playing) this.stop();
      if (loop) this.stop();
      const res = cap.end(); cap.stop();
      P.loop = savedLoop;
      const sr = res.sampleRate, lead = Math.round((startAt - began) * sr);
      let chs;
      if (loop) { const L = Math.round(lenSec * sr), a = lead + L; chs = res.channels.map(c => c.slice(a, a + L)); }
      else chs = res.channels.map(c => c.slice(lead, lead + Math.round((lenSec + tailSec) * sr)));
      this.emit('bounce', { phase: 'done' });
      return { channels: chs, sampleRate: sr, loop: loop ? { start: 0, end: chs[0].length - 1 } : null, bars, lenSec };
    }

    // ── persistence ─────────────────────────────────────────────────
    async save() {
      this.snapshotStates();
      await AK.lib.kvSet('daw_project', JSON.parse(JSON.stringify(this.project)));
    }
    async restore() { try { return await AK.lib.kvGet('daw_project'); } catch (e) { return null; } }

    // ── MIDI file ───────────────────────────────────────────────────
    // ── credits for every PATCH BANK instrument the project uses ─────
    async credits() {
      const PB = G.PatchBank, ids = this.project.devices.filter(d => d.type === 'patch' && d.patch && this.project.tracks.some(t => t.deviceId === d.id)).map(d => d.patch);
      if (!PB || !ids.length) return { lines: [], worst: 'free', text: '' };
      return PB.credits(ids);
    }
    async setPatch(devId, patch, name) {      // swap a patch device's instrument, keeping its mixer strip
      const d = this.dev(devId); if (!d) return;
      this.removeDeviceRuntimeOnly(devId);
      d.patch = patch; d.state = null; if (name) d.name = name;
      await this.createDeviceRuntime(d); this.applyMix(); this.emit('project');
    }
    removeDeviceRuntimeOnly(id) { const inst = this.devices.get(id); if (inst) { try { inst.allOff(); inst.dispose(); } catch (e) {} } this.devices.delete(id); }

    exportMidi(trackIds) {
      const P = this.project, tracks = [];
      for (const tr of P.tracks) {
        if (tr.kind !== 'midi' || (trackIds && !trackIds.includes(tr.id))) continue;
        const notes = [];
        for (const c of tr.clips) {
          const p = tr.patterns[c.pid]; if (!p) continue;
          const reps = Math.ceil((c.bars || p.lenBars) / p.lenBars);
          for (let r = 0; r < reps; r++) for (const n of p.notes) { const t = c.bar * BAR + r * p.lenBars * BAR + n.t; if (t < c.bar * BAR + (c.bars || p.lenBars) * BAR) notes.push(Object.assign({}, n, { t })); }
        }
        // tracks on our own synths have no real channel: drums go out on GM channel 10, the rest keep theirs
        const d = this.dev(tr.deviceId), routed = d && (d.type === 'emu' || d.type === 'hw');
        const drums = tr.role === 'drums' || (d && d.type === 'kit');
        tracks.push({ name: tr.name, channel: routed ? (tr.channel || 1) : drums ? 10 : (tr.channel || 1), notes });
      }
      return G.SMF.write(tracks, { ppq: PPQ, bpm: P.bpm, name: P.name });
    }
  }

  const API = { Engine, BasicSynth, KitDevice, HwDevice, RecCapture, KIT_MAP, PPQ, BAR, RATE, GRIDS, REC_MODES };
  root.DAW = API;
})(typeof window !== 'undefined' ? window : globalThis);
