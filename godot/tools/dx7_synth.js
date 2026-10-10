/* dx7_synth.js — DX7 · a Yamaha DX7-compatible 6-operator FM synth for the Modern Mythology tools
 *
 * Plays the public DX7 patch ecosystem (32-voice .syx cartridges, single-voice dumps) in the
 * browser, with the same engine the M-VAVE FM-1 stock firmware and Dexed are built on: msfa.
 * Plain classic script (no modules, no build step, no fetch) — works from file:// in Chrome, in a
 * live AudioContext or an OfflineAudioContext. The engine runs in an AudioWorklet added from a
 * data: URL (Chrome refuses Blob-URL worklet modules on file://; Blob URL is only the fallback).
 *
 *   const synth = new DX7Synth(ctx, { output: ctx.destination, maxVoices: 16 });
 *   await synth.init();
 *   const bank = DX7.parseSysex(new Uint8Array(await file.arrayBuffer()));
 *   synth.loadVoice(bank.voices[10]);
 *   synth.noteOn(60, 0.8, t, 1);  synth.noteOff(60, t + 1, 1);
 *   const ed = synth.mountEditor(el);   …   ed.destroy();
 *
 * DX7 (window.DX7) — SysEx + voice helpers
 *   parseSysex(bytes) → {kind:'bank'|'voice'|'none', voices:[voice…], banks:[[voice×32]…],
 *                        checksums:[{index, ok, expected, got}], warnings:[string], format}
 *     accepts 32-voice VMEM bulk dumps (F0 43 0n 09 20 00 + 4096 + sum + F7), with or without
 *     trailing garbage, several dumps concatenated, raw headerless 4096-byte VMEM (and 128·k raw),
 *     and single-voice VCED dumps (F0 43 0n 00 01 1B + 155 + sum + F7; a 1n sub-status is accepted).
 *     Bad checksums are reported in checksums[] / warnings[] but the data is still used.
 *   unpackVmem(bytes128, offset?) → voice     packVmem(voice) → Uint8Array(128)
 *   voiceFromVced(bytes155, offset?) → voice  voiceToVced(voice) → Uint8Array(155)
 *   voiceToSysex(voice, ch=1) → Uint8Array(163)   (F0 43 0n 00 01 1B … — the correct bulk sub-status)
 *   bankToSysex(voices[≤32], ch=1) → Uint8Array(4104)   (missing slots are INIT VOICE)
 *   voiceName(voice) → display name (trimmed, Yamaha ¥ → ← glyphs)
 *   normalizeVoice(any) → a complete voice object, every field an in-range integer (Dexed-style clamp)
 *   defaultVoice() → INIT VOICE        checksum(bytes) → 7-bit DX7 checksum
 *   ALGORITHMS[0..31] → {n, carriers:[op…], modulators:[op…], mods:{op:[modulator ops]},
 *                        targets:{op:[ops it modulates]}, edges:[[from,to]…],
 *                        feedback:{op, from, to, loop:[ops]}}   (ops are 1-based, OP1..OP6)
 *   analyze(voice) → {algorithm, carriers, brightness, brightnessLabel, envelope, fixed, feedback}
 *   describe(voice) → 'ALG 5 · 3 car · bright · percussive · fb 6'
 *
 * VOICE OBJECT — the shape fm1_dx7.js's dx7DefaultVoice() uses (so dx7VoiceSysex / DX7.voiceToSysex
 * can send any library voice to the hardware):
 *   { name:'E.PIANO 1', algorithm:0-31 (0-based), feedback:0-7, oscKeySync:0|1,
 *     lfoSpeed, lfoDelay, lfoPmd, lfoAmd:0-99, lfoKeySync:0|1, lfoWave:0-5 (tri saw↓ saw↑ sqr sin s/h),
 *     pitchModSens:0-7, transpose:0-48 (24 = C3), pitchRates:[4×0-99], pitchLevels:[4×0-99] (50 = 0),
 *     ops:[OP1…OP6] each { rates:[4×0-99], levels:[4×0-99], breakPoint:0-99 (39 = C3),
 *       leftDepth, rightDepth:0-99, leftCurve, rightCurve:0-3 (-LIN -EXP +EXP +LIN), rateScaling:0-7,
 *       ams:0-3, kvs:0-7, output:0-99, mode:0 ratio|1 fixed, coarse:0-31, fine:0-99, detune:0-14 (7 = 0) } }
 *
 * DX7Synth (window.DX7Synth) — same device API as ForgeSynth
 *   new DX7Synth(ctx, {output, maxVoices = 16})        init() → Promise (adds the worklet)
 *   loadVoice(voice)   voice (getter: a copy)          noteOn(note, vel01, when, ch)   noteOff(note, when, ch)
 *   allOff(when)  (when ≈ now also drops notes already scheduled ahead)   panic()
 *   cc(num, v01, when)  1 mod wheel · 2 breath · 4 foot · 7 volume · 64 sustain · 120 sound off ·
 *                       121 reset controllers · 123 all notes off
 *   pitchBend(-1..1, when)   (range: state.bendRange semitones, default 2)
 *   getState() → {v:1, type:'dx7', voice, gain, bendRange, mono, wheel, breath, foot, at}   setState(obj|JSON)
 *   getParam(path) / setParam(path, value)   paths: 'algorithm', 'lfoSpeed', 'pitchLevels.2', 'name',
 *     'op1.output', 'op3.rates.0', 'gain', 'bendRange', 'mono', 'wheel.range', 'wheel.amp', …
 *   mountEditor(el) → {destroy(), element, refresh()}   on(type, fn) → off()   types: change | state | note | cc
 *   activeVoices · output (GainNode, stereo, → opts.output) · dispose()
 *   flush() → Promise: resolves when the worklet holds every message sent so far. In an
 *     OfflineAudioContext: init, loadVoice, schedule notes, await flush(), then startRendering().
 *   aftertouch(v01, when) (channel pressure, routed by state.at like the wheel; off by default)
 *   wheel / breath / foot / at = {range 0-99, pitch, amp, eg} — the DX7 FUNCTION-mode controller assigns
 *     (defaults: wheel 99 pitch+amp, breath 99 amp, foot and aftertouch off). gain 1 = Dexed's level.
 *
 * ENGINE (in the worklet) — msfa, as extended in Dexed's msfa/ directory:
 *   6 operators, the 32 msfa algorithm routings (feedback on the op msfa puts it on; algorithms 4 and 6
 *   use OP6 self-feedback exactly like msfa/Dexed, not the DX7's 3- and 2-op loops), the DX7 EG with
 *   msfa's rate → increment and level → microstep tables, the attack curve, Dexed's "accurate
 *   envelope" hold timings, output level table, keyboard level scaling (4 curves, break point, depths),
 *   keyboard rate scaling, velocity sensitivity, amplitude mod sensitivity, LFO (6 waves incl. S/H,
 *   speed, delay, PMD, AMD, key sync), pitch mod sensitivity, pitch EG, ratio/fixed oscillators with
 *   coarse/fine/detune (Dexed's measured detune curve), osc key sync, transpose, mono/poly.
 *   Rendered in msfa's 64-sample blocks (EG/LFO/pitch per block, gain ramped per sample), two per render
 *   quantum. Notes, CCs and bends carry AudioContext times; they queue inside the worklet and are applied
 *   on the sample clock (note-ons start at their exact sample, everything else at the 64-sample block
 *   that contains it), so they are immune to main-thread stalls. Stolen voices fade out over 4 ms on
 *   a spare voice while the new note starts clean. Any sample rate: frequency, EG, LFO and pitch-EG
 *   tables are built for the context rate (EG increments are scaled from 44.1 kHz the way Dexed does).
 *   Output level matches Dexed's (a full-level carrier peaks at 0.125); state.gain scales it.
 *
 * LICENCE / PROVENANCE
 *   The synthesis engine below (the DX7_WORKLET function: tables, Env, PitchEnv, Lfo, the operator
 *   kernels, the algorithm table, scaling functions and the per-note computation) is a JavaScript port
 *   of msfa — https://github.com/google/music-synthesizer-for-android — and of the msfa/ files in
 *   Dexed — https://github.com/asb2m10/dexed/tree/master/source/msfa — all of which carry this notice:
 *
 *     Copyright 2012 Google Inc.  Copyright 2016-2025 Pascal Gauthier.  Copyright 2019 Jean Pierre Cimalando.
 *     Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except
 *     in compliance with the License. You may obtain a copy of the License at
 *         http://www.apache.org/licenses/LICENSE-2.0
 *     Unless required by applicable law or agreed to in writing, software distributed under the License
 *     is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
 *     or implied. See the License for the specific language governing permissions and limitations
 *     under the License.
 *
 *   Changes from msfa: ported to JavaScript (floating-point operator kernels and gain, integer phase
 *   and EG), worklet event queue, voice pool with steal fades, sample-accurate onsets, live parameter
 *   update, the accurate-envelope hold scaled the other way round for rates above 44.1 kHz.
 *   Voice allocation / mono / sustain logic, the SysEx parser and the editor are original to this file.
 *   No code from Dexed's GPL-3 plugin sources is used.
 */
