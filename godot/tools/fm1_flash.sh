#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════
# fm1_flash.sh
# Guided firmware install for the M-VAVE FM-1 on the Steam Deck
# (or any Linux desktop). Wraps Baud Girl's official browser
# installer: this script NEVER writes to the synth itself.
#
# What it automates:
#   1. preflight — Desktop Mode, Chrome/Edge present (and allowed to
#      see MIDI devices if it's a Flatpak), FM-1 plugged in, plugged
#      in DIRECTLY (no dock/hub), Deck on AC power.
#   2. reads the current firmware version (read-only identity query,
#      the same 10 bytes the official updater sends first).
#   3. blocks sleep / idle-suspend for the whole session.
#   4. opens the installer in a clean, dedicated browser profile and
#      waits for you to close that window.
#   5. post-check — waits for the synth to come back, tells you
#      whether it booted normally or is parked in updater mode
#      (resumable: just re-run this script), reads the new version,
#      writes a log.
#
# What it does NOT do: the actual flash. The firmware image only
# exists inside Baud Girl's web installer, and the update protocol
# still has documented unknowns with no recovery path for a bad
# write (ip2k/mvave-fm1-open-firmware docs/03 + docs/07). The clicks
# inside the installer page stay yours.
#
# Usage:
#   ./fm1_flash.sh            # full guided run
#   ./fm1_flash.sh --check    # preflight + version read only
#   FM1_INSTALLER_URL=https://… ./fm1_flash.sh   # override the page
#   FM1_BROWSER="flatpak run com.google.Chrome" ./fm1_flash.sh
# ════════════════════════════════════════════════════════════════

set -u

INSTALLER_URL="${FM1_INSTALLER_URL:-https://baudgirl.com/}"
SYSFS_USB="${FM1_SYSFS_USB:-/sys/bus/usb/devices}"     # overridable for testing
PROC_ASOUND="${FM1_PROC_ASOUND:-/proc/asound}"
LOG_DIR="${FM1_LOG_DIR:-$HOME/fm1-flash-logs}"
NORMAL_ID="4c4a:c755"     # FM-1 playing      ("FM-1 Midi")
LOADER_ID="4d4a:4155"     # FM-1 OTA loader   ("ota-FM-1")
IDENTITY_QUERY='F0 00 32 45 00 00 00 40 7F F7'

CHECK_ONLY=0
[ "${1:-}" = "--check" ] && CHECK_ONLY=1

mkdir -p "$LOG_DIR" 2>/dev/null || LOG_DIR="/tmp"
LOG="$LOG_DIR/fm1-flash-$(date +%Y%m%d-%H%M%S).log"
: > "$LOG"

say()  { echo "$*"; echo "$*" >> "$LOG"; }
ok()   { say "  ✓ $*"; }
warn() { say "  ! $*"; WARNINGS=$((WARNINGS + 1)); }
bad()  { say "  ✗ $*"; BLOCKERS=$((BLOCKERS + 1)); }
WARNINGS=0
BLOCKERS=0

# ── helpers ─────────────────────────────────────────────────────

