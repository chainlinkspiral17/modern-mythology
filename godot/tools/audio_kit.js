/* audio_kit.js
 *
 * Shared audio plumbing for FIELD RECORDER and TAPE STUDIO (and any
 * later tool that records). Plain script, no build step, works from
 * file:// in Chrome / Edge.
 *
 *   AK.inputs        list / open audio inputs with every voice-call
 *                    "helper" (echo cancel, noise suppress, AGC) OFF —
 *                    those wreck music and field recordings.
 *   AK.Capture       always-on PCM capture (AudioWorklet, ScriptProcessor
 *                    fallback) with a rolling pre-roll buffer, meters,
 *                    markers. Pre-roll means the take can start up to N
 *                    seconds BEFORE you pressed record.
 *   AK.wav           encode 16/24-bit PCM WAV with bext (BWF), LIST/INFO,
 *                    smpl (loop points Godot reads) and an mmjs chunk
 *                    (our metadata as JSON); parse those chunks back.
 *   AK.lib           IndexedDB take library shared by every tool page,
 *                    plus a BroadcastChannel so open pages refresh.
 *   AK.game          link the godot/ folder once (File System Access),
 *                    read the music catalog, list tracks with no audio
 *                    yet ("wanted"), write files straight into assets/.
 *   AK.dsp           offline cleanup: high-pass, normalise (peak or
 *                    approx. LUFS), fades, trim, seamless loop crossfade,
 *                    spectral noise gate, mixdown.
 *   AK.draw          waveform, spectrogram and meter painting.
 *
 * Godot side: AudioMgr._load_audio() falls back from a catalog
 * .ogg/.mp3 path to the same name with .wav, and loads raw WAVs with
 * AudioStreamWAV.load_from_buffer — which honours the smpl loop chunk.
 */
"use strict";

const AK = {};

// ═══════════════════════════════════════════════════════════════════
// Inputs
// ═══════════════════════════════════════════════════════════════════
AK.inputs = {
  async list() {
    if (!navigator.mediaDevices || !navigator.mediaDevices.enumerateDevices) return [];
    const ds = await navigator.mediaDevices.enumerateDevices();
    return ds.filter(d => d.kind === 'audioinput');
  },
  // Raw input: no processing, stereo if the device has it.
  async open(deviceId, channels = 2) {
    const audio = {
      echoCancellation: false, noiseSuppression: false, autoGainControl: false,
      channelCount: { ideal: channels }, sampleRate: { ideal: 48000 },
    };
    if (deviceId) audio.deviceId = { exact: deviceId };
    return navigator.mediaDevices.getUserMedia({ audio, video: false });
  },
  // A friendly label for the devices this project actually uses.
  hint(label) {
    const l = label || '';
    if (/felucca/i.test(l)) return 'FM-1 · Felucca / SLOOP USB audio';
    if (/fm-?1/i.test(l)) return 'FM-1 USB audio';
    if (/zoom|tascam|h[1-6]n|\bf[368]\b|dr-[0-9]|sound ?devices|mixpre|tentacle|rode|wireless go/i.test(l)) return 'field recorder / USB mic';
    if (/steam deck|acp|internal|built-in|analog stereo/i.test(l)) return 'Deck built-in';
    return '';
  },
};

// ═══════════════════════════════════════════════════════════════════
// Capture
// ═══════════════════════════════════════════════════════════════════
const AK_CAPTURE_WORKLET = `
class AKCapture extends AudioWorkletProcessor {
  constructor() { super(); this.alive = true; this.port.onmessage = e => { if (e.data === 'stop') this.alive = false; }; }
  process(inputs) {
    const inp = inputs[0];
    if (inp && inp.length && inp[0].length) {
      const chans = inp.map(c => c.slice(0));
      this.port.postMessage(chans, chans.map(c => c.buffer));
    }
    return this.alive;
  }
}
registerProcessor('ak-capture', AKCapture);
`;