(function () {
"use strict";

// ═════════════════════════════════════════════════════════════════════════════════════════════
// The worklet. Self-contained: it is stringified and added as an AudioWorklet module, so it must
// not reference anything outside its own body.
// ═════════════════════════════════════════════════════════════════════════════════════════════
function DX7_WORKLET() {
  'use strict';
  const N = 64;                       // msfa block (LG_N = 6)
  const SR = sampleRate;
  const Q24 = 16777216;
  const INV14 = 1 / 16384;
  const LEVEL_THRESH = 1120 / Q24;    // msfa kLevelThresh, as a linear gain
  const LEVEL_FLOOR = Q24 * (14 + Math.log2(LEVEL_THRESH));   // the EG level that gives that gain
  const FADE = Math.max(32, Math.round(0.004 * SR));
  const SPARE = 8;

  // ── tables (msfa / Dexed msfa, Apache-2.0) ───────────────────────────────────────────
  const SIN = new Float64Array(2048);           // interleaved [dy, y] (msfa SIN_DELTA), Q24
  for (let i = 0; i < 1024; i++) SIN[2 * i + 1] = Math.round(Math.sin(2 * Math.PI * i / 1024) * Q24);
  for (let i = 0; i < 1024; i++) SIN[2 * i] = SIN[(2 * i + 3) & 2047] - SIN[2 * i + 1];

  const ALG = [
    [0xc1, 0x11, 0x11, 0x14, 0x01, 0x14], [0x01, 0x11, 0x11, 0x14, 0xc1, 0x14], [0xc1, 0x11, 0x14, 0x01, 0x11, 0x14],
    [0xc1, 0x11, 0x94, 0x01, 0x11, 0x14], [0xc1, 0x14, 0x01, 0x14, 0x01, 0x14], [0xc1, 0x94, 0x01, 0x14, 0x01, 0x14],
    [0xc1, 0x11, 0x05, 0x14, 0x01, 0x14], [0x01, 0x11, 0xc5, 0x14, 0x01, 0x14], [0x01, 0x11, 0x05, 0x14, 0xc1, 0x14],
    [0x01, 0x05, 0x14, 0xc1, 0x11, 0x14], [0xc1, 0x05, 0x14, 0x01, 0x11, 0x14], [0x01, 0x05, 0x05, 0x14, 0xc1, 0x14],
    [0xc1, 0x05, 0x05, 0x14, 0x01, 0x14], [0xc1, 0x05, 0x11, 0x14, 0x01, 0x14], [0x01, 0x05, 0x11, 0x14, 0xc1, 0x14],
    [0xc1, 0x11, 0x02, 0x25, 0x05, 0x14], [0x01, 0x11, 0x02, 0x25, 0xc5, 0x14], [0x01, 0x11, 0x11, 0xc5, 0x05, 0x14],
    [0xc1, 0x14, 0x14, 0x01, 0x11, 0x14], [0x01, 0x05, 0x14, 0xc1, 0x14, 0x14], [0x01, 0x14, 0x14, 0xc1, 0x14, 0x14],
    [0xc1, 0x14, 0x14, 0x14, 0x01, 0x14], [0xc1, 0x14, 0x14, 0x01, 0x14, 0x04], [0xc1, 0x14, 0x14, 0x14, 0x04, 0x04],
    [0xc1, 0x14, 0x14, 0x04, 0x04, 0x04], [0xc1, 0x05, 0x14, 0x01, 0x14, 0x04], [0x01, 0x05, 0x14, 0xc1, 0x14, 0x04],
    [0x04, 0xc1, 0x11, 0x14, 0x01, 0x14], [0xc1, 0x14, 0x01, 0x14, 0x04, 0x04], [0x04, 0xc1, 0x11, 0x14, 0x04, 0x04],
    [0xc1, 0x14, 0x04, 0x04, 0x04, 0x04], [0xc4, 0x04, 0x04, 0x04, 0x04, 0x04],
  ];
  // per algorithm, per op (OP6 first): in bus, out bus, add, fb; and which ops are carriers
  const A_IN = [], A_OUT = [], A_ADD = [], A_FB = [], A_CAR = [];
  for (let a = 0; a < 32; a++) {
    A_IN.push(ALG[a].map(f => (f >> 4) & 3)); A_OUT.push(ALG[a].map(f => f & 3));
    A_ADD.push(ALG[a].map(f => (f & 4) !== 0)); A_FB.push(ALG[a].map(f => (f & 0xc0) === 0xc0));
    A_CAR.push(ALG[a].map(f => (f & 3) === 0));
  }
  const COARSE = [
    -16777216, 0, 16777216, 26591258, 33554432, 38955489, 43368474, 47099600,
    50331648, 53182516, 55732705, 58039632, 60145690, 62083076, 63876816,
    65546747, 67108864, 68576247, 69959732, 71268397, 72509921, 73690858,
    74816848, 75892776, 76922906, 77910978, 78860292, 79773775, 80654032,
    81503396, 82323963, 83117622];
  const VEL = [
    0, 70, 86, 97, 106, 114, 121, 126, 132, 138, 142, 148, 152, 156, 160, 163,
    166, 170, 173, 174, 178, 181, 184, 186, 189, 190, 194, 196, 198, 200, 202,
    205, 206, 209, 211, 214, 216, 218, 220, 222, 224, 225, 227, 229, 230, 232,
    233, 235, 237, 238, 240, 241, 242, 243, 244, 246, 246, 248, 249, 250, 251,
    252, 253, 254];
  const EXP_SCALE = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 14, 16, 19, 23, 27, 33, 39, 47, 56, 66,
    80, 94, 110, 126, 142, 158, 174, 190, 206, 222, 238, 250];
  const PMS_TAB = [0, 10, 20, 33, 55, 92, 153, 255];
  const AMS_TAB = [0, 4342338, 7171437, 16777216];
  const LEVEL_LUT = [0, 5, 9, 13, 17, 20, 23, 25, 27, 29, 31, 33, 35, 37, 39, 41, 42, 43, 45, 46];
  const STATICS = [
    1764000, 1764000, 1411200, 1411200, 1190700, 1014300, 992250,
    882000, 705600, 705600, 584325, 507150, 502740, 441000, 418950,
    352800, 308700, 286650, 253575, 220500, 220500, 176400, 145530,
    145530, 125685, 110250, 110250, 88200, 88200, 74970, 61740,
    61740, 55125, 48510, 44100, 37485, 31311, 30870, 27562, 27562,
    22050, 18522, 17640, 15435, 14112, 13230, 11025, 9261, 9261, 7717,
    6615, 6615, 5512, 5512, 4410, 3969, 3969, 3439, 2866, 2690, 2249,
    1984, 1896, 1808, 1411, 1367, 1234, 1146, 926, 837, 837, 705,
    573, 573, 529, 441, 441];
  const LFO_SRC = [
    0.062541, 0.125031, 0.312393, 0.437120, 0.624610, 0.750694, 0.936330, 1.125302, 1.249609, 1.436782,
    1.560915, 1.752081, 1.875117, 2.062494, 2.247191, 2.374451, 2.560492, 2.686728, 2.873976, 2.998950,
    3.188013, 3.369840, 3.500175, 3.682224, 3.812065, 4.000800, 4.186202, 4.310716, 4.501260, 4.623209,
    4.814636, 4.930480, 5.121901, 5.315191, 5.434783, 5.617346, 5.750431, 5.946717, 6.062811, 6.248438,
    6.431695, 6.564264, 6.749460, 6.868132, 7.052186, 7.250580, 7.375719, 7.556294, 7.687577, 7.877738,
    7.993605, 8.181967, 8.372405, 8.504848, 8.685079, 8.810573, 8.986341, 9.122423, 9.300595, 9.500285,
    9.607994, 9.798158, 9.950249, 10.117361, 11.251125, 11.384335, 12.562814, 13.676149, 13.904338, 15.092062,
    16.366612, 16.638935, 17.869907, 19.193858, 19.425019, 20.833333, 21.034918, 22.502250, 24.003841, 24.260068,
    25.746653, 27.173913, 27.578599, 29.052876, 30.693677, 31.191516, 32.658393, 34.317090, 34.674064, 36.416606,
    38.197097, 38.550501, 40.387722, 40.749796, 42.625746, 44.326241, 44.883303, 46.772685, 48.590865, 49.261084];
  const PE_RATE = [
    1, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 10, 10, 11, 11, 12,
    12, 13, 13, 14, 14, 15, 16, 16, 17, 18, 18, 19, 20, 21, 22, 23, 24,
    25, 26, 27, 28, 30, 31, 33, 34, 36, 37, 38, 39, 41, 42, 44, 46, 47,
    49, 51, 53, 54, 56, 58, 60, 62, 64, 66, 68, 70, 72, 74, 76, 79, 82,
    85, 88, 91, 94, 98, 102, 106, 110, 115, 120, 125, 130, 135, 141, 147,
    153, 159, 165, 171, 178, 185, 193, 202, 211, 232, 243, 254, 255];
  const PE_TAB = [
    -128, -116, -104, -95, -85, -76, -68, -61, -56, -52, -49, -46, -43,
    -41, -39, -37, -35, -33, -32, -31, -30, -29, -28, -27, -26, -25, -24,
    -23, -22, -21, -20, -19, -18, -17, -16, -15, -14, -13, -12, -11, -10,
    -9, -8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
    11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27,
    28, 29, 30, 31, 32, 33, 34, 35, 38, 40, 43, 46, 49, 53, 58, 65, 73,
    82, 92, 103, 115, 127];

  const EG_SR_MULT = 44100 / SR;                                  // Dexed Env::sr_multiplier
  const PE_UNIT = Math.trunc(N * Q24 / (21.3 * SR) + 0.5);        // PitchEnv::unit_
  const LFO_UNIT = Math.trunc(N * 25190424 / SR + 0.5);           // Lfo::unit_
  const LFO_RATIO = Math.trunc(4437500000 * N / SR);              // Lfo::lforatio_

  const scaleOutLevel = ol => (ol >= 20 ? 28 + ol : LEVEL_LUT[ol]);
  function scaleVelocity(vel, sens) {
    const v = VEL[Math.max(0, Math.min(127, vel)) >> 1] - 239;
    return ((sens * v + 7) >> 3) << 4;
  }
  function scaleRate(note, sens) {
    const x = Math.min(31, Math.max(0, Math.trunc(note / 3) - 7));
    return (sens * x) >> 3;
  }
  function scaleCurve(group, depth, curve) {
    let s;
    if (curve === 0 || curve === 3) s = (group * depth * 329) >> 12;
    else s = (EXP_SCALE[Math.min(group, EXP_SCALE.length - 1)] * depth * 329) >> 15;
    return curve < 2 ? -s : s;
  }
  function scaleLevel(note, bp, ld, rd, lc, rc) {
    const off = note - bp - 17;
    return off >= 0 ? scaleCurve(Math.trunc((off + 1) / 3), rd, rc) : scaleCurve(Math.trunc(-(off - 1) / 3), ld, lc);
  }
  function oscFreq(note, mode, coarse, fine, detune) {
    let lf;
    if (mode === 0) {
      lf = 50857777 + 1398101 * note;                              // midinote_to_logfreq
      const dr = 0.0209 * Math.exp(-0.396 * (lf / Q24)) / 7;       // Dexed's measured detune
      lf = Math.trunc(lf + dr * lf * (detune - 7));
      lf += COARSE[coarse & 31];
      if (fine) lf += Math.floor(24204406.323123 * Math.log(1 + 0.01 * fine) + 0.5);
    } else {
      lf = (4458616 * ((coarse & 3) * 100 + fine)) >> 3;
      if (detune > 7) lf += 13457 * (detune - 7);
    }
    return lf;
  }
  // Freqlut::lookup — log frequency (Q24 octaves) → Q24 phase increment per sample
  const FREQ_K = Q24 / SR;
  const freqOf = lf => Math.trunc(Math.pow(2, lf / Q24) * FREQ_K);

  // ── EG (msfa Env, with Dexed's ACCURATE_ENVELOPE holds) ──────────────────────────────
  class Env {
    constructor() {
      this.rates = [0, 0, 0, 0]; this.levels = [0, 0, 0, 0];
      this.outlevel = 0; this.rs = 0; this.level = 0; this.target = 0;
      this.rising = false; this.ix = 4; this.inc = 0; this.down = true; this.sc = 0; this.on = false;
    }
    init(P, off, ol, rs) {
      for (let i = 0; i < 4; i++) { this.rates[i] = P[off + i]; this.levels[i] = P[off + 4 + i]; }
      this.outlevel = ol; this.rs = rs; this.level = 0; this.down = true; this.on = true;
      this.advance(0);
    }
    update(P, off, ol, rs) {           // live edit: keep the stage and level, retarget
      for (let i = 0; i < 4; i++) { this.rates[i] = P[off + i]; this.levels[i] = P[off + 4 + i]; }
      this.outlevel = ol; this.rs = rs;
      if (this.ix < 4) this.advance(this.down && this.ix === 3 ? 2 : this.ix);
    }
    tick() {
      if (this.sc) {
        this.sc -= N;
        if (this.sc <= 0) { this.sc = 0; this.advance(this.ix + 1); }
      }
      if (this.ix < 3 || (this.ix < 4 && !this.down)) {
        if (this.sc) { /* holding */ }
        else if (this.rising) {
          if (this.level < 112459776) this.level = 112459776;                 // jumptarget 1716 << 16
          this.level += ((285212672 - this.level) >> 24) * this.inc;          // (17 << 24)
          if (this.level >= this.target) { this.level = this.target; this.advance(this.ix + 1); }
        } else {
          this.level -= this.inc;
          if (this.level <= this.target) { this.level = this.target; this.advance(this.ix + 1); }
        }
      }
      return this.level;
    }
    keydown(d) { if (this.down !== d) { this.down = d; this.advance(d ? 0 : 3); } }
    advance(ix) {
      this.ix = ix;
      if (ix >= 4) return;
      const nl = this.levels[ix];
      let al = ((scaleOutLevel(nl) >> 1) << 6) + this.outlevel - 4256;
      if (al < 16) al = 16;
      this.target = al * 65536;
      this.rising = this.target > this.level;
      let qr = ((this.rates[ix] * 41) >> 6) + this.rs;
      if (qr > 63) qr = 63;
      if (this.target === this.level || (ix === 0 && nl === 0)) {
        let sr = this.rates[ix] + this.rs;
        if (sr > 99) sr = 99;
        let sc = sr < 77 ? STATICS[sr] : 20 * (99 - sr);
        if (sr < 77 && ix === 0 && nl === 0) sc = Math.trunc(sc / 20);
        this.sc = Math.trunc(sc * SR / 44100);      // 44.1 kHz samples → samples at this rate
      } else this.sc = 0;
      this.inc = Math.trunc(((4 + (qr & 3)) << (8 + (qr >> 2))) * EG_SR_MULT);
    }
    active() { return this.on && (this.ix < 4 || this.levels[3] > 0); }
  }

  // ── pitch EG (msfa PitchEnv) ─────────────────────────────────────────────────────────
  class PitchEnv {
    constructor() { this.rates = [0, 0, 0, 0]; this.levels = [50, 50, 50, 50]; this.level = 0; this.target = 0; this.rising = false; this.ix = 4; this.inc = 0; this.down = true; }
    set(P, ro, lo) {
      for (let i = 0; i < 4; i++) { this.rates[i] = P[ro + i]; this.levels[i] = P[lo + i]; }
      this.level = PE_TAB[this.levels[3]] * 524288;
      this.down = true;
      this.advance(0);
    }
    update(P, ro, lo) {
      for (let i = 0; i < 4; i++) { this.rates[i] = P[ro + i]; this.levels[i] = P[lo + i]; }
      if (this.ix < 4) this.advance(this.ix);
    }
    tick() {
      if (this.ix < 3 || (this.ix < 4 && !this.down)) {
        if (this.rising) {
          this.level += this.inc;
          if (this.level >= this.target) { this.level = this.target; this.advance(this.ix + 1); }
        } else {
          this.level -= this.inc;
          if (this.level <= this.target) { this.level = this.target; this.advance(this.ix + 1); }
        }
      }
      return this.level;
    }
    keydown(d) { if (this.down !== d) { this.down = d; this.advance(d ? 0 : 3); } }
    advance(ix) {
      this.ix = ix;
      if (ix >= 4) return;
      this.target = PE_TAB[this.levels[ix]] * 524288;      // << 19
      this.rising = this.target > this.level;
      this.inc = PE_RATE[this.rates[ix]] * PE_UNIT;
    }
  }

  // ── LFO (msfa Lfo, one per synth like the DX7) ───────────────────────────────────────
  class Lfo {
    constructor() { this.phase = 0; this.delta = 0; this.wave = 0; this.rand = 0; this.sync = false; this.ds = 0; this.di = 0; this.di2 = 0; }
    reset(P) {           // P[137..142]: speed delay pmd amd sync wave
      this.delta = Math.trunc(LFO_SRC[P[137]] * LFO_RATIO);
      let a = 99 - P[138];
      if (a === 99) { this.di = 4294967295; this.di2 = 4294967295; }
      else {
        a = (16 + (a & 15)) << (1 + (a >> 4));
        this.di = LFO_UNIT * a;
        a &= 0xff80; a = Math.max(0x80, a);
        this.di2 = LFO_UNIT * a;
      }
      this.wave = P[142]; this.sync = P[141] !== 0;
    }
    sample() {
      const ph = this.phase = (this.phase + this.delta) >>> 0;
      switch (this.wave) {
        case 0: { let x = ph >>> 7; if (ph >>> 31) x = ~x; return x & 0xFFFFFF; }      // triangle
        case 1: return ((~ph ^ 0x80000000) >>> 8);                                       // saw down
        case 2: return ((ph ^ 0x80000000) >>> 8);                                        // saw up
        case 3: return ((~ph) >>> 7) & 0x1000000;                                        // square
        case 4: { const p = ph >>> 8, ix = (p >> 13) & 2046; return 8388608 + Math.trunc((SIN[ix + 1] + SIN[ix] * (p & 16383) * INV14) / 2); }
        case 5: if (ph < this.delta) this.rand = (this.rand * 179 + 17) & 0xff; return ((this.rand ^ 0x80) + 1) * 65536;
      }
      return 8388608;
    }
    delay() {
      const d = this.ds + (this.ds < 2147483648 ? this.di : this.di2);
      if (d > 4294967295) return Q24;
      this.ds = d;
      return d < 2147483648 ? 0 : Math.floor(d / 128) & 0xFFFFFF;
    }
    keydown() { if (this.sync) this.phase = 2147483647; this.ds = 0; }
  }

  // ── operator kernels (msfa FmOpKernel; float gain, integer Q24 phase) ────────────────
  function kMod(out, inp, s, e, phase, freq, g1, g2, add) {
    const dg = (g2 - g1) / (e - s); let g = g1;
    if (add) for (let i = s; i < e; i++) {
      g += dg; const p = (phase + inp[i]) | 0, ix = (p >> 13) & 2046;
      out[i] += (SIN[ix + 1] + SIN[ix] * (p & 16383) * INV14) * g; phase = (phase + freq) | 0;
    } else for (let i = s; i < e; i++) {
      g += dg; const p = (phase + inp[i]) | 0, ix = (p >> 13) & 2046;
      out[i] = (SIN[ix + 1] + SIN[ix] * (p & 16383) * INV14) * g; phase = (phase + freq) | 0;
    }
  }
  function kPure(out, s, e, phase, freq, g1, g2, add) {
    const dg = (g2 - g1) / (e - s); let g = g1;
    if (add) for (let i = s; i < e; i++) {
      g += dg; const ix = (phase >> 13) & 2046;
      out[i] += (SIN[ix + 1] + SIN[ix] * (phase & 16383) * INV14) * g; phase = (phase + freq) | 0;
    } else for (let i = s; i < e; i++) {
      g += dg; const ix = (phase >> 13) & 2046;
      out[i] = (SIN[ix + 1] + SIN[ix] * (phase & 16383) * INV14) * g; phase = (phase + freq) | 0;
    }
  }
  function kFb(out, s, e, phase, freq, g1, g2, fb, fbScale, add) {
    const dg = (g2 - g1) / (e - s); let g = g1, y0 = fb[0], y = fb[1];
    for (let i = s; i < e; i++) {
      g += dg;
      const p = (phase + Math.floor((y0 + y) * fbScale)) | 0, ix = (p >> 13) & 2046;
      y0 = y;
      y = (SIN[ix + 1] + SIN[ix] * (p & 16383) * INV14) * g;
      if (add) out[i] += y; else out[i] = y;
      phase = (phase + freq) | 0;
    }
    fb[0] = y0; fb[1] = y;
  }

  // ── one note (msfa Dx7Note) ──────────────────────────────────────────────────────────
  const BUS1 = new Float64Array(N), BUS2 = new Float64Array(N);
  class Voice {
    constructor() {
      this.env = [new Env(), new Env(), new Env(), new Env(), new Env(), new Env()];
      this.penv = new PitchEnv();
      this.phase = new Int32Array(6); this.gain = new Float64Array(6); this.lvl = new Float64Array(6);
      this.base = new Float64Array(6); this.mode = new Uint8Array(6); this.ams = new Float64Array(6);
      this.fb = new Float64Array(2); this.fbShift = 16; this.alg = 0; this.pmd = 0; this.pms = 0; this.amd = 0;
      this.out = new Float64Array(N);
      this.key = -1; this.ch = 0; this.note = -1; this.vel = 0;
      this.down = false; this.sus = false; this.seq = 0; this.start = 0; this.fade = 0; this.done = false;
    }
    setup(P, note, vel) {
      this.note = note; this.vel = vel;
      for (let op = 0; op < 6; op++) {
        const off = op * 21;
        let ol = scaleOutLevel(P[off + 16]);
        ol += scaleLevel(note, P[off + 8], P[off + 9], P[off + 10], P[off + 11], P[off + 12]);
        ol = Math.min(127, ol) << 5;
        ol += scaleVelocity(vel, P[off + 15]);
        ol = Math.max(0, ol);
        this.env[op].init(P, off, ol, scaleRate(note, P[off + 13]));
        this.mode[op] = P[off + 17];
        this.base[op] = oscFreq(note, P[off + 17], P[off + 18], P[off + 19], P[off + 20]);
        this.ams[op] = AMS_TAB[P[off + 14] & 3];
      }
      this.penv.set(P, 126, 130);
      this.globals(P);
      this.done = false; this.fade = 0;
    }
    globals(P) {
      this.alg = P[134] & 31;
      this.fbShift = P[135] ? 8 - P[135] : 16;
      this.pmd = (P[139] * 165) >> 6;
      this.pms = PMS_TAB[P[143] & 7];
      this.amd = (P[140] * 165) >> 6;
    }
    update(P) {            // live patch edit (Dexed's Dx7Note::update, keeping EG stages)
      for (let op = 0; op < 6; op++) {
        const off = op * 21;
        let ol = scaleOutLevel(P[off + 16]);
        ol += scaleLevel(this.note, P[off + 8], P[off + 9], P[off + 10], P[off + 11], P[off + 12]);
        ol = Math.min(127, ol) << 5;
        ol += scaleVelocity(this.vel, P[off + 15]);
        ol = Math.max(0, ol);
        this.env[op].update(P, off, ol, scaleRate(this.note, P[off + 13]));
        this.mode[op] = P[off + 17];
        this.base[op] = oscFreq(this.note, P[off + 17], P[off + 18], P[off + 19], P[off + 20]);
        this.ams[op] = AMS_TAB[P[off + 14] & 3];
      }
      this.penv.update(P, 126, 130);
      this.globals(P);
    }
    legato(P, note) {      // mono legato: new pitch, envelopes carry on (Dexed transferState)
      this.note = note;
      for (let op = 0; op < 6; op++) { const off = op * 21; this.base[op] = oscFreq(note, P[off + 17], P[off + 18], P[off + 19], P[off + 20]); }
    }
    oscSync() { for (let op = 0; op < 6; op++) { this.phase[op] = 0; this.gain[op] = 0; } }
    keyup() { for (let op = 0; op < 6; op++) this.env[op].keydown(false); this.penv.keydown(false); }
    playing() {
      const car = A_CAR[this.alg];
      for (let op = 0; op < 6; op++) if (car[op] && this.env[op].active()) return true;
      return false;
    }
    silent() {             // released and every carrier below msfa's render threshold
      if (this.down || this.sus) return false;
      const car = A_CAR[this.alg];
      for (let op = 0; op < 6; op++) {
        if (!car[op]) continue;
        const e = this.env[op];       // EG level (before amp mod) at msfa's floor and not rising again
        if (e.ix < 3 || e.level >= LEVEL_FLOOR || (e.ix === 3 && e.target > e.level)) return false;
      }
      return true;
    }
    compute(lfoVal, lfoDelay, C, mix, b, cnt) {
      // pitch
      const senslfo = this.pms * (lfoVal - 8388608);
      const pm1 = Math.abs(Math.floor(this.pmd * lfoDelay * senslfo / 549755813888));
      const pm2 = Math.abs(Math.floor(C.pitchMod * senslfo / 16384));
      let pmod = Math.max(pm1, pm2);
      pmod = this.penv.tick() + (senslfo < 0 ? -pmod : pmod);
      const pbase = C.pb;
      pmod += pbase;
      // amplitude mod
      const lv = Q24 - lfoVal;
      let a1 = Math.floor(this.amd * lfoDelay / 256);
      a1 = Math.floor(a1 * lv / Q24);
      const a2 = Math.floor(C.ampMod * lv / 128);
      let amd = Math.max(a1, a2);
      amd = Math.max(Q24 - (C.egMod + 1) * 131072, amd);
      // per-op level and frequency
      for (let op = 0; op < 6; op++) {
        let level = this.env[op].tick();
        if (this.ams[op] !== 0) {
          const sensamp = Math.floor(amd * this.ams[op] / Q24);
          const pt = Math.trunc(Math.exp(sensamp / 262144 * 0.07 + 12.2));
          level -= Math.floor(level * pt * 16 / 268435456);
        }
        this.lvl[op] = level;
      }
      // FmCore::render
      const s = this.start, e = cnt, out = this.out;
      this.start = 0;
      out.fill(0);
      const ain = A_IN[this.alg], aout = A_OUT[this.alg], aadd = A_ADD[this.alg], afb = A_FB[this.alg];
      let h0 = true, h1 = false, h2 = false;
      const fbScale = 1 / (1 << (this.fbShift + 1));
      for (let op = 0; op < 6; op++) {
        const inb = ain[op], outb = aout[op];
        let add = aadd[op];
        const freq = freqOf(this.base[op] + (this.mode[op] ? pbase : pmod));
        const g1 = this.gain[op], g2 = Math.pow(2, this.lvl[op] / Q24 - 14);
        this.gain[op] = g2;
        const phase = this.phase[op];
        if (g1 >= LEVEL_THRESH || g2 >= LEVEL_THRESH) {
          const dst = outb === 0 ? out : outb === 1 ? BUS1 : BUS2;
          const has = outb === 0 ? h0 : outb === 1 ? h1 : h2;
          if (!has) add = false;
          const inHas = inb === 1 ? h1 : inb === 2 ? h2 : false;
          if (inb === 0 || !inHas) {
            if (afb[op] && this.fbShift < 16) kFb(dst, s, e, phase, freq, g1, g2, this.fb, fbScale, add);
            else kPure(dst, s, e, phase, freq, g1, g2, add);
          } else kMod(dst, inb === 1 ? BUS1 : BUS2, s, e, phase, freq, g1, g2, add);
          if (outb === 0) h0 = true; else if (outb === 1) h1 = true; else h2 = true;
        } else if (!add) {
          if (outb === 1) h1 = false; else if (outb === 2) h2 = false;
        }
        this.phase[op] = (phase + freq * (e - s)) | 0;
      }
      // Dexed's per-voice output conversion: >> 28 with a clip at ±1
      if (this.fade > 0) {
        for (let i = s; i < e; i++) {
          let v = out[i] / 268435456; v = v > 1 ? 1 : v < -1 ? -1 : v;
          const g = this.fade > 0 ? this.fade / FADE : 0;
          if (this.fade > 0) this.fade--;
          mix[b + i] += v * g;
        }
        if (this.fade <= 0) this.done = true;
      } else {
        for (let i = s; i < e; i++) { let v = out[i] / 268435456; v = v > 1 ? 1 : v < -1 ? -1 : v; mix[b + i] += v; }
        if (!this.playing() || this.silent()) this.done = true;
      }
    }
  }

  const clampI = (v, lo, hi) => (v < lo ? lo : v > hi ? hi : v | 0);
  function modCfg(c) { c = c || {}; return { range: clampI(+c.range || 0, 0, 99), pitch: !!c.pitch, amp: !!c.amp, eg: !!c.eg }; }

  class DX7Processor extends AudioWorkletProcessor {
    constructor(opts) {
      super();
      const po = (opts && opts.processorOptions) || {};
      this.maxVoices = clampI(po.maxVoices || 16, 1, 64);
      this.free = [];
      for (let i = 0; i < this.maxVoices + SPARE; i++) this.free.push(new Voice());
      this.active = [];
      this.P = new Int32Array(156);
      this.lfo = new Lfo();
      this.q = [];
      this.seq = 0;
      this.mono = false; this.stack = []; this.monoV = null;
      this.sustain = false;
      this.cc = { wheel: 0, breath: 0, foot: 0, at: 0 };
      this.mod = { wheel: modCfg({ range: 99, pitch: true, amp: true }), breath: modCfg(), foot: modCfg(), at: modCfg() };
      this.C = { pitchMod: 0, ampMod: 0, egMod: 127, pb: 0 };
      this.bend = 0; this.bendRange = 2;
      this.vol = 1; this.volNow = 1;
      this.dead = false; this.stTick = 0; this.lastN = -1;
      if (po.patch) this.setPatch(po.patch, false);
      if (po.cfg) this.config(po.cfg);
      this.port.onmessage = e => this.onMsg(e.data);
    }
    setPatch(arr, live) {
      for (let i = 0; i < 155 && i < arr.length; i++) this.P[i] = arr[i] | 0;
      this.P[155] = 0x3f;
      this.lfo.reset(this.P);
      if (live) for (const v of this.active) if (!v.fade) v.update(this.P);
    }
    config(c) {
      if (c.maxVoices != null) {
        this.maxVoices = clampI(c.maxVoices, 1, 64);
        while (this.free.length + this.active.length < this.maxVoices + SPARE) this.free.push(new Voice());
      }
      if (c.bendRange != null) { this.bendRange = Math.max(0, Math.min(24, +c.bendRange || 0)); this.refreshBend(); }
      for (const k of ['wheel', 'breath', 'foot', 'at']) if (c[k]) this.mod[k] = modCfg(c[k]);
      if (c.mono != null && !!c.mono !== this.mono) { this.releaseAll(); this.mono = !!c.mono; this.stack = []; this.monoV = null; }
      this.refreshCtl();
    }
    refreshBend() { this.C.pb = Math.round(this.bend * this.bendRange / 12 * Q24); }
    refreshCtl() {        // Dexed Controllers::refresh
      const C = this.C; C.ampMod = 0; C.pitchMod = 0; C.egMod = 0;
      let eg = false;
      for (const k of ['wheel', 'breath', 'foot', 'at']) {
        const m = this.mod[k], total = Math.trunc(this.cc[k] * 0.01 * m.range);
        if (m.amp) C.ampMod = Math.max(C.ampMod, total);
        if (m.pitch) C.pitchMod = Math.max(C.pitchMod, total);
        if (m.eg) { C.egMod = Math.max(C.egMod, total); eg = true; }
      }
      if (!eg) C.egMod = 127;
    }
    onMsg(m) {
      if (!m) return;
      switch (m.type) {
        case 'b': for (const x of m.list) this.onMsg(x); break;
        case 'ev': this.enqueue(m); break;
        case 'patch': this.setPatch(m.data, m.live !== false); break;
        case 'cfg': this.config(m); break;
        case 'clear': this.q.length = 0; break;
        case 'panic': this.q.length = 0; this.sustain = false; this.stack = []; this.monoV = null; for (const v of this.active) if (!v.fade) { v.fade = Math.min(FADE, 64); v.down = false; v.sus = false; } break;
        case 'ping': this.port.postMessage({ type: 'pong', id: m.id }); break;
        case 'dispose': this.dead = true; this.q.length = 0; break;
      }
    }
    enqueue(m) {
      const f = m.t == null ? -1 : m.t * SR;
      const e = { f, k: m.k, n: m.n | 0, v: m.v, c: m.c | 0 };
      const q = this.q;
      let i = q.length;
      while (i > 0 && q[i - 1].f > f) i--;
      q.splice(i, 0, e);
    }
    runEvents(f0, cnt) {
      const q = this.q, end = f0 + cnt;
      while (q.length && q[0].f < end) {
        const e = q.shift();
        const s = e.f <= f0 ? 0 : Math.min(cnt - 1, Math.floor(e.f - f0));
        switch (e.k) {
          case 'on': this.noteOn(e.n, e.v | 0, e.c, s); break;
          case 'off': this.noteOff(e.n, e.c); break;
          case 'cc': this.ctrl(e.n, e.v | 0); break;
          case 'pb': this.bend = Math.max(-1, Math.min(1, +e.v || 0)); this.refreshBend(); break;
          case 'at': this.cc.at = clampI(e.v, 0, 127); this.refreshCtl(); break;
          case 'alloff': this.releaseAll(); break;
        }
      }
    }
    anyDown() { for (const v of this.active) if (!v.fade && v.down) return true; return false; }
    alloc(key) {
      let live = 0;
      for (const v of this.active) if (!v.fade) live++;
      let victim = null;
      if (live >= this.maxVoices) {
        let best = -1;
        for (const v of this.active) {
          if (v.fade) continue;
          const sc = (v.down || v.sus ? 0 : 2) + (v.key === key ? 1 : 0);
          if (sc > best || (sc === best && v.seq < victim.seq)) { best = sc; victim = v; }
        }
      }
      let nv = this.free.pop() || null;
      if (victim) {
        if (nv) { victim.fade = FADE; victim.down = false; victim.sus = false; }
        else { nv = victim; this.active.splice(this.active.indexOf(victim), 1); nv.stolen = true; }
      }
      if (!nv) {        // every spare is fading: take the quietest fade
        let k = 0;
        for (let i = 1; i < this.active.length; i++) if (this.active[i].fade < this.active[k].fade) k = i;
        nv = this.active.splice(k, 1)[0]; nv.stolen = true;
      }
      return nv;
    }
    startVoice(v, key, ch, vel, s, sync) {
      const note = clampI(key + this.P[144] - 24, 0, 127);
      v.setup(this.P, note, vel);
      v.key = key; v.ch = ch; v.down = true; v.sus = false; v.seq = ++this.seq; v.start = s;
      if (sync) v.oscSync();
      return v;
    }
    noteOn(key, vel, ch, s) {
      if (vel <= 0) return this.noteOff(key, ch);
      if (this.mono) return this.monoOn(key, vel, ch, s);
      for (const v of this.active) if (!v.fade && v.key === key && v.ch === ch && (v.down || v.sus)) { v.down = false; v.sus = false; v.keyup(); }
      const trig = !this.anyDown();
      const v = this.alloc(key);
      const stolen = !!v.stolen; v.stolen = false;
      if (!stolen) for (let op = 0; op < 6; op++) v.gain[op] = 0;
      this.startVoice(v, key, ch, vel, stolen ? 0 : s, this.P[136] && !stolen);
      if (!this.P[136] && !stolen) {           // free-running oscs: share phase with a same-pitch voice
        for (const o of this.active) if (o !== v && !o.fade && o.note === v.note) { v.phase.set(o.phase); break; }
      }
      this.active.push(v);
      if (trig) this.lfo.keydown();
    }
    noteOff(key, ch) {
      if (this.mono) return this.monoOff(key, ch);
      for (const v of this.active) {
        if (!v.fade && v.down && v.key === key && v.ch === ch) {
          v.down = false;
          if (this.sustain) v.sus = true; else v.keyup();
          return;
        }
      }
    }
    monoOn(key, vel, ch, s) {
      const held = this.stack.length > 0;
      this.stack = this.stack.filter(e => !(e.key === key && e.ch === ch));
      this.stack.push({ key, ch, vel });
      let v = this.monoV;
      if (v && (v.done || v.fade || this.active.indexOf(v) < 0)) v = this.monoV = null;
      if (v && (v.down || v.sus) && held) {               // legato
        v.legato(this.P, clampI(key + this.P[144] - 24, 0, 127));
        v.key = key; v.ch = ch; v.down = true; v.sus = false;
        return;
      }
      if (!held) this.lfo.keydown();
      if (v) { this.startVoice(v, key, ch, vel, 0, false); return; }   // still releasing: carry phase + gain
      v = this.alloc(key);
      const stolen = !!v.stolen; v.stolen = false;
      if (!stolen) for (let op = 0; op < 6; op++) v.gain[op] = 0;
      this.startVoice(v, key, ch, vel, stolen ? 0 : s, this.P[136] && !stolen);
      this.active.push(v);
      this.monoV = v;
    }
    monoOff(key, ch) {
      this.stack = this.stack.filter(e => !(e.key === key && e.ch === ch));
      const v = this.monoV;
      if (!v || v.key !== key || v.ch !== ch || !v.down) return;
      if (this.stack.length) {
        const e = this.stack[this.stack.length - 1];
        v.legato(this.P, clampI(e.key + this.P[144] - 24, 0, 127));
        v.key = e.key; v.ch = e.ch;
      } else {
        v.down = false;
        if (this.sustain) v.sus = true; else v.keyup();
      }
    }
    releaseAll() {
      this.sustain = false; this.stack = [];
      for (const v of this.active) if (!v.fade && (v.down || v.sus)) { v.down = false; v.sus = false; v.keyup(); }
    }
    ctrl(n, val) {
      switch (n) {
        case 1: this.cc.wheel = val; this.refreshCtl(); break;
        case 2: this.cc.breath = val; this.refreshCtl(); break;
        case 4: this.cc.foot = val; this.refreshCtl(); break;
        case 7: this.vol = (val / 127) * (val / 127); break;
        case 64: {
          const on = val >= 64;
          if (on === this.sustain) break;
          this.sustain = on;
          if (!on) for (const v of this.active) if (v.sus) { v.sus = false; if (!v.down) v.keyup(); }
          break;
        }
        case 120: this.q.length = 0; this.stack = []; this.monoV = null; this.sustain = false; for (const v of this.active) if (!v.fade) { v.fade = FADE; v.down = false; v.sus = false; } break;
        case 121: this.cc.wheel = this.cc.breath = this.cc.foot = this.cc.at = 0; this.bend = 0; this.refreshBend(); this.refreshCtl();
          if (this.sustain) this.ctrl(64, 0);
          break;
        case 123: this.releaseAll(); break;
      }
    }
    process(inputs, outputs) {
      if (this.dead) return false;
      const out = outputs[0], L = out && out[0];
      if (!L) return true;
      const len = L.length;
      L.fill(0);
      for (let b = 0; b < len; b += N) {
        const cnt = Math.min(N, len - b);
        this.runEvents(currentFrame + b, cnt);
        const lv = this.lfo.sample(), ld = this.lfo.delay();
        const act = this.active;
        for (let i = act.length - 1; i >= 0; i--) {
          const v = act[i];
          v.compute(lv, ld, this.C, L, b, cnt);
          if (v.done) {
            act[i] = act[act.length - 1]; act.pop();
            v.down = false; v.sus = false; v.fade = 0; v.key = -1;
            if (v === this.monoV) this.monoV = null;
            this.free.push(v);
          }
        }
      }
      // CC 7 volume, smoothed over the quantum
      if (this.volNow !== this.vol || this.vol !== 1) {
        const a = this.volNow, d = (this.vol - a) / len;
        for (let i = 0; i < len; i++) L[i] *= a + d * (i + 1);
        this.volNow = this.vol;
      }
      for (let c = 1; c < out.length; c++) out[c].set(L);
      if (++this.stTick >= 8) {
        this.stTick = 0;
        let n = 0; for (const v of this.active) if (!v.fade) n++;
        if (n !== this.lastN) { this.lastN = n; this.port.postMessage({ type: 'st', voices: n }); }
      }
      return true;
    }
  }
  registerProcessor('mm-dx7-synth', DX7Processor);
}

// ═════════════════════════════════════════════════════════════════════════════════════════════
// DX7 — SysEx + voice helpers (main thread)
// ═════════════════════════════════════════════════════════════════════════════════════════════
const clampInt = (v, lo, hi) => { v = Math.round(+v); return !isFinite(v) ? lo : v < lo ? lo : v > hi ? hi : v; };
const isNum = v => typeof v === 'number' && isFinite(v);
const clone = o => JSON.parse(JSON.stringify(o));
const NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
const WAVES = ['TRIANGLE', 'SAW DOWN', 'SAW UP', 'SQUARE', 'SINE', 'S/HOLD'];
const CURVES = ['-LIN', '-EXP', '+EXP', '+LIN'];

const OP_FIELDS = {     // field → [min, max, default]
  breakPoint: [0, 99, 39], leftDepth: [0, 99, 0], rightDepth: [0, 99, 0], leftCurve: [0, 3, 0], rightCurve: [0, 3, 0],
  rateScaling: [0, 7, 0], ams: [0, 3, 0], kvs: [0, 7, 0], output: [0, 99, 0], mode: [0, 1, 0], coarse: [0, 31, 1],
  fine: [0, 99, 0], detune: [0, 14, 7],
};
const VOICE_FIELDS = {
  algorithm: [0, 31, 0], feedback: [0, 7, 0], oscKeySync: [0, 1, 1], lfoSpeed: [0, 99, 35], lfoDelay: [0, 99, 0],
  lfoPmd: [0, 99, 0], lfoAmd: [0, 99, 0], lfoKeySync: [0, 1, 1], lfoWave: [0, 5, 0], pitchModSens: [0, 7, 3], transpose: [0, 48, 24],
};

function defaultOp(output) {
  return { rates: [99, 99, 99, 99], levels: [99, 99, 99, 0], breakPoint: 39, leftDepth: 0, rightDepth: 0, leftCurve: 0, rightCurve: 0,
    rateScaling: 0, ams: 0, kvs: 0, output: output || 0, mode: 0, coarse: 1, fine: 0, detune: 7 };
}
function defaultVoice() {
  return { name: 'INIT VOICE', ops: [defaultOp(99), defaultOp(0), defaultOp(0), defaultOp(0), defaultOp(0), defaultOp(0)],
    pitchRates: [99, 99, 99, 99], pitchLevels: [50, 50, 50, 50], algorithm: 0, feedback: 0, oscKeySync: 1,
    lfoSpeed: 35, lfoDelay: 0, lfoPmd: 0, lfoAmd: 0, lfoKeySync: 1, lfoWave: 0, pitchModSens: 3, transpose: 24 };
}
function cleanName(s) {
  let out = '';
  s = String(s == null ? '' : s);
  for (let i = 0; i < 10; i++) {
    const c = i < s.length ? s.charCodeAt(i) & 0x7F : 32;
    out += String.fromCharCode(c < 32 ? 32 : c);
  }
  return out.replace(/\s+$/, '');
}
function arr4(a, def, lo, hi) {
  const out = [];
  for (let i = 0; i < 4; i++) out.push(clampInt(a && isNum(+a[i]) && a[i] !== null && a[i] !== '' ? a[i] : def[i], lo, hi));
  return out;
}
// Any object (or junk) → a complete voice with every value an in-range integer.
function normalizeVoice(src) {
  const s = src && typeof src === 'object' ? src : {};
  const d = defaultVoice();
  const v = { name: cleanName(typeof s.name === 'string' || typeof s.name === 'number' ? s.name : d.name) };
  const sops = Array.isArray(s.ops) ? s.ops : [];
  v.ops = [];
  for (let i = 0; i < 6; i++) {
    const so = sops[i] && typeof sops[i] === 'object' ? sops[i] : {}, dop = d.ops[i], op = {};
    op.rates = arr4(so.rates, dop.rates, 0, 99);
    op.levels = arr4(so.levels, dop.levels, 0, 99);
    for (const k in OP_FIELDS) { const f = OP_FIELDS[k]; op[k] = clampInt(isNum(+so[k]) && so[k] !== null && so[k] !== '' ? so[k] : dop[k], f[0], f[1]); }
    v.ops.push(op);
  }
  v.pitchRates = arr4(s.pitchRates, d.pitchRates, 0, 99);
  v.pitchLevels = arr4(s.pitchLevels, d.pitchLevels, 0, 99);
  for (const k in VOICE_FIELDS) { const f = VOICE_FIELDS[k]; v[k] = clampInt(isNum(+s[k]) && s[k] !== null && s[k] !== '' ? s[k] : d[k], f[0], f[1]); }
  return v;
}

function checksum(bytes, start = 0, len = bytes.length - start) {
  let sum = 0;
  for (let i = start; i < start + len; i++) sum += bytes[i] & 0x7F;
  return (128 - (sum & 0x7F)) & 0x7F;
}

// 128-byte packed voice (VMEM, inside a 32-voice cartridge). Ops stored OP6 first, 17 bytes each.
function unpackVmem(b, o = 0) {
  const at = i => (o + i < b.length ? b[o + i] & 0x7F : 0);
  const c = (x, mx) => (x > mx ? mx : x);
  const v = { ops: [] };
  for (let i = 0; i < 6; i++) {
    const p = i * 17;
    const op = {
      rates: [c(at(p), 99), c(at(p + 1), 99), c(at(p + 2), 99), c(at(p + 3), 99)],
      levels: [c(at(p + 4), 99), c(at(p + 5), 99), c(at(p + 6), 99), c(at(p + 7), 99)],
      breakPoint: c(at(p + 8), 99), leftDepth: c(at(p + 9), 99), rightDepth: c(at(p + 10), 99),
      leftCurve: at(p + 11) & 3, rightCurve: (at(p + 11) >> 2) & 3,
      rateScaling: at(p + 12) & 7, detune: c((at(p + 12) >> 3) & 15, 14),
      ams: at(p + 13) & 3, kvs: (at(p + 13) >> 2) & 7,
      output: c(at(p + 14), 99),
      mode: at(p + 15) & 1, coarse: (at(p + 15) >> 1) & 31,
      fine: c(at(p + 16), 99),
    };
    v.ops[5 - i] = op;
  }
  v.pitchRates = [c(at(102), 99), c(at(103), 99), c(at(104), 99), c(at(105), 99)];
  v.pitchLevels = [c(at(106), 99), c(at(107), 99), c(at(108), 99), c(at(109), 99)];
  v.algorithm = at(110) & 31;
  v.feedback = at(111) & 7; v.oscKeySync = (at(111) >> 3) & 1;
  v.lfoSpeed = c(at(112), 99); v.lfoDelay = c(at(113), 99); v.lfoPmd = c(at(114), 99); v.lfoAmd = c(at(115), 99);
  v.lfoKeySync = at(116) & 1; v.lfoWave = c((at(116) >> 1) & 7, 5); v.pitchModSens = (at(116) >> 4) & 7;
  v.transpose = c(at(117), 48);
  let name = '';
  for (let k = 0; k < 10; k++) name += String.fromCharCode(Math.max(32, at(118 + k)));
  v.name = cleanName(name);
  return normalizeVoice(v);
}
function packVmem(voice) {
  const v = normalizeVoice(voice), b = new Uint8Array(128);
  for (let i = 0; i < 6; i++) {
    const op = v.ops[5 - i], p = i * 17;
    for (let k = 0; k < 4; k++) { b[p + k] = op.rates[k]; b[p + 4 + k] = op.levels[k]; }
    b[p + 8] = op.breakPoint; b[p + 9] = op.leftDepth; b[p + 10] = op.rightDepth;
    b[p + 11] = (op.leftCurve & 3) | ((op.rightCurve & 3) << 2);
    b[p + 12] = (op.rateScaling & 7) | ((op.detune & 15) << 3);
    b[p + 13] = (op.ams & 3) | ((op.kvs & 7) << 2);
    b[p + 14] = op.output;
    b[p + 15] = (op.mode & 1) | ((op.coarse & 31) << 1);
    b[p + 16] = op.fine;
  }
  for (let k = 0; k < 4; k++) { b[102 + k] = v.pitchRates[k]; b[106 + k] = v.pitchLevels[k]; }
  b[110] = v.algorithm;
  b[111] = (v.feedback & 7) | ((v.oscKeySync & 1) << 3);
  b[112] = v.lfoSpeed; b[113] = v.lfoDelay; b[114] = v.lfoPmd; b[115] = v.lfoAmd;
  b[116] = (v.lfoKeySync & 1) | ((v.lfoWave & 7) << 1) | ((v.pitchModSens & 7) << 4);
  b[117] = v.transpose;
  const nm = v.name.padEnd(10, ' ');
  for (let k = 0; k < 10; k++) b[118 + k] = nm.charCodeAt(k) & 0x7F;
  return b;
}
// 155-byte unpacked voice (VCED, the single-voice dump). Ops stored OP6 first, 21 bytes each.
function voiceFromVced(b, o = 0) {
  const at = i => (o + i < b.length ? b[o + i] & 0x7F : 0);
  const v = { ops: [] };
  for (let i = 0; i < 6; i++) {
    const p = i * 21;
    v.ops[5 - i] = {
      rates: [at(p), at(p + 1), at(p + 2), at(p + 3)], levels: [at(p + 4), at(p + 5), at(p + 6), at(p + 7)],
      breakPoint: at(p + 8), leftDepth: at(p + 9), rightDepth: at(p + 10), leftCurve: at(p + 11), rightCurve: at(p + 12),
      rateScaling: at(p + 13), ams: at(p + 14), kvs: at(p + 15), output: at(p + 16), mode: at(p + 17),
      coarse: at(p + 18), fine: at(p + 19), detune: at(p + 20),
    };
  }
  v.pitchRates = [at(126), at(127), at(128), at(129)];
  v.pitchLevels = [at(130), at(131), at(132), at(133)];
  v.algorithm = at(134); v.feedback = at(135); v.oscKeySync = at(136); v.lfoSpeed = at(137); v.lfoDelay = at(138);
  v.lfoPmd = at(139); v.lfoAmd = at(140); v.lfoKeySync = at(141); v.lfoWave = at(142); v.pitchModSens = at(143); v.transpose = at(144);
  let name = '';
  for (let k = 0; k < 10; k++) name += String.fromCharCode(Math.max(32, at(145 + k)));
  v.name = name;
  return normalizeVoice(v);
}
function voiceToVced(voice) {
  const v = normalizeVoice(voice), b = new Uint8Array(155);
  let i = 0;
  for (let o = 5; o >= 0; o--) {
    const op = v.ops[o];
    for (let k = 0; k < 4; k++) b[i++] = op.rates[k];
    for (let k = 0; k < 4; k++) b[i++] = op.levels[k];
    b[i++] = op.breakPoint; b[i++] = op.leftDepth; b[i++] = op.rightDepth; b[i++] = op.leftCurve; b[i++] = op.rightCurve;
    b[i++] = op.rateScaling; b[i++] = op.ams; b[i++] = op.kvs; b[i++] = op.output; b[i++] = op.mode;
    b[i++] = op.coarse; b[i++] = op.fine; b[i++] = op.detune;
  }
  for (let k = 0; k < 4; k++) b[i++] = v.pitchRates[k];
  for (let k = 0; k < 4; k++) b[i++] = v.pitchLevels[k];
  b[i++] = v.algorithm; b[i++] = v.feedback; b[i++] = v.oscKeySync; b[i++] = v.lfoSpeed; b[i++] = v.lfoDelay;
  b[i++] = v.lfoPmd; b[i++] = v.lfoAmd; b[i++] = v.lfoKeySync; b[i++] = v.lfoWave; b[i++] = v.pitchModSens; b[i++] = v.transpose;
  const nm = v.name.padEnd(10, ' ');
  for (let k = 0; k < 10; k++) b[i++] = nm.charCodeAt(k) & 0x7F;
  return b;
}
function voiceToSysex(voice, ch = 1) {
  const d = voiceToVced(voice), n = ((ch | 0) - 1) & 0x0F, out = new Uint8Array(163);
  out.set([0xF0, 0x43, n, 0x00, 0x01, 0x1B]); out.set(d, 6); out[161] = checksum(d); out[162] = 0xF7;
  return out;
}
function bankToSysex(voices, ch = 1) {
  const n = ((ch | 0) - 1) & 0x0F, out = new Uint8Array(4104);
  out.set([0xF0, 0x43, n, 0x09, 0x20, 0x00]);
  for (let i = 0; i < 32; i++) out.set(packVmem(voices && voices[i] ? voices[i] : defaultVoice()), 6 + i * 128);
  out[4102] = checksum(out, 6, 4096); out[4103] = 0xF7;
  return out;
}
function voiceName(v) {
  const s = v && v.name != null ? String(v.name) : '';
  return s.replace(/\\/g, '¥').replace(/~/g, '→').replace(/\x7F/g, '←').replace(/\s+$/, '') || '(unnamed)';
}

// Parse anything that looks like DX7 voice data.
function parseSysex(input) {
  const b = input instanceof Uint8Array ? input : input instanceof ArrayBuffer ? new Uint8Array(input) : Uint8Array.from(input || []);
  const res = { kind: 'none', voices: [], banks: [], checksums: [], warnings: [], format: '' };
  const addBank = (off, avail, label) => {
    const vs = [];
    for (let i = 0; i < 32; i++) vs.push(unpackVmem(b, off + i * 128));
    if (avail < 4096) res.warnings.push(label + ': truncated (' + avail + ' of 4096 data bytes), missing bytes read as 0');
    res.banks.push(vs); res.voices.push(...vs);
  };
  let i = 0, found = 0;
  while (i < b.length) {
    if (b[i] !== 0xF0) { i++; continue; }
    let end = i + 1;
    while (end < b.length && b[end] !== 0xF7 && !(b[end] === 0xF0)) end++;
    const isYamaha = b[i + 1] === 0x43 && (b[i + 2] & 0x60) === 0;   // sub-status 0 (or 1, tolerated)
    if (isYamaha && b[i + 3] === 0x09 && i + 6 < b.length) {
      // 32-voice VMEM. Data is 7-bit, so a premature F7 / F0 means junk inside; read 4096 regardless.
      const off = i + 6, avail = Math.max(0, Math.min(4096, b.length - off));
      const label = 'bank ' + (res.banks.length + 1);
      if ((b[i + 4] << 7 | b[i + 5]) !== 4096) res.warnings.push(label + ': byte count says ' + (b[i + 4] << 7 | b[i + 5]) + ', reading 4096');
      addBank(off, avail, label);
      if (avail === 4096 && off + 4096 < b.length) {
        const exp = checksum(b, off, 4096), got = b[off + 4096] & 0x7F, ok = exp === got;
        res.checksums.push({ index: res.banks.length - 1, kind: 'bank', ok, expected: exp, got });
        if (!ok) res.warnings.push(label + ': checksum mismatch (expected ' + exp + ', file has ' + got + ') — data used anyway');
      } else res.checksums.push({ index: res.banks.length - 1, kind: 'bank', ok: false, expected: avail === 4096 ? checksum(b, off, 4096) : null, got: null });
      found++;
      i = off + 4096;
      continue;
    }
    if (isYamaha && b[i + 3] === 0x00 && b[i + 4] === 0x01 && b[i + 5] === 0x1B && i + 6 < b.length) {
      const off = i + 6, avail = Math.min(155, b.length - off);
      const v = voiceFromVced(b, off);
      res.voices.push(v);
      if (avail < 155) res.warnings.push('voice ' + res.voices.length + ': truncated');
      if (avail === 155 && off + 155 < b.length) {
        const exp = checksum(b, off, 155), got = b[off + 155] & 0x7F, ok = exp === got;
        res.checksums.push({ index: res.voices.length - 1, kind: 'voice', ok, expected: exp, got });
        if (!ok) res.warnings.push('voice "' + voiceName(v) + '": checksum mismatch — data used anyway');
      }
      found++;
      i = off + 155;
      continue;
    }
    i = Math.max(end, i + 1);
  }
  if (found) {
    res.kind = res.banks.length ? 'bank' : 'voice';
    res.format = res.banks.length ? 'VMEM sysex ×' + res.banks.length + (res.voices.length > res.banks.length * 32 ? ' + VCED' : '') : 'VCED sysex ×' + res.voices.length;
    return res;
  }
  // headerless data
  if (b.length >= 4096 && b[0] !== 0xF0) {
    const nb = Math.floor(b.length / 4096);
    for (let k = 0; k < nb; k++) addBank(k * 4096, 4096, 'bank ' + (k + 1));
    if (b.length % 4096) res.warnings.push((b.length % 4096) + ' trailing bytes ignored');
    res.kind = 'bank'; res.format = 'raw VMEM ×' + nb;
  } else if (b.length === 155 || b.length === 156) {
    res.voices.push(voiceFromVced(b, 0)); res.kind = 'voice'; res.format = 'raw VCED';
  } else if (b.length >= 128 && b.length % 128 === 0 && b[0] !== 0xF0) {
    for (let k = 0; k < b.length / 128; k++) res.voices.push(unpackVmem(b, k * 128));
    res.kind = res.voices.length === 1 ? 'voice' : 'bank'; res.format = 'raw VMEM voices ×' + res.voices.length;
  } else if (b.length >= 4096) {
    // starts with F0 but nothing DX7 inside — Dexed falls back to the first 4096 bytes
    addBank(0, 4096, 'bank 1'); res.kind = 'bank'; res.format = 'unrecognised, read as raw VMEM';
    res.warnings.push('no DX7 dump header found; read the first 4096 bytes as a cartridge');
  } else res.warnings.push('no DX7 voice data found (' + b.length + ' bytes)');
  return res;
}

// ── algorithms (derived from the msfa routing table the engine runs) ───────────────────────
const MSFA_ALG = [
  [0xc1, 0x11, 0x11, 0x14, 0x01, 0x14], [0x01, 0x11, 0x11, 0x14, 0xc1, 0x14], [0xc1, 0x11, 0x14, 0x01, 0x11, 0x14],
  [0xc1, 0x11, 0x94, 0x01, 0x11, 0x14], [0xc1, 0x14, 0x01, 0x14, 0x01, 0x14], [0xc1, 0x94, 0x01, 0x14, 0x01, 0x14],
  [0xc1, 0x11, 0x05, 0x14, 0x01, 0x14], [0x01, 0x11, 0xc5, 0x14, 0x01, 0x14], [0x01, 0x11, 0x05, 0x14, 0xc1, 0x14],
  [0x01, 0x05, 0x14, 0xc1, 0x11, 0x14], [0xc1, 0x05, 0x14, 0x01, 0x11, 0x14], [0x01, 0x05, 0x05, 0x14, 0xc1, 0x14],
  [0xc1, 0x05, 0x05, 0x14, 0x01, 0x14], [0xc1, 0x05, 0x11, 0x14, 0x01, 0x14], [0x01, 0x05, 0x11, 0x14, 0xc1, 0x14],
  [0xc1, 0x11, 0x02, 0x25, 0x05, 0x14], [0x01, 0x11, 0x02, 0x25, 0xc5, 0x14], [0x01, 0x11, 0x11, 0xc5, 0x05, 0x14],
  [0xc1, 0x14, 0x14, 0x01, 0x11, 0x14], [0x01, 0x05, 0x14, 0xc1, 0x14, 0x14], [0x01, 0x14, 0x14, 0xc1, 0x14, 0x14],
  [0xc1, 0x14, 0x14, 0x14, 0x01, 0x14], [0xc1, 0x14, 0x14, 0x01, 0x14, 0x04], [0xc1, 0x14, 0x14, 0x14, 0x04, 0x04],
  [0xc1, 0x14, 0x14, 0x04, 0x04, 0x04], [0xc1, 0x05, 0x14, 0x01, 0x14, 0x04], [0x01, 0x05, 0x14, 0xc1, 0x14, 0x04],
  [0x04, 0xc1, 0x11, 0x14, 0x01, 0x14], [0xc1, 0x14, 0x01, 0x14, 0x04, 0x04], [0x04, 0xc1, 0x11, 0x14, 0x04, 0x04],
  [0xc1, 0x14, 0x04, 0x04, 0x04, 0x04], [0xc4, 0x04, 0x04, 0x04, 0x04, 0x04],
];
const ALGORITHMS = MSFA_ALG.map((row, a) => {
  const bus = [null, [], []], mods = {}, targets = {}, carriers = [];
  let fbOp = 0;
  for (let op = 1; op <= 6; op++) { mods[op] = []; targets[op] = []; }
  for (let k = 0; k < 6; k++) {
    const op = 6 - k, f = row[k], inb = (f >> 4) & 3, outb = f & 3, add = (f & 4) !== 0;
    if (inb) mods[op] = bus[inb].slice();
    if ((f & 0xc0) === 0xc0) fbOp = op;
    if (outb === 0) carriers.push(op);
    else bus[outb] = add ? bus[outb].concat(op) : [op];
  }
  const edges = [];
  for (let op = 1; op <= 6; op++) for (const m of mods[op]) { edges.push([m, op]); targets[m].push(op); }
  carriers.sort((x, y) => x - y);
  const feedback = { op: fbOp, from: fbOp, to: fbOp, loop: [fbOp] };
  if (a === 3) Object.assign(feedback, { from: 4, to: 6, loop: [6, 5, 4], dx7: 'OP4 → OP6 loop on a DX7; msfa/Dexed/FM-1 run it as OP6 self-feedback' });
  if (a === 5) Object.assign(feedback, { from: 5, to: 6, loop: [6, 5], dx7: 'OP5 → OP6 loop on a DX7; msfa/Dexed/FM-1 run it as OP6 self-feedback' });
  return { n: a + 1, carriers, modulators: [1, 2, 3, 4, 5, 6].filter(o => carriers.indexOf(o) < 0), mods, targets, edges, feedback };
});

// ── voice analysis for library listings ────────────────────────────────────────────────────
const sOut = ol => (ol >= 20 ? 28 + ol : [0, 5, 9, 13, 17, 20, 23, 25, 27, 29, 31, 33, 35, 37, 39, 41, 42, 43, 45, 46][ol]);
function opRatio(op) { return op.mode ? 0 : (op.coarse === 0 ? 0.5 : op.coarse) * (1 + op.fine / 100); }
// Brightness: a tiny static render of the voice at C3 with every op held at its envelope level
// `stage` (msfa routing, gains and feedback; no EG/LFO), then spectral centroid ÷ f0 via an FFT.
const BR_N = 2048, BR_SR = 44100, BR_F0 = 261.6256;
function fftCentroid(x) {
  const n = x.length, re = Float64Array.from(x), im = new Float64Array(n);
  for (let i = 1, j = 0; i < n; i++) { let bit = n >> 1; for (; j & bit; bit >>= 1) j ^= bit; j ^= bit; if (i < j) { const t = re[i]; re[i] = re[j]; re[j] = t; } }
  for (let len = 2; len <= n; len <<= 1) {
    const ang = -2 * Math.PI / len, wr = Math.cos(ang), wi = Math.sin(ang);
    for (let i = 0; i < n; i += len) {
      let cr = 1, ci = 0;
      for (let k = 0; k < len / 2; k++) {
        const a = i + k, b = a + len / 2, tr = re[b] * cr - im[b] * ci, ti = re[b] * ci + im[b] * cr;
        re[b] = re[a] - tr; im[b] = im[a] - ti; re[a] += tr; im[a] += ti;
        const nc = cr * wr - ci * wi; ci = cr * wi + ci * wr; cr = nc;
      }
    }
  }
  let s = 0, w = 0;
  for (let i = 1; i < n / 2; i++) { const m = Math.hypot(re[i], im[i]); s += m * i; w += m; }
  return w > 1e-9 ? (s / w) * BR_SR / n : 0;
}
// msfa EG level (Q24 log) of one op after `sec` seconds held, at `note` / `vel` (44.1 kHz blocks).
const VEL_TAB = [0, 70, 86, 97, 106, 114, 121, 126, 132, 138, 142, 148, 152, 156, 160, 163, 166, 170, 173, 174, 178, 181, 184, 186, 189, 190,
  194, 196, 198, 200, 202, 205, 206, 209, 211, 214, 216, 218, 220, 222, 224, 225, 227, 229, 230, 232, 233, 235, 237, 238, 240, 241, 242,
  243, 244, 246, 246, 248, 249, 250, 251, 252, 253, 254];
const EXP_SC = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 14, 16, 19, 23, 27, 33, 39, 47, 56, 66, 80, 94, 110, 126, 142, 158, 174, 190, 206, 222, 238, 250];
function opOutLevel(op, note, vel) {
  const curve = (g, d, c) => { const s = (c === 0 || c === 3) ? (g * d * 329) >> 12 : (EXP_SC[Math.min(g, 32)] * d * 329) >> 15; return c < 2 ? -s : s; };
  const off = note - op.breakPoint - 17;
  const ls = off >= 0 ? curve(Math.trunc((off + 1) / 3), op.rightDepth, op.rightCurve) : curve(Math.trunc(-(off - 1) / 3), op.leftDepth, op.leftCurve);
  let ol = Math.min(127, sOut(op.output) + ls) << 5;
  ol += ((op.kvs * (VEL_TAB[vel >> 1] - 239) + 7) >> 3) << 4;
  return Math.max(0, ol);
}
function egLevelAt(op, note, vel, sec) {
  const ol = opOutLevel(op, note, vel), rs = (op.rateScaling * Math.min(31, Math.max(0, Math.trunc(note / 3) - 7))) >> 3;
  let level = 0, ix = 0, target = 0, rising = false, inc = 0;
  const adv = i => {
    ix = i; if (i >= 3) return;
    let al = ((sOut(op.levels[i]) >> 1) << 6) + ol - 4256; if (al < 16) al = 16;
    target = al * 65536; rising = target > level;
    const qr = Math.min(63, ((op.rates[i] * 41) >> 6) + rs);
    inc = (4 + (qr & 3)) << (8 + (qr >> 2));
  };
  adv(0);
  for (let b = 0, nb = Math.round(sec * 44100 / 64); b < nb && ix < 3; b++) {
    if (rising) { if (level < 112459776) level = 112459776; level += ((285212672 - level) >> 24) * inc; if (level >= target) { level = target; adv(ix + 1); } }
    else { level -= inc; if (level <= target) { level = target; adv(ix + 1); } }
  }
  return level;
}
// Brightness: a tiny static render of the voice at C3 / velocity 100 with every op held at the level its
// msfa EG reaches after `sec` (msfa routing, gains and feedback; no LFO), then spectral centroid ÷ f0.
function staticBrightness(v, sec) {
  const row = MSFA_ALG[v.algorithm], n = BR_N;
  const bus = [new Float64Array(n), new Float64Array(n), new Float64Array(n)], has = [true, false, false];
  const fbScale = v.feedback ? 1 / (1 << (8 - v.feedback + 1)) : 0;
  for (let k = 0; k < 6; k++) {
    const op = v.ops[5 - k], f = row[k], inb = (f >> 4) & 3, outb = f & 3;
    let add = (f & 4) !== 0;
    const g = Math.pow(2, egLevelAt(op, 60, 100, sec) / 16777216 - 14);
    const hz = op.mode ? Math.pow(10, ((op.coarse & 3) * 100 + op.fine) / 100) : opRatio(op) * BR_F0;
    const inc = hz / BR_SR, dst = bus[outb], src = inb ? bus[inb] : null, useIn = inb && has[inb];
    if (!has[outb]) add = false;
    if (g < 1e-4) { if (!add && outb) has[outb] = false; continue; }
    let y0 = 0, y = 0;
    const fb = (f & 0xc0) === 0xc0 && fbScale > 0;
    for (let i = 0; i < n; i++) {
      let ph = i * inc + (useIn ? src[i] : 0);
      if (fb) ph += (y0 + y) * fbScale;
      const o = Math.sin(2 * Math.PI * ph) * g;
      y0 = y; y = o;
      dst[i] = add ? dst[i] + o : o;
    }
    has[outb] = true;
  }
  const out = bus[0];
  for (let i = 0; i < n; i++) out[i] *= 0.5 - 0.5 * Math.cos(2 * Math.PI * i / n);
  return fftCentroid(out) / BR_F0;
}
function analyze(voice) {
  const v = normalizeVoice(voice), A = ALGORITHMS[v.algorithm];
  const b1 = staticBrightness(v, 0.03), b3 = staticBrightness(v, 0.15);
  const bright = b3 > 0 ? b3 : b1;
  const label = bright < 1.6 ? 'pure' : bright < 4 ? 'mellow' : bright < 10 ? 'bright' : 'harsh';
  const audible = A.carriers.map(c => v.ops[c - 1]).filter(o => o.output >= 40);
  const car = audible.length ? audible : A.carriers.map(c => v.ops[c - 1]);
  const atk = Math.max(...car.map(o => (o.levels[0] > 0 ? o.rates[0] : o.rates[1])));
  const sus = Math.max(...car.map(o => o.levels[2]));
  const decayFast = car.every(o => o.levels[2] < 60 || o.rates[2] > 70);
  let env = 'sustained';
  if (atk < 55) env = 'slow attack';
  else if (sus < 40 || (decayFast && sus < 75)) env = 'percussive';
  const fixed = v.ops.some(o => o.mode === 1 && o.output > 30);
  return { algorithm: v.algorithm + 1, carriers: A.carriers.slice(), brightness: Math.round(bright * 100) / 100,
    brightnessAttack: Math.round(b1 * 100) / 100, brightnessSustain: Math.round(b3 * 100) / 100, brightnessLabel: label,
    envelope: env, fixed, feedback: v.feedback, lfo: v.lfoPmd > 0 || v.lfoAmd > 0 };
}
function describe(voice) {
  const a = analyze(voice);
  return 'ALG ' + a.algorithm + ' · ' + a.carriers.length + ' car · ' + a.brightnessLabel + ' · ' + a.envelope +
    (a.feedback ? ' · fb ' + a.feedback : '') + (a.fixed ? ' · fixed op' : '') + (a.lfo ? ' · lfo' : '');
}

