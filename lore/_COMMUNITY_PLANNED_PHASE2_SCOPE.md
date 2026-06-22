# COMMUNITY PLANNED · Phase 2 Scope · The BBS Shell

Phase 1 (the strategic map + day loop) shipped. This document
scopes phase 2 — the BBS layer — before authoring or coding starts.

Phase 2 is the half of the game where Frasier sits at the office
on Sunday nights and dials in. Per _COMMUNITY_PLANNED_SPEC.md
§The BBS layer, it's also the *unlock layer* — the place where
the slow-burn rewards land.

## What phase 2 ships (the contract)

Once phase 2 lands, a Sunday-night ADVANCE DAY transitions the
player from the strategic board into a CRT-styled dial-up interface
in which they:

1. Pick a BBS to dial. (6 BBSes total. Three are unlocked from W1;
   SNACKS unlocks W2 after Frasier's readmission; sysop boards open
   as the player encounters cross-references that warrant them.)
2. Read this week's new threads. The player's known state for each
   thread tracks: read / unread, read-fully / scanned, time spent.
3. Open the DM panel for any canon human and read this week's new
   updates from them. Some weeks a DM presents a choice (1 of 2-3
   single-sentence replies); the choice writes a flag the next
   Monday's strategic state reads.
4. Make 1-2 DM choices total per BBS night. The "1-2" is the BBS
   night's strategic-budget pacing per spec.
5. Discover hidden boards by following dial-up clues tucked into
   posts. Once dialled, the board joins the directory permanently.
6. Earn unlock-shelf items by: reading-deep, downloading archive
   files from THE_LIBRARY, dispatching demons / humans enough
   times for their backstory unlocks, and other small surfaces.
7. Hang up. ADVANCE DAY continues to Monday with the choices
   committed.

## Boards visible at start

| BBS | Sysop | Where | When |
|---|---|---|---|
| RUST_CODE.BBS | Frasier | Graustark, TX/LA | W1 |
| OVERPASS.BBS | STEEPLE | Mobile, AL | W1 |
| CALICHE.BBS | WIRE_MOTHER | Lubbock, TX | W1 |
| DRY_BLOOM.BBS | PALOMINO | Santa Fe, NM | W1 (intermittent) |
| BEDROCK.BBS | THE_QUARRY | Pennsylvania | W1 |
| SNACKS | rotating | (not in public directory) | W2 (after readmission) |

RUST_CODE.BBS visible boards from start: MAINSTREET, THE_BAR,
THE_LIBRARY, THE_WORKSHOP, THE_RECTORY, THE_ART_WALL.

Hidden boards on RUST_CODE.BBS, unlocked by following dial-up
clues in posts: THE_ATTIC, THE_GROVE, THE_RIVER_HOUSE,
THE_BASEMENT.

Virtual board: THE_BACKCHANNEL aggregates sysop-tagged threads
from all five sysop boards (RUST_CODE included). Available once
the player has visited at least three sysop boards.

## Work units, sized

Sized in terms relative to phase 1's commits. Phase 1 was ~8
commits, ~3000 lines GDScript + ~1500 lines JSON content.

### A · BBS frontend scene · medium

- New scene: `godot/scenes/games/CommunityPlannedBBS.tscn`
- Phosphor-green CRT theme (matches the gallery tile)
- Dial-up directory ("D" key brings up the rolodex)
- Board nav by single-letter command per spec
- Threaded post view (subject list → post body with replies)
- DM panel (one canon human at a time; backread visible)
- Backread navigation: PgUp/PgDn through history
- Status line bottom: dial-up number, carrier state, mail count

Sized: ~800-1000 lines GDScript + ~150 lines .tscn. Comparable
in shape to `TarotGauntletGame.gd` but the rules are quieter and
the UI is denser. One sprint.

### B · Data model · medium

JSON shapes under `godot/resources/games/community_planned/bbs/`:

- `dial_directory.json` — the 6 BBSes + dial-up numbers + masthead
  references + which are visible at start
- `bbs_<id>/board_list.json` — the boards visible on that BBS
- `bbs_<id>/<board>/threads/<thread_id>.json` — one file per
  thread (subject, OP, replies, attachments, sysop-tagged flag)
