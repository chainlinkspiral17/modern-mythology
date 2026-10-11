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
 * Timing: a 25 ms timer schedules 120 ms ahead in AudioContext time; Web
 * Audio devices get exact times, the emulator dispatches messages on time,
 * hardware MIDI goes out with performance-time stamps.
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
      this.noteOff(n, undefined, true);
      this.voices.set(n, { o, g });
    }
    noteOff(n, when = this.ctx.currentTime, immediate) {
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
      try { mi.output.send(bytes, this.engine.perfTime(when ?? this.ctx.currentTime)); } catch (e) { /* port gone */ }
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

  // ═══════════════════════════════════════════════════════════════════
  class Engine {
    constructor() {
      this.ctx = null; this.project = null; this.devices = new Map(); this.strips = new Map();
      this.playing = false; this.recording = false; this.anchor = null; this.schedTick = 0; this.timer = null;
      this.sources = []; this.midi = null; this.listeners = {}; this.recTakes = new Map(); this.inputStream = null;
      this.latencyMs = 30; this.quantize = 24;
    }
    on(ev, fn) { (this.listeners[ev] = this.listeners[ev] || []).push(fn); }
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
      this.click = c.createGain(); this.click.gain.value = 0.5; this.click.connect(c.destination);   // never in a bounce
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
    swingDelay(tick) {
      const s = this.project.swing || 0; if (!s) return 0;
      const pos = ((tick % (PPQ / 2)) + PPQ / 2) % (PPQ / 2);
      return Math.abs(pos - PPQ / 4) <= 2 ? s * (PPQ / 4) * 0.5 * this.spt() : 0;
    }

    // ── transport ───────────────────────────────────────────────────
    async play(fromTick) {
      await this.start();
      if (this.playing) this.stop();
      const P = this.project;
      const startTick = fromTick ?? (P.loop.on ? P.loop.a * BAR : 0);
      this.anchor = { ctx: this.ctx.currentTime + 0.08, tick: startTick };
      this.schedTick = startTick;
      this.playing = true;
      this._auto = { fresh: true, cancel: this.ctx.currentTime, cache: new Map(), seen: new Set() };
      this._recAuto = new Map();
      this.sendClock('start', this.anchor.ctx);
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
      const now = this.ctx.currentTime;
      if (this.playing) { this._stopTick = this.tickNow(); this.sendClock('stop', now); }
      this.playing = false;
      for (const inst of this.devices.values()) { try { inst.allOff(now); } catch (e) {} }
      for (const s of this.sources) { try { s.stop(now + 0.02); } catch (e) {} }
      this.sources = [];
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
        const songEnd = this.songBars() * BAR;
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
        for (const c of tr.clips) {
          const p = tr.patterns[c.pid]; if (!p || !p.notes.length) continue;
          const plen = p.lenBars * BAR, cs = c.bar * BAR, ce = cs + (c.bars || p.lenBars) * BAR;
          if (ce <= t0 || cs >= t1) continue;
          // windows are fractional ticks: "- 1" here dropped the notes on a loop start when the window after
          // the wrap was under one tick long
          const rep0 = Math.max(0, Math.floor((t0 - cs) / plen)), rep1 = Math.floor((Math.min(t1, ce) - cs - 1e-6) / plen);
          for (let r = rep0; r <= rep1; r++) {
            const base = cs + r * plen;
            for (const n of p.notes) {
              const at = base + n.t;
              if (at < t0 || at >= t1 || at >= ce) continue;
              const when = this.timeOf(at) + this.swingDelay(at);
              const off = this.timeOf(Math.min(at + n.d, ce)) + this.swingDelay(at + n.d) - 0.002;
              const vel = Math.max(0.02, Math.min(1, n.v * (tr.vel ?? 1)));
              try { inst.noteOn(n.n, vel, when, tr.channel); inst.noteOff(n.n, Math.max(when + 0.005, off), tr.channel); } catch (e) { /* device mid-reload */ }
            }
          }
        }
      }
      for (const tr of this.activeTracks()) {
        if (tr.kind !== 'audio') continue;
        for (const a of tr.audio) if (a.t >= t0 && a.t < t1) this.startAudioClip(tr, a, this.timeOf(a.t), 0);
      }
      if (P.metro) for (let b = Math.ceil(t0 / PPQ) * PPQ; b < t1; b += PPQ) this.clickAt(this.timeOf(b), b % BAR === 0);
      this.clockRange(t0, t1);
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
      if (on) inst.noteOn(note, vel, now, tr.channel); else inst.noteOff(note, now, tr.channel);
      if (this.recording && this.playing && tr.arm) this.recordMidi(tr, note, vel, on, now - this.latencyMs / 1000);
    }
    recordMidi(tr, note, vel, on, when) {
      const take = this.recTakes.get(tr.id); if (!take) return;
      let tick = this.anchor.tick + (when - this.anchor.ctx) / this.spt();
      if (on) { take.open.set(note, { tick, vel }); return; }
      const o = take.open.get(note); if (!o) return; take.open.delete(note);
      const p = tr.patterns[take.pid], plen = p.lenBars * BAR, cs = take.bar * BAR;
      let t = o.tick, q = this.quantize;
      if (q) t = Math.round(t / q) * q;
      const rel = ((t - cs) % plen + plen) % plen;
      p.notes.push({ t: Math.round(rel), d: Math.max(6, Math.round(tick - o.tick)), n: note, v: o.vel });
      p.notes.sort((a, b) => a.t - b.t);
      this.emit('notes', { trackId: tr.id, pid: take.pid });
    }
    async startRecord() {
      await this.start();
      const P = this.project, armed = P.tracks.filter(t => t.arm);
      if (!armed.length) { this.emit('error', 'arm a track first'); return false; }
      const bar = P.loop.on ? P.loop.a : Math.floor((this._stopTick || 0) / BAR);
      for (const tr of armed) {
        if (tr.kind === 'midi') {
          const lenBars = P.loop.on ? P.loop.b - P.loop.a : 4;
          const pid = this.uid('rec');
          tr.patterns[pid] = { name: 'take ' + (Object.keys(tr.patterns).length + 1), lenBars, notes: [] };
          tr.clips = tr.clips.filter(c => !(c.bar >= bar && c.bar < bar + lenBars));
          tr.clips.push({ bar, pid });
          this.recTakes.set(tr.id, { pid, bar, open: new Map() });
        } else {
          if (!this.inputStream) { this.emit('error', 'pick an audio input first'); continue; }
          const cap = new AK.Capture(this.ctx, this.inputSrc, { preRollSec: 0, maxChannels: 2 });
          await cap.start();
          this.recTakes.set(tr.id, { cap, tick: bar * BAR, began: false });
        }
      }
      this.recording = true;
      if (!this.playing) await this.play(bar * BAR);
      for (const [id, take] of this.recTakes) if (take.cap) { take.cap.begin(0); take.beganCtx = this.ctx.currentTime; take.anchorCtx = this.anchor.ctx; take.tick = this.anchor.tick; }
      this.emit('record', { on: true });
      return true;
    }
    async stopRecord() {
      if (!this.recording) return;
      this.recording = false;
      for (const [id, take] of this.recTakes) {
        if (!take.cap) continue;
        const res = take.cap.end(); take.cap.stop();
        if (!res) continue;
        // align: drop what was captured before the transport started + the round-trip latency
        const drop = Math.max(0, Math.round(((take.anchorCtx - take.beganCtx) + this.latencyMs / 1000) * RATE));
        const chs = res.channels.map(c => c.slice(Math.min(drop, c.length - 1)));
        const tr = this.track(id);
        const rec = await AK.lib.put({ kind: 'daw-rec', name: (tr ? tr.name : 'audio') + ' take ' + AK.util.stamp(), sampleRate: res.sampleRate, meta: { title: 'DAW take', tags: ['daw'] } }, chs);
        if (tr) tr.audio.push({ t: take.tick, libId: rec.id, name: rec.name, offset: 0, len: chs[0].length / res.sampleRate, gain: 1 });
      }
      this.recTakes.clear();
      this.emit('record', { on: false }); this.emit('project');
    }
    async setInput(deviceId) {
      if (this.inputSrc) { try { this.inputSrc.disconnect(); } catch (e) {} this.inputSrc = null; }
      if (this.inputStream) { this.inputStream.getTracks().forEach(t => t.stop()); this.inputStream = null; }
      if (deviceId === null) return;
      await this.start();
      this.inputStream = await AK.inputs.open(deviceId || undefined, 2);
      this.inputSrc = this.ctx.createMediaStreamSource(this.inputStream);
      return this.inputStream.getAudioTracks()[0].label;
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
          for (const c of tr.clips) {
            const p = tr.patterns[c.pid]; if (!p || !p.notes.length) continue;
            const plen = p.lenBars * BAR, cs = c.bar * BAR, ce = cs + (c.bars || p.lenBars) * BAR;
            if (ce <= t0 || cs >= t1) continue;
            for (let base = cs; base < ce; base += plen) for (const n of p.notes) {
              const on = base + n.t; if (on < t0 || on >= t1 || on >= ce) continue;
              const offT = Math.min(on + n.d, ce, loop ? t1 : Infinity);
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

  const API = { Engine, BasicSynth, KitDevice, HwDevice, KIT_MAP, PPQ, BAR, RATE };
  root.DAW = API;
})(typeof window !== 'undefined' ? window : globalThis);