const DX7 = {
  parseSysex, unpackVmem, packVmem, voiceFromVced, voiceToVced, voiceToSysex, bankToSysex, voiceName,
  normalizeVoice, defaultVoice, checksum, ALGORITHMS, analyze, describe,
  NOTE_NAMES, WAVES, CURVES, OP_FIELDS, VOICE_FIELDS,
  noteName: n => NOTE_NAMES[((n % 12) + 12) % 12] + (Math.floor(n / 12) - 1),
  transposeName: t => NOTE_NAMES[t % 12] + (Math.floor(t / 12) + 1),
  breakPointName: bp => NOTE_NAMES[(bp + 9) % 12] + (Math.floor((bp + 9) / 12) - 1),
  opFrequency(op, note) {           // display helper: ratio (×) or Hz for fixed ops
    if (op.mode) return { fixed: true, hz: Math.pow(10, ((op.coarse & 3) * 100 + op.fine) / 100) * (op.detune > 7 ? Math.pow(2, 13457 * (op.detune - 7) / 16777216) : 1) };
    return { fixed: false, ratio: (op.coarse === 0 ? 0.5 : op.coarse) * (1 + op.fine / 100), detune: op.detune - 7 };
  },
};

// ═════════════════════════════════════════════════════════════════════════════════════════════
// DX7Synth — the device
// ═════════════════════════════════════════════════════════════════════════════════════════════
const PROC = 'mm-dx7-synth';
const _worklets = new WeakMap();
function workletSource() { return '/* dx7_synth.js engine (msfa port, Apache-2.0) */\n(' + DX7_WORKLET.toString() + ')();\n'; }
async function addWorkletModule(ctx, src) {
  // AK is a top-level const in audio_kit.js (script scope, not window) — reach it by bare name
  const ak = typeof AK !== 'undefined' && AK && typeof AK.addWorklet === 'function' ? AK : null;
  if (ak) return ak.addWorklet(ctx, src);
  const bytes = new TextEncoder().encode(src);
  let bin = '';
  for (let i = 0; i < bytes.length; i += 0x8000) bin += String.fromCharCode.apply(null, bytes.subarray(i, i + 0x8000));
  try { await ctx.audioWorklet.addModule('data:text/javascript;base64,' + btoa(bin)); }
  catch (e) {
    const url = URL.createObjectURL(new Blob([src], { type: 'application/javascript' }));
    try { await ctx.audioWorklet.addModule(url); } finally { URL.revokeObjectURL(url); }
  }
}
function loadWorklet(ctx) {
  if (!ctx.audioWorklet) return Promise.reject(new Error('AudioWorklet is not available here'));
  let p = _worklets.get(ctx);
  if (!p) { p = addWorkletModule(ctx, workletSource()); _worklets.set(ctx, p); p.catch(() => _worklets.delete(ctx)); }
  return p;
}

