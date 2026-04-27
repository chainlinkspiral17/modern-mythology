# BGM — Background Music

Looping background music tracks, one per scene/mood.

## Naming convention
`{vol}_{description}.mp3`

## Examples
```
vol1_diner_night.mp3
vol1_crossroads_theme.mp3
vol2_small_wood_ambient.mp3
vol2_funeral_procession.mp3
vol3_station_rain.mp3
vol3_oracle_interface.mp3
vol4_underpass_night.mp3
vol4_tag_chase.mp3
```

## Specs
- MP3 or OGG (MP3 preferred for compatibility)
- Should loop cleanly (loop point at silence or musical phrase boundary)
- Recommended: 2–4 minute loops, 192kbps+
- Engine fades between tracks automatically (600ms crossfade)

## In scenes
```json
{ "t": "bgm", "src": "assets/audio/bgm/vol2_small_wood_ambient.mp3" }
```
