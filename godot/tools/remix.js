/*
 * remix.js — REMIX: new takes for a catalog track made out of FINISHED music (an approved take, any take, a real
 * recording, an approved temp). Used by the AUDIO DIRECTOR (audio_director.html); the takes land in review staging
 * exactly like MAKE TAKES' (temp_maker.js writes them), so PLAY / APPROVE / ⟳ AGAIN / ✎ EDIT IN DAW all work.
 *
 * Two kinds of recipe:
 *   NOTES (a take: its project.json / meta carry the song's options) — the source's plan is rebuilt (SeqGen.plan) and
 *     grafted onto a new song: its harmony (progressions + harmonic rhythm), its sections and its motif, under another
 *     style's grooves, figures, instruments and tempo. RESTYLE · COVER (the source's literal lead) · VARIATIONS (the
 *     motif developed: inverted / reversed / stretched / displaced) · UNDERSCORE (quiet, no drums) · INTENSE · DREAM ·
 *     BLEND (harmony + sections of one source, the motif of another).
 *   AUDIO (anything that plays: a take's stems minus its drums, an approved temp's Ogg stems, a real recording) —
 *     analysed (tempo, beat phase, key, per-bar root; a take's own metadata wins over the guess), cut / processed into
 *     one audio layer ('source' stem, layer 0) and given new drums + a root-following bass in its key and tempo:
 *     CHOP (beat-sliced, re-sequenced, stutters + reversed slices) · DUB (drop-outs, filter sweeps, echo throws) ·
 *     STRETCH (paulstretch 3–10× into an ambient bed, a sparse new theme on top) · TAPE (two semitones down, wow +
 *     flutter, filtered and saturated, a lo-fi beat).
 *   The audio layer is a take-library item (AK.lib kind 'remix', mirrored to assets/audio/library/remix/) on an
 *   audio track, so the DAW opens the remix with it.
 * Every choice comes from the take's seed (SeqGen.rng): the same seed + source + recipe → the same remix (⟳ AGAIN).
 * Pure helpers (analysis, DSP, the notes plan) are exported for node tests.
 */
