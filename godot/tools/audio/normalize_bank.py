#!/usr/bin/env python3
"""Normalize the slowstick audio bank.

Playtest: 'slowstick music and sound effects not really hitting
over music player/title music.' Measured: stick BGM peaked at
0.07-0.21 (RMS -24..-36 dB) against a full-level title theme, and
SFX ranged 0.11-1.00.

Policy:
- BGM (assets/audio/bgm/<stick>/*.wav): one gain PER DIRECTORY —
  0.85 / max peak in that stick's set, capped at 14x — so every
  stick lands loud while its internal mix relationships (stem
  variants, quiet loom vs road tunes) are preserved exactly.
- SFX (assets/audio/sfx/**/*.wav + loose wavs): PER FILE peak
  normalize to 0.70 — one-shots want uniform punch; per-call
  volume scalars in SFXBank remain the mixing layer.

16-bit PCM only; anything else is skipped and reported. Idempotent
enough in practice (already-normalized files get gain ~1).

Run from repo root: python3 godot/tools/audio/normalize_bank.py
"""
import wave, struct, glob, os, math

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
BGM_TARGET = 0.85
SFX_TARGET = 0.70
MAX_GAIN = 14.0


def read_wav(path):
    w = wave.open(path, "rb")
    params = w.getparams()
    data = w.readframes(params.nframes)
    w.close()
    if params.sampwidth != 2:
        return None, None
    vals = list(struct.unpack("<%dh" % (len(data) // 2), data))
    return params, vals


def write_wav(path, params, vals):
    w = wave.open(path, "wb")
    w.setparams(params)
    w.writeframes(struct.pack("<%dh" % len(vals), *vals))
    w.close()


def peak_of(vals):
    return max(1, max(abs(v) for v in vals)) / 32768.0


def apply_gain(vals, gain):
    return [max(-32768, min(32767, int(v * gain))) for v in vals]


def main():
    skipped = []
    # ── BGM · per-directory gain ──
    for d in sorted(glob.glob(os.path.join(ROOT, "assets", "audio", "bgm", "*"))):
        if not os.path.isdir(d):
            continue
        files = sorted(glob.glob(os.path.join(d, "*.wav")))
        if not files:
            continue
        loaded = {}
        dir_peak = 0.0
        for f in files:
            params, vals = read_wav(f)
            if vals is None:
                skipped.append(f)
                continue
            loaded[f] = (params, vals)
            dir_peak = max(dir_peak, peak_of(vals))
        if not loaded or dir_peak <= 0.0:
            continue
        gain = min(BGM_TARGET / dir_peak, MAX_GAIN)
        if abs(gain - 1.0) < 0.05:
            continue
        for f, (params, vals) in loaded.items():
            write_wav(f, params, apply_gain(vals, gain))
        print("bgm %-14s gain %5.2fx (dir peak %.2f)" % (os.path.basename(d), gain, dir_peak))
    # ── SFX · per-file normalize ──
    sfx_glob = glob.glob(os.path.join(ROOT, "assets", "audio", "sfx", "**", "*.wav"), recursive=True)
    n = 0
    for f in sorted(sfx_glob):
        params, vals = read_wav(f)
        if vals is None:
            skipped.append(f)
            continue
        p = peak_of(vals)
        gain = min(SFX_TARGET / p, MAX_GAIN)
        if abs(gain - 1.0) < 0.08:
            continue
        write_wav(f, params, apply_gain(vals, gain))
        n += 1
    print("sfx normalized:", n, "files")
    if skipped:
        print("skipped (not 16-bit pcm):", len(skipped))


if __name__ == "__main__":
    main()
