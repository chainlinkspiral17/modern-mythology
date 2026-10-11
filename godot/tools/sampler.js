/* sampler.js — SAMPLE INSTRUMENT · a polyphonic sampler device + sample-format parsers
 *
 * Plain classic script (no modules, no build step) for the Modern Mythology
 * browser tools. Works on file:// pages in Chrome, inside a live AudioContext
 * or an OfflineAudioContext. Voices are AudioBufferSourceNodes started at the
 * exact `when`; no worklet is needed.
 *
 *   const smp = new SampleInstrument(ctx, { output: ctx.destination, maxVoices: 48 });
 *   await smp.init();
 *   const inst = await SampleFormats.parseSFZ(text, 'https://…/piano.sfz');
 *   await smp.load(inst, { id: 'lib:salamander', onProgress: (done, total, bytes) => … });
 *   smp.noteOn(60, 0.8, t);  smp.noteOff(60, t + 1);
 *   const ed = smp.mountEditor(el);   …   ed.destroy();
 *
 * DEVICE API (same shape as ForgeSynth)
 *   new SampleInstrument(ctx, {output, maxVoices = 48, fetchBytes?, resolveInstrument?})
 *       fetchBytes(url) → Promise<ArrayBuffer>  used by load() for undecoded zones
 *       resolveInstrument(id) → Promise<inst>   lets setState({instrument: id}) re-load by id
 *   init() → Promise            load(inst, {id, fetchBytes, onProgress, filter, retry}) → Promise<info>
 *       (decodes zones that have no buffer yet; zones that already failed are skipped unless retry)
 *   noteOn(note, vel01, when, ch)   noteOff(note, when, ch)   allOff(when)   panic()
 *   cc(num, v01, when)   1 mod wheel (vibrato | filter | off — state.mw) · 7 volume · 10 pan ·
 *                        64 sustain · 120 all sound off · 123 all notes off · every CC is also
 *                        kept for SFZ locc/hicc conditions and *_onccN modulation (read at note-on)
 *   pitchBend(-1..1, when)          ± state.bendRange semitones
 *   getState() / setState(obj|json) {v, instrument, gain, transpose, tune, attack, release,
 *                                    cutoff, resonance, velSens, bendRange, mw}
 *       gain dB (−48..+12) · transpose semitones (shifts the played key: zone choice + pitch) ·
 *       tune cents · attack = SECONDS ADDED to every zone's attack (0..4) ·
 *       release = MULTIPLIER on every zone's release (0.05..8) · cutoff Hz (device lowpass,
 *       20000 = open) · resonance dB (0..24) · velSens = exponent on the velocity curve
 *       (0 = no velocity response, 1 = as authored, 2 = steeper) · bendRange semitones ·
 *       mw 'vibrato' | 'filter' | 'off'
 *       The sample data is NOT in the state: the host re-loads the instrument by id.
 *   set(key, value)  shorthand for setState({[key]: value})
 *   info() → {id, name, format, zones, playable, failed, keyLo, keyHi, seconds, bytes, unsupported}
 *   mountEditor(el, {mapHeight}) → {destroy(), element}     on(type, fn) → off()
 *       events: change · load · progress · note
 *   activeVoices · maxVoices · output (GainNode → opts.output) · bpm · instrument · dispose()
 *
 * VOICES  every zone whose key / velocity / CC / keyswitch / random / round-robin
 *   conditions match sounds (layers). Each noteOn makes one "note event"; each
 *   noteOff releases the EARLIEST unreleased event of that note+channel whose
 *   start ≤ the off time, so a DAW that delivers on/off pairs out of time order
 *   still pairs them right (an off that arrives before its on waits for it).
 *   Envelope: delay → linear attack → hold → decay → sustain; release is a separate
 *   exponential curve node (dB-linear, 72 dB over the release time for SFZ /
 *   folder instruments, 100 dB for SF2, as the spec says), so release, choke and
 *   steal never fight over one AudioParam. Steals and chokes fade 5–6 ms.
 *   Stealing: oldest released voice first, then oldest. loop_sustain switches its
 *   loop off at the release time (timer on a live context, suspend() offline).
 *
 * FORMATS — window.SampleFormats
 *   parseSFZ(text, baseUrl, {readText(url) → Promise<string>, name}) → Promise<inst>
 *   parseSF2(arrayBuffer) → {name, presets:[{name, bank, program, index}], sampleBytes,
 *                            isSF3, instrument(presetIndex, ctx, {attenuationScale}) → inst}
 *   parseMidiJsSoundfont(text, {name}) → inst
 *   instrumentFromFiles([{name, url | bytes}], {name, spread, chromaticFrom, release, loopMode, octaveOffset})
 *                          → inst (with inst.unmapped = [names])
 *   autoOctave(inst) → octaves shifted (after decoding: measures a few zones; for libraries
 *                          that name middle C "C3", e.g. much of VCSL)   detectPitch(buf, t0) → Hz
 *   decodeAll(inst, ctx, fetchBytes?, onProgress?, {filter, concurrency, retry}) → Promise<stats>
 *       stats {total, ok, failed, bytes, seconds, errors:[{url, error}], ms}; data: URLs are decoded inline
 *   thinLayers(inst, maxLayers) → inst  (merge velocity layers: big SFZ pianos on the Deck)
 *   noteNameToMidi('c#4') → 61 · midiToNoteName(61) → 'C#4'   (C4 = 60 everywhere)
 *   parseWav(arrayBuffer) → {format, channels, rate, bits, dataOffset, dataLength, loops, unityNote}
 *   decodeBytes(arrayBuffer, ctx, hint) → Promise<{buffer, rate, loops, unityNote}>
 *
 * NORMALIZED INSTRUMENT
 *   { format: 'sfz'|'sf2'|'midijs'|'files', name, id?, zones: [zone], unsupported: [str],
 *     warnings: [str], ccInit: {num: 0..127}, curves: {idx: Float32Array(128)},
 *     keyswitch: null | {lo, hi, def}, bend: null | {up, down} (cents), unmapped?: [str] }
 *   zone = {
 *     sample: url | data: URL | null,  data: ArrayBuffer | null (encoded bytes, e.g. local file / sf3),
 *     buffer: AudioBuffer | null (filled by decodeAll / parseSF2), srcRate: native frames/s,
 *     generator: null | 'silence' | 'sine' | 'noise',  error?: string, name,
 *     lokey, hikey, lovel, hivel (inclusive 0..127), lochan, hichan (1..16),
 *     root (key the sample sounds at), tune (cents), keytrack (cents/key), velPitch (cents at vel 127),
 *     fixedKey (−1 or key: SF2 keynum), fixedVel (−1 or vel),
 *     gain (dB), pan (−1..1), ampVeltrack (−1..1), velCurve: null | Float32Array(128),
 *     env: {delay, attack, hold, decay, sustain (0..1 linear), release (s), dbDecay, keyHold, keyDecay},
 *     loopMode: null (auto: loop if the file has loop points) | 'no_loop' | 'one_shot' |
 *               'loop_continuous' | 'loop_sustain',
 *     loopStart, loopEnd (frames in the sample's own rate, end exclusive; null = from file),
 *     offset (frames), end (frames, exclusive, null = to the end),
 *     trigger: 'attack' | 'release' | 'first' | 'legato',
 *     group, offBy (0 = none), offMode: 'fast' | 'normal' | 'time', offTime (s),
 *     seqLength, seqPosition (1-based), lorand, hirand,
 *     filter: null | {type, cutoff (Hz), q (dB), veltrack (cents), keytrack (cents/key), keycenter,
 *                     env: null | {depth (cents), delay, attack, hold, decay, sustain, release}},
 *     cc: [[num, lo, hi]] (conditions), mods: [{target, cc, depth, curve}] (SFZ *_onccN),
 *     rtDecay (dB/s for release triggers), notePolyphony (0 = unlimited), swLast (null | key)
 *   }
 *
 * SF2 ATTENUATION — initialAttenuation is scaled by 0.4 (FluidSynth / EMU10K
 *   convention: 1 cB of generator = 0.04 dB), which is what most GM banks
 *   (incl. GeneralUser GS) are voiced for. instrument(i, ctx, {attenuationScale: 1})
 *   gives the strict spec reading (modulator contributions are never scaled).
 *   Modulators (pmod/imod + the default velocity→attenuation one, 960 cB
 *   concave = 40·log10(vel/127) dB) are evaluated once per voice at note-on from
 *   velocity, key and CC values; they can move any generator the engine uses
 *   (filter Fc/Q, attenuation, pan, tuning, envelopes, sample offsets). The
 *   default velocity→filter modulator is NOT applied (FluidSynth's version of it is
 *   a quirk; most banks override it). Not applied: LFOs (vib/mod), modEnv→pitch,
 *   chorus/reverb sends, continuous modulation after note-on, pressure sources.
 *
 * SFZ — headers control/global/master/group/region/curve, #define, #include
 *   (relative to the root file, then to the including file), default_path,
 *   note_offset/octave_offset, set_cc/set_hdcc, keyswitches (sw_lokey/hikey/
 *   last/default), locc/hicc, *_onccN / *_ccN (+ _curveccN) on volume, amplitude,
 *   pan, tune/pitch, offset, ampeg_*, amp_veltrack, cutoff (CC 7/10 mods are left
 *   to the device's own volume/pan), amp_velcurve_N, rt_decay, note_polyphony,
 *   generators *silence / *sine / *noise. Everything else is listed in inst.unsupported.
 */
