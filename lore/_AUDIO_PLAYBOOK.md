# Audio playbook

Hard-won rules for authoring, rendering, and wiring audio in the
Modern Mythology project. Companion to `godot/tools/audio/` (the
tool) and `godot/tools/audio/AUDIT.md` (the inventory).

## Core rules

### The audit is the map. Keep it up to date.

`godot/tools/audio/AUDIT.md` is the single source of truth for
what sound goes where. Every slot is tagged one of:

- `[existing]` · already in the repo pre-audio-arc
- `[preset]` · covered by a `slowstick_synth.py` SFX preset,
  rendered to disk
- `[rendered]` · a JSON composition rendered to a WAV
- `[compose]` · a BGM slot that needs authoring
- `[new]` · a preset needs to be added to `slowstick_synth.py`
- `[defer]` · authored intent captured, no wire-up yet

When you add or wire a sound, flip the tag in the same commit.
The tag mismatch is where audio drift begins.

### Two synthesis engines · Python + JS · always in sync.

`godot/tools/audio/slowstick_synth.py` is the reference. Every
preset there has a line-for-line JS twin in
`godot/tools/audio/importer.html` so a composer can drop a
`.mid` or `.json` into a browser tab and audition instantly
without touching the Deck. When you add a Python preset, port
it. When you can't (JS has different math semantics · e.g.
Python's negative modulo), leave a comment in both files.

### `SFXBank` is the ONE way to play short SFX.

`godot/autoload/SFXBank.gd` owns a small pool of
`AudioStreamPlayer` nodes and a preset-name → path map. Every
gameplay callsite goes through `SFXBank.play("preset_name")`.
This gives:

- **Overlapping playback** for bursts (verb select + customer
  bell + phone ring can all fire in the same second).
- **Once-warned missing files** so a mis-authored preset name
  doesn't spam the log.
- **Central volume control** via `Settings.sfx_vol`.

Do not `AudioMgr.play_sfx(path)` directly except from
`_audio_sfx()`-style legacy compat helpers that route through
the bank when a mapping exists.

### BGM belongs to `AudioMgr.play_bgm(path)`. Only one at a time.

BGM is exclusive · every controller that has a musical bed
calls `AudioMgr.play_bgm(...)` in its `boot()` or state-change
site. `AudioMgr` handles the cross-fade and format detection.
Don't try to play two BGMs at once · they'll collide on the
Music bus.

### Preset names are namespaced but flat.

Every preset name is a single string with no dot-nesting
(`tier_crossing_hungry`, not `cp.tier.crossing_hungry`). Files
live under `godot/assets/audio/sfx/<system>/<name>.wav` where
`<system>` is `e3` / `cp` / `gauntlet` / `ui`. The `SFXBank`
map handles the folder resolution; the callsite never touches
the folder.

### Composition-JSON is the authoring surface, not code.

A BGM loop lives at `godot/tools/audio/compositions/*.json` as
a tempo + tracks + notes structure. The Python tool renders it
to a WAV; Godot loads the WAV via `AudioMgr.play_bgm(...)`.
Don't hand-write raw WAV; don't try to synthesize live in
Godot. The Python round-trip is deterministic and diff-friendly.

### `_formant_voice` for anything word-shaped.

If the game needs a syllable that reads AS speech (the night-12
"sam." beat), use the 3-formant bandpass source-filter synth in
`_formant_voice()` inside `slowstick_synth.py`. Feed it three
formant breakpoints. Don't try to record TTS or fake vowels
with sine waves alone. The formant math is small (~40 lines);
the result is intelligible-enough with 30% static overlay.

## Recent lessons

### 2026-09-11 · the VN score · six volumes were playing vol5's music

The catalog is not the score. `music_catalog.json` carried 207
entries; **five audio files existed** (title_theme + vol5's four
oggs) and **thirty-six of the missing tracks were named by a
chapter.**

