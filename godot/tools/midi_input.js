/* midi_input.js
 *
 * Web MIDI sibling of gamepad_input.js. Built for the M-VAVE FM-1
 * (stock firmware or Baud Girl's FM-1+VA) but generic enough for any
 * class-compliant USB-MIDI / BLE-MIDI device. Opens MIDI access,
 * auto-picks the FM-1 ports, and re-emits incoming messages as
 * window CustomEvents so each instrument tool can route them with a
 * handful of lines — same shape the Riffmaster tools already use.
 *
 *   midiinput-connected      {inName, outName}
 *   midiinput-disconnected   {}
 *   midiinput-note           {note, vel (0..1), raw (0..127), on, ch}
 *   midiinput-cc             {cc, value (0..127), norm (0..1), ch, target}
 *   midiinput-pitchbend      {value (-1..1), raw (0..16383), ch}
 *   midiinput-program        {program, ch}
 *   midiinput-aftertouch     {value (0..1), ch}
 *   midiinput-sysex          {data: Uint8Array}
 *   midiinput-realtime       {type: 'clock'|'start'|'continue'|'stop'|'sensing'|'reset'}
 *   midiinput-message        {data: Uint8Array, ts}   (everything, for monitors)
 *   midiinput-learned        {target, cc}
 *   midiinput-status         {status, detail}
 *
 * What we know about the FM-1 on the wire (ip2k/mvave-fm1-open-firmware
 * bench notes): class-compliant, VID:PID 4C4A:C755, one bidirectional
 * port named "FM-1" (macOS) / "FM-1 Midi" (Windows) / sometimes
 * "USB Composite Device" in Chrome on macOS. Sends NOTHING on its own
 * (no clock, no active sensing). Stock firmware accepts DX7 voice
 * dumps + parameter changes but never answers a dump request. In
 * updater mode it re-enumerates as "ota-FM-1" (4D4A:4155) — if you
 * see that name the synth is mid-flash, not playable.
 *
 * Whether the four knobs emit CC (and which numbers) differs between
 * stock and Baud Girl firmware and isn't documented — so every knob
 * target here is MIDI-LEARN: click LEARN, turn the knob, done. The
 * learned map is saved in localStorage and shared by every tool.
 *
 * Web MIDI needs Chrome or Edge (same requirement as the Baud Girl
 * installer). Firefox ships it behind a site-permission flow; Safari
 * doesn't have it.
 *
 * Usage:
 *   const mi = new MidiInput();
 *   mi.start();
 *   mountMidiOverlay(mi, { learnTargets: [{ id: 'fm.ratio', label: 'MOD RATIO', el: 'ratio' }] });
 *   window.addEventListener('midiinput-note', e => { if (e.detail.on) pluck(e.detail.note, e.detail.vel); });
 *   // echo the instrument back out to the FM-1's own engine:
 *   mi.echoPluck(midi, vel, durationMs);
 */
"use strict";

const MIDI_LS_KEY = 'mm_midi_prefs';
const MIDI_DEVICE_HINTS = [/fm-?1/i, /m-?vave/i, /mvave/i];
const MIDI_OTA_HINT = /ota-?fm-?1/i;

function _midiLoadPrefs() {
  try {
    const raw = localStorage.getItem(MIDI_LS_KEY);
    if (raw) return JSON.parse(raw);
  } catch (e) { /* private mode / blocked storage — run with defaults */ }
  return {};
}
function _midiSavePrefs(p) {
  try { localStorage.setItem(MIDI_LS_KEY, JSON.stringify(p)); } catch (e) { /* ignore */ }
}

function midiNoteNameMI(n) {
  const N = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B'];
  return N[((n % 12) + 12) % 12] + (Math.floor(n / 12) - 1);
}