(function (root) {
"use strict";

const clamp = (v, a, b) => (v < a ? a : v > b ? b : v);
const isNum = v => typeof v === 'number' && isFinite(v);
const dbToGain = db => Math.pow(10, db / 20);
const NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
const LETTER = { c: 0, d: 2, e: 4, f: 5, g: 7, a: 9, b: 11 };

// ═══════════════════════════════════════════════════════════════════
// note names (C4 = 60 — SFZ, midi-js, tonejs and VCSL all agree)
// ═══════════════════════════════════════════════════════════════════
function noteNameToMidi(str) {
  if (str == null) return null;
  if (typeof str === 'number') return isFinite(str) ? Math.round(str) : null;
  const s = String(str).trim();
  if (/^-?\d+$/.test(s)) return parseInt(s, 10);
  const m = /^([A-Ga-g])(#|♯|s|b|♭)?(-?\d{1,2})$/.exec(s);
  if (!m) return null;
  let n = LETTER[m[1].toLowerCase()];
  if (m[2] === '#' || m[2] === '♯' || m[2] === 's') n++;
  else if (m[2] === 'b' || m[2] === '♭') n--;
  return n + (parseInt(m[3], 10) + 1) * 12;
}
function midiToNoteName(n) {
  n = Math.round(n);
  return NOTE_NAMES[((n % 12) + 12) % 12] + (Math.floor(n / 12) - 1);
}

// ═══════════════════════════════════════════════════════════════════
// paths / URLs
// ═══════════════════════════════════════════════════════════════════
const hasScheme = s => /^[a-z][a-z0-9+.-]*:/i.test(s);
function dirOf(url) {
  const s = String(url || '');
  const q = s.search(/[?#]/), base = q >= 0 ? s.slice(0, q) : s;
  const i = base.lastIndexOf('/');
  return i >= 0 ? base.slice(0, i + 1) : '';
}
// rel is a raw file path (as written in an SFZ: spaces, '#', backslashes) —
// every segment is percent-encoded, then joined onto dir with ./.. resolved.
function resolveUrl(dir, rel) {
  rel = String(rel || '').replace(/\\/g, '/');
  if (/^data:|^blob:/i.test(rel) || (hasScheme(rel) && /^[a-z][a-z0-9+.-]*:\/\//i.test(rel))) return rel;
  const enc = rel.split('/').map(seg => (seg === '.' || seg === '..') ? seg : encodeURIComponent(seg)).join('/');
  let prefix = '', path = dir || '';
  const m = /^([a-z][a-z0-9+.-]*:\/\/[^/]*)(.*)$/i.exec(path) || /^([a-z][a-z0-9+.-]*:)(.*)$/i.exec(path);
  if (m) { prefix = m[1]; path = m[2]; }
  if (enc.startsWith('/')) path = '';
  const parts = (path + enc).split('/');
  const out = [];
  parts.forEach((p, i) => {
    if (p === '.') return;
    if (p === '..') { if (out.length > 1) out.pop(); return; }
    if (p === '' && i > 0 && i < parts.length - 1) return;   // collapse '//'
    out.push(p);
  });
  return prefix + out.join('/');
}
function fileNameOf(url) {
  const s = String(url || '').split(/[?#]/)[0];
  let n = s.slice(s.lastIndexOf('/') + 1);
  try { n = decodeURIComponent(n); } catch (e) { /* keep */ }
  return n;
}

// ═══════════════════════════════════════════════════════════════════
// zones
// ═══════════════════════════════════════════════════════════════════
function defaultEnv() { return { delay: 0, attack: 0, hold: 0, decay: 0, sustain: 1, release: 0.001, dbDecay: false, keyHold: 0, keyDecay: 0 }; }
function makeZone(o) {
  const z = {
    sample: null, data: null, buffer: null, srcRate: 0, generator: null, name: '',
    lokey: 0, hikey: 127, lovel: 0, hivel: 127, lochan: 1, hichan: 16,
    root: 60, tune: 0, keytrack: 100, velPitch: 0, fixedKey: -1, fixedVel: -1,
    gain: 0, pan: 0, ampVeltrack: 1, velCurve: null,
    env: defaultEnv(),
    loopMode: null, loopStart: null, loopEnd: null, offset: 0, end: null,
    trigger: 'attack', group: 0, offBy: 0, offMode: 'fast', offTime: 0.006,
    seqLength: 1, seqPosition: 1, lorand: 0, hirand: 1,
    filter: null, cc: [], mods: [], rtDecay: 0, notePolyphony: 0, swLast: null,
  };
  if (o) { const env = o.env; Object.assign(z, o); z.env = Object.assign(defaultEnv(), env || {}); }
  return z;
}
function newInstrument(format, name) {
  return { format, name: name || '', zones: [], unsupported: [], warnings: [], ccInit: {}, curves: {}, keyswitch: null, bend: null };
}

// default MIDI curves (SFZ v2 curve indexes 0..6)
function builtinCurve(i) {
  const c = new Float32Array(128);
  for (let v = 0; v < 128; v++) {
    const x = v / 127;
    c[v] = i === 1 ? 2 * x - 1 : i === 2 ? 1 - x : i === 3 ? 1 - 2 * x : i === 4 ? x * x : i === 5 ? Math.sqrt(x) : i === 6 ? Math.sqrt(1 - x) : x;
  }
  return c;
}
function curveFromPoints(pts, d0, d127) {   // pts: {vel: value}
  const keys = Object.keys(pts).map(Number).filter(k => k >= 0 && k <= 127);
  const P = new Map(keys.map(k => [k, pts[k]]));
  if (!P.has(0)) P.set(0, d0);
  if (!P.has(127)) P.set(127, d127);
  const ks = [...P.keys()].sort((a, b) => a - b);
  const c = new Float32Array(128);
  for (let i = 0; i < ks.length - 1; i++) {
    const a = ks[i], b = ks[i + 1], va = P.get(a), vb = P.get(b);
    for (let v = a; v <= b; v++) c[v] = va + (vb - va) * (b === a ? 0 : (v - a) / (b - a));
  }
  return c;
}

// ═══════════════════════════════════════════════════════════════════
// SFZ
// ═══════════════════════════════════════════════════════════════════
// retries on a network error (not on an HTTP error status): 3 attempts, backing off
function fetchRetry(url, attempt) {
  attempt = attempt || 0;
  return fetch(url).catch(e => {
    if (attempt >= 2) throw e;
    return new Promise(r => setTimeout(r, 300 * Math.pow(3, attempt))).then(() => fetchRetry(url, attempt + 1));
  });
}
// at most n calls of fn in flight
function limiter(fn, n) {
  let active = 0;
  const queue = [];
  const pump = () => {
    while (active < n && queue.length) {
      const job = queue.shift();
      active++;
      Promise.resolve().then(() => fn(job.arg)).then(job.res, job.rej).then(() => { active--; pump(); });
    }
  };
  return arg => new Promise((res, rej) => { queue.push({ arg, res, rej }); pump(); });
}
const defaultReadText = url => fetchRetry(url).then(r => { if (!r.ok) throw new Error('HTTP ' + r.status + ' ' + url); return r.text(); });

function substDefines(s, defines) {
  if (s.indexOf('$') < 0) return s;
  return s.replace(/\$[A-Za-z_][A-Za-z0-9_]*/g, tok => {
    if (defines.has(tok)) return defines.get(tok);
    for (let n = tok.length - 1; n > 1; n--) { const p = tok.slice(0, n); if (defines.has(p)) return defines.get(p) + tok.slice(n); }
    return tok;
  });
}
// Fetch every literal #include of a file (and theirs, recursively) in parallel;
// the in-order pass below then awaits the cached promises.
function sfzPrefetch(text, rootDir, curDir, readText, cache, budget) {
  const re = /#include\s+"([^"$]*)"/g;
  let m;
  while ((m = re.exec(text)) && budget.n-- > 0) {
    const url = resolveUrl(rootDir, m[1].replace(/\\/g, '/'));
    if (cache.has(url)) continue;
    const p = Promise.resolve().then(() => readText(url));
    cache.set(url, p);
    p.then(t => sfzPrefetch(String(t).replace(/\/\/[^\n]*/g, ''), rootDir, dirOf(url), readText, cache, budget), () => {});
  }
}
async function sfzPreprocess(text, rootDir, curDir, defines, readText, depth, warnings, seen) {
  if (depth > 16) { warnings.push('#include nested too deeply'); return ''; }
  text = String(text).replace(/\/\*[\s\S]*?\*\//g, ' ');
  const lines = text.split(/\r\n|\r|\n/);
  const out = [];
  for (let line of lines) {
    const ci = line.indexOf('//');
    if (ci >= 0) line = line.slice(0, ci);
    if (line.indexOf('#') < 0) { out.push(substDefines(line, defines)); continue; }
    let rest = line, buf = '';
    for (;;) {
      const m = /#(include|define)\b/.exec(rest);
      if (!m) { buf += substDefines(rest, defines); break; }
      buf += substDefines(rest.slice(0, m.index), defines);
      rest = rest.slice(m.index);
      if (m[1] === 'define') {
        const d = /^#define\s+(\$[A-Za-z_][A-Za-z0-9_]*)\s+(\S+)/.exec(rest);
        if (!d) { rest = rest.replace(/^#define\S*\s*\S*/, ''); continue; }
        defines.set(d[1], substDefines(d[2], defines));
        rest = rest.slice(d[0].length);
      } else {
        const d = /^#include\s+(?:"([^"]*)"|<([^>]*)>|(\S+))/.exec(rest);
        if (!d) { rest = rest.slice(8); continue; }
        rest = rest.slice(d[0].length);
        const path = substDefines(d[1] || d[2] || d[3] || '', defines).replace(/\\/g, '/');
        out.push(buf); buf = '';
        const tries = [resolveUrl(rootDir, path)];
        if (curDir !== rootDir) tries.push(resolveUrl(curDir, path));
        let got = null, used = null;
        for (const u of tries) {
          try { got = await readText(u); used = u; break; } catch (e) { /* next */ }
        }
        if (got == null) { warnings.push('#include not found: ' + path); continue; }
        if (seen.size > 2000) { warnings.push('too many #include files'); continue; }
        seen.add(used);
        out.push(await sfzPreprocess(got, rootDir, dirOf(used), defines, readText, depth + 1, warnings, seen));
      }
    }
    out.push(buf);
  }
  return out.join('\n');
}

const SFZ_SILENT = /^(region_label|group_label|master_label|global_label|sw_label|label_cc\d+|label_key\d+|hint_.*|image|image_controls|define|sw_note_offset|sw_octave_offset|set_realcc\d+|vNNN)$/;
const SFZ_MOD_TARGETS = {
  volume: 'volume', gain: 'volume', amplitude: 'amplitude', pan: 'pan', tune: 'tune', pitch: 'tune',
  offset: 'offset', amp_veltrack: 'amp_veltrack', cutoff: 'cutoff',
  ampeg_delay: 'delay', ampeg_attack: 'attack', ampeg_hold: 'hold', ampeg_decay: 'decay', ampeg_sustain: 'sustain', ampeg_release: 'release',
};
const FIL_TYPES = { lpf: 'lowpass', hpf: 'highpass', bpf: 'bandpass', brf: 'notch', apf: 'allpass', pkf: 'peaking', lsh: 'lowshelf', hsh: 'highshelf' };

async function parseSFZ(text, baseUrl, opts) {
  opts = opts || {};
  const readText = opts.readText || defaultReadText;
  const rootDir = dirOf(baseUrl || '');
  const warnings = [];
  const defines = new Map();
  const cache = new Map();
  const limited = limiter(readText, opts.concurrency || 8);
  const cachedRead = url => { if (!cache.has(url)) cache.set(url, limited(url)); return cache.get(url); };
  sfzPrefetch(String(text).replace(/\/\/[^\n]*/g, ''), rootDir, rootDir, limited, cache, { n: 3000 });
  const body = await sfzPreprocess(text, rootDir, rootDir, defines, cachedRead, 0, warnings, new Set());
  const inst = newInstrument('sfz', opts.name || fileNameOf(baseUrl).replace(/\.sfz$/i, '') || 'SFZ');
  inst.warnings = warnings;
  inst.source = baseUrl || '';
  const unsupported = new Map();
  const noteUnsup = k => { const n = k.replace(/\d+/g, 'N'); unsupported.set(n, (unsupported.get(n) || 0) + 1); };

  // tokens: <header> | name=value
  const re = /<([A-Za-z_]+)>|(^|[\s>])([A-Za-z0-9_]+)=/g;
  const toks = [];
  let m;
  while ((m = re.exec(body))) {
    if (m[1]) toks.push({ h: m[1].toLowerCase(), at: m.index, end: m.index + m[0].length });
    else { const at = m.index + m[2].length; toks.push({ k: m[3], at, end: at + m[3].length + 1 }); }
  }
  const control = { default_path: '', note_offset: 0, octave_offset: 0 };
  let level = 'none', glob = {}, master = {}, group = {}, region = null, curve = null;
  const curvesRaw = {};
  const flush = () => {
    if (region) {
      const op = Object.assign({}, glob, master, group, region);
      try { const z = sfzZone(op, control, rootDir, inst, noteUnsup); if (z) inst.zones.push(z); }
      catch (e) { warnings.push('region skipped: ' + (e.message || e)); }
      region = null;
    }
    if (curve) {
      const idx = parseInt(curve.curve_index, 10);
      if (isFinite(idx)) { const pts = {}; for (const k in curve) { const mm = /^v(\d{1,3})$/.exec(k); if (mm) pts[+mm[1]] = parseFloat(curve[k]); } curvesRaw[idx] = pts; }
      curve = null;
    }
  };
  for (let i = 0; i < toks.length; i++) {
    const t = toks[i];
    if (t.h) {
      flush();
      level = t.h;
      if (level === 'global') { glob = {}; master = {}; group = {}; }
      else if (level === 'master') { master = {}; group = {}; }
      else if (level === 'group') { group = {}; }
      else if (level === 'region') { region = {}; }
      else if (level === 'curve') { curve = {}; }
      else if (level !== 'control') { if (!/^(effect|midi|sample)$/.test(level)) noteUnsup('<' + level + '>'); level = 'ignore'; }
      continue;
    }
    const next = toks[i + 1];
    let val = body.slice(t.end, next ? next.at : body.length).trim();
    const k = t.k;
    if (!(k === 'sample' || k === 'default_path' || /label/.test(k))) val = val.split(/\s+/)[0] || '';
    if (level === 'control') {
      let mm;
      if (k === 'default_path') control.default_path = val.replace(/\\/g, '/');
      else if (k === 'note_offset') control.note_offset = parseInt(val, 10) || 0;
      else if (k === 'octave_offset') control.octave_offset = parseInt(val, 10) || 0;
      else if ((mm = /^set_cc(\d+)$/.exec(k))) inst.ccInit[+mm[1]] = clamp(parseFloat(val) || 0, 0, 127);
      else if ((mm = /^set_hdcc(\d+)$/.exec(k))) inst.ccInit[+mm[1]] = clamp((parseFloat(val) || 0) * 127, 0, 127);
      else if (!SFZ_SILENT.test(k)) noteUnsup('control.' + k);
      continue;
    }
    if (level === 'curve') { if (curve) curve[k] = val; continue; }
    if (level === 'ignore') continue;
    const target = level === 'region' ? region : level === 'group' ? group : level === 'master' ? master : glob;
    if (target) target[k] = val;
  }
  flush();
  for (const idx in curvesRaw) inst.curves[idx] = curveFromPoints(curvesRaw[idx], 0, 1);
  // resolve mod curves now that <curve> headers are known
  for (const z of inst.zones) for (const md of z.mods) md.curveData = inst.curves[md.curve] || builtinCurve(md.curve);
  inst.unsupported = [...unsupported.entries()].map(([k, n]) => n > 1 ? k + ' ×' + n : k);
  if (inst.keyswitch && inst.keyswitch.def == null) inst.keyswitch.def = inst.keyswitch.lo;
  return inst;
}

function sfzKey(v, control) {
  const n = noteNameToMidi(v);
  if (n == null) return null;
  return n + (control.note_offset || 0) + 12 * (control.octave_offset || 0);
}
function sfzZone(op, control, rootDir, inst, noteUnsup) {
  const z = makeZone();
  const f = (k, d) => { const v = parseFloat(op[k]); return isFinite(v) ? v : d; };
  const key = k => op[k] == null ? null : sfzKey(op[k], control);
  if (op.sample == null || op.sample === '') return null;
  const smp = op.sample.trim();
  if (smp.startsWith('*')) {
    const g = smp.slice(1).toLowerCase();
    z.generator = g === 'sine' ? 'sine' : g === 'noise' ? 'noise' : 'silence';
    if (!/^(silence|sine|noise)$/.test(g)) noteUnsup('sample=*' + g);
  } else {
    z.sample = resolveUrl(rootDir, (control.default_path || '') + smp.replace(/\\/g, '/'));
  }
  z.name = op.region_label || fileNameOf(smp.replace(/\\/g, '/'));
  const used = new Set(['sample']);
  const u = k => used.add(k);
  if (op.key != null) { const kk = key('key'); if (kk != null) { z.lokey = z.hikey = z.root = kk; } u('key'); }
  if (op.lokey != null) { const kk = key('lokey'); z.lokey = kk == null ? 0 : kk; u('lokey'); }
  if (op.hikey != null) { const kk = key('hikey'); z.hikey = kk == null ? 127 : kk; u('hikey'); }
  if (op.pitch_keycenter != null) {
    u('pitch_keycenter');
    if (/^sample$/i.test(op.pitch_keycenter)) z.rootFromFile = true;
    else { const kk = key('pitch_keycenter'); if (kk != null) z.root = kk; }
  }
  if (op.lovel != null) { z.lovel = clamp(f('lovel', 0), 0, 127); u('lovel'); }
  if (op.hivel != null) { z.hivel = clamp(f('hivel', 127), 0, 127); u('hivel'); }
  if (op.lochan != null) { z.lochan = f('lochan', 1); u('lochan'); }
  if (op.hichan != null) { z.hichan = f('hichan', 16); u('hichan'); }
  z.tune = f('tune', 0) + f('pitch', 0) + 100 * f('transpose', 0); u('tune'); u('pitch'); u('transpose');
  z.keytrack = f('pitch_keytrack', 100); u('pitch_keytrack');
  z.velPitch = f('pitch_veltrack', 0); u('pitch_veltrack');
  z.gain = f('volume', 0) + f('gain', 0); u('volume'); u('gain');
  if (op.amplitude != null) { z.gain += 20 * Math.log10(Math.max(1e-4, f('amplitude', 100) / 100)); u('amplitude'); }
  z.pan = clamp(f('pan', 0) / 100, -1, 1); u('pan');
  z.ampVeltrack = clamp(f('amp_veltrack', 100) / 100, -1, 1); u('amp_veltrack');
  const vc = {};
  for (const k in op) { const mm = /^amp_velcurve_(\d+)$/.exec(k); if (mm) { vc[+mm[1]] = parseFloat(op[k]); u(k); } }
  if (Object.keys(vc).length) z.velCurve = curveFromPoints(vc, 0, 1);
  const e = z.env;
  e.delay = Math.max(0, f('ampeg_delay', 0)); e.attack = Math.max(0, f('ampeg_attack', 0)); e.hold = Math.max(0, f('ampeg_hold', 0));
  e.decay = Math.max(0, f('ampeg_decay', 0)); e.sustain = clamp(f('ampeg_sustain', 100) / 100, 0, 1); e.release = Math.max(0, f('ampeg_release', 0.001));
  ['ampeg_delay', 'ampeg_attack', 'ampeg_hold', 'ampeg_decay', 'ampeg_sustain', 'ampeg_release'].forEach(u);
  const lm = op.loop_mode || op.loopmode;
  if (lm) { if (/^(no_loop|one_shot|loop_continuous|loop_sustain)$/.test(lm)) z.loopMode = lm; else noteUnsup('loop_mode=' + lm); }
  u('loop_mode'); u('loopmode');
  const ls = op.loop_start != null ? f('loop_start', null) : op.loopstart != null ? f('loopstart', null) : null;
  const le = op.loop_end != null ? f('loop_end', null) : op.loopend != null ? f('loopend', null) : null;
  if (ls != null && le != null && le > ls) { z.loopStart = ls; z.loopEnd = le + 1; }
  ['loop_start', 'loopstart', 'loop_end', 'loopend'].forEach(u);
  z.offset = Math.max(0, f('offset', 0)); u('offset');
  if (op.end != null) { const en = f('end', null); if (en != null && en <= 0) return null; if (en != null) z.end = en + 1; u('end'); }
  const trig = (op.trigger || 'attack').toLowerCase(); u('trigger');
  z.trigger = trig === 'release' || trig === 'release_key' ? 'release' : trig === 'first' ? 'first' : trig === 'legato' ? 'legato' : 'attack';
  z.group = f('group', 0) | 0; z.offBy = f('off_by', f('offby', 0)) | 0; u('group'); u('off_by'); u('offby');
  if (op.off_time != null) { z.offTime = Math.max(0.002, f('off_time', 0.006)); z.offMode = 'time'; }
  if (op.off_mode) z.offMode = /^(fast|normal|time)$/.test(op.off_mode) ? op.off_mode : 'fast';
  u('off_time'); u('off_mode');
  z.seqLength = Math.max(1, f('seq_length', 1) | 0); z.seqPosition = clamp(f('seq_position', 1) | 0, 1, z.seqLength); u('seq_length'); u('seq_position');
  z.lorand = clamp(f('lorand', 0), 0, 1); z.hirand = clamp(f('hirand', 1), 0, 1); u('lorand'); u('hirand');
  z.rtDecay = Math.max(0, f('rt_decay', 0)); u('rt_decay');
  z.notePolyphony = Math.max(0, f('note_polyphony', 0) | 0); u('note_polyphony');
  if (op.cutoff != null) {
    const ft = (op.fil_type || op.filtype || 'lpf_2p').toLowerCase();
    z.filter = { type: FIL_TYPES[ft.slice(0, 3)] || 'lowpass', cutoff: clamp(f('cutoff', 20000), 10, 22000), q: f('resonance', 0),
      veltrack: f('fil_veltrack', 0), keytrack: f('fil_keytrack', 0), keycenter: key('fil_keycenter') ?? 60, env: null };
    if (op.fileg_depth != null && f('fileg_depth', 0) !== 0) {
      z.filter.env = { depth: f('fileg_depth', 0), delay: f('fileg_delay', 0), attack: f('fileg_attack', 0), hold: f('fileg_hold', 0),
        decay: f('fileg_decay', 0), sustain: clamp(f('fileg_sustain', 100) / 100, 0, 1), release: f('fileg_release', 0) };
    }
  }
  ['cutoff', 'resonance', 'fil_type', 'filtype', 'fil_veltrack', 'fil_keytrack', 'fil_keycenter', 'fileg_depth', 'fileg_delay', 'fileg_attack', 'fileg_hold', 'fileg_decay', 'fileg_sustain', 'fileg_release'].forEach(u);
  // keyswitches
  if (op.sw_lokey != null || op.sw_hikey != null) {
    const lo = key('sw_lokey'), hi = key('sw_hikey');
    const ks = inst.keyswitch || (inst.keyswitch = { lo: 127, hi: 0, def: null });
    if (lo != null) ks.lo = Math.min(ks.lo, lo);
    if (hi != null) ks.hi = Math.max(ks.hi, hi);
  }
  if (op.sw_default != null && inst.keyswitch && inst.keyswitch.def == null) inst.keyswitch.def = key('sw_default');
  if (op.sw_last != null) z.swLast = key('sw_last');
  ['sw_lokey', 'sw_hikey', 'sw_default', 'sw_last'].forEach(u);
  if (op.bend_up != null || op.bend_down != null) inst.bend = { up: f('bend_up', 200), down: f('bend_down', -200) };
  ['bend_up', 'bend_down', 'bend_step'].forEach(u);
  // CC conditions + modulation
  const curveOf = {};
  for (const k in op) { const mm = /^(.*?)_curvecc(\d+)$/.exec(k); if (mm) { curveOf[mm[1] + '#' + mm[2]] = parseInt(op[k], 10) || 0; u(k); } }
  const lo = {}, hi = {};
  for (const k in op) {
    let mm;
    if ((mm = /^locc(\d+)$/.exec(k))) { lo[+mm[1]] = f(k, 0); u(k); }
    else if ((mm = /^hicc(\d+)$/.exec(k))) { hi[+mm[1]] = f(k, 127); u(k); }
  }
  for (const n of new Set([...Object.keys(lo), ...Object.keys(hi)])) z.cc.push([+n, lo[n] ?? 0, hi[n] ?? 127]);
  for (const k in op) {
    if (used.has(k)) continue;
    const mm = /^(.*?)_?(?:on)?cc(\d+)$/.exec(k);
    if (mm && SFZ_MOD_TARGETS[mm[1]]) {
      const ccn = +mm[2];
      u(k);
      if (ccn === 7 || ccn === 10) continue;     // the device's own volume / pan
      z.mods.push({ target: SFZ_MOD_TARGETS[mm[1]], cc: ccn, depth: f(k, 0), curve: curveOf[mm[1] + '#' + mm[2]] || 0 });
      continue;
    }
    if (SFZ_SILENT.test(k)) continue;
    noteUnsup(k);
  }
  return z;
}

// ═══════════════════════════════════════════════════════════════════
// SF2 / SF3
// ═══════════════════════════════════════════════════════════════════
const GEN_NAMES = ['startAddrsOffset', 'endAddrsOffset', 'startloopAddrsOffset', 'endloopAddrsOffset', 'startAddrsCoarseOffset',
  'modLfoToPitch', 'vibLfoToPitch', 'modEnvToPitch', 'initialFilterFc', 'initialFilterQ', 'modLfoToFilterFc', 'modEnvToFilterFc',
  'endAddrsCoarseOffset', 'modLfoToVolume', 'unused1', 'chorusEffectsSend', 'reverbEffectsSend', 'pan', 'unused2', 'unused3', 'unused4',
  'delayModLFO', 'freqModLFO', 'delayVibLFO', 'freqVibLFO', 'delayModEnv', 'attackModEnv', 'holdModEnv', 'decayModEnv', 'sustainModEnv',
  'releaseModEnv', 'keynumToModEnvHold', 'keynumToModEnvDecay', 'delayVolEnv', 'attackVolEnv', 'holdVolEnv', 'decayVolEnv', 'sustainVolEnv',
  'releaseVolEnv', 'keynumToVolEnvHold', 'keynumToVolEnvDecay', 'instrument', 'reserved1', 'keyRange', 'velRange',
  'startloopAddrsCoarseOffset', 'keynum', 'velocity', 'initialAttenuation', 'reserved2', 'endloopAddrsCoarseOffset', 'coarseTune',
  'fineTune', 'sampleID', 'sampleModes', 'reserved3', 'scaleTuning', 'exclusiveClass', 'overridingRootKey', 'unused5', 'endOper'];
const G = {}; GEN_NAMES.forEach((n, i) => { G[n] = i; });
const GEN_DEFAULTS = new Int32Array(61);
GEN_DEFAULTS[G.initialFilterFc] = 13500;
[G.delayModLFO, G.delayVibLFO, G.delayModEnv, G.attackModEnv, G.holdModEnv, G.decayModEnv, G.releaseModEnv,
  G.delayVolEnv, G.attackVolEnv, G.holdVolEnv, G.decayVolEnv, G.releaseVolEnv].forEach(i => { GEN_DEFAULTS[i] = -12000; });
GEN_DEFAULTS[G.keyRange] = 127 << 8; GEN_DEFAULTS[G.velRange] = 127 << 8;
GEN_DEFAULTS[G.keynum] = -1; GEN_DEFAULTS[G.velocity] = -1; GEN_DEFAULTS[G.scaleTuning] = 100; GEN_DEFAULTS[G.overridingRootKey] = -1;
// preset-level values for these are ignored (spec 8.5); ranges intersect instead of adding
const NOT_ADDITIVE = new Set([G.startAddrsOffset, G.endAddrsOffset, G.startloopAddrsOffset, G.endloopAddrsOffset, G.startAddrsCoarseOffset,
  G.endAddrsCoarseOffset, G.startloopAddrsCoarseOffset, G.endloopAddrsCoarseOffset, G.keynum, G.velocity, G.sampleModes,
  G.exclusiveClass, G.overridingRootKey, G.instrument, G.sampleID, G.keyRange, G.velRange]);
const UNSUPPORTED_GENS = [G.modLfoToPitch, G.vibLfoToPitch, G.modEnvToPitch, G.modLfoToFilterFc, G.modLfoToVolume, G.chorusEffectsSend, G.reverbEffectsSend];
const tc2s = tc => (tc <= -12000 ? 0 : Math.pow(2, clamp(tc, -12000, 8000) / 1200));

// ── SF2 modulators (evaluated once per voice at note-on: velocity, key,
// CC values, "no controller"; pressure = 0, pitch wheel = centre) ─────
const SF2_DEFAULT_MODS = [
  { src: 0x0502, dest: 48, amount: 960, amtSrc: 0, trans: 0 },      // velocity → attenuation (negative concave)
];
const SF2_MOD_DESTS = new Set([0, 1, 2, 3, 4, 8, 9, 11, 12, 17, 25, 26, 27, 28, 29, 30, 33, 34, 35, 36, 37, 38, 45, 48, 50, 51, 52, 56]);
const sf2SrcSupported = src => (src & 0x80) ? true : [0, 2, 3, 10, 13, 14, 16].includes(src & 127);
const concave = x => x >= 1 ? 1 : x <= 0 ? 0 : clamp(-(20 / 96) * Math.log10((1 - x) * (1 - x)), 0, 1);
const convex = x => 1 - concave(1 - x);
function sf2Src(src, key, v127, ccv) {
  const idx = src & 127, isCC = src & 0x80, dir = (src >> 8) & 1, bip = (src >> 9) & 1, type = src >> 10;
  let x;
  if (isCC) x = ccv ? (ccv[idx] || 0) / 127 : 0;
  else if (idx === 0) return 1;
  else if (idx === 2) x = v127 / 127;
  else if (idx === 3) x = key / 127;
  else if (idx === 14) x = 0.5;
  else if (idx === 16) x = 2 / 127;
  else x = 0;
  if (dir) x = 1 - x;
  const sh = v => type === 1 ? concave(v) : type === 2 ? convex(v) : type === 3 ? (v >= 0.5 ? 1 : 0) : v;
  if (!bip) return sh(x);
  const b = 2 * x - 1;
  if (type === 3) return b >= 0 ? 1 : -1;
  return b >= 0 ? (type === 0 ? b : sh(b)) : (type === 0 ? b : -sh(-b));
}
function sf2ModDeltas(mods, key, v127, ccv, velSens) {
  const d = new Float64Array(61);
  for (const m of mods) {
    let a = m.amount * sf2Src(m.src, key, v127, ccv) * sf2Src(m.amtSrc, key, v127, ccv);
    if (m.trans === 2) a = Math.abs(a);
    if (m.dest === 48 && (m.src & 0xFF) === 2 && velSens !== 1) a *= velSens;
    d[m.dest] += a;
  }
  return d;
}
// generators (+ modulator deltas) → zone parameters
function applySf2(z, g, d, frames) {
  const S = z.sf2.S, V = op => g[op] + (d ? d[op] : 0);
  z.root = g[G.overridingRootKey] >= 0 ? g[G.overridingRootKey] : (S.pitch <= 127 ? S.pitch : 60);
  z.tune = V(G.coarseTune) * 100 + V(G.fineTune) + S.correction;
  z.keytrack = V(G.scaleTuning);
  z.fixedKey = g[G.keynum] >= 0 && g[G.keynum] <= 127 ? g[G.keynum] : -1;
  z.fixedVel = g[G.velocity] >= 1 && g[G.velocity] <= 127 ? g[G.velocity] : -1;
  z.gain = -clamp(Math.max(0, g[G.initialAttenuation]) * z.sf2.attScale + (d ? d[G.initialAttenuation] : 0), 0, 1440) / 10;
  z.pan = clamp(V(G.pan) / 500, -1, 1);
  const susAtt = clamp(V(G.sustainVolEnv), 0, 1440);
  z.env = { delay: tc2s(V(G.delayVolEnv)), attack: tc2s(V(G.attackVolEnv)), hold: tc2s(V(G.holdVolEnv)), decay: tc2s(V(G.decayVolEnv)),
    sustain: susAtt >= 1000 ? 0 : Math.pow(10, -susAtt / 200), release: tc2s(V(G.releaseVolEnv)), dbDecay: true,
    keyHold: g[G.keynumToVolEnvHold], keyDecay: g[G.keynumToVolEnvDecay] };
  const mode = g[G.sampleModes] & 3;
  z.loopMode = mode === 1 ? 'loop_continuous' : mode === 3 ? 'loop_sustain' : 'no_loop';
  const startOff = V(G.startAddrsOffset) + 32768 * V(G.startAddrsCoarseOffset);
  const endOff = V(G.endAddrsOffset) + 32768 * V(G.endAddrsCoarseOffset);
  const lsOff = V(G.startloopAddrsOffset) + 32768 * V(G.startloopAddrsCoarseOffset);
  const leOff = V(G.endloopAddrsOffset) + 32768 * V(G.endloopAddrsCoarseOffset);
  const ex = g[G.exclusiveClass];
  if (ex) { z.group = 1000000 + ex; z.offBy = 1000000 + ex; z.offMode = 'fast'; }
  const fc = V(G.initialFilterFc), fq = V(G.initialFilterQ), fenv = V(G.modEnvToFilterFc);
  z.filter = null;
  if (fc < 13500 || Math.abs(fenv) >= 1) {
    z.filter = { type: 'lowpass', cutoff: clamp(8.176 * Math.pow(2, clamp(fc, 1500, 13500) / 1200), 20, 20000), q: clamp(fq, 0, 960) / 10,
      veltrack: 0, keytrack: 0, keycenter: 60, env: null };
    if (Math.abs(fenv) >= 1) z.filter.env = { depth: fenv, delay: tc2s(V(G.delayModEnv)), attack: tc2s(V(G.attackModEnv)), hold: tc2s(V(G.holdModEnv)),
      decay: tc2s(V(G.decayModEnv)), sustain: clamp(1 - V(G.sustainModEnv) / 1000, 0, 1), release: tc2s(V(G.releaseModEnv)) };
  }
  if (z.sf2.compressed) {          // sf3: positions are relative to the decoded sample
    z.offset = Math.max(0, startOff);
    z.loopStart = S.startLoop + lsOff; z.loopEnd = S.endLoop + leOff;
    z.end = frames != null ? clamp(frames + endOff, z.offset + 1, frames) : null;
    z.endFromTail = endOff < 0 ? -endOff : 0;
  } else {
    const n = frames || 0;
    z.offset = clamp(startOff, 0, Math.max(0, n - 1));
    z.end = clamp(n + endOff, z.offset + 1, n);
    z.loopStart = clamp(S.startLoop - S.start + lsOff, 0, n);
    z.loopEnd = clamp(S.endLoop - S.start + leOff, 0, n);
  }
  if (!(z.loopEnd > z.loopStart + 1)) { z.loopStart = null; z.loopEnd = null; z.loopMode = 'no_loop'; }
  return z;
}

function parseSF2(ab) {
  if (ab instanceof Uint8Array) ab = ab.buffer.slice(ab.byteOffset, ab.byteOffset + ab.byteLength);
  const dv = new DataView(ab), len = ab.byteLength;
  const str = (o, n) => { let s = ''; for (let i = 0; i < n; i++) { const c = dv.getUint8(o + i); if (!c) break; s += String.fromCharCode(c); } return s; };
  if (len < 12 || str(0, 4) !== 'RIFF' || str(8, 4) !== 'sfbk') throw new Error('not a SoundFont (RIFF sfbk) file');
  const info = {}, chunks = {};
  let smpl = null, sm24 = null;
  const walk = (start, end, list) => {
    let o = start;
    while (o + 8 <= end) {
      const id = str(o, 4), size = dv.getUint32(o + 4, true), body = o + 8;
      const bend = Math.min(end, body + size);
      if (id === 'LIST') {
        const type = str(body, 4);
        walk(body + 4, bend, type);
      } else if (list === 'INFO') {
        if (id === 'ifil' && size >= 4) info.version = dv.getUint16(body, true) + '.' + dv.getUint16(body + 2, true);
        else info[id] = str(body, Math.min(size, 256));
      } else if (list === 'sdta') {
        if (id === 'smpl') smpl = { off: body, len: bend - body };
        else if (id === 'sm24') sm24 = { off: body, len: bend - body };
      } else if (list === 'pdta') chunks[id] = { off: body, len: bend - body };
      o = body + size + (size & 1);
    }
  };
  walk(12, len, 'RIFF');
  for (const k of ['phdr', 'pbag', 'pgen', 'inst', 'ibag', 'igen', 'shdr']) if (!chunks[k]) throw new Error('SF2 is missing the ' + k + ' chunk');
  const recs = (id, size, fn) => { const c = chunks[id], n = Math.floor(c.len / size), a = []; for (let i = 0; i < n; i++) a.push(fn(c.off + i * size)); return a; };
  const phdr = recs('phdr', 38, o => ({ name: str(o, 20), program: dv.getUint16(o + 20, true), bank: dv.getUint16(o + 22, true), bag: dv.getUint16(o + 24, true) }));
  const pbag = recs('pbag', 4, o => ({ gen: dv.getUint16(o, true), mod: dv.getUint16(o + 2, true) }));
  const pgen = recs('pgen', 4, o => ({ op: dv.getUint16(o, true), lo: dv.getUint8(o + 2), hi: dv.getUint8(o + 3), s: dv.getInt16(o + 2, true), u: dv.getUint16(o + 2, true) }));
  const insts = recs('inst', 22, o => ({ name: str(o, 20), bag: dv.getUint16(o + 20, true) }));
  const ibag = recs('ibag', 4, o => ({ gen: dv.getUint16(o, true), mod: dv.getUint16(o + 2, true) }));
  const igen = recs('igen', 4, o => ({ op: dv.getUint16(o, true), lo: dv.getUint8(o + 2), hi: dv.getUint8(o + 3), s: dv.getInt16(o + 2, true), u: dv.getUint16(o + 2, true) }));
  const shdr = recs('shdr', 46, o => ({ name: str(o, 20), start: dv.getUint32(o + 20, true), end: dv.getUint32(o + 24, true),
    startLoop: dv.getUint32(o + 28, true), endLoop: dv.getUint32(o + 32, true), rate: dv.getUint32(o + 36, true),
    pitch: dv.getUint8(o + 40), correction: dv.getInt8(o + 41), link: dv.getUint16(o + 42, true), type: dv.getUint16(o + 44, true) }));
  const modCount = (chunks.pmod ? Math.max(0, Math.floor(chunks.pmod.len / 10) - 1) : 0) + (chunks.imod ? Math.max(0, Math.floor(chunks.imod.len / 10) - 1) : 0);
  const isSF3 = shdr.some(s => s.type & 0x10) || /^3\./.test(info.version || '');

  const readMods = id => chunks[id] ? recs(id, 10, o => ({ src: dv.getUint16(o, true), dest: dv.getUint16(o + 2, true), amount: dv.getInt16(o + 4, true),
    amtSrc: dv.getUint16(o + 6, true), trans: dv.getUint16(o + 8, true) })) : [];
  const pmod = readMods('pmod'), imod = readMods('imod');
  // zones of a preset / instrument: [{gens: Map(op → rec), mods: [mod]}], global first (or null)
  const zonesOf = (bags, gens, mods, from, to, terminal) => {
    const zs = [];
    for (let b = from; b < to && b + 1 < bags.length; b++) {
      const g0 = bags[b].gen, g1 = bags[b + 1].gen, map = new Map();
      for (let g = g0; g < g1 && g < gens.length; g++) map.set(gens[g].op, gens[g]);
      const ml = [];
      for (let k = bags[b].mod; k < bags[b + 1].mod && k < mods.length; k++) ml.push(mods[k]);
      zs.push({ gens: map, mods: ml });
    }
    let global = null;
    if (zs.length && !zs[0].gens.has(terminal)) global = zs.shift();
    return { global, zones: zs.filter(z => z.gens.has(terminal)) };
  };
  const modSig = m => m.src + ':' + m.dest + ':' + m.amtSrc + ':' + m.trans;
  const valOf = (rec, op) => (op === G.keyRange || op === G.velRange) ? (rec.lo | (rec.hi << 8)) : (op === G.instrument || op === G.sampleID) ? rec.u : rec.s;

  const presets = phdr.slice(0, -1).map((p, i) => ({ name: p.name.trim(), bank: p.bank, program: p.program, index: i }));
  presets.sort((a, b) => a.bank - b.bank || a.program - b.program);
  const bufCache = new WeakMap();   // ctx → Map(sampleIndex → AudioBuffer)
  const bytesCache = new Map();     // sampleIndex → ArrayBuffer (sf3)

  function sampleBuffer(si, ctx) {
    const s = shdr[si];
    let m = bufCache.get(ctx); if (!m) { m = new Map(); bufCache.set(ctx, m); }
    if (m.has(si)) return m.get(si);
    let buf = null;
    if (smpl && s.end > s.start && !(s.type & 0x8000)) {
      const frames = Math.min(s.end, Math.floor(smpl.len / 2)) - s.start;
      if (frames > 0) {
        buf = ctx.createBuffer(1, frames, clamp(s.rate || 44100, 3000, 768000));
        const out = buf.getChannelData(0);
        const base = smpl.off + s.start * 2;
        if (sm24 && sm24.len >= s.end) {
          const lo = new Uint8Array(ab, sm24.off + s.start, frames);
          for (let i = 0; i < frames; i++) out[i] = ((dv.getInt16(base + i * 2, true) << 8) | lo[i]) / 8388608;
        } else if ((base & 1) === 0) {
          const pcm = new Int16Array(ab, base, frames);
          for (let i = 0; i < frames; i++) out[i] = pcm[i] / 32768;
        } else {
          for (let i = 0; i < frames; i++) out[i] = dv.getInt16(base + i * 2, true) / 32768;
        }
      }
    }
    m.set(si, buf);
    return buf;
  }
  function sampleBytes(si) {
    if (bytesCache.has(si)) return bytesCache.get(si);
    const s = shdr[si];
    let b = null;
    if (smpl && s.end > s.start && s.end <= smpl.len) b = ab.slice(smpl.off + s.start, smpl.off + s.end);
    bytesCache.set(si, b);
    return b;
  }

  function instrument(presetIndex, ctx, iopts) {
    iopts = iopts || {};
    const attScale = isNum(iopts.attenuationScale) ? iopts.attenuationScale : 0.4;
    const p = phdr[presetIndex];
    if (!p || presetIndex >= phdr.length - 1) throw new Error('no preset ' + presetIndex);
    const out = newInstrument(isSF3 ? 'sf3' : 'sf2', p.name.trim());
    out.bank = p.bank; out.program = p.program; out.attenuationScale = attScale;
    const uns = new Map();
    const P = zonesOf(pbag, pgen, pmod, p.bag, phdr[presetIndex + 1].bag, G.instrument);
    for (const pz of P.zones) {
      const pg = new Map();
      if (P.global) for (const [op, r] of P.global.gens) pg.set(op, valOf(r, op));
      for (const [op, r] of pz.gens) pg.set(op, valOf(r, op));
      const pm = new Map();
      if (P.global) for (const m of P.global.mods) pm.set(modSig(m), m);
      for (const m of pz.mods) pm.set(modSig(m), m);
      const ii = pg.get(G.instrument);
      const I = insts[ii];
      if (!I || ii >= insts.length - 1) continue;
      const IZ = zonesOf(ibag, igen, imod, I.bag, insts[ii + 1].bag, G.sampleID);
      for (const iz of IZ.zones) {
        const g = Int32Array.from(GEN_DEFAULTS);
        if (IZ.global) for (const [op, r] of IZ.global.gens) if (op < 61) g[op] = valOf(r, op);
        for (const [op, r] of iz.gens) if (op < 61) g[op] = valOf(r, op);
        // ranges intersect
        const pk = pg.has(G.keyRange) ? pg.get(G.keyRange) : 127 << 8, pv = pg.has(G.velRange) ? pg.get(G.velRange) : 127 << 8;
        const klo = Math.max(g[G.keyRange] & 255, pk & 255), khi = Math.min(g[G.keyRange] >> 8, pk >> 8);
        const vlo = Math.max(g[G.velRange] & 255, pv & 255), vhi = Math.min(g[G.velRange] >> 8, pv >> 8);
        if (klo > khi || vlo > vhi) continue;
        for (const [op, v] of pg) if (op < 61 && !NOT_ADDITIVE.has(op)) g[op] += v;
        const si = g[G.sampleID], sh = shdr[si];
        if (!sh || si >= shdr.length - 1) continue;
        if (sh.type & 0x8000) { uns.set('ROM samples', (uns.get('ROM samples') || 0) + 1); continue; }
        for (const op of UNSUPPORTED_GENS) if (g[op] && op !== G.reverbEffectsSend && op !== G.chorusEffectsSend) uns.set(GEN_NAMES[op], (uns.get(GEN_NAMES[op]) || 0) + 1);
        // modulators: defaults < instrument global < instrument local; preset ones add on top
        const mm = new Map(SF2_DEFAULT_MODS.map(m => [modSig(m), m]));
        if (IZ.global) for (const m of IZ.global.mods) mm.set(modSig(m), m);
        for (const m of iz.mods) mm.set(modSig(m), m);
        for (const [k, m] of pm) { const e = mm.get(k); mm.set(k, e ? Object.assign({}, e, { amount: e.amount + m.amount }) : m); }
        const mods = [];
        for (const m of mm.values()) {
          if (!m.amount || m.dest >= 61) continue;
          if (!SF2_MOD_DESTS.has(m.dest) || !sf2SrcSupported(m.src) || !sf2SrcSupported(m.amtSrc)) {
            const nm = 'modulator→' + (GEN_NAMES[m.dest] || m.dest);
            if (m.dest !== G.reverbEffectsSend && m.dest !== G.chorusEffectsSend) uns.set(nm, (uns.get(nm) || 0) + 1);
            continue;
          }
          mods.push(m);
        }
        const z = makeZone();
        z.name = sh.name.trim();
        z.lokey = klo; z.hikey = khi; z.lovel = vlo; z.hivel = vhi;
        z.ampVeltrack = 0;          // velocity → level is the vel→attenuation modulator
        const compressed = !!(sh.type & 0x10);
        z.sf2 = { g, mods, S: { start: sh.start, end: sh.end, startLoop: sh.startLoop, endLoop: sh.endLoop, rate: sh.rate, pitch: sh.pitch, correction: sh.correction }, attScale, compressed };
        if (compressed) {
          z.data = sampleBytes(si);
          z.srcRate = sh.rate;
          z.sampleKey = 'sf3:' + si;
          applySf2(z, g, null, null);
        } else {
          const buf = ctx ? sampleBuffer(si, ctx) : null;
          z.buffer = buf; z.srcRate = sh.rate;
          applySf2(z, g, null, buf ? buf.length : (sh.end - sh.start));
          if (!buf) z.error = 'no sample data';
        }
        out.zones.push(z);
      }
    }
    out.unsupported = [...uns.entries()].map(([k, n]) => k + ' ×' + n);
    out.sampleRates = [...new Set(out.zones.map(z => z.srcRate))];
    return out;
  }
  return {
    name: (info.INAM || 'SoundFont').trim(), info, version: info.version || '', isSF3,
    presets, sampleBytes: (smpl ? smpl.len : 0) + (sm24 ? sm24.len : 0), sampleCount: Math.max(0, shdr.length - 1),
    modulators: modCount, instrument,
  };
}

// ═══════════════════════════════════════════════════════════════════
// folders of note-named files, midi-js soundfonts
// ═══════════════════════════════════════════════════════════════════
const DYN = { ppp: 1, pp: 2, p: 3, mp: 4, mf: 5, f: 6, ff: 7, fff: 8 };
function parseSampleName(fullName) {
  const name = String(fullName).replace(/\\/g, '/').split('/').pop().replace(/\.[A-Za-z0-9]{2,5}$/, '');
  const notes = [];
  const re = /(?:^|[^A-Za-z])([A-Ga-g])(#|♯|s|b|♭)?(-?\d)(?![0-9])/g;
  let m;
  while ((m = re.exec(name))) {
    // "As3"-style sharps: the 's' must not be the start of a word ("_Es1" is fine, "Ds" ok)
    const n = noteNameToMidi(m[1] + (m[2] || '') + m[3]);
    if (n != null && n >= 0 && n <= 127) notes.push({ n, upper: m[1] === m[1].toUpperCase(), at: m.index, text: m[1] + (m[2] || '') + m[3] });
    re.lastIndex = m.index + 1;
  }
  const up = notes.filter(x => x.upper);
  const pick = (up.length ? up : notes);
  const noteTok = pick.length ? pick[pick.length - 1] : null;
  const note = noteTok ? noteTok.n : null;
  let vel = null, rr = null, m2;
  const vre = /(?:^|[^A-Za-z])v(?:l|el)?(\d{1,3})(?![0-9])/gi;
  while ((m2 = vre.exec(name))) vel = +m2[1];
  if (vel == null) {
    // dynamics (pp, mf, f1 …) — but never the token that is the note itself ("F4")
    for (const tok of name.split(/[_\-\s.]+/)) { if (noteTok && tok === noteTok.text) continue; const d = /^(ppp|pp|p|mp|mf|f|ff|fff)(\d*)$/i.exec(tok); if (d) vel = DYN[d[1].toLowerCase()]; }
  }
  const rre = /(?:^|[^A-Za-z])(?:rr|seq|r)(\d{1,2})(?![0-9])/gi;
  while ((m2 = rre.exec(name))) rr = +m2[1];
  const rel = /(?:^|[^A-Za-z])rel(?:ease)?(?:[^A-Za-z]|$)/i.test(name) || /[a-z]Rel(?:[^a-z]|$)/.test(name);
  return { base: name, note, vel, rr, rel };
}
function spreadKeys(roots) {
  const r = [...new Set(roots)].sort((a, b) => a - b), out = new Map();
  r.forEach((k, i) => {
    const lo = i === 0 ? 0 : Math.floor((r[i - 1] + k) / 2) + 1;
    const hi = i === r.length - 1 ? 127 : Math.floor((k + r[i + 1]) / 2);
    out.set(k, [lo, hi]);
  });
  return out;
}
function instrumentFromFiles(files, opts) {
  opts = opts || {};
  const inst = newInstrument(opts.format || 'files', opts.name || 'Samples');
  inst.unmapped = [];
  const parsed = [];
  let nextChrom = isNum(opts.chromaticFrom) ? opts.chromaticFrom : null;
  for (const f of files || []) {
    if (!f) continue;
    const nm = f.name || fileNameOf(f.url || '');
    const p = parseSampleName(nm);
    if (p.note != null && opts.octaveOffset) p.note = clamp(p.note + 12 * opts.octaveOffset, 0, 127);
    if (p.note == null) {
      if (nextChrom != null && nextChrom <= 127) { p.note = nextChrom++; p.fixed = true; }
      else { inst.unmapped.push(nm); continue; }
    }
    p.file = f; p.nm = nm;
    parsed.push(p);
  }
  const relKinds = [false, true];
  for (const rel of relKinds) {
    const set = parsed.filter(p => !!p.rel === rel);
    if (!set.length) continue;
    // a "layer" covering only a few notes (tonejs cello's "F2 v2.mp3", "G2 v2.mp3") is a pair of
    // alternate takes, not a velocity layer: spread on its own it would cover the whole keyboard
    // at high velocity. Fold sparse layers into the densest one as round-robin alternates.
    {
      const count = new Map();
      for (const p of set) { const v = p.vel == null ? 0 : p.vel; count.set(v, (count.get(v) || new Set()).add(p.note)); }
      let dense = 0, denseN = -1; for (const [v, ns] of count) if (ns.size > denseN) { dense = v; denseN = ns.size; }
      for (const p of set) { const v = p.vel == null ? 0 : p.vel; if (count.get(v).size < Math.max(3, denseN / 2)) p.vel = dense === 0 ? null : dense; }
    }
    const vels = [...new Set(set.map(p => p.vel == null ? 0 : p.vel))].sort((a, b) => a - b);
    vels.forEach((vv, li) => {
      const layer = set.filter(p => (p.vel == null ? 0 : p.vel) === vv);
      const lovel = li === 0 ? 0 : Math.floor(li * 127 / vels.length) + 1;
      const hivel = li === vels.length - 1 ? 127 : Math.floor((li + 1) * 127 / vels.length);
      const spread = opts.spread === false ? null : spreadKeys(layer.filter(p => !p.fixed).map(p => p.note));
      const byRoot = new Map();
      for (const p of layer) { const a = byRoot.get(p.note) || []; a.push(p); byRoot.set(p.note, a); }
      for (const [rootKey, ps] of byRoot) {
        ps.sort((a, b) => (a.rr || 0) - (b.rr || 0) || (a.nm < b.nm ? -1 : 1));
        ps.forEach((p, ri) => {
          const range = (!p.fixed && spread) ? spread.get(rootKey) : [rootKey, rootKey];
          const z = makeZone({
            name: p.nm, sample: p.file.url || null, data: p.file.bytes || p.file.data || null,
            root: rootKey, lokey: range[0], hikey: range[1], lovel, hivel, spread: !p.fixed && !!spread,
            seqLength: ps.length, seqPosition: ri + 1,
            trigger: rel ? 'release' : 'attack',
            loopMode: rel ? 'one_shot' : (opts.loopMode || (p.fixed ? 'one_shot' : null)),
            env: { attack: opts.attack || 0, release: rel ? 0.05 : (isNum(opts.release) ? opts.release : 0.25) },
          });
          if (rel && isNum(opts.releaseGain)) z.gain = opts.releaseGain;
          inst.zones.push(z);
        });
      }
    });
  }
  return inst;
}
// YIN fundamental estimate of an AudioBuffer (channel 0) around t0 seconds → Hz (0 if unvoiced)
// after decoding: drop zones that failed and re-spread the key ranges of spread (note-named)
// zones across the samples that DID load, so a missing file doesn't leave a hole in the keyboard
function respread(inst) {
  const ok = inst.zones.filter(z => !z.error && (z.buffer || z.generator || (!z.sample && !z.data)));
  const groups = new Map();
  for (const z of ok) if (z.spread) { const k = [z.lovel, z.hivel, z.trigger].join('|'); (groups.get(k) || groups.set(k, []).get(k)).push(z); }
  for (const zs of groups.values()) {
    const ranges = spreadKeys(zs.map(z => z.root));
    for (const z of zs) { const r = ranges.get(z.root); z.lokey = r[0]; z.hikey = r[1]; }
    // round-robin counts per root after losses
    const byRoot = new Map(); for (const z of zs) (byRoot.get(z.root) || byRoot.set(z.root, []).get(z.root)).push(z);
    for (const a of byRoot.values()) a.forEach((z, i) => { z.seqLength = a.length; z.seqPosition = i + 1; });
  }
  const dropped = inst.zones.length - ok.length;
  inst.zones = ok;
  return dropped;
}
function detectPitch(buf, t0, fmin, fmax) {
  const sr = buf.sampleRate, x = buf.getChannelData(0), W = 2048;
  const a = Math.min(Math.max(0, Math.floor((t0 || 0.15) * sr)), Math.max(0, x.length - 2 * W - 1));
  if (x.length < 2 * W) return 0;
  const tmin = Math.max(2, Math.floor(sr / (fmax || 2500))), tmax = Math.min(W - 1, Math.ceil(sr / (fmin || 30)));
  const d = new Float64Array(tmax + 2);
  for (let tau = 1; tau <= tmax + 1; tau++) { let s = 0; for (let i = 0; i < W; i++) { const v = x[a + i] - x[a + i + tau]; s += v * v; } d[tau] = s; }
  let run = 0, best = -1;
  const cm = new Float64Array(tmax + 2); cm[0] = 1;
  for (let tau = 1; tau <= tmax + 1; tau++) { run += d[tau]; cm[tau] = run ? d[tau] * tau / run : 1; }
  for (let tau = tmin; tau < tmax; tau++) if (cm[tau] < 0.15) { while (tau + 1 < tmax && cm[tau + 1] < cm[tau]) tau++; best = tau; break; }
  if (best < 0) return 0;
  const y0 = cm[best - 1], y1 = cm[best], y2 = cm[best + 1], den = y0 - 2 * y1 + y2;
  return sr / (best + (den ? 0.5 * (y0 - y2) / den : 0));
}
// Sample names disagree on octave numbering (C3 vs C4 = middle C — VCSL mixes both).
// Measure a few decoded zones and shift every zone by whole octaves when they agree.
function autoOctave(inst, opts) {
  opts = opts || {};
  const zs = inst.zones.filter(z => z.buffer && z.trigger !== 'release' && z.loopMode !== 'one_shot');
  const pick = [];
  for (let i = 0; i < zs.length && pick.length < (opts.maxZones || 7); i += Math.max(1, Math.floor(zs.length / 7))) pick.push(zs[i]);
  const offs = [];
  for (const z of pick) {
    const f = detectPitch(z.buffer, Math.min(0.25, z.buffer.duration / 3));
    if (!f) continue;
    const want = 440 * Math.pow(2, (z.root - 69 - z.tune / 100) / 12);
    offs.push(Math.round(Math.log2(f / want)));
  }
  if (!offs.length) return 0;
  const counts = {}; offs.forEach(o => { counts[o] = (counts[o] || 0) + 1; });
  const best = +Object.keys(counts).sort((p, q) => counts[q] - counts[p])[0];
  if (!best || counts[best] < Math.max(2, Math.ceil(offs.length * 0.6))) return 0;
  const k = 12 * best;
  for (const z of inst.zones) {
    z.root = clamp(z.root + k, 0, 127);
    if (z.lokey > 0) z.lokey = clamp(z.lokey + k, 0, 127);
    if (z.hikey < 127) z.hikey = clamp(z.hikey + k, 0, 127);
  }
  inst.octaveShift = (inst.octaveShift || 0) + best;
  return best;
}
function parseMidiJsSoundfont(text, opts) {
  opts = opts || {};
  const nm = /MIDI\.Soundfont\.([A-Za-z0-9_]+)\s*=/.exec(text);
  const files = [];
  const re = /["']([A-Ga-g][b#]?-?\d)["']\s*:\s*["'](data:[^"']+)["']/g;
  let m;
  while ((m = re.exec(text))) files.push({ name: m[1], url: m[2] });
  if (!files.length) throw new Error('no midi-js notes found (expected "A0": "data:audio/…")');
  const inst = instrumentFromFiles(files, { name: opts.name || (nm ? nm[1].replace(/_/g, ' ') : 'midi-js'), release: isNum(opts.release) ? opts.release : 0.3, format: 'midijs' });
  return inst;
}

// ═══════════════════════════════════════════════════════════════════
// decoding: WAV (manual PCM + smpl loops), FLAC/OGG/MP3 rate sniffing
// ═══════════════════════════════════════════════════════════════════
function parseWav(ab) {
  const dv = new DataView(ab), n = ab.byteLength;
  const s4 = o => String.fromCharCode(dv.getUint8(o), dv.getUint8(o + 1), dv.getUint8(o + 2), dv.getUint8(o + 3));
  if (n < 12 || s4(0) !== 'RIFF' || s4(8) !== 'WAVE') return null;
  const w = { format: 0, channels: 0, rate: 0, bits: 0, blockAlign: 0, dataOffset: -1, dataLength: 0, loops: [], unityNote: null, pitchFraction: 0 };
  let o = 12;
  while (o + 8 <= n) {
    const id = s4(o), size = dv.getUint32(o + 4, true), b = o + 8;
    if (id === 'fmt ' && size >= 16) {
      w.format = dv.getUint16(b, true); w.channels = dv.getUint16(b + 2, true); w.rate = dv.getUint32(b + 4, true);
      w.blockAlign = dv.getUint16(b + 12, true); w.bits = dv.getUint16(b + 14, true);
      if (w.format === 0xFFFE && size >= 26) { w.validBits = dv.getUint16(b + 18, true); w.format = dv.getUint16(b + 24, true); }
    } else if (id === 'data') {
      w.dataOffset = b; w.dataLength = Math.min(size, n - b);
    } else if (id === 'smpl' && size >= 36) {
      w.unityNote = dv.getUint32(b + 12, true);
      w.pitchFraction = dv.getUint32(b + 16, true);
      const nl = dv.getUint32(b + 28, true);
      for (let i = 0; i < nl && b + 36 + i * 24 + 24 <= n; i++) {
        const lo = b + 36 + i * 24;
        w.loops.push({ type: dv.getUint32(lo + 4, true), start: dv.getUint32(lo + 8, true), end: dv.getUint32(lo + 12, true) + 1 });
      }
    }
    if (size > n) break;
    o = b + size + (size & 1);
  }
  if (w.dataOffset < 0 || !w.channels || !w.blockAlign) return null;
  return w;
}
function wavToBuffer(w, ab, ctx) {
  const bytes = w.bits >> 3, ch = w.channels, frames = Math.floor(w.dataLength / w.blockAlign);
  if (frames <= 0) throw new Error('empty WAV');
  const okInt = w.format === 1 && (w.bits === 8 || w.bits === 16 || w.bits === 24 || w.bits === 32);
  const okFloat = w.format === 3 && (w.bits === 32 || w.bits === 64);
  if (!okInt && !okFloat) return null;
  const buf = ctx.createBuffer(ch, frames, clamp(w.rate, 3000, 768000));
  const dv = new DataView(ab), ba = w.blockAlign, base = w.dataOffset;
  for (let c = 0; c < ch; c++) {
    const out = buf.getChannelData(c);
    let o = base + c * bytes;
    if (okFloat && w.bits === 32) for (let i = 0; i < frames; i++, o += ba) out[i] = dv.getFloat32(o, true);
    else if (okFloat) for (let i = 0; i < frames; i++, o += ba) out[i] = dv.getFloat64(o, true);
    else if (w.bits === 16) for (let i = 0; i < frames; i++, o += ba) out[i] = dv.getInt16(o, true) / 32768;
    else if (w.bits === 24) for (let i = 0; i < frames; i++, o += ba) { const v = dv.getUint8(o) | (dv.getUint8(o + 1) << 8) | (dv.getInt8(o + 2) << 16); out[i] = v / 8388608; }
    else if (w.bits === 32) for (let i = 0; i < frames; i++, o += ba) out[i] = dv.getInt32(o, true) / 2147483648;
    else for (let i = 0; i < frames; i++, o += ba) out[i] = (dv.getUint8(o) - 128) / 128;
  }
  return buf;
}
function sniffRate(u8) {
  const n = u8.length, s = (o, l) => String.fromCharCode.apply(null, u8.subarray(o, o + l));
  if (n > 22 && s(0, 4) === 'fLaC') return (u8[18] << 12) | (u8[19] << 4) | (u8[20] >> 4);
  if (n > 40 && s(0, 4) === 'OggS') {
    const lim = Math.min(n - 16, 512);
    for (let i = 0; i < lim; i++) {
      if (u8[i] === 1 && s(i + 1, 6) === 'vorbis') return u8[i + 12] | (u8[i + 13] << 8) | (u8[i + 14] << 16) | (u8[i + 15] << 24);
      if (s(i, 8) === 'OpusHead') return 48000;
    }
    return 0;
  }
  let o = 0;
  if (n > 10 && s(0, 3) === 'ID3') o = 10 + ((u8[6] & 127) << 21 | (u8[7] & 127) << 14 | (u8[8] & 127) << 7 | (u8[9] & 127));
  for (let i = o, lim = Math.min(n - 4, o + 65536); i < lim; i++) {
    if (u8[i] === 0xFF && (u8[i + 1] & 0xE0) === 0xE0) {
      const ver = (u8[i + 1] >> 3) & 3, layer = (u8[i + 1] >> 1) & 3, sri = (u8[i + 2] >> 2) & 3;
      if (ver === 1 || layer === 0 || sri === 3) continue;
      const r = [44100, 48000, 32000][sri];
      return ver === 3 ? r : ver === 2 ? r / 2 : r / 4;
    }
  }
  return 0;
}
function decodeAudio(ctx, ab) {
  return new Promise((res, rej) => {
    let p;
    try { p = ctx.decodeAudioData(ab, res, e => rej(e || new Error('decodeAudioData failed'))); } catch (e) { rej(e); return; }
    if (p && p.then) p.then(res, e => rej(e || new Error('decodeAudioData failed')));
  });
}
async function decodeBytes(ab, ctx, hint) {
  if (ab instanceof Uint8Array) ab = ab.buffer.slice(ab.byteOffset, ab.byteOffset + ab.byteLength);
  const w = parseWav(ab);
  if (w) {
    let buf = null;
    try { buf = wavToBuffer(w, ab, ctx); } catch (e) { buf = null; }
    if (!buf) buf = await decodeAudio(ctx, ab.slice(0));
    return { buffer: buf, rate: w.rate || buf.sampleRate, loops: w.loops, unityNote: w.unityNote, wav: true };
  }
  const rate = sniffRate(new Uint8Array(ab, 0, Math.min(ab.byteLength, 70000)));
  const buf = await decodeAudio(ctx, ab.slice(0));
  return { buffer: buf, rate: rate || buf.sampleRate, loops: [], unityNote: null };
}
function dataUrlToBytes(url) {
  const i = url.indexOf(',');
  const meta = url.slice(5, i), body = url.slice(i + 1);
  if (/;base64/i.test(meta)) {
    const bin = atob(body.replace(/\s/g, ''));
    const u8 = new Uint8Array(bin.length);
    for (let k = 0; k < bin.length; k++) u8[k] = bin.charCodeAt(k);
    return u8.buffer;
  }
  return new TextEncoder().encode(decodeURIComponent(body)).buffer;
}
const defaultFetchBytes = url => {
  if (/^data:/i.test(url)) return Promise.resolve(dataUrlToBytes(url));
  return fetchRetry(url).then(r => { if (!r.ok) throw new Error('HTTP ' + r.status); return r.arrayBuffer(); });
};

async function decodeAll(inst, ctx, fetchBytes, onProgress, opts) {
  opts = opts || {};
  fetchBytes = fetchBytes || defaultFetchBytes;
  const jobs = new Map();
  for (const z of inst.zones) {
    if (z.buffer || z.generator) continue;
    if (!z.sample && !z.data) continue;
    if (z.error && !opts.retry) continue;
    if (opts.filter && !opts.filter(z)) continue;
    const key = z.sampleKey || z.sample || z.data;
    let j = jobs.get(key);
    if (!j) { j = { url: z.sample, data: z.data, zones: [] }; jobs.set(key, j); }
    j.zones.push(z);
  }
  const list = [...jobs.values()];
  const stats = { total: list.length, ok: 0, failed: 0, bytes: 0, seconds: 0, errors: [], ms: 0 };
  const t0 = (typeof performance !== 'undefined' ? performance.now() : Date.now());
  let next = 0, done = 0;
  const work = async () => {
    while (next < list.length) {
      const j = list[next++];
      try {
        const ab = j.data ? j.data.slice(0) : /^data:/i.test(j.url) ? dataUrlToBytes(j.url) : await fetchBytes(j.url);
        stats.bytes += ab.byteLength;
        const d = await decodeBytes(ab, ctx, j.url);
        stats.seconds += d.buffer.duration * d.buffer.numberOfChannels;
        stats.ok++;
        for (const z of j.zones) {
          z.buffer = d.buffer; z.error = null;
          if (!z.srcRate || !z.sampleKey) z.srcRate = d.rate;
          if (z.rootFromFile && d.unityNote != null && d.unityNote <= 127) z.root = d.unityNote;
          if ((z.loopStart == null || z.loopEnd == null) && d.loops && d.loops.length) {
            const L = d.loops[0];
            if (L.end > L.start + 1) { z.loopStart = L.start; z.loopEnd = L.end; z.fileLoop = true; }
          }
          if (z.endFromTail) { const fr = Math.round(d.buffer.duration * z.srcRate); z.end = Math.max(1, fr - z.endFromTail); }
        }
      } catch (e) {
        stats.failed++;
        const msg = String((e && e.message) || e || 'decode failed');
        stats.errors.push({ url: j.url ? String(j.url).slice(0, 200) : '(bytes)', error: msg });
        for (const z of j.zones) { z.buffer = null; z.error = msg; }
      }
      done++;
      if (onProgress) { try { onProgress(done, list.length, stats.bytes); } catch (e) { /* ignore */ } }
    }
  };
  const N = clamp(opts.concurrency || 6, 1, 16);
  await Promise.all(Array.from({ length: Math.min(N, list.length) }, work));
  stats.ms = Math.round((typeof performance !== 'undefined' ? performance.now() : Date.now()) - t0);
  return stats;
}

// Keep at most maxLayers velocity layers per key range (evenly spaced, top
// layer kept), widening the survivors to cover the dropped ranges.
function thinLayers(inst, maxLayers) {
  maxLayers = Math.max(1, maxLayers | 0);
  const groups = new Map();
  for (const z of inst.zones) {
    const k = [z.lokey, z.hikey, z.trigger, z.swLast, z.seqPosition, z.lorand, z.hirand, z.group, (z.cc || []).join(';')].join('|');
    const a = groups.get(k) || []; a.push(z); groups.set(k, a);
  }
  const keep = new Set();
  for (const zs of groups.values()) {
    const ranges = [...new Set(zs.map(z => z.lovel + '-' + z.hivel))].map(s => s.split('-').map(Number)).sort((a, b) => a[0] - b[0]);
    if (ranges.length <= maxLayers) { zs.forEach(z => keep.add(z)); continue; }
    const pick = [];
    for (let i = 0; i < maxLayers; i++) pick.push(ranges[Math.round((i + 1) * ranges.length / maxLayers) - 1]);
    let lo = 0;
    for (const r of pick) {
      const nlo = lo, nhi = r[1];
      for (const z of zs) if (z.lovel === r[0] && z.hivel === r[1]) { z.lovel = nlo; z.hivel = nhi; keep.add(z); }
      lo = nhi + 1;
    }
  }
  inst.zones = inst.zones.filter(z => keep.has(z));
  return inst;
}

// ═══════════════════════════════════════════════════════════════════
// timing helper: run fn at AudioContext time t (live: timer; offline: suspend)
// ═══════════════════════════════════════════════════════════════════
const OFFLINE_SUSPENDS = new WeakMap();
function runAt(ctx, t, fn) {
  const now = ctx.currentTime;
  const isOffline = typeof OfflineAudioContext !== 'undefined' && ctx instanceof OfflineAudioContext;
  if (t <= now + (isOffline ? 0 : 0.004)) { fn(); return; }
  if (isOffline) {
    const q = 128 / ctx.sampleRate, ts = Math.floor(t / q) * q;
    if (ts <= now) { fn(); return; }
    let m = OFFLINE_SUSPENDS.get(ctx); if (!m) { m = new Map(); OFFLINE_SUSPENDS.set(ctx, m); }
    let list = m.get(ts);
    if (!list) {
      list = [];
      try {
        ctx.suspend(ts).then(() => { m.delete(ts); for (const f of list) { try { f(); } catch (e) { /* ignore */ } } ctx.resume(); });
        m.set(ts, list);
      } catch (e) { fn(); return; }
    }
    list.push(fn);
    return;
  }
  setTimeout(fn, Math.max(0, (t - now) * 1000 - 2));
}

// release curve: dB-linear fall by `drop` dB, last point exactly 0
const REL_CURVES = {};
function relCurve(drop) {
  if (REL_CURVES[drop]) return REL_CURVES[drop];
  const N = 96, c = new Float32Array(N);
  for (let i = 0; i < N; i++) c[i] = Math.pow(10, -drop * (i / (N - 1)) / 20);
  c[N - 1] = 0;
  return (REL_CURVES[drop] = c);
}
const GEN_BUFFERS = new WeakMap();
function generatorBuffer(ctx, kind) {
  let m = GEN_BUFFERS.get(ctx); if (!m) { m = {}; GEN_BUFFERS.set(ctx, m); }
  if (m[kind]) return m[kind];
  let b;
  if (kind === 'sine') {   // one cycle of 1024 samples at 450560 Hz = 440 Hz (key 69)
    b = ctx.createBuffer(1, 1024, 450560);
    const d = b.getChannelData(0); for (let i = 0; i < 1024; i++) d[i] = Math.sin(2 * Math.PI * i / 1024);
  } else {
    b = ctx.createBuffer(1, ctx.sampleRate, ctx.sampleRate);
    const d = b.getChannelData(0); for (let i = 0; i < d.length; i++) d[i] = Math.random() * 2 - 1;
  }
  return (m[kind] = b);
}

// ═══════════════════════════════════════════════════════════════════
// SampleInstrument — the device
// ═══════════════════════════════════════════════════════════════════
const DEFAULT_STATE = { v: 1, instrument: null, gain: 0, transpose: 0, tune: 0, attack: 0, release: 1, cutoff: 20000, resonance: 0, velSens: 1, bendRange: 2, mw: 'vibrato' };
const STATE_SPEC = {
  gain: [-48, 12, 0], transpose: [-36, 36, 0, true], tune: [-100, 100, 0], attack: [0, 4, 0], release: [0.05, 8, 1],
  cutoff: [20, 20000, 20000], resonance: [0, 24, 0], velSens: [0, 2, 1], bendRange: [0, 24, 2, true],
};
function normalizeState(s) {
  const o = Object.assign({}, DEFAULT_STATE);
  if (s && typeof s === 'object') {
    for (const k in STATE_SPEC) {
      const [lo, hi, d, int] = STATE_SPEC[k];
      let v = s[k] != null ? +s[k] : d;
      if (!isFinite(v)) v = d;
      v = clamp(v, lo, hi);
      o[k] = int ? Math.round(v) : v;
    }
    o.instrument = s.instrument == null ? null : String(s.instrument);
    o.mw = ['vibrato', 'filter', 'off'].includes(s.mw) ? s.mw : 'vibrato';
  }
  return o;
}

class SampleInstrument {
  constructor(ctx, opts) {
    opts = opts || {};
    if (!ctx) throw new Error('SampleInstrument needs an AudioContext');
    this.ctx = ctx;
    this.maxVoices = clamp(Math.round(opts.maxVoices || 48), 1, 256);
    this._fetch = opts.fetchBytes || null;
    this._resolve = opts.resolveInstrument || null;
    this._bpm = 120;
    this.state = normalizeState(DEFAULT_STATE);
    this.inst = null;
    this.voices = [];
    this.events = [];
    this._pendingOff = [];
    this._chokeLog = [];
    this._pedal = [{ t: -1, down: false }];
    this._ccv = new Float32Array(128);
    this._ls = {};
    this._editors = new Set();
    this._seq = new Map();
    this._sw = null;
    this._evId = 0;
    this._loadSeq = 0;
    this._loading = Promise.resolve();
    this._disposed = false;
    this._mw = 0; this._bend = 0;
    this._offline = typeof OfflineAudioContext !== 'undefined' && ctx instanceof OfflineAudioContext;
    // bus: voices → _in → _filter → _pan → _vol → output → opts.output
    this.output = ctx.createGain();
    this.output.connect(opts.output || ctx.destination);
    this._in = ctx.createGain();
    this._filter = ctx.createBiquadFilter(); this._filter.type = 'lowpass';
    this._pan = ctx.createStereoPanner();
    this._vol = ctx.createGain();
    this._in.connect(this._filter); this._filter.connect(this._pan); this._pan.connect(this._vol); this._vol.connect(this.output);
    this._cc7 = 1;
    // pitch bus (cents) → every voice's detune: bend + mod-wheel vibrato
    this._pitchBus = ctx.createGain();
    this._bendSrc = ctx.createConstantSource(); this._bendSrc.offset.value = 0; this._bendSrc.connect(this._pitchBus);
    this._vib = ctx.createOscillator(); this._vib.frequency.value = 5.4;
    this._vibAmt = ctx.createGain(); this._vibAmt.gain.value = 0;
    this._vib.connect(this._vibAmt); this._vibAmt.connect(this._pitchBus);
    this._bendSrc.start(0); this._vib.start(0);
    this._applyState(null);
  }

  // ── lifecycle ───────────────────────────────────────────────────
  async init() { this._inited = true; return this; }
  loaded() { return this._loading.then(() => this); }
  get bpm() { return this._bpm; }
  set bpm(v) { if (isNum(v)) this._bpm = clamp(v, 20, 400); }
  get instrument() { return this.inst; }
  dispose() {
    if (this._disposed) return;
    this.panic();
    [...this._editors].forEach(e => { try { e.destroy(); } catch (err) { /* ok */ } });
    this._disposed = true;
    try { this._bendSrc.stop(); this._vib.stop(); } catch (e) { /* ok */ }
    [this._bendSrc, this._vib, this._vibAmt, this._pitchBus, this._in, this._filter, this._pan, this._vol, this.output]
      .forEach(n => { try { n.disconnect(); } catch (e) { /* ok */ } });
    this._ls = {};
  }

  // ── events ──────────────────────────────────────────────────────
  on(type, fn) { (this._ls[type] = this._ls[type] || new Set()).add(fn); return () => this.off(type, fn); }
  off(type, fn) { if (this._ls[type]) this._ls[type].delete(fn); }
  _emit(type, d) { const s = this._ls[type]; if (s) for (const fn of [...s]) { try { fn(d); } catch (e) { console.error(e); } } }

  // ── instrument ──────────────────────────────────────────────────
  load(inst, opts) {
    opts = opts || {};
    const seq = ++this._loadSeq;
    const p = (async () => {
      if (!inst || !Array.isArray(inst.zones)) throw new Error('load() needs a normalized instrument {zones: […]}');
      const need = inst.zones.some(z => !z.buffer && !z.generator && (z.sample || z.data) && (!z.error || opts.retry) && !(opts.filter && !opts.filter(z)));
      let stats = null;
      if (need) {
        stats = await decodeAll(inst, this.ctx, opts.fetchBytes || this._fetch, (d, t, b) => {
          this._emit('progress', { done: d, total: t, bytes: b });
          if (opts.onProgress) opts.onProgress(d, t, b);
        }, { filter: opts.filter, concurrency: opts.concurrency, retry: opts.retry });
        inst.loadStats = stats;
      }
      if (seq !== this._loadSeq || this._disposed) return this.info();
      this._setInstrument(inst, opts.id !== undefined ? opts.id : (inst.id != null ? inst.id : null));
      return this.info();
    })();
    this._loading = p.catch(() => {});
    return p;
  }
  _setInstrument(inst, id) {
    this.allOff();
    this.inst = inst;
    this.state.instrument = id == null ? null : String(id);
    this._seq = new Map();
    this._ccv.fill(0);
    this._ccv[7] = 100; this._ccv[10] = 64; this._ccv[11] = 127;
    for (const k in inst.ccInit || {}) this._ccv[+k] = inst.ccInit[k];
    this._sw = inst.keyswitch ? inst.keyswitch.def : null;
    // per-key index of attack / release zones
    this._byKey = Array.from({ length: 128 }, () => []);
    this._relByKey = Array.from({ length: 128 }, () => []);
    let lo = 127, hi = 0, playable = 0;
    inst.zones.forEach(z => {
      if (z.buffer || z.generator) playable++;
      const a = clamp(z.lokey, 0, 127), b = clamp(z.hikey, 0, 127);
      if (z.lokey < 0 || z.hikey < 0 || z.lokey > z.hikey) return;
      const tbl = z.trigger === 'release' ? this._relByKey : this._byKey;
      for (let k = a; k <= b; k++) tbl[k].push(z);
      if (z.trigger !== 'release' && (z.buffer || z.generator)) { lo = Math.min(lo, z.lokey); hi = Math.max(hi, z.hikey); }
    });
    this._range = playable ? [lo, hi] : null;
    this._emit('load', this.info());
    this._emit('change', { path: 'instrument' });
  }
  info() {
    const inst = this.inst;
    if (!inst) return { id: this.state.instrument, name: '', format: '', zones: 0, playable: 0, failed: 0, keyLo: null, keyHi: null, seconds: 0, bytes: 0, unsupported: [] };
    const bufs = new Set();
    let playable = 0, failed = 0;
    for (const z of inst.zones) { if (z.buffer) { bufs.add(z.buffer); playable++; } else if (z.generator) playable++; else failed++; }
    let seconds = 0, mem = 0;
    for (const b of bufs) { seconds += b.duration; mem += b.length * b.numberOfChannels * 4; }
    return { id: this.state.instrument, name: inst.name, format: inst.format, zones: inst.zones.length, playable, failed,
      keyLo: this._range ? this._range[0] : null, keyHi: this._range ? this._range[1] : null,
      seconds, memoryBytes: mem, bytes: inst.loadStats ? inst.loadStats.bytes : (inst.sampleBytes || 0),
      buffers: bufs.size, unsupported: inst.unsupported || [], warnings: inst.warnings || [], keyswitch: inst.keyswitch || null };
  }

  // ── state ───────────────────────────────────────────────────────
  getState() { return Object.assign({}, this.state); }
  setState(json) {
    let s = json;
    if (typeof s === 'string') { try { s = JSON.parse(s); } catch (e) { return false; } }
    if (!s || typeof s !== 'object') return false;
    const prevId = this.state.instrument;
    const merged = normalizeState(Object.assign({}, this.state, s));
    this.state = merged;
    this._applyState(null);
    if (s.instrument !== undefined && merged.instrument !== prevId && merged.instrument && this._resolve) {
      const id = merged.instrument;
      Promise.resolve().then(() => this._resolve(id)).then(inst => inst && this.load(inst, { id })).catch(e => console.warn('sampler: could not load', id, e));
    }
    this._emit('change', { path: '*' });
    return true;
  }
  set(key, value) { return this.setState({ [key]: value }); }
  _applyState(t) {
    const s = this.state, now = this.ctx.currentTime;
    const at = (p, v) => { if (t == null) { p.cancelScheduledValues(0); p.value = v; } else p.setTargetAtTime(v, t, 0.01); };
    at(this._vol.gain, dbToGain(s.gain) * this._cc7);
    at(this._filter.frequency, clamp(s.cutoff, 20, this.ctx.sampleRate / 2 - 100));
    at(this._filter.Q, s.resonance - 3);
    this._applyMw(now);
    this._bendSrc.offset.setTargetAtTime(this._bend * s.bendRange * 100, now, 0.004);
  }
  _applyMw(t) {
    const mw = this._mw, mode = this.state.mw;
    this._vibAmt.gain.setTargetAtTime(mode === 'vibrato' ? mw * 40 : 0, t, 0.01);
    this._filter.detune.setTargetAtTime(mode === 'filter' ? -mw * 4800 : 0, t, 0.01);
  }

  // ── playing ─────────────────────────────────────────────────────
  _t(when) { const now = this.ctx.currentTime; return (when == null || !isFinite(when)) ? now : Math.max(now, when); }
  get activeVoices() { const t = this.ctx.currentTime; let n = 0; for (const v of this.voices) if (v.end > t && !(v.killT <= t)) n++; return n; }
  _pedalDown(t) { let d = false; for (const p of this._pedal) { if (p.t <= t) d = p.down; else break; } return d; }
  _pedalUpAfter(t) { for (const p of this._pedal) if (p.t > t && !p.down) return p.t; return null; }

  noteOn(note, vel, when, ch) {
    try {
      if (this._disposed) return;
      note = clamp(Math.round(+note || 0), 0, 127);
      vel = isNum(vel) ? clamp(vel, 0, 1) : 0.8;
      if (vel <= 0) { this.noteOff(note, when, ch); return; }
      const t = this._t(when);
      ch = isNum(ch) ? ch : 1;
      this._prune();
      const inst = this.inst;
      if (inst && inst.keyswitch && note >= inst.keyswitch.lo && note <= inst.keyswitch.hi) this._sw = note;
      const key = clamp(note + this.state.transpose, 0, 127);
      const v127 = Math.max(1, Math.round(vel * 127));
      const ev = { id: ++this._evId, note, ch, key, vel, v127, tOn: t, offAt: null, released: false, voices: [] };
      let held = 0;
      for (const e of this.events) if (e.tOn <= t && (e.offAt == null || e.offAt > t)) held++;
      if (inst && this._byKey) {
        const rnd = Math.random();
        for (const z of this._byKey[key]) {
          if (z.trigger === 'first' && held) continue;
          if (z.trigger === 'legato' && !held) continue;
          if (!this._match(z, key, v127, ch, rnd)) continue;
          this._startZone(ev, z, t, 0);
        }
      }
      this.events.push(ev);
      // an off that arrived before this on
      let pi = -1;
      for (let i = 0; i < this._pendingOff.length; i++) {
        const p = this._pendingOff[i];
        if (p.note === note && p.ch === ch && p.t >= t && (pi < 0 || p.t < this._pendingOff[pi].t)) pi = i;
      }
      if (pi >= 0) { const p = this._pendingOff.splice(pi, 1)[0]; this._offEvent(ev, p.t); }
      this._emit('note', { note, vel, on: true, t });
    } catch (e) { console.warn('sampler noteOn', e); }
  }
  noteOff(note, when, ch) {
    try {
      if (this._disposed) return;
      note = clamp(Math.round(+note || 0), 0, 127);
      ch = isNum(ch) ? ch : 1;
      const t = this._t(when);
      let ev = null;
      for (const e of this.events) if (e.note === note && e.ch === ch && e.offAt == null && e.tOn <= t && (!ev || e.tOn < ev.tOn)) ev = e;
      if (!ev) { this._pendingOff.push({ note, ch, t }); return; }
      this._offEvent(ev, t);
      this._emit('note', { note, on: false, t });
    } catch (e) { console.warn('sampler noteOff', e); }
  }
  _offEvent(ev, t) {
    ev.offAt = t;
    if (this._pedalDown(t)) {
      const up = this._pedalUpAfter(t);
      if (up == null) { ev.pedal = true; return; }
      t = up;
    }
    this._releaseEvent(ev, t);
  }
  _releaseEvent(ev, t) {
    if (ev.released) return;
    ev.released = true; ev.relT = t;
    for (const v of ev.voices) this._releaseVoice(v, t, false);
    // release-trigger zones
    if (this.inst && this._relByKey) {
      const rnd = Math.random();
      for (const z of this._relByKey[ev.key]) {
        if (!this._match(z, ev.key, ev.v127, ev.ch, rnd)) continue;
        const rel = { id: ++this._evId, note: ev.note, ch: ev.ch, key: ev.key, vel: ev.vel, v127: ev.v127, tOn: t, offAt: t, released: true, voices: [], isRelease: true };
        this._startZone(rel, z, t, -(z.rtDecay || 0) * Math.max(0, t - ev.tOn));
      }
    }
  }
  allOff(when) {
    try {
      const t = this._t(when);
      this._pendingOff = [];
      this._pedal = [{ t: -1, down: false }];
      for (const ev of this.events) { if (ev.offAt == null) ev.offAt = t; if (!ev.released) this._releaseEvent(ev, Math.max(t, ev.tOn)); }
      this._emit('note', { all: true, on: false, t });
    } catch (e) { console.warn('sampler allOff', e); }
  }
  panic() {
    const t = this.ctx.currentTime;
    this._pendingOff = [];
    this._pedal = [{ t: -1, down: false }];
    for (const v of this.voices) this._killVoice(v, t, 0.005);
    for (const ev of this.events) { ev.released = true; if (ev.offAt == null) ev.offAt = t; }
    this.events = [];
  }
  cc(num, v01, when) {
    try {
      num = num | 0;
      const v = clamp(isNum(v01) ? v01 : 0, 0, 1), t = this._t(when);
      if (num >= 0 && num < 128) this._ccv[num] = v * 127;
      if (num === 1) { this._mw = v; this._applyMw(t); }
      else if (num === 7) { this._cc7 = v * v; this._vol.gain.setTargetAtTime(dbToGain(this.state.gain) * this._cc7, t, 0.01); }
      else if (num === 10) this._pan.pan.setTargetAtTime(v * 2 - 1, t, 0.01);
      else if (num === 64) this._sustain(v >= 0.5, t);
      else if (num === 120) { for (const vv of this.voices) if (vv.start <= t) this._killVoice(vv, t, 0.005); }
      else if (num === 121) { this._mw = 0; this._applyMw(t); }
      else if (num === 123) this.allOff(when);
      this._emit('cc', { num, value: v, t });
    } catch (e) { console.warn('sampler cc', e); }
  }
  pitchBend(v, when) {
    try {
      this._bend = clamp(isNum(v) ? v : 0, -1, 1);
      this._bendSrc.offset.setTargetAtTime(this._bend * this.state.bendRange * 100, this._t(when), 0.003);
    } catch (e) { /* ignore */ }
  }
  _sustain(down, t) {
    // keep the pedal log in time order (a DAW may deliver events ahead of time)
    this._pedal.push({ t, down });
    this._pedal.sort((a, b) => a.t - b.t);
    const now = this.ctx.currentTime;
    while (this._pedal.length > 2 && this._pedal[1].t < now - 1) this._pedal.shift();
    if (!down) {
      for (const ev of this.events) {
        if (ev.pedal && !ev.released && ev.offAt != null && ev.offAt <= t && !this._pedalDown(t)) { ev.pedal = false; this._releaseEvent(ev, Math.max(t, ev.offAt)); }
      }
    }
  }

  _match(z, key, v127, ch, rnd) {
    if (!(z.buffer || z.generator)) return false;
    if (key < z.lokey || key > z.hikey) return false;
    if (v127 < z.lovel || v127 > z.hivel) return false;
    if (ch < z.lochan || ch > z.hichan) return false;
    if (z.swLast != null && z.swLast !== this._sw) return false;
    for (const c of z.cc) { const cv = this._ccv[c[0]]; if (cv < c[1] || cv > c[2]) return false; }
    if (rnd < z.lorand || (rnd >= z.hirand && z.hirand < 1)) return false;
    if (z.seqLength > 1) {
      const n = this._seq.get(z) || 0;
      this._seq.set(z, n + 1);
      if (n % z.seqLength !== z.seqPosition - 1) return false;
    }
    return true;
  }

  // gather *_onccN modulation (read once at note-on)
  _mods(z) {
    const m = { volume: 0, amplitude: 1, pan: 0, tune: 0, offset: 0, amp_veltrack: 0, cutoff: 0, delay: 0, attack: 0, hold: 0, decay: 0, sustain: 0, release: 0 };
    for (const md of z.mods) {
      const x = clamp(Math.round(this._ccv[md.cc]), 0, 127);
      const y = md.curveData ? md.curveData[x] : x / 127;
      if (md.target === 'amplitude') m.amplitude *= Math.max(0, md.depth / 100 * y);
      else m[md.target] += md.depth * y;
    }
    return m;
  }
  _velGain(z, v127, extraVt) {
    const c = z.velCurve ? z.velCurve[v127] : (v127 / 127) * (v127 / 127);
    const cs = Math.pow(Math.max(0, c), this.state.velSens);
    const vt = clamp(z.ampVeltrack + extraVt, -1, 1);
    return vt >= 0 ? 1 - vt * (1 - cs) : 1 + vt * cs;
  }

  _startZone(ev, z, t, extraDb) {
    const M = z.mods.length ? this._mods(z) : null;
    // chokes: this voice silences earlier voices whose off_by is our group
    if (z.group) {
      this._choke(z.group, t, ev);
      this._chokeLog.push({ group: z.group, t, ev });
      if (this._chokeLog.length > 512) { const now = this.ctx.currentTime; this._chokeLog = this._chokeLog.filter(c => c.t > now - 0.5).slice(-256); }
    }
    // note_polyphony
    if (z.notePolyphony > 0) {
      const same = this.voices.filter(v => v.ev !== ev && v.key === ev.key && v.z.group === z.group && v.z.trigger === z.trigger && v.start <= t && v.end > t && !(v.killT <= t));
      same.sort((a, b) => a.start - b.start);
      for (let i = 0; i <= same.length - z.notePolyphony; i++) this._offVoice(same[i], t);
    }
    if (z.generator === 'silence') return null;
    const buf = z.generator ? generatorBuffer(this.ctx, z.generator) : z.buffer;
    if (!buf) return null;
    // voice limit: steal the oldest released voice, else the oldest
    let alive = 0;
    for (const v of this.voices) if (v.end > t && !(v.killT <= t)) alive++;
    while (alive >= this.maxVoices) {
      let pick = null;
      for (const v of this.voices) {
        if (!(v.end > t) || v.killT <= t || v.start > t) continue;
        const r = v.relT != null && v.relT <= t;
        if (!pick) { pick = v; continue; }
        const pr = pick.relT != null && pick.relT <= t;
        if (r !== pr) { if (r) pick = v; continue; }
        if (v.start < pick.start) pick = v;
      }
      if (!pick) break;
      this._killVoice(pick, t, 0.005);
      alive--;
    }
    const ctx = this.ctx, S = this.state;
    const key = z.fixedKey >= 0 ? z.fixedKey : ev.key;
    const v127 = z.fixedVel >= 1 ? z.fixedVel : ev.v127;
    if (z.sf2 && z.sf2.mods.length) {     // SF2 modulators → this voice's own copy of the zone
      const zz = Object.create(z);
      const frames = z.sf2.compressed ? Math.round(buf.duration * (z.srcRate || buf.sampleRate)) : buf.length;
      applySf2(zz, z.sf2.g, sf2ModDeltas(z.sf2.mods, key, v127, this._ccv, S.velSens), frames);
      z = zz;
    }
    const sr = z.generator ? buf.sampleRate : (z.srcRate || buf.sampleRate);
    let cents = (key - z.root) * z.keytrack + z.tune + S.tune + z.velPitch * v127 / 127 + (M ? M.tune : 0);
    if (z.generator === 'sine') cents += (z.root - 69) * 100;     // the sine buffer sounds A4 at rate 1
    const rate = Math.pow(2, cents / 1200);
    const src = ctx.createBufferSource();
    src.buffer = buf;
    src.playbackRate.value = rate;
    try { this._pitchBus.connect(src.detune); } catch (e) { /* old browsers */ }
    // loop
    let mode = z.loopMode;
    const hasLoop = z.loopStart != null && z.loopEnd != null && z.loopEnd > z.loopStart + 1;
    if (z.generator) mode = 'loop_continuous';
    else if (mode == null) mode = hasLoop ? 'loop_continuous' : 'no_loop';
    if (ev.isRelease && (mode === 'loop_continuous' || mode === 'loop_sustain')) mode = 'one_shot';
    const looping = mode === 'loop_continuous' || mode === 'loop_sustain';
    if (looping) {
      src.loop = true;
      if (hasLoop && !z.generator) { src.loopStart = z.loopStart / sr; src.loopEnd = Math.min(buf.duration, z.loopEnd / sr); }
      else { src.loopStart = 0; src.loopEnd = buf.duration; }
    }
    let offset = Math.max(0, (z.offset + (M ? M.offset : 0)) / sr);
    if (offset >= buf.duration) offset = 0;
    const endSec = z.end != null ? Math.min(buf.duration, z.end / sr) : buf.duration;
    // gain
    const mono = buf.numberOfChannels === 1;
    let gain = dbToGain(z.gain + (M ? M.volume : 0) + (extraDb || 0)) * (M ? M.amplitude : 1) * this._velGain(z, v127, M ? M.amp_veltrack / 100 : 0);
    const pan = clamp(z.pan + (M ? M.pan / 100 : 0), -1, 1);
    if (mono) gain *= Math.SQRT2;
    if (!(gain > 1e-5)) return null;
    // nodes
    let head = src;
    let filt = null;
    if (z.filter) {
      const F = z.filter;
      filt = ctx.createBiquadFilter();
      filt.type = F.type;
      const fc = F.cutoff * Math.pow(2, ((F.veltrack || 0) * v127 / 127 + (F.keytrack || 0) * (key - (F.keycenter || 60)) + (M ? M.cutoff : 0)) / 1200);
      filt.frequency.value = clamp(fc, 10, ctx.sampleRate / 2 - 100);
      filt.Q.value = (F.type === 'lowpass' || F.type === 'highpass') ? F.q : Math.pow(10, F.q / 20);
      head.connect(filt); head = filt;
    }
    const env = ctx.createGain(), rel = ctx.createGain(), kill = ctx.createGain();
    head.connect(env); env.connect(rel); rel.connect(kill);
    let panner = null;
    if (mono || pan !== 0) { panner = ctx.createStereoPanner(); panner.pan.value = pan; kill.connect(panner); panner.connect(this._in); }
    else kill.connect(this._in);
    // amp envelope
    const E = z.env;
    const keyScale = tcpk => Math.pow(2, (tcpk || 0) * (60 - key) / 1200);
    const delay = Math.max(0, E.delay + (M ? M.delay : 0));
    const attack = Math.max(0, E.attack + (M ? M.attack : 0)) + S.attack;
    const hold = Math.max(0, E.hold + (M ? M.hold : 0)) * keyScale(E.keyHold);
    const decay = Math.max(0, E.decay + (M ? M.decay : 0)) * keyScale(E.keyDecay);
    const sus = clamp(E.sustain + (M ? M.sustain / 100 : 0), 0, 1);
    const g = env.gain;
    const ta = t + delay;
    g.setValueAtTime(delay > 0 ? 0 : (attack < 0.0005 ? gain : 0), t);
    if (attack >= 0.0005) { g.setValueAtTime(0, ta); g.linearRampToValueAtTime(gain, ta + attack); }
    else if (delay > 0) g.setValueAtTime(gain, ta);
    const th = ta + attack + hold;
    let silentAt = Infinity;
    if (sus < 0.9999 && (decay > 0 || sus <= 0)) {
      if (hold > 0) g.setValueAtTime(gain, th);
      if (E.dbDecay) {
        if (sus > 1e-5) g.exponentialRampToValueAtTime(gain * sus, th + Math.max(0.001, decay * (-20 * Math.log10(sus) / 100)));
        else { g.setTargetAtTime(0, th, Math.max(0.0005, decay / 11.5)); silentAt = th + decay; }
      } else if (sus > 0.001) g.exponentialRampToValueAtTime(gain * sus, th + Math.max(0.001, decay));
      else { g.setTargetAtTime(0, th, Math.max(0.0005, decay / 6.9)); silentAt = th + decay * 1.4 + 0.005; }
    }
    // filter envelope
    let fenv = null;
    if (filt && z.filter.env) {
      const FE = z.filter.env, d = filt.detune, fa = t + FE.delay;
      fenv = FE;
      d.setValueAtTime(0, t);
      d.setValueAtTime(0, fa);
      d.linearRampToValueAtTime(FE.depth, fa + Math.max(0.0005, FE.attack));
      if (FE.hold) d.setValueAtTime(FE.depth, fa + FE.attack + FE.hold);
      d.setTargetAtTime(FE.depth * FE.sustain, fa + FE.attack + FE.hold, Math.max(0.001, FE.decay / 5));
    }
    // start
    const naturalDur = looping ? Infinity : Math.max(0, endSec - offset) / Math.max(1e-3, rate * Math.pow(2, -Math.abs(S.bendRange) / 12));
    try {
      if (!looping && z.end != null && endSec < buf.duration) src.start(t, offset, Math.max(0.001, endSec - offset));
      else src.start(t, offset);
    } catch (e) { src.start(t); }
    const relDur = Math.max(0.006, (E.release + (M ? M.release : 0)) * S.release);
    const v = { ev, z, key: ev.key, src, filt, env, rel, kill, panner, start: t, end: Math.min(t + naturalDur, silentAt) + 0.02,
      relT: null, killT: Infinity, stopAt: Infinity, mode, relDur, drop: E.dbDecay ? 100 : 72, fenv, released: false };
    if (isFinite(silentAt)) this._stop(v, silentAt);
    src.onended = () => this._cleanup(v);
    // a later-starting voice already scheduled in our off_by group chokes us
    if (z.offBy) {
      let first = null;
      for (const c of this._chokeLog) if (c.ev !== ev && c.group === z.offBy && c.t > t && (first == null || c.t < first)) first = c.t;
      if (first != null) this._offVoice(v, first);
    }
    this.voices.push(v);
    ev.voices.push(v);
    return v;
  }
  _choke(group, t, ev) {
    for (const v of this.voices) {
      if (v.ev === ev || v.z.offBy !== group || v.start > t || v.end <= t || v.killT <= t) continue;
      this._offVoice(v, t);
    }
  }
  // choke / note_polyphony: by the victim's off_mode
  _offVoice(v, t) {
    const z = v.z;
    if (z.offMode === 'normal') this._releaseVoice(v, t, true);
    else this._killVoice(v, t, z.offMode === 'time' ? Math.max(0.002, z.offTime) : 0.006);
  }
  _releaseVoice(v, t, force) {
    if (v.released || v.killT <= t) return;
    if (v.mode === 'one_shot' && !force) { v.relT = t; return; }
    v.released = true; v.relT = t;
    const t0 = Math.max(t, v.start);
    try { v.rel.gain.setValueCurveAtTime(relCurve(v.drop), t0, v.relDur); }
    catch (e) { try { v.rel.gain.setTargetAtTime(0, t0, v.relDur / 6); } catch (e2) { /* ignore */ } }
    if (v.mode === 'loop_sustain') runAt(this.ctx, t0, () => { try { v.src.loop = false; } catch (e) { /* ok */ } });
    if (v.fenv && v.filt) {
      try {
        const d = v.filt.detune;
        if (d.cancelAndHoldAtTime) d.cancelAndHoldAtTime(t0); else d.cancelScheduledValues(t0);
        d.setTargetAtTime(0, t0, Math.max(0.001, v.fenv.release / 5));
      } catch (e) { /* ignore */ }
    }
    const endT = t0 + v.relDur;
    v.end = Math.min(v.end, endT + 0.01);
    this._stop(v, endT);
  }
  _killVoice(v, t, fade) {
    if (v.killT <= t) return;
    const g = v.kill.gain;
    try {
      if (v.killT !== Infinity) g.cancelScheduledValues(0);
      const t0 = Math.max(t, v.start);
      g.setValueAtTime(1, t0);
      g.linearRampToValueAtTime(0, t0 + fade);
      v.killT = t0;
      v.end = Math.min(v.end, t0 + fade + 0.01);
      this._stop(v, t0 + fade);
    } catch (e) { /* ignore */ }
  }
  _stop(v, t) {
    if (!(t < v.stopAt)) return;
    v.stopAt = t;
    try { v.src.stop(t + 0.003); } catch (e) { /* ignore */ }
  }
  _cleanup(v) {
    if (v.cleaned) return;
    v.cleaned = true;
    try { this._pitchBus.disconnect(v.src.detune); } catch (e) { /* ok */ }
    for (const n of [v.src, v.filt, v.env, v.rel, v.kill, v.panner]) if (n) { try { n.disconnect(); } catch (e) { /* ok */ } }
    const i = this.voices.indexOf(v); if (i >= 0) this.voices.splice(i, 1);
    const j = v.ev.voices.indexOf(v); if (j >= 0) v.ev.voices.splice(j, 1);
  }
  _prune() {
    const now = this.ctx.currentTime;
    if (this.voices.length > this.maxVoices * 3) for (const v of this.voices.slice()) if (v.end < now - 0.5) this._cleanup(v);
    if (this.events.length > 64) {
      this.events = this.events.filter(e => !(e.released && e.voices.length === 0 && (e.relT == null || e.relT < now)));
      if (this.events.length > 4096) this.events = this.events.slice(-4096);
    }
    if (this._pendingOff.length) this._pendingOff = this._pendingOff.filter(p => p.t > now - 2);
  }

  // ── editor ──────────────────────────────────────────────────────
  mountEditor(el, opts) { return mountSamplerEditor(this, el, opts || {}); }
}
SampleInstrument.defaultState = () => Object.assign({}, DEFAULT_STATE);
SampleInstrument.normalizeState = normalizeState;

// ═══════════════════════════════════════════════════════════════════
// Editor — compact, finger-friendly panel (range inputs: touch_controls.js
// turns them into press-and-slide controls on a touchscreen)
// ═══════════════════════════════════════════════════════════════════
const EDITOR_CSS = `
.sm-root { --sm-bg0:#050304; --sm-bg1:#0e0908; --sm-ink:#1a1410; --sm-rule:#553318; --sm-gold:#d8a060; --sm-hi:#ffd896;
  --sm-text:#c8a878; --sm-dim:#7a5828; --sm-rust:#c87633; --sm-red:#c64a3a; --sm-em:#a8e89c;
  font-family:"Courier New",monospace; color:var(--sm-text); background:var(--sm-bg0); font-size:11px; box-sizing:border-box; padding:6px 8px; }
.sm-root * { box-sizing:border-box; }
.sm-head { display:flex; gap:8px; align-items:baseline; flex-wrap:wrap; border-bottom:1px solid var(--sm-rule); padding-bottom:4px; }
.sm-head b { color:var(--sm-hi); letter-spacing:.14em; font-weight:normal; }
.sm-name { color:var(--sm-gold); max-width:46ch; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.sm-info { color:var(--sm-dim); font-size:10px; }
.sm-info.bad { color:var(--sm-red); }
.sm-map { width:100%; height:44px; display:block; margin:5px 0 4px; border:1px solid var(--sm-rule); background:#0a0605; }
.sm-grid { display:grid; grid-template-columns:repeat(auto-fill, minmax(250px, 1fr)); gap:3px 12px; }
.sm-ctl { display:grid; grid-template-columns:62px minmax(0,1fr) 52px; align-items:center; gap:4px; min-height:30px; }
.sm-ctl span { color:var(--sm-dim); font-size:10px; letter-spacing:.08em; }
.sm-ctl output { color:var(--sm-hi); font-size:10px; text-align:right; white-space:nowrap; }
.sm-ctl input[type=range] { width:100%; margin:0; accent-color:var(--sm-rust); height:26px; touch-action:none; }
.sm-ctl2 { grid-template-columns:70px minmax(0,1fr); }
.sm-ctl select { background:var(--sm-ink); color:var(--sm-hi); border:1px solid var(--sm-rule); font-family:inherit; font-size:11px; padding:4px; min-height:28px; }
.sm-uns { color:var(--sm-dim); font-size:10px; font-style:italic; margin-top:4px; line-height:1.4; max-height:3.2em; overflow:hidden; cursor:pointer; }
.sm-uns.open { max-height:none; }
`;
let editorCssAdded = false;
function mountSamplerEditor(s, el, opts) {
  if (!editorCssAdded && typeof document !== 'undefined') {
    const st = document.createElement('style'); st.textContent = EDITOR_CSS; document.head.appendChild(st); editorCssAdded = true;
  }
  const rootEl = document.createElement('div');
  rootEl.className = 'sm-root';
  const head = document.createElement('div'); head.className = 'sm-head';
  head.innerHTML = '<b>SAMPLER</b><span class="sm-name"></span><span class="sm-info"></span><span class="sm-info sm-voices" style="margin-left:auto"></span>';
  const map = document.createElement('canvas'); map.className = 'sm-map';
  if (opts.mapHeight) map.style.height = opts.mapHeight + 'px';
  const grid = document.createElement('div'); grid.className = 'sm-grid';
  const uns = document.createElement('div'); uns.className = 'sm-uns';
  uns.addEventListener('click', () => uns.classList.toggle('open'));
  rootEl.append(head, map, grid, uns);
  // log mapping for cutoff (slider 0..1000)
  const cutToPos = hz => Math.round(1000 * Math.log(hz / 20) / Math.log(1000));
  const posToCut = p => Math.round(20 * Math.pow(1000, p / 1000));
  const CTLS = [
    { k: 'gain', label: 'GAIN', min: -48, max: 12, step: 0.5, fmt: v => (v > 0 ? '+' : '') + v.toFixed(1) + ' dB' },
    { k: 'transpose', label: 'TRANSP', min: -36, max: 36, step: 1, fmt: v => (v > 0 ? '+' : '') + v + ' st' },
    { k: 'tune', label: 'TUNE', min: -100, max: 100, step: 1, fmt: v => (v > 0 ? '+' : '') + v + ' ct' },
    { k: 'attack', label: 'ATTACK +', min: 0, max: 4, step: 0.005, fmt: v => v < 1 ? Math.round(v * 1000) + ' ms' : v.toFixed(2) + ' s' },
    { k: 'release', label: 'RELEASE ×', min: 0.05, max: 8, step: 0.05, fmt: v => '×' + v.toFixed(2) },
    { k: 'cutoff', label: 'CUTOFF', min: 0, max: 1000, step: 1, to: cutToPos, from: posToCut, fmt: v => v >= 19990 ? 'open' : v >= 1000 ? (v / 1000).toFixed(1) + ' k' : v + ' Hz' },
    { k: 'resonance', label: 'RESO', min: 0, max: 24, step: 0.5, fmt: v => v.toFixed(1) + ' dB' },
    { k: 'velSens', label: 'VEL SENS', min: 0, max: 2, step: 0.05, fmt: v => v.toFixed(2) },
    { k: 'bendRange', label: 'BEND', min: 0, max: 24, step: 1, fmt: v => '±' + v + ' st' },
  ];
  const rows = {};
  for (const c of CTLS) {
    const row = document.createElement('label'); row.className = 'sm-ctl';
    const sp = document.createElement('span'); sp.textContent = c.label;
    const inp = document.createElement('input'); inp.type = 'range'; inp.min = c.min; inp.max = c.max; inp.step = c.step;
    const def = DEFAULT_STATE[c.k];
    inp.dataset.default = c.to ? c.to(def) : def;
    const out = document.createElement('output');
    inp.addEventListener('input', () => { const v = c.from ? c.from(+inp.value) : +inp.value; s.setState({ [c.k]: v }); });
    row.append(sp, inp, out);
    grid.appendChild(row);
    rows[c.k] = { c, inp, out };
  }
  const mwRow = document.createElement('label'); mwRow.className = 'sm-ctl sm-ctl2';
  mwRow.innerHTML = '<span>MOD WHEEL</span>';
  const mwSel = document.createElement('select');
  ['vibrato', 'filter', 'off'].forEach(m => { const o = document.createElement('option'); o.value = m; o.textContent = m; mwSel.appendChild(o); });
  mwSel.addEventListener('change', () => s.setState({ mw: mwSel.value }));
  mwRow.append(mwSel);
  grid.appendChild(mwRow);

  const sync = () => {
    const st = s.state;
    for (const k in rows) {
      const { c, inp, out } = rows[k];
      const pos = c.to ? c.to(st[k]) : st[k];
      if (document.activeElement !== inp || String(+inp.value) !== String(pos)) inp.value = pos;
      out.textContent = c.fmt(st[k]);
    }
    mwSel.value = st.mw;
  };
  // key × velocity map: every playable zone is a translucent box (x = keys, y = velocity,
  // loud at the top), root keys ticked along the bottom, keyswitch keys in green, and
  // the notes sounding right now lit (refreshed with the voice counter).
  const drawMap = () => {
    const inf = s.info(), w = map.clientWidth || 600, h = map.clientHeight || 22, dpr = (typeof devicePixelRatio !== 'undefined' ? devicePixelRatio : 1) || 1;
    if (map.width !== Math.round(w * dpr) || map.height !== Math.round(h * dpr)) { map.width = Math.round(w * dpr); map.height = Math.round(h * dpr); }
    const g = map.getContext('2d'); if (!g) return;
    g.setTransform(dpr, 0, 0, dpr, 0, 0);
    g.fillStyle = '#0a0605'; g.fillRect(0, 0, w, h);
    const lo = 12, hi = 120, kw = w / (hi - lo + 1), top = 9, bot = h - 4, vh = Math.max(4, bot - top);
    for (let k = lo; k <= hi; k++) if ([1, 3, 6, 8, 10].includes(k % 12)) { g.fillStyle = 'rgba(255,255,255,.03)'; g.fillRect((k - lo) * kw, top, kw, vh); }
    const roots = new Set();
    if (s.inst) {
      const tall = vh > 30;
      for (const z of s.inst.zones) {
        if (!(z.buffer || z.generator) || z.trigger === 'release' || z.lokey < 0 || z.hikey < lo || z.lokey > hi) continue;
        const a = Math.max(lo, z.lokey), b = Math.min(hi, z.hikey);
        const y0 = tall ? top + vh * (1 - (z.hivel + 1) / 128) : top, y1 = tall ? top + vh * (1 - z.lovel / 128) : bot;
        g.fillStyle = 'rgba(216,160,96,.16)'; g.fillRect((a - lo) * kw, y0, (b - a + 1) * kw, y1 - y0);
        if (tall) { g.strokeStyle = 'rgba(216,160,96,.35)'; g.lineWidth = 0.5; g.strokeRect((a - lo) * kw + 0.25, y0 + 0.25, (b - a + 1) * kw - 0.5, y1 - y0 - 0.5); }
        roots.add(z.root);
      }
    }
    g.fillStyle = '#ffd896';
    for (const r of roots) if (r >= lo && r <= hi) g.fillRect((r - lo) * kw + kw * 0.25, bot + 1, Math.max(1, kw * 0.5), 3);
    const sounding = new Set();
    const now = s.ctx.currentTime;
    for (const v of s.voices) if (v.start <= now && v.end > now && !(v.killT <= now) && v.relT == null) sounding.add(v.key);
    g.fillStyle = 'rgba(255,216,150,.85)';
    for (const k of sounding) if (k >= lo && k <= hi) g.fillRect((k - lo) * kw, top, Math.max(1, kw - 0.5), 3);
    g.font = '8px Courier New';
    for (let k = lo; k <= hi; k += 12) { g.fillStyle = '#7a5828'; g.fillText('C' + (k / 12 - 1), (k - lo) * kw + 1, 7); }
    const ks = inf.keyswitch;
    if (ks) { g.fillStyle = '#a8e89c'; for (let k = Math.max(lo, ks.lo); k <= Math.min(hi, ks.hi); k++) g.fillRect((k - lo) * kw, top, kw - 0.5, vh); }
    map._sig = sounding.size + ':' + [...sounding].join(',');
  };
  const refreshInfo = () => {
    const inf = s.info(), name = head.querySelector('.sm-name'), info = head.querySelector('.sm-info');
    name.textContent = inf.name || '— no instrument —';
    if (s.inst) {
      const range = inf.keyLo != null ? midiToNoteName(inf.keyLo) + '–' + midiToNoteName(inf.keyHi) : 'no playable keys';
      info.textContent = `${inf.format} · ${inf.zones} zones · ${range} · ${inf.seconds.toFixed(1)} s audio` + (inf.failed ? ` · ${inf.failed} missing` : '');
      info.classList.toggle('bad', !!inf.failed);
      const u = (inf.unsupported || []);
      uns.textContent = u.length ? 'ignored: ' + u.join(', ') : '';
    } else { info.textContent = ''; uns.textContent = ''; }
    drawMap();
  };
  const offChange = s.on('change', e => { sync(); if (e && e.path === 'instrument') refreshInfo(); });
  const offLoad = s.on('load', refreshInfo);
  const offProg = s.on('progress', p => { head.querySelector('.sm-info').textContent = `loading ${p.done}/${p.total} · ${(p.bytes / 1048576).toFixed(1)} MB`; });
  const vEl = head.querySelector('.sm-voices');
  let lastSig = '';
  const timer = setInterval(() => {
    vEl.textContent = 'voices ' + s.activeVoices + '/' + s.maxVoices;
    const now = s.ctx.currentTime, sig = s.voices.filter(v => v.start <= now && v.end > now && v.relT == null).map(v => v.key).join(',');
    if (sig !== lastSig) { lastSig = sig; drawMap(); }
  }, 120);
  let ro = null;
  if (typeof ResizeObserver !== 'undefined') { ro = new ResizeObserver(() => drawMap()); ro.observe(map); }
  el.appendChild(rootEl);
  sync(); refreshInfo();
  const ed = {
    element: rootEl,
    destroy() { clearInterval(timer); offChange(); offLoad(); offProg(); if (ro) ro.disconnect(); rootEl.remove(); s._editors.delete(ed); },
  };
  s._editors.add(ed);
  return ed;
}

const SampleFormats = {
  parseSFZ, parseSF2, parseMidiJsSoundfont, instrumentFromFiles, decodeAll, decodeBytes, thinLayers, autoOctave, detectPitch, respread,
  noteNameToMidi, midiToNoteName, parseWav, parseSampleName, resolveUrl, dirOf, sniffRate, makeZone,
  dataUrlToBytes, defaultFetchBytes,
};
root.SampleFormats = SampleFormats;
root.SampleInstrument = SampleInstrument;
})(typeof window !== 'undefined' ? window : globalThis);
