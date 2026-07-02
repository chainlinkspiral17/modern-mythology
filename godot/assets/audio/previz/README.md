# Previz show tracks

Drop the song(s) the light show plays to **here** (`godot/assets/audio/previz/`).

- Formats: **.ogg**, **.wav**, or **.mp3** (Godot imports all three).
- One master mix for the whole ~4-minute film is simplest. If you drop several,
  they load in **sorted filename order**, so prefix them: `01_nana.ogg`,
  `02_omn.ogg`, `03_zonk.ogg`.
- The previz picks these up automatically on launch (it also accepts
  `user://song.ogg`). The HUD shows `(music)` once a track is loaded.

## How the music-reactive light show works

1. The loaded track becomes the timeline's **master clock** — press **T** to
   play; every camera/light/ref cue plays along with the music.
2. A spectrum analyzer on the Master bus feeds the rig live: beams **pump** and
   strobes **flash on the beat** (bass 40–280 Hz), so the show is generated from
   the audio automatically.
3. **Manual overrides:** press **O** until the timeline target reads `lighting`,
   set the look/fog/stage you want, then **J** to drop a light cue at the
   playhead. Those cues set discrete state (look, formation, strobe, blackout,
   fog, stage level) at exact times, layered on top of the live beat reactivity.
   Save the timeline with **/**.
