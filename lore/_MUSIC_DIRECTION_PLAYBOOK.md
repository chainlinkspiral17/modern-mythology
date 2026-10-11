# Music Direction Playbook

How the visual novels' music is *directed*: which track plays in a
scene and how hard it plays, beat by beat. The scene engine
(`GameEngine.gd`) directs pictures and words. The **MusicDirector**
(`godot/scripts/vn/MusicDirector.gd`) directs the score, and
GameEngine owns one.

Read this before touching `MusicDirector.gd`,
`godot/resources/music/direction.json`,
`godot/tools/music_direction.py`, or adding `{"t":"music"}` nodes to
a scene. For how audio files get made and reach the game, see
`_AUDIO_CAPTURE_PLAYBOOK.md`.

## Core rules

### 1. `direction.json` is the single source of truth

`godot/resources/music/direction.json` is strict JSON and documents
itself through `_doc` strings. Its sections:

| Section | Who writes it | What it holds |
|---|---|---|
| `defaults` | hand | attack/release, choice/cg/interlude levels, leitmotif cooldown |
| `lexicon` | hand | tension / calm words the inference scans |
| `scenes` | hand | **cue sheets** — per-scene track, intensity, beats |
| `locales` | hand | bg src → `{"<vol>": catalog id}` overrides |
| `characters` | hand | character key → `{"theme", "leitmotif"}` overrides |
| `locales_auto` | `music_direction.py suggest` | generated bg → track matches |
| `characters_auto` | `music_direction.py suggest` | generated `*_theme` → character |

- Never hand-edit the `*_auto` sections. Fix the authored section
  instead; authored entries always beat auto ones.
- Never hand-edit `music_catalog.json` to make the director happy.
- CI runs `python3 tools/music_direction.py validate` from `godot/`.
  It checks:
  - scene ids exist;
  - beat indices are in range;
  - tracks exist in the catalog;
  - music-node keys are valid.
- `report` shows where every scene's music comes from.

### 2. Track choice is a priority list — first playable wins

1. The scene cue sheet's `track`, which crossfades in.
2. A `{"t":"music","track":…}` or `{"t":"bgm"}` node, played as
   authored.
3. **Leitmotif.** The focal character's theme gets queued. The focal
   character is the themed speaker with the most lines, as long as
   they have at least 30% of the scene's lines.
4. The **locale track** for the scene's background, queued.
5. Otherwise AudioMgr's chapter list or volume queue, exactly as
   before the director existed.

A rule only counts if `AudioMgr.can_play(src)` is true. That means
the src file, its `.wav` sibling or its `.stems.json` exists. The
music binaries live in Google Drive (see the audio playbook), so on a
fresh checkout most tracks are missing. **A missing track must never
silence a scene that already had music.** It falls through to the
next rule.

### 3. Intensity drives the stems, not the volume

`AudioMgr.set_music_intensity(level)` fades layered stems in and out:

| Level | Layers playing |
|---|---|
| 0 | pad + chords |
| 0.25 | + bass |
| 0.5 | + drums |
| 0.75 | + lead |

A track without stems ignores intensity, which is harmless. So
intensity is how hard the score *plays*, never how loud it is. Don't
use it as a volume fader.

- **Authored** values hold until the next authored value. They come
  from three places:
  - the cue sheet's `intensity`;
  - beats (`{"at": <node index> | "choice" | "cg" | "interlude" | "end"}`);
  - `music` nodes.

  `{"auto": true}` hands control back to inference.
- **Inferred** values are used everywhere else.
  - The scene baseline comes from the tension of the whole scene's
    writing.
  - Each node then nudges it:
    - lexicon words;
    - exclamations;
    - clipped or CAPS lines;
    - `think` lines are quieter.
  - Choice (0.85) is anticipation, interlude (0.2) is breath, and
    cg (0.9) is lift.
- Smoothing uses `attack_sec` (2.5) for rises and `release_sec` (8)
  for falls. Music rises fast and decays slowly, like a film mix.
  Without the release, every calm line between two tense ones would
  pump the drums in and out.

### 4. Authoring, cheapest first

1. **Do nothing.** Inference plus the locale and leitmotif rules
   cover every scene.
2. **Cue sheet** in `direction.json` `scenes` gives a scene a fixed
   track or level, or a beat at a node index. This leaves the scene
   JSON untouched.