class MidiInput {
  constructor(opts = {}) {
    const prefs = _midiLoadPrefs();
    this.access = null;
    this.input = null;
    this.output = null;
    this.supported = typeof navigator !== 'undefined' && !!navigator.requestMIDIAccess;
    this.sysexOk = false;
    this.status = 'idle';          // idle | unsupported | denied | no-device | connected | ota
    this.statusDetail = '';
    this.channel = prefs.channel ?? 0;          // input filter: 0 = omni, 1..16
    this.outChannel = prefs.outChannel ?? 1;    // 1..16
    this.outEnabled = prefs.outEnabled ?? false;
    this.ccMap = prefs.ccMap || {};             // targetId -> cc number
    this.preferredIn = prefs.inName || null;
    this.preferredOut = prefs.outName || null;
    this.learning = null;                       // targetId while learning
    this.heldNotes = new Set();
    this.lastEvent = '—';
    this.wantSysex = opts.sysex !== false;
    this._echoNote = -1;                        // last mono-echoed note
    this._onMsg = e => this._onMessage(e);
    this._onState = () => this._pickPorts();
  }

  _savePrefs() {
    _midiSavePrefs({
      channel: this.channel,
      outChannel: this.outChannel,
      outEnabled: this.outEnabled,
      ccMap: this.ccMap,
      inName: this.input ? this.input.name : this.preferredIn,
      outName: this.output ? this.output.name : this.preferredOut,
    });
  }

  _setStatus(status, detail) {
    this.status = status;
    this.statusDetail = detail || '';
    window.dispatchEvent(new CustomEvent('midiinput-status', { detail: { status, detail: this.statusDetail } }));
  }

  async start() {
    if (!this.supported) {
      this._setStatus('unsupported', 'Web MIDI needs Chrome or Edge.');
      return false;
    }
    try {
      this.access = await navigator.requestMIDIAccess({ sysex: this.wantSysex });
      this.sysexOk = !!this.access.sysexEnabled;
    } catch (e) {
      // SysEx denied — fall back to plain MIDI so notes still work.
      try {
        this.access = await navigator.requestMIDIAccess({ sysex: false });
        this.sysexOk = false;
      } catch (e2) {
        this._setStatus('denied', 'MIDI permission denied: ' + (e2 && e2.message || e2));
        return false;
      }
    }
    this.access.addEventListener('statechange', this._onState);
    this._pickPorts();
    return true;
  }

  stop() {
    if (this.input) this.input.removeEventListener('midimessage', this._onMsg);
    if (this.access) this.access.removeEventListener('statechange', this._onState);
    this.input = null; this.output = null; this.access = null;
    this._setStatus('idle');
  }

  inputs()  { return this.access ? [...this.access.inputs.values()]  : []; }
  outputs() { return this.access ? [...this.access.outputs.values()] : []; }

  _rank(port, preferredName) {
    if (!port) return -1;
    const name = port.name || '';
    if (MIDI_OTA_HINT.test(name)) return -2;
    if (preferredName && name === preferredName) return 3;
    if (MIDI_DEVICE_HINTS.some(rx => rx.test(name))) return 2;
    return 0;
  }

  _best(ports, preferredName) {
    let best = null, bestRank = -3;
    for (const p of ports) {
      const r = this._rank(p, preferredName);
      if (r > bestRank) { best = p; bestRank = r; }
    }
    return best;
  }

  _pickPorts() {
    if (!this.access) return;
    const ins = this.inputs(), outs = this.outputs();
    const ota = [...ins, ...outs].find(p => MIDI_OTA_HINT.test(p.name || ''));

    // Keep an explicitly selected port if it's still around.
    const stillIn  = this.input  && ins.find(p => p.id === this.input.id);
    const stillOut = this.output && outs.find(p => p.id === this.output.id);
    const nextIn  = stillIn  ? this.input  : this._best(ins,  this.preferredIn);
    const nextOut = stillOut ? this.output : this._best(outs, this.preferredOut);
    this._attachInput(nextIn);
    this.output = nextOut || null;

    if (ota && !this.input) {
      this._setStatus('ota', 'FM-1 is in updater mode (ota-FM-1). Finish / power-cycle, then rescan.');
      return;
    }
    if (!this.input && !this.output) {
      const was = this.status === 'connected';
      this._setStatus('no-device', ins.length + outs.length === 0
        ? 'no MIDI ports. plug the FM-1 in over USB-C (or pair BLE-MIDI).'
        : 'ports present but none selected.');
      if (was) window.dispatchEvent(new CustomEvent('midiinput-disconnected', {}));
      return;
    }
    const wasConnected = this.status === 'connected';
    this._setStatus('connected', (this.input ? 'in: ' + this.input.name : 'in: —') +
      ' · ' + (this.output ? 'out: ' + this.output.name : 'out: —'));
    if (!wasConnected) {
      window.dispatchEvent(new CustomEvent('midiinput-connected', {
        detail: { inName: this.input && this.input.name, outName: this.output && this.output.name }
      }));
    }
    this._savePrefs();
  }