- **A chapter's music fails UP, not down.**
  `GameEngine._apply_chapter_music_context()` collects every entry
  whose `chapters` names the scene and calls
  `AudioMgr.set_chapter()`. An empty list is not silence — step 3
  of `play_next()` falls through to the player's unlocked
  playlist. So every vol1/2/3/4/6/7 chapter has been scored by
  whatever the player last heard, which in practice is
  D'Ambrosio's at dawn and the cicadas. **A missing bed sounds
  like a bed; that is why it survived.**
- **234 of 312 scenes had no entry naming them at all** — all of
  vol6 and vol7 bar a dozen, the whole Louisiana arcana run
  (ch6-ch21), the vol1 link hub. Fixed with a two-tier rule that
  is just what the assigned scenes were already doing:
  PLACE (the scene's dominant `3d:` background → that locale's
  bed) then the VOLUME FLOOR (`vol<N>_ambient`, which is exactly
  what those entries have always been). A place may cross volumes
  when it is the SAME PLACE — the Foxhole in vol1 and vol6, the
  cathedral in vol5 and vol7's interlude.
- **Author the locale→bed table; do not learn it.** Learning from
  the existing assignments smeared Kestrel's wind over the
  accretion basement, because a scene visits several places and
  the mapping is many-to-many.
- **READ `git status` BEFORE RENDERING OVER A NAME.** Ten of the
  thirty-six had been rendered long ago as `.wav` and sat on disk
  while their catalog `src` pointed at an `.mp3`/`.ogg` nobody
  ever made. The first pass overwrote all ten with new
  compositions and only the tracked-vs-untracked split in `git
  status` caught it. They are listed in `author_vn_beds.ON_DISK`
  now and are repointed, never re-authored.
- **`normalize_bank.py` walked `bgm/*/` and skipped `bgm/`.** The
  per-directory gain only visited SUBdirectories, so every
  slowstick sat at 0.85 peak and every VN bed shipped at the
  synth's raw 0.07-0.25. The top level is one more set now (one
  gain, 3.37x, relationships preserved).