3. **`{"t":"music"}` node** in the scene goes in when the cue has to
   move with the text. The Scene Editor (`SceneEditorOverlay`) has a
   MUSIC node type with these fields:
   - TRACK
   - INTENSITY
   - STINGER
   - FADE
   - SILENCE
   - AUTO

   GameEngine skips past music nodes instantly, so they cost the
   reader nothing.

Music-node and beat keys:
- `track` is a catalog id.
- `intensity` is 0..1.
- `stinger` is a name, played from `assets/audio/stingers/<name>.ogg`
  over the track.
- `silence` is a bool.
- `fade` is in seconds. At 0 (≤ 0.05) the level snaps instead of
  smoothing, for hard cuts.
- `hard` defaults to true, which crossfades now. `hard: false`
  queues the track after the current one.
- `auto: true` hands intensity back to inference.

### 5. Replay and save/load

`GameEngine._load_scene(start_at)` calls `_music.replay(start_at)`
after `_replay_state`. The director re-walks nodes `0..start_at` with
no audio side effects, then applies the resulting state once. A
loaded save therefore lands on the right track at the right level.
**Any new director state must be rebuilt by `replay`, never
carried in a save.**

### 6. F4 and the readout

The director's readout is a CanvasLayer (layer 121, group `ui`). It
shows only while `FirstPersonController.hud_visible` and the VN debug
panel (Shift+F12) are both on. The readout shows:
- the track and the reason it was picked;
- the target and current intensity, and why;
- the focal character.

When a scene "sounds wrong", turn on the readout first.

### 7. The DAW composes temp tracks from the director's briefs

`python3 godot/tools/music_direction.py brief` writes
`resources/music/temp_briefs.json`. It is generated, so never
hand-edit it. `validate` warns when it is stale.

The brief replays every scene the way the director would, assuming
every catalog track has audio. For each track it records:
- the scenes that play it, and why (cue / bgm / leitmotif / locale /
  chapter);
- the intensity those scenes drive (p10 / mean / p90 of the per-node
  target);
- whether stems are needed;
- lexicon words, focal characters, locales;
- choice / cg / interlude moments;
- `energy` / `darkness`: the track's rank (0..1) against the game's
  other music;
