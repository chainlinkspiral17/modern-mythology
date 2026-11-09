#!/usr/bin/env python3
"""sound_gen.py — generation hooks for the Sound Studio: MIDI to finished audio.

Three stages, each one a hook you can swap:

  COMPOSE   brief -> score        Claude writes a score (JSON, see SCORE FORMAT),
                                  or any other model / person does; a .mid from a
                                  DAW works too.
  RENDER    score/.mid -> audio   builtin synth (numpy), fluidsynth + SoundFont,
                                  or any command you configure.
  GENERATE  brief -> audio        outside audio models that skip MIDI entirely
                                  (ElevenLabs music / SFX / speech, or any HTTP
                                  endpoint or command in sound_providers.json).

Everything lands in the audio library (../../audio_library by default) as a
candidate; nothing here touches the game. Assign candidates in the Sound Studio.

Usage:
  python3 tools/sound_gen.py palette                       # builtin instruments
  python3 tools/sound_gen.py providers                     # hooks + readiness
  python3 tools/sound_gen.py brief music:vol5_two_speeds   # composer brief + score spec
  python3 tools/sound_gen.py compose music:vol5_two_speeds # Claude -> score -> .mid -> .mp3
  python3 tools/sound_gen.py render path/to/x.score.json   # or path/to/x.mid
  python3 tools/sound_gen.py generate music:vol5_two_speeds --provider elevenlabs_music
  python3 tools/sound_gen.py generate sfx:ui_back --provider elevenlabs_sfx

SCORE FORMAT ("mm-score/1") — what a composer hook returns:
  {
    "format": "mm-score/1",
    "title": "Faucet Metronome", "key": "D dorian",
    "tempo": 54,                 # beats per minute
    "length_beats": 108,         # loop length; the reverb tail folds back into the head
    "tracks": [
      { "name": "kitchen pad", "instrument": "warm_pad",
        "gain": 0.8, "pan": -0.2, "reverb": 0.5,
        "loop_beats": 0,         # >0 repeats `notes` every N beats to the end
        "notes": [[0, 16, 50, 70], ...] }   # [start_beat, dur_beats, midi_pitch, velocity]
    ],
    "master": { "reverb": 0.35, "loop": true }
  }

Requirements: ffmpeg on PATH (encode + loudness). numpy for the builtin renderer.
The Claude hook needs `pip install anthropic` and credentials (ANTHROPIC_API_KEY
or an `ant auth login` profile). tools/run_sound_studio.sh sets up both.
"""

import argparse
import json
import math
import os
import re
import shlex
import shutil
import struct
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
import wave
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent          # godot/
ROOT = REPO.parent
TOOLS = REPO / "tools"
LIB_DEFAULT = ROOT / "audio_library"
SCENES_ROOT = REPO / "resources" / "scenes"
MUSIC_CATALOG = REPO / "resources" / "music_catalog.json"
SFX_CATALOG = REPO / "resources" / "sfx_catalog.json"
CANON_PATH = REPO / "resources" / "sonic_canon.json"
PROVIDERS_PATH = TOOLS / "sound_providers.json"
VOICE_MAP_PATH = TOOLS / "voice_map.json"
SR = 44100
PPQ = 480


class GenError(Exception):
    """A failure the user can act on; the message is shown as-is."""


# ── Instrument palette ─────────────────────────────────────────────────────
# name: (GM program or None, GM drum note or None, default reverb send, blurb)
INSTRUMENTS = {
    "warm_pad":  (89, None, 0.55, "Slow detuned pad, soft attack. The default held tone."),
    "glass_pad": (92, None, 0.65, "Bowed-glass sine cluster with an airy octave. Slow."),
    "sine_pad":  (88, None, 0.45, "Near-pure sine pad. The vol 6 68-degree HVAC register."),
    "drone":     (95, None, 0.50, "Low sustained drone with slow beating. Roots below C3."),
    "sub":       (38, None, 0.05, "Sine sub bass. Felt more than heard."),
    "strings":   (48, None, 0.50, "Soft string ensemble, slight vibrato."),
    "organ":     (19, None, 0.45, "Reed / pump organ. Hymn fragments from another room."),
    "piano":     (0,  None, 0.40, "Felted upright piano. After-hours, sparse."),
    "epiano":    (4,  None, 0.40, "Soft FM electric piano."),
    "bell":      (14, None, 0.55, "FM bell. Brass call bell, milestone chimes."),
    "pluck":     (24, None, 0.35, "Plucked nylon string (Karplus-Strong)."),
    "bass":      (33, None, 0.10, "Round finger bass."),
    "drip":      (115, None, 0.50, "Water drip: a tuned tick with a falling pitch. Use pitches 80-96."),
    "tick":      (None, 76, 0.25, "Clock tick / wood block. Pitch nudges the tone."),
    "kick_soft": (None, 36, 0.10, "Soft felt kick. Rare; club thud or jukebox B-side only."),
    "brush":     (None, 38, 0.25, "Brushed noise hit."),
    "noise_bed": (122, None, 0.20, "Sustained filtered noise: room tone / air / HVAC. Pitch sets the band (36 rumble, 60 air, 84 hiss)."),
    "rain":      (96, None, 0.25, "Rain on a roof: hiss plus droplets. Velocity = density. Pitch ignored."),
    "cicadas":   (123, None, 0.20, "Dusk cicada wash, slow swells. Pitch ignored."),
    "hum":       (94, None, 0.10, "Fluorescent / mains hum with buzz harmonics. Pitch 35 is about 60 Hz."),
    "crackle":   (120, None, 0.15, "Sparse crackle: tape, vinyl, kitchen fire. Velocity = density."),
}
FIELD_LAYERS = ("noise_bed", "rain", "cicadas", "hum", "crackle")
_PROGRAM_TO_INST = {v[0]: k for k, v in INSTRUMENTS.items() if v[0] is not None}
_DRUM_TO_INST = {35: "kick_soft", 36: "kick_soft", 38: "brush", 40: "brush", 42: "brush",
                 44: "brush", 46: "brush", 69: "brush", 70: "brush", 37: "tick", 75: "tick",
                 76: "tick", 77: "tick"}
_GM_FAMILY = [  # (last program in family, builtin instrument)
    (3, "piano"), (7, "epiano"), (15, "bell"), (23, "organ"), (31, "pluck"), (39, "bass"),
    (51, "strings"), (55, "glass_pad"), (79, "organ"), (87, "epiano"), (95, "warm_pad"),
    (103, "glass_pad"), (111, "pluck"), (119, "drip"), (127, "noise_bed"),
]


def _instrument_for_program(prog):
    if prog in _PROGRAM_TO_INST:
        return _PROGRAM_TO_INST[prog]
    for last, name in _GM_FAMILY:
        if prog <= last:
            return name
    return "warm_pad"


# ── Score validation ───────────────────────────────────────────────────────

def _num(v, default, lo, hi):
    try:
        v = float(v)
    except (TypeError, ValueError):
        return default
    if math.isnan(v) or math.isinf(v):
        return default
    return max(lo, min(hi, v))


