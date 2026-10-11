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
 *
 * Device types (each exposes noteOn/noteOff/allOff/cc(/midi) + getState/setState):
 *   forge  ForgeSynth (forge_synth.js) — one patch
 *   kit    a drum kit: one ForgeSynth per GM drum note
 *   emu    an FM-1 firmware running in the browser (fm1_emu.js); tracks pick its MIDI channel
 *   hw     the real FM-1 (or anything) over Web MIDI; its USB audio can come back in on a strip
 *   basic  tiny built-in synth (used if forge_synth.js isn't loaded)
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
  };

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
    ensureStrip(id, mix) {
      if (this.strips.has(id)) return this.strips.get(id);
      const c = this.ctx, s = { in: c.createGain(), pan: c.createStereoPanner(), vol: c.createGain(), sendA: c.createGain(), sendB: c.createGain(), an: c.createAnalyser(), mix };
      s.an.fftSize = 512;
      s.in.connect(s.pan); s.pan.connect(s.vol); s.vol.connect(this.master); s.vol.connect(s.sendA); s.vol.connect(s.sendB); s.vol.connect(s.an);
      s.sendA.connect(this.verbIn); s.sendB.connect(this.delayIn);
      this.strips.set(id, s);
      return s;
    }
    removeStrip(id) { const s = this.strips.get(id); if (!s) return; try { s.vol.disconnect(); s.in.disconnect(); } catch (e) {} this.strips.delete(id); }
    applyMix() {
      if (!this.ctx) return;
      const now = this.ctx.currentTime;
      const mixes = [...this.strips.values()].map(s => s.mix);
      const anySolo = mixes.some(m => m && m.solo);
      for (const s of this.strips.values()) {
        const m = s.mix; if (!m) continue;
        const on = !m.mute && (!anySolo || m.solo);
        s.vol.gain.setTargetAtTime(on ? m.vol : 0, now, 0.02);
        s.pan.pan.setTargetAtTime(m.pan, now, 0.02);
        s.sendA.gain.setTargetAtTime(m.sendA, now, 0.02);
        s.sendB.gain.setTargetAtTime(m.sendB, now, 0.02);
      }
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
          const rep0 = Math.max(0, Math.floor((t0 - cs) / plen)), rep1 = Math.floor((Math.min(t1, ce) - 1 - cs) / plen);
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
      const strip = mix => {
        const s = { in: off.createGain(), pan: off.createStereoPanner(), vol: off.createGain(), a: off.createGain(), b: off.createGain() };
        s.in.connect(s.pan); s.pan.connect(s.vol); s.vol.connect(master); s.vol.connect(s.a); s.vol.connect(s.b); s.a.connect(verbIn); s.b.connect(dIn);
        s.pan.pan.value = mix.pan; s.vol.gain.value = mix.vol; s.a.gain.value = mix.sendA; s.b.gain.value = mix.sendB;
        return s;
      };
      // which tracks sound: the project's mute/solo, narrowed to trackIds for a stem
      const devMixes = [...P.devices.map(d => d.mix), ...P.tracks.filter(t => t.kind === 'audio').map(t => t.mix)].filter(Boolean);
      const anyDevSolo = devMixes.some(m => m.solo);
      const audible = mix => mix && !mix.mute && (!anyDevSolo || mix.solo);
      const tracks = this.activeTracks().filter(t => !trackIds || trackIds.includes(t.id));
      const insts = new Map(), strips = new Map();
      for (const tr of tracks) {
        if (tr.kind === 'midi') {
          const d = this.dev(tr.deviceId); if (!d || insts.has(d.id) || !audible(d.mix)) continue;
          const st = strip(d.mix); strips.set(d.id, st);
          const inst = await this._offlineDevice(off, d, st.in);
          if (!inst) throw new Error(d.name + ' cannot render offline');
          insts.set(d.id, inst);
          if (inst.syncAt) inst.syncAt(0);
        } else if (audible(tr.mix)) strips.set(tr.id, strip(tr.mix));
      }
      // notes: same rules as live playback (patterns repeat inside clips, clipped at clip end, swing)
      const at = tick => (tick - t0) * spt + this.swingDelay(tick);
      let notes = 0;
      for (const tr of tracks) {
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
      for (const inst of insts.values()) if (inst.flush) await inst.flush();
      if (onProgress) onProgress({ phase: 'render', notes });
      const buf = await off.startRendering();
      let chs = [buf.getChannelData(0).slice(0), buf.getChannelData(1).slice(0)];
      const L = Math.round(lenSec * sampleRate);
      if (loop) {            // what rings past the end belongs at the start of the next pass
        chs = chs.map(c => { const o = c.slice(0, L); for (let i = L; i < c.length; i++) o[(i - L) % L] += c[i]; return o; });
      }
      for (const inst of insts.values()) { try { inst.dispose(); } catch (e) {} }
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
