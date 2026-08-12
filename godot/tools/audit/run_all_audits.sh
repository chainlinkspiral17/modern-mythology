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

# ── Shot-cue coverage (2026-08-12) · informational ──────────────
# Object cues with no marker no longer zoom into a wall (the
# director substitutes a same-type marker from the locale, or holds
# the wide), but a high count still means chapters are asking for
# framings nobody authored. Track it; drive it down.
echo "── shot_marker_audit.py ──"
python3 shot_marker_audit.py 2>/dev/null | tail -2
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
