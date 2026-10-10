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
 *
 * Field guide:
 *   usb.vidpid / usb.products   what the running firmware enumerates as.
 *                    1209:0001 is a shared hobby ID: match the product.
 *   identity.range   decimal after "FM-1_" in the vendor identity reply
 *                    (F0 00 32 45 …). Ranges overlap between forks, so
 *                    INFO decides inside the Felucca family.
 *   info.match       regex on the editor INFO string (F0 7D 46 4C 01 F7),
 *                    tested in registry order — specific forks first.
 *   roles            OUT channel per tool role. Felucca-family default
 *                    sounds (TRK_DEF): track 1 bass, 2 pad/keys, 3 lead.
 *   dx7              true: F0 43 voice dumps work · "editor": only via
 *                    the firmware's web editor · false: no FM-DX7 engine.
 */
"use strict";

const FM1_REGISTRY = /*FM1-JSON-BEGIN*/{
  "catalogued": "2026-10-10",
  "loaders": {
    "usb": ["4d4a:4155", "1209:0002", "4c4a:8057"],
    "names": ["ota-FM-1", "Update", "WL80UBOOT"],
    "note": "updater / boot modes — never treat as a playable port; re-run the SAME firmware's installer to finish"
  },
  "firmwares": [
    {
      "id": "stock", "name": "Stock M-VAVE", "author": "M-VAVE", "url": "https://www.m-vave.com/download",
      "license": "proprietary", "version": "V15", "date": "2026-07-30", "kind": "synth", "base": "—",
      "status": "installable", "installer": null, "editor": null,
      "cli": "M-UPGRADE (Win/Mac) — the macOS one downgrades V15 to V14",
      "usb": { "vidpid": "4c4a:c755", "products": ["FM-1"] },
      "identity": { "range": [9, 19], "pattern": "FM-1_015" }, "info": null,
      "roles": null, "drums": null, "clock": "unknown", "dx7": true,
      "recovery": "single flash bank, no rescue key; a unit that will not boot needs a mask-ROM dongle (FM-1 Transporter)",
      "warnings": [], "summary": "6-op FM (Dexed core), 128 tones, 16-step sequencer."
    },
    {
      "id": "baudgirl", "name": "FM-1+VA", "author": "Madeline (Baud Girl)", "url": "https://baudgirl.com/work/FM-1+VA",
      "license": "closed (free)", "version": "FM-1_097", "date": "2026-10-09", "kind": "synth", "base": "stock app",
      "status": "installable", "installer": "https://baudgirl.com/work/FM-1+VA/install", "editor": null, "cli": null,
      "usb": { "vidpid": "4c4a:c755", "products": ["FM-1"] },
      "identity": { "range": [20, 99], "pattern": "FM-1_0XX" }, "info": null,
      "roles": null, "drums": null, "clock": "unknown", "dx7": true,
      "recovery": "M-UPGRADE with V15 or the installer's restore; a dongle if it will not boot",
      "warnings": ["a single-voice DX7 dump overwrites the selected stored preset without asking"],
      "summary": "Keeps the stock FM engine; adds VA (303 / supersaw), 8-bit, bitcrush, a 64-step sequencer, list menus, live knobs."
    },
    {
      "id": "grooveos", "name": "Groove OS", "author": "Peter Gombos", "url": "https://www.groove-os.com/",
      "license": "commercial ($29)", "version": "1.2.1", "date": "2026-10-10", "kind": "groovebox", "base": "built on V15",
      "status": "installable", "installer": "https://www.groove-os.com/", "editor": null, "cli": null,
      "usb": { "vidpid": "4c4a:c755", "products": ["FM-1"], "unverified": true },
      "identity": null, "info": null,
      "roles": null, "drums": null, "clock": "unknown", "dx7": "unknown",
      "recovery": "its installer can put V15 back",
      "warnings": ["USB identity and MIDI map not verified — closed source; set the OUT channel by hand"],
      "summary": "Eight-track groovebox with FM / VA engines; each track on its own MIDI channel."
    },
    {
      "id": "sloop_alg", "name": "SLOOP ALG", "author": "shaw-core", "url": "https://github.com/shaw-core/Sloop_ALG02",
      "license": "GPL-3.0-only", "version": "ALG05 TEST", "date": "2026-10-07", "kind": "groovebox", "base": "SLOOP 2.2",
      "status": "installable", "installer": "https://shaw-core.github.io/Sloop_ALG02/webapp/installer/", "editor": null, "cli": null,
      "usb": { "vidpid": "1209:0001", "products": ["Felucca"] },
      "identity": { "range": [980, 989], "pattern": "FM-1_985" }, "info": { "match": "^FELUCCA\\b.*\\bALG" },
      "roles": { "lead": 3, "bass": 1, "chords": 2, "drums": 10 }, "drums": "GM, nearest of 16 lanes", "clock": "in USB / TRS", "dx7": "editor",
      "recovery": "as SLOOP: hold OCT− at power-on (USB RESCUE), reinstall",
      "warnings": ["test build", "docs in Chinese", "close M-UPGRADE / DAWs first", "export sounds and projects first"],
      "summary": "Experimental SLOOP fork adding DX7, VA and Karplus-Strong engines."
    },
    {
      "id": "sloop", "name": "SLOOP", "author": "3dSam (isod89)", "url": "https://github.com/isod89/sloop-fm1",
      "license": "GPL-3.0", "version": "2.5", "date": "2026-10-08", "kind": "groovebox", "base": "Felucca",
      "status": "installable", "installer": "https://isod89.github.io/sloop-fm1/", "editor": "https://isod89.github.io/sloop-fm1/webapp/editor/",
      "cli": "python3 tools/fm1_install.py sloop-2.x.fwsc",
      "usb": { "vidpid": "1209:0001", "products": ["Felucca"] },
      "identity": { "range": [920, 929], "pattern": "FM-1_92Y" }, "info": { "match": "^FELUCCA\\b.*SLOOP" },
      "roles": { "lead": 3, "bass": 1, "chords": 2, "drums": 10 }, "drums": "GM, nearest of 16 lanes", "clock": "in USB / TRS (GLO > SYSTEM > SYNC)", "dx7": "editor",
      "recovery": "hold OCT− while switching on (SLOOP USB RESCUE), then install again; an interrupted install finishes on retry",
      "warnings": ["data cable, directly (no hub)", "back up first — newer projects do not open in older versions"],
      "summary": "Live four-track groovebox: three synths + a 16-sound drum track, 12 engines, 37 kits, song mode, USB audio."
    },
    {
      "id": "felucca", "name": "Felucca", "author": "Leo Kuroshita (Hügelton Instruments)", "url": "https://github.com/hugelton/Felucca",
      "license": "GPL-3.0-only", "version": "1.5.1", "date": "2026-10-10", "kind": "synth", "base": "from scratch",
      "status": "installable", "installer": "https://hugelton.github.io/Felucca/", "editor": "https://hugelton.github.io/Felucca/webapp/editor/",
      "cli": "python3 tools/fm1_install.py PKG.fwsc",
      "usb": { "vidpid": "1209:0001", "products": ["Felucca"] },
      "identity": { "range": [900, 919], "pattern": "FM-1_9XY" }, "info": { "match": "^FELUCCA\\s+v?\\d" },
      "roles": { "lead": 3, "bass": 1, "chords": 2, "drums": 4 }, "drums": "GM 35–81 on a DRUM track (track 4 by default)", "clock": "in INT / USB / TRS", "dx7": false,
      "recovery": "re-run the installer (finishes an interrupted write); OCT− + OCT+ for 5 s = UBOOT; a black screen / WL80UBOOT needs a FM-1 Transporter",
      "warnings": ["connect directly to the computer", "complete backup before returning to V15"],
      "summary": "Four tracks, each its own engine (13: ANALOG, FM6, PHASE, LOFI, SAMPLE, VOICE, TRIO, WHEEL, GRAIN, PHYS, NOISE, SLICE, DRUM)."
    },
    {
      "id": "x0x", "name": "X0X", "author": "Charles Vestal", "url": "https://github.com/charlesvestal/fm1-x0x",
      "license": "GPL-3.0-only", "version": "1.0.5", "date": "2026-10-10", "kind": "groovebox", "base": "Felucca",
      "status": "installable", "installer": "https://charlesvestal.github.io/fm1-x0x/install/", "editor": null,
      "cli": "python3 tools/fm1_install.py x0x-X.fwsc",
      "usb": { "vidpid": "1209:0001", "products": ["X0X FM-1"] },
      "identity": { "range": [9000000, 9999999], "pattern": "FM-1_9XXYYZZ" }, "info": { "match": "^X0X\\b" },
      "roles": { "lead": 3, "bass": 2, "chords": null, "drums": 10 }, "drums": "GM: 909 on ch10, 808 on ch11", "clock": "follows clock in; clock out optional", "dx7": false,
      "recovery": "SAFE MODE after two boot crashes (installer still works); OCT− + OCT+ 5 s = update mode",
      "warnings": ["beta"],
      "summary": "ReBirth-style: 909 (ch10), 808 (ch11), two 303s (ch2, ch3), a break slicer (ch4)."
    },
    {
      "id": "jangada", "name": "Jangada", "author": "zednaked", "url": "https://github.com/zednaked/jangada",
      "license": "GPL-3.0", "version": "0.9.4 alpha", "date": "2026-10-10", "kind": "synth", "base": "Felucca",
      "status": "installable", "installer": "https://zednaked.github.io/jangada/", "editor": null, "cli": "./instalar-linux.sh",
      "usb": { "vidpid": "1209:0001", "products": ["Jangada"] },
      "identity": { "range": [900, 909], "pattern": "FM-1_9XY (collides with Felucca 0.9)" }, "info": { "match": "^JANGADA\\b" },
      "roles": { "lead": 3, "bass": 1, "chords": 2, "drums": 10 }, "drums": "own kits + GM", "clock": "in INT / USB / TRS; sync out over USB", "dx7": true,
      "recovery": "hold OCT− at power-on (JANGADA USB RESCUE); Felucca's installer will not find it",
      "warnings": ["alpha", "data cable straight to the computer", "back up first"],
      "summary": "Superwave analog, a modulation matrix, drum synthesis; DX7 voices and banks edit its FM6 live."
    },
    {
      "id": "melodee", "name": "Melodee", "author": "Kerem Kilic (Ellic Studio)", "url": "https://github.com/keremimo/melodee",
      "license": "GPL-3.0-only", "version": "1.1.0", "date": "2026-10-10", "kind": "synth", "base": "Felucca",
      "status": "installable", "installer": "https://keremimo.github.io/melodee/", "editor": null, "cli": "tools/fm1_install.py",
      "usb": { "vidpid": "1209:0001", "products": ["Melodee"] },
      "identity": { "range": [91000, 99999], "pattern": "FM-1_9X[Y|YYZ]" }, "info": { "match": "^MELODEE\\b" },
      "roles": { "lead": 3, "bass": 1, "chords": 2, "drums": 10 }, "drums": "808 / 909 kits (GM assumed)", "clock": "INT / USB / TRS", "dx7": true,
      "recovery": "OCT− + OCT+ 5 s = UBOOT; Transporter if it will not start; try the 'Single core' build if Standard crashes",
      "warnings": ["direct cable", "the installer saves a complete backup first"],
      "summary": "Ten engines, eight patterns per track, STUDIO workspaces; DX7 banks load straight to presets, plus CZ and Prophet SysEx."
    },
    {
      "id": "lunar", "name": "Lunar Modulator", "author": "ip2k", "url": "https://github.com/ip2k/lunar-modulator",
      "license": "MIT", "version": "unreleased", "date": "2026-10-10", "kind": "research", "base": "from scratch (Mutable engines)",
      "status": "not-installable", "installer": null, "editor": null, "cli": null, "usb": null, "identity": null, "info": null,
      "roles": null, "drums": null, "clock": null, "dx7": false, "recovery": null, "warnings": ["browser simulation only"],
      "summary": "Research firmware on Plaits / Braids / Rings; runs as a browser sim."
    },
    {
      "id": "polyseq", "name": "fm1-polyseq", "author": "NOVALENTI", "url": "https://github.com/NOVALENTI/fm1-polyseq",
      "license": "unknown", "version": null, "date": "2026-09-04", "kind": "sequencer", "base": "from scratch (C99)",
      "status": "not-installable", "installer": null, "editor": null, "cli": null, "usb": null, "identity": null, "info": null,
      "roles": null, "drums": null, "clock": null, "dx7": false, "recovery": null, "warnings": ["its source says do not flash any build yet"],
      "summary": "Polyphonic 16-step sequencer in strict C99."
    },
    {
      "id": "fm1nes", "name": "fm1-nes", "author": "Keitark", "url": "https://github.com/Keitark/fm1-nes",
      "license": "Apache-2.0 (+GPLv3/MIT parts)", "version": "source only", "date": "2026-10-09", "kind": "game-port", "base": "JieLi SDK",
      "status": "source-only", "installer": null, "editor": null, "cli": "JieLi UBOOT writer (first install needs a forced-download adapter)",
      "usb": { "vidpid": "3654:5155", "products": ["FM1 USB Diagnostic", "FM1 NES USB Audio"] }, "identity": null, "info": null,
      "roles": null, "drums": null, "clock": null, "dx7": false, "recovery": "serial UBOOT command", "warnings": ["no MIDI", "experimental"],
      "summary": "An NES emulator on the FM-1."
    },
    {
      "id": "fm1doom", "name": "fm1-doom", "author": "Keitark", "url": "https://github.com/Keitark/fm1-doom",
      "license": "GPL-2.0", "version": "unflashed", "date": "2026-10-09", "kind": "game-port", "base": "Doomgeneric",
      "status": "source-only", "installer": null, "editor": null, "cli": null, "usb": null, "identity": null, "info": null,
      "roles": null, "drums": null, "clock": null, "dx7": false, "recovery": "as fm1-nes", "warnings": ["no MIDI", "not hardware-verified"],
      "summary": "Doom on the FM-1, in progress."
    }
  ],
  "others": [
    "FoMni", "FiMba-1", "sloopDX", "GHOULBOX", "ChoralRoot", "Hortator", "zp12", "ORBIT", "AMB-1", "CTL-1", "FuMi-1",
    "fm1-chord", "WaveLoop", "Rainbow", "PurpleMonkey", "FM1 Quest", "April OS", "Optimist", "NoteSorcery", "FM1 Move",
    "Dinghy", "Felucca [Salt]", "SLOOP DX7 Banks", "SLOOP Floyd FM", "FM-1 Doom (zvenson)", "FM-1 B-Boy Edition (repo gone)"
  ],
  "others_note": "Listed on github.com/cicloid/awesome-fm-1 and the fm1-editor.com firmware directory; not yet catalogued. Most Felucca forks enumerate as 1209:0001 — the tools treat an unknown one as 'Felucca family' and show its INFO string."
}/*FM1-JSON-END*/;

const FM1_FIRMWARES = FM1_REGISTRY.firmwares;
function fm1Firmware(id) { return FM1_FIRMWARES.find(f => f.id === id) || null; }