def validate_score(score):
    """Normalize a score in place-safe fashion; returns (score, warnings)."""
    if not isinstance(score, dict) or not isinstance(score.get("tracks"), list):
        raise GenError("not a score: expected an object with a \"tracks\" list")
    warns = []
    out = {
        "format": "mm-score/1",
        "title": str(score.get("title") or "untitled"),
        "key": str(score.get("key") or ""),
        "tempo": _num(score.get("tempo"), 60.0, 20.0, 240.0),
        "tracks": [],
        "master": {},
    }
    for k in ("id", "intent", "composer"):
        if score.get(k):
            out[k] = str(score[k])
    m = score.get("master") if isinstance(score.get("master"), dict) else {}
    out["master"] = {"reverb": _num(m.get("reverb"), 0.35, 0.0, 1.0),
                     "loop": bool(m.get("loop", True))}
    end = 0.0
    for ti, tr in enumerate(score["tracks"]):
        if not isinstance(tr, dict):
            continue
        inst = str(tr.get("instrument") or "warm_pad")
        if inst not in INSTRUMENTS:
            warns.append(f"track {ti}: unknown instrument {inst!r}, using warm_pad")
            inst = "warm_pad"
        notes = []
        for n in tr.get("notes") or []:
            if not isinstance(n, (list, tuple)) or len(n) < 3:
                warns.append(f"track {ti}: dropped malformed note {n!r}")
                continue
            start = _num(n[0], 0.0, 0.0, 1e6)
            dur = _num(n[1], 1.0, 0.02, 1e5)
            pitch = int(round(_num(n[2], 60, 0, 127)))
            vel = int(round(_num(n[3] if len(n) > 3 else 80, 80, 1, 127)))
            notes.append([round(start, 4), round(dur, 4), pitch, vel])
        notes.sort()
        loop_beats = _num(tr.get("loop_beats"), 0.0, 0.0, 1e5)
        t = {"name": str(tr.get("name") or f"track {ti + 1}"), "instrument": inst,
             "gain": _num(tr.get("gain"), 0.8, 0.0, 1.5),
             "pan": _num(tr.get("pan"), 0.0, -1.0, 1.0),
             "reverb": _num(tr.get("reverb"), INSTRUMENTS[inst][2], 0.0, 1.0),
             "loop_beats": loop_beats, "notes": notes}
        if notes and not loop_beats:
            end = max(end, max(n[0] + n[1] for n in notes))
        out["tracks"].append(t)
    if not any(t["notes"] for t in out["tracks"]):
        raise GenError("score has no notes")
    length = _num(score.get("length_beats"), 0.0, 0.0, 1e6)
    if length <= 0:
        length = end or max(t["loop_beats"] for t in out["tracks"])
        warns.append(f"length_beats missing; using {length:g}")
    out["length_beats"] = length
    secs = length * 60.0 / out["tempo"]
    if secs > 600:
        raise GenError(f"score is {secs:.0f}s long; the ceiling is 600s")
    return out, warns


def expand_notes(score):
    """Per track, the concrete note list with loop_beats unrolled to the piece length."""
    length = score["length_beats"]
    out = []
    for tr in score["tracks"]:
        notes = tr["notes"]
        lb = tr["loop_beats"]
        if lb > 0 and notes:
            rolled, k = [], 0
            while k * lb < length - 1e-9:
                for s, d, p, v in notes:
                    if s < lb and s + k * lb < length:
                        rolled.append([s + k * lb, d, p, v])
                k += 1
            notes = rolled
        else:
            notes = [n for n in notes if n[0] < length]
        out.append(notes)
    return out


def score_seconds(score):
    return score["length_beats"] * 60.0 / score["tempo"]


# ── MIDI write / read ──────────────────────────────────────────────────────

def _vlq(n):
    n = int(n)
    out = [n & 0x7F]
    n >>= 7
    while n:
        out.append((n & 0x7F) | 0x80)
        n >>= 7
    return bytes(reversed(out))


def _meta(kind, data):
    return bytes([0xFF, kind]) + _vlq(len(data)) + data


def write_midi(score, path):
    """Standard MIDI File, format 1. Track names carry an [mm:instrument] tag so
    read_midi() round-trips the builtin palette exactly; any DAW ignores the tag."""
    score, _ = validate_score(score)
    tempo_us = int(round(60_000_000 / score["tempo"]))
    conductor = (b"\x00" + _meta(0x03, score["title"].encode("utf-8")[:120])
                 + b"\x00" + _meta(0x51, struct.pack(">I", tempo_us)[1:])
                 + b"\x00" + _meta(0x58, bytes([4, 2, 24, 8]))
                 + _vlq(int(score["length_beats"] * PPQ)) + _meta(0x2F, b""))
    chunks = [conductor]
    melodic = [c for c in range(16) if c != 9]
    mi = 0
    for tr, notes in zip(score["tracks"], expand_notes(score)):
        prog, drum, _, _ = INSTRUMENTS[tr["instrument"]]
        if drum is not None:
            ch = 9
        else:
            ch = melodic[mi % len(melodic)]
            mi += 1
        events = []  # (tick, order, bytes)
        for s, d, p, v in notes:
            pitch = drum if drum is not None else p
            on = int(round(s * PPQ))
            off = max(on + 1, int(round((s + d) * PPQ)))
            events.append((on, 1, bytes([0x90 | ch, pitch, v])))
            events.append((off, 0, bytes([0x80 | ch, pitch, 0])))
        events.sort(key=lambda e: (e[0], e[1]))
        name = f"{tr['name']} [mm:{tr['instrument']}]".encode("utf-8")[:120]
        body = b"\x00" + _meta(0x03, name)
        if prog is not None:
            body += b"\x00" + bytes([0xC0 | ch, prog])
        body += b"\x00" + bytes([0xB0 | ch, 7, int(min(127, tr["gain"] * 100))])
        body += b"\x00" + bytes([0xB0 | ch, 10, int(round(64 + tr["pan"] * 63))])
        last = 0
        for tick, _, data in events:
            body += _vlq(tick - last) + data
            last = tick
        body += b"\x00" + _meta(0x2F, b"")
        chunks.append(body)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        f.write(b"MThd" + struct.pack(">IHHH", 6, 1, len(chunks), PPQ))
        for c in chunks:
            f.write(b"MTrk" + struct.pack(">I", len(c)) + c)
    return path


def read_midi(path):
    """Parse a Standard MIDI File (format 0/1) into a score. Tempo changes are
    honoured by converting everything to seconds, so the result has tempo 60."""
    data = Path(path).read_bytes()
    if data[:4] != b"MThd":
        raise GenError(f"{Path(path).name}: not a MIDI file")
    hlen, _fmt, ntrk, div = struct.unpack(">IHHH", data[4:14])
    if div & 0x8000:
        raise GenError("SMPTE-timed MIDI files are not supported")
    pos = 8 + hlen
    tempos = [(0, 500000)]
    raw = []   # (tick, track_index, channel, kind, a, b)
    names, tags, programs = {}, {}, {}
    for ti in range(ntrk):
        if data[pos:pos + 4] != b"MTrk":
            break
        tlen = struct.unpack(">I", data[pos + 4:pos + 8])[0]
        p, end = pos + 8, pos + 8 + tlen
        pos = end
        tick, status = 0, 0
        while p < end:
            delta = 0
            while True:
                b = data[p]; p += 1
                delta = (delta << 7) | (b & 0x7F)
                if not b & 0x80:
                    break
            tick += delta
            b = data[p]
            if b == 0xFF:
                kind = data[p + 1]; p += 2
                ln = 0
                while True:
                    c = data[p]; p += 1
                    ln = (ln << 7) | (c & 0x7F)
                    if not c & 0x80:
                        break
                payload = data[p:p + ln]; p += ln
                if kind == 0x51 and ln == 3:
                    tempos.append((tick, int.from_bytes(payload, "big")))
                elif kind == 0x03:
                    nm = payload.decode("utf-8", "replace")
                    m = re.search(r"\[mm:([a-z_]+)\]", nm)
                    if m and m.group(1) in INSTRUMENTS:
                        tags[ti] = m.group(1)
                    names[ti] = re.sub(r"\s*\[mm:[a-z_]+\]", "", nm).strip()
                continue
            if b in (0xF0, 0xF7):
                p += 1
                ln = 0
                while True:
                    c = data[p]; p += 1
                    ln = (ln << 7) | (c & 0x7F)
                    if not c & 0x80:
                        break
                p += ln
                continue
            if b & 0x80:
                status = b; p += 1
            hi, ch = status & 0xF0, status & 0x0F
            if hi in (0xC0, 0xD0):
                a = data[p]; p += 1
                if hi == 0xC0:
                    programs[(ti, ch)] = a
                continue
            a, v = data[p], data[p + 1]; p += 2
            if hi == 0x90 and v > 0:
                raw.append((tick, ti, ch, 1, a, v))
            elif hi == 0x80 or (hi == 0x90 and v == 0):
                raw.append((tick, ti, ch, 0, a, 0))
    tempos.sort()

    def to_sec(tick):
        sec, last_tick, us = 0.0, 0, 500000
        for t, u in tempos:
            if t >= tick:
                break
            sec += (t - last_tick) * us / 1e6 / div
            last_tick, us = t, u
        return sec + (tick - last_tick) * us / 1e6 / div

    raw.sort(key=lambda e: (e[0], e[3]))
    open_notes, tracks = {}, {}
    for tick, ti, ch, on, pitch, vel in raw:
        key = (ti, ch, pitch)
        if on:
            open_notes.setdefault(key, []).append((tick, vel))
        elif open_notes.get(key):
            t0, v0 = open_notes[key].pop(0)
            s, e = to_sec(t0), to_sec(tick)
            if ch == 9:
                inst = tags.get(ti) or _DRUM_TO_INST.get(pitch, "tick")
            else:
                inst = tags.get(ti) or _instrument_for_program(programs.get((ti, ch), 0))
            tr = tracks.setdefault((ti, ch, inst), [])
            tr.append([round(s, 4), round(max(0.02, e - s), 4), 72 if ch == 9 else pitch, v0])
    if not tracks:
        raise GenError(f"{Path(path).name}: no notes found")
    end = max(n[0] + n[1] for notes in tracks.values() for n in notes)
    score = {"format": "mm-score/1", "title": Path(path).stem, "tempo": 60,
             "length_beats": round(end + 0.5, 2),
             "tracks": [{"name": names.get(ti) or f"ch{ch + 1} {inst}", "instrument": inst,
                         "notes": notes}
                        for (ti, ch, inst), notes in sorted(tracks.items())],
             "master": {"loop": False}}
    return validate_score(score)[0]


