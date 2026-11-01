/* fm1_firmwares.js — the M-VAVE FM-1 firmware registry.
 *
 * ONE source of truth for every tool that cares which firmware is on
 * the synth:
 *   midi_input.js        port auto-select, identity → firmware, per-role
 *                        OUT channels, DX7 guard
 *   fm1_console.html     firmware picker + notes
 *   fm1_firmware_atlas.html   the browsable scene map
 *   fm1_flash.sh         installer menu, USB detection, post-check
 *                        (reads the JSON between the markers below with
 *                        python3 — keep it strict JSON: double quotes, no
 *                        trailing commas, no comments inside)
 *
 * Catalogued 2026-10-10 from each project's own source (usb.c string
 * descriptors, build.py identity, editor.c INFO, TRK_DEF default
 * sounds) — see lore/_INSTRUMENT_TOOLS_PLAYBOOK.md for how to add one.
 * Re-checked 2026-11-01 against each project's GitHub releases / README /
 * source (`checked`, `sources`, `buzz`, `stars` below).
 *
 * Field guide:
 *   usb.vidpid / usb.products   what the running firmware enumerates as.
 *                    1209:0001 is a shared hobby ID: match the product.
 *                    usb.unverified: read from docs / source, not seen.
 *   identity.range   decimal after "FM-1_" in the vendor identity reply
 *                    (F0 00 32 45 …). Ranges overlap between forks, so
 *                    INFO decides inside the Felucca family. For
 *                    1209:0001 firmwares the range is informational; for
 *                    the rest it classifies (FM1 Open's FM-1_8000014 is
 *                    matched by range before the ≥ 900 family rule).
 *   info.match       regex on the editor INFO string (F0 7D 46 4C 01 F7),
 *                    tested in registry order — specific forks first
 *                    (GHOULBOX's "FELUCCA v1.4.1 GB…" must win over Felucca).
 *   roles            OUT channel per tool role. Felucca-family default
 *                    sounds (TRK_DEF): track 1 bass, 2 pad/keys, 3 lead.
 *   dx7              true: F0 43 voice dumps work · "editor": only via
 *                    the firmware's web editor · false: no FM-DX7 engine ·
 *                    "unknown".
 *   cc               (optional, hardware-verified) filter: the CC that moves
 *                    the filter · responds / ignores: CCs tested from USB ·
 *                    knobsSend: whether turning the knobs sends CC.
 *   keys             (optional) channel / fixed velocity the keys send.
 *   verified         (optional) what a real unit confirmed, when, on which
 *                    version and how; `pending` lists what is still untested.
 *                    Only FM-1 CHECK-OUT results (or equal) go here.
 *   prerelease       (optional) newest pre-release / release candidate, when
 *                    newer than `version` (which is the newest stable).
 *   checked          date the version / status / buzz were last checked.
 *   sources          URLs those facts came from (GitHub first).
 *   buzz             evidence-backed popularity note: stars, articles, demo
 *                    videos, forks — every number with its source and date.
 *   stars            (optional) GitHub stars / forks on `checked`.
 */
"use strict";