- `dms/<canon_id>.json` — per-human DM thread with weekly
  beats keyed by `available_from_week`
- `unlocks/<unlock_id>.json` — the unlock-shelf extension
  payloads (POV docs, archive files, demon dossiers, regional
  easter eggs)

Sized: schema is small; the volume comes from the authored
content (§C below).

### C · Authored content · the large piece

Volume estimate using phase 1's arcana-scenario authoring as a
yardstick (where I shipped ~1000 lines of in-voice content per
arcana × 14 arcana over several days):

| Surface | Threads | Posts | Volume |
|---|---|---|---|
| RUST_CODE / MAINSTREET | 12-15 | 60-100 | high |
| RUST_CODE / THE_BAR | 8-10 | 40-60 | medium-high |
| RUST_CODE / THE_LIBRARY | 8 | 20-30 | medium (mostly metadata for file unlocks) |
| RUST_CODE / THE_WORKSHOP | 6 | 25-40 | medium |
| RUST_CODE / THE_RECTORY | 5 | 20-30 | medium |
| RUST_CODE / THE_ART_WALL | 6 (file refs) | 8-10 | low + ASCII art assets |
| 4 sysop boards (full) | 4-6 each | 20-30 each | medium each |
| SNACKS | 12-15 | 40-60 | medium-high (incl. THE BLEACHED COUNTER weekly entries) |
| 4 hidden boards | 3-5 each | 10-20 each | medium combined |
| DMs (6 canon humans × 14 weeks) | n/a | ~120 beat-posts | high |
| Regulars (3 named) | spread across boards | ~25-40 each | medium-high combined |

Roughly: 100-150 distinct threads, 500-900 individual posts,
plus 6-10 ASCII art pieces for board mastheads and signed pieces
on THE_ART_WALL, plus a handful of MIDI references (the files
themselves are non-essential — period-correct flavor, not
required content).

This is the biggest piece. It's comparable to authoring the 14
arcana scenarios from earlier — maybe 1.2× that. Three to four
focused sprints if I batch by BBS.

### D · Weekly cadence wiring · small-medium

Engine work in `CommunityPlannedGame.gd`:

- After the Sunday weekly_spawn pass, transition into the BBS
  scene rather than rendering the strategic board for the
  Sunday→Monday tick.
- On BBS exit, ADVANCE DAY commits choices and resumes Monday.
- Add new effect kinds for the effect interpreter so DM replies
  can write strategic state: `demon_tip_off`, `ally_goes_silent`,
  `reveal_dial_up_clue`, `mark_thread_read`, `mark_file_downloaded`.
- Save state captures: read_thread_ids (set), opened_dm_thread_
  positions (per canon → last beat read), dialled_bbs_ids (set),
  unlocked_hidden_boards (set), downloaded_files (set),
  bbs_choices_made_this_session.

Sized: ~300-400 lines GDScript. One sprint.

### E · Frasier's ban + W2 readmission · small

- W1 SNACKS: locked. Attempting to dial it gets "NO CARRIER" +
  a one-line log "Your tombstone is still pinned."
- W2 BBS night: a DM from WIRE_MOTHER lands in Frasier's mail
  with the new dial-up number and a single sentence ("you're back").
- Player adds the number to the dialer. SNACKS opens.
- The tombstone thread on SNACKS is the canonical first read
  the player encounters: pinned post, banner ASCII, two pages of
  ribbing in the replies.

Sized: ~80 lines GDScript + ~150 lines authored content (the
tombstone thread is rich). Small.

### F · Hidden board discovery · small-medium

Each hidden board is discoverable by reading a specific thread
on a public board that contains a dial-up number. The dialer
recognises the number on enter and unlocks the board.

- THE_GROVE: dial-up clue in a MAINSTREET thread around W5
- THE_RIVER_HOUSE: dial-up clue in a THE_BAR thread (you only
  notice the clue if you've read enough threads to recognise the
  handle)
- THE_BASEMENT: dial-up clue in a THE_WORKSHOP thread
- THE_ATTIC: discoverable from a SNACKS bleached-counter entry
  (so post-W2)