AK.Capture = class {
  // opts: preRollSec, onChunk(chans), maxChannels
  constructor(ctx, sourceNode, opts = {}) {
    this.ctx = ctx;
    this.source = sourceNode;
    this.sampleRate = ctx.sampleRate;
    this.preRollSec = opts.preRollSec ?? 10;
    this.maxChannels = opts.maxChannels ?? 2;
    this.onChunk = opts.onChunk || null;
    this.ring = [];             // pre-roll: arrays of Float32Array per channel
    this.ringFrames = 0;
    this.take = null;           // { chunks, frames, preRollFrames, markers }
    this.frameClock = 0;        // frames seen since start()
    this.peak = [0, 0];         // decaying peak per channel (linear)
    this.hold = [0, 0];         // peak hold (linear)
    this.rms = [0, 0];
    this.clipped = false;
    this.channels = 1;
    this.node = null;
    this.sink = null;
    this.mode = '';
  }

  async start() {
    this.sink = this.ctx.createGain();
    this.sink.gain.value = 0;
    this.sink.connect(this.ctx.destination);
    try {
      if (!this.ctx.__akWorklet) {
        const url = URL.createObjectURL(new Blob([AK_CAPTURE_WORKLET], { type: 'application/javascript' }));
        await this.ctx.audioWorklet.addModule(url);
        this.ctx.__akWorklet = true;
      }
      this.node = new AudioWorkletNode(this.ctx, 'ak-capture', {
        numberOfInputs: 1, numberOfOutputs: 1, outputChannelCount: [1],
        channelCount: this.maxChannels, channelCountMode: 'explicit', channelInterpretation: 'discrete',
      });
      this.node.port.onmessage = e => this._chunk(e.data);
      this.mode = 'worklet';
    } catch (e) {
      // ScriptProcessor fallback (deprecated but universal).
      const sp = this.ctx.createScriptProcessor(4096, this.maxChannels, 1);
      sp.onaudioprocess = ev => {
        const ib = ev.inputBuffer, chans = [];
        for (let c = 0; c < ib.numberOfChannels; c++) chans.push(ib.getChannelData(c).slice(0));
        this._chunk(chans);
      };
      this.node = sp;
      this.mode = 'scriptprocessor';
    }
    this.source.connect(this.node);
    this.node.connect(this.sink);
  }

  stop() {
    try { this.source.disconnect(this.node); } catch (e) { /* already */ }
    if (this.node && this.node.port) this.node.port.postMessage('stop');
    try { this.node.disconnect(); this.sink.disconnect(); } catch (e) { /* ignore */ }
    this.node = null;
  }

  _chunk(chans) {
    if (!chans || !chans.length) return;
    // Mono sources come in as 2 identical channels with channelCount 2 —
    // fine; we record what we get.
    this.channels = Math.min(chans.length, this.maxChannels);
    const n = chans[0].length;
    this.frameClock += n;
    for (let c = 0; c < this.channels; c++) {
      const d = chans[c];
      let pk = 0, sq = 0;
      for (let i = 0; i < n; i++) { const v = d[i], a = v < 0 ? -v : v; if (a > pk) pk = a; sq += v * v; }
      if (pk >= 0.999) this.clipped = true;
      this.peak[c] = Math.max(pk, this.peak[c] * 0.93);
      this.hold[c] = Math.max(pk, this.hold[c] * 0.995);
      this.rms[c] = Math.sqrt(sq / n) * 0.3 + this.rms[c] * 0.7;
    }
    const kept = chans.slice(0, this.channels);
    // pre-roll ring
    this.ring.push(kept);
    this.ringFrames += n;
    const maxRing = Math.round(this.preRollSec * this.sampleRate);
    while (this.ringFrames - this.ring[0][0].length >= maxRing && this.ring.length > 1) {
      this.ringFrames -= this.ring.shift()[0].length;
    }
    if (this.take) { this.take.chunks.push(kept); this.take.frames += n; }
    if (this.onChunk) this.onChunk(kept);
  }

  recording() { return !!this.take; }
  // includePreRoll: seconds of the ring to prepend (0 = none).
  begin(includePreRollSec = 0) {
    const want = Math.round(Math.max(0, includePreRollSec) * this.sampleRate);
    const chunks = [];
    let frames = 0;
    for (let i = this.ring.length - 1; i >= 0 && frames < want; i--) { chunks.unshift(this.ring[i]); frames += this.ring[i][0].length; }
    // trim the oldest chunk so pre-roll is exactly `want` (or what we have)
    if (frames > want && chunks.length) {
      const cut = frames - want;
      chunks[0] = chunks[0].map(c => c.slice(cut));
      frames = want;
    }
    this.take = { chunks, frames, preRollFrames: frames, markers: [], startedAt: new Date() };
    this.clipped = false;
  }
  mark(label) {
    if (!this.take) return null;
    const m = { frame: this.take.frames, label: label || ('M' + (this.take.markers.length + 1)) };
    this.take.markers.push(m);
    return m;
  }
  end() {
    const t = this.take;
    this.take = null;
    if (!t) return null;
    const chans = AK.util.concat(t.chunks, this.channels);
    return { channels: chans, sampleRate: this.sampleRate, preRollFrames: t.preRollFrames,
             markers: t.markers, startedAt: t.startedAt, clipped: this.clipped };
  }
  elapsedSec() { return this.take ? this.take.frames / this.sampleRate : 0; }
  resetClip() { this.clipped = false; this.hold = [0, 0]; }
};

// ═══════════════════════════════════════════════════════════════════
// Small utilities
// ═══════════════════════════════════════════════════════════════════
AK.util = {
  concat(chunks, nch) {
    let total = 0;
    for (const ch of chunks) total += ch[0].length;
    const out = [];
    for (let c = 0; c < nch; c++) {
      const o = new Float32Array(total);
      let off = 0;
      for (const ch of chunks) { const src = ch[c] || ch[0]; o.set(src, off); off += src.length; }
      out.push(o);
    }
    return out;
  },
  db(lin) { return lin <= 1e-9 ? -180 : 20 * Math.log10(lin); },
  lin(db) { return Math.pow(10, db / 20); },
  fmtTime(sec) {
    sec = Math.max(0, sec);
    const m = Math.floor(sec / 60), s = sec - m * 60;
    return String(m).padStart(2, '0') + ':' + s.toFixed(1).padStart(4, '0');
  },
  slug(s) {
    return String(s || '').toLowerCase().replace(/[^a-z0-9]+/g, '_').replace(/^_+|_+$/g, '').slice(0, 60) || 'take';
  },
  stamp(d = new Date()) {
    const p = n => String(n).padStart(2, '0');
    return d.getFullYear() + p(d.getMonth() + 1) + p(d.getDate()) + '_' + p(d.getHours()) + p(d.getMinutes()) + p(d.getSeconds());
  },
  uid() { return 'tk_' + Date.now().toString(36) + '_' + Math.random().toString(36).slice(2, 8); },
  peakOf(chs) { let p = 0; for (const c of chs) for (let i = 0; i < c.length; i++) { const a = Math.abs(c[i]); if (a > p) p = a; } return p; },
  rmsOf(chs) { let s = 0, n = 0; for (const c of chs) { for (let i = 0; i < c.length; i++) s += c[i] * c[i]; n += c.length; } return n ? Math.sqrt(s / n) : 0; },
  toBuffer(ctx, chs, sr) {
    const b = ctx.createBuffer(chs.length, chs[0].length || 1, sr);
    chs.forEach((c, i) => b.copyToChannel(c, i));
    return b;
  },
  fromBuffer(buf) {
    const out = [];
    for (let c = 0; c < buf.numberOfChannels; c++) out.push(buf.getChannelData(c).slice(0));
    return out;
  },
  download(blob, name) {
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = name;
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(a.href), 4000);
  },
};