const MOD_DEFAULTS = { wheel: { range: 99, pitch: true, amp: true, eg: false }, breath: { range: 99, pitch: false, amp: true, eg: false },
  foot: { range: 0, pitch: false, amp: false, eg: false }, at: { range: 0, pitch: false, amp: false, eg: false } };
function normMod(m, d) {
  m = m && typeof m === 'object' ? m : {};
  return { range: clampInt(isNum(+m.range) && m.range !== null ? m.range : d.range, 0, 99),
    pitch: m.pitch == null ? d.pitch : !!m.pitch, amp: m.amp == null ? d.amp : !!m.amp, eg: m.eg == null ? d.eg : !!m.eg };
}
function normalizeState(s) {
  s = s && typeof s === 'object' ? s : {};
  return { v: 1, type: 'dx7', voice: normalizeVoice(s.voice),
    gain: isNum(+s.gain) && s.gain !== null ? Math.max(0, Math.min(4, +s.gain)) : 1,
    bendRange: isNum(+s.bendRange) && s.bendRange !== null ? clampInt(s.bendRange, 0, 24) : 2,
    mono: !!s.mono,
    wheel: normMod(s.wheel, MOD_DEFAULTS.wheel), breath: normMod(s.breath, MOD_DEFAULTS.breath), foot: normMod(s.foot, MOD_DEFAULTS.foot),
    at: normMod(s.at, MOD_DEFAULTS.at) };
}
const SYNTH_KEYS = { gain: [0, 4], bendRange: [0, 24], mono: [0, 1] };