def load_score_file(path):
    path = Path(path)
    if path.suffix.lower() in (".mid", ".midi"):
        return read_midi(path)
    try:
        return validate_score(json.loads(path.read_text(encoding="utf-8")))[0]
    except json.JSONDecodeError as e:
        raise GenError(f"{path.name}: invalid JSON ({e})")


# ── Builtin synth (numpy) ──────────────────────────────────────────────────

def _np():
    try:
        import numpy as np
        return np
    except ImportError:
        raise GenError("the builtin renderer needs numpy. Start the studio with "
                       "tools/run_sound_studio.sh (it installs numpy into a private venv), "
                       "or pick the fluidsynth renderer.")


_TABLES = {}
TABLE_N = 4096


def _table(np, amps):
    if amps not in _TABLES:
        ph = np.arange(TABLE_N) / TABLE_N * 2 * np.pi
        w = np.zeros(TABLE_N)
        for k, a in enumerate(amps, 1):
            if a:
                w += a * np.sin(k * ph)
        w /= max(1e-9, np.abs(w).max())
        _TABLES[amps] = np.concatenate([w, w[:1]]).astype(np.float32)
    return _TABLES[amps]


def _harm(freq, kmax, fn):
    k_hi = max(1, min(kmax, int(SR * 0.45 / freq)))
    return tuple(round(fn(k), 5) for k in range(1, k_hi + 1))


def _osc(np, table, freq, n, phase0=0.0, vib=None):
    if vib is None:
        ph = phase0 + freq * np.arange(n) / SR
    else:
        ph = phase0 + np.cumsum(freq * (1.0 + vib)) / SR
    ph = (ph % 1.0) * TABLE_N
    i = ph.astype(np.int32)
    f = (ph - i).astype(np.float32)
    return table[i] * (1 - f) + table[i + 1] * f


def _adsr(np, n, dur, a, d, s, r):
    a = min(a, max(0.004, dur * 0.45))
    d = min(d, max(0.004, dur - a))
    t = np.arange(n) / SR
    hold = max(a + d + 1e-4, dur)
    return np.interp(t, [0, a, a + d, hold, hold + r], [0, 1, s, s, 0]).astype(np.float32)


def _shaped_noise(np, n, rng, shape):
    """White noise with an arbitrary magnitude response shape(freqs_hz)."""
    nfft = 1 << max(10, (n - 1).bit_length())
    spec = np.fft.rfft(rng.standard_normal(nfft))
    spec *= shape(np.fft.rfftfreq(nfft, 1 / SR))
    x = np.fft.irfft(spec)[:n]
    return (x / max(1e-9, np.abs(x).max())).astype(np.float32)


def _band(np, lo, hi, soft=0.5):
    def shape(f):
        f = np.maximum(f, 1.0)
        return 1.0 / (1 + (lo / f) ** (2 / soft)) / (1 + (f / hi) ** (2 / soft))
    return shape


def _wander(np, n, rng, rate=0.15, depth=0.3):
    """Slow random amplitude drift in [1-depth, 1]."""
    pts = max(4, int(n / SR * rate * 4) + 4)
    ctl = rng.random(pts)
    x = np.interp(np.linspace(0, pts - 1, n), np.arange(pts), ctl)
    return (1 - depth + depth * x).astype(np.float32)


