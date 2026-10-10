#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════
# fm1_flash.sh
# Guided firmware install for the M-VAVE FM-1 on the Steam Deck
# (or any Linux desktop). Wraps the firmware author's own browser
# installer: this script NEVER writes to the synth itself.
#
# Which firmwares it offers, how each one shows up on USB, how to
# tell them apart and how to recover — all of it comes from
# fm1_firmwares.js (the same registry the browser tools use).
#
# What it automates:
#   1. preflight — Desktop Mode, Chrome/Edge present (and allowed to
#      see MIDI devices if it's a Flatpak), FM-1 plugged in (and in
#      which mode: playing / updater / boot / game port), hub in the
#      path, Deck power.
#   2. reads what's on it now (read-only: the vendor identity query
#      the official updater sends first, plus the Felucca-family
#      editor INFO request on 1209:0001 devices).
#   3. blocks sleep / idle-suspend while the installer is open.
#   4. opens the chosen firmware's installer in a clean browser
#      profile and waits for you to close that window.
#   5. post-check — playing again, parked in the updater (resumable:
#      re-run with the same --firmware), or gone; is it the firmware
#      you picked?; writes a log.
#
# What it does NOT do: the actual flash. Each firmware's image and
# package checks live inside its own web installer, and a bad write
# can need a hardware dongle to recover.
#
# Usage:
#   ./fm1_flash.sh                      # guided run, menu of firmwares
#   ./fm1_flash.sh --firmware sloop     # straight to one (ids: --list)
#   ./fm1_flash.sh --list               # every installable firmware
#   ./fm1_flash.sh --check              # preflight + version read only
#   FM1_INSTALLER_URL=https://… ./fm1_flash.sh --firmware x   # override the page
#   FM1_BROWSER="flatpak run com.google.Chrome" ./fm1_flash.sh
# ════════════════════════════════════════════════════════════════

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REGISTRY="${FM1_REGISTRY_FILE:-$SCRIPT_DIR/fm1_firmwares.js}"
SYSFS_USB="${FM1_SYSFS_USB:-/sys/bus/usb/devices}"     # overridable for testing
PROC_ASOUND="${FM1_PROC_ASOUND:-/proc/asound}"
LOG_DIR="${FM1_LOG_DIR:-$HOME/fm1-flash-logs}"
IDENTITY_QUERY='F0 00 32 45 00 00 00 40 7F F7'
EDITOR_INFO='F0 7D 46 4C 01 F7'     # Felucca-family editor INFO (read-only)

command -v python3 >/dev/null 2>&1 || { echo "python3 is needed (it ships with SteamOS)."; exit 1; }
[ -f "$REGISTRY" ] || { echo "firmware registry not found: $REGISTRY"; exit 1; }