  _attachInput(port) {
    if (this.input === port) return;
    if (this.input) this.input.removeEventListener('midimessage', this._onMsg);
    this.input = port || null;
    this.heldNotes.clear();
    if (this.input) this.input.addEventListener('midimessage', this._onMsg);
  }

  selectInput(id) {
    const p = this.inputs().find(x => x.id === id) || null;
    this._attachInput(p);
    this.preferredIn = p ? p.name : null;
    this._pickPorts();
  }
  selectOutput(id) {
    const p = this.outputs().find(x => x.id === id) || null;
    this.output = p;
    this.preferredOut = p ? p.name : null;
    this._pickPorts();
  }
  setChannel(ch)    { this.channel = ch | 0; this._savePrefs(); }
  setOutChannel(ch) { this.outChannel = Math.max(1, Math.min(16, ch | 0)); this._savePrefs(); }
  setOutEnabled(on) { this.outEnabled = !!on; if (!on) this.allNotesOff(); this._savePrefs(); }

  // ── CC learn ────────────────────────────────────────────────────
  learn(targetId) { this.learning = targetId; }
  cancelLearn()   { this.learning = null; }
  forget(targetId) { delete this.ccMap[targetId]; this._savePrefs(); }
  targetForCc(cc) {
    for (const k in this.ccMap) if (this.ccMap[k] === cc) return k;
    return null;
  }

  // ── Incoming ────────────────────────────────────────────────────
  _onMessage(e) {
    const d = e.data;
    if (!d || d.length === 0) return;
    window.dispatchEvent(new CustomEvent('midiinput-message', { detail: { data: d, ts: e.timeStamp } }));
    const st = d[0];
    if (st >= 0xF8) {
      const types = { 0xF8: 'clock', 0xFA: 'start', 0xFB: 'continue', 0xFC: 'stop', 0xFE: 'sensing', 0xFF: 'reset' };
      window.dispatchEvent(new CustomEvent('midiinput-realtime', { detail: { type: types[st] || ('0x' + st.toString(16)) } }));
      return;
    }
    if (st === 0xF0) {
      this.lastEvent = 'sysex ' + d.length + 'B';
      window.dispatchEvent(new CustomEvent('midiinput-sysex', { detail: { data: d } }));
      return;
    }
    if (st >= 0xF0) return;   // other system common — ignore
    const type = st & 0xF0;
    const ch = (st & 0x0F) + 1;
    if (this.channel !== 0 && ch !== this.channel) return;
    const a = d[1] ?? 0, b = d[2] ?? 0;
    switch (type) {
      case 0x90:
      case 0x80: {
        const on = type === 0x90 && b > 0;
        if (on) this.heldNotes.add(a); else this.heldNotes.delete(a);
        this.lastEvent = (on ? 'note on ' : 'note off ') + midiNoteNameMI(a) + (on ? ' v' + b : '');
        window.dispatchEvent(new CustomEvent('midiinput-note', {
          detail: { note: a, vel: on ? b / 127 : 0, raw: b, on, ch }
        }));
        break;
      }
      case 0xB0: {
        if (this.learning) {
          const t = this.learning;
          this.learning = null;
          this.ccMap[t] = a;
          this._savePrefs();
          window.dispatchEvent(new CustomEvent('midiinput-learned', { detail: { target: t, cc: a } }));
        }
        if (a === 123 || a === 120) this.heldNotes.clear();
        this.lastEvent = 'cc ' + a + ' = ' + b;
        window.dispatchEvent(new CustomEvent('midiinput-cc', {
          detail: { cc: a, value: b, norm: b / 127, ch, target: this.targetForCc(a) }
        }));
        break;
      }
      case 0xE0: {
        const raw = a | (b << 7);
        this.lastEvent = 'bend ' + ((raw - 8192) / 8192).toFixed(2);
        window.dispatchEvent(new CustomEvent('midiinput-pitchbend', {
          detail: { value: (raw - 8192) / 8192, raw, ch }
        }));
        break;
      }
      case 0xC0:
        this.lastEvent = 'program ' + a;
        window.dispatchEvent(new CustomEvent('midiinput-program', { detail: { program: a, ch } }));
        break;
      case 0xD0:
        window.dispatchEvent(new CustomEvent('midiinput-aftertouch', { detail: { value: a / 127, ch } }));
        break;
      case 0xA0:
        window.dispatchEvent(new CustomEvent('midiinput-aftertouch', { detail: { value: b / 127, note: a, ch } }));
        break;
    }
  }

