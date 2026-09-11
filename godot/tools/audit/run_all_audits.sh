#!/usr/bin/env bash
# Run every audit tool in this directory and print the summary
# line from each. Zero-issue means the map is clean for that
# audit dimension.
set -e
cd "$(dirname "${BASH_SOURCE[0]}")"
for f in audit_*.py; do
    echo "── $f ──"
    python3 "$f" 2>/dev/null | tail -2
    echo ""
done

echo "── locale_geometry_audit.py ──"
python3 locale_geometry_audit.py 2>/dev/null | tail -2
echo ""

# ── Shot-cue coverage (2026-08-12 · gated 2026-09-11) ──────────
# A cue that names an object the locale has no marker for used to punch
# the lens into a wall; since 2026-08-12 the director substitutes, but a
# blind cue still means the frame is not the one the line asked for.
# Reached ZERO on 2026-09-11 (1532 object cues across 123 presets) by
# authoring the missing markers and retargeting the cues whose object
# does not exist — a knock at a window the cell does not have is a knock
# on the wall. Nonzero fails.
echo "── shot_marker_audit.py ──"
BOUT="$(python3 shot_marker_audit.py 2>/dev/null)" || true
echo "$BOUT" | tail -2
BN="$(echo "$BOUT" | tail -1 | grep -oE "^[0-9]+ blind" | grep -oE "^[0-9]+")"
if [ "${BN:-999}" -gt 0 ]; then
    echo "$BOUT" | grep "^==\|x  shot_"
    echo "REGRESSION  $BN blind object cue(s) (ceiling 0)"; exit 1; fi
echo ""

# ── Preset-vantage gate (2026-08-11) ───────────────────────────
# Every Background3D camera preset must SEE its locale's geometry
# (the graustark_ruins preset stood 350m from all four chapters'
# staging and every one rendered flat brown). Nonzero exit fails.
echo "── preset_vantage_audit.py ──"
# Captured (not piped) so a nonzero exit fails the suite under set -e.
VOUT="$(python3 preset_vantage_audit.py 2>/dev/null)" || {
    echo "$VOUT" | grep -v "^\["; exit 1; }
echo "$VOUT" | grep -v "^\[" | tail -2
echo ""