// ═══════════════════════════════════════════════════════════════════
// WAV
// ═══════════════════════════════════════════════════════════════════
AK.wav = {
  // channels: Float32Array[]; opts: bitDepth 16|24, meta {title, comment,
  // keywords, date, originator, description, ...anything → mmjs},
  // loop {start, end} in frames, markers [{frame,label}]
  encode(channels, sampleRate, opts = {}) {
    const bits = opts.bitDepth === 16 ? 16 : 24;
    const nch = channels.length, frames = channels[0].length;
    const bps = bits / 8, block = nch * bps;
    const chunks = [];
    const enc = new TextEncoder();
    const mk = (id, bytes) => chunks.push({ id, bytes });

    // fmt
    const fmt = new DataView(new ArrayBuffer(16));
    fmt.setUint16(0, 1, true); fmt.setUint16(2, nch, true);
    fmt.setUint32(4, sampleRate, true); fmt.setUint32(8, sampleRate * block, true);
    fmt.setUint16(12, block, true); fmt.setUint16(14, bits, true);
    mk('fmt ', new Uint8Array(fmt.buffer));

    const meta = opts.meta || {};
    // bext (Broadcast WAV v1, 602 bytes + coding history)
    {
      const b = new Uint8Array(602);
      const put = (str, off, len) => { const e = enc.encode(String(str || '')).slice(0, len); b.set(e, off); };
      const d = meta.date ? new Date(meta.date) : new Date();
      const p = n => String(n).padStart(2, '0');
      put(meta.description || meta.title || '', 0, 256);
      put(meta.originator || 'Modern Mythology tools', 256, 32);
      put(meta.originatorRef || (meta.id || ''), 288, 32);
      put(d.getFullYear() + '-' + p(d.getMonth() + 1) + '-' + p(d.getDate()), 320, 10);
      put(p(d.getHours()) + ':' + p(d.getMinutes()) + ':' + p(d.getSeconds()), 330, 8);
      const dv = new DataView(b.buffer);
      const tr = Math.max(0, Math.round(meta.timeReference || 0));
      dv.setUint32(338, tr >>> 0, true); dv.setUint32(342, Math.floor(tr / 4294967296), true);
      dv.setUint16(346, 1, true);   // version 1
      mk('bext', b);
    }
    // LIST/INFO
    {
      const info = [];
      const add = (id, v) => { if (v === undefined || v === null || v === '') return; info.push([id, enc.encode(String(v) + '\0')]); };
      add('INAM', meta.title); add('ICMT', meta.comment); add('IKEY', (meta.tags || []).join('; '));
      add('ICRD', meta.date ? new Date(meta.date).toISOString().slice(0, 10) : undefined);
      add('ISFT', 'Modern Mythology audio_kit'); add('IART', meta.artist);
      if (info.length) {
        let size = 4;
        for (const [, v] of info) size += 8 + v.length + (v.length & 1);
        const out = new Uint8Array(size);
        const dv = new DataView(out.buffer);
        out.set(enc.encode('INFO'), 0);
        let o = 4;
        for (const [id, v] of info) {
          out.set(enc.encode(id), o); dv.setUint32(o + 4, v.length, true); out.set(v, o + 8);
          o += 8 + v.length + (v.length & 1);
        }
        mk('LIST', out);
      }
    }
    // smpl (loop points — Godot's WAV loader reads these)
    if (opts.loop && opts.loop.end > opts.loop.start) {
      const s = new DataView(new ArrayBuffer(36 + 24));
      s.setUint32(8, Math.round(1e9 / sampleRate), true);
      s.setUint32(12, 60, true);
      s.setUint32(28, 1, true);              // one loop
      s.setUint32(36 + 0, 0, true);          // cue id
      s.setUint32(36 + 4, 0, true);          // forward
      s.setUint32(36 + 8, Math.max(0, opts.loop.start | 0), true);
      s.setUint32(36 + 12, Math.min(frames - 1, opts.loop.end | 0), true);
      mk('smpl', new Uint8Array(s.buffer));
    }
    // cue (markers) — read by most editors
    if (opts.markers && opts.markers.length) {
      const ms = opts.markers.slice(0, 500);
      const dv = new DataView(new ArrayBuffer(4 + ms.length * 24));
      dv.setUint32(0, ms.length, true);
      ms.forEach((m, i) => {
        const o = 4 + i * 24;
        dv.setUint32(o, i + 1, true); dv.setUint32(o + 4, m.frame | 0, true);
        dv.setUint8(o + 8, 0x64); dv.setUint8(o + 9, 0x61); dv.setUint8(o + 10, 0x74); dv.setUint8(o + 11, 0x61); // 'data'
        dv.setUint32(o + 20, m.frame | 0, true);
      });
      mk('cue ', new Uint8Array(dv.buffer));
    }
    // mmjs — our metadata, verbatim JSON (field_ingest.py reads it)
    {
      const j = enc.encode(JSON.stringify(Object.assign({}, meta, {
        markers: opts.markers || [], loop: opts.loop || null, sampleRate, channels: nch, frames,
      })));
      mk('mmjs', j);
    }
    // data
    const dataBytes = frames * block;
    let total = 4;
    for (const c of chunks) total += 8 + c.bytes.length + (c.bytes.length & 1);
    total += 8 + dataBytes + (dataBytes & 1);
    const buf = new ArrayBuffer(8 + total);
    const dv = new DataView(buf), u8 = new Uint8Array(buf);
    u8.set(enc.encode('RIFF'), 0); dv.setUint32(4, total, true); u8.set(enc.encode('WAVE'), 8);
    let o = 12;
    for (const c of chunks) {
      u8.set(enc.encode(c.id), o); dv.setUint32(o + 4, c.bytes.length, true); u8.set(c.bytes, o + 8);
      o += 8 + c.bytes.length + (c.bytes.length & 1);
    }
    u8.set(enc.encode('data'), o); dv.setUint32(o + 4, dataBytes, true); o += 8;
    // TPDF dither when going to 16 bit
    for (let i = 0; i < frames; i++) {
      for (let c = 0; c < nch; c++) {
        let v = channels[c][i];
        if (v > 1) v = 1; else if (v < -1) v = -1;
        if (bits === 16) {
          let s = v * 32767 + (Math.random() - Math.random());
          s = Math.max(-32768, Math.min(32767, Math.round(s)));
          dv.setInt16(o, s, true); o += 2;
        } else {
          let s = Math.max(-8388608, Math.min(8388607, Math.round(v * 8388607)));
          dv.setUint8(o, s & 0xFF); dv.setUint8(o + 1, (s >> 8) & 0xFF); dv.setUint8(o + 2, (s >> 16) & 0xFF); o += 3;
        }
      }
    }
    return new Blob([buf], { type: 'audio/wav' });
  },

  // Returns { chunks: {id: Uint8Array}, info: {INAM..}, bext: {...}, mmjs: obj|null, smpl: {start,end}|null }
  parseChunks(arrayBuffer) {
    const dv = new DataView(arrayBuffer), u8 = new Uint8Array(arrayBuffer);
    const dec = new TextDecoder();
    const id = o => String.fromCharCode(u8[o], u8[o + 1], u8[o + 2], u8[o + 3]);
    const out = { chunks: {}, info: {}, bext: null, mmjs: null, smpl: null };
    if (u8.length < 12 || id(0) !== 'RIFF' || id(8) !== 'WAVE') return out;
    let o = 12;
    while (o + 8 <= u8.length) {
      const cid = id(o), size = dv.getUint32(o + 4, true);
      const body = u8.subarray(o + 8, Math.min(u8.length, o + 8 + size));
      out.chunks[cid] = body;
      if (cid === 'LIST' && dec.decode(body.subarray(0, 4)) === 'INFO') {
        let p = 4;
        while (p + 8 <= body.length) {
          const sid = dec.decode(body.subarray(p, p + 4));
          const sz = new DataView(body.buffer, body.byteOffset + p + 4, 4).getUint32(0, true);
          out.info[sid] = dec.decode(body.subarray(p + 8, p + 8 + sz)).replace(/\0+$/, '');
          p += 8 + sz + (sz & 1);
        }
      } else if (cid === 'bext' && body.length >= 346) {
        const s = (a, b) => dec.decode(body.subarray(a, b)).replace(/\0+$/, '').trim();
        out.bext = { description: s(0, 256), originator: s(256, 288), originatorRef: s(288, 320), date: s(320, 330), time: s(330, 338) };
      } else if (cid === 'mmjs') {
        try { out.mmjs = JSON.parse(dec.decode(body)); } catch (e) { /* ignore */ }
      } else if (cid === 'smpl' && body.length >= 60) {
        const sv = new DataView(body.buffer, body.byteOffset, body.length);
        if (sv.getUint32(28, true) > 0) out.smpl = { start: sv.getUint32(44, true), end: sv.getUint32(48, true) };
      } else if (cid === 'iXML') {
        out.ixml = dec.decode(body);
      }
      o += 8 + size + (size & 1);
    }
    return out;
  },
};