  // ── Outgoing (raw — sends whenever an output port is selected) ──
  send(bytes) {
    if (!this.output) return false;
    try { this.output.send(bytes); return true; }
    catch (e) { this._setStatus(this.status, 'send failed: ' + (e.message || e)); return false; }
  }
  _st(type, ch) { return type | (((ch || this.outChannel) - 1) & 0x0F); }
  noteOn(note, vel01 = 0.8, ch)  { return this.send([this._st(0x90, ch), note & 0x7F, Math.max(1, Math.min(127, Math.round(vel01 * 127)))]); }
  noteOff(note, ch)              { return this.send([this._st(0x80, ch), note & 0x7F, 0]); }
  cc(cc, value, ch)              { return this.send([this._st(0xB0, ch), cc & 0x7F, Math.max(0, Math.min(127, value | 0))]); }
  programChange(program, ch)     { return this.send([this._st(0xC0, ch), program & 0x7F]); }
  pitchBend(norm, ch) {
    const raw = Math.max(0, Math.min(16383, Math.round(8192 + norm * 8191)));
    return this.send([this._st(0xE0, ch), raw & 0x7F, (raw >> 7) & 0x7F]);
  }
  allNotesOff(ch) {
    this._echoNote = -1;
    if (!this.output) return false;
    const chans = ch ? [ch] : [this.outChannel];
    for (const c of chans) { this.cc(123, 0, c); this.cc(120, 0, c); }
    return true;
  }
  sendSysex(bytes) {
    if (!this.sysexOk) { this._setStatus(this.status, 'SysEx not permitted — reload and allow "control and reprogram MIDI devices".'); return false; }
    if (bytes[0] !== 0xF0 || bytes[bytes.length - 1] !== 0xF7) return false;
    return this.send(bytes);
  }

  // ── Firmware identity (read-only) ──────────────────────────────
  // Sends the vendor identity query the official updater opens with
  // (F0 00 32 45 00 00 00 40 7F F7) and decodes the reply into e.g.
  // "FM-1_015" (stock) or "FM-1_092" (Baud Girl FM-1+VA). This is the
  // ONLY message with the 00 32 45 header the tools ever send — the
  // rest of that protocol is the flasher. Resolves null on timeout.
  identify(timeoutMs = 3000) {
    return new Promise(resolve => {
      if (!this.output || !this.input) return resolve(null);
      if (!this.sysexOk) return resolve({ error: 'SysEx not permitted' });
      const q = [0xF0, 0x00, 0x32, 0x45, 0x00, 0x00, 0x00, 0x40, 0x7F, 0xF7];
      let done = false;
      const onSx = e => {
        const d = e.detail.data;
        if (d.length < 20 || d[1] !== 0x00 || d[2] !== 0x32 || d[3] !== 0x45) return;
        const id = fm1DecodeIdentity(d);
        if (!id) return;
        done = true; window.removeEventListener('midiinput-sysex', onSx); resolve(id);
      };
      window.addEventListener('midiinput-sysex', onSx);
      this.send(q);
      setTimeout(() => { if (!done) { window.removeEventListener('midiinput-sysex', onSx); resolve(null); } }, timeoutMs);
    });
  }

