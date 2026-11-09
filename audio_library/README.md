# audio_library

Working material for the Sound Studio (`godot/tools/sound_studio.py`). Everything
here is a *candidate*. The game only plays what you assign, and assigning copies
the file into `godot/assets/audio/`.

```
takes/<scene_id>/NNN_*.wav|mp3|ogg   dialogue takes. The NNN prefix is the node index,
                                     which is what links a take to its line.
sfx/<slot_id>/*                      candidates for one SFX slot
sfx/<anything else>/*                general effects (packs, foley) — browse under "All sfx"
music/<track_id>/*                   candidates for one music track
music/<anything else>/*              general music
scores/<track_id>/*.score.json|.mid  composed scores and their MIDI   ← tracked in git
library.json                         ratings, notes, links, what is live where (local)
.trash/                              items removed from the studio
```

Drop files into these folders by hand or through the studio; both work. Files
anywhere else under `takes/`, `sfx/` or `music/` still show up, just without an
automatic link to a slot (use **Link** in the studio).

Audio here is git-ignored, so it survives `update.sh` (which stashes untracked
files that are *not* ignored) and never bloats the repo. To keep the library
somewhere else, start the studio with `--library /path/to/folder` or set
`MM_AUDIO_LIBRARY`.

Render any tracked score to audio:

```bash
cd godot/tools && ./run_sound_studio.sh gen render ../../audio_library/scores/vol5_faucet_metronome/vol5_faucet_metronome__claude_session_01.score.json
```
