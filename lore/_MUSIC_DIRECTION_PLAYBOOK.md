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

## TEMPLATE

```
### YYYY-MM-DD — <one-line summary>

- <lesson>
- <lesson>
```