# ── Marker-aim gate (2026-08-19) ───────────────────────────────
# Every vn_shot marker is a CAMERA POSE (VnDirector assigns its
# global_transform to the camera; forward is −Z). A wave of markers
# shipped facing 180° from their subjects. Nonzero exit fails.
echo "── marker_aim_audit.py ──"
AOUT="$(python3 marker_aim_audit.py 2>/dev/null | grep -v "^\[")" || {
    echo "$AOUT" | grep -E "MISAIM|misaim"; exit 1; }
echo "$AOUT" | tail -2
echo ""

# ── VN story gate (2026-08-30) ─────────────────────────────────
# Every directive in every chapter must RESOLVE: bg presets, CG
# paths, jump targets, moods, beats, panels, bgm/sfx files. The
# engine degrades gracefully on all of these, which is exactly why
# they rot unnoticed (ten chapters opened in silence for months —
# their bgm files never existed). Nonzero exit fails.
echo "── vn_story_audit.py ──"
SOUT="$(python3 vn_story_audit.py 2>/dev/null)" || {
    echo "$SOUT" | grep "PROBLEM"; exit 1; }
echo "$SOUT" | tail -2
echo ""

# ── Prop-overlap ZERO-REGRESSION gate (2026-08-11) ─────────────
# Every locale audits clean except four known holdouts. A locale
# outside the allowlist reporting ANY clips is a regression; a
# holdout exceeding its recorded ceiling is one too. Fix the
# builder (or, for genuinely natural contact, extend the grammar
# in prop_overlap_audit.py) — never bump a ceiling to make the
# gate pass.
echo "── prop_overlap_audit.py (zero-regression gate) ──"
python3 - <<'PYGATE'
import re
import subprocess
import sys

HOLDOUTS = {
    # ── TRIAGE COMPLETE, 2026-08-12 (2 holdouts, both intentional)
    # The day's arc: opening the audit's eyes (the composite _props
    # modules had been stubbed to no-ops) took the repo 18 -> 286,
    # and triage took it to 15. What that exposed, beyond ordinary
    # clipping: ELEVEN windows centered at floor level, TWELVE
    # counters and SIX windows built 90 DEGREES ROTATED (helper
    # axis conventions), and the centro grocery double-booked
    # store-wide. Both remaining entries are BY DESIGN.
    "crumpled_barn": 11,    # the crumple IS the overlap
    "diner": 4,             # ticket tucks at <=0.06
}
out = subprocess.run(
    [sys.executable, "prop_overlap_audit.py", "--all"],
    capture_output=True, text=True, timeout=900).stdout
bad = []
for m in re.finditer(r"^== (\S+) · \d+ objects · (\d+) clips", out, re.M):
    name, n = m.group(1), int(m.group(2))
    if n > HOLDOUTS.get(name, 0):
        bad.append((name, n, HOLDOUTS.get(name, 0)))
total = re.search(r"^(\d+) clip\(s\)", out, re.M)
print("total: %s clips across the repo" % (total.group(1) if total else "?"))
if bad:
    for name, n, ceil in bad:
        print("REGRESSION  %-28s %d clips (allowed %d)" % (name, n, ceil))
    sys.exit(1)
print("0 regressions: every non-holdout locale is clean")
PYGATE

# ── Vantage-obstruction gate (2026-09-03) ──────────────────────
# A wall in the camera's face: the cabin's opening wide stood inside
# the bed alcove, Elicia's bungalow behind a closet. Every preset
# casts a ray fan; near-fills and single-surface fills fail. Nonzero
# exit fails the suite.
echo "── vantage_obstruction_audit.py ──"
OOUT="$(python3 vantage_obstruction_audit.py 2>/dev/null)" || {
    echo "$OOUT" | grep -v "^\["; exit 1; }
echo "$OOUT" | grep -v "^\[" | tail -2
echo ""

# ── Marker-obstruction gate (2026-09-07) ───────────────────────
# The same ray fan over every vn_shot marker (the diner's clock
# insert faced the upper south wall: a yellow field with a door
# sliver). NEAR / WALL / EMPTY verdicts; nonzero exit fails.
# ZERO-REGRESSION CEILING: 17 after the 2026-09-07 reframe passes (128
# before them; harmony_terrain's five markers skipped as unmeasured): the
# eleven STUCK subjects are resolved; what remains is mostly cast closeups
# with a wall 2.4 m behind the subject and two sky-heavy exteriors subjects behind walls from every side, 12 sky
# frames, the rest non-subject markers with a surface in the lens.
# Drive it down; never raise it.
echo "── vantage_obstruction_audit.py --markers ──"
MARKER_CEILING=0
MOUT="$(python3 vantage_obstruction_audit.py --markers 2>/dev/null | grep -v "^\[")" || true
MCOUNT="$(echo "$MOUT" | grep -oE "^[0-9]+ obstructed marker" | grep -oE "^[0-9]+")"
echo "$MOUT" | tail -1
if [ "${MCOUNT:-999}" -gt "$MARKER_CEILING" ]; then
    echo "REGRESSION  $MCOUNT obstructed markers (ceiling $MARKER_CEILING)"; exit 1; fi
echo ""

# ── Furniture grammar (2026-09-07 · gated 2026-09-08) ──────────
# Intra-assembly clipping and floating props stay informational
# (draft 1 still carries noise). CHAIR (facing away from its
# table), DESK (off the wall) and LANE (a parked car in a travel
# lane) reached ZERO repo-wide on 2026-09-08 after the Deck's
# "cars in the middle of streets keeps happening" — those three
# are now gates. POKE (a post, leg or chair back passing clean through
# a solid part of its own assembly — the "exploded chair") joined them
# the same day at 0. Nonzero in any of them fails the suite.
echo "── furniture_grammar_audit.py ──"
GOUT="$(python3 furniture_grammar_audit.py 2>/dev/null | grep -v "^\[")" || true
GLINE="$(echo "$GOUT" | tail -1)"
echo "$GLINE"
for CLS in POKE CHAIR DESK LANE BED OUTSIDE; do
    N="$(echo "$GLINE" | grep -oE "$CLS [0-9]+" | grep -oE "[0-9]+$")"
    if [ "${N:-999}" -gt 0 ]; then
        echo "$GOUT" | grep "^   $CLS"
        echo "REGRESSION  $N $CLS grammar break(s) (ceiling 0)"; exit 1; fi
done
# ── Expression-tint gate (2026-09-11) ─────────────────────────
# CharLayer's EXPR_TINTS (what the game multiplies a portrait by) and
# raster_substrate's EXPRESSION_TINTS (what the offline baker writes
# into a PNG) are the same table twice. The baker held six of the
# game's thirty-one, so every other expression baked FLAT. Zero.
echo "── expr_tint_audit.py ──"
TOUT="$(python3 expr_tint_audit.py 2>/dev/null)" || { echo "$TOUT"; exit 1; }
echo "$TOUT" | tail -1
echo ""

# ── Space-map gate (2026-09-11) ───────────────────────────────
# A gauntlet space lives in three places: the location JSON (the
# board), the host's SPACE_MAP (world positions) and the gauntlet's
# hand-copied mirror (standalone). The mirror's own comment said "copy
# the change here too", and it had rotted: five Magician stations
# missing, D'Ambrosio's booth_1/booth_6 swapped against the builder's
# numbering, precipice_door absent. Zero.
echo "── space_map_audit.py ──"
SPOUT="$(python3 space_map_audit.py 2>/dev/null)" || { echo "$SPOUT"; exit 1; }
echo "$SPOUT" | tail -1
echo ""

# ── Mood-vs-clock gate (2026-09-11) ───────────────────────────
# A mood is a claim about time and light. ch23_sleep ran five midnight
# bedrooms under dawn_warm for a month because the mood was placed once
# and never revisited when the chapter's clock moved. Light-against-dark
# only; deliberate choices are declared in the tool. Zero.
echo "── mood_clock_audit.py ──"
MOUT="$(python3 mood_clock_audit.py 2>/dev/null)" || true
echo "$MOUT" | tail -1
MN="$(echo "$MOUT" | tail -1 | grep -oE "[0-9]+ contradicted" | grep -oE "^[0-9]+")"
if [ "${MN:-999}" -gt 0 ]; then
    echo "$MOUT" | grep "^MOOD"
    echo "REGRESSION  $MN mood cue(s) the prose contradicts (ceiling 0)"; exit 1; fi
echo ""

# ── Music-coverage gate (2026-09-11) ──────────────────────────
# A chapter whose catalog track list comes back EMPTY is scored by
# AudioMgr's fallback — the unlocked playlist — so it plays whatever
# came before it. That happened two ways: 234 scenes no entry named,
# and 36 entries chapters DID name whose file was never rendered. Six
# volumes played vol5's four beds. Both gate at zero.
echo "── music_coverage_audit.py ──"
MUOUT="$(python3 music_coverage_audit.py 2>/dev/null)" || {
    echo "$MUOUT" | grep "^SILENT\|^NOFILE" | head -20
    echo "$MUOUT" | tail -1; exit 1; }
echo "$MUOUT" | tail -1
echo ""

# ── Audio-reference gate (2026-09-11) ─────────────────────────
# Everything the catalog does NOT cover: every assets/audio path in a
# .gd/.json/.tscn/.tres, and every SFXBank preset a *_BANK_KEYS table
# routes to. First run: 15 paths that had never existed — the
# gauntlet's twelve dead .ogg fallbacks, the Fool's two jukebox 45s
# (usable items that played nothing) and the file gating the Music
# Player's TAPE REEL skin, which was therefore unreachable. Zero.
echo "── audio_reference_audit.py ──"
AROUT="$(python3 audio_reference_audit.py 2>/dev/null)" || {
    echo "$AROUT" | grep "^NOFILE\|^NOPRESET" | head -20
    echo "$AROUT" | tail -1; exit 1; }
echo "$AROUT" | tail -1
echo ""

# ── Finale-id gate (2026-09-11) ───────────────────────────────
# TarotGauntletGame branches on finale ids in three places (milestone
# unlocks, achievement triggers, ending stings). An arm naming an id
# no finale.json produces never runs and looks like working code: the
# Priestess block matched six ids from a staging where the board was a
# recording booth, so no priestess finale milestone could ever fire.
echo "── finale_id_audit.py ──"
FIOUT="$(python3 finale_id_audit.py 2>/dev/null)" || {
    echo "$FIOUT" | grep "^DEAD" | head -20
    echo "$FIOUT" | tail -1; exit 1; }
echo "$FIOUT" | tail -1
echo ""

# ── Inside/out gate (2026-09-11) ──────────────────────────────
# The prose says where the camera is. The Magician opened on the
# cathedral interior under two paragraphs of the warehouse seen from
# the road; the Harmony Creek prelude walked into the Miller kitchen
# with the street still on screen. Strong place openers only; a
# window in the two lines before makes an exterior line a view.
echo "── inside_out_audit.py ──"
IOOUT="$(python3 inside_out_audit.py 2>/dev/null)" || {
    echo "$IOOUT" | grep -A1 "^PLACE" | head -30
    echo "$IOOUT" | tail -1; exit 1; }
echo "$IOOUT" | tail -1
echo ""

# ── Phantom-surface gate (2026-09-10) ─────────────────────────
# A detail pass that hard-codes a desk/counter/bar origin the builder
# never put there (eighteen locales had one). Static: reads the x/y/z
# claims in every builder and checks a box top exists there. Zero.
echo "── phantom_surface_audit.py ──"
PHOUT="$(python3 phantom_surface_audit.py 2>/dev/null | grep -v "^\[")" || true
echo "$PHOUT" | tail -1
PHN="$(echo "$PHOUT" | tail -1 | grep -oE "[0-9]+ unbacked" | grep -oE "^[0-9]+")"
if [ "${PHN:-999}" -gt 0 ]; then
    echo "$PHOUT" | grep "^   L"
    echo "REGRESSION  $PHN unbacked surface claim(s) (ceiling 0)"; exit 1; fi
echo ""

# FLOAT reached 2 on 2026-09-09 (two palmetto trunks on terrain samples)
# after 1408 → 713 → 353 → 102 → 2 across five class passes. ZERO-
# REGRESSION CEILING 2: drive it down; never raise it.
FLOAT_CEILING=0
N="$(echo "$GLINE" | grep -oE "FLOAT [0-9]+" | grep -oE "[0-9]+$")"
if [ "${N:-999}" -gt "$FLOAT_CEILING" ]; then
    echo "$GOUT" | grep "^   FLOAT"
    echo "REGRESSION  $N floating props (ceiling $FLOAT_CEILING)"; exit 1; fi
echo ""