// ═══════════════════════════════════════════════════════════════════
// Take library (IndexedDB, shared by every tool page on file://)
// ═══════════════════════════════════════════════════════════════════
AK.lib = {
  _db: null,
  _chan: null,
  open() {
    if (this._db) return Promise.resolve(this._db);
    return new Promise((resolve, reject) => {
      let req;
      try { req = indexedDB.open('mm_audio', 2); } catch (e) { return reject(e); }
      req.onupgradeneeded = () => {
        const db = req.result;
        if (!db.objectStoreNames.contains('takes')) db.createObjectStore('takes', { keyPath: 'id' });
        if (!db.objectStoreNames.contains('pcm')) db.createObjectStore('pcm', { keyPath: 'id' });
        if (!db.objectStoreNames.contains('kv')) db.createObjectStore('kv', { keyPath: 'k' });
      };
      req.onsuccess = () => { this._db = req.result; resolve(this._db); };
      req.onerror = () => reject(req.error);
    });
  },
  channel() {
    if (!this._chan && typeof BroadcastChannel !== 'undefined') {
      try { this._chan = new BroadcastChannel('mm_audio'); } catch (e) { this._chan = null; }
    }
    return this._chan;
  },
  onChange(fn) { const c = this.channel(); if (c) c.addEventListener('message', e => fn(e.data)); },
  _tx(stores, mode, fn) {
    return this.open().then(db => new Promise((resolve, reject) => {
      const tx = db.transaction(stores, mode);
      let result;
      Promise.resolve(fn(tx)).then(r => { result = r; });
      tx.oncomplete = () => resolve(result);
      tx.onerror = () => reject(tx.error);
      tx.onabort = () => reject(tx.error || new Error('aborted'));
    }));
  },
  _req(r) { return new Promise((res, rej) => { r.onsuccess = () => res(r.result); r.onerror = () => rej(r.error); }); },
  // record: {id?, kind, name, sampleRate, meta}, channels: Float32Array[]
  async put(record, channels) {
    const rec = Object.assign({ created: Date.now() }, record);
    if (rec.id === undefined || rec.id === null || rec.id === '') rec.id = AK.util.uid();
    if (channels) {
      rec.channels = channels.length;
      rec.frames = channels[0].length;
      rec.durationSec = rec.frames / rec.sampleRate;
    }
    await this._tx(['takes', 'pcm'], 'readwrite', tx => {
      tx.objectStore('takes').put(rec);
      if (channels) tx.objectStore('pcm').put({ id: rec.id, data: channels });
    });
    const c = this.channel(); if (c) c.postMessage({ type: 'put', id: rec.id, kind: rec.kind });
    return rec;
  },
  async update(id, patch) {
    const rec = await this.meta(id);
    if (!rec) return null;
    Object.assign(rec, patch);
    await this._tx(['takes'], 'readwrite', tx => { tx.objectStore('takes').put(rec); });
    const c = this.channel(); if (c) c.postMessage({ type: 'update', id });
    return rec;
  },
  async list(kind) {
    const all = await this._tx(['takes'], 'readonly', tx => this._req(tx.objectStore('takes').getAll()));
    return (all || []).filter(r => !kind || r.kind === kind).sort((a, b) => b.created - a.created);
  },
  meta(id) { return this._tx(['takes'], 'readonly', tx => this._req(tx.objectStore('takes').get(id))); },
  async pcm(id) {
    const r = await this._tx(['pcm'], 'readonly', tx => this._req(tx.objectStore('pcm').get(id)));
    return r ? r.data : null;
  },
  async del(id) {
    await this._tx(['takes', 'pcm'], 'readwrite', tx => { tx.objectStore('takes').delete(id); tx.objectStore('pcm').delete(id); });
    const c = this.channel(); if (c) c.postMessage({ type: 'del', id });
  },
  // Raw PCM slots outside the take list (e.g. TAPE STUDIO's track tapes).
  pcmPut(id, channels) { return this._tx(['pcm'], 'readwrite', tx => { tx.objectStore('pcm').put({ id, data: channels }); }); },
  pcmDel(id) { return this._tx(['pcm'], 'readwrite', tx => { tx.objectStore('pcm').delete(id); }); },
  kvGet(k) { return this._tx(['kv'], 'readonly', tx => this._req(tx.objectStore('kv').get(k))).then(r => r ? r.v : undefined); },
  kvSet(k, v) { return this._tx(['kv'], 'readwrite', tx => { tx.objectStore('kv').put({ k, v }); }); },
};