def _synth_note(np, inst, pitch, dur, vel, rng):
    """One mono note as float32, including its release tail."""
    f = 440.0 * 2 ** ((pitch - 69) / 12)
    v = vel / 127.0
    ph = lambda: float(rng.random())

    if inst in ("warm_pad", "glass_pad", "sine_pad", "drone", "strings", "organ", "bass", "sub", "hum"):
        spec = {
            "warm_pad":  (lambda k: 1 / k ** (2.1 - 0.7 * v), 14, (-7, 0, 6), (1.8, 1.0, 0.8, 2.6)),
            "glass_pad": (lambda k: (1, 0, .3, 0, .12, 0, .05)[k - 1] if k <= 7 else 0, 7, (-4, 4), (2.5, 1.0, 0.85, 3.6)),
            "sine_pad":  (lambda k: (1, .08, .02)[k - 1] if k <= 3 else 0, 3, (-1.5, 1.5), (2.0, 0.8, 0.9, 2.6)),
            "drone":     (lambda k: 1 / k ** 1.25, 10, (-5, 3), (3.0, 1.5, 0.85, 4.0)),
            "strings":   (lambda k: 1 / k ** (1.5 - 0.4 * v), 20, (-11, -4, 5, 12), (0.5, 0.6, 0.8, 0.9)),
            "organ":     (lambda k: (1, .6, .5, .3, 0, .2, 0, .15)[k - 1] if k <= 8 else 0, 8, (-2, 2), (0.08, 0.2, 0.9, 0.25)),
            "bass":      (lambda k: 1 / k ** 2.0, 8, (0,), (0.012, 0.4, 0.6, 0.16)),
            "sub":       (lambda k: 1.0 if k == 1 else 0, 1, (0,), (0.08, 0.3, 0.85, 0.6)),
            "hum":       (lambda k: (1, .5, .35, .2, .25, .1, .12)[k - 1] if k <= 7 else (0.02 if k % 2 else 0.008), 30, (0,), (1.5, 0.5, 0.95, 2.0)),
        }[inst]
        fn, kmax, cents, (a, d, s, r) = spec
        n = int((dur + r) * SR)
        table = _table(np, _harm(f, kmax, fn))
        vib = None
        if inst == "strings":
            t = np.arange(n) / SR
            vib = 0.003 * np.minimum(1, t / 0.6) * np.sin(2 * np.pi * 5.1 * t + ph() * 6.28)
        x = np.zeros(n, np.float32)
        for c in cents:
            x += _osc(np, table, f * 2 ** (c / 1200), n, ph(), vib)
        x /= len(cents)
        if inst == "glass_pad":
            x += 0.15 * _osc(np, _table(np, (1.0,)), f * 2.003, n, ph())
        if inst in ("warm_pad", "glass_pad", "drone", "organ", "sine_pad"):
            rate = 5.5 if inst == "organ" else 0.09 + 0.1 * ph()
            depth = 0.04 if inst == "organ" else 0.14
            x *= 1 - depth * (0.5 + 0.5 * np.sin(2 * np.pi * rate * np.arange(n) / SR + ph() * 6.28)).astype(np.float32)
        trim = 0.4 if inst == "hum" else 1.0     # a field layer, not a voice
        return x * _adsr(np, n, dur, a, d, s, r) * (0.35 + 0.65 * v) * trim

    if inst in ("epiano", "bell"):
        tail = 3.5 if inst == "bell" else 0.5
        n = int((dur + tail) * SR)
        t = np.arange(n) / SR
        if inst == "bell":
            idx = 4.5 * v * np.exp(-t / 1.1) + 0.2
            x = np.sin(2 * np.pi * f * t + idx * np.sin(2 * np.pi * f * 3.5 * t))
            x += 0.35 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t / 0.7)
            env = np.exp(-t / 2.2)
        else:
            idx = 2.4 * v * np.exp(-t / 0.55) + 0.25
            x = np.sin(2 * np.pi * f * t + idx * np.sin(2 * np.pi * f * t))
            x += 0.18 * v * np.sin(2 * np.pi * f * 14 * t) * np.exp(-t / 0.05)
            env = np.exp(-t / 2.4)
        env *= np.minimum(1, t / 0.004)
        rel = np.clip(1 - (t - dur) / tail, 0, 1) if inst == "epiano" else np.clip(1 - (t - dur - 2.5) / 1.0, 0, 1)
        return (x * env * rel * (0.3 + 0.7 * v)).astype(np.float32)

    if inst == "piano":
        n = int((dur + 0.45) * SR)
        t = np.arange(n) / SR
        x = np.zeros(n)
        for k in range(1, min(12, int(SR * 0.45 / f)) + 1):
            fk = k * f * math.sqrt(1 + 0.0004 * k * k)
            x += (1 / k ** (1.9 - 0.6 * v)) * np.sin(2 * np.pi * fk * t + ph() * 6.28) \
                * np.exp(-t * (0.5 + 0.3 * k) * (f / 220) ** 0.35)
        env = np.minimum(1, t / 0.006) * np.clip(1 - (t - dur) / 0.45, 0, 1)
        return (x * env * (0.3 + 0.7 * v) * 0.8).astype(np.float32)

    if inst == "pluck":
        n = int((min(dur, 6.0) + 0.3) * SR)
        period = max(2, int(round(SR / f)))
        buf = rng.random(period) * 2 - 1
        buf = v * buf + (1 - v) * 0.5 * (buf + np.roll(buf, 1))   # softer pick = duller attack
        out = np.empty(n, np.float32)
        decay = 0.996 - 0.002 * (f / 880)
        for i in range(0, n, period):
            out[i:i + period] = buf[:max(0, min(period, n - i))]
            buf = decay * 0.5 * (buf + np.roll(buf, 1))
        t = np.arange(n) / SR
        return out * np.clip(1 - (t - dur) / 0.3, 0, 1).astype(np.float32) * (0.3 + 0.7 * v)

    if inst == "drip":
        n = int(0.5 * SR)
        t = np.arange(n) / SR
        fi = f * (1 + 1.6 * np.exp(-t / 0.010))
        x = np.sin(2 * np.pi * np.cumsum(fi) / SR) * np.exp(-t / 0.055)
        x += 0.35 * np.sin(2 * np.pi * f * 0.5 * t) * np.exp(-t / 0.12) * np.minimum(1, t / 0.02)
        x[: int(0.002 * SR)] += 0.25 * (rng.random(int(0.002 * SR)) * 2 - 1)
        return (x * (0.25 + 0.75 * v)).astype(np.float32)

    if inst == "tick":
        n = int(0.12 * SR)
        t = np.arange(n) / SR
        x = np.sin(2 * np.pi * (1400 + 14 * (pitch - 60)) * t) * np.exp(-t / 0.012)
        x += 0.5 * _shaped_noise(np, n, rng, _band(np, 2500, 7000)) * np.exp(-t / 0.006)
        return (x * (0.25 + 0.75 * v) * 0.7).astype(np.float32)

    if inst == "kick_soft":
        n = int(0.3 * SR)
        t = np.arange(n) / SR
        fi = 46 + 50 * np.exp(-t / 0.035)
        x = np.sin(2 * np.pi * np.cumsum(fi) / SR) * np.exp(-t / 0.11) * np.minimum(1, t / 0.004)
        return (x * (0.3 + 0.7 * v)).astype(np.float32)

    if inst == "brush":
        n = int(0.28 * SR)
        t = np.arange(n) / SR
        x = _shaped_noise(np, n, rng, _band(np, 1800, 8000)) * np.exp(-t / 0.07) * np.minimum(1, t / 0.008)
        return (x * (0.2 + 0.8 * v) * 0.6).astype(np.float32)

    # Sustained field layers. Synthesised stand-ins for field recordings.
    a, r = 3.0, 4.0
    n = int((dur + r) * SR)
    t = np.arange(n) / SR
    if inst == "noise_bed":
        centre = 440.0 * 2 ** ((pitch - 69) / 12) * 2
        x = _shaped_noise(np, n, rng, _band(np, centre * 0.45, centre * 2.2, 0.8)) * _wander(np, n, rng)
    elif inst == "rain":
        x = 0.55 * _shaped_noise(np, n, rng, _band(np, 1500, 9000)) * _wander(np, n, rng, 0.2, 0.35)
        drops = int(n / SR * (2 + 22 * v))
        pip_n = int(0.03 * SR)
        pt = np.arange(pip_n) / SR
        for start in rng.integers(0, max(1, n - pip_n), drops):
            fr = 1800 + 4200 * rng.random()
            x[start:start + pip_n] += (0.25 + 0.5 * rng.random()) * np.sin(2 * np.pi * fr * pt) * np.exp(-pt / 0.006)
    elif inst == "cicadas":
        x = _shaped_noise(np, n, rng, _band(np, 4200, 7200, 0.3))
        x *= 0.3 + 0.7 * (0.5 + 0.5 * np.sin(2 * np.pi * 31 * t)) ** 2
        x *= 0.45 + 0.55 * (0.5 + 0.5 * np.sin(2 * np.pi * 0.07 * t + ph() * 6.28)) ** 2
    else:  # crackle
        x = np.zeros(n)
        hits = int(n / SR * (0.6 + 9 * v))
        pip_n = int(0.012 * SR)
        pt = np.arange(pip_n) / SR
        for start in rng.integers(0, max(1, n - pip_n), hits):
            fr = 900 + 5000 * rng.random()
            x[start:start + pip_n] += (0.2 + 0.8 * rng.random() ** 2) * np.sin(2 * np.pi * fr * pt) * np.exp(-pt / 0.0015)
        x += 0.04 * _shaped_noise(np, n, rng, _band(np, 300, 4000))
    return (x * _adsr(np, n, dur, a, 0.5, 1.0, r) * (0.25 + 0.75 * v) * 0.5).astype(np.float32)


def _reverb_ir(np, rng, seconds=3.2):
    n = int(seconds * SR)
    t = np.arange(n) / SR
    ir = []
    for _ in range(2):
        x = _shaped_noise(np, n, rng, _band(np, 180, 5200, 0.9)).astype(np.float64)
        x *= np.exp(-t / (seconds / 6.9)) * np.minimum(1, t / 0.012)
        for tap, g in ((0.011, 0.5), (0.019, 0.4), (0.031, 0.3), (0.047, 0.22)):
            x[int((tap + 0.004 * rng.random()) * SR)] += g
        ir.append(x / math.sqrt(np.sum(x * x)))
    return ir


def _convolve(np, x, ir, block=1 << 16):
    nfft = 1 << (block + len(ir) - 1).bit_length()
    spec = np.fft.rfft(ir, nfft)
    out = np.zeros(len(x) + nfft, np.float64)
    for i in range(0, len(x), block):
        out[i:i + nfft] += np.fft.irfft(np.fft.rfft(x[i:i + block], nfft) * spec, nfft)
    return out[:len(x) + len(ir)]


