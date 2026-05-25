# Audio assets

The engine resolves audio `src` paths as `res://<src>`, so any `.ogg`,
`.mp3`, or `.wav` Godot can import works. Three buses, three folders:

```
assets/audio/
    bgm/      background music (BGM bus, spectrum-analyzed for visualizers)
    sfx/      one-shot effects (SFX bus, supports L/R pan per speaker)
    voice/    voice lines       (Voice bus, ducks BGM while playing)
```

## To test the visualizer

Drop a track at:

```
assets/audio/bgm/title_theme.ogg
```

The main menu calls `AudioMgr.play_bgm("assets/audio/bgm/title_theme.ogg")`
on load, and the music player overlay (and any AsciiVisualizer windows)
read magnitudes off the spectrum analyzer wired into the BGM bus. Any
filename in `music_catalog.json` works the same way — drop the file at
the path listed there.

## In-scene triggers

Scene JSON nodes:

```json
{ "t": "bgm", "src": "assets/audio/bgm/vol5_ambient.mp3" }
{ "t": "sfx", "src": "assets/audio/sfx/door_bell.ogg" }
{ "t": "say", "char": "John", "voice": "assets/audio/voice/john/0001.ogg", "text": "..." }
```

Missing files log a warning and are skipped — they don't crash the scene.