// ═══════════════════════════════════════════════════════════════════
// Game folder (File System Access) + music catalog
// ═══════════════════════════════════════════════════════════════════
AK.game = {
  root: null,          // FileSystemDirectoryHandle for godot/
  supported() { return typeof window.showDirectoryPicker === 'function'; },
  async _resolveGodot(handle) {
    // Accept the repo root or godot/ itself.
    const has = async (h, name, kind) => {
      try { kind === 'dir' ? await h.getDirectoryHandle(name) : await h.getFileHandle(name); return true; } catch (e) { return false; }
    };
    if (await has(handle, 'project.godot', 'file')) return handle;
    if (await has(handle, 'godot', 'dir')) {
      const g = await handle.getDirectoryHandle('godot');
      if (await has(g, 'project.godot', 'file')) return g;
    }
    return null;
  },
  async link() {
    if (!this.supported()) throw new Error('This browser has no folder access (use Chrome / Edge).');
    const h = await window.showDirectoryPicker({ id: 'mm-godot', mode: 'readwrite' });
    const g = await this._resolveGodot(h);
    if (!g) throw new Error('Pick the modern-mythology folder (or its godot/ folder).');
    this.root = g;
    try { await AK.lib.kvSet('godot_dir', g); } catch (e) { /* handles not storable here */ }
    return g;
  },
  // Restore a previously linked folder. needGesture=true → may prompt.
  async restore(needGesture = false) {
    let h;
    try { h = await AK.lib.kvGet('godot_dir'); } catch (e) { return null; }
    if (!h || !h.queryPermission) return null;
    let p = await h.queryPermission({ mode: 'readwrite' });
    if (p !== 'granted' && needGesture) p = await h.requestPermission({ mode: 'readwrite' });
    if (p !== 'granted') { this._pending = h; return null; }
    this.root = h;
    return h;
  },
  async _dir(path, create) {
    let d = this.root;
    for (const part of path.split('/').filter(Boolean)) d = await d.getDirectoryHandle(part, { create });
    return d;
  },
  async exists(path) {
    if (!this.root) return false;
    const parts = path.split('/').filter(Boolean), name = parts.pop();
    try { const d = await this._dir(parts.join('/'), false); await d.getFileHandle(name); return true; } catch (e) { return false; }
  },
  async readText(path) {
    const parts = path.split('/').filter(Boolean), name = parts.pop();
    const d = await this._dir(parts.join('/'), false);
    return (await (await d.getFileHandle(name)).getFile()).text();
  },
  async write(path, blob) {
    const parts = path.split('/').filter(Boolean), name = parts.pop();
    const d = await this._dir(parts.join('/'), true);
    const fh = await d.getFileHandle(name, { create: true });
    const w = await fh.createWritable();
    await w.write(blob); await w.close();
    return path;
  },
  async catalog() { return JSON.parse(await this.readText('resources/music_catalog.json')); },
  // Field-friendliness: how much a track's brief reads like something
  // you can go and record, vs. something you'd compose.
  fieldScore(t) {
    const s = ((t.title || '') + ' ' + (t.desc || '') + ' ' + (t.id || '')).toLowerCase();
    const yes = ['rain', 'wind', 'cicada', 'storm', 'thunder', 'halyard', 'gull', 'creak', 'hum', 'room', 'stove', 'woodstove',
      'traffic', 'crowd', 'kitchen', 'dock', 'tide', 'water', 'insect', 'bird', 'fan', 'fridge', 'static', 'radio', 'marina',
      'rest stop', 'diner', 'bar', 'night shift', 'porch', 'field', 'substation', 'interior', 'ambient', 'drone', 'wash', 'surf',
      'frog', 'crickets', 'bell', 'clock', 'tap', 'faucet', 'engine', 'boat', 'train', 'hospital', 'office', 'warehouse', 'shop'];
    const no = ['theme', 'credits', 'hymn', 'strings', 'chord', 'band', 'song', 'stinger', 'melody', 'piano', 'guitar', 'choir', 'title'];
    let sc = 0;
    for (const w of yes) if (s.includes(w)) sc += 1;
    for (const w of no) if (s.includes(w)) sc -= 2;
    return sc;
  },
  async wanted() {
    const cat = await this.catalog();
    const out = [];
    for (const t of cat) {
      if (!t.src) continue;
      const wavSrc = t.src.replace(/\.[^.\/]+$/, '') + '.wav';
      const have = await this.exists(t.src) || await this.exists(wavSrc);
      if (!have) out.push(Object.assign({}, t, { wavSrc, fieldScore: this.fieldScore(t) }));
    }
    return out.sort((a, b) => b.fieldScore - a.fieldScore || (a.vol - b.vol));
  },
};