class DX7Synth {
  constructor(ctx, opts = {}) {
    if (!ctx) throw new Error('DX7Synth needs an AudioContext');
    this.ctx = ctx;
    this.maxVoices = clampInt(opts.maxVoices || 16, 1, 64);
    this.state = normalizeState({});
    this.output = ctx.createGain();
    this._amp = ctx.createGain();
    this._amp.gain.value = this.state.gain;
    this._amp.connect(this.output);
    this._dest = opts.output || ctx.destination;
    this.output.connect(this._dest);
    this._node = null; this._pend = []; this._patchQ = false;
    this._ls = {}; this._editors = new Set(); this._nActive = 0;
    this._inited = null; this._disposed = false; this._worklet = false;
    this._pings = new Map(); this._pingId = 0;
  }
  static defaultState() { return normalizeState({}); }
  static workletSource() { return workletSource(); }
  static normalizeState(s) { return normalizeState(s); }

  // ── lifecycle ────────────────────────────────────────────────────
  init() {
    if (this._inited) return this._inited;
    this._inited = (async () => {
      await loadWorklet(this.ctx);
      if (this._disposed) return this;
      this._node = new AudioWorkletNode(this.ctx, PROC, {
        numberOfInputs: 0, numberOfOutputs: 1, outputChannelCount: [2],
        processorOptions: { maxVoices: this.maxVoices, patch: Array.from(voiceToVced(this.state.voice)), cfg: this._cfg() },
      });
      this._node.port.onmessage = e => {
        const m = e.data;
        if (m && m.type === 'st') this._nActive = m.voices;
        else if (m && m.type === 'pong') { const f = this._pings.get(m.id); if (f) { this._pings.delete(m.id); f(); } }
      };
      this._node.onprocessorerror = e => console.error('DX7Synth worklet error', e);
      this._node.connect(this._amp);
      this._worklet = true;
      if (this._pend.length) { this._node.port.postMessage({ type: 'b', list: this._pend }); this._pend = []; }
      return this;
    })();
    return this._inited;
  }
  dispose() {
    if (this._disposed) return;
    [...this._editors].forEach(e => e.destroy());
    this._disposed = true;
    if (this._node) {
      try { this._node.port.postMessage({ type: 'dispose' }); } catch (e) { /* closed */ }
      try { this._node.disconnect(); } catch (e) { /* ok */ }
    }
    try { this._amp.disconnect(); this.output.disconnect(); } catch (e) { /* ok */ }
    this._ls = {};
  }
  get activeVoices() { return this._nActive; }
  // Resolves once the worklet has taken every message posted so far. Needed in an OfflineAudioContext:
  // schedule the notes, `await synth.flush()`, then `startRendering()`.
  async flush() {
    await this.init();
    if (this._disposed || !this._node) return this;
    await new Promise(res => { const id = ++this._pingId; this._pings.set(id, res); this._post({ type: 'ping', id }); });
    return this;
  }