- **A description is a usable spec.** Each catalog entry already
  said what its track was made of ("chain-link buzz + transformer
  60 Hz drone + a single grackle that won't leave"). The synth's
  `ambient_drone` / `fluorescent_hum` / `rain` / `slowstick_pad`
  cover that vocabulary directly; 33 beds came out of the prose in
  one pass.
- Draft 1 numbers to revisit on the Deck: **22050 Hz** (halves the
  WAV, and the hiss-forward beds — rest-stop wind, the cicada
  field, Kestrel's thermal — are where it will show first);
  **~40 s with no loop seam** (the chapter refill restarts the
  track, so the top of the bed is audible as a seam); and the
  five remaining `.ogg` tracks, which `normalize_bank` cannot
  read and may now sit under the wavs.
- New gate: `godot/tools/audit/music_coverage_audit.py` — a scene
  with no bed and a named bed with no file both fail at zero. 89
  ghosts (character themes, gauntlet B-sides, finale stingers)
  stay informational: their own systems play them.

### 2026-09-11 (ii) · the audio the CATALOG doesn't cover

Same defect one layer out: an `assets/audio/...` path written into a
script or a data file. Fifteen had never existed.

- **A player VERB that plays nothing is worse than a quiet room.**
  The Fool's diner carries two jukebox 45s as usable items
  (`play_jukebox_track` in `resources/games/fool/items.json`) —
  NOON ROOM ROOM and WHERE THE BAR USED TO BE — and both were a
  flavor paragraph and a filename. Authored, and they are the two
  tracks in this whole wave with an actual TUNE in them, because a
  45 on a jukebox is diegetic: the player chose to hear it.
- **An unlock can be gated on a file that does not exist.** The
  Music Player's TAPE REEL skin unlocks on having HEARD
  `vol5_elicia_theme_solo`. No file, no hearing, no skin — a
  cosmetic reward unreachable by construction. Check the unlock
  conditions when you check the tracks.
- **A dead fallback reads exactly like a live bug.** All twelve
  `gauntlet_*.ogg` paths in TarotGauntletGame's `_SFX` had never
  existed, and it took reading the routing to learn they were
  unreachable — an earlier pass had rerouted every key to an
  SFXBank preset. Deleted the table; `_audio_sfx` now
  `push_warning`s instead of falling through to a phantom path.
- **Per-directory normalization is wrong for an incremental add.**
  Once a directory is at target, the computed gain is 1.00, so a
  newly-dropped file keeps the synth's raw level forever. Three
  tracks shipped that way inside this same session before
  `normalize_bank.py --set <files…>` existed. **Render → `--set` the
  new files → then the directory pass stays a no-op.**
- New gate: `godot/tools/audit/audio_reference_audit.py` — every
  audio path in a .gd/.json/.tscn/.tres must exist, and every
  preset a `*_BANK_KEYS` table routes to must be in SFXBank.
  603 paths, 12 bank routes, zero.

### 2026-09-11 (iii) · the gauntlet's scenario beds

Fifteen catalog entries described one bed per **arcana × difficulty**
across the first five arcana — "Tarot Gauntlet · Empress · hard-mode
B-side. 11:14 PM, late February. The river has ice in it for the
first time in a decade" — with no files AND NO CALLER. Every board
played `_BGM_BY_LOCATION`'s location drone instead.

- **A catalog entry with no consumer is invisible to both audits.**
  `music_coverage_audit` only sees the chapter relation;
  `audio_reference_audit` only sees paths someone wrote down. A
  described track that nothing plays is caught by neither — the
  only thing that finds it is reading the descriptions and asking
  who would ever hear this. Fifteen more are still like that (the
  Magician's seven finale stingers and the Priestess's six, plus
  gauntlet_win / gauntlet_loss).
- **Difficulty is a time of day.** The B-side descriptions make it
  explicit and the beds follow: easy is afternoon light (major
  triads, the room open), medium is the working evening, hard is
  the small hours (drone forward, the pad down to two voices, one
  high tone that does not resolve). That reading also matches
  `_GAUNTLET_DESIGN_PLAYBOOK.md`'s "time-of-day as the primary
  difficulty axis" — the score should say what the board says.
- Wired as `_BGM_BY_SCENARIO` keyed `"<arcana>:<difficulty>"`, ahead
  of `_BGM_BY_LOCATION`, which still serves the other seventeen
  arcana. Scenario beds run 12-14 bars (55-65 s) rather than the
  chapter beds' ~40: a run is minutes, not a page.

### 2026-09-11 (v) · the endings get their music

Every gauntlet run ends on a win screen or a named Finale, and
neither played anything but a one-shot SFX — while the catalog had
carried "THE LEAP (won)", "TWENTY-FOUR HOURS (reversed)" and thirteen
named finale stingers since the music-slot pass.

- **Two shared stings first, named ones second.** `_audio_ending()`
  plays the win sting, or the finale's own sting if one is mapped,
  or the shared loss sting. That way all 22 arcana end on music
  today, and adding a named sting later is one table entry — no
  arcana is left in silence waiting for its own.
- The two shared stings are the **same two chords taken opposite
  ways**: A minor opening to C major and holding (the only cadence
  in the gauntlet's music, because winning is the only thing here
  that resolves), and C major falling to A minor with the third
  left out.
- `request_scene_bgm(path, false)` — non-looping, so the sting owns
  the ending screen and the rotation comes back on its own.
- **A `match` arm on an id nothing produces is silent dead code.**
  The Priestess milestone block matched six finale ids from the
  recording-booth staging; the bungalow board's four have different
  ids, so `milestone:priestess_finale:*` could never unlock. Rewritten
  by TRIGGER (stagnation / doubt / three claimed / shift over), which
  is the part that survives a restaging. New gate
  `godot/tools/audit/finale_id_audit.py` — 27 id references across 22
  arcana, zero dead. Scope the arcana guard **to the function**: an
  arcana-agnostic helper like `_loss_cg_path` otherwise inherits
  whatever guard precedes it and every id it names reads as dead.

### 2026-09-11 (iv) · the description was not the board

**THE SPEC CAN BE OUT OF DATE. CHECK IT AGAINST THE THING.** The
previous entry says "a description is a usable spec" and that is
true right up until the described thing moves. Six of the fifteen
B-side descriptions named a room the scenario no longer happens in,
and the first render believed all six:

- The **Emperor's** three describe a courthouse — brass clock,
  radiator on too high, a six-month appellate hearing. Every Emperor
  scenario is `location: riverboat_interior`: the Friday helm at
  8:14 PM, the produce contract at 9:06 AM, Sunday brunch.
- The **Hierophant's** three describe a BBS night and a ham band at
  14.301 MHz. The board is a Sunday circuit — St Jude's at 10:42 AM
  after the service, table 17 at brunch, the bandstand at 3:18 PM.
- The other nine had drifted only in their CLOCK (the Priestess's
  "booth" is Elicia's bungalow now; the times moved by hours). A bed
  survives a clock change if the hour it evokes still fits, so those
  kept their music and took corrected text.

The rule that comes out of it: **`resources/games/<arcana>/setup_*.json`
is the board of record.** It carries the location, the time, the
subtitle and the scene description, and it is maintained because the
game reads it. The catalog's `desc` is prose nobody's code checks, so
it rots. Read the setup first, then the description, and when they
disagree fix the description.

- Corrected in the tool, not by hand: `author_vn_beds.py --retitle`
  writes twelve titles and descriptions back into the catalog from a
  `RETITLE` table, so the correction is repeatable and reviewable.
  Ids stayed put — they are storage keys; the Music Player shows the
  title.
- A partial gate now exists: `audio_reference_audit.py` fails on a
  `_BGM_BY_SCENARIO` key whose `arcana × difficulty` no
  `setup_*.json` defines. That catches STRUCTURAL drift only —
  nothing automatic can tell you the prose has moved to another
  building.

### 2026-08-04 · CP · four dedicated beds + weekly rotation

- **When the user says "more of that," rotate — don't replace.**
  CP's three shared vol5 tracks stayed; four new compositions
  (cp_drafting_table / cp_phosphor_night / cp_tower_watch /
  cp_labor_day_dusk) alternate with them by week parity, so a
  100-day campaign stops wearing one groove without losing the
  sound the user praised.
- **Give states their own pieces, and give exactly one piece
  permission to resolve.** The tower bright/white + endless mode
  share an unresolving minor-second bed (the mode's argument is
  that nothing resolves); the Labor Day finale gets the only CP
  track with a cadence. Music routing IS state legibility — same
  principle as the banner variants.
- **normalize_bank after every render, still.** The fresh cp/ dir
  peaked at 0.23 and took a 3.71x gain; unnormalized it would sit
  buried under the menu music.

### 2026-07-22 · Spiderdrops · scoring a real-time physics stick

Five verb/weather SFX + one whole-run BGM bed for the new physics
stick, in one pass. Nothing new about the pipeline; two reminders:

- **`sfx <name> <output>` is POSITIONAL, not `--output`.** Lost a
  minute to `--output`. The subcommand takes the preset then a bare
  output path.
- **A live game wants the verb sounds SHORT and the bed LONG.** The
  four verbs are 50–340 ms (pluck/snap/spin/step); only the gust is
  ~1.1 s. The BGM is a 60 s Em loop that never resolves — the storm
  keeps coming. Ported all five presets to importer.html the same
  commit (parity rule held). normalize_bank gave the bed a 3.3x dir
  gain; run it after any render or the stick sits buried under the
  menu music.

### 2026-07-13 · per-locale ambient bed · the inverted soundtrack player

The VN now has a fourth audio layer: when a 3D locale loads, the
dominant Music Player track ducks WAY down and the locale's own
ambient bed rises on its own bus. Inverted crossfade — as ambient
goes up, BGM goes down; leaving the locale reverses it.

- **New `Ambient` bus + `_ambient` player in AudioMgr.** Mirrors the
  BGM/SFX/Voice trio. Starts silent (0.0001); a locale bed fades it
  up, exit fades it back to silence and stops the stream.
- **Compose your ducks, don't stack tweens fighting one bus.** The
  dialogue duck (DUCK_RATIO 0.32) and the ambient duck (AMBIENT_DUCK
  0.14) both attenuate the BGM bus. Instead of each writing the bus
  directly, `_bgm_bus_target()` returns `bgm_vol * duck_mult *
  amb_mult` and a single `_retarget_bgm_bus()` tweens to it. Dialogue
  shown inside a locale bed then Just Works (both pulls compose to
  0.32×0.14). Refactored `duck()/unduck()` onto this path.
- **Config is JSON, keyed by the Background3D `preset_id`.**
  `res://resources/audio/locale_ambient.json` maps locale → {bed,
  gain}. Fallback discipline: a locale with no entry (or a missing
  bed file, or a null parse) is a silent no-op — the Music Player is
  untouched there. Wrapped `{"locales": {...}}` form supported for
  future globals.
- **Hook at the locale boundary, not per-scene.** GameEngine calls
  `enter_locale_ambient(preset_id)` in `_apply_bg_3d` (BEFORE the GLB
  existence check, so the bed plays even on PNG fallback — the scene
  IS that locale) and `exit_locale_ambient()` in `_clear_bg_3d`.
- **Loop the bed per stream type.** `_set_stream_loop` sets `.loop`
  on Ogg/MP3 and `loop_mode = LOOP_FORWARD` on WAV — the three types
  `_load_audio` can return. Ambient beds MUST loop or the room goes
  silent after one pass.
- **Ship reusing existing drones, author bespoke where it counts.**
  17 locales mapped on first pull to the four shipped drones
  (riverboat, warehouse, cicadas, vol5/vol1 ambient); the two
  most-seen (diner_interior, cathedral_interior) got bespoke beds
  authored via `slowstick_synth compose` (diner: fluorescent_hum +
  low room drone + a far register ring; cathedral: A1 pedal-organ
  drone + fifths pad + one distant bell). NOTE: the instrument is
  `fluorescent_hum`, not `fluorescent` — a wrong name silently falls
  back to `slowstick_lead` (a LOUD tone that ruins a room-tone). Run
  `slowstick_synth list` and check the render log for "unknown
  instrument" before trusting the WAV.

### 2026-07-08 · closing the audit · 94-slot SFX arc from zero to 96/96

The audio arc landed nine wave-commits (A · C · D · gauntlet
wire-up · B · E · F · Wave B tail · Wave A itself). Went from
2 existing audio assets to 96 shipping slots · 82 SFX presets ·
12 rendered BGM compositions · every player-facing moment in
Estuary 3 and every state-change in CP has authored sound.

Lessons:

- **The audit is the plan.** Writing `AUDIT.md` first · listing
  every audio slot the game needs, keyed by act and moment ·
  turned the 96-slot commitment from "author until we run out
  of time" into "author until this file says green everywhere."
  Every wave-commit's diff was legible against the audit:
  which rows flipped from `[new]` to `[preset]`, which stayed.
  Without the audit we'd be discovering missing sounds in
  playtest for months.
- **Wave-based dev order gives huge leverage.** Wave A (10
  presets covering the six most-audibly-obvious UI moments)
  unblocked the entire loop's sense of "this game reacts to
  me." Wave B (BGM) came in second because a game with buttons
  clicking still feels dead if the music slot is silent. Wave
  C (CP demon-depth) came last of the gameplay waves because
  the CP demon economy was already legible without audio · the
  audio just added texture. Sequence by "how much dead silence
  is this wave removing?"
- **Small preset functions are the unit of authoring.** Every
  SFX preset is a ~10-30 line function that returns a
  `list[float]`. This shape is:  (a) trivially portable to JS
  for the importer, (b) trivially testable (pipe through
  `write_wav()` and open the file), (c) trivially auditable
  from the audit doc. Bigger units (multi-envelope samplers,
  patch-based synth voices) would sprawl. Fight the temptation.
- **Route legacy call sites through a central compat map.**
  `TarotGauntletGame._audio_sfx()` was already calling out to
  `_SFX[key] → AudioMgr.play_sfx(path)` at 12 sites. Adding an
  `_SFX_BANK_KEYS` compat map · one dict lookup at the head of
  `_audio_sfx` · picked up eight of those 12 sites for
  overlapping-pooled Wave-D playback with zero call-site
  changes. Never rewrite legacy call sites when a compat map
  works.
- **The importer.html is worth the porting cost.** JS port of
  the Python synth is ~1,000 lines and needs to be re-touched
  every wave. But: the composer can audition presets in a
  browser tab (Deck's Firefox works) with no `.wav` roundtrip.
  Any preset added to Python gets a JS twin in the same
  commit. The parity discipline is what keeps the two engines
  reconciled; a stale importer is a broken importer.
- **Formant synthesis is a small ceiling but a real one.** The
  night-12 "sam." beat took ~40 lines of source-filter synth
  and now the game has a distinctive human-speech-shaped beat
  that no other slowstick would try. When a sound genuinely
  wants to be a word, don't ambient-noise around it · do the
  math.

### 2026-07-08 · three-layer audio stack · BGM + ambient + SFX

Pirate Summer ships its audio in three cooperating layers.
Each layer answers a different question about the moment:

- **BGM** answers *what does this place feel like right now.*
  Six per-zone compositions (cabin_warmth, camp_daytime,
  alder_pond_water, caves_echo, campfire_evening,
  ghost_ship_forever · 42-90s loops), played via AudioMgr,
  swaps on zone-change.
- **Ambient** answers *what does the world do while you stand
  there.* Five one-shot loops (waves_lap, spruce_wind,
  campfire_crackle, ghost_moan, heron_call) fire every 15-45s
  on top of the BGM via a dedicated AudioStreamPlayer + a
  SceneTreeTimer that reschedules itself.
- **SFX** answers *what did you just do.* SFXBank presets from
  the existing library trigger on interactions (fact discovery,
  pickup, dialogue open, chatter appear, story beat, zone
  transition, day advance).

Lessons:

- **BGM is the room · Ambient is the world · SFX is the verb.**
  Once separated this way, mixing gets easy · BGM sits at
  base loudness, ambients duck slightly under it (~-12 to
  -14 dB), SFX one-shots peak briefly through everything.
  A single loud one-shot on top of a quiet room-tone reads
  as an event without breaking the atmosphere.
- **Author ambient loops as short compositions, not as one-off
  WAVs.** waves_lap.json is a 6-second rain-instrument note
  over a low drone.  ghost_moan.json is a 12-second D1 drone
  plus a fluorescent hum plus two soft-sine bells.  Each
  authored as a slowstick_synth JSON.  Regenerating them from
  edits is one command.  Compared to sourcing royalty-free
  WAVs, this discipline scales: the pipeline is the same as
  BGM, the review is the same as BGM, and the vibe is
  consistent with the rest of the game's sound.
- **Re-use existing SFX presets before authoring new ones.**
  Pirate Summer's SFX wire-up added zero new preset functions
  · it just wired existing register_ding, pickup, customer_
  bell, boot, season_settle, tile_hover, door_open into new
  trigger sites.  The estuary 3 audit pool was designed to
  be re-usable; use it before extending it.

### 2026-07-09 · ff/em roots · scoring two slowsticks in one wave

Fey Faire and Earthman Chronicles went from silent to fully scored
(6 BGM compositions, 6 ambient one-shots, 30+ SFX call sites) in
one session.

- **A slowstick's score is three layers, added in this order: BGM
  bed → moment SFX → ambient one-shots.** BGM via host-level
  `_play_bgm()` calls at scene-routing points (AudioMgr crossfades
  and dedupes, so calling on every route is safe). Moment SFX from
  the existing shared preset registry FIRST — win_chord /
  threshold_cross / basement_rite covered 18 moments with zero new
  WAVs. Only author new presets for sounds that are place-specific
  (calliope_drift, kyrindi_bell).
- **Ambient one-shot loops: self-terminating timer chains.** A
  `_schedule_ambient()` that plays a preset, then
  `create_timer(interval).timeout.connect(self)` — with an
  `_ambient_alive` flag flipped in `_exit_tree()`. SceneTreeTimers
  outlive freed nodes; without the flag the chain keeps firing
  into a dead scene.
- **Per-root SFXBank folders keep the registry auditable.** New
  games get their own root ("ff", "em") rather than piling into
  e3/. The PRESET_MAP stays the single registry the audit doc
  reads.
- **Cross-slowstick preset reuse is a lore tool.** Earthman's
  Working VII fires basement_rite — the same sting Community
  Planned uses for its basement rituals. Players who know both
  games hear the rhyme. Reuse on purpose, not just for thrift.

### 2026-07-11 · loudness normalization · the bank finally hits

- **Synth output must be normalized before it ships.** The
  slowstick_synth WAVs left the bank at peaks 0.04-0.30 (RMS -24
  to -36 dB) while the title theme and jukebox oggs ran at full
  master level — so every stick's music and SFX felt buried the
  moment the player had heard the menu ("not really hitting").
  New tool godot/tools/audio/normalize_bank.py: BGM gets one gain
  PER STICK DIRECTORY (0.85 / dir max peak, 14x cap) so internal
  mix relationships survive; one-shot SFX are peak-normalized PER
  FILE to 0.70, with SFXBank per-call scalars as the mixing layer.
  Run it after any synth wave; loudness is part of the render.

### 2026-07-11 · jukebox mode · the player owns the music

- **Scene BGM and player BGM are different requests — name them.**
  Hosts now call `AudioMgr.request_scene_bgm(src, loop)` instead
  of `play_bgm`; the Music Player and its transport keep the
  direct API. With the new jukebox toggle ON (default, persisted
  as `Settings.music_jukebox`), scene requests only mark the
  track heard while the FULL catalog rotates in order; toggled
  OFF, scenes get their looping beds and the VN queue/chapter
  logic back. Player feedback that forced it: "I don't want to
  have to mess with hearing the same song forever."
- **`res://`-prefixed srcs never played.** Every slowstick host
  passed `res://assets/audio/bgm/...` while `_load_audio`
  prepended `res://` again — double prefix, silent failure, and
  the queue quietly substituted an old VN track. That was a big
  part of "slowstick music not hitting." AudioMgr now
  `trim_prefix("res://")` at every entry point. Catalog srcs stay
  un-prefixed; that's the canonical form.
- **A jukebox must defeat import-level loops.** Rotation only
  advances on `finished`, and a looping stream never finishes.
  `_start_bgm` duplicates the stream and forces loop off in
  jukebox mode (on, with computed `loop_end`, for scene beds).
  Never mutate the shared imported resource — always duplicate.
- **Catalog entries can precede their audio; skip them cheaply.**
  132 of 207 catalog srcs have no file yet. The rotation checks
  `ResourceLoader.exists` + `FileAccess.file_exists` before
  returning a pick and marks gaps failed, so it never bounces
  off a failed load chain.
- **Slowstick tracks register with a `section` label, vol=99.**
  `add_stick_tracks_to_catalog.py` (idempotent) appends all 69
  stick WAVs grouped "SLOWSTICK · <NAME>"; MusicPlayerOverlay
  renders `section` as the group header when present. vol=99
  keeps `unlock_volume(n)` from mass-enqueueing them.

## TEMPLATE — new lesson entry

```
### YYYY-MM-DD · short session title

- **Punchy lesson, present tense.** Two-to-four sentences.
- **Next lesson.** Same shape.
```
