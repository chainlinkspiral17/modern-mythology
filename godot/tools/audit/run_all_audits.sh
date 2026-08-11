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

# holdout: recorded ceiling (2026-08-11)
HOLDOUTS = {
    "diner": 6,             # 4 ticket-tuck contacts <=0.06
    "crumpled_barn": 15,    # the crumple IS the overlap
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