  // ── events ───────────────────────────────────────────────────────
  on(type, fn) { (this._ls[type] = this._ls[type] || new Set()).add(fn); return () => this.off(type, fn); }
  off(type, fn) { if (this._ls[type]) this._ls[type].delete(fn); }
  _emit(type, detail) { const s = this._ls[type]; if (s) for (const fn of [...s]) { try { fn(detail); } catch (e) { console.error(e); } } }

  // ── messaging (posted at once — the worklet queues by time; held until init) ─
  _post(m) {
    if (this._disposed) return;
    if (!this._node) { this._pend.push(m); return; }
    this._node.port.postMessage(m);
  }
  _t(when) { return isNum(when) && when > this.ctx.currentTime ? when : null; }
  _cfg() {
    const s = this.state;
    return { type: 'cfg', maxVoices: this.maxVoices, bendRange: s.bendRange, mono: s.mono, wheel: s.wheel, breath: s.breath, foot: s.foot, at: s.at };
  }

  // ── playing ─────────────────────────────────────────────────────
  noteOn(note, vel = 0.8, when, ch = 1) {
    note = clampInt(note, 0, 127);
    const v = clampInt((isNum(vel) ? vel : 0.8) * 127, 0, 127);
    if (v <= 0) return this.noteOff(note, when, ch);
    const t = this._t(when);
    this._post({ type: 'ev', k: 'on', t, n: note, v, c: ch | 0 });
    this._emit('note', { note, vel: v / 127, on: true, t: t == null ? this.ctx.currentTime : t, ch });
  }
  noteOff(note, when, ch = 1) {
    note = clampInt(note, 0, 127);
    const t = this._t(when);
    this._post({ type: 'ev', k: 'off', t, n: note, c: ch | 0 });
    this._emit('note', { note, on: false, t: t == null ? this.ctx.currentTime : t, ch });
  }
  allOff(when) {
    const now = !isNum(when) || when <= this.ctx.currentTime + 0.003;
    if (now) this._post({ type: 'clear' });
    this._post({ type: 'ev', k: 'alloff', t: now ? null : when });
    this._emit('note', { all: true, on: false, t: now ? this.ctx.currentTime : when });
  }
  panic() { this._post({ type: 'panic' }); this._emit('note', { all: true, on: false, t: this.ctx.currentTime }); }
  cc(num, value01, when) {
    num = num | 0;
    const v = clampInt((isNum(value01) ? value01 : 0) * 127, 0, 127);
    if (num === 120 || num === 123) { if (!isNum(when) || when <= this.ctx.currentTime + 0.003) this._post({ type: 'clear' }); }
    this._post({ type: 'ev', k: 'cc', t: this._t(when), n: num, v });
    this._emit('cc', { num, value: v / 127, t: when });
  }
  pitchBend(norm, when) {
    const v = Math.max(-1, Math.min(1, isNum(norm) ? norm : 0));
    this._post({ type: 'ev', k: 'pb', t: this._t(when), v });
  }
  aftertouch(value01, when) { this._post({ type: 'ev', k: 'at', t: this._t(when), v: clampInt((isNum(value01) ? value01 : 0) * 127, 0, 127) }); }

