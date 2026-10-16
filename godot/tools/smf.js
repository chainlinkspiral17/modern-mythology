/* smf.js — Standard MIDI File write/read for the MM tools.
 *
 *   SMF.write(tracks, { ppq, bpm, name, timeSig })  → Uint8Array (type 1)
 *     tracks: [{ name, channel (1-16), notes: [{ t, d, n, v }] }]   (t/d in ticks at ppq, v 0..1)
 *   SMF.read(bytes) → { ppq, bpm, tracks: [{ name, channel, notes }] }
 *
 * The SLOOP / Felucca web editors import a MIDI file per track; any DAW
 * takes the song.
 */
(function (root) {
  "use strict";

  function vlq(n) {
    const out = [n & 0x7F];
    while ((n >>= 7)) out.unshift((n & 0x7F) | 0x80);
    return out;
  }
  function str(s) { return Array.from(new TextEncoder().encode(s)); }
  function u32(n) { return [(n >>> 24) & 255, (n >>> 16) & 255, (n >>> 8) & 255, n & 255]; }
  function chunk(id, body) { return [...str(id), ...u32(body.length), ...body]; }

  function write(tracks, o = {}) {
    const ppq = o.ppq || 96, bpm = o.bpm || 120;
    const conductor = [];
    const tempo = Math.round(60000000 / bpm);
    if (o.name) conductor.push(0, 0xFF, 0x03, ...vlq(str(o.name).length), ...str(o.name));
    conductor.push(0, 0xFF, 0x51, 3, (tempo >> 16) & 255, (tempo >> 8) & 255, tempo & 255);
    const [num, den] = o.timeSig || [4, 4];
    conductor.push(0, 0xFF, 0x58, 4, num, Math.round(Math.log2(den)), 24, 8);
    conductor.push(0, 0xFF, 0x2F, 0);
    const chunks = [chunk('MTrk', conductor)];
    for (const tr of tracks) {
      const ch = Math.max(1, Math.min(16, tr.channel || 1)) - 1;
      const ev = [];
      // a key can't be down twice: trim same-pitch overlaps, drop exact duplicates
      const ns = (tr.notes || []).map(x => ({ t: Math.max(0, Math.round(x.t)), d: Math.max(1, Math.round(x.d)), n: x.n & 127, v: x.v }))
        .sort((a, b) => a.t - b.t || a.n - b.n);
      const lastBy = new Map(), clean = [];
      for (const x of ns) {
        const pr = lastBy.get(x.n);
        if (pr && pr.t === x.t) continue;
        if (pr && pr.t + pr.d > x.t) pr.d = x.t - pr.t;
        clean.push(x); lastBy.set(x.n, x);
      }
      for (const n of clean) {
        const vel = Math.max(1, Math.min(127, Math.round((n.v ?? 0.8) * 127)));
        const t0 = n.t, t1 = t0 + Math.max(1, n.d);
        ev.push([t0, 1, [0x90 | ch, n.n & 127, vel]]);
        ev.push([t1, 0, [0x80 | ch, n.n & 127, 0]]);      // offs sort before ons at the same tick
      }
      ev.sort((a, b) => a[0] - b[0] || a[1] - b[1]);
      const body = [];
      if (tr.name) body.push(0, 0xFF, 0x03, ...vlq(str(tr.name).length), ...str(tr.name));
      let last = 0;
      for (const [t, , bytes] of ev) { body.push(...vlq(t - last), ...bytes); last = t; }
      body.push(0, 0xFF, 0x2F, 0);
      chunks.push(chunk('MTrk', body));
    }
    const header = chunk('MThd', [0, 1, 0, chunks.length, (ppq >> 8) & 255, ppq & 255]);
    return Uint8Array.from([...header, ...chunks.flat()]);
  }

  function read(bytes) {
    const b = bytes instanceof Uint8Array ? bytes : new Uint8Array(bytes);
    let p = 0;
    const u16 = () => (b[p++] << 8) | b[p++];
    const u32r = () => ((b[p++] << 24) | (b[p++] << 16) | (b[p++] << 8) | b[p++]) >>> 0;
    const id = () => String.fromCharCode(b[p++], b[p++], b[p++], b[p++]);
    const rv = () => { let n = 0, c; do { c = b[p++]; n = (n << 7) | (c & 0x7F); } while (c & 0x80); return n; };
    if (id() !== 'MThd') throw new Error('not a MIDI file');
    const hl = u32r(); const fmt = u16(), ntr = u16(), div = u16(); p += hl - 6;
    if (div & 0x8000) throw new Error('SMPTE time division is not supported');
    const out = { ppq: div, bpm: 120, format: fmt, tracks: [] };
    for (let k = 0; k < ntr && p < b.length; k++) {
      if (id() !== 'MTrk') break;
      const len = u32r(), end = p + len;
      let t = 0, status = 0, name = '';
      const open = new Map(), notes = [], chans = {};
      while (p < end) {
        t += rv();
        let s = b[p];
        if (s & 0x80) p++; else s = status;
        if (s === 0xFF) {
          const type = b[p++], l = rv(), data = b.subarray(p, p + l); p += l;
          if (type === 0x03 && !name) name = new TextDecoder().decode(data);
          if (type === 0x51 && l === 3) out.bpm = Math.round(60000000 / ((data[0] << 16) | (data[1] << 8) | data[2]) * 100) / 100;
          continue;
        }
        if (s === 0xF0 || s === 0xF7) { const l = rv(); p += l; continue; }
        status = s;
        const type = s & 0xF0, ch = s & 0x0F;
        const d1 = b[p++], d2 = (type === 0xC0 || type === 0xD0) ? 0 : b[p++];
        if (type === 0x90 && d2 > 0) { open.set(ch * 128 + d1, { t, v: d2 / 127 }); chans[ch] = (chans[ch] || 0) + 1; }
        else if (type === 0x80 || (type === 0x90 && d2 === 0)) {
          const o = open.get(ch * 128 + d1);
          if (o) { notes.push({ t: o.t, d: Math.max(1, t - o.t), n: d1, v: o.v, ch: ch + 1 }); open.delete(ch * 128 + d1); }
        }
      }
      p = end;
      if (notes.length) {
        const ch = +Object.entries(chans).sort((a, c) => c[1] - a[1])[0][0] + 1;
        out.tracks.push({ name: name || 'track ' + (k + 1), channel: ch, notes: notes.sort((a, c) => a.t - c.t) });
      }
    }
    return out;
  }

  const API = { write, read };
  if (typeof module !== 'undefined' && module.exports) module.exports = API;
  root.SMF = API;
})(typeof window !== 'undefined' ? window : globalThis);