Sized: ~100 lines engine + ~400 lines authored content (4
hidden boards × ~3-5 threads each, smaller-volume posts).

### G · THE_BACKCHANNEL aggregator · small

Virtual board view. Pulls posts from the 5 sysop boards (RUST_CODE
included) that carry the `sysop_tagged: true` field, sorts by
date, shows them as a single feed.

Sized: ~80 lines engine. No new authored content (uses existing
threads); the data flag is added to ~15-20 existing threads
that the writer designates as sysop-talk.

### H · Audio · small

- 14.4k modem dial-up tone (sampled or synthesised; 8 seconds)
- Carrier-locking soft click
- Optional: per-board ANSI redraw chirp on board navigation

If we have a sampled dial-up audio asset already in the project,
we use that; if not, synthesised from a sine generator at the
canonical V.32 / V.34 frequencies. I can write the generator.

Sized: ~50 lines GDScript + one audio file (or one ~30-line
synthesis function).

### I · Aria-coded vocabulary · the W11 glossary unlock · small

The sysop circle uses a specific vocabulary for Aria across all
boards. Reading any of those boards before W11 reads as ordinary
sysop-talk. The W11 glossary unlock — earned by reading enough
SNACKS bleached-counter entries — flips a re-read flag.

After unlock, the same posts re-read carry the glossary's
substitutions (the player can choose to see annotations or read
the original). The annotation reveals the sysop circle has been
talking about Aria the whole time.

Sized: ~80 lines engine (toggle + annotation rendering layer)
+ a glossary JSON file (~15-25 entries) + a one-shot W11
unlock notification.

### J · Regulars across the network · medium

Three named handles with cross-board presence:

- **chainlinkspiral** — RUST_CODE most often; OVERPASS and DRY_BLOOM
  occasionally; rarely on BEDROCK. Long careful threads, ASCII
  spiral signatures.
- **hasslein** — the time-loop physicist. Mostly on CALICHE;
  visits RUST_CODE on Wednesdays.
- **uzhekwurm** — transliterated cadence, mostly on BEDROCK.
  THE_QUARRY's only consistent correspondent.

Each gets a small dossier the player can compile by reading
enough posts (auto-tracks completion).

Sized: ~25-40 posts per regular = 75-120 posts, plus ~3 dossier
unlocks. Medium authoring task.

### K · Unlock shelf extension · small engine, medium content

The existing interlude shelf gets four new sections:

- POV documents (the surviving son's unsent memorial fragments,
  John Frank's column drafts, Mackenzie's grief threads, etc.)
- Archive files (audio recordings, photo scans, vol5-era
  documents from THE_LIBRARY)
- Demon dossiers (one per demon as the player dispatches enough)
- Regional easter eggs (one signature unlock per region)

Sized: ~100 lines engine (just new sections + earn predicates)
+ ~25-35 unlock payloads (significant but each is small).

### L · Architecture sweep · small

- `reveals.json` extension for the new BBS-night unlocks
- Save state capture for new fields (§D above)
- Validation cross-check (each DM references a canonical_
  character_id; each thread's referenced regulars exist in
  the regulars table)

Sized: ~150 lines total.

## Suggested order — four sprints

**Sprint 1 · Foundation (~1 week)**
- A · UI shell (CRT scene, dial directory, board nav, thread view)
- B · Data model schemas
- C · Cadence wiring (Sunday transition + save/load)
- L · Architecture sweep
- ~3 boards worth of skeleton threads to prove the data flow

After sprint 1 the player can dial in on Sunday, see boards,
read threads, hang up. No DMs yet; no real content.

**Sprint 2 · Texture (~1-2 weeks)**
- C · Authored content for RUST_CODE.BBS · all 6 public boards
- D · DM panel UI + 3 canon humans (John Frank / Mackenzie /
  Surviving Son) authored across the summer
- E · Frasier's ban + W2 readmission
- H · Audio (dial-up tone + carrier click)

After sprint 2 RUST_CODE is real, the friendship arcs read on
the DMs, the ban is a running gag.