# ── registry queries (python reads the JSON between the markers) ─────
reg() {
  python3 -I - "$REGISTRY" "$@" <<'PY'
import json, re, sys
src = open(sys.argv[1], encoding="utf-8").read()
R = json.loads(re.search(r"/\*FM1-JSON-BEGIN\*/(.*)/\*FM1-JSON-END\*/", src, re.S).group(1))
F = R["firmwares"]; cmd = sys.argv[2]; a = sys.argv[3:]
by = {f["id"]: f for f in F}
inst = [f for f in F if f.get("status") == "installable" and f.get("installer")]
fam = lambda f: (f.get("usb") or {}).get("vidpid") == "1209:0001"
if cmd == "installable":
    print("\n".join(f["id"] for f in inst))
elif cmd == "menu":
    for i, f in enumerate(inst, 1):
        print(f"{i:>2}) {f['name'][:16]:<16} {f['kind'][:9]:<9} {f['author'][:22]:<22} {(f.get('summary') or '')[:58]}")
elif cmd == "pick":
    n = int(a[0]) if a and a[0].isdigit() else 0
    print(inst[n - 1]["id"] if 1 <= n <= len(inst) else "")
elif cmd == "get":
    v = by.get(a[0], {})
    for k in a[1].split("."):
        v = v.get(k) if isinstance(v, dict) else None
    print("; ".join(map(str, v)) if isinstance(v, list) else ("" if v is None else v))
elif cmd == "usb":          # vidpid<TAB>kind<TAB>product-regex  (kind: play | noMidi)
    seen = set()
    for f in F:
        u = f.get("usb")
        if not u or u.get("unverified"): continue
        kind = "noMidi" if "no MIDI" in " ".join(f.get("warnings") or []) else "play"
        for p in u["products"]:
            key = (u["vidpid"], p)
            if key in seen: continue
            seen.add(key)
            print(f"{u['vidpid']}\t{kind}\t{p}")
elif cmd == "loaders":
    print("\n".join(R["loaders"]["usb"]))
elif cmd == "family-products":
    print("\n".join(sorted({p for f in F if fam(f) for p in f["usb"]["products"]})))
elif cmd == "classify":     # vendor-name info-string port-product → id<TAB>display
    vendor, info, port = (a + ["", "", ""])[:3]
    fid, disp = "", vendor or info or "(no reply)"
    if info:
        hit = next((f for f in F if f.get("info") and re.search(f["info"]["match"], info, re.I)), None)
        fid = hit["id"] if hit else "felucca-family"
        disp = info
        if hit and hit["id"] == "felucca": disp = "Felucca " + re.sub(r"^FELUCCA\s*", "", info, flags=re.I)
        elif hit and re.match(r"^FELUCCA\s+", info, re.I): disp = re.sub(r"^FELUCCA\s+", "", info, flags=re.I)
        if vendor: disp += f" (package {vendor})"
    else:
        m = re.match(r"^(\S+?)_(\d+)$", vendor or "")
        if m:
            v = int(m.group(2))
            if m.group(1).lower().startswith("ota"): fid, disp = "loader", vendor + " (updater)"
            elif v == 0: fid, disp = "rescue", vendor + " (USB rescue mode)"
            elif v >= 900:
                byp = [f for f in F if fam(f) and any(p != "Felucca" and p.lower() in port.lower() for p in f["usb"]["products"])]
                fid = byp[0]["id"] if len(byp) == 1 else "felucca-family"
                disp = vendor + ("" if len(byp) == 1 else " (Felucca family — editor didn't answer)")
            else:
                hits = [f for f in F if f.get("identity") and f["identity"].get("range") and not fam(f)
                        and f["identity"]["range"][0] <= v <= f["identity"]["range"][1]]
                fid = hits[0]["id"] if len(hits) == 1 else ("stock" if 9 <= v <= 19 else "unknown")
    name = by[fid]["name"] if fid in by else fid
    if not info and fid in by and vendor: disp = f"{name} ({vendor})"
    print(f"{fid}\t{disp}\t{name}")
else:
    sys.exit("unknown reg command " + cmd)
PY
}

CHECK_ONLY=0
TARGET=""
while [ $# -gt 0 ]; do
  case "$1" in
    --check)      CHECK_ONLY=1 ;;
    --firmware)   TARGET="${2:-}"; shift ;;
    --firmware=*) TARGET="${1#*=}" ;;
    --list)       reg menu; echo; echo "ids: $(reg installable | tr '\n' ' ')"; exit 0 ;;
    *) echo "unknown option: $1 (use --check, --list, --firmware <id>)"; exit 1 ;;
  esac
  shift
done
if [ -n "$TARGET" ] && ! reg installable | grep -qx "$TARGET"; then
  echo "unknown firmware '$TARGET'. Installable: $(reg installable | tr '\n' ' ')"; exit 1
fi

mkdir -p "$LOG_DIR" 2>/dev/null || LOG_DIR="/tmp"
LOG="$LOG_DIR/fm1-flash-$(date +%Y%m%d-%H%M%S).log"
: > "$LOG"