- `curves`: for each listed scene (≤ 16), the director's per-node target
  compacted to ≤ 32 steps `{n, at: [node index], v: [target]}` (each
  step holds its bucket's PEAK, 2 decimals). The AUDIO DIRECTOR's PLAY
  AS SCENE drives the stems along it. `brief` writes every all-number
  list on one line so the file stays ~4k lines.

The DAW's TEMP TRACKS (the "VN scenes first" box, on by default) uses
it in four ways:
- makes the most-played tracks first;
- composes each one with `SeqGen.moodFromBrief`. The catalog text
  decides style and mode, and the scenes' words fill in only when it
  says nothing. Energy moves tempo and density inside the style;
  darkness ≥ 0.8 pushes a bright mode to minor (≥ 0.95: phrygian);
- gives a leitmotif track a song form;
- always renders stems for a track whose scenes move its intensity.

`simulate()` in `music_direction.py` is a Python port of the
director's scoring. **Change both together.** The `godot_director`
test runs the real GDScript and the port over every 20th real scene
and fails on any per-node difference above 1e-4.

### 8. Temp tracks are reviewed before the game hears them (AUDIO DIRECTOR)

By default the DAW no longer writes temp tracks straight into the game.
TEMP TRACKS (and every request from the AUDIO DIRECTOR) stages
**candidate takes**. `godot/tools/audio_director.html` previews them, and
APPROVE puts one where AudioMgr looks.

| Where | What |
|---|---|
| `assets/audio/review/<track id>/<take id>/` | Staging: `mix.wav`, `stems/<role>.wav`, `stems.json`, `credits.txt` (only for non-free instruments) and `meta.json`. It is ignored by version control, excluded from `music_drive.sh`, and `review/.gdignore` stops Godot importing or exporting it. |
| `<src base>.wav` · `<src base>.stems/<role>.wav` · `<src base>.stems.json` · `<src base>.wav.credits.txt` | What APPROVE writes: exactly what `AudioMgr._load_audio` / `_load_stems` read. Verified headless: an approved take plays as `AudioStreamSynchronized`, and intensity drops its layers. |
| `resources/music/temp_approvals.json` | Committed, and written only by the AUDIO DIRECTOR. Per track: `approved` (take, seed, mood, the request, instruments, date, `by`, notes, loudness, files), `rejected` [{take, seed, …}] and `history`. |

- **Take id** = `YYYYMMDD-HHMMSS-s<seed>`. `meta.json` holds:
  - `mood` `{style, form, mode, key, bpm, density, seed}` and `why`;
  - `request` (the creative direction below) and `instruments` (what
    each role actually played on);
  - `arrangement`, `roles`, `stems` [{name, role, layer}];
  - `lufs`, `true_peak`, `seconds`, `bars`;
  - credits, a summary of the brief, and `status` (candidate / approved
    / rejected).
- **Seeds:** each new take of a track uses a seed that no take in
  review, no approved take and **no rejected seed** has used. The first
  seed tried is the track's own (`hash(id)`), then
  `hash(id + '#takeN')`.
- **Identical regeneration:** ⟳ AGAIN sends the take's request plus its
  resolved mood and instruments. `key` is sent only if it was asked for:
  passing it changes `SeqGen.song`'s dice even when it is the same key.
- **Creative direction.** All of it is optional and is recorded in
  `meta.json` and the approval.
  - `description` goes through `SeqGen.moodFromBrief(track, brief,
    text)`. Words in it override the catalog's style / mode / pace /
    density words.
  - `instruments` per role (`kit`, `forge:<preset>`, `patch:<uid>`),
    picked from `window.FORGE_PRESETS` and `PatchBank.all()` at runtime.
  - `length` is `{bars}` or `{sec}`. Seconds nudge the tempo so that
    whole bars land on the length exactly. An asked-for length renders
    folded (the tail wraps onto the head), so it is exact and seamless.
  - `loop: true` also writes WAV loop points. Godot then loops the file
    forever, so use it only for beds.
  - `roles` chooses which of drums / bass / chords / lead / pad play.
  - `extraPads`: pad2 is the pad an octave up, pad3 its root an octave
    down. Each gets its own stem on layer 0.
  - `density`, `energy` (a ± nudge to the brief's rank), `style`,
    `mode`, `form`, `bpm` and `seed`.
- **Status per track:**
  - REAL AUDIO: a real `.ogg` / `.mp3`, or a `.wav` without the temp
    marker (a FIELD RECORDER take).
  - APPROVED TEMP: a `.wav` titled "(temp)" or carrying `mmjs.temp`.
  - CANDIDATES (n).
  - MISSING.
- **Safety:**
  - APPROVE refuses real audio.
  - Replacing an approved temp, REJECT and REVOKE each need a second tap
    within 4 s.
  - REVOKE deletes only the temp `.wav` plus its stems, manifest and
    credits.
- **Preview = the game.**
  - The player layers the stems with AudioMgr's rule
    (`level + 0.0001 >= layer`) and linear `1 / fade` per second fades.
  - PLAY AS SCENE replays a scene's curve with the director's attack /
    release from `direction.json`. It sends to the stems when the level
    changes by ≥ 0.02, with the 0.4 s fade, and shows the scene's lines.
- **Request protocol** (AUDIO DIRECTOR → DAW):
  1. The director stores `{rid, ids, takes, opts}` in localStorage
     `mm_director_req:<rid>`.
  2. It posts `{type: 'request', req}` on BroadcastChannel `mm_director`.
     An open, started DAW answers `ack` and runs the request.
  3. With no ack in 0.9 s, it opens
     `daw.html?director=<id,id>&takes=N&rid=<rid>&…` (simple overrides
     go in the URL too). That DAW shows the request on its START gate.
     One tap starts audio, re-grants the folder and makes the takes.
  4. The DAW reports `progress` / `take` / `done` on the BroadcastChannel
     **and** as a localStorage `mm_director_event` write (a `storage`
     event). Both reach other file:// pages in Chrome; the director
     de-duplicates by `uid`.
- The DAW's "straight into game (skip review)" box keeps the old direct
  write, for when you don't want a review step. It is off by default.

## Anti-patterns

- ❌ **Put `bgm` nodes everywhere to force a track.** Use a cue
  sheet; it's one line and survives scene rewrites.
- ❌ **Use intensity as a volume fader.** It switches stem layers.
- ❌ **Make a speaker alias match on a bare prefix.** `carlos` must
  never pick up `carl`'s theme. `suggest` checks word boundaries;
  keep it that way.
- ❌ **Treat a bgm src that isn't in the catalog as an error.** It
  is only a warning, because legacy directives are allowed. Fix the
  extension (vol5 had `.mp3` where the catalog says `.ogg`).
- ❌ **Assume a track exists because the catalog names it.** Always
  go through `AudioMgr.can_play`.

## Testing

- `godot/tools/tests/run_tests.sh godot_director` runs the headless
  Godot suite (`DirectorTester.gd` in the stub project). It checks:
  - tense vs calm inference;
  - choice / interlude / cg levels;
  - cue sheet pinning, beats and auto;
  - the leitmotif;
  - the locale track;
  - silence;
  - smoothing reaching AudioMgr;
  - replay.
- To compile-check the game scripts in the real project, see the
  2026-10-11 lesson below.

## Recent lessons

### 2026-10-11 — first pass: director, data file, tooling

- The user asked for music direction in the VNs "like the scene
  director". The answer is the same shape as the liminal system: a
  JSON truth file, a generator for the mechanical part, a validator
  in CI, and a thin runtime that only reads the JSON.
- Generated coverage on day one:
  - 132 of 312 scenes get a locale track;
  - 94 get chapter tracks;
  - 68 get only the volume queue;
  - 18 use bgm directives;
  - 48 characters have a leitmotif theme.
- The bg-src → track matcher needs a stoplist of generic tokens
  (back, room, station, …). Otherwise "back_room" matches every
  "back_*" track.
- `--check-only` and a `-s` script's `_init()` see neither autoloads
  nor the global class cache. To compile-check game scripts:
  1. Run `--import` once.
  2. Run a `-s` SceneTree script that calls `load()` a few frames in,
     from `_process`.
  3. Delete only the `.uid` / `.import` files the import created.
     Diff `git status --ignored` from before and after; never use a
     broad clean.
- Three vol5 scenes had `.mp3` bgm srcs for `.ogg` catalog tracks.
  `validate` catches that class of drift now.

### 2026-10-11 — director → DAW: temp tracks composed for their scenes

- The user asked to sync the director with the DAW so temp tracks
  fit the scenes. A brief file generated from the director (not a
  second set of rules in the DAW) keeps one source of truth. The
  Python port is guarded by a GDScript parity test; changing a
  calm-word weight from 0.75 to 0.70 fails it.
- First brief: **69 catalog tracks** are actually played by scenes:
  31 via chapter lists, 20 as leitmotifs, 14 via bgm, 10 as locale
  tracks. 12 need stems. The most-played are character themes: Tem
  (29 scenes), Sam (22), Lena (20).
- **Finding: the director barely varies its baseline between
  scenes.** Scene baselines span only 0.47–0.51, because most lines
  hit no lexicon word and `baseline = 0.5 + tension × 0.6`. Per-line
  bumps, choices and CGs still move it, but scene to scene the score
  plays at about the same strength. The briefs work around this with
  ranks. The real fix is in the director: a bigger lexicon or a larger
  tension gain. That's a tuning decision for the user, so it was not
  changed silently.

### 2026-10-11 — AUDIO DIRECTOR: review, approve, reject, regenerate

- The user asked for "an audio director tool that lets me preview and
  approve or reject the temp tracks and put them in the game files".
  They then asked for regeneration "with added description, instruments,
  length, and complexity". The DAW now stages candidate takes. Nothing
  reaches `<src>.wav` without an APPROVE, unless skip-review is ticked.
- `simulate()` was left untouched. The per-scene curves only compact its
  `targets`, inside `brief()`, so the GDScript parity test and the
  `validate` staleness check kept passing.
- A curve bucket keeps its **peak**, not its mean. The director attacks
  in 2.5 s and releases over 8 s, so a peak rules its neighbourhood. A
  mean flattened every choice / cg lift away.
- An approved temp is recognised from the WAV itself, not only from the
  approvals file: a "(temp)" INAM title or `mmjs.temp`. Without that
  check, a FIELD RECORDER `.wav` at the same path would read as a temp
  and could be revoked or replaced.
- APPROVE removes the old `.stems.json` and `.stems/` **before** it
  copies. If the new take had no stems, a stale manifest would keep
  playing the old stems over the new mix.
- `SeqGen.song` rolls the key only when none is given. Sending the
  recorded key to "regenerate identically" changed every note. So a
  regenerate request leaves `key` out unless the original asked for one.

## TEMPLATE

```
### YYYY-MM-DD — <one-line summary>

- <lesson>
- <lesson>
```