def render_builtin(score, wav_path, progress=None):
    """Render a score with the builtin synth to a 16-bit stereo WAV. Returns the mix
    report: per-track level in dB relative to the loudest track, so a composer that
    can't listen (a model) can still balance the cue."""
    np = _np()
    score, _ = validate_score(score)
    seed = sum(ord(c) for c in score["title"]) + int(score["tempo"] * 10)
    rng = np.random.default_rng(seed)
    beat = 60.0 / score["tempo"]
    length = int(score_seconds(score) * SR)
    tail = int(8.0 * SR)
    total = length + tail
    dry = [np.zeros(total, np.float32), np.zeros(total, np.float32)]
    wet = [np.zeros(total, np.float32), np.zeros(total, np.float32)]
    cache = {}
    all_notes = expand_notes(score)
    n_notes = sum(len(n) for n in all_notes) or 1
    done = 0
    energy = []
    for tr, notes in zip(score["tracks"], all_notes):
        inst = tr["instrument"]
        energy.append(0.0)
        stochastic = inst in FIELD_LAYERS or inst in ("pluck", "tick", "brush")
        for s, d, p, v in notes:
            dur = d * beat
            key = (inst, p, round(dur, 3), v // 8)
            if stochastic or key not in cache:
                x = _synth_note(np, inst, p, dur, v, rng)
                if not stochastic:
                    cache[key] = x
            else:
                x = cache[key]
            i0 = int(s * beat * SR)
            x = x[: max(0, total - i0)]
            pan = max(-1.0, min(1.0, tr["pan"] + (rng.random() - 0.5) * 0.12))
            ang = (pan + 1) * math.pi / 4
            gl, gr = math.cos(ang) * tr["gain"], math.sin(ang) * tr["gain"]
            sl = slice(i0, i0 + len(x))
            dry[0][sl] += x * gl
            dry[1][sl] += x * gr
            wet[0][sl] += x * gl * tr["reverb"]
            wet[1][sl] += x * gr * tr["reverb"]
            energy[-1] += float(np.dot(x, x)) * tr["gain"] ** 2
            done += 1
            if progress and done % 16 == 0:
                progress(0.75 * done / n_notes, f"synth {done}/{n_notes} notes")
    if progress:
        progress(0.78, "reverb")
    ir = _reverb_ir(np, rng)
    amount = score["master"]["reverb"] * 2.2
    out = []
    for c in range(2):
        other = 1 - c
        send = wet[c] * 0.8 + wet[other] * 0.2
        y = dry[c].astype(np.float64)
        if amount > 0:
            y = y + amount * _convolve(np, send, ir[c])[:total]
        out.append(y)
    if score["master"]["loop"]:
        for c in range(2):
            out[c][:tail] += out[c][length:length + tail]
            out[c] = out[c][:length]
    else:
        fade = np.clip((total - np.arange(total)) / (2.0 * SR), 0, 1)
        out = [y * fade for y in out]
    peak = max(1e-9, max(float(np.abs(y).max()) for y in out))
    pcm = np.stack([y / peak * 0.89 for y in out], axis=1)
    pcm = (np.clip(pcm, -1, 1) * 32767).astype("<i2")
    wav_path = Path(wav_path)
    wav_path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(wav_path), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    if progress:
        progress(0.9, "mastering")
    top = max(energy) or 1.0
    return [{"name": tr["name"], "instrument": tr["instrument"],
             "db": round(10 * math.log10(max(e, 1e-12) / top), 1)}
            for tr, e in zip(score["tracks"], energy)]


# ── ffmpeg: master + encode, transcode, probe ──────────────────────────────

def have(tool):
    return shutil.which(tool) is not None


def _ffmpeg(args, what):
    if not have("ffmpeg"):
        raise GenError("ffmpeg not found on PATH (needed to encode audio)")
    p = subprocess.run(["ffmpeg", "-hide_banner", "-nostdin", "-y"] + args,
                       capture_output=True, text=True)
    if p.returncode != 0:
        raise GenError(f"ffmpeg failed while {what}: {p.stderr.strip().splitlines()[-1] if p.stderr.strip() else 'unknown error'}")
    return p.stderr


CODEC = {".mp3": ["-c:a", "libmp3lame", "-q:a", "2"],
         ".ogg": ["-c:a", "libvorbis", "-q:a", "6"],
         ".wav": ["-c:a", "pcm_s16le"],
         ".flac": ["-c:a", "flac"]}


def transcode(src, dst, mono=False):
    dst = Path(dst)
    if dst.suffix.lower() not in CODEC:
        raise GenError(f"can't encode {dst.suffix}; use .mp3, .ogg or .wav")
    dst.parent.mkdir(parents=True, exist_ok=True)
    _ffmpeg(["-i", str(src), "-vn", "-ar", str(SR)] + (["-ac", "1"] if mono else [])
            + CODEC[dst.suffix.lower()] + [str(dst)], f"encoding {dst.name}")
    return dst


def master(src, dst, lufs=-16.0):
    """Normalise to a loudness target with one static gain (no pumping), then encode."""
    err = _ffmpeg(["-i", str(src), "-af", f"loudnorm=I={lufs}:TP=-1.5:LRA=11:print_format=json",
                   "-f", "null", "-"], "measuring loudness")
    gain = 0.0
    m = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", err, re.S)
    if m:
        st = json.loads(m.group(0))
        try:
            gain = min(lufs - float(st["input_i"]), -1.0 - float(st["input_tp"]))
        except (ValueError, KeyError):
            gain = 0.0
    dst = Path(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    _ffmpeg(["-i", str(src), "-af", f"volume={gain:.2f}dB", "-ar", str(SR)]
            + CODEC[dst.suffix.lower()] + [str(dst)], f"encoding {dst.name}")
    return dst


def probe_duration(path):
    path = Path(path)
    if path.suffix.lower() == ".wav":
        try:
            with wave.open(str(path), "rb") as w:
                return w.getnframes() / float(w.getframerate())
        except (wave.Error, EOFError):
            pass
    if not have("ffprobe"):
        return None
    p = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=nw=1:nk=1", str(path)], capture_output=True, text=True)
    try:
        return float(p.stdout.strip())
    except ValueError:
        return None


# ── Renderers (score/.mid -> audio) ────────────────────────────────────────

def find_soundfont(cfg):
    sf = (cfg or {}).get("soundfont") or os.environ.get("MM_SOUNDFONT", "")
    if sf and Path(sf).expanduser().exists():
        return str(Path(sf).expanduser())
    for d in ("/usr/share/soundfonts", "/usr/share/sounds/sf2", str(Path.home() / ".local/share/soundfonts")):
        for f in sorted(Path(d).glob("*.sf[23]")) if Path(d).is_dir() else []:
            return str(f)
    return ""


def renderers(config=None):
    cfg = (config or load_providers()).get("renderers", {})
    out = {"builtin": {"label": "Builtin synth", "ready": True, "why": ""}}
    try:
        _np()
    except GenError:
        out["builtin"].update(ready=False, why="numpy missing — start with tools/run_sound_studio.sh")
    sf = find_soundfont(cfg.get("fluidsynth"))
    ok = have("fluidsynth") and bool(sf)
    out["fluidsynth"] = {"label": "FluidSynth + SoundFont", "ready": ok,
                         "why": "" if ok else ("fluidsynth not installed" if not have("fluidsynth")
                                               else "no SoundFont found; set renderers.fluidsynth.soundfont")}
    for name, c in cfg.items():
        if isinstance(c, dict) and c.get("type") == "command" and c.get("enabled", True):
            out[name] = {"label": c.get("label", name), "ready": bool(c.get("cmd")),
                         "why": "" if c.get("cmd") else "no cmd configured"}
    return out


def render(source, out_path, renderer="builtin", lufs=None, progress=None, config=None):
    """source: score dict, or a path to .score.json / .mid. Writes out_path (mp3/ogg/wav).
    Returns {"out", "midi", "seconds", "renderer"}; the .mid is written beside the output
    when the source was a score."""
    config = config or load_providers()
    out_path = Path(out_path)
    if lufs is None:
        lufs = load_canon().get("loudness_lufs", -16)
    score = source if isinstance(source, dict) else load_score_file(source)
    score, _ = validate_score(score)
    src_is_midi = not isinstance(source, dict) and Path(source).suffix.lower() in (".mid", ".midi")
    midi = Path(source) if src_is_midi else out_path.with_suffix(".mid")
    if not src_is_midi:
        write_midi(score, midi)
    with tempfile.TemporaryDirectory(prefix="mm_render_") as td:
        wav = Path(td) / "render.wav"
        levels = []
        if renderer == "builtin":
            levels = render_builtin(score, wav, progress)
        elif renderer == "fluidsynth":
            sf = find_soundfont(config.get("renderers", {}).get("fluidsynth"))
            if not have("fluidsynth") or not sf:
                raise GenError("fluidsynth renderer needs the fluidsynth binary and a SoundFont "
                               "(set renderers.fluidsynth.soundfont in sound_providers.json)")
            p = subprocess.run(["fluidsynth", "-ni", "-g", "0.7", "-r", str(SR), "-F", str(wav), sf, str(midi)],
                               capture_output=True, text=True)
            if p.returncode != 0 or not wav.exists():
                raise GenError("fluidsynth failed: " + (p.stderr.strip().splitlines() or ["unknown error"])[-1])
        else:
            c = config.get("renderers", {}).get(renderer)
            if not c or c.get("type") != "command" or not c.get("cmd"):
                raise GenError(f"unknown renderer {renderer!r}")
            sketch = Path(td) / "sketch.wav"
            if "{sketch}" in c["cmd"]:
                render_builtin(score, sketch, progress)
            run_command(c["cmd"], {"midi": midi, "sketch": sketch, "out": wav, "seconds": int(score_seconds(score)),
                                   "title": score["title"]})
            if not wav.exists():
                raise GenError(f"renderer {renderer!r} finished without writing {{out}}")
        master(wav, out_path, lufs)
    if progress:
        progress(1.0, "done")
    return {"out": out_path, "midi": midi, "seconds": probe_duration(out_path), "renderer": renderer,
            "levels": levels}


# ── Briefs ─────────────────────────────────────────────────────────────────

_CANON = None


def load_canon():
    global _CANON
    if _CANON is None:
        try:
            _CANON = json.loads(CANON_PATH.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            _CANON = {"canon": "", "volume_brief": {}, "loudness_lufs": -16}
    return _CANON


def load_slot(slot_id):
    """Resolve "music:<id>", "sfx:<id>" or "voice:<scene_id>:<node>" to a dict."""
    kind, _, rest = slot_id.partition(":")
    if kind == "music":
        for t in json.loads(MUSIC_CATALOG.read_text(encoding="utf-8")):
            if t.get("id") == rest:
                return {"slot": slot_id, "kind": "music", "id": rest, "title": t.get("title", rest),
                        "vol": t.get("vol", 0), "desc": t.get("desc", ""), "target": t.get("src", ""),
                        "chapters": t.get("chapters", []), "chars": t.get("chars", [])}
    elif kind == "sfx":
        for s in json.loads(SFX_CATALOG.read_text(encoding="utf-8")):
            if s.get("id") == rest:
                return {"slot": slot_id, "kind": "sfx", "id": rest, "title": s.get("label", rest),
                        "desc": s.get("brief", ""), "target": s.get("src", "")}
    elif kind == "voice":
        scene_id, _, idx = rest.rpartition(":")
        for p in SCENES_ROOT.glob(f"vol*/{scene_id}.json"):
            data = json.loads(p.read_text(encoding="utf-8"))
            node = data.get("nodes", [])[int(idx)]
            char = "_narrator" if node.get("t") == "narrate" else (node.get("char") or "_narrator")
            return {"slot": slot_id, "kind": "voice", "id": f"{scene_id}/{int(idx):03d}", "scene": scene_id,
                    "index": int(idx), "char": char, "text": (node.get("text") or "").strip(),
                    "title": f"{char} · {scene_id} #{int(idx):03d}", "vol": data.get("vol", 0)}
    raise GenError(f"unknown slot {slot_id!r}")


def sfx_seconds(brief, default=2.0):
    m = re.search(r"(\d+(?:\.\d+)?)\s*(ms|s)\b(?!.*\d\s*(?:ms|s)\b)", brief or "")
    if not m:
        return default
    val = float(m.group(1)) / (1000 if m.group(2) == "ms" else 1)
    return max(0.5, min(22.0, val))


def audio_prompt(slot, seconds=None):
    """Short prompt for text-to-audio models (they don't want the whole canon)."""
    if slot["kind"] == "music":
        vb = load_canon().get("volume_brief", {}).get(str(slot.get("vol", "")), "")
        return (f"{slot['title']}. {slot['desc']} {vb} Instrumental ambient underscore for a literary "
                "visual novel: held tones and texture rather than melody, a faint field-recording layer, "
                "no vocals, no drums, no swells or drops, melancholy and restrained, loops naturally, "
                "sits quietly under spoken dialogue.").strip()
    if slot["kind"] == "sfx":
        return f"{slot['desc']} Single dry one-shot sound effect, close and intimate, no music, no reverb wash."
    return slot.get("text", "")


SCORE_SPEC = """SCORE FORMAT (mm-score/1). Return one JSON object:
  title          string
  key            string, informational ("D dorian")
  intent         one or two sentences on what you were going for
  tempo          beats per minute
  length_beats   loop length in beats (length_beats * 60 / tempo = seconds)
  tracks[]       name, instrument, gain 0..1, pan -1..1, reverb 0..1, loop_beats, notes
                 notes are [start_beat, duration_beats, midi_pitch, velocity 1..127]
                 loop_beats > 0 repeats that track's notes every N beats until the end
                 (write an ostinato once); 0 means the notes are placed literally.
  master         reverb 0..1 (0.35 is a medium room), loop true|false

The renderer loops the piece: whatever rings past length_beats is folded back onto
the opening, so let the last notes ring out rather than cutting them, and avoid a hard
event exactly on beat 0 that would double with the fold."""


def palette_text():
    return "\n".join(f"  {name:<10} {v[3]}" for name, v in INSTRUMENTS.items())


def composer_brief(slot, seconds=120):
    """Full brief for a composing model: canon, slot, palette, score format."""
    canon = load_canon()
    vb = canon.get("volume_brief", {}).get(str(slot.get("vol", "")), "")
    parts = [canon.get("canon", ""), "",
             f"TRACK: {slot['title']}  (id {slot['id']}, volume {slot.get('vol', '?')})",
             f"VOLUME BRIEF: {vb}" if vb else "",
             f"DESCRIPTION: {slot.get('desc') or '—'}"]
    if slot.get("chapters"):
        parts.append("PLAYS IN: " + ", ".join(slot["chapters"]))
    if slot.get("chars"):
        parts.append("CHARACTERS: " + ", ".join(c for c in slot["chars"] if c != "_narrator"))
    parts += [f"TARGET LENGTH: about {int(seconds)} seconds, loopable.", "",
              "INSTRUMENT PALETTE (builtin synth; these are the only instrument names):",
              palette_text(), "", SCORE_SPEC]
    return "\n".join(p for p in parts if p is not None)


COMPOSER_SYSTEM = """You are the composer for Modern Mythology, a literary visual novel. \
You write underscore as a symbolic score that a synthesiser renders, so every choice you make \
is heard literally: there is no performer to add taste afterwards.

What makes these cues work is restraint. They sit under read dialogue for minutes at a time \
and loop, so a melody that announces itself becomes an irritant by the third pass. Think in \
held tones, slow voice-leading between two or three chords, and one small recurring detail \
that gives the room its identity (a drip, a tick, a distant bell). Leave real silence in the \
upper register.

Practical guidance for this renderer:
- Pads and drones want long notes (8 to 32 beats) that overlap by a beat or two so chords \
cross-fade instead of stepping.
- Keep the low end to one voice at a time: a drone or sub root, not both stacked in fifths.
- Every cue carries one field layer (noise_bed, rain, cicadas, hum or crackle) held for the \
whole piece at low gain. It is the room the music lives in.
- Velocity is expression: 35 to 70 for almost everything; reserve anything above 90.
- Gain is per track and chords add up: a four-note pad chord lands roughly 12 dB above a \
single piano note at the same gain. Start pads near 0.3, single-line voices (piano, pluck, \
bell, drip) at 0.6 to 0.9, the low voice near 0.3, and field layers at 0.1 to 0.3.
- Use loop_beats for repeating figures instead of writing them out.
- Three to six tracks is typical. More is rarely better.

Follow the project canon and the track description in the brief; when they conflict with \
your instincts, the canon wins. Fill `intent` with what you were going for so the producer \
can judge the render against it."""

SCORE_SCHEMA = {
    "type": "object", "additionalProperties": False,
    "required": ["title", "key", "intent", "tempo", "length_beats", "tracks", "master"],
    "properties": {
        "title": {"type": "string"}, "key": {"type": "string"}, "intent": {"type": "string"},
        "tempo": {"type": "number"}, "length_beats": {"type": "number"},
        "tracks": {"type": "array", "items": {
            "type": "object", "additionalProperties": False,
            "required": ["name", "instrument", "gain", "pan", "reverb", "loop_beats", "notes"],
            "properties": {
                "name": {"type": "string"},
                "instrument": {"type": "string", "enum": list(INSTRUMENTS)},
                "gain": {"type": "number"}, "pan": {"type": "number"}, "reverb": {"type": "number"},
                "loop_beats": {"type": "number"},
                "notes": {"type": "array", "items": {"type": "array", "items": {"type": "number"}}},
            }}},
        "master": {"type": "object", "additionalProperties": False, "required": ["reverb", "loop"],
                   "properties": {"reverb": {"type": "number"}, "loop": {"type": "boolean"}}},
    },
}


# ── Providers ──────────────────────────────────────────────────────────────

def load_providers():
    try:
        return json.loads(PROVIDERS_PATH.read_text(encoding="utf-8"))
    except OSError:
        return {"providers": {}, "renderers": {}}
    except json.JSONDecodeError as e:
        raise GenError(f"sound_providers.json is not valid JSON: {e}")


def _env_refs(obj):
    return set(re.findall(r"\$\{([A-Z0-9_]+)\}", json.dumps(obj)))


def providers(config=None):
    """{name: {label, kinds, type, makes, ready, why}} for every configured hook."""
    config = config or load_providers()
    out = {}
    for name, c in config.get("providers", {}).items():
        if not isinstance(c, dict) or c.get("enabled") is False:
            continue
        ready, why = True, ""
        if c.get("type") == "claude":
            try:
                import anthropic  # noqa: F401
            except ImportError:
                ready, why = False, "pip install anthropic (run_sound_studio.sh does it)"
        elif c.get("type") == "http":
            missing = [e for e in _env_refs(c) if not os.environ.get(e)]
            if missing:
                ready, why = False, "set " + ", ".join(sorted(missing))
        elif c.get("type") == "command":
            if not c.get("cmd"):
                ready, why = False, "no cmd configured"
        else:
            ready, why = False, f"unknown type {c.get('type')!r}"
        out[name] = {"label": c.get("label", name), "kinds": c.get("kinds", []), "type": c.get("type"),
                     "makes": "score" if c.get("type") == "claude" or c.get("makes") == "score" else "audio",
                     "ready": ready, "why": why, "note": c.get("note", "")}
    return out


def compose_with_claude(slot, cfg, seconds=120, direction="", progress=None):
    """COMPOSE hook: Claude writes an mm-score/1 for the slot. Returns the raw score dict."""
    try:
        import anthropic
    except ImportError:
        raise GenError("the Claude hook needs the anthropic package: pip install anthropic "
                       "(tools/run_sound_studio.sh installs it)")
    brief = composer_brief(slot, seconds)
    if direction:
        brief += "\n\nPRODUCER'S DIRECTION FOR THIS TAKE: " + direction.strip()
    if progress:
        progress(0.05, "Claude is composing")
    client = anthropic.Anthropic()
    try:
        # Streaming: a full score is a long output, and a non-streaming request that
        # large can outlive the HTTP timeout. Server-side fallbacks re-run the request
        # on another model if a safety classifier declines it.
        with client.beta.messages.stream(
            model=cfg.get("model", "claude-opus-5-5"),
            max_tokens=int(cfg.get("max_tokens", 64000)),
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
            thinking={"type": "adaptive"},
            system=COMPOSER_SYSTEM,
            output_config={"effort": cfg.get("effort", "high"),
                           "format": {"type": "json_schema", "schema": SCORE_SCHEMA}},
            messages=[{"role": "user", "content": brief}],
        ) as stream:
            msg = stream.get_final_message()
    except anthropic.AuthenticationError:
        raise GenError("Claude: no valid credentials. Set ANTHROPIC_API_KEY or run `ant auth login`.")
    except anthropic.PermissionDeniedError as e:
        raise GenError(f"Claude: this key can't use {cfg.get('model', 'claude-opus-5-5')} ({e.message})")
    except anthropic.NotFoundError:
        raise GenError(f"Claude: model {cfg.get('model')!r} not found; check sound_providers.json")
    except anthropic.RateLimitError:
        raise GenError("Claude: rate limited. Wait a minute and try again.")
    except anthropic.BadRequestError as e:
        raise GenError(f"Claude rejected the request: {e.message}")
    except anthropic.APIStatusError as e:
        raise GenError(f"Claude API error {e.status_code}: {e.message}")
    except anthropic.APIConnectionError:
        raise GenError("Claude: network error reaching the API.")
    if msg.stop_reason == "refusal":
        raise GenError("Claude declined this request.")
    if msg.stop_reason == "max_tokens":
        raise GenError("Claude ran out of output room mid-score; raise max_tokens or shorten the piece.")
    text = next((b.text for b in msg.content if b.type == "text"), "")
    try:
        score = json.loads(text)
    except json.JSONDecodeError:
        raise GenError("Claude returned something that isn't a JSON score.")
    score["composer"] = f"claude ({msg.model})"
    return score


def _fill(obj, vars_):
    """Substitute {placeholders} and ${ENV} through a JSON-ish structure. A string that is
    exactly one numeric placeholder becomes a number, so "{ms}" can sit in a JSON body."""
    if isinstance(obj, dict):
        return {k: _fill(v, vars_) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_fill(v, vars_) for v in obj]
    if not isinstance(obj, str):
        return obj
    m = re.fullmatch(r"\{([a-z_]+)\}", obj)
    if m and m.group(1) in vars_ and isinstance(vars_[m.group(1)], (int, float, bool)):
        return vars_[m.group(1)]
    out = re.sub(r"\$\{([A-Z0-9_]+)\}", lambda mm: os.environ.get(mm.group(1), ""), obj)
    return re.sub(r"\{([a-z_]+)\}", lambda mm: str(vars_.get(mm.group(1), mm.group(0))), out)


def run_command(template, vars_, timeout=1800):
    args = [str(_fill(a, {k: str(v) for k, v in vars_.items()})) for a in shlex.split(template)]
    try:
        p = subprocess.run(args, capture_output=True, text=True, timeout=timeout, cwd=str(REPO))
    except FileNotFoundError:
        raise GenError(f"command not found: {args[0]}")
    except subprocess.TimeoutExpired:
        raise GenError(f"command timed out after {timeout}s: {args[0]}")
    if p.returncode != 0:
        raise GenError(f"{args[0]} exited {p.returncode}: " + ((p.stderr or p.stdout).strip().splitlines() or [""])[-1])
    return p.stdout


def _voice_id(char_key):
    try:
        vm = json.loads(VOICE_MAP_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return "", {}
    chars = vm.get("characters", {})
    entry = chars.get(char_key) or chars.get("_narrator") or {}
    settings = dict(vm.get("default_voice_settings", {}))
    settings.update(entry.get("voice_settings", {}))
    return entry.get("voice_id", ""), {"model": vm.get("model", "eleven_v3"), "voice_settings": settings}


def generate_audio(slot, name, cfg, out_stem, seconds=None, direction="", progress=None):
    """GENERATE hook: run an http or command provider. Returns the written audio path."""
    if slot["kind"] == "sfx":
        seconds = seconds or sfx_seconds(slot.get("desc"))
    seconds = float(seconds or 120)
    prompt = audio_prompt(slot, seconds)
    if direction:
        prompt = (prompt + " " + direction.strip()).strip()
    vars_ = {"prompt": prompt, "text": slot.get("text", prompt), "seconds": seconds,
             "seconds_int": int(round(seconds)), "ms": int(seconds * 1000), "title": slot["title"],
             "id": slot["id"], "kind": slot["kind"]}
    if slot["kind"] == "voice":
        key = slot["char"].strip().lower().replace(" ", "_")
        vid, extra = _voice_id(key)
        if "{voice_id}" in json.dumps(cfg) and not vid:
            raise GenError(f"no voice_id for {key!r} in tools/voice_map.json")
        vars_.update(voice_id=vid, model=extra.get("model", ""), char=key)
    out = Path(str(out_stem) + "." + cfg.get("ext", "mp3"))
    out.parent.mkdir(parents=True, exist_ok=True)
    if progress:
        progress(0.1, f"{name}: generating")
    if cfg["type"] == "command":
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as f:
            f.write(prompt)
        try:
            run_command(cfg["cmd"], dict(vars_, prompt_file=f.name, out=out))
        finally:
            os.unlink(f.name)
        if not out.exists():
            raise GenError(f"{name}: command finished without writing {{out}} ({out.name})")
        return out
    missing = [e for e in _env_refs(cfg) if not os.environ.get(e)]
    if missing:
        raise GenError(f"{name}: set {', '.join(sorted(missing))} in the environment first")
    body = _fill(cfg.get("body", {}), vars_)
    if slot["kind"] == "voice" and cfg.get("voice_settings_from_map"):
        body["voice_settings"] = _voice_id(vars_["char"])[1].get("voice_settings", {})
    req = urllib.request.Request(_fill(cfg["url"], vars_), data=json.dumps(body).encode("utf-8"),
                                 method=cfg.get("method", "POST"))
    req.add_header("Content-Type", "application/json")
    for k, v in _fill(cfg.get("headers", {}), vars_).items():
        req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=int(cfg.get("timeout", 600))) as resp:
            data = resp.read()
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")[:300].replace("\n", " ")
        raise GenError(f"{name}: HTTP {e.code} {detail}")
    except urllib.error.URLError as e:
        raise GenError(f"{name}: network error ({e.reason})")
    if len(data) < 512:
        raise GenError(f"{name}: response too small to be audio ({len(data)} bytes)")
    out.write_bytes(data)
    return out


def stamp():
    return time.strftime("%m%d_%H%M%S")


def run_job(slot_id, provider, library=LIB_DEFAULT, seconds=None, direction="", renderer="builtin",
            fmt="mp3", progress=None, config=None):
    """One end-to-end generation for a slot. Returns the files it added to the library."""
    config = config or load_providers()
    cfg = config.get("providers", {}).get(provider)
    if not cfg:
        raise GenError(f"unknown provider {provider!r}; see `sound_gen.py providers`")
    slot = load_slot(slot_id)
    if slot["kind"] not in cfg.get("kinds", []):
        raise GenError(f"{provider} doesn't make {slot['kind']}")
    library = Path(library)
    tag = f"{provider}_{stamp()}"
    if slot["kind"] == "voice":
        stem = library / "takes" / slot["scene"] / f"{slot['index']:03d}_{tag}"
    else:
        stem = library / slot["kind"] / slot["id"] / f"{slot['id']}__{tag}"
    if cfg["type"] == "claude" or cfg.get("makes") == "score":
        seconds = float(seconds or 120)
        if cfg["type"] == "claude":
            raw = compose_with_claude(slot, cfg, seconds, direction, progress)
        else:
            with tempfile.TemporaryDirectory(prefix="mm_score_") as td:
                brief_file, out_file = Path(td) / "brief.txt", Path(td) / "score.json"
                brief_file.write_text(composer_brief(slot, seconds) + ("\n\nDIRECTION: " + direction if direction else ""),
                                      encoding="utf-8")
                run_command(cfg["cmd"], {"prompt_file": brief_file, "out": out_file, "seconds": int(seconds),
                                         "id": slot["id"], "title": slot["title"]})
                if not out_file.exists():
                    raise GenError(f"{provider}: command finished without writing {{out}}")
                raw = json.loads(out_file.read_text(encoding="utf-8"))
        score, warns = validate_score(raw)
        score["id"] = slot["id"]
        score_path = library / "scores" / slot["id"] / f"{slot['id']}__{tag}.score.json"
        save_score(score, score_path)
        sub = (lambda f, m: progress(0.3 + 0.7 * f, m)) if progress else None
        res = render(score, Path(str(stem) + "." + fmt), renderer, progress=sub, config=config)
        midi = score_path.with_name(score_path.name.replace(".score.json", ".mid"))
        shutil.move(str(res["midi"]), midi)
        return {"audio": res["out"], "score": score_path, "midi": midi, "warnings": warns,
                "intent": score.get("intent", ""), "levels": res["levels"]}
    out = generate_audio(slot, provider, cfg, stem, seconds, direction, progress)
    if progress:
        progress(1.0, "done")
    return {"audio": out, "warnings": []}


def save_score(score, path):
    """Scores are hand-editable, so notes go one per line rather than one number per line."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(score, indent=1, ensure_ascii=False)
    text = re.sub(r"\[\s*(-?[\d.]+),\s*(-?[\d.]+),\s*(-?[\d.]+),\s*(-?[\d.]+)\s*\]", r"[\1, \2, \3, \4]", text)
    path.write_text(text + "\n", encoding="utf-8")
    return path


# ── CLI ────────────────────────────────────────────────────────────────────

def _cli_progress(frac, msg):
    print(f"\r  {int(frac * 100):3d}%  {msg:<40}", end="", file=sys.stderr, flush=True)


def _print_levels(levels):
    if levels:
        print("mix (dB relative to the loudest track):")
        for lv in levels:
            print(f"  {lv['db']:6.1f}  {lv['name']}  [{lv['instrument']}]")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("palette", help="list builtin instruments")
    sub.add_parser("providers", help="list generation hooks and whether each is ready")
    b = sub.add_parser("brief", help="print the brief for a slot (paste into any model)")
    b.add_argument("slot")
    b.add_argument("--seconds", type=float, default=120)
    b.add_argument("--audio", action="store_true", help="short text-to-audio prompt instead of the composer brief")
    r = sub.add_parser("render", help="score.json or .mid -> mp3")
    r.add_argument("source")
    r.add_argument("--out", help="output file (.mp3/.ogg/.wav). Default: audio_library/music/<id>/")
    r.add_argument("--renderer", default="builtin")
    r.add_argument("--library", default=str(LIB_DEFAULT))
    for name, hlp in (("compose", "Claude (or a score hook) -> score -> .mid -> audio"),
                      ("generate", "outside audio model -> audio")):
        g = sub.add_parser(name, help=hlp)
        g.add_argument("slot", help="music:<track_id>, sfx:<slot_id> or voice:<scene_id>:<node>")
        g.add_argument("--provider", default="claude_score" if name == "compose" else None, required=name == "generate")
        g.add_argument("--seconds", type=float)
        g.add_argument("--direction", default="", help="extra direction for this take")
        g.add_argument("--renderer", default="builtin")
        g.add_argument("--format", default="mp3", choices=("mp3", "ogg", "wav"))
        g.add_argument("--library", default=str(LIB_DEFAULT))
    args = ap.parse_args()
    try:
        if args.cmd == "palette":
            print(palette_text())
        elif args.cmd == "providers":
            for name, p in providers().items():
                print(f"{name:<20} {'/'.join(p['kinds']):<16} {p['type']:<8} {'ready' if p['ready'] else 'NOT READY: ' + p['why']}")
            print()
            for name, p in renderers().items():
                print(f"renderer {name:<11} {'ready' if p['ready'] else 'NOT READY: ' + p['why']}")
        elif args.cmd == "brief":
            slot = load_slot(args.slot)
            print(audio_prompt(slot, args.seconds) if args.audio or slot["kind"] != "music"
                  else composer_brief(slot, args.seconds))
        elif args.cmd == "render":
            src = Path(args.source)
            score = load_score_file(src)
            sid = score.get("id") or re.sub(r"(__.*|\.score)$", "", src.stem)
            out = Path(args.out) if args.out else Path(args.library) / "music" / sid / (re.sub(r"\.score$", "", src.stem) + ".mp3")
            res = render(src, out, args.renderer, progress=_cli_progress)
            if src.suffix == ".json":
                mid = src.with_name(src.name.replace(".score.json", ".mid"))
                shutil.move(str(res["midi"]), mid)
                res["midi"] = mid
            print(f"\n{res['out']}  ({res['seconds']:.1f}s, {res['renderer']})\n{res['midi']}")
            _print_levels(res["levels"])
        else:
            res = run_job(args.slot, args.provider, args.library, args.seconds, args.direction,
                          args.renderer, args.format, _cli_progress)
            print()
            for k in ("audio", "score", "midi"):
                if res.get(k):
                    print(f"{k:<6} {res[k]}")
            if res.get("intent"):
                print("intent", res["intent"])
            for w in res.get("warnings", []):
                print("warn  ", w)
            _print_levels(res.get("levels", []))
    except GenError as e:
        print(f"\nerror: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
