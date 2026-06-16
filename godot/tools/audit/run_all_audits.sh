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