const FM1_REGISTRY = /*FM1-JSON-BEGIN*/{
  "catalogued": "2026-10-10",
  "checked": "2026-11-01",
  "loaders": {
    "usb": ["4d4a:4155", "1209:0002", "4c4a:8057"],
    "names": ["ota-FM-1", "Update", "WL80UBOOT"],
    "note": "updater / boot modes — never treat as a playable port; re-run the SAME firmware's installer to finish"
  },
  "firmwares": [
    {
      "id": "stock", "name": "Stock M-VAVE", "author": "M-VAVE", "url": "https://www.m-vave.com/download",
      "license": "proprietary", "version": "V16", "date": "2026-10-21", "kind": "synth", "base": "—",
      "status": "installable", "installer": null, "editor": null,
      "cli": "M-UPGRADE (Win/Mac) with the V16 .fwsc; the V15 image stays in m-vave/fm1_open (an earlier macOS M-UPGRADE shipped V14)",
      "usb": { "vidpid": "4c4a:c755", "products": ["FM-1"] },
      "identity": { "range": [9, 19], "pattern": "FM-1_015 (V16 expected FM-1_016)" }, "info": null,
      "roles": null, "drums": null, "clock": "unknown", "dx7": true,
      "recovery": "single flash bank, no rescue key; a unit that will not boot needs a mask-ROM dongle (FM-1 Transporter)",
      "warnings": ["V16 not yet seen on a unit here: its identity number and DX7 behaviour are assumed from V15",
                   "most custom firmwares were built against V15 — read each installer's notes before leaving V16"],
      "summary": "6-op FM (Dexed core), 128 tones. V16 (Oct 2026) adds stereo effects, new presets and a 64-step sequencer with ratchets; the stock and FM1 Open lines are separate.",
      "checked": "2026-11-01",
      "sources": ["https://github.com/cicloid/awesome-fm-1", "https://www.matrixsynth.com/2026/10/m-vave-fm-1-official-v16-firmware.html",
                  "https://www.neoteo.com/en/m-vave-fm-1-firmware-why-stock-v16-and-open-v14-are-separate", "https://github.com/isod89/sloop-fm1/releases"],
      "buzz": "V16 covered by MatrixSynth (2026-10-23, via search); awesome-fm-1 calls it the current official image (Oct 2026). Custom-firmware installers now name V16 as the way back (SLOOP 2.8.4, Clipper, JIANT). m-vave.com and the release-notes file were unreachable from here."
    },
    {
      "id": "fm1open", "name": "FM1 Open", "author": "M-VAVE", "url": "https://github.com/m-vave/fm1_open",
      "license": "GPL-3.0 + FM1 SDK linking exception (engine: binary SDK)", "version": "V14", "date": "2026-10-19", "kind": "groovebox", "base": "M-VAVE's open line (separate from stock V16)",
      "status": "installable", "installer": "https://open.m-vave.com/fm1-workbench", "editor": "https://open.m-vave.com/fm1-workbench",
      "cli": "workbench (online or the offline FM1-Open-V14-Workbench.html from the release)",
      "usb": { "vidpid": "4c4a:c755", "products": ["FM-1"], "unverified": true },
      "identity": { "range": [8000000, 8000099], "pattern": "FM-1_80000XX (V14 = FM-1_8000014, app/version.h)" }, "info": null,
      "roles": null, "drums": "ch 1–7 → tracks 1–7, ch 10 → track 8 by default (TRACK ROLE sets each); DRUM 808 / SAMPLER tracks",
      "clock": "in DIN / USB / BLE (clock, start/stop, SPP); CLK OUT on 7/8 MIDI ROUTING", "dx7": true,
      "recovery": "the workbench returns to original V15 and migrates from compatible third-party firmware; the standard FM1 update protocol (M-UPGRADE) still works",
      "warnings": ["identity read from source (version.h FM1_UPDATE_PRODUCT), not yet seen on a unit",
                   "FoMni numbers itself FM-1_8XXYYZZ too (0.1 = FM-1_8000100); FoMni is 1209:0001, so the USB ID tells them apart",
                   "projects and samples don't carry across firmwares — export backups (voice groups A–D separately)"],
      "summary": "M-VAVE's own open firmware: 8 tracks, 8 sample slots, 16 demo projects, a 128-voice DX7 library, NORMAL / PLAY / OFF track roles with per-track MIDI channels, tap tempo, synced delay.",
      "checked": "2026-11-01",
      "sources": ["https://github.com/m-vave/fm1_open", "https://github.com/m-vave/fm1_open/releases", "https://raw.githubusercontent.com/m-vave/fm1_open/HEAD/app/version.h",
                  "https://synthanatomy.com/2026/10/m-vave-fm-1-open-the-green-light-for-custom-firmware-and-community-hacks.html"],
      "buzz": "274★ / 45 forks on 2026-11-01, two releases (V12 2026-10-14, V14 2026-10-19). Synth Anatomy: 'the green light for custom firmware'. awesome-fm-1: most new firmwares build on it or on fm1-base; FM-1 Pocket / FM-1 for Android run it in the browser / on phones.",
      "stars": { "count": 274, "forks": 45 }
    },
    {
      "id": "baudgirl", "name": "Baud Girl FM-1+VA", "author": "Madeline (Baud Girl)", "url": "https://baudgirl.com/work/FM-1+VA",
      "license": "closed (free)", "version": "FM-1_097", "date": "2026-10-09", "kind": "synth", "base": "stock app",
      "status": "installable", "installer": "https://baudgirl.com/work/FM-1+VA/install", "editor": null, "cli": null,
      "usb": { "vidpid": "4c4a:c755", "products": ["FM-1"] },
      "identity": { "range": [20, 99], "pattern": "FM-1_0XX" }, "info": null,
      "roles": null, "drums": null, "clock": "unknown", "dx7": true,
      "recovery": "M-UPGRADE with V15 or the installer's restore; a dongle if it will not boot",
      "warnings": ["a single-voice DX7 dump overwrites the selected stored preset without asking"],
      "cc": { "filter": 74, "responds": [74], "ignores": [1, 7, 71], "knobsSend": false },
      "keys": { "channel": 1, "velocity": 90 },
      "verified": { "date": "2026-10-11", "version": "FM-1_093", "how": "FM-1 CHECK-OUT on the Steam Deck (USB-C)",
        "facts": ["port name FM-1 MIDI 1 (in and out)", "answers the version query", "plays notes from USB on ch 1",
                  "keys send on ch 1 at a fixed velocity of 90, note-offs arrive", "CC 74 changes the sound; CC 71, 1 and 7 do not",
                  "the knobs send no MIDI CC",
                  "single-voice DX7 dumps load and play as sent (MM SINE / BRASS / BELL)",
                  "a DX7 parameter change (algorithm) is heard at once and redraws the screen",
                  "USB audio reaches the Deck: a digitally silent input carried the FM-1 at -14 dBFS (Chrome hid the input's name)",
                  "round trip MIDI out -> FM-1 -> USB audio in, Flatpak Chrome on the Deck: 142.9 ms (jitter 3.3 ms); an earlier run 149.9 ms"],
        "pending": ["clock follow"] },
      "summary": "Keeps the stock FM engine; adds VA (303 / supersaw), 8-bit, bitcrush, a 64-step sequencer, list menus, live knobs.",
      "checked": "2026-11-01",
      "sources": ["https://synthanatomy.com/2026/09/baud-girl-fm-1-va-custom-m-vave-fm-1-firmware.html", "https://sonicstate.com/news/2026/09/29/free-custom-firmware-for-mvave-fm-1-/",
                  "https://github.com/cicloid/awesome-fm-1"],
      "buzz": "The first third-party firmware: Sonicstate and Synth Anatomy (late Sept, FM-1_089), MatrixSynth video round-up; Virtual FM-1 and FM-1 Pulses sync with it. No newer FM-1 build found by search (Baud Girl's October news was SMK-37+VA); baudgirl.com was unreachable, so FM-1_097 is unconfirmed as latest."
    },
    {
      "id": "grooveos", "name": "Groove OS", "author": "Peter Gombos", "url": "https://www.groove-os.com/",
      "license": "commercial ($29)", "version": "1.3", "date": "2026-10-12", "kind": "groovebox", "base": "built on V15",
      "status": "installable", "installer": "https://www.groove-os.com/", "editor": null, "cli": null,
      "usb": { "vidpid": "4c4a:c755", "products": ["FM-1"], "unverified": true },
      "identity": null, "info": null,
      "roles": null, "drums": null, "clock": "unknown", "dx7": "unknown",
      "recovery": "its installer can put V15 back",
      "warnings": ["USB identity and MIDI map not verified — closed source; set the OUT channel by hand",
                   "1.3 is from a video post (2026-10-12); groove-os.com was unreachable, so newer builds may exist"],
      "summary": "Eight-track groovebox with FM / VA engines; each track on its own MIDI channel.",
      "checked": "2026-11-01",
      "sources": ["https://synthanatomy.com/2026/10/groove-os-turns-the-m-vave-fm-1-into-an-8-track-groovebox.html",
                  "https://www.matrixsynth.com/2026/10/m-vave-fm-1-groove-os-13-update-drum.html"],
      "buzz": "Synth Anatomy launch article (Oct 2026); MatrixSynth video posts 'Groove OS' (2026-10-06) and 'Groove OS 1.3 Update' (2026-10-12), found by search. Closed and paid, so no star counts."
    },
    {
      "id": "sloop_alg", "name": "SLOOP ALG", "author": "shaw-core", "url": "https://github.com/shaw-core/Sloop_ALG02",
      "license": "GPL-3.0-only", "version": "ALG05 TEST", "date": "2026-10-07", "kind": "groovebox", "base": "SLOOP 2.2",
      "status": "installable", "installer": "https://shaw-core.github.io/Sloop_ALG02/webapp/installer/", "editor": null, "cli": null,
      "usb": { "vidpid": "1209:0001", "products": ["Felucca"] },
      "identity": { "range": [980, 989], "pattern": "FM-1_985" }, "info": { "match": "^FELUCCA\\b.*\\bALG" },
      "roles": { "lead": 3, "bass": 1, "chords": 2, "drums": 10 }, "drums": "GM, nearest of 16 lanes", "clock": "in USB / TRS", "dx7": "editor",
      "recovery": "as SLOOP: hold OCT− at power-on (USB RESCUE), reinstall",
      "warnings": ["test build", "docs in Chinese", "close M-UPGRADE / DAWs first", "export sounds and projects first", "still on SLOOP 2.2 — none of SLOOP 2.3–2.8's fixes"],
      "summary": "Experimental SLOOP fork adding DX7, VA and Karplus-Strong engines (16 engines, 93 sounds, 37 kits).",
      "checked": "2026-11-01",
      "sources": ["https://github.com/shaw-core/Sloop_ALG02"],
      "buzz": "Quiet: 5★ / 0 forks, 7 commits, no releases on 2026-11-01 (3★ on 2026-10-14 per atlas-fm-1's GitHub metadata).",
      "stars": { "count": 5, "forks": 0 }
    },
    {
      "id": "sloop", "name": "SLOOP", "author": "3dSam (isod89)", "url": "https://github.com/isod89/sloop-fm1",
      "license": "GPL-3.0", "version": "2.8.4", "date": "2026-10-30", "kind": "groovebox", "base": "Felucca",
      "status": "installable", "installer": "https://isod89.github.io/sloop-fm1/", "editor": "https://isod89.github.io/sloop-fm1/webapp/editor/",
      "cli": "python3 tools/fm1_install.py sloop-2.x.fwsc",
      "usb": { "vidpid": "1209:0001", "products": ["Felucca"] },
      "identity": { "range": [920, 929], "pattern": "FM-1_92Y" }, "info": { "match": "^FELUCCA\\b.*SLOOP" },
      "roles": { "lead": 3, "bass": 1, "chords": 2, "drums": 10 }, "drums": "GM, nearest of 16 lanes (synths ch 1–3, drums ch 10; reassign in GLO > MIDI)", "clock": "in USB / TRS (GLO > SYSTEM > SYNC); CLOCK OUT on GLO > MIDI", "dx7": "editor",
      "recovery": "hold OCT− while switching on (SLOOP USB RESCUE, fixed in 2.8), then install again — the installer finds the loader by handshake; HOME > SYSTEM > 2ND CORE OFF on second-core crashes",
      "warnings": ["data cable, directly (no hub)", "back up first — newer projects do not open in older versions",
                   "2.8 dropped the in-browser return to stock: use M-UPGRADE with V16 (or Clipper's installer page)"],
      "summary": "Live four-track groovebox: three synths + a 16-sound drum track, FM6 / PHYS / NOISE among its engines, a NOTES piano roll (2.8), song mode, both CPU cores (2.7), USB audio at 44.1 / 48 kHz.",
      "checked": "2026-11-01",
      "sources": ["https://github.com/isod89/sloop-fm1", "https://github.com/isod89/sloop-fm1/releases",
                  "https://synthanatomy.com/2026/10/3dsam-sloop-custom-firmware-turns-m-vave-fm-1-into-a-4-track-groovebox.html",
                  "https://www.noizefield.com/news/sloop-custom-firmware-turns-m-vave-fm-1-into-4-track-groovebox",
                  "https://www.matrixsynth.com/2026/10/fm-1-sloop-is-epic.html", "https://dreyandersson.com/blog/m-vave-fm-1-custom-firmware/"],
      "buzz": "Most-starred FM-1 firmware: 703★ / 96 forks, 108 open issues, 16 PRs on 2026-11-01 (485★ on 2026-10-14). Ten releases in October (2.4 → 2.8.4). Synth Anatomy + Noizefield articles, YouTube 'FM-1 Sloop is EPIC' (DECIMA1) and 'Loop with SLOOP'; a ranking blog ties it with Felucca as best all-round (live play). The most-forked base after Felucca (ORBIT, zp12, sloopDX, Clipper, winampFM) with its own apps (sloop-fm1-go, SloopStudio).",
      "stars": { "count": 703, "forks": 96 }
    },
    {
      "id": "clipper", "name": "Clipper", "author": "3dSam (isod89)", "url": "https://github.com/isod89/clipper-fm1",
      "license": "GPL-3.0", "version": "1.3", "date": null, "kind": "synth", "base": "SLOOP (Felucca)",
      "status": "installable", "installer": "https://isod89.github.io/clipper-fm1/webapp/installer/", "editor": "https://isod89.github.io/clipper-fm1/webapp/editor/", "cli": null,
      "usb": { "vidpid": "1209:0001", "products": ["Clipper"] },
      "identity": { "range": [900, 999], "pattern": "FM-1_9XY (collides with Felucca / SLOOP)" }, "info": { "match": "^FELUCCA\\b.*CLIPPER" },
      "roles": null, "drums": null, "clock": "unknown", "dx7": "editor",
      "recovery": "its installer page returns to official V16 or V15 (or SLOOP via INSTALL-SLOOP.bat); HOME (held) > SYS > 2ND CORE OFF on second-core faults",
      "warnings": ["experimental — 'a lot to do' per its README", "back up with the editor first",
                   "MIDI in is OMNI by default (or one channel): every tool role lands on the one synth",
                   "a --release build would answer INFO 'FELUCCA 1.x BETA' and read as Felucca; source builds say 'FELUCCA CLIPPER 1.3'"],
      "summary": "Deep single-synth firmware from the SLOOP author: FM6 + FMX engines that load DX7 banks through the editor, SLOOP 2.8.3's fixes (1.2).",
      "checked": "2026-11-01",
      "sources": ["https://github.com/isod89/clipper-fm1", "https://raw.githubusercontent.com/isod89/clipper-fm1/HEAD/firmware/src/usb.c",
                  "https://raw.githubusercontent.com/isod89/clipper-fm1/HEAD/firmware/src/editor.c", "https://github.com/isod89/sloop-fm1/releases"],
      "buzz": "68★ / 3 forks, 68 commits, 22 open issues on 2026-11-01; no GitHub releases (version from its README). SLOOP's own release notes point to Clipper's installer page for the way back to stock.",
      "stars": { "count": 68, "forks": 3 }
    },
    {
      "id": "ghoulbox", "name": "GHOULBOX", "author": "Jason Persinger", "url": "https://github.com/jasonpersinger/ghoulbox-fm1-dungeon-synth",
      "license": "GPL-3.0", "version": "2.3.2", "date": null, "kind": "synth", "base": "Felucca 1.4.1",
      "status": "installable", "installer": "https://ghoulbox.messy.quest/webapp/installer/", "editor": "https://ghoulbox.messy.quest/webapp/editor/", "cli": null,
      "usb": { "vidpid": "1209:0001", "products": ["Felucca"] },
      "identity": { "range": [900, 919], "pattern": "FM-1_9XY (collides with Felucca)" }, "info": { "match": "^FELUCCA\\b.*\\bGB\\d" },
      "roles": null, "drums": null, "clock": "unknown", "dx7": "unknown",
      "recovery": "hold OCT− at power-on (USB rescue; two failed starts open it too), reinstall; FM-1 Transporter as the last resort",
      "warnings": ["hobby project, tested on one FM-1", "the installer makes no backup — save one from the editor's Settings first",
                   "its INFO reads 'FELUCCA v1.4.1 GB…': listed before Felucca so the fork wins"],
      "summary": "Dungeon-synth Felucca fork: cathedral reverb, tape, a hurdy-gurdy engine, 59 curated sounds, an old-RPG screen.",
      "checked": "2026-11-01",
      "sources": ["https://github.com/jasonpersinger/ghoulbox-fm1-dungeon-synth", "https://raw.githubusercontent.com/jasonpersinger/ghoulbox-fm1-dungeon-synth/HEAD/firmware/src/editor.c",
                  "https://www.matrixsynth.com/2026/10/m-vave-fm1-ghoulbox-firmware.html"],
      "buzz": "78★ / 3 forks, 184 commits on 2026-11-01 (43★ on 2026-10-14); MatrixSynth post (2026-10-12); forks PALEOTONE and ESTAMPIE, and a Ghoulbox VST3 / felucca-vst build.",
      "stars": { "count": 78, "forks": 3 }
    },
    {
      "id": "felucca", "name": "Felucca", "author": "Leo Kuroshita (Hügelton Instruments)", "url": "https://github.com/hugelton/Felucca",
      "license": "GPL-3.0-only", "version": "1.8.0", "date": "2026-10-31", "kind": "synth", "base": "from scratch",
      "status": "installable", "installer": "https://hugelton.github.io/Felucca/", "editor": "https://hugelton.github.io/Felucca/webapp/editor/",
      "cli": "python3 tools/fm1_install.py PKG.fwsc",
      "usb": { "vidpid": "1209:0001", "products": ["Felucca"] },
      "identity": { "range": [900, 919], "pattern": "FM-1_9XY (1.8.0 = FM-1_918)" }, "info": { "match": "^FELUCCA\\s+v?\\d" },
      "roles": { "lead": 3, "bass": 1, "chords": 2, "drums": 4 }, "drums": "GM 35–81 on a DRUM track (track 4 by default)", "clock": "in INT / USB / TRS; NO CLOCK detection (1.8)", "dx7": false,
      "recovery": "re-run the installer (finishes an interrupted write; 1.6.1+ refuses packages made for other devices before erasing); 1.7's installer returns to official V15 (may erase some saved data); OCT− + OCT+ for 5 s = UBOOT; a black screen / WL80UBOOT needs a FM-1 Transporter",
      "warnings": ["connect directly to the computer", "complete backup before returning to V15", "projects with conditional steps (1.6+) don't open on 1.5.x",
                   "the in-browser emulator in these tools is pinned to 1.5.1"],
      "summary": "Four tracks, each its own engine (13: ANALOG, FM6, PHASE, LOFI, SAMPLE, VOICE, TRIO, WHEEL, GRAIN, PHYS, NOISE, SLICE, DRUM); per-track MIDI channels and conditional steps (1.6), aftertouch and undo for hand-edited steps (1.8).",
      "emulator": {"vendor": "vendor/fm1emu/felucca/", "processor": "felucca", "rate": 44100, "hosted": "https://hugelton.github.io/Felucca/webapp/try/", "commit": "92d0634be3def39b7ae2a099a326d2cf8270453f"},
      "checked": "2026-11-01",
      "sources": ["https://github.com/hugelton/Felucca", "https://github.com/hugelton/Felucca/releases", "https://raw.githubusercontent.com/hugelton/Felucca/HEAD/tools/build.py",
                  "https://synthanatomy.com/2026/10/hugelton-instruments-felucca-custom-m-vave-fm-1-firmware-turns-it-into-a-multi-engine-synth.html"],
      "buzz": "617★ / 148 forks, 5 open issues on 2026-11-01 (479★ on 2026-10-14). The base nearly every open firmware forks (awesome-fm-1: 'most of the open source ones descend from Felucca'); its engines and BSP are now separate repos. Ten releases in October (1.1.5 → 1.8.0); Synth Anatomy 1.0 article; YouTube 'Felucca 0.9 full guide', 'first look', 'jam session'. A ranking blog ties it with SLOOP (sound design).",
      "stars": { "count": 617, "forks": 148 }
    },
    {
      "id": "x0x", "name": "X0X", "author": "Charles Vestal", "url": "https://github.com/charlesvestal/fm1-x0x",
      "license": "GPL-3.0-only", "version": "1.1.0", "date": "2026-10-15", "kind": "groovebox", "base": "Felucca",
      "status": "installable", "installer": "https://charlesvestal.github.io/fm1-x0x/install/", "editor": null,
      "cli": "python3 tools/fm1_install.py x0x-X.fwsc",
      "usb": { "vidpid": "1209:0001", "products": ["X0X FM-1"] },
      "identity": { "range": [9000000, 9999999], "pattern": "FM-1_9XXYYZZ" }, "info": { "match": "^X0X\\b" },
      "roles": { "lead": 3, "bass": 2, "chords": null, "drums": 10 }, "drums": "GM: 909 on ch10, 808 on ch11", "clock": "follows clock in; clock out optional", "dx7": false,
      "recovery": "SAFE MODE after two boot crashes (installer still works); OCT− + OCT+ 5 s = update mode; a project backup / restore page (1.0.9); interrupted saves load the previous save",
      "warnings": ["beta (per its README)", "GLO > 2ND CORE changes apply at the next power-on"],
      "summary": "ReBirth-style: 909 (ch10), 808 (ch11), two 303s (ch2, ch3), a break slicer (ch4); speaks its screen to a screen reader (1.1.0).",
      "emulator": {"vendor": "vendor/fm1emu/x0x/", "processor": "x0x", "rate": 44100, "hosted": "https://charlesvestal.github.io/fm1-x0x/emu/", "commit": "225e01d0ec330abbde0409e51d14062d523d6598"},
      "checked": "2026-11-01",
      "sources": ["https://github.com/charlesvestal/fm1-x0x", "https://github.com/charlesvestal/fm1-x0x/releases",
                  "https://synthanatomy.com/2026/10/charles-vestal-x0x-custom-firmware-turns-the-m-vave-fm-1-into-a-rebirth-like-groovebox.html"],
      "buzz": "211★ / 27 forks, 239 commits on 2026-11-01 (158★ on 2026-10-14); Synth Anatomy article; forks X0X-RMX, Acultur8 X0X, fm1-rocket-os, DREADNOUGHT, Carnac OS. A ranking blog names it the pick for acid / techno.",
      "stars": { "count": 211, "forks": 27 }
    },
    {
      "id": "fomni", "name": "FoMni", "author": "Charles Vestal", "url": "https://github.com/charlesvestal/fm1-fomni",
      "license": "GPL-3.0", "version": "unversioned (installer build)", "date": null, "kind": "synth", "base": "Felucca platform via X0X; Chordian rhythms (CC0)",
      "status": "installable", "installer": "https://charlesvestal.github.io/fm1-fomni/install/", "editor": null, "cli": null,
      "usb": { "vidpid": "1209:0001", "products": ["FoMni FM-1"] },
      "identity": { "range": [8000100, 8999999], "pattern": "FM-1_8XXYYZZ (0.1 = FM-1_8000100)" }, "info": null,
      "roles": { "lead": 1, "bass": null, "chords": 2, "drums": null }, "drums": "sends strings ch1, chord ch2, bass ch3, drums ch10 OUT; MIDI in: ch1 plucks the nearest string, ch2 sets the chord",
      "clock": "follows MIDI clock + start / stop; sends clock", "dx7": false,
      "recovery": "its installer can restore M-VAVE's firmware; a unit that keeps crashing starts in a safe mode",
      "warnings": ["no Felucca editor INFO — the port name 'FoMni FM-1' identifies it", "no tagged releases"],
      "summary": "Omnichord-style chord harp: the 16 white keys are a strum plate, the 11 black keys pick chords; rhythms and drums from Chordian.",
      "checked": "2026-11-01",
      "sources": ["https://github.com/charlesvestal/fm1-fomni", "https://raw.githubusercontent.com/charlesvestal/fm1-fomni/HEAD/firmware/src/usb.c",
                  "https://raw.githubusercontent.com/charlesvestal/fm1-fomni/HEAD/tools/build.py",
                  "https://synthanatomy.com/2026/10/charles-vestal-fomni-1-an-omnichord-custom-firmware-for-the-m-vave-fm-1.html", "https://www.synthtopia.com/?p=155230"],
      "buzz": "73★ / 10 forks on 2026-11-01 (58★ on 2026-10-14); Synth Anatomy and Synthtopia ('pocket Omnichord') articles; forks FuMi-1 and ZEN-1; works with the FM-1 Screen Reader.",
      "stars": { "count": 73, "forks": 10 }
    },
    {
      "id": "jangada", "name": "Jangada", "author": "zednaked", "url": "https://github.com/zednaked/jangada",
      "license": "GPL-3.0", "version": "1.0.1", "date": "2026-10-16", "kind": "synth", "base": "Felucca",
      "status": "installable", "installer": "https://zednaked.github.io/jangada/", "editor": null, "cli": "./instalar-linux.sh (downloads the latest release, checks its SHA-256)",
      "usb": { "vidpid": "1209:0001", "products": ["Jangada"] },
      "identity": { "range": [900, 919], "pattern": "FM-1_9XY (collides with Felucca: 1.0 = FM-1_910)" }, "info": { "match": "^JANGADA\\b" },
      "roles": { "lead": 3, "bass": 1, "chords": 2, "drums": 10 }, "drums": "own kits + GM (drum channel 10; ROUT blocks CH5-8 / 9-12 / 13-16)", "clock": "in INT / USB / TRS; sync out over USB", "dx7": true,
      "recovery": "hold OCT− at power-on (JANGADA USB RESCUE); Felucca's installer will not find it",
      "warnings": ["use at your own risk (out of pre-release since 0.9.9)", "data cable straight to the computer", "back up first", "MENU 2ND CORE = BOOST raises chip voltage (own risk)"],
      "summary": "Superwave analog, a modulation matrix, drum synthesis, 49 factory beats (1.0); DX7 voices and banks edit its FM6 live.",
      "checked": "2026-11-01",
      "sources": ["https://github.com/zednaked/jangada", "https://github.com/zednaked/jangada/releases", "https://raw.githubusercontent.com/zednaked/jangada/HEAD/tools/build.py"],
      "buzz": "36★ / 3 forks, 208 commits on 2026-11-01 (26★ on 2026-10-14); 1.0.1 added editor protocol v8 for the FM-1 strip in Nirbija 0.6.0; UnholyUnion builds on it.",
      "stars": { "count": 36, "forks": 3 }
    },
    {
      "id": "jiant", "name": "JIANT FM", "author": "Juan Jiant (juanjiant-bit)", "url": "https://github.com/juanjiant-bit/JIANT",
      "license": "GPL-3.0-only", "version": "V10 (beta V10.20)", "date": "2026-10-30", "kind": "groovebox", "base": "Felucca 1.1.5.1 (+ SLOOP's song system)",
      "status": "installable", "installer": "https://juanjiant-bit.github.io/JIANT/webapp/installer/", "editor": "https://juanjiant-bit.github.io/JIANT/webapp/editor/", "cli": null,
      "usb": { "vidpid": "1209:0001", "products": ["JIANT"] },
      "identity": { "range": [900, 999], "pattern": "FM-1_9XY (collides with Felucca)" }, "info": { "match": "^JIANT\\b" },
      "roles": { "lead": 4, "bass": 5, "chords": 6, "drums": 1 }, "drums": "DRUM-X kit on track 1 (ch 1); ch 1–6 play tracks 1–6 (ROUT CH1-6), 7–16 stay free",
      "clock": "unknown", "dx7": "editor",
      "recovery": "'Return to official' (V16 or V15, checked byte for byte, after a full JIANT backup); hold REC at power-on for one-core mode; it falls back to one core by itself",
      "warnings": ["coming from Felucca / Skiff / another fork: 'Return to official' first", "the full backup leaves out the DX7 bank — keep your .syx files",
                   "roles are main's power-on sounds (TRK_DEF: DRUM-X, SINGER, CMOS BIRD, BYTEBEAT, FAT BASS, TINE EP) — a project can differ",
                   "Bluetooth is beta", "a README line says it shows as 'FM-1'; its usb.c names the port 'JIANT' (older builds 'JIANT FM')"],
      "summary": "Live / whole-song groovebox: six tracks (DRUM-X, VOICE, ANIMAL, LOFI, ANALOG, FM6 at power-on), song mode, 6-op FM from Dexed with 32-voice cartridges into B1–B32.",
      "checked": "2026-11-01",
      "sources": ["https://github.com/juanjiant-bit/JIANT", "https://raw.githubusercontent.com/juanjiant-bit/JIANT/HEAD/firmware/src/usb.c",
                  "https://raw.githubusercontent.com/juanjiant-bit/JIANT/HEAD/firmware/src/editor.c", "https://raw.githubusercontent.com/juanjiant-bit/JIANT/HEAD/firmware/src/engines.c",
                  "https://www.matrixsynth.com/2026/10/jiant-fm-fm1-firmware-new-floatbeat.html"],
      "buzz": "193★ / 15 forks, 849 commits, 11 open PRs on 2026-11-01 (112★ on 2026-10-14 — fourth most-starred FM-1 firmware); MatrixSynth post on v0.6.29 (2026-10-11); forks ACID FM, and the Falua plugin runs its engines on a computer.",
      "stars": { "count": 193, "forks": 15 }
    },
    {
      "id": "melodee", "name": "Melodee", "author": "Kerem Kilic (Ellic Studio)", "url": "https://github.com/keremimo/melodee",
      "license": "GPL-3.0-only", "version": "1.5.1", "date": "2026-10-26", "prerelease": "1.6.0-rc.7 · 2026-10-29", "kind": "synth", "base": "Felucca",
      "status": "installable", "installer": "https://keremimo.github.io/melodee/", "editor": "https://keremimo.github.io/melodee/webapp/editor/", "cli": "tools/fm1_install.py",
      "usb": { "vidpid": "1209:0001", "products": ["Melodee"] },
      "identity": { "range": [900, 99999], "pattern": "FM-1_9XY[Z] (0.11.1 = FM-1_90111)" }, "info": { "match": "^MELODEE\\b" },
      "roles": { "lead": 3, "bass": 1, "chords": 2, "drums": 10 }, "drums": "808 / 909 / CR-78 / FM kits (GM assumed); DRUM channel 10", "clock": "INT / USB / TRS", "dx7": true,
      "recovery": "OCT− + OCT+ 5 s = UBOOT; each release ships native UBOOT recovery tools (Windows, macOS, Linux); Transporter if it will not start",
      "warnings": ["direct cable", "the installer saves a complete backup first", "the port now reads 'Melodee FM-1'", "the 1.6 release candidates change the project format (FBKM…FBKQ)"],
      "summary": "Eight tracks — four synth parts plus four MIDI tracks on their own channels (1.5) — ten engines, USB-host MIDI, punch FX; DX7 banks load straight to presets, plus CZ and Prophet SysEx. 1.6 RCs add Bluetooth MIDI and 64-section songs.",
      "checked": "2026-11-01",
      "sources": ["https://github.com/keremimo/melodee", "https://github.com/keremimo/melodee/releases", "https://raw.githubusercontent.com/keremimo/melodee/HEAD/tools/build.py",
                  "https://raw.githubusercontent.com/keremimo/melodee/HEAD/firmware/src/usb.c"],
      "buzz": "164★ / 33 forks, 634 commits, 18 open issues on 2026-11-01 (74★ on 2026-10-14 — the fastest-growing of the big forks); a release candidate almost daily at the end of October; Tessera and Saadet fork it; FM1VST and FM-1 for Android run it.",
      "stars": { "count": 164, "forks": 33 }
    },
    {
      "id": "lunar", "name": "Lunar Modulator", "author": "ip2k", "url": "https://github.com/ip2k/lunar-modulator",
      "license": "MIT", "version": "unreleased", "date": "2026-10-26", "kind": "research", "base": "from scratch (Mutable engines)",
      "status": "not-installable", "installer": null, "editor": null, "cli": null, "usb": null, "identity": null, "info": null,
      "roles": null, "drums": null, "clock": null, "dx7": false, "recovery": null, "warnings": ["browser simulation only — 'has not run on an FM-1 yet'"],
      "summary": "Research firmware on Plaits / Braids / Rings; runs as a browser sim. 2026-10-26: the author's unit was recovered with a Pico 2 W after an interrupted install.",
      "checked": "2026-11-01",
      "sources": ["https://github.com/ip2k/lunar-modulator"],
      "buzz": "63★ / 5 forks, 2,009 commits on 2026-11-01 (59★ on 2026-10-14); its USB_KEY dongle write-up is a go-to recovery reference.",
      "stars": { "count": 63, "forks": 5 }
    },
    {
      "id": "polyseq", "name": "fm1-polyseq", "author": "NOVALENTI", "url": "https://github.com/NOVALENTI/fm1-polyseq",
      "license": "unknown", "version": null, "date": "2026-09-04", "kind": "sequencer", "base": "from scratch (C99)",
      "status": "not-installable", "installer": null, "editor": null, "cli": null, "usb": null, "identity": null, "info": null,
      "roles": null, "drums": null, "clock": null, "dx7": false, "recovery": null, "warnings": ["its README says do not flash it onto an FM-1"],
      "summary": "Polyphonic 16-step sequencer in strict C99 (host simulation only).",
      "checked": "2026-11-01",
      "sources": ["https://github.com/NOVALENTI/fm1-polyseq"],
      "buzz": "Quiet: 3★ / 0 forks, 40 commits, no releases or licence file on 2026-11-01.",
      "stars": { "count": 3, "forks": 0 }
    },
    {
      "id": "fm1nes", "name": "fm1-nes", "author": "Keitark", "url": "https://github.com/Keitark/fm1-nes",
      "license": "Apache-2.0 (+GPLv3/MIT parts)", "version": "source only", "date": "2026-10-09", "kind": "game-port", "base": "JieLi SDK",
      "status": "source-only", "installer": null, "editor": null, "cli": "JieLi UBOOT writer (first install needs a forced-download adapter)",
      "usb": { "vidpid": "3654:5155", "products": ["FM1 USB Diagnostic", "FM1 NES USB Audio"] }, "identity": null, "info": null,
      "roles": null, "drums": null, "clock": null, "dx7": false, "recovery": "serial UBOOT command", "warnings": ["no MIDI", "experimental"],
      "summary": "An NES emulator on the FM-1.",
      "checked": "2026-11-01",
      "sources": ["https://github.com/Keitark/fm1-nes"],
      "buzz": "19★ / 0 forks, 21 commits, no releases on 2026-11-01; its GETTING_STARTED / APP_UPDATES docs are what awesome-fm-1 points developers to.",
      "stars": { "count": 19, "forks": 0 }
    },
    {
      "id": "fm1doom", "name": "fm1-doom", "author": "Keitark", "url": "https://github.com/Keitark/fm1-doom",
      "license": "GPL-2.0", "version": "unflashed", "date": "2026-10-09", "kind": "game-port", "base": "Doomgeneric",
      "status": "source-only", "installer": null, "editor": null, "cli": null, "usb": null, "identity": null, "info": null,
      "roles": null, "drums": null, "clock": null, "dx7": false, "recovery": "as fm1-nes", "warnings": ["no MIDI", "not hardware-verified"],
      "summary": "Doom on the FM-1, in progress (the 2026-10-09 candidate has not been flashed).",
      "checked": "2026-11-01",
      "sources": ["https://github.com/Keitark/fm1-doom"],
      "buzz": "5★ / 0 forks on 2026-11-01. Other Doom ports have overtaken it: zvenson's FM-1 Doom (playable) and ChanceTheMaker's Doom FM-1 / SMK (nine maps).",
      "stars": { "count": 5, "forks": 0 }
    }
  ],
  "others": [
    "Mutable Dreams", "TRIBE", "LOOM-8", "MONK-1", "Polly", "AMB-1", "CTL-1", "ChoralRoot", "Hortator", "sloopDX", "zp12", "ORBIT", "FiMba-1",
    "FuMi-1", "fm1-chord", "WaveLoop (Felucca from a MiniLab 3)", "Rainbow", "PurpleMonkey", "FM1 Quest", "Optimist", "NoteSorcery", "FM1 Move", "Skiff",
    "Caravel", "Felucca MPE", "Felucca [Salt]", "Felucca 8 Patterns", "X0X-RMX", "Acultur8 X0X", "fm1-dock", "FM-1 SID", "OberVave", "FM-106", "Golana",
    "Tessera", "Saadet", "BEETLE", "ETCH", "DUELL", "SIDOU", "OPLBOX", "GammaWave", "Mini-Tone", "MYCELIUM", "UTA BOX (closed)", "April OS (closed)",
    "Dinghy (starter)", "fm1-base (starter)", "FM-1 Doom (zvenson)", "Doom FM-1 / SMK", "GameDude", "SLOOP DX7 Banks", "SLOOP Floyd FM", "FM-1 B-Boy Edition (repo gone)"
  ],
  "others_note": "github.com/cicloid/awesome-fm-1 lists 224 open-source FM-1 firmwares on 2026-11-01 (plus closed ones and game ports); these are the ones with releases, articles or forks behind them, not yet catalogued. fm1-editor.com/firmware, thefirmwarehub.com and stanleygurvich's FM-1 Firmware Database track the field live. Most Felucca forks enumerate as 1209:0001 — the tools treat an unknown one as 'Felucca family' and show its INFO string."
}/*FM1-JSON-END*/;

const FM1_FIRMWARES = FM1_REGISTRY.firmwares;
function fm1Firmware(id) { return FM1_FIRMWARES.find(f => f.id === id) || null; }