  // ── Echo helpers (tool-facing — gated by the OUT toggle) ────────
  // A one-shot: note on, timed note off. For pluck-style instruments.
  echoPluck(note, vel01, durMs) {
    if (!this.outEnabled || !this.output) return;
    if (note < 0 || note > 127) return;
    this.noteOn(note, vel01);
    setTimeout(() => this.noteOff(note), Math.max(30, Math.min(8000, durMs | 0)));
  }
  // Mono legato: releases the previous echoed note, holds the new one.
  echoMono(note, vel01) {
    if (!this.outEnabled || !this.output) return;
    if (this._echoNote >= 0 && this._echoNote !== note) this.noteOff(this._echoNote);
    if (this._echoNote !== note) this.noteOn(note, vel01);
    this._echoNote = note;
  }
  echoRelease() {
    if (this._echoNote >= 0 && this.output) this.noteOff(this._echoNote);
    this._echoNote = -1;
  }
  // Poly: caller tracks pairs.
  echoNoteOn(note, vel01)  { if (this.outEnabled && this.output) this.noteOn(note, vel01); }
  echoNoteOff(note)        { if (this.output) this.noteOff(note); }

  snapshot() {
    return {
      status: this.status,
      detail: this.statusDetail,
      inName: this.input ? this.input.name : null,
      outName: this.output ? this.output.name : null,
      held: [...this.heldNotes].sort((a, b) => a - b),
      last: this.lastEvent,
      sysex: this.sysexOk,
      outEnabled: this.outEnabled,
    };
  }
}

// ── FM-1 identity reply decoder ────────────────────────────────────
// Body between F0 and F7 is a 7-bit LSB-first bitstream that unpacks
// to a 34-byte JieLi ID block starting 00 59 11; bytes 6..30 hold
// "<model>_<version>". Mirrors fm1_identify.py in
// ip2k/mvave-fm1-open-firmware. Returns {name, model, version,
// firmware: 'stock'|'baudgirl'} or null.
function fm1DecodeIdentity(bytes) {
  const d = [...bytes];
  if (d[0] !== 0xF0 || d[d.length - 1] !== 0xF7) return null;
  let acc = 0, bits = 0; const out = [];
  for (const b of d.slice(1, -1)) {
    acc |= (b & 0x7F) << bits; bits += 7;
    while (bits >= 8) { out.push(acc & 0xFF); acc >>>= 8; bits -= 8; }
  }
  if (out.length < 31 || out[0] !== 0x00 || out[1] !== 0x59 || out[2] !== 0x11) return null;
  const field = String.fromCharCode(...out.slice(6, 31));
  const m = field.match(/([A-Za-z0-9-]{2,})_(\d+)/);
  if (!m) return null;
  const version = parseInt(m[2], 10);
  return {
    name: m[1] + '_' + String(version).padStart(3, '0'),
    model: m[1], version,
    // Stock ships as 014 / 015; Baud Girl's FM-1+VA builds are 020+.
    firmware: version >= 20 ? 'baudgirl' : 'stock',
  };
}

// ── CC → <input type=range> binding ────────────────────────────────
// Scales the 0..127 CC over the slider's min/max/step, sets it, and
// fires an 'input' event so the tool's own listeners run. Returns an
// unbind function.
function bindCcToRange(mi, targetId, rangeEl) {
  const el = typeof rangeEl === 'string' ? document.getElementById(rangeEl) : rangeEl;
  if (!el) return () => {};
  const handler = e => {
    if (e.detail.target !== targetId) return;
    const min = parseFloat(el.min || 0), max = parseFloat(el.max || 100);
    const step = parseFloat(el.step || 1) || 1;
    let v = min + e.detail.norm * (max - min);
    v = Math.round(v / step) * step;
    const decimals = (String(step).split('.')[1] || '').length;
    el.value = v.toFixed(decimals);
    el.dispatchEvent(new Event('input', { bubbles: true }));
    el.dispatchEvent(new Event('change', { bubbles: true }));
  };
  window.addEventListener('midiinput-cc', handler);
  return () => window.removeEventListener('midiinput-cc', handler);
}