// ═══════════════════════════════════════════════════════════════════
// Offline DSP
// ═══════════════════════════════════════════════════════════════════
AK.dsp = {
  // Run channels through a graph built by build(ctx, srcNode) → output node.
  async render(chs, sr, build, extraSec = 0) {
    const len = chs[0].length + Math.round(extraSec * sr);
    const ctx = new OfflineAudioContext(chs.length, Math.max(1, len), sr);
    const src = ctx.createBufferSource();
    src.buffer = AK.util.toBuffer(ctx, chs, sr);
    const out = build(ctx, src);
    out.connect(ctx.destination);
    src.start();
    return AK.util.fromBuffer(await ctx.startRendering());
  },
  highpass(chs, sr, hz = 80) {
    return this.render(chs, sr, (ctx, src) => {
      const a = ctx.createBiquadFilter(), b = ctx.createBiquadFilter();
      a.type = b.type = 'highpass'; a.frequency.value = b.frequency.value = hz; a.Q.value = b.Q.value = 0.707;
      src.connect(a); a.connect(b); return b;
    });
  },
  lowpass(chs, sr, hz = 12000) {
    return this.render(chs, sr, (ctx, src) => {
      const a = ctx.createBiquadFilter(); a.type = 'lowpass'; a.frequency.value = hz; a.Q.value = 0.707;
      src.connect(a); return a;
    });
  },
  gain(chs, g) { return chs.map(c => { const o = new Float32Array(c.length); for (let i = 0; i < c.length; i++) o[i] = c[i] * g; return o; }); },
  normalizePeak(chs, dbfs = -1) {
    const p = AK.util.peakOf(chs);
    return p > 0 ? this.gain(chs, AK.util.lin(dbfs) / p) : chs;
  },
  // Approximate integrated loudness (ITU-R BS.1770 K-weighting, 400 ms
  // blocks, absolute gate -70 LUFS, relative gate -10 LU).
  async lufs(chs, sr) {
    const k = await this.render(chs, sr, (ctx, src) => {
      const shelf = ctx.createBiquadFilter(); shelf.type = 'highshelf'; shelf.frequency.value = 1681; shelf.gain.value = 4;
      const hp = ctx.createBiquadFilter(); hp.type = 'highpass'; hp.frequency.value = 38; hp.Q.value = 0.5;
      src.connect(shelf); shelf.connect(hp); return hp;
    });
    const blk = Math.round(0.4 * sr), hop = Math.round(0.1 * sr), n = k[0].length;
    const ms = [];
    for (let s = 0; s + blk <= n; s += hop) {
      let sum = 0;
      for (const c of k) { for (let i = s; i < s + blk; i++) sum += c[i] * c[i]; }
      ms.push(sum / blk);
    }
    if (!ms.length) return -70;
    const L = m => -0.691 + 10 * Math.log10(m || 1e-12);
    let gated = ms.filter(m => L(m) > -70);
    if (!gated.length) return -70;
    const rel = L(gated.reduce((a, b) => a + b, 0) / gated.length) - 10;
    gated = gated.filter(m => L(m) > rel);
    return L(gated.reduce((a, b) => a + b, 0) / gated.length);
  },
  async normalizeLufs(chs, sr, target = -23, ceilingDb = -1) {
    const now = await this.lufs(chs, sr);
    let g = AK.util.lin(target - now);
    const p = AK.util.peakOf(chs) * g;
    if (p > AK.util.lin(ceilingDb)) g *= AK.util.lin(ceilingDb) / p;   // never clip
    return { channels: this.gain(chs, g), before: now, gainDb: AK.util.db(g) };
  },
  trim(chs, a, b) { return chs.map(c => c.slice(Math.max(0, a | 0), Math.min(c.length, b | 0))); },
  fades(chs, sr, inSec = 0.05, outSec = 0.25) {
    return chs.map(c => {
      const o = c.slice(0), n = o.length;
      const fi = Math.min(n, Math.round(inSec * sr)), fo = Math.min(n, Math.round(outSec * sr));
      for (let i = 0; i < fi; i++) o[i] *= Math.sin(0.5 * Math.PI * i / fi);
      for (let i = 0; i < fo; i++) o[n - 1 - i] *= Math.sin(0.5 * Math.PI * i / fo);
      return o;
    });
  },
  // Seamless loop: the head crossfades into the tail (equal power), so
  // sample L-1 flows into sample 0. Output is shorter by xfadeSec.
  loop(chs, sr, xfadeSec = 2) {
    const n = chs[0].length;
    const X = Math.max(1, Math.min(Math.floor(n / 3), Math.round(xfadeSec * sr)));
    const L = n - X;
    return chs.map(c => {
      const o = new Float32Array(L);
      o.set(c.subarray(X, n));
      for (let j = 0; j < X; j++) {
        const t = j / X;
        o[L - X + j] = c[n - X + j] * Math.cos(0.5 * Math.PI * t) + c[j] * Math.sin(0.5 * Math.PI * t);
      }
      return o;
    });
  },
  reverse(chs) { return chs.map(c => c.slice(0).reverse()); },
  mono(chs) {
    if (chs.length === 1) return chs;
    const o = new Float32Array(chs[0].length);
    for (let i = 0; i < o.length; i++) { let s = 0; for (const c of chs) s += c[i]; o[i] = s / chs.length; }
    return [o];
  },
  // Spectral noise gate. Learns the noise floor from [noiseA, noiseB)
  // (frames) — or the quietest 0.5 s if not given — then pulls every
  // bin that does not rise `sensitivityDb` (default 10) above it down by `reductionDb`,
  // with time smoothing so it doesn't warble.
  denoise(chs, sr, opts = {}) {
    const N = 2048, H = 512, red = AK.util.lin(-(opts.reductionDb ?? 12)), sens = AK.util.lin(opts.sensitivityDb ?? 10);
    const win = new Float32Array(N);
    for (let i = 0; i < N; i++) win[i] = 0.5 - 0.5 * Math.cos(2 * Math.PI * i / N);
    let [na, nb] = [opts.noiseA, opts.noiseB];
    if (!(nb > na)) { [na, nb] = this.quietest(chs, sr, 0.5); }
    return chs.map(c => {
      const n = c.length;
      const re = new Float32Array(N), im = new Float32Array(N);
      // noise profile
      const prof = new Float32Array(N / 2 + 1);
      let frames = 0;
      for (let s = na; s + N <= Math.max(nb, na + N) && s + N <= n; s += H) {
        for (let i = 0; i < N; i++) { re[i] = c[s + i] * win[i]; im[i] = 0; }
        AK.fft(re, im, false);
        for (let k = 0; k <= N / 2; k++) prof[k] += Math.hypot(re[k], im[k]);
        frames++;
      }
      if (!frames) return c.slice(0);
      for (let k = 0; k <= N / 2; k++) prof[k] /= frames;
      const out = new Float32Array(n + N), norm = new Float32Array(n + N);
      const g = new Float32Array(N / 2 + 1).fill(1);
      for (let s = -N + H; s < n; s += H) {
        for (let i = 0; i < N; i++) { const j = s + i; re[i] = (j >= 0 && j < n ? c[j] : 0) * win[i]; im[i] = 0; }
        AK.fft(re, im, false);
        for (let k = 0; k <= N / 2; k++) {
          const mag = Math.hypot(re[k], im[k]);
          const target = mag > prof[k] * sens ? 1 : red;
          g[k] = target > g[k] ? target * 0.7 + g[k] * 0.3 : target * 0.15 + g[k] * 0.85;  // fast open, slow close
          re[k] *= g[k]; im[k] *= g[k];
          if (k > 0 && k < N / 2) { re[N - k] = re[k]; im[N - k] = -im[k]; }
        }
        AK.fft(re, im, true);
        for (let i = 0; i < N; i++) { const j = s + i; if (j >= 0 && j < n + N) { out[j] += re[i] * win[i]; norm[j] += win[i] * win[i]; } }
      }
      const o = new Float32Array(n);
      for (let i = 0; i < n; i++) o[i] = norm[i] > 1e-6 ? out[i] / norm[i] : 0;
      return o;
    });
  },
  // [start, end) frames of the quietest `sec`-long window.
  quietest(chs, sr, sec = 0.5) {
    const w = Math.max(1, Math.round(sec * sr)), n = chs[0].length;
    if (n <= w) return [0, n];
    const hop = Math.max(1, Math.round(w / 4));
    let best = Infinity, at = 0;
    for (let s = 0; s + w <= n; s += hop) {
      let e = 0;
      for (const c of chs) for (let i = s; i < s + w; i += 4) e += c[i] * c[i];
      if (e < best) { best = e; at = s; }
    }
    return [at, at + w];
  },
  // Sum tracks [{channels, gain, pan, offset(frames)}] into stereo.
  mix(tracks, frames) {
    const L = new Float32Array(frames), R = new Float32Array(frames);
    for (const t of tracks) {
      if (!t.channels) continue;
      const g = t.gain ?? 1, p = Math.max(-1, Math.min(1, t.pan ?? 0));
      const gl = g * Math.cos((p + 1) * Math.PI / 4), gr = g * Math.sin((p + 1) * Math.PI / 4);
      const a = t.channels[0], b = t.channels[1] || t.channels[0], off = t.offset | 0;
      for (let i = 0; i < a.length; i++) { const j = i + off; if (j < 0 || j >= frames) continue; L[j] += a[i] * gl; R[j] += b[i] * gr; }
    }
    return [L, R];
  },
};