**Sprint 3 · Reach (~1-2 weeks)**
- C · The 4 sysop boards (OVERPASS / CALICHE / DRY_BLOOM /
  BEDROCK) authored
- C · SNACKS authored (incl. THE BLEACHED COUNTER weekly entries)
- D · The remaining 3 canon humans' DMs (Elicia / Nicola / Jules)
- G · THE_BACKCHANNEL aggregator
- J · Regulars across the network (chainlinkspiral, hasslein,
      uzhekwurm)

After sprint 3 the network is the network. Federated sysop
conversation works. The regulars appear in voice.

**Sprint 4 · Depth (~1 week)**
- F · Hidden board discovery (4 hidden boards)
- I · Aria-coded vocabulary glossary (W11 unlock)
- K · Unlock shelf extension (POV docs, archive files, demon
      dossiers, regional easter eggs)
- Polishing, balance, the audio sweep

After sprint 4, phase 2 is materially done. Phase 3 (the hookup)
becomes the final integration pass.

Total estimate: **4-6 weeks** of focused work if I'm the only
hand on it; faster if some of the authoring lands in parallel.

## Pre-work checklist · what should land before I open sprint 1

1. **Aria glossary draft.** Mini-task — author ~15-25 substitutions
   (sysop coded term → canonical term). This is a lore-side
   decision the writer needs to make before I can author the
   sysop boards in voice. Can be a separate small commit.

2. **Hidden board placement decisions.** Confirm THE_GROVE,
   THE_RIVER_HOUSE, THE_BASEMENT, THE_ATTIC discovery weeks (W5,
   W6, W7, W8 vs others). Currently I have W5/W6/W7/W8 sketched.

3. **Audio asset decision.** Sampled dial-up tone in the asset
   tree, or synthesise? If sampled, who's sourcing it.

4. **Save state migration.** Phase 1 save files (save_version=1)
   will need to bump to save_version=2 to accommodate the new
   BBS read-state fields. The existing save loader already has
   a soft-fail on version mismatch; I'll wire migration on the
   sprint-1 commit.

## Risks · in honesty order

1. **Authoring volume is the big one.** 500-900 individual posts
   plus DMs plus mastheads is a 2-3 week solo-author task. It's
   comparable to the arcana scenarios but denser per post (each
   thread has authored replies that read as distinct voices).
   Mitigation: I batch by BBS, ship sprint by sprint, you can
   redirect mid-sprint if voice drifts.

2. **The strategic-effect surface widens.** DM replies want new
   effect kinds the engine doesn't have yet. Each one is small to
   wire but the count adds up. Mitigation: I write effects as
   I encounter them in the DM authoring; existing _exec_effect
   interpreter takes new kinds cleanly.

3. **The Aria-coded vocabulary needs a glossary decision before
   sprint 3.** Without it, the sysop boards read as deliberately
   coded but the player has nothing to decode. Mitigation:
   pre-work checklist above.

4. **Save state size grows from ~50KB to ~500KB.** Probably fine
   but worth knowing. Mitigation: read_thread_ids stored as a
   set of ints (each thread auto-numbered) keeps the size down.

5. **MIDI files were spec'd as period flavor.** Mitigation: I
   skip them in phase 2; flag them as one-day-future polish.
   The board posts can reference them; the data layer holds
   placeholders.

## Success criteria for phase 2

Mirroring the spec's phase-1 success criteria:

- A typical Sunday-night BBS session takes 12-25 minutes (the
  player wants to look forward to it, not be exhausted).
- The DM panel reads as character POV documents the player
  actually reads (not scrolls past).
- At least 3 canon-human DM threads "land" — the player feels
  like a friendship changed shape across the summer.
- Frasier's ban + W2 readmission lands as a running gag.
- By Labor Day the player has discovered at least 2 hidden boards.
- The unlock shelf has POV documents, archive files, and ≥1
  demon dossier on top of the phase-1 interludes.
- The chill-unwind tone holds — no quiz-style "right answer"
  beats, no failure for not reading enough.

If those land, the BBS layer earns its place alongside the
strategic map. Phase 3 (the hookup) becomes the final pass
that makes the two halves talk to each other clean.
