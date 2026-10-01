/* fm1_dx7.js
 *
 * DX7-format SysEx builders for the M-VAVE FM-1. The FM-1's stock
 * engine is Google's msfa / Dexed core and, per the open-firmware
 * project's analysis, "accepts DX7 dumps and parameter changes but
 * has no read-back path over MIDI". So we can PUSH a voice to the
 * synth; we can never ask what's loaded. Baud Girl's FM-1+VA keeps
 * the Dexed core (with its detune / LFO / feedback / note-off fixes),
 * so the same dumps apply — but the VA engine is its own thing and
 * is not reachable through DX7 messages.
 *
 * HARDWARE-UNVERIFIED: these are built to the public DX7 spec and
 * Dexed's parser. Confirm on the device via fm1_console.html — if a
 * push does nothing, open the monitor and check the SysEx permission
 * badge first, then try the single-parameter change (which Dexed
 * also handles) before assuming the dump format is wrong.
 *
 * Exposes:
 *   dx7DefaultVoice()                       — INIT-style voice object
 *   dx7VoiceFromTwoOp({...})                — riffmaster_fm knobs → voice
 *   dx7VoiceToVced(voice)                   — 155-byte Uint8Array
 *   dx7VoiceSysex(voice, channel)           — full F0…F7 single-voice dump
 *   dx7ParamChangeSysex(param, value, ch)   — F0 43 1n gh pp vv F7
 *   DX7_ALGORITHMS                          — carrier sets per algorithm (for display)
 *
 * VCED layout (155 bytes), ops stored OP6 → OP1, 21 bytes each:
 *   0-3 EG rates, 4-7 EG levels, 8 break point, 9 L depth, 10 R depth,
 *   11 L curve, 12 R curve, 13 rate scaling, 14 AMS, 15 KVS,
 *   16 output level, 17 osc mode, 18 coarse, 19 fine, 20 detune (7 = 0)
 * then 126-129 pitch EG rates, 130-133 pitch EG levels, 134 algorithm,
 * 135 feedback, 136 osc key sync, 137 LFO speed, 138 LFO delay,
 * 139 LFO PMD, 140 LFO AMD, 141 LFO key sync, 142 LFO wave,
 * 143 pitch mod sens, 144 transpose (24 = C3), 145-154 name.
 */
"use strict";

// Which operators are carriers in each of the 32 algorithms (1-based
// op numbers). Used only for the console's algorithm readout.
const DX7_ALGORITHMS = [
  [1,3],[1,3],[1,4],[1,4],[1,3,5],[1,3,5],[1,3],[1,3],[1,3],[1,4],
  [1,4],[1,3],[1,3],[1,3],[1,3],[1],[1],[1],[1,4,5],[1,2,4],
  [1,2,4,5],[1,3,4,5],[1,2,4,5],[1,2,3,4,5],[1,2,3,4,5],[1,2,4],[1,2,4],[1,3,6],[1,2,3,5],[1,2,3,6],
  [1,2,3,4,5],[1,2,3,4,5,6],
];

function _clamp(v, lo, hi) { return Math.max(lo, Math.min(hi, Math.round(v))); }

function dx7DefaultOp(outputLevel = 0) {
  return {
    rates: [99, 99, 99, 99],
    levels: [99, 99, 99, 0],
    breakPoint: 39,       // C3
    leftDepth: 0, rightDepth: 0,
    leftCurve: 0, rightCurve: 0,
    rateScaling: 0,
    ams: 0,
    kvs: 0,
    output: outputLevel,
    mode: 0,              // 0 = ratio, 1 = fixed
    coarse: 1,
    fine: 0,
    detune: 7,            // 7 = centre
  };
}

function dx7DefaultVoice() {
  return {
    name: 'INIT VOICE',
    ops: [dx7DefaultOp(99), dx7DefaultOp(0), dx7DefaultOp(0), dx7DefaultOp(0), dx7DefaultOp(0), dx7DefaultOp(0)],  // OP1..OP6
    pitchRates: [99, 99, 99, 99],
    pitchLevels: [50, 50, 50, 50],
    algorithm: 0,         // 0-based (algorithm 1)
    feedback: 0,
    oscKeySync: 1,
    lfoSpeed: 35, lfoDelay: 0, lfoPmd: 0, lfoAmd: 0, lfoKeySync: 1, lfoWave: 0,
    pitchModSens: 3,
    transpose: 24,
  };
}

// DX7 EG rates are 0 (slowest) … 99 (instant). The curve is roughly
// exponential; this log map puts 5 ms at 99, ~50 ms at 77, ~500 ms at
// 55, ~2.5 s at 40 — close enough that riffmaster_fm presets keep
// their character when pushed to the hardware.
function dx7MsToRate(ms) {
  return _clamp(99 - 22 * Math.log10(Math.max(1, ms) / 5), 5, 99);
}

// Frequency ratio → coarse/fine. coarse 0 is 0.5×, coarse n≥1 is n×;
// fine scales by (1 + fine/100).
function dx7RatioToCoarseFine(ratio) {
  if (ratio < 0.5) ratio = 0.5;
  if (ratio < 1) return { coarse: 0, fine: _clamp((ratio / 0.5 - 1) * 100, 0, 99) };
  const coarse = Math.min(31, Math.floor(ratio));
  return { coarse, fine: _clamp((ratio / coarse - 1) * 100, 0, 99) };
}