# Echo "<sysfs-name> <vid:pid>" for the first FM-1 found (normal or loader).
find_fm1() {
  local d vid pid
  for d in "$SYSFS_USB"/*; do
    [ -f "$d/idVendor" ] || continue
    vid=$(cat "$d/idVendor" 2>/dev/null); pid=$(cat "$d/idProduct" 2>/dev/null)
    case "$vid:$pid" in
      "$NORMAL_ID"|"$LOADER_ID") echo "$(basename "$d") $vid:$pid"; return 0 ;;
    esac
  done
  return 1
}

# Hub chain between the root port and the device. "3-1" is direct;
# "3-1.4" sits behind the hub at "3-1"; "3-1.4.2" behind two.
hub_chain() {
  local name="$1" port parent out=""
  port="${name#*-}"
  while [[ "$port" == *.* ]]; do
    port="${port%.*}"
    parent="${name%%-*}-$port"
    out="$out [$(cat "$SYSFS_USB/$parent/product" 2>/dev/null || echo "hub $parent")]"
  done
  echo "$out"
}

# ALSA raw-MIDI port of the FM-1 in normal mode, e.g. hw:2,0,0.
fm1_rawmidi_port() {
  local c n
  for c in "$PROC_ASOUND"/card*; do
    [ -f "$c/usbid" ] || continue
    if [ "$(tr 'A-F' 'a-f' < "$c/usbid")" = "$NORMAL_ID" ]; then
      n="${c##*card}"; echo "hw:$n,0,0"; return 0
    fi
  done
  command -v amidi >/dev/null 2>&1 &&
    amidi -l 2>/dev/null | awk 'tolower($0) ~ /fm-1/ && tolower($0) !~ /ota/ {print $2; exit}'
}

# Decode the 41-byte identity reply. The body between F0 and F7 is a
# 7-bit LSB-first bitstream that unpacks to a 34-byte JieLi ID block
# starting 00 59 11; the version is the decimal after "<model>_".
# Mirrors fm1_identify.py in ip2k/mvave-fm1-open-firmware.
decode_identity() {
  command -v python3 >/dev/null 2>&1 || { echo "(python3 missing — raw reply logged)"; return; }
  python3 - "$1" <<'PY'
import re, sys
raw = [int(x, 16) for x in sys.argv[1].split()]
if not raw or raw[0] != 0xF0 or raw[-1] != 0xF7:
    print("(no identity reply)"); sys.exit()
body = raw[1:-1]
acc = bits = 0; out = []
for b in body:
    acc |= (b & 0x7F) << bits; bits += 7
    while bits >= 8:
        out.append(acc & 0xFF); acc >>= 8; bits -= 8
blk = bytes(out[:34])
if blk[:3] != b"\x00\x59\x11":
    print("(unrecognised reply)"); sys.exit()
m = re.search(rb"([A-Za-z0-9-]{2,})_(\d+)", blk[6:31])
print(f"{m.group(1).decode()}_{int(m.group(2)):03d}" if m else "(version field not found)")
PY
}

# Read the version over raw MIDI. Read-only; only ever sends the query.
read_version() {
  local port reply
  command -v amidi >/dev/null 2>&1 || { echo "(amidi not installed — use IDENTIFY in fm1_console.html)"; return; }
  port=$(fm1_rawmidi_port)
  [ -n "$port" ] || { echo "(no FM-1 raw-MIDI port)"; return; }
  echo "  sending read-only identity query to $port: $IDENTITY_QUERY" >> "$LOG"
  reply=$(amidi -p "$port" -S "$IDENTITY_QUERY" -d -t 3 2>&1)
  echo "  reply: $reply" >> "$LOG"
  if echo "$reply" | grep -qi "busy"; then
    echo "(port busy — PipeWire holds raw MIDI; use IDENTIFY in fm1_console.html instead)"; return
  fi
  reply=$(echo "$reply" | grep -oE '\b[0-9A-Fa-f]{2}\b' | tr '\n' ' ')
  decode_identity "$reply"
}

# Find Chrome / Edge / Chromium. Prints the command to run.
find_browser() {
  if [ -n "${FM1_BROWSER:-}" ]; then echo "$FM1_BROWSER"; return 0; fi
  local id b
  if command -v flatpak >/dev/null 2>&1; then
    for id in com.google.Chrome com.microsoft.Edge org.chromium.Chromium; do
      if flatpak info "$id" >/dev/null 2>&1; then echo "flatpak run $id"; return 0; fi
    done
  fi
  for b in google-chrome-stable google-chrome microsoft-edge-stable microsoft-edge chromium chromium-browser; do
    command -v "$b" >/dev/null 2>&1 && { echo "$b"; return 0; }
  done
  return 1
}

wait_for_fm1() {
  local i hit
  for i in $(seq 1 "${1:-30}"); do
    hit=$(find_fm1) && { echo "$hit"; return 0; }
    sleep 1
  done
  return 1
}

# ── 1. preflight ────────────────────────────────────────────────
say "FM-1 firmware install helper · log: $LOG"
say ""
say "→ preflight"

case "${XDG_CURRENT_DESKTOP:-}${DESKTOP_SESSION:-}" in
  *gamescope*|"") warn "not in a desktop session — switch the Deck to Desktop Mode first." ;;
  *) ok "desktop session (${XDG_CURRENT_DESKTOP:-$DESKTOP_SESSION})" ;;
esac

BROWSER=$(find_browser)
if [ -z "$BROWSER" ]; then
  bad "no Chrome / Edge / Chromium found. Install Chrome from Discover, or run:"
  say "      flatpak install -y flathub com.google.Chrome"
else
  ok "browser: $BROWSER"
  if [[ "$BROWSER" == flatpak\ run\ * ]]; then
    APPID="${BROWSER#flatpak run }"
    if flatpak info --show-permissions "$APPID" 2>/dev/null | grep -qE '^devices=.*\ball\b'; then
      ok "$APPID can see MIDI devices"
    else
      warn "$APPID may not see MIDI devices. Allow it (user-level, reversible) with:"
      say "      flatpak override --user --device=all $APPID"
    fi
  fi
fi

HIT=$(find_fm1)
if [ -z "$HIT" ]; then
  bad "FM-1 not detected over USB. Plug it in with a data-capable USB-C cable and switch it on."
  DEV=""; MODE=""
else
  DEV="${HIT%% *}"; MODE="${HIT##* }"
  if [ "$MODE" = "$LOADER_ID" ]; then
    warn "FM-1 is in UPDATER mode (ota-FM-1). A previous install stopped part-way."
    say  "      Baud Girl's installer resumes from here — continue when prompted, don't unplug."
  else
    ok "FM-1 detected (normal mode, USB $DEV)"
  fi
  CHAIN=$(hub_chain "$DEV")
  if [ -n "$CHAIN" ]; then
    warn "FM-1 is behind a hub:$CHAIN (a dock counts)"
    say  "      The open-firmware project says no hubs or docks during writes."
    say  "      Plug the FM-1 straight into the Deck's USB-C port and re-run."
  else
    ok "connected directly (no hub in the path)"
  fi
fi

AC=""; CAP=""
for p in /sys/class/power_supply/*; do
  [ -f "$p/type" ] || continue
  case "$(cat "$p/type")" in
    Mains)   [ "$(cat "$p/online" 2>/dev/null)" = "1" ] && AC=1 ;;
    Battery) CAP=$(cat "$p/capacity" 2>/dev/null) ;;
  esac
done
if [ -n "$CAP" ]; then
  if [ -n "$AC" ]; then ok "Deck on AC power (battery ${CAP}%)"
  elif [ "$CAP" -ge 50 ] 2>/dev/null; then warn "Deck on battery (${CAP}%) — AC power is safer."
  else bad "Deck battery at ${CAP}% and not charging — plug in before flashing."; fi
fi
say "  · charge the FM-1 itself too — its battery can't be read from here."

if [ "$MODE" = "$NORMAL_ID" ]; then
  BEFORE=$(read_version)
  say "  · firmware now: $BEFORE"
else
  BEFORE="(not read)"
  [ "$MODE" = "$LOADER_ID" ] && say "  · not querying the loader — leaving it alone for the installer."
fi

say ""
if [ "$CHECK_ONLY" = 1 ]; then
  say "→ --check done · $BLOCKERS blocker(s), $WARNINGS warning(s)."
  exit $(( BLOCKERS > 0 ))
fi
if [ "$BLOCKERS" -gt 0 ]; then
  say "→ $BLOCKERS blocker(s) above. Fix them and re-run."
  exit 1
fi

# ── 2. confirm ──────────────────────────────────────────────────
say "→ ready. Next: a browser window opens on $INSTALLER_URL"
say "    · allow the MIDI prompt (including 'control and reprogram')."
say "    · follow Baud Girl's installer. Don't touch the cable or the synth until it says done."
say "    · then CLOSE that browser window — this script picks up from there."
[ "$WARNINGS" -gt 0 ] && say "    · $WARNINGS warning(s) above — read them first."
read -r -p "Type go to open the installer (anything else quits): " ans
[ "$(echo "$ans" | tr "[:upper:]" "[:lower:]")" = "go" ] || { say "quit — nothing was changed."; exit 0; }

# ── 3 + 4. inhibit sleep, launch installer ──────────────────────
if [[ "$BROWSER" == flatpak\ run\ * ]]; then
  PROFILE="$HOME/.var/app/${BROWSER#flatpak run }/mm-fm1-flash-profile"
else
  PROFILE="${XDG_CACHE_HOME:-$HOME/.cache}/mm-fm1-flash-profile"
fi
mkdir -p "$PROFILE"
# shellcheck disable=SC2206
CMD=($BROWSER --user-data-dir="$PROFILE" --no-first-run --no-default-browser-check --new-window "$INSTALLER_URL")

say ""
say "→ installer open · sleep blocked until the window closes"
if command -v systemd-inhibit >/dev/null 2>&1 &&
   systemd-inhibit --what=sleep:idle --mode=block true >/dev/null 2>&1; then
  systemd-inhibit --what=sleep:idle:handle-lid-switch --who="fm1_flash.sh" \
    --why="Flashing M-VAVE FM-1 firmware" --mode=block "${CMD[@]}" >> "$LOG" 2>&1
else
  warn "couldn't take a sleep lock — set Deck sleep to Never in Settings for the next few minutes."
  "${CMD[@]}" >> "$LOG" 2>&1
fi

# ── 5. post-check ───────────────────────────────────────────────
say ""
say "→ browser closed · waiting for the FM-1 to settle"
sleep 3
HIT=$(wait_for_fm1 30)
if [ -z "$HIT" ]; then
  say "  ✗ FM-1 not visible on USB."
  say "    Unplug, switch it on, plug back in DIRECTLY, then run:  $0 --check"
  say "    If it won't power on or enumerate at all, stop retrying — see"
  say "    github.com/ip2k/mvave-fm1-open-firmware docs/07-recovery-and-risk.md"
  exit 2
fi
MODE="${HIT##* }"
if [ "$MODE" = "$LOADER_ID" ]; then
  say "  ! FM-1 is still in UPDATER mode (ota-FM-1) — the install didn't finish."
  say "    Don't unplug it. Re-run this script; the installer resumes from the loader."
  exit 3
fi
AFTER=$(read_version)
ok "FM-1 back in normal mode"
say "  · firmware before: $BEFORE"
say "  · firmware after:  $AFTER"
case "$AFTER" in
  FM-1_0[2-9]*) ok "that's a Baud Girl FM-1+VA build." ;;
  FM-1_01*)     warn "still a stock version — the installer may not have run its write step." ;;
esac
say ""
say "→ done. Open godot/tools/fm1_console.html and press IDENTIFY to confirm from the tools side."
say "  log: $LOG"