// ── Connection / learn overlay ─────────────────────────────────────
// Sits bottom-right, just left of the Riffmaster gamepad panel (which
// is 280px wide + 10px margin). opts.learnTargets: [{id, label, el?}]
// — entries with `el` (a range input id) are auto-bound via
// bindCcToRange so a learned knob drives the slider immediately.
function mountMidiOverlay(mi, opts = {}) {
  const targets = opts.learnTargets || [];
  targets.forEach(t => { if (t.el) bindCcToRange(mi, t.id, t.el); });

  const panel = document.createElement('div');
  panel.style.cssText = `
    position: fixed; bottom: 10px; right: ${opts.right || '300px'};
    background: rgba(0,0,0,0.78);
    color: #d8a060;
    font-family: "Courier New", monospace;
    font-size: 11px;
    padding: 8px 12px;
    border: 1px solid #553318;
    width: 250px; max-width: 250px;
    z-index: 999;
  `;
  const sel = 'background:#1a1410;color:#ffd896;border:1px solid #553318;font-family:inherit;font-size:10px;max-width:100%;';
  const btn = 'background:#3a2614;color:#ffd896;border:1px solid #d8a060;padding:2px 8px;font-family:inherit;font-size:10px;cursor:pointer;';
  const btnDim = 'background:transparent;color:#7a5828;border:1px solid #553318;padding:2px 8px;font-family:inherit;font-size:10px;cursor:pointer;';
  panel.innerHTML = `
    <div style="display:flex;justify-content:space-between;align-items:baseline;">
      <div style="color:#ffd896;letter-spacing:0.12em;font-weight:bold;margin-bottom:4px;">FM-1 · MIDI</div>
      <a href="fm1_console.html" style="color:#7a5828;font-size:9px;text-decoration:none;letter-spacing:0.08em;" title="FM-1 console: monitor, program change, DX7 patch push">console ↗</a>
    </div>
    <div id="mio-status" style="color:#c64a3a;">starting…</div>
    <div style="display:grid;grid-template-columns:28px 1fr;gap:3px 6px;margin-top:5px;align-items:center;color:#7a5828;font-size:10px;">
      <span>IN</span><select id="mio-in" style="${sel}"></select>
      <span>OUT</span><select id="mio-out" style="${sel}"></select>
      <span>CH</span>
      <div style="display:flex;gap:4px;align-items:center;">
        <select id="mio-ch" style="${sel}" title="input channel filter"></select>
        <label style="display:flex;align-items:center;gap:3px;cursor:pointer;" title="Mirror what this instrument plays out to the FM-1's own 6-op engine.">
          <input type="checkbox" id="mio-out-en" style="margin:0;"> OUT→FM-1
        </label>
      </div>
    </div>
    <div id="mio-held" style="color:#d8a060;font-size:10px;margin-top:5px;">held: —</div>
    <div id="mio-last" style="color:#7a5828;font-size:10px;margin-top:2px;font-style:italic;">last: —</div>
    <div id="mio-learn" style="margin-top:6px;${targets.length ? '' : 'display:none;'}">
      <div style="display:flex;gap:4px;align-items:center;">
        <select id="mio-target" style="${sel}flex:1;"></select>
        <button id="mio-learn-btn" style="${btn}">LEARN</button>
        <button id="mio-forget" style="${btnDim}" title="forget this target's CC">✕</button>
      </div>
      <div id="mio-map" style="color:#88b87a;font-size:10px;margin-top:3px;line-height:1.5;"></div>
    </div>
    <div style="margin-top:6px;display:flex;gap:4px;">
      <button id="mio-panic" style="${btnDim}" title="all notes off on the OUT port">PANIC</button>
      <button id="mio-rescan" style="${btnDim}">RESCAN</button>
    </div>
    <div id="mio-msg" style="color:#7a5828;font-size:10px;margin-top:4px;font-style:italic;"></div>
  `;
  document.body.appendChild(panel);
  const $ = id => panel.querySelector('#' + id);
  const statusEl = $('mio-status'), inSel = $('mio-in'), outSel = $('mio-out'), chSel = $('mio-ch');
  const outEn = $('mio-out-en'), heldEl = $('mio-held'), lastEl = $('mio-last');
  const targetSel = $('mio-target'), learnBtn = $('mio-learn-btn'), forgetBtn = $('mio-forget');
  const mapEl = $('mio-map'), msgEl = $('mio-msg');

  chSel.innerHTML = '<option value="0">omni</option>' +
    Array.from({ length: 16 }, (_, i) => `<option value="${i + 1}">ch ${i + 1}</option>`).join('');
  chSel.value = String(mi.channel);
  outEn.checked = mi.outEnabled;
  targets.forEach(t => {
    const o = document.createElement('option');
    o.value = t.id; o.textContent = t.label; targetSel.appendChild(o);
  });

  function fillPorts() {
    const mk = (selEl, ports, current) => {
      selEl.innerHTML = '<option value="">—</option>';
      ports.forEach(p => {
        const o = document.createElement('option');
        o.value = p.id; o.textContent = (p.name || p.id).slice(0, 30);
        if (current && current.id === p.id) o.selected = true;
        selEl.appendChild(o);
      });
    };
    mk(inSel, mi.inputs(), mi.input);
    mk(outSel, mi.outputs(), mi.output);
  }
  function refreshMap() {
    const rows = targets.filter(t => mi.ccMap[t.id] !== undefined)
      .map(t => t.label + ' ← CC ' + mi.ccMap[t.id]);
    mapEl.textContent = rows.length ? rows.join(' · ') : 'no knobs learned yet.';
  }
  function refreshStatus() {
    const colors = { connected: '#a8e89c', ota: '#f0b94a', denied: '#c64a3a', unsupported: '#c64a3a', 'no-device': '#c64a3a', idle: '#7a5828' };
    statusEl.style.color = colors[mi.status] || '#7a5828';
    statusEl.textContent = mi.status === 'connected'
      ? ('connected' + (mi.sysexOk ? ' · sysex ok' : ' · no sysex'))
      : (mi.status + (mi.statusDetail ? ' · ' + mi.statusDetail : ''));
    statusEl.title = mi.statusDetail || '';
    fillPorts();
  }
  refreshStatus(); refreshMap();

  window.addEventListener('midiinput-status', refreshStatus);
  window.addEventListener('midiinput-connected', refreshStatus);
  window.addEventListener('midiinput-disconnected', refreshStatus);
  window.addEventListener('midiinput-learned', e => {
    learnBtn.textContent = 'LEARN';
    msgEl.textContent = (targets.find(t => t.id === e.detail.target) || {}).label + ' ← CC ' + e.detail.cc;
    refreshMap();
  });
  inSel.addEventListener('change', () => mi.selectInput(inSel.value));
  outSel.addEventListener('change', () => mi.selectOutput(outSel.value));
  chSel.addEventListener('change', () => mi.setChannel(parseInt(chSel.value)));
  outEn.addEventListener('change', () => {
    mi.setOutEnabled(outEn.checked);
    msgEl.textContent = outEn.checked
      ? 'instrument notes now mirror to the FM-1 engine.'
      : 'OUT off — browser audio only.';
  });
  learnBtn.addEventListener('click', () => {
    if (mi.learning) { mi.cancelLearn(); learnBtn.textContent = 'LEARN'; msgEl.textContent = 'learn cancelled.'; return; }
    if (!targetSel.value) return;
    mi.learn(targetSel.value);
    learnBtn.textContent = 'TURN IT…';
    msgEl.textContent = 'turn the knob on the FM-1 you want to drive ' + targetSel.selectedOptions[0].textContent + '.';
  });
  forgetBtn.addEventListener('click', () => { mi.forget(targetSel.value); refreshMap(); msgEl.textContent = 'forgot.'; });
  $('mio-panic').addEventListener('click', () => { mi.allNotesOff(); msgEl.textContent = 'all notes off sent.'; });
  $('mio-rescan').addEventListener('click', () => { mi._pickPorts(); refreshStatus(); });

  setInterval(() => {
    const s = mi.snapshot();
    heldEl.textContent = s.held.length ? 'held: ' + s.held.map(midiNoteNameMI).join(' ') : 'held: —';
    lastEl.textContent = 'last: ' + s.last;
  }, 100);
  return panel;
}
