# Sourced by the other scripts. Warns (non-blocking) if this clone is not the
# canonical one, so asset copies/edits/launches don't silently land in a
# stray clone. Expects $REPO to be set by the caller.
__CANON="$HOME/modern-mythology"
if [ "${REPO:-}" != "$__CANON" ]; then
  echo "!! ───────────────────────────────────────────────────────────────────"
  echo "!! WARNING: running from a NON-canonical clone:"
  echo "!!   this:      $REPO"
  echo "!!   canonical: $__CANON"
  echo "!! You have multiple clones. Keep all assets/edits/launches in the"
  echo "!! canonical clone or things won't line up. (continuing in 2s…)"
  echo "!! ───────────────────────────────────────────────────────────────────"
  sleep 2 || true
fi
