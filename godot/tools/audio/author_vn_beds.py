#!/usr/bin/env python3
"""author_vn_beds.py — the volumes that played vol5's music (2026-09-11).

WHAT THIS FOUND. Thirty-six catalog tracks are NAMED BY A CHAPTER and
had no file at the path the catalog gave. GameEngine hands those
entries to AudioMgr.set_chapter(); the file isn't there, the chapter's
track list resolves to nothing, and AudioMgr falls through to "the
unlocked playlist" — which is vol5's four beds. So volumes 1, 2, 3, 4,
6 and 7 have all been playing D'Ambrosio's at Dawn and the cicadas,
wherever you were.

TWO CAUSES, and the second one matters more:
  · 26 were never rendered at all. The Kwik Stop's sodium
    fluorescents, Substation Nine's transformer, the hymn from another
    room — a description and nothing else.
  · 10 WERE RENDERED, as .wav, and sat on disk the whole time while
    their catalog entries pointed at a .mp3 or .ogg nobody ever made
    (see ON_DISK). Same silence, better music, worse bug. Those are
    repointed, never re-authored — this pass overwrote all ten once
    before the git status was read, which is the lesson.

For the 26, the catalog's own `desc` is the spec: each entry already
says what its track is made of. One composition each, through the
project's synth (slowstick_synth.py, stdlib-only, deterministic).

DRAFT 1 CHOICES, and what draft 2 should revisit:
  · 22050 Hz mono. These are beds — drone, hum, rain, pad — and the
    rate halves 74 MB of WAV to 37. The hiss-forward ones (rest-stop
    wind, the cicada field, the thermal above Kestrel) are the ones to
    listen to first: if they read dull on the Deck, re-render those at
    44100 by dropping `sample_rate` from the spec.
  · ~40 s at 52-64 BPM, no fade. AudioMgr's chapter refill restarts
    the track when it ends, so a bed is heard as a loop with a seam at
    the top. Draft 2: author the last bar to land on the first bar's
    voicing, or give each chapter two beds so the seam is a change.
  · Room tone, not melody. Only the hymn fragment, the Casio in the
    comic shop, the El Rancho guitar and the four stings carry a line;
    everything else is texture, because that is what the catalog's own
    prose asks for.

    python3 godot/tools/audio/author_vn_beds.py --list
    python3 godot/tools/audio/author_vn_beds.py [track_id …]

Writes `godot/tools/audio/compositions/vn/<id>.json` (editable, the
authoring artifact) and `godot/assets/audio/bgm/<id>.wav`.
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SYNTH = os.path.join(HERE, "slowstick_synth.py")
COMPS = os.path.join(HERE, "compositions", "vn")
OUT = os.path.join(ROOT, "godot", "assets", "audio", "bgm")

SR = 22050


def n(pitch, bar, beat, dur, vel):
    return {"pitch": pitch, "bar": bar, "beat": beat, "dur": dur, "vel": vel}


def hold(pitches, bar, dur, vel):
    """A chord held from the top of `bar`."""
    return [n(p, bar, 1, dur, vel) for p in pitches]


def track(instrument, gain, notes):
    return {"instrument": instrument, "gain": gain, "notes": notes}


# ── the beds ───────────────────────────────────────────────────────
# Each entry: id, tempo, and the layers. The `note` is the authorial
# read of the catalog description — keep them in sync.
BEDS = {}


def bed(tid, tempo, note, layers):
    BEDS[tid] = {"tempo": tempo, "note": note, "layers": layers}


# ── beds that WERE rendered, under a name the catalog didn't use ───
# Ten tracks existed on disk as .wav the whole time while their catalog
# entries pointed at a .mp3 / .ogg that was never made. Same silence,
# different cause, and the more embarrassing one: the music was there.
# Nothing is authored for these — only the `src` is repointed. Do NOT
# add specs for them; rendering over an authored track is how this pass
# nearly destroyed ten of them.
ON_DISK = (
    "vol1_club_thump", "vol1_diner_ambient", "vol1_dream_drone",
    "vol1_drive_night", "vol2_ambient", "vol2_rest_stop_wind",
    "vol2_seagash_drone", "vol6_ambient", "vol7_apartment_rain",
    "vol7_rain_on_roof",
)


# ── VOLUME 1 · the diner at the crossroads ─────────────────────────
bed("vol1_ambient", 58,
    "The diner at the crossroads. D minor, the room's own hum under a "
    "pad that turns over twice and a single high note that answers "
    "nothing.",
    [track("ambient_drone", 0.30, [n("D2", 1, 1, 40, 0.42)]),
     track("fluorescent_hum", 0.10, [n("A2", 1, 1, 40, 0.30)]),
     track("slowstick_pad", 0.20,
           hold(["D3", "F3", "A3"], 1, 20, 0.28)
           + hold(["A#2", "D3", "F3"], 6, 20, 0.26)),
     track("soft_sine", 0.14, [n("A4", 4, 3, 6, 0.22),
                               n("F4", 9, 1, 8, 0.20)])])

bed("vol1_pharmacy", 54,
    "The pharmacy mirror. Bright fixtures and a tritone that will "
    "not resolve — the room is fine, the reflection is not.",
    [track("fluorescent_hum", 0.20, [n("C3", 1, 1, 38, 0.38)]),
     track("ambient_drone", 0.24, [n("A2", 1, 1, 38, 0.34)]),
     track("slowstick_pad", 0.18,
           hold(["A3", "C4", "E4"], 1, 18, 0.24)
           + hold(["A3", "C4", "D#4"], 6, 18, 0.24)),
     track("soft_sine", 0.13, [n("D#5", 4, 1, 7, 0.20),
                               n("D#5", 9, 1, 6, 0.18)])])

bed("vol1_painting", 60,
    "The painting. F major, warm, and the melody is four notes long "
    "because that is all anyone gets to see of it.",
    [track("ambient_drone", 0.20, [n("F2", 1, 1, 40, 0.30)]),
     track("slowstick_pad", 0.24,
           hold(["F3", "A3", "C4"], 1, 16, 0.28)
           + hold(["D3", "F3", "A3"], 5, 16, 0.26)
           + hold(["A#2", "D3", "F3"], 9, 14, 0.26)),
     track("soft_sine", 0.20,
           [n("C5", 2, 1, 3, 0.26), n("A4", 2, 4, 3, 0.24),
            n("F4", 3, 3, 5, 0.24), n("G4", 10, 1, 6, 0.22)])])

bed("vol1_title", 64,
    "Crossroads · title. The five-note statement, once plain and "
    "once underneath.",
    [track("ambient_drone", 0.24, [n("D2", 1, 1, 40, 0.36)]),
     track("slowstick_bass", 0.20,
           [n("D1", 1, 1, 8, 0.30), n("A#0", 5, 1, 8, 0.28),
            n("F1", 9, 1, 8, 0.28)]),
     track("slowstick_pad", 0.20,
           hold(["D3", "F3", "A3"], 1, 16, 0.26)
           + hold(["A#2", "D3", "F3"], 5, 16, 0.24)
           + hold(["F3", "A3", "C4"], 9, 14, 0.24)),
     track("slowstick_lead", 0.20,
           [n("D4", 2, 1, 2, 0.26), n("F4", 2, 3, 2, 0.24),
            n("A4", 3, 1, 3, 0.26), n("G4", 3, 4, 2, 0.22),
            n("F4", 4, 2, 5, 0.24),
            n("D4", 10, 1, 3, 0.18), n("F4", 10, 4, 5, 0.16)])])

bed("vol1_milestone_choice", 60,
    "The choice, resolved. Three notes up and the pad opens to "
    "major. Twenty-five seconds; it is a release, not a theme.",
    [track("slowstick_pad", 0.26,
           hold(["D3", "F3", "A3"], 1, 10, 0.26)
           + hold(["D3", "F#3", "A3"], 4, 12, 0.28)),
     track("ambient_drone", 0.22, [n("D2", 1, 1, 24, 0.34)]),
     track("slowstick_lead", 0.22,
           [n("A4", 3, 3, 2, 0.26), n("C#5", 4, 1, 2, 0.26),
            n("D5", 4, 3, 6, 0.28)])])

# ── VOLUME 2 · the small wood, the falls, the coast ────────────────
bed("vol2_briar_falls_night", 54,
    "Briar Falls after dark. Water in the middle distance, two "
    "chords, nothing arriving.",
    [track("rain", 0.22, [n("C3", 1, 1, 38, 0.28)]),
     track("ambient_drone", 0.26, [n("E2", 1, 1, 38, 0.36)]),
     track("slowstick_pad", 0.18,
           hold(["E3", "G3", "B3"], 1, 18, 0.24)
           + hold(["A2", "C3", "E3"], 6, 18, 0.22)),
     track("soft_sine", 0.11, [n("B4", 8, 3, 5, 0.16)])])

bed("vol2_graveyard_solo", 50,
    "The graveyard. One line, alone, over almost nothing — the solo "
    "is the point.",
    [track("ambient_drone", 0.16, [n("A1", 1, 1, 38, 0.26)]),
     track("soft_sine", 0.26,
           [n("A4", 1, 3, 4, 0.26), n("C5", 2, 3, 3, 0.24),
            n("B4", 3, 2, 5, 0.22), n("E4", 5, 1, 6, 0.24),
            n("G4", 7, 1, 4, 0.22), n("A4", 8, 2, 8, 0.24)])])

bed("vol2_milestone_seagash", 58,
    "Seagash, closed. B minor lifts to B major and holds; the siren "
    "note comes once and stops.",
    [track("ambient_drone", 0.24, [n("B1", 1, 1, 26, 0.34)]),
     track("slowstick_pad", 0.26,
           hold(["B2", "D3", "F#3"], 1, 10, 0.26)
           + hold(["B2", "D#3", "F#3"], 4, 12, 0.28)),
     track("soft_sine", 0.22, [n("F#4", 4, 2, 8, 0.26)])])

# ── VOLUME 3 · the station ─────────────────────────────────────────
bed("vol3_ambient", 60,
    "Station Omega-14. A room whose air is manufactured: hum high in "
    "the mix, a slow arp that is machinery and not music.",
    [track("ambient_drone", 0.30, [n("C1", 1, 1, 40, 0.42)]),
     track("fluorescent_hum", 0.18, [n("C3", 1, 1, 40, 0.34)]),
     track("slowstick_pad", 0.18,
           hold(["C3", "D#3", "G3", "D4"], 1, 22, 0.22)
           + hold(["G#2", "C3", "D#3"], 7, 20, 0.22)),
     track("chiptune_arp", 0.08,
           [n(p, b, be, 0.3, 0.14)
            for b in (4, 9)
            for be, p in ((1, "C5"), (2, "D#5"), (3, "G5"), (4, "D#5"))])])

bed("vol3_call_drop", 56,
    "The call drops. Everything is here and then the line isn't: the "
    "pad and the tone stop mid-bar and the drone keeps going alone.",
    [track("ambient_drone", 0.28, [n("C2", 1, 1, 34, 0.38)]),
     track("slowstick_pad", 0.22, hold(["C3", "D#3", "G3"], 1, 14, 0.26)),
     track("soft_sine", 0.20, [n("G4", 2, 1, 11, 0.24)]),
     track("fluorescent_hum", 0.12, [n("A2", 6, 1, 20, 0.26)])])

bed("vol3_milestone_choice", 54,
    "Decompression. The drone steps down a whole tone and the pad "
    "lets go of it.",
    [track("ambient_drone", 0.28, [n("C2", 1, 1, 12, 0.38),
                                   n("A#1", 4, 1, 14, 0.34)]),
     track("slowstick_pad", 0.24,
           hold(["C3", "D#3", "G3"], 1, 10, 0.26)
           + hold(["A#2", "D3", "F3"], 4, 12, 0.26))])

# ── VOLUME 4 · five AM ─────────────────────────────────────────────
bed("vol4_ambient", 52,
    "Five AM, no one around. Street air very dark, an A minor that "
    "turns once to F major seven and no one hears it.",
    [track("rain", 0.18, [n("D#1", 1, 1, 42, 0.28)]),
     track("ambient_drone", 0.28, [n("A1", 1, 1, 42, 0.40)]),
     track("slowstick_pad", 0.20,
           hold(["A2", "C3", "E3"], 1, 20, 0.26)
           + hold(["F2", "A2", "C3", "E3"], 7, 20, 0.24)),
     track("soft_sine", 0.12, [n("E4", 5, 3, 7, 0.18)])])

bed("vol4_standoff_strings", 56,
    "Five AM strings. A cluster that will not open — A, B-flat and E "
    "together — and a repeated note counting.",
    [track("ambient_drone", 0.26, [n("A1", 1, 1, 40, 0.36)]),
     track("slowstick_pad", 0.24,
           hold(["A2", "A#2", "E3"], 1, 20, 0.28)
           + hold(["A2", "A#2", "F3"], 7, 18, 0.26)),
     track("soft_sine", 0.16,
           [n("E5", b, 1, 1.5, 0.20) for b in (3, 4, 5, 8, 9)])])

bed("vol4_milestone_standoff", 58,
    "The standoff, resolved. The cluster resolves outward and the "
    "line comes down instead of holding.",
    [track("ambient_drone", 0.24, [n("A1", 1, 1, 26, 0.34)]),
     track("slowstick_pad", 0.26,
           hold(["A2", "A#2", "E3"], 1, 8, 0.26)
           + hold(["A2", "C#3", "E3"], 3, 14, 0.28)),
     track("slowstick_lead", 0.20,
           [n("E5", 3, 3, 2, 0.24), n("C#5", 4, 1, 2, 0.22),
            n("A4", 4, 3, 7, 0.24)])])

# ── VOLUME 6 · New Auburn ──────────────────────────────────────────
bed("vol6_kwik_stop_interior", 58,
    "The Kwik Stop at 11:47 PM. Sodium fluorescents forward, the "
    "beer-cooler compressor as the drone, the door chime twice.",
    [track("fluorescent_hum", 0.26, [n("A2", 1, 1, 40, 0.40)]),
     track("ambient_drone", 0.24, [n("C2", 1, 1, 40, 0.34)]),
     track("slowstick_pad", 0.14,
           hold(["C3", "D#3", "G3"], 1, 20, 0.20)
           + hold(["A#2", "D3", "F3"], 6, 20, 0.20)),
     track("soft_sine", 0.15, [n("G5", 3, 1, 2, 0.22),
                               n("D5", 3, 2, 3, 0.18),
                               n("G5", 8, 3, 2, 0.20),
                               n("D5", 8, 4, 3, 0.16)])])

bed("vol6_cosmic_comics_interior", 72,
    "Cosmic Comics, Saturday pull. A 60 Hz CRT in the back, mylar "
    "shuffle as texture, and the hand-me-down Casio's demo loop "
    "running four bars at a time because nobody stops it.",
    [track("fluorescent_hum", 0.16, [n("A2", 1, 1, 42, 0.30)]),
     track("rain", 0.10, [n("C4", 1, 1, 42, 0.18)]),
     track("slowstick_pad", 0.18,
           hold(["F3", "A3", "C4"], 1, 20, 0.24)
           + hold(["D3", "F3", "A3"], 6, 20, 0.22)),
     track("chiptune_arp", 0.14,
           [n(p, b, be, 0.45, 0.20)
            for b in (2, 3, 7, 8)
            for be, p in ((1, "F5"), (2, "A5"), (3, "C6"), (4, "A5"))])])

bed("vol6_gas_and_go_interior", 60,
    "NexCorp Gas & Go, locker four. Canopy fans as the floor, the "
    "ice-maker cycling, and the office printer ginning out the daily "
    "report in short irregular runs.",
    [track("rain", 0.20, [n("A#1", 1, 1, 42, 0.30)]),
     track("ambient_drone", 0.26, [n("D2", 1, 1, 42, 0.36)]),
     track("fluorescent_hum", 0.14, [n("A2", 1, 1, 42, 0.28)]),
     track("chiptune_arp", 0.07,
           [n("D6", 4, 1, 0.2, 0.14), n("D6", 4, 1.6, 0.2, 0.12),
            n("D6", 4, 2.1, 0.2, 0.12), n("D6", 7, 3, 0.2, 0.14),
            n("D6", 7, 3.5, 0.2, 0.12), n("D6", 10, 1, 0.2, 0.12)])])

bed("vol6_el_rancho_interior", 64,
    "El Rancho, late plate. One norteño chord held a bar longer than "
    "it should be, the dishwasher's last cycle under it.",
    [track("rain", 0.16, [n("C3", 1, 1, 42, 0.26)]),
     track("ambient_drone", 0.22, [n("A1", 1, 1, 42, 0.32)]),
     track("slowstick_pad", 0.24,
           hold(["A2", "C#3", "E3"], 1, 24, 0.28)
           + hold(["D3", "F#3", "A3"], 8, 16, 0.26)),
     track("slowstick_lead", 0.16,
           [n("E4", 5, 1, 2, 0.22), n("C#4", 5, 3, 2, 0.20),
            n("A3", 6, 1, 6, 0.22)])])

bed("vol6_live_oak_field", 60,
    "Live Oak field, two-a-days. Cicadas at 6:15 AM bright over the "
    "grass; the whistle's three short bursts once, a long way off.",
    [track("rain", 0.22, [n("A4", 1, 1, 42, 0.26)]),
     track("ambient_drone", 0.26, [n("G1", 1, 1, 42, 0.36)]),
     track("slowstick_pad", 0.16,
           hold(["G2", "B2", "D3"], 1, 20, 0.22)
           + hold(["C3", "E3", "G3"], 6, 20, 0.22)),
     track("soft_sine", 0.13, [n("D6", 5, 1, 0.6, 0.18),
                               n("D6", 5, 2, 0.6, 0.18),
                               n("D6", 5, 3, 0.9, 0.16)])])

bed("vol6_substation_nine", 56,
    "Substation Nine. The transformer is the whole piece — 60 Hz and "
    "the chain-link ringing with it. One grackle, twice, that will "
    "not leave.",
    [track("fluorescent_hum", 0.34, [n("A2", 1, 1, 40, 0.46)]),
     track("ambient_drone", 0.26, [n("A1", 1, 1, 40, 0.36)]),
     track("slowstick_lead", 0.10, [n("A#5", 4, 2, 0.5, 0.18),
                                    n("A#5", 9, 1, 0.4, 0.16)])])

bed("vol6_corporate_hum", 60,
    "Sixty-eight, year-round. The HVAC and one sine near 68 Hz. "
    "Clean. Inhuman. Nothing else is allowed in.",
    [track("rain", 0.14, [n("G1", 1, 1, 32, 0.24)]),
     track("ambient_drone", 0.34, [n("C#2", 1, 1, 32, 0.46)])])

bed("vol6_new_auburn_kitchen", 56,
    "A New Auburn house at rest — the Millers, the Hendersons, the "
    "Kowalskis. A window unit two rooms over, a refrigerator that "
    "cycles, a clock in the hall. Warm where vol6_ambient is not: "
    "these houses are inside Harmony Creek and are not of it.",
    [track("ambient_drone", 0.26, [n("G1", 1, 1, 40, 0.36)]),
     track("rain", 0.09, [n("D#1", 1, 1, 40, 0.20)]),
     track("slowstick_pad", 0.22,
           hold(["G3", "A#3", "D4"], 1, 20, 0.26)
           + hold(["D#3", "G3", "A#3"], 6, 20, 0.24)),
     track("soft_sine", 0.11, [n("D5", 4, 3, 5, 0.16),
                               n("A#4", 9, 1, 6, 0.14)])])

bed("vol6_two_lane", 62,
    "The New Auburn two-lane from inside the cab. Tire hiss, the "
    "engine's note, and a figure that comes around every eight bars "
    "the way the mile markers do.",
    [track("rain", 0.20, [n("A#1", 1, 1, 42, 0.30)]),
     track("ambient_drone", 0.24, [n("D2", 1, 1, 42, 0.34)]),
     track("slowstick_bass", 0.16,
           [n("D1", b, 1, 2.0, 0.26) for b in range(1, 12)]),
     track("slowstick_pad", 0.16,
           hold(["D3", "F3", "A3"], 1, 20, 0.22)
           + hold(["A#2", "D3", "F3"], 6, 20, 0.20)),
     track("soft_sine", 0.10, [n("A4", 5, 1, 3, 0.16),
                               n("F4", 5, 4, 4, 0.14)])])

# ── VOLUME 7 · Smolvud ─────────────────────────────────────────────
bed("vol7_ambient", 54,
    "Smolvud. Coastal air very low, E minor turning to C major seven "
    "— the town knows you have arrived before you do.",
    [track("rain", 0.13, [n("F1", 1, 1, 42, 0.24)]),
     track("ambient_drone", 0.28, [n("E1", 1, 1, 42, 0.40)]),
     track("slowstick_pad", 0.22,
           hold(["E3", "G3", "B3"], 1, 16, 0.26)
           + hold(["C3", "E3", "G3", "B3"], 5, 16, 0.24)
           + hold(["A2", "C3", "E3"], 9, 14, 0.24)),
     track("soft_sine", 0.13, [n("B4", 4, 3, 6, 0.18),
                               n("E5", 10, 1, 6, 0.16)])])

bed("vol7_hymn_fragment", 60,
    "A German hymn on a far piano in another room of the house. Six "
    "notes, played twice, the second time quieter — it is not for "
    "you and it does not finish.",
    [track("ambient_drone", 0.16, [n("G1", 1, 1, 42, 0.26)]),
     track("slowstick_pad", 0.14,
           hold(["G2", "B2", "D3"], 1, 20, 0.20)
           + hold(["C3", "E3", "G3"], 7, 18, 0.18)),
     track("slowstick_lead", 0.18,
           [n("G4", 1, 3, 2, 0.24), n("A4", 2, 1, 2, 0.22),
            n("B4", 2, 3, 2, 0.24), n("G4", 3, 1, 2, 0.22),
            n("D5", 3, 3, 3, 0.24), n("B4", 4, 2, 5, 0.22),
            n("G4", 7, 3, 2, 0.16), n("A4", 8, 1, 2, 0.14),
            n("B4", 8, 3, 2, 0.16), n("G4", 9, 1, 6, 0.14)])])

bed("vol7_bread_table", 58,
    "Bread, table, family. Kitchen fire low in the room, C major "
    "warm, and the hymn from the other room reaching four notes in.",
    [track("rain", 0.16, [n("G1", 1, 1, 42, 0.26)]),
     track("ambient_drone", 0.22, [n("C2", 1, 1, 42, 0.32)]),
     track("slowstick_pad", 0.24,
           hold(["C3", "E3", "G3"], 1, 20, 0.28)
           + hold(["F3", "A3", "C4"], 7, 20, 0.26)),
     track("slowstick_lead", 0.14,
           [n("G4", 4, 1, 2, 0.18), n("A4", 4, 3, 2, 0.16),
            n("B4", 5, 1, 2, 0.18), n("G4", 5, 3, 5, 0.16)])])

bed("vol7_cabin_woodstove", 54,
    "The cabin's woodstove. A damper tick, a log settling at the "
    "back of the firebox, and the plank floor cooling — F major with "
    "the sixth in it so the warmth has an edge.",
    [track("rain", 0.11, [n("D#1", 1, 1, 42, 0.22)]),
     track("ambient_drone", 0.26, [n("F1", 1, 1, 42, 0.36)]),
     track("slowstick_pad", 0.22,
           hold(["F3", "A3", "C4", "D4"], 1, 22, 0.26)
           + hold(["D3", "F3", "A3"], 8, 16, 0.24)),
     track("chiptune_arp", 0.06, [n("F5", 3, 2, 0.15, 0.14),
                                  n("F5", 6, 1, 0.15, 0.12),
                                  n("C5", 9, 3, 0.3, 0.12)])])

bed("vol7_kestrel_circle", 50,
    "Kestrel, wind above. The thermal is bright and continuous; the "
    "bird's cry is small, high and very far, and comes twice.",
    [track("rain", 0.28, [n("C5", 1, 1, 42, 0.30)]),
     track("ambient_drone", 0.28, [n("B1", 1, 1, 42, 0.38)]),
     track("slowstick_pad", 0.16,
           hold(["B2", "D3", "F#3"], 1, 22, 0.22)
           + hold(["G2", "B2", "D3"], 8, 16, 0.20)),
     track("soft_sine", 0.10, [n("F#6", 4, 3, 0.8, 0.16),
                               n("F#6", 9, 2, 0.7, 0.14)])])

bed("vol7_marina_morning", 62,
    "The marina. Halyard tap on an aluminum mast — irregular, never "
    "on the beat — dock-line creak underneath, one gull a long way "
    "off.",
    [track("ambient_drone", 0.24, [n("D2", 1, 1, 42, 0.34)]),
     track("slowstick_pad", 0.18,
           hold(["D3", "F#3", "A3"], 1, 20, 0.24)
           + hold(["B2", "D3", "F#3"], 7, 20, 0.22)),
     track("chiptune_arp", 0.09,
           [n("A5", 2, 1.3, 0.15, 0.16), n("A5", 3, 2.7, 0.15, 0.14),
            n("A5", 5, 1.1, 0.15, 0.15), n("A5", 6, 3.4, 0.15, 0.13),
            n("A5", 8, 2.2, 0.15, 0.15), n("A5", 10, 1.7, 0.15, 0.13)]),
     track("soft_sine", 0.10, [n("D6", 6, 1, 1.2, 0.14)])])

bed("vol7_painting_room", 50,
    "The painting room. Turpentine uncorked, a brush tap, the close "
    "attentive breath of someone looking — so three notes and a lot "
    "of room.",
    [track("ambient_drone", 0.22, [n("A1", 1, 1, 42, 0.32)]),
     track("slowstick_pad", 0.20,
           hold(["A2", "C3", "E3"], 1, 22, 0.24)
           + hold(["F2", "A2", "C3", "E3"], 8, 16, 0.22)),
     track("soft_sine", 0.18, [n("E4", 3, 1, 5, 0.22),
                               n("C5", 6, 3, 4, 0.20),
                               n("A4", 10, 1, 6, 0.18)])])

bed("vol7_loft_dust", 56,
    "The loft at four. Hayloft settle, a sparrow in the eaves, and "
    "the four-o'clock sun on warm wood — C to G, and the sparrow "
    "does not stay.",
    [track("rain", 0.10, [n("F#1", 1, 1, 42, 0.20)]),
     track("ambient_drone", 0.22, [n("C2", 1, 1, 42, 0.32)]),
     track("slowstick_pad", 0.24,
           hold(["C3", "E3", "G3"], 1, 20, 0.26)
           + hold(["G2", "B2", "D3"], 7, 20, 0.24)),
     track("soft_sine", 0.11, [n("G5", 5, 2, 0.4, 0.16),
                               n("B5", 5, 2.5, 0.4, 0.14),
                               n("G5", 5, 3.1, 0.6, 0.14)])])

bed("vol7_shop_signal_bell", 60,
    "The shop's signal bell. Door-spring chime at the top and again "
    "when someone leaves, the till's small click between, and the "
    "floorboard that always pops under the second step.",
    [track("ambient_drone", 0.22, [n("G2", 1, 1, 40, 0.32)]),
     track("slowstick_pad", 0.20,
           hold(["G3", "B3", "D4"], 1, 18, 0.24)
           + hold(["E3", "G3", "B3"], 6, 18, 0.22)),
     track("soft_sine", 0.18, [n("D6", 1, 1, 1.2, 0.24),
                               n("G5", 1, 1.6, 1.6, 0.20),
                               n("D6", 7, 1, 1.2, 0.20),
                               n("G5", 7, 1.6, 1.8, 0.18)]),
     track("chiptune_arp", 0.06, [n("B5", 4, 2, 0.12, 0.14),
                                  n("G3", 9, 3, 0.25, 0.12)])])

bed("vol7_milestone_bell", 56,
    "Aria rings the bell. Her signature made literal: a strike, "
    "three seconds of held silence, again, and the pad arriving "
    "only under the third.",
    [track("soft_sine", 0.30, [n("D6", 1, 1, 2.5, 0.30),
                               n("D6", 3, 1, 2.5, 0.28),
                               n("D6", 5, 1, 4.0, 0.30)]),
     track("ambient_drone", 0.22, [n("D2", 5, 1, 18, 0.32)]),
     track("slowstick_pad", 0.22, hold(["D3", "F#3", "A3"], 5, 16, 0.26))])


# ── VOLUME 5 · three tracks a PLAYER VERB asks for ─────────────────
# Not chapter beds. Each of these is reached by something the player
# does, and each played nothing: the Fool's diner has two jukebox 45s
# as usable items (`play_jukebox_track` in resources/games/fool/
# items.json) whose files never existed, and the Music Player's TAPE
# REEL skin unlocks on having HEARD Elicia's solo theme — a file that
# has never existed, so the skin could not be reached at all.

bed("vol5_noon_room_room", 104,
    "NOON ROOM ROOM — the lunch-service jukebox 45. An accordion "
    "B-side from a Lake Charles wedding band, 1991, and whoever set "
    "the brass mic by the dance floor heard everything in the room. A "
    "two-step in G: bass on the one and the three, the chuck between "
    "them, and a tune that goes around twice because that is how long "
    "a 45 gives you.",
    [track("slowstick_bass", 0.24,
           [n(p, b, be, 0.7, 0.30)
            for b in range(1, 17)
            for be, p in ((1, "G1"), (3, "D2"))]),
     track("chiptune_arp", 0.10,
           [n(p, b, be, 0.22, 0.16)
            for b in range(1, 17)
            for be in (2, 4)
            for p in ("G4", "B4", "D5")]),
     track("slowstick_pad", 0.14,
           hold(["G2", "B2", "D3"], 1, 16, 0.20)
           + hold(["C3", "E3", "G3"], 9, 8, 0.20)
           + hold(["D3", "F#3", "A3"], 11, 8, 0.20)
           + hold(["G2", "B2", "D3"], 13, 16, 0.20)),
     track("slowstick_lead", 0.24,
           [n("D5", 1, 1, 1, 0.28), n("G5", 1, 2, 1, 0.26),
            n("B5", 1, 3, 1, 0.26), n("A5", 1, 4, 1, 0.24),
            n("G5", 2, 1, 2, 0.28), n("D5", 2, 3, 2, 0.24),
            n("E5", 3, 1, 1, 0.26), n("D5", 3, 2, 1, 0.24),
            n("C5", 3, 3, 2, 0.26),
            n("B4", 4, 1, 2, 0.26), n("D5", 4, 3, 2, 0.24),
            n("D5", 5, 1, 1, 0.28), n("G5", 5, 2, 1, 0.26),
            n("B5", 5, 3, 1, 0.26), n("D6", 5, 4, 1, 0.24),
            n("B5", 6, 1, 2, 0.28), n("G5", 6, 3, 2, 0.24),
            n("A5", 7, 1, 1, 0.26), n("B5", 7, 2, 1, 0.24),
            n("A5", 7, 3, 2, 0.26),
            n("G5", 8, 1, 4, 0.28),
            n("E5", 9, 1, 1, 0.26), n("G5", 9, 2, 1, 0.26),
            n("E5", 9, 3, 1, 0.24), n("C5", 9, 4, 1, 0.24),
            n("E5", 10, 1, 3, 0.26),
            n("F#5", 11, 1, 1, 0.26), n("A5", 11, 2, 1, 0.26),
            n("F#5", 11, 3, 2, 0.24),
            n("D5", 12, 1, 3, 0.26),
            n("D5", 13, 1, 1, 0.28), n("G5", 13, 2, 1, 0.26),
            n("B5", 13, 3, 1, 0.26), n("A5", 13, 4, 1, 0.24),
            n("G5", 14, 1, 2, 0.28), n("D5", 14, 3, 2, 0.24),
            n("E5", 15, 1, 1, 0.26), n("D5", 15, 2, 1, 0.24),
            n("C5", 15, 3, 2, 0.26),
            n("B4", 16, 1, 1, 0.26), n("G4", 16, 2, 4, 0.28)])])

bed("vol5_where_the_bar_used_to_be", 62,
    "WHERE THE BAR USED TO BE — the evening-service 45. Solo piano, "
    "after hours, recorded in this diner in 1979 when there was still "
    "a piano. A minor, no rhythm section, and every phrase comes down "
    "instead of up. The piano was sold the year you started.",
    [track("slowstick_pad", 0.12,
           hold(["A2", "C3", "E3"], 1, 16, 0.16)
           + hold(["F2", "A2", "C3"], 5, 12, 0.15)
           + hold(["D2", "F2", "A2"], 8, 12, 0.15)
           + hold(["E2", "G#2", "B2"], 11, 10, 0.16)),
     track("slowstick_lead", 0.26,
           [n("E5", 1, 2, 2, 0.28), n("C5", 1, 4, 1, 0.24),
            n("A4", 2, 1, 3, 0.28),
            n("B4", 3, 1, 1, 0.24), n("C5", 3, 2, 1, 0.26),
            n("B4", 3, 3, 2, 0.24),
            n("A4", 4, 1, 4, 0.26),
            n("C5", 5, 2, 2, 0.26), n("A4", 5, 4, 1, 0.22),
            n("F4", 6, 1, 4, 0.26),
            n("G4", 7, 2, 1, 0.24), n("F4", 7, 3, 2, 0.24),
            n("E4", 8, 1, 4, 0.26),
            n("D5", 9, 2, 2, 0.26), n("C5", 9, 4, 1, 0.22),
            n("A4", 10, 1, 4, 0.26),
            n("B4", 11, 1, 1, 0.24), n("G#4", 11, 2, 1, 0.24),
            n("E4", 11, 3, 2, 0.26),
            n("A4", 12, 1, 6, 0.28)])])

bed("vol5_elicia_theme_solo", 54,
    "Elicia · Tape Reel. Cassette-spool noise and a soft sustained "
    "voice-tone with no vocal in it — the sound of a reel turning "
    "with someone's silence on it. This gates the Music Player's TAPE "
    "REEL skin, which nobody could reach.",
    [track("rain", 0.16, [n("A#3", 1, 1, 34, 0.24)]),
     track("ambient_drone", 0.22, [n("D2", 1, 1, 34, 0.32)]),
     track("slowstick_pad", 0.16,
           hold(["D3", "F3", "A3"], 1, 18, 0.22)
           + hold(["A#2", "D3", "F3"], 6, 14, 0.20)),
     track("soft_sine", 0.24, [n("A4", 2, 1, 9, 0.26),
                               n("F4", 6, 3, 8, 0.22)])])


# ── the gauntlet's scenario B-sides ────────────────────────────────
# Fifteen catalog entries describe one bed per (arcana × difficulty)
# across the first five arcana — twenty of the 88 scenarios. Each is
# a TIME OF DAY as much as a difficulty: easy is afternoon light,
# medium is the working evening, hard is the small hours. None had a
# file and nothing played them; every board used the location bed.
# `_BGM_BY_SCENARIO` in TarotGauntletGame now prefers these.
#
# These are longer than the chapter beds (12-14 bars) because a
# scenario run is minutes, not a page.

bed("vol5_sinking_feeling", 52,
    "Magician · easy. Afternoon sun on the cathedral skylights, low "
    "river lap outside, a distant freight horn. The riverside knowing "
    "what's coming and taking its time about it.",
    [track("rain", 0.14, [n("D#1", 1, 1, 56, 0.24)]),
     track("ambient_drone", 0.26, [n("C2", 1, 1, 56, 0.36)]),
     track("slowstick_pad", 0.20,
           hold(["C3", "E3", "G3"], 1, 24, 0.24)
           + hold(["A2", "C3", "E3"], 7, 24, 0.22)
           + hold(["F2", "A2", "C3"], 13, 12, 0.22)),
     track("soft_sine", 0.12, [n("G3", 5, 1, 6, 0.18),
                               n("G3", 11, 3, 7, 0.16)])])

bed("vol5_watch_party", 58,
    "Magician · medium. TV-room hum, the Pomegranate Hour theme "
    "bleeding through one wall, a far laugh from someone who isn't "
    "supposed to be in the house.",
    [track("fluorescent_hum", 0.16, [n("A2", 1, 1, 56, 0.30)]),
     track("ambient_drone", 0.24, [n("A1", 1, 1, 56, 0.34)]),
     track("slowstick_pad", 0.18,
           hold(["A2", "C3", "E3"], 1, 24, 0.24)
           + hold(["D3", "F3", "A3"], 7, 24, 0.22)
           + hold(["E3", "G3", "B3"], 13, 12, 0.22)),
     track("chiptune_arp", 0.08,
           [n(p, b, be, 0.35, 0.14)
            for b in (4, 10)
            for be, p in ((1, "E5"), (2, "A5"), (3, "C6"), (4, "A5"))]),
     track("soft_sine", 0.10, [n("C6", 8, 3, 0.8, 0.14)])])

bed("vol5_blow_out_the_candles", 50,
    "Magician · hard. Full moon over the river, the bank making a "
    "noise the bank should not be making, candle hiss, a rager house "
    "party a long way downstream.",
    [track("rain", 0.18, [n("A#1", 1, 1, 56, 0.28)]),
     track("ambient_drone", 0.30, [n("F1", 1, 1, 56, 0.42)]),
     track("slowstick_pad", 0.18,
           hold(["F2", "G#2", "C3"], 1, 26, 0.24)
           + hold(["D#2", "G2", "A#2"], 8, 24, 0.22)),
     track("slowstick_bass", 0.14,
           [n("F1", b, 1, 1.2, 0.24) for b in (5, 9, 13)]),
     track("soft_sine", 0.10, [n("C5", 6, 3, 5, 0.14),
                               n("G#4", 12, 1, 6, 0.12)])])

bed("vol5_cicada_session", 54,
    "Priestess · easy. 9:18 PM. The cicadas outside louder than they "
    "should be, the booth's red record light, the reel fresh.",
    [track("rain", 0.24, [n("A4", 1, 1, 56, 0.28)]),
     track("ambient_drone", 0.24, [n("E1", 1, 1, 56, 0.34)]),
     track("slowstick_pad", 0.18,
           hold(["E3", "G3", "B3"], 1, 24, 0.24)
           + hold(["C3", "E3", "G3"], 7, 24, 0.22)
           + hold(["A2", "C3", "E3"], 13, 12, 0.22)),
     track("soft_sine", 0.11, [n("B4", 6, 1, 6, 0.16)])])

bed("vol5_long_quiet", 50,
    "Priestess · medium. 11:02 PM, confessional hour. The cicadas "
    "have gone and what is left is the booth's own noise floor.",
    [track("rain", 0.10, [n("C3", 1, 1, 56, 0.20)]),
     track("ambient_drone", 0.28, [n("E1", 1, 1, 56, 0.38)]),
     track("slowstick_pad", 0.16,
           hold(["E3", "G3", "B3"], 1, 28, 0.22)
           + hold(["A2", "C3", "E3"], 9, 24, 0.20)),
     track("soft_sine", 0.12, [n("E4", 4, 1, 9, 0.16),
                               n("B4", 12, 1, 8, 0.14)])])

bed("vol5_tape_witness", 48,
    "Priestess · hard. 2:14 AM, off the books. The truth-teller is "
    "already in the booth and the cathedral is dark on the other side "
    "of the glass.",
    [track("ambient_drone", 0.32, [n("D#1", 1, 1, 56, 0.44)]),
     track("rain", 0.09, [n("A#3", 1, 1, 56, 0.18)]),
     track("slowstick_pad", 0.16,
           hold(["D#3", "F#3", "A#3"], 1, 28, 0.22)
           + hold(["C#3", "F3", "G#3"], 9, 24, 0.20)),
     track("soft_sine", 0.10, [n("A#4", 7, 3, 7, 0.14)])])

bed("vol5_static_bloom", 56,
    "Empress · easy. Friday dinner on Nicola's riverboat: first "
    "arrivals setting the long table, the garden deck still in "
    "season.",
    [track("ambient_drone", 0.22, [n("G1", 1, 1, 56, 0.32)]),
     track("slowstick_pad", 0.24,
           hold(["G3", "B3", "D4"], 1, 24, 0.26)
           + hold(["C3", "E3", "G3"], 7, 24, 0.24)
           + hold(["D3", "F#3", "A3"], 13, 12, 0.24)),
     track("soft_sine", 0.16, [n("D5", 3, 3, 5, 0.20),
                               n("B4", 9, 1, 6, 0.18),
                               n("G4", 14, 1, 6, 0.18)])])

bed("vol5_harvest_dinner", 52,
    "Empress · medium. Late autumn. Frasier on the bank walking "
    "slow. The garden deck has cooled and the table is set anyway.",
    [track("rain", 0.12, [n("F1", 1, 1, 56, 0.22)]),
     track("ambient_drone", 0.26, [n("G1", 1, 1, 56, 0.36)]),
     track("slowstick_pad", 0.20,
           hold(["G3", "A#3", "D4"], 1, 26, 0.24)
           + hold(["D#3", "G3", "A#3"], 9, 24, 0.22)),
     track("soft_sine", 0.12, [n("D5", 5, 1, 7, 0.18),
                               n("A#4", 12, 3, 6, 0.16)])])

bed("vol5_ice_in_the_river", 46,
    "Empress · hard. 11:14 PM, late February. The river has ice in "
    "it for the first time in a decade and everyone at the table "
    "knows.",
    [track("rain", 0.16, [n("C5", 1, 1, 56, 0.24)]),
     track("ambient_drone", 0.30, [n("C2", 1, 1, 56, 0.40)]),
     track("slowstick_pad", 0.16,
           hold(["C3", "D#3", "G3"], 1, 28, 0.22)
           + hold(["G#2", "C3", "D#3"], 9, 24, 0.20)),
     track("soft_sine", 0.10, [n("G5", 8, 1, 4, 0.14)])])

bed("vol5_docket", 58,
    "Emperor · easy. Tuesday morning. Brass clock, radiator on too "
    "high, a stamp coming down on the blotter every so often.",
    [track("ambient_drone", 0.24, [n("D2", 1, 1, 56, 0.34)]),
     track("fluorescent_hum", 0.12, [n("A2", 1, 1, 56, 0.26)]),
     track("slowstick_pad", 0.20,
           hold(["D3", "F#3", "A3"], 1, 24, 0.24)
           + hold(["G3", "B3", "D4"], 7, 24, 0.22)
           + hold(["A2", "C#3", "E3"], 13, 12, 0.22)),
     track("chiptune_arp", 0.07, [n("D4", 4, 2, 0.18, 0.14),
                                  n("D4", 9, 1, 0.18, 0.13),
                                  n("D4", 13, 3, 0.18, 0.13)])])

bed("vol5_first_session", 54,
    "Emperor · medium. Pre-clerk Monday. The petitioner slept in "
    "their car and the radiator is cold.",
    [track("ambient_drone", 0.28, [n("D2", 1, 1, 56, 0.38)]),
     track("slowstick_pad", 0.18,
           hold(["D3", "F3", "A3"], 1, 26, 0.22)
           + hold(["A#2", "D3", "F3"], 9, 24, 0.20)),
     track("soft_sine", 0.12, [n("A4", 6, 1, 7, 0.16),
                               n("F4", 13, 1, 6, 0.14)])])

bed("vol5_appeal", 50,
    "Emperor · hard. Late Tuesday afternoon, six-month appellate "
    "hearing, and volumes 9 and 10 of the river code are missing off "
    "the shelf.",
    [track("ambient_drone", 0.30, [n("A#1", 1, 1, 56, 0.40)]),
     track("fluorescent_hum", 0.14, [n("C3", 1, 1, 56, 0.28)]),
     track("slowstick_pad", 0.18,
           hold(["A#2", "C#3", "F3"], 1, 26, 0.24)
           + hold(["G#2", "C3", "D#3"], 9, 24, 0.22)),
     track("soft_sine", 0.10, [n("F5", 7, 1, 3, 0.14),
                               n("D#5", 14, 1, 5, 0.12)])])

bed("vol5_green_phosphor", 60,
    "Hierophant · easy. Tuesday night BBS: the modem rack humming "
    "and the printer's banner paper rolling slowly out onto the "
    "floor.",
    [track("fluorescent_hum", 0.22, [n("A2", 1, 1, 56, 0.36)]),
     track("ambient_drone", 0.24, [n("A1", 1, 1, 56, 0.34)]),
     track("slowstick_pad", 0.16,
           hold(["A2", "C3", "E3"], 1, 26, 0.22)
           + hold(["F2", "A2", "C3"], 9, 24, 0.20)),
     track("chiptune_arp", 0.09,
           [n(p, b, be, 0.25, 0.16)
            for b in (3, 8, 13)
            for be, p in ((1, "A5"), (1.6, "E5"), (2.2, "A5"))])])

bed("vol5_long_signal", 54,
    "Hierophant · medium. Late Wednesday. Anya at the floppy wall, "
    "the ham band open, 14.301 MHz live and someone on it.",
    [track("rain", 0.14, [n("D#4", 1, 1, 56, 0.22)]),
     track("ambient_drone", 0.26, [n("A1", 1, 1, 56, 0.36)]),
     track("slowstick_pad", 0.18,
           hold(["A2", "D3", "E3"], 1, 28, 0.22)
           + hold(["G2", "C3", "D3"], 9, 24, 0.20)),
     track("soft_sine", 0.13, [n("E5", 5, 1, 8, 0.18),
                               n("D5", 12, 3, 6, 0.16)])])

bed("vol5_broadcast_night", 48,
    "Hierophant · hard. 3:14 AM. The lurker logged in. The ham band "
    "hisses and then, for no reason anyone can give, clears.",
    [track("rain", 0.22, [n("C5", 1, 1, 26, 0.28),
                          n("G2", 8, 1, 30, 0.16)]),
     track("ambient_drone", 0.30, [n("D#1", 1, 1, 56, 0.42)]),
     track("fluorescent_hum", 0.14, [n("A2", 1, 1, 56, 0.26)]),
     track("slowstick_pad", 0.16,
           hold(["D#3", "G3", "A#3"], 1, 28, 0.22)
           + hold(["C3", "D#3", "G3"], 9, 24, 0.20)),
     track("soft_sine", 0.10, [n("A#4", 10, 1, 8, 0.14)])])


# ── beds that were already on disk and nothing pointed at ──────────
# Six vol5 room tones were rendered at some point and never entered the
# catalog, so the arcana chapters could not use them even though they
# are exactly what those chapters want. Adopted here.
ADOPT = [
    ("vol5_diner_roomtone", "D'Ambrosio's · Room Tone",
     "The dining room with no one talking: booth vinyl, the pass-through "
     "fan, the register drawer somewhere behind you."),
    ("vol5_domestic_roomtone", "Someone's Rooms",
     "The generic Louisiana interior at rest — a window unit two rooms "
     "over, a refrigerator that cycles. Every apartment in the arcana run."),
    ("vol5_store_ambient", "The Store",
     "Aisle fluorescents and a cooler compressor. The grocery, the "
     "pharmacy, the ice company front office."),
    ("vol5_cafe_ambient", "Café · Montreal",
     "Espresso machine at the far end, chairs on tile, two conversations "
     "in a language the scene is not in."),
    ("vol5_venue_ambient", "The Room With the Bar In It",
     "Bottles, ice, a room built to hold a crowd, holding fewer."),
    ("vol5_cathedral_drone", "Cathedral of Rust and Code · Drone",
     "The warehouse's own note. Longer and lower than the vol5 warehouse "
     "drone, and it does not develop."),
]


def adopt_into_catalog(cat_path):
    """Point the catalog at the files that exist: rewrite the authored
    beds' `src` to the rendered .wav, and add the orphan vol5 room
    tones as entries. Idempotent."""
    cat = json.loads(open(cat_path, encoding="utf-8").read())
    by_id = {e["id"]: e for e in cat}
    changed = 0
    for tid in list(BEDS) + list(ON_DISK):
        e = by_id.get(tid)
        want = "assets/audio/bgm/%s.wav" % tid
        if e is None and tid not in BEDS:
            print("  MISSING CATALOG ENTRY  %s" % tid)
            continue
        if e is None:
            # A bed authored here that the catalog never imagined.
            cat.append({
                "id": tid, "vol": int(tid[3]) if tid[:3] == "vol" else 0,
                "title": BEDS[tid]["note"].split(".")[0],
                "src": want, "composer": "—",
                "desc": BEDS[tid]["note"],
                "unlock": {"type": "key", "key": "music:%s" % tid},
                "chapters": [],
            })
            by_id[tid] = cat[-1]
            print("  new    %-32s %s" % (tid, want))
            changed += 1
            continue
        if e.get("src") != want:
            print("  src  %-32s %s -> %s" % (tid, e.get("src"), want))
            e["src"] = want
            changed += 1
    for tid, title, desc in ADOPT:
        if tid in by_id:
            continue
        src = "assets/audio/bgm/%s.wav" % tid
        if not os.path.exists(os.path.join(ROOT, "godot", src)):
            print("  ADOPT SKIPPED (no file)  %s" % tid)
            continue
        cat.append({
            "id": tid, "vol": 5, "title": title, "src": src,
            "composer": "—", "desc": desc,
            "unlock": {"type": "key", "key": "music:%s" % tid},
            "chapters": [],
        })
        print("  adopt  %-32s %s" % (tid, src))
        changed += 1
    with open(cat_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(cat, indent=1, ensure_ascii=False) + "\n")
    print("\n%d catalog change(s)" % changed)


def compose(tid):
    spec = BEDS[tid]
    return {
        "meta": {
            "title": tid,
            "composer": "authored for the VN score",
            "for": "music_catalog.json · %s" % tid,
            "notes": spec["note"],
        },
        "tempo_bpm": spec["tempo"],
        "time_sig": [4, 4],
        "sample_rate": SR,
        "tracks": spec["layers"],
    }


def main():
    if "--list" in sys.argv:
        for tid in sorted(BEDS):
            print("%-32s %s" % (tid, BEDS[tid]["note"].split(".")[0]))
        print("\n%d bed(s)" % len(BEDS))
        return 0
    if "--catalog" in sys.argv:
        adopt_into_catalog(os.path.join(
            ROOT, "godot", "resources", "music_catalog.json"))
        return 0
    only = [a for a in sys.argv[1:] if not a.startswith("--")]
    os.makedirs(COMPS, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)
    total = 0
    for tid in sorted(BEDS):
        if only and tid not in only:
            continue
        cj = os.path.join(COMPS, tid + ".json")
        with open(cj, "w") as f:
            json.dump(compose(tid), f, indent=1)
            f.write("\n")
        wav = os.path.join(OUT, tid + ".wav")
        r = subprocess.run([sys.executable, SYNTH, "compose", cj, wav],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print("FAIL %-32s %s" % (tid, r.stderr.strip()[:120]))
            continue
        print("%-32s %s" % (tid, r.stdout.strip()))
        total += 1
    print("\n%d bed(s) rendered" % total)
    return 0


if __name__ == "__main__":
    sys.exit(main())