  // ── voice / state ───────────────────────────────────────────────
  get voice() { return clone(this.state.voice); }
  loadVoice(voice) {
    this.state.voice = normalizeVoice(voice);
    this._sendPatch(true);
    this._emit('change', { path: 'voice', voice: true });
    return this;
  }
  _sendPatch(now) {
    if (now) { this._patchQ = false; this._post({ type: 'patch', data: Array.from(voiceToVced(this.state.voice)) }); return; }
    if (this._patchQ) return;
    this._patchQ = true;
    Promise.resolve().then(() => { if (this._patchQ) this._sendPatch(true); });
  }
  getState() { return clone(this.state); }
  setState(json) {
    let src = json;
    if (typeof src === 'string') { try { src = JSON.parse(src); } catch (e) { return false; } }
    if (!src || typeof src !== 'object') return false;
    if (src.ops && !src.voice) src = { voice: src };        // a bare voice object
    this.state = normalizeState(src);
    this._amp.gain.setTargetAtTime(this.state.gain, this.ctx.currentTime, 0.01);
    this._post(this._cfg());
    this._sendPatch(true);
    this._emit('state', this.getState());
    this._emit('change', { path: '*' });
    return true;
  }

  // ── parameter paths (editor / automation) ───────────────────────
  _resolve(path) {
    const parts = String(path).split('.');
    const st = this.state;
    if (parts[0] in SYNTH_KEYS && parts.length === 1) return { obj: st, key: parts[0], range: SYNTH_KEYS[parts[0]], synth: true };
    if ((parts[0] === 'wheel' || parts[0] === 'breath' || parts[0] === 'foot' || parts[0] === 'at') && parts.length === 2 && parts[1] in st.wheel)
      return { obj: st[parts[0]], key: parts[1], range: parts[1] === 'range' ? [0, 99] : [0, 1], synth: true, bool: parts[1] !== 'range' };
    const v = st.voice;
    if (parts[0] === 'name' && parts.length === 1) return { obj: v, key: 'name', name: true };
    const m = /^op([1-6])$/.exec(parts[0]);
    if (m) {
      const op = v.ops[+m[1] - 1];
      if (parts.length === 2 && parts[1] in OP_FIELDS) return { obj: op, key: parts[1], range: OP_FIELDS[parts[1]] };
      if (parts.length === 3 && (parts[1] === 'rates' || parts[1] === 'levels') && /^[0-3]$/.test(parts[2])) return { obj: op[parts[1]], key: +parts[2], range: [0, 99] };
      return null;
    }
    if (parts.length === 1 && parts[0] in VOICE_FIELDS) return { obj: v, key: parts[0], range: VOICE_FIELDS[parts[0]] };
    if (parts.length === 2 && (parts[0] === 'pitchRates' || parts[0] === 'pitchLevels') && /^[0-3]$/.test(parts[1])) return { obj: v[parts[0]], key: +parts[1], range: [0, 99] };
    return null;
  }
  getParam(path) { const r = this._resolve(path); return r ? r.obj[r.key] : undefined; }
  setParam(path, value) {
    const r = this._resolve(path);
    if (!r) return false;
    let v;
    if (r.name) v = cleanName(value);
    else if (r.bool || path === 'mono') v = !!(typeof value === 'string' ? +value : value);
    else if (path === 'gain') v = Math.max(0, Math.min(4, +value || 0));
    else v = clampInt(value, r.range[0], r.range[1]);
    r.obj[r.key] = v;
    if (r.synth) {
      if (path === 'gain') this._amp.gain.setTargetAtTime(v, this.ctx.currentTime, 0.01);
      else this._post(this._cfg());
    } else this._sendPatch(false);
    this._emit('change', { path, value: v });
    return true;
  }

  mountEditor(el, opts) { return mountEditor(this, el, opts || {}); }
}

// ═════════════════════════════════════════════════════════════════════════════════════════════
// Editor — touch-friendly: every control is an <input type=range> (touch_controls.js gives them
// relative finger drag), op cards and diagram boxes are tap targets ≥ 34 px.
// ═════════════════════════════════════════════════════════════════════════════════════════════
const ED_CSS = `
.dx7e{--g:var(--gold,#d8a060);--gh:var(--gold-hi,#ffd896);--t:var(--text,#c8a878);--td:var(--text-dim,#7a5828);--r:var(--rule,#553318);
  --ink:var(--ink,#1a1410);--rust:var(--rust,#c87633);--em:var(--emerald-hi,#a8e89c);
  font-family:"Courier New",monospace;font-size:11px;color:var(--t);height:100%;min-height:0;display:grid;
  grid-template-columns:minmax(260px,320px) minmax(0,1fr);grid-template-rows:auto minmax(0,1fr);gap:6px;padding:6px 10px;box-sizing:border-box;overflow:auto}
.dx7e *{box-sizing:border-box}
.dx7e-top{grid-column:1/3;display:flex;flex-wrap:wrap;gap:6px 12px;align-items:center}
.dx7e-top .nm{background:var(--ink);color:var(--gh);border:1px solid var(--r);font:inherit;font-size:13px;letter-spacing:.12em;width:16ch;padding:4px 6px}
.dx7e-btn{background:var(--ink);color:var(--gh);border:1px solid var(--g);font:inherit;font-size:11px;min-width:34px;min-height:30px;padding:2px 8px;cursor:pointer;touch-action:manipulation}
.dx7e-btn.on{background:var(--rust);color:var(--ink);border-color:var(--gh)}
.dx7e-btn.dim{color:var(--td);border-color:var(--r)}
.dx7e-alg{display:inline-flex;align-items:center;gap:4px}
.dx7e-alg b{color:var(--gh);font-size:15px;min-width:3ch;text-align:center}
.dx7e-left{display:flex;flex-direction:column;gap:6px;min-height:0;overflow:auto}
.dx7e-panel{border:1px solid var(--r);padding:4px 6px 5px;background:rgba(14,9,8,.6)}
.dx7e-panel h4{margin:0 0 3px;font-size:10px;letter-spacing:.14em;color:var(--g);font-weight:normal;display:flex;justify-content:space-between;align-items:center;gap:6px}
.dx7e-diag{width:100%;height:auto;display:block;touch-action:manipulation}
.dx7e-diag .opb{cursor:pointer}
.dx7e-diag rect{fill:#1a1410;stroke:#7a5828;stroke-width:1.5}
.dx7e-diag .car rect{fill:#3a2412;stroke:#d8a060}
.dx7e-diag .sel rect{stroke:#ffd896;stroke-width:3}
.dx7e-diag text{fill:#ffd896;font:bold 14px "Courier New",monospace;text-anchor:middle;dominant-baseline:central;pointer-events:none}
.dx7e-diag line,.dx7e-diag path{stroke:#c8a878;stroke-width:1.5;fill:none}
.dx7e-diag .fbk{stroke:#c87633;stroke-width:2}
.dx7e-right{display:flex;flex-direction:column;gap:6px;min-height:0;min-width:0}
.dx7e-cards{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:4px}
.dx7e-card{border:1px solid var(--r);padding:3px 4px;cursor:pointer;background:rgba(14,9,8,.6);min-width:0;touch-action:manipulation}
.dx7e-card.sel{border-color:var(--gh);background:#24180e}
.dx7e-card.car .ct{color:var(--g)}
.dx7e-card button{all:unset;display:block;width:100%;box-sizing:border-box;cursor:pointer;touch-action:manipulation}
.dx7e-card .ct{display:flex;justify-content:space-between;font-size:10px;letter-spacing:.08em;color:var(--td);min-height:24px;align-items:center}
.dx7e-card .cb{min-height:40px}
.dx7e-card .ct b{color:var(--gh)}
.dx7e-card .fq{font-size:10px;color:var(--t);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.dx7e-card svg{width:100%;height:26px;display:block}
.dx7e-card input{width:100%}
.dx7e-detail{flex:1;min-height:0;overflow:auto;border:1px solid var(--r);padding:5px 8px;background:rgba(14,9,8,.6)}
.dx7e-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(165px,1fr));gap:2px 12px}
.dx7e-s{display:grid;grid-template-columns:7.2ch minmax(0,1fr) 4.8ch;align-items:center;gap:4px;min-height:28px}
.dx7e-g2{display:grid;grid-template-columns:1fr 1fr;gap:0 10px}
.dx7e-g4{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:0 12px}
.dx7e-g4 .dx7e-s{grid-template-columns:2.6ch minmax(0,1fr) 3.4ch}
.dx7e-top .dx7e-s{grid-template-columns:auto minmax(0,1fr) 4.8ch}
.dx7e-s span{color:var(--td);font-size:10px;letter-spacing:.06em;white-space:nowrap;overflow:hidden}
.dx7e-s b{color:var(--gh);font-weight:normal;text-align:right;font-size:11px;white-space:nowrap}
.dx7e input[type=range]{width:100%;min-width:0;height:24px;margin:0;accent-color:var(--rust,#c87633);touch-action:none}
.dx7e-eg{width:100%;height:70px;display:block;margin:2px 0 4px}
.dx7e-sub{font-size:10px;letter-spacing:.14em;color:var(--g);margin:5px 0 2px;border-bottom:1px solid var(--r)}
.dx7e-row{display:flex;gap:6px;align-items:center;flex-wrap:wrap}
`;
function injectCss() {
  if (typeof document === 'undefined' || document.getElementById('dx7e-style')) return;
  const st = document.createElement('style'); st.id = 'dx7e-style'; st.textContent = ED_CSS; document.head.appendChild(st);
}

// Layout an algorithm for drawing: carriers on the bottom row, modulators stacked above their target.
function layoutAlgorithm(a) {
  const A = ALGORITHMS[a], pos = {}, row = {};
  const primary = op => (A.targets[op].length ? Math.min(...A.targets[op]) : 0);
  const kids = op => A.mods[op].filter(m => primary(m) === op && m !== op).sort((x, y) => x - y);
  const depth = op => { if (row[op] != null) return row[op]; const t = A.targets[op]; row[op] = t.length ? 1 + Math.max(...t.map(depth)) : 0; return row[op]; };
  for (let op = 1; op <= 6; op++) depth(op);
  let col = 0;
  const place = op => {
    const k = kids(op).filter(m => A.targets[m].length === 1);
    if (!k.length) { pos[op] = col++; return; }
    const xs = k.map(m => { place(m); return pos[m]; });
    pos[op] = (Math.min(...xs) + Math.max(...xs)) / 2;
  };
  for (const c of A.carriers) place(c);
  for (let op = 1; op <= 6; op++) {          // shared modulators: centre over their targets
    if (pos[op] == null) {
      const t = A.targets[op];
      pos[op] = t.length ? t.reduce((s, x) => s + (pos[x] != null ? pos[x] : col), 0) / t.length : col++;
    }
  }
  // keep two ops on one row from sitting on top of each other
  const rows = {};
  for (let op = 1; op <= 6; op++) (rows[row[op]] = rows[row[op]] || []).push(op);
  for (const r in rows) {
    const ops = rows[r].sort((x, y) => pos[x] - pos[y]);
    for (let i = 1; i < ops.length; i++) if (pos[ops[i]] - pos[ops[i - 1]] < 1) pos[ops[i]] = pos[ops[i - 1]] + 1;
  }
  let cols = 0, rmax = 0;
  for (let op = 1; op <= 6; op++) { cols = Math.max(cols, pos[op] + 1); rmax = Math.max(rmax, row[op]); }
  return { pos, row, cols, rows: rmax + 1 };
}
function algorithmSvg(a, sel) {
  const A = ALGORITHMS[a], L = layoutAlgorithm(a);
  const W = 280, H = 168, bw = 36, bh = 26;
  const cw = Math.min(58, (W - 30) / Math.max(1, L.cols)), rh = Math.min(40, (H - 34) / Math.max(1, L.rows));
  const x0 = (W - cw * L.cols) / 2 + cw / 2, yb = H - 22 - Math.max(0, (H - 34 - rh * L.rows) / 2);
  const X = op => x0 + L.pos[op] * cw, Y = op => yb - L.row[op] * rh;
  let s = '<svg class="dx7e-diag" viewBox="0 0 ' + W + ' ' + H + '" xmlns="http://www.w3.org/2000/svg">';
  // output bus
  const cx = A.carriers.map(X);
  s += '<line x1="' + (Math.min(...cx)) + '" y1="' + (H - 8) + '" x2="' + (Math.max(...cx)) + '" y2="' + (H - 8) + '"/>';
  for (const c of A.carriers) s += '<line x1="' + X(c) + '" y1="' + (Y(c) + bh / 2) + '" x2="' + X(c) + '" y2="' + (H - 8) + '"/>';
  for (const [f, t] of A.edges) s += '<line x1="' + X(f) + '" y1="' + (Y(f) + bh / 2) + '" x2="' + X(t) + '" y2="' + (Y(t) - bh / 2) + '"/>';
  // feedback: the DX7 loop as drawn by Yamaha (from → to), a self-loop otherwise
  const fb = A.feedback;
  if (fb.from === fb.to) {
    const x = X(fb.op), y = Y(fb.op);
    s += '<path class="fbk" d="M' + (x + bw / 2) + ' ' + y + ' h8 V' + (y - bh / 2 - 7) + ' H' + x + ' V' + (y - bh / 2) + '"/>';
  } else {
    const xf = X(fb.from), yf = Y(fb.from), xt = X(fb.to), yt = Y(fb.to), xr = Math.max(xf, xt) + bw / 2 + 10;
    s += '<path class="fbk" d="M' + (xf + bw / 2) + ' ' + yf + ' H' + xr + ' V' + (yt - bh / 2 - 7) + ' H' + xt + ' V' + (yt - bh / 2) + '"/>';
  }
  for (let op = 1; op <= 6; op++) {
    const car = A.carriers.indexOf(op) >= 0;
    s += '<g class="opb' + (car ? ' car' : '') + (op === sel ? ' sel' : '') + '" data-op="' + op + '"><rect x="' + (X(op) - bw / 2) + '" y="' + (Y(op) - bh / 2) +
      '" width="' + bw + '" height="' + bh + '" rx="3"/><text x="' + X(op) + '" y="' + Y(op) + '">' + op + '</text></g>';
  }
  return s + '</svg>';
}
// EG polyline: time per stage approximated from msfa's increments (display only).
function egPoints(rates, levels, w, h, pad) {
  const lv = l => ((l >= 20 ? 28 + l : sOut(l)) >> 1) << 6;
  const qinc = r => { const q = Math.min(63, (r * 41) >> 6); return (4 + (q & 3)) << (2 + (q >> 2)); };
  let cur = lv(levels[3]), t = 0;
  const pts = [[0, cur]];
  for (let i = 0; i < 4; i++) {
    const tgt = lv(levels[i]), d = Math.abs(tgt - cur);
    let dt = d * 65536 / qinc(rates[i]) / 64 * 64 / 44100;
    if (tgt > cur) dt *= 0.35;
    if (i === 3) { t += 0.25; pts.push([t, cur]); }                  // the sustain hold
    t += Math.min(4, dt + 0.004);
    pts.push([t, tgt]); cur = tgt;
  }
  const T = Math.sqrt(t || 1), top = lv(99);
  return pts.map(([x, y]) => [pad + (Math.sqrt(x) / T) * (w - 2 * pad), h - pad - (y / top) * (h - 2 * pad)]);
}
function egSvg(rates, levels, cls, w, h) {
  const p = egPoints(rates, levels, w, h, 3);
  return '<svg class="' + cls + '" viewBox="0 0 ' + w + ' ' + h + '" preserveAspectRatio="none"><polyline points="' +
    p.map(q => q[0].toFixed(1) + ',' + q[1].toFixed(1)).join(' ') + '" fill="none" stroke="#d8a060" stroke-width="1.5" vector-effect="non-scaling-stroke"/></svg>';
}
const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const fmtFreq = op => {
  const f = DX7.opFrequency(op);
  if (f.fixed) return (f.hz >= 1000 ? (f.hz / 1000).toFixed(2) + 'k' : f.hz.toFixed(f.hz < 10 ? 2 : 1)) + 'Hz';
  return '×' + f.ratio.toFixed(2) + (f.detune ? (f.detune > 0 ? ' +' : ' ') + f.detune : '');
};
const DISP = {
  detune: v => (v - 7 > 0 ? '+' : '') + (v - 7), leftCurve: v => CURVES[v], rightCurve: v => CURVES[v],
  breakPoint: v => DX7.breakPointName(v), lfoWave: v => ['TRI', 'SAW↓', 'SAW↑', 'SQR', 'SIN', 'S/H'][v],
  transpose: v => DX7.transposeName(v), mode: v => (v ? 'FIXED' : 'RATIO'), algorithm: v => v + 1,
  gain: v => (+v).toFixed(2), bendRange: v => v + ' st',
};