// In-place radix-2 complex FFT (n power of two). inverse → scaled by 1/n.
AK.fft = function (re, im, inverse) {
  const n = re.length;
  for (let i = 1, j = 0; i < n; i++) {
    let bit = n >> 1;
    for (; j & bit; bit >>= 1) j ^= bit;
    j ^= bit;
    if (i < j) { let t = re[i]; re[i] = re[j]; re[j] = t; t = im[i]; im[i] = im[j]; im[j] = t; }
  }
  for (let len = 2; len <= n; len <<= 1) {
    const ang = 2 * Math.PI / len * (inverse ? 1 : -1);
    const wr = Math.cos(ang), wi = Math.sin(ang);
    for (let i = 0; i < n; i += len) {
      let cr = 1, ci = 0;
      for (let k = 0; k < len / 2; k++) {
        const a = i + k, b = a + len / 2;
        const xr = re[b] * cr - im[b] * ci, xi = re[b] * ci + im[b] * cr;
        re[b] = re[a] - xr; im[b] = im[a] - xi; re[a] += xr; im[a] += xi;
        const nr = cr * wr - ci * wi; ci = cr * wi + ci * wr; cr = nr;
      }
    }
  }
  if (inverse) for (let i = 0; i < n; i++) { re[i] /= n; im[i] /= n; }
};

