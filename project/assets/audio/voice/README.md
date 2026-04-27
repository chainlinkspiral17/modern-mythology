# Voice — Character Voice Acting

Per-line voice audio, one file per spoken node.

## Naming convention
`{scene_id}_{node_index}_{character}.mp3`

## Examples
```
vol1_intro_006_stranger.mp3     ← node 6 of vol1_intro, Stranger speaking
vol2_graveyard_001_jo.mp3
vol3_station14_005_oracle.mp3
```

## Specs
- MP3, 44.1kHz, 128kbps minimum
- Trim silence from start/end
- Consistent volume across all files for a character

## In scenes
Voice is attached directly to `say` nodes:
```json
{ "t": "say", "char": "Jo", "expr": "cold", "voice": "assets/audio/voice/vol2_graveyard_001_jo.mp3", "text": "You're late." }
```

The `voice` field is optional — if absent the line plays without audio.
