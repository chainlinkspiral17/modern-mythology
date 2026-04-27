# SFX — Sound Effects

One-shot sound effects triggered during scenes.

## Naming convention
`{description}.mp3`

## Examples
```
door_creak.mp3
rain_thunder.mp3
footsteps_gravel.mp3
spray_can_shake.mp3
paper_rustle.mp3
glass_clink.mp3
terminal_beep.mp3
static_burst.mp3
```

## Specs
- MP3 or OGG
- Short (under 10 seconds for most effects)
- Normalize to -6dB peak

## In scenes
```json
{ "t": "sfx", "src": "assets/audio/sfx/door_creak.mp3" }
```