function mountEditor(synth, el, opts) {
  injectCss();
  let sel = 1, destroyed = false, selfChange = false;
  const root = document.createElement('div');
  root.className = 'dx7e';
  el.appendChild(root);
  const slider = (path, label, min, max, key) =>
    '<label class="dx7e-s"><span>' + label + '</span><input type="range" min="' + min + '" max="' + max + '" step="' + (path === 'gain' ? 0.01 : 1) +
    '" data-p="' + path + '" data-k="' + (key || '') + '"><b data-v="' + path + '"></b></label>';
  const toggle = (path, label, title) => '<button type="button" class="dx7e-btn dim" data-t="' + path + '" title="' + (title || '') + '">' + label + '</button>';

  root.innerHTML =
    '<div class="dx7e-top">' +
      '<input class="nm" maxlength="10" spellcheck="false" data-name title="voice name (10 characters)">' +
      '<span class="dx7e-alg">ALG <button type="button" class="dx7e-btn" data-alg="-1" title="previous algorithm">−</button><b data-v="algorithm"></b>' +
      '<button type="button" class="dx7e-btn" data-alg="1" title="next algorithm">+</button></span>' +
      '<span style="width:130px">' + slider('feedback', 'FB', 0, 7) + '</span>' +
      '<span style="width:160px">' + slider('transpose', 'TRANSP', 0, 48, 'transpose') + '</span>' +
      toggle('oscKeySync', 'OSC SYNC', 'oscillator key sync: phases restart on every note') +
      toggle('mono', 'MONO', 'mono (last-note priority, legato) / poly') +

    '</div>' +
    '<div class="dx7e-left">' +
      '<div class="dx7e-panel"><h4><span>ALGORITHM</span><span data-algnote style="color:var(--td)"></span></h4><div data-diag></div></div>' +
      '<div class="dx7e-panel"><h4><span>LFO</span>' + toggle('lfoKeySync', 'KEY SYNC', 'LFO restarts with the first key') + '</h4><div class="dx7e-g2">' +
        slider('lfoWave', 'WAVE', 0, 5, 'lfoWave') + slider('lfoSpeed', 'SPEED', 0, 99) + slider('lfoDelay', 'DELAY', 0, 99) +
        slider('lfoPmd', 'PMD', 0, 99) + slider('lfoAmd', 'AMD', 0, 99) + slider('pitchModSens', 'P.SENS', 0, 7) + '</div></div>' +
      '<div class="dx7e-panel"><h4>PITCH EG</h4><div data-peg></div><div class="dx7e-g2">' +
        [0, 1, 2, 3].map(i => slider('pitchRates.' + i, 'R' + (i + 1), 0, 99) + slider('pitchLevels.' + i, 'L' + (i + 1), 0, 99, 'plevel')).join('') + '</div></div>' +
      '<div class="dx7e-panel"><h4>CONTROLLERS</h4><div class="dx7e-g2">' + slider('bendRange', 'BEND', 0, 24, 'bendRange') + slider('gain', 'GAIN', 0, 2, 'gain') +
        '</div>' + slider('wheel.range', 'WHEEL', 0, 99) +
        '<div class="dx7e-row">' + toggle('wheel.pitch', 'PITCH', 'wheel → LFO pitch depth (× each voice\'s P.SENS)') + toggle('wheel.amp', 'AMP', 'wheel → LFO amp depth (× each op\'s AMS)') +
        toggle('wheel.eg', 'EG BIAS', 'wheel → level bias on ops with AMS') + '</div></div>' +
    '</div>' +
    '<div class="dx7e-right"><div class="dx7e-cards" data-cards></div><div class="dx7e-detail" data-detail></div></div>';

  const $ = q => root.querySelector(q), $$ = q => [...root.querySelectorAll(q)];
  const st = () => synth.state, voice = () => synth.state.voice;
  const disp = (path, v) => {
    const k = path.split('.').pop();
    if (/^pitchLevels\./.test(path)) return (v - 50 > 0 ? '+' : '') + (v - 50);
    if (typeof v === 'boolean') return v ? 'ON' : 'OFF';
    return DISP[k] ? DISP[k](v) : String(v);
  };

  function renderCards() {
    const A = ALGORITHMS[voice().algorithm];
    $('[data-cards]').innerHTML = [1, 2, 3, 4, 5, 6].map(op => {
      const o = voice().ops[op - 1], car = A.carriers.indexOf(op) >= 0;
      return '<div class="dx7e-card' + (car ? ' car' : '') + (op === sel ? ' sel' : '') + '" data-op="' + op + '">' +
        '<button type="button" class="ct" data-op="' + op + '" title="edit OP' + op + '"><span>OP' + op + (car ? ' ◆' : '') + '</span><b data-v="op' + op + '.output"></b></button>' +
        '<input type="range" min="0" max="99" step="1" data-p="op' + op + '.output" title="OP' + op + ' output level">' +
        '<button type="button" class="cb" data-op="' + op + '" title="edit OP' + op + '"><div class="fq" data-fq="' + op + '">' + esc(fmtFreq(o)) + '</div>' +
        '<div data-egmini="' + op + '">' + egSvg(o.rates, o.levels, '', 100, 26) + '</div></button></div>';
    }).join('');
  }
  function renderDetail() {
    const p = 'op' + sel + '.';
    $('[data-detail]').innerHTML =
      '<div class="dx7e-row" style="justify-content:space-between"><span class="dx7e-sub" style="border:0;margin:0">OPERATOR ' + sel + '</span>' +
        '<span class="dx7e-row">' + toggle(p + 'mode', 'FIXED', 'fixed frequency (Hz) instead of a ratio') +
        '<button type="button" class="dx7e-btn dim" data-mute="' + sel + '" title="output level 0 / 99">MUTE</button></span></div>' +
      '<div class="dx7e-grid">' + slider(p + 'output', 'LEVEL', 0, 99) + slider(p + 'coarse', 'COARSE', 0, 31) + slider(p + 'fine', 'FINE', 0, 99) +
        slider(p + 'detune', 'DETUNE', 0, 14, 'detune') + '</div>' +
      '<div class="dx7e-sub">ENVELOPE</div><div data-eg></div>' +
      '<div class="dx7e-g4">' + [0, 1, 2, 3].map(i => slider(p + 'rates.' + i, 'R' + (i + 1), 0, 99)).join('') +
        [0, 1, 2, 3].map(i => slider(p + 'levels.' + i, 'L' + (i + 1), 0, 99)).join('') + '</div>' +
      '<div class="dx7e-sub">SENSITIVITY</div><div class="dx7e-grid">' + slider(p + 'kvs', 'VELO', 0, 7) + slider(p + 'ams', 'AMS', 0, 3) +
        slider(p + 'rateScaling', 'RATE.S', 0, 7) + '</div>' +
      '<div class="dx7e-sub">KEYBOARD LEVEL SCALING</div><div class="dx7e-grid">' + slider(p + 'breakPoint', 'BREAK', 0, 99, 'breakPoint') +
        slider(p + 'leftDepth', 'L.DEPTH', 0, 99) + slider(p + 'rightDepth', 'R.DEPTH', 0, 99) +
        slider(p + 'leftCurve', 'L.CURVE', 0, 3, 'leftCurve') + slider(p + 'rightCurve', 'R.CURVE', 0, 3, 'rightCurve') + '</div>';
  }
  function renderDiagram() {
    $('[data-diag]').innerHTML = algorithmSvg(voice().algorithm, sel);
    const fb = ALGORITHMS[voice().algorithm].feedback;
    $('[data-algnote]').textContent = fb.from !== fb.to ? 'fb: OP6 self (msfa)' : 'fb OP' + fb.op;
  }
  function renderEgs() {
    const o = voice().ops[sel - 1];
    const eg = $('[data-eg]'); if (eg) eg.innerHTML = egSvg(o.rates, o.levels, 'dx7e-eg', 400, 70);
    for (let op = 1; op <= 6; op++) {
      const m = root.querySelector('[data-egmini="' + op + '"]'), q = voice().ops[op - 1];
      if (m) m.innerHTML = egSvg(q.rates, q.levels, '', 100, 26);
      const f = root.querySelector('[data-fq="' + op + '"]'); if (f) f.textContent = fmtFreq(q);
    }
    $('[data-peg]').innerHTML = pegSvg(voice());
  }
  function pegSvg(v) {      // pitch EG: centre line = no bend
    const w = 260, h = 40, pts = [], lvl = l => h / 2 - ((l - 50) / 50) * (h / 2 - 3);
    let t = 0; pts.push([0, lvl(v.pitchLevels[3])]);
    for (let i = 0; i < 4; i++) { if (i === 3) t += 0.6; t += (100 - v.pitchRates[i]) / 25 + 0.1; pts.push([t, lvl(v.pitchLevels[i])]); }
    const T = t || 1;
    return '<svg class="dx7e-eg" style="height:40px" viewBox="0 0 ' + w + ' ' + h + '" preserveAspectRatio="none"><line x1="0" x2="' + w + '" y1="' + h / 2 + '" y2="' + h / 2 +
      '" stroke="#553318"/><polyline points="' + pts.map(p => (p[0] / T * (w - 6) + 3).toFixed(1) + ',' + p[1].toFixed(1)).join(' ') +
      '" fill="none" stroke="#d8a060" stroke-width="1.5" vector-effect="non-scaling-stroke"/></svg>';
  }
  function sync() {
    const s = st();
    for (const inp of $$('input[data-p]')) {
      const v = synth.getParam(inp.dataset.p);
      if (v === undefined) continue;
      if (document.activeElement !== inp || !selfChange) inp.value = typeof v === 'boolean' ? +v : v;
    }
    for (const b of $$('[data-v]')) { const v = synth.getParam(b.dataset.v); if (v !== undefined) b.textContent = disp(b.dataset.v, v); }
    for (const b of $$('[data-t]')) { const v = synth.getParam(b.dataset.t); b.classList.toggle('on', !!v); b.classList.toggle('dim', !v); }
    const nm = $('[data-name]'); if (document.activeElement !== nm) nm.value = s.voice.name;
  }
  function full() { renderCards(); renderDetail(); renderDiagram(); renderEgs(); sync(); }
  function select(op) { sel = op; renderDetail(); renderDiagram(); for (const c of $$('.dx7e-card')) c.classList.toggle('sel', +c.dataset.op === op); renderEgs(); sync(); }

  const set = (path, value) => { selfChange = true; try { synth.setParam(path, value); } finally { selfChange = false; } };
  const onInput = e => {
    const t = e.target;
    if (t.dataset && t.dataset.p) set(t.dataset.p, +t.value);
    else if (t.dataset && t.dataset.name !== undefined) set('name', t.value.toUpperCase());
  };
  const onClick = e => {
    const t = e.target.closest('button, .dx7e-card, .opb');
    if (!t || !root.contains(t)) return;
    if (t.dataset.alg) { set('algorithm', (voice().algorithm + 32 + +t.dataset.alg) % 32); return; }
    if (t.dataset.t) { const v = synth.getParam(t.dataset.t); set(t.dataset.t, typeof v === 'boolean' ? !v : v ? 0 : 1); return; }
    if (t.dataset.mute) { const p = 'op' + t.dataset.mute + '.output'; const o = synth.getParam(p); t._prev = o || t._prev || 99; set(p, o ? 0 : t._prev); return; }
    if (t.dataset.op && !(e.target.tagName === 'INPUT')) select(+t.dataset.op);
  };
  root.addEventListener('input', onInput);
  root.addEventListener('click', onClick);
  const off = synth.on('change', d => {
    if (destroyed) return;
    const p = d && d.path || '*';
    if (p === '*' || p === 'voice' || p === 'algorithm') { if (p === 'algorithm') { renderCards(); renderDiagram(); renderEgs(); sync(); } else full(); return; }
    if (/rates|levels|coarse|fine|detune|mode/.test(p)) renderEgs();
    sync();
  });
  full();
  const ed = {
    element: root,
    refresh: full,
    select,
    destroy() { if (destroyed) return; destroyed = true; off(); root.removeEventListener('input', onInput); root.removeEventListener('click', onClick); root.remove(); synth._editors.delete(ed); },
  };
  synth._editors.add(ed);
  return ed;
}

DX7Synth.DX7 = DX7;
window.DX7 = DX7;
window.DX7Synth = DX7Synth;
})();
