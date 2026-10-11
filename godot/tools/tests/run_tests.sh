#!/usr/bin/env bash
# Run the browser-tool + AudioMgr test suites.
#   godot/tools/tests/run_tests.sh              # everything offline (≈ 3–4 min)
#   godot/tools/tests/run_tests.sh daw dsp      # just these suites
#   TEST_NETWORK=1 …  also download from the PATCH BANK sources
#   TEST_SLOW=1 …     also render TEMP TRACKS with stems (several minutes)
#   GODOT=/path/to/Godot_v4.6 …   Godot binary for the AudioMgr suite (skipped without one)
#   CHROME_PATH=…     Chromium for playwright (defaults to playwright's own)
# Needs node + playwright (npm i -g playwright). Exit code = number of failed suites.
set -uo pipefail
cd "$(dirname "$0")"
export NODE_PATH="${NODE_PATH:-$(npm root -g 2>/dev/null)}"
suites=("$@"); [ ${#suites[@]} -eq 0 ] && suites=(data dsp engines touch daw daw_fx daw_rec fm1_checkout godot_audiomgr godot_director patchbank_network)
failed=0; t0=$(date +%s)
for s in "${suites[@]}"; do
  f="$s.test.js"; [ -f "$f" ] || { echo "no suite $s"; failed=$((failed+1)); continue; }
  node "$f" || failed=$((failed+1))
  echo
done
echo "── $(( $(date +%s) - t0 )) s · ${#suites[@]} suite(s) · $failed failed"
exit $failed