(function (root) {
  'use strict';
  const SG = () => root.SeqGen, TM = () => root.TempMaker, AKg = () => (typeof AK !== 'undefined' ? AK : root.AK);
  const RATE = 48000;
  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));

  const RECIPES = {
    restyle:    { kind: 'notes', name: 'RESTYLE',    hint: 'the same tune and chords in another style, with a new band' },
    cover:      { kind: 'notes', name: 'COVER',      hint: 'the exact melody, new accompaniment in another style' },
    variations: { kind: 'notes', name: 'VARIATIONS', hint: 'the theme developed (inverted, reversed, stretched, displaced), a new middle section' },
    underscore: { kind: 'notes', name: 'UNDERSCORE', hint: 'a quiet version to talk over: no drums, sparse theme' },
    intense:    { kind: 'notes', name: 'INTENSE',    hint: 'the action version: faster, driving drums, risers' },
    dream:      { kind: 'notes', name: 'DREAM',      hint: 'the theme slowed into haze: twice as slow, no drums' },
    blend:      { kind: 'notes', name: 'BLEND',      hint: 'this source’s chords + sections with the WITH source’s theme', needsWith: true },
    chop:       { kind: 'audio', name: 'CHOP',       hint: 'the recording sliced on the beat and re-sequenced, new drums + bass under it' },
    dub:        { kind: 'audio', name: 'DUB',        hint: 'drops in and out with echo throws and filter sweeps, dub drums + bass' },
    stretch:    { kind: 'audio', name: 'STRETCH',    hint: 'stretched 3–10× into an ambient bed, a sparse new theme on top' },
    tape:       { kind: 'audio', name: 'TAPE',       hint: 'a worn tape memory: two semitones down, wobbling, filtered, a lo-fi beat' },
  };
  // styles that sit near each other (RESTYLE / COVER pick from here when no style is asked)
  const NEAR = {
    noir: ['jazz', 'trip_hop', 'lofi', 'chamber', 'piano', 'dub'], jazz: ['noir', 'lofi', 'boom_bap', 'bayou', 'piano', 'shuffle'],
    trip_hop: ['noir', 'dub', 'lofi', 'boom_bap', 'dark_drone', 'chamber'], lofi: ['boom_bap', 'jazz', 'trip_hop', 'piano', 'folk', 'lullaby'],
    boom_bap: ['lofi', 'trip_hop', 'jazz', 'dub', 'trap'], trap: ['boom_bap', 'synth_horror', 'trip_hop', 'industrial', 'dnb'],
    dnb: ['synthwave', 'industrial', 'trap', 'four_floor', 'motorik'], four_floor: ['synthwave', 'motorik', 'dnb', 'minimal', 'chiptune'],
    motorik: ['minimal', 'post_rock', 'synthwave', 'four_floor', 'industrial'], synthwave: ['four_floor', 'synth_horror', 'chiptune', 'motorik', 'post_rock'],
    synth_horror: ['synthwave', 'industrial', 'dark_drone', 'trap'], industrial: ['synth_horror', 'dark_drone', 'motorik', 'dnb', 'trap'],
    ambient: ['dark_drone', 'minimal', 'post_rock', 'hymn', 'piano', 'chamber'], dark_drone: ['ambient', 'synth_horror', 'industrial', 'chamber', 'hymn'],
    chamber: ['piano', 'hymn', 'noir', 'ambient', 'folk', 'lullaby'], piano: ['chamber', 'lullaby', 'lofi', 'jazz', 'ambient', 'hymn'],
    hymn: ['chamber', 'folk', 'ambient', 'piano', 'lullaby'], folk: ['bayou', 'hymn', 'chamber', 'shuffle', 'lullaby', 'lofi'],
    bayou: ['folk', 'shuffle', 'jazz', 'dub', 'surf'], shuffle: ['bayou', 'jazz', 'surf', 'folk', 'boom_bap'], surf: ['shuffle', 'post_rock', 'synthwave', 'chiptune', 'bayou'],
    post_rock: ['ambient', 'motorik', 'minimal', 'chamber', 'surf'], minimal: ['motorik', 'ambient', 'post_rock', 'piano', 'chiptune'],
    lullaby: ['piano', 'chamber', 'hymn', 'folk', 'chiptune'], chiptune: ['synthwave', 'lullaby', 'four_floor', 'minimal', 'surf'], dub: ['trip_hop', 'boom_bap', 'bayou', 'noir', 'jazz'],
  };
  const QUIET = { dark: ['ambient', 'dark_drone', 'chamber', 'piano', 'minimal'], bright: ['ambient', 'piano', 'chamber', 'lullaby', 'hymn', 'minimal'] };
  const DRIVE = { dark: ['dnb', 'industrial', 'synth_horror', 'trap', 'motorik', 'post_rock'], bright: ['surf', 'synthwave', 'four_floor', 'chiptune', 'motorik', 'post_rock', 'dnb'] };
  const HAZE = { dark: ['dark_drone', 'ambient', 'post_rock'], bright: ['ambient', 'post_rock', 'minimal'] };
  // the audio recipes' new band: drums style by mood, and the part of the source that stays (stems they drop)
  const AUDIO_STYLE = { chop: { dark: ['trip_hop', 'boom_bap', 'dnb', 'trap'], bright: ['boom_bap', 'lofi', 'four_floor', 'dnb'] },
    dub: { dark: ['dub'], bright: ['dub'] }, stretch: { dark: ['dark_drone', 'ambient'], bright: ['ambient'] }, tape: { dark: ['lofi', 'boom_bap', 'trip_hop'], bright: ['lofi', 'boom_bap'] } };
  const DROP_STEMS = { chop: /^(drums|perc|fx|hit|texture\d*)$/, dub: /^(drums|perc|fx|hit)$/, stretch: /^(drums|perc|fx|hit)$/, tape: /^(drums|perc|fx|hit)$/ };
  const MINORISH = { minor: 1, dorian: 1, phrygian: 1, harmonic: 1, locrian: 1 };

  // ═══════════════════════════════════════════════════════════════
  // FFT (radix-2, in place; inverse scaled by 1/n) with cached twiddles
  // ═══════════════════════════════════════════════════════════════
  const TW = new Map();
  function fft(re, im, inverse) {
    const n = re.length;
    let tw = TW.get(n);
    if (!tw) { tw = { c: new Float64Array(n / 2), s: new Float64Array(n / 2) }; for (let k = 0; k < n / 2; k++) { tw.c[k] = Math.cos(2 * Math.PI * k / n); tw.s[k] = Math.sin(2 * Math.PI * k / n); } TW.set(n, tw); }
    for (let i = 1, j = 0; i < n; i++) {
      let bit = n >> 1;
      for (; j & bit; bit >>= 1) j ^= bit;
      j ^= bit;
      if (i < j) { let t = re[i]; re[i] = re[j]; re[j] = t; t = im[i]; im[i] = im[j]; im[j] = t; }
    }
    const sg = inverse ? 1 : -1;
    for (let len = 2; len <= n; len <<= 1) {
      const half = len >> 1, step = n / len;
      for (let i = 0; i < n; i += len) {
        for (let k = 0; k < half; k++) {
          const cr = tw.c[k * step], ci = sg * tw.s[k * step], a = i + k, b = a + half;
          const xr = re[b] * cr - im[b] * ci, xi = re[b] * ci + im[b] * cr;
          re[b] = re[a] - xr; im[b] = im[a] - xi; re[a] += xr; im[a] += xi;
        }
      }
    }
    if (inverse) for (let i = 0; i < n; i++) { re[i] /= n; im[i] /= n; }
  }
  const hann = n => { const w = new Float64Array(n); for (let i = 0; i < n; i++) w[i] = 0.5 - 0.5 * Math.cos(2 * Math.PI * i / n); return w; };
  const mono = chs => { if (chs.length === 1) return chs[0]; const m = new Float32Array(chs[0].length); for (const c of chs) for (let i = 0; i < m.length; i++) m[i] += c[i] / chs.length; return m; };

  // ═══════════════════════════════════════════════════════════════
  // analysis: tempo + beat phase, key, the root of each bar
  // ═══════════════════════════════════════════════════════════════
  // spectral-flux onset envelope (hop 512): what a beat tracker listens to
  function onsetEnvelope(x, sr, maxSec = 90) {
    const N = 1024, hop = 512, len = Math.min(x.length, Math.round(maxSec * sr)), frames = Math.max(0, Math.floor((len - N) / hop));
    const env = new Float32Array(frames), w = hann(N), re = new Float64Array(N), im = new Float64Array(N), prev = new Float64Array(N / 2);
    const top = Math.min(N / 2, Math.round(8000 / (sr / N)));
    for (let f = 0; f < frames; f++) {
      const o = f * hop;
      for (let i = 0; i < N; i++) { re[i] = x[o + i] * w[i]; im[i] = 0; }
      fft(re, im, false);
      let flux = 0;
      for (let k = 1; k < top; k++) { const m = Math.log1p(100 * Math.hypot(re[k], im[k])); const d = m - prev[k]; if (d > 0) flux += d; prev[k] = m; }
      env[f] = flux;
    }
    // minus a local mean (half a second), half-wave rectified: the onsets, not the loudness
    const out = new Float32Array(frames), W = Math.round(0.25 * sr / hop);
    let acc = 0; const q = [];
    for (let f = 0; f < frames + W; f++) {
      if (f < frames) { acc += env[f]; q.push(env[f]); }
      if (q.length > 2 * W + 1) acc -= q.shift();
      const c = f - W; if (c >= 0 && c < frames) out[c] = Math.max(0, env[c] - acc / q.length);
    }
    return { env: out, fps: sr / hop, hop };
  }
  // → { bpm, phase (s: the first downbeat), confidence 0..1 }
  function estimateTempo(x, sr) {
    const { env, fps } = onsetEnvelope(x, sr), n = env.length;
    if (n < fps * 4) return { bpm: 0, phase: 0, confidence: 0 };
    const lagLo = Math.floor(fps * 60 / 180), lagHi = Math.ceil(fps * 60 / 60), ac = new Float64Array(lagHi + 2);
    let e0 = 0; for (let i = 0; i < n; i++) e0 += env[i] * env[i];
    if (e0 <= 1e-9) return { bpm: 0, phase: 0, confidence: 0 };
    for (let lag = lagLo; lag <= lagHi + 1; lag++) { let s = 0; for (let i = 0; i + lag < n; i++) s += env[i] * env[i + lag]; ac[lag] = s / (n - lag) * n / e0; }
    let best = lagLo, bestS = -1, sum = 0, cnt = 0;
    for (let lag = lagLo; lag <= lagHi; lag++) {
      const bpm = 60 * fps / lag, prior = Math.exp(-0.5 * Math.pow(Math.log2(bpm / 110) / 0.7, 2));
      // the beat's own peak backed by its double (the half-time pulse) — keeps the tracker off an off-beat lag
      const s = (ac[lag] + 0.5 * (2 * lag <= lagHi + 1 ? ac[2 * lag] || 0 : 0)) * prior;
      sum += ac[lag]; cnt++;
      if (s > bestS) { bestS = s; best = lag; }
    }
    // parabolic refinement of the peak
    const a = ac[best - 1] || ac[best], b = ac[best], c = ac[best + 1] || ac[best], den = a - 2 * b + c;
    const lag = best + (den ? clamp(0.5 * (a - c) / den, -0.5, 0.5) : 0), bpm = 60 * fps / lag;
    const mean = sum / Math.max(1, cnt), confidence = clamp((ac[best] - mean) / Math.max(1e-6, ac[best]), 0, 1);
    // tempo + phase together on a fine grid: a 0.3 % tempo error drifts the grid ~0.1 s over a minute
    const at = (t) => { const i = t * fps, j = Math.floor(i), f = i - j; return j + 1 < n ? env[j] * (1 - f) + env[j + 1] * f : 0; };
    const gridScore = (bp, ph) => { const bs = 60 / bp; let s = 0; for (let t = ph; t * fps < n - 1; t += bs) s += at(t); return s; };
    let fb = bpm, fp = 0, fs = -1;
    for (let k = -30; k <= 30; k++) {
      const bp = bpm * (1 + k * 0.0005), bs = 60 / bp;
      for (let ph = 0; ph < bs; ph += 1 / fps / 2) { const sc = gridScore(bp, ph); if (sc > fs) { fs = sc; fb = bp; fp = ph; } }
    }
    return { bpm: +fb.toFixed(3), phase: fp, beat: 60 / fb, confidence: +confidence.toFixed(3) };
  }
  // which of the four beats starts the bar: where the harmony changes (beat-synchronous chroma novelty), helped by
  // the low end (a kick on the one)
  function downbeat(x, sr, bpm, phase) {
    const beat = 60 / bpm, nb = Math.min(256, Math.floor((x.length / sr - phase) / beat)), score = [0, 0, 0, 0];
    if (nb < 8) return phase;
    let prev = null;
    for (let i = 0; i < nb; i++) {
      const a = Math.round((phase + i * beat) * sr), ch = chroma(x, sr, a, Math.min(x.length, a + Math.round(beat * sr)));
      if (prev) {
        let d = 0, na = 0, nb2 = 0; for (let k = 0; k < 12; k++) { d += ch[k] * prev[k]; na += ch[k] * ch[k]; nb2 += prev[k] * prev[k]; }
        score[i % 4] += 1 - (na && nb2 ? d / Math.sqrt(na * nb2) : 1);
      }
      prev = ch;
    }
    const k = score.indexOf(Math.max(...score));
    return phase + k * beat;
  }
  // pitch-class profile of x[a, b) (8192-point frames, 55 Hz – 2 kHz)
  function chroma(x, sr, a = 0, b = x.length) {
    const N = 8192, ch = new Float64Array(12), w = hann(N), re = new Float64Array(N), im = new Float64Array(N);
    const lo = Math.ceil(55 / (sr / N)), hi = Math.min(N / 2 - 1, Math.floor(2000 / (sr / N)));
    for (let o = a; o + N <= b || (o === a && b - a > N / 4); o += N) {
      for (let i = 0; i < N; i++) { const v = x[o + i]; re[i] = (v === undefined ? 0 : v) * w[i]; im[i] = 0; }
      fft(re, im, false);
      for (let k = lo; k <= hi; k++) {
        const f = k * sr / N, pc = ((Math.round(12 * Math.log2(f / 440)) + 9) % 12 + 12) % 12;
        ch[pc] += Math.hypot(re[k], im[k]);
      }
      if (o + N > b) break;
    }
    return ch;
  }
  const KK_MAJ = [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88], KK_MIN = [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17];
  function corr(a, b) {
    const n = a.length, ma = a.reduce((s, v) => s + v, 0) / n, mb = b.reduce((s, v) => s + v, 0) / n;
    let x = 0, ya = 0, yb = 0; for (let i = 0; i < n; i++) { x += (a[i] - ma) * (b[i] - mb); ya += (a[i] - ma) ** 2; yb += (b[i] - mb) ** 2; }
    return ya && yb ? x / Math.sqrt(ya * yb) : 0;
  }
  // Krumhansl–Kessler key finding → { key (0 = C), mode: 'major' | 'minor', score }
  function estimateKey(x, sr, maxSec = 90) {
    const ch = chroma(x, sr, 0, Math.min(x.length, Math.round(maxSec * sr)));
    let best = { key: 0, mode: 'minor', score: -2 };
    for (let k = 0; k < 12; k++) for (const [mode, prof] of [['major', KK_MAJ], ['minor', KK_MIN]]) {
      const rot = Array.from({ length: 12 }, (_, i) => prof[((i - k) % 12 + 12) % 12]), s = corr(Array.from(ch), rot);
      if (s > best.score) best = { key: k, mode, score: +s.toFixed(3) };
    }
    return best;
  }
  // the scale degree (0–6) each bar of x sits on: the diatonic triad its pitch classes fit best (tonic slightly preferred)
  function barRoots(x, sr, an) {
    const S = SG(), scale = S.SCALES[an.mode] || S.SCALES.minor, barSec = 240 / an.bpm, out = [];
    const tri = [0, 1, 2, 3, 4, 5, 6].map(d => S.chordPCs(an.key, scale, d, false));
    const bias = [0.06, 0, 0, 0.02, 0.03, 0.01, 0];
    for (let t = an.phase; t + barSec * 0.5 <= x.length / sr; t += barSec) {
      const ch = chroma(x, sr, Math.round(t * sr), Math.min(x.length, Math.round((t + barSec) * sr)));
      const tot = ch.reduce((s, v) => s + v, 0) || 1;
      let bd = 0, bs = -1;
      tri.forEach((pcs, d) => { const s = pcs.reduce((a, pc) => a + ch[pc], 0) / tot + bias[d]; if (s > bs) { bs = s; bd = d; } });
      out.push(bd);
    }
    return out.length ? out : [0];
  }

  // ═══════════════════════════════════════════════════════════════
  // audio DSP: the four ways a recording becomes the remix's 'source' layer
  // ═══════════════════════════════════════════════════════════════
  // copy src[a, a+n) into dst at d with short fades (no clicks at the cuts); reverse plays the slice backwards
  function copySlice(src, dst, a, n, d, { reverse = false, gain = 1, fade = 96 } = {}) {
    for (let c = 0; c < dst.length; c++) {
      const s = src[c % src.length], o = dst[c];
      for (let i = 0; i < n; i++) {
        const di = d + i; if (di < 0 || di >= o.length) continue;
        const si = reverse ? a + n - 1 - i : a + i; if (si < 0 || si >= s.length) continue;
        const f = Math.min(1, i / fade, (n - 1 - i) / fade);
        o[di] += s[si] * gain * f;
      }
    }
  }
  // CHOP: eighth-note slices re-sequenced bar by bar. → { channels, srcBars: the source bar each output bar came from }
  function chopLayer(chs, sr, an, outBars, R, density = 0.6) {
    const beat = 60 / an.bpm, bar = 4 * beat, slot = beat / 2, slotN = Math.round(slot * sr), barN = Math.round(bar * sr);
    const avail = Math.max(1, Math.floor((chs[0].length / sr - an.phase) / bar));
    const out = [new Float32Array(outBars * barN), new Float32Array(outBars * barN)], srcBars = [];
    let sb = 0;
    for (let b = 0; b < outBars; b++) {
      if (b > 0) sb = R.chance(0.25) ? sb : R.chance(0.3) ? R.int(0, avail - 1) : (sb + 1) % avail;   // repeat · jump · walk on
      srcBars.push(sb);
      const base = Math.round((an.phase + sb * bar) * sr), roll = b % 4 === 3;
      let prev = 0;
      for (let k = 0; k < 8; k++) {
        const at = b * barN + k * slotN;
        if (roll && k >= 6) {                                          // a fill: 16th, then 32nd stutters of slot 5
          const div = k === 6 ? 2 : 4, n = Math.round(slotN / div);
          for (let j = 0; j < div; j++) copySlice(chs, out, base + 5 * slotN, n, at + j * n, { gain: 0.85 + 0.15 * (j % 2) });
          continue;
        }
        const r = R();
        let s = k, opt = {};
        if (k && r < 0.15 * density) s = prev;                         // repeat the slot before
        else if (r < 0.15 * density + 0.1 * density) {                // a 16th stutter
          const n = Math.round(slotN / 2);
          copySlice(chs, out, base + k * slotN, n, at); copySlice(chs, out, base + k * slotN, n, at + n);
          prev = k; continue;
        } else if (r < 0.25 * density + 0.08) opt.reverse = true;
        else if (r < 0.25 * density + 0.14) { prev = k; continue; }   // a gap
        else if (r < 0.25 * density + 0.19) s = R.int(0, 7);
        copySlice(chs, out, base + s * slotN, slotN, at, opt);
        prev = s;
      }
    }
    return { channels: out, srcBars };
  }
  // the source laid bar by bar from its downbeat (looping when shorter): which source bar plays under each output bar
  const linearBars = (chs, sr, an, outBars, startBar = 0) => {
    const avail = Math.max(1, Math.floor((chs[0].length / sr - an.phase) / (240 / an.bpm)));
    return Array.from({ length: outBars }, (_, b) => (startBar + b) % avail);
  };
  // lay source bars (srcBars) end to end at the source tempo, with 3 ms joins
  function barsLayer(chs, sr, an, srcBars) {
    const barN = Math.round(240 / an.bpm * sr), out = [new Float32Array(srcBars.length * barN), new Float32Array(srcBars.length * barN)];
    srcBars.forEach((sb, b) => copySlice(chs, out, Math.round((an.phase + sb * 240 / an.bpm) * sr), barN, b * barN, { fade: 144 }));
    return out;
  }
  // DUB: the source through drop-outs, filter sweeps and echo throws (dotted-eighth delay, darkening feedback)
  async function dubLayer(chs, sr, an, outBars, R) {
    const srcBars = linearBars(chs, sr, an, outBars), dry = barsLayer(chs, sr, an, srcBars);
    const barSec = 240 / an.bpm, beat = barSec / 4, len = dry[0].length + Math.round(4 * barSec * sr);
    const ctx = new OfflineAudioContext(2, len, sr), src = ctx.createBufferSource(), buf = ctx.createBuffer(2, dry[0].length, sr);
    buf.copyToChannel(dry[0], 0); buf.copyToChannel(dry[1], 1); src.buffer = buf;
    const g = ctx.createGain(), lp = ctx.createBiquadFilter(), send = ctx.createGain(), dl = ctx.createDelay(4), fb = ctx.createGain(), fl = ctx.createBiquadFilter(), fh = ctx.createBiquadFilter(), wet = ctx.createGain();
    lp.type = 'lowpass'; lp.Q.value = 0.9; lp.frequency.value = 16000;
    dl.delayTime.value = beat * 0.75; fb.gain.value = 0.58; fl.type = 'lowpass'; fl.frequency.value = 2400; fh.type = 'highpass'; fh.frequency.value = 280; wet.gain.value = 0.9;
    src.connect(g); g.connect(lp); lp.connect(ctx.destination);
    lp.connect(send); send.connect(dl); dl.connect(fl); fl.connect(fh); fh.connect(fb); fb.connect(dl); fh.connect(wet); wet.connect(ctx.destination);
    g.gain.setValueAtTime(1, 0); send.gain.setValueAtTime(0, 0);
    for (let p = 0; p < outBars; p += 4) {
      const t0 = p * barSec, end = Math.min(outBars, p + 4) * barSec;
      const drop = p > 0 && R.chance(0.45), sweep = R.chance(0.35);
      if (drop) {                                                       // bars 2–3 of the phrase drop out (drums + bass carry on)
        const a = t0 + barSec + (R.chance(0.5) ? 0 : 2 * beat), z = t0 + 3 * barSec;
        g.gain.setValueAtTime(1, a - 0.01); g.gain.linearRampToValueAtTime(0, a + 0.02); g.gain.setValueAtTime(0, z - 0.02); g.gain.linearRampToValueAtTime(1, z + 0.01);
        send.gain.setValueAtTime(0, a - 2 * beat); send.gain.linearRampToValueAtTime(0.85, a - 2 * beat + 0.02); send.gain.setValueAtTime(0.85, a); send.gain.linearRampToValueAtTime(0, a + 0.05);
      }
      if (sweep) { lp.frequency.setValueAtTime(320, t0); lp.frequency.exponentialRampToValueAtTime(16000, t0 + Math.min(2 * barSec, end - t0)); }
      // a throw on the phrase's last beat
      const th = end - beat;
      if (th > t0 && R.chance(0.7)) { send.gain.setValueAtTime(0, th - 0.01); send.gain.linearRampToValueAtTime(0.8, th + 0.01); send.gain.setValueAtTime(0.8, th + beat * 0.6); send.gain.linearRampToValueAtTime(0, th + beat * 0.65); }
    }
    src.start(0);
    const r = await ctx.startRendering();
    const n = dry[0].length;                                            // the tail past the end folds back to the top (loops cleanly)
    const o = [r.getChannelData(0).slice(0, n), r.getChannelData(1).slice(0, n)];
    for (let c = 0; c < 2; c++) { const d = r.getChannelData(c); for (let i = n; i < d.length; i++) o[c][i - n] += d[i]; }
    return { channels: o, srcBars };
  }
  // TAPE: playback slowed by `rate` (pitch with it) with wow (0.5 Hz) + flutter (6.5 Hz), band-limited, softly saturated
  async function tapeLayer(chs, sr, an, outBars, rate, R) {
    const srcBars = linearBars(chs, sr, an, Math.ceil(outBars * rate) + 1), dry = barsLayer(chs, sr, an, srcBars);
    const barSec = 240 / (an.bpm * rate), len = Math.round(outBars * barSec * sr);
    const ctx = new OfflineAudioContext(2, len, sr), src = ctx.createBufferSource(), buf = ctx.createBuffer(2, dry[0].length, sr);
    buf.copyToChannel(dry[0], 0); buf.copyToChannel(dry[1], 1); src.buffer = buf; src.playbackRate.value = rate;
    const wow = ctx.createOscillator(), wg = ctx.createGain(), fl = ctx.createOscillator(), fg = ctx.createGain();
    wow.frequency.value = 0.45 + R() * 0.15; wg.gain.value = 0.0035 * rate; fl.frequency.value = 6.5; fg.gain.value = 0.0012 * rate;
    wow.connect(wg); wg.connect(src.playbackRate); fl.connect(fg); fg.connect(src.playbackRate);
    const lp = ctx.createBiquadFilter(), hp = ctx.createBiquadFilter(), sat = ctx.createWaveShaper(), g = ctx.createGain();
    lp.type = 'lowpass'; lp.frequency.value = 4200; lp.Q.value = 0.5; hp.type = 'highpass'; hp.frequency.value = 90;
    const curve = new Float32Array(1024); for (let i = 0; i < 1024; i++) { const x = i / 511.5 - 1; curve[i] = Math.tanh(1.6 * x) / Math.tanh(1.6); }
    sat.curve = curve; g.gain.value = 0.8;
    src.connect(hp); hp.connect(lp); lp.connect(sat); sat.connect(g); g.connect(ctx.destination);
    wow.start(0); fl.start(0); src.start(0);
    const r = await ctx.startRendering();
    // which source bar each output bar holds (the slowed tape covers fewer source bars than output bars)
    return { channels: [r.getChannelData(0), r.getChannelData(1)], srcBars: Array.from({ length: outBars }, (_, b) => srcBars[Math.min(srcBars.length - 1, Math.floor(b * rate))]) };
  }
  // STRETCH: paulstretch — magnitudes kept, phases randomised, overlap-added; L and R get different random phases
  // (one inverse FFT carries both: Z = X·e^{iφL} + i·X·e^{iφR} → real part left, imaginary part right)
  function paulstretch(x, sr, outFrames, R, { N = 8192 } = {}) {
    const hop = N / 4, w = hann(N), outL = new Float32Array(outFrames + N), outR = new Float32Array(outFrames + N);
    const frames = Math.ceil(outFrames / hop), inHop = Math.max(1, (x.length - N) / Math.max(1, frames));
    const re = new Float64Array(N), im = new Float64Array(N), zr = new Float64Array(N), zi = new Float64Array(N);
    for (let f = 0; f < frames; f++) {
      const o = Math.min(Math.max(0, x.length - N), Math.round(f * inHop));
      for (let i = 0; i < N; i++) { re[i] = (x[o + i] || 0) * w[i]; im[i] = 0; }
      fft(re, im, false);
      zr.fill(0); zi.fill(0);
      for (let k = 1; k < N / 2; k++) {
        const m = Math.hypot(re[k], im[k]), a = R() * 2 * Math.PI, b = R() * 2 * Math.PI;
        const lr = m * Math.cos(a), li = m * Math.sin(a), rr = m * Math.cos(b), ri = m * Math.sin(b);
        // Z[k] = L[k] + i·R[k]; Z[N-k] = conj(L[k]) + i·conj(R[k])
        zr[k] = lr - ri; zi[k] = li + rr;
        zr[N - k] = lr + ri; zi[N - k] = -li + rr;
      }
      fft(zr, zi, true);
      const at = f * hop;
      for (let i = 0; i < N; i++) { const g = w[i] / 1.5; if (at + i < outL.length) { outL[at + i] += zr[i] * g; outR[at + i] += zi[i] * g; } }
    }
    return [outL.subarray(0, outFrames), outR.subarray(0, outFrames)];
  }
  // the loudest stretch of the recording (where something is happening): [a, b) in frames, sec long
  function liveliest(x, sr, sec) {
    const n = Math.min(x.length, Math.round(sec * sr)); if (n >= x.length) return [0, x.length];
    const step = Math.round(sr), energies = [];
    for (let i = 0; i + step <= x.length; i += step) { let e = 0; for (let j = i; j < i + step; j++) e += x[j] * x[j]; energies.push(e); }
    const win = Math.round(n / step); let best = 0, bestE = -1, acc = 0;
    for (let i = 0; i < energies.length; i++) { acc += energies[i]; if (i >= win) acc -= energies[i - win]; if (i >= win - 1 && acc > bestE) { bestE = acc; best = i - win + 1; } }
    return [best * step, best * step + n];
  }
  function stretchLayer(chs, sr, outSec, R) {
    const x = mono(chs), [a, b] = liveliest(x, sr, clamp(outSec / 5, 6, 30));
    const seg = x.subarray(a, b), outFrames = Math.round(outSec * sr);
    const st = paulstretch(seg, sr, outFrames, R);
    // a slow fade in and out, peak to -6 dBFS
    let pk = 0; for (const c of st) for (let i = 0; i < c.length; i++) pk = Math.max(pk, Math.abs(c[i]));
    const g = pk > 0 ? 0.5 / pk : 1, fi = Math.round(2 * sr), fo = Math.round(4 * sr);
    for (const c of st) for (let i = 0; i < c.length; i++) c[i] *= g * Math.min(1, i / fi, (c.length - 1 - i) / fo);
    return { channels: st, factor: outFrames / Math.max(1, seg.length), excerpt: [a / sr, b / sr] };
  }
  const peakNorm = (chs, to = 0.5) => { let pk = 0; for (const c of chs) for (let i = 0; i < c.length; i++) pk = Math.max(pk, Math.abs(c[i])); if (pk > 0) for (const c of chs) for (let i = 0; i < c.length; i++) c[i] *= to / pk; return chs; };

  // ═══════════════════════════════════════════════════════════════
  // notes: motif development + the grafted plan
  // ═══════════════════════════════════════════════════════════════
  const MOTIF_OPS = ['invert', 'retro', 'augment', 'diminish', 'displace', 'sequence'];
  // a motif is [{s: 16th step 0–31 (two bars), step: scale-degree offset}]
  function motifOp(motif, op) {
    const m = (motif || []).map(x => ({ s: x.s, step: x.step })).sort((a, b) => a.s - b.s);
    if (!m.length) return m;
    const uniq = list => { const seen = new Set(); return list.filter(x => x.s >= 0 && x.s < 32 && !seen.has(x.s) && seen.add(x.s)).sort((a, b) => a.s - b.s); };
    if (op === 'invert') { const p = m[0].step; return m.map(x => ({ s: x.s, step: clamp(2 * p - x.step, -7, 9) })); }
    if (op === 'retro') { const last = m[m.length - 1].s, steps = m.map(x => x.step).reverse(); return uniq(m.map((x, i) => ({ s: last - m[m.length - 1 - i].s, step: steps[i] }))); }
    if (op === 'augment') return uniq(m.map(x => ({ s: x.s * 2, step: x.step })));
    if (op === 'diminish') { const h = m.map(x => ({ s: Math.floor(x.s / 2), step: x.step })); return uniq(h.concat(h.map(x => ({ s: x.s + 16, step: x.step + 1 })))); }
    if (op === 'displace') return uniq(m.map(x => ({ s: (x.s + 2) % 32, step: x.step })));
    if (op === 'sequence') return uniq(m.filter(x => x.s < 16).concat(m.filter(x => x.s < 16).map(x => ({ s: x.s + 16, step: x.step + 2 }))));
    return m;
  }
  const darkOf = mode => !!MINORISH[mode];
  const inRange = (st, bpm) => Math.round(clamp(bpm, st.bpm[0] * 0.85, st.bpm[1] * 1.1));
  // the options for one NOTES remix take. src: the source song's options (a take's project.gen.o / its mood), tm: the
  // target track's own mood (takeMood), with: a BLEND partner's options. → { o (TempMaker.compose options, with the
  // graft), style, op, key, label, roles }
  function notesOptions(recipe, src, ctx) {
    const S = SG(), tm = ctx.target || {}, srcPl = S.plan(Object.assign({}, src, { graft: null }));
    // one stream per decision: an asked-for style (⟳ AGAIN passes the one it got) leaves every other draw where it was
    const RS = S.rng(ctx.seed * 3 + 17), R = S.rng(ctx.seed * 3 + 29), RT = S.rng(ctx.seed * 3 + 41);
    const dark = darkOf(srcPl.mode), side = dark ? 'dark' : 'bright', same = !!ctx.sameTrack;
    const pickFrom = (list, not) => { const l = list.filter(x => S.STYLES[x] && x !== not); return l.length ? RS.pick(l) : not; };
    let style = ctx.style && S.STYLES[ctx.style] ? ctx.style : null, op = 'none', density = same ? srcPl.density : tm.density ?? srcPl.density, bpm = srcPl.bpm;
    const drop = new Set(), add = new Set();
    if (recipe === 'restyle' || recipe === 'cover' || recipe === 'blend') {
      if (!style) style = !same && ctx.n === 0 && tm.style && tm.style !== srcPl.styleId ? tm.style : pickFrom(NEAR[srcPl.styleId] || Object.keys(S.STYLES), srcPl.styleId);
      if (recipe === 'restyle' && R.chance(0.3)) op = R.pick(['sequence', 'displace']);
    } else if (recipe === 'variations') {
      style = style || srcPl.styleId; op = R.pick(MOTIF_OPS);
      density = clamp(srcPl.density + (R() - 0.5) * 0.3, 0.2, 0.9); bpm = srcPl.bpm * (0.92 + R() * 0.16);
    } else if (recipe === 'underscore') {
      style = style || pickFrom(QUIET[side]); density = 0.22 + R() * 0.12; bpm = srcPl.bpm * 0.85; op = R.chance(0.5) ? 'augment' : 'none';
      drop.add('drums'); if (R.chance(0.5)) drop.add('bass');
    } else if (recipe === 'intense') {
      style = style || (DRIVE[side].includes(srcPl.styleId) ? srcPl.styleId : pickFrom(DRIVE[side])); density = 0.8 + R() * 0.12; bpm = srcPl.bpm * 1.18;
      op = R.chance(0.4) ? 'diminish' : 'none'; add.add('drums'); add.add('bass');
    } else if (recipe === 'dream') {
      style = style || pickFrom(HAZE[side]); density = 0.28 + R() * 0.1; bpm = srcPl.bpm * 0.7; op = 'augment'; drop.add('drums');
    }
    const st = S.STYLES[style];
    if (recipe === 'restyle' || recipe === 'cover' || recipe === 'blend') bpm = srcPl.bpm >= st.bpm[0] * 0.85 && srcPl.bpm <= st.bpm[1] * 1.1 ? srcPl.bpm : st.bpm[0] + (st.bpm[1] - st.bpm[0]) * RT();
    bpm = recipe === 'intense' ? Math.round(clamp(bpm, st.bpm[0], st.bpm[1] * 1.1)) : inRange(st, bpm);
    // key: the target's tonal home when the remix is for another track (its volume's key), else the source's own
    const key = ctx.key !== undefined && ctx.key !== null ? ((+ctx.key % 12) + 12) % 12 : !same && tm.key !== undefined && tm.key !== null ? tm.key : srcPl.key;
    const sections = srcPl.sections.map((s, i) => {
      let roles = s.roles.filter(r => !drop.has(r));
      if (add.size && s.base !== 'intro') for (const r of add) if (!roles.includes(r)) roles.push(r);
      if (!roles.length) roles = ['pad'];
      return Object.assign({}, s, { roles });
    });
    const withPl = ctx.with ? S.plan(Object.assign({}, ctx.with, { graft: null })) : null;
    const theme = withPl || srcPl;
    const keepB = recipe !== 'variations';
    const graft = pl => {
      const HP = {};
      for (const [k, h] of Object.entries(srcPl.HP)) {
        const mine = pl.HP[k] || pl.HP.A, keep = keepB || ['A', 'intro', 'outro', 'loop', 'bed'].includes(k);
        HP[k] = keep ? { prog: h.prog, hr: h.hr, ext: mine.ext } : mine;
      }
      return { mode: srcPl.mode, scale: srcPl.scale, key, HP, sections: sections.map(s => Object.assign({}, s, { roles: s.roles.slice() })),
        motifA: motifOp(theme.motifA, op), motifB: motifOp(theme.motifB, op), motif: theme.motif };
    };
    const o = { seed: ctx.seed, style, form: 'song', mode: srcPl.mode, key, bpm, density: +density.toFixed(2), motif: theme.motif || undefined,
      textures: recipe === 'intense' ? undefined : src.textures, fx: recipe === 'underscore' || recipe === 'dream' ? 'none' : undefined, graft };
    const label = RECIPES[recipe].name + ' · ' + st.name + (op !== 'none' ? ' · theme ' + op : '') + (key !== srcPl.key ? ' · in ' + S.NOTE_NAMES[key] : '');
    return { o, style, op, key, srcKey: srcPl.key, srcPlan: srcPl, label, sections };
  }

  // ═══════════════════════════════════════════════════════════════
  // sources
  // ═══════════════════════════════════════════════════════════════
  // a source is { kind: 'take', id, title, dir } (a take folder in review staging) or { kind: 'file', id, title, path }
  // (real audio at a catalog src, or an approved temp's <base>.temp.ogg). → the loaded source:
  // { ref, title, opts (the song options; takes only), project (the take's project.json, if any), meta, known {bpm, key, mode} }
  async function loadSource(ref) {
    const G = AKg().game, out = { ref, title: ref.title || ref.id, opts: null, project: null, meta: null, known: null };
    if (ref.kind === 'take') {
      out.meta = JSON.parse(await G.readText(ref.dir + 'meta.json'));
      try { out.project = JSON.parse(await G.readText(ref.dir + 'project.json')); } catch (e) {}
      const mo = out.meta.mood || {}, g = out.project && out.project.gen && out.project.gen.o;
      out.opts = g && g.style ? Object.assign({}, g) : { seed: mo.seed, style: mo.style, form: mo.form, mode: mo.mode, bpm: mo.bpm, density: mo.density, key: mo.key,
        motif: mo.motif, motifSpec: mo.motifSpec, shape: mo.shape, textures: mo.textures, fx: mo.fx, hit: mo.hit, voices: mo.voices };
      // an edit in the DAW may have changed the tempo
      if (out.project && +out.project.bpm > 0) out.opts.bpm = +out.project.bpm;
      out.known = { bpm: +(out.project && out.project.bpm) || +mo.bpm, key: mo.key, mode: mo.mode, phase: 0 };
    } else if (ref.known) out.known = Object.assign({ phase: 0 }, ref.known);
    return out;
  }
  async function decodeFile(path) {
    const f = await AKg().game.readFile(path), ab = await f.arrayBuffer();
    const ctx = new OfflineAudioContext(2, 1, RATE), buf = await ctx.decodeAudioData(ab);
    const chs = []; for (let c = 0; c < Math.min(2, buf.numberOfChannels); c++) chs.push(buf.getChannelData(c).slice());
    if (chs.length === 1) chs.push(chs[0].slice());
    return chs;
  }
  // the audio a recipe works from: the source's stems minus the ones the recipe replaces (drums …), else its mix
  async function sourceAudio(src, recipe) {
    const G = AKg().game, dropRe = DROP_STEMS[recipe] || /^drums$/;
    let man = null, mixPath = null;
    if (src.ref.kind === 'take') { mixPath = src.ref.dir + 'mix.wav'; try { man = JSON.parse(await G.readText(src.ref.dir + 'stems.json')); } catch (e) {} }
    else {
      mixPath = src.ref.path;
      const base = src.ref.path.replace(/\.temp\.ogg$/, '').replace(/\.[^.\/]+$/, '');
      if (/\.temp\.ogg$/.test(src.ref.path)) { try { man = JSON.parse(await G.readText(base + '.stems.json')); } catch (e) {} }
    }
    const keep = man && man.stems ? man.stems.filter(s => !dropRe.test(String(s.role || s.name)) && !dropRe.test(String(s.name))) : [];
    if (keep.length && keep.length < man.stems.length) {
      let sum = null;
      for (const s of keep) {
        const chs = await decodeFile(s.file);
        if (!sum) sum = [new Float32Array(chs[0].length), new Float32Array(chs[0].length)];
        for (let c = 0; c < 2; c++) for (let i = 0; i < Math.min(sum[c].length, chs[c].length); i++) sum[c][i] += chs[c][i];
      }
      return { channels: sum, sampleRate: RATE, stems: keep.map(s => s.name) };
    }
    return { channels: await decodeFile(mixPath), sampleRate: RATE, stems: null };
  }
  // tempo / key / phase: the source's own metadata when it has it, else listened for
  function analyse(chs, sr, known) {
    const x = mono(chs), an = { bpm: 0, phase: 0, key: 0, mode: 'minor', guessed: [] };
    if (known && +known.bpm > 0) { an.bpm = +known.bpm; an.phase = +known.phase || 0; }
    else { const t = estimateTempo(x, sr); an.bpm = t.bpm || 90; an.phase = t.bpm ? downbeat(x, sr, t.bpm, t.phase) : 0; an.tempoConfidence = t.confidence; an.guessed.push('tempo'); }
    // keep the guess musical: fold into 70–160
    while (an.bpm > 160) an.bpm /= 2; while (an.bpm < 65) an.bpm *= 2;
    if (known && known.key !== undefined && known.key !== null && known.mode) { an.key = +known.key; an.mode = known.mode; }
    else { const k = estimateKey(x, sr); an.key = k.key; an.mode = k.mode; an.keyScore = k.score; an.guessed.push('key'); }
    an.roots = barRoots(x, sr, an);
    an.seconds = x.length / sr;
    return an;
  }

  // a root-following bass: each bar on the root of the source bar under it, on the style's kick steps (dub: off the one)
  function rootBass(roots, an, bars, styleId, R) {
    const S = SG(), BAR = S.BAR, S16 = S.S16, scale = S.SCALES[an.mode] || S.SCALES.minor, st = S.STYLES[styleId] || {};
    const grid = String(((st.grooves || [])[0] || {}).kick || '1000000010000000');
    let steps = []; for (let i = 0; i < 16; i++) if (grid[Math.floor(i * grid.length / 16)] === '1' || grid[Math.floor(i * grid.length / 16)] === 'x') steps.push(i);
    if (styleId === 'dub') steps = R.pick([[2, 3, 6, 8, 10, 12], [0, 3, 6, 10, 12], [2, 6, 8, 10, 14]]);
    if (!steps.length) steps = [0, 8];
    const notes = [];
    for (let b = 0; b < bars; b++) {
      const deg = roots[b % roots.length] || 0;
      let n = S.deg2midi(an.key, scale, deg, 2); while (n < 33) n += 12; while (n > 47) n -= 12;
      steps.forEach((s, i) => {
        const next = i + 1 < steps.length ? steps[i + 1] : 16, d = Math.max(S16, (next - s) * S16 - 6);
        const fifth = i > 0 && R.chance(0.18) ? S.deg2midi(an.key, scale, deg + 4, 2) : null;
        let m = fifth || n; while (m < 33) m += 12; while (m > 50) m -= 12;
        notes.push({ t: b * BAR + s * S16, d, n: m, v: s === 0 ? 0.82 : 0.66 + R() * 0.08 });
      });
    }
    return notes;
  }

  // ═══════════════════════════════════════════════════════════════
  // making remix takes
  // ═══════════════════════════════════════════════════════════════
  // req: { takes, recipe, from: ref, with?: ref, style?, key?, seed?, review? } → like TempMaker.makeTakes (events
  // progress / take / done; returns the entries)
  async function remixTakes(E, list, req, ctx = {}) {
    const S = SG(), T = TM(), AK = AKg(), on = ctx.onEvent || (() => {});
    const recipe = RECIPES[req.recipe] ? req.recipe : 'restyle', R0 = RECIPES[recipe], nTakes = clamp(Math.round(+req.takes || 1), 1, 12);
    if (!req.from) throw new Error('no source to remix');
    if (R0.needsWith && !req.with) throw new Error(R0.name + ' needs a second source (WITH)');
    const briefs = ctx.briefs !== undefined ? ctx.briefs : await T.loadBriefs();
    const score = ctx.score !== undefined ? ctx.score : await T.loadScore();
    const src = await loadSource(req.from), wth = req.with ? await loadSource(req.with) : null;
    if (R0.kind === 'notes' && !src.opts) throw new Error(R0.name + ' needs a take made here (its notes) — a recording can only take the audio recipes (CHOP, DUB, STRETCH, TAPE)');
    if (recipe === 'blend' && !(wth && wth.opts)) throw new Error('BLEND needs a take (with notes) as its WITH source');
    let audio = null, an = null;
    const done = [], total = list.length * nTakes; let k = 0;
    for (const t of list) {
      const b = (briefs && briefs[t.id]) || null, seeds = await T.seedsUsed(t.id);
      const tm = T.takeMood(t, b, {}, score);
      for (let n = 0; n < nTakes; n++) {
        k++;
        const seed = req.seed != null && n === 0 ? Math.round(+req.seed) : T.nextSeed(t.id, S.hash(t.id + '|' + recipe + '|' + JSON.stringify(req.from) + '|' + n) % 1000000000, seeds.used);
        seeds.used.add(seed);
        const tag = k + '/' + total + ' · ' + t.title + ' · ' + R0.name + ' of ' + src.title + ' · seed ' + seed;
        const say = (stage, text) => on({ type: 'progress', id: t.id, n: k, total, stage, text: tag + ' — ' + text });
        try {
          if (E.project) E.project.name = t.id;
          let song, why, bars, label, extra = {};
          if (R0.kind === 'notes') {
            say('compose', 'grafting the source’s chords, sections and theme…');
            const no = notesOptions(recipe, src.opts, { seed, n, target: tm, sameTrack: src.ref.id === t.id, style: req.style, key: req.key, with: wth && wth.opts });
            song = await T.compose(E, no.o, ctx.inst || 'forge');
            if (recipe === 'cover') coverLead(E, src, no);
            label = no.label; extra = { op: no.op, key: no.key };
            await T.shapeArrangement(E, song, {});
            if (req.bars) bars = Math.max(1, Math.round(+req.bars));
            else { const secs = song.bars * S.BAR * E.spt(); bars = song.bars * Math.max(1, Math.ceil(T.TEMP_MIN_SEC / secs)); }
            extra.arrangement = T.arrangeTo(E, song, bars);
          } else {
            if (!audio) { say('listen', 'reading the source audio…'); audio = await sourceAudio(src, recipe); say('listen', 'listening for tempo + key…'); an = analyse(audio.channels, RATE, src.known); }
            const R = S.rng(seed * 5 + 3), side = darkOf(an.mode) ? 'dark' : 'bright';
            const style = req.style && S.STYLES[req.style] ? req.style : R.pick(AUDIO_STYLE[recipe][side]);
            const rate = recipe === 'tape' ? Math.pow(2, -2 / 12) : 1;
            const key = recipe === 'tape' ? (an.key + 10) % 12 : an.key;
            const bpm = recipe === 'stretch' ? Math.round(clamp(tm.bpm || 66, 56, 72)) : +(an.bpm * rate).toFixed(4);
            // length: at least TEMP_MIN_SEC, whole 4-bar phrases
            bars = req.bars ? Math.max(4, Math.round(+req.bars)) : Math.max(8, Math.ceil(T.TEMP_MIN_SEC * bpm / 240 / 4) * 4);
            say('compose', 'composing the new band…');
            const shape = recipe === 'stretch' ? [['bed', 8, ['lead']]] : [['A', 4, ['drums']], ['B', 4, ['drums']]];
            const o = { seed, style, form: 'song', mode: an.mode === 'major' ? 'major' : an.mode, key, bpm, density: recipe === 'stretch' ? 0.3 : 0.6, shape,
              textures: recipe === 'tape' ? ['amb_vinyl'] : recipe === 'stretch' ? undefined : 'none', fx: recipe === 'stretch' ? 'none' : undefined, hit: recipe === 'dub' ? 'none' : undefined };
            if (recipe === 'stretch') o.progression = [an.roots.length ? mostCommon(an.roots) : 0];
            song = await T.compose(E, o, ctx.inst || 'forge');
            await T.shapeArrangement(E, song, {});
            extra.arrangement = T.arrangeTo(E, song, bars);
            say('process', 'cutting the source (' + R0.name + ')…');
            const DR = S.rng(seed * 11 + 7);
            let layer, srcBars = null;
            if (recipe === 'chop') ({ channels: layer, srcBars } = chopLayer(audio.channels, RATE, an, bars, DR, 0.6));
            else if (recipe === 'dub') ({ channels: layer, srcBars } = await dubLayer(audio.channels, RATE, an, bars, DR));
            else if (recipe === 'tape') ({ channels: layer, srcBars } = await tapeLayer(audio.channels, RATE, an, bars, rate, DR));
            else { const r = stretchLayer(audio.channels, RATE, bars * 240 / bpm, DR); layer = r.channels; extra.stretch = { factor: +r.factor.toFixed(2), excerpt: r.excerpt.map(x => +x.toFixed(2)) }; }
            peakNorm(layer, 0.5);
            // the new bass follows the source's harmony bar by bar (stretch: one sustained root)
            if (recipe !== 'stretch') {
              const roots = srcBars.map(sb => an.roots[sb % an.roots.length]);
              await addBass(E, rootBass(roots, Object.assign({}, an, { key }), bars, style, S.rng(seed * 7 + 1)), bars, style, seed);
            }
            const rec = await AK.lib.put({ kind: 'remix', name: t.id + ' ' + recipe + ' ' + seed, sampleRate: RATE,
              meta: { tags: ['remix', recipe], forTrack: t.id, from: src.title, recipe, seed } }, layer);
            const tr = E.addTrack('audio', { name: 'source', role: 'source', color: '#c9a0dc' });
            tr.audio.push({ t: 0, libId: rec.id, name: R0.name + ' · ' + src.title, offset: 0, len: layer[0].length / RATE, gain: 1 });
            tr.mix.vol = 0.72;
            E.applyMix();
            label = R0.name + ' · ' + S.STYLES[style].name + ' band' + (recipe === 'tape' ? ' · two semitones down' : '');
            extra.analysis = { bpm: an.bpm, key: an.key, mode: an.mode, guessed: an.guessed, tempo_confidence: an.tempoConfidence, stems: audio.stems };
            extra.lib = rec.id;
          }
          const P = E.project; P.name = t.id; P.loop = { on: false, a: 0, b: bars };
          E.emit('project');
          await E.whenReady();
          say('render', 'rendering…');
          const stems = req.stems !== false && E.canRenderOffline();
          const r = await T.render(E, { loop: false, stems, master: ctx.master !== false, lufs: ctx.lufs ?? -14,
            onProgress: p => p && p.phase === 'stem' && say('render', 'rendering stems: ' + p.done + ' of ' + p.total + ' done…') });
          const credits = await E.credits(), sec = r.channels[0].length / r.sampleRate;
          why = 'REMIX · ' + label + ' — from ' + src.title + (src.ref.take ? ' (take ' + src.ref.take + ')' : '') + (wth ? ' with the theme of ' + wth.title : '');
          const mood = { style: song.style, form: song.form, mode: song.mode, key: song.key, bpm: +(+P.bpm).toFixed(4), density: song.density, seed,
            composer: song.v || 1, motif: song.motif || undefined, textures: song.textures && song.textures.length ? song.textures : 'none', fx: song.fx || 'none', hit: song.hit || 'none', vocab: song.vocab };
          const request = { remix: { recipe, from: req.from, with: req.with || undefined, style: req.style || undefined, key: req.key ?? undefined, bars: req.bars || undefined } };
          say('write', 'saving…');
          const take = T.takeStamp() + '-s' + seed + '-' + recipe, dir = T.REVIEW_DIR + '/' + t.id + '/' + take + '/';
          const meta = { v: 1, id: t.id, take, created: new Date().toISOString(), status: 'candidate', title: t.title, vol: t.vol, src: t.src,
            mood, why, request, remix: Object.assign({ recipe, from: src.title, label }, extra), instruments: T.instrumentsOf(E), arrangement: extra.arrangement,
            roles: P.tracks.map(x => x.role || x.name), lufs: r.mastered ? +r.mastered.after.toFixed(1) : null,
            true_peak: r.mastered ? +r.mastered.truePeak.toFixed(2) : +AK.util.db(AK.util.peakOf(r.channels)).toFixed(2),
            seconds: +sec.toFixed(3), bars, sample_rate: r.sampleRate, credits: credits.text || '', credits_worst: credits.worst || 'free', stems: [] };
          const files = await T.writeTake(E, dir, r, r.stems, credits, meta);
          done.push({ id: t.id, take, dir, seed, files, recipe, label });
          on({ type: 'take', id: t.id, take, seed });
        } catch (e) { done.push({ id: t.id, seed, error: e.message || String(e) }); on({ type: 'take', id: t.id, error: e.message || String(e) }); }
      }
    }
    on({ type: 'done', made: done.filter(d => !d.error), failed: done.filter(d => d.error) });
    return done;
  }
  const mostCommon = a => { const c = new Map(); for (const x of a) c.set(x, (c.get(x) || 0) + 1); return [...c.entries()].sort((p, q) => q[1] - p[1])[0][0]; };
  // COVER: the source's own lead notes (its project's lead patterns; else regenerated from its options), section by
  // section, moved to the remix's key
  function coverLead(E, src, no) {
    const S = SG(), tr = E.project.tracks.find(x => x.role === 'lead'); if (!tr) return;
    const srcTr = src.project && src.project.tracks && src.project.tracks.find(x => x.role === 'lead');
    const gen = srcTr ? null : S.song(Object.assign({}, src.opts)).parts.lead;
    const pats = srcTr ? srcTr.patterns : gen.patterns;
    let d = ((no.key - no.srcKey) % 12 + 12) % 12; if (d > 6) d -= 12;
    for (const [pid, p] of Object.entries(tr.patterns)) {
      const q = pats[pid]; if (!q || !q.notes) continue;
      p.notes = q.notes.filter(x => x.t < p.lenBars * S.BAR).map(x => Object.assign({}, x, { n: clamp(x.n + d, 0, 127), d: Math.min(x.d, p.lenBars * S.BAR - x.t) }));
    }
  }
  async function addBass(E, notes, bars, style, seed) {
    const T = TM(), S = SG(), pr = S.presetFor(style, 'bass', seed) || 'bass_sub';
    let dev;
    try { dev = await T.deviceFor(E, 'bass', 'forge:' + pr); } catch (e) { dev = await T.deviceFor(E, 'bass', 'forge:bass_sub'); }
    dev.mix.vol = T.ROLE_LEVEL.bass;
    const tr = E.addTrack('midi', { name: 'bass', role: 'bass', deviceId: dev.id, color: T.COLORS.bass });
    tr.patterns = { bass_remix: { name: 'bass (follows the source)', lenBars: bars, notes } };
    tr.clips = [{ bar: 0, pid: 'bass_remix' }];
  }

  // every finished thing in the game folder that can be a source, for the director's REMIX FROM list:
  // takes (approved first) with their track, the catalog's real recordings, the approved temps' Oggs
  function sourcesFrom(cat, state, approvals) {
    const out = [];
    for (const t of cat) {
      const st = state[t.id]; if (!st) continue;
      const ap = st.approved && st.approved.take;
      for (const m of st.takes || []) {
        if (m.status === 'rejected') continue;
        out.push({ kind: 'take', id: t.id, title: t.title, take: m.take, dir: m.dir, approved: m.take === ap, label: t.title + ' — ' + (m.take === ap ? 'APPROVED ' : '') + 'take ' + m.take + ' (' + ((SG().STYLES[(m.mood || {}).style] || {}).name || '?') + ')' });
      }
      // a real recording: the catalog's own .ogg / .mp3, or a .wav that is not a temp (a FIELD RECORDER / TAPE STUDIO take)
      const rp = st.real ? t.src : st.wav === 'real' ? t.src.replace(/\.[^.\/]+$/, '') + '.wav' : null;
      if (rp) out.push({ kind: 'file', id: t.id, title: t.title, path: rp, real: true, label: t.title + ' — recording (' + rp.split('/').pop() + ')' });
      if (st.temp === 'ogg') {
        const a = ((approvals.tracks || {})[t.id] || {}).approved, mo = a && a.mood;
        // the approved take's folder is the better source (its notes too); the Ogg stands in when that folder is gone
        if (!(st.takes || []).some(m => a && m.take === a.take)) out.push({ kind: 'file', id: t.id, title: t.title, path: t.src.replace(/\.[^.\/]+$/, '') + '.temp.ogg', temp: true,
          known: mo ? { bpm: mo.bpm, key: mo.key, mode: mo.mode } : undefined, label: t.title + ' — approved temp (Ogg)' });
      }
    }
    return out.sort((a, b) => (b.approved || b.real || b.temp ? 1 : 0) - (a.approved || a.real || a.temp ? 1 : 0) || a.label.localeCompare(b.label));
  }

  root.Remix = { RECIPES, NEAR, MOTIF_OPS, fft, onsetEnvelope, estimateTempo, downbeat, estimateKey, chroma, barRoots, chopLayer, dubLayer, tapeLayer, paulstretch, stretchLayer,
    liveliest, motifOp, notesOptions, rootBass, loadSource, sourceAudio, analyse, remixTakes, sourcesFrom, coverLead };
  if (typeof module !== 'undefined' && module.exports) module.exports = root.Remix;
})(typeof window !== 'undefined' ? window : globalThis);