// riffmaster_fm's 2-op model → a 6-op voice using algorithm 1 with
// only OP1 (carrier) and OP2 (modulator) audible. The 2-op tool's
// "mod index" (0..500) is the raw FM depth in Hz-ish units; the DX7's
// modulator OUTPUT LEVEL is log-ish, so we take a square-root curve
// into the 50..99 range where DX7 modulators actually live.
function dx7VoiceFromTwoOp(p) {
  const v = dx7DefaultVoice();
  v.name = String(p.name || 'RIFF FM').toUpperCase().slice(0, 10).padEnd(10, ' ');
  v.algorithm = 0;
  v.feedback = 0;

  const car = v.ops[0], mod = v.ops[1];
  // Carrier
  car.output = 99;
  car.coarse = 1; car.fine = 0;
  car.rates  = [dx7MsToRate(p.attackMs ?? 8), dx7MsToRate(p.modDecMs ?? 600), 40, dx7MsToRate(p.releaseMs ?? 600)];
  const sus = _clamp((p.susPct ?? 35) * 0.99, 0, 99);
  car.levels = [99, sus, sus, 0];
  car.kvs = 3;
  // Modulator
  const cf = dx7RatioToCoarseFine(p.ratio ?? 2);
  mod.coarse = cf.coarse; mod.fine = cf.fine;
  const idx = _clamp(p.index ?? 120, 0, 500);
  mod.output = idx === 0 ? 0 : _clamp(50 + 49 * Math.sqrt(idx / 500), 0, 99);
  mod.rates  = [dx7MsToRate(p.attackMs ?? 8), dx7MsToRate(p.modDecMs ?? 600), 50, dx7MsToRate(p.releaseMs ?? 600)];
  mod.levels = [99, 5, 5, 0];     // index decays to ~5%, like the tool's exponential ramp
  mod.kvs = 2;
  return v;
}

function dx7VoiceToVced(v) {
  const out = new Uint8Array(155);
  let i = 0;
  // Ops are stored OP6 first.
  for (let o = 5; o >= 0; o--) {
    const op = v.ops[o];
    for (let k = 0; k < 4; k++) out[i++] = _clamp(op.rates[k], 0, 99);
    for (let k = 0; k < 4; k++) out[i++] = _clamp(op.levels[k], 0, 99);
    out[i++] = _clamp(op.breakPoint, 0, 99);
    out[i++] = _clamp(op.leftDepth, 0, 99);
    out[i++] = _clamp(op.rightDepth, 0, 99);
    out[i++] = _clamp(op.leftCurve, 0, 3);
    out[i++] = _clamp(op.rightCurve, 0, 3);
    out[i++] = _clamp(op.rateScaling, 0, 7);
    out[i++] = _clamp(op.ams, 0, 3);
    out[i++] = _clamp(op.kvs, 0, 7);
    out[i++] = _clamp(op.output, 0, 99);
    out[i++] = _clamp(op.mode, 0, 1);
    out[i++] = _clamp(op.coarse, 0, 31);
    out[i++] = _clamp(op.fine, 0, 99);
    out[i++] = _clamp(op.detune, 0, 14);
  }
  for (let k = 0; k < 4; k++) out[i++] = _clamp(v.pitchRates[k], 0, 99);
  for (let k = 0; k < 4; k++) out[i++] = _clamp(v.pitchLevels[k], 0, 99);
  out[i++] = _clamp(v.algorithm, 0, 31);
  out[i++] = _clamp(v.feedback, 0, 7);
  out[i++] = _clamp(v.oscKeySync, 0, 1);
  out[i++] = _clamp(v.lfoSpeed, 0, 99);
  out[i++] = _clamp(v.lfoDelay, 0, 99);
  out[i++] = _clamp(v.lfoPmd, 0, 99);
  out[i++] = _clamp(v.lfoAmd, 0, 99);
  out[i++] = _clamp(v.lfoKeySync, 0, 1);
  out[i++] = _clamp(v.lfoWave, 0, 5);
  out[i++] = _clamp(v.pitchModSens, 0, 7);
  out[i++] = _clamp(v.transpose, 0, 48);
  const name = String(v.name || '').padEnd(10, ' ').slice(0, 10);
  for (let k = 0; k < 10; k++) out[i++] = name.charCodeAt(k) & 0x7F;
  return out;
}

function dx7Checksum(bytes) {
  let sum = 0;
  for (const b of bytes) sum += b;
  return (128 - (sum & 0x7F)) & 0x7F;
}

// Single-voice dump: F0 43 1n 00 01 1B <155 bytes> <checksum> F7.
// n = device number = channel - 1.
function dx7VoiceSysex(voice, channel = 1) {
  const vced = dx7VoiceToVced(voice);
  const n = ((channel | 0) - 1) & 0x0F;
  const head = [0xF0, 0x43, 0x10 | n, 0x00, 0x01, 0x1B];
  return Uint8Array.from([...head, ...vced, dx7Checksum(vced), 0xF7]);
}

// Single parameter change: F0 43 1n gh pp vv F7 — g = group (0 =
// voice), h = top bit of the parameter number, pp = low 7 bits.
// `param` is the VCED byte index (0-155), e.g. 134 = algorithm.
function dx7ParamChangeSysex(param, value, channel = 1) {
  const n = ((channel | 0) - 1) & 0x0F;
  const p = _clamp(param, 0, 155);
  return Uint8Array.from([0xF0, 0x43, 0x10 | n, (p >> 7) & 0x01, p & 0x7F, _clamp(value, 0, 127), 0xF7]);
}

function dx7Hex(bytes) {
  return [...bytes].map(b => b.toString(16).toUpperCase().padStart(2, '0')).join(' ');
}