// ═══════════════════════════════════════════════════════════════════
// Drawing
// ═══════════════════════════════════════════════════════════════════
AK.draw = {
  fit(canvas) {
    const r = window.devicePixelRatio || 1;
    const w = Math.max(1, Math.round(canvas.clientWidth * r)), h = Math.max(1, Math.round(canvas.clientHeight * r));
    if (canvas.width !== w || canvas.height !== h) { canvas.width = w; canvas.height = h; }
    return { w, h, r };
  },
  // opts: color, bg, sel [a,b] frames, markers [{frame,label}], playhead frame, loop [a,b]
  wave(canvas, chs, opts = {}) {
    const { w, h, r } = this.fit(canvas);
    const g = canvas.getContext('2d');
    g.fillStyle = opts.bg || '#0e0908'; g.fillRect(0, 0, w, h);
    if (!chs || !chs.length || !chs[0].length) return;
    const n = chs[0].length, per = n / w;
    if (opts.loop) {
      g.fillStyle = 'rgba(78,160,96,0.14)';
      g.fillRect(opts.loop[0] / per, 0, (opts.loop[1] - opts.loop[0]) / per, h);
    }
    if (opts.sel) {
      g.fillStyle = 'rgba(216,160,96,0.16)';
      g.fillRect(opts.sel[0] / per, 0, (opts.sel[1] - opts.sel[0]) / per, h);
    }
    const lanes = chs.length, lh = h / lanes;
    g.strokeStyle = opts.color || '#d8a060';
    g.lineWidth = 1;
    chs.forEach((c, li) => {
      const mid = lh * li + lh / 2;
      g.beginPath();
      for (let x = 0; x < w; x++) {
        const a = Math.floor(x * per), b = Math.min(n, Math.floor((x + 1) * per) + 1);
        let mn = 1, mx = -1;
        for (let i = a; i < b; i += Math.max(1, Math.floor((b - a) / 64))) { const v = c[i]; if (v < mn) mn = v; if (v > mx) mx = v; }
        g.moveTo(x + 0.5, mid - mx * lh * 0.47); g.lineTo(x + 0.5, mid - mn * lh * 0.47 + 0.5);
      }
      g.stroke();
    });
    if (opts.markers) {
      g.fillStyle = '#a8e89c'; g.font = (10 * r) + 'px "Courier New", monospace';
      for (const m of opts.markers) { const x = m.frame / per; g.fillRect(x, 0, r, h); g.fillText(m.label || '', x + 3 * r, 11 * r); }
    }
    if (opts.preRoll) {
      g.fillStyle = 'rgba(0,0,0,0.35)'; g.fillRect(0, 0, opts.preRoll / per, h);
    }
    if (opts.playhead !== undefined && opts.playhead !== null) {
      g.fillStyle = '#ffd896'; g.fillRect(opts.playhead / per, 0, Math.max(1, r), h);
    }
  },
  spectrogram(canvas, chs, sr, opts = {}) {
    const { w, h } = this.fit(canvas);
    const g = canvas.getContext('2d');
    const img = g.createImageData(w, h);
    const c = AK.dsp.mono(chs)[0], n = c.length, N = 1024;
    const re = new Float32Array(N), im = new Float32Array(N), win = new Float32Array(N);
    for (let i = 0; i < N; i++) win[i] = 0.5 - 0.5 * Math.cos(2 * Math.PI * i / N);
    const fMax = Math.min(sr / 2, opts.maxHz || 16000), kMax = Math.floor(fMax / (sr / N));
    for (let x = 0; x < w; x++) {
      const s = Math.floor((x / w) * Math.max(0, n - N));
      for (let i = 0; i < N; i++) { re[i] = (c[s + i] || 0) * win[i]; im[i] = 0; }
      AK.fft(re, im, false);
      for (let y = 0; y < h; y++) {
        // log frequency axis
        const fr = Math.pow((h - 1 - y) / (h - 1), 2.2);
        const k = Math.max(1, Math.min(kMax, Math.round(fr * kMax)));
        const db = 20 * Math.log10(Math.hypot(re[k], im[k]) / N + 1e-9);
        const v = Math.max(0, Math.min(1, (db + 100) / 80));
        const o = (y * w + x) * 4;
        img.data[o] = Math.round(255 * Math.min(1, v * 1.6));
        img.data[o + 1] = Math.round(216 * Math.pow(v, 1.6));
        img.data[o + 2] = Math.round(150 * Math.pow(v, 3));
        img.data[o + 3] = 255;
      }
    }
    g.putImageData(img, 0, 0);
  },
  // horizontal meter: peak (linear), hold, rms, clipped
  meter(canvas, peak, hold, rms, clipped) {
    const { w, h } = this.fit(canvas);
    const g = canvas.getContext('2d');
    g.fillStyle = '#0e0908'; g.fillRect(0, 0, w, h);
    const pos = lin => Math.max(0, Math.min(1, (AK.util.db(lin) + 60) / 60)) * w;
    const grad = g.createLinearGradient(0, 0, w, 0);
    grad.addColorStop(0, '#4ea060'); grad.addColorStop(0.8, '#d8a060'); grad.addColorStop(0.95, '#c64a3a');
    g.fillStyle = grad; g.fillRect(0, 0, pos(peak), h);
    g.fillStyle = 'rgba(255,216,150,0.35)'; g.fillRect(0, h * 0.35, pos(rms), h * 0.3);
    g.fillStyle = '#ffd896'; g.fillRect(pos(hold) - 1, 0, 2, h);
    for (const db of [-48, -36, -24, -18, -12, -6, -3]) { g.fillStyle = 'rgba(0,0,0,0.5)'; g.fillRect(((db + 60) / 60) * w, 0, 1, h); }
    if (clipped) { g.fillStyle = '#c64a3a'; g.fillRect(w - 6, 0, 6, h); }
  },
};
