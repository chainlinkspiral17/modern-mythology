#!/usr/bin/env python3
"""sprinkler_chug — the Meadowlark Circle impact sprinklers (2026-09-24).

The user: "sprinklers should do the rotational chug-chug-chug thing".
An impact sprinkler's arm knocks the jet aside on every step — a dry
"tch" with a small metallic ring — "tch · tch · tch" across the arc,
then a fast ratchet "brrrrt" as the head swings back, over the hiss
of the spray. This renders a seamless loop of three heads out of
phase (a block of lawns, not one yard) at 22050 Hz mono 16-bit, the
project's draft rate (lore/_AUDIO_PLAYBOOK.md). Stdlib only.

Events are ADDED MODULO the loop length, so the loop is seamless by
construction.

    python3 godot/tools/audio/sprinkler_chug.py [out.wav]
default out: godot/assets/audio/sfx/env/sprinkler_chug_loop.wav
"""
import math
import os
import random
import struct
import sys
import wave

SR = 22050
LOOP_S = 8.0
N = int(SR * LOOP_S)
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "..", "assets", "audio", "sfx", "env", "sprinkler_chug_loop.wav"))


def tick(rng, gain, ring_hz):
    """One arm strike: a noise burst, a damped metallic ring, a small thump."""
    n = int(SR * 0.055)
    out = [0.0] * n
    hp_prev_in = hp_prev_out = 0.0
    for i in range(n):
        t = i / SR
        env = math.exp(-t * 90.0)
        noise = rng.uniform(-1.0, 1.0)
        # one-pole high-pass: the dry "tch"
        hp = 0.86 * (hp_prev_out + noise - hp_prev_in)
        hp_prev_in, hp_prev_out = noise, hp
        ring = math.sin(2 * math.pi * ring_hz * t) * math.exp(-t * 55.0)
        thump = math.sin(2 * math.pi * 170.0 * t) * math.exp(-t * 70.0)
        out[i] = gain * (0.62 * hp * env + 0.30 * ring + 0.22 * thump)
    return out


def add(buf, start, clip):
    for i, v in enumerate(clip):
        buf[(start + i) % N] += v


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else OUT
    rng = random.Random(1402)
    buf = [0.0] * N
    # three heads: (tick period s, ticks per sweep, return ratchet s, phase s, gain, ring Hz)
    heads = ((0.160, 18, 0.90, 0.00, 1.00, 2350.0),
             (0.172, 16, 0.80, 2.70, 0.62, 2150.0),
             (0.151, 21, 1.00, 5.10, 0.45, 2550.0))
    for period, n_ticks, ret_s, phase, gain, ring in heads:
        t = phase
        end = phase + LOOP_S
        while t < end:
            for k in range(n_ticks):
                add(buf, int(t * SR), tick(rng, gain * rng.uniform(0.85, 1.05), ring * rng.uniform(0.98, 1.02)))
                t += period * rng.uniform(0.96, 1.04)
            # the return: a fast ratchet, quieter and quicker
            r_end = t + ret_s
            while t < r_end:
                add(buf, int(t * SR), tick(rng, gain * 0.34, ring * 1.1))
                t += 0.038
            t += 0.25
    # the spray: a soft band-limited hiss under everything
    lp = 0.0
    for i in range(N):
        lp += 0.18 * (rng.uniform(-1.0, 1.0) - lp)
        buf[i] += 0.05 * lp
    peak = max(abs(v) for v in buf) or 1.0
    scale = (10 ** (-6.0 / 20.0)) / peak           # peak at -6 dBFS
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with wave.open(out, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(b"".join(struct.pack("<h", int(max(-1.0, min(1.0, v * scale)) * 32767)) for v in buf))
    print("sprinkler_chug: wrote %s (%.1f s, %d Hz mono)" % (out, LOOP_S, SR))


if __name__ == "__main__":
    main()