say()  { echo "$*"; echo "$*" >> "$LOG"; }
ok()   { say "  ✓ $*"; }
warn() { say "  ! $*"; WARNINGS=$((WARNINGS + 1)); }
bad()  { say "  ✗ $*"; BLOCKERS=$((BLOCKERS + 1)); }
WARNINGS=0
BLOCKERS=0

USB_TABLE="$(reg usb)"
LOADER_IDS="$(reg loaders)"

# ── helpers ─────────────────────────────────────────────────────

# Echo "<sysfs-name> <mode> <vid:pid> <product>" for the first FM-1 found.
# mode: play | loader | boot | noMidi. A shared vid:pid (1209:0001) only
# counts when its product string is one the registry knows.
find_fm1() {
  local d vid pid prod line pv kind pp
  for d in "$SYSFS_USB"/*; do
    [ -f "$d/idVendor" ] || continue
    vid=$(cat "$d/idVendor" 2>/dev/null); pid=$(cat "$d/idProduct" 2>/dev/null)
    prod=$(cat "$d/product" 2>/dev/null || true)
    if echo "$LOADER_IDS" | grep -qx "$vid:$pid"; then
      if [ "$vid:$pid" = "4c4a:8057" ]; then echo "$(basename "$d") boot $vid:$pid $prod"; else echo "$(basename "$d") loader $vid:$pid $prod"; fi
      return 0
    fi
    while IFS=$'\t' read -r pv kind pp; do
      [ "$pv" = "$vid:$pid" ] || continue
      if [ "$pv" != "1209:0001" ] || echo "$prod" | grep -qiF "$pp"; then
        echo "$(basename "$d") $kind $vid:$pid $prod"; return 0
      fi
    done <<< "$USB_TABLE"
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

# ALSA raw-MIDI port of the playing FM-1, e.g. hw:2,0,0.
fm1_rawmidi_port() {
  local vidpid="$1" c n
  for c in "$PROC_ASOUND"/card*; do
    [ -f "$c/usbid" ] || continue
    if [ "$(tr 'A-F' 'a-f' < "$c/usbid")" = "$vidpid" ]; then n="${c##*card}"; echo "hw:$n,0,0"; return 0; fi
  done
  command -v amidi >/dev/null 2>&1 &&
    amidi -l 2>/dev/null | awk 'tolower($0) ~ /fm-1|felucca|jangada|melodee|x0x/ && tolower($0) !~ /ota|update/ {print $2; exit}'
}

hexbytes() { grep -oE '\b[0-9A-Fa-f]{2}\b' | tr '\n' ' '; }

# Vendor identity reply → "FM-1_015" etc. (7-bit LSB-first → 34-byte
# JieLi block 00 59 11 …; mirrors ip2k/mvave-fm1-open-firmware).
decode_identity() {
  python3 -I - "$1" <<'PY'
import re, sys
raw = [int(x, 16) for x in sys.argv[1].split()]
if not raw or raw[0] != 0xF0 or raw[-1] != 0xF7: sys.exit()
acc = bits = 0; out = []
for b in raw[1:-1]:
    acc |= (b & 0x7F) << bits; bits += 7
    while bits >= 8: out.append(acc & 0xFF); acc >>= 8; bits -= 8
blk = bytes(out[:34])
if blk[:3] != b"\x00\x59\x11": sys.exit()
m = re.search(rb"([A-Za-z0-9-]{2,})_(\d+)", blk[6:31])
if m: print(m.group(1).decode() + "_" + m.group(2).decode().rjust(3, "0"))
PY
}

# Editor INFO reply F0 7D 46 4C 01 "<string>" 00 … → the string.
decode_editor_info() {
  python3 -I - "$1" <<'PY'
import sys
raw = [int(x, 16) for x in sys.argv[1].split()]
for i in range(len(raw) - 5):
    if raw[i:i+5] == [0xF0, 0x7D, 0x46, 0x4C, 0x01]:
        s = ""
        for b in raw[i+5:]:
            if b < 32 or b > 126 or len(s) >= 32: break
            s += chr(b)
        print(s.strip()); break
PY
}

# Read what's on the synth. Read-only. Prints "<id>\t<display>\t<name>".
read_version() {
  local vidpid="$1" product="$2" port reply vendor="" info=""
  command -v amidi >/dev/null 2>&1 || { printf 'unknown\t(amidi not installed — use IDENTIFY in fm1_console.html)\t?\n'; return; }
  port=$(fm1_rawmidi_port "$vidpid")
  [ -n "$port" ] || { printf 'unknown\t(no FM-1 raw-MIDI port)\t?\n'; return; }
  echo "  sending read-only identity query to $port: $IDENTITY_QUERY" >> "$LOG"
  reply=$(amidi -p "$port" -S "$IDENTITY_QUERY" -d -t 3 2>&1)
  echo "  reply: $reply" >> "$LOG"
  if echo "$reply" | grep -qi "busy"; then
    printf 'unknown\t(port busy — another app has it open, usually a Chrome tab on an installer or fm1_console.html. Close Chrome and re-run, or press IDENTIFY in the console)\t?\n'; return
  fi
  vendor=$(decode_identity "$(echo "$reply" | hexbytes)")
  # The Felucca family shares 1209:0001 and colliding FM-1_9xx numbers;
  # its editor INFO string names the fork.
  if [ "$vidpid" = "1209:0001" ] || [[ "$vendor" == FM-1_9* ]]; then
    echo "  sending read-only editor INFO to $port: $EDITOR_INFO" >> "$LOG"
    info=$(amidi -p "$port" -S "$EDITOR_INFO" -d -t 2 2>&1)
    echo "  reply: $info" >> "$LOG"
    info=$(decode_editor_info "$(echo "$info" | hexbytes)")
  fi
  reg classify "$vendor" "$info" "$product"
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

# split "dev mode vidpid product…"
parse_hit() { DEV=$(echo "$1" | cut -d' ' -f1); MODE=$(echo "$1" | cut -d' ' -f2); VIDPID=$(echo "$1" | cut -d' ' -f3); PRODUCT=$(echo "$1" | cut -d' ' -f4-); }

# ── 1. preflight ────────────────────────────────────────────────
say "FM-1 firmware install helper · log: $LOG"
say "  registry: $(reg installable | wc -l) installable firmwares (fm1_firmwares.js)"
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

DEV=""; MODE=""; VIDPID=""; PRODUCT=""
HIT=$(find_fm1)
if [ -z "$HIT" ]; then
  bad "FM-1 not detected over USB. Plug it in with a data-capable USB-C cable and switch it on."
else
  parse_hit "$HIT"
  case "$MODE" in
    loader) warn "FM-1 is in UPDATER mode ($VIDPID ${PRODUCT:-ota}). A previous install stopped part-way."
            say  "      Re-open the SAME firmware's installer and press install again — it resumes from here. Don't unplug." ;;
    boot)   bad "FM-1 is in boot mode (4c4a:8057 / WL80UBOOT) — the application isn't running."
            say "      Stop here: recovery needs a FM-1 Transporter (or the firmware's documented rescue). Don't keep retrying installers." ;;
    noMidi) warn "FM-1 is running a game port (${PRODUCT:-no MIDI}) — web installers can't reach it over MIDI."
            say  "      Follow that port's own instructions to get back to a MIDI firmware." ;;
    *)      ok "FM-1 detected (playing, $VIDPID \"${PRODUCT}\", USB $DEV)" ;;
  esac
  CHAIN=$(hub_chain "$DEV")
  if [ -n "$CHAIN" ]; then
    warn "FM-1 is behind a hub:$CHAIN (a dock counts)"
    say  "      Installers ask for a direct cable. On a Deck the dock is also the keyboard and power,"
    say  "      so if you stay on it: unplug every other USB device from the dock, keep it on AC, don't touch the cable."
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

BEFORE_ID=""; BEFORE="(not read)"
if [ "$MODE" = "play" ]; then
  IFS=$'\t' read -r BEFORE_ID BEFORE _ <<< "$(read_version "$VIDPID" "$PRODUCT")"
  say "  · firmware now: $BEFORE"
elif [ "$MODE" = "loader" ]; then
  say "  · not querying the updater — leaving it alone for the installer."
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

# ── 2. choose + confirm ─────────────────────────────────────────
if [ -z "$TARGET" ]; then
  say "→ which firmware? (details: godot/tools/fm1_firmware_atlas.html)"
  reg menu | while IFS= read -r line; do say "   $line"; done
  read -r -p "Number (anything else quits): " pick
  TARGET=$(reg pick "$pick")
  [ -n "$TARGET" ] || { say "quit — nothing was changed."; exit 0; }
fi
TNAME=$(reg get "$TARGET" name)
INSTALLER_URL="${FM1_INSTALLER_URL:-$(reg get "$TARGET" installer)}"
say "  · target: $TNAME $(reg get "$TARGET" version) — $(reg get "$TARGET" author)"
REC=$(reg get "$TARGET" recovery); [ -n "$REC" ] && say "  · if it goes wrong: $REC"
WARN=$(reg get "$TARGET" warnings); [ -n "$WARN" ] && say "  ! its author says: $WARN"
case "$REC" in *Transporter*|*dongle*) case "$REC" in *RESCUE*|*SAFE*) ;; *)
  say "    No USB rescue key for this one — a failed write that won't boot needs a hardware dongle." ;; esac ;; esac
if [ "$TARGET" = "$BEFORE_ID" ]; then
  say "  · it's already on $TNAME — the installer may refuse the same version (that's normal)."
elif [ -n "$(reg get "$BEFORE_ID" editor)" ] || [ "$BEFORE_ID" = "felucca-family" ]; then
  say "  · switching away from $BEFORE: back up first in its web editor (projects, presets, samples)."
  say "    Projects don't carry between different firmwares."
fi

say "→ ready. Next: a browser window opens on $INSTALLER_URL"
say "    · allow the MIDI prompt (including 'control and reprogram')."
say "    · follow the installer (press its INSTALL button). Don't touch the cable or the synth until it says done."
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
  say "    Unplug, switch it on, plug back in, then run:  $0 --check"
  say "    If it won't power on or enumerate at all, stop retrying. Recovery for $TNAME: $REC"
  exit 2
fi
parse_hit "$HIT"
if [ "$MODE" = "loader" ]; then
  say "  ! FM-1 is still in UPDATER mode ($VIDPID) — the install didn't finish."
  say "    Don't unplug it. Re-run:  $0 --firmware $TARGET   — the installer resumes from the loader."
  exit 3
fi
if [ "$MODE" = "boot" ]; then
  say "  ✗ FM-1 came back in boot mode (WL80UBOOT). Recovery: $REC"
  exit 4
fi
IFS=$'\t' read -r AFTER_ID AFTER AFTER_NAME <<< "$(read_version "$VIDPID" "$PRODUCT")"
ok "FM-1 playing again ($VIDPID \"$PRODUCT\")"
say "  · firmware before: $BEFORE"
say "  · firmware after:  $AFTER"
case "$AFTER_ID" in
  "$TARGET")        ok "that's $TNAME." ;;
  felucca-family)   ok "a Felucca-family build (its editor didn't name itself — IDENTIFY in fm1_console.html checks again)." ;;
  rescue)           warn "it's in USB rescue mode — run the $TNAME installer again." ;;
  unknown|"")       say "  · couldn't read the version from here — press IDENTIFY in fm1_console.html." ;;
  *)                warn "expected $TNAME but the synth reports $AFTER — the install may not have taken." ;;
esac
case "$(reg get "$TARGET" summary) $(reg get "$TARGET" warnings)" in
  *"USB audio"*) say "  · unplug and replug the FM-1 once so the computer finds its USB audio input." ;;
esac
say ""
say "→ done. Open godot/tools/fm1_console.html and press IDENTIFY to confirm from the tools side."
say "  log: $LOG"
